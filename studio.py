import argparse
import difflib
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from styles import FONT_DIR, MAC_TO_OFL, OFL, STYLES

ROOT = Path(__file__).parent
FPS, SR = 30, 24000
from frame import H, W
OLLAMA = "http://localhost:11434"
BIBLE = ROOT / "profiles" / "characters" / "ramayana.json"
CAPTION_MAX_W = W - 60
LOUDNESS_TARGET = {"I": -14.0, "TP": -1.5, "LRA": 11.0}
V2_DEFAULTS = {
    "caption_autosplit": True,
    "loudnorm": "two-pass",
    "narration_lufs": -16.0,
    "ducking": "v2",
    "duck_under_db": -20.0,
    "duck_gap_lift_db": 6.0,
    "autocrop": True,
}
SHOT_HINTS = {
    "EWS": "extreme wide shot, tiny figures in a vast landscape",
    "WS": "wide shot, full figures with their surroundings",
    "MS": "medium shot, figures from the waist up",
    "CU": "close-up shot",
    "ECU": "extreme close-up detail shot",
    "insert": "close-up insert of a single object",
    "silhouette": "strong dark silhouette composition",
    "map": "illustrated top-down map view",
    "text": "",
}
ANGLE_HINTS = {"eye": "", "low": "low angle view looking up", "high": "high angle view looking down", "ots": "over-the-shoulder view", "pov": "first-person point of view", "dutch": ""}
NEGATION = re.compile(r"^\s*(no|not|never|without|absolutely no|avoid)\b", re.I)


def engine_version(script):
    try:
        return int(script.get("engine_version", 1) or 1)
    except (TypeError, ValueError):
        return 1


def effective_style(style_name, script):
    import frame

    st = {**STYLES[style_name], **script.get("style_overrides", {})}
    if frame.LONG:
        st["size"] = frame.IMAGE_SIZE
        st["prefix"] = st.get("prefix", "") + frame.PROMPT_SUFFIX
        st["caption_y"] = 0.88
    if engine_version(script) < 2:
        return st
    if script.get("fonts", "mac") == "ofl":
        for key, idx in (("font", None), ("caption_font", "caption_font_index")):
            path = st.get(key)
            if path in MAC_TO_OFL and Path(MAC_TO_OFL[path]).exists():
                st[key] = MAC_TO_OFL[path]
                if idx:
                    st[idx] = 0
    for k, v in V2_DEFAULTS.items():
        st.setdefault(k, v)
    return st


def short_hash(*parts):
    return hashlib.sha256("|".join(str(x) for x in parts).encode()).hexdigest()[:20]


def cache_valid(asset, sidecar, key):
    if not asset.exists():
        return False
    if not sidecar.exists():
        sidecar.write_text(key)
        return True
    return sidecar.read_text().strip() == key


def load_bible(path=None):
    p = Path(path) if path else BIBLE
    return json.loads(p.read_text()) if p.exists() else {}


def expand_tokens(text, bible, ev=1):
    chars = bible.get("characters", {})

    def sub(m):
        key = m.group(1)
        if key not in chars:
            raise KeyError(f"unknown character token {{{key}}} (known: {', '.join(sorted(chars))})")
        c = chars[key]
        return c.get("prompt_positive", c["prompt"]) if ev >= 2 else c["prompt"]

    return re.sub(r"\{([a-z][a-z0-9_]*)\}", sub, text or "")


def positive_only(text):
    keep = [p for p in text.split(",") if not (NEGATION.match(p) and ":" not in p)]
    return ",".join(keep).strip().strip(",").strip()


def scene_still(script, i, _depth=0):
    ref = script["scenes"][i].get("image")
    if ref is None or ref == "" or _depth > 8:
        return i
    if isinstance(ref, bool):
        return i
    if isinstance(ref, int):
        j = ref
    else:
        m = re.match(r"^\s*(\d+)", str(ref))
        if not m:
            raise ValueError(f"scene {i + 1}: image '{ref}' must be a scene index like 3 or '03'")
        j = int(m.group(1))
    if not 0 <= j < len(script["scenes"]):
        raise ValueError(f"scene {i + 1}: image {ref} is out of range")
    return i if j == i else scene_still(script, j, _depth + 1)


def raw_path(script, out, i):
    return out / "img" / f"{scene_still(script, i):02d}_raw.png"


def scene_prompt(script, sc, st, bible=None):
    ev = engine_version(script)
    bible = load_bible() if bible is None else bible
    visual = expand_tokens(sc["visual"], bible, ev)
    hints = [SHOT_HINTS.get(sc.get("shot"), ""), ANGLE_HINTS.get(sc.get("angle"), "")]
    body = ", ".join([h for h in hints if h] + [visual])
    if ev >= 2:
        body = positive_only(body)
    character = expand_tokens(script.get("character") or "", bible, ev)
    if character:
        body += f". Recurring character: {character}"
    prefix = st["prefix"] if ev >= 2 else st.get("prefix_v1", st["prefix"])
    negative = st.get("negative", "") if ev >= 2 else st.get("negative_v1", st.get("negative", ""))
    return f"{prefix} {body}", body, negative


def border_lines(a, thr, max_frac=0.12):
    h, w = a.shape
    rows, cols = a.mean(axis=1), a.mean(axis=0)
    mh, mw = max(1, int(h * max_frac)), max(1, int(w * max_frac))

    def inset(lines):
        idx = np.nonzero(lines > thr)[0]
        return int(idx.max()) + 1 if len(idx) else 0

    return inset(rows[:mh]), inset(rows[::-1][:mh]), inset(cols[:mw]), inset(cols[::-1][:mw])


def border_detect(img, delta=0.25, band=0.03):
    a = np.asarray(img.convert("L"), np.float32) / 255
    h, w = a.shape
    inner = float(a[int(h * 0.15):int(h * 0.85), int(w * 0.15):int(w * 0.85)].mean())
    thr = inner + delta
    bh, bw = max(1, int(h * band)), max(1, int(w * band))
    bands = {"top": a[:bh].mean(), "bottom": a[-bh:].mean(), "left": a[:, :bw].mean(), "right": a[:, -bw:].mean()}
    lines = border_lines(a, thr)
    bordered = any(v > thr for v in bands.values()) or any(lines)
    return {"bordered": bool(bordered), "inner": inner, "bands": {k: round(float(v), 3) for k, v in bands.items()}, "insets": lines}


def autocrop_border(img, delta=0.25, pad=3):
    info = border_detect(img, delta)
    if not info["bordered"]:
        return img, None, "clean"
    w, h = img.size
    t, b, l, r = info["insets"]
    t, b, l, r = [v + pad if v else 0 for v in (t, b, l, r)]
    if not any((t, b, l, r)):
        bh, bw = int(h * 0.03), int(w * 0.03)
        t, b, l, r = [x if info["bands"][k] > info["inner"] + delta else 0 for k, x in (("top", bh), ("bottom", bh), ("left", bw), ("right", bw))]
    x0, y0, x1, y1 = l, t, w - r, h - b
    cw, ch = x1 - x0, y1 - y0
    if cw / ch > w / h:
        nw = ch * w / h
        x0, x1 = x0 + (cw - nw) / 2, x0 + (cw + nw) / 2
    else:
        nh = cw * h / w
        y0, y1 = y0 + (ch - nh) / 2, y0 + (ch + nh) / 2
    box = tuple(int(round(v)) for v in (x0, y0, x1, y1))
    out = img.crop(box).resize((w, h), Image.LANCZOS)
    status = "rejected" if border_detect(out, delta)["bordered"] else "cropped"
    return out, box, status


def ensure_raqm():
    from PIL import features

    lib = "/opt/homebrew/lib"
    if not features.check("raqm") and Path(lib, "libraqm.dylib").exists() and os.environ.get("DYLD_FALLBACK_LIBRARY_PATH") != lib:
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = lib
        os.execv(sys.executable, [sys.executable] + sys.argv)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


SCRIPT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "character": {"type": "string"},
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "narration": {"type": "string"},
                    "visual": {"type": "string"},
                    "emphasis": {"type": "string"},
                },
                "required": ["narration", "visual", "emphasis"],
            },
        },
        "description": {"type": "string"},
        "hashtags": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["title", "character", "scenes", "description", "hashtags"],
}

SCRIPT_PROMPT = """You write viral, factually accurate short-form explainer videos (YouTube Shorts, Reels, TikTok).

Topic: {topic}

Source material (base every factual claim ONLY on this; if a claim is not supported here, leave it out):
<<<
{notes}
>>>

Target length: {seconds} seconds of narration (about {words} words total).
Visual style: {style}

Rules:
- Scene 1 is the HOOK: a surprising fact, question or bold claim in under 12 words. No greetings, no "in this video".
- {n} scenes total. Each scene's narration is 1-2 short punchy sentences (8-22 words), spoken conversationally.
- Build curiosity: each scene should make the viewer want the next one. Use concrete numbers and vivid comparisons.
- The last scene delivers the payoff and ends with a short loop-back line or a question that invites comments.
- Only state facts supported by the source material. Copy numbers exactly; do not extrapolate or invent comparisons with numbers.
- "character": one sentence describing a recurring mascot or guide character (species/look/clothing/colors) that can appear in scenes for visual consistency.
- "visual": a concrete image-generation prompt for that scene (subject, action, setting, camera angle). Mention the character by its description when it appears. Never ask for text, letters or numbers in the image.
- "emphasis": 1-3 word on-screen keyword for the scene, ALL CAPS.
- "description": 1-2 sentence post caption. "hashtags": 5 relevant hashtags without the # symbol.
Return JSON only."""


WIKI_HEADERS = {"User-Agent": "shorts-studio/0.1 (local research script)"}


def wiki(params):
    for attempt in range(4):
        try:
            r = requests.get("https://en.wikipedia.org/w/api.php", params={**params, "format": "json"}, headers=WIKI_HEADERS, timeout=30)
            r.raise_for_status()
            return r.json()["query"]
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))


def research(topic, model, out, extra_notes=None):
    path = out / "notes.txt"
    if path.exists():
        return path.read_text()
    parts = []
    if extra_notes:
        parts.append(Path(extra_notes).read_text())
    try:
        q = ollama_json(
            model,
            f"Give the exact titles of the 2 English Wikipedia articles that best explain this topic in depth: {topic}\nPrefer the specific scientific/historical article over broad ones.",
            {"type": "object", "properties": {"titles": {"type": "array", "items": {"type": "string"}}}, "required": ["titles"]},
            0.1,
        )["titles"][:2]
        hits, seen = [], set()
        for term in q + [topic]:
            res = wiki({"action": "query", "list": "search", "srsearch": term, "srlimit": 1})["search"]
            if res and res[0]["title"] not in seen:
                seen.add(res[0]["title"])
                hits.append(res[0])
        for h in hits[:2]:
            page = wiki({"action": "query", "prop": "extracts", "explaintext": 1, "titles": h["title"], "redirects": 1})["pages"]
            text = next(iter(page.values())).get("extract", "")
            text = re.split(r"\n== (See also|References|Notes|External links|Further reading) ==", text)[0]
            parts.append(f"# {h['title']} (Wikipedia)\n{text[:7000]}")
            log(f"research: pulled Wikipedia '{h['title']}'")
    except Exception as e:
        log(f"research: Wikipedia lookup failed ({e})")
    notes = "\n\n".join(parts) or "(no source material; keep claims general and well known)"
    path.write_text(notes)
    return notes


def ollama_json(model, prompt, schema, temperature, think=False):
    r = requests.post(
        f"{OLLAMA}/api/chat",
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "format": schema,
            "stream": False,
            "think": think,
            "options": {"temperature": temperature, "num_ctx": 16384, "num_predict": 6000},
        },
        timeout=1800,
    )
    r.raise_for_status()
    return json.loads(r.json()["message"]["content"])


FACTCHECK_PROMPT = """You are a strict fact-checker for a short educational video.

Source material:
<<<
{notes}
>>>

Draft script (JSON):
{draft}

For every scene, check each factual claim in "narration" against the source material and basic physics/common knowledge.
- If a claim is wrong, exaggerated or unsupported, rewrite that narration so it is correct (keep it short, punchy and spoken-style, 8-22 words).
- Remove any request for text, labels, letters or numbers from "visual".
- Remove scenes that repeat an earlier fact; replace them with a different supported fact.
- Keep everything else (structure, hook, ending question, character) the same.
Return the corrected script as JSON with the same fields."""


def step_script(topic, style, seconds, model, out, notes_file=None):
    path = out / "script.json"
    if path.exists():
        return json.loads(path.read_text())
    notes = research(topic, model, out, notes_file)
    n = max(5, min(12, round(seconds / 6)))
    prompt = SCRIPT_PROMPT.format(topic=topic, notes=notes, seconds=seconds, words=int(seconds * 2.6), style=style, n=n)
    log(f"script: asking {model} for {n} scenes")
    draft = ollama_json(model, prompt, SCRIPT_SCHEMA, 0.7, think=True)
    (out / "script_draft.json").write_text(json.dumps(draft, indent=2))
    log("script: fact-check pass (thinking on)")
    data = ollama_json(model, FACTCHECK_PROMPT.format(notes=notes, draft=json.dumps(draft, indent=2)), SCRIPT_SCHEMA, 0.2, think=True)
    data["topic"] = topic
    data["style"] = style
    path.write_text(json.dumps(data, indent=2))
    log(f"script: wrote {path} ({len(data['scenes'])} scenes). Edit it and re-run to change anything.")
    return data


def write_wav(path, audio, sr=SR):
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def read_wav(path):
    with wave.open(str(path), "rb") as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32767
    if ch > 1:
        data = data.reshape(-1, ch).mean(axis=1)
    if sr != SR:
        x = np.linspace(0, len(data) - 1, int(len(data) * SR / sr))
        data = np.interp(x, np.arange(len(data)), data)
    return data


def say_fallback(text, path):
    aiff = path.with_suffix(".aiff")
    subprocess.run(["say", "-o", str(aiff), text], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(aiff), "-ar", str(SR), "-ac", "1", str(path)], check=True)
    aiff.unlink()


def audio_key(sc, voice):
    parts = [sc["narration"], sc.get("tts", ""), voice]
    parts += [f"{k}={sc[k]}" for k in ("speed", "voice_seed") if k in sc]
    return short_hash(*parts)


def step_voice(script, voice, speed, out):
    d = out / "audio"
    d.mkdir(exist_ok=True)
    todo = []
    for i, sc in enumerate(script["scenes"]):
        wav, side = d / f"{i:02d}.wav", d / f"{i:02d}.hash"
        if cache_valid(wav, side, audio_key(sc, voice)):
            continue
        if wav.exists():
            log(f"voice: scene {i + 1} narration/tts/voice changed; regenerating")
            wav.replace(d / f"{i:02d}.prev.wav")
            (d / f"{i:02d}.words.json").unlink(missing_ok=True)
            (d / f"{i:02d}.heard.json").unlink(missing_ok=True)
        todo.append(i)
    if not todo:
        return
    (d / "voice.txt").write_text(voice)
    try:
        voice_generate(script, voice, speed, d, todo)
    finally:
        for i in todo:
            if (d / f"{i:02d}.wav").exists():
                (d / f"{i:02d}.hash").write_text(audio_key(script["scenes"][i], voice))


def voice_generate(script, voice, speed, d, todo):
    if voice.startswith(("maya2:", "svara:")):
        from pipeline import voicepack

        for i in todo:
            sc = script["scenes"][i]
            log(f"voice: scene {i + 1}/{len(script['scenes'])} ({voice})")
            write_wav(d / f"{i:02d}.wav", voicepack.speak(voice, sc.get("tts", sc["narration"]), script.get("language", "hi")))
        return
    if voice.startswith("veena:"):
        from veena import Veena

        engine = Veena()
        vpp = json.loads((ROOT / "profiles" / "voices.json").read_text()).get(script.get("language", "hi"), {}).get("voice_prompt")
        if vpp:
            engine.set_voice_prompt(ROOT / vpp["wav"], vpp["text"], voice.split(":", 1)[1])
        for i in todo:
            sc = script["scenes"][i]
            log(f"voice: scene {i + 1}/{len(script['scenes'])} (Veena)")
            spk_name = voice.split(":", 1)[1]
            from pipeline import speaker as spk

            refp = spk.reference_path(script.get("language", "hi"), spk_name)
            ref = np.load(refp) if refp.exists() else None
            write_wav(d / f"{i:02d}.wav", engine.speak(sc.get("tts", sc["narration"]), spk_name, seed=sc.get("voice_seed", i), ref=ref))
        return
    model = None
    try:
        from mlx_audio.tts.utils import load_model

        model = load_model("mlx-community/Kokoro-82M-bf16")
    except Exception as e:
        log(f"voice: Kokoro unavailable ({e}); using macOS 'say'")
    for i in todo:
        text = script["scenes"][i].get("tts", script["scenes"][i]["narration"])
        path = d / f"{i:02d}.wav"
        log(f"voice: scene {i + 1}/{len(script['scenes'])}")
        if model is None:
            say_fallback(text, path)
            continue
        sp = script["scenes"][i].get("speed", speed)
        chunks = [np.array(r.audio).reshape(-1) for r in model.generate(text=text, voice=voice, speed=sp, lang_code=voice[0])]
        write_wav(path, np.concatenate(chunks))


def pixelate(img, factor, colors):
    small = img.resize((img.width // factor, img.height // factor), Image.BOX)
    if colors:
        small = small.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    return small


def placeholder(text, path):
    img = Image.new("RGB", (576, 1024))
    dr = ImageDraw.Draw(img)
    for y in range(1024):
        dr.line([(0, y), (576, y)], fill=(30 + y // 12, 40, 90 + y // 10))
    font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 28)
    dr.multiline_text((30, 400), "\n".join(wrap(text, font, 516, dr)), font=font, fill="white")
    img.save(path)


def image_model_id(st, steps, model_args):
    width, height = st.get("size", (576, 1024))
    return f"z-image-turbo|{' '.join(model_args)}|{steps}|{width}x{height}"


def generate_still(prompt, negative, seed, raw, st, steps, model_args):
    width, height = st.get("size", (576, 1024))
    cmd = [
        shutil.which("mflux-generate-z-image-turbo") or str(Path(sys.executable).parent / "mflux-generate-z-image-turbo"), *model_args, "--steps", str(steps),
        "--width", str(width), "--height", str(height), "--seed", str(seed),
        "--prompt", prompt,
    ]
    if negative:
        cmd += ["--negative-prompt", negative]
    Path(raw).unlink(missing_ok=True)
    subprocess.run(cmd + ["--output", str(raw)], check=True, stdout=subprocess.DEVNULL)


def step_images(script, style, seed, steps, out):
    d = out / "img"
    d.mkdir(exist_ok=True)
    st = effective_style(style, script)
    ev = engine_version(script)
    bible = load_bible()
    have_mflux = shutil.which("mflux-generate-z-image-turbo") is not None or (Path(sys.executable).parent / "mflux-generate-z-image-turbo").exists()
    if not have_mflux and os.environ.get("STUDIO_ALLOW_PLACEHOLDER") != "1":
        raise SystemExit("images: the image model (mflux-generate-z-image-turbo) was not found; refusing to write placeholder pictures. Activate .venv or set STUDIO_ALLOW_PLACEHOLDER=1 for a test run.")
    local = ROOT / "models" / "z-image-turbo-4bit"
    model_args = ["--model", str(local)] if local.exists() else ["--quantize", "4"]
    flags = {}
    for i, sc in enumerate(script["scenes"]):
        if scene_still(script, i) != i:
            continue
        raw = d / f"{i:02d}_raw.png"
        side = d / f"{i:02d}_raw.hash"
        if sc.get("kind") in ("verse", "shloka"):
            import chalk

            fields = {k: sc.get(k) for k in ("kind", "devanagari", "source", "from", "to", "from_label", "to_label")}
            key = short_hash(json.dumps(fields, ensure_ascii=False, sort_keys=True), chalk.FONTSET["name"])
            if cache_valid(raw, side, key):
                continue
            if raw.exists():
                raw.replace(d / f"{i:02d}_raw.prev.png")
            chalk.text_scene(sc, raw, seed + i)
            side.write_text(key)
            continue
        prompt, body, negative = scene_prompt(script, sc, st, bible)
        sseed = sc.get("seed", seed + i)
        key = short_hash(body, negative, sseed, image_model_id(st, steps, model_args))
        if cache_valid(raw, side, key):
            continue
        if raw.exists():
            log(f"images: scene {i + 1} prompt/seed/model changed; regenerating")
            raw.replace(d / f"{i:02d}_raw.prev.png")
        log(f"images: scene {i + 1}/{len(script['scenes'])}")
        if not have_mflux:
            placeholder(sc["visual"], raw)
            side.write_text(key)
            continue
        generate_still(prompt, negative, sseed, raw, st, steps, model_args)
        if st.get("autocrop"):
            img, box, status = autocrop_border(Image.open(raw).convert("RGB"))
            if status == "rejected":
                log(f"images: scene {i + 1} still bordered after crop; retrying with seed {sseed + 977}")
                generate_still(prompt, negative, sseed + 977, raw, st, steps, model_args)
                img, box, status = autocrop_border(Image.open(raw).convert("RGB"))
            if box:
                Image.open(raw).save(d / f"{i:02d}_uncropped.png")
                img.save(raw)
                flags[f"{i:02d}"] = {"status": status, "box": box}
                log(f"images: scene {i + 1} border {status}, crop {box}")
        side.write_text(key)
    if flags:
        prev = json.loads((d / "borders.json").read_text()) if (d / "borders.json").exists() else {}
        (d / "borders.json").write_text(json.dumps({**prev, **flags}, indent=2))


def load_scene_image(path, st):
    img = Image.open(path).convert("RGB")
    if st["pixelate"]:
        small = pixelate(img, st["pixelate"] // 2 or 1, st["colors"])
        scale = math.ceil(H * 1.08 / small.height)
        return small.resize((small.width * scale, small.height * scale), Image.NEAREST)
    return img.resize((int(W * 1.15), int(H * 1.15)), Image.LANCZOS)


def wrap(text, font, maxw, dr):
    lines, cur = [], ""
    for word in text.split():
        t = f"{cur} {word}".strip()
        if dr.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def caption_tokens(text):
    out = []
    for tok in text.split():
        if out and not re.search(r"\w", tok):
            out[-1] += " " + tok
        else:
            out.append(tok)
    return out


POSTPOSITIONS = {"से", "में", "का", "की", "के", "को", "ने", "पर", "तक"}


def split_wide(groups, measure, maxw):
    out = []
    for g in groups:
        if len(g) < 2 or measure(g) <= maxw:
            out.append(g)
            continue
        best = None
        for k in range(1, len(g)):
            if g[k] in POSTPOSITIONS and k + 1 < len(g):
                continue
            score = max(measure(g[:k]), measure(g[k:]))
            if best is None or score < best[0]:
                best = (score, k)
        k = best[1] if best else len(g) // 2
        out += split_wide([g[:k], g[k:]], measure, maxw)
    return out


def caption_groups(text, start, dur, size=3, word_times=None, max_chars=None, measure=None, maxw=None):
    words = caption_tokens(text)
    phrases, cur = [], []
    for w in words:
        cur.append(w)
        if w[-1] in ".,?!:;।॥—":
            phrases.append(cur)
            cur = []
    if cur:
        phrases.append(cur)
    groups = []
    for ph in phrases:
        n = math.ceil(len(ph) / size)
        if max_chars:
            n = max(n, math.ceil(len(" ".join(ph)) / max_chars))
        n = min(n, len(ph))
        while True:
            base, extra = divmod(len(ph), n)
            k, chunk = 0, []
            for j in range(n):
                m = base + (1 if j < extra else 0)
                chunk.append(ph[k:k + m])
                k += m
            if not max_chars or n >= len(ph) or all(len(c) == 1 or len(" ".join(c)) <= max_chars for c in chunk):
                break
            n += 1
        for j in range(1, len(chunk)):
            if len(chunk[j]) > 1 and chunk[j][0] in POSTPOSITIONS:
                chunk[j - 1].append(chunk[j].pop(0))
        groups += chunk
    if measure and maxw:
        groups = split_wide(groups, measure, maxw)
    if word_times and len(word_times) == len(words):
        res, k = [], 0
        for g in groups:
            wt = [(start + a, start + b) for a, b in word_times[k:k + len(g)]]
            res.append({"words": g, "start": wt[0][0], "end": wt[-1][1], "word_times": wt})
            k += len(g)
        for a, b in zip(res, res[1:]):
            a["end"] = max(a["end"], b["start"] - 0.02)
            a["word_times"][-1] = (a["word_times"][-1][0], a["end"])
        res[0]["start"] = min(res[0]["start"], start)
        return res
    weights = [sum(len(w) + 2 for w in g) for g in groups]
    total = sum(weights)
    t, res = start, []
    for g, wgt in zip(groups, weights):
        gd = dur * wgt / total
        wt = t
        word_times = []
        for w in g:
            wd = gd * (len(w) + 2) / wgt
            word_times.append((wt, wt + wd))
            wt += wd
        res.append({"words": g, "start": t, "end": t + gd, "word_times": word_times})
        t += gd
    return res


def norm_word(w):
    return re.sub(r"[\W_]", "", w.lower())


def scene_caption_groups(script, st, cap, i, start, dur, word_times=None):
    size = st.get("caption_words", 3)
    hook = engine_version(script) >= 2 and i == 0
    if hook:
        size = min(size, st.get("hook_caption_words", 3))
    auto = st.get("caption_autosplit")
    gs = caption_groups(script["scenes"][i]["narration"], start, dur, size, word_times, st.get("caption_max_chars"), cap.width if auto else None, CAPTION_MAX_W if auto else None)
    if hook and gs:
        gs[0]["start"] = 0.0
    return gs


class Captioner:
    def __init__(self, st, keywords=()):
        cf, ci = st.get("caption_font", st["font"]), st.get("caption_font_index", 0)
        size = st.get("caption_size", 92)
        self.font = ImageFont.truetype(cf, size, index=ci)
        self.small = ImageFont.truetype(cf, int(size * 0.7), index=ci)
        self.color = st["caption_color"]
        self.idle = st.get("caption_idle", (255, 255, 255))
        self.key = st.get("caption_key", self.color)
        self.y = st.get("caption_y", 0.68)
        self.upper = st.get("caption_upper", True)
        self.keywords = {norm_word(k) for k in keywords} - {""}
        self._probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))

    def width(self, words, font=None):
        words = [w.upper() if self.upper else w for w in words]
        f = font or self.font
        return sum(self._probe.textlength(w, font=f) for w in words) + 22 * (len(words) - 1)

    def draw(self, frame, group, t, emphasis, scene_t):
        dr = ImageDraw.Draw(frame)
        if group:
            words = [w.upper() if self.upper else w for w in group["words"]]
            spacing = 22
            widths = [dr.textlength(w, font=self.font) for w in words]
            total = sum(widths) + spacing * (len(words) - 1)
            age = t - group["start"]
            pop = 1.0 if age > 0.08 else 0.85 + age * 1.9
            y = int(H * self.y)
            if total > W - 120:
                font = self.small
                widths = [dr.textlength(w, font=font) for w in words]
                total = sum(widths) + spacing * (len(words) - 1)
            else:
                font = self.font
            x = (W - total) / 2
            for w, wd, (ws, we) in zip(words, widths, group["word_times"]):
                current = ws <= t < we + 0.05
                if norm_word(w) in self.keywords:
                    fill = self.key
                elif current:
                    fill = self.color
                else:
                    fill = self.idle
                yy = y + int((1 - pop) * 40)
                dr.text((x, yy), w, font=font, fill=fill, stroke_width=10, stroke_fill=(0, 0, 0))
                x += wd + spacing
        if emphasis and scene_t < 1.6:
            a = min(1.0, scene_t / 0.15)
            f = ImageFont.truetype(self.font.path, int(110 * (0.9 + 0.1 * a)))
            tw = dr.textlength(emphasis, font=f)
            if tw > W - 80:
                f = ImageFont.truetype(self.font.path, int(110 * (W - 80) / tw))
                tw = dr.textlength(emphasis, font=f)
            dr.text(((W - tw) / 2, int(H * 0.14)), emphasis, font=f, fill=self.color, stroke_width=12, stroke_fill=(0, 0, 0))


def scene_frame(img, st, p, dur, seed):
    rng = np.random.default_rng(seed)
    if st["motion"] == "pan":
        dx = img.width - W
        dy = img.height - H
        direction = 1 if seed % 2 else -1
        ox = int(dx * (0.5 + direction * (p - 0.5) * 0.9))
        oy = int(dy * (0.8 - 0.6 * p))
        return img.crop((ox, oy, ox + W, oy + H))
    zoom_in = rng.random() > 0.4
    z = 1.0 + 0.12 * (p if zoom_in else 1 - p)
    e = 0.5 - 0.5 * math.cos(math.pi * p)
    cw = W * 1.15 / z
    ch = H * 1.15 / z
    cx = img.width / 2 + (rng.random() - 0.5) * (img.width - cw) * (e - 0.5)
    cy = img.height / 2 + (rng.random() - 0.5) * (img.height - ch) * (e - 0.5)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    frame = img.resize((W, H), Image.BILINEAR, box=box)
    if st["motion"] == "reveal":
        reveal = min(1.0, p / 0.55)
        if reveal < 1:
            mask = Image.new("L", (W, H), 0)
            md = ImageDraw.Draw(mask)
            md.rectangle([0, 0, int(W * reveal), H], fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(40))
            frame = Image.composite(frame, Image.new("RGB", (W, H), "white"), mask)
    return frame


def chiptune(dur, seed):
    rng = np.random.default_rng(seed)
    bpm = 132
    beat = 60 / bpm
    n = int(dur * SR)
    t = np.arange(n) / SR
    roots = [57, 53, 48, 55]
    scale = [0, 3, 5, 7, 10, 12]
    out = np.zeros(n, dtype=np.float32)

    def sq(freq, tt, duty=0.5):
        return np.where((tt * freq) % 1 < duty, 1.0, -1.0)

    step = beat / 2
    steps = int(dur / step) + 1
    melody = [scale[rng.integers(len(scale))] for _ in range(16)]
    for k in range(steps):
        s0 = int(k * step * SR)
        s1 = min(n, int((k + 1) * step * SR))
        if s0 >= n:
            break
        seg = t[s0:s1] - t[s0]
        env = np.exp(-seg * 7)
        root = roots[(k // 16) % 4]
        fb = 440 * 2 ** ((root - 12 - 69) / 12)
        out[s0:s1] += 0.10 * sq(fb, seg, 0.25) * np.exp(-seg * 3)
        if k % 2 == 0 or rng.random() > 0.5:
            note = root + 12 + melody[k % 16]
            fm = 440 * 2 ** ((note - 69) / 12)
            out[s0:s1] += 0.06 * sq(fm, seg, 0.125) * env
        if k % 4 == 0:
            out[s0:s1] += 0.25 * np.sin(2 * np.pi * (120 * np.exp(-seg * 30)) * seg) * np.exp(-seg * 20)
        if k % 4 == 2:
            out[s0:s1] += 0.08 * rng.uniform(-1, 1, s1 - s0) * np.exp(-seg * 25)
    return out


def pad(dur, seed):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    bar = 4.0
    out = np.zeros(n, dtype=np.float32)
    for ci in range(int(dur / bar) + 1):
        s0 = int(ci * bar * SR)
        s1 = min(n, int((ci + 1.25) * bar * SR))
        if s0 >= n:
            break
        seg = t[s0:s1] - t[s0]
        env = np.minimum(1, seg / 0.8) * np.minimum(1, np.maximum(0, (bar * 1.25 - seg) / 1.0))
        for note in chords[ci % 4]:
            f = 440 * 2 ** ((note - 69) / 12)
            out[s0:s1] += 0.05 * env * (np.sin(2 * np.pi * f * seg) + 0.3 * np.sin(2 * np.pi * f * 2.003 * seg))
        pulse = 0.5 + 0.5 * np.sin(2 * np.pi * seg / (60 / 100) * 2)
        out[s0:s1] += 0.015 * env * pulse * np.sin(2 * np.pi * 440 * 2 ** ((chords[ci % 4][0] - 57) / 12) * seg)
    return out


def whoosh(seed):
    rng = np.random.default_rng(seed)
    n = int(0.35 * SR)
    noise = rng.uniform(-1, 1, n)
    k = np.linspace(0, 1, n)
    env = np.sin(np.pi * k) ** 2
    cut = np.convolve(noise, np.ones(6) / 6, mode="same")
    return (0.18 * cut * env).astype(np.float32)


def blip(seed):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = 660 + 600 * t / t[-1]
    return (0.12 * np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 25)).astype(np.float32)


WHISPER = []


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_heard(wav, text, model, language):
    rec = {"wav_sha256": file_sha256(wav), "text": text, "model": model, "language": language}
    Path(wav).with_suffix(".heard.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2))
    return rec


def align_words(wav, narration, language="en"):
    cache = wav.with_suffix(".words.json")
    if cache.exists():
        return json.loads(cache.read_text())
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    name = "small" if language == "en" else "large-v3-turbo"
    if not WHISPER or WHISPER[0][0] != name:
        WHISPER[:] = [(name, WhisperModel(name, device="cpu", compute_type="int8"))]
    a = read_wav(wav)
    a16 = np.interp(np.arange(0, len(a), SR / 16000), np.arange(len(a)), a).astype(np.float32)
    segs, _ = WHISPER[0][1].transcribe(a16, language=language, word_timestamps=True)
    segs = list(segs)
    heard = [(w.word, w.start, w.end) for sg in segs for w in sg.words]
    write_heard(wav, "".join(sg.text for sg in segs).strip(), name, language)
    tokens = caption_tokens(narration)
    times = [None] * len(tokens)
    sm = difflib.SequenceMatcher(None, [norm_word(t) for t in tokens], [norm_word(h[0]) for h in heard], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("equal", "replace") and j2 > j1:
            s0, e0 = heard[j1][1], heard[j2 - 1][2]
            lens = [len(t) + 2 for t in tokens[i1:i2]]
            acc = s0
            for k, ln in zip(range(i1, i2), lens):
                d = (e0 - s0) * ln / sum(lens)
                times[k] = (acc, acc + d)
                acc += d
    k = 0
    end_audio = len(a) / SR
    while k < len(times):
        if times[k] is None:
            j = k
            while j < len(times) and times[j] is None:
                j += 1
            lo = times[k - 1][1] if k > 0 else 0.0
            hi = times[j][0] if j < len(times) else end_audio
            step = (hi - lo) / (j - k)
            for m in range(k, j):
                times[m] = (lo + step * (m - k), lo + step * (m - k + 1))
            k = j
        k += 1
    cache.write_text(json.dumps(times))
    return times


def scene_word_times(script, out):
    lang = script.get("language", "en")
    return [align_words(out / "audio" / f"{i:02d}.wav", sc["narration"], lang) for i, sc in enumerate(script["scenes"])]


def loudnorm_json(text):
    return json.loads(text[text.rindex("{"):text.rindex("}") + 1])


def loudnorm_measure(src, target=LOUDNESS_TARGET):
    af = f"loudnorm=I={target['I']}:TP={target['TP']}:LRA={target['LRA']}:print_format=json"
    if isinstance(src, np.ndarray):
        cmd = ["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", af, "-f", "null", "-"]
        r = subprocess.run(cmd, input=src.astype(np.float32).tobytes(), capture_output=True)
        return loudnorm_json(r.stderr.decode())
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-af", af, "-f", "null", "-"], capture_output=True, text=True)
    return loudnorm_json(r.stderr)


def lufs(audio):
    v = float(loudnorm_measure(audio)["input_i"])
    return v if math.isfinite(v) else -70.0


def true_peak_env(x, over=4):
    from scipy.signal import resample_poly

    up = np.abs(resample_poly(x.astype(np.float64), over, 1))[: len(x) * over]
    up = np.pad(up, (0, len(x) * over - len(up)))
    return np.maximum(np.abs(x), up.reshape(len(x), over).max(axis=1)).astype(np.float32)


def limit_peaks(x, ceiling, look=0.005):
    from scipy import ndimage

    need = np.minimum(1.0, ceiling / np.maximum(true_peak_env(x), 1e-9)).astype(np.float32)
    w = 2 * max(1, int(look * SR)) + 1
    g = ndimage.minimum_filter1d(need, w)
    g = ndimage.uniform_filter1d(g, w)
    return (x * np.minimum(g, need)).astype(np.float32)


def speech_presence(voice, attack=0.02, release=0.3, block=0.01):
    b = int(block * SR)
    nb = len(voice) // b + 1
    pad = np.pad(np.abs(voice), (0, nb * b - len(voice)))
    env = np.sqrt((pad.reshape(nb, b) ** 2).mean(axis=1))
    voiced = env[env > 1e-4]
    ref = float(np.percentile(voiced, 75)) if len(voiced) else 1.0
    raw = np.clip(env / (0.3 * ref), 0, 1)
    ka, kr = 1 - math.exp(-block / attack), 1 - math.exp(-block / release)
    sm = np.zeros(nb, np.float32)
    acc = 0.0
    for k in range(nb):
        x = raw[k]
        acc += (x - acc) * (ka if x > acc else kr)
        sm[k] = acc
    return np.interp(np.arange(len(voice)) / b, np.arange(nb), sm).astype(np.float32)


def duck_v2(voice, bed, st):
    sp = speech_presence(voice)
    speech = sp > 0.5
    rms = lambda x: 20 * math.log10(math.sqrt(float((x ** 2).mean())) + 1e-9)
    lv = rms(voice[speech]) if speech.any() else rms(voice)
    lm = rms(bed[np.abs(bed) > 1e-6]) if (np.abs(bed) > 1e-6).any() else -90.0
    under = min(12.0, lv + st.get("duck_under_db", -20.0) - lm)
    gdb = under + st.get("duck_gap_lift_db", 5.0) * (1 - sp)
    return (10 ** (gdb / 20)).astype(np.float32), {"voice_rms_db": round(lv, 2), "bed_rms_db": round(lm, 2), "under_gain_db": round(under, 2)}


def scene_timings(script, out, gap=0.18):
    lead_s = 0.15 if engine_version(script) >= 2 else 0.35
    voice_parts, timings, t = [np.zeros(int(lead_s * SR), dtype=np.float32)], [], lead_s
    for i in range(len(script["scenes"])):
        v = read_wav(out / "audio" / f"{i:02d}.wav")
        dur = len(v) / SR
        timings.append((t, dur))
        voice_parts.append(v)
        pause = script["scenes"][i].get("pause", gap)
        voice_parts.append(np.zeros(int(pause * SR), dtype=np.float32))
        t += dur + pause
    voice_parts.append(np.zeros(int(0.8 * SR), dtype=np.float32))
    voice = np.concatenate(voice_parts)
    return timings, len(voice) / SR, voice, lead_s


def step_audio(script, st, music_path, out, seed, gap=0.18):
    ev = engine_version(script)
    timings, total, voice, lead_s = scene_timings(script, out, gap)
    report = {"engine_version": ev, "lead": lead_s}
    gv = 1.0
    if st.get("narration_lufs") is not None:
        li = lufs(voice)
        gv = 10 ** ((st["narration_lufs"] - li) / 20)
        voice = voice * gv
        report.update(narration_lufs_in=round(li, 2), narration_gain_db=round(20 * math.log10(gv), 2))
    if music_path:
        tmp = out / "music_in.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", music_path, "-ar", str(SR), "-ac", "1", str(tmp)], check=True)
        music = read_wav(tmp)
        reps = int(math.ceil(len(voice) / len(music)))
        music = np.tile(music, reps)[: len(voice)] * 0.5
    elif st["music"] == "raga":
        import chalk

        music = chalk.music(total, timings, script, seed)[: len(voice)]
    elif st["music"] == "chiptune":
        music = chiptune(total, seed)[: len(voice)]
    else:
        music = pad(total, seed)[: len(voice)]
    music = np.pad(music, (0, len(voice) - len(music)))
    env = np.abs(voice)
    win = int(0.25 * SR)
    env = np.convolve(env, np.ones(win) / win, mode="same")
    duck = 1 - 0.65 * np.clip(env / 0.05, 0, 1)
    fade = np.minimum(1, np.minimum(np.arange(len(music)) / SR / 0.5, (len(music) - np.arange(len(music))) / SR / 1.2))
    sfx = np.zeros_like(voice)
    if st["motion"] == "chalkdraw":
        import chalk

        pl = chalk.plan(script, timings, total)
        sfx = chalk.sound(script, timings, total, pl, scene_word_times(script, out), seed)[: len(voice)]
        sfx = np.pad(sfx, (0, len(voice) - len(sfx)))
        duck = 1 - 0.45 * np.clip(env / 0.05, 0, 1)
    else:
        fx = blip if st["music"] == "chiptune" else whoosh
        for i, (start, _) in enumerate(timings[1:], 1):
            s = fx(seed + i)
            p = max(0, int((start - 0.15) * SR))
            sfx[p:p + len(s)] += s[: len(sfx) - p]
    if st.get("ducking") == "v2":
        bed = music * fade * st.get("music_gain", 0.55)
        gdyn, info = duck_v2(voice, bed, st)
        report["ducking"] = info
        mix = voice + bed * gdyn + sfx * gv
    else:
        mix = voice * 1.0 + music * duck * fade * st.get("music_gain", 0.55) + sfx * gv
    if st.get("loudnorm") == "two-pass":
        ceiling = 10 ** ((LOUDNESS_TARGET["TP"] - 0.7) / 20)
        for _ in range(3):
            mix = mix * 10 ** ((LOUDNESS_TARGET["I"] - lufs(mix)) / 20)
            mix = limit_peaks(mix, ceiling)
        write_wav(out / "mix.wav", mix)
        m = loudnorm_measure(out / "mix.wav")
        report["loudnorm_pass1"] = m
        (out / "loudnorm.json").write_text(json.dumps(report, indent=2))
    else:
        peak = np.max(np.abs(mix))
        if peak > 0.98:
            mix = mix / peak * 0.98
        write_wav(out / "mix.wav", mix)
    return timings, total


def loudnorm_filter(st, out):
    tg = LOUDNESS_TARGET
    if st.get("loudnorm") != "two-pass":
        return "loudnorm=I=-14:TP=-1.5:LRA=11"
    path = out / "loudnorm.json"
    m = json.loads(path.read_text())["loudnorm_pass1"] if path.exists() else loudnorm_measure(out / "mix.wav")
    lra = max(tg["LRA"], float(m["input_lra"]) + 1.0)
    return (
        f"loudnorm=I={tg['I']}:TP={tg['TP']}:LRA={lra}:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
        f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
    )


def write_timeline(script, timings, total, out, pl=None, bounds=None):
    scenes = []
    for i, (start, dur) in enumerate(timings):
        sc = script["scenes"][i]
        if pl:
            p = pl[i]
            row = {"start": round(p["vs"], 3), "cut": round(p["ds"], 3), "end": round(p["ve"], 3), "draw_end": round(p["de"], 3), "reveal": p["reveal"], "transition": p["transition"], "start_drawn": p["p0"]}
        else:
            s, e = bounds[i]
            row = {"start": round(s, 3), "cut": round(s, 3), "end": round(e, 3)}
        row.update(index=i, narration_start=round(start, 3), narration_end=round(start + dur, 3), kind=sc.get("kind", "story"), image=scene_still(script, i))
        for k in ("shot", "move", "accent", "overlay", "hit", "emphasis"):
            if sc.get(k):
                row[k] = sc[k]
        scenes.append(row)
    verses = [{"index": r["index"], "start": r["cut"], "end": r["end"]} for r in scenes if r["kind"] in ("verse", "shloka")]
    tl = {
        "engine_version": engine_version(script),
        "fps": FPS,
        "total": round(total, 3),
        "frames": int(total * FPS),
        "first_word": round(timings[0][0], 3),
        "hook_end": round(timings[0][0] + timings[0][1], 3),
        "verses": verses,
        "scenes": scenes,
    }
    (out / "timeline.json").write_text(json.dumps(tl, indent=2, ensure_ascii=False))
    return tl


def step_masks(script, st, out):
    if st.get("motion") != "chalkdraw" or engine_version(script) < 2:
        return []
    import parallax

    WHISPER.clear()
    stats = parallax.ensure_maps(script, out / "img", scene_still, log)
    for s in stats:
        if s["computed"]:
            log(f"{s['kind']}: {len(s['computed'])} still(s), model load {s['load_s']}s, {sum(s['per_image_s']):.1f}s inference")
    return stats


def step_render(script, st, timings, total, out, seed):
    step_masks(script, st, out)
    keywords = [k for sc in script["scenes"] for k in sc.get("keywords", [])]
    cap = Captioner(st, keywords)
    groups = []
    wts = scene_word_times(script, out)
    for i, ((start, dur), wt) in enumerate(zip(timings, wts)):
        groups += scene_caption_groups(script, st, cap, i, start, dur, wt)
    bounds = []
    for i, (start, dur) in enumerate(timings):
        s = 0 if i == 0 else start - 0.09
        e = timings[i + 1][0] - 0.09 if i + 1 < len(timings) else total
        bounds.append((s, e))
    video = out / "video.mp4"
    proc = subprocess.Popen(
        [
            "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(out / "mix.wav"),
            "-c:v", "h264_videotoolbox", "-b:v", "12M", "-pix_fmt", "yuv420p",
            "-af", loudnorm_filter(st, out), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(video),
        ],
        stdin=subprocess.PIPE,
    )
    if st["motion"] == "chalkdraw" and engine_version(script) >= 3:
        import puppetstudio

        raws = [raw_path(script, out, i) for i in range(len(script["scenes"]))]
        masks = [out / "img" / f"{scene_still(script, i):02d}_mask.png" for i in range(len(script["scenes"]))]
        if not puppetstudio.qa(script, timings, total, out, seed, raws, masks, log) and os.environ.get("STUDIO_RIG_FORCE") != "1":
            proc.stdin.close()
            proc.wait()
            raise SystemExit(f"Rig QA failed: see {out / 'rigqa'}; fix the rig (content/<ID>/rig.json) or set STUDIO_RIG_FORCE=1 to render anyway")
        pl = puppetstudio.render(script, st, timings, total, raws, proc, cap, groups, seed, log, masks, out)
        proc.stdin.close()
        proc.wait()
        write_timeline(script, timings, total, out, pl=pl)
        return video
    if st["motion"] == "chalkdraw":
        import chalk

        raws = [raw_path(script, out, i) for i in range(len(script["scenes"]))]
        masks = [out / "img" / f"{scene_still(script, i):02d}_mask.png" for i in range(len(script["scenes"]))]
        depths = [out / "img" / f"{scene_still(script, i):02d}_depth.png" for i in range(len(script["scenes"]))]
        pl = chalk.render(script, st, timings, total, raws, proc, cap, groups, seed, log, masks, depths)
        proc.stdin.close()
        proc.wait()
        write_timeline(script, timings, total, out, pl=pl)
        return video
    write_timeline(script, timings, total, out, bounds=bounds)
    imgs = [load_scene_image(raw_path(script, out, i), st) for i in range(len(script["scenes"]))]
    nframes = int(total * FPS)
    xf = 0.2
    log(f"render: {nframes} frames ({total:.1f}s)")
    for f in range(nframes):
        t = f / FPS
        idx = next((i for i, (s, e) in enumerate(bounds) if s <= t < e), len(bounds) - 1)
        s, e = bounds[idx]
        p = (t - s) / max(0.01, e - s)
        frame = scene_frame(imgs[idx], st, p, e - s, seed + idx)
        since = t - s
        if idx > 0 and since < xf:
            q = since / xf
            if st["transition"] == "crossfade":
                prev = scene_frame(imgs[idx - 1], st, 1.0, 1, seed + idx - 1)
                frame = Image.blend(prev, frame, q)
            elif st["transition"] == "flash":
                frame = Image.blend(Image.new("RGB", (W, H), "white"), frame, min(1, q * 1.6))
            elif st["transition"] == "slide":
                prev = scene_frame(imgs[idx - 1], st, 1.0, 1, seed + idx - 1)
                ease = 1 - (1 - q) ** 3
                off = int(W * ease)
                canvas = Image.new("RGB", (W, H))
                canvas.paste(prev, (-off, 0))
                canvas.paste(frame, (W - off, 0))
                frame = canvas
        group = next((g for g in groups if g["start"] <= t < g["end"] + 0.12), None)
        cap.draw(frame, group, t, script["scenes"][idx].get("emphasis", "").upper(), since)
        proc.stdin.write(frame.tobytes())
        if f % (FPS * 10) == 0:
            log(f"render: {t:.0f}s / {total:.0f}s")
    proc.stdin.close()
    proc.wait()
    return video


def step_extras(script, st, out):
    if st.get("thumbnail") == "chalk":
        import chalk

        if script.get("thumbnail"):
            chalk.thumbnail(script, raw_path(script, out, script["thumbnail"]["scene"]), out / "thumbnail.png", 42)
        else:
            log("extras: no thumbnail spec in the script; skipped (long-form thumbnails are made at the packaging step)")
        tags = " ".join("#" + h.lstrip("#").replace(" ", "") for h in script.get("hashtags", []))
        (out / "post.txt").write_text(f"{script['title']}\n\n{script.get('description', '')}\n\n{tags}\n")
        return out / "post.txt"
    first = load_scene_image(raw_path(script, out, 0), st)
    thumb = scene_frame(first, st, 0.5, 1, 0)
    dr = ImageDraw.Draw(thumb)
    font = ImageFont.truetype(st["font"], 120)
    lines = wrap(script["title"].upper(), font, W - 120, dr)
    y = int(H * 0.12)
    for line in lines:
        tw = dr.textlength(line, font=font)
        dr.text(((W - tw) / 2, y), line, font=font, fill=st["caption_color"], stroke_width=14, stroke_fill="black")
        y += 140
    thumb.save(out / "thumbnail.png")
    tags = " ".join("#" + h.lstrip("#").replace(" ", "") for h in script["hashtags"])
    (out / "post.txt").write_text(f"{script['title']}\n\n{script['description']}\n\n{tags} #shorts\n")
    return out / "post.txt"


def main():
    ap = argparse.ArgumentParser(description="Topic in, publish-ready vertical short out. Free and local.")
    ap.add_argument("topic")
    ap.add_argument("--style", default="pixel", choices=list(STYLES))
    ap.add_argument("--seconds", type=int, default=45)
    ap.add_argument("--voice", default="am_michael", help="Kokoro voice, e.g. af_heart, am_michael, bf_emma, am_puck")
    ap.add_argument("--speed", type=float, default=1.08)
    ap.add_argument("--llm", default="qwen3:8b")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--steps", type=int, default=9)
    ap.add_argument("--notes", help="optional text file of facts/research to ground the script")
    ap.add_argument("--music", help="optional music file (e.g. from YouTube Audio Library); default is generated music")
    ap.add_argument("--redo", nargs="*", default=[], choices=["script", "voice", "images", "render"])
    ap.add_argument("--stop-after", choices=["script", "voice", "images"])
    ap.add_argument("--out", help="working folder for this video (default: out/<topic-slug>)")
    a = ap.parse_args()
    ensure_raqm()

    out = Path(a.out) if a.out else ROOT / "out" / slugify(a.topic)
    out.mkdir(parents=True, exist_ok=True)
    if "script" in a.redo:
        (out / "script.json").unlink(missing_ok=True)
        (out / "notes.txt").unlink(missing_ok=True)
    if "voice" in a.redo or "script" in a.redo:
        shutil.rmtree(out / "audio", ignore_errors=True)
    if "images" in a.redo or "script" in a.redo:
        shutil.rmtree(out / "img", ignore_errors=True)
    st = STYLES[a.style]
    t0 = time.time()

    script = step_script(a.topic, a.style, a.seconds, a.llm, out, a.notes)
    st = effective_style(a.style, script)
    if st.get("motion") == "chalkdraw":
        import chalk

        chalk.use_fonts(script.get("fonts", "mac"))
    if a.stop_after == "script":
        return
    step_voice(script, a.voice, a.speed, out)
    if a.stop_after == "voice":
        return
    step_images(script, a.style, a.seed, a.steps, out)
    if a.stop_after == "images":
        return
    timings, total = step_audio(script, st, a.music, out, a.seed)
    video = step_render(script, st, timings, total, out, a.seed)
    step_extras(script, st, out)
    final = out / f"{slugify(script['title'])}.mp4"
    shutil.move(video, final)
    log(f"done in {(time.time() - t0) / 60:.1f} min -> {final}")


if __name__ == "__main__":
    main()
