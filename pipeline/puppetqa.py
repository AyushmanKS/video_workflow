import json
import math

import cv2
import numpy as np

LIMITS = [("khand", 8.0), ("hand", 12.0), ("head", 16.0), ("neck", 16.0), ("torso", 6.0), ("legs", 0.5), ("upper", 22.0), ("fore", 28.0), ("scarf", 22.0), ("cloth", 22.0), ("arm", 22.0)]
INK = 0.12
MOVE = 1.0
POP = 9.0
CONTACT = 1.2
ORPHAN_MAX = 1500
EXPOSED_MAX = 700
BOARD_LUM = 0.2
CHECKS = [
    ("joint_gap", "a body part pulls away from its pivot (for example a head sliding off the neck)"),
    ("unpivoted_motion", "a part slides instead of turning about its pivot (only hips and torso may shift, and only a few px)"),
    ("object_without_pivot", "a moving object has no declared pivot (flag pole, hinge, chain point, axle, holding hand)"),
    ("line_captured", "a straight scenery line (pole, rail, pillar edge) belongs to a moving character's cut-out"),
    ("body_gap", "while moving, a gap or crack opens inside a character's silhouette"),
    ("object_captured", "a character's cut-out contains pixels of another object (that object would move with the character)"),
    ("split_surface", "one continuous drawn surface is split between two moving characters"),
    ("rest_fidelity", "before anything moves, the frame does not reproduce the original drawing"),
    ("torn_stroke", "a chalk line crosses from a moving piece into a still one (object cut in two)"),
    ("orphan_fragment", "a small piece of a moving object stays behind"),
    ("fold", "the mesh folds over or is crushed / stretched beyond what cloth and skin allow"),
    ("exposed_patch", "a filled background patch becomes visible"),
    ("joint_limit", "a joint turns further than a body can"),
    ("pop", "something jumps between two frames"),
    ("contact_drift", "a resting hand, planted foot or seated body slides"),
    ("double_owner", "one drawn pixel belongs to two moving objects"),
    ("lost_ink", "a moving object loses part of its drawing while it moves (shredded or hollowed)"),
    ("background_seam", "an uncovered area does not continue the drawing around it (wrong or mismatched background)"),
]


def limit_for(bone):
    for key, lim in LIMITS:
        if key in bone:
            return lim
    return 20.0


def owners(stage):
    out = []
    for p in stage.puppets:
        out.append({"name": p.spec.get("name", "puppet"), "alpha": p.fig, "disp": p.src_disp, "puppet": p})
    if stage.elements:
        for i, it in enumerate(stage.elements.items):
            if "core" not in it:
                continue

            def disp(t, it=it):
                ddx, ddy, _ = stage.elements.motion(it, t)
                X0, Y0, X1, Y1 = it["pbox"]
                D = np.zeros(stage.layer.shape[:2] + (2,), np.float32)
                D[Y0:Y1, X0:X1, 0] = ddx
                D[Y0:Y1, X0:X1, 1] = ddy
                return D

            out.append({"name": f"{it['spec']['kind']}#{i}", "alpha": it["alpha"], "disp": disp, "element": it})
    return out


def stroke_field(lum):
    g = cv2.GaussianBlur(lum, (0, 0), 1.2)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    jxx = cv2.GaussianBlur(gx * gx, (0, 0), 3)
    jyy = cv2.GaussianBlur(gy * gy, (0, 0), 3)
    jxy = cv2.GaussianBlur(gx * gy, (0, 0), 3)
    tr = jxx + jyy
    det = np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2)
    coh = det / np.maximum(tr, 1e-6)
    ang = 0.5 * np.arctan2(2 * jxy, jxx - jyy)
    return np.cos(ang + math.pi / 2), np.sin(ang + math.pi / 2), coh


def boxes(mask, min_px):
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(mask.astype(np.uint8), np.ones((9, 9), np.uint8)), 8)
    out = []
    for i in range(1, n):
        x, y, w, h, a = st[i]
        px = int((mask & (lab == i)).sum())
        if px >= min_px:
            out.append((int(x), int(y), int(x + w), int(y + h), px))
    return out


def plain_board(stage, layer, holes, ex, box):
    x0, y0, x1, y1 = box
    r = 24
    X0, Y0, X1, Y1 = max(0, x0 - r), max(0, y0 - r), min(layer.shape[1], x1 + r), min(layer.shape[0], y1 + r)
    patch = ex[Y0:Y1, X0:X1]
    fill = stage.bg[Y0:Y1, X0:X1][patch]
    ring = ~holes[Y0:Y1, X0:X1] & ~cv2.dilate(patch.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    orig = layer[Y0:Y1, X0:X1][ring]
    if len(fill) < 40 or len(orig) < 40:
        return False
    flum, olum = fill.max(axis=1), orig.max(axis=1)
    board = olum < BOARD_LUM
    if board.mean() < 0.5:
        return False
    return float(flum.mean()) < BOARD_LUM and float(flum.std()) < 0.05 and float(np.abs(fill.mean(0) - orig[board].mean(0)).max()) < 0.05


def check(stage, span, fps=30, step=0.1):
    layer = stage.layer
    h, w = layer.shape[:2]
    lum = layer.max(axis=2)
    ink = lum > INK
    own = owners(stage)
    times = np.arange(0, span, step)
    issues = []
    peak = {o["name"]: (0.0, 0.0) for o in own}
    maxd = np.zeros((h, w), np.float32)
    moving_owner = np.zeros((h, w), bool)
    for o in own:
        md = np.zeros((h, w), np.float32)
        for t in times:
            D = o["disp"](t)
            m = np.hypot(D[..., 0], D[..., 1]) * (o["alpha"] > 0.5)
            md = np.maximum(md, m)
            v = float(m.max())
            if v > peak[o["name"]][1]:
                peak[o["name"]] = (float(t), v)
        o["maxd"] = md
        maxd = np.maximum(maxd, md)
        if peak[o["name"]][1] > MOVE:
            moving_owner |= o["alpha"] > 0.5
    count = np.zeros((h, w), np.int32)
    for o in own:
        if peak[o["name"]][1] > MOVE:
            claim = o["element"]["core"] if "element" in o else o["alpha"]
            count += ((claim > 0.5) & ink).astype(np.int32)
    for x0, y0, x1, y1, px in boxes(count > 1, 30):
        issues.append({"check": "double_owner", "box": [x0, y0, x1, y1], "pixels": px, "t": None})
    moving = moving_owner & (maxd > MOVE)
    bgink = (stage.bg.max(axis=2) > INK) if hasattr(stage, "bg") else ink
    still_ink = ink & bgink & ~moving_owner
    ring = cv2.dilate(moving.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~moving_owner
    near = cv2.dilate(maxd, np.ones((9, 9), np.uint8))
    sx, sy, coh = stroke_field(lum)
    mb = cv2.GaussianBlur(moving.astype(np.float32), (0, 0), 3)
    nx = cv2.Sobel(mb, cv2.CV_32F, 1, 0, ksize=5)
    ny = cv2.Sobel(mb, cv2.CV_32F, 0, 1, ksize=5)
    nn = np.hypot(nx, ny) + 1e-6
    mv = moving.astype(np.float32)
    mcol = cv2.GaussianBlur(layer * mv[..., None], (0, 0), 3) / np.maximum(cv2.GaussianBlur(mv, (0, 0), 3), 1e-3)[..., None]
    same = np.linalg.norm(layer - mcol, axis=2) < 0.12
    figure = np.zeros((h, w), bool)
    for o in own:
        p = o.get("puppet")
        if p is not None and p.fgraw is not None and peak[o["name"]][1] > MOVE:
            hull = np.zeros((h, w), np.float32)
            for k in p.z:
                hull = np.maximum(hull, p.core[k])
            figure |= p.fgraw & (hull > 0.5)
    gap = ring & still_ink & figure & same & (near > 1.5)
    cross = ring & still_ink & ~figure & same & (coh > 0.45) & (np.abs(sx * nx / nn + sy * ny / nn) > 0.72) & (near > 1.5)
    for x0, y0, x1, y1, px in boxes(gap, 12):
        issues.append({"check": "torn_stroke", "box": [x0, y0, x1, y1], "pixels": px, "t": None, "who": "figure gap"})
    for x0, y0, x1, y1, px in boxes(cross, 10):
        issues.append({"check": "torn_stroke", "box": [x0, y0, x1, y1], "pixels": px, "t": None, "who": "object cut"})
    n, lab, st, _ = cv2.connectedComponentsWithStats(still_ink.astype(np.uint8), 8)
    touch = np.unique(lab[ring & still_ink])
    for i in touch:
        if i == 0:
            continue
        x, y, ww, hh, a = st[i]
        if 15 <= a <= ORPHAN_MAX:
            comp = lab[y:y + hh, x:x + ww] == i
            col = layer[y:y + hh, x:x + ww][comp].mean(0)
            mc = mcol[y:y + hh, x:x + ww][comp].mean(0)
            if float(near[y:y + hh, x:x + ww][comp].max()) > 2.0 and (np.linalg.norm(col - mc) < 0.15 or figure[y:y + hh, x:x + ww][comp].any()):
                issues.append({"check": "orphan_fragment", "box": [int(x), int(y), int(x + ww), int(y + hh)], "pixels": int(a), "t": None})
    dense = np.arange(0, span, 1 / fps)
    import puppet as _pp2
    R = _pp2.rigs()["rules"]
    need = {"flag": "anchor", "hang": "pivot_y", "swing": "pivot", "attach": "attach", "spin": "axle"}
    if stage.elements:
        for it in stage.elements.items:
            k = it["spec"]["kind"]
            if k in need and need[k] not in it["spec"]:
                x0, y0, x1, y1 = it.get("box", (0, 0, 10, 10))
                issues.append({"check": "object_without_pivot", "box": [x0, y0, x1, y1], "t": 0.0, "who": f"{k} has no {need[k]}"})
    for p in stage.puppets:
        name = p.spec.get("name", "puppet")
        for a in p.spec.get("actions", []):
            if "shift" in a and a.get("bone") not in R["shift_allowed"]:
                bx, by = p.bones[a["bone"]]["a"]
                issues.append({"check": "unpivoted_motion", "box": [int(bx) - 30, int(by) - 30, int(bx) + 30, int(by) + 30], "t": round(float(a.get("at", 0.0)), 2), "who": f"{name}:{a['bone']} slides instead of turning about its pivot"})
            if "shift" in a and max(abs(a["shift"][0]) * w, abs(a["shift"][1]) * h) > R["shift_max_px"]:
                bx, by = p.bones[a["bone"]]["a"]
                issues.append({"check": "unpivoted_motion", "box": [int(bx) - 30, int(by) - 30, int(bx) + 30, int(by) + 30], "t": round(float(a.get("at", 0.0)), 2), "who": f"{name}:{a['bone']} shift too large"})
        worstgap = {}
        for t in dense:
            M = p.matrices(t)
            for k, b in p.bones.items():
                par = b["parent"]
                if not par or p.spec["bones"][k].get("pin"):
                    continue
                pa = np.array([b["a"][0], b["a"][1], 1.0])
                g = float(np.hypot(*((M[k] @ pa) - (M[par] @ pa))[:2]))
                if g > R["joint_gap_max_px"] and g > worstgap.get(k, (0, 0))[1]:
                    worstgap[k] = (float(t), g)
        for k, (t, g) in worstgap.items():
            bx, by = p.bones[k]["a"]
            issues.append({"check": "joint_gap", "box": [int(bx) - 30, int(by) - 30, int(bx) + 30, int(by) + 30], "t": round(t, 2), "who": f"{name}:{k} pulls {g:.1f}px off its pivot"})
        a0 = tri_area(p.pts, p.tri)
        cen = p.pts[p.tri].mean(1).astype(int)
        visible = np.concatenate([mm["own"][mm["pts"][mm["tri"]].mean(1).astype(int)[:, 1], mm["pts"][mm["tri"]].mean(1).astype(int)[:, 0]] > 0.5 for mm in p.meshes]) & (np.abs(a0) > 6.0)
        bi = {k: j for j, k in enumerate(p.order)}
        prev = None
        worst = {}
        for t in dense:
            d = p.deform(t)
            r = tri_area(d, p.tri) / np.where(np.abs(a0) < 1e-6, 1e-6, a0)
            bad = ((r < 0.55) | (r > 1.8)) & visible
            if bad.sum() >= 3 or ((r < 0.35) & visible).any():
                c = p.pts[p.tri[bad]].reshape(-1, 2)
                worst.setdefault("fold", (t, c))
            if prev is not None:
                v = np.hypot(*(d - prev).T)
                if v.max() > POP:
                    worst.setdefault("pop", (t, p.pts[[int(v.argmax())]]))
            for b in p.spec.get("contact", []) + [k for k in p.bones if k == "legs"]:
                sel = p.W[:, bi[b]] > 0.95 if b in bi else np.zeros(len(p.pts), bool)
                if sel.any():
                    dd = np.hypot(*(d[sel] - p.pts[sel]).T)
                    if dd.max() > CONTACT:
                        worst.setdefault(f"contact:{b}", (t, p.pts[sel][[int(dd.argmax())]]))
            prev = d
            ang = p.angles(t)[0]
            for b, v in ang.items():
                if abs(v) > float(p.spec["bones"][b].get("limit", limit_for(b))):
                    worst.setdefault(f"limit:{b}", (t, np.array([p.bones[b]["a"]]), v))
        for key, val in worst.items():
            t, c = val[0], val[1]
            x0, y0 = c.min(0) - 30
            x1, y1 = c.max(0) + 30
            chk = "fold" if key == "fold" else "pop" if key == "pop" else "contact_drift" if key.startswith("contact") else "joint_limit"
            issue = {"check": chk, "box": [int(max(0, x0)), int(max(0, y0)), int(min(w, x1)), int(min(h, y1))], "t": round(float(t), 2), "who": f"{name}:{key}"}
            if chk == "joint_limit":
                issue["angle"] = round(float(val[2]), 1)
                issue["limit"] = float(p.spec["bones"][key.split(":")[1]].get("limit", limit_for(key.split(":")[1])))
            issues.append(issue)
    worst_split = np.zeros((h, w), bool)
    split_t = {}
    for t in times[::3]:
        D = np.zeros((h, w, 2), np.float32)
        who = np.full((h, w), -1, np.int32)
        for j, o in enumerate(own):
            m = o["alpha"] > 0.5
            d = o["disp"](float(t))
            D[m] = d[m]
            who[m] = j
        for dy, dx in ((0, 1), (1, 0)):
            a = D[: h - dy, : w - dx]
            b = D[dy:, dx:]
            jump = np.hypot(*(a - b).transpose(2, 0, 1)) > 2.0
            wa, wb = who[: h - dy, : w - dx], who[dy:, dx:]
            ia, ib = ink[: h - dy, : w - dx], ink[dy:, dx:]
            col = np.abs(layer[: h - dy, : w - dx] - layer[dy:, dx:]).max(axis=2) < 0.1
            figs = np.array([("puppet" in o) for o in own] + [False])
            both_fig = figs[wa] & figs[wb] & (wa != wb) & (wa >= 0) & (wb >= 0)
            sp = jump & ia & ib & col & both_fig
            if sp.any():
                worst_split[: h - dy, : w - dx] |= sp
                split_t.setdefault("t", float(t))
    for x0, y0, x1, y1, px in boxes(worst_split, 15):
        issues.append({"check": "split_surface", "box": [x0, y0, x1, y1], "pixels": px, "t": round(split_t.get("t", 0.0), 2), "who": "one surface torn between two characters"})
    for i in issues:
        if i["t"] is None:
            x0, y0, x1, y1 = i["box"]
            best = max(own, key=lambda o: float(o["maxd"][max(0, y0 - 10):y1 + 10, max(0, x0 - 10):x1 + 10].max()))
            i["t"] = round(peak[best["name"]][0], 2)
            i.setdefault("who", best["name"])
    for p in stage.puppets:
        p.frozen = True
    if stage.elements:
        stage.elements.frozen = True
    rest = np.clip(stage.frame(0.0, 0) / stage.boil[0], 0, None)
    for p in stage.puppets:
        p.frozen = False
    if stage.elements:
        stage.elements.frozen = False
    diff = cv2.GaussianBlur(np.abs(rest - layer).max(axis=2), (0, 0), 1.5)
    tol = 0.08
    blob = cv2.morphologyEx((diff > tol).astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)).astype(bool)
    for x0, y0, x1, y1, px in boxes(blob, 60):
        issues.append({"check": "rest_fidelity", "box": [x0, y0, x1, y1], "pixels": px, "t": 0.0, "who": "rest frame differs from the drawing"})

    def own_ink(o, t):
        if "puppet" in o:
            lay, acc = o["puppet"].render(layer, t)
            return int(((lay.max(axis=2) > INK) & (acc > 0.5)).sum())
        it = o["element"]
        ddx, ddy, _ = stage.elements.motion(it, t)
        X0, Y0, X1, Y1 = it["pbox"]
        if it.get("premul") is not None:
            obj = it["premul"][Y0:Y1, X0:X1]
        else:
            src = it["src"] if it.get("src") is not None else layer
            obj = (src * it["alpha"][..., None])[Y0:Y1, X0:X1]
        mx, my = it["X"] - X0 - ddx, it["Y"] - Y0 - ddy
        ow = cv2.remap(obj, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        aw = cv2.remap(it["alpha"][Y0:Y1, X0:X1], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        return int(((ow.max(axis=2) > INK) & (aw > 0.5)).sum())

    for o in own:
        if peak[o["name"]][1] <= MOVE:
            continue
        base = own_ink(o, 0.0)
        if base < 200:
            continue
        for t in times[::2]:
            cur = own_ink(o, float(t))
            tol = 0.15 if "element" in o and o["element"]["spec"]["kind"] in ("flag", "hang", "sway") else 0.06
            if abs(cur - base) / base > tol:
                ys, xs = np.nonzero(o["alpha"] > 0.5)
                issues.append({"check": "lost_ink", "box": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())], "t": round(float(t), 2), "who": f"{o['name']} {(cur - base) / base:+.0%}"})
                break
    figs = np.zeros((h, w), bool)
    for p in stage.puppets:
        figs |= p.fig > 0.5
    import puppet as _pp
    lines = _pp.scenery_lines(layer)
    for p in stage.puppets:
        if p.fgraw is None:
            continue
        fgd = cv2.dilate(p.fgraw.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        cap = lines & ~fgd & (p.fig > 0.5) & ink
        for x0, y0, x1, y1, px in boxes(cap, 20):
            issues.append({"check": "line_captured", "box": [x0, y0, x1, y1], "pixels": px, "t": 0.0, "who": f"a background line is part of {p.spec.get('name')}'s cut-out"})
    pre = getattr(stage.elements, "precore", None) if stage.elements else None
    if pre is not None:
        cap = pre & figs & ink
        for x0, y0, x1, y1, px in boxes(cap, 25):
            issues.append({"check": "object_captured", "box": [x0, y0, x1, y1], "pixels": px, "t": 0.0, "who": "a character cut-out contains another object's pixels"})
    if stage.puppets and hasattr(stage, "holes"):
        Hh = stage.holes > 0.3
        under = np.zeros((h, w), bool)
        for p in stage.puppets:
            cnt = np.zeros((h, w), np.int32)
            for k in p.z:
                cnt += (p.core[k] > 0.5).astype(np.int32)
            under |= cnt >= 2
            if getattr(p, "front_ext", None) is not None:
                under |= p.front_ext & (cnt > 0)
        under = cv2.erode(under.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        found = []
        for t in times:
            cover = np.zeros((h, w), np.float32)
            for p in stage.puppets:
                cover = np.maximum(cover, p.render(layer, float(t))[1])
            gap = (cover < 0.3) & Hh & ink & under & (np.abs(stage.bg - layer).max(axis=2) > 0.08)
            gap = cv2.morphologyEx(gap.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
            for bx in boxes(gap, 40):
                found.append((float(t), bx))
        for t, (x0, y0, x1, y1, px) in found:
            issues.append({"check": "body_gap", "box": [x0, y0, x1, y1], "pixels": px, "t": round(t, 2), "who": "body surface uncovered with nothing behind it"})
    if hasattr(stage, "holes"):
        Hm = (stage.holes > 0.3).astype(np.uint8)
        n, lab = cv2.connectedComponents(cv2.dilate(Hm, np.ones((5, 5), np.uint8)), 8)
        bgb = cv2.GaussianBlur(stage.bg, (0, 0), 2)
        orig = cv2.GaussianBlur(layer, (0, 0), 2)
        vis = ~moving_owner & (Hm == 0)
        for i in range(1, n):
            comp = (lab == i).astype(np.uint8)
            inner = (comp > 0) & (cv2.erode(comp, np.ones((7, 7), np.uint8)) == 0)
            outer = (cv2.dilate(comp, np.ones((7, 7), np.uint8)) > 0) & (comp == 0) & vis
            if inner.sum() < 40 or outer.sum() < 40:
                continue
            d = float(np.abs(bgb[inner].mean(0) - orig[outer].mean(0)).max())
            if d > 0.12:
                ys, xs = np.nonzero(comp)
                issues.append({"check": "background_seam", "box": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())], "t": 0.0, "who": f"jump {d:.2f}"})
    if hasattr(stage, "holes") and getattr(stage, "plate", None) is None:
        H = stage.holes > 0.5
        for t in times:
            cover = np.zeros((h, w), np.float32)
            for p in stage.puppets:
                cover = np.maximum(cover, p.render(layer, t)[1])
            if stage.elements:
                for it in stage.elements.items:
                    if "core" not in it:
                        continue
                    ddx, ddy, _ = stage.elements.motion(it, t)
                    X0, Y0, X1, Y1 = it["pbox"]
                    al = it["alpha"][Y0:Y1, X0:X1]
                    aw = cv2.remap(al, it["X"] - X0 - ddx, it["Y"] - Y0 - ddy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
                    cover[Y0:Y1, X0:X1] = np.maximum(cover[Y0:Y1, X0:X1], aw)
            changed = np.abs(stage.bg - layer).max(axis=2) > 0.08
            ex = (H & (cover < 0.3) & changed).astype(np.uint8)
            thick = cv2.distanceTransform(ex, cv2.DIST_L2, 3) > 4
            ex = ex.astype(bool) & cv2.dilate(thick.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
            for x0, y0, x1, y1, px in boxes(ex, EXPOSED_MAX):
                if plain_board(stage, layer, H, ex, (x0, y0, x1, y1)):
                    continue
                issues.append({"check": "exposed_patch", "box": [x0, y0, x1, y1], "pixels": px, "t": round(float(t), 2)})
        issues = dedupe(issues)
    return issues


def tri_area(p, tri):
    a, b, c = p[tri[:, 0]], p[tri[:, 1]], p[tri[:, 2]]
    return 0.5 * ((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (c[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1]))


def dedupe(issues):
    out, seen = [], set()
    for i in issues:
        k = (i["check"], tuple(np.array(i["box"]) // 40))
        if k in seen:
            continue
        seen.add(k)
        out.append(i)
    return out


def sheet(stage, issues, board, path, scale=0.5):
    tiles = []
    for n, i in enumerate(issues[:24]):
        x0, y0, x1, y1 = i["box"]
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        r = max(90, (x1 - x0) // 2 + 40, (y1 - y0) // 2 + 40)
        X0, Y0 = max(0, cx - r), max(0, cy - r)
        X1, Y1 = min(stage.layer.shape[1], cx + r), min(stage.layer.shape[0], cy + r)
        row = []
        frames = []
        if i["check"] == "rest_fidelity":
            for p in stage.puppets:
                p.frozen = True
            if stage.elements:
                stage.elements.frozen = True
            frames = [stage.layer, stage.frame(0.0, 0) / stage.boil[0]]
            for p in stage.puppets:
                p.frozen = False
            if stage.elements:
                stage.elements.frozen = False
        else:
            frames = [stage.frame(t, 0) / stage.boil[0] for t in (0.0, i["t"] if i["t"] is not None else 0.0)]
        for fr in frames:
            f = np.clip(board + fr, 0, 1)[Y0:Y1, X0:X1]
            f = (cv2.resize(f, (260, 260)) * 255).astype(np.uint8).copy()
            sx, sy = 260 / (X1 - X0), 260 / (Y1 - Y0)
            cv2.rectangle(f, (int((x0 - X0) * sx), int((y0 - Y0) * sy)), (int((x1 - X0) * sx), int((y1 - Y0) * sy)), (255, 40, 40), 2)
            row.append(f)
        lab = np.zeros((26, 520, 3), np.uint8)
        cv2.putText(lab, f"{n + 1}. {i['check']} {i.get('who', '')} t={i['t']}", (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 0), 1)
        tiles.append(np.concatenate([lab, np.concatenate(row, 1)], 0))
    if not tiles:
        return None
    cols = 3
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.concatenate(tiles[k:k + cols], 1) for k in range(0, len(tiles), cols)]
    cv2.imwrite(str(path), cv2.cvtColor(np.concatenate(rows, 0), cv2.COLOR_RGB2BGR))
    return path


def waive(issues, waivers, w, h):
    keep, waived = [], []
    for i in issues:
        x0, y0, x1, y1 = i["box"]
        cx, cy = (x0 + x1) / 2 / w, (y0 + y1) / 2 / h
        hit = next((v for v in waivers if v["check"] == i["check"] and v["box"][0] <= cx <= v["box"][2] and v["box"][1] <= cy <= v["box"][3]), None)
        if hit:
            waived.append(dict(i, reason=hit["reason"]))
        else:
            keep.append(i)
    return keep, waived


def report(issues):
    by = {}
    for i in issues:
        by.setdefault(i["check"], 0)
        by[i["check"]] += 1
    return {"pass": not issues, "counts": by, "checklist": [{"check": c, "what": d, "found": by.get(c, 0)} for c, d in CHECKS]}


def rig_sheet(stage, board, path):
    from PIL import Image, ImageDraw

    img = Image.fromarray((np.clip(board + stage.layer, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    cols = [(255, 80, 80), (80, 200, 255), (120, 255, 120), (255, 200, 60)]
    for n, p in enumerate(stage.puppets):
        c = cols[n % len(cols)]
        for k in p.z:
            m = (p.core[k] > 0.5).astype(np.uint8)
            cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for ct in cs:
                d.line([tuple(q[0]) for q in ct] + [tuple(ct[0][0])], fill=c, width=2)
        for k, b in p.bones.items():
            d.line([tuple(b["a"]), tuple(b["b"])], fill=(255, 255, 255), width=3)
            x, y = b["a"]
            r = 9 if p.spec["bones"][k].get("pin") else 7
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 0), width=3, fill=(255, 60, 60) if p.spec["bones"][k].get("pin") else None)
            d.text((x + 10, y - 8), f"{p.spec['bones'][k].get('joint', k)}", fill=(255, 255, 0))
    if stage.elements:
        for it in stage.elements.items:
            s = it["spec"]
            pv = s.get("anchor") or s.get("pivot") or s.get("axle") or s.get("grip")
            if pv:
                x, y = pv[0] * stage.layer.shape[1], pv[1] * stage.layer.shape[0]
                d.rectangle([x - 7, y - 7, x + 7, y + 7], outline=(0, 255, 255), width=3)
                d.text((x + 10, y - 8), s["kind"], fill=(0, 255, 255))
            elif "pivot_y" in s and "box" in it:
                x0, y0, x1, y1 = it["box"]
                yy = s["pivot_y"] * stage.layer.shape[0]
                d.line([(x0, yy), (x1, yy)], fill=(0, 255, 255), width=3)
    img.resize((img.width // 2, img.height // 2)).save(path)
    return path
