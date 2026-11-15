import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from . import CONTENT, DATA, PROFILES, ROOT, db

STAGES = ["research", "strategy", "script", "gate:script", "voice", "voice_qa", "images", "render", "video_qa", "gate:final", "metadata", "schedule", "gate:publish", "published", "analytics"]
GATES = {"script": "gate:script", "final": "gate:final", "publish": "gate:publish"}


def manifest_path(cid):
    return CONTENT / cid / "manifest.json"


def load(cid):
    p = manifest_path(cid)
    if not p.exists():
        sys.exit(f"Unknown content id {cid}")
    return json.loads(p.read_text())


def save(m):
    manifest_path(m["id"]).write_text(json.dumps(m, indent=2, ensure_ascii=False))


def mark(m, stage, lang=None, status="done", note=None):
    key = f"{stage}:{lang}" if lang and not stage.startswith("gate:") else stage
    m["stages"][key] = {"status": status, "at": db.now(), **({"note": note} if note else {})}
    save(m)


def voice_profile(lang):
    vp = json.loads((PROFILES / "voices.json").read_text())
    if lang not in vp or vp[lang].get("status") != "approved":
        sys.exit(f"No approved voice profile for '{lang}'. Test voices first (see PROJECT_CONTEXT.md §Voice QA).")
    return vp[lang]


def require(m, gate, lang=None):
    g = m["stages"].get(GATES[gate], {})
    langs = g.get("langs", [])
    if g.get("status") != "approved" or (lang and langs and lang not in langs):
        sys.exit(f"Blocked: human approval '{gate}' is required for {m['id']}{' / ' + lang if lang else ''}. Use: python -m pipeline approve {m['id']} {gate} --note ...")


def cmd_new(a):
    with db.connect() as con:
        cid = db.next_content_id(con)
        folder = CONTENT / cid
        folder.mkdir(parents=True)
        langs = a.langs.split(",")
        db.upsert(con, "contents", {"id": cid, "series": a.series, "episode": a.episode, "topic": a.topic, "category": a.category, "style": a.style, "status": "research", "folder": str(folder.relative_to(ROOT)), "notes": None, "created_at": db.now(), "updated_at": db.now()})
        for lang in langs:
            db.upsert(con, "variants", {"id": f"{cid}-{lang}", "content_id": cid, "language": lang, "voice": None, "script_path": f"content/{cid}/{lang}/script.json", "video_path": None, "thumbnail_path": None, "duration_s": None, "status": "planned", "created_at": db.now(), "updated_at": db.now()})
    m = {"id": cid, "series": a.series, "episode": a.episode, "topic": a.topic, "category": a.category, "style": a.style, "languages": langs, "primary_language": langs[0], "stages": {}}
    save(m)
    (folder / "brief.md").write_text(f"# {cid}: {a.topic}\n\n- Series: {a.series or '-'} · Episode: {a.episode or '-'}\n- Category: {a.category} · Style: {a.style}\n- Languages: {', '.join(langs)} (primary {langs[0]})\n\n## Goal\n\n## Constraints\n")
    print(f"Created {cid} at content/{cid}")


def cmd_status(a):
    with db.connect() as con:
        ids = [a.id] if a.id else [r["id"] for r in con.execute("SELECT id FROM contents ORDER BY id")]
    for cid in ids:
        m = load(cid)
        print(f"\n{cid} · {m['topic']} · langs {','.join(m['languages'])}")
        for st in STAGES:
            keys = [st] if st.startswith("gate:") or st in ("research", "strategy") else [f"{st}:{l}" for l in m["languages"]]
            for k in keys:
                s = m["stages"].get(k)
                if s:
                    print(f"  {'✔' if s['status'] in ('done', 'approved') else '•'} {k:22s} {s['status']:9s} {s['at']} {s.get('note', '')[:60]}")
        nxt = next_action(m)
        print(f"  → next: {nxt}")


def next_action(m):
    for st in STAGES:
        if st.startswith("gate:"):
            if m["stages"].get(st, {}).get("status") != "approved":
                return f"human approval {st} (python -m pipeline approve {m['id']} {st.split(':')[1]})"
            continue
        langs = [None] if st in ("research", "strategy") else m["languages"]
        for l in langs:
            k = f"{st}:{l}" if l else st
            if m["stages"].get(k, {}).get("status") not in ("done", "approved"):
                return f"{st}{' for ' + l if l else ''}"
    return "complete"


def cmd_trending(a):
    from . import research

    tr = research.yt_trending(a.region)
    out = DATA / "reports" / f"trending-{a.region}-{tr['captured_at'][:10]}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(research.trending_markdown(tr))
    print(out)


def cmd_research(a):
    from . import research

    m = load(a.id)
    query = json.loads(a.query) if a.query.strip().startswith("{") else a.query
    with db.Run("research", a.id):
        rep = research.topic_report(m["topic"], query, a.wiki, a.langs.split(","), a.id)
    d = CONTENT / a.id / "research"
    d.mkdir(exist_ok=True)
    (d / "evidence.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False))
    (d / "evidence.md").write_text(research.report_markdown(rep))
    mark(m, "research", note="evidence collected; agent report pending" if not (d / "report.md").exists() else None)
    print(d / "evidence.md")


def cmd_approve(a):
    m = load(a.id)
    gate = GATES[a.gate]
    m["stages"][gate] = {"status": "approved", "at": db.now(), "note": a.note or "", "langs": a.langs.split(",") if a.langs else m["languages"]}
    save(m)
    with db.connect() as con:
        db.log_decision(con, gate, "approved", a.note, "human", content_id=a.id)
    print(f"{a.id}: {gate} approved")


def cmd_done(a):
    m = load(a.id)
    mark(m, a.stage, a.lang, note=a.note)
    print(f"{a.id}: {a.stage}{':' + a.lang if a.lang else ''} done")


def share_images(m, lang):
    if lang == m["primary_language"]:
        return
    src = CONTENT / m["id"] / m["primary_language"] / "img"
    dst = CONTENT / m["id"] / lang / "img"
    dst.mkdir(parents=True, exist_ok=True)
    script = json.loads((CONTENT / m["id"] / lang / "script.json").read_text())
    for i, sc in enumerate(script["scenes"]):
        if sc.get("kind") in ("verse", "shloka"):
            continue
        f = src / f"{i:02d}_raw.png"
        if f.exists() and not (dst / f.name).exists():
            shutil.copy2(f, dst / f.name)


def studio(args):
    cmd = [sys.executable, str(ROOT / "studio.py"), *args]
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT)


def cmd_produce(a):
    m = load(a.id)
    require(m, "script", a.lang)
    vp = voice_profile(a.lang)
    work = CONTENT / a.id / a.lang
    if not (work / "script.json").exists():
        sys.exit(f"Missing {work}/script.json")
    script = json.loads((work / "script.json").read_text())
    prof_path = PROFILES / "languages" / f"{a.lang}.json"
    if prof_path.exists() and "style_overrides" not in script:
        script["style_overrides"] = json.loads(prof_path.read_text()).get("style_overrides", {})
        script.setdefault("language", a.lang)
        (work / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False))
    base = [f"{m['id']} {a.lang}", "--out", str(work), "--style", m["style"], "--voice", vp["voice"]]
    if vp.get("speed"):
        base += ["--speed", str(vp["speed"])]
    steps = a.steps.split(",")
    if "voice" in steps:
        with db.Run("voice", a.id, f"{a.id}-{a.lang}"):
            studio(base + ["--stop-after", "voice"])
        mark(m, "voice", a.lang)
    if "images" in steps:
        share_images(m, a.lang)
        with db.Run("images", a.id, f"{a.id}-{a.lang}"):
            studio(base + ["--stop-after", "images"])
        mark(m, "images", a.lang)
    if "render" in steps:
        with db.Run("render", a.id, f"{a.id}-{a.lang}"):
            studio(base)
        vids = sorted(work.glob("*.mp4"), key=lambda p: p.stat().st_mtime)
        if vids:
            final = work / f"{a.id}-{a.lang}.mp4"
            if vids[-1] != final:
                shutil.move(vids[-1], final)
            with db.connect() as con:
                con.execute("UPDATE variants SET video_path=?, thumbnail_path=?, voice=?, status='rendered', updated_at=? WHERE id=?",
                            (str(final.relative_to(ROOT)), str((work / "thumbnail.png").relative_to(ROOT)), vp["voice"], db.now(), f"{a.id}-{a.lang}"))
            print(f"Rendered {final}")
        mark(m, "render", a.lang)
    from . import progress as _pg

    _pg.learn_from(a.id)


def cmd_qa(a):
    from . import qa

    m = load(a.id)
    work = CONTENT / a.id / a.lang
    video = work / f"{a.id}-{a.lang}.mp4"
    with db.Run("video_qa", a.id, f"{a.id}-{a.lang}"):
        rep = qa.run(video, work, work / "script.json", a.lang, f"{a.id}-{a.lang}", m["style"])
    (work / "qa.md").write_text(qa.markdown(rep))
    mark(m, "video_qa", a.lang, status="done" if rep["verdict"] != "fail" else "failed", note=rep["verdict"])
    print(qa.markdown(rep))


def cmd_schedule(a):
    from . import schedule

    rec = schedule.recommend(a.lang)
    print(json.dumps(rec, indent=2, ensure_ascii=False))
    if a.id:
        m = load(a.id)
        (CONTENT / a.id / a.lang / "schedule.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
        mark(m, "schedule", a.lang, note=f"{rec['slot']} {rec['publish_at']}")


def cmd_publish(a):
    m = load(a.id)
    require(m, "final", a.lang)
    require(m, "publish", a.lang)
    work = CONTENT / a.id / a.lang
    meta = work / "publish.json"
    sched = json.loads((work / "schedule.json").read_text()) if (work / "schedule.json").exists() else {}
    when = a.at or sched.get("publish_at")
    args = [sys.executable, str(ROOT / "publish.py"), "youtube", str(work / f"{a.id}-{a.lang}.mp4"), "--meta", str(meta), "--thumbnail", str(work / "thumbnail.png"), "--variant", f"{a.id}-{a.lang}", "--slot", a.slot or sched.get("slot", "")]
    if when:
        args += ["--publish-at", when]
    subprocess.run(args, check=True, cwd=ROOT)
    mark(m, "published", a.lang, note=when or "private")


def cmd_takes(a):
    from . import takes

    m = load(a.id)
    require(m, "script", a.lang)
    vp = voice_profile(a.lang)
    if not vp["voice"].startswith("veena:"):
        sys.exit("takes currently supports Veena voices (stochastic); Kokoro is deterministic — rephrase instead.")
    scenes = [int(x) for x in a.scenes.split(",")] if a.scenes else None
    with db.Run("voice_takes", a.id, f"{a.id}-{a.lang}"):
        takes.best_of(CONTENT / a.id / a.lang, a.lang, vp["voice"].split(":", 1)[1], scenes, a.n)
    mark(m, "voice", a.lang, note=f"best-of-{a.n}{' scenes ' + a.scenes if a.scenes else ''}")


def cmd_progress(a):
    import time as _t
    from . import progress

    while True:
        snap = progress.snapshot(a.id)
        print(progress.oneline(snap) if a.oneline else progress.render_table(snap), flush=True)
        if not a.watch or all(r["status"] == "done" for r in snap["steps"]):
            break
        _t.sleep(a.watch)


def cmd_link(a):
    with db.connect() as con:
        con.execute("INSERT OR REPLACE INTO publications (variant_id, platform, platform_id, url, privacy, scheduled_for, published_at, slot, metadata, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (a.variant, "youtube", a.video_id, f"https://www.youtube.com/shorts/{a.video_id}", "public", None, a.published_at, a.slot, None, db.now()))
    print(f"linked {a.variant} -> {a.video_id}")


def cmd_analytics(a):
    from . import analytics

    done = analytics.snapshot_due(force=a.force, label_override=a.label)
    for v, lab, views in done:
        print(f"snapshot {v} {lab}: views={views}")
    if not done:
        print("no snapshots due")


def cmd_report(a):
    from . import analytics

    text = analytics.report(a.variant)
    out = DATA / "reports" / f"performance-{a.variant}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(text)


def main():
    ap = argparse.ArgumentParser(prog="python -m pipeline", description="shorts-studio orchestration: research → script → production → QA → publish → analytics")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("new"); p.add_argument("--topic", required=True); p.add_argument("--series"); p.add_argument("--episode", type=int); p.add_argument("--category", default="mythology"); p.add_argument("--style", default="chalk"); p.add_argument("--langs", default="en,hi"); p.set_defaults(fn=cmd_new)
    p = sp.add_parser("status"); p.add_argument("id", nargs="?"); p.set_defaults(fn=cmd_status)
    p = sp.add_parser("trending"); p.add_argument("--region", default="IN"); p.set_defaults(fn=cmd_trending)
    p = sp.add_parser("research"); p.add_argument("id"); p.add_argument("--query", required=True, help='string, or JSON {"en": "...", "hi": "..."}'); p.add_argument("--wiki", required=True, help="English Wikipedia title"); p.add_argument("--langs", default="en,hi"); p.set_defaults(fn=cmd_research)
    p = sp.add_parser("approve"); p.add_argument("id"); p.add_argument("gate", choices=list(GATES)); p.add_argument("--note"); p.add_argument("--langs"); p.set_defaults(fn=cmd_approve)
    p = sp.add_parser("done"); p.add_argument("id"); p.add_argument("stage"); p.add_argument("--lang"); p.add_argument("--note"); p.set_defaults(fn=cmd_done)
    p = sp.add_parser("produce"); p.add_argument("id"); p.add_argument("--lang", required=True); p.add_argument("--steps", default="voice,images,render"); p.set_defaults(fn=cmd_produce)
    p = sp.add_parser("qa"); p.add_argument("id"); p.add_argument("--lang", required=True); p.set_defaults(fn=cmd_qa)
    p = sp.add_parser("schedule"); p.add_argument("--id"); p.add_argument("--lang", required=True); p.set_defaults(fn=cmd_schedule)
    p = sp.add_parser("publish"); p.add_argument("id"); p.add_argument("--lang", required=True); p.add_argument("--at"); p.add_argument("--slot"); p.set_defaults(fn=cmd_publish)
    p = sp.add_parser("takes"); p.add_argument("id"); p.add_argument("--lang", required=True); p.add_argument("--scenes", help="comma list of 1-based scene numbers (default all)"); p.add_argument("--n", type=int, default=3); p.set_defaults(fn=cmd_takes)
    p = sp.add_parser("progress", help="live progress, per-step ETA and finish time"); p.add_argument("id"); p.add_argument("--watch", type=int, default=0, help="refresh every N seconds until done"); p.add_argument("--oneline", action="store_true"); p.set_defaults(fn=cmd_progress)
    p = sp.add_parser("link"); p.add_argument("--variant", required=True); p.add_argument("--video-id", required=True); p.add_argument("--published-at", required=True); p.add_argument("--slot"); p.set_defaults(fn=cmd_link)
    p = sp.add_parser("analytics"); p.add_argument("--force", action="store_true"); p.add_argument("--label"); p.set_defaults(fn=cmd_analytics)
    p = sp.add_parser("report"); p.add_argument("variant"); p.set_defaults(fn=cmd_report)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
