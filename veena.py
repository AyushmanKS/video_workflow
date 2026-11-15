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

    def _chunk(self, text, speaker, temperature, seed):
        torch.manual_seed(seed)
        ids = self.tok.encode(f"<spk_{speaker}> {text}", add_special_tokens=False)
        inp = torch.tensor([[START_OF_HUMAN, *ids, END_OF_HUMAN, START_OF_AI, START_OF_SPEECH]], device=self.device)
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
    def phrases(text):
        parts = re.split(r"(\.\.\.|।|॥|!|\?|—|,|:)", text)
        res, cur = [], ""
        for p in parts:
            if p in PAUSES:
                cur = cur.strip()
                if cur:
                    res.append((cur + ("" if p in ("—", "...") else p), PAUSES[p]))
                elif res:
                    res[-1] = (res[-1][0], max(res[-1][1], PAUSES[p]))
                cur = ""
            else:
                cur += p
        if cur.strip():
            res.append((cur.strip(), 0.0))
        merged = []
        for t, pause in res:
            if merged and len(merged[-1][0]) < 18 and merged[-1][1] <= 0.14:
                merged[-1] = (merged[-1][0] + ", " + t, pause)
            else:
                merged.append((t, pause))
        return merged

    def speak(self, text, speaker="kavya", temperature=0.4, seed=0):
        out = []
        for k, (phrase, pause) in enumerate(self.phrases(text)):
            audio, _ = self._chunk(phrase, speaker, temperature, seed + k)
            out.append(trim(audio))
            out.append(np.zeros(int(pause * SR), np.float32))
        return np.concatenate(out) if out else np.zeros(SR // 10, np.float32)


def trim(a, thresh=0.01):
    idx = np.nonzero(np.abs(a) > thresh)[0]
    if not len(idx):
        return a
    s = max(0, idx[0] - int(0.03 * SR))
    e = min(len(a), idx[-1] + int(0.08 * SR))
    return a[s:e]
