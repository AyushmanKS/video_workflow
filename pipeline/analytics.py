import json
import os
import re
import plistlib
import statistics
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from . import CONTENT, DATA, ROOT, db
from .research import retry

WINDOWS = [("24h", 24), ("48h", 48), ("7d", 168), ("14d", 336), ("30d", 720)]
WINDOW_HOURS = dict(WINDOWS)
TOLERANCE_H = 12
LAST_WINDOW_H = WINDOWS[-1][1] + TOLERANCE_H
FINAL_AFTER_DAYS = 3
CORE = "views,engagedViews,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,comments,shares,subscribersGained,subscribersLost"
DAY_METRICS = "views,engagedViews,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,shares,subscribersGained"
IG_METRICS = ("views", "reach", "saved", "shares", "likes", "comments", "total_interactions", "ig_reels_avg_watch_time", "ig_reels_video_view_total_time")
IG_DEPRECATED = {
    "plays": "deprecated for v22.0+ (2025-01-21) and all versions from 2025-04-21; use views",
    "clips_replays_count": "deprecated for v22.0+ (2025-01-21) and all versions from 2025-04-21",
    "ig_reels_aggregated_all_plays_count": "deprecated for v22.0+ (2025-01-21) and all versions from 2025-04-21",
    "video_views": "deprecated for v21.0+ and all versions from 2025-01-08",
}
IG_DOC = "developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights (checked 2026-11-16, API v27.0)"
TOKENISH = re.compile(r"(access_token=|Bearer\s+|\bEAA)[A-Za-z0-9_\-.%]+")
AGENT_LABEL = "com.shortsstudio.analytics.daily"
AGENT_PLIST = Path.home() / "Library" / "LaunchAgents" / f"{AGENT_LABEL}.plist"
DAILY_AT = (20, 0)


def parse_time(s):
    if not s:
        return None
    t = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return t


def window_label(age_h):
    if age_h is None:
        return "unknown_age"
    if age_h < 0:
        return f"prepublish_{round(-age_h)}h"
    for label, hours in WINDOWS:
        if abs(age_h - hours) <= TOLERANCE_H:
            return label
    return f"age_{round(age_h)}h"


def age_hours(captured_at, published_at):
    c, p = parse_time(captured_at), parse_time(published_at)
    if not c or not p:
        return None
    return round((c - p).total_seconds() / 3600, 2)


def publication_time(p):
    return p["published_at"] or p["scheduled_for"]


def table(resp):
    cols = [h["name"] for h in resp.get("columnHeaders", [])]
    return [dict(zip(cols, r)) for r in resp.get("rows", [])]


def services():
    import publish

    return publish.analytics_services()


def day_range(start, end):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def query_day(ya, video_id, day):
    q = dict(ids="channel==MINE", startDate=day.isoformat(), endDate=day.isoformat(), filters=f"video=={video_id}")
    try:
        rows = table(retry(lambda: ya.reports().query(**q, metrics=DAY_METRICS).execute()))
    except Exception:
        rows = table(retry(lambda: ya.reports().query(**q, metrics=DAY_METRICS.replace("engagedViews,", "")).execute()))
    row = rows[0] if rows else {}
    return {"day": day.isoformat(), **row, **({} if rows else {"empty": True})}


def day_series(ya, video_id, start, end, prev=None):
    keep = {}
    final_before = end - timedelta(days=FINAL_AFTER_DAYS)
    for r in (prev or []):
        if isinstance(r, dict) and r.get("day") and not r.get("empty") and date.fromisoformat(r["day"]) < final_before:
            keep[r["day"]] = r
    out = []
    for d in day_range(start, end):
        out.append(keep.get(d.isoformat()) or query_day(ya, video_id, d))
    return out


def windows_from_by_day(by_day, pub_date, age_h):
    if not isinstance(by_day, list) or age_h is None:
        return {}
    have = {r["day"]: r for r in by_day if isinstance(r, dict) and r.get("day")}
    with_data = [d for d, r in have.items() if not r.get("empty")]
    if not with_data:
        return {}
    last = max(date.fromisoformat(d) for d in with_data)
    out = {}
    for label, hours in WINDOWS:
        n = hours // 24
        days = [pub_date + timedelta(days=k) for k in range(n)]
        if age_h < hours - TOLERANCE_H or days[-1] > last:
            continue
        rows = [have.get(d.isoformat(), {}) for d in days]
        views = sum(int(r.get("views") or 0) for r in rows)
        minutes = sum(float(r.get("estimatedMinutesWatched") or 0) for r in rows)
        pct = sum(float(r.get("averageViewPercentage") or 0) * int(r.get("views") or 0) for r in rows)
        engaged = [r.get("engagedViews") for r in rows]
        out[label] = {"views": views, "estimatedMinutesWatched": round(minutes, 2), "averageViewPercentage": round(pct / views, 2) if views else None,
                      "engagedViews": sum(int(e or 0) for e in engaged) if any(e is not None for e in engaged) else None,
                      "days": [d.isoformat() for d in days], "basis": f"sum of the first {n} calendar day(s) of the by_day series (YouTube Analytics days; day 1 is partial)"}
    return out


def fetch_metrics(yt, ya, video_id, published, prev=None):
    out = {"captured_at": db.now(), "video_id": video_id}
    v = retry(lambda: yt.videos().list(part="statistics,snippet,status,contentDetails", id=video_id).execute())["items"]
    if not v:
        out["error"] = "video not found"
        return out
    v = v[0]
    out["public_counters"] = {k: int(x) for k, x in v.get("statistics", {}).items()}
    out["privacy"] = v["status"]["privacyStatus"]
    pub = published or parse_time(v["snippet"]["publishedAt"])
    now = datetime.now(timezone.utc)
    out["published_ref"] = pub.isoformat()
    out["age_h"] = round((now - pub).total_seconds() / 3600, 2)
    start, end = pub.date(), now.date()
    if start > end or out["age_h"] < 0:
        out["note"] = "not yet public at capture time; no Analytics queries made"
        return out
    q = dict(ids="channel==MINE", startDate=start.isoformat(), endDate=end.isoformat(), filters=f"video=={video_id}")
    for key, extra in {
        "totals_to_date": dict(metrics=CORE),
        "traffic_sources": dict(metrics="views,estimatedMinutesWatched", dimensions="insightTrafficSourceType", sort="-views"),
        "countries": dict(metrics="views,estimatedMinutesWatched", dimensions="country", sort="-views", maxResults=10),
        "retention": dict(metrics="audienceWatchRatio,relativeRetentionPerformance", dimensions="elapsedVideoTimeRatio"),
    }.items():
        try:
            out[key] = table(retry(lambda: ya.reports().query(**q, **extra).execute()))
        except Exception as e:
            if key == "totals_to_date":
                try:
                    out[key] = table(retry(lambda: ya.reports().query(**q, metrics=CORE.replace("engagedViews,", "")).execute()))
                    out["note_engaged"] = "engagedViews not accepted for this query: " + str(e)[:160]
                    continue
                except Exception as e2:
                    e = e2
            out[key] = {"unavailable": str(e)[:240]}
    try:
        out["by_day"] = day_series(ya, video_id, start, end, prev)
    except Exception as e:
        out["by_day"] = {"unavailable": str(e)[:240]}
    out["windows"] = windows_from_by_day(out["by_day"], start, out["age_h"])
    out["note"] = "by_day rows are queried with startDate=endDate per day; rows younger than 3 days are re-queried each run because YouTube Analytics lags 1-3 days."
    return out


def ig_config():
    sys.path.insert(0, str(ROOT))
    import instagram

    cfg = instagram.load_config()
    return instagram, cfg


def redact(text, token):
    return scrub(str(text).replace(token, "<token>") if token else str(text))


def scrub(text):
    return TOKENISH.sub(lambda m: m.group(1) + "<redacted>", str(text))


def ig_value(item):
    vals = item.get("values")
    if vals:
        return vals[0].get("value")
    tv = item.get("total_value")
    return tv.get("value") if isinstance(tv, dict) else None


PERMISSION_CODES = (10, 200, 190)


def ig_get(url, params, token, timeout=25):
    import requests

    try:
        r = requests.get(url, params=params, headers={"Authorization": f"Bearer {token}"}, timeout=timeout)
    except requests.RequestException as e:
        return 0, {"error": {"message": f"{type(e).__name__}: network error contacting {url.split('?')[0]}"}}
    try:
        body = r.json()
    except ValueError:
        body = {"error": {"message": redact(r.text[:200], token)}}
    return r.status_code, body


def ig_error(body, token):
    e = body.get("error", {}) if isinstance(body, dict) else {}
    return e.get("code"), redact(e.get("message", "unknown error"), token)[:200]


def fetch_instagram(media_id, published=None, metrics=IG_METRICS, ctx=None):
    instagram, cfg = ctx or ig_config()
    token = cfg["access_token"]
    base = f"{instagram.graph(cfg)}/{media_id}"
    out = {"captured_at": db.now(), "media_id": media_id, "doc": IG_DOC, "deprecated_not_requested": IG_DEPRECATED}
    if published:
        out["published_ref"] = published.isoformat()
        out["age_h"] = round((datetime.now(timezone.utc) - published).total_seconds() / 3600, 2)
    code, body = ig_get(base, {"fields": "like_count,comments_count,timestamp,permalink,media_product_type"}, token)
    if code == 0:
        raise ConnectionError(ig_error(body, token)[1])
    out["fields"] = body if code < 400 else {"unavailable": ig_error(body, token)[1]}
    insights, unsupported = {}, {}
    code, body = ig_get(f"{base}/insights", {"metric": ",".join(metrics)}, token)
    if code == 0:
        raise ConnectionError(ig_error(body, token)[1])
    if code < 400:
        for item in body.get("data", []):
            insights[item["name"]] = ig_value(item)
    else:
        ecode, msg = ig_error(body, token)
        if ecode in PERMISSION_CODES:
            out["permission_error"] = f"(#{ecode}) {msg}; the token likely lacks instagram_manage_insights (Facebook Login) or instagram_business_manage_insights (Instagram Login). Re-authorise with that permission; no insights were stored."
            unsupported = {m: "permission" for m in metrics}
        else:
            for m in metrics:
                c, b = ig_get(f"{base}/insights", {"metric": m}, token)
                if c and c < 400:
                    for item in b.get("data", []):
                        insights[item["name"]] = ig_value(item)
                else:
                    unsupported[m] = ig_error(b, token)[1]
    for m in metrics:
        if m not in insights and m not in unsupported:
            unsupported[m] = "no data returned (Meta returns an empty set when data is unavailable)"
    out["insights"] = insights
    if unsupported:
        out["unsupported"] = unsupported
    out["units_note"] = "ig_reels_avg_watch_time and ig_reels_video_view_total_time are stored as returned; Meta's reference page does not state units (verify before use)."
    return out


def sync_instagram_publications(con):
    added = 0
    for path in sorted(CONTENT.glob("C*/*/published.json")):
        try:
            entries = json.loads(path.read_text())
        except ValueError:
            continue
        variant = f"{path.parent.parent.name}-{path.parent.name}"
        for e in entries if isinstance(entries, list) else []:
            if e.get("platform") != "instagram" or not e.get("id"):
                continue
            cur = con.execute("INSERT OR IGNORE INTO publications (variant_id, platform, platform_id, url, privacy, scheduled_for, published_at, slot, metadata, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                              (variant, "instagram", e["id"], e.get("url"), e.get("privacy"), None, e.get("time"), None, None, db.now()))
            added += cur.rowcount
    return added


def snapshots_of(con, pub_id):
    return con.execute("SELECT * FROM analytics_snapshots WHERE publication_id=? ORDER BY captured_at", (pub_id,)).fetchall()


def due(con, force=False, platforms=("youtube", "instagram"), now=None):
    now = now or datetime.now(timezone.utc)
    todo = []
    marks = ",".join("?" for _ in platforms)
    for p in con.execute(f"SELECT * FROM publications WHERE platform IN ({marks})", tuple(platforms)).fetchall():
        t0 = parse_time(publication_time(p))
        if not t0:
            continue
        age = (now - t0).total_seconds() / 3600
        if age < 0:
            continue
        snaps = snapshots_of(con, p["id"])
        have = {s["label"] for s in snaps}
        ages = [s["age_h"] for s in snaps if s["age_h"] is not None]
        label = window_label(age)
        if force:
            todo.append((p, label, t0))
            continue
        if age > LAST_WINDOW_H:
            continue
        if label in WINDOW_HOURS and label not in have:
            todo.append((p, label, t0))
            continue
        missed = [lab for lab, h in WINDOWS if lab not in have and age > h + TOLERANCE_H and not any(a > h + TOLERANCE_H for a in ages)]
        if missed:
            todo.append((p, label, t0))
    return todo


def store(con, pub, label, metrics, platform):
    age = metrics.get("age_h")
    if label in WINDOW_HOURS and age is not None and abs(age - WINDOW_HOURS[label]) > TOLERANCE_H:
        label = window_label(age)
    con.execute("INSERT OR REPLACE INTO analytics_snapshots (publication_id, label, captured_at, metrics, age_h, platform, published_ref) VALUES (?,?,?,?,?,?,?)",
                (pub["id"], label, db.now(), json.dumps(metrics, ensure_ascii=False), age, platform, metrics.get("published_ref")))
    return label


def latest_metrics(con, pub_id):
    r = con.execute("SELECT metrics FROM analytics_snapshots WHERE publication_id=? ORDER BY captured_at DESC LIMIT 1", (pub_id,)).fetchone()
    return json.loads(r["metrics"]) if r else None


def snapshot_due(force=False, label_override=None, platforms=("youtube", "instagram")):
    done, errors = [], []
    with db.connect() as con:
        if "instagram" in platforms:
            sync_instagram_publications(con)
        todo = due(con, force, platforms)
    yt = ya = ig = None
    for p, label, t0 in todo:
        try:
            if p["platform"] == "youtube":
                if yt is None:
                    yt, ya = services()
                with db.connect() as con:
                    prev = (latest_metrics(con, p["id"]) or {}).get("by_day")
                m = fetch_metrics(yt, ya, p["platform_id"], t0, prev if isinstance(prev, list) else None)
                value = m.get("public_counters", {}).get("viewCount")
            else:
                ig = ig or ig_config()
                m = fetch_instagram(p["platform_id"], t0, ctx=ig)
                value = m.get("insights", {}).get("views")
            with db.connect() as con:
                lab = store(con, p, label_override or label, m, p["platform"])
            done.append((p["variant_id"], p["platform"], lab, value))
        except SystemExit as e:
            errors.append((p["variant_id"], p["platform"], scrub(str(e))[:200]))
        except Exception as e:
            errors.append((p["variant_id"], p["platform"], scrub(f"{type(e).__name__}: {e}")[:200]))
    return done, errors


def relabel(dry_run=False):
    changes = []
    with db.connect() as con:
        rows = con.execute("SELECT s.*, p.platform AS pplatform, p.published_at, p.scheduled_for FROM analytics_snapshots s JOIN publications p ON p.id=s.publication_id ORDER BY s.publication_id, s.captured_at").fetchall()
        taken = {}
        for r in rows:
            ref = r["published_at"] or r["scheduled_for"]
            m = json.loads(r["metrics"])
            age = age_hours(r["captured_at"], ref)
            new = window_label(age)
            key = (r["publication_id"], new)
            if key in taken:
                new = f"{new}_s{r['id']}"
            taken[(r["publication_id"], new)] = r["id"]
            changes.append({"id": r["id"], "publication_id": r["publication_id"], "old": r["label"], "new": new, "age_h": age, "captured_at": r["captured_at"], "published_ref": ref})
        if not dry_run:
            for c in changes:
                con.execute("UPDATE analytics_snapshots SET label=? WHERE id=?", (f"tmp_{c['id']}", c["id"]))
            for c, r in zip(changes, rows):
                m = json.loads(r["metrics"])
                if c["old"] != c["new"]:
                    m.setdefault("label_history", []).append({"label": c["old"], "relabelled_at": db.now(), "reason": "D2: label from age_h = captured_at - published_at (±12 h)"})
                m["age_h"], m["published_ref"] = c["age_h"], c["published_ref"]
                con.execute("UPDATE analytics_snapshots SET label=?, age_h=?, platform=?, published_ref=?, metrics=? WHERE id=?",
                            (c["new"], c["age_h"], r["pplatform"], c["published_ref"], json.dumps(m, ensure_ascii=False), c["id"]))
    return changes


def window_value(con, pub, label, metric="views"):
    snaps = snapshots_of(con, pub["id"])
    if pub["platform"] == "youtube":
        for s in reversed(snaps):
            w = (json.loads(s["metrics"]).get("windows") or {}).get(label)
            if w and w.get(metric) is not None:
                return w[metric], f"by_day window (snapshot #{s['id']})"
        for s in snaps:
            if s["label"] == label:
                m = json.loads(s["metrics"])
                if metric == "views" and m.get("public_counters", {}).get("viewCount") is not None:
                    return m["public_counters"]["viewCount"], f"public viewCount at age {s['age_h']} h (snapshot #{s['id']})"
        return None, None
    for s in snaps:
        if s["label"] == label:
            v = (json.loads(s["metrics"]).get("insights") or {}).get(metric)
            if v is not None:
                return v, f"Instagram lifetime insight at age {s['age_h']} h (snapshot #{s['id']})"
    return None, None


def publications(con, platform=None):
    q = """SELECT p.*, COALESCE(v.language, substr(p.variant_id, 7)) AS language, substr(p.variant_id, 1, 5) AS content_id, c.episode
           FROM publications p LEFT JOIN variants v ON v.id=p.variant_id LEFT JOIN contents c ON c.id=substr(p.variant_id, 1, 5)"""
    rows = con.execute(q + (" WHERE p.platform=?" if platform else ""), ((platform,) if platform else ())).fetchall()
    return rows


def equal_window_table(label="48h", platform="youtube", metric="views"):
    out = []
    with db.connect() as con:
        for p in publications(con, platform):
            val, src = window_value(con, p, label, metric)
            if val is None:
                continue
            out.append({"variant": p["variant_id"], "content_id": p["content_id"], "episode": p["episode"], "language": p["language"], "platform": p["platform"],
                        "slot": p["slot"], "published_at": publication_time(p), "views": val, "source": src})
    return out


def median_or_none(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def retention_insights(curve):
    if not isinstance(curve, list) or not curve:
        return []
    pts = sorted((float(r["elapsedVideoTimeRatio"]), float(r["audienceWatchRatio"])) for r in curve)
    notes = []
    early = [w for t, w in pts if t <= 0.1]
    if early and min(early) < 0.6:
        notes.append(f"Large early drop: watch ratio falls to {min(early):.2f} within the first 10% of the video. Review the hook and first visual.")
    drops = [(pts[i][0], pts[i - 1][1] - pts[i][1]) for i in range(1, len(pts))]
    for t, d in sorted(drops, key=lambda d: -d[1])[:3]:
        if d > 0.05:
            notes.append(f"Steep drop of {d:.2f} around {t:.0%} of runtime; check which scene plays there.")
    rewatch = [t for t, w in pts if w > 1.0]
    if rewatch:
        notes.append(f"Rewatch/loop signal (watch ratio > 1.0) at {min(rewatch):.0%}–{max(rewatch):.0%} of runtime.")
    return notes


def latest(con, pub_id):
    return latest_metrics(con, pub_id)


def report(variant_id):
    with db.connect() as con:
        pubs = con.execute("SELECT * FROM publications WHERE variant_id=?", (variant_id,)).fetchall()
        lines = [f"# Performance report: {variant_id}", ""]
        for p in pubs:
            lines += [f"## {p['platform']} · {p['url']}", f"Published: {publication_time(p)} · slot: {p['slot'] or '-'}", ""]
            snaps = snapshots_of(con, p["id"])
            if not snaps:
                lines += ["No analytics snapshot yet. Run `python -m pipeline analytics`.", ""]
                continue
            lines.append("| label | age_h | captured_at | views |")
            lines.append("|---|---|---|---|")
            for s in snaps:
                m = json.loads(s["metrics"])
                v = m.get("insights", {}).get("views") if p["platform"] == "instagram" else m.get("public_counters", {}).get("viewCount")
                lines.append(f"| {s['label']} | {s['age_h']} | {s['captured_at']} | {v} |")
            m = json.loads(snaps[-1]["metrics"])
            if p["platform"] == "instagram":
                lines.append(f"- Latest insights: {m.get('insights')}")
                if m.get("unsupported"):
                    lines.append(f"- Unavailable metrics: {m['unsupported']}")
            else:
                tot = m.get("totals_to_date", m.get("totals"))
                lines.append(f"- Analytics totals to capture date: {tot[0] if isinstance(tot, list) and tot else tot}")
                if m.get("windows"):
                    lines.append("- Windows from by_day: " + ", ".join(f"{k} {v['views']} views" for k, v in m["windows"].items()))
                ts = m.get("traffic_sources")
                if isinstance(ts, list) and ts:
                    lines.append("- Traffic sources: " + ", ".join(f"{r['insightTrafficSourceType']} {r['views']}" for r in ts))
                for n in retention_insights(m.get("retention")):
                    lines.append(f"- Retention: {n}")
            lines.append("")
        lines.append("Compare variants only at equal windows and within one language (`python -m pipeline report --weekly`).")
        return "\n".join(lines) + "\n"


def agent_spec():
    log = DATA / "logs" / "analytics-daily.log"
    return {
        "Label": AGENT_LABEL,
        "ProgramArguments": [sys.executable, "-m", "pipeline", "analytics", "--insights"],
        "WorkingDirectory": str(ROOT),
        "StartCalendarInterval": {"Hour": DAILY_AT[0], "Minute": DAILY_AT[1]},
        "StandardOutPath": str(log),
        "StandardErrorPath": str(log),
        "EnvironmentVariables": {"PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin", "PYTHONUNBUFFERED": "1"},
    }


def install_daily(dry_run=False):
    spec = agent_spec()
    cmds = [f"launchctl bootout gui/{os.getuid()}/{AGENT_LABEL}", f"launchctl bootstrap gui/{os.getuid()} {AGENT_PLIST}"]
    if dry_run:
        return spec, cmds, False
    (DATA / "logs").mkdir(parents=True, exist_ok=True)
    AGENT_PLIST.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{AGENT_LABEL}"], capture_output=True)
    AGENT_PLIST.write_bytes(plistlib.dumps(spec))
    r = subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(AGENT_PLIST)], capture_output=True, text=True)
    return spec, cmds, r.returncode == 0


def uninstall_daily():
    subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{AGENT_LABEL}"], capture_output=True)
    existed = AGENT_PLIST.exists()
    if existed:
        AGENT_PLIST.unlink()
    return existed
