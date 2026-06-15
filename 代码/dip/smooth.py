"""第六章 图像平滑（去噪）：均值、中值、高斯、双边、非局部均值。"""
from __future__ import annotations

import cv2

try:
    from .basic import is_color
except ImportError:
    from basic import is_color


def mean_blur(img, k=3):
    """均值滤波（邻域平均）。"""
    return cv2.blur(img, (k, k))


def median_blur(img, k=3):
    """中值滤波（非线性，专治椒盐噪声）。"""
    if k % 2 == 0:
        k += 1
    return cv2.medianBlur(img, k)


def gaussian_blur(img, k=5, sigma=0):
    """高斯滤波（加权平均）。"""
    if k % 2 == 0:
        k += 1
    return cv2.GaussianBlur(img, (k, k), sigma)


def bilateral(img, d=9, sigma_color=75, sigma_space=75):
    """双边滤波：保边去噪（可作"磨皮"）。"""
    return cv2.bilateralFilter(img, d, sigma_color, sigma_space)


def nlmeans(img, h=10):
    """非局部均值去噪：对老照片噪点效果好、保细节（推荐用于一键修复）。"""
    if is_color(img):
        return cv2.fastNlMeansDenoisingColored(img, None, h, h, 7, 21)
    return cv2.fastNlMeansDenoising(img, None, h, 7, 21)
