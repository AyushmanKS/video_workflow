import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, features
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "brand"
BRAND = ROOT / "profiles" / "brand.json"
SLATE = "#14191C"
CHALK = "#F2EFE6"
GOLD = "#E8BE6E"
SAFFRON = "#F28C28"
TAGLINE = "India's epics, drawn in chalk"
NAME = "Chalk Tales"
LANG_LINE = "English · हिंदी · ગુજરાતી · తెలుగు · मराठी · New chapter daily"
CHALKDUSTER = "/System/Library/Fonts/Supplemental/Chalkduster.ttf"
CHALKBOARD = "/System/Library/Fonts/Supplemental/ChalkboardSE.ttc"
HELVETICA = "/System/Library/Fonts/Helvetica.ttc"
SCRIPTS = [
    ("ऀ", "ॿ", "/System/Library/Fonts/Supplemental/ITFDevanagari.ttc", 4, 1.06),
    ("઀", "૿", "/System/Library/Fonts/KohinoorGujarati.ttc", 2, 1.02),
    ("ఀ", "౿", "/System/Library/Fonts/KohinoorTelugu.ttc", 2, 1.0),
]
BANNER = (2560, 1440)
SAFE = (507, 508, 2053, 932)
TABLET = (352, 508, 2208, 932)
DESKTOP = (0, 508, 2560, 932)


def ensure_raqm():
    lib = "/opt/homebrew/lib"
    if not features.check("raqm") and Path(lib, "libraqm.dylib").exists() and os.environ.get("DYLD_FALLBACK_LIBRARY_PATH") != lib:
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = lib
        os.chdir(ROOT)
        os.execv(sys.executable, [sys.executable, "-m", "pipeline.brandart"] + sys.argv[1:])


def hexrgb(value):
    if isinstance(value, dict):
        value = value.get("hex") or value.get("value")
    v = str(value).lstrip("#")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def tokens():
    cfg = {}
    if BRAND.exists():
        try:
            cfg = json.loads(BRAND.read_text()).get("brand", {})
        except (json.JSONDecodeError, AttributeError):
            cfg = {}
    colors = cfg.get("colors", {}) if isinstance(cfg.get("colors"), dict) else {}
    pick = lambda k, d: hexrgb(colors.get(k, d)) if colors.get(k) else hexrgb(d)
    return {
        "slate": pick("slate", SLATE),
        "chalk": pick("chalk", CHALK),
        "gold": pick("gold", GOLD),
        "saffron": pick("saffron", SAFFRON),
        "tagline": cfg.get("tagline") or TAGLINE,
        "name": cfg.get("name") or NAME,
    }


def board(w, h, slate, seed=7):
    rng = np.random.default_rng(seed)
    base = np.array(slate, np.float32) / 255
    low = ndimage.zoom(ndimage.gaussian_filter(rng.normal(size=(h // 24 + 2, w // 24 + 2)), 2.2), 24, order=1)[:h, :w].astype(np.float32)
    low /= np.abs(low).max() + 1e-6
    grain = ndimage.gaussian_filter(rng.normal(size=(h, w)).astype(np.float32), 0.9)
    grain /= np.abs(grain).max() + 1e-6
    lum = 1 + 0.20 * low + 0.05 * grain
    ghost = Image.new("L", (w // 2, h // 2), 0)
    d = ImageDraw.Draw(ghost)
    for _ in range(int(18 * w * h / 2e6) + 6):
        x, y = rng.uniform(-100, w // 2), rng.uniform(-100, h // 2)
        r = rng.uniform(50, 240)
        a0 = rng.uniform(0, 360)
        d.arc([x, y, x + r * 2.4, y + r], a0, a0 + 140, fill=255, width=int(rng.uniform(16, 46)))
    g = np.asarray(ghost.resize((w, h), Image.BILINEAR), np.float32) / 255
    g = ndimage.gaussian_filter(g, 12)
    img = base[None, None, :] * lum[..., None] + 0.035 * g[..., None]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r2 = ((xx - w / 2) / (w / 2)) ** 2 * 0.8 + ((yy - h / 2) / (h / 2)) ** 2
    img *= (1 - 0.28 * np.clip(r2, 0, 1.6))[..., None]
    return np.clip(img, 0, 1)


def chalkify(img, mask, color, seed=1, strength=1.0):
    rng = np.random.default_rng(seed)
    m = np.asarray(mask, np.float32) / 255
    edge = m * (1 - m) * 4
    m = np.clip(m * 1.1 + (rng.random(m.shape).astype(np.float32) - 0.5) * 0.9 * edge, 0, 1)
    grain = ndimage.gaussian_filter(rng.random(m.shape).astype(np.float32), 0.7)
    grain = (grain - grain.min()) / (grain.max() - grain.min() + 1e-6)
    holes = (rng.random(m.shape) < 0.05).astype(np.float32)
    a = m * np.clip(0.62 + 0.5 * grain, 0, 1) * (1 - 0.55 * holes) * strength
    col = np.array(color, np.float32) / 255
    return img * (1 - a[..., None]) + col[None, None, :] * a[..., None]


def to_image(arr):
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8), "RGB")


class Mask:
    def __init__(self, w, h, ss=2):
        self.ss = ss
        self.size = (w, h)
        self.im = Image.new("L", (w * ss, h * ss), 0)
        self.d = ImageDraw.Draw(self.im)

    def p(self, pts):
        return [(x * self.ss, y * self.ss) for x, y in pts]

    def poly(self, pts):
        self.d.polygon(self.p(pts), fill=255)

    def line(self, pts, width, round_caps=True):
        w = max(1, int(round(width * self.ss)))
        pp = self.p(pts)
        self.d.line(pp, fill=255, width=w, joint="curve")
        if round_caps:
            r = w / 2
            for x, y in (pp[0], pp[-1]):
                self.d.ellipse([x - r, y - r, x + r, y + r], fill=255)

    def ring(self, cx, cy, r, width):
        s = self.ss
        self.d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], outline=255, width=max(1, int(width * s)))

    def text(self, xy, text, font, anchor="ls"):
        f = ImageFont.truetype(font.path, font.size * self.ss, index=getattr(font, "index", 0), layout_engine=font.layout_engine) if hasattr(font, "path") else font
        self.d.text((xy[0] * self.ss, xy[1] * self.ss), text, font=f, fill=255, anchor=anchor)

    def done(self):
        return self.im.resize(self.size, Image.LANCZOS)


def limb_x(v):
    a = abs(v)
    return 0.30 - 0.50 * v * v + 0.30 * max(0.0, (a - 0.70) / 0.30) ** 2


def bow_unit(weight=1.0):
    wt = weight
    half = 0.86
    n = 90
    outer, inner = [], []
    for i in range(n + 1):
        v = -1 + 2 * i / n
        x, y = limb_x(v), half * v
        dx = (limb_x(v + 1e-3) - limb_x(v - 1e-3)) / 2e-3
        dy = half
        ln = math.hypot(dx, dy)
        nx, ny = dy / ln, -dx / ln
        th = (0.115 * (1 - v * v) + 0.055 * v * v) * wt
        outer.append((x + nx * th / 2, y + ny * th / 2))
        inner.append((x - nx * th / 2, y - ny * th / 2))
    tips = [(limb_x(-1), -half), (limb_x(1), half)]
    nock = (-0.50, 0.0)
    head_tip, head_base, head_w = (0.86, 0.0), 0.60, 0.15
    feathers = []
    for d in (0.0, 0.12):
        for sgn in (-1, 1):
            feathers.append([(-0.14 - d, 0.0), (-0.30 - d, sgn * 0.14)])
    return {
        "polys": [outer + inner[::-1], [head_tip, (head_base, -head_w), (head_base + 0.05, 0.0), (head_base, head_w)]],
        "dots": [(t, 0.05 * wt) for t in tips],
        "lines": [([tips[0], nock, tips[1]], 0.042 * wt), ([nock, (head_base + 0.02, 0.0)], 0.07 * wt)] + [(f, 0.038 * wt) for f in feathers],
    }


def bow_parts(cx, cy, r, weight=1.0, angle=-45.0):
    u = bow_unit(weight)
    pts = [q for poly in u["polys"] for q in poly] + [q for pl, _ in u["lines"] for q in pl]
    mx = (min(q[0] for q in pts) + max(q[0] for q in pts)) / 2
    my = (min(q[1] for q in pts) + max(q[1] for q in pts)) / 2
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    ext = max(math.hypot(q[0] - mx, q[1] - my) for q in pts) + 0.06 * weight
    k = r / ext

    def tf(q):
        x, y = q[0] - mx, q[1] - my
        return (cx + k * (x * ca - y * sa), cy + k * (x * sa + y * ca))

    return {"polys": [[tf(q) for q in poly] for poly in u["polys"]], "dots": [(tf(c), w * k) for c, w in u["dots"]],
            "lines": [([tf(q) for q in pl], w * k) for pl, w in u["lines"]]}


def draw_bow(m, cx, cy, r, weight=1.0, angle=-45.0):
    b = bow_parts(cx, cy, r, weight, angle)
    for poly in b["polys"]:
        m.poly(poly)
    for (x, y), w in b["dots"]:
        m.d.ellipse([(x - w) * m.ss, (y - w) * m.ss, (x + w) * m.ss, (y + w) * m.ss], fill=255)
    for pl, w in b["lines"]:
        m.line(pl, w)


def script_of(ch):
    for lo, hi, path, idx, scale in SCRIPTS:
        if lo <= ch <= hi:
            return (path, idx, scale)
    return None


def runs(text):
    out = []
    for ch in text:
        sc = script_of(ch)
        neutral = ch in " ·" or (not ch.isalpha() and sc is None)
        if out and (neutral or out[-1][0] == sc):
            out[-1][1] += ch
        else:
            out.append([sc, ch])
    return [(sc, t) for sc, t in out]


def run_font(sc, size, latin):
    if sc is None:
        return ImageFont.truetype(latin, size, index=1 if latin == CHALKBOARD else 0)
    path, idx, scale = sc
    return ImageFont.truetype(path, int(size * scale), index=idx, layout_engine=ImageFont.Layout.RAQM)


def mixed_width(text, size, latin):
    return sum(run_font(sc, size, latin).getlength(t) for sc, t in runs(text))


def mixed_text(m, x, y, text, size, latin):
    for sc, t in runs(text):
        f = run_font(sc, size, latin)
        big = run_font(sc, size * m.ss, latin)
        m.d.text((x * m.ss, y * m.ss), t, font=big, fill=255, anchor="ls")
        x += f.getlength(t)
    return x


def fit(text, size, maxw, latin):
    while size > 10 and mixed_width(text, size, latin) > maxw:
        size -= 1
    return size


NOTDEF = ""


def missing_glyphs(text, latin):
    bad = []
    for sc, t in runs(text):
        f = run_font(sc, 64, latin)
        ref = f.getmask(NOTDEF).getbbox(), bytes(f.getmask(NOTDEF))
        for ch in t:
            if ch.isspace() or ch == "·" and sc is not None:
                continue
            if 0x0900 <= ord(ch) <= 0x0DFF and not ch.isalpha():
                continue
            mk = f.getmask(ch)
            if (mk.getbbox(), bytes(mk)) == ref:
                bad.append((ch, getattr(f, "path", "?")))
    return bad


def banner(tk, seed=11):
    w, h = BANNER
    base = board(w, h, tk["slate"], seed)
    x0, y0, x1, y1 = SAFE
    pad = 34
    s = 190
    mark_w = 2 * s
    gap = 70
    textmax = (x1 - x0) - 2 * pad - mark_w - gap
    ts = fit(tk["name"], 170, textmax, CHALKDUSTER)
    gs = fit(tk["tagline"], 66, textmax, CHALKBOARD)
    ls = fit(LANG_LINE, 40, textmax, CHALKBOARD)
    tw = max(mixed_width(tk["name"], ts, CHALKDUSTER), mixed_width(tk["tagline"], gs, CHALKBOARD), mixed_width(LANG_LINE, ls, CHALKBOARD))
    total = mark_w + gap + tw
    left = x0 + ((x1 - x0) - total) / 2
    cy = (y0 + y1) / 2
    mg = Mask(w, h)
    title_y = cy - 34
    tag_y = title_y + gs * 1.45
    line_y = tag_y + ls * 1.75
    block_mid = (title_y - 0.72 * ts + line_y + 0.25 * ls) / 2
    draw_bow(mg, left + mark_w / 2, block_mid, s, weight=0.85)
    tx = left + mark_w + gap
    mt = Mask(w, h)
    mixed_text(mt, tx, title_y, tk["name"], ts, CHALKDUSTER)
    mgold = Mask(w, h)
    mixed_text(mgold, tx, tag_y, tk["tagline"], gs, CHALKBOARD)
    ml = Mask(w, h)
    mixed_text(ml, tx, line_y, LANG_LINE, ls, CHALKBOARD)
    mr = Mask(w, h)
    mr.line([(tx, title_y + 22), (tx + mixed_width(tk["name"], ts, CHALKDUSTER) * 0.98, title_y + 18)], 5)
    img = chalkify(base, mg.done(), tk["gold"], seed + 1)
    img = chalkify(img, mt.done(), tk["chalk"], seed + 2)
    img = chalkify(img, mr.done(), tk["chalk"], seed + 5, 0.45)
    img = chalkify(img, mgold.done(), tk["gold"], seed + 3)
    img = chalkify(img, ml.done(), tk["chalk"], seed + 4, 0.82)
    return to_image(img), to_image(base)


def profile(tk, seed=21):
    w = h = 1080
    base = board(w, h, tk["slate"], seed)
    c = w / 2
    ring = Mask(w, h)
    ring.ring(c, c, 468, 18)
    mg = Mask(w, h)
    draw_bow(mg, c, c, 385, weight=1.45)
    img = chalkify(base, ring.done(), tk["chalk"], seed + 1, 0.9)
    img = chalkify(img, mg.done(), tk["gold"], seed + 2)
    return to_image(img)


def icon_bow(m, cx, cy, r):
    draw_bow(m, cx, cy, r * 1.12, weight=1.35)


def icon_star(m, cx, cy, r, lw):
    pts = []
    for i in range(8):
        t = math.pi / 4 * i
        rr = r * (0.86 if i % 2 == 0 else 0.26)
        pts.append((cx + rr * math.sin(t), cy - rr * math.cos(t)))
    m.line(pts + [pts[0], pts[1]], lw, round_caps=False)
    for dx, dy, k in ((0.66, -0.62, 0.17), (-0.66, 0.60, 0.13)):
        x, y = cx + dx * r, cy + dy * r
        m.line([(x - k * r, y), (x + k * r, y)], lw * 0.8)
        m.line([(x, y - k * r), (x, y + k * r)], lw * 0.8)


def icon_chalk(m, cx, cy, r, lw):
    ang = math.radians(-35)
    L, W = r * 1.25, r * 0.36
    ux, uy = math.cos(ang), math.sin(ang)
    vx, vy = -uy, ux
    ox, oy = cx - r * 0.05, cy - r * 0.22
    corners = [(ox - ux * L / 2 - vx * W / 2, oy - uy * L / 2 - vy * W / 2), (ox + ux * L / 2 - vx * W / 2, oy + uy * L / 2 - vy * W / 2),
               (ox + ux * L / 2 + vx * W / 2, oy + uy * L / 2 + vy * W / 2), (ox - ux * L / 2 + vx * W / 2, oy - uy * L / 2 + vy * W / 2)]
    m.line(corners + [corners[0], corners[1]], lw, round_caps=False)
    bx, by = ox - ux * L * 0.22, oy - uy * L * 0.22
    m.line([(bx - vx * W / 2, by - vy * W / 2), (bx + vx * W / 2, by + vy * W / 2)], lw * 0.7)
    sx = cx - r * 0.85
    wave = [(sx + i * r * 1.7 / 40, cy + r * 0.62 + math.sin(i / 40 * 3 * math.pi) * r * 0.1) for i in range(41)]
    m.line(wave, lw)


def icon_mail(m, cx, cy, r, lw):
    w2, h2 = r * 0.92, r * 0.62
    box = [(cx - w2, cy - h2), (cx + w2, cy - h2), (cx + w2, cy + h2), (cx - w2, cy + h2)]
    m.line(box + [box[0], box[1]], lw, round_caps=False)
    m.line([(cx - w2 + lw * 0.3, cy - h2 + lw * 0.3), (cx, cy + h2 * 0.18), (cx + w2 - lw * 0.3, cy - h2 + lw * 0.3)], lw)


ICONS = {"ramayana": "bow", "new": icon_star, "behind_the_chalk": icon_chalk, "collabs": icon_mail}


def highlight(tk, kind, seed=31):
    w, h = 1080, 1920
    base = board(w, h, tk["slate"], seed)
    cx, cy = w / 2, h / 2
    ring = Mask(w, h)
    ring.ring(cx, cy, 300, 12)
    mi = Mask(w, h)
    r, lw = 190, 26
    fn = ICONS[kind]
    if fn == "bow":
        icon_bow(mi, cx, cy, r)
    else:
        fn(mi, cx, cy, r, lw)
    img = chalkify(base, ring.done(), tk["chalk"], seed + 1, 0.75)
    img = chalkify(img, mi.done(), tk["gold"], seed + 2)
    return to_image(img)


def circle_crop(im, size, bg):
    sm = im.resize((size * 4, size * 4), Image.LANCZOS)
    mask = Image.new("L", sm.size, 0)
    ImageDraw.Draw(mask).ellipse([0, 0, sm.size[0] - 1, sm.size[1] - 1], fill=255)
    out = Image.new("RGB", sm.size, bg)
    out.paste(sm, (0, 0), mask)
    return out.resize((size, size), Image.LANCZOS)


def label(d, xy, text, size=22, fill=(235, 235, 235), anchor="la"):
    d.text(xy, text, font=ImageFont.truetype(HELVETICA, size), fill=fill, anchor=anchor)


def profile_preview(options):
    W, H = 1280, 640
    im = Image.new("RGB", (W, H), (60, 60, 60))
    d = ImageDraw.Draw(im)
    half = H // 2
    d.rectangle([0, 0, W, half], fill=(0, 0, 0))
    d.rectangle([0, half, W, H], fill=(255, 255, 255))
    colw = W // len(options)
    for i, (name, src) in enumerate(options):
        x = i * colw + 40
        for j, (bg, fg) in enumerate((((0, 0, 0), (230, 230, 230)), ((255, 255, 255), (30, 30, 30)))):
            y = j * half + 70
            label(d, (x, j * half + 24), f"{name}", 22, fg)
            a = circle_crop(src, 110, bg)
            b = circle_crop(src, 40, bg)
            im.paste(a, (x, y))
            im.paste(b, (x + 140, y + 35))
            label(d, (x, y + 128), "110 px        40 px", 18, fg)
            label(d, (x, y + 160), "actual size", 16, fg)
    return im


def mark_preview(options):
    big = 720
    W = 40 + len(options) * (big + 40)
    H = 70 + big + 260
    im = Image.new("RGB", (W, H), (34, 36, 38))
    d = ImageDraw.Draw(im)
    for i, (name, src) in enumerate(options):
        x = 40 + i * (big + 40)
        label(d, (x, 24), f"{name} · 1080 px (shown at {big})", 26)
        im.paste(src.resize((big, big), Image.LANCZOS), (x, 70))
        y = 70 + big + 30
        for j, bg in enumerate(((0, 0, 0), (255, 255, 255))):
            bx = x + j * 330
            d.rectangle([bx, y, bx + 300, y + 170], fill=bg)
            im.paste(circle_crop(src, 110, bg), (bx + 20, y + 20))
            im.paste(circle_crop(src, 40, bg), (bx + 170, y + 55))
            label(d, (bx + 20, y + 140), "110 px      40 px", 16, (230, 230, 230) if j == 0 else (30, 30, 30))
    return im


def banner_preview(img):
    im = img.copy()
    d = ImageDraw.Draw(im)
    guides = [((0, 0, 2559, 1439), (120, 200, 255), "TV: full 2560×1440"),
              (DESKTOP, (255, 120, 120), "Desktop max: 2560×423"),
              (TABLET, (255, 210, 80), "Tablet: 1855×423"),
              (SAFE, (120, 255, 140), "Mobile / safe area: 1546×423 (all text and logo)")]
    f = ImageFont.truetype(HELVETICA, 34)
    for k, (box, col, txt) in enumerate(guides):
        d.rectangle(box, outline=col, width=6)
        y = box[1] + 12 if k == 0 else (box[3] + 14 + 44 * (k - 1))
        x = box[0] + 16
        d.text((x, y), txt, font=f, fill=col)
    return im


def contact_sheet(files, tk):
    W = 1800
    im = Image.new("RGB", (W, 1660), (34, 36, 38))
    d = ImageDraw.Draw(im)
    label(d, (40, 30), f"{tk['name']} · brand review", 40)
    label(d, (40, 84), "slate #%02X%02X%02X · chalk #%02X%02X%02X · gold #%02X%02X%02X" % (tk["slate"] + tk["chalk"] + tk["gold"]), 22, (200, 200, 200))
    for i, key in enumerate(("slate", "chalk", "gold", "saffron")):
        d.rectangle([1300 + i * 110, 34, 1390 + i * 110, 100], fill=tk[key], outline=(120, 120, 120))
        label(d, (1345 + i * 110, 108), key, 16, (200, 200, 200), "ma")
    b = Image.open(files["banner"]).resize((1720, 967), Image.LANCZOS)
    im.paste(b, (40, 140))
    label(d, (40, 1112), "YouTube banner 2560×1440 (safe 1546×423)", 20)
    y = 1150
    x = 40
    for key, name in (("old_profile", "Old mark (retired)"), ("profile", "Profile: bow and arrow")):
        if key not in files:
            x += 380
            continue
        p = circle_crop(Image.open(files[key]).convert("RGB"), 340, (34, 36, 38))
        im.paste(p, (x, y))
        label(d, (x, y + 350), name, 20)
        x += 380
    for key, name in (("highlight_ramayana", "Ramayana"), ("highlight_new", "New"), ("highlight_behind_the_chalk", "Behind the Chalk"), ("highlight_collabs", "Collabs")):
        hl = Image.open(files[key]).resize((200, 356), Image.LANCZOS)
        im.paste(hl, (x, y))
        c = circle_crop(Image.open(files[key]).crop((240, 660, 840, 1260)), 90, (34, 36, 38))
        im.paste(c, (x + 55, y + 396))
        label(d, (x, y + 362), name, 20)
        x += 235
    return im


def content_bbox_outside_safe(img, base, thresh=18):
    a = np.asarray(img, np.int16)
    b = np.asarray(base, np.int16)
    diff = np.abs(a - b).max(axis=2) > thresh
    x0, y0, x1, y1 = SAFE
    outside = diff.copy()
    outside[y0:y1, x0:x1] = False
    ys, xs = np.nonzero(diff)
    return int(outside.sum()), (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if len(xs) else None


def build(out_dir=OUT):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tk = tokens()
    written = {}
    bimg, bbase = banner(tk)
    p = out_dir / "youtube_banner_2560x1440.png"
    bimg.save(p, optimize=True)
    if p.stat().st_size > 6 * 1024 * 1024:
        bimg.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(p, optimize=True)
    written["banner"] = p
    stray, bbox = content_bbox_outside_safe(bimg, bbase)
    written["_banner_check"] = {"pixels_outside_safe": stray, "content_bbox": bbox, "bytes": p.stat().st_size}
    p = out_dir / "youtube_banner_preview.png"
    banner_preview(bimg).resize((1600, 900), Image.LANCZOS).save(p, optimize=True)
    written["banner_preview"] = p
    prof = profile(tk)
    p = out_dir / "profile_bow_1080.png"
    prof.save(p, optimize=True)
    written["profile"] = p
    stale = out_dir / "profile_bow_ct_1080.png"
    if stale.exists():
        stale.unlink()
    old = out_dir / "instagram_profile_bow.png"
    if old.exists():
        written["old_profile"] = old
    opts = [("Old mark", Image.open(old).convert("RGB"))] if old.exists() else []
    opts += [("New bow and arrow", prof)]
    p = out_dir / "mark_preview.png"
    mark_preview(opts).save(p, optimize=True)
    written["mark_preview"] = p
    p = out_dir / "profile_preview.png"
    profile_preview(opts).save(p, optimize=True)
    written["profile_preview"] = p
    for kind in ICONS:
        p = out_dir / f"highlight_{kind}.png"
        highlight(tk, kind).save(p, optimize=True)
        written[f"highlight_{kind}"] = p
    p = out_dir / "brand_review.png"
    contact_sheet(written, tk).save(p, optimize=True)
    written["review"] = p
    written["_glyphs_missing"] = missing_glyphs(LANG_LINE, CHALKBOARD) + missing_glyphs(tk["name"], CHALKDUSTER) + missing_glyphs(tk["tagline"], CHALKBOARD)
    return written


def main():
    ensure_raqm()
    res = build(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
    for k, v in res.items():
        if isinstance(v, Path):
            with Image.open(v) as im:
                print(f"{v.relative_to(ROOT) if v.is_relative_to(ROOT) else v}  {im.size[0]}x{im.size[1]}  {v.stat().st_size / 1e6:.2f} MB")
        else:
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
