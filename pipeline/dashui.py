import html
import json
import re
import time
from urllib.parse import quote

from . import DATA, db, episodes as E, monitor

NAV = [("/", "Home", "home"), ("/progress", "Progress", "chart"), ("/uploads", "Uploads", "upload"), ("/problems", "Problems", "alert")]
TIER_WORDS = {"anecdote": "Early sign", "directional": "Likely pattern", "confirmed": "Confirmed"}

ICONS = {
    "home": '<path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10v10h13V10"/><path d="M10 20v-5h4v5"/>',
    "chart": '<path d="M4 20h16"/><path d="M7 16V10"/><path d="M12 16V5"/><path d="M17 16v-3"/>',
    "upload": '<path d="M12 15V4"/><path d="m7 9 5-5 5 5"/><path d="M5 20h14"/>',
    "alert": '<path d="M12 3.5 21.5 20h-19z"/><path d="M12 10v4.5"/><path d="M12 17.5v.01"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "youtube": '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="M10 9.3v5.4l4.7-2.7z" fill="currentColor" stroke="none"/>',
    "instagram": '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="3.8"/><circle cx="17" cy="7" r="1" fill="currentColor" stroke="none"/>',
    "next": '<path d="m9.5 6 6 6-6 6"/>',
    "back": '<path d="m14.5 6-6 6 6 6"/>',
    "bell": '<path d="M6 16.5V11a6 6 0 0 1 12 0v5.5l1.5 1.5h-15z"/><path d="M10 21h4"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/>',
    "stats": '<path d="M4 4v16h16"/><path d="m8 14 3.5-3.5 3 3L19 8"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "dot": '<circle cx="12" cy="12" r="4" fill="currentColor" stroke="none"/>',
    "cross": '<path d="M7 7l10 10M17 7 7 17"/>',
}


def e(s):
    return html.escape("" if s is None else str(s), quote=True)


def icon(name, cls=""):
    return f'<svg class="ic {cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'


def pill(text, tone):
    return f'<span class="pill t-{e(tone)}">{e(text)}</span>'


def dash():
    from . import dashboard

    return dashboard


def now_s():
    return time.time()


def page(title, body, active="/", live_after=0, badge=0, sub=None, back=None):
    nav = []
    for href, name, ic in NAV:
        on = href == active
        b = f'<span class="nb" aria-label="{badge} open">{badge}</span>' if href == "/problems" and badge else ""
        nav.append(f'<a href="{href}"{" aria-current=page class=on" if on else ""}>{icon(ic)}{b}<span>{name}</span></a>')
    updated = E.when(now_s())
    head = f'<p class="sub">{e(sub)}</p>' if sub else ""
    backl = f'<a class="back" href="{e(back[0])}">{icon("back")}{e(back[1])}</a>' if back else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#14191c" media="(prefers-color-scheme: dark)"><meta name="theme-color" content="#f5f3ee" media="(prefers-color-scheme: light)">
<title>{e(title)} · Studio</title><link rel="manifest" href="/manifest.webmanifest"><link rel="icon" href="/icon-192.png"><link rel="apple-touch-icon" href="/icon-192.png">
<link rel="stylesheet" href="/static/app.css"></head>
<body data-live="1" data-sse="1" data-after="{int(live_after or 0)}" data-updated="{e(updated)}">
<div id="net" class="net" hidden role="status"><span id="netmsg"></span></div>
<main><header class="top"><span class="brand">Shorts Studio</span><span class="upd"><span class="live-dot"></span>Updated {e(updated)}</span></header>
{backl}<h1>{e(title)}</h1>{head}{body}</main>
<nav class="tabs" aria-label="Main">{''.join(nav)}</nav><script src="/static/app.js"></script></body></html>"""


def bar(pct, tone="gold"):
    p = max(0, min(100, int(round(pct))))
    return f'<div class="bar" role="img" aria-label="{p} percent"><i class="w{p} f-{tone}"></i></div>'


def seg_bar(parts, total):
    total = max(1, total)
    out, used = [], 0
    for count, tone, label in parts:
        if count <= 0:
            continue
        p = max(1, round(100 * count / total))
        p = min(p, 100 - used)
        used += p
        out.append(f'<i class="w{p} f-{tone}" title="{e(label)}"></i>')
    desc = ", ".join(f"{c} {lbl}" for c, _, lbl in parts if c > 0)
    return f'<div class="bar seg" role="img" aria-label="{e(desc)}">{"".join(out)}</div>'


def ring(pct):
    p = max(0.0, min(100.0, float(pct)))
    c = 2 * 3.14159 * 42
    shown = c * p / 100 if p == 0 or p >= 1 else c / 100
    return (f'<svg class="ring" viewBox="0 0 100 100" aria-hidden="true"><circle class="ring-bg" cx="50" cy="50" r="42"/>'
            f'<circle class="ring-fg" cx="50" cy="50" r="42" stroke-dasharray="{shown:.1f} {c:.1f}" transform="rotate(-90 50 50)"/></svg>')


PLAT_TONE = {"live": "done", "scheduled": "gold", "waiting": "wait", "failed": "bad", "late": "bad", "none": "grey"}
PLAT_SHORT = {"live": "posted", "scheduled": "scheduled", "waiting": "waiting to post", "failed": "failed", "late": "late", "none": "not yet"}


def lang_chips(ep):
    out = []
    for l in ep["langs"]:
        dots = []
        desc = []
        for p in ("youtube", "instagram"):
            if p not in l["platforms"]:
                continue
            ps = l["platforms"][p]
            tone = "bad" if any(x.get("platform") == p for x in l["problems"]) else PLAT_TONE[ps["state"]]
            dots.append(f'<i class="d f-{tone}" role="img" aria-label="{e(E.platform_name(p))}: {e(PLAT_SHORT[ps["state"]] if tone != "bad" else "problem")}" title="{e(E.platform_name(p))}: {e(PLAT_SHORT[ps["state"]])}"></i>')
            desc.append(f"{E.platform_name(p)} {PLAT_SHORT[ps['state']]}")
        tone = "bad" if l["problems"] else E.TONES[l["stage"]]
        out.append(f'<span class="lc t-{tone}" title="{e(l["name"])}: {e(", ".join(desc))}" aria-label="{e(l["name"])}: {e(", ".join(desc))}">'
                   f'{e(l["lang"].upper())}{"".join(dots)}</span>')
    return f'<span class="chips">{"".join(out)}</span>'


def ep_row(ep):
    st = ep["status"]
    return (f'<a class="row ep" href="/episode/{quote(ep["id"])}"><span class="epn">{e(E.ep_label(ep["episode"], ep["id"]))}</span>'
            f'<span class="grow"><span class="t">{e(ep["title"])}</span><span class="meta">{pill(st["label"], st["tone"])}</span>'
            f'{lang_chips(ep)}</span>{icon("next", "chev")}</a>')


def dot_legend():
    return ('<p class="legend"><span class="lg"><b>Dots:</b> first = YouTube, second = Instagram.</span>'
            '<span class="lg"><i class="d f-done"></i>live</span><span class="lg"><i class="d f-gold"></i>scheduled</span><span class="lg"><i class="d f-wait"></i>waiting</span>'
            '<span class="lg"><i class="d f-bad"></i>problem</span><span class="lg"><i class="d f-grey"></i>not yet</span></p>')


def empty(text):
    return f'<p class="empty">{e(text)}</p>'


def card(title, body, cls="", ic=None, link=None):
    head = f'<h2>{icon(ic) if ic else ""}{e(title)}</h2>'
    more = f'<a class="more" href="{e(link[0])}">{e(link[1])}{icon("next")}</a>' if link else ""
    return f'<section class="card {cls}">{head}{body}{more}</section>'


def load_all(con):
    D = dash()
    eps = E.load(con, D.ig_jobs())
    return eps


def projects(con):
    rows = con.execute("SELECT * FROM projects ORDER BY created_at").fetchall()
    return rows


def project_progress(con, eps, p):
    plan = E.project_plan(p["config"])
    mine = [x for x in eps if x["project_id"] == p["id"]]
    return plan, E.progress(mine, plan), mine


def ep_name(ep):
    return f"Episode {ep['episode']}" if ep.get("episode") else ep["title"]


def relevant_issue_ids(eps):
    return {i for ep in eps for l in ep["langs"] for i in l["relevant"]}


def flagged_issue_ids(eps):
    return {pr["id"] for ep in eps for l in ep["langs"] for pr in l["problems"] if pr.get("id")}


def needs_you_issues(con, eps):
    flag = flagged_issue_ids(eps)
    return [r for r in open_issues(con) if r["status"] == "open" and r.get("error_code") not in E.TRANSIENT
            and (r["id"] in flag or (not r["variant_id"] and r["severity"] in ("critical", "recoverable", "warning")))]


def synthetic_problems(eps):
    out = []
    for ep in eps:
        for l in ep["langs"]:
            for pr in l["problems"]:
                if not pr.get("id"):
                    out.append((ep, l, pr))
    return out


def open_issues(con):
    return [dict(r) for r in con.execute("SELECT * FROM issues WHERE status IN ('open','acknowledged') ORDER BY CASE severity WHEN 'critical' THEN 0 WHEN 'recoverable' THEN 1 WHEN 'warning' THEN 2 ELSE 3 END, last_t DESC").fetchall()]


def problem_count(con, eps):
    return len(group_issues(needs_you_issues(con, eps))) + len(synthetic_problems(eps))


def who(con_ep_map, variant_id, content_id=None, platform=None):
    parts = []
    cid, lang = (variant_id.rsplit("-", 1) if variant_id and "-" in variant_id else (variant_id or content_id, None))
    ep = con_ep_map.get(cid)
    if ep:
        parts.append(ep_name(ep))
    elif cid:
        parts.append(E.plain(cid))
    if lang:
        parts.append(E.lang_name(lang))
    if platform:
        parts.append(E.platform_name(platform))
    return " · ".join(parts) or "Whole studio"


def approvals(con, epmap):
    groups = {}
    for v, gate in monitor.pending_approvals(con):
        cid, lang = v.rsplit("-", 1)
        groups.setdefault((cid, gate), []).append(lang)
    out = []
    for (cid, gate), langs in groups.items():
        ep = epmap.get(cid)
        name = ep_name(ep) if ep else E.plain(cid)
        ln = ", ".join(E.lang_name(x) for x in langs)
        if gate == "gate:script":
            t, s = f"{name}: scripts are ready for your OK", f"{ln} · read them, then reply OK in the Claude chat"
        elif gate == "gate:final":
            t, s = f"{name}: videos are ready to watch", f"{ln} · watch them on the Mac, then reply OK in the Claude chat"
        else:
            plat = gate.rsplit(":", 1)[-1]
            t, s = f"{name}: ready to post on {E.platform_name(plat)}", f"{ln} · tell Claude the posting time"
        out.append({"cid": cid, "title": t, "sub": s})
    return out


def running_now(con, eps):
    epmap = {x["id"]: x for x in eps}
    rows = con.execute("SELECT * FROM task_state WHERE status='Running' AND t >= ? ORDER BY t DESC", (now_s() - E.STALE_S,)).fetchall()
    out = []
    for r in rows:
        words = E.RUNNING_WORDS.get(r["stage"], "Working")
        if r["stage"] == "publish" and r["platform"]:
            words = f"Posting to {E.platform_name(r['platform'])}"
        cid = r["content_id"] or ((r["variant_id"] or "").rsplit("-", 1)[0] or None)
        lang = r["variant_id"].rsplit("-", 1)[1] if r["variant_id"] and "-" in r["variant_id"] else None
        ep = epmap.get(cid)
        whom = " · ".join(x for x in (ep_name(ep) if ep else "", E.lang_name(lang) if lang else "") if x)
        measured = None
        if r["progress"] is not None:
            measured = (float(r["progress"]) * 100, f"{float(r['progress']) * 100:.0f}% done")
        elif lang and cid and r["stage"] in ("voice", "images"):
            c = E.file_counts(cid, lang, "voice" if r["stage"] == "voice" else "pictures")
            if c and c[1]:
                measured = (100 * c[0] / c[1], f"{'voice parts' if r['stage'] == 'voice' else 'pictures'} {c[0]} of {c[1]}")
        out.append({"words": words, "who": whom, "cid": cid, "measured": measured, "since": E.ago(r["started_at"] or r["t"])})
    return out


def coming_up(eps, limit=None):
    items = []
    for ep in eps:
        for l in ep["langs"]:
            for p, ps in l["platforms"].items():
                if ps["state"] in ("scheduled", "waiting"):
                    items.append({"ep": ep, "lang": l, "platform": p, "ps": ps, "t": ps.get("t") or 0})
    items.sort(key=lambda x: (0 if x["t"] else 1, x["t"] or 0, x["platform"]))
    return items[:limit] if limit else items


def up_row(x, show_day=True):
    ps = x["ps"]
    if ps["state"] == "scheduled":
        time_txt = E.when(ps["t"]) if show_day else E.clock(E.to_dt(ps["t"]))
        status = "Scheduled"
        tone = "gold"
    else:
        pn = E.platform_name(x["platform"])
        if not ps.get("t"):
            time_txt, status = "After the scheduled ones", (f"no fixed time, waits for {pn}'s daily limit" if ps.get("held") else "no fixed time")
        else:
            time_txt, status = (E.when(ps["t"]) if show_day else E.clock(E.to_dt(ps["t"]))), E.platform_words(ps)
        tone = "wait"
    return (f'<a class="row up" href="/episode/{quote(x["ep"]["id"])}"><span class="pl pl-{x["platform"]}">{icon(x["platform"])}</span>'
            f'<span class="grow"><span class="t">{e(E.ep_label(x["ep"]["episode"], x["ep"]["id"]))} · {e(x["lang"]["name"])}</span>'
            f'<span class="meta">{e(time_txt)} · {e(E.platform_name(x["platform"]))} · <span class="tx-{tone}">{e(status)}</span></span></span></a>')


def greeting():
    h = E.to_dt(now_s()).hour
    return "Good morning" if 5 <= h < 12 else "Good afternoon" if 12 <= h < 17 else "Good evening" if 17 <= h < 22 else "Hello"


def render_home(con):
    eps = load_all(con)
    epmap = {x["id"]: x for x in eps}
    D = dash()
    aps = approvals(con, epmap)
    probs = needs_you_issues(con, eps)
    synth = synthetic_problems(eps)
    n = len(aps) + len(group_issues(probs)) + len(synth)
    if n:
        status = f'<div class="hero t-wait">{icon("bell")}<div><b>{n} thing{"s" if n != 1 else ""} need{"s" if n == 1 else ""} you</b><span>{e(greeting())}. Everything else is on track.</span></div></div>'
    else:
        status = f'<div class="hero t-done">{icon("check")}<div><b>All good</b><span>{e(greeting())}. Nothing needs you right now.</span></div></div>'
    needs = []
    for a in aps:
        needs.append(f'<a class="row need" href="/episode/{quote(a["cid"])}"><span class="pl t-wait">{icon("bell")}</span><span class="grow"><span class="t">{e(a["title"])}</span>'
                     f'<span class="meta">{e(a["sub"])}</span></span>{icon("next", "chev")}</a>')
    for g in group_issues(probs):
        r = g["rep"]
        tone = E.SEVERITY_TONES.get(r["severity"], "wait")
        needs.append(f'<a class="row need" href="/problems"><span class="pl t-{tone}">{icon("alert")}</span><span class="grow"><span class="t">{e(E.issue_title(r))}</span>'
                     f'<span class="meta">{e(group_who(g, epmap))} · {e(E.SEVERITY_WORDS.get(r["severity"], "Heads-up"))}</span></span>{icon("next", "chev")}</a>')
    for ep, l, pr in synth:
        needs.append(f'<a class="row need" href="/episode/{quote(ep["id"])}"><span class="pl t-bad">{icon("alert")}</span><span class="grow"><span class="t">{e(E.issue_title(pr))}</span>'
                     f'<span class="meta">{e(ep_name(ep))} · {e(l["name"])}</span></span>{icon("next", "chev")}</a>')
    body = [status]
    body.append(card("Needs you", "".join(needs) or empty("Nothing needs you right now. You can relax."), "needs" if needs else "", "bell"))
    run = running_now(con, eps)
    rows = []
    for r in run:
        prog = (f'{bar(r["measured"][0], "gold")}<span class="meta">{e(r["measured"][1])} · started {e(r["since"])}</span>' if r["measured"]
                else f'<span class="meta"><span class="spin"></span>Working… started {e(r["since"])}</span>')
        rows.append(f'<div class="row run"><span class="grow"><span class="t">{e(r["words"])}</span><span class="meta">{e(r["who"])}</span>{prog}</span></div>')
    body.append(card("Happening now", "".join(rows) or empty("Nothing is running right now. The Mac is resting."), "", "gear"))
    up = coming_up(eps, 3)
    body.append(card("Coming up next", "".join(up_row(x) for x in up) or empty("Nothing is scheduled yet."), "", "calendar", ("/uploads", "See all uploads")))
    for p in projects(con):
        plan, pr, mine = project_progress(con, eps, p)
        name = D.short_project(p["name"], p["id"])
        if pr["goal"]:
            cur = pr["milestones"][pr["current"]] if pr["current"] is not None and pr["milestones"] else None
            curl = f'<span class="meta">Now on {e(cur["name"])}: {cur["made"]} of {cur["planned"]} made</span>' if cur else ""
            body.append(f'<a class="card goal" href="/progress?p={quote(p["id"])}"><div class="ringbox">{ring(100 * pr["made"] / pr["goal"])}<span class="rp">{pr["pct"]}%</span></div>'
                        f'<span class="grow"><span class="t">{e(name)} goal</span><span class="big">{pr["made"]} of {pr["goal"]} episodes</span>'
                        f'<span class="meta">{pr["pct"]}% · {pr["to_go"]} to go</span>{curl}</span>{icon("next", "chev")}</a>')
        else:
            body.append(f'<a class="card goal" href="/progress?p={quote(p["id"])}"><span class="grow"><span class="t">{e(name)}</span>'
                        f'<span class="meta">{len(mine)} episodes · goal not set</span></span>{icon("next", "chev")}</a>')
    body.append(f'<a class="card linkcard" href="/results">{icon("stats")}<span class="grow"><span class="t">How videos are doing</span>'
                f'<span class="meta">Views, likes and watch time</span></span>{icon("next", "chev")}</a>')
    after = con.execute("SELECT COALESCE(MAX(rowid),0) FROM events").fetchone()[0]
    return page("Home", "".join(body), "/", after, problem_count(con, eps))


def render_progress(con, q):
    D = dash()
    eps = load_all(con)
    ps = projects(con)
    if not ps:
        return page("Progress", empty("No projects yet."), "/progress", badge=problem_count(con, eps))
    want = (q.get("p") or [""])[0]
    sel = next((p for p in ps if p["id"] == want), None) or next((p for p in ps if E.project_plan(p["config"])["goal"]), ps[0])
    picker = []
    for p in ps:
        plan, pr, mine = project_progress(con, eps, p)
        sub = f"{pr['made']} of {pr['goal']} episodes made" if pr["goal"] else f"{len(mine)} episodes · goal not set"
        on = p["id"] == sel["id"]
        picker.append(f'<a class="proj{" on" if on else ""}" href="/progress?p={quote(p["id"])}"{" aria-current=true" if on else ""}>'
                      f'<span class="t">{e(D.short_project(p["name"], p["id"]))}</span><span class="meta">{e(sub)}</span></a>')
    body = [f'<div class="projs">{"".join(picker)}</div>']
    plan, pr, mine = project_progress(con, eps, sel)
    if pr["goal"]:
        parts = [(pr["done"], "done", "posted everywhere"), (pr["posting"], "gold", "made, posting under way"), (pr["working"], "work", "being made"),
                 (pr["not_started"], "grey", "not started")]
        legend = "".join(f'<li><i class="d f-{t}"></i><b>{c}</b> {e(lbl)}</li>' for c, t, lbl in parts)
        body.append(f'<section class="card"><p class="big">{pr["made"]} of {pr["goal"]} episodes made</p><p class="meta">{pr["pct"]}% · {pr["to_go"]} to go</p>'
                    f'{seg_bar(parts, pr["goal"])}<ul class="leg">{legend}</ul></section>')
    else:
        body.append(f'<section class="card"><p class="big">{len(mine)} episodes</p><p class="meta">Goal not set. Ask Claude to set a goal for this project.</p></section>')
    if pr["milestones"]:
        rows = []
        for i, m in enumerate(pr["milestones"]):
            open_ = " open" if i == pr["current"] else ""
            eps_html = (dot_legend() + "".join(ep_row(x) for x in m["episodes"])) if m["episodes"] else empty("No episodes here yet.")
            stat = f"{m['made']} made of {m['planned']} · {m['to_go']} to go" if m["planned"] else f"{m['made']} made"
            if m["made"] >= m["planned"] and m["planned"]:
                stat = f"All {m['planned']} made"
            tone = "done" if m["planned"] and m["made"] >= m["planned"] else "gold"
            rows.append(f'<details class="ms"{open_}><summary><span class="grow"><span class="t">{e(m["name"])}</span>'
                        f'<span class="meta">{e(m.get("subtitle") or "")}</span>{bar(m["pct"], tone)}<span class="meta strong">{e(stat)}</span></span>'
                        f'{icon("next", "chev")}</summary><div class="eps">{eps_html}</div></details>')
        body.append(f'<h2 class="sec">Parts of the story</h2>{"".join(rows)}')
    else:
        body.append(f'<h2 class="sec">Episodes</h2>{"".join(ep_row(x) for x in sorted(mine, key=lambda x: x["id"])) or empty("No episodes yet.")}{dot_legend()}')
    after = con.execute("SELECT COALESCE(MAX(rowid),0) FROM events").fetchone()[0]
    return page("Progress", "".join(body), "/progress", after, problem_count(con, eps))


def step_html(s):
    if s["state"] == "done":
        mark, words = icon("check"), ("Done" if s["total"] <= 1 else f"Done for all {s['total']} languages")
    elif s["state"] == "now":
        mark = '<span class="nowdot"></span>'
        words = "Next" if s["done"] == 0 else (f"{s['done']} of {s['total']} languages done" if s["total"] > 1 else "In progress")
    else:
        mark, words = "", "Not yet"
    langs = "".join(f'<li>{icon("check") if x["done"] else ('<span class="nowdot sm"></span>' if x["now"] else '<span class="todo"></span>')}<span>{e(x["name"])}</span>'
                    f'<span class="meta">{"done" if x["done"] else ("working on it" + (": " + e(x["detail"]) if x["detail"] else "")) if x["now"] else "not yet"}</span></li>'
                    for x in s["langs"])
    return (f'<li class="step st-{s["state"]}"><span class="mk">{mark}</span><details><summary><span class="t">{e(s["name"])}</span>'
            f'<span class="meta">{e(words)}</span></summary><p class="help">{e(s["help"])}</p><ul class="langs">{langs}</ul></details></li>')


def render_episode(con, cid):
    eps = load_all(con)
    ep = next((x for x in eps if x["id"] == cid), None)
    if not ep:
        return None
    pr_cfg = None
    msname = None
    if ep["project_id"]:
        r = con.execute("SELECT config FROM projects WHERE id=?", (ep["project_id"],)).fetchone()
        pr_cfg = E.project_plan(r["config"]) if r else None
        if pr_cfg and pr_cfg["milestones"]:
            i = E.milestone_index(ep, pr_cfg["milestones"])
            msname = pr_cfg["milestones"][i]["name"] if i is not None else None
    st = ep["status"]
    body = []
    sub = " · ".join(x for x in (msname, f"{len(ep['langs'])} languages" if ep["langs"] else None) if x)
    body.append(f'<section class="card status">{pill(st["label"], st["tone"])}<p class="lead">{e(st["text"])}</p>'
                + ('<p class="meta">This episode is fully done.</p>' if st["done"] else "") + "</section>")
    if ep["langs"]:
        steps = E.combined_steps(ep["langs"])
        body.append(card("Steps", f'<ol class="steps">{"".join(step_html(s) for s in steps)}</ol><p class="meta">Tap a step to see each language.</p>', "", None))
    langs = []
    for l in ep["langs"]:
        lines = "".join(f'<li><span class="pl pl-{p}" title="{e(E.platform_name(p))}">{icon(p)}</span><span><span class="sr">{e(E.platform_name(p))}: </span>'
                        f'<span class="tx-{PLAT_TONE[ps["state"]]}">{e(E.platform_words(ps))}</span>'
                        + (f' · <a href="{e(ps["url"])}" rel="noreferrer" target="_blank">open</a>' if ps.get("url") else "") + "</span></li>"
                        for p, ps in l["platforms"].items()) if E.ORDER.index(l["stage"]) >= E.ORDER.index("ready") else ""
        extra = f'<span class="meta">{e(l["detail"])}</span>' if l["detail"] else ""
        probs = "".join(f'<p class="tx-bad">{icon("alert")}{e(E.issue_title(p))}</p>' for p in l["problems"])
        tone = "bad" if l["problems"] else E.TONES[l["stage"]]
        same = l["stage"] == st["stage"] and not l["problems"]
        langs.append(f'<div class="row lang"><span class="grow"><span class="lh"><span class="t">{e(l["name"])}</span>{"" if same else pill(l["label"], tone)}</span>{extra}'
                     f'{probs}<ul class="plats">{lines}</ul></span></div>')
    if langs:
        body.append(card("Each language", "".join(langs), "", None))
    hist = E.history(con, cid)
    hrows = "".join(f'<li><span class="when">{e(h["when"])}</span><span>{e(h["text"])}{(" · " + e(h["who"])) if h["who"] else ""}</span></li>' for h in hist)
    body.append(card("What happened", f'<ul class="hist">{hrows}</ul>' if hrows else empty("Nothing has happened yet."), "", None))
    D = dash()
    if any(r["variant"].startswith(cid + "-") for r in D.analytics_rows(con)):
        body.append(f'<a class="card linkcard" href="/results?ep={quote(cid)}">{icon("stats")}<span class="grow"><span class="t">How this episode is doing</span>'
                    f'<span class="meta">Views, likes and watch time</span></span>{icon("next", "chev")}</a>')
    title = f"{E.ep_label(ep['episode'], cid)} · {ep['title']}"
    after = con.execute("SELECT COALESCE(MAX(rowid),0) FROM events").fetchone()[0]
    return page(title, "".join(body), "/progress", after, problem_count(con, eps), sub or None, ("/progress?p=" + quote(ep["project_id"] or ""), "Progress"))


def retry_words(v):
    return "Yes" if v == 1 else "No" if v == 0 else "Not sure"


def group_issues(rows):
    groups = {}
    for r in rows:
        cid = r["content_id"] or ((r["variant_id"] or "").rsplit("-", 1)[0] or None)
        k = (cid, r["platform"], r["error_code"] or r["title"], r["stage"], r["status"])
        groups.setdefault(k, []).append(r)
    out = []
    for rs in groups.values():
        langs = [x["variant_id"].rsplit("-", 1)[1] for x in rs if x["variant_id"] and "-" in x["variant_id"]]
        out.append({"rep": rs[0], "rows": rs, "langs": sorted(set(langs), key=lambda x: (x != "en", x))})
    return out


def group_who(g, epmap):
    r = g["rep"]
    if len(g["rows"]) == 1:
        return who(epmap, r["variant_id"], r["content_id"], r["platform"])
    cid = r["content_id"] or (r["variant_id"] or "").rsplit("-", 1)[0]
    ep = epmap.get(cid)
    parts = [ep_name(ep) if ep else E.plain(cid)]
    if g["langs"]:
        parts.append(", ".join(E.lang_name(x) for x in g["langs"]))
    if r["platform"]:
        parts.append(E.platform_name(r["platform"]))
    return " · ".join(parts)


def ack_form(g, csrf):
    ids = [int(x["id"]) for x in g["rows"] if x["status"] == "open"]
    if not csrf or not ids:
        return ""
    return (f'<form method="post" action="/issues/{ids[0]}/ack"><input type="hidden" name="csrf" value="{e(csrf)}">'
            f'<input type="hidden" name="ids" value="{",".join(map(str, ids))}"><button class="btn">Mark as seen</button></form>')


def problem_card(g, epmap, csrf=None, note=None):
    r = g["rep"] if isinstance(g, dict) and "rep" in g else g
    if r is g:
        g = {"rep": r, "rows": [r], "langs": []}
    tone = E.SEVERITY_TONES.get(r["severity"], "wait")
    sev = E.SEVERITY_WORDS.get(r["severity"], "Heads-up")
    if r.get("error_code") in E.TRANSIENT:
        tone, sev = "grey", "Fixes itself"
    techtxt = E.plain(dash().scrub(r["technical"] or ""))[:2000]
    occ = sum(int(x["occurrences"] or 1) for x in g["rows"])
    last = max((x["last_seen"] for x in g["rows"] if x["last_seen"]), default=None)
    times = f"Happened {occ} times, last {E.when(last)}" if occ > 1 else f"Happened {E.when(last)}"
    return (f'<article class="card prob t-{tone}"><div class="ph">{pill(sev, tone)}</div><h3>{e(E.issue_title(r))}</h3>'
            f'<p class="meta">{e(group_who(g, epmap))} · {e(times)}</p>'
            + (f'<p class="note">{e(note)}</p>' if note else "")
            + f'<h4>What happened</h4><p>{e(E.plain(r["explanation"]))}</p><h4>What to do</h4><p>{e(E.issue_todo(r))}</p>'
            f'<p><b>Safe to try again:</b> {retry_words(r["retry_safe"])}</p>'
            + (f'<details class="tech"><summary>Technical details</summary><pre>{e(techtxt)}</pre></details>' if techtxt else "")
            + f"{ack_form(g, csrf)}</article>")


def compact_list(groups, epmap, word):
    items = "".join(f'<li><span class="t">{icon("check")}{e(E.issue_title(g["rep"]))}</span><span class="meta">{e(group_who(g, epmap))} · {e(word(g))}</span></li>' for g in groups)
    return f'<ul class="fx">{items}</ul>'


def render_uploads(con):
    D = dash()
    eps = load_all(con)
    epmap = {x["id"]: x for x in eps}
    rel = relevant_issue_ids(eps)
    fails = [r for r in open_issues(con) if r["id"] in rel and r["status"] == "open" and r.get("error_code") not in E.TRANSIENT and (r["stage"] == "publish" or (r["stage"] or "").startswith("gate:publish"))]
    cards = [problem_card(g, epmap) for g in group_issues(fails)]
    for ep, l, pr in synthetic_problems(eps):
        if pr.get("stage") == "publish":
            ps = l["platforms"].get(pr.get("platform"), {})
            cards.append(f'<article class="card prob t-bad"><div class="ph">{pill("Needs attention", "bad")}</div><h3>{e(E.issue_title(pr))}</h3>'
                         f'<p class="meta">{e(ep_name(ep))} · {e(l["name"])}</p><h4>What happened</h4><p>The post did not go out as planned.</p>'
                         f'<h4>What to do</h4><p>Ask Claude to check this upload and try again.</p><p><b>Safe to try again:</b> Not sure</p>'
                         + (f'<details class="tech"><summary>Technical details</summary><pre>{e(E.plain(D.scrub(ps.get("error"))))}</pre></details>' if ps.get("error") else "")
                         + "</article>")
    body = []
    if cards:
        body.append(f'<h2 class="sec">Needs fixing</h2>{"".join(cards)}')
    up = coming_up(eps)
    groups = []
    cur = None
    for x in up:
        day = E.day_name(x["t"]) if x["t"] else "After the scheduled ones"
        if day != cur:
            groups.append([day, []])
            cur = day
        groups[-1][1].append(x)
    html_up = "".join(f'<h3 class="day">{e(d)}</h3>{"".join(up_row(x, show_day=False) for x in items)}' for d, items in groups)
    body.append(f'<section class="card"><h2>{icon("calendar")}Coming up</h2>{html_up or empty("Nothing is scheduled yet.")}</section>')
    posted = []
    for ep in eps:
        for l in ep["langs"]:
            for p, ps in l["platforms"].items():
                if ps["state"] == "live":
                    posted.append({"ep": ep, "lang": l, "platform": p, "ps": ps, "t": ps.get("t") or 0})
    posted.sort(key=lambda x: -(x["t"] or 0))
    groups, cur = [], None
    for x in posted[:60]:
        day = E.day_name(x["t"]) if x["t"] else "Earlier"
        if day != cur:
            groups.append([day, []])
            cur = day
        groups[-1][1].append(x)
    rows = []
    for d, items in groups:
        rows.append(f'<h3 class="day">{e(d)}</h3>')
        for x in items:
            url = x["ps"].get("url")
            link = f'<a class="open" href="{e(url)}" rel="noreferrer" target="_blank">Open</a>' if url else ""
            tm = E.clock(E.to_dt(x["t"])) if x["t"] else ""
            rows.append(f'<div class="row up"><span class="pl pl-{x["platform"]}">{icon(x["platform"])}</span><span class="grow">'
                        f'<span class="t">{e(E.ep_label(x["ep"]["episode"], x["ep"]["id"]))} · {e(x["lang"]["name"])}</span>'
                        f'<span class="meta">{e(tm + " · " if tm else "")}{e(E.platform_name(x["platform"]))} · <span class="tx-done">Posted</span></span></span>{link}</div>')
    body.append(f'<section class="card"><h2>{icon("check")}Posted</h2>{"".join(rows) or empty("Nothing posted yet.")}</section>')
    after = con.execute("SELECT COALESCE(MAX(rowid),0) FROM events").fetchone()[0]
    return page("Uploads", "".join(body), "/uploads", after, problem_count(con, eps))


def render_problems(con, csrf, q):
    eps = load_all(con)
    epmap = {x["id"]: x for x in eps}
    rel = relevant_issue_ids(eps)
    rows = open_issues(con)
    open_rows = [r for r in rows if r["status"] == "open"]
    live = [r for r in open_rows if r["id"] in rel or not r["variant_id"]]
    stale = [r for r in open_rows if r not in live]
    known = [r for r in rows if r["status"] == "acknowledged"]
    synth = synthetic_problems(eps)
    selfheal = [r for r in live if r.get("error_code") in E.TRANSIENT]
    live = [r for r in live if r not in selfheal]
    live_g = group_issues(live)
    n_open = len(live_g) + len(synth)
    body = []
    if n_open:
        body.append(f'<div class="hero t-wait">{icon("alert")}<div><b>{n_open} problem{"s" if n_open != 1 else ""} need{"s" if n_open == 1 else ""} you</b><span>Each one says what to do.</span></div></div>')
    else:
        body.append(f'<div class="hero t-done">{icon("check")}<div><b>Nothing needs you</b><span>{"A few things are sorting themselves out (below)." if selfheal else "Everything is working."}</span></div></div>')
    cards = [problem_card(g, epmap, csrf) for g in live_g]
    for ep, l, pr in synth:
        cards.append(f'<article class="card prob t-bad"><div class="ph">{pill("Needs attention", "bad")}</div><h3>{e(E.issue_title(pr))}</h3>'
                     f'<p class="meta">{e(ep_name(ep))} · {e(l["name"])}</p><h4>What to do</h4><p>Ask Claude to look at this episode.</p></article>')
    body.append("".join(cards))
    if selfheal:
        body.append('<h2 class="sec">Sorting itself out</h2><p class="meta">The studio retries these by itself. No action needed.</p>'
                    + "".join(problem_card(g, epmap, csrf) for g in group_issues(selfheal)))
    if stale:
        body.append(f'<h2 class="sec">Probably already sorted</h2><p class="meta">These are still marked open, but the video has already moved past this step. '
                    f'Mark them as seen to clear them.</p>' + "".join(problem_card(g, epmap, csrf, "The video has moved on since this happened.") for g in group_issues(stale)))
    if known:
        kg = group_issues(known)
        body.append(f'<details class="card fixed"><summary><span class="grow"><span class="t">Known, no action needed ({len(kg)})</span>'
                    f'<span class="meta">You have already seen these.</span></span>{icon("next", "chev")}</summary>'
                    + compact_list(kg, epmap, lambda g: "seen") + "</details>")
    fixed = [dict(r) for r in con.execute("SELECT * FROM issues WHERE status='resolved' ORDER BY COALESCE(last_t, 0) DESC LIMIT 200")]
    if fixed:
        fg = group_issues(fixed)
        body.append(f'<details class="card fixed"><summary><span class="t">Fixed problems ({len(fg)})</span>{icon("next", "chev")}</summary>'
                    + compact_list(fg, epmap, lambda g: "fixed " + E.when(max((x["resolved_at"] for x in g["rows"] if x["resolved_at"]), default=None))) + "</details>")
    after = con.execute("SELECT COALESCE(MAX(rowid),0) FROM events").fetchone()[0]
    return page("Problems", "".join(body), "/problems", after, n_open)


def insights():
    try:
        return json.loads((DATA / "reports" / "latest_insights.json").read_text())
    except (OSError, ValueError):
        return {}


def takeaway(ins):
    for f in ins.get("findings") or []:
        tier = TIER_WORDS.get(f.get("tier"), "Early sign")
        n = f.get("n")
        basis = f"Based on {n} video{'s' if n != 1 else ''}" if isinstance(n, int) else ""
        if f.get("median_avg_watch_s") is not None:
            plat = E.platform_name(f.get("platform")) if f.get("platform") else "these platforms"
            secs = round(float(f["median_avg_watch_s"]))
            tail = ", so most viewers leave before the end." if (f.get("median_watch_ratio") or 1) < 0.5 else "."
            dur = f" of a {f['duration_range_s']} second video" if f.get("duration_range_s") else ""
            return tier, f"On {plat}, people watch about {secs} seconds{dur} on average{tail}", basis
        txt = E.plain(f.get("text"))
        if txt:
            return tier, txt, basis
    return None


def metric(v):
    if v is None or v == "":
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f"{int(round(f)):,}"


def render_results(con, q):
    D = dash()
    eps = load_all(con)
    epmap = {x["id"]: x for x in eps}
    only = (q.get("ep") or [""])[0]
    rows = [r for r in D.analytics_rows(con) if not only or r["variant"].startswith(only + "-")]
    body = []
    ins = insights()
    tk = takeaway(ins)
    if tk and not only:
        body.append(f'<section class="card take">{pill(tk[0], "gold")}<p class="lead">{e(tk[1])}</p><p class="meta">{e(tk[2])}{" · " if tk[2] else ""}'
                    'Too early to be sure; this will firm up as more videos come in.</p></section>')
    groups = {}
    for r in rows:
        groups.setdefault(r["variant"].rsplit("-", 1)[0], []).append(r)
    for cid in sorted(groups, reverse=True):
        ep = epmap.get(cid)
        items = []
        for r in sorted(groups[cid], key=lambda r: (r["variant"], r["platform"])):
            lang = r["variant"].rsplit("-", 1)[1]
            bits = []
            for key, word in (("views", "views"), ("likes", "likes"), ("shares", "shares"), ("comments", "comments")):
                m = metric(r.get(key))
                if m is not None:
                    bits.append(f"<b>{m}</b> {word}")
            w = r.get("watch")
            watch = f"People watched <b>{float(w):.0f} seconds</b> on average" if isinstance(w, (int, float)) else ""
            age = r.get("age_h")
            if isinstance(age, (int, float)) and age < 0:
                bits, watch, age = ["Not public yet. Numbers start once it goes live."], "", None
            agetxt = f"{int(round(age))} hours after posting" if isinstance(age, (int, float)) and age < 48 else (f"{int(round(age / 24))} days after posting" if isinstance(age, (int, float)) else "")
            items.append(f'<div class="row res"><span class="pl pl-{e(r["platform"])}">{icon(r["platform"]) if r["platform"] in ("youtube", "instagram") else ""}</span><span class="grow">'
                         f'<span class="t">{e(E.lang_name(lang))} · {e(E.platform_name(r["platform"]))}</span><span class="stats">{" · ".join(bits) or "No numbers yet"}</span>'
                         + (f'<span class="meta">{watch}</span>' if watch else "") + (f'<span class="meta">Measured {e(agetxt)}</span>' if agetxt else "") + "</span></div>")
        title = f"{E.ep_label(ep['episode'], cid)} · {ep['title']}" if ep else E.plain(cid)
        body.append(card(title, "".join(items)))
    if not rows:
        body.append(empty("No numbers yet. They appear about a day after a video is posted."))
    try:
        nxt, has = D.next_collection()
        body.append(f'<p class="meta center">Numbers update once a day. Next update {e(E.when(nxt.timestamp()))}.' + ("" if has else " The daily update is not switched on.") + "</p>")
    except Exception:
        pass
    return page("How videos are doing", "".join(body), "/", 0, problem_count(con, eps), None, ("/episode/" + quote(only), "Episode") if only else ("/", "Home"))


def offline_html():
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Offline · Studio</title>'
            '<link rel="stylesheet" href="/static/app.css"></head><body><main><h1>Your Mac is offline or asleep</h1>'
            '<section class="card"><p class="lead">The studio runs on the Mac, so this page needs the Mac to be awake and online.</p>'
            '<p>Wake the Mac or check its internet, then pull down to refresh.</p><p>If it still does not open, send <b>/link</b> to the Telegram bot to get the current address.</p></section></main></body></html>')


def signin_html():
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sign in · Studio</title>'
            '<link rel="stylesheet" href="/static/app.css"></head><body><main><h1>Sign-in needed</h1><section class="card">'
            '<p class="lead">Open the dashboard link from the Telegram bot. Send <b>/link</b> to the bot to get it again.</p>'
            '<p>Using the home-screen app? Long-press the link in Telegram, copy it, and paste it here:</p>'
            '<form method="post" action="/login" class="signin"><input name="link" autocomplete="off" aria-label="Sign-in link" placeholder="https://…/login?k=…">'
            '<button type="submit" class="btn primary">Sign in</button></form></section></main></body></html>')


WIDTHS = "".join(f".w{i}{{width:{i}%}}" for i in range(101))

CSS = """:root{color-scheme:dark;--bg:#14191c;--card:#1c2327;--card2:#242d32;--line:#313c42;--fg:#f3f1ea;--mut:#b3bdc2;--acc:#e8be6e;--gold:#e8be6e;--on-acc:#1d1606;
--done:#79d49e;--wait:#f2b851;--bad:#ff8b80;--grey:#66737a;--work:#9cc0f5;
--done-bg:#1d3a2a;--wait-bg:#3c2f15;--bad-bg:#47211e;--gold-bg:#3a3120;--grey-bg:#2a3337;--work-bg:#1e2e44;--shadow:0 1px 0 rgba(0,0,0,.25)}
@media (prefers-color-scheme:light){:root{color-scheme:light;--bg:#f4f1ea;--card:#ffffff;--card2:#f1ede4;--line:#ddd6c8;--fg:#1a2124;--mut:#4d5960;--acc:#8a5b0c;--gold:#d9a441;--on-acc:#1d1606;
--done:#17683f;--wait:#8f5300;--bad:#b3261e;--grey:#a3adb2;--work:#1f5aa6;
--done-bg:#dcf1e4;--wait-bg:#fbebcf;--bad-bg:#fbe0dd;--gold-bg:#f8ecd2;--grey-bg:#e9e6df;--work-bg:#dde9fb;--shadow:0 1px 2px rgba(40,30,10,.08)}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans",sans-serif;overflow-x:hidden}
main{max-width:640px;margin:0 auto;padding:12px 16px calc(96px + env(safe-area-inset-bottom))}
a{color:var(--acc)}h1{font-size:1.6rem;line-height:1.25;margin:6px 0 14px;overflow-wrap:anywhere}h2{font-size:1.1rem;margin:0 0 10px;display:flex;align-items:center;gap:8px}
h3{font-size:1.05rem;margin:4px 0}h4{font-size:.95rem;margin:12px 0 2px;color:var(--mut)}p{margin:6px 0}
.top{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:.85rem;color:var(--mut);padding:4px 0}
.brand{font-weight:600;letter-spacing:.02em}.upd{display:flex;align-items:center;gap:6px}.live-dot{width:8px;height:8px;border-radius:50%;background:var(--done)}
.sub{color:var(--mut);margin:-8px 0 14px}
.ic{width:22px;height:22px;flex:none;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:0 0 14px;box-shadow:var(--shadow);color:var(--fg);text-decoration:none;overflow-wrap:anywhere}
.card.needs{border-color:var(--wait)}
.hero{display:flex;gap:14px;align-items:center;border-radius:12px;padding:16px;margin:0 0 14px}.hero .ic{width:34px;height:34px}
.hero b{display:block;font-size:1.35rem;line-height:1.25}.hero span{color:var(--fg);opacity:.9}
.hero.t-done{background:var(--done-bg);color:var(--done)}.hero.t-wait{background:var(--wait-bg);color:var(--wait)}.hero.t-bad{background:var(--bad-bg);color:var(--bad)}
.hero div span{display:block;color:var(--fg)}
.row{display:flex;align-items:center;gap:12px;min-height:56px;padding:10px 0;border-top:1px solid var(--line);color:var(--fg);text-decoration:none}
.card h2+.row,.card h3.day+.row,.eps>.row:first-child{border-top:0}
.grow{flex:1;min-width:0;display:flex;flex-direction:column;gap:3px}.t{font-weight:600;display:block}
.meta{color:var(--mut);font-size:.9rem;display:block}.meta.strong{color:var(--fg)}.big{font-size:1.35rem;font-weight:700;display:block;margin:0}.lead{font-size:1.05rem}
.chev{color:var(--mut);width:20px;height:20px}
.more{display:flex;align-items:center;justify-content:flex-end;gap:4px;min-height:44px;font-weight:600;text-decoration:none;border-top:1px solid var(--line);margin-top:4px}
.more .ic{width:18px;height:18px}
.pl{display:flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:10px;background:var(--card2);flex:none}
.pl.t-wait{background:var(--wait-bg);color:var(--wait)}.pl.t-bad{background:var(--bad-bg);color:var(--bad)}.pl.t-grey{background:var(--grey-bg);color:var(--mut)}
.pl-youtube{color:#ff6b6b}.pl-instagram{color:#e58bd8}
@media (prefers-color-scheme:light){.pl-youtube{color:#c4302b}.pl-instagram{color:#a3338f}}
.pill{display:inline-block;font-size:.85rem;font-weight:600;padding:3px 10px;border-radius:999px;line-height:1.35;white-space:nowrap}
.t-done.pill{background:var(--done-bg);color:var(--done)}.t-wait.pill{background:var(--wait-bg);color:var(--wait)}
.t-bad.pill{background:var(--bad-bg);color:var(--bad)}.t-gold.pill{background:var(--gold-bg);color:var(--acc)}
.t-grey.pill{background:var(--grey-bg);color:var(--mut)}.t-work.pill{background:var(--work-bg);color:var(--work)}
.tx-done{color:var(--done)}.tx-wait{color:var(--wait)}.tx-bad{color:var(--bad)}.tx-gold{color:var(--acc)}.tx-grey{color:var(--mut)}
.bar{display:flex;height:10px;border-radius:999px;background:var(--grey-bg);overflow:hidden;margin:8px 0 4px}.bar i{display:block;height:100%}
.bar.seg{height:16px}.bar.seg i+i{border-left:2px solid var(--card)}
.f-done{background:var(--done)}.f-gold{background:var(--gold)}.f-wait{background:var(--wait)}.f-bad{background:var(--bad)}.f-grey{background:var(--grey)}.f-work{background:var(--work)}
.leg{list-style:none;padding:0;margin:10px 0 0;display:grid;gap:6px}.leg li{display:flex;align-items:center;gap:8px}
.d{display:inline-block;width:10px;height:10px;border-radius:50%;flex:none}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:4px}.lc{display:inline-flex;align-items:center;gap:5px;font-size:.78rem;font-weight:700;padding:4px 8px;border-radius:8px;letter-spacing:.03em;background:var(--card2);color:var(--fg);border:1px solid var(--line)}
.lc .d{width:9px;height:9px}.d.f-wait{background:transparent;box-shadow:inset 0 0 0 2px var(--wait)}.lc.t-bad{border-color:var(--bad)}
.legend{color:var(--mut);font-size:.85rem;display:flex;flex-wrap:wrap;gap:4px 12px;align-items:center;margin:10px 0 4px}.lg{display:inline-flex;align-items:center;gap:5px}
.epn{font-weight:700;font-size:.85rem;background:var(--card2);border-radius:8px;padding:6px 8px;flex:none;align-self:flex-start;margin-top:2px}
.goal{display:flex;align-items:center;gap:14px}.ringbox{position:relative;width:76px;height:76px;flex:none}.ring{width:76px;height:76px}
.ring-bg{fill:none;stroke:var(--grey-bg);stroke-width:10}.ring-fg{fill:none;stroke:var(--gold);stroke-width:10;stroke-linecap:round}
.rp{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.95rem}
.linkcard{display:flex;align-items:center;gap:12px;min-height:56px}.linkcard>.ic:first-child{color:var(--acc)}
.projs{display:flex;gap:10px;overflow-x:auto;padding-bottom:4px;margin-bottom:12px;scrollbar-width:none}
.proj{flex:1 0 auto;min-width:200px;max-width:100%;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 14px;text-decoration:none;color:var(--fg);min-height:56px}
.proj.on{border:2px solid var(--gold)}
.sec{margin:20px 0 10px;font-size:1.15rem}
details.ms{background:var(--card);border:1px solid var(--line);border-radius:12px;margin:0 0 10px;box-shadow:var(--shadow)}
details>summary{list-style:none;cursor:pointer}details>summary::-webkit-details-marker{display:none}
.ms>summary{display:flex;align-items:center;gap:10px;padding:12px 16px;min-height:56px}.ms[open]>summary .chev,.fixed[open]>summary .chev{transform:rotate(90deg)}
.ms .eps{padding:0 16px 6px;border-top:1px solid var(--line)}
.ep{align-items:flex-start}.ep .chev{align-self:center}
.back{display:inline-flex;align-items:center;gap:4px;min-height:44px;font-weight:600;text-decoration:none;margin:-4px 0 -6px -4px}.lh{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.status .pill{font-size:.95rem}
.lang{align-items:flex-start}.plats{list-style:none;padding:0;margin:6px 0 0;display:grid;gap:6px}.plats li{display:flex;align-items:center;gap:10px;font-size:.95rem;position:relative}
.plats .pl{width:32px;height:32px;border-radius:8px}.plats .ic{width:18px;height:18px}
.lang p.tx-bad{display:flex;gap:6px;align-items:center;font-size:.92rem;margin:4px 0}.lang p.tx-bad .ic{width:18px;height:18px}
.steps{list-style:none;margin:0;padding:0}
.step{position:relative;display:flex;gap:12px;padding:0 0 4px}
.step:not(:last-child)::before{content:"";position:absolute;left:15px;top:32px;bottom:-2px;width:2px;background:var(--line)}
.step.st-done:not(:last-child)::before{background:var(--done)}
.mk{width:32px;height:32px;border-radius:50%;flex:none;display:flex;align-items:center;justify-content:center;border:2px solid var(--grey);background:var(--card);z-index:1}
.st-done .mk{background:var(--done);border-color:var(--done);color:var(--card)}.st-done .mk .ic{width:18px;height:18px;stroke-width:3}
.st-now .mk{border-color:var(--gold)}.nowdot{width:12px;height:12px;border-radius:50%;background:var(--gold)}
.step details{flex:1;min-width:0}.step summary{display:flex;flex-direction:column;min-height:44px;padding:2px 0 10px}
.st-todo .t{color:var(--mut)}.help{color:var(--mut);font-size:.9rem;margin:-4px 0 6px}
.langs{list-style:none;padding:0;margin:0 0 12px;display:grid;gap:4px}.langs li{display:grid;grid-template-columns:22px 1fr auto;gap:6px;align-items:center;font-size:.92rem}
.langs .ic{width:16px;height:16px;color:var(--done)}.nowdot.sm{width:10px;height:10px;margin:0 3px}.todo{width:10px;height:10px;border-radius:50%;border:2px solid var(--grey);margin:0 3px}
.hist{list-style:none;padding:0;margin:0}.hist li{display:flex;flex-direction:column;padding:8px 0;border-top:1px solid var(--line)}.hist li:first-child{border-top:0}
.when{color:var(--mut);font-size:.85rem}
.day{font-size:.9rem;color:var(--mut);text-transform:uppercase;letter-spacing:.05em;margin:14px 0 2px}.card h2+.day{margin-top:0}
.open{font-weight:600;min-height:44px;display:flex;align-items:center;padding:0 4px}
.prob{border-left:5px solid var(--wait)}.prob.t-bad{border-left-color:var(--bad)}.prob.t-grey{border-left-color:var(--grey)}
.ph{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px}.note{background:var(--card2);border-radius:8px;padding:8px 10px;font-size:.92rem}
.tech summary{color:var(--mut);min-height:44px;display:flex;align-items:center;font-size:.92rem;text-decoration:underline}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.8rem;background:var(--card2);padding:10px;border-radius:8px;margin:0}
.btn{font:inherit;font-weight:600;min-height:44px;padding:8px 18px;border-radius:10px;border:1px solid var(--line);background:var(--card2);color:var(--fg);cursor:pointer;margin-top:8px}
.btn.primary{background:var(--gold);border-color:var(--gold);color:var(--on-acc)}
.signin{display:grid;gap:10px;margin-top:10px}.signin input{font:inherit;width:100%;min-height:48px;padding:10px 12px;border-radius:10px;border:1px solid var(--line);background:var(--card2);color:var(--fg)}
.fixed>summary{display:flex;align-items:center;justify-content:space-between;min-height:44px}.fx{list-style:none;padding:0;margin:8px 0 0}
.fx li{padding:8px 0;border-top:1px solid var(--line)}.fx .t{display:flex;gap:6px;align-items:center;font-weight:500}.fx .ic{width:18px;height:18px;color:var(--done)}
.empty{color:var(--mut);margin:4px 0}.center{text-align:center}
.take .lead{font-size:1.1rem;font-weight:500}.stats{font-size:.95rem}.res{align-items:flex-start}
.run .bar{margin:6px 0 2px}.spin{display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--gold);margin-right:6px;animation:pulse 1.4s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:.25}50%{opacity:1}}
@media (prefers-reduced-motion:reduce){.spin{animation:none}}
.tabs{position:fixed;left:0;right:0;bottom:0;z-index:10;display:flex;justify-content:center;background:var(--card);border-top:1px solid var(--line);padding-bottom:env(safe-area-inset-bottom)}
.tabs a{position:relative;flex:1;max-width:160px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;min-height:62px;color:var(--mut);text-decoration:none;font-size:.78rem;font-weight:600}
.tabs a .ic{width:24px;height:24px}.tabs a.on{color:var(--acc)}.tabs a.on::before{content:"";position:absolute;top:0;left:28%;right:28%;height:3px;border-radius:0 0 3px 3px;background:var(--gold)}
.nb{position:absolute;top:7px;left:calc(50% + 6px);min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:var(--wait);color:var(--on-acc);font-size:.72rem;line-height:18px;text-align:center}
.net{position:sticky;top:0;z-index:20;padding:10px 16px;text-align:center;font-weight:600;font-size:.92rem;cursor:pointer}
.net.off{background:var(--grey-bg);color:var(--fg)}.net.new{background:var(--gold);color:var(--on-acc)}
:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
""" + WIDTHS

JS = """(function(){var b=document.body,net=document.getElementById('net'),msg=document.getElementById('netmsg');
if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js').catch(function(){});}
if(!b||!b.dataset.live)return;var last=parseInt(b.dataset.after||'0',10),updated=b.dataset.updated||'',touched=false,es=null,timer=null,lastReload=Date.now(),pending=false;
document.addEventListener('toggle',function(){touched=true;},true);
function show(cls,text,click){net.hidden=false;net.className='net '+cls;msg.textContent=text;net.onclick=click||null;}
function hide(){if(!pending)net.hidden=true;}
function offline(){show('off','Your Mac is offline or asleep \\u2014 showing the last update from '+updated+'.');}
function busy(){var a=document.activeElement;return touched||(a&&/INPUT|TEXTAREA|SELECT|BUTTON/.test(a.tagName));}
function changed(){if(busy()||Date.now()-lastReload<20000){pending=true;show('new','New updates \\u2014 tap to refresh',function(){location.reload();});return;}location.reload();}
function poll(){fetch('/api/events?after='+last,{credentials:'same-origin',cache:'no-store'}).then(function(r){if(r.status===401){location.reload();return null;}if(!r.ok)throw new Error('http');return r.json();})
.then(function(d){if(!d)return;hide();var ev=d.events||[];if(ev.length){last=ev[ev.length-1].rowid;changed();}}).catch(offline);}
function startPoll(){if(es){es.close();es=null;}if(!timer){timer=setInterval(poll,10000);}}
function startSSE(){if(!window.EventSource){startPoll();return;}var seen=Date.now();es=new EventSource('/events/stream?after='+last);
es.addEventListener('ev',function(m){seen=Date.now();try{var x=JSON.parse(m.data);if(x.rowid>last){last=x.rowid;changed();}}catch(e){}});
es.addEventListener('ping',function(){seen=Date.now();hide();});es.onerror=function(){if(Date.now()-seen>20000)startPoll();};
setInterval(function(){if(es&&Date.now()-seen>25000)startPoll();},5000);}
window.addEventListener('offline',offline);window.addEventListener('online',function(){poll();});
if(!navigator.onLine)offline();if(b.dataset.sse==='1'){startSSE();}else{startPoll();}})();"""

SW = """const C='ss-shell-v2',P='ss-pages-v2';const SHELL=['/offline.html','/static/app.css','/static/app.js','/icon-192.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(SHELL)));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C&&k!==P).map(k=>caches.delete(k)))));self.clients.claim();});
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET')return;const u=new URL(r.url);if(u.origin!==location.origin)return;
if(r.mode==='navigate'){e.respondWith(fetch(r).then(res=>{if(res.ok&&res.status===200&&!u.pathname.startsWith('/login')){const cp=res.clone();caches.open(P).then(c=>c.put(r,cp));}return res;})
.catch(()=>caches.open(P).then(c=>c.match(r)).then(m=>m||caches.match('/offline.html'))));return;}
if(SHELL.includes(u.pathname)){e.respondWith(fetch(r).catch(()=>caches.match(r)));}});"""
