# Financials in Visuals — ACTIVE PROJECT STATE

**2026-11-13 新公司真实生产候选：海尔智家600690。** 已取得192页原中报，181条原始/推导事实，23项会计勾稽，12项重大附注主题和12项问题驱动财务图；真实三屏与36次当前SVG下载通过。目录扩至12家；新图全部进入同一强制质量合同及自动源码重建，原11家公司文章保持原字节。当前新公司尚未合并上线，不借用旧Cloudflare绿色；人类二审、8–12季度同行估值仍单列未完成。见 `research/issuers/600690/release-gates.json` 与 `publication.json`。

**2026-11-13 已合并并核验正式站：七个历史系列的完整财务图已统一。** [PR #66](https://github.com/kobolibra/financials/pull/66) 合并源码 `5346ff0`；三家光通信、翱捷、长江、恒瑞、中国人寿共65幅源财务图，正式站1440/768/390共21个布局及195次当前可见SVG下载全部通过，线上完整HTML与发布源码逐字节相同。生产证据见 `research/quality/full-figure-production-20261113/result.json`，明确为本地真实浏览器访问正式站；本地源码证据见 `research/quality/full-figure-20261113/result.json`。公共图形核心与行业适配保留原始会计差异；新公司/新期间必须通过目录 `FULL_SOURCE_FIGURES_V1` 进入同一套逐图云端验收。下方旧HERO-only、未合并及权限受阻内容是历史记录，不能覆盖当前字节证据。人类审稿及未见真实财报的长期稳定性不声称通过。[历史四家合同](docs/ACTIVE_PR35_HANDOFF.md) 保留。


**2026-11-11 当前正式交付（覆盖下方历史候选快照）：** [PR #62](https://github.com/kobolibra/financials/pull/62) 已合并并正式发布，内容主分支 `e72bae81a9df22f54db7ba365f25bb8160c34111`；[PR #63](https://github.com/kobolibra/financials/pull/63) 已合并，修复新版研究附表、ASR隔离验收数据和保险累计桥的三处旧验收规则，主分支 `9101d76b178d50c8f76b9ffbb03b769c9ff5b6e4`。正式站11篇报告整页字节与源码一致，Chromium/WebKit共108次真实SVG导出通过；33屏/315图形观察未发现新阻断。11家132项重大附注主题经独立AI二审，3家24个连续单季/96项差分、41份官方PDF、3家同行及三季报反证已写入正文。美的依据物理p171附注46的自身成本改用Type A；银行利润桥及保险五幅累计桥按原金额验证。GitHub连接已恢复，验收规则成功更新，先前“权限不足未启用”是历史状态。真实线上证据见 `project-status.json.current_release_provenance_20261111` 与各发行人 `live-release-receipt.json`。独立人类签署未声称；原披露矛盾仍公开，三家跨期样本不能外推全行业泛化。 [历史四家交接](docs/ACTIVE_PR35_HANDOFF.md) 保留为历史证据。


**2026-11-11 current PR #62 source candidate:** All eleven source publishers now include the 132-theme independent-AI material-note review, with source exceptions visible; three cases add 24 single quarters/96 differences, 41 official PDFs, three peers and actual Q3 thesis tests. Midea note46 physical p171 proves own costs: TYPE A now replaces the historical TYPE B snapshot. Insurance five mobile bridges and bank source-to-parent bridge are truly cumulative; native fonts improved. New all-library checks use `delivery_quality_suite.py` through the existing two-sector workflow entrypoint, so the earlier missing-workflow-scope blocker is superseded. Current local same-source 33-view/315-figure matrix has zero blockers; cloud on the new head and production promotion remain pending until actually verified. [Historical four-issuer contract](docs/ACTIVE_PR35_HANDOFF.md) remains linked, not current deployment authority.


**Workflow activation boundary:** GitHub rejected the new Actions file because the current credential lacks workflow write scope. The complete candidate remains reviewable at `docs/ci-candidates/verify-comparative-economics.yml`; it is NOT active CI. All 2026-11-10 PASS claims below are local tests/browser observations, not remote Actions or deployment.

**2026-11-10 local quality candidate, unmerged and not deployed:** Main reviewed at `2478b37dac358b3c96fd37aa0ba88ec5364ebef5`. Three original-PDF-bound comparative GP analyses (600900/600276/688220); native tablet repairs (600900/600276/601628); stricter Sankey identity/cost/zero guards; four V10 original-PDF rebuilds repair negative label collisions and minimum-width cash distortion. Current full-catalog browser evidence: `research/quality/delivery-20261110/result.json`, 33 article viewports, 315 figure/panel observations, zero blockers, nine actual economics SVG exports. Seven partial-hero families remain partially migrated. Independent finance/art, complete material notes, unseen real multi-period panel and new Cloudflare live SHA remain NOT_CHECKED. See `docs/QUALITY_REVIEW_20261110.html` and `project-status.json.quality_upgrade_20261110`. The historical four-issuer source/artifact contract is linked in [ACTIVE_PR35_HANDOFF.md](docs/ACTIVE_PR35_HANDOFF.md); it does not replace this current candidate state; historical production receipts below remain bound only to their actual old SHA.


**2026-11-09 最新已验证线上记录（源码精确对应，不外推未来提交）：** PR [#54](https://github.com/kobolibra/financials/pull/54) 已合并，长江电力 600900、恒瑞医药 600276 的 390px 真实金额守恒桑基来源名称、金额/毛利率改为更清晰的分行排版，并按真实 Noto CJK 字符边界修正行距；PR [#55](https://github.com/kobolibra/financials/pull/55) 修复了 GitHub 主分支与 Cloudflare 已发布字节不同步时的 fail-closed 门禁。主分支 `b72e6074795bc0cb9aabe0b312c79f1decf567f4` 经 [Cloudflare 正式站 11 路由、原始整页 SHA、1440/768/390 中文浏览器验证](https://github.com/kobolibra/financials/actions/runs/42599056086) PASS。对应源 HTML SHA：600900=`cf18a4e1ff655d989d439bb16a0684adeff9a300d46ca6a892aef86284680f88`，600276=`9a51d251d271a6dc7803c4036c71a441634ef784258aabaf85e97d1081962d99`；冻结截图及现场证据 artifact `13664069157`。发行人 `release-gates.json` 和 `live-release-receipt.json` 只能以这份真实线上回执晋升，不能用先前线上版本伪装成新版上线。详细机器源见 `project-status.json.current_release_provenance_20261109`。**此验收仅涉及两家具体已取证财务图、页面及指定数据；11 家全篇研究审美、跨期/同行、材料附注完备性、独立金融研究与视觉审查依然 NOT_CHECKED。**

## 2026-11-09 主分支真实增量（下文历史段落不是当前候选指令）

**2026-11-09 可审计增量（PR #50–#52 已合并）：** [PR #51](https://github.com/kobolibra/financials/pull/51) 将长江电力 600900、恒瑞医药 600276 的桌面/手机经营图改为原始来源类型化驱动，剔除硬编码发电量/创新药值、禁止商品子集与 RPO 错误加总；[PR #52](https://github.com/kobolibra/financials/pull/52) 将两家可复算同比决策板块真正写入公司 HTML（原始元额、页码、反证，不宣称经营因果）。在历史 main `328ce615557390f1f0a52611496032557e87800a` 上，真实 [Cloudflare 11 路由 / 1440、768、390 CJK、全文 HTML SHA](https://github.com/kobolibra/financials/actions/runs/42595318738) PASS；本次发行人 receipt 与 release-gates 采用同一当次真实证据。交接另见 `project-status.json.current_release_provenance_20261109`。**十一家全篇顶级审美、全部重大附注、跨期和同业因果、独立财经/视觉双审仍不是通过状态。** 每次必须重新查询当前 GitHub HEAD 和生产文件 SHA，不能把历史 PASS 当未来 PASS。

## 2026-11-07 latest source-of-truth PR #35 (supersedes the dated historical snapshots below)

**Actual eleven-company report status:** V10 688111/000333/600036 positive source-money Sankeys and 600519 lawful signed alternative; **seven** historically different publishing families (300394/300308/300502/688220/600900/600276/601628) now use shared native desktop/phone original-yuan financial *hero* diagrams. China Life's 601628 premium is a distinct old-management-statistics 4→new/renew→premium-total graph, NOT CAS25 insurance service revenue, profit or CFO. Full source PDFs/typed facts and real 1440/768/390 Noto CJK Chromium checks as referenced from [the current zero-memory handoff](docs/ACTIVE_PR35_HANDOFF.md); strict PR-only SHA release gate has separate proof from historical production. **Every one of the seven former legacy families remains HERO_SANKEY_UNIFIED_OTHER_FIGURES_LEGACY:** remaining P&L, cash, stock and operating-driver designs have not all been migrated to the one editorial visual treatment, so full-11 aesthetic, independent second human finance/art review, unseen 20–30 issue/period sample evaluation, latest same-SHA Cloudflare live and production merge remain NOT_ESTABLISHED / NOT_CHECKED / NOT_DEPLOYED. Read the current on-disk census `scripts/audit_unified_visual_corpus.py` and `project-status.json` before citing status. Previous “only four active” and “seven fully legacy” paragraphs below are **dated historical checkpoints** superseded here.


## 2026-11-07 v9 production Skill + AEI first-party reference: unified visual grammar candidate

**Canonical Skill is now v9.0.0, compact mandatory control plane, not 125 KB historical append-only narrative.** Full historical v8.8 is preserved at docs/history/ASHARE_FINANCIAL_STORYTELLING_SKILL_V8_8_ARCHIVE.md. One legitimate industry-aware positive income Sankey engine is research/shared/unified_income_sankey.py, adapted by research/rebuild-v10/unified_finance.py, with own cost/GP Type A, group-only Type B and bank net-income business rules. TYPE C negative income / stock or crossing remains a signed independent figure. Both desktop/mobile connected Sankeys must show ONE actual group income node; all money must reconcile exact Decimal yuan. See docs/UNIFIED_FINANCIALS_VISUAL_STANDARD.md for first-party App Economy Insights structural benchmark, original colors, reader labeling and **11-company honest migration matrix**.

**IMPORTANT: only four V10 candidates are being actively migrated to this engine.** The other seven are LEGACY_NOT_UNIFIED until their original-source authoring pipelines actually consume the common design. Do not use passing old site CI to claim 11 unified. Any changed candidate HTML MUST be regenerated from original PDFs and verified with same source SHA at 1440/768/390 and real preview; older screenshots do not transfer. Production main remains separate; independent finance and editorial 5-second review and multi-period generalization remain NOT_CHECKED.



## 2026-11-07 候选 PR #35 ACTIVE，main 仍不同：图形与交接品质整改

**新候选真实 SHA 验证已闭环**：原始财报重编与 36 图 CJK 三屏 [#42347332430](https://github.com/kobolibra/financials/actions/runs/42347332430) PASS；真正新图所对应的 Cloudflare HTTPS 预览 11 路由全文字节、16 档浏览器/设备视口、108 次 SVG 真实可见版本导出 [#42347520600](https://github.com/kobolibra/financials/actions/runs/42347520600) PASS。四公司 source HTML SHA 收在 research/quality/active-pr35.json 和 build-manifest.json（注意不是新 main）。零记忆交接与四家图形财务红队通过的准确 CI 以 PR 最新 HEAD 查询，不用旧会话声称。独立财经/视觉总编与跨期陌生公司稳定性、生产 main 新 HTML 仍 **NOT_CHECKED / NOT_DEPLOYED**；此段证明候选工程质量，不证明超越 AEI。


**权威实时状态入口 [docs/ACTIVE_PR35_HANDOFF.md](docs/ACTIVE_PR35_HANDOFF.md) + [research/quality/active-pr35.json](research/quality/active-pr35.json)**。PR #35 quality/aei-sankey-source-contract-v1 正在改造四家 2026H1 报告；本段只是带日期候选快照，新会话必须重新查 main、PR HEAD、Actions 和 Cloudflare 全 HTML SHA。正式 main 的四篇旧页面不可因为 PR 预览成功就写为正式生产已修。候选会计路径金山办公 A（自身收入/成本/毛利）、茅台 C（真实小负毛利不画正向带）、美的 B（仅集团总毛利）、招商银行 BANK（净利息已减息）各不同。

**本次新实装修复尚须新 SHA 实测**：金山 WPS 独立 1040 单位的原元三阶段桌面收入→自身成本/毛利→集团合计桑基，手机 330 单位独立；茅台 −12,446,319.42 元其他业务真正极小主比例正负图＋明确独立尺度的收入/成本局部放大，机器内部原因只保留 SVG 属性。针对这两种误导图已加源金额的对抗测试，但旧浏览器成功记录 #42344600791、#42344715944 只证旧候选 SHA，**不得继承到新改网页**。本次分支变更以实际 HEAD 及最新 CI 为准，不能写本地截图成功如未执行。

**持续高质量审核未完成**：另一期/另一公司跨行业无代码特例复现、20–30未见样本、完整重大附注、独立机构分析师和视觉总编五秒盲评、真实实体移动设备与合并后主站新 SHA 都 NOT_CHECKED。机器代码 scripts/check_pr35_quality_handoff.py 与 python scripts/check_handoff.py 的双门必须在真实生成回执一致后 PASS；研究深度边界与明确经济命题见 docs/AEI_RESEARCH_EDITORIAL_SCORECARD.md。跨轮交接需要更新机器状态和真实 HTML SHA，不可依赖前一次对话记忆。



## 2026-11-05 · ACTIVE MAIN: AEI/FT v8.8 实证视觉编审与真实财务流语义引擎已合并（不冒充修好四旧页）

- **当前可复验main** `37ab35fd4c861b60ed65536e072b5aa6fa8b7ba8`，同一个11家目录无增删，11篇独立已发布HTML/所有原始PDF及发布器**本轮未变更**。PR [#33](https://github.com/kobolibra/financials/pull/33) 的方法标准、静态视觉失败检查及恶意用例，PR [#34](https://github.com/kobolibra/financials/pull/34) 的原始元级A/B/C流向会计语义执行器 `research/shared/editorial_financial_flow.py` 与十项基于实际账本/恶意会计情形的测试均已经合入。报告级「稳定顶级审美」「全面超越AEI」**仍未被证明**。
- **对应真实Actions**：PR #33 最终旧四FAIL被真实读出的视觉策略 [#41968781177](https://github.com/kobolibra/financials/actions/runs/41968781177) PASS（策略识别而非四页修复），候选交接 [#41968781200](https://github.com/kobolibra/financials/actions/runs/41968781200) PASS；PR #34 [#41969451617](https://github.com/kobolibra/financials/actions/runs/41969451617) 中 `Test exact-Yuan source/type/negative/segment financial flow semantics` PASS；正式main新语义 [#41969534693](https://github.com/kobolibra/financials/actions/runs/41969534693) Skill+交接 PASS。PR#33 合并后原11家实际云端入口/路由 [#41968932787](https://github.com/kobolibra/financials/actions/runs/41968932787) PASS（未改变公司HTML，本次非新的视觉审美认证）。
- **确切新会计/视觉区分**：688111金山办公真实账本有WPS个人/WPS365/许可/其他**各自**收入与成本，不能再将只到集团COGS/GP的B图当成A业务利润；600519贵州茅台「其他」原收入低于原成本，不可画正毛利飘带；000333美的工业三组仅集团统一成本时可承认真实B图却须突出 `PRODUCT_LEVEL_GP_NOT_ESTABLISHED`。新增校验同时拒绝期别/并表/货币混合、父子收入重复、未披露差额被当业务、银行净利息二次扣息、保费充CAS服务收入。此合同现已在CI执行，但旧V10出版器没有消费该模块，**不能称相关四页图已升级**。
- **剩余P0具体源头**：V10旧图 `research/rebuild-v10/publisher.py` 的390手机规则隐藏非桑基SVG、唯一桑基850px横滑；四家公司 `600036/688111/600519/000333` 的生产财务图 **FAIL**；旧V10工作流 `sw>cw` 的反向验收仍未修。须先修公司对应真实图源生成器、对负数选择有符号瀑布/移动原生图，不得直接靠CSS把850px缩成5px中文或假扮图已修；必须跑原PDF/真实业务口径和1440/768/390每图审美截图，重新Cloudflare同HTML SHA双页面验证。独立第二人类审稿/完整重大附注与外部8–12Q同行仍NOT_CHECKED。


## 2026-11-05 · ACTIVE MAIN SOURCE AUDIT / AEI-FT financial editorial v8.8 candidate, not a fixed four-report website

- **本轮用户暂停新公司研究，要求现有Skill与11个已发布公司的机构研究/财经信息设计深度审核**。开始时真实GitHub main=b0b7087a8bd06177512de1f6bb2a574f9461cbe0；11家公司唯一目录、原Skill v8.7.5全文/五研究手册及原交接均在本次会话核对。公开AEI三张报表及6图、Alphabet公开可看部分与FT关系语法对照，付费完整图不可冒称已看。
- **根因**：实际 research/rebuild-v10/publisher.py 的手机CSS在390px直接隐藏全部非桑基SVG，剩下桑基min-width:850px且内滚；.github/workflows/verify-v10-sankey-research.yml旧浏览器assert要求内部滚动才算PASS。明确现有四家600036、688111、600519、000333移动财务图FAIL，非会计CI绿色或数字列表能改正。现阶段并未修改V10原页面/生成器，不能写已修。
- **方法修正**：Skill v8.8.0-rc1专门加入独立AEI/FT总编门，文件 docs/AEI_FINANCIAL_VISUAL_EDITORIAL_STANDARD.md：Type A逐来源自身成本/毛利真实加权桑基、Type B仅集团毛利必须显性PRODUCT_LEVEL_GP_NOT_ESTABLISHED、Type C跨组/负数/异口径弃流并使用合法符号/存量对照。仍需逐图在真实公司财报内执行，不能只靠文字。
- **实际新增回归代码**：scripts/audit_aei_editorial_delivery.py 读取独立HTML真实字节检查隐藏非桑基图/850px小窗/缺source-table/iframe；scripts/test_audit_aei_editorial_delivery.py 多种恶意反例。默认审计保留四家明确FAIL但仅新额外失误阻断CI；严格 --fail-known 模式四家没修必须红。静态门只能检查源码结构，真实新截图/CJK/金额真实几何/第二人类编辑均 NOT_CHECKED。
- **范围/发布**：本次只变更Skill/研究图形规范/Actions质量门/交接，并没有修改现有11家公司任何原始PDF、账本、图形生成器、HTML，也不新增研究入口。旧7家源版本验收仍以各自历史事实SHA为准。第二位真实独立人类研究分析师/艺术总监、全体重大附注穷尽核查和多季度估值均NOT_CHECKED。
- **当前本轮质量门**：MAIN_START_STATE=PASS；AEI_FIRST_PARTY_PUBLIC_METHOD=PASS_LIMITED_PUBLIC; MOBILE_OLD_FOUR=FAIL；NEW_STATIC_GUARD=CI_TO_VERIFY；SKILL_METHOD_PATCH=BRANCH_TO_MERGE；CURRENT_LIVE_CLOUDFLARE_11_SCREENSHOTS=NOT_CHECKED；HUMAN_INDEPENDENT_ART_AND_FINANCE_REVIEW=NOT_CHECKED。新PR/Actions准确SHA须以新实际结果记录，不能用旧CI替代。
- **下一执行动作**：直接修V10源publisher的8/9/9/10幅财务图手机独立金融图（不是隐藏其余图或把850缩成330小字），移除旧Action反向sw>cw条件，原始4家PDF+账本重跑，真正1440/768/390每图截图与源元守恒/正式Pages双SHA验证才升旧四PASS；检验更深行业利润来源后再评估是否接近AEI的阅读效率。


## 2026-11-05 · ACTIVE INTAKE CHECK: 用户本轮未提供可识别新发行人原始 PDF（非新的已发布公司）

- **本轮启动查验**：实际 GitHub `main` = `b7cf9daf79cb9abda0b6da2a0b85d60f995ff834`；权威 `site/research_catalog.json` = **11家公司**，统一网站独立离线报告，不改既有11家报告、不新建第二入口。已实际获取 START_HERE、project-status、PROJECT_STATE、AGENTS、交接协议、发布清单、现行 Skill v8.7.5-RC1 全文与五册研究手册；抽查 688220 的真实独立 HTML、source-ledger/figure-briefs/release-gates、601628 原始来源账本和统一目录生成器。仓库 Skill **不是自动安装的 ChatGPT 全局 Skill**。
- **本轮输入证据**：本次消息未提供证券代码/公司名称、PDF 附件或完整官方 PDF URL；当前会话附件数为0。Library 可访问的PDF仅识别为已有旧公司或其他项目材料，**不能在未获指定时推断其为本次新公司**。所以 `NEW_ISSUER_IDENTITY=NOT_CHECKED`，`NEW_SOURCE_BYTES_SHA_PAGES=NOT_CHECKED`；无从复核报告期间、合并原表/重大附注或新图金额，禁止由历史候选公司替代。
- **本轮实际最新 Actions**：同一 HEAD 的研究构建 `#41872906405` **PASS（仅既有688220研究构建范围）**、Skill/交接 `#41872906530` **PASS**；统一生产路由 `#41872906424` **CANCELLED**（中文 Chromium 安装阶段被取消，Cloudflare 真浏览器步骤未执行），故当前 HEAD 最新 live 验收 **NOT_CHECKED**。此前 `e63ee316db22d8d079be6a80cd3cd9f08fd1d98e` 的 688220 真 Cloudflare `#41871662195` PASS 只证明该特定已发布 HTML 及其截图与 SHA，**不证明本轮新增公司或当次 HEAD 的未执行 live 检查**。本会话直接访问 Cloudflare 工具报禁止/URL不可达，本地网络 DNS 解析失败；不虚构最新站点截图。
- **现行已知遗留门槛**：原始研究网页 `600036`、`688111`、`600519`、`000333` 的390手机财务图裁切 **FAIL**（未在本轮改动）；688220 p137 应收集中度分母差异及p179 0.01元附注差异仍 **FAIL_BOUNDED**；完整重大附注第二人核查、外部多期估值、独立人类财务和视觉审阅 `NOT_CHECKED`。不以既有通过记录覆盖上述缺口。
- **本轮新发行人独立质量门**：`PDF_BYTES=NOT_CHECKED`; `SOURCE_ROW_COLUMN=NOT_CHECKED`; `ACCOUNTING_THREE_STATEMENTS=NOT_CHECKED`; `RESEARCH_COUNTERCASE=NOT_CHECKED`; `AEI_FT_VISUAL_EDITORIAL=NOT_CHECKED`; `SANKEY_GEOMETRY=NOT_CHECKED`; `BROWSER_1440_768_390=NOT_CHECKED`; `CLEAN_OFFLINE_REBUILD=NOT_CHECKED`; `GITHUB_NEW_REPORT=NOT_CHECKED`; `CLOUDFLARE_NEW_REPORT=NOT_CHECKED`; `INDEPENDENT_SECOND_HUMAN=NOT_CHECKED`。未生成或发布新 HTML，未修改任何已发布公司网页及目录。
- **可执行下一个真实动作**：取得用户本次指定的新公司原始 PDF（上传或给出证券代码+原始完整公告链接），先验证字节、PDF SHA/物理页、公告和修订状态，随后按现行 Skill 创建该发行人源账本/行业会计模型/反证/逐图 brief/独立 HTML，完成三屏和真实 Pages 逐字节验收，再加入唯一目录。此记录只保存真实阻碍和核验结果，不把缺少 PDF 当作已完成研究。每个后续新对话仍须重新核 main、Actions、源字节。


## 2026-11-05 · ACTIVE MAIN: 688220 真正完成独立网站新版发布与逐字节中文三屏核验

**已核对的真实 GitHub main / Cloudflare（不是候选绿灯）**：原研究报告十一家公司统一研究库、每家独立离线 HTML。不另建任何入口，也不更改另十家既有公司 HTML。最新版 688220 研究图像直接以原始元账本生成九幅手机原生研究图；保留原 Desktop 全部原财务 SVG、SVG 导出、附注和逐行人民币元证据表。PR #29 发布正式研究 HTML `dfce7f700997b501cccd230f38925695e39a6e71`；后续 PR #30、#31 只更新真实 Cloudflare 验收程序和严格收据格式，不重写 `public/688220.html`。上一次实际生产核验工作提交 `e63ee316db22d8d079be6a80cd3cd9f08fd1d98e`，最新文档提交以实际新 main 为准。

**真实公开网页来源回放**：[Action #41871662195](https://github.com/kobolibra/financials/actions/runs/41871662195) PASS：`https://financials-in-visuals.pages.dev/688220` 实际最终公司 URL，返回 `https://financials-in-visuals.pages.dev/#companies`，真实 11 个公司路由；公司整字节 HTML SHA `aca567335dbec04d94569bc93a52f207b4b1bacb6b77cb41a3ca5eaae2f5d973` 与 main 源一致，首页 SHA `f625453172a83b7db38d0c5a67ddbecd84fbf078bc9f78c2e20c45b00b23ab41`。真实 Noto 中文 Chromium **1440、768、390** 各捕获首页与 688220 独立公司全页，合计六张真实截图带 SHA/实际字节，长期签名 `research/issuers/688220/live-release-receipt.json`；对应财务与可视化发布门 `research/issuers/688220/release-gates.json`。本地原始源 hostile 8 反例、29 项会计核验、21 张逐图候选实截图、9 张 source/CFO/BS 专业源驱动图、实际渲染源/目标金额权重和带符号累计等比例/中文BBox及 HTML 重建见 [Action #41869385326](https://github.com/kobolibra/financials/actions/runs/41869385326) PASS。

**原始会计来源严格边界**：`research/issuers/688220/source/688220_2026H1_20260829_original.pdf` 镜像 224物理页，SHA `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`；原 p178 四个互斥商品合同组的每笔收入→该组原披露成本+推导毛利，零毛利为零路径，实际比例宽度不膨胀；利润表负数、完整17项间接CFO（原表保留）、现金等价物、资产负债时点对照分别有合法不同图形。**不可消掉的原始报告附注异常仍是 FAIL**：p137 前五名应收+合同资产占比报告90.50%，本研究从p135/p138原金额推导约89.17%，分母未解释；p179 未来履约收入分期合计差 RMB 0.01。上交所官方 PDF 与当前存档镜像的逐字节同一性、所有重大附注穷尽审读、外部历史同行与估值、独立第二名人类研究员或艺术总监签字都仍 **NOT_CHECKED**。工程 PASS 不等于 AEI 品牌背书。

**明确尚未修复的生产站点手机390图内裁切**：四家 `600036` 招商银行、`688111` 金山办公、`600519` 贵州茅台、`000333` 美的集团 **FAIL**。历史旧源10个FAIL的统计是历史源冻结快照；现已真实修复源图的七家包括 300394、300502、300308、600900、600276、601628、688220，不可将旧截图当成最新站点当前全部失败。下一轮根据每家实际原始 PDF 源字节和财务口径选择独立图形，别将银行保费/利息、软件订阅、白酒渠道与电子制造机械套用一个工业CFO公式。600036 现存源建设位于 `research/cases/600036/`，其原247页档案在用户 Library 而非仓库；其他三家源输入在 `research/rebuild-v10/input-ledgers/`，须真实复核而非猜数。

**零记忆复现顺序**：当次查询 main HEAD → 完整 START_HERE / project-status / PROJECT_STATE / AGENTS / 报告发布/交接清单 / Skill 与五册全文 → `site/research_catalog.json` → 原发行人 SHA 与物理页 → `python research/issuers/688220/verify_pages.py`, `python research/issuers/688220/test_accounting.py`, `python -m unittest research/issuers/688220/test_native_mobile.py -v`, `python research/issuers/688220/publish.py --out public/688220.html`, `python research/issuers/688220/qa_browser.py --html public/688220.html`, `python scripts/check_release_contract.py`, `python scripts/check_visual_editorial_policy.py`, `python scripts/check_handoff.py` → 主站 `python scripts/verify_live_688220_native.py` 真实外部三屏及全部公司路径。所有 PASS/FAIL/NOT_CHECKED 分门记录，不能把其他发行人或旧网页自动升级。

---


## HISTORY ONLY · 2026-11-04 snapshot before 688220 actual release (not current)

Real main rechecked: d4ceb34caad00e9adc5088690b6a5b08b475a86b. [Actual production full-byte optical CJK run #41855709571](https://github.com/kobolibra/financials/actions/runs/41855709571) **PASS** all THREE 300394 / 300502 / 300308 standalone real Cloudflare HTML articles, 1440/768/390, 12 published original Chromium screenshots, all 11 issuer routes and return-to-home. Exact complete HTML SHA: 300394 40024eeffb333986549eff6eebb1a532028b4e9cb3354efb2e30676d0687785b; 300502 ccd5a81af61db6924d30cb77c5544df2a8f7e60f00cf148e0ebed8d8ce874367; **300308 now REAL LIVE** dc7231532a39e6d1c4994f26a8c63fce6d6cc49f4a3e0abb926eed45bc721f2e. Home full HTML SHA f625453172a83b7db38d0c5a67ddbecd84fbf078bc9f78c2e20c45b00b23ab41. The older section BELOW saying 300308 production pending was historical BEFORE main release, so must not be considered current.

Original 300308 complete 184 physical-page PDF is archived (2,984,970 original bytes, SHA e0ecd7c365c65e90b1fa4b4616ba3f4649449d64451e0ba0b1b78ba9ce3170bf), 63 original exact facts, 15 signed indirect CFO items. Original p139 duplicate “other business” total +1 yuan contradiction disclosed, not a new business. Three first optical reports therefore no longer have that source-frozen 390 clipping on the current live source. Remaining current-main legacy 390 finance figure failures: **600036, 688111, 600519, 000333, 688220**. The 11-company homepage stays single, other old published HTML source-frozen.

New actual candidate: work/688220-native-mobile-visual-editorial-20261104, Skill v8.7.5-RC1 / VIS-048, second cross-industry original money editorial grammar. Original semiconductor 688220 complete 224-page mirrored original PDF SHA 9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc. New company-specific original source renderer research/issuers/688220/native_mobile.py is embedded by existing publish.py into the SAME offline independent HTML. Exactly nine new 330px company-specific charts on phone/tablet alongside the original nine independently editable desktop SVGs and original source tables: mutually exclusive four product/ASIC/IP/service source→each disclosed COGS+GP at original yuan-proportional Bézier path actual widths; signed GP, full CAS P&L, parent nonrecurring/recurring, 17-row indirect CFO (all source rows remain), signed cash close, same-day asset=liabilities+equity two dates, real business GP money and margin, dated capital stocks. No fake residual business, negative-money Sankey or oversize micro flow.

Actual original 224p PDF page/position and hostile original accounting passes in candidate CI; CJK true 1440/768/390, source path and signed cumulative QA as separate gate must PASS **before** integrating any modified 688220 HTML or recording Cloudflare success. Current production changed article full SHA and live source receipt remain **NOT_CHECKED** until actual main merge and remote browser. Existing p137 AR+contract assets reported top-five 90.50% vs independently recomputed p135/p138 gross denominators ~89.17% is **BOUNDED_FAIL_SOURCE_DENOMINATOR_UNKNOWN**; do not guess or conceal. Human second financial/editorial review, all nonfinancial sector history/valuation and full material notes remain NOT_CHECKED.

Reproduce from verified main: python research/issuers/688220/verify_pages.py ; python research/issuers/688220/test_accounting.py ; python -m unittest research/issuers/688220/test_native_mobile.py -v ; python research/issuers/688220/publish.py --out public/688220.html --qa research/issuers/688220/qa.json ; python research/issuers/688220/qa_browser.py --html public/688220.html --out research/issuers/688220/visual-qa-native ; compare exact independently rebuilt HTML; run scripts/check_visual_editorial_policy.py and scripts/check_handoff.py; then actual public full HTML SHA and all 11 Cloudflare routes/three CJK widths. Candidate source arithmetic / CI is not a human art-director signoff.

---


## 2026-11-04 · ACTIVE FIN-047 original 300308 complete original report 184p, 3-source optical 390 authoring, visually distinctive cash conversion — real Cloudflare third issuer pending

**Current real baseline before this candidate**: main after PR #26 and PR #27 `f1e8bc42b691517e0c1e62b381b924e564a2047e`; PR #26 shipped **300394/300502 exact Cloudflare complete article** 1440/768/390 PASS [#41849552022](https://github.com/kobolibra/financials/actions/runs/41849552022), SHA 300394 `40024eeffb333986549eff6eebb1a532028b4e9cb3354efb2e30676d0687785b` and SHA 300502 `ccd5a81af61db6924d30cb77c5544df2a8f7e60f00cf148e0ebed8d8ce874367`. PR #27 fixed obsolete markup-only CI figure selector without weakening original revenue source/cost/GP; main [#41850299881](https://github.com/kobolibra/financials/actions/runs/41850299881) PASS. Still exact one unified 11 issuer directory and separate offline HTML pages, no iframe, old HTML unaffected beyond those explicit re-releases.

**New third optical 300308 source changes and verified original PDF**: user Library complete PDF `H2_AN202608211828276722_1.pdf` and independent GitHub downloadable original are exact 2,984,970 bytes, **184 physical pages, SHA `e0ecd7c365c65e90b1fa4b4616ba3f4649449d64451e0ba0b1b78ba9ce3170bf`** permanently archived to `research/issuers/300308/original-2026h1.pdf`. Program `research/issuers/300308/verify_original.py` and ledger `skills/ashare-financial-storytelling/v7/examples/zhongji-2026H1-ledger.json`, receipt `research/issuers/300308/source-verification.json` verified 63 actual original report-page source amounts, all 15 original signed indirect CFO rows, financial statement exact equations; actual source archive Action [#41851449349](https://github.com/kobolibra/financials/actions/runs/41851449349) PASS. Original PDF physical p56 income tax value 2,497,175,782.71 (old ledger wrongly p57); p147 deferred income tax liability CFO adjustment 244,565,424.70 (old ledger wrongly p148; textual label spans). Physical p139 source discrepancy is real: primary “其他” business revenue 422,649,612.97 vs duplicate total-cell 422,649,613.97, differs 1 yuan. Use only primary column that exactly reconciles to group 41,777,861,795.03 revenues; source conflict prominently in article, **never create fake business residual**. 2026-07-30 H-share capital event occurred after balance sheet 2026-06-30; prohibited to include it in H1 cash.

**Actual distinct financial editorial visuals, not just more templates:** original full 4-stage desktop 1250 SVG unmodified; third mobile separate 330 true money source→own COGS/GP with Yuan-proportional real edge path widths and source click-highlighting, signed P&L/gross/CFO/cash and clear stock/flow; 300308 *unique editorial protagonist* before main: 2026H1 consolidation net profit **147.33亿**, CFO **18.00亿**, conversion **12.21%**, actual cash CapEx **48.02亿**, simple FCF **−30.02亿** on honest identical Yuan-zero-scale positive comparison bars, explicitly **not** a false cash transfer from profit into CFO. 390 and 1440 actual screenshots `optical-native-visual-qa-300308/300308_cashfocus_{390,1440}.png` personally inspected, no clip; other 9 source figures including cash bridge and source ribbon actually opened. CJK original source-to-full HTML browser [#41854062950](https://github.com/kobolibra/financials/actions/runs/41854062950) **PASS_LOCAL**. Deterministic rebuilt independent standalone `public/300308.html` and nested original historical route; older 300394/300502 rebuilt bytes identical. Local current HTML SHA `dc7231532a39e6d1c4994f26a8c63fce6d6cc49f4a3e0abb926eed45bc721f2e` from screenshot/real source receipt (reconfirm after any final changes). **Public new 300308 Cloudflare full-byte / external real production browser NOT_CHECKED until merge and actual run of `scripts/verify_live_optical_native.py`.** No human secondary expert review.

**Transferable skill FIX**: v8.7.4-rc1, FIN-047 in `skills/ashare-financial-storytelling/quality-regressions.json`: actual full PDF bytes and table printed column matter; genuine source contradiction itself is part of financial story; signed and conserved relationships strictly distinct; above-the-fold featured original accounting insight, CJK at 1440/768/390, actual production navigation and human editorial review are all separate gates. Current remaining older mobile inner finance chart FAIL (after shipping third): **600036, 688111, 600519, 000333, 688220**; source-limited research peer, 8–12Q valuation, art director and second human analyst NOT_CHECKED. New chat **first check current main** before assuming candidate or this documented run is current.

---


## 2026-11-04 · Candidate v8.7.3-RC1: optical original 390 money editor actually rebuilt from typed issuer facts, release NOT_CHECKED until main / real Cloudflare

**First actual current main read:** `43a403a834ddfaa5df16dae38897e0a013d1c634`; 11 issuer single directory, Skill v8.7.2-RC1. Read all five manuals, Skill, handoff/AGENTS/checklist and inspected originally captured CJK 1440/390 screenshots for initial three optical, 688220, bank/software and insurance. Real 390 main financial-figure clipping remains **8 FAIL** after already source-fixed 600900/600276. Older optical 300394/300308/300502 original 1250 SVG 4-stage amounts are editorially stronger on desktop but 930px inner figure is only 320px visible on phone. User's “AEI top visual quality” is **not yet met**, even when source arithmetic passes. No external second human editor, no 8–12Q valuation or all material notes completion.

**ACTUAL WORK on PR [#26](https://github.com/kobolibra/financials/pull/26), branch `work/optical-three-native-editorial-20261104`:** source `skills/ashare-financial-storytelling/v7/engine/native_mobile_finance.py` + shared `render_v7.py`, original two complete issuer source-ledgers `300394/300502`. Desktop four-stage original SVG mathematically and byte-identically preserved, plus 390/768 real native finance: each mutually exclusive product revenue exactly splits to its own original COGS and derived GP at actual yuan-proportional SVG ribbon *visible width*, sums to group income/cost/profit; full signed P&L, GP delta, 15 original-indirect-item CFO (graphic groups and full original source table), cash-equivalent close and simple FCF mobile cumulative bridges; two-date stock BS, WC and true same-denominator comparative metrics; **not** a downscaled 930px figure or decorative money bands. Source class excludes negative product GP and invented difference. Clean-room generated `public/300394.html`/`public/300502.html` + original nested stable routes, no change to other issuer HTML or single homepage. Browser CJK 1440/768/390, screenshots saved at `optical-native-visual-qa/`; see real Figure 01 and Figure 03/06/09 390 captures.

**Real Actions**: [#41812019064](https://github.com/kobolibra/financials/actions/runs/41812019064) PASS and [#41812941302](https://github.com/kobolibra/financials/actions/runs/41812941302) PASS first native-source two-company audited clean rebuild / 6 real CJK browser views. New `qa_native_browser.py` checks every visible money rect and source ribbon *path width*, signed original step cumulative/negative geometry, same money-scale per waterfall, Chinese SVG text BBox, 390 no figure internal scroll, full offline independent report byte reconstruction and original desktop editable export. Common `scripts/check_visual_editorial_policy.py` now **will not recognize updated old HTML from old screenshot**; requires exact new issuer full HTML SHA + 3 real browser screenshot hashes, genuine money source and signed accounting receipts. Poison tests for wrong report SHA or fake 390 step proof. The historical 10 earlier FAIL remain historical; unchanged current main still contains **8** legacy phone failures, whereas the two candidate sources are **PASS_LOCAL** only. Real public new Cloudflare article SHA, 11-route 1440/768/390 production, external reviewers = `NOT_CHECKED` until true independent run and published bytes. Do not merge when finance/browser/visual current SHA PR gate fails.

**Third old optical 300308 source blocker now more precisely identified, not silently “fixed”**: actual user Library complete `H2_AN202608211828276722_1.pdf` has **2,984,970 bytes, 184 physical pages, SHA256 `e0ecd7c365c65e90b1fa4b4616ba3f4649449d64451e0ba0b1b78ba9ce3170bf`**. Original PDF was opened and p26/56/57/60/139/148 spot-checked against reported revenue/cost/consolidated net/CFO/source categories. However existing source ledger `skills/ashare-financial-storytelling/v7/examples/zhongji-2026H1-ledger.json` still embeds old `NOT_VERIFIED_REMOTE_PDF` and unarchived source; analysis memo `DRAFT_NEEDS_SECOND_REVIEW`. Do **not** mislabel human second review or overwrite current 300308 HTML until source signed ledger and release tests are reconciled; 300308 mobile remains one of six other old FAILs after two-source candidate passes.

**For new chat/reproduction**: always re-query real current main HEAD, full Skill and 5 manuals and main Actions. Proposed code path `python -m unittest discover -s skills/ashare-financial-storytelling/v7/tests -p test_native_mobile.py -v`; source app `python skills/ashare-financial-storytelling/v7/engine/render_v7.py --ledger ... --memo ... --out ... --qa ...`; real browser `python skills/ashare-financial-storytelling/v7/tests/qa_native_browser.py --out optical-native-visual-qa`; checks `python scripts/check_visual_editorial_policy.py` and `python scripts/check_handoff.py`. Candidate CI `.github/workflows/candidate-optical-native-editorial.yml`. Per release PASS/FAIL/NOT_CHECKED must survive separate QA stages, and new source compiler changes require regeneration of exact HTML and actual Cloudflare fingerprint if merged. Skill v8.7.3-RC1 candidate rules + VIS-046 in registry. `source_limited_preview` only, no invented second human approval.

---

## 2026-11-04 · CURRENT VERIFIED HANDOFF — v8.7.2-rc1 / PUB-045 release QA fix and actual source-stamped two-sector Cloudflare truth

**Start of this session:** queried actual GitHub main `9060bd2a0bf3ddc32d267c176388214ef3316f13`, then read the complete canonical Skill v8.7.1 and all 01–05 research manuals, root state, AGENTS, release checklist, handoff protocol, actual 11 issuer catalog, true source files and Actions. Original 9060 real Cloudflare full-HTML/source proof [#41804157527](https://github.com/kobolibra/financials/actions/runs/41804157527) = **PASS**; same-commit old unified live test [#41804157343](https://github.com/kobolibra/financials/actions/runs/41804157343) = **FAIL** due to a **false-positive old chart selector**, not source PDF or figure missing. Exact job log: `AssertionError: ('600900','new route lost original source flow')`; actual new HTML contains one original desktop money-Sankey `#chart-flow > svg` plus one independently authored phone `.native-mobile-finance svg`. The legacy `#chart-flow svg == 1` counted two; never delete the phone version merely to make CI green.

**Source correction actually shipped:** [PR #24](https://github.com/kobolibra/financials/pull/24) changed `.github/workflows/verify-unified-research-library.yml` to assert **one desktop SVG + one phone SVG = two authored monetary graphics**, preserving all actual money conservation, signed accounting, primary-source citations and all navigation checks. Branch full-source real unified Cloudflare [#41806506722](https://github.com/kobolibra/financials/actions/runs/41806506722) **PASS**; two-sector original PDF/finance [#41806506321](https://github.com/kobolibra/financials/actions/runs/41806506321) **PASS**; insurer finance [#41806506534](https://github.com/kobolibra/financials/actions/runs/41806506534) **PASS**; handoff [#41806506329](https://github.com/kobolibra/financials/actions/runs/41806506329) **PASS**. PR #24 was **merged** at actual commit `25c5796b40276d6ae395573ab8001f5990144979`, with **no existing company HTML or accounting amounts changed**. A later main workflow must have its own run number: PR PASS is not automatically a main-run PASS.

**Two immutable old-source company public HTML records now correctly recorded per issuer rather than obsolete `NOT_CHECKED_PENDING_MAIN_DEPLOY`:**
- 长江电力 600900: `/600900`; source PDF 214 physical pages, original SHA256 `738de3b36a31646f344cefaf90b4f149d653c3f68e89f4f8d14bdf02fc9c65a2`; *actual exact public and repo article* SHA256 `d928676e87ff3d415de36931ee5706614d797264a88dc4980b94426f1492eef8`.
- 恒瑞医药 600276: `/600276`; source PDF 182 physical pages, original SHA256 `ff6910663a9726acb889aa061a8bab1433f58890d81ebea013b8c637a097a7aa`; *actual exact public and repo article* SHA256 `cd4d0c694c2c1c36c5ba2b2d5028f7db157668139edfe0b00f310f9cd94bee0a`.
- Same genuine canonical homepage full HTML SHA `f625453172a83b7db38d0c5a67ddbecd84fbf078bc9f78c2e20c45b00b23ab41`; both original 1440/768/390 real CJK Chromium receipts with 6 screenshot file SHA/bytes apiece and 11 separate route/nav proof in [#41804157527](https://github.com/kobolibra/financials/actions/runs/41804157527). Durable exact issuance records `research/issuers/{600900,600276}/live-release-receipt.json`, matching `release-gates.json`. These are **automated genuine captured browser receipts**, not an external second human art-director sign-off.

**Current publication boundary:** Unique `site/research_catalog.json` directory still **11 real independent offline company HTMLs**, no alternate four-company homepage, original published pages not replaced. Two repaired new sector 390 finance originals + original insurer 601628 are source-verified, but **8 older code routes remain genuine 390 internal-money-chart overflow FAIL**: 300394, 300308, 300502, 600036, 688111, 600519, 000333, 688220. Source-preview research and any unfinished material notes/market history/valuation/independent second human finance and visual review = **NOT_CHECKED**. No reclassification of 8 old FAIL based on the new success, no universal sector maturity claim.

**Intake boundary for user request:** This chat has **no newly supplied/identified issuer PDF attached in the accessible current conversation**; no ticker or complete issuer source URL was specified. A historical unmerged `work/shipping-601919-2026h1-zero-context-source-stress` exists, but is **NOT the user's newly identified report by assumption**. This turn's new-issuer original PDF SHA/period/notes/financial analysis/figures/new HTML/live deployment all **NOT_CHECKED**, no invented data and no invented extra company entry.

**Reproduction / next new chat, not a plan as substitute for this source fix:** query current `main` SHA and current `project-status.json` first (this section is an **as-of historical proof** after later commits); use `python scripts/check_release_contract.py`, `python scripts/check_handoff.py`, `python -m unittest discover -s scripts -p test_check_release_contract.py -v`, `python research/shared/test_two_sector_accounting.py` and actual current `Verify unified issuer research library (live)` workflow. New company starts only from a **named actual complete original PDF** and its physical page/byte checks; then company-specific ledger and handoff. Skill canonical method now v8.7.2-rc1; new portable regression `PUB-045` registered in `skills/ashare-financial-storytelling/quality-regressions.json` with the exact workflow assertion as proof.

---


**历史快照（上方最新已核实 2026-11-04 交接优先）：曾发布同一首页 11 家独立公司研究，中国人寿 601628 2026H1 新手机十大图形版本真实 Cloudflare PASS，源网页 main 提交 `b88698a0cf1cfcd89c16eda1e399796d9418ea04`；当前 Skill 本轮视觉审计升级候选 `v8.7.0-rc1`（正式 main 版本须独立重新读取）。下一次新对话必须重新确认真实 main HEAD、原始 PDF 与确切 Actions 结果。**

> **一套统一目录**：<https://financials-in-visuals.pages.dev/>；第十一家公司中国人寿独立全文：<https://financials-in-visuals.pages.dev/601628>。原目录卡 href `/601628.html` 被 Cloudflare Pages 规范化为 `/601628`，是真正独立的 HTML 页面，不是首页回跳，也不是 iframe。其余十家公司的独立报告未被改动。研究仍为**源限制预览**，不等于已完成独立第二人类审稿。

## 2026-11-04 · 历史开发阶段：水电与创新药 v8.7.1 当时尚未上线（最新真实上线状态见本文件顶部）

**版本真实性**：当前候选完整仓库 Skill 与机器 manifest 均为 `8.7.1-rc1`（严格版本字符串）；正式 main SHA 在合并前保持实际上一版本，不能把候选误认为当前线上版本。

**用户要求**：不能停留于审计“为什么新页面越来越差”，必须重建实际可复用的 Financial Storytelling Skill、财务图形生成器和手机真实图表，保证新聊读取当前主干后可立刻继续。基于先前11公司33次真实 CJK 浏览器视觉核验和10个390内部横向滚动真实FAIL，已将共用的 **600900 长江电力 + 600276 恒瑞医药** 正式源生产器 `research/shared/build_two_sector.py` 改为在原独立单体离线 HTML 中 **嵌入不同会计文法的八幅390原生财务SVG**；JS原图源在 `research/shared/mobile_finance.js`。这不是加几个绿色柱、把760px原SVG缩成300px或者iframe。原始8幅桌面同比/桑基/利润/间接CFO/资产负债/业务来源图继续存在并支持SVG导出，390手机不显示桌面宽图，而显示真正从同一源账本导出的原生专业中文图。

**两个实际具体公司已独立通过完整原始PDF、原注、完整源财务金额守恒、CJK Chromium1440/768/390、每家公司16幅真实SVG、源金额加权收入→成本/毛利的重算节点与路径物理宽度、带符号利润/间接CFO/现金桥、两日期BS、真实万元/亿元单位、创新药商品销售子集且不二次计入收入、手机每图无内部横向溢出/文本BBox在视口、两次确定性独立生成**。真实源Actions [#41799046343](https://github.com/kobolibra/financials/actions/runs/41799046343) 及含7张仓库真实图审阅样本的 [#41799335392](https://github.com/kobolibra/financials/actions/runs/41799335392) **PASS 候选**。真实截图已逐幅亲看（非另一名人类分析师），见 [专门设计修复报告](research/visual-audit/VISUAL_CHANGESET_2026-11-04_TWO_SECTORS.md) 和 `research/issuers/{600900,600276}/visual-qa/*-390-*.png`，每家公司各 `visual-qa/result.json` 有真实新HTML SHA+三屏浏览器源守恒证据。

**完整新HTML SHA**：600900 `d928676e87ff3d415de36931ee5706614d797264a88dc4980b94426f1492eef8`、600276 `cd4d0c694c2c1c36c5ba2b2d5028f7db157668139edfe0b00f310f9cd94bee0a`。**新字节线上验证尚未完成，本段在正式合入前只能标 `CLOUDFLARE_LIVE=NOT_CHECKED`，旧 main 的在线证明不可以自动继承**。2026H1真实巨潮PDF、源回查财务和原版2公司的会计检查依旧PASS。本轮改的是财务视觉和交互，不修改原始财报元金额或报表日期。

**关键失败修正**：之前 `scripts/check_visual_editorial_policy.py` 只检验历史33屏截图中的旧SHA，但不核对 **当前候选HTML SHA**，形成“曾经浏览器通过就永久通过”的漏洞。已增加 `validate_current_published_files` 和恶意修改测试：任何变化的公司源HTML必须具备同一源SHA+真实1440/768/390浏览器财务视觉证明；中国人寿601628另外用新版b065真 Cloudflare 6张截图证明代替不能适用的两行业JSON；没凭证的任何变更FAIL。旧原11公司基线仍诚实记录**10个历史已存在手机图内滚FAIL**。本候选修复2公司手机后，其他**8家原始已发布的手机财务横滚**仍独立FAIL（300394/300308/300502/600036/688111/600519/000333/688220），**仍要继续实改**。v8.7.1技能新增VIS-044案例，43个可复制教训。

**仍不等于研究和视觉两条都完美**：Desktop 600900主收入来源只有主营+极小其他的真实互斥来源，不允许为画出四阶段AEI剧烈效果捏造不存在的业务收入来源；600276创新药属于药品商品子集，不能重复计入法定收入。桌面行业原生长图故事、早三家公司手机真正原金额路径、其他六家、多行业公司第12个601919航运原始财报研究和第三方人类视觉/会计审稿仍为待独立验证/FAIL。**不得把局部手机端PASS称作11家机构级全部最终出版。**

**操作下一步**：确保新分支 `work/two-sector-native-mobile-aei-original-finance-20261104` 的全源PDF+3屏 Actions 与 PR 所有工作流PASS，合并当前main且不动老八家公司；在新main重新跑真实 Cloudflare 11家公司入口/三屏/这两份新HTML SHA，同步 `release-gates.json` 和状态收据，然后继续改善其他8家和601919航运行业图。时间不够时保留分支未检查真相，不造成功劳。

---

## 2026-11-04 · 601628 视觉修复新字节现已真实上线，精确发布收据 [#41786674737](https://github.com/kobolibra/financials/actions/runs/41786674737)

**已在真实生产网站而非GitHub静态推测验证**：`main` 最后实证代码 `eba76b207a7bb5a5f1e027acbb2e59b1f58445d5`，公开 `https://financials-in-visuals.pages.dev/601628` 的完整HTML SHA `b065071a19803465d6f1f62994d190d2b8e0212317ea7db9c08de453cfa3e8b0`，唯一11家公司目录原始首页完整字节SHA `f625453172a83b7db38d0c5a67ddbecd84fbf078bc9f78c2e20c45b00b23ab41`。实际GitHub Actions #41786674737 使用真实 Cloudflare HTTP + 中文Chromium，独立公司导航、返回唯一公司目录、1440/768/390、10 SVG及源表、原保费流几何及390完整财务图 **PASS**，6张截图和真实行程均在 `research/issuers/601628/live-release-receipt.json`。源原件 PDF SHA `b094bf337309e30564dda86ff4b3c4d66aeeb37ce0357a3568e246569f0e2943`。原 `6f386...` 线上发行页面PASS是仅针对旧版，完整保留在 `historical_live_before_1440_label_collision_qa_fix`。现 `release-gates.json` 的 `CLOUDFLARE_LIVE` 恢复**PASS**只因同一新SHA确实通过真公网验证，而非自赋值。

**仍未通过或尚未验收**：截至该真实网页版本，全站其余十家报告的手机重要财务图内滚原债 **VISUAL_MOBILE=FAIL**（源字节及图证见 `research/visual-audit/quality-debt.json`）；新 `work/two-sector-native-mobile-aei-original-finance-20261104` 独立重构长江电力和恒瑞医药的手机桑基/有符号瀑布等，须完整PDF、原值守恒、实际三屏、真实Cloudflare新字节才能解除这两家相应FAIL。用户要求对早三家继续图形升级，不得称全站11家视觉顶级已完成。独立第二名人类资深研究员、资深视觉总监以及全部重大附注仍 **NOT_CHECKED**。

---

## 2026-11-04 · P0最新审核：早期3家公司 vs 后续11家真实图形退化（Skill v8.7.0候选）

**先说问题，不用图多/CI绿冒充顶级**：本轮由真实 `main=8f41d0ea50eeccead7215a99a7aa29808cefa535` 检索所有11家独立完整HTML，完整读取唯一 Skill + AEI/FT/会计/设计五份研究手册与发布门槛，运行 GitHub Actions [#41783946027](https://github.com/kobolibra/financials/actions/runs/41783946027) **33次真实本地Chromium 中文字体1440/768/390** 并保存36张实截图，逐幅查看最早300394/300308/300502和后来的600036/688111/688220/600900/600276/601628。结果令人警醒：**10/11家公司的390px重要财务图仍藏在内部横向滑动小窗口（真实图宽780–1050px、可视320–356px）**；全部 document 根宽度没有溢出却不等于图形可读。严格 **VISUAL_MOBILE=FAIL**，前3家公司桌面原创多阶段资金图的视觉层级明显强于某些后来的一源分二及重复横条，但早三家手机同样失败、逐图展开原始金额表也不够。参见独立完整 [视觉退化审计](research/visual-audit/VISUAL_DESIGN_DRIFT_REPORT_2026-11-04.md)、[真实33次浏览器结果](research/visual-audit/cross-issuer-visual-audit.json)、[十大真实FAIL绑定旧HTML SHA，不能刷成PASS](research/visual-audit/quality-debt.json)，以及 `research/visual-audit/*.webp` 原始证据照片。**真正独立另一名人类资深视觉总监和财报研究员没有审查，仍是 NOT_CHECKED。**

**方法真改变**：新增 `scripts/check_visual_editorial_policy.py` 和 `scripts/test_visual_editorial_policy.py`（新公司或修改过的老公司如仍有390内部横向裁切，强制 FAIL，十家老页面原SHA可作为历史已知 FAIL，不是PASS，也不能更新旧源SHA来洗白；新的公司要有原始来源表及真正可读的SVG数值）。**不能简单缩小一个1250px SVG到300px或统一转换普通数字条代替财务图**：所有新公司必须做真正同源、原金额权重的手机图形重新布局或适用的带符号瀑布，桌面保留原创图导出；有负分部抵销/保险口径/嵌套子集不准为了模仿AEI伪造桑基。此为 VIS-043 跨公司实际截图驱动的发布准入。

**已直接修发行人真源码，而非只写计划**：先前已发表中国人寿601628第一幅比较图在1440真实截图中“2025/2026元金额”和“+2.2/+5.3/+228.6/-5.8%”实际上相互重叠。直接改 `research/issuers/601628/publish.py::comparative()` 源头的独立金额与同比列，并改 `qa_browser.py` 以真实 `getBBox` 红队。该实际重构源PDF、18保险会计、十SVG/十手机完整图和3屏浏览器 + 二次独立重建 [#41784420788](https://github.com/kobolibra/financials/actions/runs/41784420788) **PASS**；修正后真实 1440 图片 `research/issuers/601628/visual-qa/figure_clocks_1440.png` 已逐图查看无重叠。**新候选HTML SHA** `b065071a19803465d6f1f62994d190d2b8e0212317ea7db9c08de453cfa3e8b0`，旧生产已验 6f386…不能为新页背书，故候选 `release-gates.json` 的 `CLOUDFLARE_LIVE=NOT_CHECKED`，须合并后真实跑 Cloudflare 11公司和3屏、双全HTML SHA 才可升 PASS。为此新增 VIS-042。其余十家旧页面不在本次未经完整原始研究和逐个实测前改写，上线仍存在已知移动端 FAIL。

**下一个全新商业模式继续了**：中远海控601919 2026H1 的真实巨潮完整原始PDF 178物理页、1,207,059字节、SHA `0265a4ca61fb24ff15e14b53b258d7febc03bdb7349f379e42e2c28476dd2ff1` 已由真实GitHub Action #41780361853归档于独立分支 `work/shipping-601919-2026h1-zero-context-source-stress`；42处原件x/y行列证据与46条法定IS/BS/直接CFO+原文p148真实间接CFO/分部负抵销/航运成本/受限现金源守恒经 #41781615665 **PASS**（当时159条有效来源，随后追加了五航线TEU与航线运费原事实但**追加部分尚未全量再验**）。真航运主线应审五航线货量、RMB千元运费与美元/TEU单位不同、航运码头合并抵销、真实成本挤压、已签建造承诺与实际船舶购建现金支出的不同；不能套用寿险手机数字条。第十二家公司独立HTML/官网 LIVE **NOT_CHECKED，不准为凑新增公司而出空图**。

**本次硬状态**：研究源核算与33屏原视觉样本 **PASS**；已有十家390横滚 **FAIL**；新中国人寿碰撞修正候选本地 **PASS、未上线新字节 NOT_CHECKED**；独立人类视觉质量鉴定、完整重大附注、可比同行估值仍是 **NOT_CHECKED**。重开新聊天必须先读取实际最新main而不是使用当前候选branch声称已发布。

---

## 2026-11-04 · 当前正式已发布（PR #18 / main b88698a / 390 原生手机全图）

- **纠正上次源交接滞后**：实际 [PR #18](https://github.com/kobolibra/financials/pull/18) 已在 **2026-11-04 05:17 UTC** 合并到当时真实 main `b88698a0cf1cfcd89c16eda1e399796d9418ea04`，并通过同源的全部真实主站 Actions：[Cloudflare 11发行人、主页与独立 HTML 双全字节SHA、中文浏览器1440/768/390、全部10 SVG+10张原报表来源表和手机10完整图、返回唯一路径 #41778320066](https://github.com/kobolibra/financials/actions/runs/41778320066) **PASS**；[原PDF104页/133原事实/18保险财务勾稽/10真SVG及手机完整图/确定性重建 #41778320037](https://github.com/kobolibra/financials/actions/runs/41778320037) **PASS**；[统一研究库 #41778320121](https://github.com/kobolibra/financials/actions/runs/41778320121) **PASS**；[交接 #41778320045](https://github.com/kobolibra/financials/actions/runs/41778320045) **PASS**；[Pages历史路由 #41778320141](https://github.com/kobolibra/financials/actions/runs/41778320141) **PASS**。这五项精确对应**原已发布版本 b88698a**，不是自动证明下一次文件变更。
- **真实公网页面双指纹和截图**：独立公司 `https://financials-in-visuals.pages.dev/601628` 的原始响应完整HTML `SHA256=6f38612a58fe5e50bbe3d7fe43a35d64cc6652328f4446525b6981cdeb3b22dd`，原有首页 `SHA256=f625453172a83b7db38d0c5a67ddbecd84fbf078bc9f78c2e20c45b00b23ab41`，同本次源main实际字节逐一相等。真实公司URL与返回 `/#companies` 分别被记录，旧十公司一份独立报告都没重写。Actions真实执行记录的 **6 张桌面/平板/手机公司页和首页 PNG** 的原始字节长度与SHA全部摘录保存于 `research/issuers/601628/live-release-receipt.json`，便于独立新聊天读取，具体公网页面原图仍从原 Actions artifact 获得，不能把收据SHA冒充可见图片。
- **新原图审美红队纠正已真实可见**：原来 390 宽浏览器把900宽SVG装在内部滚动小窗，真实只见三项经营付现/未见全部CSM组成。新的十组手机自然竖向、来自**同一会计源账本**的金额图形，10组全部完整可见且内部无横向滚动；桌面依然保留原10个专业SVG、可导出真桑基/带符号瀑布，真实图内金额标签不再撞标题。旧桑基“新/续期现金业务”误导标题已在 `figure-briefs.json` 原始源修为“管理层保费统计类别汇总”，不将旧标准保费 536634 百万元冒充CAS保险服务收入112525或现金收现626732百万元。
- **本次发布证明合同纠偏**：本轮发现旧源 `release-gates.json` 的 `CLOUDFLARE_LIVE=NOT_CHECKED` 和机器状态还说新版未合并，**与已经实际运行通过的 #41778320066 相矛盾**。现按真实PDF→133原值→18会计检查→离线SHA→已验 main→真实公网页完整SHA、双真实路由和6截图指纹回写 **LIVE=PASS**，存独立原始收据并在通用 `scripts/check_release_contract.py` 添加任意实报错SHA/假公司首页/假提交/缺手机证据/缺PNG无条件失败的恶意回归 `PUB-041`。Skill 候选 `v8.6.3-rc1`，旧一家公司寿险**L1**实证，不能称保险行业L2或通用L3。
- **严格保留未验**：全104页重大保险合同附注的第二独立审查、精算CSM敏感性与投资负债匹配的外部模型、SSE独立PDF字节与CNINFO相等、8-12季度同业可比估值、真正第二名人类财报分析师及视觉审稿 **NOT_CHECKED**；688220应收集中度报告90.50%与自推89.17%的历史问题独立**FAIL**，不因第十一家公司升级自动归零。中国人寿继续 `release_class=source_limited_preview`。

---

## 历史发布前候选记录（现已由上方已发布事实覆盖）· 2026-11-04 原手机视觉修复

- **先验证真实图，不以CI数量代替视觉**：直接读取 `research/issuers/601628/visual-qa/figure_cash_390.png`、`figure_csm_390.png`、`figure_pnl_1440.png`。发现原 390px 真实截图用了固定900px SVG滚动小窗口，现金8项只能见左3项、CSM存量图右侧不可见；1440px 法定利润瀑布若干最大源金额标签与图内标题视觉重叠；p10保费统计图标题把新单/续期叫“现金业务”，违反 p53 现金收现实际金额的不同会计宇宙。旧 `body scrollWidth`、十张SVG存在和来源金额恒等式都PASS，却**不能代表高水准的手机阅读体验**。
- **已直接修正主源码并实跑**：独立分支 `work/601628-mobile-financial-visual-storytelling-v861` 从原始 133 类事实生成 10 组手机完整竖向图形（保留原 10 桌面 SVG 与导出），每项有真正原元金额、正负号、明确分母与非假最小线，390px 无小窗口横向滚动；瀑布 SVG 顶部金额与标题增加真实布局间距；保费题头改为统计分组而非现金。真实 104页PDF、18个原始会计守恒、三视口移动源金额与条长按实际比例测试、10幅手机单图真实截图、双次确定重建 [#41777012329](https://github.com/kobolibra/financials/actions/runs/41777012329) **PASS**。独立阅读了新 `figure_cash_390.png` 和 `figure_csm_390.png`，整图能在手机宽度内自然竖向阅读且每个数值完整可见，桌面 `figure_pnl_1440.png` 标签已不与图内标题重叠。
- **新版和旧版的真实发布证据不可互相继承**：先前 `main` 全文章 SHA `051a8ec...` 的 Cloudflare **PASS**只支持**旧发布字节**；新版候选 `public/601628.html` SHA `6f38612a58fe5e50bbe3d7fe43a35d64cc6652328f4446525b6981cdeb3b22dd`，在 PR #18 合并并实际线上验证之前，必须使 `research/issuers/601628/release-gates.json` 的 `CLOUDFLARE_LIVE=NOT_CHECKED`，待同一个新 SHA 的 real Cloudflare 浏览器/双SHA/11条公司路由/手机真实可读全面 PASS 才可升级。新视觉回归 VIS-037/SEM-038/VIS-039，Skill 候选 `v8.6.2-rc1`；独立人类审稿依旧 `NOT_CHECKED`。

## 历史较早主站版本 · 十一家公司中国人寿 2026H1 旧 HTML SHA 051a（已被新 6f386 版替代）

- **代码与真实上线**：经实际重新查 GitHub，在本轮交接修订之前 `main` 为 `d11638f0c76ff8aef2beb163a1028f176123bbdc`（中国人寿实际源码与修复后的最终 SVG 版本）。真实公网页面+唯一首页双全字节 SHA、真实 1440/768/390 Chromium 点击和返回、全部 11 条公司路径 / 原始来源表 / 10 个有效 SVG 的线上验收运行 [#41771178361](https://github.com/kobolibra/financials/actions/runs/41771178361) **PASS**。测试输出逐幅真实浏览器公司页 `https://financials-in-visuals.pages.dev/601628`，11家公司从首页点击并能返回 `/#companies`；**公司页 SHA-256 `051a8ecb56cb200f4c411bb53ad672096cfb299e297f149fd58aad334cbfb763`，首页 SHA-256 `f625453172a83b7db38d0c5a67ddbecd84fbf078bc9f78c2e20c45b00b23ab41`**。当前网页此时真实等于已发布主分支字节，而非仅提供 Cloudflare provider 成功通知。
- **其他同源 `main` PASS**：保险原始 PDF/专业财务/十张原创 SVG [#41771178355](https://github.com/kobolibra/financials/actions/runs/41771178355)，旧十公司完整统一目录真实浏览 [#41771178360](https://github.com/kobolibra/financials/actions/runs/41771178360)，发布路由 [#41771178350](https://github.com/kobolibra/financials/actions/runs/41771178350)，跨会话交接 Skill [#41771178406](https://github.com/kobolibra/financials/actions/runs/41771178406)，均在同一源 `d11638f` **PASS**。新的 PR/工具改动不凭旧绿色称为已验，须看本次提交新增的 CI。
- **官方原始 PDF 的真实物理证据**：中国人寿 `601628 2026H1` 真完整 CNINFO PDF：`https://static.cninfo.com.cn/finalpage/2026-08-28/1225516873.PDF`；原始文件 4,867,339 字节、104 物理页、SHA `b094bf337309e30564dda86ff4b3c4d66aeeb37ce0357a3568e246569f0e2943`，归档原件 `research/issuers/601628/source/601628_2026H1_complete_original.pdf`，[#41765739795](https://github.com/kobolibra/financials/actions/runs/41765739795) 下载证明。**133 条**带页码、期间、单位和合并范围的源事实、33 项被锁存并重新计算的源物理页 x/y 行列、**18 条**真实原始会计/直接 CFO/偿付资本及安永中期有限保证复核、10 组原创源证 SVG 与恶意财务变异测试。研究底稿/源码 `research/issuers/601628/`，正式独立文件 `public/601628.html`。原始合并资产负债表 p43–44、合并利润表 p47–48、直接法经营现金 p53–54、保险合同负债 p85、CSM 摊销 p87、安永华明中期审阅报告 p42、监管偿付能力 p21/p66。
- **行业源概念禁止混假**：总保费**536634**、法定保险服务收入**112525**、实际收取保险合同保费现金**626732**（人民币百万元）绝不串成“销售→盈利”桑基；只对原件 p10 四项互斥旧保费分组→新单/续期→总保费生成真正几何守恒的原始 SVG 数带。承保服务净结果 **41177**、本期投资收益 **112902**、公允价值变动收益 **135835** 与承保财务损益 **−188067** 联动，完整 signed P&L 最终归母净利润 **134489**；CFO 用原件实际**直接法**而非编造净利润→CFO 间接表。CSM期末**813253** 是保险服务未赚负债时点存量，本期摊销 **35155** 不等于存量；管理层 NBV **38167** 又是特定价值评估口径。监管核心/实际/最低资本和覆盖率来自 p21，而非合并所有者权益。
- **真实失败与纠偏已归入 Skill**：先纠正p44保险合同负债误抓附注p85、保费真桑基两阶段对金额重复误验，随后补安永**有限保证审阅而非审计意见**、监管资本的独立财务范围和零分母，最后线上真浏览器纠正 URL 后发现最终桑基汇总节点 `fill=money-sink` 的无效 SVG 属性并**回修原生成器**；新 1440/768/390 浏览器 QA 检查每个 rect 的填充、最终节点真实金额与高度，PR [#16](https://github.com/kobolibra/financials/pull/16) + 实际 `main` LIVE PASS。又发现线上 PASS 日志里的 `actual_dedicated_article_final_url` 在返回首页后才获取，虽然实际浏览的文章是 `/601628`，但证据字段错误；**本交接修订正在补通用 URL 分离取证模块 + hostile tests + 六张线上真截图 SHA**。不将这项新修订声称为已验，须跑新 `main` Actions。
- **质量门槛，不能混同**：原始PDF/部分关键原始附注与33行列/18项准确会计守恒/10张原创图/真实Sankey的来源及最终节点/本地3视口/离线一致重建/十一家公司独立路径/生产双全字节 SHA/真实三屏 Cloudflare 导航 **PASS**（对精确 d11638f 的上述 Actions）。**NOT_CHECKED**：104页重大附注及潜在精算敏感性完整独立审阅、源PDF与另一个上交所副本逐字节相等、8–12季度同业市场估值和利率/精算模型、独立第二名人类财报分析师及独立专业视觉审稿；保持 `source_limited_preview`，不得写 `verified_research`。早期 688220 的 90.50% 与自推 89.17% AR 客户集中度问题也仍是独立 FAIL，不能由601628通过覆盖。
- **现行跨会话入口**：先读 `START_HERE.md`、`project-status.json`、本文件；逐个读完整 `skills/ashare-financial-storytelling/SKILL.md`、`research/01–05`、`docs/REPORT_RELEASE_CHECKLIST.md`、`docs/HANDOFF_PROTOCOL.md`、`skills/ashare-financial-storytelling/quality-regressions.json`；从 GitHub 查询真实 `main` HEAD 与确切 commit 的五个 Actions；财务源、HTML、真截图、生产 HTTP 和提交SHA互不替代。本次 v8.6.1 新增通用模块 `research/shared/live_route_evidence.py` 及 `scripts/test_live_route_evidence.py`，live 证明代码 `research/issuers/601628/qa_cloudflare_live.py`，发布合同 `research/issuers/601628/release-gates.json`。再新增公司应下载本公司的**完整原始PDF字节**并独立运行其行业专有财务和图形门槛；本轮601628是单公司寿险 L1，不能自动宣称 L2跨保险或L3全行业泛化已证实。

---


## 历史实施记录（已被上方真实 MAIN 生产结果覆盖）· 2026-11-04 中国人寿零记忆实测和 PR #14/#15/#16

- **严格身份和范围**：本次实际以 GitHub `main` 初始 HEAD `07ea54b5d6e917623a87f6bad83f817d277c6e2d` 开始；真实 `main` 在正式合并前仍是原有 **10 家**；候选分支 `work/insurance-601628-original-2026h1-skill-stress` 提交第 **11** 家中国人寿（保险新经济模型）的唯一独立 `/601628.html` 和原有主页 `public/index.html` 的 **11家公司统一目录**。绝不改变旧十家公司任一家 HTML，也不另开四家公司首页。最新 Skill **v8.6.0-rc1**；新会话必须读本文件、project-status、实际 main HEAD、完整五研究手册、发布清单。
- **官方原件是真实字节，不是网络文字摘要**：巨潮 `https://static.cninfo.com.cn/finalpage/2026-08-28/1225516873.PDF`；GitHub 真实 Runner 下载、逐字节 SHA 与 `pymupdf` 封面/页数验证：[原件归档动作 #41765739795](https://github.com/kobolibra/financials/actions/runs/41765739795) **PASS**；文件 `research/issuers/601628/source/601628_2026H1_complete_original.pdf`，**4,867,339 bytes、104 物理页、SHA256 `b094bf337309e30564dda86ff4b3c4d66aeeb37ce0357a3568e246569f0e2943`**。逐页独立正文/主题索引在 `research/issuers/601628/extracted/`；`verify_source.py` 用真实原始 PDF 校验 **33 项选定 x/y 行锚+当前列来源格**；原报告合并 BS p43–44、合并 P&L p47–48、直接法现金流 p53–54、保险合同负债与 CSM p85、CSM 服务释放 p87。物理 p45–46、p49–50 为**母公司**，不能误当合并。SSE 单独 PDF URL 返回非 PDF，SSE/CNINFO 字节同一性 **NOT_CHECKED**。
- **完整的会计研究优先于画图**：`source-ledger.json` 原始报告 **133 带物理页/会计期间/原报表百万元换算元的事实**，`story.json` 研究论点与反证，`figure-briefs.json` **10 张原创图逐张设计简报**，`publish.py` 18 个 signed 财务恒等式 + `test_accounting.py` 对 wrong year、负数、漏保险财务、CSM 存量当收益、保费误等于服务收入、现金直接法被强换间接法、错母公司等有具体恶意变异测试。
- **行业会计最重要的三个互不等价**：p10旧保险合同统计的总保费 **536,634 百万元**（`101294+17696+61049+356595`）；p47新保险准则确认的保险服务收入 **112,525 百万元**；p53直接现金表实际签发保险合同收现 **626,732 百万元**。三者**禁止互联成盈利流**。管理层 NBV **38,167** 亦不是当前 IFRS/CAS 法定收入。
- **十张真正原创财务图不是通用 dashboard**：仅对同一统计口径四种互斥保费从来源→新单/续期→总保费做真实几何金额权重守恒 SVG 桑基，绝不连到新保险服务收入；五组成分保险服务确认、带符号保险服务结果、完整法定利润桥、两期利润增量桥、实际直接法 CFO 七项负数支出桥、现金开闭桥、CSM+精算负债同日存量构成、两时点合并资产融资、各不混基准 KPI。公允价值变动收益 **135,835**、投资收益 **112,902** 与承保财务损益 **−188,067**、OCI **−48,038**（均 RMB 百万元）必须并读。保费仅 +2.2%，服务收入 +5.3%，归母利润 +228.6%，同期 CFO **282,879 百万元**却同比 −5.8%；这种矛盾是研究主线，不是利润预测外推。
- **实跑失败→修正**：首轮财报坐标锁错源页（p85的保险合同负债附注与合并BS p44 行锚混淆）导致 Actions #41767214612 FAIL，修真实 ledger 后选定 33 项 x/y PASS；首轮桑基验证器错误将原始来源强制双重数带，Actions #41767325656 FAIL，修为 4一级原值 + 2聚合后出口实几何守恒，Actions [#41767495751](https://github.com/kobolibra/financials/actions/runs/41767495751) **PASS**，10 图、10 表、真实 CJK Chromium 1440/768/390、每图截图、实际 SVG 导出、2次字节一致重建。10 项真实失败与未覆盖披露锁进 `skills/ashare-financial-storytelling/quality-regressions.json`（INS-021..INS-030、VIS-027、PUB-028）并在 Skill v8.6.0 规定**L1 单一保险发行人实测 ≠ 保险行业 L2 或通用 L3**。
- **当前状态门槛严格拆开**：原件/选定行列/合并三表+直接现金/10图会计语义/真桑基几何/三视口本地浏览器/同源码重建 **PASS（对应 Actions 具体提交）**；全104页重大附注的专业独立穷尽、历史8–12季同行和估值、独立第二名人类财务及视觉审稿、SSE第二源原件字节相等仍 **NOT_CHECKED**。**在生产真正新路由主站导航完成之前，`CLOUDFLARE_LIVE=NOT_CHECKED`，分支截图不会被冒充为线上发布；绝不写`verified_research`。**每张图原始文件/源事实/研究反证与释放门槛见 `research/issuers/601628/release-gates.json`。
- **在新会话的下一步**：看候选分支最新 GitHub Actions、完成 `public/index.html` 同一个主页重建；原页10家公司全部 `git diff origin/main -- public/*.html`（排除本次新增 601628）应无变更；运行 `python scripts/check_release_contract.py`、`python scripts/check_handoff.py`、所有 issuer hostile/unified portal 测试、实际生产 Cloudflare 11 路由 Chromium 链接和指纹，随后真实 PR 合并 main 再更新本段。若任何一步失败应修原始源头和回归，而不是降级检查。无需让用户重新说明公司、技能和站点。

- **新增机构级源事实修正（重要）**：完整原件 **p42** 是安永华明2026-08-27有限保证审阅报告（审阅准则第2101号，非完整审计、无审计意见）；原摘要仅标“未经审计”会漏掉真实会计保证层级，`issuer.audit`/全文出版现已明确限度。原件 **p21/p66** 监管资本 **核心1,058,166、实际1,334,688、最低674,846** 百万元，核心与综合充足率 **156.80%/197.78%**，年末历史 **128.77%/174.01%**；监管资本与股东CAS权益并非同一会计量。已添加 **6 新事实、4项当前/比较期两位比例实际校验**和4个恶意测试（零分母不能以浮点异常冒充专业门槛），注册 INS-029/INS-030。p17总投资收益3,145.04亿元是管理层经营收益口径，亦不等于合并利润表投资收益1,129.02亿元。
- **当前校验最新状态（勿从过去绿色推定新提交）**：添加p42审阅与p21偿付能力后，机器状态显示候选强约束**正在等待新 133-fact、18-identity HTML 实际重新构建**；旧 [#41767901626](https://github.com/kobolibra/financials/actions/runs/41767901626) 绿色仅对应改动前代码。PR [#14](https://github.com/kobolibra/financials/pull/14) 正在跑新校验，未合并之前 `CLOUDFLARE_LIVE=NOT_CHECKED`。上游旧版`published_html_sha256`必须在新网页编译后按**实际字节**更新；新 PUB-028 反例会拦截指纹漂移，旧600900/600276的显式`NOT_CHECKED_PENDING_MAIN_DEPLOY`仍保留，不能假写已验。

## 2026-11-04 · 本次新发行人入库核验（等待明确的新原始披露对象，禁止虚构第十一家公司）

- **读取基线**：在本次会话通过 GitHub 连接读取实际 `main` `7ee99b608fc4d0376de80f89c20539698b051ba2`；完整 `SKILL.md v8.5.0-RC1`、研究手册 01–05、发布/交接协议、十公司目录、既有 600900/600276 原始账本与研究故事及最新 Actions 均已读取。项目当前是**十家公司**，不是历史七/八家；不要把旧 `AGENTS.md` 中八家公司快照当作现行规模。
- **本次第十一家公司来源门槛**：本会话未收到任何可识别为**新发行人**的证券代码、公司名、原始 PDF 附件或官方完整 PDF URL；会话文件列表为空，检查了现有 Library `/Financials-in-Visuals/`，仅能定位历史已覆盖公司的归档。**ISSUER_IDENTITY / NEW_ORIGINAL_PDF_BYTES / PERIOD_AND_REVISIONS / ORIGINAL_PAGE_ROW_COLUMN / NEW_ISSUER_ACCOUNTING / NEW_ISSUER_VISUAL / NEW_ISSUER_BROWSER / NEW_ISSUER_LIVE = NOT_CHECKED**。不拿历史 601628 作为用户这次指定的新公司，不生成猜测的数字或空公司卡。
- **本次已做的可迁移源修复**：`AGENTS.md` 中硬编码的八家公司描述与当前十公司目录矛盾；已改为从 `project-status.json` 和 `site/research_catalog.json` 动态读取，并在 `scripts/check_handoff.py` 增设 `AGENT_STALE_HARDCODED_ISSUER_COUNT` 检测及 `scripts/test_check_handoff.py` 的恶意回归。该修复仅覆盖交接误导，**不是**第十一家机构财报报告。
- **本次工程验证**：[PR #13](https://github.com/kobolibra/financials/pull/13) 在源提交 `797e27f75de1e4b4b4774dc85e1a31832ce84760` 上运行新的交接反例及源文件约束 [41763814988](https://github.com/kobolibra/financials/actions/runs/41763814988) **PASS**；旧两家水电/医药完整原始PDF、会计和真实三尺寸图形回归 [41763815011](https://github.com/kobolibra/financials/actions/runs/41763815011) **PASS**。这两个运行只证明此代码提交的旧公司和交接测试，不是新公司研究或本会话真人视觉审稿。
- **准确的既有 CI 时点**：`main` HEAD `7ee99b6` 交接 Actions [41738267454](https://github.com/kobolibra/financials/actions/runs/41738267454) PASS；财务/原 PDF/本地三屏 [41737976198](https://github.com/kobolibra/financials/actions/runs/41737976198) 对应 `0ed43ee45ad2aa52e44b11c6b4d371cc4bec5792` PASS；Cloudflare 公网 Chromium [41738152741](https://github.com/kobolibra/financials/actions/runs/41738152741) 对应 `93709bfcd5fe9d2008d12f62b14304c23a26700d` PASS。以上均为旧十公司确切范围；此会话独立 Cloudflare 直接 HTTP/本人新截图：**NOT_CHECKED**。
- **后续真实入库前提**：唯一待取得的对象是本次发行人的完整原始 PDF 或可以直接取到 PDF 字节的官方报告 URL，连同发行人标识；取得后重新核对原始 SHA/报告期/行列，研究全三表与重大附注，创建 `research/issuers/<code>/` 证据及 `public/<code>.html`，只扩容统一目录，再独立执行新公司的会计、视觉、1440/768/390、离线重建和真实 Cloudflare 检查。第二名真实独立人类审稿维持 NOT_CHECKED。

## 2026-11-04 · CURRENT · 两个真实新行业研究 + 十家公司唯一正式网站

**已完成生产合并/真实在线验收**：[PR #12](https://github.com/kobolibra/financials/pull/12) merge `7704ecc6c6a0f0470f7dd5f2c6fe71d5527de511`；只新增 `public/600900.html`、`public/600276.html` 两份各8图/8源证据表的**完整独立离线 HTML**，原八家公司HTML未改，唯一 `site/research_catalog.json`→`public/index.html` 变为**十家公司**。<https://financials-in-visuals.pages.dev/600900.html>（水电长江电力）、<https://financials-in-visuals.pages.dev/600276.html>（创新药恒瑞医药）；唯一入口 <https://financials-in-visuals.pages.dev/>。

**官方披露完整 PDF 字节、源码及样本**：600900 2026H1 完整214页，1,296,750 bytes，SHA256 `738de3b36a31646f344cefaf90b4f149d653c3f68e89f4f8d14bdf02fc9c65a2`；600276 2026H1 完整182页，4,594,202 bytes，SHA256 `ff6910663a9726acb889aa061a8bab1433f58890d81ebea013b8c637a097a7aa`，真实源获取 [41671538396](https://github.com/kobolibra/financials/actions/runs/41671538396) PASS，全物理页文本索引 [41735314032](https://github.com/kobolibra/financials/actions/runs/41735314032) PASS，原始 PDF/重要行列x-y/账本/图表简报/行业分析均在 `research/issuers/{600900,600276}/`。每家公司都有独立三态 `release-gates.json`；SHA 校验并不代替所有重大附注或第二名专业人类审稿。

**main 实际交付 QA（同源 SHA `7704ecc6c6a0f0470f7dd5f2c6fe71d5527de511`）**：财报原 PDF、选定20+26重大源单元格的物理行/列、签名完整三表及间接 CFO、现金等价物闭合、逐源金额加权桑基/有符号瀑布/两时点BS、16幅原生财务图和16份表、CJK浏览器1440/768/390、真 SVG ribbon 几何、独立HTML双次位对位生成 **PASS** [41736999153](https://github.com/kobolibra/financials/actions/runs/41736999153)。真实公开Cloudflare**10公司×3视口30实际URL检查**，两新页原PDF SHA、来源节点与成本/毛利流带、手机及主页回跳、原七页回归 **PASS** [41736999189](https://github.com/kobolibra/financials/actions/runs/41736999189)。老页面/站点规范 [41736999101](https://github.com/kobolibra/financials/actions/runs/41736999101) PASS；原 v10 桑基 [41736999269](https://github.com/kobolibra/financials/actions/runs/41736999269) PASS；零记忆Skill/handoff [41736999465](https://github.com/kobolibra/financials/actions/runs/41736999465) PASS。

**v8.5.0-RC1 原创行业研究/反馈迁移**：长江发电量1327.44亿千瓦时**不是**售电量/收入均价分母，2025H1比较期受2025年10月同控合并影响而追溯调整；投资收益、融资、利息与分红不可当售电现金。恒瑞创新药销售88.09亿元是商品收入**子集**，许可收入独立，7月才生效的BMS不是本期确认，p153非现金银行承兑汇票背书共19.94亿元，其中购建资产7.03亿元不能混入现金CapEx/FCF；研发费用与开发支出资产存量不同。2026版源会计/可视化红队反例存 `research/shared/test_two_sector_accounting.py`、`quality-regressions.json`（共20登记案例）。跨行业实测只足以证明两个L1原始公司样本，**不是**各行业两家L2或全行业自动研究认证。

**仍未完成/不能冒充**：600900/600276各自全部214/182页重大附注的完整独立语义审稿、外部8–12Q同业估值、第二名真正独立人类财务/视觉研究员、交易所SSE与CNINFO原始 PDF 逐字节同一性全部 **NOT_CHECKED**。旧688220 p137/p179原始附注差异仍在以前章节独立标明。发布的是来源限定研究预览，不是独立人类审稿签章的完整机构投资研究。

**下次聊天必须先取得最新实际 main SHA**；以下原始代码路径/执行命令是可重建起点而非仅靠记忆：`python scripts/check_release_contract.py`; `python scripts/check_handoff.py`; `python research/shared/verify_two_sector_cells.py --code 600900` 和 `--code 600276`; `python -m unittest research/shared/test_two_sector_accounting.py -v`; `python research/shared/build_two_sector.py --code <code> --out public/<code>.html`; `python research/shared/qa_two_sector_browser.py --code <code>`; `python site/portal_builder.py --out /tmp/financials-ten-issuer`。实际重跑需PyMuPDF、Playwright/CJK及完整原PDF归档。**未来每家继续按照同样标准验收且有新反馈即新增真实反例，不会自动获得独立研究认证。**

## 2026-11-03 · HISTORICAL CANDIDATE (NOW RELEASED): ZERO-MEMORY GENERICITY TEST: v8.5.0-RC1 · 水电+创新药两家真实 PDF / 十公司统一目录候选

**起始与隔离边界：** 按新聊天场景重新读取 2026-11-03 实际 `main` `2889046506890397082ec3896a057bed0b31d478`、START_HERE/PROJECT_STATE/project-status、唯一完整 Skill 和研究手册 01–05、质量检查和交接。独立分支 `work/two-sector-600900-600276-real-2026h1`，**不是另起四公司网站**；原八公司报告文件未改，本次新增 `public/600900.html`、`public/600276.html`，**十公司首页仍需候选自动生成、PR/main 合并和 Cloudflare 真实逐公司验证**，当前不能冒充线上完成。

- **实际完整新 PDF 已直接取得并归档**：长江电力 **600900** 2026H1，官方 CNINFO 原始 PDF **1,296,750 bytes / 214 物理页 / SHA256 `738de3b36a31646f344cefaf90b4f149d653c3f68e89f4f8d14bdf02fc9c65a2`**；恒瑞医药 **600276** 2026H1，官方 CNINFO 原始 PDF **4,594,202 bytes / 182 物理页 / SHA256 `ff6910663a9726acb889aa061a8bab1433f58890d81ebea013b8c637a097a7aa`**。真实 Runner [41671538396](https://github.com/kobolibra/financials/actions/runs/41671538396) **PASS** 完整 PDF 魔数/覆盖公告/发行人封面/年号/页数/真实 byte SHA；第二家不是截图或摘要文本。另一个上交所同一公告原 PDF 字节与 CNINFO 的一一同一性 **NOT_CHECKED**。
- **机构会计实证不是模拟财报**：`research/issuers/600900/source-ledger.json` 中 63 项原始披露或管理层经营指标，`source-critical-cells.json` 有 20 个**源 PDF 物理页和原始(x,y)列/行语义**硬验证；`600276` 75 项原数据/管理指标、26 个相同原页行列强核验。不只有页上字符串命中，还按本期/对比列原 x 坐标与行标验；其余金额也通过真实原 PDF 对应页金额定位，不表示全部 214/182 页重大附注全面独立审阅。
- **核心实际财务勾稽/原创视觉**：[41677614389](https://github.com/kobolibra/financials/actions/runs/41677614389) **PASS**（原 PDF 20+26 个源格；15+17 精确 Decimal 关系，含利润总额/归母+少数/资产=负债+权益/16+17 条 signed CFO/现金等价物变动/互斥收入→成本+毛利的真加权桑基，行业对抗反例；两家公司**各 8 张、共 16 张**原创研究图和各自八份源表，1440/768/390 真实 CJK Chromium 截图、逐条 Bézier/SVG 实际面积验、图形导出及离线 HTML 逐字节干净重建）。需确认最新变更覆盖新附注后的完整运行记录，以最新 GitHub Actions 为准，不能把较早跑次跨 commit 冒称最新版已通过。
- **真正跨行业发现、修源头、入 Skill v8.5**：水电发电量 1,327.44 亿千瓦时 ≠ 净售电量 ≠ 当期会计收入，缺全量上网售电电量不得倒算平均电价；2025 年 10 月同一控制下合并导致 2025H1 **追溯调整比较期**（原 p.7），水资源税本期约 9.00 亿与成本/财务费用/投资收益分别分析。恒瑞创新药销售88.09亿元是药品等商品销售的**子集**；p.145 商品/许可/其他为真正同维度收入分类；BMS 合同于 2026年7月才生效，潜在约152亿美元合同里程碑收入既非 H1 确认，也非确定未来现金；p.153 **承兑汇票背书支付19.94亿元**，其中材料12.91亿、购建长期资产7.03亿是非现金结算，不能混进现金 FCF；受限资金和研发开发支出存量均不同于可用现金及当期研发开支。可运行对抗测试 `research/shared/test_two_sector_accounting.py` 与 `research/shared/verify_two_sector_cells.py`；`quality-regressions.json` 新增 SRC-016/HYD-017/PHA-018/CSH-019/VIS-020。
- **实际失败不删**：首版 `41673697402` 在真实 **390px 手机报告页滚到 429px** **FAIL**，已经从 CSS 布局和正文/卡片 BoundingClientRect 源头改动，并增加“不允许根部隐藏超宽内容而伪通过”的真实 Chromium 核验。PDF 行列测试首次查出 `cash_end` 对应的源账本是**合并现金流量表 p.56**而非 p.161 现金补充资料; 已把源坐标证据实际改回 p.56。后续发现恒瑞 p.153 银行承兑票据材料字样跨行断字，保留物理切行原文而非做错误 OCR。水电 p.7 追溯比较期也在实际 story 的 countercase 中明确展示。
- **明确的研究边界**：审阅过原始报告重大实际财务/经营/许可/现金附注及关键数据，但全物理页/全部材料附注系统独立全文审计、8–12Q 长期同行估值、第二名真正人类财务/设计审稿仍 **NOT_CHECKED**；每家分类为 `SOURCE_LIMITED_PREVIEW` 而非经独立审稿的完成机构研报。二公司 Cloudflare **NOT_CHECKED**，除非真实新 URL 访问 200、连续导航、截图及本次独特源节点通过。
- **后续第三家独立模型**：计划 **601628 中国人寿保险** 2026H1 真实完整原始 PDF，重点测试保险准则保险服务收入 vs 实际保费、合同服务边际 CSM、金融资产负债、投资收益/OCI/新业务价值、偿付能力，不得照搬工业企业收入−COGS/Sankey；第三家公司不是借第一二家图形模板原样复制。

**新一轮验收需要依次**：分支双公司源+视觉 CI 再跑成功 → `site/research_catalog.json` 唯一首页 10 家 + 按同一 `site/portal_builder.py` 生成根页 → `scripts/check_handoff.py`、`scripts/check_release_contract.py` 与对抗测试 → PR/main 实际合并 → GitHub/main Actions → 真 Cloudflare 2 条独立 URL 和全旧网址点击+1440/768/390 → 三态交接。不得以质量合同 PASS 推断实时 Cloudflare 成功。

## 2026-11-03 · CURRENT: Skill v8.4.2-RC1 · 第 N 家独立质量合同与源→出版一致性

**实际已合并的 Skill（三次小步迭代）：** [PR #9](https://github.com/kobolibra/financials/pull/9) v8.4.0 merged `ffb57ac6142546a66233fa01741b54812422f40e`；[PR #10](https://github.com/kobolibra/financials/pull/10) v8.4.1 merged `d0eed02f7c3bb5bdffb3cb7cea6f4620d0e1bc96`；源账本真实内容修复 `f1e2343cb0b4c76d68b2c386218dde7a3d5bd403`；[PR #11](https://github.com/kobolibra/financials/pull/11) v8.4.2 merged `c2c8b15ab67cb91770b0e04818b181d38f567cfa`。**PR #11 真实 CI**：[41668925315](https://github.com/kobolibra/financials/actions/runs/41668925315) 交接/源与 20 个恶意反例 PASS，[41668925267](https://github.com/kobolibra/financials/actions/runs/41668925267) 统一目录本地 QA PASS；**main** [41669011190](https://github.com/kobolibra/financials/actions/runs/41669011190) 交接 PASS。合并后的主分支 **严格 Cloudflare** [41669011093](https://github.com/kobolibra/financials/actions/runs/41669011093) **PASS**（八家公司×三个视口，确认翱捷科技真实来源节点面积/小额分流/零毛利/桌面终点）；[41669011100](https://github.com/kobolibra/financials/actions/runs/41669011100) **PASS**（已有正式网址及导航）；前一源核验 [41667953097](https://github.com/kobolibra/financials/actions/runs/41667953097) **PASS**（29 会计检验、完整 PDF 镜像 SHA、9 图真实渲染、严格逐字节离线重建）。当前 v8.4.2 的测试入口、交接与线上 route 已在真实 GitHub Actions 执行，而不是未来计划；完整重大附注和真人第二研究员仍 **NOT_CHECKED**。

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
