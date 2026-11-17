# Playbook 07 · 从原件到专业研究与原生可视化：泛化能力编译

本文件为新公司、新报告期和新行业的强制步骤。在 `SKILL.md` / Playbook 06 之后先编译能力再写研究与画图。目标不是图的数量，而是每个新结论都由同口径源证据支持，每个图都合法、可读、必要；未知时必须拒绝。

## 1. 五层互不替代的质量合同

| 层 | 必须检查 | 禁止等价替代 |
|---|---|---|
| S1 原件 | 完整PDF原字节SHA、报告年期、原页及范围、未映射金额行完整性 | 会计等式闭合不代表事实覆盖 |
| S2 财务语义 | 报表格式、存量/流量、源格、期间、合并口径、单位、符号、互斥分区 | 应收较年初变化不是同比；成本不能混为利润 |
| S3 研究推理 | 商业模式、量化驱动式、最强替代解释、反证、下一期可检验条件 | 规则生成的几句数字解读不是专业研究 |
| S4 编辑可视化 | 经济问题→数据关系→合法图族→独立审计→桌面/手机原生版式 | SVG几何正确不代表信息设计和审美优秀 |
| S5 发布 | 当前commit、云端预览、Chromium+WebKit原图截图、生产HTML精确字节 | 旧PR/旧截图/旧正式站不能证明新字节 |

各层分别记录 PASS / FAIL / NOT_CHECKED；不得加权平均、不得以技术PASS推断人工审稿。

## 2. 新公司必跑能力编译

~~~bash
T=skills/ashare-financial-storytelling/tools
python $T/v2_builder.py capabilities --code 300570
python $T/v2_builder.py capabilities --code 300394 --period 20269M
python $T/v2_builder.py capabilities --code <新公司代码> --out /tmp/capability.json
~~~

`tools/research_capabilities.py` 从账本类型、金额、原页事实、所属经济模型和期间生成 `financials.research_capabilities.v1`。它不按公司代码打补丁，输出：

- `sector_route`：industrial / bank / insurance / securities / real_estate / unknown；
- `period_basis`：同长度累计流量同比、期末与上年末存量（非同比）；
- `visual_candidates`：对应研究问题、精确来源事实、许可条件及拒绝原因；`ELIGIBLE_PENDING_SOURCE_AND_VISUAL_AUDIT` 不是图形验收PASS；
- `research_questions`：各行业的重要证据线索，始终 `REQUIRES_ANALYST_REVIEW`，不自动宣称研究结论；
- `publication_route`：只有已证明的工业类通用路径可以成为作者候选，其余一律 `SECTOR_ADAPTER_OR_EVIDENCE_REQUIRED`；
- 来源哈希只说明记录了哈希，原件可用性、重大性、人工财经与视觉评审、生产字节都必须另外证明。

`v2_builder.py scaffold` 将该能力报告写入草稿，工业新报告仍需人工选题和图序。未实现的金融或地产新出版路由，正常 `scaffold` 和 `apply` 直接失败；用于 PDF 技术烟测的 `scaffold --source-probe` 生成 `SOURCE_DIAGNOSTIC_ONLY_NOT_FOR_PUBLICATION` 草稿，**不能通过 apply 转为正式报告**。`findings` 对非工业模型拒绝输出通用工业结论。

## 3. 图形必须从问题和证据反向选择

| 问题 | 证据充分时可选 | 明确拒绝 |
|---|---|---|
| 哪个业务留下了毛利？ | income:同一维度互斥业务收入和成本逐元合计闭合 | 仅集团成本、分部交叉叠加、负业务毛利 |
| 法定收入如何形成归母？ | income_flow_v3:六阶段累计财务源格两期合法 | 负数语法不成立或不属于工业会计模型时改签名桥并独立审计 |
| 哪些损益项目增速分化？ | growth_bars:同一累计期间且比较基数正 | 负/零基期、单季与累计混搭、把存量当同比 |
| 毛利率/费用率怎么变？ | ratio_dumbbell:非负比率、合并口径、两期相同分母 | 负毛利或缺证据则不画正区间比例图 |
| 资金沉淀在何处？ | stock_delta:工业营运资产/负债报告日与上年末两时点 | 把银行贷款/存款、保险合同负债套工业现金语义 |
| 单季增长在加速？ | period_columns:至少三季真实可比单季流量及对比期 | 一份半年度累计数、只有Q3列却臆造季度序列 |

每图必须有编辑 brief：研究问题、关键证据键和分母、为什么该图比其他图更有信息增量、读者五秒可见的结论、最强反证、手机文字层级。图与图不要重复表达同一个利润链。没有独立证据时，图形应省略并标明来源限制，不以“至少五图族”强迫无效可视化。当前 `lint_v2` 的配额型规则尚未适用性重构，仍是待整改项，不授权伪造图种。

## 4. 行业是真正的经济模型差异，不是换名称

工业：分业务真实毛利、现金转换与营运资本、资本开支、成本/费用会计驱动。银行：净利息收入≠利息收入，净息差必须用平均生息资产；监管资本、拨备与不良另证。保险：管理层保费≠CAS25保险服务收入，NBV、CSM、偿付能力和经营现金各为不同口径。证券：经纪、投行、资管、自营和净资本不能套工业利润率。地产：预售/结转、合同负债、交付义务、受限资金、债务到期与持续经营必须单独分析。

行业新适配器至少使用不同发行人的真实原件及不同报告期建立对抗测试，然后再声明有可迁移的图形与指标能力。单一旧报告专用出版器不等于通用新行业出版器。

## 5. 研究判断的六部分证据链

**新增可执行研究证据合同**：每份新报告在正式 `apply` 前必须创建 `research-brief.json`（模板：`templates/research-brief.template.json`），运行 `python skills/ashare-financial-storytelling/tools/research_evidence.py --code <代码> [--period P]`。`financials.research_evidence.v1` 针对每项核心研究问题要求：论点、公司经济机制、最强替代解释、准确来源事实键、同口径可复算 Decimal 算式、区分证据或明确的未披露限制、以及未来报告的证伪条件。系统核验当次发行人/原 PDF SHA/期间/行业路由、事实源格、流量与存量合法期间、精确算术，禁止零或伪造比较、混用存量与流量、数字手写和虚构反证。

机器结果仅为 `PASS_MACHINE_SOURCE_MATH_AND_STRUCTURAL_EVIDENCE_ONLY`；专业归因判断、最强反解释的经济真实性和人类视觉编审继续标 `NOT_CHECKED`，不允许用机器通过代替顶级研究认证。研究证据与图形可视化是两层独立的门禁。

每个重要判断必须包含“可证伪论点 → 原始事实和页码 → 量化算式 → 最强替代解释 → 区分假说的证据 → 下一次报告的明确证伪指标”。标明 DISCLOSED / DERIVED / MANAGEMENT / HYPOTHESIS / UNKNOWN。同比/同环比、存量/流量、合并/母公司、会计/监管统计必须明确比较前提。没有数据的盈利驱动、价格/销量/渠道因果不允许自动成立。

## 6. 真正的盲测与当前尚未实现的能力

四轴测试：陌生发行人 × 行业经济模型 × Q1/H1/9M/FY × 负毛利、重述、缺附注、亏损等异常场景。分别统计 source supported / lawful fallback / source limited / rejected / human required，不能只报一个“全部PASS”。每个从源格到读者可见图标注的审计必须可重算，所有负面样例永久进入回归。

截至2026-11-17，历史30份原件/838条未映射记录的技术快照仅有**当前Git仓库可复验10份原件/183条记录**，另20份原始PDF缺失；这不意味着其余20份以前的记录被推翻，只意味着无法在当前干净环境复验。详见 `docs/UNMAPPED_COVERAGE_PROTOCOL.md`，完整强制原件运行 `generalization_probe.py --require-reference-corpus` 必须阻断缺件。

**未完成重点**：20份源原件恢复；TYPE B、银行、保险、券商和地产的通用出版适配器；研究证据合同虽已能机检源数学与必要的反论证结构，但**尚不能机器判断假说是否真正解释商业模式**；依据真实中文字宽的响应式布局求解器；独立财经和视觉总编盲审；不同公司、周期和行业的大样本无人干预生产级验收。新的能力编译器是质量拒绝与编辑决策基础设施，绝不能据此宣称这些缺口已经完成。
