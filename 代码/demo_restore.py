"""对单张图片跑一键修复，输出 修复图 + 前后对比图 到 结果/。

用法：E:\\miniconda3\\envs\\ai-service\\python.exe 代码\\demo_restore.py 输入图
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import cv2
import numpy as np

from utils.imgio import imread, imwrite
from dip import pipeline, basic


def side_by_side(before, after, max_h=600):
    """原图 | 修复图 横向拼接（等高），中间留白缝。"""
    def fit(im):
        im = basic.to_bgr(im)
        s = max_h / im.shape[0]
        return cv2.resize(im, (int(round(im.shape[1] * s)), max_h))
    b, a = fit(before), fit(after)
    gap = np.full((max_h, 14, 3), 255, np.uint8)
    return cv2.hconcat([b, gap, a])


def main():
    if len(sys.argv) < 2:
        raise SystemExit("用法: demo_restore.py 输入图")
    inp = sys.argv[1]
    img = imread(inp)
    if img is None:
        raise SystemExit(f"读不到图片: {inp}")

    fixed = pipeline.one_click_restore(img)

    out_dir = os.path.join(os.path.dirname(HERE), "结果")
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(inp))[0]
    p_fixed = os.path.join(out_dir, f"{stem}_修复.jpg")
    p_cmp = os.path.join(out_dir, f"{stem}_对比.jpg")
    imwrite(p_fixed, fixed)
    imwrite(p_cmp, side_by_side(img, fixed))

    print(f"输入: {basic.info(img)}")
    print(f"修复图 -> {p_fixed}")
    print(f"对比图 -> {p_cmp}")


if __name__ == "__main__":
    main()
