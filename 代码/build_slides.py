"""
build_slides.py — 生成演示文稿 HTML（自写 CSS 暗色主题，零外部依赖）
运行: E:\miniconda3\envs\ai-service\python.exe build_slides.py
输出: ../演示文稿.html（单文件，浏览器直接打开）
"""
import base64
import json
import os

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

CSS = r"""
:root{--bg:#0a0e1a;--card:#111827;--card2:#0f172a;--accent:#d4a054;--blue:#5b8cff;--green:#80d98c;--red:#ff7b7b;--txt:#e2e8f0;--dim:#a8b4cf;--border:rgba(255,255,255,.08)}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:var(--bg);color:var(--txt);font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;overflow:hidden}
.slide{display:none;flex-direction:column;justify-content:center;align-items:center;height:100vh;padding:48px 88px;position:relative;overflow:hidden}
.slide.active{display:flex}.left-align{align-items:flex-start;text-align:left}.center{text-align:center}.slide>*{width:100%;max-width:1060px}.center>*{margin-left:auto;margin-right:auto}
.nav{position:fixed;bottom:22px;right:30px;z-index:10;font-size:13px;color:var(--dim);display:flex;gap:14px;align-items:center}.nav button{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);color:var(--dim);padding:6px 14px;border-radius:6px;cursor:pointer;font-size:13px}.nav button:hover{color:#fff;border-color:var(--accent)}.progress{position:fixed;top:0;left:0;height:3px;background:var(--accent);transition:width .3s;z-index:10}
h1{font-size:46px;font-weight:700;letter-spacing:.5px;line-height:1.25}h2{font-size:31px;font-weight:700;margin-bottom:22px;line-height:1.35}h3{font-size:19px;font-weight:600;color:var(--accent);margin-bottom:10px}p,.item{font-size:17px;line-height:1.65;color:var(--txt)}.sub{font-size:20px;color:var(--dim);margin-top:12px;font-weight:400}.tag{display:inline-block;font-size:13px;padding:3px 12px;border-radius:999px;background:rgba(212,160,84,.15);color:var(--accent);margin-bottom:15px;font-weight:600;letter-spacing:.5px}.accent{color:var(--accent)}.blue{color:var(--blue)}.green{color:var(--green)}b{font-weight:700}
.cols{display:flex;gap:36px;width:100%;align-items:flex-start}.col{flex:1;min-width:0}.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:17px 21px;margin-bottom:13px}.card h3{margin-bottom:6px;font-size:18px}.card p{font-size:15px;color:var(--dim);line-height:1.55}.mini{font-size:13px;color:var(--dim);line-height:1.45}
table{border-collapse:collapse;width:100%;font-size:14px;margin-top:4px}th{text-align:left;padding:8px 11px;color:var(--dim);font-weight:600;border-bottom:2px solid rgba(255,255,255,.1);font-size:13px}td{padding:7px 11px;border-bottom:1px solid rgba(255,255,255,.04)}tr:last-child td{border-bottom:none}tr.hl td{background:rgba(212,160,84,.1);color:#fff;font-weight:600}
.flow{display:flex;gap:0;align-items:stretch;width:100%;margin-top:8px}.flow .box{flex:1;padding:16px 13px;border:1px solid rgba(255,255,255,.1);text-align:center;background:rgba(255,255,255,.025)}.flow .box:first-child{border-radius:10px 0 0 10px}.flow .box:last-child{border-radius:0 10px 10px 0}.flow .box h3{font-size:14px;margin-bottom:6px}.flow .box p{font-size:13px;color:var(--dim);line-height:1.4}.flow .arrow{flex:0 0 28px;display:flex;align-items:center;justify-content:center;color:var(--dim);font-size:18px}
.varch{display:flex;flex-direction:column;gap:0;width:100%;margin-top:8px}.varch .vbox{padding:13px 20px;border:1px solid rgba(255,255,255,.1);border-top:none;text-align:center}.varch .vbox:first-child{border-top:1px solid rgba(255,255,255,.1);border-radius:10px 10px 0 0}.varch .vbox:last-child{border-radius:0 0 10px 10px}.varch .vbox h3{font-size:14px;margin-bottom:4px}.varch .vbox p{font-size:13px;color:var(--dim);line-height:1.4}.varch .varrow{text-align:center;color:var(--accent);font-size:14px;padding:3px 0;border-left:1px solid rgba(255,255,255,.1);border-right:1px solid rgba(255,255,255,.1)}
.problem-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;width:100%}.problem{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:15px}.problem h3{font-size:17px;margin-bottom:7px}.problem p{font-size:14px;color:var(--dim);line-height:1.5}.problem strong{color:var(--txt)}
.img-row{display:flex;gap:16px;justify-content:center;width:100%;margin-top:8px}.img-row .img-item{flex:1;min-width:0;text-align:center}.img-row .img-item img{width:100%;height:auto;max-height:195px;object-fit:contain;border-radius:6px;display:block;margin:0 auto;box-shadow:0 4px 18px rgba(0,0,0,.35)}.img-row .img-item .cap{font-size:13px;color:var(--dim);margin-top:5px}.footer{position:fixed;bottom:22px;left:30px;font-size:12px;color:rgba(255,255,255,.18)}
@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}.slide.active>*{animation:fadeUp .5s ease both}.slide.active>*:nth-child(2){animation-delay:.07s}.slide.active>*:nth-child(3){animation-delay:.14s}.slide.active>*:nth-child(4){animation-delay:.21s}.slide.active>*:nth-child(5){animation-delay:.28s}
"""

slides = []

slides.append(f"""
<section class="slide active center" id="s0">
  <span class="tag">数字图像处理 · 期末项目</span>
  <h1>老照片修复与风格化迁移纪念</h1>
  <p class="sub">从家庭老照片修复，到艺术纪念版生成</p>
  <p style="font-size:14px;color:var(--dim);margin-top:30px">华东师范大学 软件工程学院 · 2026</p>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s1">
  <span class="tag">应用动机</span>
  <h2>为什么是老照片修复</h2>
  <div class="cols">
    <div class="col">
      <div class="card"><h3>真实需求</h3><p>家庭老照片常见发黄、灰蒙、噪点、折痕和划痕，修复前后差异直观，容易形成可演示的完整应用。</p></div>
      <div class="card"><h3>处理链完整</h3><p>一张照片通常需要去噪、去偏色、增强、锐化、局部修补等多步组合，不是单一滤镜即可完成。</p></div>
      <div class="card"><h3>纪念价值</h3><p>修复版保留真实记忆；艺术版可做相册封面、纪念海报或礼物卡片，让风格迁移自然服务于主题。</p></div>
    </div>
    <div class="col" style="flex:0 0 360px;display:flex;align-items:center;justify-content:center">
      <img src="{img('一键修复_真实.jpg')}" style="max-width:100%;border-radius:8px;box-shadow:0 4px 24px rgba(0,0,0,.5)">
    </div>
  </div>
</section>
""")

slides.append("""
<section class="slide left-align" id="s2">
  <span class="tag">用户流程</span>
  <h2>从导入照片到纪念版输出</h2>
  <div class="flow">
    <div class="box" style="background:rgba(91,140,255,.06)"><h3 class="blue">导入</h3><p>打开家庭老照片</p></div>
    <div class="arrow">→</div>
    <div class="box" style="background:rgba(212,160,84,.06)"><h3>诊断</h3><p>偏色 / 噪声 / 模糊 / 划痕</p></div>
    <div class="arrow">→</div>
    <div class="box" style="background:rgba(128,217,140,.06)"><h3 class="green">修复</h3><p>一键修复 + 针对性精修</p></div>
    <div class="arrow">→</div>
    <div class="box" style="background:rgba(212,160,84,.06)"><h3>纪念版</h3><p>艺术风格迁移</p></div>
    <div class="arrow">→</div>
    <div class="box" style="background:rgba(255,255,255,.04)"><h3>导出</h3><p>保存结果 / 对比图</p></div>
  </div>
  <div class="card" style="margin-top:26px;border-color:var(--accent)">
    <h3>设计重点</h3>
    <p>普通用户按“照片问题”操作；高级用户进入算法工具箱继续调参。功能不是孤立罗列，而是围绕一次真实修复任务组织。</p>
  </div>
</section>
""")

slides.append("""
<section class="slide left-align" id="s3">
  <span class="tag">问题地图</span>
  <h2>老照片退化问题 → 处理策略</h2>
  <div class="problem-grid">
    <div class="problem"><h3>发黄偏色</h3><p><strong>现象：</strong>整体偏黄、肤色不自然<br><strong>处理：</strong>白平衡</p></div>
    <div class="problem"><h3>低对比 / 灰蒙</h3><p><strong>现象：</strong>层次弱、轮廓不突出<br><strong>处理：</strong>CLAHE / Gamma</p></div>
    <div class="problem"><h3>颗粒噪声</h3><p><strong>现象：</strong>扫描颗粒、椒盐点<br><strong>处理：</strong>中值 / NLM / 双边</p></div>
    <div class="problem"><h3>轻微模糊</h3><p><strong>现象：</strong>边缘和人脸细节弱<br><strong>处理：</strong>USM / 维纳滤波</p></div>
    <div class="problem"><h3>划痕折痕</h3><p><strong>现象：</strong>白线、裂痕、破损<br><strong>处理：</strong>掩膜 + inpaint</p></div>
    <div class="problem"><h3>纪念化需求</h3><p><strong>现象：</strong>想做封面或海报<br><strong>处理：</strong>Gatys 风格迁移</p></div>
  </div>
</section>
""")

slides.append("""
<section class="slide left-align" id="s4">
  <span class="tag">系统总览</span>
  <h2>普通修复入口 + 高级算法工具箱</h2>
  <div class="cols">
    <div class="col">
      <div class="card" style="border-color:var(--accent)"><h3>普通修复入口</h3><p>一键温和修复、去黄偏色、提亮增强、去颗粒噪声、增强清晰度、划痕/折痕修复、艺术纪念版生成。</p></div>
      <div class="card"><h3>高级算法工具箱</h3><p>增强、去噪、锐化、分割、形态学、恢复、频域、小波等完整功能保留，用于课堂展示和精修调参。</p></div>
    </div>
    <div class="col">
      <div class="varch">
        <div class="vbox" style="background:rgba(212,160,84,.06)"><h3>GUI 层 · tkinter</h3><p>修复向导 · 并排预览 · 动态参数 · 撤销 / 重置 · 导出</p></div>
        <div class="varrow">▼ ndarray</div>
        <div class="vbox" style="background:rgba(91,140,255,.06)"><h3 class="blue">算法核心 · dip/ + style/</h3><p>一键修复流水线 · 经典图像处理 · Gatys 风格迁移</p></div>
        <div class="varrow">▼</div>
        <div class="vbox" style="background:rgba(128,217,140,.06)"><h3 class="green">底层依赖</h3><p>OpenCV · NumPy · SciPy · PyWavelets · PyTorch</p></div>
      </div>
    </div>
  </div>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s5">
  <span class="tag">一键修复</span>
  <h2>稳定、自然、不过度处理的默认流水线</h2>
  <div class="img-row" style="max-width:720px">
    <div class="img-item"><img src="{img('一键修复_合成.jpg')}"><p class="cap">合成老照片一键修复</p></div>
    <div class="img-item"><img src="{img('一键修复_真实.jpg')}"><p class="cap">真实老照片一键修复</p></div>
  </div>
  <div class="flow" style="margin-top:18px">
    <div class="box" style="background:rgba(91,140,255,.06)"><h3 class="blue">去噪</h3><p>先减少颗粒，避免后续放大噪点</p></div>
    <div class="arrow">→</div>
    <div class="box" style="background:rgba(212,160,84,.06)"><h3>去偏色</h3><p>白平衡缓解发黄、偏棕</p></div>
    <div class="arrow">→</div>
    <div class="box" style="background:rgba(212,160,84,.06)"><h3>增强</h3><p>CLAHE 提升局部层次</p></div>
    <div class="arrow">→</div>
    <div class="box" style="background:rgba(128,217,140,.06)"><h3 class="green">锐化</h3><p>USM 轻微恢复细节</p></div>
  </div>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s6">
  <span class="tag">去黄与提亮</span>
  <h2>从“发黄灰蒙”到“色彩更自然”</h2>
  <div class="img-row">
    <div class="img-item"><img src="{img('ch04_直方图均衡.jpg')}"><p class="cap">直方图均衡</p></div>
    <div class="img-item"><img src="{img('ch04_CLAHE.jpg')}"><p class="cap">CLAHE 自适应增强</p></div>
    <div class="img-item"><img src="{img('ch04_伽马变换.jpg')}"><p class="cap">Gamma 提亮暗部</p></div>
  </div>
  <div class="card" style="margin-top:15px">
    <p>白平衡校正通道偏移；CLAHE 分块增强局部对比并限制过曝；Gamma 针对暗部提亮。它们共同解决老照片常见的发黄、偏暗和灰蒙问题。</p>
  </div>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s7">
  <span class="tag">去颗粒噪声</span>
  <h2>噪声抑制与细节保留的平衡</h2>
  <div class="img-row">
    <div class="img-item"><img src="{img('ch06_中值滤波.jpg')}"><p class="cap">中值滤波：去孤立噪点</p></div>
    <div class="img-item"><img src="{img('ch06_高斯滤波.jpg')}"><p class="cap">高斯滤波：平滑噪声</p></div>
    <div class="img-item"><img src="{img('ch06_非局部均值.jpg')}"><p class="cap">NLM：自相似去噪</p></div>
  </div>
  <div style="margin-top:14px;display:flex;gap:22px;width:100%">
    <div class="card" style="flex:0 0 245px;text-align:center;padding:12px 16px"><p class="mini">中值滤波 PSNR</p><p style="font-size:24px;font-weight:700;color:var(--accent)">17.38 → 22.74 dB</p><p class="mini">+5.36 dB</p></div>
    <div class="card" style="flex:1;padding:12px 16px"><p>中值适合椒盐点；双边和 NLM 更注重保边与自然度。实际修复中不只看指标，也要避免把老照片质感完全抹平。</p></div>
  </div>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s8">
  <span class="tag">划痕与模糊修复</span>
  <h2>局部破损修补 + 退化模型恢复</h2>
  <div class="img-row">
    <div class="img-item"><img src="{img('ch09_划痕修复.jpg')}"><p class="cap">inpaint 划痕修复</p></div>
    <div class="img-item"><img src="{img('ch09_退化模拟.jpg')}"><p class="cap">运动模糊退化模拟</p></div>
    <div class="img-item"><img src="{img('ch09_维纳滤波.jpg')}"><p class="cap">维纳滤波恢复</p></div>
  </div>
  <div class="card" style="margin-top:14px;border-color:var(--accent)">
    <p>划痕修复：白色掩膜标出待修补区域，inpaint 用周围像素自动填补。模糊恢复：退化模型 <b>g = f*h + n</b>，维纳滤波用噪功比 K 在恢复细节与抑制噪声之间折中。</p>
  </div>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s9">
  <span class="tag">高级工具箱</span>
  <h2>保留完整算法能力，用于展示与精修</h2>
  <div class="img-row">
    <div class="img-item"><img src="{img('ch05_Canny.jpg')}"><p class="cap">边缘检测</p></div>
    <div class="img-item"><img src="{img('ch08_开运算.jpg')}"><p class="cap">形态学开运算</p></div>
    <div class="img-item"><img src="{img('ch03_频谱.jpg')}"><p class="cap">傅里叶频谱</p></div>
  </div>
  <div class="card" style="margin-top:14px">
    <p>这些功能不是普通用户的第一入口，但能支持课堂展示：从空间域、频域、多分辨率和结构处理等角度观察同一张照片的变化。</p>
  </div>
</section>
""")

slides.append("""
<section class="slide left-align" id="s10">
  <span class="tag">艺术纪念版</span>
  <h2>Gatys 风格迁移：修复后的再创作</h2>
  <div class="cols">
    <div class="col">
      <div class="card"><h3>内容表示</h3><p>用预训练 VGG19 的深层特征保留人物、姿态和画面布局。</p></div>
      <div class="card"><h3>风格表示</h3><p>用多层特征的 Gram 矩阵表示笔触、纹理和色彩相关性。</p></div>
      <div class="card"><h3>像素优化</h3><p>从内容图出发，用 L-BFGS 优化输出图像素，最小化内容损失与风格损失。</p></div>
    </div>
    <div class="col" style="flex:0 0 320px">
      <div class="varch">
        <div class="vbox" style="background:rgba(212,160,84,.08)"><p>修复照片 + 风格图</p></div>
        <div class="varrow">▼</div>
        <div class="vbox" style="background:rgba(91,140,255,.08)"><p>VGG19 特征提取</p></div>
        <div class="varrow">▼</div>
        <div class="vbox" style="background:rgba(91,140,255,.08)"><p>内容特征 + Gram 矩阵</p></div>
        <div class="varrow">▼</div>
        <div class="vbox" style="background:rgba(128,217,140,.08)"><p>L-BFGS 像素优化</p></div>
        <div class="varrow">▼</div>
        <div class="vbox" style="background:rgba(212,160,84,.08)"><p>艺术纪念版</p></div>
      </div>
    </div>
  </div>
</section>
""")

slides.append(f"""
<section class="slide center" id="s11">
  <span class="tag">纪念版效果</span>
  <h2>修复版保留真实，艺术版用于纪念</h2>
  <img src="{img('风格迁移_老照片星空.jpg')}" style="max-width:600px;width:100%;border-radius:8px;box-shadow:0 4px 24px rgba(0,0,0,.4)">
  <p style="font-size:14px;color:var(--dim);margin-top:8px">修复后老照片 × 梵高《星空》</p>
  <div style="display:flex;gap:16px;justify-content:center;margin-top:15px">
    <div><img src="{img('starry_night.jpg', STYLES)}" style="height:78px;border-radius:4px"><p class="mini">星空</p></div>
    <div><img src="{img('great_wave.jpg', STYLES)}" style="height:78px;border-radius:4px"><p class="mini">神奈川冲浪里</p></div>
  </div>
  <p style="margin-top:12px;font-size:15px;color:var(--dim)">风格强度可调 · 支持自定义风格图 · 后台线程 + 进度条</p>
</section>
""")

metrics_rows = ""
for m in metrics:
    name = m["方法"]
    psnr = m["PSNR (dB)"]
    ssim = m["SSIM"]
    cls = ' class="hl"' if "一键修复 (中值)" in name else ""
    metrics_rows += f"<tr{cls}><td>{name}</td><td>{psnr:.2f}</td><td>{ssim:.4f}</td></tr>\n"

slides.append(f"""
<section class="slide left-align" id="s12">
  <span class="tag">量化评估</span>
  <h2>合成老照片：PSNR / SSIM 对比</h2>
  <div class="cols" style="align-items:flex-start">
    <div class="col">
      <table><tr><th>方法</th><th>PSNR (dB)</th><th>SSIM</th></tr>{metrics_rows}</table>
    </div>
    <div class="col" style="flex:0 0 382px;text-align:center;display:flex;flex-direction:column;justify-content:center">
      <img src="{img('metrics_chart.jpg')}" style="max-width:100%;border-radius:6px">
      <div class="card" style="margin-top:12px;text-align:left"><p>PSNR 衡量像素接近程度；增强和白平衡会重映射像素，指标未必最高，但主观对比度和色彩可能更好。</p></div>
    </div>
  </div>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s13">
  <span class="tag">真实案例</span>
  <h2>真实老照片：问题诊断与改善</h2>
  <div class="img-row" style="max-width:870px">
    <div class="img-item"><img src="{img('一键修复_真实.jpg')}"><p class="cap">案例 #1：偏色、低对比、颗粒改善</p></div>
    <div class="img-item"><img src="{img('一键修复_真实2.jpg')}"><p class="cap">案例 #2：整体提亮、轮廓更清楚</p></div>
  </div>
  <div class="problem-grid" style="grid-template-columns:repeat(4,1fr);margin-top:16px">
    <div class="problem"><h3>偏色</h3><p>发黄减轻，色彩更中性</p></div>
    <div class="problem"><h3>对比度</h3><p>灰蒙感降低，人物更突出</p></div>
    <div class="problem"><h3>噪声</h3><p>背景颗粒减少，保留质感</p></div>
    <div class="problem"><h3>自然度</h3><p>默认强度温和，避免过修</p></div>
  </div>
</section>
""")

slides.append("""
<section class="slide left-align" id="s14">
  <span class="tag">总结</span>
  <h2>围绕“修复 + 纪念”的完整应用</h2>
  <div class="cols">
    <div class="col">
      <div class="card"><h3>应用完整</h3><p>从导入、问题诊断、一键修复、针对性精修，到艺术纪念版和结果导出，形成完整用户流程。</p></div>
      <div class="card"><h3>算法扎实</h3><p>经典图像处理功能完整保留，既能支撑修复任务，也能用于课堂演示和参数实验。</p></div>
    </div>
    <div class="col">
      <div class="card" style="border-color:var(--accent)"><h3>纪念化输出</h3><p>Gatys 风格迁移让修复后的老照片从“保存真实”进一步扩展到“艺术再创作”。</p></div>
      <div class="card"><h3>Q & A</h3><p>谢谢老师和同学，欢迎提问。</p></div>
    </div>
  </div>
</section>
""")

slides_html = "\n".join(slides)

JS = r"""
const slides=document.querySelectorAll('.slide'),bar=document.getElementById('bar'),pn=document.getElementById('pn');
let cur=0;
function show(i){slides.forEach(s=>s.classList.remove('active'));slides[i].classList.add('active');bar.style.width=((i/(slides.length-1))*100)+'%';pn.textContent=(i+1)+' / '+slides.length;}
function go(d){const n=cur+d;if(n>=0&&n<slides.length){cur=n;show(cur);}}
document.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key===' '||e.key==='Enter'){e.preventDefault();go(1);}if(e.key==='ArrowLeft'){e.preventDefault();go(-1);}if(e.key==='Home'){e.preventDefault();cur=0;show(0);}if(e.key==='End'){e.preventDefault();cur=slides.length-1;show(cur);}});
show(0);
"""

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>老照片修复与风格化迁移纪念 · 期末项目</title>
<style>{CSS}</style>
</head>
<body>
<div class="progress" id="bar"></div>
{slides_html}
<div class="nav"><button onclick="go(-1)">← 上一页</button><span id="pn"></span><button onclick="go(1)">下一页 →</button></div>
<div class="footer">老照片修复与风格化迁移纪念 · 数字图像处理</div>
<script>{JS}</script>
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

sz = os.path.getsize(OUT) / 1024 / 1024
print(f"OK: {OUT}")
print(f"Size: {sz:.1f} MB, Slides: {len(slides)}")
