import json
import sys
from pathlib import Path

from . import ROOT, db
from .qa import char_error


def best_of(work_dir, language, speaker, scenes=None, n=3, threshold=0.0):
    sys.path.insert(0, str(ROOT))
    import numpy as np
    import studio
    from faster_whisper import WhisperModel
    from veena import Veena

    work = Path(work_dir)
    (work / "audio").mkdir(parents=True, exist_ok=True)
    script = json.loads((work / "script.json").read_text())
    asr = WhisperModel("small" if language == "en" else "large-v3-turbo", device="cpu", compute_type="int8")
    engine = Veena()
    log_path = work / "voice_qa.json"
    log = json.loads(log_path.read_text()) if log_path.exists() else {}
    for i, sc in enumerate(script["scenes"]):
        if scenes and i + 1 not in scenes:
            continue
        best = None
        for k in range(n):
            seed = 1000 + i * 10 + k
            a = engine.speak(sc.get("tts", sc["narration"]), speaker, seed=seed)
            a16 = np.interp(np.arange(0, len(a), studio.SR / 16000), np.arange(len(a)), a).astype(np.float32)
            heard = " ".join(s.text.strip() for s in asr.transcribe(a16, language=language, beam_size=5)[0])
            cer, ratio = char_error(sc["narration"], heard)
            score = cer + max(0, ratio - 1.08)
            print(f"scene {i + 1} take {k + 1} seed {seed}: {len(a) / studio.SR:.1f}s score {score:.3f} | {heard}", flush=True)
            if best is None or score < best[0]:
                best = (score, seed, a, heard)
            if score <= threshold:
                break
        studio.write_wav(work / "audio" / f"{i:02d}.wav", best[2])
        (work / "audio" / f"{i:02d}.words.json").unlink(missing_ok=True)
        sc["voice_seed"] = best[1]
        log[str(i + 1)] = {"score": round(best[0], 3), "seed": best[1], "heard": best[3], "at": db.now()}
        print(f"==> scene {i + 1}: kept seed {best[1]} (score {best[0]:.3f})", flush=True)
    fresh = json.loads((work / "script.json").read_text())
    for i, sc in enumerate(script["scenes"]):
        if "voice_seed" in sc and i < len(fresh["scenes"]):
            fresh["scenes"][i]["voice_seed"] = sc["voice_seed"]
    (work / "script.json").write_text(json.dumps(fresh, indent=2, ensure_ascii=False))
    log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False))
    return log
