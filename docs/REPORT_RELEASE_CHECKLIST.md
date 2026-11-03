# Financials in Visuals — 一家公司财报研究与视觉出版“不能跳过”清单

> 适用：在统一网站添加 / 更新 **任意**发行人财报研究。不按图表数量验收，不以“CI 通过”推定研究质量。主规范为 [Skill v8.3.3](../skills/ashare-financial-storytelling/SKILL.md) 和全部五份研究手册。**本清单是执行门槛，不是重新设计一个平行 Skill。**

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
- [ ] `D05 OTHER_FIGURE_GRAMMAR`：带符号变动用瀑布；时点资产结构用组成图，不能伪装现金流；完整财务利润桥、净利润→经营现金流桥、现金和资本投入、真正有可比数据的增长/利润率/同行趋势按问题选择；不自动重复普通条形图/固定图表数量。
- [ ] `D06 ORIGINAL_VISUAL_QA`：完整文章有独立视觉风格、高质量中文排版、精确直接标注、来源近图、适当空白、强弱重点、行业特有信息图。逐图实际检查是否有标签裁切、孤行、假零点、重复或不可能的资金流；**技术截图通过不是审美质量 PASS**。

## E. 可复现独立 HTML 与生产验收

- [ ] `E01 ACTUAL_STANDALONE_HTML`：用户可离线阅读的独立完整网页（不是 PDF、单图缩略图、首页 iframe 或局部小窗口），复用已有出版社与账本。
- [ ] `E02 MOBILE_DESKTOP_VISUAL`：Playwright/Chromium 1440/768/390，全图中文不方块、零页面横向溢出；移动端仅图内允许横向滚动并提供明显提示与完整文字解释。
- [ ] `E03 INTERACTION`：SVG 导出可用、source table、文本/键盘访问、章节跳转、公司首页往返、目录搜索筛选，真实测试而非“理论上可用”。
- [ ] `E04 EXACT_REBUILD`：原 PDF/SHA、账本、生成器与已发布 HTML 可以干净环境重新生成并比对，不允许不知来源的手工覆盖。
- [ ] `E05 UNIFIED_LIBRARY`：新公司加到 `site/research_catalog.json` 及同一个首页 `public/index.html`，其独立 URL 真实存在。保留此前所有公司与专题；禁止新的多公司独立入口。
- [ ] `E06 ACTUAL_DEPLOY`：GitHub `main` blob、Actions 的**确切提交和运行**、Cloudflare 真实 URL 与页面点击/截图分别核实；不因 Git push 成功直接声称站点更新。
- [ ] `E07 HANDOFF`：现行 `PROJECT_STATE.md` 与 `project-status.json` 同步，列出最新工作、来源 PDF、门槛状态和未决异常；`python scripts/check_handoff.py` 通过。

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
