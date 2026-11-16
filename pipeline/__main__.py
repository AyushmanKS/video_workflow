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
    m = {"id": cid, "series": a.series, "episode": a.episode, "topic": a.topic, "category": a.category, "style": a.style, "languages": langs, "primary_language": langs[0], "stages": {}}
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
    c = names.get(a.check)
    if not c:
        sys.exit(f"{variant}: no check named '{a.check}' in QA report #{rep['id']} ({', '.join(names)})")
    if c.get("class") == "reject" and not c["ok"]:
        sys.exit(f"{variant}: '{a.check}' is an auto-reject check; it cannot be waived — fix it")
    owner_confirm(a, a.id, [f"Waive {a.check} for {variant} (QA #{rep['id']}, video {sha[:12]}): {a.note}", *[f"  - {i}" for i in c["issues"]]], [variant])
    with db.connect() as con:
        con.execute("INSERT INTO waivers (variant_id, check_name, mp4_sha256, note, actor, channel, created_at) VALUES (?,?,?,?,?,?,?)", (variant, a.check, sha, a.note, a.by, a.channel or "terminal", db.now()))
        db.log_decision(con, "waiver", a.check, a.note, "human", content_id=a.id, variant_id=variant, actor=a.by, channel=a.channel or "terminal", artifact_sha256=sha)
    print(f"{variant}: waiver recorded for {a.check}")


def cmd_done(a):
    if a.stage in PROTECTED_STAGES or a.stage.startswith("gate:"):
        sys.exit(f"'{a.stage}' cannot be marked done by hand: run python -m pipeline qa (it records the verdict), or use approve for gates.")
    m = load(a.id)
    mark(m, a.stage, a.lang, note=a.note)
    print(f"{a.id}: {a.stage}{':' + a.lang if a.lang else ''} done")
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
        lint.log_features(m, a.lang, "render")
    from . import progress as _pg

    _pg.learn_from(a.id)


def cmd_qa(a):
    from . import qa

    m = load(a.id)
    work = CONTENT / a.id / a.lang
    video = gates.variant_files(m, a.lang)["video"]
    stage = "voice_qa" if a.audio_only else "video_qa"
    with db.Run(stage, a.id, f"{a.id}-{a.lang}"):
        rep = qa.run(None if a.audio_only else video, work, work / "script.json", a.lang, f"{a.id}-{a.lang}", m["style"], audio_only=a.audio_only)
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
        print(f"{variant}: Instagram {'dry run ' if a.dry_run else ''}scheduled for {local:%a %d %b %H:%M} local ({path.name})")
        print("  the Mac must be on; if it is asleep then, the post goes out when it wakes")
        if not a.dry_run:
            mark(m, "instagram_scheduled", a.lang, note=when)
        return
    if a.now and at and (now - at).total_seconds() > 24 * 3600:
        igschedule.remove(variant)
        sys.exit(f"{variant}: scheduled time {when} is more than 24 h ago; not posting. Job removed.")
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
        print(f"  tunnel failed; retrying in 2 min (attempt {attempt + 2} of 4)", flush=True)
        time.sleep(120)
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
    p = sp.add_parser("approve", help="OWNER ONLY: record a gate approval bound to file hashes (interactive; --yes needs STUDIO_OWNER_APPROVED=<ID>)"); p.add_argument("id"); p.add_argument("gate", choices=list(GATES)); p.add_argument("--langs", required=True); p.add_argument("--platform", choices=list(gates.PLATFORMS)); p.add_argument("--at", help="publish: ISO time for all langs, or lang=ISO,lang=ISO; 'now' for immediate"); p.add_argument("--note", default=""); p.add_argument("--by", default="owner"); p.add_argument("--channel", help="chat, telegram, terminal …"); p.add_argument("--nonce"); p.add_argument("--yes", action="store_true"); p.set_defaults(fn=cmd_approve)
    p = sp.add_parser("reject", help="record a gate rejection (blocks the gate for those langs)"); p.add_argument("id"); p.add_argument("gate", choices=list(GATES)); p.add_argument("--platform", choices=list(gates.PLATFORMS)); p.add_argument("--langs"); p.add_argument("--note", required=True); p.add_argument("--by", default="owner"); p.add_argument("--channel"); p.set_defaults(fn=cmd_reject)
    p = sp.add_parser("waive", help="OWNER ONLY: waive one auto-warn QA check for the current video"); p.add_argument("id"); p.add_argument("--lang", required=True); p.add_argument("--check", required=True); p.add_argument("--note", required=True); p.add_argument("--by", default="owner"); p.add_argument("--channel"); p.add_argument("--yes", action="store_true"); p.set_defaults(fn=cmd_waive)
    p = sp.add_parser("lint", help="pre-G1 script lint: duration estimate, hook, scenes, digits, sources, quotes, parity"); p.add_argument("id", nargs="?"); p.add_argument("--lang"); p.add_argument("--calibrate", action="store_true", help="recompute speech rates from existing renders into data/lint_rates.json"); p.set_defaults(fn=cmd_lint)
    p = sp.add_parser("migrate-gates", help="convert legacy gate:publish into per-platform, hash-bound records (evidence only)"); p.add_argument("id", nargs="?"); p.add_argument("--dry-run", action="store_true"); p.set_defaults(fn=cmd_migrate_gates)
    p = sp.add_parser("hooks", help="load <lang>/hooks.json into the hooks table"); p.add_argument("id"); p.add_argument("--lang"); p.set_defaults(fn=cmd_hooks)
    p = sp.add_parser("features", help="(re)write the features row per variant"); p.add_argument("id"); p.add_argument("--lang"); p.add_argument("--stage", default="manual"); p.set_defaults(fn=cmd_features)
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
    p = sp.add_parser("analytics"); p.add_argument("--force", action="store_true"); p.add_argument("--label"); p.set_defaults(fn=cmd_analytics)
    p = sp.add_parser("report"); p.add_argument("variant"); p.set_defaults(fn=cmd_report)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
