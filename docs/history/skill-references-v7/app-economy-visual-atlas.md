# App Economy Insights：完整财务视觉研究地图

**独立研究／2026-10-30｜Financials in Visuals**

本文件通过 App Economy Insights 官方公开文章与公开图形，研究其**可核实的设计与研究方法**，并把每种方法转换为 A 股财报分析及可编程图形的要求。参考其分析思路，不复制图片、标识、源代码、品牌资产或独家版式。不假装已访问付费会员月报的完整档案。

## 一、参考范围，不止一张收入图

| 公开来源 | 真正展示的研究问题 | 主要图形/表现 | A 股实现要求 |
|---|---|---|---|
| [How to Analyze an Income Statement](https://www.appeconomyinsights.com/p/how-to-analyze-an-income-statement) | 卖什么？收入由何而来？成本和利润如何形成？ | 多来源收入汇集、营业成本与毛利分流、毛利到营业利润/净利；直接标明金额、同比与 margin | 一张完整的经营利润图 + 一座**有符号**会计桥；区分 CAS 收益/损失，流带不显示负金额；有分部时依据披露拆分 |
| [How to Analyze a Balance Sheet](https://www.appeconomyinsights.com/p/how-to-analyze-a-balance-sheet) | 资产由何构成，负债和权益如何覆盖？ | 总资产→流动/非流动项目，负债→流动/非流动项目，权益组成；资产负债相等 | 资产、负债、权益分级构成；控制「时点结构≠资金实际流向」语义；存货/应收及减值附注验证 |
| [How to Analyze a Cash Flow Statement](https://www.appeconomyinsights.com/p/how-to-analyze-a-cash-flow-statement) | 净利润如何调成 CFO，钱最终流向哪？ | 净利润→非现金/营运资本→CFO，CFO/投资/筹资/期末现金的连贯可视化 | 第一层准确勾稽间接法，第二层期初+CFO+CFI+CFF+汇率=期末；保留正负及调节标签 |
| [Free Cash Flow Explained](https://www.appeconomyinsights.com/p/free-cash-flow-explained) | CFO 减 CapEx 后保留多少现金？ | 从经营利润、净利润到 CFO、CapEx、FCF 的连续价值逻辑 | CFO−购建长期资产现金支出作分析师定义，不称扣除全部股东分红后的现金；必要时区分维护/扩张性 CapEx 未披露 |
| [6 Charts Before You Buy](https://www.appeconomyinsights.com/p/6-charts-before-you-buy) | 判断公司是否值得投资，需要哪些比较？ | 六图框架：增长、利润率、债务杠杆、股价与基本面、估值区间、同业比较 | 六图是**候选研究模块**而非一份半年报强行凑齐；只有足够历史、价格与可比数据才允许输出 |
| [How to Analyze a 10-K](https://www.appeconomyinsights.com/p/how-to-analyze-a-10-k) | 财报不仅是三张表，如何读风险与 MD&A？ | 通过商业模式、风险、三表、管理层讨论、附注构成完整研究架构 | 披露→会计核对→价值创造/资本配置→反面解释→可证伪监测；必要时引入经许可的同业来源 |
| [How to Analyze a Stock](https://www.appeconomyinsights.com/p/how-to-analyze-a-stock) | 生意、机会、风险、财务、估值六方面完整审视 | 商业模式优先，业务质量与估值相结合 | 财报-only 模式排除未经核实的市占率、目标价、利润预测；扩展研究模式须另有市场数据源 |
| [Stock-Based Compensation Explained](https://www.appeconomyinsights.com/p/stock-based-compensation-explained) | 股权激励如何同时影响利润、现金与股东权益？ | 将 SBC 作为 P&L 成本，又通过间接法从净利加回 CFO，分析稀释影响 | A 股股权支付与限制性股票、股份变动、复权 EPS；**不能**简单把非现金股权支付当免费经营现金 |
| [How to Analyze an Income Statement — discussion](https://www.appeconomyinsights.com/p/how-to-analyze-an-income-statement/comments) | 作者如何制作图？ | 作者明确称图表由团队内部制作、耗费大量人工设计工作 | 自动绘图≠出版级设计；静态数据 QA 和人工截图审核是两道不同门槛 |
| [About](https://www.appeconomyinsights.com/about) | 这类产品如何运营？ | 数据准备、映射、编程、图形设计，再压缩成读者可迅速理解的信息 | 采用分析师+财务审计员+信息设计师的三角色交叉审稿，不依赖一次 LLM 输出 |

### 特别注意：公开资料与付费资料的边界

Premium/PRO 的某些月度《Earnings Visuals》和深入个股报告需要订阅；本文未声称读取或分析这些付费文件的全部图页。所有已观察到的风格和案例都来自官方公开网页/其可见图片或开放网页摘要。**不要把作者的全套内部生产工作流说成已被逆向还原。**

## 二、《六图框架》应当逐张如何实现

1. **Revenue Growth / growth by segment**：2–3 年收入或 8–12 个季度分部增长率，用堆叠柱/折线或小倍数；同比定义、收入分类变更和重述警示。没有足够历史期数时显示 **NOT AVAILABLE**，不能使用插值或机械年化 H1。
2. **Gross, operating and FCF margin trend**：三条明确同期间利润率曲线，需有一致 CapEx 口径；严格区分会计净利润和经营现金/资本开支现金。缺少季度 CapEx 则不声称季度 FCF margin。
3. **Debt & leverage**：净现金/净债务及有息负债到期结构；债务+租赁是否包含须统一；若 EBITDA 不具适用性（银行、保险或业务特殊），改用行业指标。
4. **Price vs fundamentals**：价格与财务基本面分别指数化，以同一基点统一或双轴明确；需交易数据与财务发布日期，防前视偏差；财报 PDF-only 禁用。
5. **Valuation spectrum**：5–10 年历史倍数的低/中/高区间，标明 trailing/forward 及预期来源；A 股盈利周期和资金口径匹配；财报 PDF-only 禁用。
6. **Peer comparison**：同行企业同一季节/行业/收入结构的可比毛利、增速、现金、资本回报和估值；只在同行报告及已核实价格数据齐备时做，不拿非同质业务强行比较。

## 三、同样重要的资产负债与现金流视觉

**Balance sheet anatomy** 不是两根相等的堆叠柱：把净额口径资产科目从左端合并到总资产节点，再从此节点展示负债与权益的**会计结构对照**；此图不意味着负债向特定资产提供实际现金。原始金额逐元核对，权益是账面所有者权益而非市值。

**Indirect cash-to-CFO** 是有符号加减序列，不可把负项在桑基图中当正流带。第一层净利润→非现金/营运资本调整→CFO，第二层期初现金→经营/投资/筹资/汇率净变动→期末现金。必须显示会计现金等价物口径与货币资金区别。

**FCF / CapEx / Shareholder Returns** 不应只写一个 CFO 减 CapEx 的数字：资本开支、股利、债务偿还、股份回购要按现金流实际项目，并区分维护性/扩张性支出未知项。若未披露维护性 CapEx，说明分析师简化定义。

**Working Capital & Counterparty Exposure** 不能把 AR 占比误当收入占比，把第一大预付供应商余额误当采购份额。应收、原材料、合同资产、预付账款等用面积条/变化矩阵加占比，标注账面净额、跌价/坏账准备和计量时点。

## 四、App Economy Insights 视觉语言的具体规律（可借鉴但需独立创作）

- 图形组织的是 **因果需有证据、会计关系需可核对** 的问题，而不是“有多少 KPI”。
- 主图从左到右，关键业务/产品节点近左侧，中部资金/利润节点，右侧结果/成本；进出方向清楚。节点有金额，重要的增长率和毛利率直接出现于图内。
- 颜色承担语义：收入/业务灰或多业务识别色，利润绿色，成本/流出红色；我们应用独立的色系与字体，不复制其品牌资源。
- 一张主图应在 5 秒内回答业务如何赚钱；三表结构应当能各自独立解释且共同指向同一条研究判断。
- 历史、估值、市场定位使用不同类型图表，**桑基图不是万能设计系统**。
- 复杂信息从重要到次要分层：主视觉清晰、一屏主要结论、辅助图定位驱动、页末对审计数据/原始来源透明说明；高质量不等于图越多越密。
- 作者公开明确提到图表需要大量数据整理与人工设计，因此必须设独立的编辑审稿和桌面/手机截图门槛。

## 五、Financials v6 逐项审核结论

| 目标模块 | v6 事实情况 | 下一步硬性验收 |
|---|---|---|
| 收入/毛利润 | 6 条比例流带存在，但只显示到毛利 | 以经核实的收益/费用项目处理延伸利润路径；不造假净利润正流 |
| 完整 P&L | 已有有符号桥 | 增强图内直接标示毛利率、运营利润与净利率；保留负值准确 |
| CFO 间接法 | 已有分组调整瀑布 | 增加视图明确区分净利润→CFO 与期初→期末现金两层关系 |
| Balance Sheet | 两根堆叠柱对照 | 改为完整多层金额比例流带，资产各科目→合并总资产→负债/权益；警告为时点结构 |
| FCF/CapEx | CFO−现金 CapEx 数字存在 | 增加与经营现金、长期资产购建现金支出、股利/债务/外汇之间的关系说明 |
| Working capital | 两期差额和部分集中度存在 | 增加营运资金质量分析，提供存货原材料与减值明细，注明应收余额集中不等于营收集中 |
| Growth trends | 两期半年数据可比 | 增加足够历史原始报告时才开启 8–12 季趋势，不编造 |
| Leverage | 有资产/负债/权益 | 有息债/现金/到期明细齐备后才做净杠杆图 |
| Price vs fundamentals | 无足够交易数据 | 明确 NOT AVAILABLE，不作零值或模拟行情 |
| Valuation/peers | 无独立价格与可比报告数据 | 明确 NOT AVAILABLE，需单独验证外部数据 |

## 六、工程化交付与真实图形样例

单独提供 `build_exhibits.py`：源数据是审核过的财务证据账本，原生 SVG，不依赖外部 JS。新增原始研究图：
- `Capital Anatomy`：货币资金、应收、存货、其他流动资产、非流动资产 → 总资产 → 负债与权益；所有节点面积严格按 CNY 元同比例缩放。
- `Cash Architecture`：合并净利润 + 15 项间接调整（分 4 组） = 经营现金流；期初现金 + CFO + CFI + CFF + FX = 期末现金，两套精确 Decimal 计算；使用有符号瀑布，而非伪正向桑基。

以上是**两张独立的真实财务可视化样图**，不代表已解决了全部多季度、估值、同行数据采集。当地 Chromium 三个 viewport 通过 DOM、控制台和横向溢出检测；仍应进行出版美学人工逐图审查，避免以浏览器无报错替代设计水准。