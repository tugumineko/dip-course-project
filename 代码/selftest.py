"""Phase 1 自测：各 DIP 模块冒烟测试 + 一键修复指标 + 导出样例图。

运行：E:\\miniconda3\\envs\\ai-service\\python.exe 代码\\selftest.py
"""
import os
import sys
import traceback

try:  # Windows 控制台默认 GBK，强制 UTF-8 输出避免编码报错
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np

from utils.imgio import imread, imwrite
from utils.metrics import psnr, ssim
from dip import (basic, enhance, smooth, sharpen, segment,
                 morphology, frequency, restore, wavelet, pipeline)

ROOT = os.path.dirname(HERE)
CLEAN = os.path.join(ROOT, "素材", "干净原图", "test.jpg")
OLD = os.path.join(ROOT, "素材", "合成老照片", "test_old.jpg")
OUT = os.path.join(ROOT, "结果")
os.makedirs(OUT, exist_ok=True)

clean = imread(CLEAN)
old = imread(OLD)
assert clean is not None and old is not None, "读不到测试图，请先跑 utils/degrade.py"


def smoke():
    """逐一调用所有模块的函数，任一抛异常即定位到具体行。"""
    basic.rotate(basic.resize(old, 0.5), 10); basic.to_gray(old); basic.info(old)
    enhance.hist_equalize(old); enhance.clahe(old); enhance.normalize(old)
    enhance.gamma_transform(old, 0.8); enhance.log_transform(old)
    enhance.piecewise_linear(old); enhance.histogram(old)
    smooth.mean_blur(old); smooth.median_blur(old); smooth.gaussian_blur(old)
    smooth.bilateral(old); smooth.nlmeans(old)
    sharpen.laplacian_sharpen(old); sharpen.sobel_edges(old); sharpen.unsharp_mask(old)
    b, _ = segment.otsu(old)
    segment.threshold(old); segment.adaptive_threshold(old); segment.canny(old)
    morphology.erode(b); morphology.dilate(b); morphology.opening(b)
    morphology.closing(b); morphology.gradient(b); morphology.tophat(old)
    frequency.spectrum(old); frequency.ideal_lowpass(old); frequency.ideal_highpass(old)
    frequency.butterworth_lowpass(old); frequency.butterworth_highpass(old)
    psf = restore.motion_blur_kernel(9, 0)
    restore.add_gaussian_noise(old); restore.inverse_filter(old, psf)
    restore.wiener_filter(old, psf)
    restore.inpaint(old, np.zeros(old.shape[:2], np.uint8))
    if wavelet.available():
        wavelet.wavelet_denoise(old)


print("== 模块冒烟测试 ==")
try:
    smoke()
    print("  [OK] 所有 DIP 模块函数调用通过（pywt 可用: %s）" % wavelet.available())
except Exception:
    traceback.print_exc()
    print("  [FAILED] 冒烟测试失败")

print("\n== 一键修复效果（PSNR/SSIM 越高越接近干净原图）==")
print(f"  修复前(老照片) vs 干净:  PSNR={psnr(old, clean):5.2f} dB   SSIM={ssim(old, clean):.3f}")
fixed = pipeline.one_click_restore(old)
print(f"  修复后         vs 干净:  PSNR={psnr(fixed, clean):5.2f} dB   SSIM={ssim(fixed, clean):.3f}")

print("\n== 导出样例图到 结果/ ==")
samples = {
    "demo_old.jpg": old,
    "demo_fixed.jpg": fixed,
    "demo_clahe.jpg": enhance.clahe(old),
    "demo_canny.jpg": segment.canny(old),
    "demo_spectrum.jpg": frequency.spectrum(old),
}
for name, im in samples.items():
    imwrite(os.path.join(OUT, name), im)
    print("  写出", name)
