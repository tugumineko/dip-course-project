"""Phase 4: 批量生成对比图 + PSNR/SSIM 指标表。

为报告/演讲稿/幻灯片准备素材:
  1. 每章核心操作的 before/after 对比图 (用合成+真实老照片)
  2. 一键修复 + 各去噪方法的 PSNR/SSIM 量化对照表
  3. 风格迁移效果图 (如已有则跳过, 因 GPU 耗时)

产出全部放到 结果/gallery/ 目录。

运行: E:\\miniconda3\\envs\\ai-service\\python.exe generate_gallery.py
"""
import os
import sys
import json

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt

from utils.imgio import imread, imwrite
from utils.metrics import psnr, ssim
from dip import (basic, enhance, smooth, sharpen, segment,
                 morphology, frequency, restore, wavelet, pipeline)

PROJ = os.path.dirname(HERE)
GALLERY = os.path.join(PROJ, "结果", "gallery")
os.makedirs(GALLERY, exist_ok=True)

CLEAN = os.path.join(PROJ, "素材", "干净原图", "test.jpg")
OLD = os.path.join(PROJ, "素材", "合成老照片", "test_old.jpg")
REAL1 = os.path.join(PROJ, "素材", "真实老照片", "R.jpg")
REAL2 = os.path.join(PROJ, "素材", "真实老照片", "R (1).jpg")
MASK = os.path.join(PROJ, "素材", "合成老照片", "test_mask.png")


def side_by_side(before, after, title_l="处理前", title_r="处理后",
                 label="", max_h=400):
    """matplotlib 横向对比图, 返回 BGR ndarray。"""
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


# ── load images ─────────────────────────────────────────

clean = imread(CLEAN)
old = imread(OLD)
mask = imread(MASK, cv2.IMREAD_GRAYSCALE) if os.path.exists(MASK) else None
real = imread(REAL1)

assert clean is not None, f"Missing {CLEAN}"
assert old is not None, f"Missing {OLD}"

# Use real photo or fall back to synthetic
demo = real if real is not None else old
print(f"干净原图: {basic.info(clean)}")
print(f"合成老照片: {basic.info(old)}")
if real is not None:
    print(f"真实老照片: {basic.info(real)}")

print(f"\n产出目录: {GALLERY}\n")


# ═══════════════════════════════════════════════════════
# 1. 各章对比图 (用真实老照片展示效果)
# ═══════════════════════════════════════════════════════
print("== 1. 各章操作对比图 ==")

# 第二章: 灰度化
gray = basic.to_gray(demo)
save("ch02_灰度化.jpg",
     side_by_side(demo, gray, "原图", "灰度化", "第二章 灰度化"))

# 第四章: 对比度增强
for name, func, label in [
    ("直方图均衡", enhance.hist_equalize, "直方图均衡化"),
    ("CLAHE", enhance.clahe, "CLAHE 自适应均衡"),
    ("伽马变换", lambda im: enhance.gamma_transform(im, gamma=0.6), "伽马变换 (gamma=0.6)"),
    ("白平衡", enhance.white_balance, "灰度世界白平衡"),
]:
    result = func(demo)
    save(f"ch04_{name}.jpg",
         side_by_side(demo, result, "原图", label, f"第四章 {label}"))

# 直方图对比图
fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
for ax, im, title in [(axes[0], demo, "原图直方图"),
                       (axes[1], enhance.hist_equalize(demo), "均衡后直方图")]:
    if im.ndim == 3:
        for i, (c, n) in enumerate(zip(["b", "g", "r"], ["B", "G", "R"])):
            h = cv2.calcHist([im], [i], None, [256], [0, 256]).flatten()
            ax.plot(h, color=c, label=n, linewidth=0.8)
        ax.legend()
    else:
        h = cv2.calcHist([im], [0], None, [256], [0, 256]).flatten()
        ax.bar(range(256), h, color="gray", width=1)
    ax.set_xlim(0, 255)
    ax.set_title(title)
fig.suptitle("第四章 直方图均衡 -- 直方图对比", fontweight="bold")
fig.tight_layout()
fig.savefig(os.path.join(GALLERY, "ch04_直方图对比.jpg"), dpi=150)
plt.close(fig)
print("  ch04_直方图对比.jpg")

# 第六章: 平滑去噪
for name, func, label in [
    ("中值滤波", lambda im: smooth.median_blur(im, 5), "中值滤波 (k=5)"),
    ("高斯滤波", lambda im: smooth.gaussian_blur(im, 5, 1.0), "高斯滤波 (k=5)"),
    ("双边滤波", smooth.bilateral, "双边滤波 (保边去噪)"),
    ("非局部均值", lambda im: smooth.nlmeans(im, 10), "非局部均值去噪 (h=10)"),
]:
    result = func(demo)
    save(f"ch06_{name}.jpg",
         side_by_side(demo, result, "原图", label, f"第六章 {label}"))

# 第七章: 锐化
for name, func, label in [
    ("USM锐化", lambda im: sharpen.unsharp_mask(im, amount=1.5), "USM 锐化 (amount=1.5)"),
    ("Laplacian", lambda im: sharpen.laplacian_sharpen(im, 1.5), "Laplacian 锐化"),
    ("Sobel边缘", sharpen.sobel_edges, "Sobel 梯度幅值"),
]:
    result = func(demo)
    save(f"ch07_{name}.jpg",
         side_by_side(demo, result, "原图", label, f"第七章 {label}"))

# 第五章: 分割/边缘
for name, func, label in [
    ("Otsu", lambda im: segment.otsu(im)[0], "Otsu 自动阈值"),
    ("Canny", lambda im: segment.canny(im, 80, 160), "Canny 边缘检测"),
    ("自适应阈值", segment.adaptive_threshold, "自适应阈值"),
]:
    result = func(demo)
    save(f"ch05_{name}.jpg",
         side_by_side(demo, result, "原图", label, f"第五章 {label}"))

# 第八章: 形态学 (在二值图上操作更直观)
binary = segment.otsu(demo)[0]
for name, func, label in [
    ("腐蚀", lambda im: morphology.erode(im, 3, 2), "腐蚀 (k=3, iter=2)"),
    ("膨胀", lambda im: morphology.dilate(im, 3, 2), "膨胀 (k=3, iter=2)"),
    ("开运算", lambda im: morphology.opening(im, 5), "开运算 (去噪点)"),
    ("闭运算", lambda im: morphology.closing(im, 5), "闭运算 (填孔洞)"),
]:
    result = func(binary)
    save(f"ch08_{name}.jpg",
         side_by_side(binary, result, "二值图", label, f"第八章 {label}"))

# 第九章: 图像恢复 (用合成图展示, 因有干净原图可对照)
psf = restore.motion_blur_kernel(15, 0)
blurred = cv2.filter2D(basic.to_gray(clean), -1, psf)
noisy = restore.add_gaussian_noise(blurred, sigma=5)
inv = restore.inverse_filter(noisy, psf, eps=0.02)
wie = restore.wiener_filter(noisy, psf, k=0.01)
save("ch09_退化模拟.jpg",
     side_by_side(clean, noisy, "干净原图", "运动模糊+噪声 (模拟退化)",
                  "第九章 退化模型 g=h*f+n"))
save("ch09_逆滤波.jpg",
     side_by_side(noisy, inv, "退化图", "逆滤波恢复",
                  "第九章 逆滤波"))
save("ch09_维纳滤波.jpg",
     side_by_side(noisy, wie, "退化图", "维纳滤波恢复",
                  "第九章 维纳滤波"))
if mask is not None:
    scratched = old
    repaired = restore.inpaint(scratched, mask)
    save("ch09_划痕修复.jpg",
         side_by_side(scratched, repaired, "有划痕", "Inpaint 修复",
                      "第九章 划痕修复 (Inpaint)"))

# 第3.2章: 频域
spec = frequency.spectrum(demo)
lp = frequency.butterworth_lowpass(demo, d0=40)
hp = frequency.butterworth_highpass(demo, d0=40)
save("ch03_频谱.jpg",
     side_by_side(demo, spec, "原图", "傅里叶幅度谱",
                  "第3.2章 傅里叶频谱"))
save("ch03_低通.jpg",
     side_by_side(demo, lp, "原图", "巴特沃斯低通 (D0=40)",
                  "第3.2章 频域低通滤波"))
save("ch03_高通.jpg",
     side_by_side(demo, hp, "原图", "巴特沃斯高通 (D0=40)",
                  "第3.2章 频域高通滤波"))

# 第十章: 小波
if wavelet.available():
    wd = wavelet.wavelet_denoise(demo, thresh=25)
    save("ch10_小波去噪.jpg",
         side_by_side(demo, wd, "原图", "小波软阈值去噪",
                      "第十章 小波去噪"))


# ═══════════════════════════════════════════════════════
# 2. 一键修复对比 (合成 + 真实)
# ═══════════════════════════════════════════════════════
print("\n== 2. 一键修复对比图 ==")

fixed_syn = pipeline.one_click_restore(old)
save("一键修复_合成.jpg",
     side_by_side(old, fixed_syn, "合成老照片", "一键修复后",
                  "一键修复流水线 (合成样张)"))

if real is not None:
    fixed_real = pipeline.one_click_restore(real)
    save("一键修复_真实.jpg",
         side_by_side(real, fixed_real, "真实老照片", "一键修复后",
                      "一键修复流水线 (真实老照片)"))

# 真实老照片 R(1) 如果有
real2 = imread(REAL2)
if real2 is not None:
    fixed_real2 = pipeline.one_click_restore(real2)
    save("一键修复_真实2.jpg",
         side_by_side(real2, fixed_real2, "真实老照片 2", "一键修复后",
                      "一键修复流水线 (真实老照片 2)"))


# ═══════════════════════════════════════════════════════
# 3. PSNR/SSIM 指标表 (合成样张)
# ═══════════════════════════════════════════════════════
print("\n== 3. PSNR/SSIM 指标 (合成老照片 vs 干净原图) ==")

metrics = []


def add_metric(label, result):
    p = psnr(result, clean)
    s = ssim(result, clean)
    metrics.append({"方法": label, "PSNR (dB)": round(p, 2), "SSIM": round(s, 4)})
    print(f"  {label:20s}  PSNR={p:6.2f} dB  SSIM={s:.4f}")


add_metric("退化老照片 (基线)", old)
add_metric("中值滤波 k=3", smooth.median_blur(old, 3))
add_metric("中值滤波 k=5", smooth.median_blur(old, 5))
add_metric("高斯滤波 k=5", smooth.gaussian_blur(old, 5, 1.0))
add_metric("双边滤波", smooth.bilateral(old))
add_metric("非局部均值 h=8", smooth.nlmeans(old, 8))
add_metric("非局部均值 h=12", smooth.nlmeans(old, 12))
add_metric("CLAHE", enhance.clahe(old))
add_metric("直方图均衡", enhance.hist_equalize(old))
add_metric("白平衡+CLAHE",
           enhance.clahe(enhance.white_balance(old)))
if wavelet.available():
    add_metric("小波去噪 t=20", wavelet.wavelet_denoise(old, thresh=20))
add_metric("一键修复 (默认)", pipeline.one_click_restore(old))
add_metric("一键修复 (中值)", pipeline.one_click_restore(old, denoise="median"))
add_metric("一键修复 (双边)", pipeline.one_click_restore(old, denoise="bilateral"))

# Save metrics JSON
with open(os.path.join(GALLERY, "metrics.json"), "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)
print("  -> metrics.json")

# Plot metrics bar chart
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
# 4. 风格迁移效果 (复用已有结果, 不重新跑 GPU)
# ═══════════════════════════════════════════════════════
print("\n== 4. 风格迁移 ==")
RESULTS = os.path.join(PROJ, "结果")
style_bus = os.path.join(RESULTS, "style_bus_starry.jpg")
style_old = os.path.join(RESULTS, "style_oldphoto_starry.jpg")

if os.path.exists(style_old):
    s_img = imread(style_old)
    # Use the restored real2 or real as content reference
    content_ref = imread(REAL2) if os.path.exists(REAL2) else demo
    if content_ref is not None and s_img is not None:
        save("风格迁移_老照片星空.jpg",
             side_by_side(content_ref, s_img,
                          "修复后老照片", "梵高《星空》风格",
                          "风格迁移: Gatys + VGG19"))
    print("  (复用已有风格迁移结果)")
else:
    print("  (未找到已有结果, 跳过; 可从 GUI 手动生成)")


# ═══════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════
gallery_files = sorted(os.listdir(GALLERY))
print(f"\n== 完成: {len(gallery_files)} 个文件 ==")
for f in gallery_files:
    sz = os.path.getsize(os.path.join(GALLERY, f)) // 1024
    print(f"  {f} ({sz} KB)")
