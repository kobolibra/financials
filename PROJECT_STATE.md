# Financials in Visuals — ACTIVE PROJECT STATE

**状态日期：2026-11-03。生产分支：`main`。现行入口：[START_HERE.md](START_HERE.md)。机器状态：[project-status.json](project-status.json)。**

> **唯一网站：八家公司的同一研究库，严格的翱捷科技新版桑基几何已在真实 Cloudflare 浏览器运行 [41667952839](https://github.com/kobolibra/financials/actions/runs/41667952839) PASS；完整财报附注与独立审稿仍 NOT_CHECKED。** <https://financials-in-visuals.pages.dev/>。不是四家公司 v9/v10 独立站点，更不是 `research-lab` 里的工程样本。

## 2026-11-03 · CURRENT: Skill v8.4.2-RC1 · 第 N 家独立质量合同与源→出版一致性

**实际已合并的 Skill（三次小步迭代）：** [PR #9](https://github.com/kobolibra/financials/pull/9) v8.4.0 merged `ffb57ac6142546a66233fa01741b54812422f40e`；[PR #10](https://github.com/kobolibra/financials/pull/10) v8.4.1 merged `d0eed02f7c3bb5bdffb3cb7cea6f4620d0e1bc96`；源账本真实内容修复 `f1e2343cb0b4c76d68b2c386218dde7a3d5bd403`；[PR #11](https://github.com/kobolibra/financials/pull/11) v8.4.2 merged `c2c8b15ab67cb91770b0e04818b181d38f567cfa`。**PR #11 真实 CI**：[41668925315](https://github.com/kobolibra/financials/actions/runs/41668925315) 交接/源与 20 个恶意反例 PASS，[41668925267](https://github.com/kobolibra/financials/actions/runs/41668925267) 统一目录本地 QA PASS；**main** [41669011190](https://github.com/kobolibra/financials/actions/runs/41669011190) 交接 PASS。合并后的最新版公开站点核验 [41669011093](https://github.com/kobolibra/financials/actions/runs/41669011093) 及既有网址 [41669011100](https://github.com/kobolibra/financials/actions/runs/41669011100) 在此交接快照时仍在运行（**NOT_CHECKED 正在运行**），前一个 main 确认在线新版几何 [41667952839](https://github.com/kobolibra/financials/actions/runs/41667952839) 已 PASS。**当前有效的 v8.4.2 执行状态以最新 main + Actions 为准，不应据本段假设后续运行已完成。**

- **已有可复现自动化（不是口头方案）**：`scripts/check_release_contract.py` 在同一八家公司统一目录 `site/research_catalog.json` 上查每家新公司（原七家的历史欠账固定豁免，绝不扩张）的 `research/issuers/<code>/release-gates.json`；实际 PDF 字节、SHA/大小/魔数、Source Ledger 公司/期间/金额单位/物理页、Figure Briefs 事实 ID/来源哈希/原始分析问题、行业会计类型、个人审核与实时 Cloudflare 独立三态。不允许未经登记的新发行人通过；源限制预览不是研究全认证。
- **实际反馈→测试**：`skills/ashare-financial-storytelling/quality-regressions.json` 当前 11 个真实根因/修复/可执行标记（旧错误 p87 期别错列、跨轴加总、负毛利假流、微小来源节点放大、桌面图内隐藏、Cloudflare 滞后、账本哈希陈旧、Figure Briefs 借用事实、银行保险工业会计等），涵盖**单公司证据与跨发行人机制分级**；`scripts/test_check_release_contract.py` 已加入额外两项对原始来源说明／披露数值恶意篡改、而已发布 HTML 仍旧的测试，PR #11 的自动检查实际执行并通过；该 PASS 只证明结构性防线，不代替实图专业审美或原报告每一单元格的人工判断。
- **真实被 CI 抓住的 v8.4.1 回归**：[41667517537](https://github.com/kobolibra/financials/actions/runs/41667517537) **FAIL**，公司财务算术29项、浏览器三屏均 PASS，但源 `source-ledger.json` 的 `source.reason` 随新哈希说明被改，真实已发布 `public/688220.html` 的内嵌原始账本仍是旧说明，导致独立重建逐字节比对失败。已**从真实源账本修复**：保留验证过的完整 PDF 镜像 SHA `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc` 与镜像状态、将 `reason` 恢复成已发布且仍准确的原文，**不更改公司财务金额或已发布 HTML**。新回归会比对所有内嵌 `ledger-data` 的原始 `issuer/source/facts/segments` 字段，禁止下一家公司在重建时才暴露问题。
- **最新实际 QA 证据**：源账本修复后 [41667953097](https://github.com/kobolibra/financials/actions/runs/41667953097) **PASS**（完整 PDF/29 会计检查/九图原始渲染/真实1440、768、390/干净再次生成与已发布 HTML 逐字节比对）；真实 Cloudflare 八家公司目录与翱捷科技新四源节点金额几何 [41667952839](https://github.com/kobolibra/financials/actions/runs/41667952839) **PASS**；主分支交接 [41667952648](https://github.com/kobolibra/financials/actions/runs/41667952648) **PASS**。该线上 PASS 证明确实检查到了上次旧版没有的细来源节点，但**不能**冒充完整重大附注、独立金融/视觉研究编辑审查或整个 A 股行业的验证。
- **未解决 P0/P1 数据问题明确保留**：688220 p.137 应收集中度披露 90.50% vs 简单导出89.17% 分母 **FAIL**，p.179 剩余履约义务分类差 0.01 元 **FAIL（披露取整的有界例外）**；上交所官方 PDF 与归档镜像字节完全一致 **NOT_CHECKED**；全部重大附注完成复核、外部8–12季度/可比/估值、第二名真实独立研究员 **NOT_CHECKED**。这批工作没有以新文档替代这些需要原报告的深入追证。
- **真实公司目录/出版产物**：仍仅原八家公司+已有光通信专题，所有既有独立 URL 保留，未修改 `public/*.html`、未另起入口。未来新公司必须从原始 PDF → 行列和三表/附注 → 研究主线与反例 → AEI/FT 原创图形 → 截图 → 本地重建 → 本次 Cloudflare 逐级通过，并将所有失败转化为真正可运行的恶意回归，最后更新现行此文件和机器状态。精确协议见 [docs/SKILL_EVOLUTION_PROTOCOL.md](docs/SKILL_EVOLUTION_PROTOCOL.md)。

## 2026-11-03 · 历史故障复盘：桑基真实比例与早期 Cloudflare 旧版发布阻断（现已解决）

**以下 FAIL 是旧提交、旧检查时点的真实历史记录，必须保留作反例，不代表此刻的线上状态**。后续严格真实站点检查 [41667952839](https://github.com/kobolibra/financials/actions/runs/41667952839) 已 PASS，参见本文件最顶部 CURRENT 状态；不可重复将旧 FAIL 当成最新项目结论。

- **实际源工程已合并 `main`**：修复来自 [PR #8](https://github.com/kobolibra/financials/pull/8) 的提交 `3a1878fa127eb8f757d1da1b68c5d8c1985b0ec0`。原有九张独立财务研究图、全部八个公司独立 URL 保留，原七公司 HTML 没有被改写。主版本是 `public/688220.html`，源头是 `research/issuers/688220/report-template.html` 与 `publish.py`。
- **真正的 AEI/FT 图形错误**：旧版 p.178 “测试服务与其他”收入 79,769.92 元在桑基里按金额计算只有约 **0.011 SVG 单位**高，但来源节点 `span<1` 被换成固定 `stroke-width=1` 的线，视觉放大约 92 倍（流向 ribbon 原金额未变）。现移除最小 1px 线条，四类来源全按真实元金额构成节点，七条真正有金额的成本/毛利 Ribbon 与一条 **零毛利、零正面积**分流均如实处理。所有来源/终点源标签、期间、物理 p178、金额与图形几何有独立 browser 校验，不能只将 `data-value` 当成可视比例的证据。
- **桌面阅读修复**：原收入桑基 SVG 1190px，现金及资产负债图 1100/1090px，桌面 figure 可用区域约 1060px，虽然整页不溢出却会让部分成本/利润终点隐藏于图内滚动。上述三图现改为 1050px；Playwright 在 1440px 逐图强制内部 `scrollWidth <= clientWidth + 2` 并检查 SVG 文字 `getBBox()` 不出边界；768/390 保留图内滚动并确保第一层结论金额可直接阅读。
- **PASS / 真实运行证据**：旧完整原始 PDF 镜像 224 页/1,449,510 字节/SHA256 `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`，原始选定 118 项（109 连续文字+9 原单元格坐标）不变；`main` 会计/浏览器重建 [41660215226](https://github.com/kobolibra/financials/actions/runs/41660215226) **PASS**，线上现有 8 公司/24 路径尺寸 [41660215201](https://github.com/kobolibra/financials/actions/runs/41660215201) **PASS（仅已部署旧版的目录/路由层）**，主分支交接 [41660215142](https://github.com/kobolibra/financials/actions/runs/41660215142) PASS。真实 `1440/768/390` + 实图 Path 坐标、四来源、两个终点、零利润、不截断与 SVG 导出完成，21 张新图截图已在 [41659486482](https://github.com/kobolibra/financials/actions/runs/41659486482) 的 artifact 开卷检查。严格 Skill 条款与发布清单同步修正。
- **FAIL / 线上真正阻断**：新增 `main` live QA commit `ac588ebab444ec4510747ddcb46395b397ca9699` 后，[41660682930](https://github.com/kobolibra/financials/actions/runs/41660682930) 在 Cloudflare 线上 `/688220.html` 找不到修复版 `rect.money-source`，说明公网仍提供旧版图形；**LIVE_NEW_SVG=FAIL**，而不是“站点已全新通过”。对应 `3a1878...` 的 **Cloudflare Pages** GitHub provider check 仍 `in_progress`（检查时点），不能对外声称新代码的 Cloudflare 部署 PASS。新上线验收条件不能删除或放宽。
- **线上再次重试仍失败（已真实执行）**：GitHub Actions [41660682930](https://github.com/kobolibra/financials/actions/runs/41660682930) **run_attempt=2** 于 2026-11-03 15:14 UTC 再次结束 **FAIL**，报错仍为 `ASR source amounts not represented as geometric nodes`，证明部署公开页确实未变而非一过性的浏览器等待错误；对应 Cloudflare Pages provider 检查尚无完成结论。不能删掉严格断言来换绿色。
- **NOT_CHECKED / 不得冒充**：上交所官方静态 PDF 服务器与已核镜像的字节同一性、全部 224 页重大附注完整独立逐项复核、8–12 季度真实同行/估值、第二名真正独立人类财务或视觉审稿人；应收及合同资产附注集中度 p137 披露 90.50% 与简单披露分母回算 89.17% 仍 **FAIL_UNRECONCILED**，待履约义务 p179 明细相加比披露总额多 **0.01 元**，没有编造补差额。
- **此历史阻断已关闭**：后续真实 Chrome/Cloudflare 严格检查 [41667952839](https://github.com/kobolibra/financials/actions/runs/41667952839) 在八公司×三视口检验新版四个 `money-source`、7 条真实流带、极小源金额、零毛利和桌面图内不裁切 **PASS**。依然要求每个未来新 `main` 的部署重新验本次精确版本，不能用这次的通过替代未来所有提交。

## 2026-11-03 · 九图正式版增量原始 PDF 行列证据与图形通用财务关系

以实际 main 九图、Skill v8.3.3-RC1 为基准；不将旧开发八图版本覆盖九图发布页。原始 224 页 PDF 副本 SHA256 `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`，1,449,510 字节。交易所源文件 vs 镜像原字节同一性 NOT_CHECKED。

**原始源页重点**：`research/issuers/688220/source-cells.json` 定位 p.135 应收坏账准备，以及 p.146 八项库存原值、跌价、库存商品、委托加工及履约成本，包含原始 PDF words bbox、行名、列标题、2025-12-31 或 2026-06-30 日期。`verify_pages.py` 在完整 PDF 原字节直接复原，109 项连续原数字 + 9 项物理单元格 = **118/118 选定原金额可定位**。仍保留 p.87 上期列 15.30 元营业外支出的 x 坐标、本期空格核验。绝不等于全部 224 页重大附注独立全文审阅。

**可重用守恒与反例**：`research/shared/conserved_flow.py` 和 `research/shared/test_conserved_flow.py` 是一个源分类关系内核，要求同一分类轴、原币种、同合并期间、原始物理页，精确 Decimal 验证四类来源→成本/毛利，七条非零带与一条真实零毛利（不捏造可见面积）。八种故意错误的源关系必须被拒绝。单公司实例和合成反例并不认证跨行业 Level 2/3。

**旧目录元数据修复**：`site/research_catalog.json` 中 688220 原留七图，当前正式研究正文和 `figure-briefs.json` 为九图，已纠正为九图并用唯一 `site/portal_builder.py` 重新生成原 `public/index.html`；原七公司 HTML 未改动。

**独立门槛**：PDF 镜像 SHA、指定源金额/源格、三报表/全部 17 CFO 会计身份、九图本地源表、真实浏览器响应式分别 PASS（在对应运行的确切 SHA 上）；原 p.137 应收及合同资产集中度披露 90.50% vs 直接重算 89.17% 仍 FAIL_UNRECONCILED，p.179 RPO 拆分 0.01 元不闭合；SSE 与镜像原字节一致性、完整附注系统审阅、外部估值及第二名独立人类财务／设计审核 NOT_CHECKED。正式 Cloudflare 需以合并后最新 commit + GitHub Actions 真实八公司导航和 1440/768/390 为准，绝不从分支成功推定线上成功。

## 2026-11-03 · 现行正式状态：AEI/FT 源证据重构已上线；财务源边界仍明确保留

**唯一正式站点**：<https://financials-in-visuals.pages.dev/>，目前八家公司**在同一个**目录下各有完整独立 HTML。翱捷科技-U 688220：<https://financials-in-visuals.pages.dev/688220.html>。没有新增另一版四公司入口、没有改写旧七家 HTML。本次 AEI/FT 重构已通过 [PR #6](https://github.com/kobolibra/financials/pull/6) 合并真实 `main`，研究/HTML 源提交 `5f2cf82cd515e5e85a8a41a93ab4bcc0f10554d8`，Skill 为 **v8.3.3-RC1**。主分支新发布回归适配提交 `f9f3ac4377c98fb5d9390716531c023a4def1393` 与 `52c4a6f166451ef3a132f929ab1e776a1521e130`。

**真实执行并非口号**：从 `research/issuers/688220/source/688220_2026H1_20260829_original.pdf` 完整 PDF 镜像字节（2026-08-29，2026H1，224 物理页，1,449,510 bytes，SHA-256 `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`）读取合并三表、原始业务收入/成本及现金流全 17 条 signed 调节。4 类互斥业务来源分别以**其自己的 p.178 原始成本和推导毛利**绘制真实比例尺分流（四条正成本 + 三条正毛利；测试服务真实零毛利不制造假流量）；另有完整毛利→法定净利润 signed CAS 瀑布，以及共同金额尺度两期资产＝负债＋权益存量组成。总共九项不同研究问题、九张原始证据表与手机端独立数字结论，这些数目只表示技术覆盖而非审稿认证。逐图独立研究契约：`research/issuers/688220/figure-briefs.json`；发行人独有研究：`research-memo.md`；可重建 HTML：`public/688220.html`、`report-template.html`、`publish.py`。研究依 Skill v8.3.3/完整研究手册 01–05，重构实际插图和原文均已在本会话打开检查。

**本轮最关键的已解决源问题**：原始 PDF 物理第 87 页 `减：营业外支出 15.30 元` 在 **2025H1 对比右列**，**非 2026H1 本期**；本期该格空白，经营利润 54,945,406.18 + 营业外收入 256,125.37 = 税前利润 55,201,531.55，故本期贡献为**推导零，非发行人披露的 0.00 元**。旧账本错列已直接更正到 `source-ledger.json` 和 PDF 物理 x 列核验 `verify_pages.py`，完整带符号 P&L 测试使该错误显现并在真实发布前修复。只在同一页找到金额绝不等于行列语义检验。

**实际核实的 GitHub/Cloudflare**：

- 完整源/会计/SVG/移动端分支 [41652625378](https://github.com/kobolibra/financials/actions/runs/41652625378)：**PASS**，含 `scripts/check_handoff.py`、同目录单测、PDF SHA、原始 p.87 列坐标、29 项元精度身份、8 项 hostile 错误注入反例，9 图/9 证据表/21 张 1440/768/390 实截图及 3 SVG 导出，干净重建位对位一致。
- 新版主分支源财报与离线浏览器 [41653197855](https://github.com/kobolibra/financials/actions/runs/41653197855)，SHA `f9f3ac4377c98fb5d9390716531c023a4def1393`：**PASS**。
- 八家公司统一目录 **真实 Cloudflare 公共页面** Chromium 导航和三尺寸 [41653304202](https://github.com/kobolibra/financials/actions/runs/41653304202)，SHA `52c4a6f166451ef3a132f929ab1e776a1521e130`：**PASS**；原七家旧 URL 未改。
- 主分支 Skill 与交接 [41653016658](https://github.com/kobolibra/financials/actions/runs/41653016658)：**PASS**。最初主分支运行 `41653016669` 与 `41653016654` 曾因**测试仍硬编码七图**失败，现已直接修改测试为按图形 brief 动态计数，重新实际通过，不掩盖失败历史。
- 本会话 web 抓取对 Cloudflare 页面返回访问限制；以上 LIVE PASS 特指 GitHub-hosted Chromium **真实线上浏览器访问**，不是当前 web 工具自己直开成功，也不是人工独立设计编审签字。

**两套研究+视觉质量门槛并列，不能合并**：

| 门槛 | 当前实况 |
|---|---|
| 完整 224p PDF 镜像 SHA + 报表期间 | **PASS** |
| 上交所服务器原 PDF vs 归档镜像逐字节完全一致 | **NOT_CHECKED**（交易所静态主机返回挑战/无法取到完整 PDF 字节） |
| 重大原始行列语义 | **p.87 重大列错 PASS 修复；其他附注 PARTIAL**，9 项 PDF 窄表文字需更大覆盖 |
| 财务精确恒等式 / CFO 全 17 项 / 同维度真实分流 | **PASS**（元精度） |
| 机构级行业研究、反证与现金/资本逻辑 | **PASS 自审源限定研究；外部多年同业/估值 NOT_CHECKED** |
| AEI/FT 真实桑基、signed P&L、BS 语义与实际截图 | **PASS 技术/自审视觉纠错；独立高等级设计编审 NOT_CHECKED** |
| 原始附注 p.137 前五名应收+合同资产披露占比 90.50% 对 p.135+p.138 原值计算 89.17% | **FAIL（边界明确、不能捏造分母）** |
| p.179 RPO 拆分对合计差额 0.01 元 | **FAIL 有界原披露精度，禁做假守恒图** |
| 真实 Cloudflare 八家公司路由 1440/768/390 / 无 iframe | **PASS** |
| 第二位独立人类财务分析师签核 | **NOT_CHECKED** |

**当前发布类别：RESEARCH_PREVIEW / SOURCE_LIMITED**。不将技术通过或九图当作全附注、同行估值、独立研究签核通过。若进一步推进，按原始报告行列直接解决有争议的 p.137 比例分母、p.179 一分钱与剩余重大附注，再增加有真实披露的 8–12Q/同行数据。不能以这些遗留项为借口放弃已能完成的研究或设计迭代。

**当前可再现命令**：

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
