import json
import statistics
from datetime import datetime

from . import DATA, db, learn
from .analytics import WINDOWS, equal_window_table

REPORTS = DATA / "reports"
MANUAL = REPORTS / "e7_manual.json"
RANK_WINDOWS = ("7d", "48h", "24h")
STALL, NORMAL = 0.5, 0.8
CANNIBAL_RUN = 3
SPLIT_RUN, SPLIT_TRIGGERS = 5, 2
SELF_SUFFICIENT = 0.5
E7 = [("self_sufficiency", "auto", f"window views >= {SELF_SUFFICIENT:.0%} of the leading language's for the same episode"),
      ("cannibalisation", "auto", f"this language's outlier ratio < {STALL} while another language's is >= {NORMAL} on the same episode"),
      ("audience_separation", "manual", "YouTube Studio audience language/geography shows a distinct audience (no API metric)"),
      ("comment_confusion", "manual", "comments asking for another language or confused by mixed-language uploads"),
      ("policy_pressure", "manual", "e.g. a YPP rejection citing inauthentic or repetitive content"),
      ("capacity", "manual", "producing this language delays G2 for the others")]
EVIDENCE = ("data/studio.db: publications, analytics_snapshots (label, age_h), features, experiments", "content/<ID>/<lang>/published.json (Instagram ids)")


def collect(platforms=("youtube", "instagram")):
    windows = {p: {lab: equal_window_table(lab, p) for lab, _ in WINDOWS} for p in platforms}
    with db.connect() as con:
        exps = [learn.as_dict(r) for r in learn.all_experiments(con)]
        inv = {}
        for p in platforms:
            pubs = con.execute("SELECT COUNT(*) n FROM publications WHERE platform=?", (p,)).fetchone()["n"]
            snaps = con.execute("SELECT label, COUNT(*) n, MAX(captured_at) last FROM analytics_snapshots s JOIN publications p ON p.id=s.publication_id WHERE p.platform=? GROUP BY label", (p,)).fetchall()
            inv[p] = {"publications": pubs, "snapshots": {r["label"]: r["n"] for r in snaps}, "last_capture": max((r["last"] for r in snaps), default=None)}
        feats = con.execute("SELECT COUNT(*) n FROM features").fetchone()["n"]
        langs = [r["l"] for r in con.execute("SELECT DISTINCT substr(variant_id, 7) l FROM publications ORDER BY l")]
    manual = json.loads(MANUAL.read_text()) if MANUAL.exists() else {}
    return {"windows": windows, "experiments": exps, "inventory": inv, "features": feats, "manual": manual, "languages": langs}


def fmt(x, nd=2):
    if x is None:
        return "–"
    return f"{x:.{nd}f}" if isinstance(x, float) else str(x)


def section_inventory(d):
    out = ["## Data inventory", ""]
    for p, v in d["inventory"].items():
        snaps = ", ".join(f"{k}: {n}" for k, n in sorted(v["snapshots"].items())) or "none"
        out.append(f"- **{p}**: {v['publications']} publications; snapshots by label: {snaps}; last capture {v['last_capture'] or '–'}")
    out.append(f"- features rows: {d['features']}")
    return out + [""]


def section_medians(d):
    out = ["## Per-language medians (equal windows)", ""]
    for p, by in d["windows"].items():
        any_rows = False
        for lab in ("48h", "7d"):
            rows = by.get(lab) or []
            if not rows:
                continue
            any_rows = True
            out += [f"**{p} · {lab}**", "", "| language | n | median views | variants |", "|---|---|---|---|"]
            langs = sorted({r["language"] for r in rows})
            for l in langs:
                vs = [r["views"] for r in rows if r["language"] == l]
                out.append(f"| {l} | {len(vs)} | {fmt(statistics.median(vs), 1)} | {', '.join(r['variant'] for r in rows if r['language'] == l)} |")
            out.append("")
        if not any_rows:
            out += [f"**{p}**: insufficient data (no 48h or 7d window values yet).", ""]
    out.append("Raw views are listed per language only; they are never compared across languages.")
    return out + [""]


def best_window(by):
    for lab in RANK_WINDOWS:
        rated = [r for r in learn.rolling_ratios(by.get(lab) or []) if r["ratio"] is not None]
        if rated:
            return lab, rated
    return None, []


def section_ranking(d):
    out = ["## Top and bottom variants by outlier ratio", "", f"Ratio = window views / that language's rolling median (leave-one-out, up to {learn.ROLLING} nearest episodes, at least {learn.MIN_PEERS} peers).", ""]
    for p, by in d["windows"].items():
        lab, rated = best_window(by)
        if not rated:
            out += [f"**{p}**: insufficient data (needs {learn.MIN_PEERS + 1}+ variants of one language at the same window).", ""]
            continue
        rated.sort(key=lambda r: -r["ratio"])
        out += [f"**{p} · {lab}**", "", "| rank | variant | language | ratio | views | language median | source |", "|---|---|---|---|---|---|---|"]
        picks = rated[:3] + [r for r in rated[-3:] if r not in rated[:3]]
        for r in picks:
            out.append(f"| {'top' if r in rated[:3] else 'bottom'} | {r['variant']} | {r['language']} | {r['ratio']:.2f} | {r['views']} | {fmt(r['language_median'], 1)} | {r['source']} |")
        out.append("")
    return out


def section_experiments(d):
    out = ["## Experiments", ""]
    if not d["experiments"]:
        return out + ["No experiments registered.", ""]
    active = [e for e in d["experiments"] if e["status"] == "active"]
    out.append(f"Active: {', '.join('#' + str(e['id']) for e in active) or 'none'} (rule: one at a time; slots frozen while a content experiment is active).")
    out.append("")
    for e in d["experiments"]:
        win = learn.metric_window(e)
        rows = d["windows"].get("youtube", {}).get(win) or []
        ev = learn.evaluate(e, rows)
        out += [f"### #{e['id']} {e.get('name') or e['variable']} — {e['status']}", "", f"- Hypothesis: {e['hypothesis']}", f"- Arms: {', '.join(e['arms'])}; assignment: {json.dumps(e['assignment_rule'], ensure_ascii=False)}",
                f"- Metric: {e['metric']}", f"- Stop rule: {e['stop_rule']}"]
        if e.get("design"):
            out.append(f"- Design: {e['design']}")
        if not ev["languages"]:
            out.append(f"- n per arm: insufficient data (no {win} ratio values yet) → **anecdote**")
        for lang, r in ev["languages"].items():
            iv = r.get("interval")
            out.append(f"- {lang}: n {r['n']} · median ratio {r['median_ratio']} · **{r['tier']}**" + (f" · effect {iv['effect']} [{iv['lo']}, {iv['hi']}] 95% bootstrap" if iv else "") + (f" ({r['why']})" if r.get("why") else ""))
        out.append(f"- Overall: **{ev['overall']}**")
        if e.get("result"):
            out.append(f"- Result: {e['result']}")
        out.append("")
    return out


def episode_matrix(rows):
    rated = [r for r in learn.rolling_ratios(rows) if r.get("episode") is not None]
    m = {}
    for r in rated:
        m.setdefault(r["episode"], {})[r["language"]] = r
    return dict(sorted(m.items()))


def cannibalisation(rows):
    mat = episode_matrix(rows)
    usable = {e: {l: r for l, r in v.items() if r["ratio"] is not None} for e, v in mat.items()}
    usable = {e: v for e, v in usable.items() if len(v) >= 2}
    if len(usable) < CANNIBAL_RUN:
        return {"status": "insufficient data", "episodes": len(usable), "flags": [], "streaks": {}}
    streaks, best = {}, {}
    for e, v in usable.items():
        for l in v:
            others = [r["ratio"] for k, r in v.items() if k != l]
            hit = v[l]["ratio"] < STALL and any(o >= NORMAL for o in others)
            streaks[l] = streaks.get(l, 0) + 1 if hit else 0
            best[l] = max(best.get(l, 0), streaks[l])
    flags = []
    for e, v in usable.items():
        normal = [l for l, r in v.items() if r["ratio"] >= NORMAL]
        stalled = [l for l, r in v.items() if r["ratio"] < STALL]
        if len(normal) == 1 and len(stalled) == len(v) - 1:
            flags.append((e, normal[0], stalled))
    run, worst = 0, 0
    prev = None
    for e, n, _ in flags:
        run = run + 1 if prev is not None and e == prev + 1 else 1
        worst, prev = max(worst, run), e
    return {"status": "flag" if worst >= CANNIBAL_RUN else "ok", "episodes": len(usable), "flags": flags, "longest_run": worst, "streaks": streaks, "best": best}


def section_cannibalisation(d):
    lab, _ = best_window(d["windows"].get("youtube", {}))
    out = ["## Cannibalisation check (D10)", "", f"Rule: flag when one language is normal (ratio ≥ {NORMAL}) while every other language stalls (ratio < {STALL}) on {CANNIBAL_RUN}+ consecutive episodes. YouTube, window {lab or '–'}.", ""]
    if not lab:
        return out + ["Insufficient data: no ratio values yet.", ""]
    c = cannibalisation(d["windows"]["youtube"][lab])
    if c["status"] == "insufficient data":
        return out + [f"Insufficient data: {c['episodes']} episode(s) with ratios in ≥2 languages (needs {CANNIBAL_RUN}).", ""]
    out.append(f"Status: **{c['status']}** over {c['episodes']} episodes (longest run {c['longest_run']}).")
    for e, n, s in c["flags"]:
        out.append(f"- episode {e}: {n} normal; stalled: {', '.join(s)}")
    return out + [""]


def e7_auto(rows):
    mat = episode_matrix(rows)
    ss, cn = {}, {}
    for e, v in mat.items():
        lead = max((r["views"] for r in v.values()), default=0)
        for l, r in v.items():
            ok = lead > 0 and len(v) >= 2 and r["views"] >= SELF_SUFFICIENT * lead
            ss[l] = ss.get(l, 0) + 1 if ok else 0
            others = [o["ratio"] for k, o in v.items() if k != l and o["ratio"] is not None]
            hit = r["ratio"] is not None and r["ratio"] < STALL and any(o >= NORMAL for o in others)
            cn[l] = cn.get(l, 0) + 1 if hit else 0
    return {"self_sufficiency": ss, "cannibalisation": cn, "episodes": len(mat)}


def section_e7(d):
    lab, _ = best_window(d["windows"].get("youtube", {}))
    if not lab:
        lab = next((l for l in RANK_WINDOWS if d["windows"].get("youtube", {}).get(l)), None)
    rows = d["windows"].get("youtube", {}).get(lab) or [] if lab else []
    auto = e7_auto(rows) if rows else {"self_sufficiency": {}, "cannibalisation": {}, "episodes": 0}
    langs = sorted(set(d.get("languages") or []) | {r["language"] for r in rows} | {l for t in d["manual"].values() if isinstance(t, dict) for l in t})
    out = ["## Account split triggers (E7)", "", f"Split a language only when ≥{SPLIT_TRIGGERS} of 6 triggers hold for ≥{SPLIT_RUN} consecutive episodes, with owner approval, never during the YPP application window. Instagram candidates first: gu, te.", "",
           f"Auto triggers use YouTube window {lab or '–'} over {auto['episodes']} episode(s). Manual triggers are read from `data/reports/e7_manual.json` ({{trigger: {{lang: {{consecutive_episodes, evidence}}}}}}).", ""]
    if not langs:
        return out + ["Insufficient data: no YouTube window values and no manual trigger records.", ""]
    out += ["| trigger | kind | rule | " + " | ".join(langs) + " |", "|---|---|---|" + "---|" * len(langs)]
    held = {l: [] for l in langs}
    for name, kind, rule in E7:
        cells = []
        for l in langs:
            if kind == "auto":
                if auto["episodes"] < SPLIT_RUN:
                    run = auto[name].get(l)
                    cells.append(f"insufficient data ({run or 0} run, {auto['episodes']} ep)")
                    continue
                run = auto[name].get(l, 0)
                ev = f"run {run}"
            else:
                rec = (d["manual"].get(name) or {}).get(l)
                if not rec:
                    cells.append("not recorded")
                    continue
                run = int(rec.get("consecutive_episodes", 0))
                ev = f"run {run} · {rec.get('evidence', 'no evidence given')}"
            if run >= SPLIT_RUN:
                held[l].append(name)
            cells.append(("**met** " if run >= SPLIT_RUN else "") + ev)
        out.append(f"| {name} | {kind} | {rule} | " + " | ".join(cells) + " |")
    out.append("")
    for l in langs:
        recorded = any((d["manual"].get(n) or {}).get(l) for n, k, _ in E7 if k == "manual")
        if len(held[l]) >= SPLIT_TRIGGERS:
            verdict = "split candidate → owner decision"
        elif auto["episodes"] < SPLIT_RUN and not recorded:
            verdict = "insufficient data to evaluate (no split)"
        else:
            verdict = "no split"
        out.append(f"- {l}: {len(held[l])} trigger(s) held for ≥{SPLIT_RUN} episodes ({', '.join(held[l]) or 'none'}) → **{verdict}**")
    return out + [""]


def weekly_markdown(d, today=None):
    today = today or datetime.now().date().isoformat()
    lines = [f"# Weekly report — {today}", "", "Evidence: " + "; ".join(EVIDENCE) + ". Numbers come only from these; anything missing is reported as insufficient data.", ""]
    for sec in (section_inventory, section_medians, section_ranking, section_experiments, section_cannibalisation, section_e7):
        lines += sec(d)
    return "\n".join(lines) + "\n"


def weekly(today=None, write=True):
    today = today or datetime.now().date().isoformat()
    text = weekly_markdown(collect(), today)
    path = REPORTS / f"weekly-{today}.md"
    if write:
        REPORTS.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return path, text
