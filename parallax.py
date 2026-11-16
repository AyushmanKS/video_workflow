import gc
import hashlib
import os
import shutil
import time
from contextlib import contextmanager
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).parent
LOCK = ROOT / "data" / "heavy.lock"
MASK_REPO, MASK_REV = "ZhengPeng7/BiRefNet", "e2bf8e4460fc8fa32bba5ea4d94b3233d367b0e4"
DEPTH_REPO, DEPTH_REV = "depth-anything/Depth-Anything-V2-Small-hf", "5426e4f0f36572d16453bbda7a8389317b1bef99"
REPOS = {MASK_REPO, DEPTH_REPO}
MODES = ("off", "mask", "depth")
TEXT_KINDS = ("verse", "shloka")
MEAN = np.array([0.485, 0.456, 0.406], np.float32)
STD = np.array([0.229, 0.224, 0.225], np.float32)
NEAR_ZOOM, FOCUS_GAIN, DRIFT_PX, JITTER_GAIN, FILL_GAIN = 0.045, 0.15, 14.0, 0.6, 0.7
_HELD = []


@contextmanager
def heavy_lock(label, log=print, wait=15, timeout=4 * 3600):
    if _HELD:
        yield
        return
    t0 = time.time()
    told = False
    while True:
        try:
            LOCK.mkdir(parents=True)
            break
        except FileExistsError:
            if time.time() - t0 > timeout:
                raise TimeoutError(f"{LOCK} held for over {timeout} s")
            if not told:
                log(f"{label}: waiting for {LOCK.relative_to(ROOT)} (another heavy model run)")
                told = True
            time.sleep(wait)
    (LOCK / "owner").write_text(f"{label} pid {os.getpid()} {time.strftime('%Y-%m-%dT%H:%M:%S%z')}")
    _HELD.append(True)
    try:
        yield
    finally:
        _HELD.clear()
        shutil.rmtree(LOCK, ignore_errors=True)


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def scene_mode(script, sc, i=0):
    if sc.get("kind") in TEXT_KINDS:
        return "off"
    mode = sc.get("depth", script.get("depth", "off")) or "off"
    if mode not in MODES:
        raise ValueError(f"scene {i + 1}: unknown depth '{mode}' (use {', '.join(MODES)})")
    return mode


def wants_mask(script, sc, i=0):
    if sc.get("kind") in TEXT_KINDS:
        return False
    return scene_mode(script, sc, i) != "off" or sc.get("alive", script.get("alive")) is True


def map_paths(img_dir, j, kind):
    return Path(img_dir) / f"{j:02d}_{kind}.png", Path(img_dir) / f"{j:02d}_{kind}.hash"


def map_key(raw, kind):
    repo, rev = (MASK_REPO, MASK_REV) if kind == "mask" else (DEPTH_REPO, DEPTH_REV)
    return f"{kind}|{repo}@{rev[:12]}|{file_sha(raw)}"


def fresh(img_dir, j, kind):
    png, side = map_paths(img_dir, j, kind)
    raw = Path(img_dir) / f"{j:02d}_raw.png"
    if not png.exists():
        return False
    if not side.exists():
        return True
    return side.read_text().strip() == map_key(raw, kind)


def torch_device():
    import torch

    return "mps" if torch.backends.mps.is_available() else "cpu"


def load_mask_model():
    from transformers import AutoModelForImageSegmentation

    model = AutoModelForImageSegmentation.from_pretrained(MASK_REPO, revision=MASK_REV, trust_remote_code=True)
    dev = torch_device()
    return (model.half() if dev == "mps" else model.float()).eval().to(dev)


def predict_mask(model, img):
    import torch

    img = img.convert("RGB")
    x = (np.asarray(img.resize((1024, 1024), Image.BILINEAR), np.float32) / 255 - MEAN) / STD
    w = next(model.parameters())
    x = torch.from_numpy(x.transpose(2, 0, 1)[None].copy()).to(w.device, dtype=w.dtype)
    with torch.no_grad():
        p = model(x)[-1].sigmoid().float().cpu().numpy()[0, 0]
    return cv2.resize(p, img.size, interpolation=cv2.INTER_LINEAR)


def load_depth_model():
    from transformers import AutoImageProcessor, AutoModelForDepthEstimation

    proc = AutoImageProcessor.from_pretrained(DEPTH_REPO, revision=DEPTH_REV)
    model = AutoModelForDepthEstimation.from_pretrained(DEPTH_REPO, revision=DEPTH_REV)
    return proc, model.eval().to(torch_device())


def predict_depth(bundle, img):
    import torch

    proc, model = bundle
    img = img.convert("RGB")
    inputs = {k: v.to(next(model.parameters()).device) for k, v in proc(images=img, return_tensors="pt").items()}
    with torch.no_grad():
        d = model(**inputs).predicted_depth
    d = torch.nn.functional.interpolate(d[:, None], size=(img.height, img.width), mode="bicubic", align_corners=False)
    d = d[0, 0].float().cpu().numpy()
    lo, hi = np.percentile(d, [2, 98])
    return np.clip((d - lo) / max(1e-6, hi - lo), 0, 1)


def unload():
    gc.collect()
    try:
        import torch

        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    except Exception:
        pass


def save_map(arr, path, kind):
    if kind == "depth":
        Image.fromarray((np.clip(arr, 0, 1) * 65535).astype(np.uint16)).save(path)
    else:
        Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(path)


def compute_maps(img_dir, stills, kind, log=print):
    img_dir = Path(img_dir)
    todo = [j for j in sorted(stills) if (img_dir / f"{j:02d}_raw.png").exists() and not fresh(img_dir, j, kind)]
    stats = {"kind": kind, "computed": todo, "load_s": 0.0, "per_image_s": []}
    if not todo:
        return stats
    loader, predict = (load_mask_model, predict_mask) if kind == "mask" else (load_depth_model, predict_depth)
    with heavy_lock(f"{kind} maps", log):
        unload()
        t0 = time.time()
        model = loader()
        stats["load_s"] = round(time.time() - t0, 2)
        try:
            for j in todo:
                raw = img_dir / f"{j:02d}_raw.png"
                t1 = time.time()
                arr = predict(model, Image.open(raw))
                png, side = map_paths(img_dir, j, kind)
                save_map(arr, png, kind)
                side.write_text(map_key(raw, kind))
                stats["per_image_s"].append(round(time.time() - t1, 2))
                log(f"{kind}: still {j:02d} in {stats['per_image_s'][-1]:.1f}s")
        finally:
            del model
            unload()
    return stats


def ensure_maps(script, img_dir, still_of, log=print):
    need = {"mask": set(), "depth": set()}
    for i, sc in enumerate(script["scenes"]):
        if wants_mask(script, sc, i):
            need["mask"].add(still_of(script, i))
        if scene_mode(script, sc, i) == "depth":
            need["depth"].add(still_of(script, i))
    return [compute_maps(img_dir, need[k], k, log) for k in ("mask", "depth") if need[k]]


def read_map(path, size, crop=None, crop_fn=None, sigma=0.0):
    path = Path(path) if path else None
    if path is None or not path.exists():
        return None
    im = Image.open(path)
    a = np.asarray(im, np.float32) / (65535.0 if im.mode.startswith("I") else 255.0)
    if a.ndim == 3:
        a = a[..., 0]
    if crop and crop_fn:
        a = np.asarray(crop_fn(Image.fromarray(a, "F"), crop), np.float32)
    a = cv2.resize(a, size, interpolation=cv2.INTER_LINEAR)
    return cv2.GaussianBlur(a, (0, 0), sigma) if sigma > 0 else a


def inpaint_fill(chalk, alpha):
    h, w = alpha.shape
    small = cv2.resize(chalk, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    hole = (cv2.resize(alpha, (w // 2, h // 2), interpolation=cv2.INTER_AREA) > 0.06).astype(np.uint8)
    hole = cv2.dilate(hole, np.ones((5, 5), np.uint8))
    if not hole.any():
        return np.zeros_like(chalk)
    u8 = (np.clip(small, 0, 1) * 255).astype(np.uint8)
    filled = cv2.inpaint(u8, hole, 7, cv2.INPAINT_TELEA).astype(np.float32) / 255
    return cv2.resize(filled, (w, h), interpolation=cv2.INTER_LINEAR) * FILL_GAIN


def usable_mask(mask, lo=0.002, hi=0.85):
    if mask is None:
        return False
    frac = float((mask > 0.5).mean())
    return lo < frac < hi


def plane_alpha(a, grow=7, sigma=2.0):
    hard = (a > 0.5).astype(np.uint8)
    if grow:
        hard = cv2.dilate(hard, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1)))
    return cv2.GaussianBlur(hard.astype(np.float32), (0, 0), sigma)


def build_planes(chalk, mask=None, depth=None):
    if usable_mask(mask):
        mask = plane_alpha(mask)
    if depth is not None:
        vis = chalk.max(axis=2) > 0.05
        vals = depth[vis] if vis.sum() > 2000 else depth.ravel()
        t1, t2 = np.quantile(vals, [0.45, 0.8])
        a1 = plane_alpha((depth > t1).astype(np.float32), 5)
        a2 = plane_alpha((depth > t2).astype(np.float32), 5)
        if usable_mask(mask):
            a2 = np.maximum(a2, mask)
        alphas, strength = [np.maximum(a1, a2), a2], [0.45, 1.0]
    elif usable_mask(mask):
        alphas, strength = [mask], [1.0]
    else:
        return None
    alphas = [np.clip(a, 0, 1).astype(np.float32) for a in alphas]
    fills = [inpaint_fill(chalk, a) for a in alphas]
    alphas = [a[..., None] for a in alphas]
    return {"alphas": alphas, "fills": fills, "inv": [1 - a for a in alphas], "filled": [f * a for f, a in zip(fills, alphas)], "strength": strength}


def progress(t, de, ve):
    x = min(1.0, max(0.0, (t - de) / max(0.5, ve - de)))
    return x * x * (3 - 2 * x)


def plane_cams(cam, f0, planes, u, amount=1.0, direction=1.0):
    z, fx, fy, jx, jy, rot = cam
    out = [cam]
    for s in planes["strength"]:
        k = s * amount
        out.append((
            z * (1 + NEAR_ZOOM * k * u),
            f0[0] + (fx - f0[0]) * (1 + FOCUS_GAIN * k * u),
            f0[1] + (fy - f0[1]) * (1 + FOCUS_GAIN * k * u),
            jx * (1 + JITTER_GAIN * k * u) + direction * DRIFT_PX * k * u,
            jy * (1 + JITTER_GAIN * k * u),
            rot,
        ))
    return out


def composite(layer, planes, mats, size, fill_gain=1.0):
    alphas = planes["alphas"]
    n = len(alphas)
    acc = None
    for k in range(n + 1):
        content = layer
        if k < n:
            filled = planes["filled"][k] if np.isscalar(fill_gain) and fill_gain == 1.0 else planes["filled"][k] * fill_gain
            content = layer * planes["inv"][k] + filled
        if k > 0:
            content = content * alphas[k - 1]
        border = cv2.BORDER_CONSTANT if k == 0 else cv2.BORDER_REFLECT
        w = cv2.warpAffine(content, mats[k], size, flags=cv2.INTER_LINEAR, borderMode=border)
        if k == 0:
            acc = w
        else:
            aw = cv2.warpAffine(alphas[k - 1][..., 0], mats[k], size, flags=cv2.INTER_LINEAR, borderMode=border)
            acc = acc * (1 - aw[..., None]) + w
    return acc


def overlay_png(raw, arr, path, color=(255, 64, 64)):
    img = np.asarray(Image.open(raw).convert("RGB"), np.float32)
    a = cv2.resize(arr, (img.shape[1], img.shape[0]))[..., None]
    out = img * (1 - 0.5 * a) + np.array(color, np.float32) * 0.5 * a
    edge = cv2.Canny((a[..., 0] > 0.5).astype(np.uint8) * 255, 50, 150) > 0
    out[edge] = (255, 255, 0)
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(path)


def depth_png(arr, path):
    c = cv2.applyColorMap((np.clip(arr, 0, 1) * 255).astype(np.uint8), cv2.COLORMAP_INFERNO)
    Image.fromarray(c[..., ::-1]).save(path)


def default_direction(i):
    return -1.0 if i % 2 else 1.0


def drift_amount(sc):
    try:
        return max(0.0, min(2.0, float(sc.get("parallax", 1.0))))
    except (TypeError, ValueError):
        return 1.0

