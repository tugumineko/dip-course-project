"""第五章 图像分割：固定阈值、Otsu、自适应阈值、Canny 边缘。"""
from __future__ import annotations

import cv2

try:
    from .basic import to_gray
except ImportError:
    from basic import to_gray


def threshold(img, t=127):
    """固定阈值二值化。"""
    _, b = cv2.threshold(to_gray(img), t, 255, cv2.THRESH_BINARY)
    return b


def otsu(img):
    """Otsu 自动阈值二值化（第五章），返回 (二值图, 阈值)。"""
    t, b = cv2.threshold(to_gray(img), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return b, int(t)


def adaptive_threshold(img, block=11, c=2):
    """自适应阈值：光照不均时分割更稳。"""
    if block % 2 == 0:
        block += 1
    return cv2.adaptiveThreshold(to_gray(img), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, block, c)


def canny(img, t1=100, t2=200):
    """Canny 边缘检测（第五/七章）。"""
    return cv2.Canny(to_gray(img), t1, t2)
