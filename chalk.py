import math
import re

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage
from scipy.signal import butter, fftconvolve, lfilter

W, H, FPS, SR = 1080, 1920, 30, 24000
CW, CH = 1188, 2112
ERASE = 0.55
CHALKDUSTER = "/System/Library/Fonts/Supplemental/Chalkduster.ttf"
DEVANAGARI = "/System/Library/Fonts/Supplemental/ITFDevanagari.ttc"
PALETTE_HUES = [27.0, 42.0, 95.0]
CHALK_SFX_GAIN = 0.035


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


def is_devanagari(text):
    return any("\u0900" <= ch <= "\u097f" for ch in text)


def font_for(text, size, latin=CHALKDUSTER):
    letters = text.replace("।", "").replace("॥", "")
    for lo, hi, path, idx in SCRIPT_FONTS:
        if any(lo <= ch <= hi for ch in letters):
            return ImageFont.truetype(path, int(size * 1.15), index=idx, layout_engine=ImageFont.Layout.RAQM)
    return ImageFont.truetype(latin, size)


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


def restrict_palette(rgb):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    hues = np.array(PALETTE_HUES, np.float32)
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


def chalk_from_image(img, seed):
    a = np.asarray(img.convert("RGB").resize((CW, CH), Image.LANCZOS)).astype(np.float32) / 255
    lum = a.max(axis=2)
    floor = ndimage.minimum_filter(lum[::4, ::4], size=11)
    floor = ndimage.gaussian_filter(floor, 5)
    floor = cv2.resize(floor, (CW, CH), interpolation=cv2.INTER_LINEAR)
    chalk = np.clip(a - floor[..., None] - 0.035, 0, 1) * 1.2
    chalk = restrict_palette(np.clip(chalk, 0, 1))
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
        dev = ImageFont.truetype(DEVANAGARI, 210, layout_engine=ImageFont.Layout.RAQM)
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


def plan(script, timings, total):
    out = []
    for i, (start, dur) in enumerate(timings):
        vs = 0.0 if i == 0 else start - ERASE
        ve = timings[i + 1][0] - ERASE if i + 1 < len(timings) else total
        ds = 0.0 if i == 0 else start
        avail = ve - ds
        if i == 0:
            draw = 1.6
        elif script["scenes"][i].get("kind") in ("verse", "shloka"):
            draw = min(max(0.7 * avail, 2.6), 5.5)
        else:
            draw = min(max(0.5 * avail, 2.0), 3.6)
        out.append({"vs": vs, "ve": ve, "ds": ds, "de": ds + draw})
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


def cam_matrix(z, fx, fy, jx=0.0, jy=0.0):
    return np.float32([[z, 0, W / 2 - z * fx + jx], [0, z, H / 2 - z * fy + jy]])


def clamp_focus(z, fx, fy):
    hx = (CW - W / z) / 2
    hy = (CH - H / z) / 2
    return min(max(fx, CW / 2 - hx), CW / 2 + hx), min(max(fy, CH / 2 - hy), CH / 2 + hy)


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


def render(script, st, timings, total, raw_paths, writer, captioner, groups, seed, log):
    pl = plan(script, timings, total)
    board = make_board(seed)
    rng = np.random.default_rng(seed)
    scenes = []
    prev_cam = (1.0, CW / 2, CH / 2)
    for i, sc in enumerate(script["scenes"]):
        img = Image.open(raw_paths[i])
        chalk = chalk_from_image(img, seed + i)
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
        prev_cam = cam[1]
        title = title_layer(sc["emphasis"].upper(), seed + 100 + i) if sc.get("emphasis") else None
        scenes.append({"chalk": chalk, "order": order, "pts": pts, "ghost": ghost.astype(np.float32), "cam": cam, "title": title})
        log(f"render: prepared scene {i + 1}/{len(script['scenes'])} ({len(pts)} stroke points)")
    stick = chalk_stick()
    parts = Particles(seed)
    field = ndimage.gaussian_filter(rng.normal(size=(CH // 4, CW // 4)), sigma=(2.5, 22)).astype(np.float32)
    field = (np.argsort(np.argsort(field.ravel())).reshape(field.shape) / field.size).astype(np.float32)
    nframes = int(total * FPS)
    tip = None
    log(f"render: {nframes} frames ({total:.1f}s)")
    for f in range(nframes):
        t = f / FPS
        i = next((k for k, p in enumerate(pl) if p["vs"] <= t < p["ve"]), len(pl) - 1)
        p, s = pl[i], scenes[i]
        jx, jy = 2.5 * math.sin(t * 0.7), 2.0 * math.sin(t * 0.53 + 1)
        tip_pos = None
        if i > 0 and t < p["ds"]:
            q = (t - p["vs"]) / ERASE
            ps = scenes[i - 1]
            erased = np.clip((q * 1.2 - field) / 0.2, 0, 1)
            erased = cv2.resize(erased, (CW, CH), interpolation=cv2.INTER_LINEAR)[..., None]
            layer = ps["chalk"] * (1 - erased) + ps["ghost"] * erased
            if i > 1:
                layer = np.maximum(layer, scenes[i - 2]["ghost"] * 0.5)
            z, fx, fy = ps["cam"][1]
            for _ in range(2):
                parts.emit(float(rng.uniform(80, W - 80)), float(rng.uniform(200, H - 300)), 2, 2.0)
        else:
            dp = (t - p["ds"]) / max(0.01, p["de"] - p["ds"])
            prog = ease(min(1.0, max(0.0, dp)))
            if prog < 1:
                vis = np.clip((prog * 1.01 - s["order"]) / 0.012, 0, 1)[..., None]
                layer = s["chalk"] * vis
            else:
                layer = s["chalk"]
            if i > 0:
                fade = max(0.0, 1 - (t - p["ds"]) / 2.5)
                layer = np.maximum(layer, scenes[i - 1]["ghost"] * (0.35 + 0.65 * fade))
            u = smooth(min(1.0, max(0.0, (t - p["ds"]) / max(0.5, p["ve"] - p["ds"]))))
            (z0, fx0, fy0), (z1, fx1, fy1) = s["cam"]
            z, fx, fy = z0 + (z1 - z0) * u, fx0 + (fx1 - fx0) * u, fy0 + (fy1 - fy0) * u
            if prog < 1:
                n = len(s["pts"])
                k = prog / 0.8 if prog < 0.8 else (prog - 0.8) / 0.2
                py, px = s["pts"][min(n - 1, int(k * (n - 1)))]
                tip_pos = ((px - fx) * z + W / 2 + jx, (py - fy) * z + H / 2 + jy)
        M = cam_matrix(z, fx, fy, jx, jy)
        comp = cv2.warpAffine(board, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        comp += cv2.warpAffine(layer, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        frame = Image.fromarray((np.clip(comp, 0, 1) * 255).astype(np.uint8))
        if tip_pos is not None:
            tip = tip_pos if tip is None else (tip[0] * 0.45 + tip_pos[0] * 0.55, tip[1] * 0.45 + tip_pos[1] * 0.55)
            parts.emit(tip[0], tip[1], 1)
        else:
            tip = None
        parts.draw(frame, 1 / FPS)
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
    flute = np.zeros(n, np.float32)
    for i, sc in enumerate(script["scenes"]):
        name = sc.get("melody")
        if name:
            ph = flute_phrase(phrases[name], sa * 2, rng)
            s0 = int(max(0, timings[i][0] - 0.3) * SR)
            e = min(n, s0 + len(ph))
            flute[s0:e] += 0.075 * ph[: e - s0]
    out += reverb(flute, 2.2, 0.35, rng)
    sw = np.zeros(n, np.float32)
    for i, sc in enumerate(script["scenes"]):
        if sc.get("swell"):
            s0 = int(timings[i][0] * SR)
            e = min(n, int((timings[i][0] + timings[i][1] + 1.2) * SR))
            tt = np.arange(e - s0) / SR
            env = np.minimum(1, tt / 1.2) * np.minimum(1, (tt[-1] - tt) / 1.0)
            sw[s0:e] += 0.05 * env * (np.sin(2 * np.pi * sa / 2 * tt) + 0.5 * np.sin(2 * np.pi * sa * 0.75 * tt))
    out += sw
    return out[: int(total * SR)]


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
        put(sfx_chalk(p["de"] - p["ds"], rng), p["ds"])
        if i > 0:
            put(sfx_erase(rng), p["vs"])
        for cue in script["scenes"][i].get("sfx", []):
            name = cue["name"]
            at = p["vs"] + cue.get("at", 0.0)
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
            if name in ("birds", "river", "wind"):
                x = {"birds": sfx_birds, "river": sfx_river, "wind": sfx_wind}[name](dur, rng)
                m = len(x)
                tt = np.arange(m) / SR
                x = x * np.minimum(1, tt / 0.5) * np.minimum(1, (tt[-1] - tt) / 0.5)
                put(x, p["vs"])
            else:
                put({"arrow": sfx_arrow, "cry": sfx_cry, "bell": sfx_bell}[name](rng), at)
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
    dev = ImageFont.truetype(DEVANAGARI, 120, layout_engine=ImageFont.Layout.RAQM)
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

