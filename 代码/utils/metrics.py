"""图像质量指标：PSNR / SSIM。

用于"修复结果 vs 干净原图"的量化评估（演讲/报告里的实验数据）。

命令行：
    python utils/metrics.py 图A 图B
作为库：
    from utils.metrics import psnr, ssim
"""
from __future__ import annotations

import argparse

import cv2
import numpy as np

try:  # 兼容"作为包导入"与"作为脚本直接运行"
    from .imgio import imread
except ImportError:
    from imgio import imread


def psnr(a, b):
    """峰值信噪比（dB）。越大越接近，完全相同为 inf。"""
    a = a.astype(np.float64)
    b = b.astype(np.float64)
    mse = np.mean((a - b) ** 2)
    if mse == 0:
        return float("inf")
    return 10.0 * np.log10((255.0 ** 2) / mse)


def _ssim_gray(a, b):
    """单通道 SSIM（高斯窗），scipy 实现，作为无 skimage 时的回退。"""
    from scipy.ndimage import gaussian_filter

    a = a.astype(np.float64)
    b = b.astype(np.float64)
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2
    win = 1.5
    mu_a = gaussian_filter(a, win)
    mu_b = gaussian_filter(b, win)
    mu_a2, mu_b2, mu_ab = mu_a ** 2, mu_b ** 2, mu_a * mu_b
    sa = gaussian_filter(a * a, win) - mu_a2
    sb = gaussian_filter(b * b, win) - mu_b2
    sab = gaussian_filter(a * b, win) - mu_ab
    ssim_map = ((2 * mu_ab + c1) * (2 * sab + c2)) / \
               ((mu_a2 + mu_b2 + c1) * (sa + sb + c2))
    return float(ssim_map.mean())


def ssim(a, b):
    """结构相似度（0~1，越大越像）。优先 skimage，否则 scipy 回退（转灰度）。"""
    try:
        from skimage.metrics import structural_similarity as sk
        if a.ndim == 3:
            return float(sk(a, b, channel_axis=2))
        return float(sk(a, b))
    except Exception:
        if a.ndim == 3:
            a = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
            b = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
        return _ssim_gray(a, b)


def main():
    ap = argparse.ArgumentParser(description="计算两图 PSNR/SSIM")
    ap.add_argument("img_a")
    ap.add_argument("img_b")
    args = ap.parse_args()
    a = imread(args.img_a, cv2.IMREAD_COLOR)
    b = imread(args.img_b, cv2.IMREAD_COLOR)
    if a is None or b is None:
        raise SystemExit("读不到图片")
    if a.shape != b.shape:
        b = cv2.resize(b, (a.shape[1], a.shape[0]))
    print(f"PSNR = {psnr(a, b):.2f} dB")
    print(f"SSIM = {ssim(a, b):.4f}")


if __name__ == "__main__":
    main()
