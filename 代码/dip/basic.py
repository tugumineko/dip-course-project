"""第二章 数字图像基础 + 共享小工具。

色彩/类型规整、几何变换、逐通道应用。所有函数 输入/输出 均为 ndarray
（BGR 彩色或单通道灰度，uint8）。本项目算法**统一用 OpenCV** 实现。
"""
from __future__ import annotations

import cv2
import numpy as np


def to_gray(img):
    """转灰度（第二章 灰度图）。"""
    if img.ndim == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def to_bgr(img):
    """转 3 通道 BGR。"""
    if img.ndim == 3:
        return img
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


def is_color(img):
    return img.ndim == 3 and img.shape[2] == 3


def to_uint8(arr):
    """裁剪到 [0,255] 并转 uint8。"""
    return np.clip(arr, 0, 255).astype(np.uint8)


def apply_per_channel(img, func):
    """对彩色图逐通道应用 func；灰度直接应用。"""
    if img.ndim == 2:
        return func(img)
    return cv2.merge([func(c) for c in cv2.split(img)])


def resize(img, scale=None, size=None, interp=cv2.INTER_LINEAR):
    """缩放（第二章 几何变换）。size=(w,h) 优先，否则按 scale 比例。"""
    if size is not None:
        return cv2.resize(img, size, interpolation=interp)
    if scale is not None:
        return cv2.resize(img, None, fx=scale, fy=scale, interpolation=interp)
    return img


def rotate(img, angle):
    """绕中心旋转 angle 度（逆时针），保持画布大小。"""
    h, w = img.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(img, m, (w, h))


def split_channels(img):
    """通道分离：彩色返回 [B,G,R]，灰度返回 [gray]。"""
    if img.ndim == 2:
        return [img]
    return list(cv2.split(img))


def info(img):
    """图像基本信息字符串。"""
    if img.ndim == 2:
        return f"{img.shape[1]}x{img.shape[0]} 灰度 {img.dtype}"
    return f"{img.shape[1]}x{img.shape[0]} {img.shape[2]}通道 {img.dtype}"
