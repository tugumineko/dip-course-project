"""家庭老照片纪念版模板。

主流程使用传统图像处理生成相册/胶片/明信片/淡彩手绘风格。
Gatys VGG 风格迁移保留为高级自定义艺术风格功能。
"""
from __future__ import annotations

import cv2
import numpy as np

try:
    from .basic import to_bgr, to_uint8
except ImportError:
    from basic import to_bgr, to_uint8


def _vignette_mask(h, w, strength=0.35):
    y = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
    x = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
    r = np.sqrt(x * x + y * y)
    mask = 1.0 - strength * np.clip((r - 0.25) / 0.95, 0, 1)
    return mask[:, :, None]


def _adjust_saturation(bgr, scale=0.9):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * scale, 0, 255)
    return cv2.cvtColor(to_uint8(hsv), cv2.COLOR_HSV2BGR)


def _warm_curve(bgr, red=1.06, green=1.01, blue=0.94):
    f = bgr.astype(np.float32)
    f[:, :, 2] *= red
    f[:, :, 1] *= green
    f[:, :, 0] *= blue
    return to_uint8(f)


def _add_border(img, border_ratio=0.055, color=(238, 230, 209)):
    h, w = img.shape[:2]
    border = max(18, int(min(h, w) * border_ratio))
    return cv2.copyMakeBorder(img, border, border, border, border, cv2.BORDER_CONSTANT, value=color)


def _add_grain(img, amount=5, seed=7):
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, amount, img.shape).astype(np.float32)
    return to_uint8(img.astype(np.float32) + noise)


def vintage_album_style(img):
    """复古相册风：低饱和、暖纸色、柔和暗角、米色相纸边框。"""
    out = to_bgr(img)
    out = _adjust_saturation(out, 0.82)
    out = _warm_curve(out, red=1.08, green=1.02, blue=0.92)
    out = cv2.GaussianBlur(out, (3, 3), 0)
    h, w = out.shape[:2]
    out = to_uint8(out.astype(np.float32) * _vignette_mask(h, w, 0.28))
    out = _add_border(out, border_ratio=0.06, color=(232, 224, 204))
    return out


def warm_film_style(img):
    """暖色胶片风：柔和 S 曲线、暖高光、轻微颗粒。"""
    out = to_bgr(img)
    f = out.astype(np.float32) / 255.0
    f = 0.5 + 1.12 * (f - 0.5)
    f = np.clip(f, 0, 1)
    out = to_uint8(f * 255)
    out = _warm_curve(out, red=1.07, green=1.0, blue=0.95)
    out = _adjust_saturation(out, 0.92)
    out = _add_grain(out, amount=3)
    h, w = out.shape[:2]
    out = to_uint8(out.astype(np.float32) * _vignette_mask(h, w, 0.18))
    return out


def postcard_style(img):
    """纪念明信片风：白边、米色画布、轻微阴影，适合导出展示。"""
    photo = to_bgr(img)
    h, w = photo.shape[:2]
    max_w = 900
    if w > max_w:
        scale = max_w / w
        photo = cv2.resize(photo, (max_w, int(h * scale)), interpolation=cv2.INTER_AREA)
        h, w = photo.shape[:2]

    inner_border = max(18, int(min(h, w) * 0.04))
    photo = cv2.copyMakeBorder(photo, inner_border, inner_border, inner_border, inner_border,
                               cv2.BORDER_CONSTANT, value=(248, 246, 238))
    ph, pw = photo.shape[:2]
    margin_x = max(45, int(pw * 0.08))
    margin_top = max(38, int(ph * 0.07))
    margin_bottom = max(92, int(ph * 0.17))
    canvas = np.full((ph + margin_top + margin_bottom, pw + 2 * margin_x, 3),
                     (226, 218, 198), dtype=np.uint8)

    shadow = np.zeros_like(photo)
    shadow[:, :] = (120, 112, 96)
    sx, sy = margin_x + 8, margin_top + 10
    canvas[sy:sy + ph, sx:sx + pw] = cv2.addWeighted(canvas[sy:sy + ph, sx:sx + pw], 0.35, shadow, 0.65, 0)
    x, y = margin_x, margin_top
    canvas[y:y + ph, x:x + pw] = photo

    cv2.putText(canvas, "Family Memory", (x + 12, y + ph + 42),
                cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.2, (92, 78, 58), 2, cv2.LINE_AA)
    cv2.putText(canvas, "Restored with Digital Image Processing", (x + 14, y + ph + 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (116, 104, 84), 1, cv2.LINE_AA)
    return canvas


def soft_handpainted_style(img):
    """淡彩手绘风：双边平滑 + 浅线稿 + 低强度色彩提升。"""
    bgr = to_bgr(img)
    smooth = cv2.bilateralFilter(bgr, 11, 80, 80)
    smooth = cv2.bilateralFilter(smooth, 9, 60, 60)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 60, 140)
    edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)
    line = 255 - edges
    line_bgr = cv2.cvtColor(line, cv2.COLOR_GRAY2BGR)
    color = _adjust_saturation(smooth, 1.08)
    out = cv2.addWeighted(color, 0.86, line_bgr, 0.14, 0)
    return out
