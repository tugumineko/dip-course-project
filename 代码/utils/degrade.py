"""退化样张合成 —— 把干净图合成成"老照片"。

用途：开发自测 + 指标对照（修复结果 vs 干净原图 算 PSNR/SSIM）。
对应课程：第九章 图像恢复的退化模型  g(x,y) = h * f(x,y) + n(x,y)
          （模糊核 h 卷积 + 加性噪声 n）。本脚本反向制造退化。

命令行：
    python utils/degrade.py 干净图 输出老照片 [--mask 划痕掩膜] [--seed 0]
作为库：
    from utils.degrade import make_old_photo
    old_bgr, scratch_mask = make_old_photo(clean_bgr, seed=0)
"""
from __future__ import annotations

import argparse

import cv2
import numpy as np

try:  # 兼容"作为包导入"与"作为脚本直接运行"
    from .imgio import imread, imwrite
except ImportError:
    from imgio import imread, imwrite


def add_gaussian_noise(img, sigma=12.0, rng=None):
    """加性高斯噪声（第九章 噪声模型）。"""
    rng = np.random.default_rng() if rng is None else rng
    noise = rng.normal(0.0, sigma, img.shape).astype(np.float32)
    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def add_salt_pepper(img, amount=0.01, rng=None):
    """椒盐噪声（随机黑白点）。"""
    rng = np.random.default_rng() if rng is None else rng
    out = img.copy()
    h, w = img.shape[:2]
    n = int(amount * h * w)
    for val in (0, 255):
        ys = rng.integers(0, h, n)
        xs = rng.integers(0, w, n)
        out[ys, xs] = val
    return out


def add_blur(img, ksize=3):
    """高斯模糊，模拟失焦/老化（退化模型里的 h）。"""
    k = int(ksize)
    if k % 2 == 0:
        k += 1
    if k < 3:
        return img
    return cv2.GaussianBlur(img, (k, k), 0)


def fade_and_sepia(img, fade=0.65, sepia=0.6):
    """褪色 + 泛黄（棕褐色调），模拟老照片色衰。
    fade: 0~1，越小越褪（向中灰靠拢，降对比）；sepia: 0~1，棕褐强度。
    """
    f = img.astype(np.float32)
    f = f * fade + 128.0 * (1.0 - fade)  # 降对比/褪色：向中灰混合
    if img.ndim == 3 and sepia > 0:
        b, g, r = f[..., 0], f[..., 1], f[..., 2]  # cv2 通道序为 BGR
        tr = 0.393 * r + 0.769 * g + 0.189 * b
        tg = 0.349 * r + 0.686 * g + 0.168 * b
        tb = 0.272 * r + 0.534 * g + 0.131 * b
        sep = np.stack([tb, tg, tr], axis=-1)
        f = f * (1.0 - sepia) + sep * sepia
    return np.clip(f, 0, 255).astype(np.uint8)


def add_scratches(img, n=8, rng=None):
    """随机划痕（亮/暗细线），返回 (加划痕图, 划痕掩膜)。
    掩膜：255 处为划痕，供后续 inpaint 修复使用。
    """
    rng = np.random.default_rng() if rng is None else rng
    out = img.copy()
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    for _ in range(n):
        x1, x2 = (int(v) for v in rng.integers(0, w, 2))
        y1, y2 = (int(v) for v in rng.integers(0, h, 2))
        thick = int(rng.integers(1, 3))
        color = int(rng.choice([0, 255, 230]))
        c = (color, color, color) if img.ndim == 3 else color
        cv2.line(out, (x1, y1), (x2, y2), c, thick)
        cv2.line(mask, (x1, y1), (x2, y2), 255, thick + 1)
    return out, mask


def make_old_photo(img, seed=None, blur=3, sigma=12.0, sp=0.01,
                   fade=0.65, sepia=0.6, scratches=8):
    """组合多种退化，返回 (老照片 BGR, 划痕掩膜)。顺序模拟真实老化过程。"""
    rng = np.random.default_rng(seed)
    out = add_blur(img, blur)
    out = fade_and_sepia(out, fade=fade, sepia=sepia)
    out = add_gaussian_noise(out, sigma=sigma, rng=rng)
    out = add_salt_pepper(out, amount=sp, rng=rng)
    out, mask = add_scratches(out, n=scratches, rng=rng)
    return out, mask


def main():
    ap = argparse.ArgumentParser(description="把干净图合成为老照片")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--mask", default=None, help="划痕掩膜输出路径")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    img = imread(args.input, cv2.IMREAD_COLOR)
    if img is None:
        raise SystemExit(f"读不到图片: {args.input}")
    old, mask = make_old_photo(img, seed=args.seed)
    imwrite(args.output, old)
    if args.mask:
        imwrite(args.mask, mask)
    print(f"OK 老照片 -> {args.output}  ({old.shape[1]}x{old.shape[0]})"
          + (f"  掩膜 -> {args.mask}" if args.mask else ""))


if __name__ == "__main__":
    main()
