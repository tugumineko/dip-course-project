"""第八章 数学形态学：腐蚀/膨胀/开/闭/梯度/顶帽。

常用于二值图后处理（去小噪点、连断裂、提取边界），也可作用于灰度图。
"""
from __future__ import annotations

import cv2


def _kernel(k=3, shape=cv2.MORPH_ELLIPSE):
    return cv2.getStructuringElement(shape, (k, k))


def erode(img, k=3, it=1):
    """腐蚀：缩小亮区、去小白点。"""
    return cv2.erode(img, _kernel(k), iterations=it)


def dilate(img, k=3, it=1):
    """膨胀：扩大亮区、连断裂。"""
    return cv2.dilate(img, _kernel(k), iterations=it)


def opening(img, k=3):
    """开运算（先腐蚀后膨胀）：去小噪点。"""
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, _kernel(k))


def closing(img, k=3):
    """闭运算（先膨胀后腐蚀）：填小孔洞。"""
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, _kernel(k))


def gradient(img, k=3):
    """形态学梯度：提取边界。"""
    return cv2.morphologyEx(img, cv2.MORPH_GRADIENT, _kernel(k))


def tophat(img, k=9):
    """顶帽：提取比邻域亮的细节（如划痕、亮斑）。"""
    return cv2.morphologyEx(img, cv2.MORPH_TOPHAT, _kernel(k))
