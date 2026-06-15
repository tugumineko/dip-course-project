# 老照片修复与增强馆

华东师大《数字图像处理_2026》期末项目（目标难度 **系数 1.3**）。

**做什么**：导入褪色 / 起噪 / 有划痕 / 模糊的老照片，用经典数字图像处理算法逐步或一键修复增强，并可对修复结果做艺术风格迁移留念。

- **系数 1（地基）**：完整 DIP 系统 —— 基础操作、对比度增强、平滑去噪、锐化、分割/边缘、形态学、图像恢复、频域处理。
- **+0.3（进阶）**：图像风格迁移（Gatys 优化法 + 预训练 VGG19，**零训练**）。

## 运行

必须用 conda `ai-service` 环境（含 GPU 版 torch）：

```powershell
E:\miniconda3\envs\ai-service\python.exe 代码\main.py
```

工具脚本可单独跑：

```powershell
# 合成一张"老照片"
E:\miniconda3\envs\ai-service\python.exe 代码\utils\degrade.py 素材\干净原图\test.jpg 素材\合成老照片\test_old.jpg --mask 素材\合成老照片\test_mask.png
# 算指标
E:\miniconda3\envs\ai-service\python.exe 代码\utils\metrics.py 素材\干净原图\test.jpg 素材\合成老照片\test_old.jpg
```

## 结构与设计

完整设计、需求分析、风险与计划见 [设计.md](设计.md)。代码在 `代码/`，按课程章节组织（见 `代码/dip/__init__.py`）。

## 说明

- 真实老照片（`素材/真实老照片/`）涉及隐私，**不纳入版本库**（见 `.gitignore`）。
- 合成老照片与处理结果均可由脚本重新生成，故不纳入版本库。
