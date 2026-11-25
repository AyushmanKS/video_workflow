import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def preview(work, scene, dst, style="marionette", seed=42, fps=15, scale=0.5):
    sys.path.insert(0, str(ROOT))
    import numpy as np
    from PIL import Image

    import chalk
    import puppetstudio as P
    import studio

    work = Path(work)
    script = json.loads((work / "script.json").read_text())
    st = studio.effective_style(style, script)
    chalk.use_fonts(script.get("fonts", "mac"))
    P.MARIONETTE["flag"] = P.is_marionette(script)
    P.puppet.FILL_GRAIN["on"] = not P.MARIONETTE["flag"]
    timings, total, _, _ = studio.scene_timings(script, work)
    pl = chalk.plan(script, timings, total)
    rig = P.load_rig(work)
    shot = P.shot_for(rig, scene)
    span = P.scene_span(pl, scene)
    s = P.resolve(shot, timings, pl[scene]["vs"], span)
    raw = studio.raw_path(script, work, scene)
    mask = work / "img" / f"{studio.scene_still(script, scene):02d}_mask.png"
    stage = P.build_scene(script, work, scene, seed, raw, mask, s)
    w, h = int(P.CW * scale) // 2 * 2, int(P.CH * scale) // 2 * 2
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
                             "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "20", str(dst)], stdin=subprocess.PIPE)
    n = int(span * fps)
    for f in range(n):
        u = f / fps
        img = Image.fromarray((np.clip(stage.frame(u, int(u * 30)), 0, 1) * 255).astype(np.uint8))
        P.draw_strings(img, stage, u, 1.0, 0.0, 0.0)
        proc.stdin.write(np.asarray(img.resize((w, h))).tobytes())
    proc.stdin.close()
    proc.wait()
    return dst


if __name__ == "__main__":
    print(preview(sys.argv[1], int(sys.argv[2]), sys.argv[3]))
