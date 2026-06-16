"""
build_slides.py — 生成演示文稿 HTML（自写 CSS 暗色主题，零外部依赖）
运行: E:\miniconda3\envs\ai-service\python.exe build_slides.py
输出: ../演示文稿.html（单文件，浏览器直接打开）
"""
import base64, json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
GALLERY = os.path.join(PROJ, "结果", "gallery")
STYLES = os.path.join(PROJ, "素材", "风格图")
OUT = os.path.join(PROJ, "演示文稿.html")


def b64(path):
    with open(path, "rb") as f:
        return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"


def img(name, folder=GALLERY):
    p = os.path.join(folder, name)
    if not os.path.exists(p):
        print(f"  [WARN] missing: {p}")
        return ""
    return b64(p)


metrics = json.load(open(os.path.join(GALLERY, "metrics.json"), encoding="utf-8"))

# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = r"""
:root{--bg:#0a0e1a;--card:#111827;--accent:#d4a054;--blue:#5b8cff;--green:#80d98c;
--txt:#e2e8f0;--dim:#a8b4cf;--border:rgba(255,255,255,.07)}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:var(--bg);color:var(--txt);
font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;overflow:hidden}

/* slides */
.slide{display:none;flex-direction:column;justify-content:center;align-items:center;
height:100vh;padding:50px 90px;position:relative;overflow:hidden}
.slide.active{display:flex}
.left-align{align-items:flex-start;text-align:left}
.center{text-align:center}

/* ensure children stretch full width in left-align */
.slide>*{width:100%;max-width:1060px}
.center>*{margin-left:auto;margin-right:auto}

/* nav */
.nav{position:fixed;bottom:22px;right:30px;z-index:10;font-size:13px;color:var(--dim);display:flex;gap:14px;align-items:center}
.nav button{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);
color:var(--dim);padding:6px 14px;border-radius:6px;cursor:pointer;font-size:13px}
.nav button:hover{color:#fff;border-color:var(--accent)}
.progress{position:fixed;top:0;left:0;height:3px;background:var(--accent);transition:width .3s;z-index:10}

/* typography — matched to reference */
h1{font-size:48px;font-weight:700;letter-spacing:.5px;line-height:1.3}
h2{font-size:32px;font-weight:700;margin-bottom:24px;line-height:1.35}
h3{font-size:20px;font-weight:600;color:var(--accent);margin-bottom:12px}
p,.item{font-size:18px;line-height:1.7;color:var(--txt)}
.sub{font-size:20px;color:var(--dim);margin-top:12px;font-weight:400}
.tag{display:inline-block;font-size:13px;padding:3px 12px;border-radius:999px;
background:rgba(212,160,84,.15);color:var(--accent);margin-bottom:16px;font-weight:600;letter-spacing:.5px}
.accent{color:var(--accent)}
.blue{color:var(--blue)}
b{font-weight:700}

/* layout */
.cols{display:flex;gap:40px;width:100%;align-items:flex-start}
.col{flex:1;min-width:0}

/* cards */
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 22px;margin-bottom:14px}
.card h3{margin-bottom:6px;font-size:18px}
.card p{font-size:15px;color:var(--dim);line-height:1.6}

/* table */
table{border-collapse:collapse;width:100%;font-size:15px;margin-top:6px}
th{text-align:left;padding:8px 12px;color:var(--dim);font-weight:600;border-bottom:2px solid rgba(255,255,255,.1);font-size:13px;letter-spacing:.3px}
td{padding:7px 12px;border-bottom:1px solid rgba(255,255,255,.04)}
tr:last-child td{border-bottom:none}
tr.hl td{background:rgba(212,160,84,.1);color:#fff;font-weight:600}

/* horizontal arch diagram */
.arch{display:flex;gap:0;align-items:stretch;width:100%;margin-top:8px}
.arch .box{flex:1;padding:18px 16px;border:1px solid rgba(255,255,255,.1);text-align:center}
.arch .box:first-child{border-radius:10px 0 0 10px}
.arch .box:last-child{border-radius:0 10px 10px 0}
.arch .box h3{font-size:14px;margin-bottom:6px}
.arch .box p{font-size:13px;color:var(--dim);line-height:1.4}
.arch .arrow{flex:0 0 30px;display:flex;align-items:center;justify-content:center;color:var(--dim);font-size:20px}

/* vertical arch (3-tier) — seamless borders */
.varch{display:flex;flex-direction:column;gap:0;width:100%;margin-top:8px}
.varch .vbox{padding:14px 22px;border:1px solid rgba(255,255,255,.1);border-top:none;text-align:center}
.varch .vbox:first-child{border-top:1px solid rgba(255,255,255,.1);border-radius:10px 10px 0 0}
.varch .vbox:last-child{border-radius:0 0 10px 10px}
.varch .vbox h3{font-size:14px;margin-bottom:4px}
.varch .vbox p{font-size:13px;color:var(--dim);line-height:1.4}
.varch .varrow{text-align:center;color:var(--accent);font-size:14px;padding:3px 0;
border-left:1px solid rgba(255,255,255,.1);border-right:1px solid rgba(255,255,255,.1)}

/* image grid — 3 per row, never overflow */
.img-row{display:flex;gap:16px;justify-content:center;width:100%;margin-top:8px}
.img-row .img-item{flex:1;min-width:0;text-align:center}
.img-row .img-item img{width:100%;height:auto;max-height:200px;object-fit:contain;border-radius:6px;display:block;margin:0 auto}
.img-row .img-item .cap{font-size:13px;color:var(--dim);margin-top:5px}

/* footer */
.footer{position:fixed;bottom:22px;left:30px;font-size:12px;color:rgba(255,255,255,.18)}

/* animations */
@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.slide.active>*{animation:fadeUp .5s ease both}
.slide.active>*:nth-child(2){animation-delay:.07s}
.slide.active>*:nth-child(3){animation-delay:.14s}
.slide.active>*:nth-child(4){animation-delay:.21s}
.slide.active>*:nth-child(5){animation-delay:.28s}
"""

# ── Slides ────────────────────────────────────────────────────────────────────

slides = []

# 1 — Title
slides.append(f"""
<section class="slide active center" id="s0">
  <span class="tag">数字图像处理 · 期末项目</span>
  <h1>老照片修复与增强馆</h1>
  <p class="sub">经典 DIP 算法系统 + Gatys 神经风格迁移</p>
  <p style="font-size:14px;color:var(--dim);margin-top:32px">华东师范大学 软件工程学院 · 2026</p>
</section>
""")

# 2 — Motivation
slides.append(f"""
<section class="slide left-align" id="s1">
  <span class="tag">出发点</span>
  <h2>为什么选老照片修复</h2>
  <div class="cols">
    <div class="col">
      <div class="card">
        <h3>贴近生活</h3>
        <p>几乎每个家庭都有发黄褪色的老照片，「修复老照片」是人人能共情的真实需求，也容易做出直观的前后对比效果。</p>
      </div>
      <div class="card">
        <h3>课程覆盖最全</h3>
        <p>一张老照片的「退化 → 恢复」串起了课程几乎全部核心知识点——去噪、增强、锐化、恢复、频域、形态学、小波。</p>
      </div>
      <div class="card">
        <h3>零训练约束友好</h3>
        <p>经典修复纯 OpenCV；风格迁移只借预训练 VGG19，不需数据集、不需训练时间。</p>
      </div>
    </div>
    <div class="col" style="flex:0 0 360px;display:flex;align-items:center;justify-content:center">
      <img src="{img('一键修复_真实.jpg')}" style="max-width:100%;border-radius:8px;box-shadow:0 4px 24px rgba(0,0,0,.5)">
    </div>
  </div>
</section>
""")

# 3 — System overview (CSS arch diagram)
slides.append(f"""
<section class="slide left-align" id="s2">
  <span class="tag">系统设计</span>
  <h2>三层架构</h2>
  <div class="varch" style="max-width:780px">
    <div class="vbox" style="background:rgba(212,160,84,.06)">
      <h3 style="color:var(--accent)">GUI 层 · tkinter</h3>
      <p>10 个折叠分组 · 40 项操作 · 动态参数区 · 原图 | 结果并排预览 · 撤销 / 重置 · 直方图 · 导出对比图</p>
    </div>
    <div class="varrow">▼ ndarray</div>
    <div class="vbox" style="background:rgba(91,140,255,.06)">
      <h3 style="color:var(--blue)">算法核心 · dip/</h3>
      <p>basic · enhance · smooth · sharpen · segment · morphology · restore · frequency · wavelet · pipeline + style/（Gatys 风格迁移）</p>
    </div>
    <div class="varrow">▼</div>
    <div class="vbox" style="background:rgba(128,217,140,.06)">
      <h3 style="color:var(--green)">底层依赖</h3>
      <p>OpenCV 4.13 · NumPy · SciPy · PyWavelets · PyTorch 2.5 + CUDA</p>
    </div>
  </div>
  <p style="margin-top:18px;font-size:15px;color:var(--dim)">GUI 与算法完全解耦：算法函数统一 ndarray → ndarray，可独立测试</p>
</section>
""")

# 4 — Enhancement (Ch4)
slides.append(f"""
<section class="slide left-align" id="s3">
  <span class="tag">对比度增强</span>
  <h2>老照片偏暗、低对比度、偏色</h2>
  <div class="img-row">
    <div class="img-item"><img src="{img('ch04_直方图均衡.jpg')}"><p class="cap">直方图均衡化</p></div>
    <div class="img-item"><img src="{img('ch04_CLAHE.jpg')}"><p class="cap">CLAHE 自适应均衡</p></div>
    <div class="img-item"><img src="{img('ch04_伽马变换.jpg')}"><p class="cap">Gamma 变换 (γ=0.6)</p></div>
  </div>
  <p style="margin-top:14px;font-size:16px">直方图均衡拉平灰度分布，CLAHE 避免全局过曝，Gamma 针对性提亮暗部。系统还有白平衡、对数变换、分段线性等共 7 种增强。</p>
</section>
""")

# 5 — Smoothing (Ch6)
slides.append(f"""
<section class="slide left-align" id="s4">
  <span class="tag">平滑去噪</span>
  <h2>噪声抑制与保边平衡</h2>
  <div class="img-row">
    <div class="img-item"><img src="{img('ch06_中值滤波.jpg')}"><p class="cap">中值滤波</p></div>
    <div class="img-item"><img src="{img('ch06_高斯滤波.jpg')}"><p class="cap">高斯滤波</p></div>
    <div class="img-item"><img src="{img('ch06_非局部均值.jpg')}"><p class="cap">非局部均值 NLM</p></div>
  </div>
  <div style="margin-top:14px;display:flex;gap:24px;width:100%">
    <div class="card" style="flex:0 0 240px;text-align:center;padding:12px 16px">
      <p style="font-size:14px;color:var(--dim)">中值滤波 PSNR</p>
      <p style="font-size:24px;font-weight:700;color:var(--accent)">17.38 → 22.74 dB</p>
      <p style="font-size:13px;color:var(--dim)">+5.36 dB</p>
    </div>
    <div class="card" style="flex:1;padding:12px 16px">
      <p style="font-size:15px">中值滤波是椒盐噪声克星；NLM 利用图像自相似性，保边效果更好但计算量大。去噪方法的选择取决于噪声类型。</p>
    </div>
  </div>
</section>
""")

# 6 — Sharpening + Segmentation (Ch7 + Ch5)
slides.append(f"""
<section class="slide left-align" id="s5">
  <span class="tag">锐化 / 分割</span>
  <h2>细节恢复与结构提取</h2>
  <div class="img-row">
    <div class="img-item"><img src="{img('ch07_USM锐化.jpg')}"><p class="cap">USM 非锐化掩蔽</p></div>
    <div class="img-item"><img src="{img('ch07_Sobel边缘.jpg')}"><p class="cap">Sobel 梯度</p></div>
    <div class="img-item"><img src="{img('ch05_Canny.jpg')}"><p class="cap">Canny 边缘检测</p></div>
  </div>
  <p style="margin-top:14px;font-size:16px">去噪后细节模糊 → USM 用「原图减去平滑版」提取细节层再加回来。Sobel / Canny 提取边缘结构，对应分割前处理。</p>
</section>
""")

# 7 — Morphology + Frequency (Ch8 + Ch3)
slides.append(f"""
<section class="slide left-align" id="s6">
  <span class="tag">形态学 / 频域</span>
  <h2>结构处理与频谱分析</h2>
  <div class="img-row">
    <div class="img-item"><img src="{img('ch08_开运算.jpg')}"><p class="cap">开运算（去小噪点）</p></div>
    <div class="img-item"><img src="{img('ch03_频谱.jpg')}"><p class="cap">傅里叶频谱</p></div>
    <div class="img-item"><img src="{img('ch03_低通.jpg')}"><p class="cap">巴特沃斯低通</p></div>
  </div>
  <p style="margin-top:14px;font-size:16px">形态学开运算 = 先腐蚀后膨胀，去除二值图小噪点。频域低通从另一角度做平滑——噪声在频谱上是高频分量。</p>
</section>
""")

# 8 — Restoration (Ch9) — highlight
slides.append(f"""
<section class="slide left-align" id="s7">
  <span class="tag">图像恢复</span>
  <h2>退化建模与最优恢复</h2>
  <div class="img-row">
    <div class="img-item"><img src="{img('ch09_退化模拟.jpg')}"><p class="cap">运动模糊退化模拟</p></div>
    <div class="img-item"><img src="{img('ch09_维纳滤波.jpg')}"><p class="cap">维纳滤波恢复</p></div>
    <div class="img-item"><img src="{img('ch09_划痕修复.jpg')}"><p class="cap">inpaint 划痕修复</p></div>
  </div>
  <div class="card" style="margin-top:14px;border-color:var(--accent)">
    <h3 style="color:var(--accent)">课程难点</h3>
    <p>退化模型 <b>g = f*h + n</b>。逆滤波直接除以 H(u,v)，在 H 接近零时噪声被严重放大。维纳滤波引入噪功比 K，在「还原细节」和「抑制噪声」之间做最优折中。inpaint 根据掩膜自动填补划痕。</p>
  </div>
</section>
""")

# 9 — Wavelet + Pipeline
slides.append(f"""
<section class="slide left-align" id="s8">
  <span class="tag">小波去噪 / 一键修复</span>
  <h2>多分辨率去噪与自动流水线</h2>
  <div class="img-row" style="max-width:700px">
    <div class="img-item"><img src="{img('ch10_小波去噪.jpg')}"><p class="cap">小波阈值去噪</p></div>
    <div class="img-item"><img src="{img('一键修复_合成.jpg')}"><p class="cap">一键修复效果</p></div>
  </div>
  <div class="arch" style="margin-top:16px;max-width:700px">
    <div class="box" style="background:rgba(91,140,255,.06)"><h3 style="color:var(--blue)">中值去噪</h3><p>去椒盐噪声</p></div>
    <div class="arrow">→</div>
    <div class="box" style="background:rgba(212,160,84,.06)"><h3 style="color:var(--accent)">CLAHE 增强</h3><p>自适应提亮</p></div>
    <div class="arrow">→</div>
    <div class="box" style="background:rgba(128,217,140,.06)"><h3 style="color:var(--green)">USM 锐化</h3><p>恢复细节</p></div>
  </div>
  <p style="margin-top:12px;font-size:15px;color:var(--dim)">一键修复 PSNR <b style="color:var(--accent)">16.15 → 18.06 dB</b> · SSIM <b style="color:var(--accent)">0.40 → 0.60</b></p>
</section>
""")

# 10 — Style transfer principle
slides.append(f"""
<section class="slide left-align" id="s9">
  <span class="tag">进阶功能</span>
  <h2>Gatys 神经风格迁移</h2>
  <div class="cols">
    <div class="col">
      <div class="card">
        <h3 style="color:var(--accent)">核心思想</h3>
        <p>用 ImageNet 预训练的 <b>VGG19</b> 当特征提取器，不训练它。内容由深层特征图表示，风格由各层 <b>Gram 矩阵</b>（通道间相关性）表示。</p>
      </div>
      <div class="card">
        <h3 style="color:var(--blue)">优化过程</h3>
        <p>从内容图出发，直接对<b>输出图像素</b>做 L-BFGS 梯度下降，最小化 L_content + L_style 加权和。200–300 步后收敛。</p>
      </div>
      <div class="card">
        <h3 style="color:var(--green)">工程约束</h3>
        <p>零训练 · 零数据集 · 任意内容 + 任意风格 · GPU 约 21 秒 / 512px · 处理尺寸 ≤ 720px 防 OOM</p>
      </div>
    </div>
    <div class="col" style="flex:0 0 300px">
      <div class="card" style="border-color:var(--accent);padding:16px;text-align:center">
        <p style="font-size:13px;color:var(--dim);margin-bottom:6px">风格迁移数据流</p>
        <div class="varch" style="margin:0">
          <div class="vbox" style="padding:7px 10px;background:rgba(212,160,84,.08)"><p style="font-size:13px">内容图 + 风格图</p></div>
          <div class="varrow">▼</div>
          <div class="vbox" style="padding:7px 10px;background:rgba(91,140,255,.08)"><p style="font-size:13px">VGG19 特征提取</p></div>
          <div class="varrow">▼</div>
          <div class="vbox" style="padding:7px 10px;background:rgba(91,140,255,.08)"><p style="font-size:13px">Gram 矩阵 + 内容特征</p></div>
          <div class="varrow">▼</div>
          <div class="vbox" style="padding:7px 10px;background:rgba(128,217,140,.08)"><p style="font-size:13px">L-BFGS 像素优化</p></div>
          <div class="varrow">▼</div>
          <div class="vbox" style="padding:7px 10px;background:rgba(212,160,84,.08)"><p style="font-size:13px">风格化输出</p></div>
        </div>
      </div>
    </div>
  </div>
</section>
""")

# 11 — Style transfer results
slides.append(f"""
<section class="slide center" id="s10">
  <span class="tag">风格迁移效果</span>
  <h2>修复后老照片 × 艺术风格</h2>
  <div style="text-align:center">
    <img src="{img('风格迁移_老照片星空.jpg')}" style="max-width:580px;width:100%;border-radius:8px;box-shadow:0 4px 24px rgba(0,0,0,.4)">
    <p style="font-size:14px;color:var(--dim);margin-top:8px">修复后老照片 × 梵高《星空》</p>
  </div>
  <div style="display:flex;gap:16px;justify-content:center;margin-top:16px">
    <div style="text-align:center">
      <img src="{img('starry_night.jpg', STYLES)}" style="height:80px;border-radius:4px">
      <p style="font-size:12px;color:var(--dim);margin-top:4px">星空</p>
    </div>
    <div style="text-align:center">
      <img src="{img('great_wave.jpg', STYLES)}" style="height:80px;border-radius:4px">
      <p style="font-size:12px;color:var(--dim);margin-top:4px">神奈川冲浪里</p>
    </div>
  </div>
  <p style="margin-top:14px;font-size:15px;color:var(--dim)">风格强度可调 · 预设 + 自定义上传 · 后台线程 + 进度条</p>
</section>
""")

# 12 — Metrics
metrics_rows = ""
for m in metrics:
    name = m["方法"]
    psnr = m["PSNR (dB)"]
    ssim = m["SSIM"]
    cls = ' class="hl"' if "一键修复 (中值)" in name else ""
    metrics_rows += f"<tr{cls}><td>{name}</td><td>{psnr:.2f}</td><td>{ssim:.4f}</td></tr>\n"

slides.append(f"""
<section class="slide left-align" id="s11">
  <span class="tag">量化评估</span>
  <h2>合成老照片 · 14 种方法对比</h2>
  <div class="cols" style="align-items:flex-start">
    <div class="col">
      <table>
        <tr><th>方法</th><th>PSNR (dB)</th><th>SSIM</th></tr>
        {metrics_rows}
      </table>
    </div>
    <div class="col" style="flex:0 0 380px;text-align:center;display:flex;flex-direction:column;justify-content:center">
      <img src="{img('metrics_chart.jpg')}" style="max-width:100%;border-radius:6px">
      <p style="font-size:13px;color:var(--dim);margin-top:8px">高亮行 = 综合最优方案</p>
    </div>
  </div>
</section>
""")

# 13 — Real photos
slides.append(f"""
<section class="slide center" id="s12">
  <span class="tag">真实效果</span>
  <h2>真实老照片修复</h2>
  <div class="img-row" style="max-width:860px;margin:0 auto">
    <div class="img-item"><img src="{img('一键修复_真实.jpg')}" style="box-shadow:0 4px 16px rgba(0,0,0,.4)"><p class="cap">真实老照片 #1</p></div>
    <div class="img-item"><img src="{img('一键修复_真实2.jpg')}" style="box-shadow:0 4px 16px rgba(0,0,0,.4)"><p class="cap">真实老照片 #2</p></div>
  </div>
  <p style="margin-top:16px;font-size:16px">同一套一键修复流水线，对发黄 / 低对比 / 有噪点的老照片均有明显改善</p>
</section>
""")

# 14 — Difficulties & takeaways
slides.append(f"""
<section class="slide left-align" id="s13">
  <span class="tag">回顾</span>
  <h2>难点与收获</h2>
  <div class="cols">
    <div class="col">
      <div class="card">
        <h3>难点</h3>
        <p>Windows 中文路径 OpenCV I/O 失败 → 自写 Unicode 安全读写<br><br>
        维纳滤波噪功比 K 调参——过大模糊、过小噪声放大<br><br>
        6 GB 显存下风格迁移分辨率控制<br><br>
        tkinter 后台线程 + 进度回调避免 GUI 阻塞</p>
      </div>
    </div>
    <div class="col">
      <div class="card" style="border-color:var(--accent)">
        <h3 style="color:var(--accent)">收获</h3>
        <p>从退化模型出发，把课程核心知识点串成完整的修复故事线<br><br>
        Gram 矩阵 = 特征通道相关性，深入理解 CNN 特征表达<br><br>
        完整经历 设计 → 实现 → 量化评估 → GUI 集成 → 演示 的全流程</p>
      </div>
    </div>
  </div>
</section>
""")

# 15 — Thank you
slides.append(f"""
<section class="slide center" id="s14">
  <span class="tag">结束</span>
  <h1 style="font-size:40px">谢谢</h1>
  <p class="sub">Q &amp; A</p>
</section>
""")

# ── Assemble HTML ─────────────────────────────────────────────────────────────

slides_html = "\n".join(slides)

JS = r"""
const slides=document.querySelectorAll('.slide'),bar=document.getElementById('bar'),pn=document.getElementById('pn');
let cur=0;
function show(i){slides.forEach(s=>s.classList.remove('active'));slides[i].classList.add('active');
bar.style.width=((i/(slides.length-1))*100)+'%';pn.textContent=(i+1)+' / '+slides.length;}
function go(d){const n=cur+d;if(n>=0&&n<slides.length){cur=n;show(cur);}}
document.addEventListener('keydown',e=>{
if(e.key==='ArrowRight'||e.key===' '||e.key==='Enter'){e.preventDefault();go(1);}
if(e.key==='ArrowLeft'){e.preventDefault();go(-1);}
if(e.key==='Home'){e.preventDefault();cur=0;show(0);}
if(e.key==='End'){e.preventDefault();cur=slides.length-1;show(cur);}
});
show(0);
"""

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>老照片修复与增强馆 · 期末项目</title>
<style>{CSS}</style>
</head>
<body>
<div class="progress" id="bar"></div>
{slides_html}
<div class="nav">
  <button onclick="go(-1)">← 上一页</button>
  <span id="pn"></span>
  <button onclick="go(1)">下一页 →</button>
</div>
<div class="footer">老照片修复与增强馆 · 数字图像处理</div>
<script>{JS}</script>
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

sz = os.path.getsize(OUT) / 1024 / 1024
print(f"OK: {OUT}")
print(f"Size: {sz:.1f} MB, Slides: {len(slides)}")
