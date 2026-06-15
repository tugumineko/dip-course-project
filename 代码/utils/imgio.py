"""Windows 中文路径安全的图像读写。

⚠️ cv2.imread / cv2.imwrite 在 Windows 上**无法处理非 ASCII（中文）路径**，
而本项目整个位于中文路径（数字图像处理\\项目\\素材...）下，故**全项目统一**
用本模块的 imread / imwrite 替代 cv2 的同名函数。

原理：numpy.fromfile 读原始字节 → cv2.imdecode 解码；
      cv2.imencode 编码 → ndarray.tofile 落盘。
"""
from __future__ import annotations

import os

import cv2
import numpy as np


def imread(path, flags=cv2.IMREAD_COLOR):
    """中文路径安全的读图，返回 BGR ndarray；失败返回 None。"""
    try:
        data = np.fromfile(path, dtype=np.uint8)
    except OSError:
        return None
    if data.size == 0:
        return None
    return cv2.imdecode(data, flags)


def imwrite(path, img):
    """中文路径安全的写图。按扩展名编码后落盘，返回是否成功。"""
    ext = os.path.splitext(path)[1] or ".png"
    ok, buf = cv2.imencode(ext, img)
    if not ok:
        return False
    buf.tofile(path)
    return True
