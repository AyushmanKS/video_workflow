import os

LONG = os.environ.get("STUDIO_FORMAT") == "long"
W, H = (1920, 1080) if LONG else (1080, 1920)
CW, CH = (2112, 1188) if LONG else (1188, 2112)
IMAGE_SIZE = (1344, 768) if LONG else (768, 1344)
PROMPT_SUFFIX = " wide horizontal 16:9 landscape composition with the scene spread across the frame," if LONG else ""


def limits(fmt):
    if fmt == "long":
        return {"target": (480.0, 720.0), "max": 900.0, "lint_max": 780.0, "width": 1920, "height": 1080}
    return {"target": (35.0, 55.0), "max": 60.0, "lint_max": 57.0, "width": 1080, "height": 1920}
