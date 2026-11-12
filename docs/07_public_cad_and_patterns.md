# 07 公开可得的背包 CAD、纸样、五金图纸与标准资料

> 这份调研回答：能不能找到 Mystery Ranch、Osprey、Deuter、Gregory、凯乐石等品牌的公开 CAD 文件，在它们的基础上改。结论是不能，原因和可行的替代做法见第 0 节和第 7 节。
> 我们自己的量产资料见 [08 A1 量产资料包](08_production_package_A1.md)。

- 调研日期：2026-11-12（桌面检索，仅核对网页是否存在并记录信息，未下载大文件）
- 目标：为自研并量产约 40 L 户外徒步背包的团队，查清知名品牌（Mystery Ranch、Osprey、Deuter、Gregory、Kailas 凯乐石、Arc'teryx、Black Diamond、Aarn 等）是否有**公开可得**的 CAD 文件或缝纫纸样，以及有哪些合法可用的替代起点。
- 核实等级标注：
  - **[已核实]**：本次直接打开过该页面/PDF 并读到了所引内容。
  - **[检索摘要]**：只在搜索结果摘录中看到，原页面直接抓取失败（403/404/504）或未单独打开。
  - **[未核实]**：未找到可靠来源，或只有单一非权威来源；请勿当作事实使用。
- 本报告不是法律意见。涉及许可、专利、商标的部分，量产前应请知识产权律师确认。

---

## 0. 一页结论

1. **没有任何一个所列品牌公开过真正的生产用 CAD、DXF 纸样或 tech pack。** 官方公开的只有使用说明书、调节/试背指南、保修与零配件申请页面。品牌的纸样和 tech pack 保存在内部 PLM/CAD 系统里（Mystery Ranch 公开说过其 tech pack 全部在内部完成）。
2. **社区 3D 模型全部是爱好者自建或照片扫描的外观网格**，不是品牌文件。**外观网格（OBJ/FBX/GLB/STL、摄影测量扫描）不能用于软包制造**：里面没有二维裁片、缝份、刀口对位、纱向、内部结构（背板、铝条、泡棉分层）和物料信息，也无法可靠地"展开"成可量产的裁片。
3. **五金件是唯一能拿到接近工程级公开数据的部分**：YKK、ITW Nexus、Nifco、Woojin、Fidlock、AustriAlpin 都公开了带尺寸的目录或数据表；但**公开 STEP 下载基本不存在**，3D 数据要通过销售代表索取（YKK 明确提供的是 OBJ/STL/FBX 网格，且有保密使用条件）。
4. **真正带二维裁片的 30–50 L 背包纸样确实存在，但几乎都只许个人使用**（Prickly Gorse、LearnMYOG、Ray-Way 明文禁止商用；Stitchback 明文表示可以另谈量产授权）。唯一查到明确允许商用的是 Open+Pattern 的瑞士 M70/M79 军用背包（CC BY 4.0，含 DXF-AAMA），但它不是现代徒步包。
5. **中国标准方面**：QB/T 1333-2018《背提包》是可引用的产品标准，但其振荡冲击负重对 >20 L 双肩包只有 6 kg，远低于 40 L 徒步包的真实工况，企业必须自定更严的内控指标。GB 18401-2010 的附录 A 把"箱包、背提包"列为**不属于该标准范围**的产品。

---

## 1. 品牌官方 CAD / 纸样 / 技术文件

### 1.1 结论：没有官方生产文件

对所列全部品牌，**没有找到**任何官方发布的生产 CAD、DXF/PLT 纸样、tech pack、带爆炸图的维修手册或开源计划。也没有找到可核实的"泄露 tech pack"（即使存在，也属于商业秘密，不能使用，见第 7 节）。

| 品牌 | 官方公开的东西 | 性质 | 状态 |
| --- | --- | --- | --- |
| Osprey | 使用说明书合集页 [Owner's Manuals](https://www.osprey.com/owners-manual)，例如 [Talon/Tempest 说明书 PDF](https://www.osprey.com/gb/media/user_manuals/OM_TalonTempest_S23_ENG.pdf)；[零配件申请 FAQ](https://knowledge-base.osprey.com/en_us/replacement-parts-faq-s-rkldmwag1e.md)；[All Mighty Guarantee](https://www.osprey.com/customer-support/all-mighty-guarantee) | 功能/调节说明；插扣、拉片、胸带等可自行更换的零件凭照片申请。无尺寸图、无爆炸图 | [已核实] |
| Deuter | [Repair Service](https://pimcore.deuter.com/deuter-master/en/responsibility/repair-service) | 维修服务说明，原文称"There are no repair kits for backpacks"；仅有更换绳扣/插扣的 DIY 视频 | [已核实] |
| Mystery Ranch | [Centric PLM 新闻稿](https://www.snewsnet.com/press-release/new-adventure-for-mystery-ranch-and-centric-software) | 原文："Our tech packs and product documentation are extensive because everything is put together and finalized in-house…"，说明 tech pack 只在内部 PLM 中 | [已核实] |
| Gregory | [Locks & Spare Parts FAQ](https://eu.gregorypacks.com/uk-en/customer-service/faq/locks-spare-parts/)、[Warranty](https://eu.gregorypacks.com/uk-en/warranty.html) | 通过 Support & Go 门户按产品代码订购零件；有更换胸带的说明文档。无图纸 | [检索摘要] |
| Black Diamond | [Spare Parts for Backpacks & Bags](https://blackdiamondequipment.com/collections/spare-parts-for-backpacks-bags)、[Repair Services](https://blackdiamondequipment.com/pages/repair-services) | 出售零件（如 Beta Light 45 Hipbelt、Beta Light 45 Metal Stay、25 mm 腰带插扣）；无尺寸图 | [检索摘要] |
| Aarn | [Fitting instructions](https://www.aarnpacks.com/pages/instructions) | 带编号示意图的试背/调节说明，网页形式，不是结构图纸 | [检索摘要] |
| Arc'teryx | 未找到官方背包零件页或维修手册 | — | [未核实] |
| Kailas 凯乐石 | 未找到任何官方图纸或纸样；公开的技术披露只有专利文本（例如"平衡收紧系统和背心式背包"实用新型，见 [技术网页转载](https://www.xjishu.com/zhuanli/07/202020343865.html)） | 专利附图是原理示意，不是生产图 | [检索摘要] |

说明：专利说明书附图（各品牌都有）是公开的，但它们是权利要求的示意图，没有生产尺寸，而且恰恰标出了**不能照做**的受保护结构。

### 1.2 最接近"厂商公开纸样"的三个例外（都不是所列品牌）

| 项目 | 内容 | 格式 / 价格 | 许可 | 状态 |
| --- | --- | --- | --- | --- |
| Whiskey Two Four "Backpack 00" | 约 12 L 战术小背包（9"W × 17"T × 5"D），2022 年 8 月曾以"Open Source CAD Pattern"名义发布（[Soldier Systems 报道](https://soldiersystems.net/2022/08/23/whiskey-two-four-releases-backpack-00-open-source-cad-pattern/)）。原免费链接已 404；现为 [WTFiles Backpack 00 2023 CAD Developer's Pattern](https://www.wtfidea.com/wtfiles-backpack-00-2023-cad-developer-s-pattern/)，同系列还有 [Backpack 36 等](https://wtfidea.com/patterns-wtfiles/) | 矢量 PDF，20 美元；页面写明"No support is offered… This purchase is for a CAD PDF only" | 许可条款页面上没有写，**[未核实]** | 页面 [已核实] |
| Gossamer Gear G4（Glen Van Peski） | 无框超轻包，约 4400 立方英寸（约 70 L）。Gossamer Gear 称自己已不再提供纸样，可向 Quest Outfitters 获取（[官方博客](https://www.gossamergear.com/blogs/our-blog/tip-of-the-week-make-your-own-g4)）；旧版说明曾见于 backpacking.net（`backpacking.net/makegear/gvp-pack/G4_print.htm`，搜索索引中有全文，但本次直接访问返回 404） | PDF 说明 + 尺寸图 | 第三方博客转述"Note this pattern is for personal use only"（[Sewn By Tanya](https://sewnbytanya.com/blog/gvp-pack/)）；原始许可文本 **[未核实]** | [检索摘要] |
| Open+Pattern 瑞士 M70/M79 军用背包 | 由实物老军包数字化；单一尺码，容积未标明 | CLO3D (ZPRJ)、DXF (AAMA)、PDF、GLB、PNG；自愿付费（建议 5 欧元） | 页面原文："Free under CC BY 4.0. Use it, change it, sell what you make. Just credit Open+Pattern." | [已核实] [产品页](https://openpattern.io/product/swiss-m70-m79-backpack/) |

### 1.3 一个容易被忽略的真正"公开生产规范"：美军规格书

- [MIL-F-43832C《FIELD PACK, COMBAT, NYLON, LARGE, LC-1》（ALICE 大号背包，1986）](https://everyspec.com/MIL-SPECS/MIL-SPECS-MIL-F/MIL-F-43832C_43423/) 在 EverySpec 上可免费下载（1.07 MB）。**[已核实]**
- 它是一份真实的量产采购规范，写明了面料（MIL-C-7219 尼龙帆布）、线、织带、泡棉、线迹、打枣、检验缺陷分类等（具体数值见第 5 节）。
- 规范引用了 U.S. Army Natick 的全尺寸纸样图纸 2-2-336 至 2-2-343、2-2-357，并写明"Standard patterns … are shown full scale on drawings and provide allowances for all seams"。**但这些图纸本身并不在规格书 PDF 里**，规范写的是向合同主管机构索取；图纸能否公开下载 **[未核实]**。
- 中号包对应 MIL-F-43833（[CIE Hub 说明](https://ciehub.info/equipment/loadbearing/ALICE/FieldPackCombatNylonMedium.html)）。**[检索摘要]**
- 用途：它不是现代徒步包，但可作为"tech pack 里的工艺条款应该怎么写"的权威范本。

---

## 2. 社区 3D 模型

### 2.1 必须先说清楚的一点

**外观网格不能用于制造软包。** 网上的背包模型绝大多数是为渲染、游戏或展示建的多边形网格，或是手机/相机摄影测量扫描。即使是 GrabCAD 上的 SOLIDWORKS/STEP 文件，也只是把背包外形当作刚体画出来的曲面/实体，不包含二维裁片、缝份、对位刀口、纱向、分层结构和物料。它们最多能用来做外观提案、渲染图或估算外形体积。

### 2.2 代表性条目（均为用户自建，**没有一个是品牌官方文件**）

| # | 标题 | 作者 | 平台 / 链接 | 格式 | 类型 | 许可 | 真伪 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Backpack - Lost Paradise Project | Krista Casal | [GrabCAD](https://grabcad.com/library/backpack-lost-paradise-project-1) | SOLIDWORKS 2012 + STEP/IGES；8,428 次下载（2013） | 工程 CAD 格式，但只是外形实体 | GrabCAD Cross License（非商业、内部使用） | 爱好者自建 |
| 2 | A Backpack | Aashish Kumar | [GrabCAD](https://grabcad.com/library/a-backpack-1) | SOLIDWORKS 2015；5,417 次下载（2017） | 同上 | 同上 | 爱好者自建 |
| 3 | Backpack（"Generic backpack"） | Andrew Hunter | [GrabCAD](https://grabcad.com/library/backpack-1) | SOLIDWORKS 2010；3,677 次下载 | 同上 | 同上 | 爱好者自建 |
| 4 | expandable backpack | Alejandro Rodriguez | [GrabCAD](https://grabcad.com/library/expandable-backpack-1) | STEP/IGES；576 次下载（2022） | 同上 | 同上 | 爱好者自建 |
| 5 | Backpack Frame SJ01（"Aluminium Backpack Frame"） | Mai T. Sự | [GrabCAD](https://grabcad.com/library/backpack-frame-sj01-1) | STEP/IGES；22 次下载（2019） | 工程 CAD（外架，可参考管架画法） | 同上 | 爱好者自建 |
| 6 | Arcteryx Alpha FL 45 Red Backpack | MarcoWorkspace | [Sketchfab](https://sketchfab.com/3d-models/arcteryx-alpha-fl-45-red-backpack-063ec59a6944445cb477b90b94a55742) | 可下载网格，约 60 万面（2026-04-10 上传） | 外观网格 | CC BY | 粉丝上传，非官方；品牌名涉及商标 |
| 7 | Hiking Backpack | menhankam | [Sketchfab](https://sketchfab.com/3d-models/hiking-backpack-ffd0bd8f61034f17a90e41fe8f2da003) | 网格，约 20 万面 | 外观网格 | CC BY-SA | 通用款 |
| 8 | Green Backpack 3D Scan | arkify | [Sketchfab](https://sketchfab.com/3d-models/green-backpack-3d-scan-f217d4ea8a4547b7b6bd5791250c55c7) | 扫描网格，约 13.8 万面 | 摄影测量扫描 | CC BY-NC（禁止商用） | 实物扫描 |
| 9 | Rucksack DEUTER RawScan Showcase | Frank_Zwick | [Sketchfab](https://sketchfab.com/3d-models/rucksack-deuter-rawscan-showcase-acd0cdd2e4d34904a1b7da4fabdc27f9) | 扫描网格，约 6 万面，**不可下载** | 摄影测量扫描 | 仅在线查看 | 实物扫描，非官方 |
| 10 | OSPREY TALON BACKPACK | Devesh-Lahoti | [CGTrader](https://www.cgtrader.com/3d-models/various/various-models/osprey-talon-backpack) | BLEND/OBJ/FBX/GLTF，约 8.1 万面，10 美元 | 外观网格 | Royalty Free | 卖家自称"based on the manufacturers original dimensions and technical data"，**无法核实，按粉丝作品对待** |
| 11 | Gregory Paragon 48 Hiking Backpack Blue | 3dmi | [CGTrader](https://www.cgtrader.com/3d-models/character/clothing/gregory-paragon-48-hiking-backpack-blue) | MAX/OBJ/FBX/BLEND/C4D/MA，37,268 面，69 美元；标称 42.23 × 56.19 × 70.75 cm | 外观网格 | Royalty Free | 粉丝作品 |
| 12 | MYSTERY RANCH 3 DAY ASSAULT PACK TRI ZIP | 3DMAStudios | [CGTrader](https://www.cgtrader.com/3d-models/military/military-character/mystery-ranch-3-day-assault-pack-tri-zip) | FBX/OBJ/Blend，63.94 美元 | 游戏资产（"inspired by"） | Custom License | 粉丝作品 |

其他平台（均 [已核实] 或 [检索摘要]，都只找到通用外观网格）：
- CGTrader 还有 [OSPREY RENN](https://www.cgtrader.com/3d-models/various/various-models/osprey-renn-hiking-bag)、[DEUTER HIKING BACKPACK](https://www.cgtrader.com/3d-models/various/various-models/deuter-hiking-backpack)。
- TurboSquid：只见通用款，如 [3D Sport Backpack 2](https://www.turbosquid.com/FullPreview/1936256)。
- Free3D：[Backpack Long Distance v1](https://free3d.com/3d-model/backpack-long-distance-v1--871794.html)，OBJ/STL，Personal Use License。
- Grab3D：[Hiking Backpack](https://grab3d.com/models/props/hiking-backpack/)，CC0，GLB/FBX/OBJ，14,848 三角面。
- 沐风网：[户外徒步背包设计三维模型](https://m.mfcad.com/tuzhi/show_1312920.html)，STEP（SolidWorks 2016，10.98 MB）；标题是徒步包，描述实际是帆布斜挎包。
- Printables：用户自建的 Osprey/Deuter 替换插扣，如 [Osprey buckle（20 mm 织带）](https://www.printables.com/model/768886-osprey-buckle)、[Osprey buckle/clip male replacement](https://www.printables.com/model/770437-osprey-buckleclip-male-replacement)、[tag:deuter](https://www.printables.com/search/models?q=tag%3Adeuter)。
- GrabCAD 上搜索"deuter"无结果，"osprey"只有 V-22 飞机，"ITW nexus""duraflex"无结果。
- 3D ContentCentral、TraceParts、Cults3D、Thingiverse：未发现背包或品牌插扣的厂商目录，**未做穷尽检索 [未核实]**。

### 2.3 GrabCAD 上的五金件模型（同样是爱好者测绘，尺寸不具权威性）

- [Quick Release Buckle 19mm](https://grabcad.com/library/quick-release-buckle-19mm)（Taikonaught，SW2011/STEP/STL，20,111 次下载）
- [.75" Ladder Lock with webbing prethreaded](https://grabcad.com/library/75-ladder-lock-with-webbing-prethreaded-1)、[.75" Slide Lock Buckle/Tri-glide](https://grabcad.com/library/75-slide-lock-buckle-tri-glide-1)（NorCalNomad）
- [1in SIDE RELEASE BUCKLE](https://grabcad.com/library/1in-side-release-buckle-1)（Lauritz Berg）
- [WJ(woojin) side release buckle 25mm](https://grabcad.com/library/wj-woojin-side-release-buckle-25mm-1)（Keiichi Demae，STL）
- [YKK webbing buckle 20mm](https://grabcad.com/library/ykk-webbing-buckle-20mm-1)（connor Bisby，STL）
- [Tri-Glide Buckle](https://grabcad.com/library/tri-glide-buckle-1)、[Basic cord lock](https://grabcad.com/library/basic-cord-lock-1)
- 通用参数化 25 mm 插扣 STEP（锁舌未建模）：[The Library of Everything](https://thelibraryofeverything.org/c/cmp_d500351d5895)

### 2.4 许可要点

- **GrabCAD**：[使用条款](https://grabcad.com/terms) §6.2 给其他用户的许可仅限"for such user's own benefit and non-commercial, internal use (the 'Cross License')"。页面还声明这些 CAD 文件与任何公司无赞助或隶属关系。**不能直接用于商业量产。** [已核实]
- **Sketchfab**：按模型标注，CC BY 需署名，CC BY-SA 要求衍生作品同样许可，CC BY-NC 禁止商用。
- **CGTrader**：[Royalty Free License](https://help.cgtrader.com/hc/en-us/articles/360015124437-Royalty-Free-License) 与 [条款 §21A](https://www.cgtrader.com/pages/terms-and-conditions) 只允许把模型用在"Incorporated Product"（渲染图、游戏、影片等）里；带品牌名的模型另有商标问题。

---

## 3. 五金厂商的 CAD 与规格资料

### 3.1 各厂商公开情况一览

| 厂商 | 公开了什么 | 在哪里 | 是否需注册 | 是否有 STEP/3D |
| --- | --- | --- | --- | --- |
| YKK（塑料五金） | 带尺寸表和线图的目录 PDF（注明"Dimensional information is for reference only"） | [YKK Europe 目录](https://ykkeurope.com/wp-content/uploads/2019/03/ykk-plastic-hardware-catalog.pdf)、[YKK Poland 目录](https://ykk.pl/wp-content/uploads/2021/01/ykk-plastic-hardware-catalog.pdf) | 否 | 官方称可提供 OBJ、STL、FBX（[Global Collection 2025](https://ykkdigitalshowroom.com/assets/YKK_Volume16_GlobalCollection_2025.pdf)）；需通过销售代表或 [Trim Creator 申请表](https://ykkdigitalshowroom.com/en/gf/digitalization/ykk_trim_creator/admission/)，并声明数据"for reference only"、不得提供给能生产同类产品的第三方。是网格，不是 STEP |
| ITW Nexus | 网页产品目录带尺寸表；Global Catalog 2021 PDF | [global.itwnexus.com 目录页](https://global.itwnexus.com/content/catalog-0)；欧洲目录见经销商转载 [ITWNexus.pdf](https://www.acesupplies.co.uk/wp-content/uploads/2022/10/ITWNexus.pdf) | 否 | 未见公开 STEP 下载 |
| Duraflex | 北美（National Molding）与亚洲目录只列料号，**不公布尺寸** | [National Molding Stealth](https://nationalmolding.com/product/stealth-side-squeeze-buckle/)、[duraflexusacatalog.com](https://duraflexusacatalog.com/stealth-series/)、[2024 目录 PDF](https://www.texnetinc.com/wp-content/uploads/2025/04/DuraflexCatalogue-2024-04-12.pdf)、[duraflexgroup.com](https://www.duraflexgroup.com/products?productType=Buckle) | 否 | 无 |
| Woojin Plastic (WJ) | 2019 目录 PDF 只列料号；官网产品页列长/宽/高/强度 | [2019 目录](http://www.woojinplastic.com/kr/download/2019%20Woojin%20Plastic%20Catalogue.pdf)（镜像 [asiaplastic.com.hk](https://asiaplastic.com.hk/catalog.html)） | 否 | 无 |
| Nifco | 网页尺寸表 + 单品数据表 PDF | [SR 系列](https://nifcobuckle.com/buckle/sidereleasebuckle/sr)、[SR25 数据表](https://nifcobuckle.com/images/sr/28_SR25.pdf)、[SRGT 系列](https://en.nifcobuckle.com/side-release-plastic-buckles/) | 否 | 无 |
| Fidlock | 产品页 + 带尺寸的 PDF 数据表 | [V-BUCKLE](https://www.fidlock.com/components/en/products/v-buckle)、[数据表示例](https://www.fidlock.com/components/sites/default/files/FV-11202_FV-11402_V-BUCKLE-25-split-bar%2Bpull-tab-datasheet.pdf) | 否 | 未见公开 STEP（需联系 info@fidlock.com） |
| AustriAlpin COBRA | 含尺寸的产品手册及单品数据表 | [Workbook Components 2026](https://www.austrialpin.at/fileadmin/userdaten/dateien/AA_Workbook_Component_2026.pdf)、[下载页](https://www.austrialpin.at/en/service/downloads/) | 目录否；图片库需登录 | 未见公开 STEP |
| 2M（Due Emme，意大利） | 技术资料在保留区 | [2m-italia.it](https://www.2m-italia.it)，例 [CRP/DR](https://www.2m-italia.it/en/products/42/buckles/50896/crp-dr.html) | **是** | 未核实 |
| SBS 拉链 | 规格对照表、电子目录 | [尼龙拉链规格页](https://www.sbs-zipper.com/standard-coil-zipper-cord-p81/)、[电子目录](https://www.sbs-zipper.com/catalog-download/sbs-e-catalogue-for-garment-2/) | 否 | 无 |
| UTX-Flex | 未找到厂商自己的目录或尺寸图。零售商把它与 Duraflex 并列标为"UTX / Duraflex"（例 [Element Trimming](https://elementrimming.com/collections/custom/utx-duraflex)，型号如 C3SSB-20），页面只有适用织带宽度 | — | — | **[未核实]** |

补充：经销商 Components Direct 对通用重型插扣 BSR016 提供 CAD 下载（[页面](https://components-direct.com/component-and-fastener-products/plastic-side-release-buckles-heavy-duty)），不是品牌原厂件。

更正一个常见误称："Airloc"是 **ITW Nexus** 的系列（AIRLOC 20/25/40/50），不是 Woojin 的。Woojin 的对应系列是 Dolphin、Stag Beetle、ST Buckle 等。用户所说的"YKK LB-20"对应目录里的 LB20R、LB20GV 等具体代码。

### 3.2 已核实的 20 mm / 25 mm 织带用五金尺寸

各厂的 A/B/C/D 字母定义不同，**以原表图示为准**；下表按原表字母照录，单位 mm。

**YKK（来源：上述 YKK 目录 PDF，[已核实]）**

| 类别 | 代码 | A | B | C | D |
| --- | --- | --- | --- | --- | --- |
| 侧开插扣 | LB20GV / LB25GV | 21 / 26 | 28 / 34 | 47 / 56 | 10 / 12 |
| 侧开插扣（双调） | LB20GVD / LB25GVD | 21 / 26 | 28 / 34 | 55 / 64 | 10 / 12 |
| 侧开插扣 | LB20R / LB25R | 20 / 26 | 27 / 34 | 54 / 66 | 9 / 11 |
| 侧开插扣（双调） | LB25RD | 25 | 34 | 76 | 11 |
| 侧开插扣 | LB20RS / LB25RS | 20 / 25 | 27 / 32 | 45 / 46 | 7 / 7 |
| 侧开插扣 | LB20S / LB25S | 21 / 26 | 26 / 31 | 42 / 46 | 8 / 9 |
| 侧开插扣 | LB20HE / LB25HE | 21 / 26 | 26 / 33 | 44 / 55 | 9 / 10 |
| 梯扣 | LK20GV / LK25GV | 21 / 26 | 27 / 32 | 32 / 35 | 9 / 10 |
| 梯扣 | LK20TS / LK25TS | 21 / 26 | 27 / 32 | 28 / 30 | 9 / 9 |
| 日字扣 | LA20S / LA25S | 21 / 26 | 27 / 32 | 22 / 25 | 6 / 6 |
| 凸轮扣 | LA20CB / LA25CB（适用带厚 1.2–1.7 mm） | 21 / 26 | 27 / 32 | 30 / 30 | 12 / 14 |
| 口字环 | LH20E / LH25E | 21 / 26 | 28 / 33 | 14 / 14 | 3 / 3 |
| 三角环类 | LT20TG / LT25TG | 20 / 26 | 28 / 35 | 12 / 16 | 5 / 6 |

胸带调节件：LH10GYC、LH15CS、LA-PS（3.5 mm 滚边滑块）在目录中列出，本次未记录尺寸。

**ITW Nexus（[已核实]）**

| 产品 | 料号 | A | B | C | D | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| Classic SR 20 | — | 20.3 | 25.8 | 54.5 | 8.8 | [eu.itwnexus.com/content/classic-sr](https://eu.itwnexus.com/content/classic-sr) |
| Classic SR 25 | — | 25.5 | 33 | 72.3 | 13.4 | 同上 |
| SR 1（缩醛） | P/N 305814（101-0100） | 25.0 | 31.9 | 70.0 | 11.7 | [global.itwnexus.com/content/sr-1](https://global.itwnexus.com/content/sr-1) |
| Ladderloc 1" | 104-0100 | 25.3 | 32.4 | 40.7 | 7.7 | [na.itwnexus.com/content/ladderloc](https://na.itwnexus.com/content/ladderloc) |
| GTSR Ladderloc Body 1" / Latch 1" / 3/4" body | 810-1070 / 810-1058 / 810-1084 | 尺寸栏为"-"，**未公布** | | | | [GTSR 页面](https://na.itwnexus.com/content/gtsr-ladderloc-body) |

**Nifco（[已核实]，POM）**

| 代码 | A | B | C | D | E |
| --- | --- | --- | --- | --- | --- |
| SR20-02 | 53 | 26 | 20 | 20 | 9 |
| SR25-02 | 68 | 32 | 25 | 25 | 12 |

**Woojin（[检索摘要]，官网产品页直接抓取返回 403）**

- ST Buckle 25 mm（3314/3315）：62.3 × 35.4 × 13.2 mm，强度 75 kg；38 mm：71.8 × 48.2 × 13.8 mm，80 kg（[产品页](http://www.woojinplastic.com/kr/product/view.php?idx=894&part_idx=145)）。
- 目录料号（[已核实]，无尺寸）：Dolphin 20 mm W331/W332、25 mm W334/W335、38 mm W337/W338；Dual Adjust Dolphin 25 mm W334/W336；Stag Beetle 25 mm W091/W092。

**Duraflex（料号 [已核实]，尺寸无官方数据）**

- Stealth Side Squeeze 3/4" 缩醛 6403/6404（尼龙 5616/5617）；1" 缩醛 6358/6359（尼龙 5614/5615）；Dual Adjust 1" 6358/6410；Mojave 1" 5000/5001。
- 零售商（非官方）数据：Stealth 25 mm 外形 35 × 60 × 11 mm，最小拉力 90 kg，11.6 g（[Shelby Outdoor](https://shelbyoutdoor.com/en/p103225/duraflex-stealth-buckle-for-25-mm-webbing)）。**[未核实，仅供参考]**

**Fidlock（[已核实]）**

- V-BUCKLE 25：72.0 × 34.0 × 14.0 mm，约 25 g，PA66GF + 不锈钢，静态破断力 686 N。
- V-BUCKLE 20（FV-14410-000012(BLK)）：74.0 × 34.2 × 13.5 mm，约 23 g，686 N。

### 3.3 拉链

- YKK 5CN：链牙宽 6.5 mm，布带总宽约 31 mm（[Extremtextil 商品页](https://www.extremtextil.de/en/ykk-aquaguard-5c-zippertape-by-the-meter/70186.SW)，零售商数据）。[已核实]
- YKK 8C 约 7.9 mm、10C 约 10.5 mm 链牙宽：只来自对 [YKK Poland 2025 目录](https://ykk.pl/wp-content/uploads/2026/07/YKK-katalog-2025_nowe-logo_prev.pdf) 的检索摘要，**[未完全核实]**。
- AquaGuard 布带单边宽：5C 为 5/8"（16 mm），8C 为 5/8" 或 3/4"（19 mm），10C 为 3/4"（[YKK USA AquaGuard 资料](https://ykkdigitalshowroom.com/assets/USA_AQUAGUARD_Water_Repellent_zipper_en.pdf)）。[已核实]
- YKK Racquet Coil（RC）5/8/10 号："Especially designed for luggage and backpack where resistance to abrasion is a must"（[YKK Americas Fastening Catalogue](https://ykkamericas.com/wp-content/uploads/2021/10/FasteningCatalogue_update20220120.pdf)）。[已核实]
- SBS：拉链号数按啮合后链牙宽定义，#8 约 7.2–8.0 mm（[SBS 说明](https://sbs-zipper.com/zipper/10690.html)）；规格页并列了 QB/T 2171-2014、SBS 企标 Q/XXKG.001-2015 与 DIN 3419 的指标。[已核实]

### 3.4 实务建议

选定供应商后直接向其销售/代理索取 2D 图（PDF/DWG）和承诺的强度数据，这是行业惯例；公开目录只够做前期选型和 tech pack 里的占位尺寸。

---

## 4. 带真实二维裁片的 MYOG 背包纸样（30–50 L 为主）

### 4.1 可购买/可下载的纸样

| 来源 | 型号与容积 | 结构 | 文件格式 | 价格 | 许可（原文） | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| Prickly Gorse / MYOG Tutorials | [40 L Frameless](https://myogtutorials.com/40-litre-frameless-ultralight-backpack/) | 卷口无框超轻包 | PDF（US Letter/A4/大幅面） | £8.99 | 商品页："Not for commercial use"；纸样页印有"Copyright Prickly Gorse 2023. No unauthorised copying or distribution. Not for commercial use, personal use only!" | [已核实] |
| 同上 | [40 L Framed](https://www.myogtutorials.com/40-litre-framed-ultralight-backpack/) | 卷口、内框、可拆加垫腰带，约 880 g，标称可背 >15 kg | 同上 | £9.99 | 同上 | [已核实] |
| 同上 | [50 L Framed](https://www.myogtutorials.com/50-litre-framed-ultralight-backpack-sewing-guide/) | 同上 | 同上 | £9.99 | 同上 | [已核实] |
| Stitchback | [FL 40 L](https://www.stitchbackgear.com/patterns/stitchback-fl-sewing-pattern) | 前开拉链式、含背板纸样、肩带上拉带、腰带 | "CAD drafted" PDF（8.5×11 + 36×48 英寸） | $12 | 见下方 4.2 | [已核实] |
| 同上 | [TH50 50 L](https://www.stitchbackgear.com/patterns/stitchback-th-sewing-pattern) | 卷口、背板套、男女款腰带与肩带；背板 11" × 24"，外形约 12"w × 9"d × 26"t | 同上 | $11 | 同上 | [已核实] |
| 同上 | [Metamorph 45 L](https://www.stitchbackgear.com/patterns/stitchback-metamorph) | — | 同上 | $10 | 同上 | [已核实] |
| Bag Buff（Stephen Jones） | Mountain Flyer [40 L](https://www.bagbuff.com/products/40l-mountain-flyer-ultralight-backpack-pattern)（RBTR [40 L](https://ripstopbytheroll.com/products/mountain-flyer-backpack-pattern-40-l)、[34 L](https://ripstopbytheroll.com/products/mountain-flyer-ul-backpack-pattern-34-l)） | 卷口超轻包，Y 形顶带、腰带、加垫背板 | 数字包：大幅面模板、物料清单、工序顺序、"Tech pack"、排料图；另有 [纸质模板套装 $38.50](https://ripstopbytheroll.com/products/mountain-flyer-ul-backpack-template-40-l) | $20 | 商品页没有许可条款，**[未核实]**；设计者在[个人网站](https://mrjones.tech/mountain-flyer-ultralight-backpack)泛称"Open-Source Pattern"，无正式许可文本 | 页面 [已核实] |
| DutchWare | [DIY 30L Backpack Pattern](https://dutchwaregear.com/product/diy-30l-backpack-pattern/) | 面向新手的简单背包 | PDF（A0 与 A4）+ 视频教程 | $40 | 页面未写许可，**[未核实]** | [检索摘要] |
| Ray-Way（Ray Jardine） | [Backpack Kit](https://www.rayjardine.com/ray-way/Backpack-Kit/index.php)，2,200–3,000 立方英寸（2,600 约 42.6 L） | 无框 | 实物材料包 + 纸质说明，**无数字纸样** | $95.49 | [订购页](https://rayjardine.com/Order-Form/index.php)："These projects are for individual use only Commercial use of our designs, instructions, or patterns - or something like them - is strictly prohibited." | [已核实] |
| Gossamer Gear G4 | 约 70 L 无框 | 见 1.2 | PDF | 免费 | 个人使用（转述） | [检索摘要] |
| Whiskey Two Four WTFiles | Backpack 00（约 12 L）、Backpack 36 | 战术包 | 矢量 PDF | $20 | [未核实] | [已核实] |
| Open+Pattern | 瑞士 M70/M79 | 老式军用背包 | ZPRJ、DXF-AAMA、PDF、GLB | 自愿付费 | **CC BY 4.0，允许商用，需署名** | [已核实] |
| LearnMYOG | 目前只有 [Trail Running Backpack 12 L](https://learnmyog.com/trailRunningBackpack.html)（RBTR 售 [$30](https://ripstopbytheroll.com/products/trail-running-backpack-pattern)）；[Fastpack](https://learnmyog.com/fastpack.html) 已下架。**没有 30–50 L 徒步包** | — | PDF（Letter/A4/A0） | — | [About 页](https://learnmyog.com/about)："LearnMYOG patterns are for personal use only. Make gear for your friends and family… Small businesses, Reddit sellers, Etsy shops, etc -- please respect indie creators and their wishes." | [已核实] |

### 4.2 Stitchback 的使用政策（对量产团队最有价值）

[Pattern Use Policy](https://www.stitchbackgear.com/use-policy) 原文要点 [已核实]：

- "you are granted a limited use license to use the pattern for your own personal use"
- "The copyright on our patterns extends only to the pattern and instructions contained in the PDF, and not to any item that you make… We hope you will respect the DIY spirit of the site, by not mass producing any of the items"
- "If you run a small business and are looking for a pattern that you would like to put into mass production, we may be able to help… through a licensing agreement."

也就是说，它是本次查到的**唯一明确表示愿意谈量产授权**的 MYOG 纸样商，而且 FL 40 L 的架构（前开、背板、上拉带、腰带）最接近常规 40 L 徒步包。

### 4.3 参数化/开源生成器

| 项目 | 内容 | 许可 | 状态 |
| --- | --- | --- | --- |
| Prickly Gorse [在线纸样生成器](https://myogtutorials.com/online-automatic-pattern-generator/)、[Roll Top Bag Calculator](https://www.myogtutorials.com/roll-top-bag-calculator/) | 侧片/卷口袋尺寸计算 | 未声明 | [已核实] |
| [pricklygorse/Inkscape-Unroll-to-Straight-Extension](https://github.com/pricklygorse/Inkscape-Unroll-to-Straight-Extension) | Inkscape 扩展，把曲线边展开对长度 | 仓库未见许可文件 | [已核实] |
| Friluftstyger [纸样生成器](https://www.friluftstyger.se/en/pages/monster-generatorer) | Rolltop Backpack、Shoulder Strap 等，导出 PDF + SVG，带 3D 预览 | **[未核实]** | [检索摘要] |
| FreeSewing | MIT 许可，[明确允许商用](https://freesewing.eu/docs/about/faq/commercial-use/)；但包类只有 Hortensia 手提包，没有徒步背包 | MIT | [已核实] |
| [kieranklaassen/kabaka](https://github.com/kieranklaassen/kabaka) | 仓库描述："A backpack design by Adam Atkins made into a pattern by Kieran Klaassen"；FreeSewing 式 JS 纸样，0 star | MIT | 元数据 [已核实]；容积与完成度 **[未核实]** |
| [Caleb68864/Seamly2d-Tutorial-Patterns](https://github.com/Caleb68864/Seamly2d-Tutorial-Patterns) | Seamly2D 教学用简单背包（.val + PDF） | MIT | [已核实] |
| [myogpatterns/myogpatterns.github.io](https://github.com/myogpatterns/myogpatterns.github.io) | LearnMYOG 网站源码 | 仓库无许可文件（默认保留所有权利），且网站声明仅限个人使用 | [已核实] |
| [b0bTHEbilder/Patterns](https://github.com/b0bTHEbilder/Patterns) | 战术小件，不是背包 | 无许可 | [已核实] |

用 GitHub 搜索"backpack pattern""rucksack pattern""roll top backpack""backpack dxf"等均无结果。**没有找到成熟的参数化徒步背包纸样生成器。**

### 4.4 中文来源

- 没有找到信誉可靠、可免费下载的 30–50 L 登山包纸格/DXF。
- 素材站有用户上传的工程文件，例如绘图狗的 [MD战术双肩包纸样文件CLO背包zprj](https://huitugou.com/index/index/show/cid/438/id/3188)（2023-11-23 上传）。来源、是否原创、许可条款页面上都没有写，**[未核实]，不建议用于量产**。
- 中文资料主要是打版**教程**而不是成品纸样：皮具论坛的 [ET 电脑出格教学文档](https://bbs.ggpiju.com/forum.php?mod=viewthread&tid=1603)（含抛量、打角、拉链缝合、ET 围等箱包专用工具）；B 站 [博克箱包CAD 出格设计系列](https://www.bilibili.com/video/BV1Mn15BNEnK/)（含"背包直围、拉链缝合"）；广州唯耀培训中心的 [博楷皮具箱包CAD 视频教程](https://training.veryio.com/shipinjiaocheng/287.html)（含"背包抛围""转到 CorelDRAW 打印纸格"）；教材《箱包CAD应用教程》（2011 年版，基于富怡箱包 CAD，第五章有"结实耐用的运动双肩背包"出格实例）。
- 台湾鞋类暨运动休闲科技研发中心的 [Bag Source Code 袋包快速打樣中心](https://bagsdesign.bestmotion.com/download) 有按前片/侧片/后片/肩背带/腰带分类的组件库页面；下载条件与许可 **[未核实]**。
- 淘宝、闲鱼上的"背包纸样"本次无法访问核实，来源通常不明，**[未核实]**。

### 4.5 关于"纸样版权管不管成品"

[Craft Industry Alliance 的文章](https://craftindustryalliance.org/personal-use-restrictive-clauses-craft-patterns/) 指出（美国法语境）：版权保护的是纸样文件本身，而不是按它做出来的实用物品；"仅限个人使用"多数是购买时的合同条款。这**不等于可以放心商用**：合同约束仍然成立，其他法域（含中国）规则不同，还可能涉及外观设计、专利和不正当竞争。见第 7 节。

---

## 5. 做生产 tech pack 用得上的标准与技术参考

### 5.1 中国标准

**QB/T 1333-2018《背提包》**（2018-05-08 发布，2018-09-01 实施，代替 QB/T 1333-2010）。以下内容来自第三方转录文本（[标准翻译网](https://www.bzfyw.com/site/bz/standard/QBT1333-2018.html)、[标准下载网](https://www.bzxz.net/bzxz/197397.html)）与检测机构摘要（[SCS](https://www.scsgroup.com.cn/zh-CN/content/522-qb-t-1333-2018-%E8%83%8C%E6%8F%90%E5%8C%85%E6%A0%87%E5%87%86)、[欧冠检测](https://www.cpst.com.tw/news/ins.php?index_id=121)），转录有 OCR 错字，**正式引用前请对照正版标准文本**。

- 适用范围："适用于各种日常生活用的背提包。具有特殊用途的背提包可参照使用。" 即徒步包只是"可参照"。
- 振荡冲击：按 QB/T 5083 测容积，按表 5 取负重，按 QB/T 2922 试验。次数：双背带、双提把各 400 次；单背带、单提把各 250 次；侧提带 150 次。
- 表 5 规定负重（不含包体自重）：

| 容积 / L | 提把、单背带、侧提带 / kg | 双背带 / kg |
| --- | --- | --- |
| ≤2 | 不检 | 0.5 |
| >2～4 | 0.5 | 1 |
| >4～8 | 1 | 2 |
| >8～12 | 2 | 3 |
| >12～16 | 3 | 4 |
| >16～20 | 4 | 5 |
| >20 | 5 | 6 |

  **对 40 L 徒步包，标准只要求双背带负重 6 kg 振荡 400 次，远低于实际 12–18 kg 的使用负荷。** 企业内控必须另定更高负重。
- 缝合强度：在 100 mm × 30 mm 有效面积上不低于 240 N（简易收叠式包不低于 120 N）；拉伸速度 (100±10) mm/min。
- 拉链耐用度：取 20 cm 长，20 次/min，开合 200 次，试验后无掉牙、错牙、损坏。
- 扣件耐用性能：按 QB/T 5084，1000 次。塑料插扣耐用性能：按 QB/T 5247，1000 次。背带耐折：按 QB/T 5246，500 次。
- 摩擦色牢度（纺织材料）：干擦 ≥3-4 级，湿擦 ≥2-3 级（GB/T 3920）。
- 五金耐腐蚀：中性盐雾（QB/T 3826），16 h，腐蚀点不超过 3 个且单点面积不大于 1 mm²。
- 有害物质（纺织类材料）：可分解有害芳香胺染料 ≤30 mg/kg；游离甲醛 ≤300 mg/kg（甲醛按 GB/T 2912.1，偶氮按 GB/T 17592）。胶粘剂按 GB 19340。
- 拉链应符合 QB/T 2171、QB/T 2172、QB/T 2173。

**QB/T 2922-2018《箱包 振荡冲击试验方法》**（[规范库转录](https://www.guifanku.com/828281.html)，[检索摘要]）：冲击装置总质量 (8.1±0.2) kg；单向行程 (150±5) mm（以外加 30 kg 负载设定）；减震弹簧常数 (17.54±0.88) N/mm；双肩背带夹具 (1.35±0.05) kg；试验频率优先 (20±2) 次/min；提把、背带用自由落体模式。

**QB/T 2173-2014《尼龙拉链》**（[原创力文档转录](https://max.book118.com/html/2023/0809/8055100106005117.shtm)，OCR 文本，[检索摘要]，请对照正版）：

| 型号 | 3 | 4 | 5 | 7 | 8 | 10 |
| --- | --- | --- | --- | --- | --- | --- |
| 链牙啮合宽度 / mm | 3.9～4.5 | 4.9～5.4 | 5.5～6.2 | 6.3～7.0 | 7.2～8.0 | 10.0～10.6 |
| 平拉强力 / N ≥ | 380 | 400 | 600 | 650 | 800 | 900 |

负荷拉次 ≥600 双次。金属拉链为 QB/T 2171-2014，注塑拉链为 [QB/T 2172-2014](https://std.samr.gov.cn/hb/search/stdHBDetailed?id=8B1827F21AE0BB19E05397BE0A0AB44A)（全国标准信息公共服务平台，现行）。出口欧洲常用 BS EN 16732（[CTI 华测解读](https://www.cti-cert.com/new/45804.html)）。

**GB 18401-2010《国家纺织产品基本安全技术规范》**（[全文](https://law.resource.org/pub/cn/ibr/gb.18401.c.2010.pdf)，[已核实]）：
- A/B/C 类甲醛限量分别为 20 / 75 / 300 mg/kg；pH 分别为 4.0–7.5 / 4.0–8.5 / 4.0–9.0；甲醛测定按 GB/T 2912.1。
- **附录 A（不属本标准范围的纺织产品目录）A.12 明列"箱包、背提包、鞋、伞等"**；商务部转载的[解读](http://chinawto.mofcom.gov.cn/article/jsbl/zszc/201411/20141100792845.shtml)也这样写。
- 有些检测机构网页仍称它适用于箱包并按 C 类要求（例如 [这一页](https://www.testrust.com/company/product--16930--520058.html)），与标准附录 A 文本不一致。客户或电商平台若在合同里指定 GB 18401，则按合同执行。

**其他**
- 没有找到专门针对"户外登山背包"的 GB/T 或 QB/T 产品标准（检索未发现，不代表一定不存在）。团体标准有 [T/CASME 1285-2024《多功能户外休闲包》](https://www.ndls.org.cn/standard/detail/f10ec5b25d2f5e98a8154df7171f2465)，内容未读，**[未核实]**。
- 一份公开的国内背包技术规范范例：中国地质调查局《地质调查野外作业服装 地质背包 技术规范》（2023 年 10 月，[PDF](http://www.chegs.cgs.gov.cn/gzdt_4611/zbzp_4615/202607/W020260716514215977418.pdf)，[检索摘要]）。它列出了成品尺寸与公差、物料表（500D 涤纶 PVC 涂层、420D 里布、8 mm 珍珠棉、15 mm 海绵、3 mm PE 板、三明治网、1 寸尼龙织带）、开裁与缝制要求，以及塑料扣具拉力下限（赛钢，耐低温 -30 ℃）：插扣 20 mm 30 kg、25 mm 35 kg、38 mm 50 kg；梯扣 20 mm 30 kg、25 mm 40 kg。注意：该文件引用的拉链数值与上面 QB/T 2173-2014 转录值不一致（例如 5 号平拉 ≥500 N），以正版标准为准。
- 织带拉伸：检测机构网页提到用 GB/T 3923.1-2013（条样法）、ISO 13934-1、ASTM D5034（[北检院页面](https://www.bjytest.com/bjy/xnjc/qdsy/166759.html)）。这是机构营销页的说法，**[未核实]** 是否为织带的规范方法。

### 5.2 线迹、缝型、打枣

- 线迹分类：[ISO 4915:1991](https://www.iso.org/standard/10932.html)（线迹类型，300 类为锁式线迹，301 为单针锁式）；缝型分类：[ISO 4916:1991](https://www.iso.org/standard/10934.html)（8 大类，见 [Coats 说明](https://www.coats.com/en-us/info-hub/seam-types/)）；美国对应 [ASTM D6193](https://www.astm.org/d6193-16r25.html)，旧版为公有领域的 FED-STD-751。[已核实]
- MIL-F-43832C 的实际条款（[已核实]，PDF 为 OCR 文本）：
  - 除包边、拷边外的缝合用线迹 301 或 401，**8–10 针/英寸**；包边与预缝用 301，8–10 针/英寸；拼接缝型 SSa-1，缝边 1/2 英寸；拷边用 503、504 或 602，8–12 针/英寸。
  - 301 线迹起止回针不少于 1 英寸（方框、方框叉线迹为 1/2 英寸）。
  - 打枣（bartack）表：长 1/2 英寸 → 28 针；长 3/4 英寸 → 42 针；长 1 英寸 → 42 针；长 2 英寸 → 80–84 针；宽均为 1/8 英寸（OCR 表头模糊，列含义按上下文判读）。
  - 线：涤纶线 V-T-285，一般缝合用 F 号，包边、拷边、打枣用 E 号；禁止在缝制前后给线上油。
- "42 针打枣"在行业里通用：降落伞厂 Performance Designs 的维修文件写"bartacker with between 28 and 42 stitch… between 1/2" and 5/8" long, and 1/8" wide"（[PDF](https://www.performancedesigns.com/_files/ugd/cc1125_b6bf6147c19f4b478486c08db2cf0e60.pdf)，[检索摘要]）。工厂博客给出的典型值是 12–16 mm × 3–4 mm、28–42 针（[示例](https://modularbagpro.com/blog/bar-tack-placement-on-modular-panels/)，非权威来源）。

### 5.3 缝纫线

- 粘合尼龙线尺寸对应关系（[Fil-Tec B.A.T. 规格表](https://www.fil-tec.com/BAT-USA-Government-and-Mil-Spec)，[检索摘要]）：

| 美军号 | 商业号 | Tex | 强度 / lb | 建议机针（公制） |
| --- | --- | --- | --- | --- |
| B | 46 | 45 | 7.5 | 90–100 |
| E | 69 | 70 | 11.5 | 110–120 |
| F | 92 | 90 | 15 | 120–130 |
| FF | 138 | 135 | 23 | 130–140 |

- 其他供应商给 #69/Tex 70 的机针范围是 100/16–110/18（[Superior Threads](https://www.superiorthreads.com/education/bonded-thread-needle-guide)、[Longhorn Textiles](https://longhorntex.com/NYLONTHREAD)）。
- Tex 70 对应 210D/3，Tex 90 对应 280D/3（[NEXUS 线厂说明](https://bondedthread.com/blog/tex-90-bonded-nylon-thread-description/)，厂商内部测试数据）。
- "20/3 涤纶线"作为背包主缝线的说法，本次**未找到来源，[未核实]**。

### 5.4 缝份、包边带、织带宽度

- 缝份：背包常用 3/8 英寸（约 10 mm）。佐证：Prickly Gorse 计算器推荐 1/4、3/8（1 cm）、1/2 英寸（[页面](https://www.myogtutorials.com/roll-top-bag-calculator/)）；OV Innovations 对 Gregory ILBE 试验包的拆解称其缝份为 1/2 英寸，并说这比行业通行的 3/8 英寸大（原文"larger than the industry standard 3/8"）（[文章](https://ovinnovations.com/pages/gregory-ilbe)）；一家工厂的 tech pack 模板示例写 10 mm（[Senszx](https://senszxfactory.com/blogs/how-to-write-a-backpack-tech-pack/)）。这些都是经验值，**不是标准规定**。
- 包边带：内缝包边常用 20–25 mm（3/4–1 英寸）罗纹带/包边带（Prickly Gorse 物料清单用 1 英寸罗纹带；Senszx 模板示例为 20 mm 涤纶包边带）。经验值。
- 织带宽度：五金目录按 15/16、20、25、38、50 mm（5/8"、3/4"、1"、1-1/2"、2"）分档；YKK 凸轮扣 LA20CB/LA25CB 标明适用带厚 1.2–1.7 mm。织带宽度本身的标准号 **[未核实]**。

### 5.5 泡棉

没有找到公开的权威规范，以下均为工厂博客或爱好者经验，**仅作起点，[未核实]**：
- 肩带用闭孔 EVA 50–75 kg/m³，腰带用更硬的 80–100 kg/m³，双密度做法是硬芯（约 100 kg/m³）加软面（约 50–60 kg/m³）（[MBK 文章](https://mensbackpack.co.uk/articles/backpack-foam-density-compared.html)、[r/myog 讨论](https://www.reddit.com/r/myog/comments/mxghmc/shoulder_straphip_belt_eva_foam_density_for/)）。
- 典型厚度：肩带约 8–20 mm，腰带约 10–15 mm，背板约 8–15 mm（[Sympathybag 文章](https://sympathybag.com/backpack-foam-padding-guide)）。
- 唯一查到的规范性写法：MIL-F-43832C 的背垫泡棉为 1/2 英寸厚，符合 ASTM D 1056 RE 41 级。[已核实]

### 5.6 背板与铝条

没有公开标准，以下为公开的实例数据：
- Stitchback 教程：1/16 英寸（约 1.6 mm）HDPE 板；铝条用 3/4" × 1/8" 或 1" × 1/8" 扁铝，作者用 6061-T6511（[文章](https://www.stitchbackgear.com/articles/frame-sheet-with-stay)）。[已核实]
- Gregory ILBE 试验包（第三方拆解）：两根 7075-T6 铝条，各 0.75" × 24"，固定在 3/16 英寸 HDPE 板上（由 1/8" 与 1/16" 两层组成）（[OV Innovations](https://ovinnovations.com/pages/gregory-ilbe)）。[检索摘要]
- 爱好者实例：1.5 mm HDPE + 两根 3 mm × 19 mm 7075 铝条 + 6 mm EVA，背 20 kg（[r/myog](https://www.reddit.com/r/myog/comments/173jt6c/weight_limits_for_hdpe_frame_sheets_aluminium/)）。
- 用户提到的"25 × 3 mm 7075-T6"：接近论坛里提到的 1" × 1/8"（25.4 × 3.2 mm）7075 规格，但没有品牌官方数据，**[未核实]**。
- 国内范例（地质背包规范）用 3 mm PE 板。

### 5.7 国际/出口测试方法

- **没有找到专门针对徒步背包的 EN/ISO 协调产品标准**（检索未发现）。品牌通常用自定规范加通用方法：面料拉伸 ISO 13934-1、撕裂 ISO 13937-2、耐磨 ISO 12947、静水压 ISO 811、摩擦色牢度 ISO 105-X12、盐雾 ISO 9227、偶氮 EN 14362、拉链 EN 16732 / ASTM D2061，以及 SATRA 的静载/动载/跌落方法（见 [STC 检测服务页](https://stc.group/en/services/detail/174)）。各方法是否被具体品牌采用 **[未核实]**。
- "jerk test（猛拉试验）"不是一个有标准号的试验名称；国内对应的是 QB/T 2922 振荡冲击。

---

## 6. 箱包行业的软件与文件流转

### 6.1 软件

| 环节 | 软件 | 证据 | 状态 |
| --- | --- | --- | --- |
| 国内箱包出格（打版） | ET-BAG（ET 箱包出格）、富怡箱包 CAD、博克箱包 CAD、博楷皮具箱包 CAD | 见 4.4 的教程与教材；这些软件有箱包专用功能（抛量、打角、围条、拉链缝合、自动算料、排料） | [检索摘要] |
| 效果图、印刷、logo、简单纸格 | CorelDRAW、Adobe Illustrator、AutoCAD | 博楷教程含"转到 CorelDRAW 打印纸格""转入到 AutoCAD 打印纸格"两节；工厂普遍要求 logo 提供 AI/EPS/PDF 矢量 | [检索摘要] |
| 服装/软包通用纸样 CAD | Gerber AccuMark、Lectra Modaris、Optitex PDS | DXF 互导流程见 [Modeltex 指南](https://modeltex.fashion/guides/import-dxf-patterns-optitex-audaces-gerber)；一家泉州背包厂自称使用 Lectra、Gerber、Optitex、CLO 3D（[Hetaixing OEM 页](https://www.hetaixingbackpack.com/oem-odm)，厂家自述） | [检索摘要]；它们在背包行业的普及程度 **[未核实]** |
| 3D 打样 | CLO3D、Browzwear VStitcher、Optitex | The North Face 装备与配件开发岗位写明"Familiarity with 3D development tools such as Browzwear, CLO, or Optitex is a plus"并用 Flex PLM（[招聘页](https://vfc.wd5.myworkdayjobs.com/en-US/northface_careers/job/USCA--USA--Colorado--Denver-HQ---VFC/The-North-Face--Associate-Developer--Equipment---Accessories_R-20260814-0014)）；Mystery Ranch 用 Centric PLM；Optitex 有 [YKK 3D 拉链库](https://optitex.com/ykk-zippers/) | [检索摘要] |
| CLO → 国内箱包 CAD | CLO3D 导出 DXF 再导入箱包 ET | CLO 社区有中文用户反馈导入 ET 后纱向线需逐片清理（[CLO-SET Connect](https://connect.clo-set.com/ko/community/user/6841/commented)） | [检索摘要] |

### 6.2 纸样交换格式

- **DXF-AAMA / ASTM D6673**：[ASTM D6673](https://store.astm.org/d6673-10.html) 是基于 AutoCAD R13 DXF 的缝制品纸样交换规范，**已于 2019 年撤销**，但 DXF-AAMA / DXF-ASTM 仍是事实标准。约定图层：1 外轮廓、4 刀口、7 纱向线、8 内部线、13 钻孔、14 缝线、15 文字；放码规则用 .rul 文件。[已核实]
- CLO3D 支持导入/导出 Standard DXF、DXF-AAMA、DXF-ASTM（[官方帮助](https://support.clo3d.com/hc/en-us/articles/115000493067-2D-Pattern-DXF-Import-Export)）。[已核实]
- 博克箱包 CAD 有"打开 DXF""保存 DXF 格式"功能（见其教学视频列表）。[检索摘要]

### 6.3 国内工厂裁床接受的文件格式

| 设备 / 厂商 | 标称支持格式 | 来源 |
| --- | --- | --- |
| 爱邦 箱包皮具振动刀裁切机 | PLT、DXF、CDR 等 | [产品页](http://www.iboncut.com/HTML/2023/11/16639.shtml) |
| 爱邦 服装电脑裁剪机 | AI、PLT、DXF、CDR 等 | [产品页](http://www.iboncut.com/HTML/2022/10/10417.shtml) |
| TRUSTER 鞋类/箱包振动刀切割机 | AI、PLT、DXF、DST、DSB、EPS 等；绘图软件列出 AUTOCAD、CORELDRAW、PGM、BOKE、GERBER | [产品页](https://www.trustercnc.com/zh-CN/cnc-oscillating-knife-cutting-machine-for-shoes-bags/) |
| 冠力激光 CO₂ 切割机（箱包皮具方案） | AI、DXF、PLT、CDR 等 | [方案页](https://gllaser.com/articles/95689611307145729.html) |
| 东兴科 振动刀皮革切割机 | DXF、PLT 等 | [产品页](https://www.dxcut.cn/show-36-78-1.html) |

以上均为设备商自述 [检索摘要]。结论：**DXF 和 PLT 是裁床的通用入口，AI/CDR 多数也能直接读**。给工厂的资料包通常是：PDF 版 tech pack（受控版本）+ 矢量图稿（AI/EPS）+ 纸样（DXF，最好 1:1 并注明单位和是否含缝份）。具体格式应在打样前与工厂确认。Hetaixing 自称接受 AI/EPS、DXF/DWG、Lectra/Gerber 原生文件、CLO 3D (.ZPRJ)、模塑件的 STEP/IGES 以及 PDF tech pack（厂家自述）。

实际情况提醒：多数国内背包厂仍由版师根据样包和尺寸图在自己的箱包 CAD 里重新出格，客户提供的 DXF 往往只作为参考。这一点来自行业常识，**[未核实]**。

---

## 7. 直白结论

### (a) 这些品牌有没有真正的公开生产 CAD？

**没有。** Mystery Ranch、Osprey、Deuter、Gregory、Kailas、Arc'teryx、Black Diamond、Aarn 都没有公开过生产纸样、DXF、tech pack 或带爆炸图的维修手册。网上带品牌名的 3D 模型全部是粉丝自建或实物扫描的外观网格，卖家关于"基于厂商原始数据"的说法无法核实。任何自称"原厂 tech pack / 原厂纸格"的文件，要么是假的，要么是泄露的商业秘密，都不能用。

### (b) 现实中存在的、最好的合法起点

按实用性排序：

1. **自己出版**：购买目标竞品实物做拆解测量（学习结构与工艺是常规做法），由自己的版师或工厂版师重新设计出格。注意避开仍有效的专利和外观设计，专利需另行检索。
2. **向 Stitchback 谈量产授权**：它是唯一明文表示可谈授权的 MYOG 纸样商，FL 40 L 的架构最接近目标。也可花十几美元/英镑购买 Stitchback FL、Prickly Gorse 40 L Framed 等纸样**用于内部学习**结构与工序（不得直接照搬量产）。
3. **Open+Pattern 瑞士 M70/M79（CC BY 4.0）**：款式不对，但它是一套完整的、允许商用的 ZPRJ + DXF-AAMA + PDF 文件，可用来打通"CLO → DXF → 工厂 CAD/裁床"的数据流程。
4. **MIL-F-43832C**：公开的真实量产规范，适合当作 tech pack 工艺条款（线迹密度、打枣针数、线号、检验缺陷分类）的写法范本。
5. **五金厂商目录**：YKK、ITW Nexus、Nifco 的公开尺寸表足以支持前期选型；定点后向供应商索取正式 2D 图和强度承诺。
6. **标准**：以 QB/T 1333-2018 为合规底线，配合 QB/T 2922、QB/T 2173、QB/T 5247 等方法，并自行加严负重与次数。

### (c) 把社区模型或 MYOG 纸样用于商业量产的法律/许可风险

1. **许可直接禁止**：GrabCAD 的 Cross License 仅限非商业、内部使用；CC BY-NC 禁止商用；CC BY-SA 要求衍生作品同样开放；Free3D 多为 Personal Use；CGTrader 的 Royalty Free 只允许用在渲染/游戏等"Incorporated Product"里。
2. **合同约束**：Prickly Gorse、LearnMYOG、Ray-Way 明文禁止商用，购买即受约束。即使在某些法域版权不延及成品，违反购买条款仍可能构成违约，并有商誉风险。
3. **没写许可 ≠ 可以用**：GitHub 上无许可文件的仓库默认保留所有权利；Bag Buff、DutchWare、WTFiles 页面没有写明许可，量产前必须取得书面许可。
4. **商标与外观**：带 Osprey、Arc'teryx 等品牌名的模型涉及商标；照着扫描网格复刻外形还可能触及外观设计专利、立体商标或不正当竞争（混淆）。
5. **专利**：背负系统、调节机构多有发明/实用新型专利（各品牌官网和专利库可查），纸样许可并不带专利许可。
6. **商业秘密**：泄露的 tech pack 或原厂纸格来源不合法，使用会带来侵害商业秘密的风险。
7. **厂商 3D 数据的使用条件**：YKK 的 3D 数据声明仅供参考且不得提供给能生产同类产品的第三方；爱好者测绘的插扣模型尺寸不可靠，不能据此开模或定孔位。
8. **技术上也不可用**：即使许可允许，外观网格也无法变成可量产的裁片，见 2.1。

---

## 附：访问失败与未核实清单

- GrabCAD 网页抓取返回 403，元数据通过其公开 JSON 接口取得；模型文件本身未下载、未打开。
- `https://www.wtfidea.com/wtfiles-backpack-00-open-source-cad-pattern`（原免费链接）404。
- Woojin 产品页 403；Fidlock 下载页 404；duraflexgroup.com 产品列表 504。相关数据来自搜索摘要。
- 写完后用脚本对全文 160 多个链接做了一次状态检查：约 140 个返回 200/206；backpacking.net 的 G4 旧说明页返回 404（已在正文改为纯文本）；osprey.com、iso.org、printables.com、reddit.com、turbosquid.com、free3d.com、dutchwaregear.com、superiorthreads.com、CLO 与 CGTrader 帮助中心等约 20 个站点对脚本返回 403/429 等反爬状态；标准翻译网（bzfyw.com）与 longhorntex.com 脚本连接超时。这些页面的内容此前是通过检索工具读到的，浏览器能否打开未逐一确认。
- 未核实项：Arc'teryx 官方零件/维修资料；UTX-Flex 厂商目录；2M 保留区资料；Bag Buff、DutchWare、WTFiles、Friluftstyger 的许可条款；kabaka 的容积与完成度；MIL-F-43832C 引用的 Natick 图纸能否下载；YKK 8C/10C 链牙宽；T/CASME 1285-2024 内容；"20/3 涤纶线"与"25 × 3 mm 7075-T6 铝条"的出处；泡棉密度的权威规范；淘宝/闲鱼纸样；3D ContentCentral、TraceParts、Cults3D、Thingiverse 的穷尽检索。
- QB/T 1333-2018、QB/T 2922-2018、QB/T 2173-2014 的数值来自第三方转录或 OCR 文本，正式使用前请购买并核对正版标准。
