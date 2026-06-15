"""第十章 小波变换：小波软阈值去噪。依赖 pywt（已装，缺失时自动禁用）。"""
from __future__ import annotations

try:
    from .basic import to_uint8, apply_per_channel
except ImportError:
    from basic import to_uint8, apply_per_channel

try:
    import pywt
    HAS_PYWT = True
except ImportError:
    HAS_PYWT = False


def available():
    """pywt 是否可用（界面据此启用/禁用小波功能）。"""
    return HAS_PYWT


def wavelet_denoise(img, wavelet="db1", level=2, thresh=20.0):
    """小波软阈值去噪（第十章）：多分辨率分解 → 阈值细节系数 → 重构。彩色逐通道。"""
    if not HAS_PYWT:
        raise RuntimeError("未安装 pywt，无法使用小波去噪")

    def _one(ch):
        coeffs = pywt.wavedec2(ch.astype("float32"), wavelet, level=level)
        new = [coeffs[0]]
        for detail in coeffs[1:]:
            new.append(tuple(pywt.threshold(d, thresh, mode="soft") for d in detail))
        rec = pywt.waverec2(new, wavelet)
        return to_uint8(rec[: ch.shape[0], : ch.shape[1]])

    return apply_per_channel(img, _one)
