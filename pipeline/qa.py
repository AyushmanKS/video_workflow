import difflib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

from . import ROOT, db

STANDARD = {"width": 1080, "height": 1920, "fps": 30, "lufs": (-16.5, -13.0), "true_peak_max": -1.0, "max_seconds": 180}


def ff(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=True, text=True).stderr


def probe(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate:format=duration", "-of", "json", str(video)], capture_output=True, text=True)
    return json.loads(out.stdout)


def check_format(video):
    p = probe(video)
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    a = next((s for s in p["streams"] if s["codec_type"] == "audio"), None)
    num, den = v["r_frame_rate"].split("/")
    fps = round(int(num) / int(den), 2)
    dur = float(p["format"]["duration"])
    issues = []
    if (v["width"], v["height"]) != (STANDARD["width"], STANDARD["height"]):
        issues.append(f"resolution {v['width']}x{v['height']} (expected 1080x1920)")
    if abs(fps - STANDARD["fps"]) > 0.1:
        issues.append(f"fps {fps}")
    if not a:
        issues.append("no audio stream")
    if dur > STANDARD["max_seconds"]:
        issues.append(f"duration {dur:.1f}s exceeds {STANDARD['max_seconds']}s Shorts limit")
    return {"name": "format", "ok": not issues, "issues": issues, "data": {"video": v["codec_name"], "audio": a and a["codec_name"], "fps": fps, "seconds": round(dur, 2)}}


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
    return {"name": "loudness", "ok": not issues, "issues": issues, "data": {"lufs": integ, "true_peak_dbfs": peak, "lra": lra}}


def check_black_and_freeze(video):
    err = ff(["-i", str(video), "-vf", "blackdetect=d=0.3:pix_th=0.04,freezedetect=n=0.0008:d=2.5", "-an", "-f", "null", "-"])
    blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)
    freezes = re.findall(r"freeze_start: ([\d.]+)", err)
    issues = [f"black frames {float(s):.2f}-{float(e):.2f}s" for s, e in blacks]
    issues += [f"frozen picture from {float(s):.2f}s (>=2.5s with no change)" for s in freezes]
    return {"name": "black_freeze", "ok": not issues, "issues": issues, "data": {"black": len(blacks), "freeze": len(freezes)}}


def check_silence(video, max_gap=1.6):
    err = ff(["-i", str(video), "-af", f"silencedetect=noise=-42dB:d={max_gap}", "-vn", "-f", "null", "-"])
    gaps = re.findall(r"silence_start: ([\d.]+)", err)
    issues = [f"near-silence >= {max_gap}s at {float(s):.2f}s" for s in gaps if float(s) > 0.5]
    return {"name": "silence", "ok": not issues, "issues": issues, "data": {"gaps": len(gaps)}}


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


def check_narration(work_dir, script, language, threshold=0.15):
    sys.path.insert(0, str(ROOT))
    import numpy as np
    import studio
    from faster_whisper import WhisperModel

    model = WhisperModel("small" if language == "en" else "large-v3-turbo", device="cpu", compute_type="int8")
    scenes, issues = [], []
    for i, sc in enumerate(script["scenes"]):
        wav = Path(work_dir) / "audio" / f"{i:02d}.wav"
        a = studio.read_wav(wav)
        a16 = np.interp(np.arange(0, len(a), studio.SR / 16000), np.arange(len(a)), a).astype(np.float32)
        segs, _ = model.transcribe(a16, language=language, beam_size=5)
        heard = " ".join(s.text.strip() for s in segs)
        cer, ratio = char_error(sc["narration"], heard, language)
        scenes.append({"scene": i + 1, "cer": cer, "length_ratio": ratio, "heard": heard})
        if cer > threshold or not 0.85 <= ratio <= 1.2:
            hint = "Whisper wrote digits where the script has number words; likely a false positive" if re.search(r"\d", heard) and not re.search(r"\d", sc["narration"]) else "listen and regenerate if mispronounced"
            issues.append(f"scene {i + 1}: CER {cer} length ratio {ratio} — {hint}")
    return {"name": "narration_asr", "ok": not issues, "issues": issues, "data": {"scenes": scenes, "note": "digits vs number-words and Whisper spelling quirks inflate CER; review flagged scenes by ear"}}


def check_captions(work_dir, script, style_name="chalk"):
    sys.path.insert(0, str(ROOT))
    import studio
    from PIL import Image, ImageDraw
    from styles import STYLES

    st = {**STYLES[style_name], **script.get("style_overrides", {})}
    cap = studio.Captioner(st)
    dr = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    wts = studio.scene_word_times(script, Path(work_dir))
    issues, groups = [], 0
    for i, sc in enumerate(script["scenes"]):
        toks = studio.caption_tokens(sc["narration"])
        if not wts[i] or len(wts[i]) != len(toks):
            issues.append(f"scene {i + 1}: word timing not aligned (captions fall back to estimated timing)")
        prev_end = "."
        for g in studio.caption_groups(sc["narration"], 0, 5, st.get("caption_words", 3), wts[i], st.get("caption_max_chars")):
            groups += 1
            phrase_start = prev_end[-1] in ".,?!:;।॥—"
            prev_end = g["words"][-1]
            w = sum(dr.textlength(x, font=cap.font) for x in g["words"]) + 22 * (len(g["words"]) - 1)
            if w > studio.W - 120:
                issues.append(f"scene {i + 1}: caption '{' '.join(g['words'])}' too wide ({int(w)}px)")
            if len(g["words"]) > 1 and g["words"][0] in studio.POSTPOSITIONS and not phrase_start:
                issues.append(f"scene {i + 1}: caption line starts with postposition '{g['words'][0]}'")
    return {"name": "captions", "ok": not issues, "issues": issues, "data": {"groups": groups}}


def check_speaker(work_dir, script, language, voice=None, win=2.5, min_window_sim=0.5, min_scene_sim=0.7):
    sys.path.insert(0, str(ROOT))
    import numpy as np
    import studio
    from . import speaker as spk

    ref = None
    if voice:
        rp = spk.reference_path(language, voice.split(":", 1)[-1])
        ref = np.load(rp) if rp.exists() else None
    issues, wsims, scene_sims, f0s = [], [], [], []
    for i in range(len(script["scenes"])):
        a = studio.read_wav(Path(work_dir) / "audio" / f"{i:02d}.wav")
        whole = spk.embed(a)
        if ref is None:
            ref = whole
        ss = float(whole @ ref)
        scene_sims.append(ss)
        if ss < min_scene_sim:
            issues.append(f"scene {i + 1}: whole-scene speaker similarity {ss:.2f} < {min_scene_sim}")
        n, step = int(win * spk.SR), int(win * spk.SR / 2)
        for s0 in range(0, max(1, len(a) - n + 1), step):
            seg = a[s0:s0 + n]
            if len(seg) < n or np.sqrt(np.mean(seg ** 2)) < 0.02:
                continue
            ws = float(spk.embed(seg) @ ref)
            f0 = spk.f0_median(seg)
            wsims.append(ws)
            if f0:
                f0s.append((i, s0, f0))
            if ws < min_window_sim:
                issues.append(f"scene {i + 1} @{s0 / spk.SR:.1f}s: {win}s-window speaker similarity {ws:.2f} < {min_window_sim} (possible different voice)")
    med = float(np.median([f for _, _, f in f0s])) if f0s else None
    for i, s0, f in f0s:
        if med and abs(12 * np.log2(f / med)) > 7:
            issues.append(f"scene {i + 1} @{s0 / spk.SR:.1f}s: pitch {round(f)} Hz is >7 semitones from median {round(med)} Hz (possible different voice)")
    return {"name": "speaker_consistency", "ok": not issues, "issues": issues,
            "data": {"windows": len(wsims), "window_median": round(float(np.median(wsims)), 3) if wsims else None, "window_min": round(min(wsims), 3) if wsims else None,
                     "scene_min": round(min(scene_sims), 3) if scene_sims else None, "median_f0": med and round(med),
                     "calibration": "2026-11-16: 2.5s windows — consistent voice min 0.61 / known-mixed median 0.46 (50% < 0.5); 1s clips are unreliable (same voice down to 0.57)"}}


def contact_sheet(video, out_png, n=12):
    p = probe(video)
    dur = float(p["format"]["duration"])
    times = [dur * (k + 0.5) / n for k in range(n)]
    sel = "+".join(f"eq(n\\,{int(t * 30)})" for t in times)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", f"select='{sel}',scale=270:480,tile=6x{(n + 5) // 6}", "-frames:v", "1", str(out_png)], check=True)
    return str(out_png)


def run(video, work_dir=None, script_path=None, language="en", variant_id=None, style="chalk"):
    checks = [check_format(video), check_loudness(video), check_black_and_freeze(video), check_silence(video)]
    if work_dir and script_path:
        script = json.loads(Path(script_path).read_text())
        checks += [check_narration(work_dir, script, language), check_captions(work_dir, script, style)]
        voices = json.loads((ROOT / "profiles" / "voices.json").read_text())
        used = Path(work_dir) / "audio" / "voice.txt"
        voice = used.read_text().strip() if used.exists() else voices.get(language, {}).get("voice")
        th = voices.get("_speaker_thresholds", {}).get(voice or "", {})
        checks.append(check_speaker(work_dir, script, language, voice, min_window_sim=th.get("window", 0.5), min_scene_sim=th.get("scene", 0.7)))
    sheet = contact_sheet(video, Path(video).with_suffix(".qa.png"))
    failed = [c for c in checks if not c["ok"] and c["name"] in ("format", "loudness", "black_freeze", "speaker_consistency")]
    warned = [c for c in checks if not c["ok"] and c not in failed]
    verdict = "fail" if failed else ("warn" if warned else "pass")
    report = {"video": str(video), "verdict": verdict, "checks": checks, "contact_sheet": sheet,
              "manual_review_required": ["character consistency", "visual defects / wrong illustrations", "storytelling quality", "native-speaker listen for non-English"],
              "created_at": db.now()}
    if variant_id:
        with db.connect() as con:
            con.execute("INSERT INTO qa_reports (variant_id, kind, verdict, report, created_at) VALUES (?,?,?,?,?)", (variant_id, "automated", verdict, json.dumps(report, ensure_ascii=False), db.now()))
    return report


def markdown(report):
    lines = [f"# QA report: {Path(report['video']).name}", "", f"**Verdict: {report['verdict'].upper()}** · {report['created_at']}", ""]
    for c in report["checks"]:
        lines.append(f"- {'✅' if c['ok'] else '⚠️'} **{c['name']}** {json.dumps({k: v for k, v in c['data'].items() if k != 'scenes'}, ensure_ascii=False)}")
        lines += [f"    - {i}" for i in c["issues"]]
    lines += ["", f"Contact sheet: `{report['contact_sheet']}`", "", "Manual review still required: " + ", ".join(report["manual_review_required"])]
    return "\n".join(lines) + "\n"
