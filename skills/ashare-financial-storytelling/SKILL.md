---
name: ashare-financial-storytelling
description: Deep, source-true research and AEI-grade editorial visualisation of any A-share listed company's periodic report (Q1 季报, H1 半年报, 9M 三季报, FY 年报). Use for reading and reconciling original PDFs, building typed source ledgers, writing a falsifiable analyst thesis, choosing lawful financial exhibits (income Sankey, full profit chain, signed bridges, cash, balance, working capital, trends), publishing standalone offline HTML into the Financials in Visuals library, running release gates, and improving this Skill. Also triggers for kobolibra/financials continuation across sessions.
---

# A股财报深度研究与可视化 · 统一生产技能

Contract version: 10.0.0

本文件是**唯一的执行合同**：怎么做、做到什么程度、什么必须拒绝。它不记录项目进度。当前发布状态、公司清单与证据只看 `project-status.json`、`site/research_catalog.json` 和各发行人 `research/issuers/<code>/release-gates.json`；历史 PR35 来源见 `docs/ACTIVE_PR35_HANDOFF.md`（只是历史证据，不是当前部署依据）。v8.8 与 v9.1 的长版说明分别归档在 `docs/history/ASHARE_FINANCIAL_STORYTELLING_SKILL_V8_8_ARCHIVE.md` 与 `docs/history/ASHARE_FINANCIAL_STORYTELLING_SKILL_V9_1_ARCHIVE.md`，其中的公司特例仍适用于对应旧出版器，但不授权任何新发布。

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
| 新公司 / 新报告期 | `playbooks/01_REPORT_TYPES.md`、`playbooks/02_ANALYSIS_FRAMEWORK.md`、`playbooks/03_EXHIBIT_SYSTEM.md`、`playbooks/04_PRODUCTION_RUNBOOK.md`、`playbooks/05_QUALITY_RUBRIC.md` |
| 只改图形/版式 | `playbooks/03_EXHIBIT_SYSTEM.md`、`docs/UNIFIED_FINANCIALS_VISUAL_STANDARD.md`、`docs/PROFIT_CHAIN_EDITORIAL_STANDARD.md` |
| 银行/保险/券商/地产 | `playbooks/02_ANALYSIS_FRAMEWORK.md` 第5节 + `research/05_CROSS_SECTOR_GENERALIZATION.md` |
| 发布/验收 | `docs/REPORT_RELEASE_CHECKLIST.md`、`docs/HANDOFF_PROTOCOL.md`、`playbooks/05_QUALITY_RUBRIC.md` |
| 改进本技能 | `docs/SKILL_EVOLUTION_PROTOCOL.md`、`quality-regressions.json` |

五份背景手册保存一手来源与推理依据，遇到判断争议时查阅：`research/01_APP_ECONOMY_INSIGHTS_RESEARCH.md`（AEI 一手方法）、`research/02_ASHARE_INSTITUTIONAL_RESEARCH.md`（机构研究结构）、`research/03_VISUAL_EDITORIAL_SYSTEM.md`（22种关系→图形）、`research/04_ASHARE_FORENSIC_DEEP_DIVE.md`（20阶段取证）、`research/05_CROSS_SECTOR_GENERALIZATION.md`（跨行业适配）。若与本文件冲突，以本文件和 playbooks 为准。

## 2. 七阶段工作流（每阶段有产出物和退出条件）

| 阶段 | 产出物 | 退出条件 |
|---|---|---|
| P1 来源 | `source/…complete_original.pdf`、`extracted/pNNN.txt`、骨架账本 | 完整报告（非摘要/英文版）；封面年份+报告类型；全称+证券代码页；SHA、物理页数 |
| P2 账本 | `source-ledger.json` 事实 | 三表本期+比较期全行；每个事实有 bbox 源格；`fin_intake.py preflight` 的会计恒等式全部闭合 |
| P3 研究 | `analyst-memo.md`（模板见 `templates/`） | 核心判断、驱动式、最强替代解释、证伪条件、利润质量、现金/资本约束、NOT_CHECKED 清单全部写完，**在画图之前** |
| P4 图序 | `publication.json` figures + 编辑清单 `research/editorial-20261113/<code>.json` | 每图一个问题、一句答案、一个反证；图种由关系决定（§4）；故事顺序先于图数 |
| P5 出版 | `public/<code>.html`、`figure-briefs.json`、`qa.json` | 共享出版器生成；无公司专用绘图代码；干净重建逐字节一致 |
| P6 验收 | 截图、矢量审计、`release-gates.json` | §6 全部适用门槛有证据；逐图截图自评（rubric）无 P0 |
| P7 交接 | 目录条目、首页、状态文件、PR | 合并后对生产全文件字节、导航、下载复验；未做的写 NOT_CHECKED |

效率原则：P1–P2 用 `skills/ashare-financial-storytelling/tools/fin_intake.py` 的 `init / find / scan / facts / preflight`，不手抄坐标；P3 是唯一不能省的人工判断环节；P5–P6 用现有共享出版器与审计器，不另写。

## 3. 研究必须先于画图

对每份报告写出五个与源事实 ID 绑定的决策项：

1. **核心判断**：这家公司本期最重要的经济事实是什么（一句话、可被下一期数据推翻），不是"收入增长X%"。
2. **量化驱动式**：例如 Δ归母 = Δ毛利 − Δ期间费用 ± Δ财务/投资/减值 − Δ税 − Δ少数；区分 DISCLOSED / MANAGEMENT / DERIVED / HYPOTHESIS / UNKNOWN。
3. **最强替代解释**：同一组数字的另一种成因，以及能区分两者的具体证据（页码）。
4. **持续性与约束**：利润质量（扣非、公允价值、补贴、减值）、现金转换（CFO/净利、营运资本）、再投资（现金资本开支、负债、分红）。
5. **未验证项**：缺失的8–12季、同行、量价、估值、管理层指引；不能伪造，写 NOT_CHECKED。

数字叙述一律用 `quantified_claims` 占位符从源表达式生成（含比率分母与单位倍数）；正文不得手打舍入数。归因前先比较每项毛利变化，不能把"增长最快的业务"默认成"利润改善的来源"。会计差额归因不是价格/销量/结构因果，必须在图下写明。

## 4. 图形语法：关系决定图形，会计决定合法性

**收入/利润流向的合法性（先分类再画形状）**：完整源字节+物理页 → Decimal 原始元事实 → 互斥性/期间/合并口径/符号 → 流向类型。共享类型合同在 `research/shared/editorial_financial_flow.py`。

- **TYPE A**（逐业务收入+各自披露成本）：来源 → **一个**收入合计节点 → 各自成本/毛利 → 合计成本/毛利。逐业务毛利真实。生成器 `research/shared/source_income_adapter.py` → `research/shared/unified_income_sankey.py`。
- **TYPE B**（互斥收入+仅集团成本）：来源 → 合计 → 集团成本/毛利；图中直写"无法倒推分部毛利"。只有真实缺成本时使用。
- **BANK**：净利息收入（已扣利息支出）+净手续费+其他净收入 → 营业收入 → 业务管理费/信用减值/营业利润；不称"毛利"，不重复扣利息。
- **保险**：管理层保费、CAS25 保险服务收入、保费收现、CSM 存量四者不互接；保费构成可用专用 4→2→1 图，法定利润用签名桥。
- **TYPE C / 不合法**：分类重叠、负业务毛利、存量与流量混合、不同单位/期间 → 不画正向桑基，记录 `FINANCIAL_SANKEY_OMITTED_WITH_SOURCE_REASON`，改用有符号瀑布、真比例对比或两时点存量。
- **完整利润主线**（默认主图）：同口径合法时从法定收入贯通到归母净利，`unified_income_sankey.py.render_full_profit_chain` 调用 `full_profit_chain.py`；原披露小计保持原值，收益以流入汇合，少数亏损以归属调整流入表达。规则见 `docs/PROFIT_CHAIN_EDITORIAL_STANDARD.md`。

**其他关系的图种**（共享出版器 `research/shared/source_publication.py` 的 family）：

| 研究问题 | family | 关键约束 |
|---|---|---|
| 毛利如何变成归母？同比为何变化？净利为何未变成现金？期初现金如何到期末？ | `signed_bridge` | 全部原始项目逐项出现一次；可用 `editorial_groups` 合并显示但保留展开对账；零轴可见 |
| 两期利润、扣非、现金是否同向？存量年初→期末如何变？ | `comparison` | 流量写 2026H1 vs 2025H1；存量写 2026-06-30 vs 2025-12-31，不称"同比" |
| 资产=负债+权益 | `balance` | 两个日期同一比例尺；不是现金流向 |
| 存货/收入地区/成本构成 | `components` | 各部分闭合至总额；父子层级不相加 |
| 业务毛利 | `income` | 仅 TYPE A；季报通常无分部，省略该图 |

需要但尚未实现的图种（8–12季趋势条、利润率走势、TYPE B/BANK 在新出版器中的路由、KPI 记分板）见 `playbooks/03_EXHIBIT_SYSTEM.md` 的"能力缺口"；缺口未实现时**省略并说明**，不得用别的图冒充，也不得在公司出版器里临时手画。

**统一视觉 token**（`docs/UNIFIED_FINANCIALS_VISUAL_STANDARD.md`）：收入源灰蓝 `#9CABB2`、合计深蓝灰 `#263F47`、费用低饱和红 `#CD7271`、利润深绿 `#239878`、背景 `#F8F7F2`、正文 `#19333C`。颜色表达会计角色，不做装饰；符号与文字同时表达正负。

## 5. 版式与阅读层级（AEI 方法的 A 股化）

文章两种阅读速度：**90秒**（标题判断 + 3个指标 + 完整利润主图 + 一个最大矛盾 + 反证）与**20分钟**（逐章图文、重大附注、完整对账、原页链接）。默认顺序：

1. 标题 = 一个可被回答的问题；导语给出答案方向；3个首屏指标（含同比或口径）。
2. 核心判断卡（thesis）。
3. 完整利润主线（主图）＋本期营业层主要金额构成（不是同比贡献）。
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
- `python skills/ashare-financial-storytelling/tools/fin_intake.py preflight --code <code>`（源格、恒等式、编辑 lint）
- `python -m unittest discover -s skills/ashare-financial-storytelling/tools -p 'test_*.py'`
- `python -m unittest discover -s research/shared -p 'test_*.py'`（需要 CI 下载的历史 PDF 的用例在本地缺件时会报 FileNotFoundError，属环境缺件，须在 CI 结果中核对）
- `python research/shared/source_publication.py research/issuers/<code> /tmp/<code>.html && cmp /tmp/<code>.html public/<code>.html`
- `python scripts/check_handoff.py`、`python scripts/check_release_contract.py`、`python scripts/check_pr35_quality_handoff.py`
- 浏览器：`python scripts/qa_editorial_migration.py --codes <code> --out <dir>`（1440/768/390 每图可见、无裁切/重叠/小于10px金额字、当前可见 SVG 真实下载），WebKit 375 复验；中文字体必须是真实 Noto CJK，出现豆腐块的截图不能作视觉证据。

CI 会对目录中声明 `source_publication` 的公司自动干净重建并跑全部图的双浏览器验收；合并后对生产站同一主分支复验全文件字节、导航与下载。门槛状态逐项写入 `release-gates.json`：`PASS / FAIL / NOT_CHECKED`，不得平均掉 P0。

**逐图自评（不可省）**：打开每张图在 1440 与 390 的真实截图，按 `playbooks/05_QUALITY_RUBRIC.md` 打分并写入发布说明。只看 JS 无报错和无横向溢出不算视觉审查。

## 7. 永久拒绝清单（来自真实错误的回归）

- 封面年份对但报告类型不对（半年报改元数据冒充年报）；摘要版冒充全文。
- 比较期列与本期列错位；空白单元格当披露零；母公司表冒充合并表；正数匹配到负数子串。
- 上年同期期末现金 ≠ 本年年初现金；6月30日存量与12月31日存量称"同比"。
- 产品"其他"与"其他业务"两个维度相加；创新药子集与药品销售相加；地区与产品叠加。
- 前五大**应收**占比写成客户**收入**集中度。
- 发电量当售电量；保费当保险服务收入；财务公司存款现金当工业经营现金。
- 用集团毛利率推算产品毛利；负毛利画正向流；0元画最小线宽。
- 会计差额归因写成价格/销量/汇率因果；管理层解释写成事实。
- 只有一份报告却画 8–12 季趋势、估值区间或同行对比。
- 公司专用 SVG 几何、850px 手机横滑、手机隐藏非主图、正文手打数字。
- 旧截图/旧 Action 证明新字节；部署成功即称生产已验证。

完整可执行回归在 `skills/ashare-financial-storytelling/quality-regressions.json`；运行 `python scripts/check_release_contract.py`。

## 8. 跨期、跨公司稳定性的边界

- 新期间：出版器从原报告读取 `fiscal_period`（`2026Q1`、`2026H1`、`20269M`、`2026FY`），三季报的单季列通过 `issuer.flow_columns` 显式声明；不得借用旧期图证。已用真实原件跑通的期间：H1（14 家）与三季报（天孚通信 `20269M`）；Q1 与 FY 尚无真实样例，按 playbook 01 的差异处理并先小范围验证。
- 同一公司的后续期间登记在目录 `period_reports`，以 `code@period` 解析，旧路由与旧字节不变（playbook 01 §5）。
- 新行业：先判路由（`industrial_own_cost_income` 或专门适配器）；没有适配器的金融行业不能套工业出版器（详见 playbook 02 §5 的实现状态表）。
- 能力分级：L0 仅描述；L1 一家真实原件通过；L2 同类两家真实原件+完整三表/附注+浏览器；L3 跨行业对抗回归+独立编辑+部署验证。只宣称实际达到的级别。合成样例只测机制，不证明未见真实财报的理解能力。

## 9. 交接与技能进化

任务结束前：更新 `project-status.json` 与 `PROJECT_STATE.md` 顶部（只写事实与证据链接）、发行人 `release-gates.json`、PR 与 Actions 链接；运行 `python scripts/check_handoff.py`。每次用户纠错或发现的缺陷：改源头 → 加可执行回归（`quality-regressions.json` 或单测）→ 改本技能对应条目 → 记录交接。**本文件只收录可复用规则；公司个案写进该公司的 README 或 release-gates，不写进本文件。**

历史边界保持公开：300308 原 p139 的 1 元列冲突、688220 镜像与交易所原件逐字节等价 NOT_CHECKED、保险管理层保费 ≠ CAS25 服务收入、七家历史出版器的旧状态记录（`HERO_SANKEY_UNIFIED_OTHER_FIGURES_LEGACY` 仅指 2026-11-08 快照，当前以全图收据为准）。
