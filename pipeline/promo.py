import copy
import difflib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from . import CONTENT, DATA, PROFILES, db, gates

BRAND_PATH = PROFILES / "brand.json"
PLATFORMS = ("youtube", "instagram")
HASHTAG = re.compile(r"(?<![\w&])#[^\s#]+", re.UNICODE)
YT_KINDS = ("youtube_description_line", "collab_line")


class Refused(Exception):
    pass


def deep_merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else copy.deepcopy(v)
    return out


def raw_config(path=None):
    return json.loads(Path(path or BRAND_PATH).read_text())


def project_for(m, path=None):
    projects = raw_config(path).get("projects", {})
    if m.get("project") in projects:
        return m["project"]
    for slug, p in projects.items():
        if m.get("series") and m["series"] in p.get("series", []):
            return slug
    return None


def load(project=None, path=None):
    raw = raw_config(path)
    b = copy.deepcopy(raw["brand"])
    p = raw.get("projects", {}).get(project or "")
    if p:
        b = deep_merge(b, p.get("overrides", {}))
        b["project"] = project
    return b


def fields(b):
    return {"instagram_url": b["instagram"]["url"], "instagram_handle": b["instagram"]["handle"], "email": b["email"],
            "youtube_url": b["youtube"]["active_url"], "brand": b["name"]}


def render(text, f):
    for k, v in f.items():
        text = text.replace("{" + k + "}", v)
    return text


def cta(b, lang):
    c = b["cta"].get(lang) or b["cta"]["en"]
    f = fields(b)
    return {k: render(v, f) if isinstance(v, str) and k != "review" else v for k, v in c.items()}


def known(b, kind):
    f = fields(b)
    return {render(c[kind], f).strip() for c in b["cta"].values() if kind in c}


def handle_slug(b):
    return b["instagram"]["handle"].lstrip("@").lower()


def is_yt_promo(line, b):
    s = line.strip()
    if not s:
        return False
    if s in known(b, "youtube_description_line") | known(b, "collab_line"):
        return True
    low = s.lower()
    return f"instagram.com/{handle_slug(b)}" in low or b["email"].lower() in low


def is_ig_promo(line, b):
    s = line.strip()
    if not s:
        return False
    if s in known(b, "instagram_caption_line"):
        return True
    firsts = {k.split(" ")[0] for k in known(b, "instagram_caption_line") if k}
    return "YouTube" in s and any(s.startswith(f) for f in firsts)


def is_hashtag_line(line):
    t = line.split()
    return bool(t) and all(x.startswith("#") for x in t)


def hashtags(text):
    return HASHTAG.findall(text or "")


def collapse_blanks(lines):
    out = []
    for l in lines:
        if not l.strip() and out and not out[-1].strip():
            continue
        out.append(l)
    return out


def trim(lines):
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and not lines[0].strip():
        lines.pop(0)
    return lines


def apply_description(desc, b, lang):
    c = cta(b, lang)
    block = [c["youtube_description_line"], c["collab_line"]]
    lines = (desc or "").split("\n")
    kept = [l for l in lines if not is_yt_promo(l, b)]
    if len(kept) != len(lines):
        kept = collapse_blanks(kept)
    kept = trim(kept)
    idx = len(kept)
    if kept and is_hashtag_line(kept[-1]):
        idx = len(kept) - 1
        while idx > 0 and kept[idx - 1].strip() and is_hashtag_line(kept[idx - 1]):
            idx -= 1
    head = trim(kept[:idx])
    tail = kept[idx:]
    out = head + ([""] if head else []) + block + ([""] + tail if tail else [])
    return "\n".join(out)


def apply_caption(caption, b, lang):
    line = cta(b, lang)["instagram_caption_line"]
    lines = [l for l in (caption or "").split("\n") if not is_ig_promo(l, b)]
    lines = trim(lines)
    i = len(lines)
    for j in range(len(lines) - 1, -1, -1):
        if is_hashtag_line(lines[j]):
            i = j
            break
        if lines[j].strip():
            break
    if i == len(lines):
        return "\n".join(lines + [line])
    while i > 0 and not lines[i - 1].strip():
        i -= 1
    if i == 0:
        return "\n".join([line, ""] + lines)
    return "\n".join(lines[:i] + [line] + lines[i:])


def question_from(desc):
    for l in (desc or "").split("\n"):
        s = l.strip()
        if s.startswith("💬"):
            return s.lstrip("💬").strip()
    return ""


def apply_pinned(yt, b, lang):
    tpl = cta(b, lang)["youtube_pinned_comment"]
    pre, _, suf = tpl.partition("{question}")
    suffix = suf.strip("\n")
    suffixes = {render(c["youtube_pinned_comment"], fields(b)).partition("{question}")[2].strip("\n") for c in b["cta"].values()}
    handle = b["instagram"]["handle"].lower()
    cur = yt.get("pinned_comment") or ""
    base = "\n".join(l for l in cur.split("\n") if handle not in l.lower() and l.strip() not in suffixes).strip()
    if not base:
        base = question_from(yt.get("description"))
    return (pre + base + "\n" + suffix).strip() if base else suffix


def limits(meta, b, platforms=PLATFORMS):
    lim = b.get("limits", {})
    out = []
    if "youtube" in platforms and meta.get("youtube"):
        d = meta["youtube"].get("description", "")
        if len(d) > lim.get("youtube_description_chars", 5000):
            out.append(f"youtube.description is {len(d)} chars (limit {lim.get('youtube_description_chars', 5000)})")
        if "<" in d or ">" in d:
            out.append("youtube.description contains < or >, which YouTube rejects")
    if "instagram" in platforms and meta.get("instagram"):
        c = meta["instagram"].get("caption", "")
        if len(c) > lim.get("instagram_caption_chars", 2200):
            out.append(f"instagram.caption is {len(c)} chars (limit {lim.get('instagram_caption_chars', 2200)})")
        n = len(hashtags(c))
        if n > lim.get("instagram_hashtags", 5):
            out.append(f"instagram.caption has {n} hashtags (limit {lim.get('instagram_hashtags', 5)})")
    return out


def plan(meta, b, lang, platforms=PLATFORMS):
    new = copy.deepcopy(meta)
    if "youtube" in platforms and isinstance(new.get("youtube"), dict):
        yt = new["youtube"]
        yt["description"] = apply_description(yt.get("description", ""), b, lang)
        yt["pinned_comment"] = apply_pinned(yt, b, lang)
    if "instagram" in platforms and isinstance(new.get("instagram"), dict):
        ig = new["instagram"]
        ig["caption"] = apply_caption(ig.get("caption", ""), b, lang)
    return new, limits(new, b, platforms)


def changed_sections(old, new):
    return [p for p in PLATFORMS if old.get(p) != new.get(p)]


def field_diff(old, new, label):
    out = []
    for p in PLATFORMS:
        a, z = old.get(p) or {}, new.get(p) or {}
        for k in sorted(set(a) | set(z)):
            if a.get(k) == z.get(k):
                continue
            va = a.get(k) if isinstance(a.get(k), str) else json.dumps(a.get(k), ensure_ascii=False) if k in a else ""
            vz = z.get(k) if isinstance(z.get(k), str) else json.dumps(z.get(k), ensure_ascii=False)
            out += list(difflib.unified_diff((va or "").split("\n"), vz.split("\n"), f"{label} {p}.{k} (now)", f"{label} {p}.{k} (proposed)", lineterm="", n=2))
    return "\n".join(out)


def published_platforms(m, lang, con=None):
    out = {p for p in (e.get("platform") for e in gates.published_entries(m, lang)) if p}
    f = gates.variant_files(m, lang)
    if f["legacy"]:
        log = Path(f["meta"]).with_name("published.json")
        try:
            out |= {e.get("platform") for e in json.loads(log.read_text())} if log.exists() else set()
        except json.JSONDecodeError:
            pass
    if con is not None:
        out |= {r["platform"] for r in con.execute("SELECT platform FROM publications WHERE variant_id=?", (f"{m['id']}-{lang}",))}
    return out


def g3_approved(m, lang, platform):
    e = gates.entries(m, gates.publish_key(platform)).get(lang) or {}
    return e.get("status") == "approved"


def read_meta(path):
    text = Path(path).read_text()
    return json.loads(text), text.endswith("\n")


def write_meta(path, meta, newline=True):
    Path(path).write_text(json.dumps(meta, indent=2, ensure_ascii=False) + ("\n" if newline else ""))


def run(cid, langs=None, platforms=PLATFORMS, apply=False, force=False, out=print, brand_path=None):
    m = gates.load(cid)
    b = load(project_for(m, brand_path), brand_path)
    results = []
    with db.connect() as con:
        for lang in langs or m.get("languages", []):
            f = gates.variant_files(m, lang)
            res = {"variant": f"{cid}-{lang}", "meta": gates.rel(f["meta"]), "changed": [], "written": False, "refused": [], "problems": [], "reapproval": []}
            results.append(res)
            if not Path(f["meta"]).exists():
                res["problems"].append("no publish.json yet")
                out(f"{res['variant']}: no publish.json yet; nothing to do")
                continue
            meta, nl = read_meta(f["meta"])
            new, problems = plan(meta, b, lang, platforms)
            res["problems"] = problems
            res["changed"] = changed_sections(meta, new)
            review = (b["cta"].get(lang) or {}).get("review", "")
            tag = f" [{review}]" if review and review != "approved-language" else ""
            if not res["changed"]:
                out(f"{res['variant']}: promo already present ({', '.join(platforms)}){tag}")
                continue
            out(f"{res['variant']}: changes in {', '.join(res['changed'])}{tag}")
            out(field_diff(meta, new, res["variant"]))
            for pr in problems:
                out(f"  LIMIT: {pr}")
            if not apply:
                continue
            live = published_platforms(m, lang, con)
            final = copy.deepcopy(meta)
            for p in res["changed"]:
                if p in live:
                    res["refused"].append(f"{p}: already uploaded/published; edit the live post by hand (Studio / Instagram app)")
                    continue
                if g3_approved(m, lang, p) and not force:
                    res["refused"].append(f"{p}: G3 is approved for {cid}-{lang}; changing this section would invalidate it (pass --force-reapproval-needed if the owner wants to re-approve)")
                    continue
                if g3_approved(m, lang, p):
                    res["reapproval"].append(p)
                final[p] = new[p]
            for r in res["refused"]:
                out(f"  REFUSED {r}")
            if problems:
                res["refused"].append("limits exceeded; nothing written")
                out("  REFUSED: limits exceeded; nothing written")
                continue
            if final != meta:
                write_meta(f["meta"], final, nl)
                res["written"] = True
                out(f"  wrote {res['meta']}")
            for p in res["reapproval"]:
                out(f"  OWNER MUST RE-APPROVE G3 ({p}) for {cid}-{lang}: the '{p}' section of publish.json changed, so the existing approval no longer matches")
    return results


def missing(meta, platform, lang=None, b=None):
    try:
        b = b or load()
    except (OSError, ValueError, KeyError):
        return []
    lang = lang or (meta.get("youtube") or {}).get("language") or "en"
    if platform == "youtube":
        d = (meta.get("youtube") or {}).get("description", "")
        if not any(is_yt_promo(l, b) and handle_slug(b) in l.lower() for l in d.split("\n")):
            return [f"YouTube description has no Instagram promo line ({b['instagram']['url']}); new episodes run `python -m pipeline promo <ID> --apply` before G3"]
    if platform == "instagram":
        c = (meta.get("instagram") or {}).get("caption", "")
        if not any(is_ig_promo(l, b) for l in c.split("\n")):
            return ["Instagram caption has no 'watch the full series on YouTube' line; new episodes run `python -m pipeline promo <ID> --apply` before G3"]
    return []


IST = gates.IST


def fmt_ist(value):
    t = gates.parse_time(value) if value not in (None, "", "now") else None
    return t.astimezone(IST).strftime("%Y-%m-%d %H:%M IST") if t else (value or "")


def status_of(m, lang, platform, con, now=None):
    now = now or datetime.now(timezone.utc)
    variant = f"{m['id']}-{lang}"
    row = con.execute("SELECT platform_id, url, privacy, scheduled_for, published_at FROM publications WHERE variant_id=? AND platform=?", (variant, platform)).fetchone()
    if row:
        if row["published_at"]:
            return "live", row["url"] or row["platform_id"]
        t = gates.parse_time(row["scheduled_for"]) if row["scheduled_for"] else None
        if t and t <= now:
            return "live", row["url"] or row["platform_id"]
        return f"uploaded-scheduled {fmt_ist(row['scheduled_for'])}", row["url"] or row["platform_id"]
    if platform in published_platforms(m, lang):
        return "live", ""
    if platform == "youtube":
        q = con.execute("SELECT publish_at, status FROM publish_queue WHERE content_id=? AND lang=? AND platform='youtube'", (m["id"], lang)).fetchone()
        if q and q["status"] not in ("done",):
            return f"queued ({q['status']}) for {fmt_ist(q['publish_at']) or q['publish_at']}", ""
    if platform == "instagram":
        job = gates.ig_job_time(variant)
        if job:
            return f"IG scheduled {fmt_ist(job)}", ""
    if g3_approved(m, lang, platform):
        return "G3 approved, not queued", ""
    return "not approved", ""


def category(status):
    for c in ("live", "uploaded-scheduled", "queued", "IG scheduled", "G3 approved", "not approved"):
        if status.startswith(c):
            return c
    return status


def audit(today=None, out_dir=None, brand_path=None):
    today = today or datetime.now(IST).strftime("%Y-%m-%d")
    out_dir = Path(out_dir or DATA / "reports")
    rows, details = [], []
    counts = {}
    with db.connect() as con:
        for mp in sorted(CONTENT.glob("C*/manifest.json")):
            m = json.loads(mp.read_text())
            b = load(project_for(m, brand_path), brand_path)
            for lang in m.get("languages", []):
                f = gates.variant_files(m, lang)
                if not Path(f["meta"]).exists():
                    rows.append((f"{m['id']}-{lang}", "-", "no publish.json", "-", "-"))
                    continue
                meta, _ = read_meta(f["meta"])
                for p in PLATFORMS:
                    if not isinstance(meta.get(p), dict):
                        continue
                    status, ref = status_of(m, lang, p, con)
                    has = not missing(meta, p, lang, b)
                    new, problems = plan(meta, b, lang, (p,))
                    approved = g3_approved(m, lang, p)
                    action = "none (promo present)" if has and new.get(p) == meta.get(p) else (
                        "update live post by hand (proposed text below)" if status.startswith("live") else
                        "proposal only: G3-approved/scheduled, not applied (needs owner re-approval to change)" if approved or not status.startswith("not approved") else
                        "apply with `pipeline promo --apply` before G3")
                    key = (p, category(status))
                    counts[key] = counts.get(key, 0) + 1
                    rows.append((f"{m['id']}-{lang}", p, status + (f" ({ref})" if ref else ""), "yes" if has else "no", action))
                    if new.get(p) != meta.get(p):
                        field = "description" if p == "youtube" else "caption"
                        block = [f"### {m['id']}-{lang} · {p} · {status}", ""]
                        if (b["cta"].get(lang) or {}).get("review") not in (None, "approved-language"):
                            block += [f"_{lang}: CTA text {b['cta'][lang]['review']}._", ""]
                        for pr in problems:
                            block.append(f"**Limit:** {pr}")
                        block += [f"Proposed {p}.{field}:", "", "```text", new[p][field], "```", ""]
                        if p == "youtube":
                            block += ["Proposed pinned comment (set by hand in Studio):", "", "```text", new[p]["pinned_comment"], "```", ""]
                        block += ["Diff:", "", "```diff", field_diff({p: meta[p]}, {p: new[p]}, f"{m['id']}-{lang}"), "```", ""]
                        details.append("\n".join(block))
    lines = [f"# Promo audit {today}", "",
             "Generated by `python -m pipeline promo --audit`. Read-only: nothing was applied to any approved, scheduled or published item. "
             "Changing a G3-approved `publish.json` section would invalidate that approval, and live posts can only be edited by hand.", "",
             "## Summary", ""]
    ext = (load(None, brand_path)["youtube"].get("external_channel_items") or {})
    summary = {}
    for (p, s), n in sorted(counts.items()):
        summary.setdefault(p, []).append(f"{s}: {n}")
    for p, items in summary.items():
        lines.append(f"- **{p}**: " + ", ".join(items))
    if ext.get("items"):
        lines += ["", "## Channel content outside the pipeline", "", ext.get("note", ""), ""]
        lines += [f"- {i.get('title')} ({i.get('visibility', '?')}, {i.get('date', '?')})" for i in ext["items"]]
    lines += ["", "## Per variant and platform", "", "| Variant | Platform | Status | Promo present | Action |", "|---|---|---|---|---|"]
    lines += [f"| {v} | {p} | {s} | {h} | {a} |" for v, p, s, h, a in rows]
    lines += ["", "## Proposed text (dry run)", ""] + details
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"promo-audit-{today}.md"
    path.write_text("\n".join(lines) + "\n")
    return path, rows, counts


def cli(a):
    if a.audit:
        path, rows, counts = audit()
        print(f"wrote {gates.rel(path)} ({len(rows)} rows)")
        for (p, s), n in sorted(counts.items()):
            print(f"  {p:9s} {s:20s} {n}")
        return
    if not a.id:
        raise SystemExit("promo <ID> [--lang L] [--dry-run|--apply] [--platform youtube|instagram] [--force-reapproval-needed], or promo --audit")
    platforms = (a.platform,) if a.platform else PLATFORMS
    langs = [l.strip() for l in a.lang.split(",")] if a.lang else None
    res = run(a.id, langs, platforms, apply=a.apply, force=a.force_reapproval_needed)
    if not a.apply:
        print("\n(dry run; nothing written. Use --apply to write sections that have no G3 approval yet.)")
    if any(r["refused"] for r in res):
        raise SystemExit(2)
