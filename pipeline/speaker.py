import json
from pathlib import Path

import numpy as np

from . import DATA, PROFILES

SR = 24000
_MODEL = []


def model():
    if not _MODEL:
        from speechbrain.inference.speaker import EncoderClassifier

        _MODEL.append(EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir=str(DATA / "models" / "ecapa"), run_opts={"device": "cpu"}))
    return _MODEL[0]


def embed(audio, sr=SR):
    import torch

    a16 = np.interp(np.arange(0, len(audio), sr / 16000), np.arange(len(audio)), audio).astype(np.float32)
    with torch.no_grad():
        e = model().encode_batch(torch.from_numpy(a16).unsqueeze(0)).squeeze().numpy()
    return e / (np.linalg.norm(e) + 1e-9)


def f0_median(a, sr=SR, win=1024, hop=240):
    out = []
    for s in range(0, len(a) - win, hop):
        x = a[s:s + win] - a[s:s + win].mean()
        if np.sqrt(np.mean(x ** 2)) < 0.02:
            continue
        ac = np.fft.irfft(np.abs(np.fft.rfft(x, 2 * win)) ** 2)[:win]
        lo, hi = int(sr / 400), int(sr / 70)
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[k] / (ac[0] + 1e-9) > 0.45:
            out.append(sr / k)
    return float(np.median(out)) if out else None


def split_on_silence(a, min_gap=0.08, thresh=1e-4):
    quiet = np.abs(a) < thresh
    segs, start, run = [], None, 0
    for i, q in enumerate(quiet):
        if not q:
            if start is None:
                start = i
            run = 0
        else:
            run += 1
            if start is not None and run >= int(min_gap * SR):
                end = i - run + 1
                if end - start > int(0.3 * SR):
                    segs.append((start, end))
                start = None
    if start is not None and len(a) - start > int(0.3 * SR):
        segs.append((start, len(a)))
    return segs


def reference_path(lang, speaker):
    return PROFILES / "voices" / f"{lang}_{speaker}_ref.npy"


def analyse(wavs):
    import studio

    rows = []
    for w in wavs:
        a = studio.read_wav(w)
        for k, (s, e) in enumerate(split_on_silence(a)):
            seg = a[s:e]
            rows.append({"file": Path(w).name, "seg": k, "start": round(s / SR, 2), "dur": round((e - s) / SR, 2), "f0": f0_median(seg), "emb": embed(seg)})
    return rows


def consistency(rows, ref=None):
    E = np.stack([r["emb"] for r in rows])
    if ref is None:
        sims = E @ E.T
        ref = E[int(np.argmax(sims.mean(1)))]
    for r in rows:
        r["sim"] = round(float(r["emb"] @ ref), 3)
    return rows, ref
