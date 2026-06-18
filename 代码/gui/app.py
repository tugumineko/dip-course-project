"""老照片修复与风格化迁移纪念 -- tkinter 主窗口。

功能面板(左) + 原图/结果预览(中) + 参数区(下) + 状态栏。
提供老照片修复向导、高级算法工具箱和艺术纪念版生成。
所有图像 I/O 走 imgio，PhotoImage 保留引用。
"""
from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import cv2
import numpy as np
from PIL import Image, ImageTk

# ── path setup ──────────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.dirname(HERE)
PROJ = os.path.dirname(CODE)
if CODE not in sys.path:
    sys.path.insert(0, CODE)

from utils.imgio import imread, imwrite
from dip import (basic, enhance, smooth, sharpen, segment,
                 morphology, frequency, restore, wavelet, pipeline,
                 family_restore, commemorative)

PREVIEW_MAX = 420
STYLE_DIR = os.path.join(PROJ, "素材", "风格图")


# ── helpers ─────────────────────────────────────────────

def _cv2pil(bgr):
    if bgr.ndim == 2:
        return Image.fromarray(bgr, "L")
    return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))


def _fit(pil, mx):
    w, h = pil.size
    s = min(1.0, mx / max(w, h))
    if s < 1.0:
        return pil.resize((int(w * s), int(h * s)), Image.LANCZOS)
    return pil


# ── application-oriented wrappers ──────────────────────

def _guide_gentle_restore(img):
    return family_restore.gentle_restore(img)


def _motion_blur(img, length=15, angle=0):
    psf = restore.motion_blur_kernel(int(length), angle)
    return cv2.filter2D(img, -1, psf)


def _inverse_deblur(img, length=15, angle=0, eps=0.01):
    psf = restore.motion_blur_kernel(int(length), angle)
    return restore.inverse_filter(img, psf, eps)


def _wiener_deblur(img, length=15, angle=0, k=0.01):
    psf = restore.motion_blur_kernel(int(length), angle)
    return restore.wiener_filter(img, psf, k)


# ── operation registry ─────────────────────────────────
# param_def: (kwarg, display, type, default, ...)
#   "int"   -> (lo, hi)
#   "float" -> (lo, hi)
#   "choice"-> ([options])
#   "bool"  -> ()

OP_GROUPS = [
    ("家庭老照片修复", [
        ("温和修复", family_restore.gentle_restore, []),
        ("泛黄褪色修复", family_restore.restore_faded_yellow_photo, []),
        ("黑白旧照增强", family_restore.restore_bw_photo, []),
        ("扫描颗粒修复", family_restore.reduce_photo_grain, []),
        ("人像清晰化", family_restore.portrait_clarity, []),
        ("折痕划痕辅助修复", family_restore.scratch_assisted_inpaint, []),
    ]),
    ("纪念版生成", [
        ("复古相册风", commemorative.vintage_album_style, []),
        ("暖色胶片风", commemorative.warm_film_style, []),
        ("纪念明信片风", commemorative.postcard_style, []),
        ("淡彩手绘风", commemorative.soft_handpainted_style, []),
    ]),
    ("基础操作", [
        ("灰度化", basic.to_gray, []),
        ("转彩色", basic.to_bgr, []),
        ("旋转", basic.rotate,
         [("angle", "角度", "int", 90, -180, 180)]),
        ("缩放", basic.resize,
         [("scale", "倍率", "float", 0.5, 0.1, 4.0)]),
    ]),
    ("对比度增强", [
        ("直方图均衡", enhance.hist_equalize, []),
        ("CLAHE", enhance.clahe, [
            ("clip", "对比度限制", "float", 2.0, 0.5, 10.0),
            ("grid", "网格大小", "int", 8, 2, 32),
        ]),
        ("正规化", enhance.normalize, []),
        ("分段线性", enhance.piecewise_linear, [
            ("r1", "暗端 r1", "int", 70, 0, 255),
            ("s1", "暗端 s1", "int", 30, 0, 255),
            ("r2", "亮端 r2", "int", 180, 0, 255),
            ("s2", "亮端 s2", "int", 220, 0, 255),
        ]),
        ("对数变换", enhance.log_transform, []),
        ("伽马变换", enhance.gamma_transform,
         [("gamma", "gamma", "float", 1.0, 0.1, 5.0)]),
        ("白平衡", enhance.white_balance, []),
    ]),
    ("平滑去噪", [
        ("均值滤波", smooth.mean_blur,
         [("k", "核大小", "int", 3, 3, 15)]),
        ("中值滤波", smooth.median_blur,
         [("k", "核大小", "int", 3, 3, 15)]),
        ("高斯滤波", smooth.gaussian_blur, [
            ("k", "核大小", "int", 5, 3, 15),
            ("sigma", "sigma", "float", 0, 0, 5.0),
        ]),
        ("双边滤波", smooth.bilateral, [
            ("d", "直径", "int", 9, 3, 15),
            ("sigma_color", "色彩sigma", "float", 75, 10, 200),
            ("sigma_space", "空间sigma", "float", 75, 10, 200),
        ]),
        ("非局部均值", smooth.nlmeans,
         [("h", "降噪强度", "int", 10, 3, 30)]),
    ]),
    ("锐化", [
        ("Laplacian锐化", sharpen.laplacian_sharpen,
         [("strength", "强度", "float", 1.0, 0.1, 5.0)]),
        ("Sobel边缘", sharpen.sobel_edges, []),
        ("USM锐化", sharpen.unsharp_mask,
         [("amount", "强度", "float", 1.0, 0.1, 5.0)]),
    ]),
    ("分割/边缘", [
        ("固定阈值", segment.threshold,
         [("t", "阈值", "int", 127, 0, 255)]),
        ("Otsu自动阈值", lambda img: segment.otsu(img)[0], []),
        ("自适应阈值", segment.adaptive_threshold, [
            ("block", "块大小", "int", 11, 3, 99),
            ("c", "常量C", "int", 2, -10, 10),
        ]),
        ("Canny边缘", segment.canny, [
            ("t1", "低阈值", "int", 100, 0, 255),
            ("t2", "高阈值", "int", 200, 0, 255),
        ]),
    ]),
    ("形态学", [
        ("腐蚀", morphology.erode,
         [("k", "核大小", "int", 3, 3, 15), ("it", "迭代", "int", 1, 1, 5)]),
        ("膨胀", morphology.dilate,
         [("k", "核大小", "int", 3, 3, 15), ("it", "迭代", "int", 1, 1, 5)]),
        ("开运算", morphology.opening,
         [("k", "核大小", "int", 3, 3, 15)]),
        ("闭运算", morphology.closing,
         [("k", "核大小", "int", 3, 3, 15)]),
        ("形态学梯度", morphology.gradient,
         [("k", "核大小", "int", 3, 3, 15)]),
        ("顶帽", morphology.tophat,
         [("k", "核大小", "int", 9, 3, 31)]),
    ]),
    ("图像恢复", [
        ("模拟运动模糊", _motion_blur, [
            ("length", "核长度", "int", 15, 3, 50),
            ("angle", "角度", "int", 0, -90, 90),
        ]),
        ("加高斯噪声", restore.add_gaussian_noise,
         [("sigma", "噪声sigma", "int", 25, 5, 100)]),
        ("逆滤波去模糊", _inverse_deblur, [
            ("length", "核长度", "int", 15, 3, 50),
            ("angle", "角度", "int", 0, -90, 90),
            ("eps", "正则eps", "float", 0.01, 0.001, 0.1),
        ]),
        ("维纳滤波去模糊", _wiener_deblur, [
            ("length", "核长度", "int", 15, 3, 50),
            ("angle", "角度", "int", 0, -90, 90),
            ("k", "噪信比K", "float", 0.01, 0.001, 0.1),
        ]),
    ]),
    ("频域处理", [
        ("傅里叶频谱", frequency.spectrum, []),
        ("理想低通", frequency.ideal_lowpass,
         [("d0", "截止频率", "int", 30, 5, 200)]),
        ("理想高通", frequency.ideal_highpass,
         [("d0", "截止频率", "int", 30, 5, 200)]),
        ("巴特沃斯低通", frequency.butterworth_lowpass, [
            ("d0", "截止频率", "int", 30, 5, 200),
            ("n", "阶数", "int", 2, 1, 10),
        ]),
        ("巴特沃斯高通", frequency.butterworth_highpass, [
            ("d0", "截止频率", "int", 30, 5, 200),
            ("n", "阶数", "int", 2, 1, 10),
        ]),
    ]),
]

if wavelet.available():
    OP_GROUPS.append(("小波去噪", [
        ("小波软阈值", wavelet.wavelet_denoise,
         [("thresh", "阈值", "float", 20.0, 5.0, 100.0)]),
    ]))

OP_GROUPS.append(("一键修复", [
    ("一键修复", pipeline.one_click_restore, [
        ("denoise", "去噪方法", "choice", "nlmeans",
         ["nlmeans", "median", "bilateral", "none"]),
        ("color_correct", "白平衡校正", "bool", True),
        ("enhance_method", "增强方法", "choice", "clahe",
         ["clahe", "equalize", "none"]),
        ("do_sharpen", "USM锐化", "bool", True),
    ]),
]))


# ── main application ───────────────────────────────────

class App:
    MAX_UNDO = 30

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("老照片修复与风格化迁移纪念")
        self.root.geometry("1280x800")
        self.root.minsize(960, 640)

        self.original = None
        self.current = None
        self.history: list[np.ndarray] = []
        self._filepath = None
        self._photo_orig = None
        self._photo_curr = None
        self._busy = False

        self._build_ui()
        self._bind_keys()

    def run(self):
        self.root.mainloop()

    # ── build ───────────────────────────────────────────

    def _build_ui(self):
        self._build_menu()

        body = ttk.Frame(self.root)
        body.pack(fill=tk.BOTH, expand=True)

        self._build_left(body)

        right = ttk.Frame(body)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_preview(right)
        self._build_params(right)
        self._build_status(right)

    def _build_menu(self):
        mb = tk.Menu(self.root)
        self.root.config(menu=mb)

        fm = tk.Menu(mb, tearoff=0)
        fm.add_command(label="打开  Ctrl+O", command=self.open_image)
        fm.add_command(label="保存  Ctrl+S", command=self.save_image)
        fm.add_command(label="导出对比图", command=self.export_comparison)
        fm.add_separator()
        fm.add_command(label="退出", command=self.root.quit)
        mb.add_cascade(label="文件", menu=fm)

        em = tk.Menu(mb, tearoff=0)
        em.add_command(label="撤销  Ctrl+Z", command=self.undo)
        em.add_command(label="重置到原图", command=self.reset)
        mb.add_cascade(label="编辑", menu=em)

        vm = tk.Menu(mb, tearoff=0)
        vm.add_command(label="直方图", command=self._show_histogram)
        vm.add_command(label="图像信息", command=self._show_info)
        mb.add_cascade(label="查看", menu=vm)

        hm = tk.Menu(mb, tearoff=0)
        hm.add_command(label="关于", command=self._show_about)
        mb.add_cascade(label="帮助", menu=hm)

    def _build_left(self, parent):
        left = ttk.Frame(parent, width=230)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)

        canvas = tk.Canvas(left, highlightthickness=0)
        sb = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)

        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _sync(e):
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", _sync)
        canvas.configure(yscrollcommand=sb.set)

        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for title, ops in OP_GROUPS:
            self._add_group(inner, title, ops)
            if title == "家庭老照片修复":
                ttk.Button(inner, text="    手动掩膜修复划痕",
                           command=self._do_inpaint).pack(fill=tk.X, padx=10, pady=(1, 5))
                ttk.Separator(inner).pack(fill=tk.X, pady=4)
            if title == "纪念版生成":
                ttk.Button(inner, text="    自定义艺术风格迁移（VGG）",
                           command=self._open_style_panel).pack(fill=tk.X, padx=10, pady=(1, 5))
                ttk.Separator(inner).pack(fill=tk.X, pady=4)

        def _wheel(e):
            canvas.yview_scroll(-1 * (e.delta // 120), "units")

        def _bind_wheel(w):
            w.bind("<MouseWheel>", _wheel)
            for c in w.winfo_children():
                _bind_wheel(c)
        _bind_wheel(canvas)
        _bind_wheel(inner)

    def _add_group(self, parent, title, ops):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, padx=2, pady=1)

        content = ttk.Frame(frame)
        expanded = [True]

        def toggle():
            if expanded[0]:
                content.pack_forget()
                hdr.configure(text="  ▸  " + title)
            else:
                content.pack(fill=tk.X)
                hdr.configure(text="  ▼  " + title)
            expanded[0] = not expanded[0]

        hdr = ttk.Button(frame, text="  ▼  " + title, command=toggle)
        hdr.pack(fill=tk.X)
        content.pack(fill=tk.X)

        for label, func, params in ops:
            ttk.Button(
                content, text="    " + label,
                command=lambda f=func, p=params, lb=label: self._on_op(f, p, lb)
            ).pack(fill=tk.X, padx=8)

    def _build_preview(self, parent):
        pf = ttk.LabelFrame(parent, text="预览")
        pf.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        inner = ttk.Frame(pf)
        inner.pack(fill=tk.BOTH, expand=True)
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(2, weight=1)
        inner.rowconfigure(1, weight=1)

        ttk.Label(inner, text="原图", anchor="center",
                  font=("", 10, "bold")).grid(row=0, column=0, sticky="ew")
        ttk.Separator(inner, orient="vertical").grid(
            row=0, column=1, rowspan=3, sticky="ns", padx=4)
        ttk.Label(inner, text="当前结果", anchor="center",
                  font=("", 10, "bold")).grid(row=0, column=2, sticky="ew")

        self.lbl_orig = ttk.Label(inner, anchor="center",
                                  text="← 文件 > 打开图片")
        self.lbl_orig.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.lbl_curr = ttk.Label(inner, anchor="center")
        self.lbl_curr.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)

        self.lbl_orig_info = ttk.Label(inner, text="", anchor="center",
                                       foreground="gray")
        self.lbl_orig_info.grid(row=2, column=0, sticky="ew")
        self.lbl_curr_info = ttk.Label(inner, text="", anchor="center",
                                       foreground="gray")
        self.lbl_curr_info.grid(row=2, column=2, sticky="ew")

    def _build_params(self, parent):
        self.param_frame = ttk.LabelFrame(parent, text="参数")
        self.param_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(self.param_frame, text="选择左侧功能后在此调参",
                  foreground="gray").pack(padx=10, pady=8)

    def _build_status(self, parent):
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(parent, textvariable=self.status_var,
                  relief="sunken", anchor="w").pack(fill=tk.X, padx=5, pady=2)

    def _bind_keys(self):
        self.root.bind("<Control-o>", lambda e: self.open_image())
        self.root.bind("<Control-s>", lambda e: self.save_image())
        self.root.bind("<Control-z>", lambda e: self.undo())

    # ── file ops ────────────────────────────────────────

    def open_image(self):
        path = filedialog.askopenfilename(
            title="打开图片",
            filetypes=[("图片", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"),
                       ("所有文件", "*.*")])
        if not path:
            return
        img = imread(path)
        if img is None:
            messagebox.showerror("错误", f"无法读取:\n{path}")
            return
        self._filepath = path
        self.original = img.copy()
        self.current = img.copy()
        self.history.clear()
        self._update_preview()
        self._status(f"已打开 {os.path.basename(path)}  {basic.info(img)}")

    def save_image(self):
        if self.current is None:
            messagebox.showwarning("提示", "没有可保存的图片")
            return
        path = filedialog.asksaveasfilename(
            title="保存结果", defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("BMP", "*.bmp")])
        if path:
            imwrite(path, self.current)
            self._status(f"已保存 {path}")

    def export_comparison(self):
        if self.original is None:
            messagebox.showwarning("提示", "没有图片")
            return
        path = filedialog.asksaveasfilename(
            title="导出对比图", defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if not path:
            return
        h = min(600, self.original.shape[0])

        def _fit_cv(im):
            im = basic.to_bgr(im)
            s = h / im.shape[0]
            return cv2.resize(im, (int(im.shape[1] * s), h))

        a, b = _fit_cv(self.original), _fit_cv(self.current)
        gap = np.full((h, 10, 3), 255, np.uint8)
        imwrite(path, cv2.hconcat([a, gap, b]))
        self._status(f"对比图已导出 {path}")

    # ── edit ops ────────────────────────────────────────

    def undo(self):
        if not self.history:
            self._status("无可撤销")
            return
        self.current = self.history.pop()
        self._update_preview()
        self._status(f"已撤销 (剩余{len(self.history)}步)")

    def reset(self):
        if self.original is None:
            return
        self.history.clear()
        self.current = self.original.copy()
        self._update_preview()
        self._status("已重置到原图")

    # ── operation handling ──────────────────────────────

    def _on_op(self, func, params, label):
        if self.current is None:
            messagebox.showwarning("提示", "请先打开图片")
            return
        if self._busy:
            return
        if not params:
            self._apply(func, {}, label)
        else:
            self._show_params(func, params, label)

    def _show_params(self, func, params, label):
        for w in self.param_frame.winfo_children():
            w.destroy()
        self.param_frame.configure(text=f"参数 — {label}")

        vars_ = {}
        for row, pdef in enumerate(params):
            name, disp, ptype, default = pdef[0], pdef[1], pdef[2], pdef[3]

            ttk.Label(self.param_frame, text=disp).grid(
                row=row, column=0, sticky="w", padx=5, pady=2)

            if ptype == "int":
                lo, hi = pdef[4], pdef[5]
                var = tk.IntVar(value=int(default))
                tk.Scale(self.param_frame, from_=lo, to=hi,
                         orient="horizontal", variable=var,
                         length=200).grid(row=row, column=1, sticky="ew", padx=5)
                vars_[name] = var

            elif ptype == "float":
                lo, hi = pdef[4], pdef[5]
                rng = hi - lo
                res = (0.001 if rng < 0.5 else
                       0.01 if rng < 5 else
                       0.1 if rng <= 20 else 1.0)
                var = tk.DoubleVar(value=float(default))
                tk.Scale(self.param_frame, from_=lo, to=hi,
                         orient="horizontal", variable=var,
                         resolution=res, length=200).grid(
                    row=row, column=1, sticky="ew", padx=5)
                vars_[name] = var

            elif ptype == "choice":
                opts = pdef[4]
                var = tk.StringVar(value=default)
                ttk.Combobox(self.param_frame, textvariable=var,
                             values=opts, state="readonly",
                             width=14).grid(row=row, column=1, sticky="w", padx=5)
                vars_[name] = var

            elif ptype == "bool":
                var = tk.BooleanVar(value=default)
                ttk.Checkbutton(self.param_frame, variable=var).grid(
                    row=row, column=1, sticky="w", padx=5)
                vars_[name] = var

        self.param_frame.columnconfigure(1, weight=1)
        ttk.Button(
            self.param_frame, text="应用",
            command=lambda: self._apply(
                func, {k: v.get() for k, v in vars_.items()}, label)
        ).grid(row=len(params), column=0, columnspan=2, pady=6)

    def _apply(self, func, kwargs, label):
        if self.current is None or self._busy:
            return
        try:
            self._push_history()
            result = func(self.current, **kwargs)
            if result is None:
                raise ValueError("操作返回空结果")
            self.current = result
            self._update_preview()
            self._status(f"已应用: {label}")
        except Exception as exc:
            if self.history:
                self.history.pop()
            messagebox.showerror("处理错误", f"{label}:\n{exc}")

    def _push_history(self):
        self.history.append(self.current.copy())
        while len(self.history) > self.MAX_UNDO:
            self.history.pop(0)

    # ── preview ─────────────────────────────────────────

    def _preview_max(self):
        """Compute preview size from current window geometry."""
        try:
            avail = self.lbl_orig.winfo_height()
            if avail > 50:
                return max(200, avail - 10)
        except Exception:
            pass
        return PREVIEW_MAX

    def _update_preview(self):
        if self.original is None:
            return
        mx = self._preview_max()
        self._photo_orig = ImageTk.PhotoImage(
            _fit(_cv2pil(self.original), mx))
        self._photo_curr = ImageTk.PhotoImage(
            _fit(_cv2pil(self.current), mx))
        self.lbl_orig.configure(image=self._photo_orig, text="")
        self.lbl_curr.configure(image=self._photo_curr, text="")
        self.lbl_orig_info.configure(text=basic.info(self.original))
        self.lbl_curr_info.configure(text=basic.info(self.current))

    # ── special ops ─────────────────────────────────────

    def _do_inpaint(self):
        if self.current is None:
            messagebox.showwarning("提示", "请先打开图片")
            return
        path = filedialog.askopenfilename(
            title="选择掩膜图片（白色区域 = 划痕/折痕/破损）",
            filetypes=[("图片", "*.jpg *.png *.bmp"), ("所有", "*.*")])
        if not path:
            return
        mask = imread(path, cv2.IMREAD_GRAYSCALE)
        if mask is None:
            messagebox.showerror("错误", "无法读取掩膜")
            return
        if mask.shape[:2] != self.current.shape[:2]:
            mask = cv2.resize(mask, (self.current.shape[1], self.current.shape[0]))
        self._push_history()
        self.current = restore.inpaint(self.current, mask)
        self._update_preview()
        self._status("已应用: 划痕/折痕修复 (Inpaint)")

    def _open_style_panel(self):
        if self.current is None:
            messagebox.showwarning("提示", "请先打开图片")
            return
        if self._busy:
            return
        from gui.style_panel import StylePanel
        StylePanel(self.root, self.current.copy(), STYLE_DIR,
                   self._on_style_done)

    def _on_style_done(self, result):
        if result is not None:
            self._push_history()
            self.current = result
            self._update_preview()
            self._status("已应用: 自定义艺术风格迁移")

    # ── view dialogs ────────────────────────────────────

    def _show_histogram(self):
        if self.current is None:
            return
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import matplotlib
            matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
            matplotlib.rcParams["axes.unicode_minus"] = False
        except ImportError:
            messagebox.showerror("缺少依赖", "需要安装 matplotlib")
            return

        win = tk.Toplevel(self.root)
        win.title("直方图")
        win.geometry("520x320")
        fig = Figure(figsize=(5.2, 3), dpi=100)
        ax = fig.add_subplot(111)

        if self.current.ndim == 2:
            h = cv2.calcHist([self.current], [0], None, [256],
                             [0, 256]).flatten()
            ax.bar(range(256), h, color="gray", width=1)
            ax.set_title("灰度直方图")
        else:
            for i, (color, name) in enumerate(
                    zip(["b", "g", "r"], ["B", "G", "R"])):
                h = cv2.calcHist([self.current], [i], None, [256],
                                 [0, 256]).flatten()
                ax.plot(h, color=color, label=name, linewidth=0.8)
            ax.legend()
            ax.set_title("彩色直方图")
        ax.set_xlim(0, 255)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _show_info(self):
        if self.current is None:
            messagebox.showinfo("图像信息", "未打开图片")
            return
        msg = (f"原图: {basic.info(self.original)}\n"
               f"当前: {basic.info(self.current)}\n"
               f"撤销步数: {len(self.history)}")
        if self._filepath:
            msg = f"文件: {self._filepath}\n" + msg
        messagebox.showinfo("图像信息", msg)

    def _show_about(self):
        messagebox.showinfo("关于",
            "老照片修复与风格化迁移纪念\n\n"
            "ECNU SEI 数字图像处理 2026 期末项目\n"
            "指导老师: 曹桂涛 教授\n\n"
            "面向老照片修复、精修与艺术纪念版生成\n"
            "框架: OpenCV + PyTorch + tkinter")

    # ── status ──────────────────────────────────────────

    def _status(self, msg):
        self.status_var.set(msg)
