# Financials in Visuals — ACTIVE PROJECT STATE

**状态日期：2026-11-03。生产分支：`main`。现行入口：[START_HERE.md](START_HERE.md)。机器状态：[project-status.json](project-status.json)。**

> **唯一正式站点：首页统一七家公司研究库。** <https://financials-in-visuals.pages.dev/>。不是四家公司 v9/v10 独立站点，更不是 `research-lab` 里的工程样本。

## 2026-11-03 · 本轮执行检查点（新发行人入口已扩容；尚未收到新发行人原件）

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
