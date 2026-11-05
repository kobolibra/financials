# FINANCIALS IN VISUALS — 从这里开始（最新项目入口）

**2026-11-05 AEI/FT 视觉品质 v8.8.0-RC1 已实际 main 合并：** 已在 [#33](https://github.com/kobolibra/financials/pull/33)、[#34](https://github.com/kobolibra/financials/pull/34) 实际合并；现行 Skill 方法加入 [财经总编真实审美与桑基A/B/C决策标准](docs/AEI_FINANCIAL_VISUAL_EDITORIAL_STANDARD.md) 和真实独立HTML静态审查器。已发现生产源V10四家600036/688111/600519/000333在390隐藏除桑基外所有图、剩余850px桑基只在小窗横滑，确认为旧版FAIL；新规范和自动测试绝不宣称四家公司已修或全站审美达到AEI顶级。站点仍唯一11家公司，独立人类研究/视觉审核NOT_CHECKED。



**2026-11-05 · 已公开核验的最新生产状态（后面日期较早的章节只作历史快照）**：现行 11 家公司仍在同一个 [Financials in Visuals](https://financials-in-visuals.pages.dev/) 公司目录，独立离线 HTML，`site/research_catalog.json` 为唯一公司清单。必须在每个新会话读取**当时真实 GitHub main**、`project-status.json`、当前 GitHub Actions、完整 Skill 和五册研究手册，不得凭本段硬编码未来公司数或把旧版本的“待上线”当真。

**最新真实 Cloudflare 688220 已 PASS**：[翱捷科技正式研究报告](https://financials-in-visuals.pages.dev/688220)，[完整 HTML / 六张真实中文浏览器截图 / 唯一11家目录真实路径验证 Action #41871662195](https://github.com/kobolibra/financials/actions/runs/41871662195)。真实生产提交 `e63ee316db22d8d079be6a80cd3cd9f08fd1d98e`，源报告 224 物理页镜像 SHA `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`，公司完整公开 HTML SHA `aca567335dbec04d94569bc93a52f207b4b1bacb6b77cb41a3ca5eaae2f5d973`，首页完整 HTML SHA `f625453172a83b7db38d0c5a67ddbecd84fbf078bc9f78c2e20c45b00b23ab41`。九幅按原始元金额绘制的独立手机财务图，1440 / 768 / 390 真浏览器审核、原财务来源路径与原会计有符号桥已发布；保留桌面原 SVG、全部原元级证据表和编辑导出。截图、真实最终网址与源 SHA 详见 `research/issuers/688220/live-release-receipt.json`，校验门见同目录 `release-gates.json`。Skill v8.7.5-RC1对应此前半导体发布阶段；现行方法规范见首页v8.8.0专项质量升级。原 p137 前五名应收/合同资产报告 90.50% 对比推导约 89.17% 的分母差异、RPO 0.01 元差额仍 **FAIL（附注有界）**；上交所官网 PDF 与镜像逐字节同一性及独立第二名人类财务/视觉审稿仍 **NOT_CHECKED**，不得对外称全优顶级完成。

**最初三家光通信同样真实上线**：300394、300502、300308 三份源金额财务图与真实公开 1440/768/390 的 HTML SHA 及导航见 [主站 Action #41855709571](https://github.com/kobolibra/financials/actions/runs/41855709571) PASS。当前仍明确 **FAIL 390 图内裁切的四家旧 HTML** 为 `600036`、`688111`、`600519`、`000333`，必须逐个按原报告和真实图源复核并重建，不可凭其他行业的通过结论替它们签字。AEI/FT 水准的独立专业审美审阅仍没有第二人类编辑签字。

---

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

## 2026-11-04 新近 main 真实发布核对（仅对应以下当次 SHA）

实际观测 `main=9060bd2a0bf3ddc32d267c176388214ef3316f13`：在同一个 11 家独立公司目录中，长江电力 `600900`、恒瑞医药 `600276` 的新版手机原生来源财务图与原桌面真实桑基图 **已发布**，并通过源链接完整 HTML、首页 SHA、真实中文 1440/768/390 及 6+6 张真截图验证 [#41804157527](https://github.com/kobolibra/financials/actions/runs/41804157527)。对应公司完整 HTML SHA 分别为 `d928676e87ff3d415de36931ee5706614d797264a88dc4980b94426f1492eef8`、`cd4d0c694c2c1c36c5ba2b2d5028f7db157668139edfe0b00f310f9cd94bee0a`；[原旧测试 #41804157343](https://github.com/kobolibra/financials/actions/runs/41804157343) 出现双 SVG 误判 FAIL，已在 [PR #24](https://github.com/kobolibra/financials/pull/24) 从源测试修正、正式合并 `25c5796b`，修复后实际 Cloudflare 统一目录 [#41806506722](https://github.com/kobolibra/financials/actions/runs/41806506722) PASS。之后的新 main 必须重新查询 Actions；以上 PASS 只对应所注明代码/真实数据范围，不能取代完整附注或独立人类审阅。仍有八家旧公司 390 财务图内横滚 FAIL。现行 Skill v8.7.2-rc1 原文和所有五册需要每次重新读取。

## 1. 当前独立公司研究库：不要在启动文档硬编码发行人总数

权威清单是 [site/research_catalog.json](site/research_catalog.json)，唯一线上目录是 [Financials in Visuals](https://financials-in-visuals.pages.dev/)。最近真实 `main` 生产验证 [#41778320066](https://github.com/kobolibra/financials/actions/runs/41778320066) 对应 `b88698a0cf1cfcd89c16eda1e399796d9418ea04`，当时**11家公司**全部路由以及桌面/平板/手机导航通过；这只是**明确有时间和 SHA 的历史验收快照**，新对话必须再取当前 GitHub `main`，不能把 11 当未来的固定常数。

最新实测新增寿险：中国人寿 `601628`，独立报告 [正式线上全文](https://financials-in-visuals.pages.dev/601628)，仓库源账本 `research/issuers/601628/`，原始完整报告104物理页、133项源事实、33个定位源单元、18个会计及监管资本/有限保证核验、10个原创图形；目前是**source_limited_preview**，并不等于完整附注/外部估值/第二名人类审稿 PASS。2026-11-04 的手机十张源驱动全图已发布；当时历史线上公司页 HTML SHA `6f38612a58fe5e50bbe3d7fe43a35d64cc6652328f4446525b6981cdeb3b22dd`；之后实际已更新的 `601628` 正式页面 SHA 为 `b065071a19803465d6f1f62994d190d2b8e0212317ea7db9c08de453cfa3e8b0`，请以对应当次 main/Actions 为准。该历史版本与首页 SHA `f625453172a83b7db38d0c5a67ddbecd84fbf078bc9f78c2e20c45b00b23ab41` 已通过真 Cloudflare 浏览器对比。公司目录卡 `/601628.html` 的点击跳转被 Pages 正常规范化为独立 `/601628` 路由，不是返回主页。其他既有公司不能被新发布覆盖。

产业链横向比较 `/optical-2026h1.html` 始终是**专题**，不算单独公司。后续任何新增公司必须加入现有 `site/research_catalog.json` 并运行 `site/portal_builder.py`，只发布独立、可离线打开的单公司 HTML。绝不能新建“三家／四家／v11”第二入口。

## 2026-11-04 · v8.7.1 水电和创新药行业手机原生财务图构建的历史候选阶段（正式上线证据见上）

`research/shared/build_two_sector.py` 已将 `research/shared/mobile_finance.js` 源金额真图内联至600900长江电力和600276恒瑞医药的两份完整离线HTML，各8个桌面完整SVG及8个390原生财务SVG。真金额收入流向桑基、负数利润/间接CFO/现金和CAPEX瀑布、分部嵌套创新药、两日期资产负债守恒均已实际源PDF+ CJK Chromium1440/768/390验证 [#41799046343](https://github.com/kobolibra/financials/actions/runs/41799046343) **PASS候选**，真实图证和两新完整HTML SHA详见[VIS-044](research/visual-audit/VISUAL_CHANGESET_2026-11-04_TWO_SECTORS.md)。该源修改若未真实在Cloudflare以新SHA核验，直播仍NOT_CHECKED；旧十家手机横滚基线依旧是原字节FAIL，只真实修两家后余八家待修。`scripts/check_visual_editorial_policy.py` 现在还校验**当前改后HTML SHA**与同SHA浏览器实测，不准用旧截屏替新版本造PASS。

## 2026-11-04 · 视觉质量 P0：早期三家与后期全站 11 家实际对比

真实 GitHub Actions [#41783946027](https://github.com/kobolibra/financials/actions/runs/41783946027) **11家公司×真实中文 Chromium 1440/768/390=33次实际网页渲染**，逐幅浏览样本，发现 **10/11家390px财务图被780–1050px宽 SVG 限制在320–356px水平小窗口**，旧“根页面不溢出”虽PASS但图本身 FAIL。详见[全站视觉退化审计](research/visual-audit/VISUAL_DESIGN_DRIFT_REPORT_2026-11-04.md)、[真实图证](research/visual-audit/cross-issuer-visual-audit.json)、[固定原HTML SHA的10家FAIL账本](research/visual-audit/quality-debt.json)。最早300394/300308/300502桌面复杂金额流的AEI风格更强，但手机一样失格且原金额表不如后期完善；不把图多或单独来源表当顶级视觉。

**实际源头纠错**：601628桌面首图金额与同比数值重叠，在`research/issuers/601628/publish.py`修改列布局并于真实 [#41784420788](https://github.com/kobolibra/financials/actions/runs/41784420788) 完整原PDF/会计/3屏浏览器+第二次确定性构建PASS。新版HTML SHA `b065071a19803465d6f1f62994d190d2b8e0212317ea7db9c08de453cfa3e8b0` 在当前候选工作分支，原正式版 `6f386...` 的 LIVE PASS 不证明新字节已经上线。**新公司及任何编辑后的旧公司**如仍有390px内部滚动，必须被`scripts/check_visual_editorial_policy.py`+恶意测试拦截。剩余十家老版手机视觉明确FAIL，未逐页重构前不得说已全部修好。

## 2. 已验证什么，未验证什么

**最近完成的有界修复**：天孚通信 p.140 0.38 亿元对应已披露其他业务；新易盛 p.104 0.27 亿元对应按业务类型“其他”，**不能**与另一维度“其他业务”合并。见 [附注核对报告](docs/2026H1_OPTICAL_REVENUE_NOTE_CLASSIFICATION_AUDIT.md)。

**最近一次精确 main 实测**（手机十大财务图形已真实部署）：Cloudflare 11家公司全部原始路由和 1440/768/390、唯一首页/独立公司全文双 SHA、保险公司十原SVG/十原始来源表、手机十组完整原始元账本签名金额图及导航 [41778320066](https://github.com/kobolibra/financials/actions/runs/41778320066) **PASS**；保险完整原 PDF/18项财务/桌面及手机真图和确定性离线重建 [41778320037](https://github.com/kobolibra/financials/actions/runs/41778320037) **PASS**；11家公司统一研究库 [41778320121](https://github.com/kobolibra/financials/actions/runs/41778320121) **PASS**；原 Pages 路由 [41778320141](https://github.com/kobolibra/financials/actions/runs/41778320141) **PASS**；Skill交接 [41778320045](https://github.com/kobolibra/financials/actions/runs/41778320045) **PASS**。全部对应当时真实发布 `main` `b88698a0cf1cfcd89c16eda1e399796d9418ea04`；原始公开网页浏览器六截图元数据存 `research/issuers/601628/live-release-receipt.json`。新提交必须重新核验，不能沿用旧CI冒充新版财务与审美通过。

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
