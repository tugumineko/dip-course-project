"""Generate a warm family-memory style image for VGG style-transfer demo."""
from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(PROJ, "素材", "风格图", "warm_family_memory_style.jpg")


def clamp(v):
    return max(0, min(255, int(v)))


def main():
    w, h = 900, 650
    img = Image.new("RGB", (w, h), (126, 88, 56))
    px = img.load()
    for y in range(h):
        for x in range(w):
            v = int(20 * math.sin(x / 70) + 16 * math.cos(y / 55))
            px[x, y] = (clamp(126 + v), clamp(88 + v * 0.55), clamp(56 + v * 0.35))

    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((50, 45, 850, 605), fill=(205, 164, 105, 75))
    draw.line((80, 90, 820, 90), fill=(238, 205, 150, 90), width=8)

    heads = [
        (300, 265, 64, (78, 54, 42, 230)),
        (450, 245, 70, (92, 62, 42, 235)),
        (590, 270, 60, (70, 50, 45, 230)),
        (385, 365, 48, (110, 72, 50, 230)),
        (520, 365, 44, (98, 62, 48, 230)),
    ]
    for cx, cy, r, color in heads:
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)

    bodies = [
        ((230, 330, 370, 570), (84, 58, 48, 225)),
        ((385, 315, 520, 585), (112, 76, 52, 225)),
        ((535, 335, 675, 575), (76, 56, 55, 225)),
        ((330, 410, 445, 590), (128, 82, 56, 220)),
        ((470, 410, 585, 590), (108, 70, 62, 220)),
    ]
    for box, color in bodies:
        draw.rounded_rectangle(box, radius=38, fill=color)

    draw.ellipse((190, 500, 710, 665), fill=(152, 103, 62, 175))

    for i in range(90):
        x = (i * 47) % w
        y = (i * 83) % h
        color = (210 + (i % 3) * 8, 160 + (i % 5) * 5, 95 + (i % 7) * 4, 24)
        draw.line((x, y, x + 120, y + 25), fill=color, width=5)

    img = img.filter(ImageFilter.GaussianBlur(1.2))

    texture = Image.new("RGB", (w, h), (128, 128, 128))
    tp = texture.load()
    for y in range(h):
        for x in range(w):
            n = ((x * 17 + y * 31) % 23) - 11
            tp[x, y] = (128 + n, 128 + n, 128 + n)
    img = Image.blend(img, texture, 0.08)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, quality=92)
    print(OUT)


if __name__ == "__main__":
    main()
