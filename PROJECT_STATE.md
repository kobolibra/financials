# Financials in Visuals — ACTIVE PROJECT STATE

**状态日期：2026-11-03。生产分支：`main`。现行入口：[START_HERE.md](START_HERE.md)。机器状态：[project-status.json](project-status.json)。**

> **唯一正式站点：首页统一八家公司研究库（本提交为候选，按当前 main 实际发布状态验收）。** <https://financials-in-visuals.pages.dev/>。不是四家公司 v9/v10 独立站点，更不是 `research-lab` 里的工程样本。

## 2026-11-03 · 当前最新执行：AEI/FT 源证据重构及实质财报纠错（v8.3.3-RC1）

**当前工作分支**：`work/688220-aei-financial-flow-redesign-20261103`，基于真实 main `54fa99ab29227f0aadb08f63da92c16955233381`。新规范 `skills/ashare-financial-storytelling/SKILL.md` v8.3.3-RC1 和 `research/03_VISUAL_EDITORIAL_SYSTEM.md` 已提交分支。**正式 main 和 Cloudflare 中的重构是否发布尚不能依据分支成功推断**；会以 PR + 主分支 Actions + 公开站点浏览器重新确认为准。

**原文会计问题已经直接修复（非状态挂起）**：224 页完整披露镜像 PDF（SHA-256 `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`）物理 p.87，`营业外支出 15.30 元` 属于**2025H1 上年同期列**，2026H1 当前列**空白**。前一账本错误把该数列为 2026H1 来源金额（原来的数字在该页出现的自动检查未能识别列）。已经在 `source-ledger.json` 把 15.30 迁到 `nonoperating_expense_prior`，2026H1 的同名项目作为**计算所得零、非原文披露零**保留；`verify_pages.py` 用原始 PDF p.87 坐标及营业利润+营业外收入=税前利润三方检查。原“15.30 当期现金损益”解释不得重复使用。

**重构不是机械增加图表**：旧桑基只把四项收入合并到全公司，再分成总成本/总毛利；虽然总额守恒，但缺乏真实单业务成本和毛利的财务解释。新桑基来自 p.178 四类相互排斥、同期、合并的真实收入及原始成本，每一类拆为自身披露的 COGS + 推导的 GP，7 条非零真实权重带、测试服务确实为零 GP 不生成虚假正流。新完整**合并毛利→营业利润→税前→合并净利润的带符号瀑布**依 p.86–87 展示研发、四项费用及税费、投资及其他收益、公允价值、减值和税项；与税后扣非归母、OCI 和现金相区分。两时点 **资产＝负债＋所有者权益** 图明确存量关系而非伪现金流。整个报告九张语义不同的图、九张来源表、九条移动端数值摘要。具体关系见 `research/issuers/688220/figure-briefs.json`。

**确切技术验证**：GitHub Actions `Verify AEI-inspired 688220 financial-flow and source-linked research` 运行 [41651927501](https://github.com/kobolibra/financials/actions/runs/41651927501) 对提交 `d5e42a40becf8226de7be3f2a85d00095db3fa13` 成功，包含完整 PDF 原始字节 224 页/1,449,510 字节/SHA、p.87 比较列核对、约 29 项 Decimal 财报恒等式、8 个会计错误注入反例、九图和来源表的 1440/768/390 Playwright、21 个实际截图、3 个 SVG 文件下载、清洁环境生成 HTML 字节对比。我在当前会话已**实际打开** 1440 桑基、带符号 P&L、资产结构、390 桑基截图，并发现/改正过固定导航压住图题和 `+0.00` 亿微项目误读问题。CI 成功**不是**独立视觉主编签字。

**并列质量门槛状态**：`PDF_MIRROR_SHA+PAGES:PASS`；`SSE_URL_BYTE_EQUALITY:NOT_CHECKED`；`SELECTED_PHYSICAL_ROW_COLUMN:p87_PASS;OTHER_MATERIAL_ROWS_PARTIAL`；`ACCOUNTING_IDENTITIES:PASS`；`FULL_GAAP_PNL_SIGNED:PASS`；`4_SOURCE_COST_GP_SANKEY_EXACT:PASS`；`AGGREGATE_CFO_17_SIGNED:PASS`；`FULL_MATERIAL_NOTES:NOT_CHECKED`；`ORIGINAL_AEI_FT_EDITORIAL:PARTIAL_SELF_REVIEW`；`BROWSER_LOCAL_1440_768_390:PASS`；`GITHUB_PUBLIC_MAIN_NEW_VERSION:NOT_CHECKED`；`CLOUDFLARE_LIVE_NEW_VERSION:NOT_CHECKED`；`INDEPENDENT_SECOND_HUMAN:NOT_CHECKED`；`FULL_PEERS_VALUATION:NOT_CHECKED`。

**仍存在的原始披露不一致**：p.137 应收/合同资产前五名原文 90.50% 与 p.135+p.138 原值重算 89.17% 分母不闭合；p.179 RPO 期限分拆与合计存在 0.01 元披露差。仅对这些关系保留 `FAIL_BOUNDED_SOURCE_NOTE`，不生成残差业务图，不把它们伪称财务舞弊。单 PDF 不支持多季外部估值/同行。

**下一次精确操作**：检查 PR 合并版本与生产网页 1440/768/390 的真实图形/导航/中文字体，再同步此处的准确 git SHA、CI run 和正式 URL；不要另建公司入口或改动老七家报告。重建命令：

```bash
python research/issuers/688220/verify_pages.py
python research/issuers/688220/test_accounting.py
python research/issuers/688220/publish.py --out public/688220.html --qa research/issuers/688220/qa.json
python research/issuers/688220/qa_browser.py --html public/688220.html --out research/issuers/688220/visual-qa
python scripts/check_handoff.py
```

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
