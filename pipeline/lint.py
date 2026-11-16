import json
import re
import subprocess
import unicodedata

from . import CONTENT, DATA, PROFILES, db

DEFAULT_RATES = {"en": 2.81, "hi": 2.80, "gu": 2.3, "te": 1.66}
FALLBACK_RATE = 2.3
LEAD_TAIL = 1.15
DEFAULT_PAUSE = 0.18
RATES_PATH = DATA / "lint_rates.json"
MAX_EST = 57.0
TARGET = (35.0, 55.0)
HOOK_FAIL, HOOK_WARN = 3.0, 2.2
SCENES = (8, 11)
SCENE_SECONDS = (2.5, 7.0)
SILENCES = (2, 3)
SILENCE_MIN = 0.3
DIGIT_OK = ("en", "hi", "mr")
DRAW_MAX = 3
VERSE_SOURCE = re.compile(r"\d+\.\d+\.\d+")
QUOTE = re.compile(r"[“«„\"]([^”»“\"]{3,})[”»“\"]|‘([^’]{3,}\s[^’]*)’")
VERSE_KINDS = ("verse", "shloka")


def words(text):
    return [t for t in (text or "").split() if re.search(r"\w", t)]


def norm(w):
    return re.sub(r"[\W_]", "", w.lower())


def letters(text):
    return sum(1 for ch in (text or "") if unicodedata.category(ch)[0] == "L")


def load_rates():
    rates = {l: {"wps": r, "lps": None} for l, r in DEFAULT_RATES.items()}
    meta = {l: "default (VIDEO_QUALITY_UPGRADE_PLAN §2.4)" for l in rates}
    if RATES_PATH.exists():
        cal = json.loads(RATES_PATH.read_text())
        for l, v in cal.get("languages", {}).items():
            if v.get("rate"):
                rates[l] = {"wps": v["rate"], "lps": v.get("letter_rate")}
                meta[l] = f"calibrated {v.get('at', '')} from {v.get('n', 0)} renders"
    return rates, meta


def rate_for(rates, lang):
    r = rates.get(lang, FALLBACK_RATE)
    return r if isinstance(r, dict) else {"wps": r, "lps": None}


def scene_seconds(sc, rate):
    text = sc.get("narration")
    spoken = letters(text) / rate["lps"] if rate.get("lps") else len(words(text)) / rate["wps"]
    return max(spoken, float(sc.get("dur_hint") or 0))


def estimate(script, lang, rates=None):
    rates = rates or load_rates()[0]
    rate = rate_for(rates, lang)
    secs = [scene_seconds(sc, rate) for sc in script["scenes"]]
    pauses = sum(float(sc.get("pause", DEFAULT_PAUSE)) for sc in script["scenes"])
    return {"rate": rate["wps"], "letter_rate": rate.get("lps"), "basis": "letters" if rate.get("lps") else "words",
            "scene_seconds": [round(s, 2) for s in secs], "pauses": round(pauses, 2), "total": round(sum(secs) + pauses + LEAD_TAIL, 2),
            "words": sum(len(words(sc.get("narration"))) for sc in script["scenes"])}


def ffprobe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def finding(rule, level, msg, scene=None):
    return {"rule": rule, "level": level, "message": msg, **({"scene": scene} if scene is not None else {})}


def lint_script(script, lang, primary=None, rates=None):
    rates_all, meta = load_rates() if rates is None else (rates, {})
    est = estimate(script, lang, rates_all)
    f = []
    scenes = script.get("scenes", [])
    total = est["total"]
    if total > MAX_EST:
        f.append(finding("duration", "fail", f"estimated {total:.1f} s > {MAX_EST:.0f} s (rate {est['rate']} w/s, {est['words']} words, pauses {est['pauses']} s, lead/tail {LEAD_TAIL} s)"))
    elif not TARGET[0] <= total <= TARGET[1]:
        f.append(finding("duration", "warn", f"estimated {total:.1f} s outside {TARGET[0]:.0f}–{TARGET[1]:.0f} s"))
    if scenes:
        hook = est["scene_seconds"][0]
        if hook > HOOK_FAIL:
            f.append(finding("hook", "fail", f"hook scene spoken {hook:.1f} s > {HOOK_FAIL} s", 1))
        elif hook > HOOK_WARN:
            f.append(finding("hook", "warn", f"hook scene spoken {hook:.1f} s > {HOOK_WARN} s", 1))
    if not SCENES[0] <= len(scenes) <= SCENES[1]:
        f.append(finding("scene_count", "warn", f"{len(scenes)} scenes (target {SCENES[0]}–{SCENES[1]})"))
    for i, s in enumerate(est["scene_seconds"]):
        if i and not SCENE_SECONDS[0] <= s <= SCENE_SECONDS[1]:
            f.append(finding("scene_length", "warn", f"scene {i + 1} spoken {s:.1f} s (target {SCENE_SECONDS[0]}–{SCENE_SECONDS[1]} s)", i + 1))
    for i, sc in enumerate(scenes):
        toks = {norm(t) for t in words(sc.get("narration"))}
        missing = [k for k in sc.get("keywords", []) if norm(k) and norm(k) not in toks]
        if missing:
            f.append(finding("keywords", "fail", f"scene {i + 1}: keywords not in narration: {', '.join(missing)}", i + 1))
        if lang not in DIGIT_OK and re.search(r"\d", sc.get("narration", "")):
            f.append(finding("digits", "fail", f"scene {i + 1}: digits in {lang} narration (write numbers as words)", i + 1))
        q = QUOTE.search(sc.get("narration", ""))
        if q and not sc.get("quote_src") and not (sc.get("kind") in VERSE_KINDS and sc.get("source")):
            f.append(finding("quote_src", "fail", f"scene {i + 1}: quoted text “{(q.group(1) or q.group(2))[:40]}” without quote_src", i + 1))
        if sc.get("kind") in VERSE_KINDS:
            src = sc.get("source", "")
            if not VERSE_SOURCE.search(src):
                f.append(finding("sources", "fail", f"scene {i + 1}: verse card source '{src}' lacks a kanda.sarga.verse locator", i + 1))
            if not (sc.get("edition") or script.get("edition")):
                f.append(finding("edition", "warn", f"scene {i + 1}: verse card has no edition label (scene or script 'edition')", i + 1))
    if not script.get("sources"):
        f.append(finding("sources", "fail", "script has no sources"))
    elif not script.get("edition"):
        f.append(finding("edition", "warn", "script has no 'edition' (which text edition the sources cite)"))
    silences = sum(1 for sc in scenes if float(sc.get("pause", DEFAULT_PAUSE)) >= SILENCE_MIN)
    if not SILENCES[0] <= silences <= SILENCES[1]:
        f.append(finding("silences", "warn", f"{silences} planned silences (pause ≥{SILENCE_MIN} s); target {SILENCES[0]}–{SILENCES[1]}"))
    if any("reveal" in sc for sc in scenes):
        draws = sum(1 for sc in scenes if sc.get("reveal", "draw") == "draw")
        if draws > DRAW_MAX:
            f.append(finding("reveal", "fail", f"{draws} scenes use the full 'draw' reveal (max {DRAW_MAX})"))
        if scenes[0].get("reveal", "draw") not in ("instant",):
            f.append(finding("reveal", "warn", "scene 1 reveal is not 'instant' (frame 0 should be readable)", 1))
    if any("transition" in sc for sc in scenes):
        erases = sum(1 for sc in scenes[1:] if sc.get("transition", "erase") == "erase")
        if not 1 <= erases <= 3:
            f.append(finding("transition", "warn", f"'erase' transition used {erases} times (target 1–3)"))
    if any("shot" in sc for sc in scenes):
        shots = [sc.get("shot") for sc in scenes]
        if len({s for s in shots if s}) < 3:
            f.append(finding("shot", "warn", "fewer than 3 distinct shot sizes"))
        run = 1
        for a, b in zip(scenes, scenes[1:]):
            same = a.get("shot") and a.get("shot") == b.get("shot") and json.dumps(a.get("move"), sort_keys=True) == json.dumps(b.get("move"), sort_keys=True)
            run = run + 1 if same else 1
            if run > 2:
                f.append(finding("shot", "warn", f"more than 2 consecutive shots with the same shot and move ({a.get('shot')})"))
                break
    for i, sc in enumerate(scenes):
        crop = sc.get("crop")
        if isinstance(crop, list) and len(crop) == 3 and crop[2] < 0.5 and sc.get("image") is not None:
            f.append(finding("crop", "warn", f"scene {i + 1}: crop width_frac {crop[2]} < 0.5 of a reused still (soft beyond 2×)", i + 1))
    if primary is not None:
        ps = primary.get("scenes", [])
        if len(ps) != len(scenes):
            f.append(finding("visual_parity", "fail", f"{len(scenes)} scenes vs {len(ps)} in the primary language"))
        else:
            for i, (a, b) in enumerate(zip(scenes, ps)):
                for k in ("visual", "image", "crop", "kind"):
                    if a.get(k) != b.get(k):
                        f.append(finding("visual_parity", "fail", f"scene {i + 1}: '{k}' differs from the primary language", i + 1))
    level = "fail" if any(x["level"] == "fail" for x in f) else ("warn" if f else "pass")
    return {"language": lang, "verdict": level, "estimate": est, "rate_source": meta.get(lang, "given"), "findings": f, "at": db.now()}


def lint(cid, langs=None, write=True):
    m = json.loads((CONTENT / cid / "manifest.json").read_text())
    langs = langs or m["languages"]
    prim_lang = m.get("primary_language", m["languages"][0])
    prim_path = CONTENT / cid / prim_lang / "script.json"
    primary = json.loads(prim_path.read_text()) if prim_path.exists() else None
    out = {}
    for lang in langs:
        p = CONTENT / cid / lang / "script.json"
        if not p.exists():
            out[lang] = {"language": lang, "verdict": "fail", "findings": [finding("script", "fail", f"missing {p.relative_to(CONTENT.parent)}")], "estimate": None}
            continue
        script = json.loads(p.read_text())
        rep = lint_script(script, lang, primary if lang != prim_lang else None)
        from .gates import script_sha256

        rep["script_sha256"] = script_sha256(p)
        out[lang] = rep
        if write:
            (CONTENT / cid / lang / "lint.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False))
    return out


def markdown(results):
    lines = []
    for lang, r in results.items():
        est = r.get("estimate") or {}
        lines.append(f"{lang}: {r['verdict'].upper()}" + (f"  est {est.get('total')} s · {est.get('words')} words · basis {est.get('basis')} ({est.get('letter_rate') or est.get('rate')} per s; {r.get('rate_source', '')})" if est else ""))
        for x in r["findings"]:
            lines.append(f"  {'✖' if x['level'] == 'fail' else '!'} [{x['rule']}] {x['message']}")
    return "\n".join(lines)


def current_voice(lang, work):
    vt = work / "audio" / "voice.txt"
    if vt.exists():
        return vt.read_text().strip()
    vp = json.loads((PROFILES / "voices.json").read_text()).get(lang, {})
    return vp.get("voice")


def calibrate(write=True):
    voices = json.loads((PROFILES / "voices.json").read_text())
    per = {}
    for mpath in sorted(CONTENT.glob("C*/manifest.json")):
        m = json.loads(mpath.read_text())
        for lang in m["languages"]:
            work = mpath.parent / lang
            video, sp = work / f"{m['id']}-{lang}.mp4", work / "script.json"
            if not video.exists() or not sp.exists():
                continue
            voice = current_voice(lang, work)
            if voice != voices.get(lang, {}).get("voice"):
                continue
            script = json.loads(sp.read_text())
            dur = ffprobe_duration(video)
            if not dur:
                continue
            w = sum(len(words(sc.get("narration"))) for sc in script["scenes"])
            lt = sum(letters(sc.get("narration")) for sc in script["scenes"])
            pauses = sum(float(sc.get("pause", DEFAULT_PAUSE)) for sc in script["scenes"])
            per.setdefault(lang, []).append({"variant": f"{m['id']}-{lang}", "words": w, "letters": lt, "seconds": round(dur, 2), "speech": round(dur - pauses - LEAD_TAIL, 2), "voice": voice})
    out = {"method": "rate = Σwords / Σ(rendered duration − Σpause − 1.15 s lead/tail) over renders made with the currently approved voice; letter_rate likewise with Unicode letters (combining marks excluded), which varies less across episodes and is what the estimate uses", "at": db.now(), "languages": {}}
    for lang, rows in per.items():
        speech = sum(r["speech"] for r in rows)
        rate = sum(r["words"] for r in rows) / speech
        lrate = sum(r["letters"] for r in rows) / speech
        for r in rows:
            pauses = r["seconds"] - r["speech"] - LEAD_TAIL
            r["estimate"] = round(r["letters"] / lrate + pauses + LEAD_TAIL, 2)
            r["error"] = round(r["estimate"] - r["seconds"], 2)
            r["word_estimate_error"] = round(r["words"] / rate + pauses + LEAD_TAIL - r["seconds"], 2)
        out["languages"][lang] = {"rate": round(rate, 3), "letter_rate": round(lrate, 3), "n": len(rows), "max_abs_error_s": max(abs(r["error"]) for r in rows), "voice": rows[0]["voice"], "at": out["at"][:10], "default": DEFAULT_RATES.get(lang), "renders": rows}
    if write:
        RATES_PATH.parent.mkdir(exist_ok=True)
        RATES_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    return out


def features_row(m, lang, stage):
    work = CONTENT / m["id"] / lang
    sp = work / "script.json"
    if not sp.exists():
        return None
    script = json.loads(sp.read_text())
    est = estimate(script, lang)
    video = work / f"{m['id']}-{lang}.mp4"
    dur = ffprobe_duration(video) if video.exists() else None
    hook_secs, speech = est["scene_seconds"][0] if est["scene_seconds"] else None, None
    wav0 = work / "audio" / "00.wav"
    if wav0.exists():
        try:
            import soundfile as sf

            info = sf.info(str(wav0))
            hook_secs = round(info.frames / info.samplerate, 2)
            speech = 0.0
            for i in range(len(script["scenes"])):
                wi = sf.info(str(work / "audio" / f"{i:02d}.wav"))
                speech += wi.frames / wi.samplerate
        except Exception:
            speech = None
    hooks = work / "hooks.json"
    hook_type = None
    if hooks.exists():
        sel = next((h for h in json.loads(hooks.read_text()) if h.get("selected")), None)
        hook_type = (sel or {}).get("type")
    from . import gates

    slot = gates.approved_time(m, lang, "youtube")
    sched = work / "schedule.json"
    if not slot and sched.exists():
        slot = json.loads(sched.read_text()).get("publish_at")
    t = gates.parse_time(slot) if slot and slot != gates.NOW else None
    s0 = script["scenes"][0] if script["scenes"] else {}
    return {"variant_id": f"{m['id']}-{lang}", "content_id": m["id"], "language": lang, "episode": m.get("episode"), "cohort": db.cohort_for(lang),
            "duration_s": round(dur, 2) if dur else est["total"], "duration_source": "rendered" if dur else "lint estimate",
            "scenes": len(script["scenes"]), "words": est["words"], "wps": round(est["words"] / speech, 3) if speech else est["rate"],
            "hook_type": hook_type, "hook_words": len(words(s0.get("narration"))), "hook_seconds": hook_secs,
            "first_frame": "predrawn" if s0.get("reveal") == "instant" else "blank", "voice": current_voice(lang, work),
            "slot_ist": t.astimezone(gates.IST).strftime("%H:%M") if t else None, "weekday": t.astimezone(gates.IST).strftime("%a") if t else None,
            "title_pattern": None, "has_verse": int(any(sc.get("kind") in VERSE_KINDS for sc in script["scenes"])), "stage": stage, "updated_at": db.now()}


def log_features(m, lang, stage):
    try:
        row = features_row(m, lang, stage)
    except Exception as e:
        print(f"  feature logging skipped for {m['id']}-{lang}: {e}")
        return None
    if row:
        with db.connect() as con:
            db.upsert(con, "features", row, key="variant_id")
            con.execute("UPDATE variants SET cohort=?, duration_s=COALESCE(?, duration_s), updated_at=? WHERE id=?", (row["cohort"], row["duration_s"] if row["duration_source"] == "rendered" else None, db.now(), row["variant_id"]))
    return row
