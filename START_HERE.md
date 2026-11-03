# FINANCIALS IN VISUALS — 从这里开始（最新项目入口）

> **当前有效版本：统一七家公司研究库（2026-11-03）**。不是旧 v9 首页，也不是四家公司独立专区。生产站点：[financials-in-visuals.pages.dev](https://financials-in-visuals.pages.dev/)。仓库：[`kobolibra/financials`](https://github.com/kobolibra/financials)，生产分支 `main`。

## 0. 新对话 / 新 Agent 必读

**不能假设聊天记忆中已经包含本项目。仓库中的自定义 `SKILL.md` 不会自动变成 ChatGPT 已安装的 Skill。** 必须主动读取以下实际当前文件，而不是“知道有 Skill”便开始画图：

1. `START_HERE.md`（此文件）及 `project-status.json` — 当前**机器可校验**状态；
2. `PROJECT_STATE.md` — 只描述当前生产、实际 PASS / NOT_CHECKED 和未结事项；
3. `skills/ashare-financial-storytelling/SKILL.md` — 唯一现行方法和出版质量合同；
4. Skill 下 `research/01_...` 至 `05_...` **五份全文**，不可只读摘要；
5. `docs/REPORT_RELEASE_CHECKLIST.md` — 对每篇新公司报告完成的源数据、会计、分析、可视化、网页验收清单；
6. `docs/HANDOFF_PROTOCOL.md` — 任务开始/结束的交接格式；
7. `site/research_catalog.json`、现有同行业真实研究页和发布生成器。

**新窗口一键启动文本：** [docs/NEW_SESSION_PROMPT.md](docs/NEW_SESSION_PROMPT.md)。如果新会话无法读取 GitHub，则明确说出阻碍并请求上传必需文件，不能谎称“已执行 Skill”。

## 1. 当前生产的七家独立研究

| 行业 | 公司 | 正式网页 |
|---|---|---|
| 光器件 | 天孚通信 300394 | `/300394.html` |
| 光模块 | 中际旭创 300308 | `/300308.html` |
| 光模块 | 新易盛 300502 | `/300502.html` |
| 银行 | 招商银行 600036 | `/research/2026-h1-v10/600036.html` |
| 软件 | 金山办公 688111 | `/research/2026-h1-v10/688111.html` |
| 白酒 | 贵州茅台 600519 | `/research/2026-h1-v10/600519.html` |
| 制造 | 美的集团 000333 | `/research/2026-h1-v10/000333.html` |

产业链横向比较 `/optical-2026h1.html` **属于专题，不是第八家公司**。新公司通过 `site/research_catalog.json` 和 `site/portal_builder.py` 接入同一个首页。不得另建“三家／四家／v11 公司入口”。原有公司 URL 不能因重构而损坏。

## 2. 已验证什么，未验证什么

**最近完成的有界修复**：天孚通信 p.140 0.38 亿元对应已披露其他业务；新易盛 p.104 0.27 亿元对应按业务类型“其他”，**不能**与另一维度“其他业务”合并。见 [附注核对报告](docs/2026H1_OPTICAL_REVENUE_NOTE_CLASSIFICATION_AUDIT.md)。

**最后一次已知公开验收**（历史报告对应 SHA、并非对将来任何报告的保证）：原始收入分类重建 [41599963892](https://github.com/kobolibra/financials/actions/runs/41599963892)、七家公司实际浏览器 [41599963800](https://github.com/kobolibra/financials/actions/runs/41599963800)、历史链接 [41599963891](https://github.com/kobolibra/financials/actions/runs/41599963891)。每次交接仍要查看 **GitHub 当前 HEAD 的最新 Action 和 Cloudflare 实际页面**。

**尚未完成**：七家公司的全部重大附注再次逐行审查、另一名真正独立研究员的审核签名、全行业 8–12 季度和可比公司估值研究、所有行业自动接入的证实。**源码核算、CI、截图通过≠机构级研究已认证，不能叫“全面超越 AEI”。**

## 3. 新公司从 PDF 到独立 HTML 的最短正确路径

完整原始 PDF 字节/披露版本与 SHA → 逐页重要附注与三表独立证据账本 → 行业独有商业逻辑与会计口径 → 财务勾稽/红队反证 → 深度研究论点与反论点 → 阅读 AEI/FT 参考后选择每一张图的正确语法 → 加权财务桑基（适用时）、带符号瀑布、现金、资本、分部、历史/同业（只有有来源时） → 完整单公司独立离线 HTML → 逐图审美/标签/中文/移动端 → 本地复现 + GitHub Action + 生产站点验收 → **更新当前状态和本次真实 PASS / FAIL / NOT_CHECKED**。

不要重复已存在的行业生成器或过度依赖统一柱状图模板。**有会计守恒的收入流向图是重要表达方式，但不是“做了桑基图=完成所有研究”。**

历史长记录已搬到 [docs/history/PROJECT_STATE_ARCHIVE_2026-11-03.md](docs/history/PROJECT_STATE_ARCHIVE_2026-11-03.md)，仅供考古，**不可当现行状态使用**。
