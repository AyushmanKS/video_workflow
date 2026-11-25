import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import chalk
import puppet
from chalk import CH, CW, FPS, H, W

INDIGO = np.array([31, 37, 71], np.float32) / 255
CROSSFADE = 0.5
CHAPTER_WORD = {"en": "Chapter", "hi": "अध्याय", "te": "అధ్యాయం", "gu": "અધ્યાય", "mr": "अध्याय"}
CHAPTER_SHOW = 4.0


def chapter_layers(script, seed):
    word = CHAPTER_WORD.get(script.get("language") or "en", "")
    out = {}
    n = 0
    for i, sc in enumerate(script["scenes"]):
        if sc.get("chapter_title"):
            n = sc.get("chapter") or n + 1
            text = f"{word} {n} · {sc['chapter_title']}" if word else sc["chapter_title"]
            out[i] = chalk.title_layer(text, seed + 300 + i)
    return out


def rig_path(out):
    return Path(out).parent / "rig.json"


def load_rig(out):
    p = rig_path(out)
    rig = json.loads(p.read_text()) if p.exists() else {"shots": []}
    parts = p.parent / "rig_parts"
    if parts.is_dir():
        by = {s["scene"]: s for s in rig.get("shots", [])}
        for f in sorted(parts.glob("*.json")):
            d = json.loads(f.read_text())
            for s in d.get("shots", [d]) if isinstance(d, dict) else d:
                by[s["scene"]] = s
        rig["shots"] = [by[k] for k in sorted(by)]
    return rig


def shot_for(rig, i):
    return next((s for s in rig.get("shots", []) if s.get("scene") == i), None)


def is_card(sc):
    return sc.get("kind") in ("verse", "shloka")


def load_fg(path, crop):
    path = Path(path)
    if not path.exists():
        return None
    m = chalk.crop_still(Image.open(path).convert("L"), crop)
    return np.asarray(m.resize((CW, CH), Image.BILINEAR), np.float32) / 255


MARIONETTE = {"flag": False}
STRING_RGB = (226, 214, 186)
CURTAIN_OPEN = 1.6


def is_marionette(script):
    return script.get("style") == "marionette"


def string_mask(u8):
    g = cv2.cvtColor(u8, cv2.COLOR_RGB2GRAY)
    h, w = g.shape
    th = cv2.morphologyEx(g, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1)))
    edges = (th > 18).astype(np.uint8) * 255
    lines = cv2.HoughLinesP(edges, 1, np.pi / 360, 80, minLineLength=int(h * 0.12), maxLineGap=12)
    m = np.zeros((h, w), np.uint8)
    if lines is None:
        return m
    dark = cv2.GaussianBlur(g, (0, 0), 9)
    thin = []
    for x0, y0, x1, y1 in lines.reshape(-1, 4):
        if abs(x1 - x0) > 0.16 * abs(y1 - y0):
            continue
        ys = np.linspace(y0, y1, 20).astype(int).clip(0, h - 1)
        xs = np.linspace(x0, x1, 20).astype(int).clip(0, w - 1)
        side = np.concatenate([dark[ys, (xs - 10).clip(0, w - 1)], dark[ys, (xs + 10).clip(0, w - 1)]])
        if np.median(side) > 70:
            continue
        cv2.line(m, (int(x0), int(y0)), (int(x1), int(y1)), 255, 5)
        k = (x1 - x0) / max(abs(y1 - y0), 1) * (1 if y1 >= y0 else -1)
        ya = min(y0, y1)
        xa = x0 if y0 <= y1 else x1
        band = np.zeros((h, w), np.uint8)
        cv2.line(band, (int(xa - k * ya), 0), (int(xa + k * (h - ya)), h), 255, 7)
        thin.append(band)
    if thin:
        kern = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 1))
        fine = np.maximum(cv2.morphologyEx(g, cv2.MORPH_TOPHAT, kern), cv2.morphologyEx(g, cv2.MORPH_BLACKHAT, kern)) > 10
        along = np.max(thin, axis=0) > 0
        run = cv2.morphologyEx((fine & along).astype(np.uint8) * 255, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15)))
        m |= cv2.dilate(run, np.ones((3, 3), np.uint8))
    return m


def colour_layer(img):
    u8 = np.asarray(img.convert("RGB").resize((CW, CH), Image.LANCZOS))
    m = string_mask(u8)
    if m.any():
        u8 = cv2.inpaint(u8, m, 5, cv2.INPAINT_TELEA)
    a = u8.astype(np.float32) / 255
    return np.clip((a - 0.02) / 0.98, 0, 1).astype(np.float32)


def chalk_of(path, crop, seed, hues):
    img = chalk.crop_still(Image.open(path).convert("RGB"), crop)
    if MARIONETTE["flag"]:
        return colour_layer(img)
    return chalk.chalk_from_image(img, seed, hues)


def curtain_panels():
    hw = W // 2 + 4
    rng = np.random.default_rng(3)
    xx = np.arange(hw, dtype=np.float32)
    period = 64.0 + 18.0 * np.sin(xx / 97.0)
    phase = np.cumsum(2 * np.pi / period)
    fold = np.sin(phase)
    light = 0.42 + 0.48 * (0.5 + 0.5 * fold) ** 1.6 + 0.22 * np.clip(fold, 0, 1) ** 12
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    vert = 0.78 + 0.22 * np.sin(np.pi * (0.15 + 0.85 * yy))
    grain = cv2.GaussianBlur(rng.normal(0, 1, (H, hw)).astype(np.float32), (0, 0), 1.2) * 0.04
    shade = np.clip(light[None, :] * vert + grain, 0, 1.2)
    rgb = np.stack([150 * shade, 16 * shade, 26 * shade], -1)
    edge = hw - 10
    rgb[:, edge:] = np.array([196, 150, 64], np.float32) * (0.78 + 0.22 * np.cos(np.linspace(0, 40 * np.pi, H)))[:, None, None]
    left = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    return left, left.transpose(Image.FLIP_LEFT_RIGHT)


def draw_strings(frame, stage, u, z, fx, fy):
    from PIL import ImageDraw

    Mc = chalk.cam_matrix(z, fx, fy, 0.0, 0.0)
    d = ImageDraw.Draw(frame, "RGBA")
    for k, p in enumerate(list(stage.puppets) + getattr(stage, "anchors", [])):
        names = [b for b in p.spec.get("strings", []) if b in p.bones]
        fixed = p.spec.get("string_points", [])
        if not names and not fixed:
            continue
        M = p.matrices(u)
        pts = []
        for b in names:
            bx, by = p.bones[b]["b"]
            x, y = (M[b] @ np.array([bx, by, 1.0]))[:2]
            sx, sy = Mc @ np.array([x, y, 1.0])
            pts.append((float(sx), float(sy)))
        Mh = M.get("hips", np.eye(3))
        for fx_, fy_ in fixed:
            x, y = (Mh @ np.array([fx_ * CW, fy_ * CH, 1.0]))[:2]
            sx, sy = Mc @ np.array([x, y, 1.0])
            pts.append((float(sx), float(sy)))
        bar = sum(x for x, _ in pts) / len(pts) + 7.0 * math.sin(2 * math.pi * 0.21 * u + k)
        for sx, sy in pts:
            top = bar + (sx - bar) * 0.55
            d.line([(top, -4), (sx, sy)], fill=STRING_RGB + (170,), width=2)


def build_scene(script, out, i, seed, raw, mask_path, shot):
    sc = script["scenes"][i]
    crop = sc.get("crop")
    hues = chalk.world_hues(sc.get("accent")) if sc.get("accent") else None
    layer = chalk_of(raw, crop, seed + i, hues)
    if shot is None or is_card(sc) or not (shot.get("puppets") or shot.get("elements")):
        stage = puppet.build(layer, [], [], seed + i, None, None, {})
        if MARIONETTE["flag"]:
            stage.boil = [1.0]
        return stage
    base = Path(out).parent
    fg = load_fg(mask_path, crop) if any(p.get("use_fg") for p in shot.get("puppets", [])) else None
    plate = chalk_of(base / shot["plate"], crop, seed + i, hues) if shot.get("plate") else None
    under = {p["name"]: chalk_of(base / p["underlay"], crop, seed + i, hues) for p in shot.get("puppets", []) if p.get("underlay")}
    moving = [p for p in shot.get("puppets", []) if p.get("parts")]
    stage = puppet.build(layer, moving, shot.get("elements", []), seed + i, fg, plate, under)
    stage.anchors = [Anchor(p, CW, CH) for p in shot.get("puppets", []) if not p.get("parts") and p.get("strings")]
    if MARIONETTE["flag"]:
        stage.boil = [1.0]
    return stage


class Anchor:
    def __init__(self, spec, w, h):
        self.spec = puppet.resolve(spec)
        self.bones = {k: {"b": (v["b"][0] * w, v["b"][1] * h)} for k, v in self.spec["bones"].items()}

    def matrices(self, u):
        return {k: np.eye(3) for k in self.bones}


def resolve(shot, timings, origin, span):
    s = json.loads(json.dumps(shot or {}))

    def at(line, frac, offset):
        start, dur = timings[line]
        return start - origin + frac * dur + offset

    for p in s.get("puppets", []):
        for a in p.get("actions", []):
            if "line" in a:
                a["at"] = at(a["line"], a.get("frac", 0.0), a.get("offset", 0.0))
    for e in s.get("elements", []):
        if "line" in e:
            key = "ignite" if e["kind"] == "flame" else "at"
            e[key] = at(e["line"], e.get("frac", 0.0), e.get("offset", 0.0))
        if e["kind"] == "birds" and "dur" not in e:
            e["dur"] = span
    return s


def scene_span(pl, i):
    return pl[i]["ve"] - pl[i]["vs"]


def prepare(script, out, i, seed, raws, masks, rig, timings, pl):
    shot = shot_for(rig, i)
    s = resolve(shot, timings, pl[i]["vs"], scene_span(pl, i))
    stage = build_scene(script, out, i, seed, raws[i], masks[i], s if shot else None)
    order, pts, com = chalk.reveal_order(stage.layer, "reading" if is_card(script["scenes"][i]) else "size")
    cam = (shot or {}).get("camera")
    if cam is None:
        if is_card(script["scenes"][i]):
            cam = {"z0": 1.0, "z1": 1.03}
        else:
            cam = {"z0": 1.0, "z1": 1.04 if i % 2 == 0 else 1.02, "fx": (com[0] - CW / 2) / CW * 0.5, "fy": (com[1] - CH / 2) / CH * 0.35}
    return {"stage": stage, "order": order, "pts": pts, "com": com, "cam": cam, "shot": s, "transition": (shot or {}).get("transition")}


def camera(S, p, t):
    cam = S["cam"]
    span = max(0.5, p["ve"] - p["ds"])
    u = puppet.smoothstep(min(1.0, max(0.0, (t - p["ds"]) / span)))
    z = cam.get("z0", 1.0) + (cam.get("z1", 1.03) - cam.get("z0", 1.0)) * u
    fx = CW / 2 + cam.get("fx", 0.0) * CW
    fy = CH / 2 + cam.get("fy", 0.0) * CH
    fx, fy = chalk.clamp_focus(z, fx, fy)
    return z, fx, fy


def composite(board, lay, z, fx, fy):
    M = chalk.cam_matrix(z, fx, fy, 0.0, 0.0)
    comp = cv2.warpAffine(board, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return comp + cv2.warpAffine(lay, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)


def render(script, st, timings, total, raws, writer, captioner, groups, seed, log, masks, out):
    mar = MARIONETTE["flag"] = is_marionette(script)
    puppet.FILL_GRAIN["on"] = not mar
    pl = chalk.plan(script, timings, total)
    rig = load_rig(out)
    board = np.zeros((CH, CW, 3), np.float32) if mar else chalk.make_board(seed)
    curtains = curtain_panels() if mar else None
    rng = np.random.default_rng(seed)
    field = cv2.GaussianBlur(rng.uniform(0, 1, (CH // 4, CW // 4)).astype(np.float32), (0, 0), 6)
    field = (np.argsort(np.argsort(field.ravel())).reshape(field.shape) / field.size).astype(np.float32)
    stick = chalk.chalk_stick()
    dust = chalk.Particles(seed)
    over = chalk.Overlays(seed)
    titles = {i: chalk.title_layer(sc["emphasis"].upper(), seed + 100 + i) for i, sc in enumerate(script["scenes"]) if sc.get("emphasis")}
    chapter_titles = chapter_layers(script, seed)
    cache = {}

    def get(i):
        if i not in cache:
            for k in [k for k in cache if k < i - 1]:
                del cache[k]
            cache[i] = prepare(script, out, i, seed, raws, masks, rig, timings, pl)
            log(f"render: prepared scene {i + 1}/{len(pl)} (puppet)")
        return cache[i]

    nframes = int(total * FPS)
    tip = None
    held = None
    log(f"render: {nframes} frames ({total:.1f}s), puppet engine")
    for f in range(nframes):
        t = f / FPS
        i = next((k for k, p in enumerate(pl) if p["vs"] <= t < p["ve"]), len(pl) - 1)
        p, S = pl[i], get(i)
        tr = S["transition"] or ("black" if mar else p["transition"])
        prog = 1.0
        if i > 0 and t < p["ds"]:
            P = get(i - 1)
            pp = pl[i - 1]
            lay = P["stage"].frame(t - pp["vs"], f)
            z, fx, fy = camera(P, pp, t)
            q = (t - p["vs"]) / max(1e-3, p["ds"] - p["vs"])
            if tr == "erase":
                erased = cv2.resize(np.clip((q * 1.2 - field) / 0.2, 0, 1), (CW, CH), interpolation=cv2.INTER_LINEAR)[..., None]
                lay = lay * (1 - erased)
                for _ in range(2):
                    dust.emit(float(rng.uniform(80, W - 80)), float(rng.uniform(200, H - 300)), 2, 2.0)
            comp = composite(board, lay, z, fx, fy)
            if tr == "black":
                comp = comp * (1 - q)
            held = comp
        else:
            lay = S["stage"].frame(t - p["vs"], f)
            dp = (t - p["ds"]) / max(0.01, p["de"] - p["ds"])
            prog = 1.0 if mar else p["p0"] + (1 - p["p0"]) * chalk.ease(min(1.0, max(0.0, dp)))
            if prog < 1:
                lay = lay * np.clip((prog * 1.01 - S["order"]) / 0.012, 0, 1)[..., None]
            z, fx, fy = camera(S, p, t)
            comp = composite(board, lay, z, fx, fy)
            age = t - p["ds"]
            if i > 0 and tr == "crossfade" and held is not None and age < CROSSFADE:
                a = puppet.smoothstep(age / CROSSFADE)
                comp = held * (1 - a) + comp * a
            elif i > 0 and tr == "dip" and age < CROSSFADE:
                a = puppet.smoothstep(age / CROSSFADE)
                comp = INDIGO * (1 - a) + comp * a
            elif i > 0 and tr == "black" and age < 0.25:
                comp = comp * (age / 0.25)
            if not (i > 0 and tr == "crossfade" and age < CROSSFADE):
                held = comp
        frame = Image.fromarray((np.clip(comp, 0, 1) * 255).astype(np.uint8))
        if mar:
            if i > 0 and t < p["ds"]:
                fade = 1 - (t - p["vs"]) / max(1e-3, p["ds"] - p["vs"])
                Sd, ud, zd = P, t - pp["vs"], (z, fx, fy)
            else:
                fade = min(1.0, (t - p["ds"]) / 0.25) if i > 0 else 1.0
                Sd, ud, zd = S, t - p["vs"], (z, fx, fy)
            if fade > 0.05:
                draw_strings(frame, Sd["stage"], ud, *zd)
            if t < CURTAIN_OPEN:
                off = int(puppet.smoothstep(t / CURTAIN_OPEN) * (W // 2 + 4))
                frame.paste(curtains[0], (-off, 0))
                frame.paste(curtains[1], (W // 2 - 4 + off, 0))
        if prog < 1:
            n = len(S["pts"])
            k = prog / 0.8 if prog < 0.8 else (prog - 0.8) / 0.2
            py, px = S["pts"][min(n - 1, int(k * (n - 1)))]
            pos = ((px - fx) * z + W / 2, (py - fy) * z + H / 2)
            tip = pos if tip is None else (tip[0] * 0.45 + pos[0] * 0.55, tip[1] * 0.45 + pos[1] * 0.55)
            dust.emit(tip[0], tip[1], 1)
        else:
            tip = None
        dust.draw(frame, 1 / FPS)
        kinds = chalk.scene_overlays(script["scenes"][i]) + list(S["shot"].get("overlay", []))
        level = max(0.0, min(1.0, (t - p["vs"]) / 0.4, (p["ve"] - t) / 0.4)) if kinds else 0.0
        over.draw(frame, kinds if level > 0 else [], 1 / FPS, level)
        if tip is not None:
            frame.paste(stick, (int(tip[0]) - 6, int(tip[1]) - 4), stick)
        y_title = int(H * 0.055) - 40
        ct = chapter_titles.get(i)
        if ct is not None and p["vs"] <= t < p["vs"] + CHAPTER_SHOW:
            age = t - p["vs"]
            cw = int(ct.width * min(1.0, age / 1.0))
            fade = min(1.0, (CHAPTER_SHOW - age) / 0.5)
            if cw > 0 and fade > 0:
                part = ct.crop((0, 0, cw, ct.height))
                if fade < 1:
                    part = Image.fromarray((np.asarray(part).astype(np.float32) * [1, 1, 1, fade]).astype(np.uint8), "RGBA")
                frame.paste(part, ((W - ct.width) // 2, y_title), part)
            y_title += ct.height - 60
        tl = titles.get(i)
        if tl is not None and t >= p["ds"]:
            cw = int(tl.width * min(1.0, (t - p["ds"]) / 0.8))
            if cw > 0:
                part = tl.crop((0, 0, cw, tl.height))
                frame.paste(part, ((W - tl.width) // 2, y_title), part)
        group = next((g for g in groups if g["start"] <= t < g["end"] + 0.1), None)
        captioner.draw(frame, group, t, "", 99)
        writer.stdin.write(frame.tobytes())
        if f % (FPS * 10) == 0:
            log(f"render: {t:.0f}s / {total:.0f}s")
    return pl


def qa(script, timings, total, out, seed, raws, masks, log, only=None):
    from pipeline import puppetqa

    MARIONETTE["flag"] = is_marionette(script)
    puppet.FILL_GRAIN["on"] = not MARIONETTE["flag"]
    pl = chalk.plan(script, timings, total)
    rig = load_rig(out)
    dst = Path(out) / "rigqa"
    dst.mkdir(parents=True, exist_ok=True)
    board = chalk.make_board(7)
    allpass = True
    results = {}
    for shot in rig.get("shots", []):
        i = shot["scene"]
        if not (shot.get("puppets") or shot.get("elements")) or (only and i not in only):
            continue
        span = scene_span(pl, i)
        s = resolve(shot, timings, pl[i]["vs"], span)
        stage = build_scene(script, out, i, seed, raws[i], masks[i], s)
        issues = puppetqa.check(stage, span)
        issues, waived = puppetqa.waive(issues, shot.get("qa_waive", []), CW, CH)
        rep = puppetqa.report(issues)
        rep.update(issues=issues, waived=waived)
        name = f"scene{i:02d}"
        (dst / f"{name}.json").write_text(json.dumps(rep, indent=1))
        sheet = puppetqa.sheet(stage, issues, board, dst / f"{name}.png")
        puppetqa.rig_sheet(stage, board, dst / f"{name}_rig.png")
        allpass &= rep["pass"]
        results[i] = rep["pass"]
        log(f"rig qa: scene {i + 1} {'PASS' if rep['pass'] else 'FAIL'} {rep['counts']} {sheet or ''}")
    if only:
        return allpass
    (dst / "summary.json").write_text(json.dumps({"pass": bool(allpass), "scenes": {str(k): v for k, v in results.items()}, "rig_sha": rig_hash(out)}, indent=1))
    return allpass


def rig_hash(out):
    import hashlib

    return hashlib.sha256(json.dumps(load_rig(out), sort_keys=True).encode()).hexdigest()


def main():
    import argparse
    import sys

    import studio

    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--style", default="chalk")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--scenes", help="comma list of 0-based scene indexes to check (no summary written)")
    a = ap.parse_args()
    out = Path(a.out)
    script = json.loads((out / "script.json").read_text())
    st = studio.effective_style(a.style, script)
    chalk.use_fonts(script.get("fonts", "mac"))
    studio.step_masks(script, st, out)
    timings, total, _, _ = studio.scene_timings(script, out)
    n = len(script["scenes"])
    raws = [studio.raw_path(script, out, i) for i in range(n)]
    masks = [out / "img" / f"{studio.scene_still(script, i):02d}_mask.png" for i in range(n)]
    only = {int(x) for x in a.scenes.split(",")} if a.scenes else None
    sys.exit(0 if qa(script, timings, total, out, a.seed, raws, masks, studio.log, only) else 1)


if __name__ == "__main__":
    main()
