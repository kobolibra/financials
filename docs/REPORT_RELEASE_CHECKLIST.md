# Financials in Visuals — 一家公司财报研究与视觉出版“不能跳过”清单

> 适用：在统一网站添加 / 更新 **任意**发行人财报研究。不按图表数量验收，不以“CI 通过”推定研究质量。主规范为 [Skill v8.7.2](../skills/ashare-financial-storytelling/SKILL.md) 和全部五份研究手册。**本清单是执行门槛，不是重新设计一个平行 Skill。**

### v8.7.2 · 已发布双财务SVG与真实版本收据（PUB-045）

- [ ] 同一个财务图 `#chart-flow` 同时包含**桌面原生资金图**及**390原生资金图**时，严格验证各自一个、合计两个；不能用旧的 `#chart-flow svg == 1` 错把新增手机专业图判为丢失资金流。独立验证桌面原财务加权桑基和手机独立源本图的实际金额/层次/符号/文字可读性，绝不通过删除一幅SVG来通过测试。
- [ ] 真 Cloudflare 1440/768/390 的**当次真实**文章/首页完整HTML SHA、真实主分支commit、财报源SHA、截图SHA与字节、目录/返回路由，应写入该发行人的 `live-release-receipt.json` 并同步 `release-gates.json`。只保留历史来源受限 preview 的先前证据，不能让过时的 `NOT_CHECKED_PENDING_MAIN_DEPLOY` 冒充已经通过完整字节验证的新版本。
- [ ] 若当前用户新公司的原始完整 PDF/身份尚不可判定，`ORIGINAL_PDF=NOT_CHECKED`；不得将已有候选分支的公司当成这次新财报，也不能声称新公司研究/出版已完成。

### v8.7.0 · AEI视觉编辑总监与原始财报会计双独立 P0

- [ ] **AEI第一视觉故事**：核对公开AEI Alphabet/Apple原始图与[早期三家公司金额流、后续公司实图对照](../research/visual-audit/VISUAL_DESIGN_DRIFT_REPORT_2026-11-04.md)。源业务收入、成本、毛利、后续法定经营损益能合法守恒时做原创金额加权资金图；不合法时用行业适用的分组对照或签名瀑布，绝不能混加非互斥分组、负抵销、保险保费和法定服务、TEU/USD/RMB。
- [ ] **独立艺术编辑验收**：实际1440图片里每一幅有独立研究问题、主要驱动、一眼读得懂的源/终点与商业机制；杜绝8张同款普通条/通用Dashboard/空图，图数和Actions绿都不能代表美感。
- [ ] **真实390全图可见**：真CJK Chromium的各图`scrollWidth<=clientWidth+6`，不得藏在一个固定930px小窗口，也不能把1250px整图缩成字小于可读尺寸的手机图片；需要公司原始元账本派生的独立手机图形语法。10家原HTML保持历史明确 **VISUAL_MOBILE=FAIL**，新公司及任何改动旧版不允许继承。`scripts/audit_visual_regression.py`、`scripts/check_visual_editorial_policy.py`、`scripts/test_visual_editorial_policy.py` 必跑。
- [ ] **真实标签几何**：对同比% vs 两期金额、图标题vs signed waterfalls、来源节点vs数值，用中文字体实际SVG`getBBox`查碰撞和越界；公司601628旧桌面已真实误验，候选生成器修复可复用规则VIS-042。
- [ ] **研究与视觉各自独立评级**：原PDF/三报表/重大附注/金额恒等、真实公司业务机制及反证是研究门；真实公司图形叙事、图形原创审美及手机可读性是另一个门，任一FAIL不能叫最终顶级。第二位真实人类研究员与视觉总监缺席为NOT_CHECKED，不得冒名认证。

### v8.6.3 真正上线之后持久保留来源可复核的原始 LIVE 收据（硬门槛）

- [ ] `LIVE_RECEIPT_AFTER_REAL_BROWSER`：从 **实际** `main` 真实 GitHub Actions 的 `PRODUCTION_VERIFICATION_RECEIPT_JSON`（不是用户肉眼猜想、不是Cloudflare provider badge）提取，落盘 `research/issuers/<code>/live-release-receipt.json` 并与 `release-gates.json` 的 `live_receipt_file`、`CLOUDFLARE_LIVE.proof` 完整指向；该收据需真实含原始财报 SHA、原本公司的独立浏览器 URL 与返回唯一路径的**两个不同字段**、完整线上文章HTML SHA、首页HTML SHA、对应40字节hex的 `main` 提交、11家公司或当前完整发行人路径覆盖、三档真实 Chromium 宽度、六张原始屏幕截图SHA和真实字节。不能用上一版的旧报告SHA冒充新版。
- [ ] `LIVE_ATTESTATION_HOSTILE_REPLAY`：通用 `scripts/check_release_contract.py` 对任何新公司真实64位已发布HTML SHA且 `CLOUDFLARE_LIVE=PASS` 的报告进行原始收据载入校验；伪造主页为公司页、替换报告SHA、替换原始PDF SHA、伪造 `main` 提交、截图被删减/伪造以及390财务图变为横向裁切均强制 FAIL；运行 `scripts/test_check_release_contract.py` 的反例后才可合入主分支。
- [ ] `CROSS_CHAT_NOT_STALE`：正式发布已经通过的版本必须同步改写 `project-status.json`、`PROJECT_STATE.md` 和 `START_HERE.md` 的活动状态，不能因旧分支仍被存档而把实际上线的公司写成 `NOT_CHECKED`；但真实未经独立审阅的完整附注、比较估值与第二名人类研究/视觉编辑 **继续 NOT_CHECKED**。原 `main` 发行人所有已发布 HTML 不得覆写。

### v8.6.2 源驱动的真实390px财务图形可读性（硬门槛）

- [ ] `MOBILE_FIGURE_NO_INNER_SCROLL`：实际390px中文屏幕真实截图，每张重大图形**完整可见且可竖向阅读**，不能用900px桌面SVG放入390px横向滚动小框充数；10张图应有10张相应独立移动端源驱动版，而不是同一柱状图模板。
- [ ] `MOBILE_TRUE_FINANCE_SOURCE`：移动图来自相同源账本，每个原源行元精度一致、同组零点与图形条长精确按金额比、正负明确；不可人为加1px最小值；不可把不同KPI使用相同分母制造比较。原SVG必须保留可导出，移动版并非取代财务原图。
- [ ] `MOBILE_SIGNED_MEANING`：真实带符号瀑布可在手机改为原额正负清楚、专用身份和会计合计说明的可读展示，但不能把纯正负金额列表谎称有累计上下游位移的完整瀑布；对桌面损益原图实际getBBox检查标签不重叠图内标题、保持原始财务叙事可读。
- [ ] `PREMIUM_VS_CASH_LANGUAGE`：报告原始管理层保费统计分类桑基的标题/图注不能叫“现金业务”；实际经营现金中收到保险合同保费须以合并直接法现金流单独记录。图表文案是原始财务口径校验的一部分。

### 新增 v8.6.1 发布后证据闭环（全部适用新公司）

- [ ] `LIVE_MAIN_SHA`：以实际 GitHub `main` 的完整 40 字符 commit 和真实 Cloudflare HTML 全文件字节比对为依据。要验证唯一首页和本公司的 HTML 两者均与当前版本 SHA 一致，不把 Cloudflare Provider 成功当线上报告已更新。
- [ ] `LIVE_ARTICLE_URL`：在真实公司文章加载后、点击返回目录**之前**记录实际 URL；Pages 可把 `/601628.html` 规范化为 `/601628`，但必须是同域名和同证券代码的独立文章。返回后再记录 `/#companies` 作为另一字段。恶意首页回跳、错误issuer、假域名为 FAIL。标准通用源 `research/shared/live_route_evidence.py`。
- [ ] `LIVE_SVG_REAL_PAINT`：真实 Chromium 确认每个 SVG 矩形填充颜色合法、所有源节点与最终合计节点的实际可视颜色及金额几何高度按原数据守恒；只有资金带数值与图元属性正确还不够。如最终节点 `fill=money-sink` 此类无效 SVG 绝不通过，参照 VIS-032/VIS-034。
- [ ] `LIVE_PUBLISHED_HTML_FINGERPRINT`：新公司若声明正式 64 hex `published_html_sha256`，`CLOUDFLARE_LIVE=PASS` 时 `live_release_fingerprint` 必须与之相等，并有真实 `actual_main_release_commit` 及对应 GitHub Action 运行证据；旧公司非完整字节验证状态不得被伪升级。
- [ ] `LATEST_HANDOFF_ENTRY`：不能在 `START_HERE.md` 或新会话入口把“当前公司数”硬编码成十/十一家；从 `project-status.json` 与 `site/research_catalog.json` 和真实 `main` 获取，更新项目状态顶部及各公司专属发布门槛。实际 Python 手工负面回归 `scripts/test_live_route_evidence.py`、`scripts/test_check_release_contract.py`、`scripts/test_check_handoff.py` 必跑。
- [ ] `LIVE_SCREENSHOT_RECEIPTS`：1440 / 768 / 390 各自真实拍摄独立公司文章与唯一首页，保存六张截图的 SHA256 与实际路由、当次 Git commit，记在本次 Actions artifact/输出证据中；无法看到专业人工审美评估仍保留 `INDEPENDENT_HUMAN_REVIEW=NOT_CHECKED`。

## A. 先确定研究产品、原始来源和允许的结论

- [ ] `A01 ORIGINAL_PDF_BYTES`：取得完整原始报告 PDF 字节，保留官方 URL/公告、更正或重述版本、SHA-256、字节数、真实 PDF 页数、文件身份；没有原件则明确 `NOT_CHECKED`，不能只靠网页摘录声称“已逐页审阅”。
- [ ] `A02 ENTITY_PERIOD_UNITS`：核对发行人简称/全称/代码、报告期、会计准则、审计性质、发行人合并/母公司、元/万元/千元、流量期间与资产负债表时点、同比重述、季报与累计季度。
- [ ] `A03 SCOPE`：区分**单份 PDF 来源约束研究** vs **拥有经核实历史、同行、市场价数据的机构多期研究**。缺资料不能虚构 8–12 季度、真实市占率或估值。
- [ ] `A04 EVIDENCE_LEDGER`：每个金额或关键比率记载 source label、原始报告物理页/行列、单位、符号、数据日期、会计口径、是否原文/推导/管理层说法/假设、SHA 及前后期。

## B. 财报及重大附注的系统研究（不是只复算几个总数）

- [ ] `B01 THREE_STATEMENTS`：原始合并利润表完整主要行、合并 BS 首尾、合并 CF（期初到期末现金及汇率）、归母+少数股东、非经常损益，先做小数位精确勾稽；禁止错用母公司数。
- [ ] `B02 REVENUE_SEGMENTS`：收入确认政策、分产品/业务/地域/渠道/管理层分部的层级、合并抵销、主营/其他业务**与**按业务类型是否为不同维度。跨维度不得同图累加；未披露差额不能自动命名新业务。
- [ ] `B03 PROFIT_BRIDGES`：毛利→费用→营业利润→税→合并/归母利润的带符号桥；经常/投资收益/公允价值/汇兑及税的归属；扣非及调整利润不得充当合并净利润。
- [ ] `B04 CASH_EARNINGS`：如有间接法现金流补充表，逐项 **signed Decimal** 从合并净利润勾稽到经营活动现金净额；应收/存货/应付存量变化不等于 CF 补充表现金流影响。
- [ ] `B05 WORKING_CAPITAL_AND_IMPAIRMENT`：应收账龄及坏账、合同资产/负债、存货结构和跌价/减值、预付和应付集中度、限制性货币资金 vs 现金等价物、实际资本开支与在建工程。
- [ ] `B06 NOTES_AND_OFF_BALANCE`：关联交易、承诺及或有事项、担保、金融工具/衍生品、外币、并购/商誉、股权激励、税收、管理层风险和期后事项；按照可能改变结论的重大性确定覆盖程度并形成具体记录。
- [ ] `B07 INDUSTRY_ROUTE`：商业银行（存贷、息差、信用减值/NPL/资本，不能套工业 COGS/FCF）；软件（订阅/许可、合同负债、现金）；白酒（产品渠道与财务公司资金隔离）；综合制造（父子业务层级/金融子公司）；光通信（模块/器件、产品收入分类、货运量、应收库存与外汇）。新行业另建真实行业适配，不许套同一财务词汇。
- [ ] `B08 MATERIAL_SOURCE_CHALLENGE`：从 PDF 重新验证有影响结论的每张表的行**和列**含义；抽取数字在同一页出现不等于语义已经核对。明确本次**具体复核了什么**及哪些 `NOT_CHECKED`。

### B09. 实测寿险保险企业的新会计语法（中国人寿601628，Skill v8.6）

- [ ] `INS_PREMIUM_VS_SERVICE`：从原报告脚注明确保险公司“管理层总保费”（如依据旧保险合同会计统计）、CAS保险服务收入、实际保险合同保费收现三者不同；不得伪造保费流入法定营业收入的资金流。原件 p10 / p47 / p53。
- [ ] `INS_CSM_STOCK_AND_RELEASE`：p85保险合同负债未来履约现金流现值、非金融风险调整、CSM 和 PAA 同日组成准确守恒；p87 CSM 本期摊销是**期间流量**，不得与期末 CSM 或管理层新业务价值混淆。
- [ ] `INS_PNL_INVESTMENT_LIABILITY`：保险服务收支（及再保险）、投资收益/公允价值、带符号承保财务损益、OCI、递延税、母公司/少数股东全部走法定原行；明示资产负债联动与可持续性反证。
- [ ] `INS_CASH_DIRECT_VS_INDIRECT`：先看报告是否真实附间接 CFO 补充资料；如果只有合并直接现金流量表则逐项真实赔付、保费收现、佣金等精确勾稽，不制造净利润→CFO 调节。
- [ ] `INS_WEIGHTED_PREMIUM_SANKEY`：仅原始同口径排他保费源→新/续期→总保费可以绘真金额加权图；SVG 源节点、各级带及汇总的实际路径几何必须以原始金额比率准确守恒，严禁把保费当成保险服务收入。负数用签名瀑布。
- [ ] `INS_REAL_ORIGINAL_QA`：实际 104页原PDF SHA/来源、至少33个关键原始x/y/期间坐标和127条源事实、10组原创图与逐图证据、真实1440/768/390截图和可离线双次字节重建。这个门槛在当前只得到**601628 单发行人 L1**支持，不能称跨保险公司 L2 或全行业 L3；单独标示未核查的全附注、独立人类审稿、SSE比对、外部历史同行估值。

### B08. 真实新增水电/创新药财报的禁止误算项（v8.5.0跨行业回归）

- [ ] `HYD_COMPARE_RESTATED`：长江电力2026H1的2025H1同期已根据2025年10月同控合并追溯调整，必须取同一报告重述后对比列，不能拼接原版过去报告。六座梯级发电量1327.44亿kWh属于物理产出，不等于净售电量，不得用集团收入/发电量造上网实现电价。水资源税、投资公允价值、利息与实际电费现金收入分别分析；回归 `HYD-012`。
- [ ] `PHA_NESTED_REVENUE`：恒瑞创新药销售88.09亿元为“销售商品”内子集，不得与“商品／许可／其他”披露的原始分部收入交叉加总。许可收入1,422,301,939.04元的原成本需同口径跟踪，2026年7月生效BMS合同不是2026H1本期确认收入；回归 `PHA-013`/`PHA-015`。
- [ ] `PHA_NONCASH_CAPEX`：p153背书银行承兑汇票支付供应商19.94亿元，其中7.03亿元用于购建长期资产，是非现金结算；必须与现金流量表现金CapEx完全分开；开发支出存量并非当期研发费用或资本化率直接分母。回归 `PHA-014`。
- [ ] `EVIDENCE_SCALES_BY_SECTOR`：两家公司各实证完整原始 PDF、全 signed CFO、物理 x/y 关键源格、16张原创图与三屏浏览器不代表该行业第二家公司 L2。跨行业经济模型不等于跨行业自动机构级审稿。

## C. 真正的证券研究，而非数字转可视化

- [ ] `C01 THESIS`：商业模式与价值链的经济机制 + 三个候选论点，最终给出一个研究主线、驱动因素和量级。
- [ ] `C02 OPPOSING_EVIDENCE`：逐项挑战增长来源、利润含金量、营运资金、资本投入、监管/竞争风险；给出至少一条足以推翻主线的替代解释和下一期验证指标。
- [ ] `C03 CAUSALITY`：会计恒等式只是加减，不能自动归因于 ASP、销量结构、良率、真实市场份额；按披露/管理层/推算/假设明确措辞。
- [ ] `C04 MULTIPERIOD_PEERS`：如果做趋势、同行或估值，需独立带日期原始来源和可比重述口径；没有则明确可用数据边界与 `NOT_CHECKED`，不能用示意数充当历史财报。

## D. AEI/FT 级原创视觉叙事是**独立发布主门槛**

- [ ] `D01 STUDY_BENCHMARK`：全文阅读 Skill 01（AEI 第一手公开案例）和 03（图形视觉系统/22 种关系）；另读 02/04/05 财务规范。不能只提 AEI 名字或数一数做了几张图。
- [ ] `D02 EDITORIAL_SEQUENCE`：以一个可辩驳的核心财务问题和“为什么重要”开篇；按 business economics → profit → cash → capital → risk/counterview → methodology 形成完整文章而非仪表板。
- [ ] `D03 FIGURE_BRIEF_EACH`：每张关键图填写 `question, take_away, source IDs/page, exact units/scope/period, calculation/reconciliation, type/axis/zero, color coding, alternate cause, mobile policy, reviewer/gate`，不可由代码盲选图。

- [ ] `D04B SOURCE_TO_COST_GP_EDGES`：当原 PDF **同时披露每一类互斥业务的收入与成本**时，不满足于来源→总收入→集团成本/毛利的弱分配；逐来源验证 `收入_i=原始成本_i+推算毛利_i`，金额带宽按原始元金额，微小类别保留真实面积，负毛利改有符号图，零毛利绝不能抬高成虚假的正绿流。原始账本每个正金额链接必须与 SVG 编码和原始证据表逐个一致。
- [ ] `D04 SOURCE_CONSERVED_SANKEY`：当存在**同一分组口径、互斥且非负**收入→成本/毛利或银行净收入→实际费用/利润等可守恒关系，选择真正金额宽度成比例的财务桑基图。输入/输出在原始元金额上精确相等；绝不能自动发明“other”，或银行重复扣利息支出；不适用必须书面记录 `FINANCIAL_SANKEY_OMITTED_WITH_SOURCE_REASON`。
- [ ] `D05B FULL_SIGNED_CAS_PNL`：有完整 CAS 利润表行列时，单独用带符号瀑布从毛利走到营业利润/税前/合并净利润，研发、税金、金融费用、投资/公允价值和减值保留真实符号。绝不能以扣非税后项目生拼合并税前值；核实任何空白当前列与右侧上年同期数值的物理位置。
- [ ] `D04B RENDERED_GEOMETRY_NOT_METADATA`：除了账本守恒，还要从**最终 SVG 实际 Path 坐标**重算每条业务→成本/毛利的起点带宽；核对四类来源矩形真实高度（**不得把 <1px 的金额来源换成 1px 固定线**）、终点金额、真实零毛利无面积。`data-*` 金额正确不足以证明视觉几何正确。
- [ ] `D05 OTHER_FIGURE_GRAMMAR`：带符号变动用瀑布；时点资产结构用组成图，不能伪装现金流；完整财务利润桥、净利润→经营现金流桥、现金和资本投入、真正有可比数据的增长/利润率/同行趋势按问题选择；不自动重复普通条形图/固定图表数量。
- [ ] `D06 ORIGINAL_VISUAL_QA`：完整文章有独立视觉风格、高质量中文排版、精确直接标注、来源近图、适当空白、强弱重点、行业特有信息图。逐图实际检查是否有标签裁切、孤行、假零点、重复或不可能的资金流；**技术截图通过不是审美质量 PASS**。

## E. 可复现独立 HTML 与生产验收

- [ ] `E01 ACTUAL_STANDALONE_HTML`：用户可离线阅读的独立完整网页（不是 PDF、单图缩略图、首页 iframe 或局部小窗口），复用已有出版社与账本。
- [ ] `E02 MOBILE_DESKTOP_VISUAL`：另对 1440px 检查每张核心财务图自身 `scrollWidth<=clientWidth`、SVG 字符边界不被裁切，不能因整页不溢出就忽略桌面图内隐藏的最终利润/成本。：Playwright/Chromium 1440/768/390，全图中文不方块、零页面横向溢出；移动端仅图内允许横向滚动并提供明显提示与完整文字解释。
- [ ] `E03 INTERACTION`：SVG 导出可用、source table、文本/键盘访问、章节跳转、公司首页往返、目录搜索筛选，真实测试而非“理论上可用”。
- [ ] `E04 EXACT_REBUILD`：原 PDF/SHA、账本、生成器与已发布 HTML 可以干净环境重新生成并比对，不允许不知来源的手工覆盖。
- [ ] `E05 UNIFIED_LIBRARY`：新公司加到 `site/research_catalog.json` 及同一个首页 `public/index.html`，其独立 URL 真实存在。保留此前所有公司与专题；禁止新的多公司独立入口。
- [ ] `E06 ACTUAL_DEPLOY`：GitHub `main` blob、Actions 的**确切提交和运行**、Cloudflare 真实 URL 与页面点击/截图分别核实；不因 Git push 成功直接声称站点更新。
- [ ] `E07 HANDOFF`：现行 `PROJECT_STATE.md` 与 `project-status.json` 同步，列出最新工作、来源 PDF、门槛状态和未决异常；`python scripts/check_handoff.py` 通过。

## F0. 第 N 家新公司的自动化证据合同（v8.4.0；强制）

- [ ] `ISSUER_CAPSULE`：新增公司必须提交 `research/issuers/<code>/release-gates.json`，对应唯一 `site/research_catalog.json` 路由和真实自包含 HTML；七家历史页面没有因此获得追溯合格认证。
- [ ] `PUBLISHED_EMBEDDED_LEDGER_DRIFT`：公司 HTML 若内嵌可复核的 `ledger-data`，则其发行人/原始来源说明/实际事实元值/互斥业务分类必须与 checked-in `source-ledger.json` 相同，避免报告来源文本改了、网页嵌入数据仍旧；原始 PDF 账本修改后需**真正重新生成网页并逐字节对比已发布 HTML**，不得靠关闭重建检查过关。
- [ ] `THREE_ARTIFACT_IDENTITY`：新公司 PDF 归档→source-ledger.json→figure-briefs.json→release-gates.json 四者的公司代码、报告期、原始报告 SHA、事实 ID、真实物理页范围和原始元/比例类型均一致；不能仅让状态文件中的哈希正确、但源账本仍留历史 NOT_CHECKED 占位。
- [ ] `SECTOR_ACCOUNTING_ROUTE`：本公司声明 sector_adapter 和 accounting_basis；银行/保险等不同准则不能套工业收入−成本或 CFO/FCF 图，通用机器禁用明显错误方案，具体行业报表仍要原始证据复核。
- [ ] `PDF_BYTES_REAL`：自动程序实际读取归档 PDF 魔数、**字节数与 SHA**；真实物理页、官网与镜像文件字节同一性必须另行证明，不能以 metadata 字段替代。
- [ ] `PREVIEW_P0`：即使只是来源限制预览，PDF、选定关键表原始行列、核心账务、独立研究主线及反证、图形语义、截图自查、浏览器和离线重建均需 PASS。重大附注未解与外部研究未做必须显式标出且报告不得自称最终独立认证。
- [ ] `NO_FALSE_PROMOTION`：`verified_research` 必须所有门槛 PASS，包括真实的人类独立财务/视觉审稿、外部多期同行来源、Cloudflare 最终版本真验。不能仅将 source-limited 更改分类就宣称合格。
- [ ] `FEEDBACK_TO_TEST`：每个新发现的重大错误要修原始源头、出反例、跑回归、登记 `quality-regressions.json`，注明仅个股测试还是跨发行人机制；更新 Skill 与 [进化协议](SKILL_EVOLUTION_PROTOCOL.md)。
- [ ] `AUTOMATED_COMMIT_GATE`：运行 `python scripts/check_release_contract.py` 与 `python -m unittest discover -s scripts -p test_check_release_contract.py -v`，并保留现有源会计、图形与公开浏览器独立 QA 证据。

## F. 不能合并的最终门槛（逐项给状态）

| Gate | 需要的证据 | 无证据时 |
|---|---|---|
| `PDF_HASH` | 原始报告字节 SHA+期间/版本 | NOT_CHECKED |
| `PAGE_ROW_COLUMN_SEMANTICS` | 重大原始附注行列、单位、口径的逐项复核 | NOT_CHECKED |
| `ACCOUNTING` | 全部适用的原始元精度财务恒等式 | FAIL / NOT_CHECKED |
| `RESEARCH_THESIS_RED_TEAM` | 主论点、反论点、行业机制、下一期反证 | NOT_CHECKED |
| `AEI_VISUAL_EDITORIAL` | 逐张图的原创语法/视觉编审记录 | NOT_CHECKED |
| `CHART_CONSERVATION` | 真流向的全图金额守恒，或明确不适用原因 | NOT_CHECKED |
| `BROWSER` | 全文 1440/768/390 截图、交互与返回导航 | NOT_CHECKED |
| `GITHUB_AND_LIVE_CLOUDFLARE` | 确切提交、CI、生产路由 HTTP/点击 | NOT_CHECKED |
| `HUMAN_INDEPENDENT_FINANCE_REVIEW` | 真正第二位独立专业人员的人工签核 | NOT_CHECKED |

**结论不得写“全方位顶级已认证”，除非内容与视觉两套原始证据都真的完成。** 但不应该以缺少另一位真人审稿人为借口，停止执行助手自己能够完成的原始附注交叉核验、财务分析、信息设计和迭代修复。
