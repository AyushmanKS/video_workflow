import hashlib
import json
import re
import statistics
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import requests

from . import DATA, PROFILES, db

UA = {"User-Agent": "shorts-studio/0.2 (content research; contact via repository)"}
CACHE = DATA / "cache"
CATEGORY_NAMES = {"1": "Film & Animation", "10": "Music", "17": "Sports", "20": "Gaming", "22": "People & Blogs", "23": "Comedy", "24": "Entertainment", "25": "News & Politics", "26": "Howto & Style", "27": "Education", "28": "Science & Technology"}


def cached(key, ttl_hours, fn):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (hashlib.sha1(key.encode()).hexdigest() + ".json")
    if path.exists() and time.time() - path.stat().st_mtime < ttl_hours * 3600:
        return json.loads(path.read_text())
    value = fn()
    path.write_text(json.dumps(value, ensure_ascii=False))
    return value


def retry(fn, attempts=3):
    for k in range(attempts):
        try:
            return fn()
        except Exception:
            if k == attempts - 1:
                raise
            time.sleep(2 * (k + 1))


def yt_read():
    import publish

    if (publish.SECRETS / "youtube_analytics_token.json").exists():
        return publish.analytics_services()[0]
    return publish.youtube_service()


def iso_seconds(d):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (3600, 60, 1))) if m else None


def video_rows(svc, ids):
    rows = []
    for i in range(0, len(ids), 50):
        r = retry(lambda: svc.videos().list(part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])).execute())
        for v in r.get("items", []):
            sn, stt = v["snippet"], v.get("statistics", {})
            rows.append({
                "id": v["id"], "title": sn["title"], "channel": sn["channelTitle"], "published": sn["publishedAt"],
                "language": sn.get("defaultAudioLanguage") or sn.get("defaultLanguage"),
                "category": CATEGORY_NAMES.get(sn.get("categoryId"), sn.get("categoryId")),
                "seconds": iso_seconds(v["contentDetails"].get("duration")),
                "views": int(stt.get("viewCount", 0)), "likes": int(stt.get("likeCount", 0)) if "likeCount" in stt else None,
                "comments": int(stt.get("commentCount", 0)) if "commentCount" in stt else None,
            })
    return rows


def yt_trending(region="IN", categories=("0", "1", "24", "25", "28"), per_category=25):
    def fetch():
        svc, out = yt_read(), {}
        for cat in categories:
            kw = dict(part="id", chart="mostPopular", regionCode=region, maxResults=per_category)
            if cat != "0":
                kw["videoCategoryId"] = cat
            try:
                ids = [v["id"] for v in retry(lambda: svc.videos().list(**kw).execute()).get("items", [])]
            except Exception as e:
                out[cat] = {"error": str(e)[:200]}
                continue
            out[cat] = video_rows(svc, ids)
        return {"source": "YouTube Data API videos.list chart=mostPopular", "region": region, "captured_at": db.now(), "charts": out}

    return cached(f"trending:{region}:{','.join(categories)}:{per_category}", 6, fetch)


def yt_competition(query, region="IN", language=None, max_results=25):
    def fetch():
        svc = yt_read()
        after = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        base = dict(part="id", q=query, type="video", regionCode=region, maxResults=max_results)
        if language:
            base["relevanceLanguage"] = language
        top = retry(lambda: svc.search().list(order="viewCount", **base).execute())
        recent = retry(lambda: svc.search().list(order="date", publishedAfter=after, **base).execute())
        top_rows = video_rows(svc, [i["id"]["videoId"] for i in top.get("items", [])])
        recent_rows = video_rows(svc, [i["id"]["videoId"] for i in recent.get("items", [])])
        shorts = [r for r in top_rows if r["seconds"] and r["seconds"] <= 180]
        views = [r["views"] for r in top_rows]
        return {
            "source": "YouTube Data API search.list + videos.list", "query": query, "region": region, "language": language,
            "captured_at": db.now(), "approx_total_results": top.get("pageInfo", {}).get("totalResults"),
            "top_by_views": top_rows, "recent_30d": recent_rows,
            "summary": {
                "top_median_views": int(statistics.median(views)) if views else 0,
                "top_max_views": max(views) if views else 0,
                "share_shorts_in_top": round(len(shorts) / len(top_rows), 2) if top_rows else 0,
                "recent_30d_uploads_sampled": len(recent_rows),
                "recent_30d_median_views": int(statistics.median([r["views"] for r in recent_rows])) if recent_rows else 0,
                "distinct_channels_top": len({r["channel"] for r in top_rows}),
            },
            "quota_units": 202,
        }

    return cached(f"competition:{query}:{region}:{language}:{max_results}", 24, fetch)


def wiki_langlinks(en_title, langs):
    def fetch():
        r = retry(lambda: requests.get("https://en.wikipedia.org/w/api.php", params={"action": "query", "titles": en_title, "prop": "langlinks", "lllimit": 500, "redirects": 1, "format": "json"}, headers=UA, timeout=30).json())
        page = next(iter(r["query"]["pages"].values()))
        links = {l["lang"]: l["*"] for l in page.get("langlinks", [])}
        return {lang: (en_title if lang == "en" else links.get(lang)) for lang in langs}

    return cached(f"langlinks:{en_title}:{','.join(langs)}", 168, fetch)


def wiki_pageviews(lang, title, months=6):
    end = datetime.now(timezone.utc).replace(day=1) - timedelta(days=1)
    start = (end.replace(day=1) - timedelta(days=31 * (months - 1))).replace(day=1)
    url = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{lang}.wikipedia/all-access/user/"
           f"{quote(title.replace(' ', '_'), safe='')}/monthly/{start:%Y%m%d}/{end:%Y%m%d}")

    def fetch():
        r = requests.get(url, headers=UA, timeout=30)
        if r.status_code == 404:
            return {"lang": lang, "title": title, "monthly": [], "note": "no data"}
        r.raise_for_status()
        return {"lang": lang, "title": title, "monthly": [(i["timestamp"][:6], i["views"]) for i in r.json().get("items", [])]}

    return cached(f"pv:{lang}:{title}:{months}:{end:%Y%m}", 24, lambda: retry(fetch))


def wiki_interest(en_title, langs, months=6):
    titles = wiki_langlinks(en_title, langs)
    out = {}
    for lang, title in titles.items():
        if not title:
            out[lang] = {"title": None, "note": "no article in this language Wikipedia"}
            continue
        pv = wiki_pageviews(lang, title, months)
        vals = [v for _, v in pv["monthly"]]
        trend = round((vals[-1] - statistics.mean(vals[:-1])) / max(1, statistics.mean(vals[:-1])), 2) if len(vals) >= 3 else None
        out[lang] = {"title": title, "monthly": pv["monthly"], "last_month": vals[-1] if vals else None, "change_vs_prior_avg": trend}
    return {"source": "Wikimedia REST pageviews (user agents, monthly)", "en_title": en_title, "captured_at": db.now(), "languages": out}


def yt_suggestions(query, lang="en"):
    def fetch():
        r = requests.get("https://suggestqueries.google.com/complete/search", params={"client": "firefox", "ds": "yt", "q": query, "hl": lang}, headers=UA, timeout=20)
        r.raise_for_status()
        return {"source": "Google autocomplete (YouTube, unofficial endpoint; may change)", "query": query, "lang": lang, "suggestions": r.json()[1]}

    try:
        return cached(f"suggest:{query}:{lang}", 24, fetch)
    except Exception as e:
        return {"source": "Google autocomplete", "query": query, "error": str(e)[:200]}


def topic_report(topic, query, en_wiki_title, langs, content_id=None, region="IN"):
    comp = {}
    for lang in langs:
        q = query.get(lang) if isinstance(query, dict) else query
        if q:
            comp[lang] = yt_competition(q, region=region, language=lang)
    report = {
        "topic": topic, "generated_at": db.now(),
        "wikipedia_interest": wiki_interest(en_wiki_title, langs),
        "youtube_competition": comp,
        "search_suggestions": {lang: yt_suggestions(query.get(lang) if isinstance(query, dict) else query, lang) for lang in langs},
    }
    with db.connect() as con:
        con.execute("INSERT INTO research (content_id, query, source, payload, captured_at) VALUES (?,?,?,?,?)",
                    (content_id, json.dumps(query, ensure_ascii=False), "topic_report", json.dumps(report, ensure_ascii=False), db.now()))
    return report


def report_markdown(rep):
    lines = [f"# Research evidence: {rep['topic']}", "", f"Generated {rep['generated_at']}. All figures come from the named API at capture time; nothing here is estimated.", ""]
    wi = rep["wikipedia_interest"]
    lines += ["## Wikipedia interest by language (monthly user pageviews)", "", "| Lang | Article | Last month | Change vs prior avg | Series |", "|---|---|---|---|---|"]
    for lang, d in wi["languages"].items():
        series = ", ".join(f"{m[4:]}/{m[2:4]}:{v}" for m, v in d.get("monthly", []))
        chg = d.get("change_vs_prior_avg")
        lines.append(f"| {lang} | {d.get('title') or '-'} | {d.get('last_month') or '-'} | {'' if chg is None else f'{chg:+.0%}'} | {series or d.get('note', '')} |")
    lines += ["", "## YouTube competition (India)", ""]
    for lang, c in rep["youtube_competition"].items():
        s = c["summary"]
        lines += [f"### {lang}: \"{c['query']}\"", "",
                  f"- Top-25 by views: median {s['top_median_views']:,}, max {s['top_max_views']:,}, Shorts share {s['share_shorts_in_top']:.0%}, distinct channels {s['distinct_channels_top']}",
                  f"- Uploads in last 30 days (sample of 25): median views {s['recent_30d_median_views']:,}",
                  "- Top 5:"]
        for r in c["top_by_views"][:5]:
            lines.append(f"  - {r['views']:,} views · {r['seconds']}s · {r['channel']} · {r['title'][:80]}")
        lines.append("")
    lines += ["## Search suggestions (YouTube autocomplete, unofficial)", ""]
    for lang, s in rep["search_suggestions"].items():
        lines.append(f"- {lang}: " + ("; ".join(s.get("suggestions", [])[:8]) or s.get("error", "none")))
    return "\n".join(lines) + "\n"


def trending_markdown(tr, limit=10):
    lines = [f"# YouTube trending, {tr['region']} ({tr['captured_at']})", "", f"Source: {tr['source']}. Education (27) has no regional chart, so it is not listed.", ""]
    for cat, rows in tr["charts"].items():
        name = "All" if cat == "0" else CATEGORY_NAMES.get(cat, cat)
        lines.append(f"## {name}")
        if isinstance(rows, dict):
            lines += [f"- unavailable: {rows['error']}", ""]
            continue
        for r in rows[:limit]:
            lines.append(f"- {r['views']:,} · {r['seconds']}s · {r['language'] or '-'} · {r['channel']} · {r['title'][:80]}")
        lines.append("")
    return "\n".join(lines)
