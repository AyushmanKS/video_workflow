import json
import re
import time
from datetime import datetime, timedelta, timezone

from . import CONTENT

IST = timezone(timedelta(hours=5, minutes=30))
LANG_NAMES = {"en": "English", "hi": "Hindi", "gu": "Gujarati", "te": "Telugu", "mr": "Marathi", "ta": "Tamil", "bn": "Bengali", "kn": "Kannada", "ml": "Malayalam",
              "pa": "Punjabi", "or": "Odia", "ur": "Urdu", "es": "Spanish", "fr": "French", "de": "German"}
PLATFORM_NAMES = {"youtube": "YouTube", "instagram": "Instagram"}
ORDER = ["idea", "writing", "script_ok", "making", "video_ok", "ready", "scheduled", "live"]
LABELS = {"idea": "Idea", "writing": "Writing", "script_ok": "Waiting for your OK (script)", "making": "Making video", "video_ok": "Waiting for your OK (video)",
          "ready": "Ready to post", "scheduled": "Scheduled", "live": "Live", "problem": "Problem"}
TONES = {"idea": "grey", "writing": "work", "script_ok": "wait", "making": "work", "video_ok": "wait", "ready": "wait", "scheduled": "gold", "live": "done", "problem": "bad"}
STEPS = [("script", "Script"), ("ok_script", "Your OK"), ("voice", "Voice"), ("pictures", "Pictures"), ("video", "Video"), ("check", "Quality check"),
         ("ok_video", "Your OK"), ("scheduled", "Scheduled"), ("live", "Live")]
STEP_HELP = {"script": "The story is written in each language.", "ok_script": "You read the scripts and say OK.", "voice": "The narration is recorded.",
             "pictures": "The chalk drawings are made.", "video": "Voice, pictures and music are put together.", "check": "An automatic check looks for mistakes.",
             "ok_video": "You watch the videos and say OK.", "scheduled": "Posting times are set.", "live": "The videos are public."}
RUNNING_WORDS = {"research": "Researching the story", "strategy": "Planning the episode", "script": "Writing the script", "voice": "Recording the voice",
                 "voice_takes": "Recording extra voice takes", "images": "Drawing the pictures", "render": "Putting the video together", "video_qa": "Checking the video",
                 "publish": "Posting", "schedule": "Choosing posting times", "ig_dry_run": "Testing an Instagram post"}
ISSUE_STEP = {"research": "script", "strategy": "script", "script": "script", "lint": "script", "voice": "voice", "voice_takes": "voice", "images": "pictures",
              "render": "video", "video_qa": "check", "gate:final": "ok_video", "gate:script": "ok_script"}
SEVERITY_WORDS = {"info": "Info", "warning": "Heads-up", "recoverable": "Needs attention", "critical": "Urgent"}
SEVERITY_TONES = {"info": "grey", "warning": "wait", "recoverable": "wait", "critical": "bad"}
STALE_S = 6 * 3600
TRANSIENT = {"youtube_upload_limit", "youtube_quota", "network_timeout", "network_unknown_outcome", "tunnel_failed"}
TITLE_PLAIN = {"QA failed": "The quality check found problems", "Blocked by an approval gate": "Needs a fresh OK from you", "YouTube API quota used up": "YouTube's daily allowance is used up",
               "Instagram API access blocked by Meta": "Instagram blocked the posting app", "Instagram post outcome unknown": "Not sure whether the Instagram post worked",
               "Request outcome unknown": "Not sure whether it worked", "Unrecognised error": "Something unexpected went wrong", "Production step crashed": "A making step stopped unexpectedly",
               "Expected file missing": "A file is missing", "Owner rejected this step": "You asked for changes", "YouTube refused the request (403)": "YouTube refused the upload",
               "Google sign-in expired": "The YouTube sign-in has expired", "Instagram token invalid": "The Instagram sign-in has expired",
               "Temporary upload link failed": "A temporary upload link failed", "Scheduled Instagram post skipped (over 24 h late)": "An Instagram post was skipped because it was over a day late"}
TODO_PLAIN = {"youtube_upload_limit": "Nothing for now. It uploads by itself once YouTube allows more uploads, usually within a day.",
              "youtube_quota": "Nothing for now. It tries again by itself tomorrow.", "google_token_expired": "Ask Claude to sign in to YouTube again.",
              "youtube_forbidden": "Ask Claude to check the YouTube account.", "ig_api_blocked": "Ask Claude to check the Instagram connection.",
              "ig_permission": "Ask Claude to check the Instagram connection.", "ig_token_invalid": "Ask Claude to sign in to Instagram again.",
              "ig_container_error": "Ask Claude to try posting this video again.", "ig_processing_timeout": "Ask Claude to try posting this video again.",
              "ig_container_orphaned": "Check Instagram to see if the post is there, then tell Claude.", "ig_job_late": "Ask Claude to pick a new posting time.",
              "qa_fail": "Ask Claude to fix the video and run the check again.",
              "gate_refused": "The video changed after you approved it. Watch the new version and tell Claude if it is OK.",
              "gate_rejected": "Claude will apply your notes and ask you again.", "missing_output": "Ask Claude to redo this step.", "render_failed": "Ask Claude to redo this step.",
              "network_timeout": "Usually nothing. It tries again by itself. If it keeps happening, check the Mac's internet.",
              "network_unknown_outcome": "Check the platform to see if the post is there, then tell Claude.", "disk_low": "Ask Claude to free up space on the Mac.",
              "cancelled": "Nothing, unless you want it restarted.", "tunnel_failed": "Nothing. The dashboard reconnects by itself."}
JARGON = [(r"\bQA\b", "quality check"), (r"\bG1\b", "script approval"), (r"\bG2\b", "video approval"), (r"\bG3\b", "posting approval"),
          (r"\bvariants?\b", "video"), (r"\blint\b", "script check"), (r"\boutbox\b", "message list"), (r"\bauto-reject\b", "serious"),
          (r"\bauto-warn\b", "minor"), (r"python -m pipeline \S+( \S+)?", "the pipeline on the Mac"), (r"\btask_state\b", "task list"),
          (r"\bsha256\b", "fingerprint"), (r"\bAPI\b", "connection")]


def to_dt(t):
    if t is None or t == "" or t == "now":
        return None
    if isinstance(t, (int, float)):
        return datetime.fromtimestamp(float(t), IST)
    try:
        d = datetime.fromisoformat(str(t).replace("Z", "+00:00"))
    except ValueError:
        try:
            d = datetime.strptime(str(t)[:24], "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            return None
    return (d if d.tzinfo else d.replace(tzinfo=IST)).astimezone(IST)


def epoch(t):
    d = to_dt(t)
    return d.timestamp() if d else None


def clock(d):
    h = d.hour % 12 or 12
    return f"{h}:{d.minute:02d} {'am' if d.hour < 12 else 'pm'}"


def day_name(t, now=None):
    d = to_dt(t)
    if not d:
        return ""
    today = to_dt(now or time.time()).date()
    delta = (d.date() - today).days
    if delta == 0:
        return "Today"
    if delta == 1:
        return "Tomorrow"
    if delta == -1:
        return "Yesterday"
    return f"{d.strftime('%a')} {d.day} {d.strftime('%b')}"


def when(t, now=None):
    d = to_dt(t)
    if not d:
        return "as soon as possible" if t == "now" else "not set"
    name = day_name(d, now)
    sep = " " if name in ("Today", "Tomorrow", "Yesterday") else ", "
    return f"{name}{sep}{clock(d)}"


def ago(t, now=None):
    e = epoch(t)
    if e is None:
        return "a while ago"
    s = max(0, (now or time.time()) - e)
    if s < 60:
        return "just now"
    if s < 3600:
        m = int(s // 60)
        return f"{m} min ago"
    if s < 86400:
        h = int(s // 3600)
        return f"{h} hour{'s' if h != 1 else ''} ago"
    return when(e, now)


def plain(text):
    s = "" if text is None else str(text)
    s = re.sub(r"\b(C\d{4})-([a-z]{2,3})\b", lambda m: f"Ep {int(m.group(1)[1:])} {lang_name(m.group(2))}", s)
    s = re.sub(r"\bC(\d{4})\b", lambda m: f"Episode {int(m.group(1))}", s)
    for rx, rep in JARGON:
        s = re.sub(rx, rep, s, flags=re.I)
    s = re.sub(r"\b[0-9a-f]{32,}\b", "", s)
    s = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})?", lambda m: when(m.group(0)), s)
    return s.strip()


def lang_name(code):
    return LANG_NAMES.get(code, (code or "").upper())


def platform_name(p):
    return PLATFORM_NAMES.get(p, (p or "").title())


def short_title(topic, episode=None):
    t = (topic or "").strip()
    t = re.sub(r"^.*?\bEpisode\s*\d+\s*[:\-–—]\s*", "", t, flags=re.I)
    return t or (f"Episode {episode}" if episode else "Untitled")


def ep_label(episode, cid):
    if episode:
        return f"Ep {int(episode):02d}"
    m = re.match(r"C(\d+)", cid or "")
    return f"Ep {int(m.group(1)):02d}" if m else (cid or "Ep ?")


def read_manifest(cid):
    try:
        return json.loads((CONTENT / cid / "manifest.json").read_text())
    except (OSError, ValueError):
        return None


def _stage_done(st, key):
    return (st.get(key) or {}).get("status") in ("done", "approved")


def gate_ok(m, key, lang):
    rec = (m.get("stages") or {}).get(key) or {}
    ent = rec.get("entries")
    if ent:
        return (ent.get(lang) or {}).get("status") == "approved"
    return rec.get("status") == "approved" and lang in (rec.get("langs") or m.get("languages") or [])


def _qa_failed(st, lang):
    rec = st.get(f"video_qa:{lang}") or {}
    return str(rec.get("note") or "").lower().startswith("fail")


def scene_count(cid, lang):
    try:
        return len(json.loads((CONTENT / cid / lang / "script.json").read_text()).get("scenes") or [])
    except (OSError, ValueError, AttributeError):
        return 0


def file_counts(cid, lang, step):
    n = scene_count(cid, lang)
    work = CONTENT / cid / lang
    if step == "voice" and n:
        return sum(1 for i in range(n) if (work / "audio" / f"{i:02d}.wav").exists()), n
    if step == "pictures" and n:
        return sum(1 for i in range(n) if (work / "img" / f"{i:02d}_raw.png").exists()), n
    return None


def platform_state(variant, plat, ctx, now):
    pubs = ctx["pubs"].get((variant, plat), [])
    future = [epoch(p["scheduled_for"]) for p in pubs if (epoch(p["scheduled_for"]) or 0) > now]
    if future:
        return {"state": "scheduled", "t": min(future)}
    if pubs:
        p = pubs[-1]
        return {"state": "live", "t": epoch(p["published_at"]) or epoch(p["scheduled_for"]), "url": p["url"] if str(p["url"] or "").startswith("https://") else None}
    q = ctx["queue"].get((variant, plat))
    if q:
        if q["status"] == "done":
            return {"state": "live", "t": epoch(q["updated_at"])}
        if q["status"] == "failed":
            return {"state": "failed", "t": epoch(q["publish_at"]), "error": q["last_error"]}
        te = epoch(q["publish_at"])
        if te and te > now:
            return {"state": "scheduled", "t": te, "held": bool(q["last_error"])}
        return {"state": "waiting", "t": te, "held": bool(q["last_error"]), "error": q["last_error"]}
    job = ctx["jobs"].get(variant) if plat == "instagram" else None
    if job:
        if job.get("t") and job["t"] < now - 3600:
            return {"state": "late", "t": job["t"]}
        return {"state": "scheduled", "t": job.get("t")}
    m = ctx["manifests"].get(variant.rsplit("-", 1)[0]) or {}
    st = m.get("stages") or {}
    lang = variant.rsplit("-", 1)[1]
    key = "published" if plat == "youtube" else "published_instagram"
    if _stage_done(st, f"{key}:{lang}"):
        return {"state": "live", "t": None}
    if plat == "instagram" and _stage_done(st, f"instagram_scheduled:{lang}"):
        t = epoch((st.get(f"instagram_scheduled:{lang}") or {}).get("note"))
        if t and t > now:
            return {"state": "scheduled", "t": t}
        return {"state": "late", "t": t}
    return {"state": "none", "t": None}


def platform_words(ps, now=None):
    s = ps["state"]
    if s == "live":
        return "Posted" + (f" {when(ps['t'], now)}" if ps.get("t") else "")
    if s == "scheduled":
        return f"Scheduled for {when(ps['t'], now)}" if ps.get("t") else "Scheduled"
    if s == "waiting":
        if ps.get("t") and ps["t"] < (now or time.time()) - 600:
            return "Late — waiting for the platform to allow more uploads" if ps.get("held") else "Late — not posted yet"
        return "Posting as soon as the platform allows"
    if s == "failed":
        return "Posting failed"
    if s == "late":
        return "Should have posted by now — please check"
    return "Not set up yet"


def lang_status(m, lang, ctx, now=None):
    now = now or time.time()
    cid = m["id"]
    v = f"{cid}-{lang}"
    st = m.get("stages") or {}
    platforms = m.get("platforms") or ["youtube"]
    plats = {p: platform_state(v, p, ctx, now) for p in platforms}
    done = {
        "script": _stage_done(st, f"script:{lang}"),
        "ok_script": gate_ok(m, "gate:script", lang),
        "voice": _stage_done(st, f"voice:{lang}"),
        "pictures": _stage_done(st, f"images:{lang}"),
        "video": _stage_done(st, f"render:{lang}"),
        "check": _stage_done(st, f"video_qa:{lang}") and not _qa_failed(st, lang),
        "ok_video": gate_ok(m, "gate:final", lang),
        "scheduled": bool(plats) and all(p["state"] in ("scheduled", "live", "waiting") for p in plats.values()),
        "live": bool(plats) and all(p["state"] == "live" for p in plats.values()),
    }
    keys = [k for k, _ in STEPS]
    last = max([i for i, k in enumerate(keys) if done[k]], default=-1)
    for i in range(last):
        if keys[i] not in ("scheduled",):
            done[keys[i]] = True
    if done["live"]:
        done["scheduled"] = True
    if done["live"]:
        stage = "live"
    elif done["scheduled"]:
        stage = "scheduled"
    elif done["ok_video"]:
        stage = "ready"
    elif done["check"]:
        stage = "video_ok"
    elif done["ok_script"]:
        stage = "making"
    elif done["script"]:
        stage = "script_ok"
    elif _stage_done(st, "research") or _stage_done(st, "strategy") or (CONTENT / cid / lang / "script.json").exists():
        stage = "writing"
    else:
        stage = "idea"
    current = next((k for k in keys if not done[k]), None)
    run = ctx["running"].get(v)
    detail = ""
    counts = None
    if stage == "making":
        current = next((k for k in ("voice", "pictures", "video", "check") if not done[k]), "check")
        counts = file_counts(cid, lang, current)
        names = {"voice": "voice", "pictures": "pictures", "video": "putting the video together", "check": "quality check"}
        detail = f"{names[current]} {counts[0]} of {counts[1]}" if counts else names[current]
        if _qa_failed(st, lang):
            detail = "quality check found problems"
    problems, relevant = [], set()
    for iss in ctx["issues"].get(v, []):
        if issue_relevant(iss, plats, done):
            relevant.add(iss["id"])
            if iss["status"] == "open" and iss["severity"] in ("critical", "recoverable", "warning") and iss.get("error_code") not in TRANSIENT:
                problems.append(iss)
    for p, ps in plats.items():
        if ps["state"] in ("failed", "late") and not any(i["platform"] == p for i in problems):
            problems.append({"id": None, "title": f"{platform_name(p)}: {platform_words(ps, now)}", "severity": "recoverable", "platform": p, "stage": "publish"})
    if _qa_failed(st, lang) and not done["ok_video"] and not problems:
        problems.append({"id": None, "title": "The quality check found problems", "severity": "recoverable", "platform": None, "stage": "video_qa"})
    return {"lang": lang, "name": lang_name(lang), "stage": stage, "label": LABELS[stage], "done": done, "current": current, "detail": detail, "counts": counts,
            "platforms": plats, "problems": problems, "relevant": relevant, "running": run}


def issue_relevant(iss, plats, done):
    stage = iss.get("stage") or ""
    if stage == "publish" or stage.startswith("gate:publish"):
        plat = iss.get("platform")
        targets = [plat] if plat in plats else list(plats)
        if iss.get("error_code") in TRANSIENT:
            return any(plats[p]["state"] in ("none", "waiting", "failed", "late") for p in targets)
        return any(plats[p]["state"] != "live" for p in targets)
    step = ISSUE_STEP.get(stage)
    return step is None or not done.get(step)


def issue_title(iss):
    t = iss.get("title") or ""
    return TITLE_PLAIN.get(t) or plain(t)


def issue_todo(iss):
    return TODO_PLAIN.get(iss.get("error_code") or "") or plain(iss.get("suggestion") or "Ask Claude to take a look.")


def overall(langs, now=None):
    if not langs:
        return {"stage": "idea", "base": "idea", "label": LABELS["idea"], "tone": TONES["idea"], "done": False, "partial": False, "text": "Not started yet",
                "live_counts": {}, "problem": False}
    base = min((l["stage"] for l in langs), key=ORDER.index)
    plat_names = sorted({p for l in langs for p in l["platforms"]}, key=lambda p: (p != "youtube", p))
    live_counts = {p: (sum(1 for l in langs if l["platforms"].get(p, {}).get("state") == "live"), sum(1 for l in langs if p in l["platforms"])) for p in plat_names}
    any_live = any(n for n, _ in live_counts.values())
    all_done = all(l["stage"] == "live" for l in langs)
    stage = base
    if ORDER.index(base) >= ORDER.index("scheduled") and any_live:
        stage = "live"
    n = len(langs)
    if stage == "idea":
        text = "Not started yet"
    elif stage == "writing":
        text = "The scripts are being written"
    elif stage == "script_ok":
        ready = sum(1 for l in langs if ORDER.index(l["stage"]) >= ORDER.index("script_ok"))
        text = f"Scripts ready in {ready} of {n} languages — tell Claude if they are OK"
    elif stage == "making":
        mk = [l for l in langs if l["stage"] == "making"]
        busy = next((l for l in mk if l["running"]), mk[0] if mk else None)
        finished = sum(1 for l in langs if ORDER.index(l["stage"]) > ORDER.index("making"))
        text = f"{busy['name']}: {busy['detail']}" if busy and busy["detail"] else "Making the videos"
        if finished:
            text += f" · {finished} of {n} languages finished"
    elif stage == "video_ok":
        text = "The videos are ready to watch — tell Claude if they are OK"
    elif stage == "ready":
        text = "Approved — tell Claude when to post"
    elif stage == "scheduled":
        ts = [p["t"] for l in langs for p in l["platforms"].values() if p["state"] == "scheduled" and p.get("t")]
        text = f"First post {when(min(ts), now)}" if ts else "Posting soon"
    else:
        text = " · ".join(f"{platform_name(p)} {a} of {b}" for p, (a, b) in live_counts.items())
        text = ("Posted everywhere · " if all_done else "Posted on ") + text
    problem = any(l["problems"] for l in langs)
    if problem:
        first = next(l for l in langs if l["problems"])
        text = f"{first['name']}: {issue_title(first['problems'][0])}"
    shown = "problem" if problem else stage
    return {"stage": shown, "base": base, "label": LABELS[shown], "tone": TONES[shown], "done": all_done, "partial": any_live and not all_done, "text": text,
            "live_counts": live_counts, "problem": problem}


def combined_steps(langs):
    out = []
    n = len(langs)
    for key, name in STEPS:
        k = sum(1 for l in langs if l["done"].get(key))
        working = [l for l in langs if not l["done"].get(key) and l["current"] == key]
        if n and k == n:
            state = "done"
        elif k or working:
            state = "now"
        else:
            state = "todo"
        out.append({"key": key, "name": name, "state": state, "done": k, "total": n, "help": STEP_HELP[key],
                    "langs": [{"name": l["name"], "done": bool(l["done"].get(key)), "now": l["current"] == key, "detail": l["detail"] if l["current"] == key else ""} for l in langs]})
    first_open = next((s for s in out if s["state"] != "done"), None)
    for s in out:
        if s["state"] == "now" and s is not first_open and s["done"] == 0:
            s["state"] = "todo"
    return out


def ig_job_map(jobs):
    return {j["variant"]: j for j in jobs if not j.get("dry_run")}


def load(con, jobs=None, now=None):
    now = now or time.time()
    contents = con.execute("SELECT c.*, p.name AS project_name FROM contents c LEFT JOIN projects p ON p.id=c.project_id ORDER BY c.id").fetchall()
    pubs = {}
    for p in con.execute("SELECT variant_id, platform, scheduled_for, published_at, url FROM publications ORDER BY id"):
        pubs.setdefault((p["variant_id"], p["platform"]), []).append(p)
    queue = {(f"{q['content_id']}-{q['lang']}", q["platform"]): q for q in con.execute("SELECT * FROM publish_queue")}
    issues = {}
    for r in con.execute("SELECT * FROM issues WHERE status IN ('open','acknowledged')"):
        issues.setdefault(r["variant_id"], []).append(dict(r))
    running = {}
    for t in con.execute("SELECT * FROM task_state WHERE status='Running' AND t >= ? ORDER BY t", (now - STALE_S,)):
        if t["variant_id"]:
            running[t["variant_id"]] = t
    manifests = {}
    for c in contents:
        m = read_manifest(c["id"])
        if m:
            manifests[c["id"]] = m
    ctx = {"pubs": pubs, "queue": queue, "issues": issues, "running": running, "jobs": ig_job_map(jobs or []), "manifests": manifests}
    out = []
    for c in contents:
        m = manifests.get(c["id"])
        cfg_m = (m or {}).get("milestone")
        notes_m = None
        try:
            notes_m = (json.loads(c["notes"]) or {}).get("milestone") if c["notes"] and str(c["notes"]).startswith("{") else None
        except ValueError:
            notes_m = None
        langs = [lang_status(m, lang, ctx, now) for lang in (m.get("languages") or [])] if m else []
        ov = overall(langs, now)
        out.append({"id": c["id"], "episode": c["episode"] or (m or {}).get("episode"), "title": short_title(c["topic"], c["episode"]), "topic": c["topic"],
                    "project_id": c["project_id"], "project_name": c["project_name"], "milestone": cfg_m or notes_m, "langs": langs, "status": ov,
                    "platforms": (m or {}).get("platforms") or ["youtube"]})
    return out


def is_made(ep):
    return ORDER.index(ep["status"]["base"]) >= ORDER.index("ready")


def project_plan(cfg):
    try:
        c = json.loads(cfg) if isinstance(cfg, str) else (cfg or {})
    except ValueError:
        c = {}
    goal = c.get("goal_episodes")
    ms = c.get("milestones") or []
    return {"goal": int(goal) if isinstance(goal, (int, float)) or str(goal or "").isdigit() else None, "milestones": ms, "note": c.get("note")}


def milestone_index(ep, milestones):
    if ep.get("milestone"):
        for i, m in enumerate(milestones):
            if str(m.get("name", "")).lower() == str(ep["milestone"]).lower():
                return i
    n = ep.get("episode")
    if not n:
        return None
    total = 0
    for i, m in enumerate(milestones):
        total += int(m.get("planned") or 0)
        if int(n) <= total:
            return i
    return len(milestones) - 1 if milestones else None


def progress(eps, plan):
    goal = plan.get("goal")
    made = sum(1 for e in eps if is_made(e))
    done = sum(1 for e in eps if e["status"]["done"])
    working = len(eps) - made
    out = {"goal": goal, "episodes": len(eps), "made": made, "done": done, "posting": made - done, "working": working, "milestones": []}
    if goal:
        out["not_started"] = max(0, goal - len(eps))
        out["to_go"] = max(0, goal - made)
        out["pct"] = round(100 * made / goal) if goal else 0
    ms = plan.get("milestones") or []
    buckets = [[] for _ in ms]
    for e in eps:
        i = milestone_index(e, ms)
        if i is not None:
            buckets[i].append(e)
    current = None
    for i, m in enumerate(ms):
        mine = sorted(buckets[i], key=lambda e: (e.get("episode") or 0, e["id"]))
        planned = int(m.get("planned") or 0)
        mm = sum(1 for e in mine if is_made(e))
        row = {"name": m.get("name"), "subtitle": m.get("subtitle"), "planned": planned, "made": mm, "done": sum(1 for e in mine if e["status"]["done"]),
               "working": len(mine) - mm, "to_go": max(0, planned - mm), "episodes": mine, "pct": round(100 * mm / planned) if planned else 0}
        out["milestones"].append(row)
        if current is None and mine and mm < planned:
            current = i
    if current is None:
        current = next((i for i, r in enumerate(out["milestones"]) if r["made"] < r["planned"]), None)
    out["current"] = current
    return out


EVENT_WORDS = {
    ("completed", "research"): "Research finished", ("completed", "strategy"): "Episode plan written", ("completed", "script"): "Script written",
    ("waiting_approval", "gate:script"): "Scripts ready for your OK", ("approved", "gate:script"): "You approved the script",
    ("rejected", "gate:script"): "You asked for script changes", ("completed", "voice"): "Voice recorded", ("failed", "voice"): "Voice recording failed",
    ("completed", "images"): "Pictures drawn", ("failed", "images"): "Drawing the pictures failed", ("completed", "render"): "Video put together",
    ("failed", "render"): "Putting the video together failed", ("completed", "video_qa"): "Quality check done", ("failed", "video_qa"): "Quality check found problems",
    ("waiting_approval", "gate:final"): "Videos ready for your OK", ("approved", "gate:final"): "You approved the video",
    ("rejected", "gate:final"): "You asked for video changes", ("approved", "gate:publish"): "You approved posting",
    ("approved", "gate:publish:youtube"): "You approved posting on YouTube", ("approved", "gate:publish:instagram"): "You approved posting on Instagram",
    ("completed", "schedule"): "Posting times chosen", ("unknown_outcome", "publish"): "Not sure whether posting worked — please check",
}


def event_sentence(kind, stage, platform):
    if stage == "publish":
        pn = platform_name(platform) if platform else "the platform"
        if kind == "queued":
            return f"Lined up to post on {pn}"
        if kind == "completed":
            return f"Uploaded to {pn}" if platform == "youtube" else f"Posted on {pn}"
        if kind == "failed":
            return f"Posting on {pn} failed"
        if kind == "warning":
            return f"Posting on {pn} is held up"
        if kind == "unknown_outcome":
            return f"Not sure whether posting on {pn} worked — please check"
        return None
    return EVENT_WORDS.get((kind, stage))


def history(con, cid, limit=25, now=None):
    rows = con.execute("SELECT t, kind, stage, platform, variant_id FROM events WHERE content_id=? OR variant_id LIKE ? ORDER BY t DESC, rowid DESC LIMIT 2000",
                       (cid, f"{cid}-%")).fetchall()
    groups = []
    for r in rows:
        s = event_sentence(r["kind"], r["stage"], r["platform"])
        if not s:
            continue
        lang = (r["variant_id"] or "").rsplit("-", 1)[1] if r["variant_id"] and "-" in r["variant_id"] else None
        g = groups[-1] if groups else None
        if g and g["text"] == s and g["t0"] - r["t"] <= 900:
            if lang and lang not in g["langs"]:
                g["langs"].append(lang)
            g["t0"] = r["t"]
            continue
        if len(groups) >= limit:
            break
        groups.append({"t": r["t"], "t0": r["t"], "text": s, "langs": [lang] if lang else []})
    for g in groups:
        g["when"] = when(g["t"], now)
        g["who"] = ", ".join(lang_name(x) for x in sorted(g["langs"], key=lambda x: (x != "en", x)))
    return groups


def get_config(con, pid):
    r = con.execute("SELECT config FROM projects WHERE id=?", (pid,)).fetchone()
    if not r:
        return None
    try:
        return json.loads(r["config"] or "{}") or {}
    except ValueError:
        return {}


def update_config(con, pid, **changes):
    cfg = get_config(con, pid)
    if cfg is None:
        raise KeyError(pid)
    for k, v in changes.items():
        if v is None:
            cfg.pop(k, None)
        else:
            cfg[k] = v
    con.execute("UPDATE projects SET config=?, updated_at=? WHERE id=?", (json.dumps(cfg, ensure_ascii=False), datetime.now(IST).strftime("%Y-%m-%dT%H:%M:%S%z"), pid))
    return cfg


def valid_milestones(ms):
    if not isinstance(ms, list) or not ms:
        raise ValueError("milestones must be a non-empty list")
    for m in ms:
        if not isinstance(m, dict) or not m.get("name") or not isinstance(m.get("planned"), int) or m["planned"] < 0:
            raise ValueError("each milestone needs a name and a whole-number planned count")
    return ms


def fmt_plan(pid, cfg):
    plan = project_plan(cfg)
    lines = [f"{pid}: goal {plan['goal'] if plan['goal'] else 'not set'} episodes"]
    total = 0
    for i, m in enumerate(plan["milestones"], 1):
        start = total + 1
        total += int(m.get("planned") or 0)
        extra = f", {m['sargas']} sargas" if m.get("sargas") else ""
        lines.append(f"  {i}. {m.get('name')} — {m.get('subtitle') or ''} · {m.get('planned')} planned (episodes {start}–{total}{extra})")
    if plan["milestones"]:
        lines.append(f"  planned total {total}" + (f" (goal {plan['goal']})" if plan["goal"] and plan["goal"] != total else ""))
    else:
        lines.append("  no milestones")
    if plan.get("note"):
        lines.append(f"  note: {plan['note']}")
    return "\n".join(lines)
