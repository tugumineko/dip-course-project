"""第四章 对比度增强：直方图均衡、CLAHE、正规化、分段线性、对数、伽马。

均用 OpenCV / numpy LUT 实现。
"""
from __future__ import annotations

import cv2
import numpy as np

try:
    from .basic import to_gray
except ImportError:
    from basic import to_gray


def histogram(img, bins=256):
    """计算灰度直方图（供界面画图）。"""
    g = to_gray(img)
    return np.bincount(g.ravel(), minlength=bins)[:bins]


def hist_equalize(img):
    """直方图均衡（第四章）。彩色在 YCrCb 的 Y 通道做，避免偏色。"""
    if img.ndim == 2:
        return cv2.equalizeHist(img)
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    y = cv2.equalizeHist(y)
    return cv2.cvtColor(cv2.merge([y, cr, cb]), cv2.COLOR_YCrCb2BGR)


def clahe(img, clip=2.0, grid=8):
    """限制对比度自适应直方图均衡（CLAHE）：老照片增强更自然、不过曝。"""
    op = cv2.createCLAHE(clipLimit=clip, tileGridSize=(grid, grid))
    if img.ndim == 2:
        return op.apply(img)
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    y = op.apply(y)
    return cv2.cvtColor(cv2.merge([y, cr, cb]), cv2.COLOR_YCrCb2BGR)


def normalize(img, lo=0, hi=255):
    """直方图正规化（线性拉伸到 [lo,hi]）。"""
    return cv2.normalize(img, None, lo, hi, cv2.NORM_MINMAX).astype(np.uint8)


def piecewise_linear(img, r1=70, s1=30, r2=180, s2=220):
    """分段线性变换（三段：压暗 + 拉伸中间 + 提亮）。"""
    x = np.arange(256, dtype=np.float32)
    lut = np.clip(np.interp(x, [0, r1, r2, 255], [0, s1, s2, 255]), 0, 255).astype(np.uint8)
    return cv2.LUT(img, lut)


def log_transform(img, c=None):
    """对数变换：扩展暗部细节。s = c*log(1+r)。"""
    f = img.astype(np.float32)
    if c is None:
        c = 255.0 / np.log(1 + 255.0)
    return np.clip(c * np.log1p(f), 0, 255).astype(np.uint8)


def gamma_transform(img, gamma=1.0):
    """伽马（幂律）变换。gamma<1 提亮暗部，>1 压暗。"""
    lut = np.clip((np.arange(256) / 255.0) ** gamma * 255.0, 0, 255).astype(np.uint8)
    return cv2.LUT(img, lut)


def white_balance(img):
    """灰度世界白平衡：校正整体偏色（老照片泛黄/偏棕）。仅彩色有效。

    假设：自然图像三通道均值应趋于相等（灰）。据此缩放各通道去除色偏。
    """
    if img.ndim == 2:
        return img
    f = img.astype(np.float32)
    avg = f.reshape(-1, 3).mean(axis=0)          # B,G,R 各通道均值
    scale = avg.mean() / (avg + 1e-6)
    return np.clip(f * scale, 0, 255).astype(np.uint8)
