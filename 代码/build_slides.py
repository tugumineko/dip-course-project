"""
build_slides.py — 生成演示文稿 HTML（自写 CSS 暗色主题，零外部依赖）
运行: E:\miniconda3\envs\ai-service\python.exe 代码\build_slides.py
输出: ../演示文稿.html（单文件，浏览器直接打开）
"""
from __future__ import annotations

import base64
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
GALLERY = os.path.join(PROJ, "结果", "gallery")
OUT = os.path.join(PROJ, "演示文稿.html")
DEMO_VIDEO = os.path.join(PROJ, "素材", "演示视频", "demo.mp4")


def b64(path, mime="image/jpeg"):
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"


def img(name, folder=GALLERY):
    path = os.path.join(folder, name)
    if not os.path.exists(path):
        print(f"  [WARN] missing: {path}")
        return ""
    return b64(path)


def demo_video():
    if not os.path.exists(DEMO_VIDEO):
        print(f"  [WARN] missing: {DEMO_VIDEO}")
        return ""
    size_mb = os.path.getsize(DEMO_VIDEO) / 1024 / 1024
    print(f"  embedding video: {DEMO_VIDEO} ({size_mb:.1f} MB)")
    return b64(DEMO_VIDEO, "video/mp4")


video_src = demo_video()
metrics = json.load(open(os.path.join(GALLERY, "metrics.json"), encoding="utf-8"))

CSS = r"""
:root{--bg:#0a0e1a;--card:#111827;--accent:#d4a054;--blue:#5b8cff;--green:#80d98c;--red:#ff7b7b;--txt:#e2e8f0;--dim:#a8b4cf;--border:rgba(255,255,255,.08)}
*{box-sizing:border-box;margin:0;padding:0}html,body{height:100%;background:var(--bg);color:var(--txt);font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;overflow:hidden}
.slide{display:none;flex-direction:column;justify-content:center;align-items:center;height:100vh;padding:48px 88px;position:relative;overflow:hidden}.slide.active{display:flex}.left-align{align-items:flex-start;text-align:left}.center{text-align:center}.slide>*{width:100%;max-width:1060px}.center>*{margin-left:auto;margin-right:auto}
h1{font-size:45px;font-weight:700;line-height:1.25;letter-spacing:.4px}h2{font-size:31px;font-weight:700;line-height:1.35;margin-bottom:22px}h3{font-size:18px;font-weight:600;color:var(--accent);margin-bottom:8px}p,.item{font-size:17px;line-height:1.65}.sub{font-size:20px;color:var(--dim);margin-top:12px}.tag{display:inline-block;font-size:13px;padding:3px 12px;border-radius:999px;background:rgba(212,160,84,.15);color:var(--accent);margin-bottom:15px;font-weight:600}.accent{color:var(--accent)}.blue{color:var(--blue)}.green{color:var(--green)}b{font-weight:700}
.cols{display:flex;gap:34px;width:100%;align-items:flex-start}.col{flex:1;min-width:0}.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px 20px;margin-bottom:13px}.card p{font-size:15px;color:var(--dim);line-height:1.55}.mini{font-size:13px;color:var(--dim);line-height:1.45}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;width:100%}.grid.two{grid-template-columns:repeat(2,1fr)}.grid.four{grid-template-columns:repeat(4,1fr)}.cell{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px}.cell p{font-size:14px;color:var(--dim);line-height:1.5}.cell strong{color:var(--txt)}
.flow{display:flex;gap:0;align-items:stretch;width:100%;margin-top:8px}.flow .box{flex:1;padding:15px 12px;border:1px solid rgba(255,255,255,.1);text-align:center;background:rgba(255,255,255,.025)}.flow .box:first-child{border-radius:10px 0 0 10px}.flow .box:last-child{border-radius:0 10px 10px 0}.flow .box h3{font-size:14px;margin-bottom:5px}.flow .box p{font-size:13px;color:var(--dim);line-height:1.38}.flow .arrow{flex:0 0 27px;display:flex;align-items:center;justify-content:center;color:var(--dim);font-size:18px}
.img-row{display:flex;gap:16px;justify-content:center;width:100%;margin-top:8px}.img-item{flex:1;min-width:0;text-align:center}.img-item img{width:100%;height:auto;max-height:192px;object-fit:contain;border-radius:6px;display:block;margin:0 auto;box-shadow:0 4px 18px rgba(0,0,0,.35)}.img-item .cap{font-size:13px;color:var(--dim);margin-top:5px}.video-box{width:100%;aspect-ratio:16/9;border:1px solid var(--border);border-radius:12px;background:linear-gradient(135deg,rgba(212,160,84,.12),rgba(91,140,255,.08));display:flex;align-items:center;justify-content:center;text-align:center;box-shadow:0 4px 22px rgba(0,0,0,.35);overflow:hidden}.video-box video{width:100%;height:100%;object-fit:contain;background:#05070d}.video-placeholder{padding:28px}.video-placeholder h3{font-size:22px}.video-placeholder p{font-size:14px;color:var(--dim)}
table{border-collapse:collapse;width:100%;font-size:14px;margin-top:4px}th{text-align:left;padding:8px 11px;color:var(--dim);font-weight:600;border-bottom:2px solid rgba(255,255,255,.1);font-size:13px}td{padding:7px 11px;border-bottom:1px solid rgba(255,255,255,.04)}tr.hl td{background:rgba(212,160,84,.1);color:#fff;font-weight:600}
.nav{position:fixed;bottom:22px;right:30px;z-index:10;font-size:13px;color:var(--dim);display:flex;gap:14px;align-items:center}.nav button{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);color:var(--dim);padding:6px 14px;border-radius:6px;cursor:pointer}.nav button:hover{color:#fff;border-color:var(--accent)}.progress{position:fixed;top:0;left:0;height:3px;background:var(--accent);transition:width .3s;z-index:10}.footer{position:fixed;bottom:22px;left:30px;font-size:12px;color:rgba(255,255,255,.18)}
@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}.slide.active>*{animation:fadeUp .5s ease both}.slide.active>*:nth-child(2){animation-delay:.07s}.slide.active>*:nth-child(3){animation-delay:.14s}.slide.active>*:nth-child(4){animation-delay:.21s}.slide.active>*:nth-child(5){animation-delay:.28s}
"""

slides = []

slides.append("""
<section class="slide active center" id="s0">
  <span class="tag">数字图像处理 · 期末项目</span>
  <h1>家庭老照片修复与纪念化生成</h1>
  <p class="sub">定制修复模式 · 传统纪念模板 · VGG 高级艺术风格扩展</p>
  <p style="font-size:14px;color:var(--dim);margin-top:30px">华东师范大学 软件工程学院 · 2026</p>
</section>
""")

slides.append("""
<section class="slide left-align" id="s1">
  <span class="tag">项目需求</span>
  <h2>家庭老照片需要修复，也需要纪念化输出</h2>
  <div class="cols">
    <div class="col">
      <div class="card"><h3>修复质量问题</h3><p>家庭旧照常见发黄、褪色、灰蒙、扫描颗粒、轻微模糊、折痕划痕等问题，需要有针对性的修复流程。</p></div>
      <div class="card"><h3>保留旧照质感</h3><p>修复目标不是把照片变成现代手机照片，而是让它更清楚、更干净，同时保留年代感和家庭记忆。</p></div>
      <div class="card"><h3>生成纪念成果</h3><p>修复后的照片可进一步生成相册风、胶片风、明信片风、淡彩手绘等纪念版，用于保存和展示。</p></div>
    </div>
    <div class="col"><img src="%s" style="max-width:100%%;border-radius:8px;box-shadow:0 4px 24px rgba(0,0,0,.5)"></div>
  </div>
</section>
""" % img("custom_温和修复.jpg"))

slides.append("""
<section class="slide left-align" id="s2">
  <span class="tag">修复需求</span>
  <h2>每类照片问题对应一个定制修复模块</h2>
  <div class="grid">
    <div class="cell"><h3>普通家庭旧照</h3><p><strong>目标：</strong>自然改善，不过度处理<br><strong>模式：</strong>温和修复</p></div>
    <div class="cell"><h3>泛黄褪色</h3><p><strong>目标：</strong>去掉过量黄化，保留暖色<br><strong>模式：</strong>泛黄褪色修复</p></div>
    <div class="cell"><h3>黑白旧照</h3><p><strong>目标：</strong>增强灰度层次和轮廓<br><strong>模式：</strong>黑白旧照增强</p></div>
    <div class="cell"><h3>扫描颗粒</h3><p><strong>目标：</strong>减少颗粒，保护人像边缘<br><strong>模式：</strong>扫描颗粒修复</p></div>
    <div class="cell"><h3>人像不清</h3><p><strong>目标：</strong>增强中等边缘，抑制噪声放大<br><strong>模式：</strong>人像清晰化</p></div>
    <div class="cell"><h3>折痕划痕</h3><p><strong>目标：</strong>辅助检测细线破损并修补<br><strong>模式：</strong>折痕划痕辅助修复</p></div>
  </div>
</section>
""")

slides.append("""
<section class="slide left-align" id="s3">
  <span class="tag">系统结构</span>
  <h2>四个模块完成“修复、纪念、扩展、展示”</h2>
  <div class="grid">
    <div class="cell" style="border-color:var(--accent)"><h3>家庭老照片修复</h3><p>温和修复、泛黄褪色、黑白旧照、扫描颗粒、人像清晰化、折痕划痕辅助修复。</p></div>
    <div class="cell" style="border-color:var(--green)"><h3 class="green">纪念版生成</h3><p>复古相册、暖色胶片、纪念明信片、淡彩手绘，均为传统图像处理即时模板。</p></div>
    <div class="cell" style="border-color:var(--blue)"><h3 class="blue">高级算法功能</h3><p>增强、去噪、锐化、恢复、频域、小波、形态学和分割，用于调参、实验和课程展示。</p></div>
  </div>
  <div class="flow" style="margin-top:24px">
    <div class="box"><h3>导入照片</h3><p>家庭老照片</p></div><div class="arrow">→</div>
    <div class="box"><h3>选择模式</h3><p>按场景，不按算法</p></div><div class="arrow">→</div>
    <div class="box"><h3>定制修复</h3><p>固定流水线</p></div><div class="arrow">→</div>
    <div class="box"><h3>纪念输出</h3><p>模板 / VGG 扩展</p></div>
  </div>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s4">
  <span class="tag">定制算法 1</span>
  <h2>温和修复：保留旧照质感的默认方案</h2>
  <div class="img-row"><div class="img-item"><img src="{img('custom_温和修复.jpg')}"><p class="cap">轻度去噪 + 保守增强 + 温和锐化</p></div></div>
  <div class="flow" style="margin-top:18px">
    <div class="box"><h3>轻度 NLM</h3><p>减少颗粒，不抹平人物</p></div><div class="arrow">→</div>
    <div class="box"><h3>黄化校正</h3><p>保留少量暖色</p></div><div class="arrow">→</div>
    <div class="box"><h3>低强度 CLAHE</h3><p>提升局部层次</p></div><div class="arrow">→</div>
    <div class="box"><h3>亮度 USM</h3><p>只轻微恢复细节</p></div>
  </div>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s5">
  <span class="tag">定制算法 2</span>
  <h2>泛黄褪色修复：去黄，但不去掉记忆感</h2>
  <div class="img-row"><div class="img-item"><img src="{img('custom_泛黄褪色修复.jpg')}"><p class="cap">LAB 空间限幅校正黄化</p></div></div>
  <div class="card" style="margin-top:16px"><p>简单白平衡容易把老照片调得过冷。本模式在 LAB 空间估计 b 通道黄化偏移，只去掉过量黄化，并保留少量暖色；再对 L 通道做 CLAHE，轻微恢复饱和度。</p></div>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s6">
  <span class="tag">定制算法 3</span>
  <h2>黑白旧照增强：灰度层次与旧相纸质感</h2>
  <div class="img-row"><div class="img-item"><img src="{img('custom_黑白旧照增强.jpg')}"><p class="cap">灰度层次增强 + 轻微暖纸色</p></div></div>
  <div class="flow" style="margin-top:18px">
    <div class="box"><h3>灰度化</h3><p>聚焦明暗层次</p></div><div class="arrow">→</div>
    <div class="box"><h3>轻度去噪</h3><p>减少纸面颗粒</p></div><div class="arrow">→</div>
    <div class="box"><h3>S 曲线</h3><p>增强中间调</p></div><div class="arrow">→</div>
    <div class="box"><h3>暖纸色</h3><p>模拟旧相纸</p></div>
  </div>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s7">
  <span class="tag">定制算法 4</span>
  <h2>颗粒修复与人像清晰化：保护人物边缘</h2>
  <div class="img-row">
    <div class="img-item"><img src="{img('custom_扫描颗粒修复.jpg')}"><p class="cap">扫描颗粒修复</p></div>
    <div class="img-item"><img src="{img('custom_人像清晰化.jpg')}"><p class="cap">人像清晰化</p></div>
  </div>
  <div class="card" style="margin-top:15px"><p>颗粒修复在 YCrCb 空间中让色度通道强去噪、亮度通道弱去噪，并用 Canny 边缘权重保护轮廓；人像清晰化只增强中等边缘，暗部噪声由亮度 gate 抑制。</p></div>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s8">
  <span class="tag">定制算法 5</span>
  <h2>折痕划痕辅助修复：自动检测 + 用户掩膜</h2>
  <div class="img-row">
    <div class="img-item"><img src="{img('custom_折痕划痕辅助修复.jpg')}"><p class="cap">自动辅助修复</p></div>
    <div class="img-item"><img src="{img('custom_折痕划痕_自动加手动掩膜.jpg')}"><p class="cap">自动 + 手动掩膜</p></div>
  </div>
  <div class="card" style="margin-top:15px"><p>使用 top-hat / black-hat 形态学操作提取细亮线和细暗线，得到候选划痕掩膜；复杂破损可加载用户白色掩膜补充，最后用 inpaint 填补。</p></div>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s9">
  <span class="tag">纪念模板</span>
  <h2>主流程使用传统图像处理纪念风格</h2>
  <div class="img-row">
    <div class="img-item"><img src="{img('memory_复古相册风.jpg')}"><p class="cap">复古相册风</p></div>
    <div class="img-item"><img src="{img('memory_暖色胶片风.jpg')}"><p class="cap">暖色胶片风</p></div>
  </div>
  <div class="img-row">
    <div class="img-item"><img src="{img('memory_纪念明信片风.jpg')}"><p class="cap">纪念明信片风</p></div>
    <div class="img-item"><img src="{img('memory_淡彩手绘风.jpg')}"><p class="cap">淡彩手绘风</p></div>
  </div>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s10">
  <span class="tag">高级功能</span>
  <h2>VGG 自定义艺术风格迁移：高级个性化输出</h2>
  <div class="cols">
    <div class="col"><img src="{img('vgg_家庭暖调风格迁移.jpg')}" style="max-width:100%;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,.35)"><p class="mini" style="text-align:center;margin-top:6px">家庭暖调风格迁移结果</p></div>
    <div class="col">
      <div class="card"><h3>模块目的</h3><p>Gatys 方法体现 CNN 特征图和 Gram 矩阵，支持任意用户上传风格图，适合作为高级个性化输出。</p></div>
      <div class="card"><h3>工程特点</h3><p>使用预训练 VGG19，不训练网络；逐图优化输出像素，适合展示内容特征和风格特征的组合。</p></div>
      <div class="card"><h3>风格参考</h3><p>暖调家庭记忆风格图提供柔和、怀旧、偏家庭相册语境的艺术参考。</p></div>
    </div>
  </div>
</section>
""")

video_block = (
    f'<video src="{video_src}" controls preload="metadata" poster="{img("custom_温和修复.jpg")}"></video>'
    if video_src
    else '<div class="video-placeholder"><h3>录制后运行 build_slides.py 嵌入视频</h3><p>将视频保存为：素材/演示视频/demo.mp4；建议 70–90 秒，横屏 16:9。</p></div>'
)

slides.append(f"""
<section class="slide left-align" id="s11">
  <span class="tag">系统演示视频</span>
  <h2>录屏展示完整流程：修复 → 纪念 → 高级风格</h2>
  <div class="cols">
    <div class="col" style="flex:1.45">
      <div class="video-box">{video_block}</div>
    </div>
    <div class="col">
      <div class="card"><h3>1. 导入与修复</h3><p>打开老照片，依次展示温和修复、泛黄褪色、人像清晰化或扫描颗粒修复。</p></div>
      <div class="card"><h3>2. 纪念版输出</h3><p>在修复结果上生成纪念明信片风，再快速展示复古相册风或暖色胶片风。</p></div>
      <div class="card"><h3>3. 高级扩展与导出</h3><p>展示 VGG 自定义艺术风格面板和预生成结果，最后保存或导出前后对比图。</p></div>
    </div>
  </div>
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
  <h2>合成样张可量化，真实照片看主观自然度</h2>
  <div class="cols">
    <div class="col"><table><tr><th>方法</th><th>PSNR</th><th>SSIM</th></tr>{metrics_rows}</table></div>
    <div class="col" style="flex:0 0 390px"><img src="{img('metrics_chart.jpg')}" style="max-width:100%;border-radius:6px"><div class="card" style="margin-top:12px"><p>定制修复主动调整色彩、边缘和质感，不追求单一 PSNR 最大；中值版指标最高是因为合成噪声与中值滤波匹配。</p></div></div>
  </div>
</section>
""")

slides.append(f"""
<section class="slide left-align" id="s13">
  <span class="tag">真实案例</span>
  <h2>从真实照片出发，看修复与纪念输出</h2>
  <div class="img-row">
    <div class="img-item"><img src="{img('custom_温和修复.jpg')}"><p class="cap">温和修复：自然改善</p></div>
    <div class="img-item"><img src="{img('memory_纪念明信片风.jpg')}"><p class="cap">纪念明信片：适合展示</p></div>
    <div class="img-item"><img src="{img('vgg_家庭暖调风格迁移.jpg')}"><p class="cap">VGG 高级风格：自定义扩展</p></div>
  </div>
  <div class="card" style="margin-top:15px"><p>主流程是传统处理滤镜：快、稳、符合家庭照片语境；VGG 作为高级功能保留，让用户能上传自己的艺术风格。</p></div>
</section>
""")

slides.append("""
<section class="slide left-align" id="s14">
  <span class="tag">总结</span>
  <h2>完成家庭老照片修复与纪念化生成系统</h2>
  <div class="grid two">
    <div class="cell"><h3>修复可用</h3><p>六个定制修复模块分别处理泛黄、褪色、颗粒、人像不清、折痕划痕等问题。</p></div>
    <div class="cell"><h3>输出可展示</h3><p>四个纪念模板生成相册、胶片、明信片、淡彩手绘等家庭风格成果。</p></div>
    <div class="cell"><h3>风格可扩展</h3><p>VGG 自定义艺术风格迁移支持上传任意风格图，提供高级个性化输出。</p></div>
    <div class="cell"><h3>算法可解释</h3><p>高级算法功能支撑增强、去噪、锐化、恢复、频域、小波等方法展示。</p></div>
  </div>
  <p class="sub" style="text-align:center;margin-top:20px">谢谢老师和同学，欢迎提问。</p>
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
<title>家庭老照片修复与纪念化生成 · 期末项目</title>
<style>{CSS}</style>
</head>
<body>
<div class="progress" id="bar"></div>
{slides_html}
<div class="nav"><button onclick="go(-1)">← 上一页</button><span id="pn"></span><button onclick="go(1)">下一页 →</button></div>
<div class="footer">家庭老照片修复与纪念化生成 · 数字图像处理</div>
<script>{JS}</script>
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

size = os.path.getsize(OUT) / 1024 / 1024
print(f"OK: {OUT}")
print(f"Size: {size:.1f} MB, Slides: {len(slides)}")
