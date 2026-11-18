import json
import math
from pathlib import Path

import cv2
import numpy as np

SMALL = (288, 512)
STILL = 0.006
MOVING = 0.02
INDIGO = (31, 37, 71)
MAX_SOFT = 3
MAX_DIP = 1
NIGHT_L = 40.0
DAY_L = 50.0
PHASE_MAX_L = {"night": 36.0, "dusk": 46.0, "lamp": 44.0}
PHASE_STRENGTH = {"night": 0.85, "dusk": 0.6, "lamp": 0.6}
MIN_RATE_STILL = 0.4
MIN_RATE_MOVING = 0.9
CARRY_TAU = 0.8
MAX_SCALE = 1.06
GUARD = 4

BEATS = {
    "turn": {"type": "dip", "out": 0.5, "in": 0.55, "hold": 0.35, "j": 0.6, "l": 0.0, "why": "story turn: a held dip marks the change of world; the one dip this Short allows"},
    "time_jump": {"type": "dissolve", "dur": 1.0, "j": 0.5, "l": 0.4, "why": "time passes between the shots: a 1 s dissolve on live frames reads as 'later'"},
    "simile": {"type": "cut", "j": 0.7, "l": 0.3, "why": "the image is a comparison the narration makes: lead with its sound so the sound motivates the cut"},
    "parallel": {"type": "cut", "j": 1.0, "l": 0.5, "why": "parallel action in another place: a sound bridge (J-cut) joins the two places"},
    "action": {"type": "cut", "j": 0.3, "l": 0.3, "why": "same scene, new action: a hard cut on movement keeps pace"},
    "reveal": {"type": "cut", "j": 0.4, "l": 1.0, "why": "a reveal: hard cut, the outgoing sound lingers (L-cut) so the new figure is watched in the old world's sound"},
    "same_scene": {"type": "cut", "j": 0.4, "l": 0.3, "why": "same place and moment: a straight cut, continuity carried by sound and camera"},
    "new_place": {"type": "cut", "j": 0.5, "l": 0.4, "why": "new place, same time: a cut with the new place's sound arriving first"},
}


def read_frames(path):
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    out = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        out.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
    cap.release()
    return out, float(fps)


def fit_similarity(flow, step=8):
    h, w = flow.shape[:2]
    ys, xs = np.mgrid[0:h:step, 0:w:step].astype(np.float32)
    x = ((xs - w / 2) / w).ravel()
    y = ((ys - h / 2) / w).ravel()
    u = (flow[::step, ::step, 0] / w).ravel()
    v = (flow[::step, ::step, 1] / w).ravel()
    n = len(x)
    A = np.zeros((2 * n, 4), np.float32)
    A[:n, 0] = 1
    A[:n, 2] = x
    A[:n, 3] = -y
    A[n:, 1] = 1
    A[n:, 2] = y
    A[n:, 3] = x
    b = np.concatenate([u, v])
    p, *_ = np.linalg.lstsq(A, b, rcond=None)
    res = np.hypot(*(b - A @ p).reshape(2, n))
    return p, float(np.median(res))


def smooth(x, k=5):
    x = np.asarray(x, np.float64)
    if len(x) < k:
        return x
    pad = np.pad(x, (k // 2, k // 2), mode="edge")
    return np.convolve(pad, np.ones(k) / k, mode="valid")


def measure(path, cache=None):
    path = Path(path)
    st = path.stat()
    sig = f"{st.st_size}-{int(st.st_mtime)}"
    cf = Path(cache) / f"{path.stem}.features.json" if cache else None
    if cf and cf.exists():
        d = json.loads(cf.read_text())
        if d.get("sig") == sig:
            return d
    frames, fps = read_frames(path)
    w, h = SMALL
    small = [cv2.resize(f, SMALL, interpolation=cv2.INTER_AREA) for f in frames]
    gray = [cv2.cvtColor(s, cv2.COLOR_RGB2GRAY) for s in small]
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    rec = {k: [] for k in ("pan_x", "pan_y", "zoom", "local", "energy", "diff")}
    for k in range(1, len(gray)):
        flow = dis.calc(gray[k - 1], gray[k], None)
        p, res = fit_similarity(flow)
        px, py, z = p[0] * fps, p[1] * fps * w / h, p[2] * fps
        rec["pan_x"].append(float(px))
        rec["pan_y"].append(float(py))
        rec["zoom"].append(float(z))
        rec["local"].append(res * fps)
        rec["energy"].append(float(abs(px) + abs(py) + 0.5 * abs(z)))
        rec["diff"].append(float(np.abs(gray[k].astype(np.int16) - gray[k - 1]).mean()))
    for k in rec:
        rec[k] = [rec[k][0] if rec[k] else 0.0] + rec[k]
    lab = [cv2.cvtColor(s.astype(np.float32) / 255, cv2.COLOR_RGB2Lab) for s in small]
    d = {"sig": sig, "clip": str(path), "fps": fps, "n": len(frames), "w": frames[0].shape[1], "h": frames[0].shape[0], **rec,
         "L": [float(x[..., 0].mean()) for x in lab], "a": [float(x[..., 1].mean()) for x in lab],
         "b": [float(x[..., 2].mean()) for x in lab], "Ls": [float(x[..., 0].std()) for x in lab]}
    d.update(cadence(d["diff"]))
    if cf:
        cf.parent.mkdir(parents=True, exist_ok=True)
        cf.write_text(json.dumps(d))
    return d


def cadence(diff):
    d = np.asarray(diff)
    ratios, dups = [], []
    for k in range(1, len(d) - 1):
        hi, lo = max(d[k], d[k + 1]), min(d[k], d[k + 1])
        if hi > 1.0:
            ratios.append(hi / max(lo, 0.05))
        nb = max(d[k - 1], d[k + 1])
        if nb > 1.2 and d[k] < 0.35 * nb:
            dups.append(k)
    idx = float(np.median(ratios)) if ratios else 1.0
    return {"on_twos_index": round(idx, 2), "on_twos": idx > 2.5, "duplicates": dups if idx > 2.5 else []}


def motion(f):
    return smooth(np.asarray(f["energy"]) + np.asarray(f["local"]), 5)


def runs(mask):
    out, start = [], None
    for k, v in enumerate(list(mask) + [False]):
        if v and start is None:
            start = k
        elif not v and start is not None:
            out.append((start, k - 1))
            start = None
    return out


def window(f):
    n = f["n"]
    L = np.asarray(f["L"])
    Ls = smooth(L, 5)
    diff = np.asarray(f["diff"])
    m = motion(f)
    med = np.array([np.median(L[max(0, k - 4): k + 5]) for k in range(n)])
    flick = np.abs(L - med) > np.maximum(3.0, 0.07 * med)
    spike = np.zeros(n, bool) if f.get("on_twos") else diff > max(6.0, 3.5 * np.percentile(diff, 75))
    stable = np.abs(np.gradient(Ls)) < 0.2
    ref = float(np.median(Ls[stable])) if stable.sum() > 10 else float(np.median(Ls))
    art = (np.abs(Ls - ref) > max(5.0, 0.1 * ref)) & (m < 0.05)
    bad = flick | spike | art
    good = runs(~bad)
    head, tail = max(good, key=lambda r: r[1] - r[0]) if good else (0, n - 1)
    notes = []
    for a, b in runs(art):
        notes.append(f"frames {a}–{b}: light changes with no camera move (L* {Ls[a]:.0f}→{Ls[b]:.0f}, self-fade or pulse)")
    fl = int((flick | spike).sum())
    if fl:
        notes.append(f"{fl} flicker/pop frames")
    inner = [k for k in np.where(bad)[0] if head <= k <= tail]
    for k in inner:
        if k - head < GUARD:
            head = k + 1
        elif tail - k < GUARD:
            tail = k - 1
    if head > 0 or tail < n - 1:
        notes.append(f"usable {head}–{tail} of 0–{n - 1}")
    return {"head": int(head), "tail": int(tail), "notes": notes}


def stillness(f, h, t):
    m = motion(f)[h: t + 1]
    return np.clip(1 - m / MOVING, 0, 1)


def max_slow(q):
    rmin = MIN_RATE_MOVING - (MIN_RATE_MOVING - MIN_RATE_STILL) * q
    return 1 / rmin - 1


def capacity(f, win):
    h, t = win["head"], win["tail"]
    fps = f["fps"]
    U = (t - h + 1) / fps
    extra = float(max_slow(stillness(f, h, t)).sum() / fps)
    return {"rate1": round(U, 3), "max": round(U + extra, 3)}


def describe_camera(f, a, b):
    seg = lambda k: float(np.median(np.asarray(f[k])[a: b + 1])) if b >= a else 0.0
    px, py, z, e = seg("pan_x"), seg("pan_y"), seg("zoom"), seg("energy")
    if e < STILL:
        return "static", z
    parts = []
    if z > 0.006:
        parts.append("push-in")
    elif z < -0.006:
        parts.append("pull-back")
    if abs(px) > 0.004:
        parts.append("pan left" if px > 0 else "pan right")
    if abs(py) > 0.004:
        parts.append("tilt up" if py > 0 else "tilt down")
    return ", ".join(parts) or "drift", z


def classify_light(L):
    return "night" if L < NIGHT_L else ("dim" if L < DAY_L else "day")


def decide(i, A, B, fa, fb, wa, wb, beat):
    spec = dict(BEATS.get(beat or "", BEATS["same_scene"] if A.get("place") == B.get("place") else BEATS["new_place"]))
    reasons = [spec.pop("why")]
    flags = []
    LA = float(np.mean(fa["L"][max(wa["head"], wa["tail"] - 12): wa["tail"] + 1]))
    LB = float(np.mean(fb["L"][wb["head"]: wb["head"] + 12]))
    bA = float(np.mean(fa["b"][max(wa["head"], wa["tail"] - 12): wa["tail"] + 1]))
    bB = float(np.mean(fb["b"][wb["head"]: wb["head"] + 12]))
    camA, zA = describe_camera(fa, max(wa["head"], wa["tail"] - 12), wa["tail"])
    camB, zB = describe_camera(fb, wb["head"], wb["head"] + 12)
    if spec["type"] == "cut" and A.get("place") == B.get("place") and A.get("subject") == B.get("subject") and A.get("size") == B.get("size"):
        flags.append({"kind": "jump_cut", "fix": "regenerate the incoming shot from a different angle or size (30° / one shot size), or insert a cutaway", "severity": 4})
        reasons.append("same subject, place and shot size: this cut is a jump cut; editing can only soften it (cut on the incoming action, sound bridge)")
    if (zA > 0.006 and zB < -0.006) or (zA < -0.006 and zB > 0.006):
        reasons.append(f"camera reverses ({camA} → {camB}): incoming head gets a short digital counter-move")
    if A.get("time") != B.get("time") and spec["type"] == "cut" and beat not in ("turn", "parallel", "reveal"):
        reasons.append(f"time of day changes ({A.get('time')} → {B.get('time')}) on a plain cut")
    if B.get("screen") and A.get("screen") and B.get("subject") and A.get("subject") and set(str(A["subject"]).split("+")) & set(str(B["subject"]).split("+")) and A["screen"] != B["screen"]:
        flags.append({"kind": "screen_side", "fix": f"the shared character moves from frame {A['screen']} to frame {B['screen']}: regenerate or mirror the incoming shot", "severity": 3})
    if fa.get("on_twos") != fb.get("on_twos"):
        reasons.append("motion cadence differs (12 vs 24 fps feel): the on-twos side is cadence-repaired")
    return {"into": i, "beat": beat, **spec, "reasons": reasons, "flags": flags,
            "measured": {"L_out": round(LA, 1), "L_in": round(LB, 1), "dL": round(LB - LA, 1), "db": round(bB - bA, 1), "camera_out": camA, "camera_in": camB, "zoom_out": round(zA, 4), "zoom_in": round(zB, 4)}}


def limit(decisions):
    soft = [d for d in decisions if d["type"] != "cut"]
    dips = [d for d in soft if d["type"] == "dip"]
    for d in dips[MAX_DIP:]:
        d.update(type="dissolve", dur=0.8)
        d["reasons"].append("only one dip per Short: downgraded to a dissolve")
    soft = [d for d in decisions if d["type"] != "cut"]
    for d in sorted(soft, key=lambda d: d["type"] == "dip")[: max(0, len(soft) - MAX_SOFT)]:
        d["type"] = "cut"
        d["reasons"].append(f"more than {MAX_SOFT} soft transitions: downgraded to a cut")
    return decisions


def ext(d):
    if d is None:
        return 0.0
    if d["type"] == "dissolve":
        return d["dur"] / 2
    if d["type"] == "dip":
        return -d["hold"] / 2
    return 0.0


def shot_cost(span, cap):
    if span < 1.0:
        return 50.0
    if span <= cap["rate1"]:
        return 0.0
    if span <= cap["max"]:
        return 0.5 + 2.0 * (span - cap["rate1"]) / max(cap["rate1"], 0.5)
    return 2.5 + 15.0 * (span - cap["max"])


def boundary_cost(c, d, line_prev, line_next):
    s = line_next[0]
    e = line_prev[0] + line_prev[1]
    mid = (e + s) / 2
    if d["type"] == "dip":
        return 3.0 * abs(c - mid)
    if d["type"] == "dissolve":
        return 2.0 * abs(c - mid)
    return 0.4 * abs(c - (s + 0.08))


def allocate(caps, decisions, lines, total, fps):
    n = len(caps)
    cands = []
    for i in range(1, n):
        s = lines[i][0]
        e = lines[i - 1][0] + lines[i - 1][1]
        g = np.round(np.arange(s - 0.75, s + 0.75 + 1e-9, 1 / fps) * fps) / fps
        g = g[g > lines[i - 1][0] + 0.8]
        cands.append(g)
    dec = {d["into"]: d for d in decisions}
    INF = float("inf")
    cost = [np.full(len(c), INF) for c in cands]
    back = [np.zeros(len(c), int) for c in cands]
    for j, c in enumerate(cands[0]):
        span = c + ext(dec.get(1))
        cost[0][j] = shot_cost(span, caps[0]) + boundary_cost(c, dec[1], lines[0], lines[1])
    for i in range(1, n - 1):
        din, dout = dec[i], dec[i + 1]
        for j, c in enumerate(cands[i]):
            bc = boundary_cost(c, dout, lines[i], lines[i + 1])
            best, arg = INF, 0
            for k, p in enumerate(cands[i - 1]):
                if cost[i - 1][k] == INF or c - p < 1.0:
                    continue
                span = (c + ext(dout)) - (p - ext(din))
                v = cost[i - 1][k] + shot_cost(span, caps[i])
                if v < best:
                    best, arg = v, k
            cost[i][j] = best + bc
            back[i][j] = arg
    last = dec[n - 1]
    final = np.array([cost[-1][j] + shot_cost(total - (c - ext(last)), caps[-1]) for j, c in enumerate(cands[-1])])
    j = int(np.argmin(final))
    cuts = [0.0] * (n + 1)
    cuts[n] = total
    for i in range(n - 2, -1, -1):
        cuts[i + 1] = float(cands[i][j])
        j = back[i][j]
    return cuts, float(final.min())


def pick_window(f, win, span_frames, out_kind):
    h, t = win["head"], win["tail"]
    m = motion(f)
    e = smooth(f["energy"], 5)
    moving = e[h: t + 1][e[h: t + 1] > STILL]
    e_ref = float(np.median(moving)) if len(moving) else STILL
    best, arg = -1e9, h
    slack = (t - h + 1) - span_frames
    for a in range(h, h + slack + 1):
        z = a + span_frames - 1
        sc = 0.0
        sc += 1.0 if m[a] > STILL else 0.0
        sc += 1.0 if m[z] > STILL else 0.0
        if out_kind == "cut" and e[z] > 1.5 * e_ref and e[z] > 1.3 * e[max(h, z - 6)] and e[z] > 0.02:
            sc -= 1.5
        sc -= 0.15 * abs((a - h) - 0.4 * slack) / max(slack, 1)
        if sc > best:
            best, arg = sc, a
    return arg


def retime(f, win, span, fps_out, out_kind):
    fps = f["fps"]
    h, t = win["head"], win["tail"]
    F = int(round(span * fps_out))
    need = span * fps
    avail = t - h + 1
    info = {}
    if need <= avail + 1e-6:
        nf = min(avail, int(math.ceil(need)))
        a = pick_window(f, win, nf, out_kind)
        times = [min(a + j * fps / fps_out, t) / fps for j in range(F)]
        info.update(mode="rate 1.0", src=[a, a + nf - 1], rate=1.0)
        return times, info
    q = stillness(f, h, t)
    base = np.ones(avail) / fps
    room = max_slow(q)
    total = lambda th: float((base * (1 + th * room)).sum())
    th, uni = 1.0, 0.0
    if total(1.0) >= span:
        lo, hi = 0.0, 1.0
        for _ in range(40):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if total(mid) < span else (lo, mid)
        th = hi
    else:
        uni = span / total(1.0) - 1
    dur = base * (1 + th * room) * (1 + uni)
    T = np.concatenate([[0], np.cumsum(dur)])
    times = []
    for j in range(F):
        u = j / fps_out
        k = int(min(avail - 1, np.searchsorted(T, u, side="right") - 1))
        frac = (u - T[k]) / dur[k]
        times.append((h + k + min(frac, 0.999)) / fps)
    rates = 1 / (dur * fps)
    info.update(mode="motion-aware stretch", src=[h, t], rate_min=round(float(rates.min()), 3), rate_moving=round(float(rates[q < 0.3].min()) if (q < 0.3).any() else 1.0, 3))
    if uni > 0:
        info["shortfall_s"] = round(span - total(1.0), 2)
    return times, info


def camera(f, src, intent, carry_in, span):
    a, b = src
    cam, z = describe_camera(f, a, b)
    zh = float(np.median(np.asarray(f["zoom"])[a: a + 8]))
    keys = {"native": cam, "push": 0.0, "carry": 0.0}
    if cam == "static" and intent and "push" in intent:
        keys["push"] = 0.04
    if carry_in > 0.008 and zh < 0.3 * carry_in:
        keys["carry"] = round(min(0.03, 0.6 * carry_in + max(0.0, -zh)), 4)
    return keys


def scale_at(cam, u, span):
    p = cam["push"] * (u / span) ** 1.0 if span > 0 else 0.0
    if u < 0.4 and cam["push"]:
        p = cam["push"] * (u * u / 0.8) / span
    c = cam["carry"] * CARRY_TAU * (1 - math.exp(-u / CARRY_TAU))
    return min(MAX_SCALE, 1.0 + p + c)


def grade(shots, feats, wins):
    st = []
    for f, w in zip(feats, wins):
        sl = slice(w["head"], w["tail"] + 1)
        st.append({k: float(np.mean(f[k][sl])) for k in ("L", "a", "b", "Ls")})
    phases = {}
    for i, s in enumerate(shots):
        phases.setdefault(s.get("time"), []).append(i)
    out = []
    for i, s in enumerate(shots):
        ph = s.get("time")
        measured = classify_light(st[i]["L"])
        cap = PHASE_MAX_L.get(ph)
        mismatch = cap is not None and st[i]["L"] > cap + 4
        peers = [j for j in phases[ph] if j != i]
        refs = [j for j in peers if cap is None or st[j]["L"] <= cap + 4]
        g = {"dL": 0.0, "da": 0.0, "db": 0.0, "Lk": 1.0, "vignette": 0.0, "measured_light": measured, "declared": ph}
        tgt = {k: float(np.median([st[j][k] for j in refs + [i]])) for k in ("L", "a", "b", "Ls")}
        s_ = 0.45
        if mismatch:
            s_ = PHASE_STRENGTH[ph]
            if not refs:
                tgt["L"] = cap
        g["dL"] = float(np.clip(s_ * (tgt["L"] - st[i]["L"]), -18, 18))
        g["da"] = float(np.clip(s_ * (tgt["a"] - st[i]["a"]), -6, 6)) if refs else (2.0 if ph == "dusk" and mismatch else 0.0)
        g["db"] = float(np.clip(s_ * (tgt["b"] - st[i]["b"]), -14, 14)) if refs else (4.0 if ph == "dusk" and mismatch else 0.0)
        g["Lk"] = float(np.clip(1 + s_ * (tgt["Ls"] / max(st[i]["Ls"], 1) - 1), 0.85, 1.15))
        if ph == "night":
            g["vignette"] = 0.45 if mismatch else 0.25
        elif ph == "dusk":
            g["vignette"] = 0.3 if mismatch else 0.18
        g["mean"] = st[i]["L"]
        g["flag"] = {"kind": "time_of_day", "fix": f"declared {ph} but the clip reads as {measured} (L* {st[i]['L']:.0f}): regenerate as {ph}; the grade only softens it", "severity": 5 if ph == "night" else 3} if mismatch else None
        out.append({k: (round(v, 3) if isinstance(v, float) else v) for k, v in g.items()})
    return out


def apply_grade(rgb, g, vign=None):
    if not any(abs(g[k]) > 1e-3 for k in ("dL", "da", "db", "vignette")) and abs(g["Lk"] - 1) < 1e-3:
        return rgb
    lab = cv2.cvtColor(rgb.astype(np.float32) / 255, cv2.COLOR_RGB2Lab)
    L = lab[..., 0]
    mu = g["mean"]
    L = (L - mu) * g["Lk"] + mu + g["dL"]
    if g["vignette"] and vign is not None:
        L = L * (1 - g["vignette"] * vign)
    lab[..., 0] = np.clip(L, 0, 100)
    lab[..., 1] += g["da"]
    lab[..., 2] += g["db"]
    return np.clip(cv2.cvtColor(lab, cv2.COLOR_Lab2RGB) * 255, 0, 255).astype(np.uint8)


def vignette_mask(w, h):
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.hypot((xs - w / 2) / (w / 2), (ys - h / 2) / (h / 2)) / math.sqrt(2)
    return np.clip((r - 0.35) / 0.65, 0, 1) ** 1.6


class Interp:
    def __init__(self):
        self.dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        self.cache = {}

    def flows(self, key, a, b):
        if key not in self.cache:
            if len(self.cache) > 16:
                self.cache.pop(next(iter(self.cache)))
            ga = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
            gb = cv2.cvtColor(b, cv2.COLOR_RGB2GRAY)
            self.cache[key] = (self.dis.calc(ga, gb, None), self.dis.calc(gb, ga, None))
        return self.cache[key]

    def __call__(self, key, a, b, w):
        if w < 0.02:
            return a
        if w > 0.98:
            return b
        if np.abs(a.astype(np.int16) - b).mean() < 1.2:
            return (a.astype(np.float32) * (1 - w) + b.astype(np.float32) * w).astype(np.uint8)
        fab, fba = self.flows(key, a, b)
        w = np.float32(w)
        h, wd = a.shape[:2]
        ys, xs = np.mgrid[0:h, 0:wd].astype(np.float32)
        wa = cv2.remap(a, (xs - w * fab[..., 0]).astype(np.float32), (ys - w * fab[..., 1]).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        wb = cv2.remap(b, (xs - (1 - w) * fba[..., 0]).astype(np.float32), (ys - (1 - w) * fba[..., 1]).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return (wa.astype(np.float32) * (1 - w) + wb.astype(np.float32) * w).astype(np.uint8)


def repair_cadence(frames, f, interp):
    out = list(frames)
    for k in f.get("duplicates", []):
        if 0 < k < len(frames) - 1:
            out[k] = interp(("cad", f["clip"], k), frames[k - 1], frames[k + 1], 0.5)
    return out


def plan(shots, lines, total, beats, fps_out=24, cache=None):
    feats = [measure(s["clip"], cache) for s in shots]
    wins = [window(f) for f in feats]
    caps = [capacity(f, w) for f, w in zip(feats, wins)]
    decisions = limit([decide(i, shots[i - 1], shots[i], feats[i - 1], feats[i], wins[i - 1], wins[i], beats[i]) for i in range(1, len(shots))])
    cuts, cost = allocate(caps, decisions, lines, total, fps_out)
    dec = {d["into"]: d for d in decisions}
    grades = grade(shots, feats, wins)
    out_shots = []
    carry = 0.0
    for i, s in enumerate(shots):
        start = cuts[i] - ext(dec.get(i))
        end = cuts[i + 1] + ext(dec.get(i + 1))
        span = end - start
        times, info = retime(feats[i], wins[i], span, fps_out, dec[i + 1]["type"] if i + 1 in dec else "end")
        src = info["src"]
        cam = camera(feats[i], src, s.get("intent"), carry if dec.get(i, {}).get("type") == "cut" else 0.0, span)
        carry = float(np.median(np.asarray(feats[i]["zoom"])[max(src[0], src[1] - 8): src[1] + 1]))
        flags = []
        if "shortfall_s" in info:
            flags.append({"kind": "footage", "fix": f"{info['shortfall_s']} s short even with stretch: render 121–145 frames or add a connecting shot", "severity": 4})
        if grades[i]["flag"]:
            flags.append(grades[i]["flag"])
        line = lines[i]
        out_shots.append({"shot": i + 1, "clip": Path(s["clip"]).name, "role": s.get("role"), "start": round(start, 3), "end": round(end, 3), "cut_in": round(cuts[i], 3), "cut_out": round(cuts[i + 1], 3),
                          "line": [round(line[0], 3), round(line[0] + line[1], 3)], "window": wins[i], "capacity": caps[i], "retime": info, "camera": cam, "grade": grades[i],
                          "cadence": {"on_twos_index": feats[i]["on_twos_index"], "repaired_frames": len(feats[i]["duplicates"])}, "flags": flags, "times": [round(t, 5) for t in times]})
    for d in decisions:
        i = d["into"]
        d["cut"] = round(cuts[i], 3)
        d["offset_from_line"] = round(cuts[i] - lines[i][0], 3)
        mid = (lines[i - 1][0] + lines[i - 1][1] + lines[i][0]) / 2
        if d["type"] in ("dip", "dissolve") and abs(cuts[i] - mid) > 0.3:
            short = min((i - 1, i), key=lambda k: caps[k]["rate1"])
            d["reasons"].append(f"placed {cuts[i] - mid:+.2f} s from the pause because shot {short + 1} has only {caps[short]['rate1']:.1f} s of clean footage")
    return {"fps": fps_out, "total": total, "cost": round(cost, 3), "shots": out_shots, "boundaries": decisions}


def report(p, title):
    rows = [f"# {title}", "", f"Output {p['fps']} fps, picture {p['total']:.2f} s, allocation cost {p['cost']}.", "", "## Boundaries", "",
            "| Cut | At (s) | vs line | Transition | Sound lead / tail | Why | Flags |", "|---|---|---|---|---|---|---|"]
    for d in p["boundaries"]:
        i = d["into"]
        tr = d["type"] + (f" {d['dur']:.1f} s" if d["type"] == "dissolve" else (f" {d['out']}/{d['hold']}/{d['in']} s" if d["type"] == "dip" else ""))
        fl = "; ".join(f"{x['kind']}: {x['fix']}" for x in d["flags"]) or "–"
        rows.append(f"| {i} → {i + 1} | {d['cut']:.2f} | {d['offset_from_line']:+.2f} | {tr} | {d['j']:.1f} / {d['l']:.1f} s | {' · '.join(d['reasons'])} | {fl} |")
    rows += ["", "## Shots", "", "| Shot | Clip | On screen | Window (frames) | Used | Retime | Camera | Grade | Cadence | Flags |", "|---|---|---|---|---|---|---|---|---|---|"]
    for s in p["shots"]:
        r = s["retime"]
        rt = "1.0×" if r["mode"] == "rate 1.0" else f"stretch, slowest {r['rate_min']}× (still frames), moving ≥ {r['rate_moving']}×"
        cam = s["camera"]["native"] + (f" + digital push {s['camera']['push']:.0%}" if s["camera"]["push"] else "") + (f" + carry {s['camera']['carry']:.3f}/s" if s["camera"]["carry"] else "")
        g = s["grade"]
        gr = f"{g['declared']} (reads {g['measured_light']}): ΔL {g['dL']:+.1f}, Δb {g['db']:+.1f}" + (f", vignette {g['vignette']:.2f}" if g["vignette"] else "")
        cad = f"on twos, {s['cadence']['repaired_frames']} frames rebuilt" if s["cadence"]["repaired_frames"] else "smooth"
        fl = "; ".join(f"{x['kind']}: {x['fix']}" for x in s["flags"]) or "–"
        notes = "; ".join(s["window"]["notes"])
        rows.append(f"| {s['shot']} | {s['clip']} | {s['start']:.2f}–{s['end']:.2f} | {s['window']['head']}–{s['window']['tail']}{' (' + notes + ')' if notes else ''} | {r['src'][0]}–{r['src'][1]} | {rt} | {cam} | {gr} | {cad} | {fl} |")
    return "\n".join(rows) + "\n"
