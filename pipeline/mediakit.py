import json
import re
from datetime import datetime, timezone
from pathlib import Path

from . import DATA, ROOT, db, gates, promo

NA = "not yet available"
TEMPLATE = ROOT / "docs" / "MEDIA_KIT.md"
SECRETS = ROOT / "secrets"


def fmt_int(v):
    return f"{int(v):,}" if v is not None else NA


def fmt_pct(v):
    return f"{v * 100:.1f}%" if v is not None else NA


def avg(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def latest_snapshots(con):
    rows = con.execute(
        "SELECT p.variant_id, p.platform, p.url, p.platform_id, s.metrics, s.captured_at, s.label FROM analytics_snapshots s "
        "JOIN publications p ON p.id = s.publication_id WHERE s.id IN (SELECT MAX(id) FROM analytics_snapshots GROUP BY publication_id) "
        "AND (p.published_at IS NOT NULL OR p.scheduled_for <= ?) AND s.label NOT LIKE 'prepublish%'", (utc_now(),)).fetchall()
    out = []
    for r in rows:
        try:
            met = json.loads(r["metrics"])
        except (TypeError, ValueError):
            continue
        out.append({**dict(r), "m": met})
    return out


def ig_numbers(m):
    ins = m.get("insights") or {}
    f = m.get("fields") or {}
    if not ins:
        return None
    views = ins.get("views")
    eng = sum(v for v in (ins.get("likes", f.get("like_count")), ins.get("comments", f.get("comments_count")), ins.get("shares"), ins.get("saved")) if v is not None)
    return {"views": views, "reach": ins.get("reach"), "engagement": eng}


def yt_numbers(m):
    pc = m.get("public_counters") or {}
    views = pc.get("viewCount")
    if views is None:
        return None
    eng = sum(v for v in (pc.get("likeCount"), pc.get("commentCount")) if v is not None)
    return {"views": views, "engagement": eng}


def rate(items):
    v = sum(i["views"] for i in items if i.get("views"))
    return (sum(i["engagement"] for i in items if i.get("views")) / v) if v else None


def countries(snaps):
    tally = {}
    for s in snaps:
        rows = s["m"].get("countries")
        for c in rows if isinstance(rows, list) else []:
            if not isinstance(c, dict):
                continue
            code = c.get("country") or c.get("code")
            views = c.get("views")
            if code and isinstance(views, (int, float)):
                tally[code] = tally.get(code, 0) + views
    if not tally:
        return NA
    total = sum(tally.values()) or 1
    top = sorted(tally.items(), key=lambda kv: -kv[1])[:5]
    return ", ".join(f"{k} {v / total * 100:.0f}%" for k, v in top)


def lookup_instagram():
    try:
        from . import analytics

        instagram, cfg = analytics.ig_config()
        code, body = analytics.ig_get(f"{instagram.graph(cfg)}/{cfg['ig_user_id']}", {"fields": "followers_count,media_count,username"}, cfg["access_token"], timeout=20)
        if code == 200 and isinstance(body, dict):
            return {"followers": body.get("followers_count"), "media": body.get("media_count")}
    except (SystemExit, Exception):
        pass
    return {}


def lookup_youtube():
    token = SECRETS / "youtube_analytics_token.json"
    if not token.exists():
        return {}
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_authorized_user_file(str(token), ["https://www.googleapis.com/auth/youtube.readonly"])
        if not creds.valid and creds.refresh_token:
            creds.refresh(Request())
        if not creds.valid:
            return {}
        items = build("youtube", "v3", credentials=creds, cache_discovery=False).channels().list(part="statistics", mine=True).execute().get("items", [])
        if not items:
            return {}
        st = items[0].get("statistics", {})
        return {"subscribers": None if st.get("hiddenSubscriberCount") else st.get("subscriberCount"), "views": st.get("viewCount")}
    except Exception:
        return {}


def build(con, live=True, b=None, today=None):
    b = b or promo.load()
    snaps = latest_snapshots(con)
    ig = [dict(s, n=ig_numbers(s["m"])) for s in snaps if s["platform"] == "instagram"]
    yt = [dict(s, n=yt_numbers(s["m"])) for s in snaps if s["platform"] == "youtube"]
    ig_ok = [s for s in ig if s["n"]]
    yt_ok = [s for s in yt if s["n"]]
    pubs = {r["platform"]: r["n"] for r in con.execute("SELECT platform, COUNT(*) AS n FROM publications WHERE published_at IS NOT NULL OR scheduled_for <= ? GROUP BY platform", (utc_now(),))}
    igl = lookup_instagram() if live else {}
    ytl = lookup_youtube() if live else {}
    best = []
    for label, items in (("Instagram", ig_ok), ("YouTube", yt_ok)):
        for s in sorted(items, key=lambda s: -(s["n"]["views"] or 0))[:3]:
            best.append(f"- {label} · {s['variant_id']} · {fmt_int(s['n']['views'])} views (snapshot {s['captured_at'][:10]}, {s['label']}) · {s['url'] or s['platform_id']}")
    yt_cfg = b["youtube"]
    renamed = yt_cfg.get("status") != "rename pending"
    v = {
        "brand_name": b["name"], "tagline": b.get("tagline", ""), "positioning": b.get("positioning", ""),
        "generated": today or datetime.now(gates.IST).strftime("%Y-%m-%d"),
        "data_through": max((s["captured_at"][:16] for s in snaps), default=NA),
        "instagram_handle": b["instagram"]["handle"], "instagram_url": b["instagram"]["url"],
        "youtube_name": yt_cfg["planned_name"] if renamed else yt_cfg["current_name"], "youtube_url": yt_cfg["active_url"],
        "youtube_rename_note": "" if renamed else f" (rename to {yt_cfg['planned_name']} pending)",
        "languages": " · ".join((b.get("languages") or {}).values()) or NA,
        "categories": "\n".join(f"- {c}" for c in b.get("categories", [])) or NA,
        "demographics": NA,
        "yt_countries": countries(yt),
        "ig_followers": fmt_int(igl.get("followers")) if igl.get("followers") is not None else NA,
        "ig_reels": fmt_int(pubs.get("instagram")) if pubs.get("instagram") else NA,
        "ig_avg_views": fmt_int(avg([s["n"]["views"] for s in ig_ok])) if ig_ok else NA,
        "ig_avg_reach": fmt_int(avg([s["n"]["reach"] for s in ig_ok])) if ig_ok and avg([s["n"]["reach"] for s in ig_ok]) is not None else NA,
        "ig_engagement": fmt_pct(rate([s["n"] for s in ig_ok])) if ig_ok else NA,
        "ig_sample": f"{len(ig_ok)} of {len(ig)} with snapshots" if ig else NA,
        "yt_subscribers": fmt_int(ytl.get("subscribers")) if ytl.get("subscribers") is not None else NA,
        "yt_channel_views": fmt_int(ytl.get("views")) if ytl.get("views") is not None else NA,
        "yt_videos": fmt_int(pubs.get("youtube")) if pubs.get("youtube") else NA,
        "yt_avg_views": fmt_int(avg([s["n"]["views"] for s in yt_ok])) if yt_ok else NA,
        "yt_engagement": fmt_pct(rate([s["n"] for s in yt_ok])) if yt_ok else NA,
        "yt_sample": f"{len(yt_ok)} of {len(yt)} with snapshots" if yt else NA,
        "best": "\n".join(best) or NA,
        "email": b["email"],
        "formats": "; ".join(b.get("partnership_formats", [])) or NA,
    }
    return v


def fill(template, values):
    return re.sub(r"\{\{(\w+)\}\}", lambda mt: str(values.get(mt.group(1), NA)), template)


def write(values, out_dir=None, template=None):
    out_dir = Path(out_dir or DATA / "reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"media-kit-{values['generated']}.md"
    path.write_text(fill(Path(template or TEMPLATE).read_text(), values))
    return path


def cli(a):
    with db.connect() as con:
        values = build(con, live=not a.offline)
    path = write(values)
    print(f"wrote {gates.rel(path)}")
    missing = sorted(k for k, val in values.items() if val == NA)
    if missing:
        print("not yet available: " + ", ".join(missing))
