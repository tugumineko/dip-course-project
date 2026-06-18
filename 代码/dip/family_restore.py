"""家庭老照片定制修复模式。

这些函数不是单个算法演示，而是面向家庭老照片常见场景的固定处理流水线。
所有函数输入/输出均为 uint8 ndarray，彩色图使用 BGR。
"""
from __future__ import annotations

import cv2
import numpy as np

try:
    from . import enhance, smooth, restore
    from .basic import to_bgr, to_gray, to_uint8
except ImportError:
    import enhance, smooth, restore
    from basic import to_bgr, to_gray, to_uint8


def _ensure_odd(k: int) -> int:
    return k if k % 2 else k + 1


def _clahe_luminance(img, clip=1.8, grid=8):
    if img.ndim == 2:
        return enhance.clahe(img, clip=clip, grid=grid)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    op = cv2.createCLAHE(clipLimit=clip, tileGridSize=(grid, grid))
    l = op.apply(l)
    return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)


def _soft_unsharp_luminance(img, amount=0.45, sigma=1.2, noise_gate=5):
    bgr = to_bgr(img)
    ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    yf = y.astype(np.float32)
    blur = cv2.GaussianBlur(y, (5, 5), sigma).astype(np.float32)
    detail = yf - blur
    mask = (np.abs(detail) > noise_gate).astype(np.float32)
    y2 = to_uint8(yf + amount * detail * mask)
    out = cv2.cvtColor(cv2.merge([y2, cr, cb]), cv2.COLOR_YCrCb2BGR)
    return out if img.ndim == 3 else to_gray(out)


def _soft_s_curve(gray_or_channel, strength=0.18):
    x = gray_or_channel.astype(np.float32) / 255.0
    y = x + strength * (x - 0.5) * (1 - np.abs(2 * x - 1))
    return to_uint8(y * 255.0)


def _light_warm_tone(img, strength=0.10):
    if img.ndim == 2:
        bgr = to_bgr(img)
    else:
        bgr = img.copy()
    f = bgr.astype(np.float32)
    f[:, :, 2] *= 1.0 + strength
    f[:, :, 1] *= 1.0 + strength * 0.25
    f[:, :, 0] *= 1.0 - strength * 0.35
    out = to_uint8(f)
    return out if img.ndim == 3 else to_gray(out)


def gentle_restore(img):
    """温和修复：适合多数家庭老照片，保留旧照质感。"""
    out = to_bgr(img)
    out = smooth.nlmeans(out, h=6)
    out = restore_faded_yellow_photo(out, keep_warmth=0.18, clip=1.5)
    out = _soft_unsharp_luminance(out, amount=0.35, sigma=1.4, noise_gate=6)
    return out if img.ndim == 3 else to_gray(out)


def restore_faded_yellow_photo(img, keep_warmth=0.16, clip=1.8):
    """泛黄褪色修复：校正黄化但保留少量暖色记忆感。"""
    bgr = to_bgr(img)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    l, a, b = cv2.split(lab)

    neutral_b = 128.0 + keep_warmth * 18.0
    yellow_shift = np.clip(np.mean(b) - neutral_b, 0, 32)
    b = b - yellow_shift * 0.65

    neutral_a = 128.0
    a_shift = np.clip(np.mean(a) - neutral_a, -18, 18)
    a = a - a_shift * 0.35

    op = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8))
    l = op.apply(to_uint8(l)).astype(np.float32)
    l = _soft_s_curve(to_uint8(l), strength=0.12).astype(np.float32)

    merged = cv2.merge([to_uint8(l), to_uint8(a), to_uint8(b)])
    out = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.06, 0, 255)
    out = cv2.cvtColor(to_uint8(hsv), cv2.COLOR_HSV2BGR)
    return out if img.ndim == 3 else to_gray(out)


def restore_bw_photo(img, warm_paper=True):
    """黑白旧照增强：强化灰度层次和轮廓，可加轻微暖纸色。"""
    gray = to_gray(img)
    gray = smooth.nlmeans(gray, h=6)
    gray = _clahe_luminance(gray, clip=1.7, grid=8)
    gray = _soft_s_curve(gray, strength=0.16)
    gray = _soft_unsharp_luminance(gray, amount=0.42, sigma=1.1, noise_gate=5)
    if not warm_paper:
        return gray
    bgr = to_bgr(gray)
    return _light_warm_tone(bgr, strength=0.08)


def reduce_photo_grain(img):
    """扫描颗粒修复：色度强去噪、亮度弱去噪，并用边缘权重保护轮廓。"""
    bgr = to_bgr(img)
    ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)

    y_soft = cv2.fastNlMeansDenoising(y, None, 6, 7, 21)
    cr_soft = cv2.fastNlMeansDenoising(cr, None, 12, 7, 21)
    cb_soft = cv2.fastNlMeansDenoising(cb, None, 12, 7, 21)

    edges = cv2.Canny(y, 40, 120)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)
    edge_weight = cv2.GaussianBlur(edges.astype(np.float32) / 255.0, (7, 7), 0)
    denoise_weight = 1.0 - 0.55 * edge_weight

    y_mix = to_uint8(y.astype(np.float32) * (1 - denoise_weight) + y_soft.astype(np.float32) * denoise_weight)
    out = cv2.cvtColor(cv2.merge([y_mix, cr_soft, cb_soft]), cv2.COLOR_YCrCb2BGR)
    return out if img.ndim == 3 else to_gray(out)


def portrait_clarity(img):
    """人像清晰化：只增强中等边缘，避免暗部噪声被锐化。"""
    bgr = to_bgr(img)
    ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    yf = y.astype(np.float32)

    base = cv2.bilateralFilter(y, 9, 45, 45).astype(np.float32)
    detail = yf - base
    grad = cv2.Laplacian(y, cv2.CV_32F, ksize=3)
    edge = np.clip(np.abs(grad) / 38.0, 0, 1)
    brightness_gate = np.clip((yf - 18.0) / 60.0, 0, 1)
    weight = cv2.GaussianBlur(edge * brightness_gate, (5, 5), 0)
    y2 = to_uint8(yf + detail * weight * 0.9)

    out = cv2.cvtColor(cv2.merge([y2, cr, cb]), cv2.COLOR_YCrCb2BGR)
    out = _clahe_luminance(out, clip=1.25, grid=8)
    return out if img.ndim == 3 else to_gray(out)


def _auto_scratch_mask(img):
    gray = to_gray(img)
    kernel_long_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 17))
    kernel_long_h = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 1))
    bright_v = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel_long_v)
    bright_h = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel_long_h)
    dark_v = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel_long_v)
    dark_h = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel_long_h)
    lines = cv2.max(cv2.max(bright_v, bright_h), cv2.max(dark_v, dark_h))
    _, mask = cv2.threshold(lines, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
    return mask


def scratch_assisted_inpaint(img, mask=None, auto=True):
    """折痕划痕辅助修复：自动细线掩膜与用户掩膜合并后 inpaint。"""
    merged = None
    if auto:
        merged = _auto_scratch_mask(img)
    if mask is not None:
        user_mask = to_gray(mask) if mask.ndim == 3 else mask
        user_mask = (user_mask > 0).astype(np.uint8) * 255
        merged = user_mask if merged is None else cv2.bitwise_or(merged, user_mask)
    if merged is None:
        merged = _auto_scratch_mask(img)
    return restore.inpaint(img, merged, radius=3)


def scratch_mask_preview(img):
    """生成自动划痕掩膜预览，便于说明辅助检测不是完全自动修复。"""
    return _auto_scratch_mask(img)
