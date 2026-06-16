"""
build_slides.py — 生成演示文稿 HTML（reveal.js + base64 内嵌图片）
运行: E:\miniconda3\envs\ai-service\python.exe build_slides.py
输出: ../演示文稿.html（单文件，浏览器直接打开）
"""
import base64, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
GALLERY = os.path.join(PROJ, "结果", "gallery")
STYLES = os.path.join(PROJ, "素材", "风格图")
RESULTS = os.path.join(PROJ, "结果")
OUT = os.path.join(PROJ, "演示文稿.html")


def b64(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:image/jpeg;base64,{data}"


def img(name, folder=GALLERY):
    p = os.path.join(folder, name)
    if not os.path.exists(p):
        print(f"  [WARN] missing: {p}")
        return ""
    return b64(p)


metrics = json.load(open(os.path.join(GALLERY, "metrics.json"), encoding="utf-8"))

# -- slide content ----------------------------------------------------------

slides = []

# 1 — Title
slides.append(f"""
<section>
  <h1 style="font-size:2.2em;">老照片修复与增强馆</h1>
  <p style="font-size:1.1em; color:#ccc;">基于 OpenCV 的数字图像处理系统 + Gatys 神经风格迁移</p>
  <br>
  <p style="font-size:0.8em; color:#999;">华东师范大学 软件工程学院<br>
  《数字图像处理》期末项目<br>
  2026 年 6 月</p>
</section>
""")

# 2 — Motivation
slides.append(f"""
<section>
  <h2>选题动机</h2>
  <div style="display:flex; gap:40px; align-items:center; justify-content:center;">
    <div style="flex:1; text-align:left; font-size:0.85em;">
      <p>📷 <b>贴近生活</b>：每个家庭都有发黄褪色的老照片</p>
      <p>📚 <b>课程覆盖最全</b>：一张老照片的「退化→恢复」串起<br>
         第 2–10 章，几乎全部核心知识点</p>
      <p>🧠 <b>零训练</b>：经典修复纯 OpenCV，风格迁移只借<br>
         预训练 VGG19，不需数据集、不需训练</p>
      <p>🎯 <b>系数 1.3</b> = 完整 DIP 系统（地基）<br>
         + 图像风格迁移（进阶）</p>
    </div>
    <div style="flex:0 0 auto;">
      <img src="{img('一键修复_真实.jpg')}" style="max-height:360px; border-radius:8px; box-shadow:0 4px 20px rgba(0,0,0,0.5);">
    </div>
  </div>
</section>
""")

# 3 — System overview
slides.append(f"""
<section>
  <h2>系统总览</h2>
  <div style="font-size:0.75em; text-align:left; max-width:800px; margin:0 auto;">
    <pre style="background:#1a1a2e; padding:20px; border-radius:8px; color:#e0e0e0; font-size:0.95em; line-height:1.6;">
┌─────────────────────────────────────────────┐
│             GUI 层 (tkinter)                │
│  10 个功能分组 · 40 项 DIP 操作 · 动态参数    │
│  原图|结果并排 · 撤销/重置 · 导出对比图       │
└──────────────────┬──────────────────────────┘
                   │  ndarray 进出
┌──────────────────▼──────────────────────────┐
│           算法核心 (dip/ 按章节)              │
│  basic · enhance · smooth · sharpen ·        │
│  segment · morphology · restore · frequency  │
│  wavelet · pipeline（一键修复）               │
│  + style/（Gatys 风格迁移）                   │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  OpenCV · NumPy · SciPy · PyTorch (GPU)      │
└─────────────────────────────────────────────┘</pre>
  </div>
  <p style="font-size:0.75em; color:#aaa; margin-top:10px;">9 个算法模块覆盖第 2–10 章 · GUI 与算法解耦 · 风格迁移走后台线程</p>
</section>
""")

# 4 — Enhancement (Ch4)
slides.append(f"""
<section>
  <h2>第四章 · 对比度增强</h2>
  <div style="display:flex; gap:20px; justify-content:center; flex-wrap:wrap;">
    <div style="text-align:center;">
      <img src="{img('ch04_直方图均衡.jpg')}" style="max-height:260px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">直方图均衡化</p>
    </div>
    <div style="text-align:center;">
      <img src="{img('ch04_CLAHE.jpg')}" style="max-height:260px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">CLAHE 自适应均衡</p>
    </div>
    <div style="text-align:center;">
      <img src="{img('ch04_伽马变换.jpg')}" style="max-height:260px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">Gamma 变换 (γ=0.6)</p>
    </div>
  </div>
  <p style="font-size:0.7em; margin-top:8px;">老照片典型问题：<b>偏暗、对比度低、偏色</b> → 直方图均衡/CLAHE/白平衡 + Gamma 校正</p>
</section>
""")

# 5 — Smoothing & Denoising (Ch6)
slides.append(f"""
<section>
  <h2>第六章 · 平滑去噪</h2>
  <div style="display:flex; gap:20px; justify-content:center; flex-wrap:wrap;">
    <div style="text-align:center;">
      <img src="{img('ch06_中值滤波.jpg')}" style="max-height:260px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">中值滤波（椒盐噪声克星）</p>
    </div>
    <div style="text-align:center;">
      <img src="{img('ch06_高斯滤波.jpg')}" style="max-height:260px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">高斯滤波</p>
    </div>
    <div style="text-align:center;">
      <img src="{img('ch06_非局部均值.jpg')}" style="max-height:260px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">非局部均值 (NLM)</p>
    </div>
  </div>
  <p style="font-size:0.7em; margin-top:8px;">PSNR 提升：中值滤波 <b>17.38 → 22.74 dB</b>（+5.36 dB）· NLM 保边效果更好</p>
</section>
""")

# 6 — Sharpening (Ch7) + Segmentation (Ch5)
slides.append(f"""
<section>
  <h2>第七章 · 锐化 &amp; 第五章 · 分割</h2>
  <div style="display:flex; gap:20px; justify-content:center; flex-wrap:wrap;">
    <div style="text-align:center;">
      <img src="{img('ch07_USM锐化.jpg')}" style="max-height:240px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">USM 非锐化掩蔽</p>
    </div>
    <div style="text-align:center;">
      <img src="{img('ch07_Sobel边缘.jpg')}" style="max-height:240px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">Sobel 梯度边缘</p>
    </div>
    <div style="text-align:center;">
      <img src="{img('ch05_Canny.jpg')}" style="max-height:240px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">Canny 边缘检测</p>
    </div>
  </div>
  <p style="font-size:0.7em; margin-top:8px;">锐化：恢复老照片模糊细节 · 分割/边缘检测：提取图像结构信息</p>
</section>
""")

# 7 — Morphology (Ch8) + Frequency (Ch3)
slides.append(f"""
<section>
  <h2>第八章 · 形态学 &amp; 第三章 · 频域处理</h2>
  <div style="display:flex; gap:20px; justify-content:center; flex-wrap:wrap;">
    <div style="text-align:center;">
      <img src="{img('ch08_开运算.jpg')}" style="max-height:240px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">形态学开运算（去小噪点）</p>
    </div>
    <div style="text-align:center;">
      <img src="{img('ch03_频谱.jpg')}" style="max-height:240px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">傅里叶频谱</p>
    </div>
    <div style="text-align:center;">
      <img src="{img('ch03_低通.jpg')}" style="max-height:240px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">巴特沃斯低通滤波</p>
    </div>
  </div>
  <p style="font-size:0.7em; margin-top:8px;">形态学：二值化后的精细处理 · 频域：从频谱角度理解噪声与平滑</p>
</section>
""")

# 8 — Restoration (Ch9) — highlight
slides.append(f"""
<section>
  <h2>第九章 · 图像恢复 ⭐</h2>
  <div style="display:flex; gap:20px; justify-content:center; flex-wrap:wrap;">
    <div style="text-align:center;">
      <img src="{img('ch09_退化模拟.jpg')}" style="max-height:220px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">运动模糊退化模拟</p>
    </div>
    <div style="text-align:center;">
      <img src="{img('ch09_维纳滤波.jpg')}" style="max-height:220px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">维纳滤波恢复</p>
    </div>
    <div style="text-align:center;">
      <img src="{img('ch09_划痕修复.jpg')}" style="max-height:220px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">inpaint 划痕修复</p>
    </div>
  </div>
  <p style="font-size:0.7em; margin-top:8px;"><b>课程难点 &amp; 亮点</b>：退化模型 g = f*h + n → 逆滤波（噪声放大问题）→ 维纳滤波（最优折中）<br>
  + cv2.inpaint 修复划痕/瑕疵</p>
</section>
""")

# 9 — Wavelet (Ch10) + One-click restore
slides.append(f"""
<section>
  <h2>第十章 · 小波去噪 &amp; 一键修复流水线</h2>
  <div style="display:flex; gap:30px; justify-content:center; flex-wrap:wrap;">
    <div style="text-align:center;">
      <img src="{img('ch10_小波去噪.jpg')}" style="max-height:250px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">小波去噪（pywt）</p>
    </div>
    <div style="text-align:center;">
      <img src="{img('一键修复_合成.jpg')}" style="max-height:250px; border-radius:6px;">
      <p style="font-size:0.65em; color:#aaa;">一键修复效果（合成老照片）</p>
    </div>
  </div>
  <p style="font-size:0.7em; margin-top:8px;">一键修复 = 中值去噪(Ch6) → CLAHE 增强(Ch4) → USM 锐化(Ch7)<br>
  PSNR <b>16.15 → 18.06 dB</b> · SSIM <b>0.40 → 0.60</b></p>
</section>
""")

# 10 — Style transfer principle
slides.append(f"""
<section>
  <h2>进阶功能 · Gatys 神经风格迁移</h2>
  <div style="font-size:0.78em; text-align:left; max-width:820px; margin:0 auto;">
    <p><b>核心思想</b>（A Neural Algorithm of Artistic Style, 2015）：</p>
    <ol style="line-height:1.8;">
      <li>用 <b>预训练 VGG19</b>（ImageNet 权重）作为特征提取器——<b>不训练它</b></li>
      <li><b>内容</b>由深层特征图（conv4_2）表示</li>
      <li><b>风格</b>由各层 <b>Gram 矩阵</b>（通道间相关性）表示</li>
      <li>从内容图出发，<b>直接对输出图像素做梯度下降</b><br>
        &nbsp;&nbsp;&nbsp;最小化：<code>L = α·L_content + β·L_style</code></li>
      <li>200–300 步 L-BFGS 迭代 → 保留内容结构 + 风格笔触色彩</li>
    </ol>
    <p style="color:#67d5b5; margin-top:10px;">✅ 零训练 · 零数据集 · 任意内容图 + 任意风格图 · GPU ~21s/512px</p>
  </div>
</section>
""")

# 11 — Style transfer results
slides.append(f"""
<section>
  <h2>风格迁移效果</h2>
  <div style="display:flex; gap:20px; justify-content:center; align-items:flex-end; flex-wrap:wrap;">
    <div style="text-align:center;">
      <img src="{img('风格迁移_老照片星空.jpg')}" style="max-height:340px; border-radius:6px; box-shadow:0 4px 20px rgba(0,0,0,0.4);">
      <p style="font-size:0.65em; color:#aaa;">修复后老照片 × 梵高《星空》</p>
    </div>
  </div>
  <div style="display:flex; gap:15px; justify-content:center; margin-top:15px;">
    <div style="text-align:center;">
      <img src="{img('starry_night.jpg', STYLES)}" style="max-height:100px; border-radius:4px;">
      <p style="font-size:0.55em; color:#888;">风格图</p>
    </div>
    <div style="text-align:center;">
      <img src="{img('great_wave.jpg', STYLES)}" style="max-height:100px; border-radius:4px;">
      <p style="font-size:0.55em; color:#888;">浮世绘风格</p>
    </div>
  </div>
  <p style="font-size:0.7em; margin-top:8px;">风格强度可调（1e6 含蓄 ~ 5e6 浓烈）· 支持上传自定义风格图</p>
</section>
""")

# 12 — Metrics
metrics_rows = ""
for m in metrics:
    name = m["方法"]
    psnr = m["PSNR (dB)"]
    ssim = m["SSIM"]
    hl = ' style="background:#2a4a3a; font-weight:bold;"' if "一键修复 (中值)" in name else ""
    metrics_rows += f"<tr{hl}><td>{name}</td><td>{psnr:.2f}</td><td>{ssim:.4f}</td></tr>\n"

slides.append(f"""
<section>
  <h2>量化评估 · PSNR / SSIM</h2>
  <div style="display:flex; gap:30px; justify-content:center; align-items:flex-start; flex-wrap:wrap;">
    <div>
      <table style="font-size:0.6em; border-collapse:collapse; min-width:380px;">
        <thead><tr style="background:#333;"><th style="padding:6px 12px;">方法</th><th style="padding:6px 12px;">PSNR (dB)</th><th style="padding:6px 12px;">SSIM</th></tr></thead>
        <tbody>{metrics_rows}</tbody>
      </table>
    </div>
    <div style="text-align:center;">
      <img src="{img('metrics_chart.jpg')}" style="max-height:300px; border-radius:6px;">
    </div>
  </div>
  <p style="font-size:0.65em; color:#aaa; margin-top:8px;">合成老照片（已知原图），14 种方法对比 · 高亮行 = 最佳一键修复方案</p>
</section>
""")

# 13 — Real photos
slides.append(f"""
<section>
  <h2>真实老照片修复效果</h2>
  <div style="display:flex; gap:20px; justify-content:center; flex-wrap:wrap;">
    <div style="text-align:center;">
      <img src="{img('一键修复_真实.jpg')}" style="max-height:280px; border-radius:6px; box-shadow:0 4px 16px rgba(0,0,0,0.4);">
      <p style="font-size:0.65em; color:#aaa;">真实老照片 #1</p>
    </div>
    <div style="text-align:center;">
      <img src="{img('一键修复_真实2.jpg')}" style="max-height:280px; border-radius:6px; box-shadow:0 4px 16px rgba(0,0,0,0.4);">
      <p style="font-size:0.65em; color:#aaa;">真实老照片 #2</p>
    </div>
  </div>
  <p style="font-size:0.7em; margin-top:10px;">同一套一键修复流水线 · 对发黄/低对比/有噪点的老照片均有明显改善</p>
</section>
""")

# 14 — Difficulties & takeaways
slides.append(f"""
<section>
  <h2>难点与收获</h2>
  <div style="font-size:0.8em; text-align:left; max-width:780px; margin:0 auto; line-height:1.9;">
    <p>🔧 <b>难点</b></p>
    <ul>
      <li>Windows 中文路径下 OpenCV imread/imwrite 失败 → 自写 Unicode 安全 I/O</li>
      <li>维纳滤波的噪功比参数 K 需按噪声水平调整，过大模糊、过小噪声放大</li>
      <li>风格迁移 GPU 显存管理：RTX 4050 (6GB) 限制处理分辨率 ≤ 720px</li>
      <li>tkinter 后台线程 + 进度回调：避免 GUI 阻塞的生产者-消费者模式</li>
    </ul>
    <p style="margin-top:12px;">💡 <b>收获</b></p>
    <ul>
      <li>从「退化模型」出发理解图像恢复，把第 2–10 章串成完整故事线</li>
      <li>Gatys 风格迁移：Gram 矩阵 = 特征相关性，深刻理解 CNN 特征层</li>
      <li>完整经历「设计 → 实现 → 量化评估 → GUI 集成 → 演示」的工程全流程</li>
    </ul>
  </div>
</section>
""")

# 15 — Thank you / Q&A
slides.append(f"""
<section>
  <h1 style="font-size:2em;">谢谢！</h1>
  <p style="font-size:1.1em; color:#ccc; margin-top:20px;">Q &amp; A</p>
  <br>
  <div style="font-size:0.75em; color:#888; line-height:1.8;">
    <p>项目地址：github.com/tugumineko/dip-course-project</p>
    <p>运行环境：conda activate ai-service &amp;&amp; python main.py</p>
    <p>覆盖章节：第 2–11 章 · 40 项操作 · 难度系数 1.3</p>
  </div>
</section>
""")

# -- assemble HTML ----------------------------------------------------------

slides_html = "\n".join(slides)

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>老照片修复与增强馆 — 期末项目演示</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/black.css">
<style>
  .reveal {{ font-family: "Microsoft YaHei", "PingFang SC", sans-serif; }}
  .reveal h1, .reveal h2 {{ font-family: "Microsoft YaHei", "PingFang SC", sans-serif; text-transform: none; }}
  .reveal h2 {{ font-size: 1.5em; }}
  .reveal table {{ margin: 0 auto; }}
  .reveal table th, .reveal table td {{ padding: 4px 10px; border: 1px solid #555; text-align: center; font-size: 0.65em; }}
  .reveal pre {{ box-shadow: none; }}
  .reveal img {{ border: none; box-shadow: none; }}
  .reveal ul {{ text-align: left; }}
  .reveal ol {{ text-align: left; }}
  .reveal code {{ background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 3px; }}
</style>
</head>
<body>
<div class="reveal">
<div class="slides">
{slides_html}
</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
<script>
Reveal.initialize({{
  hash: true,
  slideNumber: true,
  transition: 'slide',
  width: 1200,
  height: 700,
  margin: 0.04,
  center: true,
}});
</script>
<!-- 无网络兜底: 若 CDN 加载失败, 用纯 CSS 翻页 -->
<script>
window.addEventListener('load', function() {{
  if (typeof Reveal === 'undefined' || !Reveal.isReady || !Reveal.isReady()) {{
    document.querySelector('.reveal').style.cssText = 'overflow-y:auto;height:100vh;';
    document.querySelectorAll('section').forEach(function(s) {{
      s.style.cssText = 'min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:40px;border-bottom:2px solid #333;';
    }});
  }}
}});
</script>
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

sz = os.path.getsize(OUT) / 1024 / 1024
print(f"OK: {OUT}")
print(f"Size: {sz:.1f} MB, Slides: {len(slides)}")
