import sys

from PIL import Image, ImageDraw, ImageFont


def grid(src, dst, box=(0.0, 0.0, 1.0, 1.0), width=900, step=0.05):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    x0, y0, x1, y1 = box
    crop = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    scale = width / crop.width
    crop = crop.resize((width, int(crop.height * scale)))
    d = ImageDraw.Draw(crop)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 14)
    except OSError:
        f = ImageFont.load_default()
    fine = step / 2
    v = round(x0 / fine) * fine
    while v <= x1 + 1e-9:
        px = (v - x0) / (x1 - x0) * crop.width
        major = abs(round(v / step) * step - v) < 1e-6
        d.line([(px, 0), (px, crop.height)], fill=(0, 255, 255) if major else (0, 120, 140), width=1)
        if major:
            d.text((px + 2, 2), f"{v:.2f}", font=f, fill=(255, 255, 0))
        v += fine
    v = round(y0 / fine) * fine
    while v <= y1 + 1e-9:
        py = (v - y0) / (y1 - y0) * crop.height
        major = abs(round(v / step) * step - v) < 1e-6
        d.line([(0, py), (crop.width, py)], fill=(0, 255, 255) if major else (0, 120, 140), width=1)
        if major:
            d.text((2, py + 2), f"{v:.2f}", font=f, fill=(255, 255, 0))
        v += fine
    crop.save(dst)
    return dst


if __name__ == "__main__":
    box = tuple(float(v) for v in sys.argv[3].split(",")) if len(sys.argv) > 3 else (0.0, 0.0, 1.0, 1.0)
    print(grid(sys.argv[1], sys.argv[2], box))
