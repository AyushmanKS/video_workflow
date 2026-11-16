import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from . import CONTENT, DATA, PROFILES, ROOT, db, gates

STAGES = ["research", "strategy", "script", "gate:script", "voice", "voice_qa", "images", "render", "video_qa", "gate:final", "metadata", "schedule",
          "gate:publish:youtube", "published", "gate:publish:instagram", "instagram_scheduled", "published_instagram", "analytics"]
GLOBAL_STAGES = ("research", "strategy")
INSTAGRAM_STAGES = ("gate:publish:instagram", "instagram_scheduled", "published_instagram")
GATES = {"script": "gate:script", "final": "gate:final", "publish": "gate:publish:<platform>"}
PROTECTED_STAGES = ("voice_qa", "video_qa")


def ev(kind, stage, message="", **kw):
    try:
        from . import events

        return events.emit(kind, stage, message, **kw)
    except Exception:
        return None


def ask_approval(m, gate_key_, lang, why):
    try:
        if lang in gates.approved_langs(m, gate_key_):
            return None
        plat = gate_key_.split(":")[2] if gate_key_.count(":") == 2 else None
        return ev("waiting_approval", gate_key_, why, variant_id=f"{m['id']}-{lang}", platform=plat)
    except Exception:
        return None


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


def require(m, gate, lang, platform=None, at=None, immediate=False):
    if gate == "script":
        problems = gates.check_script(m, lang)
    elif gate == "final":
        problems = gates.check_final(m, lang)
    else:
        problems = gates.check_publish(m, lang, platform, at, immediate)
    if problems:
        sys.exit("Blocked:\n  " + "\n  ".join(problems) + f"\nOwner approval: python -m pipeline approve {m['id']} {gate}{' --platform ' + platform if platform else ''} --langs {lang}")


def cmd_new(a):
    with db.connect() as con:
        cid = db.next_content_id(con)
        folder = CONTENT / cid
        folder.mkdir(parents=True)
        langs = a.langs.split(",")
        db.upsert(con, "contents", {"id": cid, "series": a.series, "episode": a.episode, "topic": a.topic, "category": a.category, "style": a.style, "status": "research", "folder": str(folder.relative_to(ROOT)), "notes": None, "created_at": db.now(), "updated_at": db.now()})
        for lang in langs:
            db.upsert(con, "variants", {"id": f"{cid}-{lang}", "content_id": cid, "language": lang, "voice": None, "script_path": f"content/{cid}/{lang}/script.json", "video_path": None, "thumbnail_path": None, "duration_s": None, "status": "planned", "cohort": db.cohort_for(lang), "created_at": db.now(), "updated_at": db.now()})
    m = {"id": cid, "series": a.series, "episode": a.episode, "topic": a.topic, "category": a.category, "style": a.style, "languages": langs, "primary_language": langs[0], "engine_version": 2, "stages": {}}
    save(m)
    (folder / "brief.md").write_text(f"# {cid}: {a.topic}\n\n- Series: {a.series or '-'} · Episode: {a.episode or '-'}\n- Category: {a.category} · Style: {a.style}\n- Languages: {', '.join(langs)} (primary {langs[0]})\n\n## Goal\n\n## Constraints\n")
    print(f"Created {cid} at content/{cid}")


def uses_instagram(m):
    return "instagram" in m.get("platforms", ["youtube"]) or "gate:publish:instagram" in m["stages"]


def stage_keys(m, st):
    if st in GLOBAL_STAGES or st.startswith("gate:"):
        return [st]
    return [f"{st}:{l}" for l in m["languages"]]


def cmd_status(a):
    with db.connect() as con:
        ids = [a.id] if a.id else [r["id"] for r in con.execute("SELECT id FROM contents ORDER BY id")]
    for cid in ids:
        m = load(cid)
        print(f"\n{cid} · {m['topic']} · langs {','.join(m['languages'])}")
        for st in STAGES:
            for k in stage_keys(m, st):
                s = m["stages"].get(k)
                if not s:
                    continue
                if "entries" in s:
                    for l, e in s["entries"].items():
                        extra = f" {e['time']}" if e.get("time") else ""
                        mig = " (migrated)" if e.get("migrated_from_legacy") else ""
                        print(f"  {'✔' if e['status'] == 'approved' else '✖'} {k + ':' + l:30s} {e['status']:9s} {e.get('at', '')}{extra}{mig} {e.get('note', '')[:40]}")
                else:
                    print(f"  {'✔' if s['status'] in ('done', 'approved') else '•'} {k:30s} {s['status']:9s} {s['at']} {s.get('note', '')[:60]}")
        legacy = m["stages"].get(gates.LEGACY_PUBLISH)
        if legacy:
            print(f"  · {'gate:publish (legacy)':30s} {'migrated' if legacy.get('migrated') else 'NOT MIGRATED — run migrate-gates'}")
        nxt = next_action(m)
        print(f"  → next: {nxt}")


def next_action(m):
    for st in STAGES:
        if st in INSTAGRAM_STAGES and not uses_instagram(m):
            continue
        if st.startswith("gate:"):
            ok = set(gates.approved_langs(m, st))
            missing = [l for l in m["languages"] if l not in ok]
            if missing:
                gate = st.split(":")[1]
                plat = f" --platform {st.split(':')[2]}" if st.count(":") == 2 else ""
                return f"human approval {st} for {','.join(missing)} (owner: python -m pipeline approve {m['id']} {gate}{plat} --langs {','.join(missing)})"
            continue
        langs = [None] if st in GLOBAL_STAGES else m["languages"]
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


def parse_times(spec, langs):
    if not spec:
        return {}
    if "=" not in spec:
        return {l: spec for l in langs}
    out = {}
    for part in spec.split(","):
        l, t = part.split("=", 1)
        out[l.strip()] = t.strip()
    return out


def owner_confirm(a, cid, lines, variants):
    print("\n".join(lines))
    if a.yes:
        if not gates.owner_env_ok(cid):
            sys.exit(f"--yes is only allowed when the owner has set {gates.OWNER_ENV}={cid} in the environment.")
        return
    if not sys.stdin.isatty():
        sys.exit("Approval is interactive: run it in your own terminal (or set the owner variable and pass --yes).")
    typed = input(f"\nType the variant id(s) to approve ({' '.join(variants)}): ").split()
    if sorted(typed) != sorted(variants):
        sys.exit("Variant ids did not match. Nothing approved.")


def cmd_approve(a):
    from . import lint

    m = load(a.id)
    langs = a.langs.split(",")
    unknown = [l for l in langs if l not in m["languages"]]
    if unknown:
        sys.exit(f"Unknown language(s) for {a.id}: {','.join(unknown)}")
    if a.gate == "publish" and a.platform not in gates.PLATFORMS:
        sys.exit("approve publish needs --platform youtube or --platform instagram")
    key = gates.gate_key(a.gate, a.platform)
    channel = a.channel or ("terminal" if not a.yes else None)
    if not channel:
        sys.exit("--channel is required with --yes (e.g. chat, telegram, terminal)")
    problems, lines, entries_ = [], [f"Approve {key} for {a.id} ({','.join(langs)}) by {a.by} via {channel}"], {}
    times = parse_times(a.at, langs)
    for lang in langs:
        variant = f"{a.id}-{lang}"
        f = gates.variant_files(m, lang)
        if a.gate == "script":
            rep = lint.lint(a.id, [lang])[lang]
            if rep["verdict"] == "fail":
                problems.append(f"{variant}: lint FAIL — " + "; ".join(x["message"] for x in rep["findings"] if x["level"] == "fail"))
            e = gates.build_entry(m, "script", lang, by=a.by, channel=channel, note=a.note, nonce=a.nonce)
            if not e["sha256"]:
                problems.append(f"{variant}: missing script.json")
            lines.append(f"  {variant}  script sha256 {e['sha256']}  lint {rep['verdict']}")
        elif a.gate == "final":
            problems += gates.check_script(m, lang)
            ok, qp, rid = gates.qa_status(m, lang)
            problems += qp
            e = gates.build_entry(m, "final", lang, by=a.by, channel=channel, note=a.note, nonce=a.nonce, qa_report=rid)
            lines.append(f"  {variant}  video {gates.rel(f['video'])} sha256 {e['sha256']}  QA report #{rid}")
        else:
            problems += gates.check_final(m, lang)
            t = times.get(lang)
            if not t and a.platform == "youtube":
                sp = f["work"] / "schedule.json"
                sched = json.loads(sp.read_text()) if sp.exists() else {}
                t = sched.get("publish_at") or (gates.NOW if sched.get("slot") == gates.NOW else None)
            if not t:
                problems.append(f"{variant}: no publish time; pass --at {lang}=<ISO time> (or 'now')")
            elif t != gates.NOW:
                try:
                    gates.parse_time(t)
                except ValueError:
                    problems.append(f"{variant}: bad time {t}")
            if f["legacy"]:
                problems.append(f"{variant}: video is a legacy out/ file; new platform uploads of legacy files are blocked")
            if not f["meta"].exists():
                problems.append(f"{variant}: missing publish.json")
            elif a.platform not in json.loads(f["meta"].read_text()):
                problems.append(f"{variant}: publish.json has no '{a.platform}' section")
            e = gates.build_entry(m, "publish", lang, a.platform, t, by=a.by, channel=channel, note=a.note, nonce=a.nonce)
            lines.append(f"  {variant}  {a.platform} at {t}\n      video {e['video']} sha256 {e['video_sha256']}\n      meta  {e['meta']} sha256 {e['meta_sha256']}")
        entries_[lang] = e
    if problems:
        sys.exit("Refused:\n  " + "\n  ".join(problems))
    owner_confirm(a, a.id, lines, [f"{a.id}-{l}" for l in langs])
    m = load(a.id)
    for lang, e in entries_.items():
        gates.record(m, key, lang, e)
    if a.gate == "publish" and a.platform == "instagram":
        m.setdefault("platforms", ["youtube", "instagram"])
    save(m)
    with db.connect() as con:
        for lang, e in entries_.items():
            sha = e.get("sha256") or {"video": e.get("video_sha256"), "meta": e.get("meta_sha256"), "time": e.get("time")}
            db.log_decision(con, key, "approved", a.note, "human", content_id=a.id, variant_id=f"{a.id}-{lang}", actor=a.by, channel=channel, artifact_sha256=sha)
    for lang, e in entries_.items():
        when = f" for {e.get('time')}" if e.get("time") else ""
        ev("approved", key, f"owner approved {key}{when} via {channel}" + (f": {a.note[:160]}" if a.note else ""), variant_id=f"{a.id}-{lang}", platform=a.platform if a.gate == "publish" else None)
    print(f"{a.id}: {key} approved for {','.join(langs)}")


def cmd_reject(a):
    m = load(a.id)
    if a.gate == "publish" and a.platform not in gates.PLATFORMS:
        sys.exit("reject publish needs --platform youtube or --platform instagram")
    key = gates.gate_key(a.gate, a.platform)
    langs = a.langs.split(",") if a.langs else m["languages"]
    gates.reject(m, key, langs, a.note, a.by, a.channel or "terminal")
    save(m)
    with db.connect() as con:
        for lang in langs:
            db.log_decision(con, key, "rejected", a.note, "human", content_id=a.id, variant_id=f"{a.id}-{lang}", actor=a.by, channel=a.channel or "terminal")
    for lang in langs:
        ev("rejected", key, f"owner rejected {key}: {a.note[:200]}", variant_id=f"{a.id}-{lang}", platform=a.platform if a.gate == "publish" else None, error_code="gate_rejected")
    print(f"{a.id}: {key} rejected for {','.join(langs)}")


def cmd_waive(a):
    m = load(a.id)
    variant = f"{a.id}-{a.lang}"
    sha = gates.sha256(gates.variant_files(m, a.lang)["video"])
    with db.connect() as con:
        rep = gates.latest_qa(con, variant)
    if not rep or rep["mp4_sha256"] != sha:
        sys.exit(f"{variant}: no QA report for the current video; run pipeline qa first")
    names = {c["name"]: c for c in rep["report"]["checks"]}
    if a.check == "all-warnings":
        rejects = [n for n, c in names.items() if c.get("class") == "reject" and not c["ok"]]
        if rejects:
            sys.exit(f"{variant}: auto-reject checks failed and cannot be waived: {', '.join(rejects)}")
        picked = [c for c in names.values() if not c["ok"]]
        if not picked:
            sys.exit(f"{variant}: nothing to waive in QA report #{rep['id']}")
    else:
        c = names.get(a.check)
        if not c:
            sys.exit(f"{variant}: no check named '{a.check}' in QA report #{rep['id']} ({', '.join(names)})")
        if c.get("class") == "reject" and not c["ok"]:
            sys.exit(f"{variant}: '{a.check}' is an auto-reject check; it cannot be waived — fix it")
        picked = [c]
    lines = [f"Waive for {variant} (QA #{rep['id']}, video {sha[:12]}): {a.note}"]
    for c in picked:
        lines += [f"  {c['name']}"] + [f"    - {i}" for i in c["issues"]]
    owner_confirm(a, a.id, lines, [variant])
    with db.connect() as con:
        for c in picked:
            con.execute("INSERT INTO waivers (variant_id, check_name, mp4_sha256, note, actor, channel, created_at) VALUES (?,?,?,?,?,?,?)", (variant, c["name"], sha, a.note, a.by, a.channel or "terminal", db.now()))
            db.log_decision(con, "waiver", c["name"], a.note, "human", content_id=a.id, variant_id=variant, actor=a.by, channel=a.channel or "terminal", artifact_sha256=sha)
    ev("info", "waiver", f"owner waived {', '.join(c['name'] for c in picked)}: {a.note[:160]}", variant_id=variant)
    print(f"{variant}: waivers recorded for {', '.join(c['name'] for c in picked)}")


def cmd_done(a):
    if a.stage in PROTECTED_STAGES or a.stage.startswith("gate:"):
        sys.exit(f"'{a.stage}' cannot be marked done by hand: run python -m pipeline qa (it records the verdict), or use approve for gates.")
    m = load(a.id)
    mark(m, a.stage, a.lang, note=a.note)
    print(f"{a.id}: {a.stage}{':' + a.lang if a.lang else ''} done")
    if a.lang:
        ev("completed", a.stage, f"{a.stage} marked done" + (f": {a.note[:160]}" if a.note else ""), variant_id=f"{a.id}-{a.lang}")
        if a.stage == "script":
            ask_approval(m, gates.SCRIPT, a.lang, "script ready for G1 (owner review)")
        elif a.stage == "metadata":
            ask_approval(m, gates.publish_key("youtube"), a.lang, "metadata ready; G3 needs video, metadata and publish time")
    else:
        ev("completed", a.stage, f"{a.stage} marked done", content_id=a.id)
    if a.stage == "script" and a.lang:
        from . import lint

        lint.log_features(m, a.lang, "script")


def cmd_lint(a):
    from . import lint

    if a.calibrate:
        out = lint.calibrate()
        for l, v in out["languages"].items():
            print(f"{l}: {v['rate']} w/s · {v['letter_rate']} letters/s · n={v['n']} · max |error| {v['max_abs_error_s']} s ({v['voice']})")
        print(f"written {lint.RATES_PATH.relative_to(ROOT)}")
        if not a.id:
            return
    if not a.id:
        sys.exit("lint needs a content id")
    res = lint.lint(a.id, a.lang.split(",") if a.lang else None)
    print(lint.markdown(res))
    if any(r["verdict"] == "fail" for r in res.values()):
        sys.exit(1)


def cmd_migrate_gates(a):
    ids = [a.id] if a.id else sorted(p.parent.name for p in CONTENT.glob("C*/manifest.json"))
    with db.connect() as con:
        for cid in ids:
            m = load(cid)
            rep = gates.migrate(m, con, dry_run=a.dry_run)
            print(f"{cid}: script {rep['script'] or '-'} · final {rep['final'] or '-'}")
            print(f"  youtube:   {rep['youtube'] or '-'}")
            print(f"  instagram: {rep['instagram'] or '-'}")
            if rep["skipped"]:
                print(f"  skipped:   {rep['skipped']}")
            m = load(cid)
            for line in gates.rescope_meta_hashes(m):
                print(f"  meta hash: {line}")
            if not a.dry_run:
                save(m)
    print("dry run: nothing written" if a.dry_run else "migration recorded (manifests + decisions table)")


def cmd_hooks(a):
    m = load(a.id)
    n = 0
    with db.connect() as con:
        for lang in ([a.lang] if a.lang else m["languages"]):
            p = CONTENT / a.id / lang / "hooks.json"
            if not p.exists():
                continue
            variant = f"{a.id}-{lang}"
            sha = gates.sha256(p)
            con.execute("DELETE FROM hooks WHERE variant_id=?", (variant,))
            for h in json.loads(p.read_text()):
                con.execute("INSERT INTO hooks (variant_id, text, scores, selected, reasoning, created_at, source_sha256) VALUES (?,?,?,?,?,?,?)",
                            (variant, h["text"], json.dumps({**h.get("scores", {}), **({"total": h["total"]} if "total" in h else {}), **({"type": h["type"]} if "type" in h else {})}, ensure_ascii=False), int(bool(h.get("selected"))), h.get("reasoning"), db.now(), sha))
                n += 1
    print(f"{a.id}: loaded {n} hooks into data/studio.db")


def cmd_features(a):
    from . import lint

    if a.all:
        for v, row in lint.backfill_features(a.stage if a.stage != "manual" else "backfill"):
            print(f"{v}: " + (f"{row['duration_s']} s ({row['duration_source']}), {row['scenes']} scenes, first_frame {row['first_frame']}, slot {row['slot_ist']}, title {row['title_pattern']}" if row else "skipped (no script)"))
        return
    if not a.id:
        sys.exit("features needs an id or --all")
    m = load(a.id)
    for lang in ([a.lang] if a.lang else m["languages"]):
        row = lint.log_features(m, lang, a.stage)
        if row:
            print(json.dumps(row, ensure_ascii=False))


def cmd_publish_queue(a):
    from . import queue

    queue.cli(a)


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


def watch(cid, lang, step):
    try:
        from . import events

        return events.Watch(cid, lang, step)
    except Exception:
        from contextlib import nullcontext

        return nullcontext()


def studio(args):
    cmd = [sys.executable, str(ROOT / "studio.py"), *args]
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT)


def cmd_produce(a):
    from . import cleanup

    cleanup.guard()
    m = load(a.id)
    require(m, "script", a.lang)
    from . import lint

    rep = lint.lint(a.id, [a.lang])[a.lang]
    if rep["verdict"] == "fail":
        sys.exit(f"Blocked: lint fails for {a.id}-{a.lang}:\n" + lint.markdown({a.lang: rep}))
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
    if int(m.get("engine_version", 1) or 1) >= 2 and "engine_version" not in script:
        script["engine_version"] = int(m["engine_version"])
        (work / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False))
    base = [f"{m['id']} {a.lang}", "--out", str(work), "--style", m["style"], "--voice", vp["voice"]]
    if vp.get("speed"):
        base += ["--speed", str(vp["speed"])]
    steps = a.steps.split(",")
    if "voice" in steps:
        with db.Run("voice", a.id, f"{a.id}-{a.lang}"):
            with watch(a.id, a.lang, "voice"):
                studio(base + ["--stop-after", "voice"])
        mark(m, "voice", a.lang)
    if "images" in steps:
        share_images(m, a.lang)
        with db.Run("images", a.id, f"{a.id}-{a.lang}"):
            with watch(a.id, a.lang, "images"):
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
        lint.log_features(m, a.lang, "render")
    from . import progress as _pg

    _pg.learn_from(a.id)


def cmd_qa(a):
    from . import qa

    m = load(a.id)
    work = CONTENT / a.id / a.lang
    video = gates.variant_files(m, a.lang)["video"]
    stage = "voice_qa" if a.audio_only else "video_qa"
    with db.Run(stage, a.id, f"{a.id}-{a.lang}", emit_done=False):
        rep = qa.run(None if a.audio_only else video, work, work / "script.json", a.lang, f"{a.id}-{a.lang}", m["style"], audio_only=a.audio_only)
    try:
        from . import explain

        if rep["verdict"] == "fail":
            ev("failed", stage, f"QA fail (report #{rep.get('id')})", variant_id=f"{a.id}-{a.lang}", error=explain.qa_failure_text(rep), error_code="qa_fail",
               detail={"qa_report": rep.get("id"), "verdict": rep["verdict"]}, log_ref=str((work / ("voice_qa.md" if a.audio_only else "qa.md")).relative_to(ROOT)))
        else:
            warns = [c["name"] for c in rep.get("checks", []) if not c.get("ok") and not c.get("skipped")]
            ev("completed", stage, f"QA {rep['verdict']} (report #{rep.get('id')})" + (f"; warnings: {', '.join(warns)}" if warns else ""), variant_id=f"{a.id}-{a.lang}",
               detail={"qa_report": rep.get("id"), "verdict": rep["verdict"], "warnings": warns})
            if not a.audio_only:
                ask_approval(m, gates.FINAL, a.lang, f"video QA {rep['verdict']}; G2 needs the owner to watch the final video")
    except Exception:
        pass
    (work / ("voice_qa.md" if a.audio_only else "qa.md")).write_text(qa.markdown(rep))
    (work / ("voice_qa_report.json" if a.audio_only else "qa.json")).write_text(json.dumps(rep, indent=2, ensure_ascii=False))
    mark(m, stage, a.lang, status="done" if rep["verdict"] != "fail" else "failed", note=f"{rep['verdict']} (report #{rep.get('id')})")
    print(qa.markdown(rep))


def cmd_schedule(a):
    from . import schedule

    rec = schedule.recommend(a.lang)
    print(json.dumps(rec, indent=2, ensure_ascii=False))
    if a.id:
        m = load(a.id)
        (CONTENT / a.id / a.lang / "schedule.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
        mark(m, "schedule", a.lang, note=f"{rec['slot']} {rec['publish_at']}")
        ev("completed", "schedule", f"recommended slot {rec['slot']} {rec['publish_at']}", variant_id=f"{a.id}-{a.lang}")


def resolve_when(a, m, platform):
    if a.at:
        return a.at
    t = gates.approved_time(m, a.lang, platform)
    if t == gates.NOW:
        if platform == "youtube":
            from datetime import datetime, timedelta

            return (datetime.now(gates.IST) + timedelta(minutes=15)).replace(second=0, microsecond=0).isoformat()
        return None
    return t


def cmd_publish(a):
    m = load(a.id)
    variant = f"{a.id}-{a.lang}"
    if a.platform == "instagram" and a.cancel:
        from . import igschedule

        print(f"{variant}: Instagram job {'removed' if igschedule.remove(variant) else 'not found'}")
        return
    f = gates.variant_files(m, a.lang)
    work, meta, video, thumb = f["work"], f["meta"], f["video"], f["thumb"]
    sched = json.loads((work / "schedule.json").read_text()) if (work / "schedule.json").exists() else {}
    when = resolve_when(a, m, a.platform)
    require(m, "publish", a.lang, a.platform, when, immediate=a.platform == "instagram" and a.now)
    if a.check_gates_only:
        print(f"{variant}: gates OK for {a.platform} at {when or 'now'} (video {gates.sha256(video)[:12]}, meta {gates.sha256(meta)[:12]})")
        return
    if a.platform == "instagram":
        return publish_instagram(a, m, work, variant, meta, sched, when, video, thumb)
    args = [sys.executable, str(ROOT / "publish.py"), "youtube", str(video), "--meta", str(meta), "--thumbnail", str(work / "thumbnail.png"), "--variant", variant, "--slot", a.slot or sched.get("slot", "")]
    if when:
        args += ["--publish-at", when]
    if a.yes:
        args.append("--yes")
    subprocess.run(args, check=True, cwd=ROOT)
    mark(m, "published", a.lang, note=when or "private")
    from . import lint

    lint.log_features(m, a.lang, "publish")


def publish_instagram(a, m, work, variant, meta, sched, when, video, thumb):
    from datetime import datetime, timezone

    from . import igschedule

    now = datetime.now(timezone.utc)
    at = igschedule.parse(when) if when else None
    if at and not a.now and (at - now).total_seconds() > 60:
        if not a.yes:
            sys.exit("Scheduling an unattended Instagram post needs --yes (owner approval of video, caption and time).")
        path, local = igschedule.install(a.id, a.lang, at, a.dry_run)
        ev("queued", "ig_dry_run" if a.dry_run else "publish", f"launchd job installed for {local:%a %d %b %H:%M} local", variant_id=variant, platform="instagram",
           detail={"job": path.name, "at": when}, log_ref=str(igschedule.LOGS / f"ig-{variant}.log"))
        print(f"{variant}: Instagram {'dry run ' if a.dry_run else ''}scheduled for {local:%a %d %b %H:%M} local ({path.name})")
        print("  the Mac must be on; if it is asleep then, the post goes out when it wakes")
        if not a.dry_run:
            mark(m, "instagram_scheduled", a.lang, note=when)
        return
    stage = "ig_dry_run" if a.dry_run else "publish"
    log_ref = str(igschedule.LOGS / f"ig-{variant}.log") if a.now and at else None
    if a.now and at and (now - at).total_seconds() > 24 * 3600:
        igschedule.remove(variant)
        msg = f"{variant}: scheduled time {when} is more than 24 h ago; not posting. Job removed."
        ev("warning", stage, "scheduled job fired over 24 h late; skipped", variant_id=variant, platform="instagram", status="Needs Attention", error=msg, log_ref=log_ref)
        sys.exit(msg)
    if a.now and at:
        late = (now - at).total_seconds()
        ev("info", stage, f"scheduled job fired" + (f" ({late / 60:.0f} min late)" if late > 300 else ""), variant_id=variant, platform="instagram", detail={"at": when, "late_s": round(late)}, log_ref=log_ref)
    args = [sys.executable, str(ROOT / "publish.py"), "instagram", str(video), "--meta", str(meta), "--thumbnail", str(thumb), "--variant", variant, "--slot", a.slot or sched.get("slot", "")]
    if a.dry_run:
        args.append("--dry-run")
    if a.yes:
        args.append("--yes")
    print(f"{variant}: Instagram {'dry run' if a.dry_run else 'publish'} starting {now.astimezone():%Y-%m-%d %H:%M:%S}", flush=True)
    for attempt in range(4):
        r = subprocess.run(args, cwd=ROOT)
        if r.returncode != 75 or attempt == 3:
            break
        ev("warning", stage, f"temporary link failed; retrying in 2 min (attempt {attempt + 2} of 4)", variant_id=variant, platform="instagram", log_ref=log_ref)
        print(f"  tunnel failed; retrying in 2 min (attempt {attempt + 2} of 4)", flush=True)
        time.sleep(120)
    if r.returncode == 75:
        ev("failed", stage, "temporary link failed 4 times; not posted", variant_id=variant, platform="instagram", error="exit 75: tunnel failed after 4 attempts", log_ref=log_ref)
    if r.returncode == 0:
        igschedule.remove(variant)
        if not a.dry_run:
            mark(m, "published_instagram", a.lang, note=now.isoformat())
            from . import lint

            lint.log_features(m, a.lang, "publish")
    sys.exit(r.returncode)


def cmd_cleanup(a):
    from . import cleanup

    tiers = ["safe"] + (["models"] if a.models else []) + (["tools"] if a.tools else [])
    before = cleanup.free_gb()
    items = cleanup.plan(tiers)
    total = cleanup.report(items)
    print(f"\nFree now: {before:.1f} GB. Reclaimable: {total / 1e9:.2f} GB ({', '.join(tiers)}).")
    print("Never touched: final videos, thumbnails, scripts, voice takes, scene images, approvals, database, secrets, models/ (local 4-bit image model).")
    if not items or not a.apply:
        print("Preview only. Add --apply to delete (log: data/cleanup_log.jsonl with restore commands).")
        return
    if not a.yes and input(f"Delete {len(items)} items ({total / 1e9:.2f} GB)? Type 'yes': ").strip() != "yes":
        sys.exit("Cancelled.")
    freed = cleanup.apply(items)
    print(f"Freed {freed / 1e9:.2f} GB. Free now: {cleanup.free_gb():.1f} GB.")


def cmd_ig_jobs(a):
    from . import igschedule

    rows = igschedule.jobs()
    if not rows:
        print("no scheduled Instagram posts")
    for r in rows:
        print(f"{r['variant']:<12} {r['when']}{'  (dry run)' if r['dry_run'] else ''}  log: {r['log']}")


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


def cmd_retention_csv(a):
    import csv
    from . import analytics

    with db.connect() as con:
        pub = con.execute("SELECT id FROM publications WHERE variant_id=? ORDER BY id DESC LIMIT 1", (a.variant,)).fetchone()
        m = analytics.latest(con, pub["id"]) if pub else None
    curve = (m or {}).get("retention")
    if not isinstance(curve, list) or not curve:
        sys.exit(f"No retention curve yet for {a.variant} (needs an analytics snapshot; data lags 1-3 days).")
    out = DATA / "reports" / f"retention-{a.variant}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["position_percent", "audience_percent"])
        for r in sorted(curve, key=lambda r: float(r["elapsedVideoTimeRatio"])):
            w.writerow([round(float(r["elapsedVideoTimeRatio"]) * 100, 1), round(float(r["audienceWatchRatio"]) * 100, 1)])
    print(out)
    print(f"Analyse with: python3 -I .claude/skills/yt-retention/retention.py {out}")


def cmd_voicepack(a):
    from . import voicepack

    lines = [l.strip() for l in Path(a.lines).read_text().splitlines() if l.strip()]
    voicepack.build(a.out, lines, a.voices.split(","), a.lang)
    print(f"Listening pack: {a.out}/README.md")


def cmd_link(a):
    with db.connect() as con:
        con.execute("INSERT OR REPLACE INTO publications (variant_id, platform, platform_id, url, privacy, scheduled_for, published_at, slot, metadata, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (a.variant, "youtube", a.video_id, f"https://www.youtube.com/shorts/{a.video_id}", "public", None, a.published_at, a.slot, None, db.now()))
    print(f"linked {a.variant} -> {a.video_id}")


def cmd_analytics(a):
    from . import analytics

    if a.install_daily or a.print_daily:
        spec, cmds, ok = analytics.install_daily(dry_run=a.print_daily)
        print(f"LaunchAgent {analytics.AGENT_LABEL}: {' '.join(spec['ProgramArguments'])} daily at {analytics.DAILY_AT[0]:02d}:{analytics.DAILY_AT[1]:02d} local (read-only analytics; never publishes)")
        print(f"  plist: {analytics.AGENT_PLIST}\n  log:   {spec['StandardOutPath']}")
        print("  installed and loaded" if ok else "  not installed; to install run:\n    python -m pipeline analytics --install-daily")
        return
    if a.uninstall_daily:
        print("removed" if analytics.uninstall_daily() else "no daily job was installed")
        return
    if a.relabel:
        for c in analytics.relabel(dry_run=a.dry_run):
            print(f"snapshot #{c['id']} pub {c['publication_id']}: {c['old']} -> {c['new']} (age {c['age_h']} h, captured {c['captured_at']}, published {c['published_ref']})")
        print("dry run: nothing written" if a.dry_run else "relabelled")
        return
    platforms = (a.platform,) if a.platform else ("youtube", "instagram")
    if a.dry_run:
        with db.connect() as con:
            for p, lab, t0 in analytics.due(con, a.force, platforms):
                print(f"due {p['variant_id']} {p['platform']} {lab} (published {t0.isoformat()})")
        return
    done, errors = analytics.snapshot_due(force=a.force, label_override=a.label, platforms=platforms)
    for v, plat, lab, views in done:
        print(f"snapshot {v} {plat} {lab}: views={views}")
    for v, plat, err in errors:
        print(f"error {v} {plat}: {err}")
    if not done and not errors:
        print("no snapshots due")
    if a.insights:
        cmd_insights(argparse.Namespace(days=None, quiet=True))


def cmd_insights(a):
    from . import insights

    path, text, d = insights.run(days=a.days)
    if not getattr(a, "quiet", False):
        print(text)
    else:
        print(f"insights: {len(d['findings'])} findings, {len(d['actions'])} carry-forward actions")
    if d["stale"]:
        print(f"note: last snapshot {d['last_snapshot_age_h']} h ago; run `python -m pipeline analytics` for fresh data")
    print(f"written: {path}\nwritten: {insights.LATEST}")


def cmd_report(a):
    if a.weekly:
        from . import report

        path, text = report.weekly(write=True)
        print(text)
        print(f"written: {path}")
        return
    if not a.variant:
        sys.exit("report needs a variant (e.g. C0002-hi) or --weekly")
    from . import analytics

    text = analytics.report(a.variant)
    out = DATA / "reports" / f"performance-{a.variant}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(text)


def cmd_experiment(a):
    from . import learn

    if a.action in ("start", "close") and not a.exp_id:
        sys.exit(f"experiment {a.action} needs the experiment id")
    with db.connect() as con:
        if a.action == "add":
            if a.exp1:
                spec = learn.EXP1
            else:
                missing = [k for k in ("hypothesis", "variable", "arms", "metric", "stop_rule") if not getattr(a, k)]
                if missing:
                    sys.exit("experiment add needs --" + ", --".join(m.replace("_", "-") for m in missing) + " (or --exp1)")
                arms = a.arms.split(",")
                if len(arms) != 2:
                    sys.exit("--arms takes exactly two names, e.g. A,B")
                rule = {"type": "parity", "odd": arms[0], "even": arms[1]}
                spec = {"name": a.name, "hypothesis": a.hypothesis, "variable": a.variable, "arms": arms, "assignment_rule": rule, "metric": a.metric,
                        "min_n_per_arm": max(learn.MIN_N, a.min_n), "stop_rule": a.stop_rule, "design": "alternating arms by odd/even episode across all languages"}
            try:
                eid = learn.ensure_exp1(con) if a.exp1 and not a.start else learn.add(con, spec, start=a.start)
            except ValueError as e:
                sys.exit(str(e))
            print(f"experiment #{eid} registered ({'active' if a.start else 'planned'})")
        elif a.action == "start":
            try:
                learn.start(con, a.exp_id)
            except ValueError as e:
                sys.exit(str(e))
            print(f"experiment #{a.exp_id} active; slots are frozen while a content experiment is active")
        elif a.action == "close":
            if not a.result:
                sys.exit("experiment close needs --result (what was concluded, with the evidence tier)")
            learn.close(con, a.exp_id, a.result)
            print(f"experiment #{a.exp_id} closed")
        rows = [learn.as_dict(r) for r in learn.all_experiments(con)]
    if a.action == "list":
        if not rows:
            print("no experiments")
        for e in rows:
            win = learn.metric_window(e)
            ev = learn.evaluate(e, learn.rows_for(win))
            n = {l: r["n"] for l, r in ev["languages"].items()}
            print(f"#{e['id']} [{e['status']}] {e.get('name') or e['variable']}: arms {e['arms']} · metric window {win} · n per arm {n or 'none yet'} · {ev['overall']}")


def cmd_events(a):
    from . import backfill, monitor

    if a.backfill:
        res = backfill.run(force=a.force)
        if res["skipped"]:
            print(f"backfill already done ({res['existing']} backfilled events); pass --force to add them again")
        else:
            print(f"backfilled events by source: {json.dumps(res['events'])}; failed to write: {res['failed']}")
            print(f"issues by status: {json.dumps(res['issues'])}; dry-run tunnel issues settled: {res['settled']}")
        return
    with db.connect() as con:
        rows = monitor.timeline(con, a.video, a.since, a.project, a.limit, a.kind.split(",") if a.kind else None)
    if not rows:
        print("no events")
    for r in rows:
        print(monitor.fmt_event(r))


def cmd_issues(a):
    from . import monitor

    with db.connect() as con:
        rows = monitor.issues(con, only_open=a.open)
    if not rows:
        print("no open issues" if a.open else "no issues")
    for r in rows:
        print(monitor.fmt_issue(r, full=a.full or a.open))


def cmd_issue(a):
    from . import monitor

    with db.connect() as con:
        if a.action == "show":
            r = con.execute("SELECT * FROM issues WHERE id=?", (a.issue_id,)).fetchone()
            if not r:
                sys.exit(f"no issue #{a.issue_id}")
            print(monitor.fmt_issue(r, full=True))
            return
        r = monitor.resolve_issue(con, a.issue_id, a.note, "resolved" if a.action == "resolve" else "acknowledged")
    if not r:
        sys.exit(f"no issue #{a.issue_id}")
    print(f"issue #{a.issue_id} {'resolved' if a.action == 'resolve' else 'acknowledged'}: {r['title']}")


def cmd_projects(a):
    from . import monitor

    with db.connect() as con:
        if a.action == "add":
            if not a.slug or not a.name:
                sys.exit("projects add <slug> --name '...' [--languages en,hi] [--description] [--objective] [--workflow stage1,stage2]")
            monitor.add_project(con, a.slug, a.name, a.languages.split(",") if a.languages else [], a.description, a.objective, a.workflow.split(",") if a.workflow else None)
            print(f"project {a.slug} saved")
            return
        if a.action in ("set-goal", "milestones", "set-milestones"):
            from . import episodes

            if not a.slug:
                sys.exit(f"projects {a.action} <slug>")
            cfg = episodes.get_config(con, a.slug)
            if cfg is None:
                sys.exit(f"no project {a.slug}")
            if a.action == "set-goal":
                if not a.episodes or a.episodes < 1:
                    sys.exit("projects set-goal <slug> --episodes N (N >= 1)")
                cfg = episodes.update_config(con, a.slug, goal_episodes=a.episodes)
            elif a.action == "set-milestones":
                if not a.file:
                    sys.exit("projects set-milestones <slug> --file plan.json (a list, or an object with milestones, goal_episodes and note)")
                data = json.loads(Path(a.file).read_text())
                body = data if isinstance(data, dict) else {"milestones": data}
                try:
                    episodes.valid_milestones(body.get("milestones"))
                except ValueError as ex:
                    sys.exit(str(ex))
                cfg = episodes.update_config(con, a.slug, milestones=body["milestones"], **{k: body[k] for k in ("goal_episodes", "note") if k in body})
            print(episodes.fmt_plan(a.slug, cfg))
            return
        rows = monitor.projects(con)
    if not rows:
        print("no projects")
    for r in rows:
        langs = ",".join(json.loads(r["languages"] or "[]"))
        print(f"{r['id']:12s} {r['status']:8s} {r['videos']:3d} videos  langs {langs or '-':16s} {r['name']}")


def cmd_overview(a):
    from . import monitor

    with db.connect() as con:
        o = monitor.overview(con)
    print(json.dumps(o, indent=2, ensure_ascii=False, default=str) if a.json else monitor.fmt_overview(o))


def cmd_telegram(a):
    import os

    from . import notify, service

    if a.action == "setup":
        token = sys.stdin.readline().strip() if a.token_from_stdin else os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            sys.exit("Give the token on stdin (--token-from-stdin) or in TELEGRAM_BOT_TOKEN. It is never printed.")
        try:
            me = notify.setup(token)
        except ValueError as e:
            sys.exit(str(e))
        except notify.TelegramError as e:
            sys.exit(f"Telegram rejected the token: {e}")
        print(f"Saved secrets/telegram.json (mode 600) for bot @{me.get('username')}. Next: python -m pipeline telegram pair")
    elif a.action == "pair":
        cfg = notify.pair_cli(a.minutes, bot_running=service.running("bot"))
        print(f"Paired with chat {cfg['owner_chat_id']}. Other chats are ignored.")
    elif a.action == "status":
        cfg = notify.load_config()
        has, paired = notify.configured(cfg)
        print(f"token: {'set' if has else 'missing'} (bot @{cfg.get('bot_username') or '?'}) · paired: {'yes, chat ' + str(cfg['owner_chat_id']) if paired else 'no'}")
        print(f"outbox: {json.dumps(notify.counts())}")
        print(service.fmt(service.state("bot")))
    elif a.action == "test":
        cfg = notify.load_config()
        if not notify.configured(cfg)[1]:
            sys.exit("Not set up or not paired yet.")
        notify.Telegram(cfg["bot_token"]).send(cfg["owner_chat_id"], "✅ Test message from shorts-studio on the Mac.")
        print("sent")
    elif a.action == "drain":
        cfg = notify.load_config()
        if not notify.configured(cfg)[1]:
            sys.exit("Not set up or not paired yet.")
        if service.running("bot"):
            sys.exit("The bot service is running and drains the outbox itself.")
        print(f"sent {notify.drain(notify.Telegram(cfg['bot_token']), cfg['owner_chat_id'])} message(s)")


def cmd_bot(a):
    from . import bot

    bot.run()


def cmd_dashboard(a):
    from . import dashboard, notify

    if a.action == "run":
        dashboard.run(a.port, tunnel=a.with_tunnel)
    elif a.action == "tunnel":
        dashboard.run_tunnel(a.port)
    elif a.action == "rotate-key":
        dashboard.rotate_key()
        print("New login key and cookie secret saved in secrets/dashboard.json; every phone must sign in again.")
        msg = dashboard.link_message("key rotated, sign in again")
        if msg:
            notify.enqueue_local("Dashboard link", msg, secret=True)
            print("The new sign-in link is queued for Telegram.")
    elif a.action == "link":
        info = dashboard.read_url()
        print(f"address: {info.get('url') or 'none yet'} (since {info.get('since') or '-'}, checked {info.get('checked_at') or '-'})")
        if a.show:
            print(dashboard.login_link() or "no tunnel address yet")
        else:
            msg = dashboard.link_message("sent from the Mac")
            if msg:
                notify.enqueue_local("Dashboard link", msg, secret=True)
                print("Sign-in link queued for Telegram (use --show to print it here instead).")


def cmd_service(a):
    from . import service

    names = a.names or None
    bad = [n for n in (names or []) if n not in service.SERVICES]
    if bad:
        sys.exit(f"unknown service(s): {', '.join(bad)} (choose from {', '.join(service.SERVICES)})")
    if a.action == "install":
        service.install(names, restart=a.restart)
    elif a.action == "restart":
        if not names:
            sys.exit("Name the services to restart, e.g. dashboard (restarting tunnel changes the address)")
        service.restart(names)
    elif a.action == "remove":
        if not names:
            sys.exit("Name the services to remove: queue, bot, dashboard, tunnel")
        service.remove(names)
    for st in service.status(names):
        print(service.fmt(st))


def main():
    ap = argparse.ArgumentParser(prog="python -m pipeline", description="shorts-studio orchestration: research → script → production → QA → publish → analytics")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("new"); p.add_argument("--topic", required=True); p.add_argument("--series"); p.add_argument("--episode", type=int); p.add_argument("--category", default="mythology"); p.add_argument("--style", default="chalk"); p.add_argument("--langs", default="en,hi"); p.set_defaults(fn=cmd_new)
    p = sp.add_parser("status"); p.add_argument("id", nargs="?"); p.set_defaults(fn=cmd_status)
    p = sp.add_parser("trending"); p.add_argument("--region", default="IN"); p.set_defaults(fn=cmd_trending)
    p = sp.add_parser("research"); p.add_argument("id"); p.add_argument("--query", required=True, help='string, or JSON {"en": "...", "hi": "..."}'); p.add_argument("--wiki", required=True, help="English Wikipedia title"); p.add_argument("--langs", default="en,hi"); p.set_defaults(fn=cmd_research)
    p = sp.add_parser("approve", help="OWNER ONLY: record a gate approval bound to file hashes (interactive; --yes needs STUDIO_OWNER_APPROVED=<ID>)"); p.add_argument("id"); p.add_argument("gate", choices=list(GATES)); p.add_argument("--langs", required=True); p.add_argument("--platform", choices=list(gates.PLATFORMS)); p.add_argument("--at", help="publish: ISO time for all langs, or lang=ISO,lang=ISO; 'now' for immediate"); p.add_argument("--note", default=""); p.add_argument("--by", default="owner"); p.add_argument("--channel", help="chat, telegram, terminal …"); p.add_argument("--nonce"); p.add_argument("--yes", action="store_true"); p.set_defaults(fn=cmd_approve)
    p = sp.add_parser("reject", help="record a gate rejection (blocks the gate for those langs)"); p.add_argument("id"); p.add_argument("gate", choices=list(GATES)); p.add_argument("--platform", choices=list(gates.PLATFORMS)); p.add_argument("--langs"); p.add_argument("--note", required=True); p.add_argument("--by", default="owner"); p.add_argument("--channel"); p.set_defaults(fn=cmd_reject)
    p = sp.add_parser("waive", help="OWNER ONLY: waive one auto-warn QA check for the current video"); p.add_argument("id"); p.add_argument("--lang", required=True); p.add_argument("--check", required=True, help="check name, or all-warnings to waive every non-reject failure of the current QA report"); p.add_argument("--note", required=True); p.add_argument("--by", default="owner"); p.add_argument("--channel"); p.add_argument("--yes", action="store_true"); p.set_defaults(fn=cmd_waive)
    p = sp.add_parser("lint", help="pre-G1 script lint: duration estimate, hook, scenes, digits, sources, quotes, parity"); p.add_argument("id", nargs="?"); p.add_argument("--lang"); p.add_argument("--calibrate", action="store_true", help="recompute speech rates from existing renders into data/lint_rates.json"); p.set_defaults(fn=cmd_lint)
    p = sp.add_parser("migrate-gates", help="convert legacy gate:publish into per-platform, hash-bound records (evidence only)"); p.add_argument("id", nargs="?"); p.add_argument("--dry-run", action="store_true"); p.set_defaults(fn=cmd_migrate_gates)
    p = sp.add_parser("hooks", help="load <lang>/hooks.json into the hooks table"); p.add_argument("id"); p.add_argument("--lang"); p.set_defaults(fn=cmd_hooks)
    p = sp.add_parser("features", help="(re)write the features row per variant; --all backfills every content piece"); p.add_argument("id", nargs="?"); p.add_argument("--lang"); p.add_argument("--stage", default="manual"); p.add_argument("--all", action="store_true"); p.set_defaults(fn=cmd_features)
    p = sp.add_parser("publish-queue", help="persisted YouTube upload queue: add, list, remove, run (daily cap, backoff, exact approved times)"); p.add_argument("action", choices=["add", "list", "remove", "run"]); p.add_argument("id", nargs="?"); p.add_argument("--langs"); p.add_argument("--platform", default="youtube", choices=["youtube"]); p.add_argument("--priority", type=int, default=0); p.add_argument("--cap", type=int); p.add_argument("--dry-run", action="store_true"); p.add_argument("--once", action="store_true"); p.set_defaults(fn=cmd_publish_queue)
    p = sp.add_parser("done"); p.add_argument("id"); p.add_argument("stage"); p.add_argument("--lang"); p.add_argument("--note"); p.set_defaults(fn=cmd_done)
    p = sp.add_parser("cleanup", help="free disk: reproducible intermediates (default), unused model caches (--models), tool caches (--tools); preview unless --apply"); p.add_argument("--models", action="store_true"); p.add_argument("--tools", action="store_true"); p.add_argument("--apply", action="store_true"); p.add_argument("--yes", action="store_true"); p.set_defaults(fn=cmd_cleanup)
    p = sp.add_parser("produce"); p.add_argument("id"); p.add_argument("--lang", required=True); p.add_argument("--steps", default="voice,images,render"); p.set_defaults(fn=cmd_produce)
    p = sp.add_parser("qa"); p.add_argument("id"); p.add_argument("--lang", required=True); p.add_argument("--audio-only", action="store_true", help="voice QA on the scene WAVs before render (marks voice_qa)"); p.set_defaults(fn=cmd_qa)
    p = sp.add_parser("schedule"); p.add_argument("--id"); p.add_argument("--lang", required=True); p.set_defaults(fn=cmd_schedule)
    p = sp.add_parser("publish"); p.add_argument("id"); p.add_argument("--lang", required=True); p.add_argument("--at"); p.add_argument("--slot"); p.add_argument("--yes", action="store_true", help="owner already approved in chat; skip the interactive prompt"); p.add_argument("--platform", default="youtube", choices=["youtube", "instagram"]); p.add_argument("--now", action="store_true", help="instagram: post immediately instead of scheduling"); p.add_argument("--dry-run", action="store_true", help="instagram: check token, tunnel and limits without posting"); p.add_argument("--cancel", action="store_true", help="instagram: remove a scheduled post"); p.add_argument("--check-gates-only", action="store_true", help="verify the G2/G3 records, times and hashes; no tunnel, no upload"); p.set_defaults(fn=cmd_publish)
    p = sp.add_parser("ig-jobs"); p.set_defaults(fn=cmd_ig_jobs)
    p = sp.add_parser("takes"); p.add_argument("id"); p.add_argument("--lang", required=True); p.add_argument("--scenes", help="comma list of 1-based scene numbers (default all)"); p.add_argument("--n", type=int, default=3); p.set_defaults(fn=cmd_takes)
    p = sp.add_parser("progress", help="live progress, per-step ETA and finish time"); p.add_argument("id"); p.add_argument("--watch", type=int, default=0, help="refresh every N seconds until done"); p.add_argument("--oneline", action="store_true"); p.set_defaults(fn=cmd_progress)
    p = sp.add_parser("retention-csv", help="export API retention curve for .claude/skills/yt-retention"); p.add_argument("variant"); p.set_defaults(fn=cmd_retention_csv)
    p = sp.add_parser("voicepack", help="render the same lines with several voices for an A/B listening test"); p.add_argument("--lines", required=True); p.add_argument("--voices", required=True, help="e.g. veena:kavya,maya2:Malini,svara:'Hindi (Female)'"); p.add_argument("--lang", default="hi"); p.add_argument("--out", required=True); p.set_defaults(fn=cmd_voicepack)
    p = sp.add_parser("link"); p.add_argument("--variant", required=True); p.add_argument("--video-id", required=True); p.add_argument("--published-at", required=True); p.add_argument("--slot"); p.set_defaults(fn=cmd_link)
    p = sp.add_parser("analytics", help="read-only YouTube + Instagram snapshots at 24h/48h/7d/14d/30d (±12 h), else age_<n>h"); p.add_argument("--force", action="store_true", help="snapshot every publication now"); p.add_argument("--label", help="override the computed label (avoid; labels come from age_h)"); p.add_argument("--platform", choices=["youtube", "instagram"]); p.add_argument("--dry-run", action="store_true", help="list what is due / preview --relabel"); p.add_argument("--relabel", action="store_true", help="recompute labels of existing snapshots from age_h"); p.add_argument("--install-daily", action="store_true", help="install the daily read-only LaunchAgent"); p.add_argument("--print-daily", action="store_true", help="show the LaunchAgent without installing"); p.add_argument("--uninstall-daily", action="store_true"); p.add_argument("--insights", action="store_true", help="also run `insights` after the snapshots (used by the daily job)"); p.set_defaults(fn=cmd_analytics)
    p = sp.add_parser("insights", help="analytics checkup → findings with evidence tiers → carry-forward script actions (data/reports/insights-<date>.md, latest_insights.json)"); p.add_argument("--days", type=int, help="only publications from the last N days"); p.set_defaults(fn=cmd_insights)
    p = sp.add_parser("report", help="per-variant performance report, or --weekly → data/reports/weekly-<date>.md"); p.add_argument("variant", nargs="?"); p.add_argument("--weekly", action="store_true"); p.set_defaults(fn=cmd_report)
    p = sp.add_parser("experiment", help="pre-registered experiments: add | list | start | close (one active at a time; ≥6 per arm per language)"); p.add_argument("action", choices=["add", "list", "start", "close"]); p.add_argument("exp_id", nargs="?", type=int); p.add_argument("--exp1", action="store_true", help="register experiment 1 (duration, observational before/after)"); p.add_argument("--name"); p.add_argument("--hypothesis"); p.add_argument("--variable"); p.add_argument("--arms", help="two arm names A,B; odd episodes get A, even get B"); p.add_argument("--metric", help="e.g. '7d views / language rolling median'"); p.add_argument("--min-n", type=int, default=6); p.add_argument("--stop-rule"); p.add_argument("--start", action="store_true", help="activate immediately (fails if another is active)"); p.add_argument("--result"); p.set_defaults(fn=cmd_experiment)
    p = sp.add_parser("events", help="event timeline (newest last); --backfill derives history once from runs, QA, decisions, publications, queue and logs"); p.add_argument("--video", help="variant (C0006-hi) or content id (C0006)"); p.add_argument("--since", type=float, help="hours back"); p.add_argument("--project"); p.add_argument("--kind", help="comma list, e.g. failed,unknown_outcome"); p.add_argument("--limit", type=int, default=200); p.add_argument("--backfill", action="store_true"); p.add_argument("--force", action="store_true"); p.set_defaults(fn=cmd_events)
    p = sp.add_parser("issues", help="problems with plain-language explanation, suggestion and retry safety"); p.add_argument("--open", action="store_true"); p.add_argument("--full", action="store_true"); p.set_defaults(fn=cmd_issues)
    p = sp.add_parser("issue", help="issue show|resolve|ack <id>"); p.add_argument("action", choices=["show", "resolve", "ack"]); p.add_argument("issue_id", type=int); p.add_argument("--note"); p.set_defaults(fn=cmd_issue)
    p = sp.add_parser("projects", help="list projects; add <slug> --name ...; set-goal <slug> --episodes N; milestones <slug>; set-milestones <slug> --file plan.json"); p.add_argument("action", nargs="?", choices=["list", "add", "set-goal", "milestones", "set-milestones"], default="list"); p.add_argument("slug", nargs="?"); p.add_argument("--name"); p.add_argument("--episodes", type=int, help="set-goal: total episodes planned"); p.add_argument("--file", help="set-milestones: JSON file with the milestone list"); p.add_argument("--languages"); p.add_argument("--description"); p.add_argument("--objective"); p.add_argument("--workflow", help="comma list of stage names in order"); p.set_defaults(fn=cmd_projects)
    p = sp.add_parser("overview", help="workspace counts from the database and manifests (no estimates)"); p.add_argument("--json", action="store_true"); p.set_defaults(fn=cmd_overview)
    p = sp.add_parser("telegram", help="private Telegram bot: setup (token from stdin or TELEGRAM_BOT_TOKEN), pair, status, test, drain"); p.add_argument("action", choices=["setup", "pair", "status", "test", "drain"]); p.add_argument("--token-from-stdin", action="store_true"); p.add_argument("--minutes", type=int, default=10); p.set_defaults(fn=cmd_telegram)
    p = sp.add_parser("bot", help="run the Telegram bot daemon (launchd com.shortsstudio.bot)"); p.add_argument("action", choices=["run"]); p.set_defaults(fn=cmd_bot)
    p = sp.add_parser("dashboard", help="read-only mobile dashboard: run (web server on 127.0.0.1), tunnel (quick tunnel, separate so web restarts keep the address), rotate-key, link"); p.add_argument("action", choices=["run", "tunnel", "rotate-key", "link"]); p.add_argument("--port", type=int, default=8765); p.add_argument("--with-tunnel", action="store_true", help="run: also start the tunnel in this process"); p.add_argument("--no-tunnel", action="store_true", help=argparse.SUPPRESS); p.add_argument("--show", action="store_true", help="link: print the secret sign-in link in this terminal"); p.set_defaults(fn=cmd_dashboard)
    p = sp.add_parser("service", help="launchd services queue, bot, dashboard, tunnel: install|restart|remove|status [names]"); p.add_argument("action", choices=["install", "restart", "remove", "status"]); p.add_argument("names", nargs="*", help="queue, bot, dashboard, tunnel (install default: bot dashboard tunnel)"); p.add_argument("--restart", action="store_true", help="rewrite and restart even if loaded (needed to touch the queue)"); p.set_defaults(fn=cmd_service)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
