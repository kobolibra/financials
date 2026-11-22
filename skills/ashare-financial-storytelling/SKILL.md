---
name: ashare-financial-storytelling
description: Research A-share periodic reports from original PDFs, reconcile source facts, develop company-specific and falsifiable financial analysis, and publish native desktop/mobile visuals as standalone HTML. Use for Q1, H1, 9M and FY reports, or for maintaining the kobolibra/financials publication workflow.
---

# A股财报深度研究与可视化 · 统一生产技能

Contract version: 10.3.0

### 必须先走自主主编闭环：不用用户反复指出漏项

**所有首次编稿与新增报告期均先执行 [Playbook 09 · 自驱研究与审美返工闭环](playbooks/09_SELF_DIRECTED_DELIVERY.md)。** 自动盘点源事实所支持的重大问题，运行 `research/shared/autonomous_editorial_audit.py` 获取事实覆盖、现行同库参照、逐图视觉复核和需要主动返工的缺口。编辑自己查看真实桌面/手机截图、跟至少两份成熟作品对照后修改；不能拿图表数量、字数、分数、自信措辞或 CI 全绿代替论证深度/审美判断。作者自评与独立研究审稿必须分开。新稿如审稿未完成保持草稿，不等待用户充当审稿员。

```bash
python research/shared/autonomous_editorial_audit.py --code <code> \
  --out work/editorial/issues.json --review-template work/editorial/author-tasks.json
python research/shared/autonomous_editorial_audit.py --code <code> --strict
```

### 泛化与质量门禁的新增约束

**同一版本走完整交付。** 图表增删、排序或主图改变后，先核对出版稿和编辑清单的实际图 ID、顺序与角色，再做确定性重建。以同一份成稿采集四视口图证，完成作者图审并核对发布目录。共用渲染器改动时，由目录和实际图语法发现受影响的网页，包含可展开核对层及按原件构建的旧报告。用 Playbook 09 的顺序消除过期证明和重复返工。

新增公司或期间不得继承历史固定数量（原 11 家）的视觉认证：发布目录以当前 site/research_catalog.json 的动态集合为唯一分母。区分已具备全部当前源图证据的 FULL_SOURCE_FIGURES_V1、旧 HTML SHA 不变的冻结证据和来源限定的新编稿。第三类必须重新验证本期原件/账本、研究反证、当前完整 HTML SHA、全部图形的三档 Chromium 与 WebKit 手机读图/导出；证据不全则阻断发布，不能降级质量检查以追求 CI 绿灯。

所有新公司/新期间的分析测试与浏览器门禁必须在未启用 Python -O 优化的解释器中运行，保证原始 assert 有效。全库迁移比例、通用解析覆盖、独立研究审稿和独立艺术总监复核应分别记录 PASS / FAIL / NOT_CHECKED，不得把任何已知样本的机器 PASS 外推为未知行业全覆盖。

### 新公司全篇报告的同级研究完整度门禁（防止「技术通过、作品缩水」）

在首份新公司完整年度/半年度原报具备充分来源事实时，**不允许仅凭浏览器能打开、会计勾稽闭合、4张图无重叠，就把初级摘要冒充与正式目录同级的完整研究**。在发布前独立检查 `research-brief.json` 的可证伪判断与替代解释、`publication.json` 的经营经济性/利润形成/利润质量/现金转换/资本结构/持续性风险是否围绕公司独有事实展开。逐项对照现有目录真实长文，不得按固定数量机械凑图；但若源事实已支持某一重要分析问题，却没有合适图种或研究结论，必须说明有页码和源键的证据不足/遗漏原因，否则阻止升级为同级正式交付。**`source_limited_preview` 只说明披露来源仍有边界，不能为明显缺失的现成、可证明研究维度开豁免。**

P6 除真实 Chromium/WebKit 原生截图与金额守恒外，必须交付可追溯的作者 **R1–R5/V1–V6** 逐项评分（`playbooks/05_QUALITY_RUBRIC.md`）：每项≥2，平均≥2.5，无任何P0，说明被拒绝的候选图、未核重大附注与为什么不能做量价/季度趋势。评分绑定本次完整HTML SHA、原始PDF SHA及各视口截图证据。**作者自评可记 `VISUAL_EDITORIAL_SELF=PASS`，独立人类财经/艺术二审仍保持 `INDEPENDENT_HUMAN_REVIEW=NOT_CHECKED`，两者永不混用。** 新报告当前SHA没有这些证据，就应保持草稿，不准因为其他公司CI为绿而合并。

本文件是**唯一的执行合同**：怎么做、做到什么程度、什么必须拒绝。它不记录项目进度。当前发布状态、公司清单与证据只看 `project-status.json`、`site/research_catalog.json` 和各发行人 `research/issuers/<code>/release-gates.json`；历史 PR35 来源见 `docs/ACTIVE_PR35_HANDOFF.md`（只是历史证据，不是当前部署依据）。v8.8 与 v9.1 的长版说明分别归档在 `docs/history/ASHARE_FINANCIAL_STORYTELLING_SKILL_V8_8_ARCHIVE.md` 与 `docs/history/ASHARE_FINANCIAL_STORYTELLING_SKILL_V9_1_ARCHIVE.md`，其中的公司特例仍适用于对应旧出版器，但不授权任何新发布。

## 新会话的主编职责

每份新稿先读 [研究与主编决策](playbooks/08_EDITORIAL_DECISIONS.md)。让核心问题决定源表、主图和证据顺序。完成验收时同时交付成稿、实际桌面与手机图证和未解决的研究边界。复验既有作者稿和空白会话首次编稿分别报告。

## 单份 PDF 的启动入口

```bash
T=skills/ashare-financial-storytelling/tools
python "$T/start_report.py" /absolute/path/filing.pdf
```

打开能力计划，按 Playbook 07 的离线流程完成原页复核、研究简报、图序和验收。独立成稿支持合并工业报表和具备核心源格的银行报表。需要识别无法自动确认的封面时，从原页读取代码或全称并传入 `--code` 或 `--name`。金融行业仍需专门分析，保险、券商和地产保留现有适配边界。既有目录报告继续使用其发布合同。

## 0. 交付目标与质量线

每份报告是一篇**独立、可离线打开的中文财经研究长文**，同时满足三条互不替代的标准：

| 轴 | 顶级交付的含义 | 一票否决（P0） |
|---|---|---|
| FINANCIAL_SOURCE | 原始完整PDF字节+SHA；每个数字有物理页、行、列、原符号；Decimal 原始元逐元勾稽 | 错列/错期/母公司冒充合并；空白当0；虚构平衡项；数字手打未溯源 |
| ANALYTICAL_DEPTH | 公司特有、可证伪的核心判断；量化驱动式；最强替代解释；下一次披露的证伪条件；利润质量与现金约束 | 把会计差额说成因果；把管理层说法当事实；无反证；8–12季/同行/估值无数据却出图 |
| VISUAL_EDITORIAL | 问题驱动的图序；每图5秒可读出结论；合法图形语法；金额几何真实；桌面与手机各自原生构图 | 负数画成正向流；存量画成流量；手机横滑或隐藏图；文字裁切重叠；彩虹装饰无结论 |

自动化全部 PASS 只证明**被测范围**。真实独立人类财务/视觉二审未发生就写 `NOT_CHECKED`；不得自称"超越 AEI"或"机构认证"。

## 1. 必读与分层加载（按需，不要一次读完所有历史）

**每次任务先读：** 本文件 → `project-status.json`（当前状态）→ `site/research_catalog.json`（公司清单）→ 与任务相关的 playbook。

| 场景 | 必读 |
|---|---|
| 新公司 / 新报告期 / 新行业 | `playbooks/06_GENERALIZATION.md` + `playbooks/07_EVIDENCE_TO_EDITORIAL.md`（先编译能力再设计研究问题和合法图种）、`playbooks/01_REPORT_TYPES.md`、`playbooks/02_ANALYSIS_FRAMEWORK.md`、`playbooks/03_EXHIBIT_SYSTEM.md`、`playbooks/04_PRODUCTION_RUNBOOK.md`、`playbooks/05_QUALITY_RUBRIC.md` |
| 只改图形/版式 | `playbooks/03_EXHIBIT_SYSTEM.md`、`docs/UNIFIED_FINANCIALS_VISUAL_STANDARD.md`、`docs/PROFIT_CHAIN_EDITORIAL_STANDARD.md` |
| 银行/保险/券商/地产 | `playbooks/02_ANALYSIS_FRAMEWORK.md` 第5节 + `research/05_CROSS_SECTOR_GENERALIZATION.md` |
| 发布/验收 | `docs/REPORT_RELEASE_CHECKLIST.md`、`docs/HANDOFF_PROTOCOL.md`、`playbooks/05_QUALITY_RUBRIC.md` |
| 改进本技能 | `docs/SKILL_EVOLUTION_PROTOCOL.md`、`quality-regressions.json` |

五份背景手册保存一手来源与推理依据，遇到判断争议时查阅：`research/01_APP_ECONOMY_INSIGHTS_RESEARCH.md`（AEI 一手方法）、`research/02_ASHARE_INSTITUTIONAL_RESEARCH.md`（机构研究结构）、`research/03_VISUAL_EDITORIAL_SYSTEM.md`（22种关系→图形）、`research/04_ASHARE_FORENSIC_DEEP_DIVE.md`（20阶段取证）、`research/05_CROSS_SECTOR_GENERALIZATION.md`（跨行业适配）。若与本文件冲突，以本文件和 playbooks 为准。

## 2. 七阶段工作流（每阶段有产出物和退出条件）

| 阶段 | 产出物 | 退出条件 |
|---|---|---|
| P1 来源 | `source/…complete_original.pdf`、`extracted/pNNN.txt`、骨架账本 | 完整报告（非摘要/英文版）；封面年份+报告类型；全称+证券代码页；SHA、物理页数 |
| P2 账本 | `source-ledger.json` 事实 | 三表由 `fin_intake.py auto` 自动抽取为标准键（任意公司、四种报表格式），恒等式两期全部闭合；附注事实用 `facts` 规格；每个事实有 bbox 源格 |
| P3 研究 | `analyst-memo.md` + `research-brief.json`（见 `templates/research-brief.template.json`） | 先写公司特有的主要假说；每一论点绑定源事实与精确 Decimal 算式、最强替代解释、区分证据、下一披露的证伪条件。`research_evidence.py` 必须校验后才能 `v2_builder.apply`；独立人工财经判断仍 `NOT_CHECKED` |
| P4 图序 | `publication.json` figures + 编辑清单 `research/editorial-20261113/<code>.json` | 每图一个问题、一句答案、一个反证；图种由关系决定（§4）；故事顺序先于图数 |
| P5 出版 | `public/<code>.html`、`figure-briefs.json`、`qa.json` | 共享出版器生成；无公司专用绘图代码；干净重建逐字节一致 |
| P6 验收 | 截图、矢量审计、`release-gates.json` | §6 全部适用门槛有证据；逐图截图自评（rubric）无 P0 |
| P7 交接 | 目录条目、首页、状态文件、PR | 合并后对生产全文件字节、导航、下载复验；未做的写 NOT_CHECKED |

效率原则：P1–P2 用 `fin_intake.py init → auto --write`，三张表**不写任何公司规格**；只有附注（分部、地区、补充资料）用 `find / scan / facts`。出现残差或未映射行时，按 `playbooks/06_GENERALIZATION.md` §2 处理：加通用同义词并补回归测试，不写公司补丁；**未映射金额行必须先分类与核实重大性，不能由恒等式闭合推定全量覆盖**。P3 核实研究判断，P4 决定图形，P6 打开最终实图独立审视阅读质量；P5–P6 用现有共享出版器与审计器，不另写。

**目录报告的 P4 标准做法（EDITORIAL_V2）**：`T2=skills/ashare-financial-storytelling/tools/v2_builder.py`
0. **先检查** `python $T2 capabilities --code <c> [--period P]`：类型化事实、同比/余额期间、行业路由、候选图种和欠缺的研究证据逐项列出。新金融/地产出版器未实现时拒绝通用工业出版；`scaffold --source-probe` 只作原件技术诊断，永远不能直接发布。详细见 Playbook 07。
1. `python $T2 numbers --code <c> [--period P]`：打印每行同比、占收入比例、分部/地区增速与毛利率、营运资本余额变动。**叙事只按这里的方向写**。
2. `python $T2 scaffold …`：生成经过能力筛选的 `v2-draft.json`；只有证据足够的图才保留候选，原因写入 `omitted_for_evidence`。分析师先完成 `research-brief.json`，再根据核心问题筛选图形与图序。
3. 只写文字：结论、趋势、重点、反证、章节、本期一览。数字一律写宏：`[g:rev]` 同比、`[r:gm]` 比率、`[p:gm]` 百分点变化、`[y:parent_net]` 亿元、`[d:ar]` 余额变动。正文签名桥 ≤2，其余在 `roles` 设为 reference；与新图重复的两期表放进 `remove`。
4. **研究证据门禁：** `python skills/ashare-financial-storytelling/tools/research_evidence.py --code <c> [--period P]` 校验独立于绘图的源事实、精确算式、反解释和下一期证伪；这是**机器证据合同**，并非独立人类审稿。`python $T2 apply …` 在写 `publication.json` 前强制验证 `research-brief.json`；同时拒绝 TODO、手写金额、未知宏或错期，跑编辑 lint，同步编辑清单。
5. 出版 → 目录 `figures` 改为 `qa.json` 的图数 → 浏览器验收（§6）。

## 3. 研究必须先于画图

对每份报告写出五个与源事实 ID 绑定的决策项：

1. **核心判断**：这家公司本期最重要的经济事实是什么（一句话、可被下一期数据推翻），不是"收入增长X%"。
2. **量化驱动式**：例如 Δ归母 = Δ毛利 − Δ期间费用 ± Δ财务/投资/减值 − Δ税 − Δ少数；区分 DISCLOSED / MANAGEMENT / DERIVED / HYPOTHESIS / UNKNOWN。
3. **最强替代解释**：同一组数字的另一种成因，以及能区分两者的具体证据（页码）。
4. **持续性与约束**：利润质量（扣非、公允价值、补贴、减值）、现金转换（CFO/净利、营运资本）、再投资（现金资本开支、负债、分红）。
5. **未验证项**：缺失的8–12季、同行、量价、估值、管理层指引；不能伪造，写 NOT_CHECKED。

数字叙述一律用 `quantified_claims` 占位符从源表达式生成（含比率分母与单位倍数）；正文不得手打舍入数。新发布的 `research-brief.json` 按 `financials.research_evidence.v1` 写每个核心假说的逐元表达式、源事实ID与日期，要求最强替代解释、区分证据和明确的下一期证伪；`research_evidence.py` 只有机器源数学签证权，不得把它写成已证明行业因果或完成独立分析师审稿。归因前先比较每项毛利变化，不能把"增长最快的业务"默认成"利润改善的来源"。会计差额归因不是价格/销量/结构因果，必须在图下写明。

## 4. 图形语法：关系决定图形，会计决定合法性

**收入/利润流向的合法性（先分类再画形状）**：完整源字节+物理页 → Decimal 原始元事实 → 互斥性/期间/合并口径/符号 → 流向类型。共享类型合同在 `research/shared/editorial_financial_flow.py`。

- **TYPE A**（逐业务收入+各自披露成本）：来源 → **一个**收入合计节点 → 各自成本/毛利 → 合计成本/毛利。逐业务毛利真实。生成器 `research/shared/source_income_adapter.py` → `research/shared/unified_income_sankey.py`。
- **TYPE A 桑基的不可交叉端口规范**：共享总收入节点的左侧按来源排列；右侧**先按去向（成本、毛利）成组，再在每组内维持来源顺序**。严禁按“来源 A 成本→来源 A 毛利→来源 B 成本→来源 B 毛利”交错出线导致红绿流带交叉；即使金额、节点和带宽全部守恒，也必须判作视觉结构 FAIL。每张图保留统一线性金额比例、真实极细流带及源值标签，不准用假最低线宽掩饰小额来源。以 `test_income_generalization.py` 的真实六公司双端无交叉测试和浏览器实图共同验收。
- **TYPE B**（互斥收入+仅集团成本）：来源 → 合计 → 集团成本/毛利；图中直写"无法倒推分部毛利"。只有真实缺成本时使用。
- **BANK**：净利息收入（已扣利息支出）+净手续费+其他净收入 → 营业收入 → 业务管理费/信用减值/营业利润；不称"毛利"，不重复扣利息。
- **保险**：管理层保费、CAS25 保险服务收入、保费收现、CSM 存量四者不互接；保费构成可用专用 4→2→1 图，法定利润用签名桥。
- **TYPE C / 不合法**：分类重叠、负业务毛利、存量与流量混合、不同单位/期间 → 不画正向桑基，记录 `FINANCIAL_SANKEY_OMITTED_WITH_SOURCE_REASON`，改用有符号瀑布、真比例对比或两时点存量。
- **完整利润主线**：工业合并利润表披露齐全、金额为合法正向流且逐层闭合时，第一张财务主图必须从营业收入贯通至归母净利润。营业成本、费用和减值、营业外与税项、少数股东归属均逐项取原始披露。税前与合并净利润要可直接读出，并保存完整复算。结束在成本和毛利的图只承担产品或地区经济性专题。单 PDF 走 `dossier_profit_chain.py` 与 `INCOME_FLOW_V3`；若亏损、源表缺项或口径使正向流不成立，保留完整签名利润桥并写出原因。规则见 `docs/PROFIT_CHAIN_EDITORIAL_STANDARD.md`。

**其他关系的图种**（共享出版器 `research/shared/source_publication.py` 的 family）：

| 研究问题 | family | 关键约束 |
|---|---|---|
| 毛利如何变成归母？同比为何变化？净利为何未变成现金？期初现金如何到期末？ | `signed_bridge` | 全部原始项目逐项出现一次；可用 `editorial_groups` 合并显示但保留展开对账；零轴可见 |
| 两期利润、扣非、现金是否同向？存量年初→期末如何变？ | `comparison` | 流量写 2026H1 vs 2025H1；存量写 2026-06-30 vs 2025-12-31，不称"同比" |
| 资产=负债+权益 | `balance` | 两个日期同一比例尺；不是现金流向 |
| 存货/收入地区/成本构成 | `components` | 各部分闭合至总额；父子层级不相加 |
| 业务毛利 | `income` | 仅 TYPE A；季报通常无分部，省略该图 |

| 这一期最重要的六个数字？ | `kpi_board` | EDITORIAL_V2 第一张图；每格写清对比口径（同比/较年初） |
| 单季在加速还是放缓？ | `period_columns` | 单季=同一会计年度累计差；跨年同比用 `YOY_OF_SAME_FISCAL_YEAR_DIFFERENCES` |
| 利润表哪一行增长最快？ | `growth_bars` | 同一零轴；上期为负或零不计算 |
| 利润率扩张来自哪里？ | `ratio_dumbbell` | 上期空心点、本期实心点，标 pp 变化 |
| 增长把资金沉淀在哪里？ | `stock_delta` | 资产增加=占用（红），负债增加=提供（绿） |

损益主图默认用 AEI 语法的 `INCOME_FLOW_V3`（`playbooks/03_EXHIBIT_SYSTEM.md` §0、§3）。尚未实现的图种（TYPE B/BANK 在新出版器中的路由、多年分部趋势）见同一 playbook；缺口未实现时**省略并说明**，不得用别的图冒充，也不得在公司出版器里临时手画。

**统一视觉 token**（`docs/UNIFIED_FINANCIALS_VISUAL_STANDARD.md`）：收入源灰蓝 `#9CABB2`、合计深蓝灰 `#263F47`、费用低饱和红 `#CD7271`、利润深绿 `#239878`、背景 `#F8F7F2`、正文 `#19333C`。颜色表达会计角色，不做装饰；符号与文字同时表达正负。

## 5. 版式与阅读层级（AEI 方法的 A 股化）

文章两种阅读速度：**90秒**（标题判断 + 3个指标 + 完整利润主图 + 一个最大矛盾 + 反证）与**20分钟**（逐章图文、重大附注、完整对账、原页链接）。以下顺序用于既有完整利润主线版。单 PDF 新稿按 Playbook 08 决定首屏、图序及阅读层次。

1. 标题 = 一个可被回答的问题；导语给出答案方向；3个首屏指标（含同比或口径）。
2. 核心判断卡（thesis）。
3. 完整利润主线（主图）。原件允许时，单 PDF 新稿以完整损益流向作主图。前置的关键数字可用简短文字或指标摘要，也可另设 KPI 专题。既有 EDITORIAL_V2 样式允许 KPI 看板先呈现，完整利润仍必须有自己的主图角色。之后按增长、盈利、现金与资本等重要问题组织。
4. 同比变化桥：为何利润与收入增速不同。
5. 利润质量：扣非 vs 归母 vs 合并 vs CFO。
6. 现金：净利→CFO 全部间接调节（季报无补充资料时用直接法主要收支），期初→期末现金。
7. 资本占用：应收/存货/应付两时点，存货结构，客户集中（注明分母是应收还是收入）。
8. 资产负债与融资约束。
9. 研究判断长文：商业机制、驱动式、最强替代解释、反向证据、下一次披露的三组检验。
10. 重大附注表（≥6个主题：收入确认、应收、存货、CFO、债务/现金受限、非经常损益；年报加审计意见与关键审计事项）。
11. 完整核对区：所有原图与逐项对账默认折叠、锚点可展开、可导出当前可见 SVG。

每图必须有：问题式标题（≤28字）、一句话答案（≤90字）、读图结论、反证与边界、恒等式、来源页、单位/期间/口径、原始数据表。机器标记只放 DOM 属性，不露在中文正文。

## 6. 验收门槛（对**当前字节**执行，不继承昨天的结果）

本地必跑：
- **新建 / 重编 EDITORIAL_V2：** `python skills/ashare-financial-storytelling/tools/fin_intake.py preflight --code <code> --require-research-evidence`（原件、恒等式、按当前账本重新判定合法图种、独立研究证据稿与 SHA、编辑 lint）。缺失 `research-brief.json` 或篡改旧证据回执时必须失败；未重编的历史发布稿仅可记 `NOT_CHECKED_LEGACY`，不能据此宣称已满足新的研究证据门禁。
- `python -m unittest discover -s skills/ashare-financial-storytelling/tools -p 'test_*.py'`
- `python -m unittest discover -s research/shared -p 'test_*.py'`（需要 CI 下载的历史 PDF 的用例在本地缺件时会报 FileNotFoundError，属环境缺件，须在 CI 结果中核对）
- `python research/shared/source_publication.py research/issuers/<code> /tmp/<code>.html && cmp /tmp/<code>.html public/<code>.html`
- `python scripts/check_handoff.py`、`python scripts/check_release_contract.py`、`python scripts/check_pr35_quality_handoff.py`
- 浏览器：`python scripts/qa_editorial_migration.py --codes <code> --out <dir>`（1440/768/390 每图可见、无裁切/重叠/小于10px金额字、当前可见 SVG 真实下载），WebKit 375 复验；中文字体必须是真实 Noto CJK，出现豆腐块的截图不能作视觉证据。
- **合并前 WebKit**：WebKit 的中文字宽大于 Chromium，本地 Chromium 通过不代表手机 Safari 通过。PR 的 Cloudflare 预览出来后运行 `gh workflow run verify-preview-webkit.yml -f origin=<预览地址>`，对目录中全部报告做 375 宽验收，通过后再合并。
- **合并后**：生产锁定工作流通过后运行 `python scripts/promote_live_receipts.py --run <run id>`，自动归档回执、移除候选、把 CLOUDFLARE_LIVE 改为 PASS。字节不符就拒绝晋升。
- 候选改变图数时，在 `unmerged_candidate.base_figure_count` 写已部署的图数，生产回执按已部署字节核对。

CI 会对目录中声明 `source_publication` 的公司自动干净重建并跑全部图的双浏览器验收；合并后对生产站同一主分支复验全文件字节、导航与下载。门槛状态逐项写入 `release-gates.json`：`PASS / FAIL / NOT_CHECKED`，不得平均掉 P0。

**逐图自评（不可省）**：打开每张图在 1440 与 390 的真实截图，按 `playbooks/05_QUALITY_RUBRIC.md` 打分并写入发布说明。只看 JS 无报错和无横向溢出不算视觉审查。

## 7. 永久拒绝清单（来自真实错误的回归）

- 封面年份对但报告类型不对（半年报改元数据冒充年报）；摘要版冒充全文。
- 比较期列与本期列错位；空白单元格当披露零；母公司表冒充合并表；正数匹配到负数子串。
- 上年同期期末现金 ≠ 本年年初现金；6月30日存量与12月31日存量称"同比"；把应收较年初变动率与收入同比增长率直接排序，或把存货增减当作备货/去库存因果结论。
- 产品"其他"与"其他业务"两个维度相加；创新药子集与药品销售相加；地区与产品叠加。
- 前五大**应收**占比写成客户**收入**集中度。
- 发电量当售电量；保费当保险服务收入；财务公司存款现金当工业经营现金。
- 用集团毛利率推算产品毛利；负毛利画正向流；0元画最小线宽。
- 会计差额归因写成价格/销量/汇率因果；管理层解释写成事实；同比比较期为零或负数却输出常规同比增长率；图文显示为 `0.00` 却写“增长/下降”；利润、现金含量实际持平却编造方向；财务费用归零冒充正负翻转。
- 只有一份报告却画 8–12 季趋势、估值区间或同行对比。
- 公司专用 SVG 几何、850px 手机横滑、手机隐藏非主图、正文手打数字。
- 旧截图/旧 Action 证明新字节；部署成功即称生产已验证。

完整可执行回归在 `skills/ashare-financial-storytelling/quality-regressions.json`；运行 `python scripts/check_release_contract.py`。

## 8. 跨期、跨公司稳定性的边界

- 新期间：从原报告读取 `fiscal_period`（Q1/H1/9M/FY），单季列按真实 `issuer.flow_columns` 声明；不得借用旧期图证。历史 PDF-only 泛化探针记录 30 份（包含 Q1/H1/9M/FY），其中 20 份由公开披露按 SHA 恢复，30 份全部可复跑；恢复命令和历次状态见 `docs/UNMAPPED_COVERAGE_PROTOCOL.md`。完整出版/人类审稿分别标 `NOT_CHECKED`。
- 同一公司的后续期间登记在目录 `period_reports`，以 `code@period` 解析，旧路由与旧字节不变（playbook 01 §5）。
- 新行业：先运行 `v2_builder.py capabilities`（`tools/research_capabilities.py`），从报告本身的财务事实和行业口径判能力。只有工业已有通用 EDITORIAL_V2 作者路由；银行、保险、证券、地产在新出版器适配、对抗测试前仍为 `SECTOR_ADAPTER_OR_EVIDENCE_REQUIRED`，不可套工业模板（Playbook 02 §5、Playbook 07）。
- 能力分级：L0 仅描述；L1 一家真实原件通过；L2 同类两家真实原件+完整三表/附注+浏览器；L3 跨行业对抗回归+独立编辑+部署验证。只宣称实际达到的级别。合成样例只测机制，不证明未见真实财报的理解能力。

## 9. 交接与技能进化

任务结束前：更新 `project-status.json` 与 `PROJECT_STATE.md` 顶部（只写事实与证据链接）、发行人 `release-gates.json`、PR 与 Actions 链接；运行 `python scripts/check_handoff.py`。每次用户纠错或发现的缺陷：改源头 → 加可执行回归（`quality-regressions.json` 或单测）→ 改本技能对应条目 → 记录交接。**本文件只收录可复用规则；公司个案写进该公司的 README 或 release-gates，不写进本文件。**

历史边界保持公开：300308 原 p139 的 1 元列冲突、688220 镜像与交易所原件逐字节等价 NOT_CHECKED、保险管理层保费 ≠ CAS25 服务收入、七家历史出版器的旧状态记录（`HERO_SANKEY_UNIFIED_OTHER_FIGURES_LEGACY` 仅指 2026-11-08 快照，当前以全图收据为准）。
