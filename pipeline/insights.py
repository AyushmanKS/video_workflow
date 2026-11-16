import json
import math
import statistics
import subprocess
from datetime import datetime, timedelta, timezone

from . import CONTENT, db, learn
from .analytics import parse_time, publication_time, publications
from .report import REPORTS, fmt

LATEST = REPORTS / "latest_insights.json"
MIN_N = learn.MIN_N
MIN_AGE_H = 48
MAX_ACTIONS = 5
STALE_H = 12
TARGET_S = (35, 55)
HOOK_MAX_S = 3.0
SHORT_SHAPE_WATCH_S = 25
LOW_WATCH_S = 8
LOW_RATIO_FACTOR = 0.5
RAW = ("views", "reach", "likes", "comments", "shares", "saves", "avg_watch_s", "subscribers_gained")
BUCKETS = [(0, 12, "<12h"), (12, 36, "24h"), (36, 60, "48h"), (60, 156, "3-6d"), (156, 180, "7d"), (180, 324, "8-13d"),
           (324, 348, "14d"), (348, 708, "15-29d"), (708, 732, "30d"), (732, math.inf, ">30d")]
RULES = {"duration_target_s": list(TARGET_S), "hard_limit_s": 60, "hook_max_s": HOOK_MAX_S, "engagement_line_max_words": 6,
         "frame0_drawn_min": 0.7, "source": ".claude/skills/storytelling/SKILL.md (owner decisions O1, O5)"}
EVIDENCE = ["data/studio.db: publications, analytics_snapshots (metrics JSON, age_h), features (duration_s, engine_version), experiments",
            "content/<ID>/<lang>/<ID>-<lang>.mp4 (ffprobe duration when present)"]


def bucket(age_h):
    if age_h is None or age_h < 0:
        return None
    for lo, hi, name in BUCKETS:
        if lo <= age_h < hi:
            return name
    return None


def tier(n, min_age_h, confirmed=False):
    if confirmed:
        return "confirmed"
    if n < MIN_N or min_age_h is None or min_age_h < MIN_AGE_H:
        return "anecdote"
    return "directional"


def div(a, b):
    if a is None or b in (None, 0):
        return None
    return round(a / b, 4)


def num(x):
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def first_row(x):
    return x[0] if isinstance(x, list) and x and isinstance(x[0], dict) else {}


def ffprobe_duration(path):
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
                           capture_output=True, text=True, timeout=20)
        return round(float(r.stdout.strip()), 2) if r.returncode == 0 and r.stdout.strip() else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def duration_of(variant, features, probe=ffprobe_duration):
    cid, _, lang = variant.partition("-")
    mp4 = CONTENT / cid / lang / f"{variant}.mp4"
    if probe and mp4.exists():
        d = probe(mp4)
        if d:
            return d, f"ffprobe {mp4.relative_to(CONTENT.parent)}"
    f = features.get(variant) or {}
    if f.get("duration_s"):
        return round(float(f["duration_s"]), 2), f"features.duration_s ({f.get('duration_source') or 'unknown'})"
    return None, None


def extract(platform, m):
    if platform == "instagram":
        ins = m.get("insights") or {}
        if not ins or ins.get("views") is None:
            return None
        avg_ms = num(ins.get("ig_reels_avg_watch_time"))
        tot_ms = num(ins.get("ig_reels_video_view_total_time"))
        return {"views": num(ins.get("views")), "reach": num(ins.get("reach")), "likes": num(ins.get("likes")), "comments": num(ins.get("comments")),
                "shares": num(ins.get("shares")), "saves": num(ins.get("saved")), "avg_watch_s": round(avg_ms / 1000, 2) if avg_ms is not None else None,
                "total_watch_s": round(tot_ms / 1000, 1) if tot_ms is not None else None, "avg_view_pct": None, "subscribers_gained": None,
                "source": "Instagram insights (lifetime; watch times in ms → s)"}
    tot = first_row(m.get("totals_to_date")) or first_row(m.get("totals"))
    pc = m.get("public_counters") or {}
    if not tot and pc.get("viewCount") is None:
        return None
    views = num(tot.get("views")) if tot.get("views") is not None else num(pc.get("viewCount"))
    return {"views": views, "reach": None, "likes": num(tot.get("likes")) if tot.get("likes") is not None else num(pc.get("likeCount")),
            "comments": num(tot.get("comments")) if tot.get("comments") is not None else num(pc.get("commentCount")),
            "shares": num(tot.get("shares")), "saves": None, "avg_watch_s": num(tot.get("averageViewDuration")),
            "total_watch_s": round(num(tot["estimatedMinutesWatched"]) * 60, 1) if tot.get("estimatedMinutesWatched") is not None else None,
            "avg_view_pct": num(tot.get("averageViewPercentage")), "subscribers_gained": num(tot.get("subscribersGained")),
            "source": "YouTube Analytics totals_to_date" if tot else "YouTube public counters only (Analytics totals not yet available; 1-3 day lag)"}


def enrich(rec, duration):
    rec["duration_s"] = duration
    rec["watch_ratio"] = div(rec.get("avg_watch_s"), duration)
    if rec["watch_ratio"] is None and rec.get("avg_view_pct") is not None:
        rec["watch_ratio"] = round(rec["avg_view_pct"] / 100, 4)
    if rec["platform"] == "instagram":
        base, label = rec.get("reach"), "reach"
    else:
        base, label = rec.get("views"), "view"
    rec["ratios"] = {f"{k}_per_{label}": div(rec.get(k), base) for k in ("shares", "saves", "likes", "comments", "subscribers_gained") if rec.get(k) is not None}
    return rec


def load(days=None, now=None, probe=ffprobe_duration):
    now = now or datetime.now(timezone.utc)
    since = now - timedelta(days=days) if days else None
    obs = []
    with db.connect() as con:
        features = {r["variant_id"]: dict(r) for r in con.execute("SELECT * FROM features")}
        last = con.execute("SELECT MAX(captured_at) t FROM analytics_snapshots").fetchone()["t"]
        for p in publications(con):
            t0 = parse_time(publication_time(p))
            if not t0 or t0 > now or (since and t0 < since):
                continue
            for s in con.execute("SELECT * FROM analytics_snapshots WHERE publication_id=? ORDER BY captured_at", (p["id"],)):
                if s["age_h"] is None or s["age_h"] < 0:
                    continue
                vals = extract(p["platform"], json.loads(s["metrics"]))
                if not vals:
                    continue
                f = features.get(p["variant_id"]) or {}
                rec = {"variant": p["variant_id"], "content_id": p["content_id"], "language": p["language"], "platform": p["platform"],
                       "episode": p["episode"] if p["episode"] is not None else f.get("episode"), "cohort": db.cohort_for(p["language"]),
                       "engine_version": f.get("engine_version"), "snapshot_id": s["id"], "label": s["label"], "captured_at": s["captured_at"],
                       "age_h": s["age_h"], "bucket": bucket(s["age_h"]),
                       "snapshot_age_h": round((now - parse_time(s["captured_at"])).total_seconds() / 3600, 1), **vals}
                obs.append(rec)
    durs = {}
    for r in obs:
        if r["variant"] not in durs:
            durs[r["variant"]] = duration_of(r["variant"], features, probe)
        d, src = durs[r["variant"]]
        r["duration_source"] = src
        enrich(r, d)
    last_age = round((now - parse_time(last)).total_seconds() / 3600, 1) if last else None
    return obs, last_age


def latest_per_variant(obs):
    out = {}
    for r in obs:
        k = (r["variant"], r["platform"])
        if k not in out or r["captured_at"] > out[k]["captured_at"]:
            out[k] = r
    return sorted(out.values(), key=lambda r: (r["platform"], r["content_id"], r["language"]))


def groups(obs):
    g = {}
    for r in obs:
        k = (r["platform"], r["bucket"])
        cur = g.setdefault(k, {})
        if r["variant"] not in cur or r["captured_at"] > cur[r["variant"]]["captured_at"]:
            cur[r["variant"]] = r
    return {k: sorted(v.values(), key=lambda r: r["variant"]) for k, v in g.items()}


def language_medians(group_rows, metrics=("views", "watch_ratio")):
    out = []
    for metric in metrics:
        rows = [{**r, "views": r[metric]} for r in group_rows if r.get(metric) is not None]
        for r in learn.rolling_ratios(rows):
            out.append({"platform": r["platform"], "bucket": r["bucket"], "language": r["language"], "metric": metric, "variant": r["variant"],
                        "value": r["views"], "peers": r["peers"], "median": r["language_median"], "ratio": r["ratio"]})
    return out


def live_groups(gs):
    order = [b[2] for b in BUCKETS]
    keys = sorted(gs, key=lambda k: (k[0], order.index(k[1]) if k[1] in order else len(order)))
    keep = []
    for i, k in enumerate(keys):
        later = {r["variant"] for k2 in keys[i + 1:] if k2[0] == k[0] for r in gs[k2]}
        if not {r["variant"] for r in gs[k]} <= later:
            keep.append(k)
    return keep


def primary_group(gs, platform):
    live = set(live_groups(gs))
    cands = [(k, v) for k, v in gs.items() if k[0] == platform and k in live]
    if not cands:
        return None, []
    order = {b[2]: i for i, b in enumerate(BUCKETS)}
    k, v = max(cands, key=lambda kv: (len(kv[1]), order.get(kv[0][1], -1)))
    return k, v


def spearman(xs, ys):
    n = len(xs)
    if n < 3:
        return None

    def ranks(v):
        idx = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        for pos, i in enumerate(idx):
            r[i] = pos + 1.0
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num_ = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return round(num_ / den, 3) if den else None


def rng(vals, nd=0):
    vals = [v for v in vals if v is not None]
    if not vals:
        return "–"
    lo, hi = min(vals), max(vals)
    return f"{lo:.{nd}f}" if lo == hi else f"{lo:.{nd}f}–{hi:.{nd}f}"


def pct(x):
    return "–" if x is None else f"{x * 100:.1f}%"


class Builder:
    def __init__(self):
        self.findings, self.actions, self.conflicts = [], [], []

    def finding(self, text, n, min_age_h, platform=None, bucket_=None, metric=None, languages=(), variants=(), evidence=None, confirmed=False, kind="observation"):
        fid = f"F{len(self.findings) + 1}"
        t = tier(n, min_age_h, confirmed)
        self.findings.append({"id": fid, "kind": kind, "text": text, "tier": t, "n": n, "min_age_h": min_age_h, "platform": platform, "bucket": bucket_,
                              "metric": metric, "languages": sorted(set(languages)), "variants": list(variants), "evidence": evidence or []})
        return self.findings[-1]

    def action(self, text, f):
        if len(self.actions) >= MAX_ACTIONS:
            return
        self.actions.append({"id": f"A{len(self.actions) + 1}", "text": f"{text} ({f['tier']}, n={f['n']}; {f['id']})", "finding": f["id"], "tier": f["tier"], "n": f["n"]})

    def conflict(self, text, f):
        self.conflicts.append({"text": text, "finding": f["id"], "tier": f["tier"], "acted_on": False})


def snap_refs(rows):
    return [f"analytics_snapshots #{r['snapshot_id']} ({r['variant']} {r['platform']}, age {r['age_h']} h)" for r in rows]


def analyse_group(b, key, rows):
    platform, bk = key
    n = len(rows)
    min_age = min(r["age_h"] for r in rows)
    langs = [r["language"] for r in rows]
    ev = snap_refs(rows)
    out = {}
    watch = [r for r in rows if r.get("watch_ratio") is not None and r.get("avg_watch_s") is not None and r.get("duration_s")]
    if not watch:
        out["coverage"] = b.finding(f"{platform} {bk}: insufficient data for watch time ({n} variant(s) with counters only; {rows[0]['source']}).",
                                    n, min_age, platform, bk, "avg_watch_s", langs, [r["variant"] for r in rows], ev, kind="insufficient")
    else:
        med_w = statistics.median(r["avg_watch_s"] for r in watch)
        med_r = statistics.median(r["watch_ratio"] for r in watch)
        out["watch"] = b.finding(f"{platform} {bk}: average watch {rng([r['avg_watch_s'] for r in watch])} s (median {med_w:.1f} s) on {rng([r['duration_s'] for r in watch])} s videos; watch ratio {rng([r['watch_ratio'] for r in watch], 2)} (median {med_r:.2f}). Most viewers leave well before the end."
                                 if med_r < 0.5 else
                                 f"{platform} {bk}: average watch {rng([r['avg_watch_s'] for r in watch])} s on {rng([r['duration_s'] for r in watch])} s videos; watch ratio median {med_r:.2f}.",
                                 len(watch), min(r["age_h"] for r in watch), platform, bk, "watch_ratio", [r["language"] for r in watch], [r["variant"] for r in watch], snap_refs(watch))
        out["watch"]["median_avg_watch_s"], out["watch"]["median_watch_ratio"] = round(med_w, 2), round(med_r, 3)
        out["watch"]["avg_watch_range_s"], out["watch"]["duration_range_s"] = rng([r["avg_watch_s"] for r in watch]), rng([r["duration_s"] for r in watch])
        low = [r for r in watch if r["avg_watch_s"] < LOW_WATCH_S or (len(watch) > 1 and r["watch_ratio"] < LOW_RATIO_FACTOR * statistics.median(o["watch_ratio"] for o in watch if o is not r))]
        for r in low:
            others = [o["watch_ratio"] for o in watch if o is not r]
            cmp_ = f" vs median {statistics.median(others):.2f} for the other {len(others)} variant(s) at the same age" if others else ""
            cohort = " (gu/te are the unreviewed-language cohort; language quality is unverified)" if r["cohort"] else ""
            f = b.finding(f"{r['variant']} {platform} {bk}: avg watch {r['avg_watch_s']:.1f} s of {r['duration_s']:.0f} s, watch ratio {r['watch_ratio']:.2f}{cmp_}. {'Viewers drop in the opening seconds' if r['avg_watch_s'] < LOW_WATCH_S else 'It held a much smaller share than its same-age peers'}{cohort}.",
                          1, r["age_h"], platform, bk, "watch_ratio", [r["language"]], [r["variant"]], snap_refs([r]), kind="outlier")
            out.setdefault("low", []).append((f, r))
        if len(watch) >= 3:
            rho = spearman([r["duration_s"] for r in watch], [r["watch_ratio"] for r in watch])
            if rho is not None:
                pairs = ", ".join(f"{r['variant']} {r['duration_s']:.0f} s→{r['watch_ratio']:.2f}" for r in sorted(watch, key=lambda r: r["duration_s"]))
                direction = "longer videos held a smaller share" if rho < 0 else "longer videos held a larger share" if rho > 0 else "no ordering"
                out["duration"] = b.finding(f"{platform} {bk}: duration vs watch ratio rank correlation {rho:+.2f}: {direction} ({pairs}). Languages differ, so this mixes language and length.",
                                            len(watch), min(r["age_h"] for r in watch), platform, bk, "watch_ratio~duration", [r["language"] for r in watch], [r["variant"] for r in watch], snap_refs(watch), kind="association")
                out["duration"]["rho"], out["duration"]["pairs"], out["duration"]["direction"] = rho, pairs, direction
    eng = [r for r in rows if r.get("ratios")]
    if eng:
        keys = sorted({k for r in eng for k in r["ratios"]})
        parts = []
        meds = {}
        for k in keys:
            vals = [r["ratios"][k] for r in eng if r["ratios"].get(k) is not None]
            if vals:
                meds[k] = statistics.median(vals)
                parts.append(f"{k} {pct(min(vals))}–{pct(max(vals))} (median {pct(meds[k])})" if len(vals) > 1 else f"{k} {pct(vals[0])}")
        out["engagement"] = b.finding(f"{platform} {bk}: " + "; ".join(parts) + ".", len(eng), min(r["age_h"] for r in eng), platform, bk, "engagement_ratios",
                                      [r["language"] for r in eng], [r["variant"] for r in eng], snap_refs(eng))
        out["engagement"]["medians"] = {k: round(v, 4) for k, v in meds.items()}
    per_lang = {}
    for r in rows:
        per_lang.setdefault(r["language"], []).append(r)
    thin = [l for l, rs in per_lang.items() if len(rs) < learn.MIN_PEERS + 1]
    if thin:
        out["medians"] = b.finding(f"{platform} {bk}: per-language rolling medians need ≥{learn.MIN_PEERS + 1} variants of one language at the same age; insufficient data for {', '.join(sorted(thin))}. Raw views are not compared across languages.",
                                   n, min_age, platform, bk, None, langs, [r["variant"] for r in rows], ev, kind="insufficient")
    return out


def experiment_findings(b):
    out = []
    try:
        with db.connect() as con:
            exps = [learn.as_dict(r) for r in learn.all_experiments(con)]
    except Exception:
        return out
    for e in exps:
        win = learn.metric_window(e)
        ev = learn.evaluate(e, learn.rows_for(win))
        for lang, r in ev["languages"].items():
            if r["tier"] == "claim":
                iv = r.get("interval") or {}
                f = b.finding(f"Experiment #{e['id']} {e.get('name') or e['variable']} ({lang}): effect {iv.get('effect')} [{iv.get('lo')}, {iv.get('hi')}] 95% bootstrap, n {r['n']}.",
                              min(r["n"].values()), 168, "youtube", win, e["variable"], [lang], [], [f"experiments #{e['id']}"], confirmed=True, kind="experiment")
                out.append((e, f))
    return out


def plan_actions(b, primaries):
    for key, res in primaries:
        platform, bk = key
        w = res.get("watch")
        if w and w["median_avg_watch_s"] < SHORT_SHAPE_WATCH_S and w["median_watch_ratio"] < 0.5:
            b.action(f"Prefer the 35 s beat shape (turn T at 18–25 s) unless the story needs 45/55 s, and state the stakes by H2 — viewers currently leave around {w['median_avg_watch_s']:.0f} s; avg watch {w['avg_watch_range_s']} s on {w['duration_range_s']} s videos ({platform} {bk})", w)
        elif w and w["median_watch_ratio"] < 0.5:
            b.action(f"Keep the 45 s default shape and land the turn T by 30 s — median avg watch {w['median_avg_watch_s']:.0f} s, watch ratio {w['median_watch_ratio']:.2f} ({platform} {bk})", w)
        elif w and w["median_watch_ratio"] >= 0.9:
            b.conflict(f"{platform} {bk}: watch ratio median {w['median_watch_ratio']:.2f} could argue for longer videos; O1 fixes 35–55 s, so not acted on.", w)
        low = sorted(res.get("low", []), key=lambda fr: fr[1]["watch_ratio"])
        if low:
            f, _ = low[0]
            detail = ", ".join(f"{r['variant']} avg watch {r['avg_watch_s']:.1f} s of {r['duration_s']:.0f} s ({x['id']})" for x, r in low)
            langs = ", ".join(sorted({r["language"] for _, r in low}))
            b.action(f"Keep the hook ≤{HOOK_MAX_S:.1f} s with the stakes in the first sentence and frame 0 ≥70% drawn; in {langs} write the first line natively short, not translated — {detail} ({platform} {bk})", f)
        d = res.get("duration")
        if d and d["rho"] <= -0.5:
            b.action(f"Stay inside 35–55 s and aim for the lower half unless density needs 55 s — {d['direction']} (rank correlation {d['rho']:+.2f}: {d['pairs']}; {platform} {bk})", d)
        elif d and d["rho"] >= 0.5:
            b.conflict(f"{platform} {bk}: longer videos held a larger share (rho {d['rho']:+.2f}); this conflicts with the approved 35–55 s target (O1), so it is noted, not acted on.", d)
        e = res.get("engagement")
        if e and platform == "instagram":
            m = e["medians"]
            sh, sv = m.get("shares_per_reach"), m.get("saves_per_reach")
            if sh is not None and sv is not None and sh < sv:
                b.action(f"Use the ≤6-word engagement line as a share prompt with a real answer in the text and compare shares/reach next time — shares/reach median {pct(sh)} vs saves/reach {pct(sv)} ({platform} {bk})", e)


def legacy_finding(b, latest):
    if not latest:
        return None
    durs = [r["duration_s"] for r in latest if r.get("duration_s")]
    v1 = all((r.get("engine_version") or 1) == 1 for r in latest)
    if durs and min(durs) > TARGET_S[1]:
        return b.finding(f"Every measured variant is {'engine v1, ' if v1 else ''}{min(durs):.0f}–{max(durs):.0f} s long; the approved 35–55 s format has no data yet, so these signals transfer only partly.",
                         len({r['variant'] for r in latest}), min(r["age_h"] for r in latest), None, None, "duration_s", [r["language"] for r in latest],
                         sorted({r["variant"] for r in latest}), ["features.duration_s, features.engine_version"], kind="context")
    return None


def build(days=None, now=None, probe=ffprobe_duration, today=None):
    now = now or datetime.now(timezone.utc)
    obs, last_age = load(days, now, probe)
    latest = latest_per_variant(obs)
    gs = groups(obs)
    b = Builder()
    medians = []
    results = {}
    for key in live_groups(gs):
        rows = gs[key]
        medians += language_medians(rows)
        res = analyse_group(b, key, rows)
        results[key] = res
    if not obs:
        b.finding("Insufficient data: no analytics snapshot with metrics after publication. Run `python -m pipeline analytics`.", 0, None, kind="insufficient")
    legacy_finding(b, latest)
    experiment_findings(b)
    primaries = []
    for platform in ("instagram", "youtube"):
        k, _ = primary_group(gs, platform)
        if k:
            primaries.append((k, results[k]))
    primaries.sort(key=lambda kr: -len(gs[kr[0]]))
    plan_actions(b, primaries)
    tiers_order = {"confirmed": 0, "directional": 1, "anecdote": 2}
    b.actions.sort(key=lambda a: tiers_order[a["tier"]])
    for i, a in enumerate(b.actions):
        a["id"] = f"A{i + 1}"
    g1 = [a["text"] for a in b.actions[:5]] or ["No carry-forward actions: insufficient data; scripts follow the approved rules unchanged."]
    return {"generated_at": db.now(), "date": today or datetime.now().date().isoformat(), "days": days, "last_snapshot_age_h": last_age,
            "stale": last_age is None or last_age > STALE_H, "evidence": EVIDENCE, "rules": RULES,
            "tiers": {"anecdote": f"<{MIN_N} comparable variants or <{MIN_AGE_H} h of data", "directional": f"≥{MIN_N} per group at the same age bucket and ≥{MIN_AGE_H} h",
                      "confirmed": "pre-registered experiment rule met (pipeline/learn.py evaluate → claim)"},
            "variants": latest, "groups": {f"{p}|{bk}": [r["variant"] for r in rows] for (p, bk), rows in gs.items()},
            "language_medians": medians, "findings": b.findings, "actions": b.actions, "conflicts": b.conflicts, "learnings_for_g1": g1}


def markdown(d):
    L = [f"# Insights — {d['date']}", "", "Evidence: " + "; ".join(d["evidence"]) + ". Nothing here is estimated; missing values are '–' or 'insufficient data'.", "",
         f"Last snapshot {fmt(d['last_snapshot_age_h'], 1)} h ago{' (stale: run `python -m pipeline analytics`)' if d['stale'] else ''}. Window: {'last ' + str(d['days']) + ' days' if d['days'] else 'all publications'}.", "",
         "Tiers: " + "; ".join(f"**{k}** = {v}" for k, v in d["tiers"].items()) + ".", "", "## Per variant (latest snapshot per platform)", "",
         "| variant | platform | age at capture (h) | snapshot age (h) | views | reach | likes | comments | shares | saves | avg watch (s) | duration (s) | watch ratio | shares/base | saves/base | likes/base | source |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in d["variants"]:
        base = "reach" if r["platform"] == "instagram" else "view"
        rt = r.get("ratios") or {}
        L.append(f"| {r['variant']} | {r['platform']} | {fmt(r['age_h'], 1)} | {fmt(r['snapshot_age_h'], 1)} | {fmt(r['views'], 0)} | {fmt(r['reach'], 0)} | {fmt(r['likes'], 0)} | {fmt(r['comments'], 0)} | {fmt(r['shares'], 0)} | {fmt(r['saves'], 0)} | {fmt(r['avg_watch_s'], 1)} | {fmt(r['duration_s'], 1)} | {fmt(r['watch_ratio'], 3)} | {pct(rt.get('shares_per_' + base))} | {pct(rt.get('saves_per_' + base))} | {pct(rt.get('likes_per_' + base))} | {r['source']} |")
    if not d["variants"]:
        L.append("| insufficient data | | | | | | | | | | | | | | | | |")
    L += ["", "base = reach on Instagram, views on YouTube. Watch ratio = avg watch / video duration.", "", "## Per language and platform (rolling median, same age bucket)", ""]
    if d["language_medians"]:
        L += ["| platform | bucket | language | metric | variant | value | peers | language median | ratio |", "|---|---|---|---|---|---|---|---|---|"]
        for m in d["language_medians"]:
            L.append(f"| {m['platform']} | {m['bucket']} | {m['language']} | {m['metric']} | {m['variant']} | {fmt(m['value'], 3)} | {m['peers']} | {fmt(m['median'], 3) if m['median'] is not None else 'insufficient data'} | {fmt(m['ratio'], 2)} |")
    else:
        L.append("Insufficient data.")
    L += ["", f"Median = leave-one-out over up to {learn.ROLLING} nearest episodes of the same language, platform and age bucket (≥{learn.MIN_PEERS} peers). Raw views are never compared across languages.", "", "## Findings", ""]
    for f in d["findings"]:
        L.append(f"- **{f['id']}** [{f['tier']}, n={f['n']}] {f['text']}" + (f" Evidence: {'; '.join(f['evidence'][:6])}." if f["evidence"] else ""))
    L += ["", "## Carry-forward actions for the next script", ""]
    L += [f"{i + 1}. {a['text']}" for i, a in enumerate(d["actions"])] or ["None: insufficient data. Scripts follow the approved rules unchanged."]
    L += ["", "## Conflicting signals (noted, not acted on)", ""]
    L += [f"- {c['text']} ({c['tier']}; {c['finding']})" for c in d["conflicts"]] or ["None."]
    L += ["", "## Learnings applied (G1 block)", ""] + [f"- {x}" for x in d["learnings_for_g1"]]
    L += ["", f"Approved rules always win over these signals: {json.dumps(d['rules'], ensure_ascii=False)}."]
    return "\n".join(L) + "\n"


def run(days=None, write=True, now=None, probe=ffprobe_duration):
    d = build(days, now, probe)
    text = markdown(d)
    path = REPORTS / f"insights-{d['date']}.md"
    if write:
        REPORTS.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        LATEST.write_text(json.dumps({**d, "markdown_path": str(path.relative_to(REPORTS.parent.parent))}, indent=2, ensure_ascii=False))
    return path, text, d
