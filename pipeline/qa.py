import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from contextlib import contextmanager
from pathlib import Path

from . import DATA, ROOT, db

STANDARD = {"width": 1080, "height": 1920, "fps": 30, "lufs": (-16.5, -13.0), "true_peak_max": -1.0, "max_seconds": 60.0, "target_seconds": (35.0, 55.0)}
CER = {"reject": 0.30, "warn": 0.15, "warn_only": ("gu", "te", "ta", "kn", "ml", "bn", "pa", "mr")}
SPEECH_RATE = {"warn": 0.25, "reject": 0.40, "min_seconds": 1.5}
MUSIC_UNDER_SPEECH_DB = 12.0
FIRST_FRAME_MIN = 0.05
PHASH_MIN_BITS = 8
DENSITY = (0.03, 0.45)
FAMILY_PASS = 80
WEIGHT = {"reject": 2, "warn": 1}
FAMILIES = ("story", "visual", "audio", "final")
CACHE = DATA / "cache" / "qa"
LOCK = DATA / "heavy.lock"
VISUAL_CAL = DATA / "qa_visual_calibration.json"
_HELD = []
_WHISPER = {}


@contextmanager
def heavy_lock(wait=15, timeout=4 * 3600, label="qa"):
    if _HELD:
        yield
        return
    t0 = time.time()
    while True:
        try:
            LOCK.mkdir(parents=True)
            break
        except FileExistsError:
            if time.time() - t0 > timeout:
                raise TimeoutError(f"{LOCK} held for over {timeout} s")
            print(f"  waiting for {LOCK.relative_to(ROOT)} (another heavy model run)", flush=True)
            time.sleep(wait)
    (LOCK / "owner").write_text(f"{label} pid {os.getpid()} {db.now()}")
    _HELD.append(True)
    try:
        yield
    finally:
        _HELD.clear()
        shutil.rmtree(LOCK, ignore_errors=True)


class LazyLock:
    def __init__(self):
        self.cm = None

    def need(self):
        if self.cm is None and not _HELD:
            self.cm = heavy_lock()
            self.cm.__enter__()

    def release(self):
        if self.cm is not None:
            self.cm.__exit__(None, None, None)
            self.cm = None


LAZY = LazyLock()


def chk(name, family, cls, ok, issues=(), data=None, skipped=False, note=None):
    c = {"name": name, "family": family, "class": cls, "ok": bool(ok), "issues": list(issues), "data": data or {}}
    if skipped:
        c["skipped"] = True
    if note:
        c["note"] = note
    return c


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ff(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=True, text=True).stderr


def probe(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate:format=duration", "-of", "json", str(video)], capture_output=True, text=True)
    return json.loads(out.stdout)


def format_of(work_dir):
    mp = Path(work_dir).parent / "manifest.json" if work_dir else None
    fmt = json.loads(mp.read_text()).get("format", "short") if mp and mp.exists() else "short"
    sys.path.insert(0, str(ROOT))
    import frame

    lim = frame.limits(fmt)
    return fmt, {**STANDARD, "width": lim["width"], "height": lim["height"], "max_seconds": lim["max"], "target_seconds": lim["target"]}


def check_format(video, std=None):
    STANDARD = std or globals()["STANDARD"]
    p = probe(video)
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    a = next((s for s in p["streams"] if s["codec_type"] == "audio"), None)
    num, den = v["r_frame_rate"].split("/")
    fps = round(int(num) / int(den), 2)
    dur = float(p["format"]["duration"])
    issues = []
    if (v["width"], v["height"]) != (STANDARD["width"], STANDARD["height"]):
        issues.append(f"resolution {v['width']}x{v['height']} (expected {STANDARD['width']}x{STANDARD['height']})")
    if abs(fps - STANDARD["fps"]) > 0.1:
        issues.append(f"fps {fps}")
    if not a:
        issues.append("no audio stream")
    return chk("format", "final", "reject", not issues, issues, {"video": v["codec_name"], "audio": a and a["codec_name"], "fps": fps, "seconds": round(dur, 2)})


def duration_checks(seconds, std=None):
    STANDARD = std or globals()["STANDARD"]
    lo, hi = STANDARD["target_seconds"]
    out = [chk("duration", "final", "reject", seconds < STANDARD["max_seconds"], [] if seconds < STANDARD["max_seconds"] else [f"duration {seconds:.2f} s ≥ {STANDARD['max_seconds']:.1f} s"], {"seconds": round(seconds, 2)})]
    out.append(chk("duration_target", "final", "warn", lo <= seconds <= hi, [] if lo <= seconds <= hi else [f"duration {seconds:.2f} s outside {lo:.0f}–{hi:.0f} s"], {"seconds": round(seconds, 2)}))
    return out


def check_loudness(video):
    err = ff(["-i", str(video), "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = err[err.rfind("Summary:"):]
    integ = float(re.search(r"I:\s+(-?[\d.]+) LUFS", tail).group(1))
    peak_m = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", tail)
    peak = float(peak_m.group(1)) if peak_m and peak_m.group(1) != "-inf" else None
    lra = float(re.search(r"LRA:\s+(-?[\d.]+) LU", tail).group(1))
    issues = []
    lo, hi = STANDARD["lufs"]
    if not lo <= integ <= hi:
        issues.append(f"integrated loudness {integ} LUFS outside {lo}..{hi}")
    if peak is not None and peak > STANDARD["true_peak_max"]:
        issues.append(f"true peak {peak} dBFS above {STANDARD['true_peak_max']} (clipping risk)")
    return chk("loudness", "final", "reject", not issues, issues, {"lufs": integ, "true_peak_dbfs": peak, "lra": lra})


def check_black_and_freeze(video):
    err = ff(["-i", str(video), "-vf", "blackdetect=d=0.3:pix_th=0.04,freezedetect=n=0.0008:d=2.5", "-an", "-f", "null", "-"])
    blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)
    freezes = re.findall(r"freeze_start: ([\d.]+)", err)
    issues = [f"black frames {float(s):.2f}-{float(e):.2f}s" for s, e in blacks]
    issues += [f"frozen picture from {float(s):.2f}s (>=2.5s with no change)" for s in freezes]
    return chk("black_freeze", "final", "reject", not issues, issues, {"black": len(blacks), "freeze": len(freezes)})


def check_silence(video, max_gap=1.6):
    err = ff(["-i", str(video), "-af", f"silencedetect=noise=-42dB:d={max_gap}", "-vn", "-f", "null", "-"])
    gaps = re.findall(r"silence_start: ([\d.]+)", err)
    issues = [f"near-silence >= {max_gap}s at {float(s):.2f}s" for s in gaps if float(s) > 0.5]
    return chk("silence", "final", "warn", not issues, issues, {"gaps": len(gaps)})


def normalize(text, language=None):
    from .numwords import spell_numbers

    if language:
        text = spell_numbers(text, language)
    text = unicodedata.normalize("NFC", text).replace("ज्ञ", "ग्य").replace("\u093c", "").replace("\u0901", "\u0902").lower()
    return re.sub(r"[\W_]+", "", text)


def char_error(ref, hyp, language=None):
    r, h = normalize(ref, language), normalize(hyp, language)
    m = sum(b.size for b in difflib.SequenceMatcher(None, r, h, autojunk=False).get_matching_blocks())
    return round(1 - m / max(1, len(r)), 3), round(len(h) / max(1, len(r)), 2)


def whisper_model(language):
    name = "small" if language == "en" else "large-v3-turbo"
    if name not in _WHISPER:
        LAZY.need()
        _WHISPER.clear()
        from faster_whisper import WhisperModel

        _WHISPER[name] = WhisperModel(name, device="cpu", compute_type="int8")
    return name, _WHISPER[name]


def transcript(wav, language):
    sha = file_sha256(wav)
    side = wav.with_suffix(".heard.json")
    if side.exists():
        try:
            d = json.loads(side.read_text())
        except ValueError:
            d = {}
        if d.get("wav_sha256") == sha and d.get("text") is not None:
            return d["text"], "render-time transcript (heard.json)"
    wj = wav.with_suffix(".words.json")
    if wj.exists():
        try:
            d = json.loads(wj.read_text())
        except ValueError:
            d = None
        if isinstance(d, dict) and d.get("heard") is not None and d.get("wav_sha256") == sha:
            text = d["heard"] if isinstance(d["heard"], str) else " ".join(w[0] if isinstance(w, list) else str(w) for w in d["heard"])
            return text, "render-time transcript (words.json)"
    cache = CACHE / f"asr-{sha}-{language}.json"
    if cache.exists():
        return json.loads(cache.read_text())["text"], "QA cache (wav hash)"
    import numpy as np

    sys.path.insert(0, str(ROOT))
    import studio

    name, model = whisper_model(language)
    a = studio.read_wav(wav)
    a16 = np.interp(np.arange(0, len(a), studio.SR / 16000), np.arange(len(a)), a).astype(np.float32)
    segs, _ = model.transcribe(a16, language=language, beam_size=5)
    text = " ".join(s.text.strip() for s in segs)
    CACHE.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"text": text, "model": name, "language": language, "wav": str(wav), "at": db.now()}, ensure_ascii=False))
    return text, f"whisper {name} (cached now)"


def check_narration(work_dir, script, language):
    scenes, issues, sources = [], [], set()
    worst = "ok"
    for i, sc in enumerate(script["scenes"]):
        wav = Path(work_dir) / "audio" / f"{i:02d}.wav"
        heard, src = transcript(wav, language)
        sources.add(src.split(" (")[0] if src.startswith("whisper") else src)
        cer, ratio = char_error(sc["narration"], heard, language)
        scenes.append({"scene": i + 1, "cer": cer, "length_ratio": ratio, "heard": heard})
        level = None
        if cer > CER["reject"] and language not in CER["warn_only"]:
            level = "reject"
        elif cer > CER["warn"] or not 0.85 <= ratio <= 1.2:
            level = "warn"
        if level:
            hint = "Whisper wrote digits where the script has number words; likely a false positive" if re.search(r"\d", heard) and not re.search(r"\d", sc["narration"]) else "listen and regenerate if mispronounced"
            issues.append(f"scene {i + 1}: CER {cer} length ratio {ratio} ({level}) — {hint}")
            worst = "reject" if level == "reject" else ("warn" if worst == "ok" else worst)
    cls = "reject" if worst == "reject" else "warn"
    note = "CER is warn-only for this language until Indic ASR is validated" if language in CER["warn_only"] else "digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear"
    return chk("narration_asr", "audio", cls, not issues, issues, {"scenes": scenes, "transcripts": sorted(sources)}, note=note)


def wav_seconds(wav):
    import soundfile as sf

    info = sf.info(str(wav))
    return info.frames / info.samplerate


def check_speech_rate(work_dir, script, language):
    from . import lint

    rates, _ = lint.load_rates()
    ref = lint.rate_for(rates, language).get("lps")
    rows = []
    for i, sc in enumerate(script["scenes"]):
        secs = wav_seconds(Path(work_dir) / "audio" / f"{i:02d}.wav")
        rows.append({"scene": i + 1, "seconds": round(secs, 2), "letters_per_s": round(lint.letters(sc["narration"]) / secs, 2) if secs else None})
    valid = [r["letters_per_s"] for r in rows if r["letters_per_s"] and r["seconds"] >= SPEECH_RATE["min_seconds"]]
    if not ref:
        ref = sorted(valid)[len(valid) // 2] if valid else None
    issues, worst = [], None
    for r in rows:
        if not ref or not r["letters_per_s"] or r["seconds"] < SPEECH_RATE["min_seconds"]:
            continue
        dev = r["letters_per_s"] / ref - 1
        r["deviation"] = round(dev, 3)
        if abs(dev) > SPEECH_RATE["reject"]:
            issues.append(f"scene {r['scene']}: speech rate {dev:+.0%} vs {language} reference (garble, stutter or truncation?)")
            worst = "reject"
        elif abs(dev) > SPEECH_RATE["warn"]:
            issues.append(f"scene {r['scene']}: speech rate {dev:+.0%} vs {language} reference")
            worst = worst or "warn"
    return chk("speech_rate", "audio", worst or "warn", not issues, issues, {"reference_letters_per_s": ref, "scenes": rows})


def load_timeline(work_dir, script=None):
    p = Path(work_dir) / "timeline.json" if work_dir else None
    if not p or not p.exists():
        return None
    try:
        tl = json.loads(p.read_text())
    except ValueError:
        return None
    if script is not None and len(tl.get("scenes", [])) != len(script["scenes"]):
        return None
    return tl


def narration_windows(work_dir, script):
    tl = load_timeline(work_dir, script)
    if not tl:
        return None
    return [(float(r["narration_start"]), float(r["narration_end"]) - float(r["narration_start"])) for r in tl["scenes"]]


def check_music_under_speech(work_dir, script):
    import numpy as np
    from scipy import signal

    sys.path.insert(0, str(ROOT))
    import studio

    mixp = Path(work_dir) / "mix.wav"
    if not mixp.exists():
        return chk("music_under_speech", "audio", "warn", True, [], {}, skipped=True, note="mix.wav missing; skipped")
    mix = studio.read_wav(mixp)
    sr = studio.SR
    voice = np.zeros_like(mix)
    pos = None
    windows = narration_windows(work_dir, script)
    for i, sc in enumerate(script["scenes"]):
        v = studio.read_wav(Path(work_dir) / "audio" / f"{i:02d}.wav")
        if windows:
            start = int(windows[i][0] * sr)
            end = min(len(mix), start + len(v))
            if end > start:
                voice[start:end] += v[: end - start]
            continue
        lo_s = 0 if pos is None else max(0, pos - int(0.3 * sr))
        hi_s = int(0.8 * sr) if pos is None else pos + int(0.3 * sr)
        n = min(len(v), sr)
        seg = mix[lo_s:hi_s + n]
        if len(seg) < n:
            break
        corr = signal.correlate(seg, v[:n], mode="valid", method="fft")
        start = lo_s + int(np.argmax(corr))
        end = min(len(mix), start + len(v))
        voice[start:end] += v[: end - start]
        pos = start + len(v) + int(float(sc.get("pause", 0.18)) * sr)
    g = float(np.dot(mix, voice) / (np.dot(voice, voice) + 1e-9))
    bed = mix - g * voice
    sos = signal.butter(4, [300, 3400], btype="band", fs=sr, output="sos")
    vb, bb = signal.sosfilt(sos, g * voice), signal.sosfilt(sos, bed)
    frame = int(0.5 * sr)
    margins = []
    for s0 in range(0, len(mix) - frame, frame):
        vr = np.sqrt(np.mean(vb[s0:s0 + frame] ** 2))
        if vr < 0.01:
            continue
        br = np.sqrt(np.mean(bb[s0:s0 + frame] ** 2)) + 1e-9
        margins.append(20 * np.log10(vr / br))
    if not margins:
        return chk("music_under_speech", "audio", "warn", True, [], {}, skipped=True, note="no speech frames found")
    med, p10 = float(np.median(margins)), float(np.percentile(margins, 10))
    ok = med >= MUSIC_UNDER_SPEECH_DB
    return chk("music_under_speech", "audio", "warn", ok, [] if ok else [f"speech-band narration only {med:.1f} dB above the bed (target ≥{MUSIC_UNDER_SPEECH_DB:.0f} dB)"],
               {"median_db": round(med, 1), "p10_db": round(p10, 1), "voice_gain": round(g, 3), "frames": len(margins)})


def style_for(script, style_name):
    sys.path.insert(0, str(ROOT))
    import studio

    return studio.effective_style(style_name, script)


def check_captions(work_dir, script, style_name="chalk"):
    sys.path.insert(0, str(ROOT))
    import studio

    st = style_for(script, style_name)
    cap = studio.Captioner(st)
    limit = studio.CAPTION_MAX_W
    if any(not (Path(work_dir) / "audio" / f"{i:02d}.words.json").exists() for i in range(len(script["scenes"]))):
        LAZY.need()
    wts = studio.scene_word_times(script, Path(work_dir))
    windows = narration_windows(work_dir, script)
    issues, overflow, tight, groups, widest = [], [], [], 0, 0
    for i, sc in enumerate(script["scenes"]):
        toks = studio.caption_tokens(sc["narration"])
        if not wts[i] or len(wts[i]) != len(toks):
            issues.append(f"scene {i + 1}: word timing not aligned (captions fall back to estimated timing)")
        start, dur = windows[i] if windows else (0.0, 5.0)
        prev_end = "."
        for g in studio.scene_caption_groups(script, st, cap, i, start, dur, wts[i]):
            groups += 1
            phrase_start = prev_end[-1] in ".,?!:;।॥—"
            prev_end = g["words"][-1]
            w = cap.width(g["words"])
            widest = max(widest, w)
            if w > limit:
                overflow.append(f"scene {i + 1}: caption '{' '.join(g['words'])}' {int(w)} px > {limit} px")
            elif w > studio.W - 120:
                tight.append(f"scene {i + 1}: {int(w)} px")
            if len(g["words"]) > 1 and g["words"][0] in studio.POSTPOSITIONS and not phrase_start:
                issues.append(f"scene {i + 1}: caption line starts with postposition '{g['words'][0]}'")
    data = {"groups": groups, "timing": "timeline.json" if windows else "relative", "engine_version": studio.engine_version(script)}
    if tight:
        data["tight_info"] = tight
    return [chk("captions", "final", "warn", not issues, issues, data),
            chk("caption_overflow", "final", "reject", not overflow, overflow, {"widest_px": int(widest), "limit_px": limit})]


def font_cmap(path, index=0):
    from fontTools.ttLib import TTCollection, TTFont

    key = (str(path), index)
    if key not in _CMAPS:
        if str(path).lower().endswith((".ttc", ".otc")):
            font = TTCollection(str(path), lazy=True).fonts[index]
        else:
            font = TTFont(str(path), lazy=True)
        _CMAPS[key] = set(font.getBestCmap() or {})
    return _CMAPS[key]


_CMAPS = {}


def needs_glyph(ch):
    return not (ch.isspace() or unicodedata.category(ch) in ("Cc", "Cf", "Zs", "Zl", "Zp"))


def check_glyphs(script, style_name="chalk"):
    sys.path.insert(0, str(ROOT))
    import chalk

    import studio

    chalk.use_fonts(script.get("fonts", "mac"))
    st = style_for(script, style_name)
    cap_font = (st.get("caption_font", st["font"]), st.get("caption_font_index", 0))
    upper = st.get("caption_upper", True)
    jobs = []
    for i, sc in enumerate(script["scenes"]):
        text = sc.get("narration", "")
        jobs.append((f"scene {i + 1} narration", text.upper() if upper else text, cap_font))
        if sc.get("emphasis"):
            jobs.append((f"scene {i + 1} emphasis", sc["emphasis"], (cap_font[0], 0)))
        if sc.get("devanagari"):
            lines = "".join(sc["devanagari"])
            f = chalk.font_for(lines, 80)
            jobs.append((f"scene {i + 1} verse", lines, (f.path, getattr(f, "index", 0))))
        if sc.get("source"):
            f = chalk.font_for(sc["source"], 40)
            jobs.append((f"scene {i + 1} verse source", sc["source"], (f.path, getattr(f, "index", 0))))
    th = script.get("thumbnail") or {}
    for k in ("title", "episode", "series", "subtitle"):
        if th.get(k):
            f = chalk.font_for(th[k], 58)
            jobs.append((f"thumbnail {k}", th[k], (f.path, getattr(f, "index", 0))))
    if th.get("devanagari"):
        jobs.append(("thumbnail devanagari", th["devanagari"], (chalk.devanagari_font(), 0)))
    issues, checked = [], 0
    for where, text, (path, idx) in jobs:
        cmap = font_cmap(path, idx)
        miss = sorted({ch for ch in text if needs_glyph(ch) and ord(ch) not in cmap})
        checked += 1
        if miss:
            issues.append(f"{where}: {' '.join(f'{c} U+{ord(c):04X}' for c in miss)} missing from {Path(path).name}#{idx}")
    return chk("glyph_coverage", "final", "reject", not issues, issues, {"texts": checked, "fontset": chalk.FONTSET["name"]})


def frame_at(video, t):
    import numpy as np

    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", "-vf", "scale=270:480", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    a = np.frombuffer(out.stdout, dtype=np.uint8)
    return a.reshape(480, 270, 3) if a.size == 480 * 270 * 3 else None


def non_board_share(frame):
    import numpy as np

    lum = frame.astype(np.float32).max(axis=2) / 255
    board = float(np.median(lum))
    return float(np.mean(lum > board + 0.18))


def check_first_frame(video):
    data = {}
    for t in (0.0, 0.5):
        f = frame_at(video, t)
        data[f"t{t}"] = round(non_board_share(f), 4) if f is not None else None
    v = data.get("t0.5")
    ok = v is not None and v >= FIRST_FRAME_MIN
    return chk("first_frame", "final", "warn", ok, [] if ok else [f"non-board pixel share at 0.5 s is {v} (< {FIRST_FRAME_MIN}); frame 0 is a near-empty board"], data, note="style decision: warn only")


def chalk_map(path):
    import numpy as np
    from PIL import Image
    from scipy import ndimage

    a = np.asarray(Image.open(path).convert("RGB").resize((297, 528), Image.LANCZOS)).astype(np.float32) / 255
    lum = a.max(axis=2)
    floor = ndimage.gaussian_filter(ndimage.minimum_filter(lum, size=11), 2)
    return np.clip(lum - floor - 0.035, 0, 1) * 1.2


def phash(path):
    import numpy as np
    from PIL import Image
    from scipy.fft import dctn

    a = np.asarray(Image.open(path).convert("L").resize((32, 32), Image.LANCZOS)).astype(np.float32)
    d = dctn(a, norm="ortho")[:8, :8].flatten()[1:]
    return d > np.median(d)


def visual_stats(path):
    import numpy as np

    c = chalk_map(path)
    h = c.shape[0]
    total = float(c.mean()) + 1e-9
    return {"density": float(np.mean(c > 0.1)), "top": float(c[: int(h * 0.12)].mean()) / total, "bottom": float(c[int(h * 0.75):].mean()) / total}


def visual_calibration():
    if VISUAL_CAL.exists():
        return json.loads(VISUAL_CAL.read_text())
    import numpy as np

    stats = [visual_stats(p) for p in sorted((ROOT / "content").glob("C*/*/img/*_raw.png"))]
    if not stats:
        return {"top_p90": 1.0, "bottom_p90": 1.0, "n": 0}
    cal = {"top_p90": round(float(np.percentile([s["top"] for s in stats], 90)), 3), "bottom_p90": round(float(np.percentile([s["bottom"] for s in stats], 90)), 3), "n": len(stats),
           "method": "chalk-stroke energy in the top 12% / bottom 25% band relative to the whole image, p90 over every existing raw scene image", "at": db.now()}
    VISUAL_CAL.parent.mkdir(exist_ok=True)
    VISUAL_CAL.write_text(json.dumps(cal, indent=2))
    return cal


def visual_checks(work_dir, script):
    sys.path.insert(0, str(ROOT))
    import studio

    seen, raws = set(), []
    for i in range(len(script["scenes"])):
        try:
            p = studio.raw_path(script, Path(work_dir), i)
        except (ValueError, TypeError):
            p = Path(work_dir) / "img" / f"{i:02d}_raw.png"
        if p.exists() and p not in seen:
            seen.add(p)
            raws.append((i, p))
    if not raws:
        return [chk("visual", "visual", "warn", True, [], {}, skipped=True, note="no img/NN_raw.png found")]
    out = []
    if shutil.which("tesseract"):
        hits = []
        for i, p in raws:
            r = subprocess.run(["tesseract", str(p), "-", "--psm", "11"], capture_output=True, text=True)
            txt = re.sub(r"[^A-Za-z\u0900-\u097f]", "", r.stdout)
            if len(txt) >= 3:
                hits.append(f"scene {i + 1}: OCR found '{txt[:30]}' (text artifact?)")
        out.append(chk("text_artifacts", "visual", "warn", not hits, hits, {"images": len(raws)}))
    else:
        out.append(chk("text_artifacts", "visual", "warn", True, [], {}, skipped=True, note="tesseract binary not installed (brew install tesseract, Apache-2.0); skipped"))
    hashes = {i: phash(p) for i, p in raws}
    dup = []
    for a in hashes:
        for b in hashes:
            if a < b:
                sa, sb = script["scenes"][a], script["scenes"][b]
                if sa.get("image") is not None and sa.get("image") == sb.get("image"):
                    continue
                d = int((hashes[a] != hashes[b]).sum())
                if d < PHASH_MIN_BITS:
                    dup.append(f"scenes {a + 1} and {b + 1}: perceptual hash distance {d} bits (< {PHASH_MIN_BITS})")
    out.append(chk("near_duplicates", "visual", "warn", not dup, dup, {"images": len(raws)}))
    cal = visual_calibration()
    dens, zone, rows = [], [], []
    for i, p in raws:
        s = visual_stats(p)
        rows.append({"scene": i + 1, **{k: round(v, 3) for k, v in s.items()}})
        if not DENSITY[0] <= s["density"] <= DENSITY[1]:
            dens.append(f"scene {i + 1}: chalk density {s['density']:.1%} outside {DENSITY[0]:.0%}–{DENSITY[1]:.0%}")
        if s["top"] > cal["top_p90"]:
            zone.append(f"scene {i + 1}: stroke energy in the title zone (top 12%) {s['top']:.2f} > p90 {cal['top_p90']}")
        if s["bottom"] > cal["bottom_p90"]:
            zone.append(f"scene {i + 1}: stroke energy in the caption zone (bottom 25%) {s['bottom']:.2f} > p90 {cal['bottom_p90']}")
    out.append(chk("chalk_density", "visual", "warn", not dens, dens, {"scenes": rows}))
    out.append(chk("safe_zones", "visual", "warn", not zone, zone, {"calibration": {k: cal.get(k) for k in ("top_p90", "bottom_p90", "n")}}))
    hub = Path.home() / ".cache" / "huggingface" / "hub"
    present = any(hub.glob("models--facebook--dinov2*")) if hub.exists() else False
    out.append(chk("character_similarity", "visual", "warn", True, [], {"model_present": present}, skipped=True,
                   note="DINOv2 similarity is a human flag only; " + ("model cached but no character reference sheets exist yet" if present else "model not present locally and not downloaded")))
    return out


def speaker_cache(wav):
    return CACHE / f"spk-{file_sha256(wav)}.npz"


def scene_embeddings(wav, win):
    import numpy as np

    sys.path.insert(0, str(ROOT))
    import studio
    from . import speaker as spk

    cp = speaker_cache(wav)
    if cp.exists():
        d = np.load(cp)
        if float(d["win"]) == win:
            return d["whole"], d["windows"], d["starts"], d["f0"]
    LAZY.need()
    a = studio.read_wav(wav)
    whole = spk.embed(a)
    n, step = int(win * spk.SR), int(win * spk.SR / 2)
    wins, starts, f0 = [], [], []
    for s0 in range(0, max(1, len(a) - n + 1), step):
        seg = a[s0:s0 + n]
        if len(seg) < n or np.sqrt(np.mean(seg ** 2)) < 0.02:
            continue
        wins.append(spk.embed(seg))
        starts.append(s0)
        f0.append(spk.f0_median(seg) or 0.0)
    wins = np.array(wins) if wins else np.zeros((0, len(whole)))
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez(cp, whole=whole, windows=wins, starts=np.array(starts), f0=np.array(f0), win=win)
    return whole, wins, np.array(starts), np.array(f0)


def check_speaker(work_dir, script, language, voice=None, win=2.5, min_window_sim=0.5, min_scene_sim=0.7):
    import numpy as np
    from . import speaker as spk

    ref = None
    if voice:
        rp = spk.reference_path(language, voice.split(":", 1)[-1])
        ref = np.load(rp) if rp.exists() else None
    issues, wsims, scene_sims, f0s = [], [], [], []
    for i in range(len(script["scenes"])):
        whole, wins, starts, f0 = scene_embeddings(Path(work_dir) / "audio" / f"{i:02d}.wav", win)
        if ref is None:
            ref = whole
        ss = float(whole @ ref)
        scene_sims.append(ss)
        if ss < min_scene_sim:
            issues.append(f"scene {i + 1}: whole-scene speaker similarity {ss:.2f} < {min_scene_sim}")
        for e, s0, f in zip(wins, starts, f0):
            ws = float(e @ ref)
            wsims.append(ws)
            if f:
                f0s.append((i, int(s0), float(f)))
            if ws < min_window_sim:
                issues.append(f"scene {i + 1} @{s0 / spk.SR:.1f}s: {win}s-window speaker similarity {ws:.2f} < {min_window_sim} (possible different voice)")
    med = float(np.median([f for _, _, f in f0s])) if f0s else None
    for i, s0, f in f0s:
        if med and abs(12 * np.log2(f / med)) > 7:
            issues.append(f"scene {i + 1} @{s0 / spk.SR:.1f}s: pitch {round(f)} Hz is >7 semitones from median {round(med)} Hz (possible different voice)")
    return chk("speaker_consistency", "audio", "reject", not issues, issues,
               {"windows": len(wsims), "window_median": round(float(np.median(wsims)), 3) if wsims else None, "window_min": round(min(wsims), 3) if wsims else None,
                "scene_min": round(min(scene_sims), 3) if scene_sims else None, "median_f0": med and round(med),
                "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"})


def story_checks(script, language, primary=None):
    from . import lint

    rep = lint.lint_script(script, language, primary)
    by_rule = {}
    for f in rep["findings"]:
        by_rule.setdefault(f["rule"], []).append(f)
    out = []
    for rule in ("duration", "hook", "scene_count", "scene_length", "keywords", "digits", "quote_src", "sources", "edition", "silences", "visual_parity", "reveal", "transition", "shot", "crop", "engine_values"):
        fs = by_rule.get(rule, [])
        cls = "reject" if any(f["level"] == "fail" for f in fs) else "warn"
        if rule in ("reveal", "transition", "shot", "crop", "engine_values") and not fs:
            continue
        out.append(chk(f"lint_{rule}", "story", cls, not fs, [f["message"] for f in fs]))
    out[0]["data"] = {"estimate_s": rep["estimate"]["total"], "basis": rep["estimate"]["basis"]}
    return out


def contact_sheet(video, out_png, n=12):
    p = probe(video)
    dur = float(p["format"]["duration"])
    times = [dur * (k + 0.5) / n for k in range(n)]
    sel = "+".join(f"eq(n\\,{int(t * 30)})" for t in times)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", f"select='{sel}',scale=270:480,tile=6x{(n + 5) // 6}", "-frames:v", "1", str(out_png)], check=True)
    return str(out_png)


def score(checks):
    fam = {}
    for f in FAMILIES:
        cs = [c for c in checks if c["family"] == f and not c.get("skipped")]
        if not cs:
            continue
        total = sum(WEIGHT[c["class"]] for c in cs)
        got = sum(WEIGHT[c["class"]] for c in cs if c["ok"])
        rejects = [c["name"] for c in cs if not c["ok"] and c["class"] == "reject"]
        warns = [c["name"] for c in cs if not c["ok"] and c["class"] == "warn"]
        s = round(100 * got / total)
        fam[f] = {"score": s, "pass": not rejects and s >= FAMILY_PASS, "rejects": rejects, "warns": warns, "checks": len(cs)}
    return fam


def verdict_of(checks, families):
    if any(not c["ok"] and c["class"] == "reject" and not c.get("skipped") for c in checks):
        return "fail"
    if any(not c["ok"] and not c.get("skipped") for c in checks) or any(not f["pass"] for f in families.values()):
        return "warn"
    return "pass"


def primary_script(work_dir):
    m = json.loads((Path(work_dir).parent / "manifest.json").read_text()) if (Path(work_dir).parent / "manifest.json").exists() else {}
    pl = m.get("primary_language")
    if not pl or Path(work_dir).name == pl:
        return None
    p = Path(work_dir).parent / pl / "script.json"
    return json.loads(p.read_text()) if p.exists() else None


EXEMPTABLE = {"duration", "lint_duration", "lint_hook"}


def apply_exemptions(checks, work_dir):
    mp = Path(work_dir).parent / "manifest.json" if work_dir else None
    ex = json.loads(mp.read_text()).get("qa_exempt") if mp and mp.exists() else None
    names = set(ex.get("checks", [])) & EXEMPTABLE if ex else set()
    for c in checks:
        if c["name"] in names and c["class"] == "reject":
            c["class"] = "warn"
            c["data"]["exempt"] = ex.get("reason", "")
    return checks


def run(video, work_dir=None,script_path=None, language="en", variant_id=None, style="chalk", audio_only=False):
    checks = []
    try:
        script = json.loads(Path(script_path).read_text()) if script_path else None
        fmt_name, std = format_of(work_dir)
        if script:
            script.setdefault("format", fmt_name)
            checks += story_checks(script, language, primary_script(work_dir))
        if not audio_only:
            fmt = check_format(video, std)
            checks += [fmt, *duration_checks(fmt["data"]["seconds"], std), check_loudness(video), check_black_and_freeze(video), check_silence(video), check_first_frame(video)]
        if work_dir and script:
            voices = json.loads((ROOT / "profiles" / "voices.json").read_text())
            used = Path(work_dir) / "audio" / "voice.txt"
            voice = used.read_text().strip() if used.exists() else voices.get(language, {}).get("voice")
            th = voices.get("_speaker_thresholds", {}).get(voice or "", {})
            checks += [check_narration(work_dir, script, language), check_speech_rate(work_dir, script, language)]
            checks.append(check_speaker(work_dir, script, language, voice, min_window_sim=th.get("window", 0.5), min_scene_sim=th.get("scene", 0.7)))
            if not audio_only:
                checks.append(check_music_under_speech(work_dir, script))
                checks += check_captions(work_dir, script, style)
                checks.append(check_glyphs(script, style))
                checks += visual_checks(work_dir, script)
    finally:
        LAZY.release()
    checks = apply_exemptions(checks, work_dir)
    families = score(checks)
    verdict = verdict_of(checks, families)
    sha = file_sha256(video) if video and not audio_only else None
    sheet = contact_sheet(video, Path(video).with_suffix(".qa.png")) if video and not audio_only else None
    report = {"video": str(video) if video else None, "kind": "audio" if audio_only else "automated", "mp4_sha256": sha, "verdict": verdict, "families": families, "checks": checks, "contact_sheet": sheet,
              "manual_review_required": ["character consistency", "visual defects / wrong illustrations", "storytelling quality", "native-speaker listen for non-English"],
              "created_at": db.now()}
    if variant_id:
        with db.connect() as con:
            cur = con.execute("INSERT INTO qa_reports (variant_id, kind, verdict, report, created_at, mp4_sha256, scores) VALUES (?,?,?,?,?,?,?)",
                              (variant_id, report["kind"], verdict, json.dumps(report, ensure_ascii=False), db.now(), sha, json.dumps(families)))
            report["id"] = cur.lastrowid
    return report


def markdown(report):
    name = Path(report["video"]).name if report.get("video") else "audio-only"
    lines = [f"# QA report: {name}", "", f"**Verdict: {report['verdict'].upper()}** · {report['created_at']}" + (f" · report #{report['id']}" if report.get("id") else ""), ""]
    if report.get("mp4_sha256"):
        lines += [f"File sha256: `{report['mp4_sha256']}`", ""]
    for f, v in report.get("families", {}).items():
        lines.append(f"- **{f.title()}** {v['score']}/100 {'PASS' if v['pass'] else 'NOT PASSED'}" + (f" · reject: {', '.join(v['rejects'])}" if v["rejects"] else "") + (f" · warn: {', '.join(v['warns'])}" if v["warns"] else ""))
    lines.append("")
    for c in report["checks"]:
        mark = "⏭️" if c.get("skipped") else ("✅" if c["ok"] else ("❌" if c.get("class") == "reject" else "⚠️"))
        data = {k: v for k, v in c["data"].items() if k not in ("scenes",)}
        lines.append(f"- {mark} **{c['name']}** ({c.get('family', '')}/{c.get('class', '')}) {json.dumps(data, ensure_ascii=False)}" + (f" — {c['note']}" if c.get("note") else ""))
        lines += [f"    - {i}" for i in c["issues"]]
    if report.get("contact_sheet"):
        lines += ["", f"Contact sheet: `{report['contact_sheet']}`"]
    lines += ["", "Manual review still required: " + ", ".join(report["manual_review_required"])]
    return "\n".join(lines) + "\n"
