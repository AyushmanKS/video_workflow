import math

import cv2
import numpy as np
from PIL import Image, ImageDraw

SETTLE_AMP = 0.08
SETTLE_TAU = 0.22
SETTLE_PERIOD = 0.5
BOIL_FRAMES = 3
BOIL_DEPTH = 0.05


def smoothstep(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def string_ease(t, at, dur):
    if t <= at:
        return 0.0
    if t < at + dur:
        x = (t - at) / dur
        return smoothstep(x) * (1 + SETTLE_AMP * math.sin(math.pi * x) ** 2)
    tau = t - at - dur
    return 1 + SETTLE_AMP * math.exp(-tau / SETTLE_TAU) * math.cos(2 * math.pi * tau / SETTLE_PERIOD)


def rot_about(px, py, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, px - c * px + s * py], [s, c, py - s * px - c * py], [0, 0, 1]], np.float64)


def translate(dx, dy):
    return np.array([[1, 0, dx], [0, 1, dy], [0, 0, 1]], np.float64)


def seg_dist(xx, yy, a, b):
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    L2 = max(vx * vx + vy * vy, 1e-6)
    u = np.clip(((xx - ax) * vx + (yy - ay) * vy) / L2, 0, 1)
    return np.hypot(xx - (ax + u * vx), yy - (ay + u * vy))


def poly_mask(poly, w, h, grow=0, sigma=0.0):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon([(x * w, y * h) for x, y in poly], fill=255)
    a = np.asarray(m, np.float32) / 255
    if grow:
        a = cv2.dilate(a, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1)))
    if sigma:
        a = cv2.GaussianBlur(a, (0, 0), sigma)
    return a


RIGS = None


def rigs():
    global RIGS
    if RIGS is None:
        import json
        from pathlib import Path

        RIGS = json.loads((Path(__file__).parent / "profiles" / "rigs.json").read_text())
    return RIGS


def resolve(spec):
    if "template" not in spec:
        return spec
    import copy

    spec = copy.deepcopy(spec)
    tpl = rigs()["characters"][spec["template"]]
    joints = spec.get("joints", {})
    out = {}
    for name, tb in tpl["bones"].items():
        if tb["from"] in joints and tb["to"] in joints:
            b = {k: v for k, v in tb.items() if k not in ("from", "to")}
            b.update(a=list(joints[tb["from"]]), b=list(joints[tb["to"]]), joint=tb["from"])
            out[name] = b
    for name, b in out.items():
        par = b.get("parent")
        while par and par not in out:
            par = tpl["bones"].get(par, {}).get("parent")
        b["parent"] = par
    for name, ov in spec.get("bones", {}).items():
        out.setdefault(name, {}).update(ov)
    spec["bones"] = out
    spec["contact"] = sorted(set(spec.get("contact", [])) | {c for c in tpl.get("contact", []) if c in out})
    return spec


class Puppet:
    def __init__(self, spec, w, h, fg=None):
        spec = resolve(spec)
        self.spec = spec
        self.w, self.h = w, h
        self.bones = {k: {"a": (v["a"][0] * w, v["a"][1] * h), "b": (v["b"][0] * w, v["b"][1] * h), "parent": v.get("parent")} for k, v in spec["bones"].items()}
        self.order = self._order()
        grow = int(spec.get("part_grow", 8))
        self.z = spec.get("z") or [k for k in self.order if k in spec["parts"]]
        self.core, self.grown, self.alphas = {}, {}, {}
        hole = np.zeros((h, w), np.float32)
        self.keep = None
        self.fgraw = (fg > 0.5) if fg is not None else None
        if fg is not None and spec.get("use_fg", False):
            r = int(spec.get("fg_grow", 9))
            self.keep = cv2.dilate((fg > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))).astype(np.float32)
        jr = float(spec.get("joint_r", 0.02)) * w
        for k in self.z:
            poly = spec["parts"][k]
            self.core[k] = poly_mask(poly, w, h)
            self.grown[k] = poly_mask(poly, w, h, grow=grow)
            if fg is not None and spec.get("use_fg", False):
                r = int(spec.get("fg_grow", 9))
                keep = cv2.dilate((fg > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))).astype(np.float32)
                self.grown[k] = np.maximum(self.grown[k] * keep, self.core[k])
            par = self.bones[k]["parent"]
            if par and par in spec["parts"] and jr > 0:
                disc = np.zeros((h, w), np.uint8)
                cv2.circle(disc, (int(self.bones[k]["a"][0]), int(self.bones[k]["a"][1])), int(jr), 1, -1)
                disc = disc.astype(np.float32) * np.maximum(poly_mask(spec["parts"][par], w, h, grow=grow), self.grown[k])
                self.core[k] = np.maximum(self.core[k], disc)
                self.grown[k] = np.maximum(self.grown[k], disc)
            self.alphas[k] = self.grown[k]
            hole = np.maximum(hole, self.grown[k])
        self.hole = cv2.GaussianBlur(cv2.dilate(hole, np.ones((3, 3), np.uint8)), (0, 0), 1.2)
        self.alpha = self.hole
        self.string = (spec.get("string", [0.5, 0.0])[0] * w, spec.get("string", [0.5, 0.0])[1] * h)
        self.boxes = {}
        for k in self.z:
            ys, xs = np.nonzero(self.grown[k] > 0.01)
            self.boxes[k] = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)

    def refine(self, layer):
        self.layer = layer
        for name in self.z:
            self.alphas[name] = np.maximum(ink_alpha(layer, self.core[name]), ink_alpha(layer, self.grown[name]) * (layer.max(axis=2) > 0.06))
        self.figure()

    def figure(self):
        fig = np.zeros((self.h, self.w), np.float32)
        for k in self.z:
            fig = np.maximum(fig, self.alphas[k])
        kk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
        closed = cv2.morphologyEx((fig > 0.3).astype(np.uint8), cv2.MORPH_CLOSE, kk).astype(np.float32)
        if self.keep is not None:
            closed = np.maximum(snap(self.layer, closed, int(self.spec.get("snap", 24))) * self.keep, sum(self.core[k] for k in self.z).clip(0, 1))
        hull = np.zeros((self.h, self.w), np.uint8)
        for k in self.z:
            hull = np.maximum(hull, (self.grown[k] > 0.5).astype(np.uint8))
        hull = cv2.dilate(hull, np.ones((7, 7), np.uint8)).astype(np.float32)
        self.fig = np.maximum(fig, ink_alpha(self.layer, closed * hull))

    def build_mesh(self):
        from scipy import ndimage
        from scipy.spatial import Delaunay

        lab = np.zeros((self.h, self.w), np.int32)
        for i, k in enumerate(self.z):
            lab[self.core[k] > 0.5] = i + 1
        fig = self.fig
        idx = ndimage.distance_transform_edt(lab == 0, return_distances=False, return_indices=True)
        labf = lab[idx[0], idx[1]] - 1
        self.labf = labf
        m = fig > 0.03
        ys, xs = np.nonzero(m)
        self.fbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
        sp = int(self.spec.get("mesh", 8))
        rel = {k: {k} | ({self.bones[k]["parent"]} if self.bones[k]["parent"] in self.z else set()) | {c for c in self.z if self.bones[c]["parent"] == k} for k in self.z}
        self.meshes = []
        for i, k in enumerate(self.z):
            own = ((labf == i) & m).astype(np.float32)
            if own.sum() < 20:
                continue
            front = np.zeros((self.h, self.w), bool) if getattr(self, "front_ext", None) is None else self.front_ext.copy()
            for j in range(i + 1, len(self.z)):
                front |= (labf == j) & (fig > 0.5)
            band = int(self.spec.get("complete_band", getattr(self, "motion_band", 10)))
            reach = cv2.dilate(own.astype(np.uint8), np.ones((2 * band + 1, 2 * band + 1), np.uint8)) > 0
            hidden = front & reach
            dil = cv2.dilate(((own > 0.5) | hidden).astype(np.uint8), np.ones((2 * sp + 3, 2 * sp + 3), np.uint8)) > 0
            yy, xx = np.nonzero(dil)
            x0, y0, x1, y1 = int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1
            gy, gx = np.mgrid[y0 - sp:y1 + 2 * sp:sp, x0 - sp:x1 + 2 * sp:sp]
            gx = np.clip(gx, 0, self.w - 1)
            gy = np.clip(gy, 0, self.h - 1)
            keep = dil[gy, gx]
            pts = np.unique(np.stack([gx[keep], gy[keep]], 1), axis=0).astype(np.float64)
            if len(pts) < 3:
                continue
            tri = Delaunay(pts).simplices
            cen = pts[tri].mean(1)
            tri = tri[dil[cen[:, 1].astype(int), cen[:, 0].astype(int)]]
            vl = labf[pts[:, 1].astype(int), pts[:, 0].astype(int)]
            names = []
            for (px_, py_), l in zip(pts, vl):
                nm = self.z[l] if l >= 0 else k
                if nm != k and nm in rel[k]:
                    child = nm if self.bones[nm]["parent"] == k else k
                    R = float(self.spec["bones"][child].get("blend", self.spec.get("joint_blend", 0.03))) * self.w
                    ax, ay = self.bones[child]["a"]
                    if math.hypot(px_ - ax, py_ - ay) > 1.6 * R:
                        nm = k
                elif nm != k:
                    nm = k
                names.append(nm)
            W = self.weights(pts, names, rel[k])
            ownf = cv2.GaussianBlur(own, (0, 0), 0.7) * np.clip(fig * 1.5, 0, 1)
            src = None
            if hidden.any():
                src = self.layer.copy()
                if getattr(self, "underlay", None) is not None:
                    src[hidden] = self.underlay[hidden]
                else:
                    ys_, xs_ = np.nonzero(hidden)
                    bx0, by0 = max(0, xs_.min() - 30), max(0, ys_.min() - 30)
                    bx1, by1 = min(self.w, xs_.max() + 31), min(self.h, ys_.max() + 31)
                    sub = (np.clip(self.layer[by0:by1, bx0:bx1], 0, 1) * 255).astype(np.uint8)
                    hm = (own[by0:by1, bx0:bx1] < 0.5).astype(np.uint8)
                    filled = cv2.inpaint(sub, hm, 6, cv2.INPAINT_TELEA).astype(np.float32) / 255
                    grain = np.random.default_rng(int(by0 * 7 + bx0)).uniform(0.82, 1.08, filled.shape[:2]).astype(np.float32)
                    filled = filled * cv2.GaussianBlur(grain, (0, 0), 0.6)[..., None]
                    hb = hidden[by0:by1, bx0:bx1]
                    src[by0:by1, bx0:bx1][hb] = filled[hb]
                ownf = np.maximum(ownf, cv2.GaussianBlur(hidden.astype(np.float32), (0, 0), 0.7))
            self.meshes.append({"bone": k, "pts": pts, "tri": tri, "W": W, "own": ownf, "box": (x0, y0, x1, y1), "src": src})
        off = np.cumsum([0] + [len(mm["pts"]) for mm in self.meshes])
        self.pts = np.concatenate([mm["pts"] for mm in self.meshes])
        self.tri = np.concatenate([mm["tri"] + off[j] for j, mm in enumerate(self.meshes)])
        self.W = np.concatenate([mm["W"] for mm in self.meshes])
        self.vbone = [self.order[j] for j in self.W.argmax(1)]

    def weights(self, pts, names, allowed):
        bi = {k: i for i, k in enumerate(self.order)}
        W = np.zeros((len(pts), len(self.order)))
        W[np.arange(len(pts)), [bi[n] for n in names]] = 1.0
        for k in self.order:
            par = self.bones[k]["parent"]
            if not par or k not in allowed or par not in allowed or k not in self.z or par not in self.z:
                continue
            R = float(self.spec["bones"][k].get("blend", self.spec.get("joint_blend", 0.03))) * self.w
            a = np.array(self.bones[k]["a"])
            u = np.array(self.bones[k]["b"]) - a
            u /= max(np.hypot(*u), 1e-6)
            d = pts - a
            dist = np.hypot(d[:, 0], d[:, 1])
            sel = (dist < 1.6 * R) & ((W[:, bi[k]] > 0) | (W[:, bi[par]] > 0))
            q = np.clip((d[sel] @ u + R) / (2 * R), 0, 1)
            q = q * q * (3 - 2 * q)
            lat = np.abs(d[sel, 0] * u[1] - d[sel, 1] * u[0])
            fade = np.clip(1 - lat / (float(self.spec["bones"][k].get("width", 2.0)) * R), 0, 1)
            own_child = W[sel, bi[k]] > 0
            q = np.where(own_child, 1 - (1 - q) * fade, q * fade)
            tot = W[sel, bi[k]] + W[sel, bi[par]]
            W[sel, bi[k]] = tot * q
            W[sel, bi[par]] = tot * (1 - q)
        return W / np.maximum(W.sum(1, keepdims=True), 1e-9)

    def max_motion(self, span=15.0, step=0.1):
        pts = []
        for k, b in self.bones.items():
            for q in ("a", "b"):
                pts.append(b[q])
        P = np.c_[np.array(pts), np.ones(len(pts))]
        names = [k for k in self.bones for _ in (0, 1)]
        best = 0.0
        for t in np.arange(0, span, step):
            M = self.matrices(t)
            for i, n in enumerate(names):
                d = M[n] @ P[i] - P[i]
                best = max(best, float(np.hypot(d[0], d[1])))
        return best

    def deform_mesh(self, mm, t, M=None):
        M = M or self.matrices(t)
        P = np.stack([M[k][:2] for k in self.order])
        ph = np.c_[mm["pts"], np.ones(len(mm["pts"]))]
        return np.einsum("vb,bij,vj->vi", mm["W"], P, ph)

    def deform(self, t):
        M = self.matrices(t)
        return np.concatenate([self.deform_mesh(mm, t, M) for mm in self.meshes])

    def src_disp(self, t):
        D = np.zeros((self.h, self.w, 2), np.float32)
        M = self.matrices(t)
        for mm in self.meshes:
            if "bary" not in mm:
                x0, y0, x1, y1 = mm["box"]
                ids = np.full((y1 - y0, x1 - x0), -1, np.int32)
                sl = np.round((mm["pts"] - [x0, y0]) * 16).astype(np.int32)
                for j, tr in enumerate(mm["tri"]):
                    cv2.fillConvexPoly(ids, sl[tr], j, lineType=cv2.LINE_8, shift=4)
                yy, xx = np.nonzero((ids >= 0) & (mm["own"][y0:y1, x0:x1] > 0.3))
                tri = mm["tri"][ids[yy, xx]]
                a, b, c = mm["pts"][tri[:, 0]], mm["pts"][tri[:, 1]], mm["pts"][tri[:, 2]]
                q = np.stack([xx + x0, yy + y0], 1).astype(np.float64)
                v0, v1, v2 = b - a, c - a, q - a
                den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
                den = np.where(np.abs(den) < 1e-9, 1e-9, den)
                wb = (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / den
                wc = (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / den
                mm["bary"] = (yy + y0, xx + x0, tri, np.stack([1 - wb - wc, wb, wc], 1))
            yy, xx, tri, bw = mm["bary"]
            d = self.deform_mesh(mm, t, M) - mm["pts"]
            D[yy, xx] = (bw[:, :, None] * d[tri]).sum(1)
        return D

    def _order(self):
        out, seen = [], set()

        def visit(k):
            if k in seen:
                return
            p = self.bones[k]["parent"]
            if p:
                visit(p)
            seen.add(k)
            out.append(k)

        for k in self.bones:
            visit(k)
        return out

    def angles(self, t):
        if getattr(self, "frozen", False):
            return {k: 0.0 for k in self.bones}, {"sway": 0.0, "dx": 0.0, "dy": 0.0}, {k: [0.0, 0.0] for k in self.bones}
        ang, root, shift = self.base_angles(t)
        for k, f in self.spec.get("follow", {}).items():
            lag = f.get("lag", 0.18)
            prev = self.base_angles(t - lag)[0]
            ang[k] += f.get("gain", 0.8) * (prev[f["of"]] - ang[f["of"]])
        return ang, root, shift

    def base_angles(self, t):
        ang = {k: 0.0 for k in self.bones}
        root = {"sway": 0.0, "dx": 0.0, "dy": 0.0}
        shift = {k: [0.0, 0.0] for k in self.bones}
        for a in self.spec.get("actions", []):
            e = string_ease(t, a["at"], a["dur"])
            if "bone" in a:
                ang[a["bone"]] += a.get("deg", 0.0) * e
                if "shift" in a:
                    shift[a["bone"]][0] += a["shift"][0] * self.w * e
                    shift[a["bone"]][1] += a["shift"][1] * self.h * e
            if "sway" in a:
                root["sway"] += a["sway"] * e
            if "dx" in a:
                root["dx"] += a["dx"] * self.w * e
                hop = a.get("hop", 0.0) * self.h
                if hop and a["at"] < t < a["at"] + a["dur"]:
                    steps = a.get("steps", 2)
                    root["dy"] -= hop * abs(math.sin(math.pi * steps * (t - a["at"]) / a["dur"]))
            if "dy" in a:
                root["dy"] += a["dy"] * self.h * e
        idle = self.spec.get("idle", {})
        ph = idle.get("phase", 0.0)
        root["sway"] += idle.get("sway", 0.4) * math.sin(2 * math.pi * 0.23 * t + ph)
        br = idle.get("breath", 1.0) * math.sin(2 * math.pi * 0.27 * t + ph)
        if idle.get("breath_bone") in shift:
            shift[idle["breath_bone"]][1] += br
        else:
            root["dy"] += br
        for k, amp in idle.get("bones", {}).items():
            ang[k] += amp * math.sin(2 * math.pi * 0.31 * t + ph + len(k))
        return ang, root, shift

    def matrices(self, t):
        ang, root, shift = self.angles(t)
        R = rot_about(self.string[0], self.string[1], root["sway"]) @ translate(root["dx"], root["dy"])
        M = {}
        for k in self.order:
            bn = self.bones[k]
            base = M[bn["parent"]] if bn["parent"] and not self.spec["bones"][k].get("pin") else np.eye(3)
            M[k] = base @ translate(*shift[k]) @ rot_about(bn["a"][0], bn["a"][1], ang[k])
        return M

    def render(self, layer, t, pad=24, cov=None):
        M = self.matrices(t)
        out = np.zeros_like(layer)
        acc = np.zeros(layer.shape[:2], np.float32)
        for mm in self.meshes:
            dst = self.deform_mesh(mm, t, M)
            x0 = max(0, int(min(dst[:, 0].min(), mm["box"][0])) - pad)
            y0 = max(0, int(min(dst[:, 1].min(), mm["box"][1])) - pad)
            x1 = min(self.w, int(max(dst[:, 0].max(), mm["box"][2])) + pad)
            y1 = min(self.h, int(max(dst[:, 1].max(), mm["box"][3])) + pad)
            ids = np.full((y1 - y0, x1 - x0), -1, np.int32)
            dl = np.round((dst - [x0, y0]) * 16).astype(np.int32)
            for j, tr in enumerate(mm["tri"]):
                cv2.fillConvexPoly(ids, dl[tr], j, lineType=cv2.LINE_8, shift=4)
            D = np.concatenate([dst[mm["tri"]], np.ones((len(mm["tri"]), 3, 1))], 2)
            C = np.linalg.solve(D + np.eye(3)[None] * 1e-9, mm["pts"][mm["tri"]])
            mx = np.full(ids.shape, -10.0, np.float32)
            my = np.full(ids.shape, -10.0, np.float32)
            v = ids >= 0
            yy, xx = np.nonzero(v)
            c = C[ids[v]]
            X = xx + x0
            Y = yy + y0
            mx[v] = X * c[:, 0, 0] + Y * c[:, 1, 0] + c[:, 2, 0]
            my[v] = X * c[:, 0, 1] + Y * c[:, 1, 1] + c[:, 2, 1]
            base = mm["src"] if mm.get("src") is not None else layer
            lw = np.clip(cv2.remap(base * mm["own"][..., None], mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT), 0, None)
            aw = np.clip(cv2.remap(mm["own"], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT), 0, 1)
            o = out[y0:y1, x0:x1]
            out[y0:y1, x0:x1] = o * (1 - aw[..., None]) + lw
            acc[y0:y1, x0:x1] = acc[y0:y1, x0:x1] * (1 - aw) + aw
            if cov is not None:
                sub = np.zeros(ids.shape, np.float32)
                sub[v] = mm["own"][np.clip(my[v].astype(int), 0, self.h - 1), np.clip(mx[v].astype(int), 0, self.w - 1)] > -1
                srcown = cv2.dilate((mm["own"] > 0.3).astype(np.uint8), np.ones((5, 5), np.uint8))
                inside = np.zeros(ids.shape, bool)
                inside[v] = srcown[np.clip(my[v].astype(int), 0, self.h - 1), np.clip(mx[v].astype(int), 0, self.w - 1)] > 0
                cov[y0:y1, x0:x1] |= inside
        return out, acc


def scenery_lines(layer, min_len=70, extend=0, figure=None):
    g = (np.clip(layer.max(axis=2), 0, 1) * 255).astype(np.uint8)
    e = cv2.Canny(cv2.GaussianBlur(g, (0, 0), 1.0), 40, 110)
    ls = cv2.HoughLinesP(e, 1, np.pi / 180, 60, minLineLength=min_len, maxLineGap=6)
    m = np.zeros(g.shape, np.uint8)
    if ls is not None:
        for x0, y0, x1, y1 in ls.reshape(-1, 4):
            cv2.line(m, (int(x0), int(y0)), (int(x1), int(y1)), 1, 5)
            if extend and figure is not None and abs(x1 - x0) < 0.35 * abs(y1 - y0):
                dx, dy = x1 - x0, y1 - y0
                L = max(math.hypot(dx, dy), 1.0)
                ux, uy = dx / L, dy / L
                for sx, sy, sg in ((x1, y1, 1), (x0, y0, -1)):
                    if figure[min(g.shape[0] - 1, max(0, int(sy + sg * uy * 8))), min(g.shape[1] - 1, max(0, int(sx + sg * ux * 8)))]:
                        ex, ey = sx + sg * ux * extend, sy + sg * uy * extend
                        ln = np.zeros(g.shape, np.uint8)
                        cv2.line(ln, (int(sx), int(sy)), (int(ex), int(ey)), 1, 3)
                        bright = g > max(110, int(np.percentile(g[m > 0], 60)))
                        m |= (ln > 0) & bright
    return m > 0


def snap(layer, core, radius=20, step=3):
    ink = (layer.max(axis=2) > 0.08).astype(np.uint8)
    m = (core > 0.5).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * step + 1, 2 * step + 1))
    for _ in range(max(1, radius // step)):
        m = np.maximum(m, cv2.dilate(m, k) & ink)
    return np.maximum(core, m.astype(np.float32))


def ink_alpha(layer, core):
    lum = layer.max(axis=2)
    ink = np.clip((lum - 0.04) / 0.08, 0, 1)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    solid = cv2.morphologyEx((ink > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, k).astype(np.float32)
    return cv2.GaussianBlur(np.maximum(core * solid, core * ink), (0, 0), 0.8)


class Elements:
    def __init__(self, specs, w, h, seed=0):
        self.w, self.h = w, h
        self.items = []
        for s in specs:
            if s["kind"] == "birds":
                self.items.append({"spec": s})
                continue
            core = poly_mask(s["poly"], w, h, grow=int(s.get("grow", 3)))
            ys, xs = np.nonzero(core > 0.01)
            x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
            amp = s.get("amp", 6.0)
            pad = int(abs(s.get("vx", 0.0)) * 40 + 3 * amp + 16) if s["kind"] not in ("swing", "attach", "spin") else int(math.radians(max(s.get("deg", 6.0), 8.0)) * max(x1 - x0, y1 - y0) * 1.6 + 40)
            pb = (max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad))
            yy, xx = np.mgrid[pb[1]:pb[3], pb[0]:pb[2]].astype(np.float32)
            self.items.append({"spec": s, "core": core, "alpha": core, "box": (x0, y0, x1, y1), "pbox": pb, "X": xx, "Y": yy})

    def refine(self, layer, exclude=None, plate=None):
        taken = np.zeros((self.h, self.w), np.float32) if exclude is None else exclude.astype(np.float32).copy()
        hsv = cv2.cvtColor(np.clip(layer, 0, 1).astype(np.float32), cv2.COLOR_RGB2HSV)
        for it in self.items:
            if "core" in it and it["spec"].get("snap", 20):
                it["core"] = snap(layer, it["core"], int(it["spec"].get("snap", 20)))
            if "core" in it:
                it["claim"] = it["core"].copy()
            if "core" in it and "saturation_min" in it["spec"]:
                keep = (hsv[..., 1] > it["spec"]["saturation_min"]) & (it["core"] > 0.5)
                if it["spec"].get("largest", True):
                    n, lab, st, _ = cv2.connectedComponentsWithStats(keep.astype(np.uint8), 8)
                    if n > 1:
                        big = st[1:, 4].max()
                        frac = float(it["spec"].get("piece_min", 1.0))
                        ok = [1 + j for j in range(n - 1) if st[1 + j, 4] >= frac * big]
                        keep = np.isin(lab, ok)
                keep = cv2.morphologyEx(keep.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
                keep = cv2.dilate(keep, np.ones((int(it["spec"].get("edge", 5)), int(it["spec"].get("edge", 5))), np.uint8)) > 0
                it["core"] = it["core"] * cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 0.8)
            if "core" in it and "saturation_max" in it["spec"]:
                smax = it["spec"]["saturation_max"]
                soft = np.clip(1.6 - hsv[..., 1] / smax, 0, 1)
                soft = np.maximum(soft, (hsv[..., 2] < 0.08).astype(np.float32))
                it["matte"] = cv2.GaussianBlur(soft, (0, 0), 0.6)
                it["core"] = it["core"] * (it["matte"] > 0.02)
        for it in reversed(self.items):
            if "core" in it:
                raw = it["claim"].copy()
                it["core"] = it["core"] * (1 - np.clip(taken, 0, 1))
                it["alpha"] = ink_alpha(layer, it["core"])
                it["src"] = None
                it["premul"] = None
                if "matte" in it:
                    a = np.clip(it["matte"] * (raw > 0.5), 0, 1)
                    behind = plate if plate is not None else np.zeros_like(layer)
                    it["premul"] = np.clip(layer - (1 - a[..., None]) * behind, 0, None) * (raw > 0.5)[..., None]
                    it["alpha"] = a
                if plate is not None:
                    occ = (raw > 0.5) & (taken > 0.5)
                    vis = it["alpha"] > 0.5
                    if occ.any() and vis.sum() > 50:
                        hp = cv2.cvtColor(np.clip(plate, 0, 1).astype(np.float32), cv2.COLOR_RGB2HSV)
                        hv = hsv[vis]
                        hue = float(np.median(hv[:, 0]))
                        dh = np.abs(((hp[..., 0] - hue) + 180) % 360 - 180)
                        occ = occ & (dh < 18) & (hp[..., 1] > max(0.15, float(np.percentile(hv[:, 1], 20))))
                        o = occ.astype(np.float32)
                        it["src"] = layer * (1 - o[..., None]) + plate * o[..., None]
                        it["alpha"] = np.maximum(it["alpha"], ink_alpha(plate, o))
                taken = np.maximum(taken, (it["claim"] * (1 - np.clip(taken, 0, 1)) > 0.5).astype(np.float32))

    def rematte(self, bg, layer):
        self.frozen = True
        out = bg.copy()
        for it in self.items:
            if "core" not in it:
                continue
            if it.get("premul") is not None and "matte" in it:
                a = it["alpha"]
                raw = it.get("claim", it["core"]) > 0.5
                it["premul"] = np.clip(layer - (1 - a[..., None]) * out, 0, None) * raw[..., None]
            X0, Y0, X1, Y1 = it["pbox"]
            if it.get("premul") is not None:
                obj = it["premul"][Y0:Y1, X0:X1]
            else:
                src = it["src"] if it.get("src") is not None else layer
                obj = (src * it["alpha"][..., None])[Y0:Y1, X0:X1]
            al = it["alpha"][Y0:Y1, X0:X1]
            out[Y0:Y1, X0:X1] = out[Y0:Y1, X0:X1] * (1 - al[..., None]) + obj
        self.frozen = False

    def hole(self):
        A = np.zeros((self.h, self.w), np.float32)
        for it in self.items:
            if "core" in it and it["spec"]["kind"] != "flame":
                if "saturation_max" in it["spec"]:
                    own = np.maximum(it["core"], it.get("claim", it["core"]))
                else:
                    own = it["core"] * cv2.dilate((it["alpha"] > 0.3).astype(np.uint8), np.ones((5, 5), np.uint8))
                A = np.maximum(A, own)
        return A

    def motion(self, it, t):
        if getattr(self, "frozen", False):
            z = np.zeros_like(it["X"])
            return z, z, 1.0
        s = it["spec"]
        if "attach" in s and s["kind"] != "attach":
            pup = self.puppets[s["attach"]["puppet"]]
            Mi = np.linalg.inv(pup.matrices(t)[s["attach"]["bone"]])
            X, Y = it["X"], it["Y"]
            sx = (Mi[0, 0] * X + Mi[0, 1] * Y + Mi[0, 2]).astype(np.float32)
            sy = (Mi[1, 0] * X + Mi[1, 1] * Y + Mi[1, 2]).astype(np.float32)
            sub = dict(it, X=sx, Y=sy, spec={k: v for k, v in s.items() if k != "attach"})
            ox, oy, gain = self.motion(sub, t)
            return (X - (sx - ox)).astype(np.float32), (Y - (sy - oy)).astype(np.float32), gain
        k = s["kind"]
        X, Y = it["X"], it["Y"]
        x0, y0, x1, y1 = it["box"]
        ph = s.get("phase", 0.0)
        f = s.get("freq", 0.5)
        amp = s.get("amp", 6.0)
        gain = 1.0
        zero = np.zeros_like(X)
        if k == "flag":
            ax = s["anchor"][0] * self.w
            ln = s.get("length", 0.08) * self.w
            u = np.clip(np.abs(X - ax) / ln, 0, 1)
            ddy = amp * u ** 1.3 * np.sin(2 * math.pi * (f * t - 0.9 * u) + ph)
            ddx = 0.35 * amp * u * np.cos(2 * math.pi * (f * t - 0.9 * u) + ph)
        elif k == "sway":
            yb = s["pivot_y"] * self.h if "pivot_y" in s else float(y1)
            hf = np.clip((yb - Y) / max(1.0, yb - y0), 0, 1)
            gust = 0.6 + 0.4 * math.sin(2 * math.pi * 0.07 * t + ph)
            ddx = amp * gust * hf ** 2 * math.sin(2 * math.pi * f * t + ph) + 0.2 * amp * hf ** 2 * np.sin(2 * math.pi * 2.3 * f * t + Y / 37.0)
            ddy = 0.12 * amp * hf ** 2 * np.sin(2 * math.pi * 1.7 * f * t + X / 41.0)
        elif k == "hang":
            yt = s["pivot_y"] * self.h if "pivot_y" in s else float(y0)
            hf = np.clip((Y - yt) / max(1.0, y1 - yt), 0, 1)
            gust = 0.6 + 0.4 * math.sin(2 * math.pi * 0.09 * t + ph)
            ddx = amp * gust * hf ** 1.6 * np.sin(2 * math.pi * f * t + ph - 1.2 * hf)
            ddy = zero
        elif k == "swing":
            px_, py_ = s["pivot"][0] * self.w, s["pivot"][1] * self.h
            if s.get("side"):
                a = math.radians(s["side"] * s.get("deg", 6.0) * 0.5 * (1 - math.cos(2 * math.pi * f * t + ph)))
            else:
                a = math.radians(s.get("deg", 6.0) * math.sin(2 * math.pi * f * t + ph))
            c, sn = math.cos(-a), math.sin(-a)
            sx = c * (X - px_) - sn * (Y - py_) + px_
            sy = sn * (X - px_) + c * (Y - py_) + py_
            ddx, ddy = X - sx, Y - sy
        elif k == "flame":
            yb = float(y1)
            hf = np.clip((yb - Y) / max(1.0, yb - y0), 0, 1)
            n1 = math.sin(2 * math.pi * 3.1 * t + ph) + 0.6 * math.sin(2 * math.pi * 5.3 * t + 1.7 * ph)
            ddx = amp * hf ** 1.5 * np.sin(2 * math.pi * 4.2 * t + Y / 9.0 + ph) * 0.5
            ddy = amp * hf * 0.35 * n1
            gain = 1 + s.get("flicker", 0.18) * (0.6 * math.sin(2 * math.pi * 6.7 * t + ph) + 0.4 * math.sin(2 * math.pi * 11.3 * t + 2 * ph))
            if "ignite" in s:
                gain *= s.get("dim", 0.25) + (1 - s.get("dim", 0.25)) * smoothstep((t - s["ignite"]) / 0.45)
        elif k == "attach":
            pup = self.puppets[s["attach"]["puppet"]]
            M = pup.matrices(t)[s["attach"]["bone"]]
            Mi = np.linalg.inv(M)
            sx = Mi[0, 0] * X + Mi[0, 1] * Y + Mi[0, 2]
            sy = Mi[1, 0] * X + Mi[1, 1] * Y + Mi[1, 2]
            if s.get("deg"):
                gx, gy = s["grip"][0] * self.w, s["grip"][1] * self.h
                a = math.radians(s["deg"] * math.sin(2 * math.pi * f * t + ph))
                c, sn = math.cos(-a), math.sin(-a)
                sx, sy = c * (sx - gx) - sn * (sy - gy) + gx, sn * (sx - gx) + c * (sy - gy) + gy
            ddx, ddy = X - sx, Y - sy
        elif k == "spin":
            px_, py_ = s["axle"][0] * self.w, s["axle"][1] * self.h
            a = math.radians(s.get("rpm", 10.0) * 6.0 * t)
            c, sn = math.cos(-a), math.sin(-a)
            sx = c * (X - px_) - sn * (Y - py_) + px_
            sy = sn * (X - px_) + c * (Y - py_) + py_
            ddx, ddy = X - sx, Y - sy
        elif k == "flash":
            ddx, ddy = zero, zero
            gain = 1.0 + sum(s.get("strength", 1.2) * math.exp(-max(0.0, t - a0) / 0.12) * (t >= a0) for a0 in s.get("times", []))
        elif k == "drift":
            ddx = np.full_like(X, s.get("vx", 6.0) * t)
            ddy = np.full_like(X, s.get("vy", 0.0) * t)
        else:
            ddx, ddy = zero, zero
        return ddx.astype(np.float32), ddy.astype(np.float32), gain

    def apply(self, bg, layer, t):
        out = bg.copy()
        for it in self.items:
            if "core" not in it:
                continue
            ddx, ddy, gain = self.motion(it, t)
            X0, Y0, X1, Y1 = it["pbox"]
            if it.get("premul") is not None:
                obj = it["premul"][Y0:Y1, X0:X1]
            else:
                src = it["src"] if it.get("src") is not None else layer
                obj = (src * it["alpha"][..., None])[Y0:Y1, X0:X1]
            al = it["alpha"][Y0:Y1, X0:X1]
            mx = it["X"] - X0 - ddx
            my = it["Y"] - Y0 - ddy
            ow = cv2.remap(obj, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
            aw = np.clip(cv2.remap(al, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT), 0, 1)
            o = out[Y0:Y1, X0:X1]
            out[Y0:Y1, X0:X1] = o * (1 - aw[..., None]) + np.clip(ow, 0, None) * gain
        return out

    def sprites(self, layer, t, tex):
        for it in self.items:
            s = it["spec"]
            if s["kind"] != "birds":
                continue
            for j in range(s.get("n", 2)):
                at = s.get("at", 0.0) + j * s.get("gap", 0.6)
                u = (t - at) / s.get("dur", 5.0)
                if not 0 <= u <= 1:
                    continue
                (x0, y0), (x1, y1) = s["path"]
                x = (x0 + (x1 - x0) * u) * self.w + j * 38
                y = (y0 + (y1 - y0) * u) * self.h + 10 * math.sin(2 * math.pi * 0.6 * t + j) + j * 22
                flap = math.sin(2 * math.pi * 3.2 * t + j * 1.3)
                size = s.get("size", 18) * (1 - 0.2 * j)
                draw_bird(layer, x, y, size, flap, tex, s.get("color", (0.92, 0.9, 0.84)))
        return layer


def draw_bird(layer, x, y, size, flap, tex, color):
    h, w = layer.shape[:2]
    pad = int(size * 2)
    x0, y0 = int(x) - pad, int(y) - pad
    if x0 < 0 or y0 < 0 or x0 + 2 * pad >= w or y0 + 2 * pad >= h:
        return
    im = Image.new("L", (2 * pad * 4, 2 * pad * 4), 0)
    d = ImageDraw.Draw(im)
    c = 2 * pad * 2
    lift = flap * size * 0.55 * 4
    s4 = size * 4
    d.line([(c - s4, c - lift), (c - s4 * 0.45, c - lift * 0.3 - s4 * 0.15), (c, c)], fill=255, width=int(3.2 * 4), joint="curve")
    d.line([(c + s4, c - lift), (c + s4 * 0.45, c - lift * 0.3 - s4 * 0.15), (c, c)], fill=255, width=int(3.2 * 4), joint="curve")
    a = np.asarray(im.resize((2 * pad, 2 * pad), Image.LANCZOS), np.float32) / 255
    a = a * tex[y0:y0 + 2 * pad, x0:x0 + 2 * pad]
    reg = layer[y0:y0 + 2 * pad, x0:x0 + 2 * pad]
    layer[y0:y0 + 2 * pad, x0:x0 + 2 * pad] = np.maximum(reg, a[..., None] * np.array(color, np.float32))


def boil_textures(w, h, seed, n=BOIL_FRAMES):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        g = cv2.GaussianBlur(rng.normal(size=(h // 2, w // 2)).astype(np.float32), (0, 0), 1.1)
        g = cv2.resize(g / (g.std() + 1e-6), (w, h), interpolation=cv2.INTER_LINEAR)
        out.append((1 + BOIL_DEPTH * np.clip(g, -2, 2))[..., None].astype(np.float32))
    return out


class Stage:
    def __init__(self, chalk_layer, puppets, elements, fill, seed=0):
        self.layer = chalk_layer
        self.puppets = puppets
        self.elements = elements
        h, w = chalk_layer.shape[:2]
        self.boil = boil_textures(w, h, seed)
        self.tex = cv2.GaussianBlur(np.random.default_rng(seed + 5).uniform(0.55, 1.0, (h, w)).astype(np.float32), (0, 0), 0.6)
        self.bg = chalk_layer

    def frame(self, t, fidx):
        out = self.elements.apply(self.bg, self.layer, t) if self.elements else self.bg.copy()
        for p in self.puppets:
            lay, a = p.render(self.layer, t)
            out = out * (1 - a[..., None]) + lay
        if self.elements:
            out = self.elements.sprites(out, t, self.tex)
        return out * self.boil[(fidx // BOIL_FRAMES) % len(self.boil)]


def build(chalk_layer, puppet_specs, element_specs, seed=0, fg=None, plate=None, underlays=None):
    h, w = chalk_layer.shape[:2]
    pups = [Puppet(p, w, h, fg) for p in puppet_specs]
    for p in pups:
        p.underlay = (underlays or {}).get(p.spec.get("name"))
    els = Elements(element_specs, w, h, seed) if element_specs else None
    if els:
        els.puppets = {p.spec.get("name"): p for p in pups}
    A = np.zeros((h, w), np.float32)
    for p in pups:
        p.refine(chalk_layer)
        A = np.maximum(A, np.maximum(p.hole, (p.fig > 0.3).astype(np.float32)))
    Ap = A.copy()
    inkm = chalk_layer.max(axis=2) > 0.06
    if els and pups:
        pre = Elements(element_specs, w, h, seed)
        pre.puppets = els.puppets
        pre.refine(chalk_layer, None, None)
        objcol = np.zeros((h, w), bool)
        for it in pre.items:
            if "core" in it and ("saturation_min" in it["spec"] or "saturation_max" in it["spec"]) and "attach" not in it["spec"]:
                objcol |= it["core"] > 0.5
        els.precore = objcol
        for p in pups:
            notfig = ~p.fgraw if p.fgraw is not None else np.ones((h, w), bool)
            outside = np.ones((h, w), bool)
            for k in p.z:
                outside &= p.core[k] < 0.5
            steal = objcol & (notfig | outside)
            for it in pre.items:
                if "core" in it and it["spec"].get("attach", {}).get("puppet") == p.spec.get("name"):
                    steal |= it["core"] > 0.5
            p.fig = p.fig * (1 - cv2.dilate(steal.astype(np.uint8), np.ones((5, 5), np.uint8)))
    if pups:
        figany = np.zeros((h, w), bool)
        for p in pups:
            figany |= p.fig > 0.5
        lines = scenery_lines(chalk_layer, extend=260, figure=figany)
        for p in pups:
            if p.fgraw is None:
                continue
            fgd = cv2.dilate(p.fgraw.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
            fig = p.fig > 0.5
            n, lab = cv2.connectedComponents(lines.astype(np.uint8), 8)
            bad = np.zeros((h, w), bool)
            core = np.zeros((h, w), bool)
            for k in p.z:
                core |= p.core[k] > 0.5
            for i in range(1, n):
                comp = lab == i
                inside = comp & cv2.dilate(fig.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
                out = comp & ~fgd
                if inside.any() and out.sum() > 60 and out.sum() > 0.35 * comp.sum():
                    bad |= comp
            bad |= lines & ~fgd
            bad &= cv2.dilate(fig.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
            p.fig = p.fig * (1 - cv2.dilate(bad.astype(np.uint8), np.ones((3, 3), np.uint8)))
            p.scenery = bad
    for p in pups:
        p.motion_band = int(np.clip(p.max_motion() * 1.15 + 6, 8, 70))
    for i, p in enumerate(pups):
        for q in pups[i + 1:]:
            p.fig = p.fig * (1 - ((q.fig > 0.5) & inkm))
    for i, p in enumerate(pups):
        ext = np.zeros((h, w), bool)
        for q in pups[i + 1:]:
            ext |= q.fig > 0.5
        p.front_ext = ext
        p.build_mesh()
    if els:
        figs = np.zeros((h, w), np.float32)
        for p in pups:
            figs = np.maximum(figs, (p.fig > 0.5).astype(np.float32))
        els.refine(chalk_layer, figs, plate)
        A = np.maximum(A, els.hole())
    obj = np.zeros((h, w), np.float32)
    for p in pups:
        m = (p.fig > 0.5).astype(np.float32)
        if p.fgraw is not None:
            m = np.maximum(m * p.fgraw, (p.fig > 0.5) * (chalk_layer.max(axis=2) > 0.06))
        obj = np.maximum(obj, m)
    if els:
        for it in els.items:
            if "core" in it and it["spec"]["kind"] != "flame":
                cl = it.get("claim", it["core"]) if "saturation_max" in it["spec"] else it["core"]
                obj = np.maximum(obj, np.maximum(it["alpha"] > 0.5, cl > 0.5).astype(np.float32))
    obj = cv2.GaussianBlur(cv2.dilate(obj, np.ones((5, 5), np.uint8)), (0, 0), 1.5)
    A = A * obj
    for p in pups:
        if getattr(p, "scenery", None) is not None:
            A = A * (1 - cv2.dilate(p.scenery.astype(np.uint8), np.ones((3, 3), np.uint8)))
    telea = fill_holes(chalk_layer, A, seed, gain=1.0) if A.any() else np.zeros_like(chalk_layer)
    fill = telea
    if plate is not None and A.any():
        fill = reconcile(chalk_layer, plate, telea, Ap * obj, obj)
    for p in pups:
        if p.underlay is None:
            continue
        reg = np.zeros((h, w), np.uint8)
        for mm in p.meshes:
            if mm["bone"] in p.spec.get("underlay_parts", []):
                reg |= (mm["own"] > 0.2).astype(np.uint8)
        reg = cv2.GaussianBlur(cv2.dilate(reg, np.ones((7, 7), np.uint8)).astype(np.float32), (0, 0), 1.5)[..., None]
        fill = fill * (1 - reg) + p.underlay * reg
    cover = np.zeros((h, w), np.float32)
    for p in pups:
        p.frozen = True
        cover = np.maximum(cover, p.render(chalk_layer, 0.0)[1])
        p.frozen = False
    if els:
        for it in els.items:
            if "core" in it:
                cover = np.maximum(cover, it["alpha"])
    A = A * cv2.dilate((cover > 0.02).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32)
    dark = (chalk_layer.max(axis=2) < 0.12) & (cover < 0.5)
    A = A * (1 - cv2.GaussianBlur(dark.astype(np.float32), (0, 0), 0.8))
    st = Stage(chalk_layer, pups, els, fill, seed)
    st.bg = chalk_layer * (1 - A[..., None]) + fill * A[..., None]
    st.holes = A
    st.plate = plate
    if els:
        els.rematte(st.bg, chalk_layer)
    return st


def reconcile(layer, plate, telea, A, obj):
    hard = (A > 0.3).astype(np.uint8)
    n, lab = cv2.connectedComponents(cv2.dilate(hard, np.ones((5, 5), np.uint8)), 8)
    out = telea.copy()
    vis = (obj < 0.2) & (A < 0.05)
    for i in range(1, n):
        comp = (lab == i).astype(np.uint8)
        ring = (cv2.dilate(comp, np.ones((15, 15), np.uint8)) > 0) & (comp == 0) & vis
        if ring.sum() < 20:
            continue
        d = float(np.abs(plate[ring] - layer[ring]).max(axis=1).mean())
        if d < 0.06 and comp.sum() > 2500:
            m = comp.astype(bool)
            out[m] = plate[m]
    return out


def fill_holes(layer, hole, seed=0, gain=0.5):
    h, w = hole.shape
    m = (hole > 0.05).astype(np.uint8)
    if not m.any():
        return np.zeros_like(layer)
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    u8 = (np.clip(layer, 0, 1) * 255).astype(np.uint8)
    filled = cv2.inpaint(u8, m, 9, cv2.INPAINT_TELEA).astype(np.float32) / 255
    soft = cv2.GaussianBlur(filled, (0, 0), 2.0)
    grain = np.random.default_rng(seed).uniform(0.6, 1.0, (h, w)).astype(np.float32)
    grain = cv2.GaussianBlur(grain, (0, 0), 0.7)[..., None]
    return soft * grain * gain
