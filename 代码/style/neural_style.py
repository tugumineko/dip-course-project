"""图像风格迁移 —— Gatys 优化法（A Neural Algorithm of Artistic Style, 2015）。

只用 torchvision 预训练 VGG19 当"特征提取器"，**不训练任何网络、不需数据集**：
- 内容损失：输出图与内容图在深层特征图(conv4_2)上的差异（保留结构）
- 风格损失：输出图与风格图在多层特征的 Gram 矩阵（通道相关性）差异（学笔触/色彩）
- 从内容图出发，对输出图的像素做梯度下降，最小化 content_weight·内容 + style_weight·风格

对应课程第十一章（CNN/深度学习基础）。GPU 自动（无则回退 CPU）。
"""
from __future__ import annotations

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from torchvision.models import vgg19, VGG19_Weights

try:
    from utils.imgio import imread, imwrite
except ImportError:
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.imgio import imread, imwrite

_MEAN = [0.485, 0.456, 0.406]      # ImageNet 归一化（VGG 训练时所用）
_STD = [0.229, 0.224, 0.225]
_CONTENT_LAYERS = ["21"]                          # conv4_2
_STYLE_LAYERS = ["0", "5", "10", "19", "28"]      # conv1_1,2_1,3_1,4_1,5_1


def _device(prefer_gpu=True):
    return torch.device("cuda" if prefer_gpu and torch.cuda.is_available() else "cpu")


def _to_tensor(bgr, max_size, device):
    if bgr.ndim == 2:
        bgr = cv2.cvtColor(bgr, cv2.COLOR_GRAY2BGR)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    h, w = rgb.shape[:2]
    scale = min(1.0, max_size / max(h, w))
    if scale < 1.0:
        rgb = cv2.resize(rgb, (int(w * scale), int(h * scale)))
    t = torch.from_numpy(rgb).float().permute(2, 0, 1) / 255.0
    mean = torch.tensor(_MEAN).view(3, 1, 1)
    std = torch.tensor(_STD).view(3, 1, 1)
    return ((t - mean) / std).unsqueeze(0).contiguous().to(device)


def _to_image(tensor):
    mean = torch.tensor(_MEAN).view(3, 1, 1).to(tensor.device)
    std = torch.tensor(_STD).view(3, 1, 1).to(tensor.device)
    t = (tensor.squeeze(0) * std + mean).clamp(0, 1)
    arr = t.mul(255).byte().permute(1, 2, 0).cpu().numpy()
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def _gram(feat):
    _, c, h, w = feat.size()
    f = feat.view(c, h * w)
    return (f @ f.t()) / (c * h * w)


def stylize(content_bgr, style_bgr, iterations=200, style_weight=1e6,
            content_weight=1.0, max_size=512, prefer_gpu=True, progress=None):
    """对 content 应用 style 的艺术风格，返回 BGR 结果（uint8）。

    iterations: L-BFGS 迭代步数（200~300）；max_size: 处理长边（显存安全 ≤720）。
    progress(step, total): 可选回调，供 GUI 进度条（在工作线程里被调用）。
    """
    device = _device(prefer_gpu)
    content = _to_tensor(content_bgr, max_size, device)
    style = _to_tensor(style_bgr, max_size, device)
    style = F.interpolate(style, size=content.shape[2:], mode="bilinear", align_corners=False)

    vgg = vgg19(weights=VGG19_Weights.IMAGENET1K_V1).features.to(device).eval()
    for p in vgg.parameters():
        p.requires_grad_(False)

    last = _STYLE_LAYERS[-1]

    def features(x):
        feats, out = {}, x
        for name, layer in vgg._modules.items():
            out = layer(out)
            if name in _CONTENT_LAYERS or name in _STYLE_LAYERS:
                feats[name] = out
            if name == last:
                break
        return feats

    with torch.no_grad():
        cf = features(content)
        sf = features(style)
        c_targets = {l: cf[l].detach() for l in _CONTENT_LAYERS}
        s_targets = {l: _gram(sf[l]).detach() for l in _STYLE_LAYERS}

    target = content.clone().contiguous().requires_grad_(True)
    optimizer = torch.optim.LBFGS([target], max_iter=iterations, lr=1.0,
                                  line_search_fn="strong_wolfe")
    step = [0]

    def closure():
        optimizer.zero_grad()
        f = features(target)
        c_loss = sum(F.mse_loss(f[l], c_targets[l]) for l in _CONTENT_LAYERS)
        s_loss = sum(F.mse_loss(_gram(f[l]), s_targets[l]) for l in _STYLE_LAYERS)
        loss = content_weight * c_loss + style_weight * s_loss
        loss.backward()
        step[0] += 1
        if progress is not None:
            progress(min(step[0], iterations), iterations)
        return loss

    optimizer.step(closure)
    return _to_image(target.detach())


def device_name(prefer_gpu=True):
    d = _device(prefer_gpu)
    return torch.cuda.get_device_name(0) if d.type == "cuda" else "CPU"


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Gatys 风格迁移")
    ap.add_argument("content")
    ap.add_argument("style")
    ap.add_argument("output")
    ap.add_argument("--iters", type=int, default=200)
    ap.add_argument("--size", type=int, default=512)
    ap.add_argument("--style-weight", type=float, default=1e6)
    args = ap.parse_args()

    c = imread(args.content)
    s = imread(args.style)
    if c is None or s is None:
        raise SystemExit("读不到图片")

    def prog(i, n):
        if i % 25 == 0 or i == n:
            print(f"  迭代 {i}/{n}")

    print(f"设备: {device_name()}")
    out = stylize(c, s, iterations=args.iters, max_size=args.size,
                  style_weight=args.style_weight, progress=prog)
    imwrite(args.output, out)
    print(f"OK 风格化 -> {args.output}")


if __name__ == "__main__":
    main()
