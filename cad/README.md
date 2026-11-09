# CAD：参数化模型与出图脚本

所有 3D 模型、工程图、专利附图都由 Python 脚本从同一个参数化模型生成。改参数后重新运行即可，各类图纸保持一致。

## 环境

```bash
pip install cadquery ezdxf matplotlib
# 中文字体（Ubuntu）：sudo apt-get install fonts-noto-cjk
# 渲染图使用 VTK 离屏渲染（随 cadquery 安装），需要图形环境或 Xvfb
```

## 运行

```bash
cd cad
python3 build.py          # 3D 导出 + 渲染 + 外观视图 + 发明附图 + 工程图（约 2 分钟）
python3 build.py --fast   # 低分辨率渲染
python3 schematics.py     # 原理示意图（对标原理图、附图 6、附图 7）
python3 build_benchmark.py --photos <官网照片目录>  # 对标款 Aarn PM40 逆向近似模型（不带 --photos 则跳过照片对比图）
python3 build_aarn_detail.py                      # 对标款细节模型（含内部结构、五金件、剖切、爆炸图、BOM）
```

## 文件

| 文件 | 内容 |
|---|---|
| `backpack_model.py` | 参数化几何模型。`Params` 中是主要尺寸：包体、背架、联动座、滚轮、织带、肩带、腰带 |
| `drawing.py` | 消隐线投影（OpenCascade HLR）、专利线条图、局部外观实线/虚线、VTK 渲染、尺寸标注工具 |
| `build.py` | 生成全部输出 |
| `schematics.py` | 2D 原理示意图 |
| `benchmark_aarn_pm40.py` | 对标款 Aarn PM40 的逆向近似模型（照片逐行测量，剪影 IoU 侧面 0.82 / 背面 0.92），仅供对标，见 docs/05 |
| `build_benchmark.py` | 生成对标模型的 STEP/STL、渲染、视图、照片对比图，输出到 `out/benchmark_aarn_pm40/` |
| `aarn_hardware.py` | 五金件库：插扣、梯扣、三档扣、胸带滑钩、弹簧绳扣、拉链、Lasso Loc、织带环、打枣 |
| `aarn_pm40_detail.py` | 对标款细节模型：63 种零件，空壳布料件、分层肩带腰带、内部件，每件标注"实测 / 照片可见 / 推断" |
| `build_aarn_detail.py` | 生成细节模型的总装 STEP、渲染、剖切图、爆炸图、五金图集和 BOM，输出到 `out/benchmark_aarn_pm40/detail/`（约 8 分钟） |

## 输出（`cad/out/`）

| 目录 | 内容 | 用途 |
|---|---|---|
| `step/` | 总装 STEP（带颜色）、联动座总成 STEP、各硬件 STEP | 给结构工程师在 SolidWorks / Creo / Fusion 360 中继续设计、开模 |
| `stl/` | 联动座前壳/后壳、滚轮、扳手、枢转板、背架 1:1；整包 1:4 缩比模型 | 3D 打印功能样件与展示模型（手办）。部分 STL 非严格封闭，切片软件可自动修复 |
| `render/` | 着色渲染图 | 内部评审、方案说明 |
| `design/01_backpack_whole/` | 整包六视图 + 立体图（PNG 300 dpi / PDF / SVG） | 外观设计专利 C |
| `design/02_backpack_partial_back_system/` | 局部外观：背负系统实线，其余虚线 | 外观设计专利 D |
| `design/03_linkage_hub/` | 联动座六视图 + 立体图 | 外观设计专利 E |
| `invention/fig1–fig5` | 带附图标记的说明书附图 | 发明 / 实用新型 A、B |
| `schematics/fig6, fig7` | 联动原理、锁止状态示意 | 发明 / 实用新型 A、B |
| `schematics/benchmark_*` | 对标款背部原理示意 | 调研报告 |
| `benchmark_aarn_pm40/` | 对标款近似模型：STEP、1:4 STL、渲染、七视图、照片与模型对比、与我们改版的对比 | 对标分析，不用于生产和专利申请 |
| `drawings/` | BP40-HUB-001 联动座 A3 工程图（PDF/PNG/SVG/DXF）、BP40-FRM-001 Y 型背架 A3 工程图 | 打样、开模询价 |

## 建模假设

- 软质部件（包体、肩带、腰带、网面）是简化曲面，只用于外观表达和缩比模型，不是裁片。打样还需要 2D 纸样。
- 硬质部件（联动座、滚轮、凸轮扳手、枢转板、背架）按制造意图建模，尺寸为 A0 概念值，需打样验证后修正。
