"""第九章 图像恢复：退化模拟、逆滤波、维纳滤波、加噪、划痕修复(inpaint)。

退化模型 g = h * f + n。逆/维纳滤波用 FFT 实现（标准做法）；inpaint 用 OpenCV。
"""
from __future__ import annotations

import cv2
import numpy as np

try:
    from .basic import to_gray, to_uint8
except ImportError:
    from basic import to_gray, to_uint8


def motion_blur_kernel(length=15, angle=0):
    """运动模糊核（退化算子 h）。"""
    k = np.zeros((length, length), np.float32)
    k[length // 2, :] = 1.0
    m = cv2.getRotationMatrix2D((length / 2, length / 2), angle, 1.0)
    k = cv2.warpAffine(k, m, (length, length))
    s = k.sum()
    return k / s if s != 0 else k


def add_gaussian_noise(img, sigma=10):
    """加性高斯噪声（演示退化）。"""
    n = np.random.normal(0, sigma, img.shape).astype(np.float32)
    return to_uint8(img.astype(np.float32) + n)


def _psf2otf(psf, shape):
    """把小 PSF 放到图像尺寸、中心对齐到 (0,0) 后 FFT，得到 OTF=H。"""
    pad = np.zeros(shape, np.float32)
    kh, kw = psf.shape
    pad[:kh, :kw] = psf
    pad = np.roll(pad, -(kh // 2), axis=0)
    pad = np.roll(pad, -(kw // 2), axis=1)
    return np.fft.fft2(pad)


def inverse_filter(img, psf, eps=1e-2):
    """逆滤波（第九章）：F̂ = G / H（|H| 太小处加 eps 抑制噪声放大）。仅灰度。"""
    g = to_gray(img).astype(np.float32)
    h = _psf2otf(psf, g.shape)
    hc = np.where(np.abs(h) < eps, eps, h)
    f = np.fft.fft2(g) / hc
    return to_uint8(np.real(np.fft.ifft2(f)))


def wiener_filter(img, psf, k=0.01):
    """维纳滤波（第九章）：F̂ = [H* / (|H|² + K)] · G。仅灰度。"""
    g = to_gray(img).astype(np.float32)
    h = _psf2otf(psf, g.shape)
    f = np.conj(h) / (np.abs(h) ** 2 + k) * np.fft.fft2(g)
    return to_uint8(np.real(np.fft.ifft2(f)))


def inpaint(img, mask, radius=3, method="telea"):
    """划痕/瑕疵修复（第九章应用，OpenCV inpaint）。mask 非零处被修复。"""
    flags = cv2.INPAINT_TELEA if method == "telea" else cv2.INPAINT_NS
    if mask.ndim == 3:
        mask = to_gray(mask)
    mask = (mask > 0).astype(np.uint8) * 255
    return cv2.inpaint(img, mask, radius, flags)
