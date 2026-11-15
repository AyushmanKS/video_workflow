import json
import statistics
import time
from datetime import datetime, timedelta
from pathlib import Path

from . import CONTENT, DATA

DEFAULT_SECONDS = {"voice:kokoro": 1.5, "voice:veena": 150.0, "images": 100.0, "render": 90.0, "text_scene": 3.0}
RATES = DATA / "rates.json"


def load_rates():
    return {**DEFAULT_SECONDS, **(json.loads(RATES.read_text()) if RATES.exists() else {})}


def learn(key, seconds_per_unit):
    rates = json.loads(RATES.read_text()) if RATES.exists() else {}
    old = rates.get(key, DEFAULT_SECONDS.get(key, seconds_per_unit))
    rates[key] = round(0.6 * old + 0.4 * seconds_per_unit, 1)
    RATES.parent.mkdir(parents=True, exist_ok=True)
    RATES.write_text(json.dumps(rates, indent=2))


def measured_rate(files):
    times = sorted(f.stat().st_mtime for f in files)
    gaps = [b - a for a, b in zip(times, times[1:]) if b - a > 0.5]
    return statistics.median(gaps) if gaps else None


def scene_info(work):
    sp = work / "script.json"
    if not sp.exists():
        return 0, set()
    scenes = json.loads(sp.read_text())["scenes"]
    return len(scenes), {i for i, s in enumerate(scenes) if s.get("kind") in ("verse", "shloka")}


def steps_for(cid):
    m = json.loads((CONTENT / cid / "manifest.json").read_text())
    primary, langs = m["primary_language"], m["languages"]
    voices = json.loads((CONTENT.parent / "profiles" / "voices.json").read_text())
    out = []
    for lang in langs:
        work = CONTENT / cid / lang
        n, text = scene_info(work)
        eng = "voice:veena" if str(voices.get(lang, {}).get("voice", "")).startswith("veena:") else "voice:kokoro"
        out.append({"name": f"voice {lang}", "files": [work / "audio" / f"{i:02d}.wav" for i in range(n)], "rate_key": eng, "lang": lang})
    for lang in [primary] + [l for l in langs if l != primary]:
        work = CONTENT / cid / lang
        n, text = scene_info(work)
        imgs = [work / "img" / f"{i:02d}_raw.png" for i in range(n)]
        out.append({"name": f"images {lang}", "files": imgs, "rate_key": "images" if lang == primary else "text_scene", "lang": lang,
                    "units_override": None if lang == primary else len(text)})
        out.append({"name": f"render {lang}", "files": [work / f"{cid}-{lang}.mp4"], "rate_key": "render", "lang": lang})
    return out


def snapshot(cid):
    rates, now, rows, total_left, running_seen = load_rates(), time.time(), [], 0.0, False
    for st in steps_for(cid):
        files = st["files"]
        done = sum(1 for f in files if f.exists())
        total = len(files)
        if st["rate_key"] == "text_scene":
            per = rates["text_scene"]
            units_left = (st["units_override"] or 0) if done < total else 0
        else:
            per = measured_rate([f for f in files if f.exists()]) or rates[st["rate_key"]]
            units_left = total - done
        if total and done == total:
            status = "done"
        elif not running_seen and (done or all(r["status"] == "done" for r in rows)):
            status = "running"
        else:
            status = "waiting"
        if status == "running":
            running_seen = True
            last = max((f.stat().st_mtime for f in files if f.exists()), default=None)
            since = (now - last) if last else 0
            eta = max(0.0, units_left * per - min(since, per))
        else:
            eta = 0.0 if status == "done" else units_left * per
        total_left += eta
        rows.append({"step": st["name"], "status": status, "done": done, "total": total, "sec_per_unit": round(per, 1), "eta_s": round(eta)})
    finish = datetime.now() + timedelta(seconds=total_left)
    return {"content": cid, "steps": rows, "eta_total_s": round(total_left), "finish_at": finish.strftime("%H:%M"), "checked_at": datetime.now().strftime("%H:%M:%S")}


def learn_from(cid):
    for st in steps_for(cid):
        files = [f for f in st["files"] if f.exists()]
        if st["rate_key"] in ("voice:veena", "voice:kokoro", "images") and len(files) == len(st["files"]) and len(files) > 2:
            r = measured_rate(files)
            if r:
                learn(st["rate_key"], r)


def fmt_s(s):
    s = int(s)
    return f"{s // 60}m{s % 60:02d}s" if s >= 60 else f"{s}s"


def render_table(snap):
    icon = {"done": "✅", "running": "🔄", "waiting": "⏳"}
    lines = [f"{snap['content']} progress at {snap['checked_at']} — remaining ≈ {fmt_s(snap['eta_total_s'])}, finish ≈ {snap['finish_at']}", ""]
    lines.append(f"{'step':14s} {'status':9s} {'progress':>9s} {'per unit':>9s} {'time left':>10s}")
    for r in snap["steps"]:
        lines.append(f"{r['step']:14s} {icon[r['status']]} {r['status']:7s} {r['done']:>4d}/{r['total']:<4d} {fmt_s(r['sec_per_unit']):>9s} {fmt_s(r['eta_s']) if r['status'] != 'done' else '—':>10s}")
    return "\n".join(lines)


def oneline(snap):
    cur = next((r for r in snap["steps"] if r["status"] == "running"), None)
    if not cur:
        return f"{snap['checked_at']} {snap['content']}: all steps complete" if all(r["status"] == "done" for r in snap["steps"]) else f"{snap['checked_at']} {snap['content']}: idle (next: {next(r['step'] for r in snap['steps'] if r['status'] != 'done')})"
    done_steps = sum(r["status"] == "done" for r in snap["steps"])
    return (f"{snap['checked_at']} {snap['content']}: {cur['step']} {cur['done']}/{cur['total']} (step left {fmt_s(cur['eta_s'])}) · "
            f"steps {done_steps}/{len(snap['steps'])} done · total left ≈ {fmt_s(snap['eta_total_s'])} · finish ≈ {snap['finish_at']}")
