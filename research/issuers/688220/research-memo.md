# 翱捷科技-U 688220｜2026H1 证据导向研究札记与实质审查记录

## 2026-11-03 source–visual adversarial reconstruction (Skill v8.3.3-RC1)

**Actual source error discovered during full signed P&L rebuild:** On complete original PDF **physical p.87**, the '减：营业外支出' row displays **15.30 元 in the 2025H1 comparative (right) column**. The **2026H1 current (middle) cell is empty**. The previous source-ledger wrongly tagged 15.30 as disclosed 2026H1 expense; the older check passed because 15.30 appeared somewhere on the same page. The physically inspected source text-coordinate proof is x≈502 for the prior-year 15.30 vs the current middle column x≈300–450 blank. The 2026H1 zero *contribution* is DERIVED from 54,945,406.18 + 256,125.37 − 55,201,531.55 = 0.00, **NOT original issuer-reported 0.00**. Ledger, publishing, visual source table and physical column verification were corrected. A local/literal-only gate had failed to detect this until the signed full-GAAP bridge was introduced.

**Visualization diagnostic:** The former 4→1→2 conserved plot actually was a group-only COGS accounting allocation. Its inputs and GP matched to cents, yet it masked product-level cost/economics despite the exact four cost rows appearing at p.178. The rewritten original SVG traces every positive source→its OWN disclosed COGS and derived GP; 4 cost ribbons + 3 strictly positive GP ribbons, one genuinely 0-GP test-service branch, no minimum-size fake money flow. Every source and both sinks have independently checked original-yuan conservation. The P&L signed waterfall now begins with H1 GP and explicitly includes R&D, the four other CAS operating expenses/surcharges, investment/other, fair value, asset/credit impairment, disposal, nonoperating, tax benefit and consolidated NI. Tiny nonzero signed amounts are labeled 万元 and represented by source-scale hairlines, not incorrectly rounded to +0.00/-0.00 亿. A separate dated balance-stock composition displays exact A=L+E at 2025-12-31 and 2026-06-30. These are **three different financial relationships**, not three variants of an arbitrary favorite chart.

**Decision-useful economics:** Product GP now visibly separates chip sales GP (CNY 586,889,184.37) and ASIC GP (CNY 118,983,630.02). GP total CNY 721,516,109.28 includes IP GP CNY 15,643,294.89 and zero test-service GP. R&D CNY 663,322,721.74 consumes most GP, while reported investment and fair-value gains support the statutory net result. This does NOT prove pricing power, normalized EBITDA or recurring CFO. Continue tracking acceptance-based ASIC revenue vs booked order, contract costs, inventory/AR risk and subsequent cash conversion.

**Qualitative interpretation gate:** The issuer's p.137 top-five receivables-and-contract-assets 90.50% remains source-disclosure inconsistent with the naive p.135+p.138 gross denominator 89.17%; cannot claim independent denominator closure. p.179 RPO time portions exceed reported RPO total by one cent. Both remain explicit **FAIL bounded**; no dummy "unallocated" financial stream may balance them. SSE primary URL vs full mirrored PDF byte-equivalence, full every-material-note review, true 8–12Q/peer/market prices and external independent second human editor remain **NOT_CHECKED**.

**Current acceptance of redesign:** This memo and code define source and graphic invariants, not self-certification of a live release. Check latest run of \`.github/workflows/verify-aei-finance-redesign.yml\` on the exact branch/commit and actually inspect every 1440/390 PNG before calling visual editorial PASS. Only merge current verified HTML into original \`/688220.html\`; never change prior seven company pages or add a versioned aggregate homepage. Update SHA/results in PROJECT_STATE and project-status after actual deployment.



**研究产品**：`RESEARCH_PREVIEW`，不是投资评级或已经由第二名独立人类分析师审核的机构正式报告。研究完成日：2026-11-03。编制依据：仓库当前 Skill v8.3.2-RC1、research/01–05、`docs/REPORT_RELEASE_CHECKLIST.md`。

## 原始来源与范围

- 上海证券交易所公告页：<https://www.sse.com.cn/disclosure/listedinfo/summaries/indexDetail.shtml?SEQ=334686886>。公告对应 2026-08-29 翱捷科技股份有限公司《2026 年半年度报告》，未经审计。
- 上交所原始 PDF 直链在 GitHub runner 返回 HTML 而非 PDF，因此不能当作字节来源。完整 **224 物理页** 披露 PDF 从新浪公告下载镜像取得，实际 **1,449,510 字节**；SHA-256：`9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`。原字节：`source/688220_2026H1_20260829_original.pdf`（相对本目录）；`source-manifest.json` 记录完整下载和页证据。
- **SOURCE_MIRROR_FULL_BYTES_SHA = PASS**；发行人身份、报告期间、224 物理页 = PASS；与上交所静态文件服务器的原始字节是否一致 = **NOT_CHECKED**（该服务器阻断直接下载）。报告页面不可将“镜像 SHA PASS”写成“上交所原始 SHA PASS”。
- 本期金额均人民币**元**存入账本；利润及现金流为 2026-01-01 至 2026-06-30，资产负债余额为 2026-06-30、对照 2025-12-31；上年同期比较为 2025H1。

## 公司 / 商业经济机制

1. **芯片产品销售**：p.125–126 直销、买断经销、代理经销分别在控制权转移到终端客户/经销商/代理渠道对终端发货并取得委托代销结算单时确认收入；信用期通常 30–90 天。不能把发给代理经销商等同已确认收入。
2. **芯片定制设计服务 ASIC**：p.126 工程样片交付且功能验收时一次确认；量产阶段需另签独立芯片销售合同，不能把设计服务的 NRE 收入看成已量产经常芯片销售。p.147 未确认收入前履约成本列为合同履约成本，当期摊销入 COGS 157,643,639.62 元。
3. **IP 授权**：p.126 同时满足收入准则条件才按一段时间确认；否则在授权可使用时确认。p.178 另一个合同分组“时点/时段”覆盖全部收入，并非可以加到产品分组的增量。
4. **行业结构**：p.117 存货计价采用加权平均，晶圆生产及封装测试环节主要由外部供应商负责，委托加工物资是重要经营资本；不能把其变化直接归因于良率或产能利用率。p.210 披露集团一个经营分部，p.178 的四类收入属于合同的商品分类，不是四个披露经营分部。
5. **订单**：管理层 p.24 的 ASIC 在手订单估计超过 15 亿元与 p.179 所有业务待履约义务 23.64 亿元口径不同，不相加、不当作当期收入，不猜项目转量产概率。

## 重大会计逻辑／精确可重算关系

| 门槛 | 核对结果 | 物理原页 |
|---|---|---|
| 互斥收入四项合计 2,451,275,102.27 元 | PASS，精确至分 | 178 / 86 |
| 四类成本合计 1,729,758,992.99 元，毛利 721,516,109.28 元 | PASS | 178 / 86 |
| 完整法定利润表主要签名小计营业利润 54,945,406.18 元 | PASS，收益/减值方向正确 | 86–87 |
| 所得税收益 -29,042,237.12 元；合并净利 84,243,768.67 元 | PASS | 87 |
| 归母净利 - 扣非归母 = 142,914,384.80 元税后非经常项目 | PASS，原始八项税影响符号核对 | 8–10 |
| 2026-06-30 资产 7,793,957,327.97 = 负债 1,949,876,414.53 + 权益 5,844,080,913.44 | PASS | 81–83 |
| 2025-12-31 资产 = 负债 + 权益 | PASS | 81–83 |
| 合并净利润 + 间接现金流 **17 项原始带符号调整** = CFO -377,185,378.31 元 | PASS，差额 0.00 元 | 187–188 |
| 期初现金 + CFO + CFI + CFF + 汇率 = 期末现金等价物 2,914,920,011.28 元 | PASS | 90–92 |
| 存货原值 - 跌价准备 = 期末净额；期初亦平衡 | PASS，注意 p.146 的原 PDF 狭窄表格数字在文本层断行，已使用实际页面图像校验行列 | 146–147 |
| 应收账款原值 464,113,067.29 - 坏账准备 8,175,303.66 = 账面价值 455,937,763.63 | PASS | 135–137 |
| 合同负债芯片定制 291,867,010.73 + 预收货款 171,870,048.96 + IP 2,174,451.18 = 465,911,510.87 | PASS | 166 |
| 按时点收入 2,449,003,919.23 + 按时段收入 2,271,183.04 = 2,451,275,102.27 | PASS，分类与产品维度不相加 | 178 |

**两项原始披露的精度/语义问题，不能造假闭合：**

- **源附注应收集中度分母**：p.137 原文前五名应收账款及合同资产合计 414,844,022.57 元，“占比 90.50%”；但 p.135 合并应收账款账面余额 464,113,067.29 加 p.138 合同资产原值 1,113,000.00 作分母，只得到 **89.17%**。按净额口径也不能得到 90.50%；未找到能闭合的明确定义。这属于 **`AR_TOP5_RATIO_DENOMINATOR = FAIL (unreconciled in disclosed tables)`**，不能转写成经独立复算的客户销售集中度；p.213 **95.01% 是母公司附注**，绝不能混合进合并叙述。应以 p.137 **原值 4.1484 亿元**及原文占比、来源不一致提示方式表达，不为缺失分母发明业务。该不一致不能证明造假，也不应擅自修改公司原披露。
- **待履约义务期限拆分**：p.179 总额 2,364,139,874.78 元，一年内 1,878,194,944.41 + 一年后 485,944,930.38 = **2,364,139,874.79 元**，差 **0.01 元**。不画声称完全守恒的 23.64 亿分流桑基；只展示原文并说明一分差额。

## 质量、风险和对立解释

- **利润**：收入增长约 29%、毛利润从 4.69 亿提高到 7.22 亿是真实算术；但归母转正依赖约 1.43 亿税后非经常性损益。p.87 公允价值损益与 p.9–10 税后非经常项目不同税基和归属，不能直接抵消；p.87 其他权益工具公允价值变动 2.42 亿在 OCI，**不是净利润和 CFO**。
- **存货**：p.146 期末净额 21.55 亿，委托加工约 11.01 亿；p.147 本期新增存货跌价计提 55,097,071.34 元（亦有转回或转销）。存货增加可来自订单安排，也可带来库存老化，需用后续销货、量产、减值验证；不等同 CFO 间接调整 4.71 亿。
- **应收**：p.135–137 3–12 月账龄应收 50,662,511.11 元，单项逾期减值已披露；合并前五名应收及合同资产存在高度集中，但比例分母无法由列示总数准确复现。不能把应收资产占比叫客户营收占比。
- **现金与期限**：p.189 现金等价物 29.15 亿，其中仍列入现金等价物的 ASR Italy 租赁保证金 335,445.51 元受限；p.201 一年内未折现金融负债合同现金流 11.49 亿元（短期借款 5.03 亿），与现金余额不是简单可抵消的工业 FCF。p.190 美元货币性余额较大，应将 P&L 汇兑、现金流汇率、OCI 转换分开。
- **估值/估计风险**：p.202–204 第三层次公允价值资产 748,525,532.49 元，估值含不可观察参数；p.129–130 存货 NRV、信用损失、商誉、递延所得税和股权激励需重大会计估计。
- **股份支付/治理**：p.207–208 存在限制性股票及股票增值权；现金结算股票增值权公允价值波动和税后非经常项目不同定义。
- **承诺及期后**：p.205–206 报告对应采购/销售关联方交易选择不适用，p.209 无勾选适用重大承诺/或有/期后事项；不作“绝无风险”断言。
- **最佳竞争性解释**：现金流恶化也可能来自成功设计进入规模化交付前的提前晶圆/封测付款或定制服务验收延后，合同负债增长提供反证；必须以后续合同结转、坏账/库龄及实际回款检验。
- **未来披露证伪点**：ASR 项目验收和量产占比、期初合同负债兑现收入、委托加工及成品跌价、AR 账龄及现金回收、扣非/法定利润差异、现金储备与一年内到期负债。

## 视觉出版图形文法与门槛

**七项独立问题**：01 四类业务收入 → 合并收入 → COGS/GP 的真实金额加权守恒桑基；02 分部 GP 贡献与毛利率独立坐标；03 两期 ΔGP 真带符号桥；04 扣非/非经常/法定归母的真实零点与税后口径；05 完整 17 项 CFO 调整摘要瀑布及每项数据表；06 现金等价物期初到期末签名闭合；07 BS 存货/AR/预付/合同负债时点对照。没有因“画图数量”替代原始附注、实际问题或独立审稿。

生成：`python research/issuers/688220/verify_pages.py && python research/issuers/688220/test_accounting.py && python research/issuers/688220/publish.py --out public/688220.html --qa research/issuers/688220/qa.json`。图可 SVG 导出，来源近图和动态原始证据表。全 CSS、JS 内联，离线可打开。Chromium 1440/768/390 实截图及导出测试独立于内容和视觉编审。

**不可混合的验收状态**：`PDF_MIRROR_SHA = PASS`；`SSE_BYTE_EQUIVALENCE = NOT_CHECKED`；`SELECTED_SOURCE_PAGE_SEMANTICS = PASS`；`FULL_MATERIAL_NOTES = NOT_CHECKED`；`ACCOUNTING_IDENTITIES = PASS`；`AR_TOP5_RATIO_DENOMINATOR = FAIL`（仅此比率禁作守恒图）；`RESEARCH_THESIS_RED_TEAM = PASS_SELF_REVIEW`；`CHART_CONSERVATION = PASS_SOURCE_LED`；`TECHNICAL_OFFLINE_BROWSER = PASS`（见 CI 具体 SHA）；`MANUAL_GRAPHIC_EDITORIAL = PARTIAL`（截图发现重叠后已修）；`LIVE_GITHUB_CLOUDFLARE_NEW_ISSUER = NOT_CHECKED`（需主分支真实上线后）；`INDEPENDENT_HUMAN_REVIEW = NOT_CHECKED`；`EXTERNAL_QUARTERLY_PEERS_VALUATION = NOT_CHECKED`。

**重要**：即便所有技术 CI 成功，研究预览不应升级为 `INSTITUTIONAL_PUBLICATION`。报告内需保留这些边界，而非单凭 7 图或 15 项测试宣布“机构顶级已认证”。
