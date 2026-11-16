import hashlib
import json
import os
import plistlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import CONTENT, ROOT, db

PLATFORMS = ("youtube", "instagram")
SCRIPT = "gate:script"
FINAL = "gate:final"
LEGACY_PUBLISH = "gate:publish"
IST = timezone(timedelta(hours=5, minutes=30))
OWNER_ENV = "STUDIO_OWNER_APPROVED"
NOW = "now"
EARLY_TOLERANCE = timedelta(minutes=5)


def publish_key(platform):
    if platform not in PLATFORMS:
        raise ValueError(f"unknown platform {platform}")
    return f"gate:publish:{platform}"


def gate_key(gate, platform=None):
    if gate == "script":
        return SCRIPT
    if gate == "final":
        return FINAL
    if gate == "publish":
        if not platform:
            raise ValueError("publish gate needs a platform (youtube or instagram)")
        return publish_key(platform)
    raise ValueError(f"unknown gate {gate}")


def manifest_path(cid):
    return CONTENT / cid / "manifest.json"


def load(cid):
    p = manifest_path(cid)
    if not p.exists():
        raise FileNotFoundError(f"Unknown content id {cid}")
    return json.loads(p.read_text())


def save(m):
    manifest_path(m["id"]).write_text(json.dumps(m, indent=2, ensure_ascii=False))


def sha256(path):
    p = Path(path)
    if not p.exists():
        return None
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def script_sha256(path):
    p = Path(path)
    if not p.exists():
        return None
    data = json.loads(p.read_text())
    for k in ("style_overrides", "language"):
        data.pop(k, None)
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def meta_sha256(path, platform):
    p = Path(path)
    if not p.exists():
        return None
    section = json.loads(p.read_text()).get(platform)
    if section is None:
        return None
    return hashlib.sha256(json.dumps(section, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def rel(p):
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def variant_files(m, lang):
    work = CONTENT / m["id"] / lang
    video = work / f"{m['id']}-{lang}.mp4"
    meta = work / "publish.json"
    thumb = work / "thumbnail.png"
    legacy = False
    legacy_name = {"en": "english", "hi": "hindi"}.get(lang)
    if not video.exists() and m.get("legacy_folder") and legacy_name:
        final = ROOT / m["legacy_folder"] / "final"
        hits = sorted(final.glob(f"*-{legacy_name}.mp4"))
        if hits:
            stem = hits[0].stem
            video, thumb = final / f"{stem}.mp4", final / f"{stem}-thumbnail.png"
            legacy = True
            if not meta.exists():
                meta = final / f"publish-{legacy_name}.json"
    return {"work": work, "video": video, "meta": meta, "thumb": thumb, "script": work / "script.json", "legacy": legacy}


def parse_time(value):
    if value in (None, "", NOW):
        return None
    t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.tzinfo is None:
        t = t.replace(tzinfo=IST)
    return t


def ist_iso(value):
    t = parse_time(value)
    return t.astimezone(IST).isoformat() if t else value


def same_time(a, b):
    if a == NOW or b == NOW:
        return a == b
    ta, tb = parse_time(a), parse_time(b)
    return ta is not None and tb is not None and ta == tb


def entries(m, key):
    return m.get("stages", {}).get(key, {}).get("entries", {})


def approved_langs(m, key):
    return [l for l, e in entries(m, key).items() if e.get("status") == "approved"]


def summarize(rec):
    ok = [l for l, e in rec.get("entries", {}).items() if e.get("status") == "approved"]
    rec["langs"] = ok
    rec["status"] = "approved" if ok else ("rejected" if rec.get("entries") else "pending")
    return rec


def check_script(m, lang):
    key = SCRIPT
    e = entries(m, key).get(lang)
    if not e or e.get("status") != "approved":
        return [f"G1 (script) is not approved for {m['id']}-{lang}"]
    path = CONTENT / m["id"] / lang / "script.json"
    cur = script_sha256(path)
    if e.get("sha256") is None:
        return [] if cur is None and e.get("migrated_from_legacy") else [f"G1 record for {m['id']}-{lang} has no script hash; re-approve the script"]
    if cur != e["sha256"]:
        return [f"script.json for {m['id']}-{lang} changed after G1 (approved {e['sha256'][:12]}, now {(cur or 'missing')[:12]}); re-run lint and re-approve"]
    return []


def check_final(m, lang):
    e = entries(m, FINAL).get(lang)
    if not e or e.get("status") != "approved":
        return [f"G2 (final video) is not approved for {m['id']}-{lang}"]
    f = variant_files(m, lang)
    cur = sha256(f["video"])
    if not e.get("sha256"):
        return [f"G2 record for {m['id']}-{lang} has no video hash; re-approve"]
    if cur != e["sha256"]:
        return [f"video for {m['id']}-{lang} changed after G2 (approved {e['sha256'][:12]}, now {(cur or 'missing')[:12]}); re-run QA and re-approve G2"]
    return []


def check_publish(m, lang, platform, at=None, immediate=False, now=None):
    now = now or datetime.now(timezone.utc)
    key = publish_key(platform)
    problems = list(check_final(m, lang))
    e = entries(m, key).get(lang)
    if not e or e.get("status") != "approved":
        legacy = m.get("stages", {}).get(LEGACY_PUBLISH)
        hint = " (only a legacy gate:publish record exists; run python -m pipeline migrate-gates)" if legacy and not legacy.get("migrated") else ""
        return problems + [f"G3 ({platform}) is not approved for {m['id']}-{lang}{hint}"]
    f = variant_files(m, lang)
    if f["legacy"] and not e.get("migrated_from_legacy"):
        problems.append(f"{m['id']}-{lang}: legacy out/ file {rel(f['video'])} may not be uploaded to a new platform")
    vs, ms = sha256(f["video"]), meta_sha256(f["meta"], platform)
    if vs != e.get("video_sha256"):
        problems.append(f"{m['id']}-{lang}: video differs from the {platform} G3 approval (approved {str(e.get('video_sha256'))[:12]}, now {str(vs)[:12]})")
    if ms != e.get("meta_sha256"):
        problems.append(f"{m['id']}-{lang}: the '{platform}' section of publish.json differs from the G3 approval (approved {str(e.get('meta_sha256'))[:12]}, now {str(ms)[:12]})")
    approved = e.get("time")
    if approved == NOW:
        t = parse_time(at) if at else None
        base = parse_time(e.get("at"))
        if t and base and t < base - EARLY_TOLERANCE:
            problems.append(f"{m['id']}-{lang}: requested time {at} is before the approval itself")
    else:
        if at and not same_time(at, approved):
            problems.append(f"{m['id']}-{lang}: time {at} differs from the approved {platform} time {approved}")
        if not at and not immediate:
            problems.append(f"{m['id']}-{lang}: no publish time given; approved {platform} time is {approved}")
        t = parse_time(approved)
        if immediate and t and now < t - EARLY_TOLERANCE:
            problems.append(f"{m['id']}-{lang}: approved {platform} time {approved} has not arrived; not posting early")
    return problems


def approved_time(m, lang, platform):
    e = entries(m, publish_key(platform)).get(lang) or {}
    return e.get("time") if e.get("status") == "approved" else None


def latest_qa(con, variant):
    r = con.execute("SELECT id, verdict, report, mp4_sha256, created_at FROM qa_reports WHERE variant_id=? AND kind='automated' ORDER BY id DESC LIMIT 1", (variant,)).fetchone()
    if not r:
        return None
    return {"id": r["id"], "verdict": r["verdict"], "report": json.loads(r["report"]), "mp4_sha256": r["mp4_sha256"], "created_at": r["created_at"]}


def waivers(con, variant, mp4_sha):
    rows = con.execute("SELECT check_name, note, actor FROM waivers WHERE variant_id=? AND mp4_sha256=?", (variant, mp4_sha)).fetchall()
    return {r["check_name"]: dict(r) for r in rows}


def qa_status(m, lang, con=None):
    variant = f"{m['id']}-{lang}"
    cur = sha256(variant_files(m, lang)["video"])
    own = con is None
    con_cm = db.connect() if own else None
    con = con_cm.__enter__() if own else con
    try:
        rep = latest_qa(con, variant)
        if not rep:
            return False, [f"{variant}: no QA report; run python -m pipeline qa {m['id']} --lang {lang}"], None
        if not rep["mp4_sha256"]:
            return False, [f"{variant}: latest QA report (#{rep['id']}) predates file binding; re-run pipeline qa"], rep["id"]
        if rep["mp4_sha256"] != cur:
            return False, [f"{variant}: latest QA report (#{rep['id']}) was run on a different file; re-run pipeline qa"], rep["id"]
        if rep["verdict"] == "pass":
            return True, [], rep["id"]
        bad = [c for c in rep["report"]["checks"] if not c.get("ok") and not c.get("skipped")]
        rejects = [c["name"] for c in bad if c.get("class") == "reject"]
        if rep["verdict"] == "fail" or rejects:
            return False, [f"{variant}: QA verdict FAIL (#{rep['id']}): " + ", ".join(rejects or [c["name"] for c in bad])], rep["id"]
        w = waivers(con, variant, cur)
        missing = [c["name"] for c in bad if c["name"] not in w]
        if missing:
            return False, [f"{variant}: QA verdict WARN (#{rep['id']}) with unwaived checks: {', '.join(missing)} (python -m pipeline waive {m['id']} --lang {lang} --check NAME --note ...)"], rep["id"]
        return True, [], rep["id"]
    finally:
        if own:
            con_cm.__exit__(None, None, None)


def owner_env_ok(cid):
    return os.environ.get(OWNER_ENV) == cid


def new_record():
    return {"status": "pending", "langs": [], "entries": {}, "history": []}


def record(m, key, lang, entry):
    rec = m["stages"].get(key)
    if not rec or "entries" not in rec:
        rec = {**new_record(), **({"legacy": rec} if rec else {})}
    old = rec["entries"].get(lang)
    if old:
        rec["history"].append({"lang": lang, **old})
    rec["entries"][lang] = entry
    rec["at"] = entry["at"]
    rec["note"] = entry.get("note", "")
    m["stages"][key] = summarize(rec)
    return rec


def build_entry(m, gate, lang, platform=None, time=None, by="owner", channel="terminal", note="", nonce=None, qa_report=None):
    f = variant_files(m, lang)
    e = {"status": "approved", "at": db.now(), "by": by, "channel": channel, "note": note or ""}
    if nonce:
        e["nonce"] = nonce
    if gate == "script":
        e["sha256"] = script_sha256(f["script"])
        e["file"] = rel(f["script"])
    elif gate == "final":
        e["sha256"] = sha256(f["video"])
        e["file"] = rel(f["video"])
        if qa_report:
            e["qa_report_id"] = qa_report
    else:
        e.update({"platform": platform, "time": time, "video": rel(f["video"]), "video_sha256": sha256(f["video"]), "meta": rel(f["meta"]), "meta_sha256": meta_sha256(f["meta"], platform), "meta_hash_scope": f"publish.json['{platform}']"})
    return e


def reject(m, key, langs, note, by, channel):
    rec = m["stages"].get(key)
    if not rec or "entries" not in rec:
        rec = {**new_record(), **({"legacy": rec} if rec else {})}
    for lang in langs:
        old = rec["entries"].get(lang)
        if old:
            rec["history"].append({"lang": lang, **old})
        rec["entries"][lang] = {"status": "rejected", "at": db.now(), "by": by, "channel": channel, "note": note}
    m["stages"][key] = summarize(rec)
    return rec


def published_entries(m, lang):
    p = CONTENT / m["id"] / lang / "published.json"
    try:
        return json.loads(p.read_text()) if p.exists() else []
    except json.JSONDecodeError:
        return []


def ig_job_time(variant):
    p = Path.home() / "Library" / "LaunchAgents" / f"com.shortsstudio.ig.{variant}.plist"
    if not p.exists():
        return None
    args = plistlib.loads(p.read_bytes()).get("ProgramArguments", [])
    return args[args.index("--at") + 1] if "--at" in args else None


def evidence(m, lang, con):
    variant = f"{m['id']}-{lang}"
    ev = {"youtube": None, "instagram": None}
    pub = published_entries(m, lang)
    rows = [dict(r) for r in con.execute("SELECT platform, platform_id, scheduled_for, published_at FROM publications WHERE variant_id=?", (variant,))]
    sched_path = CONTENT / m["id"] / lang / "schedule.json"
    sched = json.loads(sched_path.read_text()) if sched_path.exists() else {}
    yt = next((p for p in pub if p.get("platform") == "youtube"), None)
    ytrow = next((r for r in rows if r["platform"] == "youtube"), None)
    if yt or ytrow:
        t = (yt or {}).get("scheduled_for") or (ytrow or {}).get("scheduled_for") or (ytrow or {}).get("published_at")
        ev["youtube"] = {"time": ist_iso(t) if t else NOW, "source": "published.json" if yt else "publications table", "platform_id": (yt or ytrow).get("id") or (ytrow or {}).get("platform_id"), "already_published": True}
    elif sched.get("publish_at"):
        ev["youtube"] = {"time": ist_iso(sched["publish_at"]), "source": "schedule.json", "already_published": False}
    elif sched.get("slot") == NOW:
        ev["youtube"] = {"time": NOW, "source": "schedule.json (release immediately)", "already_published": False}
    ig = next((p for p in pub if p.get("platform") == "instagram"), None)
    igrow = next((r for r in rows if r["platform"] == "instagram"), None)
    igsched = m["stages"].get(f"instagram_scheduled:{lang}", {}).get("note")
    job = ig_job_time(variant)
    if ig or igrow:
        ev["instagram"] = {"time": ist_iso(igsched) if igsched else NOW, "source": "published.json" if ig else "publications table", "platform_id": (ig or {}).get("id") or (igrow or {}).get("platform_id"), "already_published": True}
    elif job:
        ev["instagram"] = {"time": ist_iso(job), "source": "launchd job", "already_published": False}
    elif igsched:
        ev["instagram"] = {"time": ist_iso(igsched), "source": "manifest instagram_scheduled", "already_published": False}
    return ev


def migrate(m, con, dry_run=False):
    st = m["stages"]
    report = {"id": m["id"], "script": [], "final": [], "youtube": [], "instagram": [], "skipped": []}
    stamp = db.now()
    for key, gate in ((SCRIPT, "script"), (FINAL, "final")):
        rec = st.get(key)
        if not rec or "entries" in rec or rec.get("status") != "approved":
            continue
        new = {**new_record(), "legacy": dict(rec)}
        for lang in rec.get("langs") or m["languages"]:
            e = build_entry(m, gate, lang, by="owner (legacy record)", channel="legacy", note=rec.get("note", ""))
            e.update({"at": rec.get("at"), "migrated_from_legacy": True, "migrated_at": stamp})
            new["entries"][lang] = e
            report[gate].append(lang)
        new["at"], new["note"] = rec.get("at"), rec.get("note", "")
        st[key] = summarize(new)
    legacy = st.get(LEGACY_PUBLISH)
    if legacy and legacy.get("status") == "approved" and not legacy.get("migrated"):
        for lang in legacy.get("langs") or m["languages"]:
            ev = evidence(m, lang, con)
            for platform in PLATFORMS:
                key = publish_key(platform)
                if not ev[platform]:
                    report["skipped"].append(f"{lang}/{platform}: no evidence")
                    continue
                if lang in entries(m, key):
                    report["skipped"].append(f"{lang}/{platform}: platform record already exists")
                    continue
                e = build_entry(m, "publish", lang, platform, ev[platform]["time"], by="owner (legacy record)", channel="legacy", note=legacy.get("note", ""))
                e.update({"at": legacy.get("at"), "migrated_from_legacy": True, "migrated_at": stamp, "evidence": ev[platform]})
                rec = st.get(key) or new_record()
                rec["entries"][lang] = e
                rec["at"], rec["note"] = legacy.get("at"), "migrated from legacy gate:publish"
                st[key] = summarize(rec)
                report[platform].append(f"{lang} {ev[platform]['time']} ({ev[platform]['source']})")
        legacy["migrated"] = {"at": stamp, "to": [k for k in (publish_key(p) for p in PLATFORMS) if k in st], "note": "kept for history; not read by require()"}
        if "instagram" in [p for p in PLATFORMS if publish_key(p) in st]:
            m.setdefault("platforms", ["youtube", "instagram"])
    if not dry_run:
        save(m)
        db.log_decision(con, "gate:migrate", "migrated", json.dumps(report, ensure_ascii=False), "migration", content_id=m["id"], actor="pipeline migrate-gates", channel="migration")
    return report


def rescope_meta_hashes(m, git_show=None):
    import subprocess

    out = []
    for platform in PLATFORMS:
        rec = m["stages"].get(publish_key(platform))
        if not rec:
            continue
        for lang, e in rec.get("entries", {}).items():
            if e.get("meta_hash_scope") or e.get("status") != "approved":
                continue
            path = ROOT / e["meta"]
            if sha256(path) == e.get("meta_sha256"):
                e["meta_sha256"] = meta_sha256(path, platform)
                e["meta_hash_scope"] = f"publish.json['{platform}']"
                out.append(f"{m['id']}-{lang}/{platform}: rescoped (file unchanged since approval)")
                continue
            blob = git_show(e["meta"]) if git_show else subprocess.run(["git", "show", f"HEAD:{e['meta']}"], cwd=ROOT, capture_output=True).stdout
            if blob and hashlib.sha256(blob).hexdigest() == e.get("meta_sha256"):
                old = json.loads(blob.decode()).get(platform)
                cur = json.loads(path.read_text()).get(platform)
                if old == cur:
                    e["meta_sha256"] = meta_sha256(path, platform)
                    e["meta_hash_scope"] = f"publish.json['{platform}']"
                    out.append(f"{m['id']}-{lang}/{platform}: rescoped (only other sections changed since approval; '{platform}' section identical to git HEAD)")
                    continue
            out.append(f"{m['id']}-{lang}/{platform}: NOT rescoped — the '{platform}' section changed since approval; needs owner re-approval")
    return out
