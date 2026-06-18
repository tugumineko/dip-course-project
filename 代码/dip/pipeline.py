"""一键修复流水线：（可选划痕修复）→ 去噪 → 对比度增强 → 适度锐化。

按老照片常见退化的合理顺序组合，参数取温和默认值，避免过冲。
"""
from __future__ import annotations

try:
    from . import smooth, enhance, sharpen, restore
except ImportError:
    import smooth, enhance, sharpen, restore


def one_click_restore(img, denoise="nlmeans", color_correct=True,
                      enhance_method="clahe", do_sharpen=True, mask=None):
    """老照片一键修复。

    denoise: nlmeans / median / bilateral / none
    color_correct: 是否做白平衡去偏色（老照片泛黄常用）
    enhance_method: clahe / equalize / none
    mask: 若给定划痕掩膜，先做 inpaint
    """
    out = img
    if mask is not None:                       # 划痕/折痕修复
        out = restore.inpaint(out, mask)
    if denoise == "nlmeans":                   # 去噪
        out = smooth.nlmeans(out, h=8)
    elif denoise == "median":
        out = smooth.median_blur(out, 3)
    elif denoise == "bilateral":
        out = smooth.bilateral(out)
    if color_correct:                          # 色彩校正 / 白平衡（去泛黄偏色）
        out = enhance.white_balance(out)
    if enhance_method == "clahe":              # 对比度增强
        out = enhance.clahe(out)
    elif enhance_method == "equalize":
        out = enhance.hist_equalize(out)
    if do_sharpen:                             # 适度锐化
        out = sharpen.unsharp_mask(out, amount=0.6)
    return out
