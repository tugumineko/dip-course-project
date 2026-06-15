"""数字图像处理算法库（按课程章节组织，Phase 1 实现）。

计划模块：
    basic.py      第二章   基础操作（灰度/通道/缩放/旋转）
    enhance.py    第四章   对比度增强（手写直方图均衡 + OpenCV 对照）
    smooth.py     第六章   图像平滑（手写中值/均值 + 对照）
    sharpen.py    第七章   图像锐化（手写 Laplacian 卷积 + 对照）
    segment.py    第五章   图像分割（手写 Otsu + Canny）
    morphology.py 第八章   数学形态学（腐蚀/膨胀/开/闭）
    frequency.py  3.2 频域 傅里叶频谱 + 频域滤波（numpy.fft）
    restore.py    第九章   图像恢复（退化/逆滤波/维纳/inpaint）
    wavelet.py    第十章   小波去噪（pywt，可选）
    pipeline.py            一键修复流水线

约定：所有算法 输入/输出 均为 numpy ndarray（BGR 或灰度），不依赖 GUI。
"""
