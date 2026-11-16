import json
import re
import subprocess
import sys
import unicodedata

from . import CONTENT, DATA, PROFILES, ROOT, db

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


URL = re.compile(r"^https?://")
EDITION_IN_TEXT = re.compile(r"\(([^)]+)\)\s*$")
QUESTION_WORDS = re.compile(r"\b(how|why|what|who|when|which)\b|कैसे|क्यों|क्या|कौन|કેમ|કેવી|શા|ఎలా|ఎందుకు|ఏమి", re.I)
_VOCAB = {}


def engine_vocab():
    if "v" not in _VOCAB:
        try:
            sys.path.insert(0, str(ROOT))
            import chalk
            import studio

            _VOCAB["v"] = {"transition": tuple(chalk.TRANSITIONS), "reveal": tuple(chalk.REVEALS), "move": tuple(chalk.MOVES), "overlay": tuple(chalk.OVERLAYS),
                           "oneshot": tuple(chalk.ONESHOTS), "bed": tuple(chalk.BEDS), "leitmotif": tuple(chalk.LEITMOTIFS),
                           "shot": tuple(studio.SHOT_HINTS), "angle": tuple(studio.ANGLE_HINTS), "scene_still": studio.scene_still}
        except Exception as e:
            _VOCAB["v"] = {"error": f"{type(e).__name__}: {e}"}
    return _VOCAB["v"]


def as_list(x):
    if x is None or x == "" or x == []:
        return []
    return list(x) if isinstance(x, (list, tuple)) else [x]


def sound_names(x):
    out = []
    for c in as_list(x):
        out.append(c if isinstance(c, str) else (c.get("name") if isinstance(c, dict) else None))
    return out


def engine_value_findings(script):
    v = engine_vocab()
    if "error" in v:
        return [finding("engine_values", "warn", f"engine vocabulary unavailable, values not checked ({v['error'][:120]})")]
    f = []
    scenes = script.get("scenes", [])

    def bad(i, field, value, allowed):
        f.append(finding("engine_values", "fail", f"scene {i + 1}: {field} '{value}' is not one of {', '.join(allowed)}", i + 1))

    for i, sc in enumerate(scenes):
        if sc.get("transition") and sc["transition"] not in v["transition"]:
            bad(i, "transition", sc["transition"], v["transition"])
        if sc.get("reveal") and sc["reveal"] not in v["reveal"]:
            bad(i, "reveal", sc["reveal"], v["reveal"])
        mv = sc.get("move")
        if mv:
            t = mv if isinstance(mv, str) else (mv.get("type") if isinstance(mv, dict) else None)
            if t not in v["move"]:
                bad(i, "move", t, v["move"])
        for o in as_list(sc.get("overlay")):
            if o not in v["overlay"]:
                bad(i, "overlay", o, v["overlay"])
        for field in ("sfx", "hit"):
            for name in sound_names(sc.get(field)):
                if not name or not (name in v["oneshot"] or name in v["bed"] or str(name).startswith("file:")):
                    bad(i, field, name, v["bed"] + v["oneshot"] + ("file:<name>",))
        mu = sc.get("music")
        if isinstance(mu, dict) and mu.get("leitmotif") and mu["leitmotif"] not in v["leitmotif"]:
            bad(i, "music.leitmotif", mu["leitmotif"], v["leitmotif"])
        if sc.get("shot") and sc["shot"] not in v["shot"]:
            bad(i, "shot", sc["shot"], v["shot"])
        if sc.get("angle") and sc["angle"] not in v["angle"]:
            bad(i, "angle", sc["angle"], v["angle"])
        if sc.get("image") not in (None, "", False):
            try:
                v["scene_still"](script, i)
            except (ValueError, TypeError) as e:
                f.append(finding("engine_values", "fail", str(e), i + 1))
    return f


def source_edition(src):
    if isinstance(src, dict):
        return src.get("edition")
    if isinstance(src, str) and not URL.match(src):
        m = EDITION_IN_TEXT.search(src)
        return m.group(1) if m else None
    return None


def source_findings(script):
    f = []
    refs = []
    for k, src in enumerate(script.get("sources") or []):
        if isinstance(src, dict):
            if not src.get("ref"):
                f.append(finding("sources", "fail", f"sources[{k}] object needs a 'ref' (e.g. {{\"ref\": \"VR 1.26.12\", \"edition\": \"vulgate\"}})"))
            refs.append(src)
        elif isinstance(src, str):
            if not URL.match(src):
                refs.append(src)
        else:
            f.append(finding("sources", "fail", f"sources[{k}] must be a string or an object with ref/edition"))
    return f, refs


def title_pattern(title):
    if not title:
        return None
    head = title.split("|")[0]
    if "?" in head or QUESTION_WORDS.search(head):
        return "question"
    if re.search(r"\d", head):
        return "number"
    if re.match(r"\s*(when|जब|જ્યારે|ఎప్పుడు)\b", head, re.I):
        return "when-story"
    return "statement"


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
            if not (sc.get("edition") or script.get("edition") or source_edition(src) or any(source_edition(r) for r in (script.get("sources") or []))):
                f.append(finding("edition", "warn", f"scene {i + 1}: verse card has no edition label (scene or script 'edition')", i + 1))
    src_f, refs = source_findings(script)
    f += src_f
    sourced_editions = bool(refs) and all(source_edition(r) for r in refs)
    if not script.get("sources"):
        f.append(finding("sources", "fail", "script has no sources"))
    elif not script.get("edition") and not sourced_editions:
        f.append(finding("edition", "warn", "no edition: set script 'edition' or give every source one ({\"ref\", \"edition\"} or \"VR 1.26.12 (vulgate)\")"))
    f += engine_value_findings(script)
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


def variant_sources(m, lang):
    from . import gates

    work = CONTENT / m["id"] / lang
    files = gates.variant_files(m, lang)
    script, audio = work / "script.json", work / "audio"
    if not script.exists() and m.get("legacy_folder"):
        legacy = ROOT / m["legacy_folder"]
        sub = {"en": legacy, "hi": legacy / "hindi"}.get(lang)
        if sub and (sub / "script.json").exists():
            script, audio = sub / "script.json", sub / "audio"
    return {"work": work, "script": script, "audio": audio, "video": files["video"], "meta": files["meta"], "legacy": files["legacy"] or script.parent != work}


def wav_len(path):
    import soundfile as sf

    info = sf.info(str(path))
    return info.frames / info.samplerate


def features_row(m, lang, stage):
    src = variant_sources(m, lang)
    work, sp = src["work"], src["script"]
    if not sp.exists():
        return None
    script = json.loads(sp.read_text())
    est = estimate(script, lang)
    video = src["video"]
    dur = ffprobe_duration(video) if video.exists() else None
    hook_secs, speech = est["scene_seconds"][0] if est["scene_seconds"] else None, None
    if (src["audio"] / "00.wav").exists():
        try:
            hook_secs = round(wav_len(src["audio"] / "00.wav"), 2)
            speech = sum(wav_len(src["audio"] / f"{i:02d}.wav") for i in range(len(script["scenes"])))
        except Exception:
            speech = None
    tl_path = work / "timeline.json"
    tl = json.loads(tl_path.read_text()) if tl_path.exists() else None
    s0 = script["scenes"][0] if script["scenes"] else {}
    first_frame = "predrawn" if s0.get("reveal") == "instant" else "blank"
    if tl:
        hook_secs = round(tl["hook_end"] - tl["first_word"], 2)
        sc0 = (tl.get("scenes") or [{}])[0]
        if sc0.get("start_drawn") is not None:
            first_frame = "predrawn" if float(sc0["start_drawn"]) >= 0.7 else ("partial" if float(sc0["start_drawn"]) > 0 else "blank")
        if not dur and tl.get("total"):
            dur = float(tl["total"])
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
    if not slot:
        with db.connect() as con:
            r = con.execute("SELECT COALESCE(published_at, scheduled_for) AS t FROM publications WHERE variant_id=? AND platform='youtube' ORDER BY id DESC LIMIT 1", (f"{m['id']}-{lang}",)).fetchone()
        slot = r["t"] if r else None
    t = gates.parse_time(slot) if slot and slot != gates.NOW else None
    title = None
    if src["meta"].exists():
        try:
            title = (json.loads(src["meta"].read_text()).get("youtube") or {}).get("title")
        except ValueError:
            title = None
    sys.path.insert(0, str(ROOT))
    try:
        import studio

        ev = studio.engine_version(script)
    except Exception:
        ev = int(script.get("engine_version", 1) or 1)
    return {"variant_id": f"{m['id']}-{lang}", "content_id": m["id"], "language": lang, "episode": m.get("episode"), "cohort": db.cohort_for(lang),
            "duration_s": round(dur, 2) if dur else est["total"], "duration_source": ("rendered" if video.exists() else "timeline") if dur else "lint estimate",
            "scenes": len(script["scenes"]), "words": est["words"], "wps": round(est["words"] / speech, 3) if speech else est["rate"],
            "hook_type": hook_type, "hook_words": len(words(s0.get("narration"))), "hook_seconds": hook_secs,
            "first_frame": first_frame, "voice": current_voice(lang, src["audio"].parent),
            "slot_ist": t.astimezone(gates.IST).strftime("%H:%M") if t else None, "weekday": t.astimezone(gates.IST).strftime("%a") if t else None,
            "title_pattern": title_pattern(title), "has_verse": int(any(sc.get("kind") in VERSE_KINDS for sc in script["scenes"])), "stage": stage,
            "engine_version": ev, "updated_at": db.now()}


def backfill_features(stage="backfill"):
    rows = []
    for mpath in sorted(CONTENT.glob("C*/manifest.json")):
        m = json.loads(mpath.read_text())
        for lang in m["languages"]:
            row = log_features(m, lang, stage)
            rows.append((f"{m['id']}-{lang}", row))
    return rows


def log_features(m, lang, stage):
    try:
        row = features_row(m, lang, stage)
    except Exception as e:
        print(f"  feature logging skipped for {m['id']}-{lang}: {e}")
        return None
    if row:
        with db.connect() as con:
            prev = con.execute("SELECT stage FROM features WHERE variant_id=?", (row["variant_id"],)).fetchone()
            if prev and stage in ("backfill", "manual") and prev["stage"] in ("publish", "render", "script"):
                row["stage"] = prev["stage"]
            db.upsert(con, "features", row, key="variant_id")
            con.execute("UPDATE variants SET cohort=?, duration_s=COALESCE(?, duration_s), updated_at=? WHERE id=?", (row["cohort"], row["duration_s"] if row["duration_source"] == "rendered" else None, db.now(), row["variant_id"]))
    return row
