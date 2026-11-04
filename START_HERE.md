# FINANCIALS IN VISUALS — 从这里开始（最新项目入口）

> **当前有效规则：唯一公司研究库，以实际 GitHub `main` 的 `project-status.json` + `site/research_catalog.json` 为真值。不得把上次聊天、固定公司数量或旧 v9 首页当当前状态。** 生产站点：[financials-in-visuals.pages.dev](https://financials-in-visuals.pages.dev/)。仓库：[`kobolibra/financials`](https://github.com/kobolibra/financials)，生产分支 `main`。

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

## 1. 当前独立公司研究库：不要在启动文档硬编码发行人总数

权威清单是 [site/research_catalog.json](site/research_catalog.json)，唯一线上目录是 [Financials in Visuals](https://financials-in-visuals.pages.dev/)。上一轮真实 `main` 生产验证 [#41771178361](https://github.com/kobolibra/financials/actions/runs/41771178361) 对应 `d11638f0c76ff8aef2beb163a1028f176123bbdc`，当时**11家公司**全部路由以及桌面/平板/手机导航通过；这只是**明确有时间和 SHA 的历史验收快照**，新对话必须再取当前 GitHub `main`，不能把 11 当未来的固定常数。

最新实测新增寿险：中国人寿 `601628`，独立报告 [正式线上全文](https://financials-in-visuals.pages.dev/601628)，仓库源账本 `research/issuers/601628/`，原始完整报告104物理页、133项源事实、33个定位源单元、18个会计及监管资本/有限保证核验、10个原创图形；目前是**source_limited_preview**，并不等于完整附注/外部估值/第二名人类审稿 PASS。2026-11-04 的线上公司页 HTML SHA `051a8ecb56cb200f4c411bb53ad672096cfb299e297f149fd58aad334cbfb763` 与首页 SHA `f625453172a83b7db38d0c5a67ddbecd84fbf078bc9f78c2e20c45b00b23ab41` 已通过真 Cloudflare 浏览器对比。公司目录卡 `/601628.html` 的点击跳转被 Pages 正常规范化为独立 `/601628` 路由，不是返回主页。其他既有公司不能被新发布覆盖。

产业链横向比较 `/optical-2026h1.html` 始终是**专题**，不算单独公司。后续任何新增公司必须加入现有 `site/research_catalog.json` 并运行 `site/portal_builder.py`，只发布独立、可离线打开的单公司 HTML。绝不能新建“三家／四家／v11”第二入口。

## 2. 已验证什么，未验证什么

**最近完成的有界修复**：天孚通信 p.140 0.38 亿元对应已披露其他业务；新易盛 p.104 0.27 亿元对应按业务类型“其他”，**不能**与另一维度“其他业务”合并。见 [附注核对报告](docs/2026H1_OPTICAL_REVENUE_NOTE_CLASSIFICATION_AUDIT.md)。

**最近一次精确 main 实测**：真实 Cloudflare 11家公司全部路由和 1440/768/390、双页完整 HTML SHA、新寿险十图与原始来源表及导航 [41771178361](https://github.com/kobolibra/financials/actions/runs/41771178361) **PASS**；保险完整原 PDF/会计/真实图形 [41771178355](https://github.com/kobolibra/financials/actions/runs/41771178355) **PASS**；通用统一研究库 [41771178360](https://github.com/kobolibra/financials/actions/runs/41771178360) **PASS**；主站真实路由 [41771178350](https://github.com/kobolibra/financials/actions/runs/41771178350) **PASS**；Skill交接 [41771178406](https://github.com/kobolibra/financials/actions/runs/41771178406) **PASS**。全部对应同一个当时 `main` SHA `d11638f...`，绝不自动适用于以后的源码变更。

**尚未完成**：现有公司全部重大附注的完整独立系统语义复核、另一名真正独立研究员的审核签名、全行业 8–12 季度和可比公司估值研究、所有行业自动接入的证实。**源码核算、CI、截图通过≠机构级研究已认证，不能叫“全面超越 AEI”。**

## 3. 新公司从 PDF 到独立 HTML 的最短正确路径

完整原始 PDF 字节/披露版本与 SHA → 逐页重要附注与三表独立证据账本 → 行业独有商业逻辑与会计口径 → 财务勾稽/红队反证 → 深度研究论点与反论点 → 阅读 AEI/FT 参考后选择每一张图的正确语法 → 加权财务桑基（适用时）、带符号瀑布、现金、资本、分部、历史/同业（只有有来源时） → 完整单公司独立离线 HTML → 逐图审美/标签/中文/移动端 → 本地复现 + GitHub Action + 生产站点验收 → **更新当前状态和本次真实 PASS / FAIL / NOT_CHECKED**。

不要重复已存在的行业生成器或过度依赖统一柱状图模板。**有会计守恒的收入流向图是重要表达方式，但不是“做了桑基图=完成所有研究”。**

历史长记录已搬到 [docs/history/PROJECT_STATE_ARCHIVE_2026-11-03.md](docs/history/PROJECT_STATE_ARCHIVE_2026-11-03.md)，仅供考古，**不可当现行状态使用**。

### 自动发现范围的区别（Codex vs ChatGPT）

仓库已经提供 [Codex 仓库级 Skill 包装器](.agents/skills/ashare-financial-storytelling/SKILL.md)：Codex 在**已打开本仓库**时可以按官方约定发现它，再读取唯一完整 Skill。普通 ChatGPT 不会因为这些 Git 文件自动把它安装成全局 Skill。要让未来每个 ChatGPT 项目聊天具有固定指令，请按 [一次性 Project 设置说明](docs/SETUP_PERSISTENT_CONTEXT.md) 操作，复制 [Project 长期指令](docs/CHATGPT_PROJECT_INSTRUCTIONS.md)。**这一账户级 UI 操作尚未代替用户完成。**


## 2026-11-03 增量：翱捷科技原始字节与独立页面

2026H1 224 物理页 PDF 镜像原件 SHA256 `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`（1,449,510 bytes），原始字节保存于 `research/issuers/688220/source/`，账本/出版器/研究证据见同目录；正式研究页 `/688220.html`，首页仍唯一。上交所静态服务器回传 HTML，**交易所直链字节与归档副本是否完全一致尚为 NOT_CHECKED**。原始附注 p.137 的应收集中度 90.50% 与简单原值分母复算 89.17% 不一致，局部源证据门槛 **FAIL**，不可模糊称全部会计问题已解决。参考最新 `PROJECT_STATE.md`、`research/issuers/688220/research-memo.md` 和 CI 记录；本页描述的是代码预期状态，实际生产 URL 与当前 GitHub HEAD 仍需独立验证。
## 2026-11-03 AEI/FT 原始业务利润流向与重要行列纠错

该历史增量当时对应 **Skill v8.3.3-RC1**；现行唯一 Skill 版本必须以真实最新 `main` 的 `project-status.json` 和完整 `SKILL.md` 共同核对，不能把这里的旧版本字样当现行。翱捷科技 2026H1 的旧收入→集团 COGS/GP 桑基只证明集团守恒，不能解释每类业务利润。修订后的原始 p.178 桑基每类业务分别流向其对应的披露成本与推导毛利，**无最小假流**；毛利到净利润另用有符号瀑布，资产=负债+权益用两时点同尺度存量图。实际重构文件是 `research/issuers/688220/report-template.html`、`publish.py`、`figure-briefs.json`、`qa_browser.py`，生成 `/688220.html`。另发现 p.87 营业外支出 **15.30 元属于 2025H1 右列**，2026H1 当前列是空白（其损益贡献由算术推导为零），已直接更正账本与 PDF 物理坐标验证。不要将先前“页面数字找到即正确”的检查当作行列精确核对。

此处记录方法与需核实的源码事实，**不能代替最新 GitHub `main` 与 Cloudflare 正式网页的发布成功证明**；具体分支/CI/门槛见 `PROJECT_STATE.md` 顶部和 `project-status.json`。


## 2026-11-03 方法增量：Skill 持续迭代和第 N 家公司的强制发布门槛

从 v8.4.2-RC1 开始，必须同时阅读 [Skill 进化/错误闭环协议](docs/SKILL_EVOLUTION_PROTOCOL.md) 与 [可执行回归登记](skills/ashare-financial-storytelling/quality-regressions.json)。每次新增公司提供本公司 `research/issuers/<code>/release-gates.json`，实际 PDF SHA/字节、各项 PASS/FAIL/NOT_CHECKED、对应证据、预览/最终研究类型；运行 `python scripts/check_release_contract.py` 和对应恶意反例。旧七公司仍是历史来源审阅欠账，不获得自动追溯认证；翱捷科技已按来源限制研究预览记录，Cloudflare 本次版本 LIVE FAIL 不能虚报上线。每个用户反馈都要从 PDF/会计/图形源头修复并写入可迁移回归，独立核对真正生产网站。详见 `PROJECT_STATE.md` 和 `project-status.json` 最新记录。


**v8.4.2 出版漂移反例**：源账本的原始证据说明不同于已发布公司页内嵌的 `ledger-data`，即使财务和浏览器各项通过，仍会让重建失败。必须验证账本/全部来源/事实/分组与实际离线 HTML 一致；独立重建 [41667517537](https://github.com/kobolibra/financials/actions/runs/41667517537) 检出问题、修复后 [41667953097](https://github.com/kobolibra/financials/actions/runs/41667953097) 已通过。新的技术门槛见 Skill v8.4.2 与 `scripts/check_release_contract.py`。
