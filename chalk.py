import csv
import json
import math
import re
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage
from scipy.signal import butter, fftconvolve, lfilter

import parallax
from styles import FONT_DIR, OFL

ROOT = Path(__file__).parent
W, H, FPS, SR = 1080, 1920, 30, 24000
CW, CH = 1188, 2112
ERASE = 0.55
CHALKDUSTER = "/System/Library/Fonts/Supplemental/Chalkduster.ttf"
DEVANAGARI = "/System/Library/Fonts/Supplemental/ITFDevanagari.ttc"
PALETTE_HUES = [27.0, 42.0, 95.0]
CHALK_SFX_GAIN = 0.035
BIBLE = ROOT / "profiles" / "characters" / "ramayana.json"
SFX_DIR = ROOT / "data" / "sfx"
SFX_LICENSES = SFX_DIR / "licenses.csv"
SFX_ALLOWED_LICENSES = ("cc0", "creative commons 0", "public domain", "sonniss gdc", "own recording", "own")
SFX_FORBIDDEN_LICENSES = ("nc", "non-commercial", "noncommercial", "sampling+", "nd")
HOOK_START = 0.72
TRANSITION_PRE = {"erase": ERASE, "black": 0.45, "whip": 0.13, "cut": 0.0, "flash": 0.0, "dust": 0.0}
TRANSITIONS = tuple(TRANSITION_PRE)
REVEALS = ("draw", "fast", "instant", "ghost")
MOVES = ("static", "push", "pull", "tilt", "truck", "shake", "dutch", "whip")
OVERLAYS = ("embers", "smoke", "petals", "dust", "godrays", "rain")


SCRIPT_FONTS = [
    ("\u0900", "\u097f", DEVANAGARI, 0),
    ("\u0980", "\u09ff", "/System/Library/Fonts/KohinoorBangla.ttc", 1),
    ("\u0a00", "\u0a7f", "/System/Library/Fonts/Supplemental/Gurmukhi Sangam MN.ttc", 1),
    ("\u0a80", "\u0aff", "/System/Library/Fonts/KohinoorGujarati.ttc", 0),
    ("\u0b80", "\u0bff", "/System/Library/Fonts/Supplemental/Tamil Sangam MN.ttc", 2),
    ("\u0c00", "\u0c7f", "/System/Library/Fonts/KohinoorTelugu.ttc", 1),
    ("\u0c80", "\u0cff", "/System/Library/Fonts/Supplemental/Kannada Sangam MN.ttc", 1),
    ("\u0d00", "\u0d7f", "/System/Library/Fonts/Supplemental/Malayalam Sangam MN.ttc", 1),
]


OFL_SCRIPT_FONTS = [
    ("ऀ", "ॿ", OFL["devanagari_serif"], 0),
    ("઀", "૿", OFL["gujarati"], 0),
    ("ఀ", "౿", OFL["telugu"], 0),
]
OFL_LATIN = OFL["title"]
FONTSET = {"name": "mac"}


def engine_version(script):
    try:
        return int(script.get("engine_version", 1) or 1)
    except (TypeError, ValueError):
        return 1


def use_fonts(version_or_name):
    name = version_or_name if isinstance(version_or_name, str) else ("ofl" if version_or_name >= 2 else "mac")
    FONTSET["name"] = name
    return name


def script_fonts():
    if FONTSET["name"] != "ofl":
        return SCRIPT_FONTS
    covered = {(lo, hi) for lo, hi, _, _ in OFL_SCRIPT_FONTS}
    return OFL_SCRIPT_FONTS + [f for f in SCRIPT_FONTS if (f[0], f[1]) not in covered]


def latin_font():
    return OFL_LATIN if FONTSET["name"] == "ofl" else CHALKDUSTER


def devanagari_font():
    return OFL["devanagari_serif"] if FONTSET["name"] == "ofl" else DEVANAGARI


def is_devanagari(text):
    return any("ऀ" <= ch <= "ॿ" for ch in text)


def font_for(text, size, latin=None):
    letters = text.replace("।", "").replace("॥", "")
    for lo, hi, path, idx in script_fonts():
        if any(lo <= ch <= hi for ch in letters):
            return ImageFont.truetype(path, int(size * 1.15), index=idx, layout_engine=ImageFont.Layout.RAQM)
    return ImageFont.truetype(latin or latin_font(), size)


def norm(w):
    return re.sub(r"[\W_]", "", w.lower())


def make_board(seed):
    rng = np.random.default_rng(seed)
    base = np.array([0.072, 0.082, 0.078], np.float32)
    low = ndimage.gaussian_filter(rng.normal(size=(CH // 16, CW // 16)), 2.5).astype(np.float32)
    low = cv2.resize(low, (CW, CH), interpolation=cv2.INTER_CUBIC)
    low /= np.abs(low).max() + 1e-6
    grain = ndimage.gaussian_filter(rng.normal(size=(CH, CW)).astype(np.float32), 0.7)
    lum = 1 + 0.22 * low + 0.06 * grain
    board = base[None, None, :] * lum[..., None]
    ghost = Image.new("L", (CW // 2, CH // 2), 0)
    d = ImageDraw.Draw(ghost)
    for _ in range(26):
        x, y = rng.uniform(-100, CW // 2), rng.uniform(-100, CH // 2)
        r = rng.uniform(60, 260)
        d.arc([x, y, x + r * 2.4, y + r], rng.uniform(0, 360), rng.uniform(0, 360) + 140, fill=255, width=int(rng.uniform(18, 50)))
    for _ in range(40):
        x, y = rng.uniform(0, CW // 2), rng.uniform(0, CH // 2)
        d.line([x, y, x + rng.uniform(-90, 90), y + rng.uniform(-30, 30)], fill=160, width=2)
    g = np.asarray(ghost.filter(ImageFilter.GaussianBlur(14)), np.float32) / 255
    g = cv2.resize(g, (CW, CH))
    board += 0.05 * g[..., None]
    yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
    r2 = ((xx - CW / 2) / (CW / 2)) ** 2 * 0.8 + ((yy - CH / 2) / (CH / 2)) ** 2
    board *= (1 - 0.32 * np.clip(r2, 0, 1.6))[..., None]
    return np.clip(board, 0, 1).astype(np.float32)


def load_bible(path=None):
    p = Path(path) if path else BIBLE
    return json.loads(p.read_text()) if p.exists() else {}


def world_hues(accent, bible=None):
    if not accent:
        return None
    if isinstance(accent, (int, float)):
        return [float(accent)]
    if isinstance(accent, str):
        worlds = (bible if bible is not None else load_bible()).get("worlds", {})
        if accent not in worlds:
            raise KeyError(f"unknown accent world '{accent}' (known: {', '.join(sorted(worlds))})")
        accent = worlds[accent]["hues"] if isinstance(worlds[accent], dict) else worlds[accent]
    hues = [float(h) % 360 for h in accent][:3]
    return hues or None


def restrict_palette(rgb, hues=None):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    hues = np.array(PALETTE_HUES if hues is None else list(hues)[:3], np.float32)
    diff = np.abs(((h[..., None] - hues[None, None, :]) + 180) % 360 - 180)
    nearest = hues[np.argmin(diff, axis=2)]
    colored = s > 0.5
    hsv[..., 0] = np.where(colored, nearest, np.where(s > 0.15, 34.0, h))
    hsv[..., 1] = np.where(colored, np.clip(s * 0.85, 0.5, 0.7), s * 0.3)
    hsv[..., 2] = np.where(colored, np.minimum(1.0, v * 1.1), np.minimum(1.0, v * 1.12))
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)


def chalk_texture(seed):
    rng = np.random.default_rng(seed)
    n = rng.uniform(0, 1, (CH, CW)).astype(np.float32)
    streak = cv2.blur(n, (9, 2))
    tex = 0.62 + 0.5 * streak
    tex[n > 0.93] *= 0.45
    return np.clip(tex, 0, 1.05)


def crop_still(img, crop):
    if not crop:
        return img
    cx, cy, wf = (list(crop) + [1.0])[:3]
    iw, ih = img.size
    cw = max(16.0, min(1.0, float(wf)) * iw)
    ch = cw * H / W
    if ch > ih:
        ch = float(ih)
        cw = ch * W / H
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    return img.crop((int(round(x0)), int(round(y0)), int(round(x0 + cw)), int(round(y0 + ch))))


def chalk_from_image(img, seed, hues=None):
    a = np.asarray(img.convert("RGB").resize((CW, CH), Image.LANCZOS)).astype(np.float32) / 255
    lum = a.max(axis=2)
    floor = ndimage.minimum_filter(lum[::4, ::4], size=11)
    floor = ndimage.gaussian_filter(floor, 5)
    floor = cv2.resize(floor, (CW, CH), interpolation=cv2.INTER_LINEAR)
    chalk = np.clip(a - floor[..., None] - 0.035, 0, 1) * 1.2
    chalk = restrict_palette(np.clip(chalk, 0, 1), hues)
    chalk *= chalk_texture(seed)[..., None]
    return np.clip(chalk, 0, 1).astype(np.float32)


def dfs(sub, y0, x0, oy, ox, seq):
    h, w = sub.shape
    grid = sub.tolist()
    vis = [[False] * w for _ in range(h)]
    stack = [(y0, x0)]
    nb = ((0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1))
    while stack:
        y, x = stack.pop()
        if vis[y][x]:
            continue
        vis[y][x] = True
        seq.append((y + oy, x + ox))
        for dy, dx in nb:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and grid[ny][nx] and not vis[ny][nx]:
                stack.append((ny, nx))


def reveal_order(chalk, mode):
    lum = chalk.max(axis=2)
    s = cv2.resize(lum, (CW // 4, CH // 4), interpolation=cv2.INTER_AREA)
    strong = s > 0.2
    weak = s > 0.03
    lab, n = ndimage.label(strong, structure=np.ones((3, 3)))
    order = np.ones(s.shape, np.float32)
    seq = []
    if n:
        objs = ndimage.find_objects(lab)
        sizes = ndimage.sum(strong, lab, range(1, n + 1))
        comps = list(range(1, n + 1))
        if mode == "reading":
            band = s.shape[0] / 14
            comps.sort(key=lambda c: (int(objs[c - 1][0].start // band), objs[c - 1][1].start))
        else:
            big = sorted([c for c in comps if sizes[c - 1] >= 14], key=lambda c: -sizes[c - 1])
            small = sorted([c for c in comps if sizes[c - 1] < 14], key=lambda c: objs[c - 1][0].start)
            comps = big + small
        for c in comps:
            sl = objs[c - 1]
            sub = lab[sl] == c
            ys, xs = np.nonzero(sub)
            k = int(np.argmin(xs if mode == "reading" else ys))
            dfs(sub, ys[k], xs[k], sl[0].start, sl[1].start, seq)
        idx = np.array(seq)
        order[idx[:, 0], idx[:, 1]] = np.arange(len(seq), dtype=np.float32) / len(seq) * 0.8
        _, (iy, ix) = ndimage.distance_transform_edt(~strong, return_indices=True)
        near = order[iy, ix]
        fill = weak & ~strong
        order[fill] = 0.8 + 0.2 * near[fill] / 0.8
        rest = ~weak
        _, (ry, rx) = ndimage.distance_transform_edt(rest, return_indices=True)
        order[rest] = order[ry, rx][rest]
    full = cv2.resize(order, (CW, CH), interpolation=cv2.INTER_LINEAR)
    pts = (np.array(seq, np.float32) * 4 + 2) if seq else np.array([[CH / 2, CW / 2]], np.float32)
    m = lum > 0.15
    ys, xs = np.nonzero(m[::8, ::8])
    com = (float(xs.mean() * 8), float(ys.mean() * 8)) if len(xs) else (CW / 2, CH / 2)
    return full, pts, com


def chalk_text(draw_fn, size, seed):
    mask = Image.new("L", size, 0)
    draw_fn(ImageDraw.Draw(mask))
    m = np.asarray(mask, np.float32) / 255
    rng = np.random.default_rng(seed)
    noise = cv2.blur(rng.uniform(0, 1, m.shape).astype(np.float32), (5, 2))
    m = m * np.clip(0.55 + 0.6 * noise, 0, 1)
    m[(rng.uniform(0, 1, m.shape) > 0.9) & (m > 0)] *= 0.4
    return m


def text_scene(sc, path, seed):
    img = np.zeros((CH, CW, 3), np.float32)
    layers = []
    if sc["kind"] == "verse":
        lines = sc["devanagari"]
        dev = font_for("".join(lines), 80)
        small = font_for(sc["source"], 40)
        y0 = 560
        for i, line in enumerate(lines):
            col = (0.96, 0.66, 0.32) if i < 2 else (0.95, 0.94, 0.9)

            def fn(d, line=line, y=y0 + i * 168):
                tw = d.textlength(line, font=dev)
                d.text(((CW - tw) / 2, y), line, font=dev, fill=255)

            layers.append((fn, col))

        def orn(d):
            y = y0 + 4 * 168 + 40
            d.line([CW / 2 - 300, y, CW / 2 - 40, y], fill=255, width=4)
            d.line([CW / 2 + 40, y, CW / 2 + 300, y], fill=255, width=4)
            d.ellipse([CW / 2 - 14, y - 14, CW / 2 + 14, y + 14], outline=255, width=4)
            tw = d.textlength(sc["source"], font=small)
            d.text(((CW - tw) / 2, y + 40), sc["source"], font=small, fill=255)

        layers.append((orn, (0.86, 0.74, 0.44)))
    elif sc["kind"] == "shloka":
        dev = font_for(sc["from"] + sc["to"], 183)
        def word(text, y, label, ly):
            lab = font_for(label, 62)

            def fn(d):
                tw = d.textlength(text, font=dev)
                d.text(((CW - tw) / 2, y), text, font=dev, fill=255)
            def fl(d):
                tw = d.textlength(label, font=lab)
                d.text(((CW - tw) / 2, ly), label, font=lab, fill=255)
            return fn, fl

        a, al = word(sc["from"], 330, sc["from_label"], 640)
        b, bl = word(sc["to"], 960, sc["to_label"], 1270)

        def arrow(d):
            x = CW / 2
            d.line([x, 760, x, 920], fill=255, width=8)
            d.line([x - 40, 870, x, 925, x + 40, 870], fill=255, width=8)

        layers += [(a, (0.95, 0.94, 0.9)), (al, (0.86, 0.74, 0.44)), (arrow, (0.95, 0.94, 0.9)), (b, (0.96, 0.66, 0.32)), (bl, (0.86, 0.74, 0.44))]
    for k, (fn, col) in enumerate(layers):
        m = chalk_text(fn, (CW, CH), seed + k)
        img = np.maximum(img, m[..., None] * np.array(col, np.float32))
    Image.fromarray((img * 255).astype(np.uint8)).save(path)


def scene_transition(script, i):
    if i == 0:
        return None
    tr = script["scenes"][i].get("transition") or "erase"
    if tr not in TRANSITION_PRE:
        raise ValueError(f"scene {i + 1}: unknown transition '{tr}' (use {', '.join(TRANSITIONS)})")
    return tr


def scene_reveal(script, i):
    sc = script["scenes"][i]
    rv = sc.get("reveal")
    if rv and rv not in REVEALS:
        raise ValueError(f"scene {i + 1}: unknown reveal '{rv}' (use {', '.join(REVEALS)})")
    if rv:
        return rv
    if engine_version(script) < 2 or sc.get("kind") in ("verse", "shloka"):
        return "draw"
    return "fast"


def plan(script, timings, total):
    ev = engine_version(script)
    trans = [scene_transition(script, i) for i in range(len(timings))]
    out = []
    for i, (start, dur) in enumerate(timings):
        sc = script["scenes"][i]
        vs = 0.0 if i == 0 else start - TRANSITION_PRE[trans[i]]
        ve = timings[i + 1][0] - TRANSITION_PRE[trans[i + 1]] if i + 1 < len(timings) else total
        ds = 0.0 if i == 0 else start
        avail = ve - ds
        rv = scene_reveal(script, i)
        p0 = 0.0
        if i == 0 and ev >= 2:
            if rv == "instant":
                draw, p0 = 0.0, 1.0
            else:
                rv = "hybrid" if not sc.get("reveal") or rv == "ghost" else rv
                draw, p0 = {"draw": 1.6, "fast": 0.6}.get(rv, 0.8), HOOK_START
        elif i == 0:
            draw = 1.6
        elif rv == "instant":
            draw, p0 = 0.0, 1.0
        elif rv == "fast":
            draw = min(max(0.2 * avail, 0.5), 0.8)
        elif rv == "ghost":
            draw = 0.4
        elif sc.get("kind") in ("verse", "shloka"):
            draw = min(max(0.7 * avail, 2.6), 5.5)
        else:
            draw = min(max(0.5 * avail, 2.0), 3.6)
        out.append({"vs": vs, "ve": ve, "ds": ds, "de": ds + draw, "p0": p0, "reveal": rv, "transition": trans[i] or "start"})
    return out


def ease(x):
    return 1 - (1 - x) ** 2.2


def smooth(x):
    return x * x * (3 - 2 * x)


def chalk_stick():
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    body = Image.new("RGBA", (34, 120), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    bd.rounded_rectangle([0, 0, 33, 119], radius=12, fill=(238, 234, 222, 255))
    for x in range(34):
        shade = int(30 * abs(x - 12) / 22)
        bd.line([x, 4, x, 115], fill=(238 - shade, 234 - shade, 222 - shade, 255))
    shadow = Image.new("RGBA", (34, 120), (0, 0, 0, 110))
    shadow = shadow.rotate(-35, expand=True).filter(ImageFilter.GaussianBlur(5))
    body = body.rotate(-35, expand=True)
    im.alpha_composite(shadow, (14, 14))
    im.alpha_composite(body, (0, 0))
    return im


class Particles:
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.p = []
        self.motes = [
            [self.rng.uniform(0, W), self.rng.uniform(0, H), self.rng.uniform(-6, 6), self.rng.uniform(-14, -3), self.rng.uniform(1, 3.5), self.rng.uniform(25, 70)]
            for _ in range(70)
        ]

    def emit(self, x, y, n, spread=1.0):
        for _ in range(n):
            self.p.append([x + self.rng.normal(0, 6 * spread), y + self.rng.normal(0, 4), self.rng.normal(0, 25 * spread), self.rng.uniform(10, 60), self.rng.uniform(0.5, 1.3), self.rng.uniform(1.2, 3.2)])

    def draw(self, frame, dt):
        ov = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for m in self.motes:
            m[0] = (m[0] + m[2] * dt) % W
            m[1] = (m[1] + m[3] * dt) % H
            r = m[4]
            d.ellipse([m[0] - r, m[1] - r, m[0] + r, m[1] + r], fill=(235, 232, 220, int(m[5])))
        alive = []
        for q in self.p:
            q[0] += q[2] * dt
            q[1] += q[3] * dt
            q[3] += 160 * dt
            q[4] -= dt
            if q[4] > 0:
                a = int(200 * min(1, q[4]))
                r = q[5]
                d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=(240, 238, 228, a))
                alive.append(q)
        self.p = alive
        frame.paste(ov, (0, 0), ov)


class Overlays:
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed + 991)
        self.p = {k: [] for k in OVERLAYS}
        self.t = 0.0

    def spawn(self, kind, n):
        r = self.rng
        hw, hh = W // 2, H // 2
        for _ in range(n):
            if kind == "embers":
                self.p[kind].append([r.uniform(0, hw), hh + r.uniform(0, 40), r.uniform(-8, 8), r.uniform(-90, -40), r.uniform(2.5, 5.0), r.uniform(0.8, 2.0), r.uniform(0, 6.28)])
            elif kind == "smoke":
                self.p[kind].append([r.uniform(0, hw), hh + r.uniform(20, 120), r.uniform(-6, 6), r.uniform(-28, -14), r.uniform(5.0, 8.0), r.uniform(28, 60), r.uniform(0, 6.28)])
            elif kind == "petals":
                self.p[kind].append([r.uniform(0, hw), r.uniform(-60, -10), r.uniform(-12, 12), r.uniform(30, 60), r.uniform(6.0, 10.0), r.uniform(3.5, 6.0), r.uniform(0, 6.28)])
            elif kind == "dust":
                self.p[kind].append([r.uniform(-60, 0), r.uniform(0, hh), r.uniform(160, 320), r.uniform(-15, 15), r.uniform(1.5, 3.0), r.uniform(1.0, 3.2), r.uniform(0, 6.28)])
            elif kind == "rain":
                self.p[kind].append([r.uniform(0, hw + 120), r.uniform(-80, -10), -90.0, r.uniform(700, 900), r.uniform(1.2, 1.6), r.uniform(18, 30), 0.0])

    def draw(self, frame, kinds, dt, level=1.0):
        self.t += dt
        rates = {"embers": 14, "smoke": 2.5, "petals": 3.5, "dust": 40, "rain": 120}
        for k in kinds:
            if k in rates:
                n = self.rng.poisson(rates[k] * dt * level)
                self.spawn(k, int(n))
        if not any(self.p.values()) and "godrays" not in kinds:
            return frame
        hw, hh = W // 2, H // 2
        ov = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
        soft = Image.new("RGBA", (hw, hh), (0, 0, 0, 0))
        d, ds = ImageDraw.Draw(ov), ImageDraw.Draw(soft)
        if "godrays" in kinds:
            sweep = math.sin(self.t * 0.35) * 40
            for j, (x0, wdt) in enumerate([(120, 50), (220, 80), (330, 40), (420, 65)]):
                a = int((22 + 10 * math.sin(self.t * 0.9 + j * 1.7)) * level)
                x = x0 + sweep
                ds.polygon([(x - wdt * 0.2, -10), (x + wdt * 0.2, -10), (x + wdt + 140, hh), (x - 40, hh)], fill=(238, 228, 190, max(0, a)))
        for k, items in self.p.items():
            alive = []
            for q in items:
                q[4] -= dt
                q[6] += dt
                if q[4] <= 0 or q[0] < -100 or q[0] > hw + 140 or q[1] < -120 or q[1] > hh + 140:
                    continue
                if k == "embers":
                    q[0] += (q[2] + 12 * math.sin(q[6] * 3)) * dt
                    q[1] += q[3] * dt
                    fl = 0.6 + 0.4 * math.sin(q[6] * 11)
                    a = int(210 * min(1, q[4] / 1.2) * fl * level)
                    r = q[5]
                    d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=(246, 168, 82, a))
                elif k == "smoke":
                    q[0] += (q[2] + 6 * math.sin(q[6] * 0.7)) * dt
                    q[1] += q[3] * dt
                    q[5] += 6 * dt
                    a = int(26 * min(1, q[4] / 2.0) * min(1, q[6] / 1.5) * level)
                    r = q[5]
                    ds.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=(200, 198, 190, a))
                elif k == "petals":
                    q[0] += (q[2] + 18 * math.sin(q[6] * 1.6)) * dt
                    q[1] += q[3] * dt
                    a = int(200 * min(1, q[4] / 1.5) * level)
                    r = q[5]
                    ang = q[6] * 2.2
                    pts = [(q[0] + r * math.cos(ang + u) * (1.0 if u in (0, math.pi) else 0.45), q[1] + r * math.sin(ang + u) * (1.0 if u in (0, math.pi) else 0.45)) for u in (0, math.pi / 2, math.pi, 3 * math.pi / 2)]
                    d.polygon(pts, fill=(246, 168, 82, a) if int(q[6] * 100) % 2 else (226, 190, 112, a))
                elif k == "dust":
                    q[0] += q[2] * dt
                    q[1] += (q[3] + 10 * math.sin(q[6] * 2)) * dt
                    a = int(120 * min(1, q[4] / 1.0) * level)
                    r = q[5]
                    d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=(196, 184, 160, a))
                    if r > 2.6:
                        ds.ellipse([q[0] - 18, q[1] - 10, q[0] + 18, q[1] + 10], fill=(190, 180, 160, int(a * 0.25)))
                elif k == "rain":
                    x1, y1 = q[0] + q[2] * 0.03, q[1] + q[3] * 0.03
                    q[0] += q[2] * dt
                    q[1] += q[3] * dt
                    d.line([q[0], q[1], x1, y1], fill=(225, 228, 230, int(70 * level)), width=1)
                alive.append(q)
            self.p[k] = alive
        soft = soft.filter(ImageFilter.GaussianBlur(10))
        ov = Image.alpha_composite(soft, ov).resize((W, H), Image.BILINEAR)
        frame.paste(ov, (0, 0), ov)
        return frame


def load_mask(path, crop=None, sigma=6):
    path = Path(path)
    if not path.exists():
        return None
    m = Image.open(path).convert("L")
    m = crop_still(m, crop)
    m = np.asarray(m.resize((CW, CH), Image.BILINEAR), np.float32) / 255
    return cv2.GaussianBlur(m, (0, 0), sigma)


def alive_maps(mask):
    ys, xs = np.nonzero(mask > 0.5)
    if len(ys) < 500:
        return None
    yt, yb = float(ys.min()), float(ys.max())
    yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
    hf = np.clip((yb - yy) / max(1.0, yb - yt), 0, 1)
    return {"mask": mask[..., None], "xx": xx, "yy": yy, "yb": yb, "hf2": hf ** 2}


def alive(layer, am, t, phase=0.0):
    sy = 1 + 0.0075 * math.sin(2 * math.pi * 0.25 * t + phase)
    sway = 3.5 * math.sin(2 * math.pi * 0.17 * t + phase * 1.3)
    mx = am["xx"] - sway * am["hf2"]
    my = am["yb"] + (am["yy"] - am["yb"]) / sy
    moved = cv2.remap(layer, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return layer * (1 - am["mask"]) + moved * am["mask"]


def cam_matrix(z, fx, fy, jx=0.0, jy=0.0, rot=0.0):
    if not rot:
        return np.float32([[z, 0, W / 2 - z * fx + jx], [0, z, H / 2 - z * fy + jy]])
    a = math.radians(rot)
    c, sn = math.cos(a) * z, math.sin(a) * z
    return np.float32([[c, -sn, W / 2 + jx - c * fx + sn * fy], [sn, c, H / 2 + jy - sn * fx - c * fy]])


def parse_move(sc, i=0):
    mv = sc.get("move")
    if not mv:
        return None
    mv = {"type": mv} if isinstance(mv, str) else dict(mv)
    if mv.get("type") not in MOVES:
        raise ValueError(f"scene {i + 1}: unknown move '{mv.get('type')}' (use {', '.join(MOVES)})")
    return mv


def clamp_focus(z, fx, fy):
    hx = (CW - W / z) / 2
    hy = (CH - H / z) / 2
    return min(max(fx, CW / 2 - hx), CW / 2 + hx), min(max(fy, CH / 2 - hy), CH / 2 + hy)


def move_camera(mv, com, prev_cam):
    t = mv["type"]
    f = (CW / 2 + (com[0] - CW / 2) * 0.5, CH / 2 + (com[1] - CH / 2) * 0.35)
    defaults = {"static": [1.04, 1.04], "push": [1.0, 1.15], "pull": [1.15, 1.0], "tilt": [1.15, 1.15], "truck": [1.15, 1.15], "shake": [1.06, 1.09], "dutch": [1.1, 1.13], "whip": [1.12, 1.12]}
    za, zb = [min(1.2, max(1.0, float(v))) for v in (list(mv.get("z", defaults[t])) * 2)[:2]]
    fa, fb = f, f
    if t == "tilt":
        hy = (CH - H / max(za, zb)) / 2
        top, bot = (f[0], CH / 2 - hy), (f[0], CH / 2 + hy)
        fa, fb = (bot, top) if mv.get("dir") == "up" else (top, bot)
    elif t in ("truck", "whip"):
        hx = (CW - W / max(za, zb)) / 2
        left, right = (CW / 2 - hx, f[1]), (CW / 2 + hx, f[1])
        fa, fb = (right, left) if mv.get("dir") == "left" else (left, right)
        if t == "whip":
            fb = (CW / 2 + (fb[0] - CW / 2) * 0.2, f[1])
    fa, fb = clamp_focus(za, *fa), clamp_focus(zb, *fb)
    deg = float(mv.get("deg", 6.0)) if t == "dutch" else 0.0
    return ((za, fa[0], fa[1]), (zb, fb[0], fb[1])), (deg, deg)


def cam_at(s, p, t):
    span = max(0.5, p["ve"] - p["ds"])
    x = min(1.0, max(0.0, (t - p["ds"]) / span))
    if s["move"] and s["move"]["type"] == "whip":
        u = smooth(min(1.0, max(0.0, (t - p["ds"]) / 0.35)))
    elif s["move"] and s["move"].get("ease") == "linear":
        u = x
    else:
        u = smooth(x)
    (z0, fx0, fy0), (z1, fx1, fy1) = s["cam"]
    return z0 + (z1 - z0) * u, fx0 + (fx1 - fx0) * u, fy0 + (fy1 - fy0) * u


def scene_planes(script, sc, i, chalk, masks, depths):
    mode = parallax.scene_mode(script, sc, i)
    if mode == "off":
        return None
    pm = load_mask(masks[i], sc.get("crop"), 1.0) if masks and masks[i] else None
    pd = parallax.read_map(depths[i], (CW, CH), sc.get("crop"), crop_still, 2.0) if mode == "depth" and depths and depths[i] else None
    return parallax.build_planes(chalk, pm, pd)


def whip_blur(comp, strength):
    k = int(strength * 90)
    return cv2.blur(comp, (k, 1)) if k > 2 else comp


def title_layer(text, seed):
    font = font_for(text, 74)
    tmp = ImageDraw.Draw(Image.new("L", (10, 10)))
    tw = int(tmp.textlength(text, font=font)) + 40
    if tw > W - 80:
        font = font_for(text, int(74 * (W - 80) / tw))
        tw = int(tmp.textlength(text, font=font)) + 40
    pad = 40
    m = chalk_text(lambda d: d.text((20 + pad, 10 + pad), text, font=font, fill=255), (tw + 2 * pad, 130 + 2 * pad), seed)
    solid = Image.new("L", (tw + 2 * pad, 130 + 2 * pad), 0)
    ImageDraw.Draw(solid).text((20 + pad, 10 + pad), text, font=font, fill=255)
    halo = np.asarray(solid.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(16)), np.float32) / 255
    a_text = m
    a_halo = np.clip(halo * 1.6, 0, 1) * 0.78
    alpha = a_text + a_halo * (1 - a_text)
    col = np.array([226, 190, 112], np.float32)
    rgb = col * (a_text / np.maximum(alpha, 1e-4))[..., None] + np.array([8, 9, 9], np.float32) * (a_halo * (1 - a_text) / np.maximum(alpha, 1e-4))[..., None]
    rgba = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def scene_overlays(sc):
    ov = sc.get("overlay") or []
    ov = [ov] if isinstance(ov, str) else list(ov)
    bad = [o for o in ov if o not in OVERLAYS]
    if bad:
        raise ValueError(f"unknown overlay {bad} (use {', '.join(OVERLAYS)})")
    return ov


def render(script, st, timings, total, raw_paths, writer, captioner, groups, seed, log, masks=None, depths=None):
    pl = plan(script, timings, total)
    ev = engine_version(script)
    board = make_board(seed)
    rng = np.random.default_rng(seed)
    bible = None
    scenes = []
    prev_cam = (1.0, CW / 2, CH / 2)
    for i, sc in enumerate(script["scenes"]):
        img = crop_still(Image.open(raw_paths[i]), sc.get("crop"))
        hues = None
        if sc.get("accent"):
            bible = load_bible() if bible is None else bible
            hues = world_hues(sc["accent"], bible)
        chalk = chalk_from_image(img, seed + i, hues)
        mode = "reading" if sc.get("kind") in ("verse", "shloka") else "size"
        order, pts, com = reveal_order(chalk, mode)
        small = cv2.resize(chalk, (CW // 4, CH // 4), interpolation=cv2.INTER_AREA)
        ghost = cv2.resize(cv2.GaussianBlur(small, (0, 0), 3), (CW, CH)) * 0.11
        if sc.get("kind") in ("verse", "shloka"):
            z1 = 1.03
            f1 = (CW / 2, CH / 2)
        else:
            z1 = float(rng.uniform(1.04, 1.1)) if i % 2 == 0 else float(rng.uniform(1.0, 1.03))
            f1 = (CW / 2 + (com[0] - CW / 2) * 0.5, CH / 2 + (com[1] - CH / 2) * 0.35)
        f1 = clamp_focus(z1, *f1)
        cam = (prev_cam, (z1, f1[0], f1[1]))
        rot = (0.0, 0.0)
        mv = parse_move(sc, i)
        if mv:
            cam, rot = move_camera(mv, com, prev_cam)
        if sc.get("angle") == "dutch" and not any(rot):
            rot = (6.0, 6.0)
        prev_cam = cam[1]
        title = title_layer(sc["emphasis"].upper(), seed + 100 + i) if sc.get("emphasis") else None
        am = None
        if ev >= 2 and masks and masks[i] and sc.get("alive", True):
            m = load_mask(masks[i], sc.get("crop"))
            am = alive_maps(m) if parallax.usable_mask(m) else None
        scenes.append({"chalk": chalk, "order": order, "pts": pts, "com": com, "ghost": ghost.astype(np.float32), "cam": cam, "rot": rot, "move": mv, "title": title, "alive": am, "overlay": scene_overlays(sc)})
        planes = scene_planes(script, sc, i, chalk, masks, depths) if ev >= 2 else None
        if planes is not None:
            pdir = {"left": 1.0, "right": -1.0}.get((mv or {}).get("dir"), parallax.default_direction(i))
            scenes[-1].update(planes=planes, pf0=cam_at(scenes[-1], pl[i], pl[i]["de"])[1:], pamount=parallax.drift_amount(sc), pdir=pdir)
            log(f"render: scene {i + 1} parallax {parallax.scene_mode(script, sc, i)} ({len(planes['alphas']) + 1} planes)")
        log(f"render: prepared scene {i + 1}/{len(script['scenes'])} ({len(pts)} stroke points)")
    stick = chalk_stick()
    parts = Particles(seed)
    fx_layer = Overlays(seed) if any(s["overlay"] for s in scenes) else None
    field = ndimage.gaussian_filter(rng.normal(size=(CH // 4, CW // 4)), sigma=(2.5, 22)).astype(np.float32)
    field = (np.argsort(np.argsort(field.ravel())).reshape(field.shape) / field.size).astype(np.float32)
    nframes = int(total * FPS)
    tip = None
    puffed = set()
    log(f"render: {nframes} frames ({total:.1f}s)")
    for f in range(nframes):
        t = f / FPS
        i = next((k for k, p in enumerate(pl) if p["vs"] <= t < p["ve"]), len(pl) - 1)
        p, s = pl[i], scenes[i]
        jx, jy = 2.5 * math.sin(t * 0.7), 2.0 * math.sin(t * 0.53 + 1)
        tip_pos = None
        rot = 0.0
        tr = p["transition"]
        whip = 0.0
        fgain = 1.0
        if i > 0 and t < p["ds"]:
            q = (t - p["vs"]) / max(1e-3, p["ds"] - p["vs"])
            ps = scenes[i - 1]
            z, fx, fy = ps["cam"][1]
            rot = ps["rot"][1]
            if tr == "erase":
                q = (t - p["vs"]) / ERASE
                erased = np.clip((q * 1.2 - field) / 0.2, 0, 1)
                erased = cv2.resize(erased, (CW, CH), interpolation=cv2.INTER_LINEAR)[..., None]
                layer = ps["chalk"] * (1 - erased) + ps["ghost"] * erased
                fgain = 1 - erased
                if i > 1:
                    layer = np.maximum(layer, scenes[i - 2]["ghost"] * 0.5)
                for _ in range(2):
                    parts.emit(float(rng.uniform(80, W - 80)), float(rng.uniform(200, H - 300)), 2, 2.0)
            else:
                layer = ps["chalk"]
                if tr == "whip":
                    whip = q
                    jx -= 160 * q * q
        else:
            dp = (t - p["ds"]) / max(0.01, p["de"] - p["ds"])
            prog = p["p0"] + (1 - p["p0"]) * ease(min(1.0, max(0.0, dp)))
            if prog < 1 and p["reveal"] == "ghost" and i > 0:
                a = smooth(min(1.0, max(0.0, dp)))
                base = scenes[i - 1]["ghost"] if tr == "erase" else scenes[i - 1]["chalk"] * 0.6
                layer = base * (1 - a) + s["chalk"] * a
            elif prog < 1:
                vis = np.clip((prog * 1.01 - s["order"]) / 0.012, 0, 1)[..., None]
                layer = s["chalk"] * vis
            else:
                layer = s["chalk"]
            if s["alive"] is not None:
                layer = alive(layer, s["alive"], t, i * 0.9)
            if i > 0 and tr == "erase" and p["reveal"] != "ghost":
                fade = max(0.0, 1 - (t - p["ds"]) / 2.5)
                layer = np.maximum(layer, scenes[i - 1]["ghost"] * (0.35 + 0.65 * fade))
            span = max(0.5, p["ve"] - p["ds"])
            if s["move"] and s["move"]["type"] == "whip":
                u = smooth(min(1.0, max(0.0, (t - p["ds"]) / 0.35)))
            elif s["move"] and s["move"].get("ease") == "linear":
                u = min(1.0, max(0.0, (t - p["ds"]) / span))
            else:
                u = smooth(min(1.0, max(0.0, (t - p["ds"]) / span)))
            (z0, fx0, fy0), (z1, fx1, fy1) = s["cam"]
            z, fx, fy = z0 + (z1 - z0) * u, fx0 + (fx1 - fx0) * u, fy0 + (fy1 - fy0) * u
            rot = s["rot"][0] + (s["rot"][1] - s["rot"][0]) * u
            age = t - p["ds"]
            if s["move"] and s["move"]["type"] == "shake" and age < 0.5:
                amp = float(s["move"].get("amp", 8.0)) * math.exp(-age / 0.18)
                jx += amp * (0.6 * math.sin(t * 97.0 + i) + 0.4 * math.sin(t * 61.3 + 2 * i))
                jy += amp * (0.6 * math.sin(t * 89.0 + 3 * i) + 0.4 * math.sin(t * 53.1 + i))
            if tr == "whip" and age < TRANSITION_PRE["whip"]:
                whip = 1 - age / TRANSITION_PRE["whip"]
                jx += 160 * whip * whip
            if s["move"] and s["move"]["type"] == "whip" and age < 0.3:
                whip = max(whip, 1 - age / 0.3)
            if (p["reveal"] == "instant" or tr == "dust") and i not in puffed and i > 0:
                puffed.add(i)
                cx, cy = (s["com"][0] - fx) * z + W / 2, (s["com"][1] - fy) * z + H / 2
                for _ in range(14):
                    parts.emit(float(cx + rng.normal(0, 160)), float(cy + rng.normal(0, 220)), 5, 3.0)
            if prog < 1 and p["reveal"] != "ghost":
                n = len(s["pts"])
                k = prog / 0.8 if prog < 0.8 else (prog - 0.8) / 0.2
                py, px = s["pts"][min(n - 1, int(k * (n - 1)))]
                tip_pos = ((px - fx) * z + W / 2 + jx, (py - fy) * z + H / 2 + jy)
        M = cam_matrix(z, fx, fy, jx, jy, rot)
        owner = i - 1 if i > 0 and t < p["ds"] else i
        so = scenes[owner]
        up = 0.0
        if so.get("planes") is not None:
            up = 1.0 if owner != i else parallax.progress(t, p["de"], p["ve"])
        comp = cv2.warpAffine(board, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if up > 0:
            mats = [cam_matrix(*c) for c in parallax.plane_cams((z, fx, fy, jx, jy, rot), so["pf0"], so["planes"], up, so["pamount"], so["pdir"])]
            comp += parallax.composite(layer, so["planes"], mats, (W, H), fgain)
        else:
            comp += cv2.warpAffine(layer, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        if whip > 0:
            comp = whip_blur(comp, whip)
        if i > 0 and tr == "black":
            if t < p["ds"]:
                comp *= 1 - (t - p["vs"]) / max(1e-3, p["ds"] - p["vs"])
            elif t - p["ds"] < 0.25:
                comp *= (t - p["ds"]) / 0.25
        if i > 0 and tr == "flash" and 0 <= t - p["ds"] < 0.2:
            a = 1 - (t - p["ds"]) / 0.2
            comp = comp * (1 - a) + np.array([0.95, 0.94, 0.9], np.float32) * a
        frame = Image.fromarray((np.clip(comp, 0, 1) * 255).astype(np.uint8))
        if tip_pos is not None:
            tip = tip_pos if tip is None else (tip[0] * 0.45 + tip_pos[0] * 0.55, tip[1] * 0.45 + tip_pos[1] * 0.55)
            parts.emit(tip[0], tip[1], 1)
        else:
            tip = None
        parts.draw(frame, 1 / FPS)
        if fx_layer is not None:
            level = max(0.0, min(1.0, (t - p["vs"]) / 0.4, (p["ve"] - t) / 0.4)) if s["overlay"] else 0.0
            fx_layer.draw(frame, s["overlay"] if level > 0 else [], 1 / FPS, max(level, 0.0))
        if tip is not None:
            frame.paste(stick, (int(tip[0]) - 6, int(tip[1]) - 4), stick)
        if s["title"] is not None and t >= p["ds"]:
            age = t - p["ds"]
            reveal = min(1.0, age / 0.8)
            tl = s["title"]
            cw = int(tl.width * reveal)
            if cw > 0:
                frame.paste(tl.crop((0, 0, cw, tl.height)), ((W - tl.width) // 2, int(H * 0.055) - 40), tl.crop((0, 0, cw, tl.height)))
        group = next((g for g in groups if g["start"] <= t < g["end"] + 0.1), None)
        captioner.draw(frame, group, t, "", 99)
        writer.stdin.write(frame.tobytes())
        if f % (FPS * 10) == 0:
            log(f"render: {t:.0f}s / {total:.0f}s")
    return pl


def bandnoise(n, lo, hi, rng):
    b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band")
    return lfilter(b, a, rng.normal(size=n)).astype(np.float32)


def lownoise(n, hi, rng):
    b, a = butter(2, hi / (SR / 2), "low")
    return lfilter(b, a, rng.normal(size=n)).astype(np.float32)


def reverb(x, secs, mix, rng):
    n = int(secs * SR)
    ir = rng.normal(size=n) * np.exp(-np.linspace(0, 7, n))
    ir /= np.sqrt((ir ** 2).sum())
    wet = fftconvolve(x, ir)[: len(x)]
    return (x * (1 - mix) + wet * mix).astype(np.float32)


def tanpura_note(f, dur, rng):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    c = 3 + 11 * (1 - np.exp(-t / 1.4))
    for k in range(1, 25):
        amp = k ** -0.75 * np.exp(-t / (3.8 / (1 + 0.07 * k)))
        boost = 1 + 1.5 * np.exp(-((k - c) ** 2) / 5)
        out += amp * boost * np.sin(2 * np.pi * k * f * (1 + rng.normal(0, 0.0003)) * t + rng.uniform(0, 6.28))
    return (out * np.minimum(1, t / 0.008)).astype(np.float32)


def flute_phrase(notes, sa, rng):
    segs = []
    prev = None
    for semi, dur in notes:
        n = int(dur * SR)
        target = sa * 2 ** (semi / 12)
        f = np.full(n, target)
        if prev is not None:
            g = min(n, int(0.09 * SR))
            f[:g] = prev + (target - prev) * np.linspace(0, 1, g) ** 0.6
        segs.append(f)
        prev = target
    f = np.concatenate(segs)
    t = np.arange(len(f)) / SR
    vib = 1 + 0.005 * np.sin(2 * np.pi * 5.1 * t) * np.minimum(1, t / 0.6)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    tone = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
    env = np.minimum(1, t / 0.15) * np.minimum(1, (t[-1] - t) / 0.5)
    breath = bandnoise(len(f), 900, 4000, rng) * 0.05
    return ((tone + breath) * env).astype(np.float32)


def music(total, timings, script, seed):
    rng = np.random.default_rng(seed)
    n = int(total * SR) + SR
    out = np.zeros(n, np.float32)
    sa = 146.83
    strings = [sa * 0.75, sa, sa, sa * 0.5]
    notes = [tanpura_note(f, 4.5, rng) for f in strings]
    t, k = 0.0, 0
    while t < total:
        s0 = int(t * SR)
        nt = notes[k % 4]
        e = min(n, s0 + len(nt))
        out[s0:e] += 0.05 * nt[: e - s0]
        t += 0.95 if k % 4 != 3 else 1.5
        k += 1
    phrases = {
        "intro": [(7, 1.2), (8, 0.6), (7, 0.8), (5, 0.6), (3, 1.6)],
        "calm": [(3, 0.6), (5, 0.6), (3, 0.5), (1, 0.9), (0, 1.9)],
        "love": [(12, 0.8), (10, 0.5), (8, 0.6), (7, 1.4)],
        "grief": [(1, 1.6), (0, 0.6), (-2, 0.8), (0, 2.2)],
        "rise": [(7, 0.8), (8, 0.6), (10, 0.6), (12, 1.7), (10, 0.5), (8, 0.6), (7, 2.2)],
    }
    ev = engine_version(script)
    flute = np.zeros(n, np.float32)
    for i, sc in enumerate(script["scenes"]):
        name = sc.get("melody")
        if name:
            ph = flute_phrase(phrases[name], sa * 2, rng)
            at = timings[i][0] + timings[i][1] if ev >= 2 and i == 0 else timings[i][0] - 0.3
            s0 = int(max(0, at) * SR)
            e = min(n, s0 + len(ph))
            flute[s0:e] += 0.075 * ph[: e - s0]
        mu = music_field(sc)
        for key in [mu.get("leitmotif"), "unresolved" if mu.get("cue") == "unresolved" else None]:
            if not key:
                continue
            if key not in LEITMOTIFS:
                raise ValueError(f"scene {i + 1}: unknown leitmotif '{key}' (use {', '.join(LEITMOTIFS)})")
            ph = flute_phrase(LEITMOTIFS[key], sa if key == "lanka" else sa * 2, rng)
            s0 = int(max(0, timings[i][0] - 0.3) * SR)
            e = min(n, s0 + len(ph))
            flute[s0:e] += 0.075 * ph[: e - s0]
            if key == "sages":
                b = sfx_bell(rng) * 0.6
                e = min(n, s0 + len(b))
                out[s0:e] += b[: e - s0]
    out += reverb(flute, 2.2, 0.35, rng)
    sw = np.zeros(n, np.float32)
    for i, sc in enumerate(script["scenes"]):
        if sc.get("swell") or music_field(sc).get("cue") == "swell":
            s0 = int(timings[i][0] * SR)
            e = min(n, int((timings[i][0] + timings[i][1] + 1.2) * SR))
            tt = np.arange(e - s0) / SR
            env = np.minimum(1, tt / 1.2) * np.minimum(1, (tt[-1] - tt) / 1.0)
            sw[s0:e] += 0.05 * env * (np.sin(2 * np.pi * sa / 2 * tt) + 0.5 * np.sin(2 * np.pi * sa * 0.75 * tt))
    out += sw
    for i, sc in enumerate(script["scenes"]):
        if music_field(sc).get("cue") == "drop":
            tt = np.arange(n) / SR
            a, b = timings[i][0] - 0.45, timings[i][0] + 0.05
            dip = np.clip(np.maximum((a - tt) / 0.08, (tt - b) / 0.3), 0, 1)
            out *= dip.astype(np.float32)
    return out[: int(total * SR)]


LEITMOTIFS = {
    "rama": [(0, 0.45), (2, 0.45), (3, 0.45), (7, 1.2), (3, 0.4), (2, 0.4), (0, 1.4)],
    "sages": [(7, 1.4), (5, 0.6), (7, 2.0)],
    "lanka": [(8, 0.8), (7, 0.6), (5, 0.6), (3, 0.8), (1, 1.8)],
    "unresolved": [(5, 0.6), (3, 0.6), (2, 1.8)],
}


def music_field(sc):
    mu = sc.get("music") or {}
    return {"cue": mu} if isinstance(mu, str) else mu


def sfx_chalk(dur, rng):
    n = int(dur * SR)
    noise = bandnoise(n, 1800, 7000, rng)
    env = np.zeros(n, np.float32)
    t = 0.0
    while t < dur:
        L = rng.uniform(0.08, 0.3)
        s0, e = int(t * SR), min(n, int((t + L) * SR))
        seg = np.arange(e - s0) / SR
        env[s0:e] = np.sin(np.pi * seg / L) ** 0.5 * rng.uniform(0.5, 1)
        t += L + rng.uniform(0.02, 0.14)
    grit = 0.6 + 0.4 * np.sign(np.sin(2 * np.pi * rng.uniform(35, 60) * np.arange(n) / SR))
    return noise * env * grit * CHALK_SFX_GAIN


def sfx_erase(rng):
    n = int(ERASE * SR)
    t = np.arange(n) / SR
    env = np.abs(np.sin(2 * np.pi * 3.5 * t / ERASE * 0.5 * 2)) * np.sin(np.pi * t / ERASE)
    return bandnoise(n, 250, 2200, rng) * env * 0.1


def sfx_birds(dur, rng):
    n = int(dur * SR)
    out = np.zeros(n, np.float32)
    t = rng.uniform(0, 0.4)
    while t < dur - 0.3:
        f0 = rng.uniform(2600, 4800)
        for j in range(int(rng.integers(2, 6))):
            L = rng.uniform(0.04, 0.09)
            s0 = int((t + j * (L + 0.035)) * SR)
            m = int(L * SR)
            if s0 + m >= n:
                break
            tt = np.arange(m) / SR
            f = f0 * (1 + rng.uniform(-0.25, 0.3) * tt / L)
            out[s0:s0 + m] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / L) * 0.012
        t += rng.uniform(0.5, 1.6)
    return out


def sfx_river(dur, rng):
    n = int(dur * SR)
    x = bandnoise(n, 120, 900, rng) + 0.3 * bandnoise(n, 1500, 5000, rng)
    mod = 0.75 + 0.25 * np.sin(2 * np.pi * 0.23 * np.arange(n) / SR + rng.uniform(0, 6))
    return x * mod * 0.018


def sfx_wind(dur, rng):
    n = int(dur * SR)
    x = lownoise(n, 500, rng)
    t = np.arange(n) / SR
    mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.17 * t + rng.uniform(0, 6))
    return x * mod * 0.03


def sfx_arrow(rng):
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    w = int(0.28 * SR)
    whoosh = np.zeros(n, np.float32)
    whoosh[:w] = bandnoise(w, 1500, 6000, rng) * np.sin(np.pi * np.arange(w) / w) ** 2 * 0.35
    th = np.zeros(n, np.float32)
    s0 = w - int(0.02 * SR)
    tt = t[: n - s0]
    th[s0:] = (np.sin(2 * np.pi * 95 * tt) * np.exp(-tt * 22) + 0.4 * bandnoise(n - s0, 400, 3000, rng) * np.exp(-tt * 60)) * 0.5
    return whoosh + th


def sfx_cry(rng):
    out = []
    for f0, L in [(820, 0.42), (760, 0.6)]:
        n = int(L * SR)
        t = np.arange(n) / SR
        f = f0 * (1.08 - 0.18 * t / L) * (1 + 0.015 * np.sin(2 * np.pi * 28 * t))
        ph = 2 * np.pi * np.cumsum(f) / SR
        tone = sum(np.sin(k * ph) / k ** 0.9 for k in range(1, 9))
        env = np.minimum(1, t / 0.03) * np.exp(-t * 2.2)
        out.append(tone * env * 0.05)
        out.append(np.zeros(int(0.12 * SR)))
    return reverb(np.concatenate(out).astype(np.float32), 1.8, 0.4, rng)


def sfx_bell(rng):
    n = int(4.0 * SR)
    t = np.arange(n) / SR
    f0 = 587.3
    out = np.zeros(n)
    for ratio, amp, dec in [(1, 1, 1.6), (2.76, 0.5, 1.0), (5.4, 0.25, 0.6), (8.93, 0.12, 0.35), (0.5, 0.3, 2.2)]:
        out += amp * np.sin(2 * np.pi * f0 * ratio * t) * np.exp(-t / dec)
    return reverb((out * np.minimum(1, t / 0.004) * 0.06).astype(np.float32), 2.5, 0.4, rng)


def tone_env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay), t


def sfx_impact(rng):
    n = int(1.4 * SR)
    env, t = tone_env(n, 0.002, 0.35)
    f = 45 + 75 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env
    sub = np.sin(2 * np.pi * 38 * t) * np.minimum(1, t / 0.01) * np.exp(-t / 0.6) * 0.6
    hit = lownoise(n, 900, rng) * np.exp(-t * 35) * 2.0
    snap = bandnoise(n, 2500, 7500, rng) * np.exp(-t * 90) * 1.5
    x = body + sub + hit + snap
    return (x / (np.abs(x).max() + 1e-9) * 0.25).astype(np.float32)


def sfx_bowstring(rng):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f = 98 * (1 + 0.04 * np.exp(-t * 25))
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = sum(np.sin(k * ph) * np.exp(-t * (6 + 3 * k)) / k for k in range(1, 9))
    click = bandnoise(n, 1500, 6000, rng) * np.exp(-t * 120)
    x = tone + 0.8 * click
    return (x / (np.abs(x).max() + 1e-9) * 0.22).astype(np.float32)


def sfx_whoosh(rng, dur=0.45):
    n = int(dur * SR)
    k = np.linspace(0, 1, n)
    lo = bandnoise(n, 300, 1500, rng)
    hi = bandnoise(n, 1500, 6000, rng)
    x = (lo * (1 - k) + hi * k) * np.sin(np.pi * k) ** 2
    return (x / (np.abs(x).max() + 1e-9) * 0.18).astype(np.float32)


def sfx_rumble(rng, dur=2.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.minimum(1, t / 0.6) * np.minimum(1, (t[-1] - t) / 0.9)
    x = lownoise(n, 110, rng) * 6 + np.sin(2 * np.pi * 36 * t) * 0.5 * (0.7 + 0.3 * np.sin(2 * np.pi * 3.1 * t))
    x *= env
    return (x / (np.abs(x).max() + 1e-9) * 0.26).astype(np.float32)


def sfx_rocks(rng, dur=1.8):
    n = int(dur * SR)
    out = np.zeros(n, np.float32)
    t = 0.0
    while t < dur - 0.1:
        m = int(rng.uniform(0.03, 0.12) * SR)
        s0 = int(t * SR)
        if s0 + m >= n:
            break
        tt = np.arange(m) / SR
        out[s0:s0 + m] += bandnoise(m, rng.uniform(200, 600), rng.uniform(1500, 4000), rng) * np.exp(-tt * rng.uniform(30, 70)) * rng.uniform(0.4, 1.0) * (1 - t / dur)
        t += rng.exponential(0.07)
    out += sfx_rumble(rng, dur) * 0.8
    return (out / (np.abs(out).max() + 1e-9) * 0.26).astype(np.float32)


def sfx_conch(rng, dur=2.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 233 * (1 + 0.03 * np.minimum(1, t / 0.5)) * (1 + 0.004 * np.sin(2 * np.pi * 4.5 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = sum(np.sin(k * ph) * (1.0 if k == 1 else 0.7 / k ** 0.6) * (1 + 1.2 * np.exp(-((k * 233 - 900) ** 2) / 2e5)) for k in range(1, 12))
    breath = bandnoise(n, 600, 2500, rng) * 0.15
    env = np.minimum(1, t / 0.35) ** 2 * np.minimum(1, (t[-1] - t) / 0.6)
    x = reverb(((tone + breath) * env).astype(np.float32), 2.0, 0.3, rng)
    return (x / (np.abs(x).max() + 1e-9) * 0.2).astype(np.float32)


def sfx_snap(rng):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    x = bandnoise(n, 2000, 8000, rng) * np.exp(-t * 60)
    return (x / (np.abs(x).max() + 1e-9) * 0.12).astype(np.float32)


def sfx_heartbeat(dur, rng, bpm=64):
    n = int(dur * SR)
    out = np.zeros(n, np.float32)
    beat = 60 / bpm
    t = 0.1
    while t < dur - 0.4:
        for off, amp in ((0.0, 1.0), (0.19, 0.7)):
            m = int(0.25 * SR)
            s0 = int((t + off) * SR)
            if s0 + m >= n:
                break
            tt = np.arange(m) / SR
            out[s0:s0 + m] += amp * np.sin(2 * np.pi * (55 + 25 * np.exp(-tt * 30)) * tt) * np.minimum(1, tt / 0.004) * np.exp(-tt * 18)
        t += beat
    return out * 0.035


def sfx_fire(dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    roar = lownoise(n, 380, rng) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.4 * t + rng.uniform(0, 6))) * 3
    crackle = np.zeros(n, np.float32)
    k = int(dur * 18)
    for s0 in rng.integers(0, max(1, n - 400), k):
        m = int(rng.integers(40, 300))
        crackle[s0:s0 + m] += bandnoise(m, 1500, 7000, rng) * np.exp(-np.arange(m) / (m / 4)) * rng.uniform(0.3, 1.0)
    return (roar * 0.006 + crackle * 0.02).astype(np.float32)


def sfx_army(dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    murmur = sum(bandnoise(n, lo, lo * 2.2, rng) * (0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(0.1, 0.4) * t + rng.uniform(0, 6))) for lo in (180, 320, 520))
    march = np.zeros(n, np.float32)
    beat = 0.5
    s = 0.0
    while s < dur - 0.2:
        m = int(0.12 * SR)
        s0 = int(s * SR)
        tt = np.arange(m) / SR
        march[s0:s0 + m] += lownoise(m, 220, rng) * np.exp(-tt * 40) * 4
        s += beat
    clink = np.zeros(n, np.float32)
    for s0 in rng.integers(0, max(1, n - 2000), int(dur * 1.5)):
        m = 1600
        tt = np.arange(m) / SR
        clink[s0:s0 + m] += np.sin(2 * np.pi * rng.uniform(2500, 4200) * tt) * np.exp(-tt * 30) * rng.uniform(0.2, 0.6)
    return (murmur * 0.01 + march * 0.012 + clink * 0.006).astype(np.float32)


def sfx_sea(dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    phase = (t / 6.5 + rng.uniform(0, 1)) % 1
    swell = np.where(phase < 0.35, phase / 0.35, np.exp(-(phase - 0.35) * 4)) ** 1.5
    x = bandnoise(n, 120, 1400, rng) * (0.25 + 0.75 * swell) + bandnoise(n, 2000, 6000, rng) * 0.35 * swell
    return (x * 0.02).astype(np.float32)


BEDS = {"birds": sfx_birds, "river": sfx_river, "wind": sfx_wind, "fire": sfx_fire, "army": sfx_army, "sea": sfx_sea, "heartbeat": sfx_heartbeat}
ONESHOTS = {"arrow": sfx_arrow, "cry": sfx_cry, "bell": sfx_bell, "impact": sfx_impact, "bowstring": sfx_bowstring, "whoosh": sfx_whoosh, "rumble": sfx_rumble, "rocks": sfx_rocks, "conch": sfx_conch, "snap": sfx_snap}


def sfx_licenses():
    if not SFX_LICENSES.exists():
        return {}
    with SFX_LICENSES.open(newline="") as fh:
        return {row["file"].strip(): row for row in csv.DictReader(fh) if row.get("file")}


def load_licensed_sfx(name):
    rows = sfx_licenses()
    row = rows.get(name)
    if row is None:
        raise PermissionError(f"SFX file '{name}' has no row in {SFX_LICENSES}; add file,source_url,license before using it")
    lic = (row.get("license") or "").strip().lower()
    if not lic or not (row.get("source_url") or "").strip():
        raise PermissionError(f"SFX file '{name}': licenses.csv row needs both source_url and license")
    words = set(re.split(r"[^a-z0-9+]+", lic))
    if words & set(SFX_FORBIDDEN_LICENSES) or any(f in lic for f in SFX_FORBIDDEN_LICENSES if len(f) > 2):
        raise PermissionError(f"SFX file '{name}': licence '{row['license']}' is not allowed for a monetised channel")
    if not any(a in lic for a in SFX_ALLOWED_LICENSES):
        raise PermissionError(f"SFX file '{name}': licence '{row['license']}' is not on the allowed list {SFX_ALLOWED_LICENSES}")
    path = SFX_DIR / name
    if not path.exists():
        raise FileNotFoundError(path)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], check=True, capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).copy()
    gain = float(row.get("gain") or 1.0)
    return x * gain


def scene_hits(script, i):
    sc = script["scenes"][i]
    default = [{"name": "impact", "at": 0.0}] if i == 0 and engine_version(script) >= 2 else []
    h = sc.get("hit", default)
    if not h:
        return []
    if isinstance(h, str):
        return [{"name": h, "at": 0.0}]
    return [h] if isinstance(h, dict) else list(h)


def make_sfx(name, rng, dur=None, bed=False):
    if name.startswith("file:"):
        return load_licensed_sfx(name[5:]), bed
    if name in BEDS:
        return BEDS[name](dur, rng), True
    if name in ONESHOTS:
        return ONESHOTS[name](rng), False
    raise ValueError(f"unknown sfx '{name}' (beds: {', '.join(BEDS)}; one-shots: {', '.join(ONESHOTS)}; or file:<name> from {SFX_DIR})")


def sound(script, timings, total, pl, word_times, seed):
    rng = np.random.default_rng(seed + 7)
    n = int(total * SR)
    out = np.zeros(n, np.float32)

    def put(x, at):
        s0 = int(max(0, at) * SR)
        e = min(n, s0 + len(x))
        if e > s0:
            out[s0:e] += x[: e - s0]

    for i, p in enumerate(pl):
        if p["de"] - p["ds"] > 0.02:
            put(sfx_chalk(p["de"] - p["ds"], rng), p["ds"])
        elif i > 0:
            put(sfx_snap(rng), p["ds"])
        if i > 0 and p["transition"] == "erase":
            put(sfx_erase(rng), p["vs"])
        if p["transition"] == "whip":
            put(sfx_whoosh(rng), p["ds"] - 0.22)
        cues = [(c, p["vs"]) for c in script["scenes"][i].get("sfx", [])] + [(c, p["ds"]) for c in scene_hits(script, i)]
        for cue, base in cues:
            name = cue["name"]
            at = base + cue.get("at", 0.0)
            if "word" in cue and word_times[i]:
                toks = []
                for tok in script["scenes"][i]["narration"].split():
                    if toks and not re.search(r"\w", tok):
                        toks[-1] += tok
                    else:
                        toks.append(tok)
                words = [norm(w) for w in toks]
                if norm(cue["word"]) in words:
                    at = timings[i][0] + word_times[i][words.index(norm(cue["word"]))][0] + cue.get("offset", 0.0)
            dur = p["ve"] - p["vs"] + 0.4
            x, bed = make_sfx(name, rng, dur, cue.get("bed", False))
            x = x * float(cue.get("gain", 1.0)) if "gain" in cue else x
            if bed:
                x = x[: int(dur * SR)] if name.startswith("file:") else x
                m = len(x)
                tt = np.arange(m) / SR
                x = x * np.minimum(1, tt / 0.5) * np.minimum(1, (tt[-1] - tt) / 0.5)
                put(x, p["vs"])
            else:
                put(x, at)
    return out


def thumbnail(script, raw_path, out_path, seed):
    board = make_board(seed + 3)
    chalk = chalk_from_image(Image.open(raw_path), seed)
    comp = board + chalk
    lum = chalk.max(axis=2)
    ys, xs = np.nonzero(lum[::8, ::8] > 0.15)
    cy = float(ys.mean() * 8) if len(ys) else CH / 2
    z = 0.92
    fy = cy + (H / 2 - 0.64 * H) / z
    M = cam_matrix(z, CW / 2, fy)
    comp = cv2.warpAffine(comp, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    lin = np.linspace(0, 1, H)
    grad = np.maximum(np.clip(1 - lin / 0.3, 0, 1), np.clip((lin - 0.8) / 0.12, 0, 1))[:, None, None] * 0.8
    comp = comp * (1 - grad) + make_board(seed + 4)[:H, :W] * grad
    img = np.clip(comp, 0, 1)
    meta = script["thumbnail"]
    layers = []
    size = 150
    big = font_for(meta["title"], size)
    probe = ImageDraw.Draw(Image.new("L", (10, 10)))
    while size > 60 and probe.textlength(meta["title"], font=big) > W - 100:
        size -= 6
        big = font_for(meta["title"], size)
    dev = ImageFont.truetype(devanagari_font(), 120, layout_engine=ImageFont.Layout.RAQM)
    mid = font_for(meta["episode"] + meta["subtitle"], 58)
    sm = font_for(meta["series"], 44)

    def centered(text, font, y):
        def fn(d):
            tw = d.textlength(text, font=font)
            d.text(((W - tw) / 2, y), text, font=font, fill=255)
        return fn

    layers.append((centered(meta["devanagari"], dev, 70), (0.96, 0.66, 0.32)))
    layers.append((centered(meta["title"], big, 230), (0.89, 0.76, 0.46)))
    layers.append((centered(meta["series"], sm, 420), (0.95, 0.94, 0.9)))
    layers.append((centered(meta["episode"], mid, 1660), (0.95, 0.94, 0.9)))
    layers.append((centered(meta["subtitle"], mid, 1740), (0.96, 0.66, 0.32)))
    solid = Image.new("L", (W, H), 0)
    for fn, _ in layers:
        fn(ImageDraw.Draw(solid))
    halo = np.asarray(solid.filter(ImageFilter.MaxFilter(25)).filter(ImageFilter.GaussianBlur(28)), np.float32) / 255
    img = img * (1 - np.clip(halo * 1.8, 0, 1) * 0.85)[..., None]
    for k, (fn, col) in enumerate(layers):
        m = chalk_text(fn, (W, H), seed + 50 + k)
        img = np.maximum(img, m[..., None] * np.array(col, np.float32))
    Image.fromarray((img * 255).astype(np.uint8)).save(out_path)

