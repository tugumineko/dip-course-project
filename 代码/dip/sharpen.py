"""第七章 图像锐化：Laplacian、Sobel 梯度、USM 非锐化掩蔽。"""
from __future__ import annotations

import cv2
import numpy as np

try:
    from .basic import to_gray, to_uint8
except ImportError:
    from basic import to_gray, to_uint8


def laplacian_sharpen(img, strength=1.0):
    """Laplacian 锐化：g = f - strength·∇²f（第七章）。"""
    lap = cv2.Laplacian(img, cv2.CV_32F, ksize=1)
    return to_uint8(img.astype(np.float32) - strength * lap)


def sobel_edges(img):
    """Sobel 梯度幅值（第七章 边缘强调）。"""
    g = to_gray(img)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    return to_uint8(cv2.magnitude(gx, gy))


def unsharp_mask(img, k=5, sigma=1.0, amount=1.0):
    """USM 非锐化掩蔽：g = f + amount·(f - 高斯模糊(f))。最常用的锐化。"""
    blur = cv2.GaussianBlur(img, (k, k), sigma).astype(np.float32)
    return to_uint8(img.astype(np.float32) + amount * (img.astype(np.float32) - blur))
