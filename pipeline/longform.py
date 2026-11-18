import json
import sys

from . import CONTENT, ROOT

PART_WORD = {"en": "Part", "hi": "भाग", "te": "భాగం"}
INTRO_WORD = {"en": "Opening", "hi": "शुरुआत", "te": "ప్రారంభం"}


def stamp(sec):
    sec = int(sec)
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}" if sec >= 3600 else f"{sec // 60}:{sec % 60:02d}"


def chapters(cid, lang):
    work = CONTENT / cid / lang
    script = json.loads((work / "script.json").read_text())
    tl = json.loads((work / "timeline.json").read_text())
    out = [(0, INTRO_WORD.get(lang, "Opening"))]
    for sc, row in zip(script["scenes"], tl["scenes"]):
        if sc.get("chapter_title"):
            out.append((int(row["start"]), sc["chapter_title"]))
    return out


def chapter_block(cid, lang):
    return "\n".join(f"{stamp(t)} {title}" for t, title in chapters(cid, lang))


def thumbnail(cid, lang, scene, title, sub, out=None):
    sys.path.insert(0, str(ROOT))
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter

    import chalk

    work = CONTENT / cid / lang
    W, H = 1280, 720
    img = Image.open(work / "img" / f"{scene:02d}_raw.png").convert("RGB")
    layer = chalk.chalk_from_image(img, 7)
    board = chalk.make_board(7)
    comp = np.clip(board + layer, 0, 1)
    pic = Image.fromarray((comp * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    x0, y0 = int(W * 0.55), int(H * 0.52)
    shade = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shade).rectangle([x0 - 20, y0 - 20, W, H], fill=140)
    shade = shade.filter(ImageFilter.GaussianBlur(50))
    pic = Image.composite(Image.new("RGB", (W, H), (12, 14, 15)), pic, shade)
    d = ImageDraw.Draw(pic)
    box = W - x0 - 50

    def fit(text, size, maxw):
        f = chalk.font_for(text, size)
        while d.textlength(text, font=f) > maxw and size > 30:
            size -= 4
            f = chalk.font_for(text, size)
        return f

    words = title.split()
    lines = [" ".join(words[: (len(words) + 1) // 2]), " ".join(words[(len(words) + 1) // 2:])] if len(words) > 1 else [title]
    tf = min((fit(l, 96, box) for l in lines), key=lambda f: f.size)
    y = y0
    for line in lines:
        lw = d.textlength(line, font=tf)
        d.text((x0 + (box - lw) / 2, y), line, font=tf, fill=(232, 190, 110), stroke_width=7, stroke_fill=(10, 10, 10))
        y += int(tf.size * 1.25)
    sf = fit(sub, 40, box)
    sw = d.textlength(sub, font=sf)
    d.text((x0 + (box - sw) / 2, y + 14), sub, font=sf, fill=(242, 239, 230), stroke_width=4, stroke_fill=(10, 10, 10))
    dst = out or (work / "thumbnail.png")
    pic.save(dst)
    return dst


if __name__ == "__main__":
    cid, lang = sys.argv[1], sys.argv[2]
    print(chapter_block(cid, lang))
