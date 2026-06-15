"""3.2 频域处理（傅里叶变换）：幅度谱 + 理想/巴特沃斯 低通/高通滤波。

频域滤波用 numpy.fft 实现（OpenCV 无高层自定义频域滤波接口，FFT 是标准做法）。
"""
from __future__ import annotations

import numpy as np

try:
    from .basic import to_gray, to_uint8
except ImportError:
    from basic import to_gray, to_uint8


def spectrum(img):
    """傅里叶幅度谱（对数显示、中心化）——直观看频率成分。"""
    g = to_gray(img).astype(np.float32)
    f = np.fft.fftshift(np.fft.fft2(g))
    mag = np.log1p(np.abs(f))
    mag = mag / (mag.max() + 1e-8) * 255.0
    return to_uint8(mag)


def _dist(shape):
    h, w = shape
    u = np.arange(h).reshape(-1, 1) - h / 2
    v = np.arange(w).reshape(1, -1) - w / 2
    return np.sqrt(u * u + v * v)


def _filt(img, h_filter):
    g = to_gray(img).astype(np.float32)
    f = np.fft.fftshift(np.fft.fft2(g))
    out = np.fft.ifft2(np.fft.ifftshift(f * h_filter))
    return to_uint8(np.abs(out))


def ideal_lowpass(img, d0=30):
    """理想低通：保留低频（平滑、去噪），有振铃。"""
    return _filt(img, (_dist(to_gray(img).shape) <= d0).astype(np.float32))


def ideal_highpass(img, d0=30):
    """理想高通：保留高频（边缘、细节）。"""
    return _filt(img, (_dist(to_gray(img).shape) > d0).astype(np.float32))


def butterworth_lowpass(img, d0=30, n=2):
    """巴特沃斯低通：过渡平滑、无明显振铃。"""
    d = _dist(to_gray(img).shape)
    return _filt(img, 1.0 / (1.0 + (d / d0) ** (2 * n)))


def butterworth_highpass(img, d0=30, n=2):
    """巴特沃斯高通。"""
    d = _dist(to_gray(img).shape)
    with np.errstate(divide="ignore"):
        h = 1.0 / (1.0 + (d0 / np.maximum(d, 1e-6)) ** (2 * n))
    return _filt(img, h)
