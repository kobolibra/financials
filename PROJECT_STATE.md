# Financials in Visuals — ACTIVE PROJECT STATE

**状态日期：2026-11-03。生产分支：`main`。现行入口：[START_HERE.md](START_HERE.md)。机器状态：[project-status.json](project-status.json)。**

> **唯一正式站点：首页统一八家公司研究库（本提交为候选，按当前 main 实际发布状态验收）。** <https://financials-in-visuals.pages.dev/>。不是四家公司 v9/v10 独立站点，更不是 `research-lab` 里的工程样本。

## 2026-11-03 · 翱捷科技源数据/AEI 风格重新审计与 v2 八图重构 · 真实 QA 检查点

**这次不是对先前页面技术 PASS 的重新包装**：经过重读当前 `main` 的完整现行 `skills/ashare-financial-storytelling/SKILL.md` 及五份研究手册、直接核对公开 AEI 收入和现金流示例、实际原报告与已打开的桌面/手机截图，发现并修正了重大“财务图形语义”和原始比较期列错误。

**旧版 Figure 01 失败实情**：四类收入先并成一个收入总流、再以集团层面分为成本/毛利，能闭合合并收入，但**不能证明哪类业务产生了哪类毛利**，未达到源业务级桑基要求。新 `research/shared/conserved_flow.py` 为不同发行人复用同一 exact-Decimal 业务收入 `source_i -> reported_cost_i / derived_gp_i` typed graph；本 688220 原报告 p.178 四项收入、四项成本各自分流，共八条原始金额带，四个 source / 两个 sink，消除伪可守恒汇总树；浏览器对实际 SVG Path 的 `data-business`/`data-to`/`data-yuan` 和 ribbon 宽度做精确公式测试。绝不推断跨轴、相同业务父子类、负毛利为正流或创造“未披露其他”。

**P&L 深度修复**：真实合并利润表 p.87 **2025H1 比较列 15.30 元营业外支出**曾在旧 ledger 被误读作 2026H1；直接改 `research/issuers/688220/source-ledger.json` 为 `nonoperating_expense_prior` 并标签 `period=2025H1`，增加从 2026H1 毛利→研发费用 663,322,721.74 元→其他经营费用→投资及公允价值→信用及资产减值→营业利润→营业外收入→所得税收益→净利润的全部带符号利润算式，原始元零差；新独立 Figure 04 为有证据的**九步 P&L 瀑布**，原扣非/法定盈利对比成为 Figure 05。每个项目及“分析师聚合”的性质在可展开的原始源表中说明；p.87 15.30 不再计入当期。

**原始 PDF 字节与行列**：原完整 224 物理页镜像 SHA-256 `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`、大小 1,449,510 字节不变。抽核的 **118 项源证据 PASS = 109 项连续 PDF 文本原金额 + 9 项真实 p.135/p.146 表格单元格重新按物理 bbox、行标题、列标题、日期拼接**；证据 `source-cells.json`、`source-verification.json`、`source-images/p135.png`、`p146.png`，不用 OCR 猜数。不是全部 224 页附注独立全文验收。上交所静态直链与镜像字节同一性继续 **NOT_CHECKED**。

**原创视觉/页面**：`research/issuers/688220/figure-briefs.json` 提供八张图全部源键/SHA/原始物理页/问题/语法/反证/手机政策，`publish.py` 不满足会拒绝发布。人眼打开实际 `flow_1440`、`pnl_1440`、`flow_390`、`pnl_390` 等截图，发现并修正旧版“汇总型伪业务桑基”、桌面右侧源汇金额被横滚遮掉、九步利润瀑布末尾被藏、导航遮盖标题、金额 +0.00 亿误读等。最终 desktop 1440 所有八图无需内部横滚，768/390 可图内滚动但八条摘要金额先行可见，原始元数字以 SVG 导出，来源表均独立可展开。**视觉内部审稿有证据，但不冒充另一名独立人类编辑 PASS**。技术代码最后匹配 [GitHub Actions 41655445119](https://github.com/kobolibra/financials/actions/runs/41655445119) **PASS**（提交 `4a646a2a5444c03145256ae37a07b4c0bb05f463`），包括原始 PDF、25 项 exact 元级会计门槛、14 种对抗账本、8 张真实图/证据表/SVG 出口、1440/768/390 及完整 rebuild。之后文档增补未改计算逻辑；最终 PR HEAD 仍需核验。

**独立、不能合并的状态**：
- **PASS**：完整来源 PDF 镜像字节/SHA 与发行人期别、118 项指定原始元金额或原格、P&L/BS/CFO 原始元级会计桥、真实八条业务成本/毛利 source path 守恒、八图 source-typed brief、1440/768/390 本地独立 HTML 浏览器技术及已打开截图的目标修正。
- **FAIL（源信息尚不一致）**：p.137 应收与合同资产 top-5 90.50% 与 p.135+p.138 报表金额直算 89.17% 不一致，不强行补虚构分母；p.179 尚未履约金额年内+以后总和比披露总额多 0.01 元，不用于守恒图。
- **NOT_CHECKED**：上交所静态源与镜像**原始字节同一性**、所有重大财务附注完整独立逐项核验、8–12 季度/同业/估值独立资料、第二名真实独立专业研究员与外部视觉主编、重构后 PR 最终 `main`/Cloudflare 真实浏览器验收（须在合并后检查）。
- **通用化边界**：一个真实 688220 H1 半导体 source-flow + 14 反例并不能证明 22 个图形模板已全自动泛化、银行/保险/其他行业已具有同样源证据的通用财务流。

**新增可复现源码及审计**：`research/shared/conserved_flow.py`、`research/issuers/688220/{figure-briefs.json,source-cells.json,visual-audit.md,publish.py,report-template.html,test_accounting.py,verify_pages.py,qa_browser.py}`；八家公司继续同一 `public/index.html`，新独立公司链接始终是 `public/688220.html`，不创建独立版本首页。新增会计图之后需同时更新原首页卡片 `site/research_catalog.json` 的 `figures=8`，旧七家公司 HTML 保持字节不变。

**下一步必须实际做**：确认本分支生成的八图 HTML 和首页保持可重建、一并通过 handoff 和 GitHub PR；合并至当前 `main`、查看 Cloudflare Pages 针对新 commit 构建完成，并运行实际线上八家公司 1440/768/390 截图和导航、最终生产路由与来源图形断言；最后把这里从候选改为真实 commit+RUN 的确切状态。

## 2026-11-03 · 688220 翱捷科技-U · 第八家公司源限定研究预览

**发行人**：翱捷科技股份有限公司 688220.SH，2026H1，未经审计，2026-08-29 上交所公告。完整 224 物理页披露副本（新浪公告镜像、非上交所原始服务器字节认证），1,449,510 字节，SHA256 `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`。原件、源页文字/坐标、截图、原始附注行列证据：`research/issuers/688220/source/`、`extracted/`、`source-blocks/`、`source-images/`；`source-manifest.json` 和 `source-verification.json`。上交所静态直链在 GitHub runner 返回 3.8KB HTML，官方 URL vs 镜像完整字节同一性：**NOT_CHECKED**。

**新增的实际研究资产**：`research/issuers/688220/source-ledger.json`（93 原始金额/比例字段，合并/期间/元与物理页）；`research-memo.md`（商业模型、附注红队、会计分母差异）；`publish.py` + `report-template.html`（生成完整单公司独立、离线无外部 JS/CSS 的 `public/688220.html`）；`test_accounting.py`、`verify_pages.py`、`qa_browser.py`、`qa.json`。原七家公司报告和账本内容均保持不变；统一目录只由 `site/research_catalog.json` 扩容到八个条目，`site/portal_builder.py` 仍是原首页唯一生成器。

**机构财务核查（来源限制）**：
- PASS：四类互斥收入和成本精确合并、利润表带符号营业利润至归母、扣非 vs 非经常项目（税后）、合并 BS 本期/期初恒等式、合并净利润至经营现金流 **17 原始 signed 调整到元零差**、现金等价物期初至期末四项闭合、存货/应收账款净额、合同负债三类预收、收入时间分类。图形有真比例的收入流向桑基、有符号利润及现金瀑布、两期真实 BS 存量对比，原始表可追溯到源页。
- 原始物理页文本匹配：上一轮版本 109/118，9 项为 PDF 窄表拆分字符串，已对照 p.135、146 原始图像复核重要行/列；新 93 字段需要运行最终 `verify_pages.py` 后更新准确覆盖率。不能把页面上数字出现当作完成全部重大附注审核。
- **源披露差异不可造假修补**：p.137 前五名应收/合同资产原文占比 90.50%，但按 p.135 应收原值 464,113,067.29 + p.138 合同资产原值 1,113,000，得 **89.17%**；无法由同页披露表独立复现统计分母，`AR_TOP5_RATIO_DENOMINATOR = FAIL`。p.179 已签约尚未履约收入的时间拆分总额偏差 **0.01 元**，没有强制假“其他”平衡。报告保留两个异常、局部不可编审为通过。
- 本公司本期普通盈余的“扭亏”并非扣非扭亏：归母 +0.84 亿，扣非 −0.59 亿，CFO −3.77 亿。合同定制验收时点 p.126、合同履约成本 p.147、应收集中度 p.137、受限现金 p.189、短债期限 p.201、第三层次公允价值 p.203、单一经营分部 p.210 均进入研究及反证链。
- **未取得的认证**：全部重大附注逐项独立核验、官方服务器原件字节同一性、8–12 季度外部证据/估值、第二位独立专业财务研究员签字 = **NOT_CHECKED**。不得将本报告称为已正式“机构顶级认证”。

**技术与原创视觉**：七项不同研究问题图形，真实元金额宽度桑基，非负守恒、带符号会计桥、受限股权/公允价值口径分开；实际 Chromium 1440/768/390、SVG 导出、源表与移动端截图已经在 branch Actions <https://github.com/kobolibra/financials/actions/runs/41620029401> PASS（该运行时对应早于最新会计附注更新的提交）。本人已真正打开原始 PDF p.135、137、146 和图形截图，发现并在源码修正了桑基微型分类标签堆叠、毛利图数字压条及移动端标题孤行。最终新 commit 仍须独立测试后才能标 **PASS**。

**待发布验证**：`site/research_catalog.json` 八家公司、`public/index.html` 八卡、`public/688220.html` 单页、原七链接均进入**同一** <https://financials-in-visuals.pages.dev/>；必须运行 `python scripts/check_handoff.py`、目录回归和真实 Cloudflare GitHub Actions Playwright 1440/768/390。主分支已成功部署之前只能记录 **GITHUB/LIVE=NOT_CHECKED**。本轮没有创建独立新版本首页或破坏任何旧报告。

**可复现命令**：
```bash
python -m pip install pymupdf playwright
python research/issuers/688220/verify_pages.py
python research/issuers/688220/test_accounting.py
python research/issuers/688220/publish.py --out public/688220.html --qa research/issuers/688220/qa.json
python research/issuers/688220/qa_browser.py --html public/688220.html
python site/portal_builder.py --out /tmp/asr-portal
cmp public/index.html /tmp/asr-portal/index.html
python -m unittest discover -s site -p test_portal.py -v
python scripts/check_handoff.py
```

## 2026-11-03 · 本轮执行检查点（此前七家公司入口扩容工程的历史检查点）

**当前正式公司数仍为 7，绝无虚构的第八家公司。** GitHub `main` 代码增量提交 [`9f8cab1439`](https://github.com/kobolibra/financials/commit/9f8cab1439225bac3b25a431f85cbeae60487eba)，已合并 [PR #1](https://github.com/kobolibra/financials/pull/1)。修改：`site/portal_builder.py`、`site/test_portal.py`、`.github/workflows/verify-unified-research-library.yml`；没有修改任何既有七家公司独立 HTML、财务账本、`site/research_catalog.json` 或 `public/index.html`。这是一项 **N 家入库生成能力修复**，不是新公司财报研究或最终出版。

**可复现测试与确切结果：**
- `python -m unittest discover -s site -p test_portal.py -v`：模拟第八家公司、新行业、新报告期可进入同一目录；原七家首页重新生成与 `public/index.html` 字节完全一致。PR 运行 [41614961062](https://github.com/kobolibra/financials/actions/runs/41614961062) **PASS**。
- `python scripts/check_handoff.py`：在代码提交 `9f8cab1439` 的交接工作流 [41615024220](https://github.com/kobolibra/financials/actions/runs/41615024220) **PASS**。
- 统一网站原七家公司 GitHub Actions 真实 Cloudflare Chromium 1440/768/390 浏览器路线、检索/筛选、原有桑基、回程与截图采集：[41615024205](https://github.com/kobolibra/financials/actions/runs/41615024205) **PASS**，针对代码提交 `9f8cab1439`；**只覆盖当前七家，未做新增公司的视觉编审**。本会话的 Web 直接访问被禁用、容器 DNS 解析 Cloudflare 失败，所以本会话直接 HTTP/独立截图复核为 **NOT_CHECKED**；不得将 CI 截图存在等同本人逐张视觉审批。
- 老版本 `last_verified_release` 所载原 PDF 和附注会计检查仍只是对应旧提交的历史通过范围；本轮没有宣称重新完成七家全附注审计。

**新发行人取证阻碍：** 当前聊天的上传文件列表为空；已搜索本 Project/Library，仅发现此前七家公司和行业验证成果，**没有一个可确定身份的“新公司”原始 PDF 或官方完整报告链接**。故 `ISSUER_IDENTITY=NOT_CHECKED`、`ORIGINAL_PDF_BYTES=NOT_CHECKED`、`PDF_SHA256=NOT_CHECKED`、`PAGE_ROW_COLUMN_SEMANTICS=NOT_CHECKED`、`ACCOUNTING=NOT_CHECKED`、`COMPLETE_MATERIAL_NOTES=NOT_CHECKED`、`THESIS_RED_TEAM=NOT_CHECKED`、`AEI_VISUAL_EDITORIAL_NEW_ISSUER=NOT_CHECKED`、`CHART_CONSERVATION_NEW_ISSUER=NOT_CHECKED`、`BROWSER_NEW_ISSUER=NOT_CHECKED`、`GITHUB_AND_LIVE_NEW_ISSUER=NOT_CHECKED`、`INDEPENDENT_HUMAN_FINANCIAL_REVIEW=NOT_CHECKED`。不能据此开始猜数、生成财务报告或创建目录空卡。

**一旦收到新原件**：先核对 PDF 完整字节与公告/更正版本、发行人/期间/币种/审计/合并范围及 SHA、实际物理页；读取对应行业旧账本和出版器，建立原始行列证据账本、报表与附注复核、研究主线/反证和 figure brief；根据金额关系做严格守恒 Sankey 或明确不适用并采用带符号图形；仅在实际完成 HTML + 1440/768/390 本地及生产审查后向 **同一** `site/research_catalog.json` 和独立 URL 加入第 N 家，更新本文件与机器状态。该来源缺口无法靠已有七家数据补齐。

## 生产结构（经现场验证的现有基线）

原有独立光通信三篇：`/300394.html`、`/300308.html`、`/300502.html`；行业独立四篇：`/research/2026-h1-v10/600036.html`、`/688111.html`、`/600519.html`、`/000333.html`（完整路径见 [目录 JSON](site/research_catalog.json)）。完整专题 `/optical-2026h1.html` 不计入公司数。**新公司只能进入同一首页公司库，并保留旧 URL。**

当前唯一有效 Skill：`skills/ashare-financial-storytelling/SKILL.md` **v8.3.2-RC1**，并且 **01–05 研究规范全部必读**。两条研究基线并列验收：机构财报/行业深度与 App Economy Insights（AEI）/FT 风格的财务视觉叙事。Skill 是项目仓库文件，**不是自动加载的 ChatGPT 内置或已安装 Skill**。

## 最新已证实的修复

2026-11-03，已经对照原始半年度财报物理页确认：
- **300394** 合并收入中的 37,651,189.26 元确系 p.140 披露的其他业务收入，成本 9,087,378.57 元；另外两类光器件正好构成主营业务。
- **300502** 合并收入中的 27,106,113.32 元确系 p.104 按业务类型分类的“其他”，成本 17,534,949.75 元；它和同页另一分类维度的其他业务收入 21,528,572.02 元**不同，绝对不能混加**。

两篇独立 HTML、原始账本及相关收入桑基图已修复。图形引擎不再用“未列示差额（计算）”伪造财务流量。详见 `docs/2026H1_OPTICAL_REVENUE_NOTE_CLASSIFICATION_AUDIT.md`。本次仅解决**这两个分类问题**，不能外推为全部七家公司附注已复核。

## 上一次已知的实际 PASS（以后每次都须重新查看 HEAD）

上一次完整发布内容对应 GitHub commit：`4a734d60a40839c90d12a295c61be917783b7187`。

| 验收工作流 | GitHub Actions | 上次结果 |
|---|---|---|
| 原始收入分类精确重建与发布一致性 | [41599963892](https://github.com/kobolibra/financials/actions/runs/41599963892) | PASS |
| 统一七家公司真实 Cloudflare 浏览器 | [41599963800](https://github.com/kobolibra/financials/actions/runs/41599963800) | PASS |
| 老版、历史研究导航 | [41599963891](https://github.com/kobolibra/financials/actions/runs/41599963891) | PASS |

这些通过记录仅证明对应提交的测试范围；**不代表新公司/新报告/后续修改自动通过**。当前 HEAD 用 GitHub 即时读取，不把一个会随提交变化的 SHA 假写成永久“当前 commit”。

## 尚未完成（必须保留 NOT_CHECKED，不准自证）

- **七家公司完整重大附注系统复核**：NOT_CHECKED（重要性导向核查收入、往来、减值、现金流及行业特殊附注；已抽核的两个分类不代表完成）。
- **真正独立的第二名人类财务研究员签核**：NOT_CHECKED（助手自身的第二遍复查不得冒充独立人类）。
- **真实外部证据支持的 8–12 季度、行业同行/估值和市场数据**：大多数公司 NOT_CHECKED；无来源时不得出图。
- **每个行业完整可泛化的自动 PDF→出版引擎**：NOT_PROVEN。现有 v7 光通信及 v10 另外四公司是已验证案例，不代表任意新行业自动可用。

研究质量不能通过图表数、自动测试数、PDF 文本字符串匹配或站点 HTTP 200 来代替。发布流程与保守门槛见 [REPORT_RELEASE_CHECKLIST](docs/REPORT_RELEASE_CHECKLIST.md)。

## 新会话交接工作

**开始**：GitHub 读此文件、`START_HERE.md`、`project-status.json`，完整读 Skill 和五份研究手册，再检查最新 Actions；原 PDF 不在新会话里自动出现时必须取得真实字节、核实 SHA/报表期间与版本。

**执行**：对已有模块先复用、对新公司只添加一个真实公司条目与独立页面，不创建重复目录；每个财务/可视化关卡逐项 PASS/FAIL/NOT_CHECKED。

**结束**：将所改代码、来源、原始 PDF 归档引用、可复现命令、门槛状态、真正生产链接和可继续执行的下一步记录在 `PROJECT_STATE.md` 及机器状态中。绝不将未完成的问题笼统留给用户重新提醒。完整协议：[docs/HANDOFF_PROTOCOL.md](docs/HANDOFF_PROTOCOL.md)。

历史旧状态全文完整保存在 [docs/history/PROJECT_STATE_ARCHIVE_2026-11-03.md](docs/history/PROJECT_STATE_ARCHIVE_2026-11-03.md)，不是现行执行指令。

## 2026-11-03 · NEW-SESSION HANDOFF MECHANISM

Obsolete initial README and old 25k-character accumulated PROJECT_STATE are replaced by a single active seven-company status and preserved historical archive. Current source of truth: `START_HERE.md`, `project-status.json`, complete Skill v8.3.2-RC1 and five manuals. New Code/Agent entry: `AGENTS.md` and standard Codex `.agents/skills/ashare-financial-storytelling/SKILL.md` wrapper, which links to the ONE canonical full Skill. Ordinary ChatGPT new-session continuity: `docs/CHATGPT_PROJECT_INSTRUCTIONS.md` + `docs/SETUP_PERSISTENT_CONTEXT.md` for one-time user Project settings; this GitHub edit cannot modify the user's ChatGPT account automatically. Explicit copy-paste fallback: `docs/NEW_SESSION_PROMPT.md`.

First handoff validation PASS: GitHub Actions https://github.com/kobolibra/financials/actions/runs/41610923043, including manifest/Skill/manual/source/index checks, 6 adversarial handoff regressions and 9 independent portal tests. This run tested the earlier documentation-only commit; later edits need own checks. New handoff workflow `.github/workflows/verify-handoff.yml` triggers automatically on its own relevant content paths. Prior financial PDF/report browser QA remains separately logged as historical actual evidence; no new company finance report is certified by the handoff workflow.
