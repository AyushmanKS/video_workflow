import json
import statistics
from datetime import datetime, timedelta, timezone

from . import db
from .research import retry

WINDOWS = [("24h", 1), ("48h", 2), ("7d", 7), ("14d", 14), ("30d", 30)]
CORE = "views,engagedViews,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,comments,shares,subscribersGained,subscribersLost"


def services():
    import publish

    return publish.analytics_services()


def parse_time(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def table(resp):
    cols = [h["name"] for h in resp.get("columnHeaders", [])]
    return [dict(zip(cols, r)) for r in resp.get("rows", [])]


def fetch_metrics(yt, ya, video_id, published):
    out = {"captured_at": db.now(), "video_id": video_id}
    v = retry(lambda: yt.videos().list(part="statistics,snippet,status,contentDetails", id=video_id).execute())["items"]
    if not v:
        out["error"] = "video not found"
        return out
    v = v[0]
    out["public_counters"] = {k: int(x) for k, x in v.get("statistics", {}).items()}
    out["privacy"] = v["status"]["privacyStatus"]
    start = (published or parse_time(v["snippet"]["publishedAt"])).date().isoformat()
    end = datetime.now(timezone.utc).date().isoformat()
    q = dict(ids="channel==MINE", startDate=start, endDate=end, filters=f"video=={video_id}")
    for key, extra in {
        "totals": dict(metrics=CORE),
        "by_day": dict(metrics="views,estimatedMinutesWatched,averageViewPercentage", dimensions="day", sort="day"),
        "traffic_sources": dict(metrics="views,estimatedMinutesWatched", dimensions="insightTrafficSourceType", sort="-views"),
        "countries": dict(metrics="views,estimatedMinutesWatched", dimensions="country", sort="-views", maxResults=10),
        "retention": dict(metrics="audienceWatchRatio,relativeRetentionPerformance", dimensions="elapsedVideoTimeRatio"),
    }.items():
        try:
            out[key] = table(retry(lambda: ya.reports().query(**q, **extra).execute()))
        except Exception as e:
            if key == "totals" and "engagedViews" in extra["metrics"]:
                try:
                    out[key] = table(retry(lambda: ya.reports().query(**q, metrics=extra["metrics"].replace("engagedViews,", "")).execute()))
                    out["note_engaged"] = "engagedViews not accepted for this query: " + str(e)[:160]
                    continue
                except Exception as e2:
                    e = e2
            out[key] = {"unavailable": str(e)[:240]}
    out["note"] = "YouTube Analytics data typically lags 1-3 days; empty tables right after publishing are expected."
    return out


def due(con, force=False):
    now = datetime.now(timezone.utc)
    rows = con.execute("SELECT * FROM publications WHERE platform='youtube'").fetchall()
    todo = []
    for p in rows:
        t0 = parse_time(p["published_at"] or p["scheduled_for"])
        if not t0:
            continue
        if t0.tzinfo is None:
            t0 = t0.replace(tzinfo=timezone.utc)
        have = {r["label"] for r in con.execute("SELECT label FROM analytics_snapshots WHERE publication_id=?", (p["id"],))}
        for label, days in WINDOWS:
            if label not in have and (force or now >= t0 + timedelta(days=days)):
                todo.append((p, label, t0))
                break
    return todo


def snapshot_due(force=False, label_override=None):
    yt, ya = services()
    done = []
    with db.connect() as con:
        for p, label, t0 in due(con, force):
            m = fetch_metrics(yt, ya, p["platform_id"], t0)
            lab = label_override or label
            con.execute("INSERT OR REPLACE INTO analytics_snapshots (publication_id, label, captured_at, metrics) VALUES (?,?,?,?)", (p["id"], lab, db.now(), json.dumps(m, ensure_ascii=False)))
            done.append((p["variant_id"], lab, m.get("public_counters", {}).get("viewCount")))
    return done


def retention_insights(curve):
    if not isinstance(curve, list) or not curve:
        return []
    pts = sorted((float(r["elapsedVideoTimeRatio"]), float(r["audienceWatchRatio"])) for r in curve)
    notes = []
    early = [w for t, w in pts if t <= 0.1]
    if early and min(early) < 0.6:
        notes.append(f"Large early drop: watch ratio falls to {min(early):.2f} within the first 10% of the video. Review the hook and first visual.")
    drops = [(pts[i][0], pts[i - 1][1] - pts[i][1]) for i in range(1, len(pts))]
    worst = sorted(drops, key=lambda d: -d[1])[:3]
    for t, d in worst:
        if d > 0.05:
            notes.append(f"Steep drop of {d:.2f} around {t:.0%} of runtime; check which scene plays there.")
    rewatch = [t for t, w in pts if w > 1.0]
    if rewatch:
        notes.append(f"Rewatch/loop signal (watch ratio > 1.0) at {min(rewatch):.0%}–{max(rewatch):.0%} of runtime.")
    return notes


def latest(con, pub_id):
    r = con.execute("SELECT * FROM analytics_snapshots WHERE publication_id=? ORDER BY captured_at DESC LIMIT 1", (pub_id,)).fetchone()
    return json.loads(r["metrics"]) if r else None


def report(variant_id):
    with db.connect() as con:
        pubs = con.execute("SELECT * FROM publications WHERE variant_id=?", (variant_id,)).fetchall()
        allpubs = con.execute("SELECT p.*, v.language FROM publications p LEFT JOIN variants v ON v.id=p.variant_id").fetchall()
        others = {p["variant_id"]: latest(con, p["id"]) for p in allpubs}
        lang = {p["variant_id"]: p["language"] for p in allpubs}
        lines = [f"# Performance report: {variant_id}", ""]
        for p in pubs:
            m = latest(con, p["id"])
            lines += [f"## {p['platform']} · {p['url']}", f"Published: {p['published_at'] or p['scheduled_for']} · slot: {p['slot'] or '-'}", ""]
            if not m:
                lines += ["No analytics snapshot yet. Run `python -m pipeline analytics`.", ""]
                continue
            pc, tot = m.get("public_counters", {}), m.get("totals")
            lines.append(f"- Public counters: {pc}")
            lines.append(f"- Analytics totals: {tot[0] if isinstance(tot, list) and tot else tot}")
            ts = m.get("traffic_sources")
            if isinstance(ts, list) and ts:
                lines.append("- Traffic sources: " + ", ".join(f"{r['insightTrafficSourceType']} {r['views']}" for r in ts))
            cs = m.get("countries")
            if isinstance(cs, list) and cs:
                lines.append("- Top countries: " + ", ".join(f"{r['country']} {r['views']}" for r in cs[:5]))
            for n in retention_insights(m.get("retention")):
                lines.append(f"- Retention: {n}")
            views = {k: (v or {}).get("public_counters", {}).get("viewCount") for k, v in others.items() if v}
            if len(views) > 1:
                lines += ["", "### Comparison with other published videos (latest snapshot, views)"]
                for k, val in sorted(views.items(), key=lambda kv: -(kv[1] or 0)):
                    lines.append(f"- {k} ({lang.get(k) or '?'}): {val}")
            lines.append("")
        lines.append("Caution: comparisons across videos of different ages are not like-for-like. Compare equal windows (24h vs 24h) once enough snapshots exist.")
        return "\n".join(lines) + "\n"


def equal_window_table(label="48h"):
    with db.connect() as con:
        rows = con.execute("""SELECT p.variant_id, p.slot, p.published_at, v.language, s.metrics FROM analytics_snapshots s
                              JOIN publications p ON p.id=s.publication_id LEFT JOIN variants v ON v.id=p.variant_id WHERE s.label=?""", (label,)).fetchall()
    out = []
    for r in rows:
        m = json.loads(r["metrics"])
        tot = m.get("totals")
        t = tot[0] if isinstance(tot, list) and tot else {}
        out.append({"variant": r["variant_id"], "language": r["language"], "slot": r["slot"], "published_at": r["published_at"],
                    "views": m.get("public_counters", {}).get("viewCount"), "avg_view_pct": t.get("averageViewPercentage"), "avg_view_s": t.get("averageViewDuration")})
    return out


def median_or_none(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None
