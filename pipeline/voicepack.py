import json
import sys
import time
from pathlib import Path

import numpy as np

from . import ROOT

SR = 24000
_CACHE = {}


def maya2_model():
    if "maya2" not in _CACHE:
        from mlx_audio.tts.utils import load

        _CACHE["maya2"] = load("maya-research/maya2-native")
    return _CACHE["maya2"]


def maya2_speak(text, voice, lang="hi"):
    out = [np.array(r.audio).reshape(-1) for r in maya2_model().generate(text, voice=voice, lang_code=lang)]
    return np.concatenate(out).astype(np.float32)


def svara_model():
    if "svara" not in _CACHE:
        from mlx_audio.tts.utils import load

        _CACHE["svara"] = load("mlx-community/svara-tts-v1-4bit")
    return _CACHE["svara"]


def svara_speak(text, voice, lang="hi"):
    out = [np.array(r.audio).reshape(-1) for r in svara_model().generate(text=text, voice=voice)]
    return np.concatenate(out).astype(np.float32)


def veena_speak(text, speaker, lang="hi"):
    if "veena" not in _CACHE:
        from veena import Veena

        v = Veena()
        vp = json.loads((ROOT / "profiles" / "voices.json").read_text()).get(lang, {}).get("voice_prompt")
        if vp:
            v.set_voice_prompt(ROOT / vp["wav"], vp["text"], speaker)
        _CACHE["veena"] = v
    return _CACHE["veena"].speak(text, speaker, seed=7)


ENGINES = {"maya2": maya2_speak, "svara": svara_speak, "veena": veena_speak}


def speak(voice_id, text, lang):
    engine, name = voice_id.split(":", 1)
    return ENGINES[engine](text, name, lang)


def build(out_dir, lines, voices, lang="hi"):
    sys.path.insert(0, str(ROOT))
    import studio
    from faster_whisper import WhisperModel
    from .qa import char_error

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    asr = WhisperModel("small" if lang == "en" else "large-v3-turbo", device="cpu", compute_type="int8")
    rows = []
    current = None
    for v in voices:
        engine = v.split(":", 1)[0]
        if current and engine != current:
            import gc

            _CACHE.clear()
            gc.collect()
            try:
                import mlx.core as mx

                mx.clear_cache()
            except Exception:
                pass
            try:
                import torch

                torch.mps.empty_cache()
            except Exception:
                pass
        current = engine
        for k, line in enumerate(lines, 1):
            t0 = time.time()
            try:
                a = speak(v, line, lang)
            except Exception as e:
                rows.append({"voice": v, "line": k, "error": str(e)[:200]})
                print(f"{v} line {k}: ERROR {str(e)[:120]}", flush=True)
                continue
            secs = time.time() - t0
            path = out / f"{v.replace(':', '_')}_line{k}.wav"
            studio.write_wav(path, a)
            a16 = np.interp(np.arange(0, len(a), SR / 16000), np.arange(len(a)), a).astype(np.float32)
            heard = " ".join(s.text.strip() for s in asr.transcribe(a16, language=lang, beam_size=5)[0])
            cer = char_error(line, heard, lang)[0]
            rows.append({"voice": v, "line": k, "file": path.name, "seconds_audio": round(len(a) / SR, 1), "gen_seconds": round(secs, 1), "cer": cer, "heard": heard})
            print(f"{v} line {k}: {len(a) / SR:.1f}s audio in {secs:.0f}s · CER {cer} | {heard}", flush=True)
    (out / "results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    md = ["# Voice listening pack", "", "Listen to each line across voices; the CER column is a secondary automatic signal (it missed real pronunciation errors before).", "", "| Voice | Line | File | CER | Speed (gen s / audio s) |", "|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['voice']} | {r['line']} | {r.get('file', r.get('error', ''))} | {r.get('cer', '')} | {r.get('gen_seconds', '')}/{r.get('seconds_audio', '')} |")
    md += ["", "## Lines", ""] + [f"{k}. {l}" for k, l in enumerate(lines, 1)]
    (out / "README.md").write_text("\n".join(md) + "\n")
    return rows
