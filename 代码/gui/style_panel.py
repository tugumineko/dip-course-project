"""风格迁移子面板 -- 后台线程运行 Gatys 优化法，避免 UI 卡死 (R-2)。

从主窗口点击 "风格迁移 [进阶]" 打开此面板。
选择/上传风格图 -> 调节参数 -> 后台线程 stylize() -> 完成后回调主窗口。
"""
from __future__ import annotations

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageTk

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.dirname(HERE)
if CODE not in sys.path:
    sys.path.insert(0, CODE)

from utils.imgio import imread

THUMB_SIZE = 100


class StylePanel(tk.Toplevel):

    def __init__(self, parent, content_bgr, style_dir, on_done):
        """
        content_bgr: 当前图像 (BGR ndarray)
        style_dir:   预设风格图目录
        on_done:     callback(result_bgr) 迁移完成后调用
        """
        super().__init__(parent)
        self.title("图像风格迁移")
        self.geometry("560x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._content = content_bgr
        self._style_dir = style_dir
        self._on_done = on_done
        self._style_path = None
        self._thumbs = []
        self._running = False

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build()

    # ── build ───────────────────────────────────────────

    def _build(self):
        ttk.Label(self, text="选择风格图:",
                  font=("", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 4))

        tf = ttk.Frame(self)
        tf.pack(fill=tk.X, padx=10)

        styles = self._find_styles()
        for col, path in enumerate(styles):
            thumb = self._make_thumb(path)
            if not thumb:
                continue
            self._thumbs.append(thumb)
            btn = tk.Button(tf, image=thumb, relief="groove", bd=1,
                            command=lambda p=path: self._select(p))
            btn.grid(row=0, column=col, padx=4, pady=2)
            name = os.path.splitext(os.path.basename(path))[0]
            ttk.Label(tf, text=name, font=("", 8)).grid(row=1, column=col)

        ttk.Button(tf, text="+ 上传",
                   command=self._upload).grid(row=0, column=len(styles), padx=6)

        self._sel_var = tk.StringVar(value="未选择风格图")
        ttk.Label(self, textvariable=self._sel_var,
                  foreground="gray").pack(anchor="w", padx=10, pady=4)

        # ── parameters ─────────────────────────────────
        pf = ttk.LabelFrame(self, text="参数")
        pf.pack(fill=tk.X, padx=10, pady=4)

        ttk.Label(pf, text="风格强度 (1含蓄 ~ 10极强)").grid(
            row=0, column=0, padx=5, sticky="w")
        self._var_w = tk.IntVar(value=3)
        tk.Scale(pf, from_=1, to=10, orient="horizontal",
                 variable=self._var_w, length=200).grid(
            row=0, column=1, padx=5)

        ttk.Label(pf, text="迭代步数").grid(
            row=1, column=0, padx=5, sticky="w")
        self._var_it = tk.IntVar(value=200)
        tk.Scale(pf, from_=50, to=500, orient="horizontal",
                 variable=self._var_it, resolution=50, length=200).grid(
            row=1, column=1, padx=5)

        ttk.Label(pf, text="处理尺寸 (px长边)").grid(
            row=2, column=0, padx=5, sticky="w")
        self._var_sz = tk.IntVar(value=512)
        tk.Scale(pf, from_=256, to=720, orient="horizontal",
                 variable=self._var_sz, resolution=32, length=200).grid(
            row=2, column=1, padx=5)

        # ── buttons ────────────────────────────────────
        bf = ttk.Frame(self)
        bf.pack(fill=tk.X, padx=10, pady=6)
        self._btn_go = ttk.Button(bf, text="开始迁移", command=self._start)
        self._btn_go.pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="取消",
                   command=self._on_close).pack(side=tk.RIGHT, padx=4)

        # ── progress ───────────────────────────────────
        self._progress = ttk.Progressbar(self, mode="determinate")
        self._progress.pack(fill=tk.X, padx=10, pady=2)

        self._stat = tk.StringVar(value="选择风格图后点击 [开始迁移]")
        ttk.Label(self, textvariable=self._stat).pack(
            anchor="w", padx=10, pady=2)

    # ── helpers ─────────────────────────────────────────

    def _find_styles(self):
        if not os.path.isdir(self._style_dir):
            return []
        exts = (".jpg", ".jpeg", ".png")
        return sorted(
            os.path.join(self._style_dir, f)
            for f in os.listdir(self._style_dir)
            if f.lower().endswith(exts))

    def _make_thumb(self, path):
        try:
            p = Image.open(path)
            p.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
            return ImageTk.PhotoImage(p)
        except Exception:
            return None

    def _select(self, path):
        self._style_path = path
        name = os.path.splitext(os.path.basename(path))[0]
        self._sel_var.set(f"已选: {name}")

    def _upload(self):
        path = filedialog.askopenfilename(
            parent=self, title="选择风格图",
            filetypes=[("图片", "*.jpg *.jpeg *.png"), ("所有", "*.*")])
        if path:
            self._select(path)

    # ── run ─────────────────────────────────────────────

    def _start(self):
        if self._running:
            return
        if not self._style_path:
            messagebox.showwarning("提示", "请先选择风格图", parent=self)
            return

        style_bgr = imread(self._style_path)
        if style_bgr is None:
            messagebox.showerror("错误", "无法读取风格图", parent=self)
            return

        self._running = True
        self._btn_go.configure(state="disabled")
        self._progress["value"] = 0

        weight = self._var_w.get() * 1e6
        iters = self._var_it.get()
        mx = self._var_sz.get()

        def _run():
            try:
                from style.neural_style import stylize, device_name
                self.after(0, lambda: self._stat.set(
                    f"设备: {device_name()} | 迭代 0/{iters}"))
                result = stylize(
                    self._content, style_bgr,
                    iterations=iters, style_weight=weight,
                    max_size=mx, progress=self._on_progress)
                self.after(0, lambda: self._on_complete(result))
            except Exception as e:
                self.after(0, lambda: self._on_error(str(e)))

        threading.Thread(target=_run, daemon=True).start()

    def _on_progress(self, step, total):
        pct = step / total * 100
        self.after(0, lambda: self._progress.configure(value=pct))
        if step % 20 == 0 or step == total:
            self.after(0, lambda s=step, t=total:
                       self._stat.set(f"迭代 {s}/{t}"))

    def _on_complete(self, result):
        self._running = False
        self._on_done(result)
        self.destroy()

    def _on_error(self, msg):
        self._running = False
        self._btn_go.configure(state="normal")
        self._stat.set(f"失败: {msg}")
        messagebox.showerror("风格迁移失败", msg, parent=self)

    def _on_close(self):
        if self._running:
            messagebox.showwarning("提示", "正在处理中，请等待完成",
                                   parent=self)
            return
        self.destroy()
