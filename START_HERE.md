# FINANCIALS IN VISUALS — 从这里开始（最新项目入口）

当前机器依据：`project-status.json` 与 `site/research_catalog.json`；本次候选、历史生产回执分别读取。

**2026-11-13 新公司真实生产候选：海尔智家600690。** 已取得192页原中报，181条原始/推导事实，23项会计勾稽，12项重大附注主题和12项问题驱动财务图；真实三屏与36次当前SVG下载通过。目录扩至12家；新图全部进入同一强制质量合同及自动源码重建，原11家公司文章保持原字节。当前新公司尚未合并上线，不借用旧Cloudflare绿色；人类二审、8–12季度同行估值仍单列未完成。见 `research/issuers/600690/release-gates.json` 与 `publication.json`。

**2026-11-13 已合并并核验正式站：七个历史系列的完整财务图已统一。** [PR #66](https://github.com/kobolibra/financials/pull/66) 合并源码 `5346ff0`；三家光通信、翱捷、长江、恒瑞、中国人寿共65幅源财务图，正式站1440/768/390共21个布局及195次当前可见SVG下载全部通过，线上完整HTML与发布源码逐字节相同。生产证据见 `research/quality/full-figure-production-20261113/result.json`，明确为本地真实浏览器访问正式站；本地源码证据见 `research/quality/full-figure-20261113/result.json`。公共图形核心与行业适配保留原始会计差异；新公司/新期间必须通过目录 `FULL_SOURCE_FIGURES_V1` 进入同一套逐图云端验收。下方旧HERO-only、未合并及权限受阻内容是历史记录，不能覆盖当前字节证据。人类审稿及未见真实财报的长期稳定性不声称通过。[历史四家合同](docs/ACTIVE_PR35_HANDOFF.md) 保留。


**2026-11-11 当前正式交付（覆盖下方历史候选快照）：** [PR #62](https://github.com/kobolibra/financials/pull/62) 已合并并正式发布，内容主分支 `e72bae81a9df22f54db7ba365f25bb8160c34111`；[PR #63](https://github.com/kobolibra/financials/pull/63) 已合并，修复新版研究附表、ASR隔离验收数据和保险累计桥的三处旧验收规则，主分支 `9101d76b178d50c8f76b9ffbb03b769c9ff5b6e4`。正式站11篇报告整页字节与源码一致，Chromium/WebKit共108次真实SVG导出通过；33屏/315图形观察未发现新阻断。11家132项重大附注主题经独立AI二审，3家24个连续单季/96项差分、41份官方PDF、3家同行及三季报反证已写入正文。美的依据物理p171附注46的自身成本改用Type A；银行利润桥及保险五幅累计桥按原金额验证。GitHub连接已恢复，验收规则成功更新，先前“权限不足未启用”是历史状态。真实线上证据见 `project-status.json.current_release_provenance_20261111` 与各发行人 `live-release-receipt.json`。独立人类签署未声称；原披露矛盾仍公开，三家跨期样本不能外推全行业泛化。 [历史四家交接](docs/ACTIVE_PR35_HANDOFF.md) 保留为历史证据。


**机器入口优先级：** `project-status.json` 与 `site/research_catalog.json` 是动态发行人清单、最新交接状态的唯一当前源；任何本文日期和 SHA 仅为历史证据，必须重新查询 GitHub main 与生产 HTML 字节。

**2026-11-09 最新已验证线上记录（源码精确对应，不外推未来提交）：** PR [#54](https://github.com/kobolibra/financials/pull/54) 已合并，长江电力 600900、恒瑞医药 600276 的 390px 真实金额守恒桑基来源名称、金额/毛利率改为更清晰的分行排版，并按真实 Noto CJK 字符边界修正行距；PR [#55](https://github.com/kobolibra/financials/pull/55) 修复了 GitHub 主分支与 Cloudflare 已发布字节不同步时的 fail-closed 门禁。主分支 `b72e6074795bc0cb9aabe0b312c79f1decf567f4` 经 [Cloudflare 正式站 11 路由、原始整页 SHA、1440/768/390 中文浏览器验证](https://github.com/kobolibra/financials/actions/runs/42599056086) PASS。对应源 HTML SHA：600900=`cf18a4e1ff655d989d439bb16a0684adeff9a300d46ca6a892aef86284680f88`，600276=`9a51d251d271a6dc7803c4036c71a441634ef784258aabaf85e97d1081962d99`；冻结截图及现场证据 artifact `13664069157`。发行人 `release-gates.json` 和 `live-release-receipt.json` 只能以这份真实线上回执晋升，不能用先前线上版本伪装成新版上线。详细机器源见 `project-status.json.current_release_provenance_20261109`。**此验收仅涉及两家具体已取证财务图、页面及指定数据；11 家全篇研究审美、跨期/同行、材料附注完备性、独立金融研究与视觉审查依然 NOT_CHECKED。**

**2026-11-09 可审计增量（PR #50–#52 已合并）：** [PR #51](https://github.com/kobolibra/financials/pull/51) 将长江电力 600900、恒瑞医药 600276 的桌面/手机经营图改为原始来源类型化驱动，剔除硬编码发电量/创新药值、禁止商品子集与 RPO 错误加总；[PR #52](https://github.com/kobolibra/financials/pull/52) 将两家可复算同比决策板块真正写入公司 HTML（原始元额、页码、反证，不宣称经营因果）。在历史 main `328ce615557390f1f0a52611496032557e87800a` 上，真实 [Cloudflare 11 路由 / 1440、768、390 CJK、全文 HTML SHA](https://github.com/kobolibra/financials/actions/runs/42595318738) PASS；本次发行人 receipt 与 release-gates 采用同一当次真实证据。交接另见 `project-status.json.current_release_provenance_20261109`。**十一家全篇顶级审美、全部重大附注、跨期和同业因果、独立财经/视觉双审仍不是通过状态。** 每次必须重新查询当前 GitHub HEAD 和生产文件 SHA，不能把历史 PASS 当未来 PASS。

**PR35 HISTORICAL HANDOFF:** `docs/ACTIVE_PR35_HANDOFF.md` is archived source provenance, not a live UNMERGED instruction; current GitHub main and machine catalogue override old status.\n\n**CURRENT MACHINE SOURCE OF TRUTH:** `project-status.json` + `site/research_catalog.json` are authoritative over any dated summary; fetch live GitHub main HEAD, production full HTML SHA and issuer original-source audit before asserting release readiness. Historical merged PR #35–#48 notes below are not a current deploy promise.

**2026-11-08 signed visual release snapshot (not a promise of all-11 editorial completion):** PRs #35–#48 including #43–#48 have MERGED. Verified code checkpoint main `5e6ec65d5fc9563be8b9f9d33c9abccc62aac9c6` (historical snapshot; always re-query HEAD). Main ASR source rebuild [42458241039](https://github.com/kobolibra/financials/actions/runs/42458241039) PASS; three optical real Cloudflare whole-HTML SHA / 11 routes / Noto CJK 1440/768/390 [42458196003](https://github.com/kobolibra/financials/actions/runs/42458196003) PASS. WPS/美的/长江电力/恒瑞医药 and 688220 already publish signed source-bound profit bridges; **300308 FIGURE 03 now shares one exact-CNY 1040 desktop / 330 native mobile signed P&L plan** while 300394/300502 original whole HTML bytes remain stable. Current typed common V9 positive income Sankey is distinct from signed profit and bank/insurance CAS grammars. #45's genuine 688220 [production SHA and screenshot receipt](https://github.com/kobolibra/financials/actions/runs/42457017812) is bound in `release-gates.json`; do not resurrect `unmerged_candidate` for the same already-deployed bytes. **Still NOT TOP-TIER COMPLETE:** nonhero whole-article visual migration across all 11, independent second finance/art review, exhaustive note reconciliations, and 8–12Q causal/peer research NOT_CHECKED; 688220 SSE official source-vs-mirror equality NOT_CHECKED. Machine-readable snapshot: `project-status.json.current_release_provenance_20261108`. Re-query live SHA and current HEAD every session.


**2026-11-08 MAIN STATUS OVERRIDE:** PR #35 (connected 11-issuer lawful hero grammar), PR #36 (quantitative research source/period checks), and PR #37 (V10 source-rebuilt mobile readable Sankey + Midea accounting caveat) have all MERGED INTO `main`. Their previous `UNMERGED_CANDIDATE` descriptions below are archived dated notes, NOT current release status. Re-query `git main HEAD`, current Cloudflare full HTML bytes, `research/quality/active-pr35.json` and independent source/browser gates before claiming live production. Seven companies remain **HERO_UNIFIED_OTHER_FINANCIAL_FIGURES_LEGACY**, independent finance/art review NOT_CHECKED and unseen cross-period generality NOT_ESTABLISHED.

**Every new session's authoritative machine entrypoints:** `project-status.json` for current handoff and `site/research_catalog.json` for one actual 11-issuer canonical catalog. Requery GitHub HEAD; candidate branch snapshots never replace live source SHA evidence.


**2026-11-07 newest seven-source-publisher hero migration (supersedes earlier paragraphs):** The actual shared desktop/native-phone source-yuan primary Sankeys cover 300394/300502/300308, 688220, 600900, 600276 and a separate *insurance-specific premium statistics* grammar for 601628. All seven remain **HERO_SANKEY_UNIFIED_OTHER_FIGURES_LEGACY** because their remaining original figures are not entirely ported. Three V10 issuers have connected income Sankeys and one has a legal signed alternative. Strict eleven-full-report visual/editorial unification **NOT_ESTABLISHED**; independent human signoff, current Cloudflare candidate HTML SHA and unseen period generalization **NOT_CHECKED**. Old "four fully legacy" and "seven fully legacy" text below is historical, not live instructions. Requery [machine census](scripts/audit_unified_visual_corpus.py) and [PR handoff](docs/ACTIVE_PR35_HANDOFF.md); do not mix insurer management premium with CAS25 service revenue.


**2026-11-07 active PR #35 optical visual migration (candidate only):** The original-source income hero Sankeys in 300394, 300502 and 300308 now use the shared v9 connected source→single total→own disclosed COGS/GP renderer with independent 1100 desktop/330 mobile. [Real 3-company CJK Chromium, original source and export QA](https://github.com/kobolibra/financials/actions/runs/42359062392) PASS. The 300308 original p139 repeated column 1-CNY discrepancy stays visible. These reports are *partial hero-only*, their other graphics are still old V7; other four sectors 688220, 600900, 600276, 601628 have not migrated. Full 11-issuer editorial design, human blind review, unseen periods and current production release are NOT_ESTABLISHED. Treat earlier "seven legacy companies" references as historical; use [current machine census](scripts/audit_unified_visual_corpus.py) and [active handoff](docs/ACTIVE_PR35_HANDOFF.md).


**机器真值：先读 `project-status.json` 与 `site/research_catalog.json`，后按 `docs/ACTIVE_PR35_HANDOFF.md` 核对实时 GitHub 主分支和 PR；不要把 PR 预览当正式生产。**

## 2026-11-07 · v9.0.0 统一质量系统（候选 PR #35，非 main）

立即阅读 [统一图形设计与一手 AEI 比对](docs/UNIFIED_FINANCIALS_VISUAL_STANDARD.md)、[PR35 零记忆交接](docs/ACTIVE_PR35_HANDOFF.md) 和 [精简执行 Skill](skills/ashare-financial-storytelling/SKILL.md)。原始 v8.8 大段历史说明已归档，不允许作为今天的最新执行指令。新非负财务桑基统一由 research/shared/unified_income_sankey.py 输出单一营业收入合计节点＋合法成本/利润；银行、集团毛利和负利润使用不同的合法语法。**十一家公司标准一致的目标≠十一家公司都已完成迁移，未迁移的七家必须写 LEGACY_NOT_UNIFIED。** 本次新图须重新通过原始 PDF/HTML SHA/浏览器/Cloudflare 才能认证；独立财经/视觉总编仍未审核。



## 2026-11-07 活动候选 PR #35：研究深度、真实桑基和严格零记忆交接

**先判定 main 与候选分支，禁止混淆已发布内容和未合并质量改进。** 最新审查工作见 [候选真实交接](docs/ACTIVE_PR35_HANDOFF.md)、[研究与 AEI/FT 质量评分合同](docs/AEI_RESEARCH_EDITORIAL_SCORECARD.md)，机器可检状态 research/quality/active-pr35.json。PR [#35](https://github.com/kobolibra/financials/pull/35) 使用 quality/aei-sankey-source-contract-v1；开始新会话必须重新查询 GitHub main/PR HEAD 和每项 Actions 的准确 SHA，而非引用这段日期快照。

四家公司候选的原始 PDF 账目、Type A/B/C/BANK、36 张完整独立手机图有前一轮证据；**本次新改 WPS 1040px 真三阶段桌面财务桑基与茅台 −0.1245 亿负毛利的独立尺度放大必须重新重建、截图与真实预览字节审查，先标 PENDING_RETEST，不引用旧截图为新图证明。** 运行 python scripts/check_pr35_quality_handoff.py 验证网页、重建元数据与浏览器回执是同一 SHA。独立人类财经与艺术审稿、跨公司新期稳定性和正式生产新版本仍 NOT_CHECKED。项目真正的高质量交付不等于 CI 绿灯。



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
