"""批量生成定制修复对比图、纪念模板效果与 PSNR/SSIM 指标表。

产出全部放到 结果/gallery/ 目录。
运行: E:\miniconda3\envs\ai-service\python.exe 代码\generate_gallery.py
"""
from __future__ import annotations

import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cv2
import matplotlib
import numpy as np
matplotlib.use("Agg")
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt

from utils.imgio import imread, imwrite
from utils.metrics import psnr, ssim
from dip import (basic, enhance, smooth, sharpen, segment, morphology,
                 frequency, restore, wavelet, pipeline, family_restore,
                 commemorative)

PROJ = os.path.dirname(HERE)
GALLERY = os.path.join(PROJ, "结果", "gallery")
RESULTS = os.path.join(PROJ, "结果")
STYLE_DIR = os.path.join(PROJ, "素材", "风格图")
os.makedirs(GALLERY, exist_ok=True)

CLEAN = os.path.join(PROJ, "素材", "干净原图", "test.jpg")
OLD = os.path.join(PROJ, "素材", "合成老照片", "test_old.jpg")
REAL1 = os.path.join(PROJ, "素材", "真实老照片", "R.jpg")
REAL2 = os.path.join(PROJ, "素材", "真实老照片", "R (1).jpg")
MASK = os.path.join(PROJ, "素材", "合成老照片", "test_mask.png")
FAMILY_STYLE = os.path.join(STYLE_DIR, "warm_family_memory_style.jpg")


def side_by_side(before, after, title_l="处理前", title_r="处理后", label=""):
    """matplotlib 横向对比图，返回 BGR ndarray。"""
    def to_rgb(im):
        if im.ndim == 2:
            return cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)
        return cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    ax1.imshow(to_rgb(before))
    ax1.set_title(title_l, fontsize=12)
    ax1.axis("off")
    ax2.imshow(to_rgb(after))
    ax2.set_title(title_r, fontsize=12)
    ax2.axis("off")
    if label:
        fig.suptitle(label, fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3].copy()
    plt.close(fig)
    return cv2.cvtColor(buf, cv2.COLOR_RGB2BGR)


def save(name, img):
    path = os.path.join(GALLERY, name)
    imwrite(path, img)
    print(f"  {name}")


def fit_for_card(img, max_h=520):
    h, w = img.shape[:2]
    if h <= max_h:
        return img
    scale = max_h / h
    return cv2.resize(img, (int(w * scale), max_h), interpolation=cv2.INTER_AREA)


clean = imread(CLEAN)
old = imread(OLD)
mask = imread(MASK, cv2.IMREAD_GRAYSCALE) if os.path.exists(MASK) else None
real = imread(REAL1)
real2 = imread(REAL2)

assert clean is not None, f"Missing {CLEAN}"
assert old is not None, f"Missing {OLD}"

demo = real if real is not None else old
print(f"干净原图: {basic.info(clean)}")
print(f"合成老照片: {basic.info(old)}")
if real is not None:
    print(f"真实老照片: {basic.info(real)}")
print(f"\n产出目录: {GALLERY}\n")

# ═══════════════════════════════════════════════════════
# 1. 家庭老照片定制修复模式
# ═══════════════════════════════════════════════════════
print("== 1. 家庭老照片定制修复模式 ==")
custom_modes = [
    ("温和修复", family_restore.gentle_restore, demo),
    ("泛黄褪色修复", family_restore.restore_faded_yellow_photo, demo),
    ("黑白旧照增强", family_restore.restore_bw_photo, demo),
    ("扫描颗粒修复", family_restore.reduce_photo_grain, demo),
    ("人像清晰化", family_restore.portrait_clarity, demo),
    ("折痕划痕辅助修复", family_restore.scratch_assisted_inpaint, old),
]
for name, func, source in custom_modes:
    result = func(source)
    save(f"custom_{name}.jpg", side_by_side(source, result, "处理前", "处理后", name))

if mask is not None:
    manual_repaired = family_restore.scratch_assisted_inpaint(old, mask=mask, auto=True)
    save("custom_折痕划痕_自动加手动掩膜.jpg",
         side_by_side(old, manual_repaired, "有划痕", "辅助修复后", "折痕划痕辅助修复（自动+掩膜）"))

# ═══════════════════════════════════════════════════════
# 2. 纪念版模板
# ═══════════════════════════════════════════════════════
print("\n== 2. 纪念版模板 ==")
restored_for_memory = family_restore.gentle_restore(demo)
memory_templates = [
    ("复古相册风", commemorative.vintage_album_style),
    ("暖色胶片风", commemorative.warm_film_style),
    ("纪念明信片风", commemorative.postcard_style),
    ("淡彩手绘风", commemorative.soft_handpainted_style),
]
for name, func in memory_templates:
    result = fit_for_card(func(restored_for_memory))
    save(f"memory_{name}.jpg", side_by_side(restored_for_memory, result, "修复版", "纪念版", name))

# ═══════════════════════════════════════════════════════
# 3. 高级算法工具箱示例（压缩展示）
# ═══════════════════════════════════════════════════════
print("\n== 3. 高级算法工具箱示例 ==")
examples = [
    ("ch04_CLAHE.jpg", enhance.clahe(demo), "CLAHE 自适应增强"),
    ("ch06_非局部均值.jpg", smooth.nlmeans(demo, 10), "非局部均值去噪"),
    ("ch07_USM锐化.jpg", sharpen.unsharp_mask(demo, amount=1.2), "USM 锐化"),
    ("ch05_Canny.jpg", segment.canny(demo, 80, 160), "Canny 边缘检测"),
    ("ch08_开运算.jpg", morphology.opening(segment.otsu(demo)[0], 5), "形态学开运算"),
    ("ch03_频谱.jpg", frequency.spectrum(demo), "傅里叶频谱"),
]
for filename, result, label in examples:
    save(filename, side_by_side(demo, result, "原图", label, label))

psf = restore.motion_blur_kernel(15, 0)
blurred = cv2.filter2D(basic.to_gray(clean), -1, psf)
noisy = restore.add_gaussian_noise(blurred, sigma=5)
wie = restore.wiener_filter(noisy, psf, k=0.01)
save("ch09_维纳滤波.jpg", side_by_side(noisy, wie, "退化图", "维纳滤波恢复", "退化模型与维纳滤波"))
if wavelet.available():
    wd = wavelet.wavelet_denoise(demo, thresh=25)
    save("ch10_小波去噪.jpg", side_by_side(demo, wd, "原图", "小波软阈值去噪", "小波去噪"))

# ═══════════════════════════════════════════════════════
# 4. 指标评估
# ═══════════════════════════════════════════════════════
print("\n== 4. PSNR/SSIM 指标 ==")
metrics = []


def add_metric(label, result):
    p = psnr(result, clean)
    s = ssim(result, clean)
    metrics.append({"方法": label, "PSNR (dB)": round(p, 2), "SSIM": round(s, 4)})
    print(f"  {label:20s}  PSNR={p:6.2f} dB  SSIM={s:.4f}")


add_metric("退化老照片 (基线)", old)
add_metric("温和修复", family_restore.gentle_restore(old))
add_metric("泛黄褪色修复", family_restore.restore_faded_yellow_photo(old))
add_metric("扫描颗粒修复", family_restore.reduce_photo_grain(old))
add_metric("人像清晰化", family_restore.portrait_clarity(old))
add_metric("一键修复 (默认)", pipeline.one_click_restore(old))
add_metric("一键修复 (中值)", pipeline.one_click_restore(old, denoise="median"))
add_metric("中值滤波 k=3", smooth.median_blur(old, 3))
add_metric("CLAHE", enhance.clahe(old))
add_metric("白平衡+CLAHE", enhance.clahe(enhance.white_balance(old)))
if wavelet.available():
    add_metric("小波去噪 t=20", wavelet.wavelet_denoise(old, thresh=20))

with open(os.path.join(GALLERY, "metrics.json"), "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)
print("  -> metrics.json")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
labels = [m["方法"] for m in metrics]
psnrs = [m["PSNR (dB)"] for m in metrics]
ssims = [m["SSIM"] for m in metrics]
colors = ["#d32f2f" if i == 0 else "#1976d2" for i in range(len(labels))]

ax1.barh(range(len(labels)), psnrs, color=colors, height=0.6)
ax1.set_yticks(range(len(labels)))
ax1.set_yticklabels(labels, fontsize=9)
ax1.set_xlabel("PSNR (dB)")
ax1.set_title("各方法 PSNR 对比")
ax1.invert_yaxis()
for i, v in enumerate(psnrs):
    ax1.text(v + 0.2, i, f"{v:.1f}", va="center", fontsize=8)

ax2.barh(range(len(labels)), ssims, color=colors, height=0.6)
ax2.set_yticks(range(len(labels)))
ax2.set_yticklabels(labels, fontsize=9)
ax2.set_xlabel("SSIM")
ax2.set_title("各方法 SSIM 对比")
ax2.invert_yaxis()
for i, v in enumerate(ssims):
    ax2.text(v + 0.005, i, f"{v:.3f}", va="center", fontsize=8)

fig.suptitle("修复方法量化对比 (合成老照片 vs 干净原图)", fontweight="bold")
fig.tight_layout()
fig.savefig(os.path.join(GALLERY, "metrics_chart.jpg"), dpi=150)
plt.close(fig)
print("  -> metrics_chart.jpg")

# ═══════════════════════════════════════════════════════
# 5. 自定义 VGG 艺术风格迁移（复用已有结果，不强制现场跑 GPU）
# ═══════════════════════════════════════════════════════
print("\n== 5. 自定义 VGG 艺术风格迁移 ==")
family_vgg = os.path.join(RESULTS, "style_oldphoto_family_memory.jpg")
old_starry = os.path.join(RESULTS, "style_oldphoto_starry.jpg")
content_ref = real2 if real2 is not None else demo

if os.path.exists(family_vgg):
    s_img = imread(family_vgg)
    if s_img is not None:
        save("vgg_家庭暖调风格迁移.jpg",
             side_by_side(content_ref, s_img, "修复后老照片", "家庭暖调艺术风格", "自定义 VGG 艺术风格迁移"))
elif os.path.exists(old_starry):
    s_img = imread(old_starry)
    if s_img is not None:
        save("vgg_艺术风格迁移示例.jpg",
             side_by_side(content_ref, s_img, "修复后老照片", "艺术风格示例", "自定义 VGG 艺术风格迁移（备用示例）"))
else:
    print("  未找到预渲染 VGG 结果，跳过；可用 GUI 或 neural_style.py 生成")

if os.path.exists(FAMILY_STYLE):
    style_img = imread(FAMILY_STYLE)
    if style_img is not None:
        save("vgg_家庭暖调风格图.jpg", fit_for_card(style_img, max_h=420))

# ═══════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════
gallery_files = sorted(os.listdir(GALLERY))
print(f"\n== 完成: {len(gallery_files)} 个文件 ==")
for f in gallery_files:
    sz = os.path.getsize(os.path.join(GALLERY, f)) // 1024
    print(f"  {f} ({sz} KB)")
