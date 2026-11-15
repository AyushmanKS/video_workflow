import re

import numpy as np
import torch

SR = 24000
START_OF_SPEECH, END_OF_SPEECH = 128257, 128258
START_OF_HUMAN, END_OF_HUMAN = 128259, 128260
START_OF_AI, END_OF_AI = 128261, 128262
AUDIO_BASE = 128266
PAUSES = {"...": 0.34, "।": 0.26, "॥": 0.4, "!": 0.26, "?": 0.3, "—": 0.16, ",": 0.1, ":": 0.16}


class Veena:
    def __init__(self, device=None):
        from snac import SNAC
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.device = device or ("mps" if torch.backends.mps.is_available() else "cpu")
        self.tok = AutoTokenizer.from_pretrained("maya-research/Veena", trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained("maya-research/Veena", torch_dtype=torch.bfloat16, trust_remote_code=True).to(self.device).eval()
        self.snac = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").eval().to("cpu")
        self.prompt = []

    def set_voice_prompt(self, wav_path, text, speaker="kavya"):
        import wave

        with wave.open(str(wav_path)) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32767
        with torch.no_grad():
            l0, l1, l2 = [c.squeeze(0).tolist() for c in self.snac.encode(torch.from_numpy(a).float().view(1, 1, -1))]
        toks = []
        for i in range(len(l0)):
            toks += [l0[i] + AUDIO_BASE, l1[2 * i] + AUDIO_BASE + 4096, l2[4 * i] + AUDIO_BASE + 2 * 4096, l2[4 * i + 1] + AUDIO_BASE + 3 * 4096,
                     l1[2 * i + 1] + AUDIO_BASE + 4 * 4096, l2[4 * i + 2] + AUDIO_BASE + 5 * 4096, l2[4 * i + 3] + AUDIO_BASE + 6 * 4096]
        ids = self.tok.encode(f"<spk_{speaker}> {text}", add_special_tokens=False)
        self.prompt = [START_OF_HUMAN, *ids, END_OF_HUMAN, START_OF_AI, START_OF_SPEECH, *toks, END_OF_SPEECH, END_OF_AI]

    def _chunk(self, text, speaker, temperature, seed):
        torch.manual_seed(seed)
        ids = self.tok.encode(f"<spk_{speaker}> {text}", add_special_tokens=False)
        inp = torch.tensor([[*self.prompt, START_OF_HUMAN, *ids, END_OF_HUMAN, START_OF_AI, START_OF_SPEECH]], device=self.device)
        max_new = min(int(len(text) * 1.3) * 7 + 21, 1400)
        with torch.no_grad():
            out = self.model.generate(
                inp, max_new_tokens=max_new, do_sample=True, temperature=temperature, top_p=0.9,
                repetition_penalty=1.05, pad_token_id=self.tok.pad_token_id, eos_token_id=[END_OF_SPEECH, END_OF_AI],
            )
        gen = out[0][inp.shape[1]:].tolist()
        codes = [t for t in gen if AUDIO_BASE <= t < AUDIO_BASE + 7 * 4096]
        codes = codes[: len(codes) // 7 * 7]
        if not codes:
            return np.zeros(int(0.1 * SR), np.float32), True
        lv = [[], [], []]
        off = [AUDIO_BASE + i * 4096 for i in range(7)]
        for i in range(0, len(codes), 7):
            lv[0].append(codes[i] - off[0])
            lv[1] += [codes[i + 1] - off[1], codes[i + 4] - off[4]]
            lv[2] += [codes[i + 2] - off[2], codes[i + 3] - off[3], codes[i + 5] - off[5], codes[i + 6] - off[6]]
        hier = [torch.tensor(l, dtype=torch.int32).clamp(0, 4095).unsqueeze(0) for l in lv]
        with torch.no_grad():
            audio = self.snac.decode(hier).squeeze().clamp(-1, 1).numpy()
        truncated = len(gen) >= max_new
        return audio.astype(np.float32), truncated

    @staticmethod
    def sentences(text, max_chars=140):
        parts = re.split(r"(?<=[।॥!?])\s+", text.strip())
        out = []
        for p in parts:
            if out and len(out[-1]) + 1 + len(p) <= max_chars:
                out[-1] = out[-1] + " " + p
            else:
                out.append(p)
        final = []
        for p in out:
            while len(p) > max_chars:
                cut = max(p.rfind(",", 0, max_chars), p.rfind("—", 0, max_chars))
                cut = cut if cut > 40 else max_chars
                final.append(p[:cut + 1].strip())
                p = p[cut + 1:].strip()
            if p:
                final.append(p)
        return final

    def speak(self, text, speaker="kavya", temperature=0.4, seed=0, ref=None, min_sim=0.72, f0_range=(150, 320), max_tries=4, log=None):
        out = []
        chunks = self.sentences(text)
        for k, chunk in enumerate(chunks):
            best = None
            for t in range(max_tries if ref is not None else 1):
                audio, _ = self._chunk(chunk, speaker, temperature, seed + k * 100 + t)
                audio = trim(audio)
                if ref is None:
                    best = (1.0, audio)
                    break
                from pipeline import speaker as spk

                sim = float(spk.embed(audio) @ ref)
                f0 = spk.f0_median(audio)
                ok = sim >= min_sim and f0 is not None and f0_range[0] <= f0 <= f0_range[1]
                if log:
                    log(f"    chunk {k + 1}/{len(chunks)} try {t + 1}: speaker sim {sim:.2f}, F0 {f0 and round(f0)} Hz {'ok' if ok else 'rejected'}")
                if best is None or sim > best[0]:
                    best = (sim, audio)
                if ok:
                    break
            out.append(best[1])
            end = chunk.rstrip()[-1:] if chunk.strip() else ""
            if k < len(chunks) - 1:
                out.append(np.zeros(int(PAUSES.get(end, 0.25) * SR), np.float32))
        return np.concatenate(out) if out else np.zeros(SR // 10, np.float32)


def trim(a, thresh=0.01):
    idx = np.nonzero(np.abs(a) > thresh)[0]
    if not len(idx):
        return a
    s = max(0, idx[0] - int(0.03 * SR))
    e = min(len(a), idx[-1] + int(0.08 * SR))
    return a[s:e]
