# Playbook 04 · 生产手册：从一份原始 PDF 到线上报告

以下命令都在仓库根目录执行。`T=skills/ashare-financial-storytelling/tools/fin_intake.py`。最新真实范例：`research/issuers/300570`（太辰光 2026H1，工业 TYPE A），可直接对照其 `source-ledger.json`、`publication.json` 和 `research/editorial-20261113/300570.json`。

## 0. 环境（含沙箱说明）

```
python -m venv .venv && . .venv/bin/activate
pip install pymupdf playwright && python -m playwright install --with-deps chromium webkit
```
本地截图需要 Noto CJK 字体；没有中文字体时截图会出现方块，只能检查布局，不能作为视觉证据。无法安装系统字体或 Playwright 浏览器的沙箱：把 Noto Sans SC / Noto Serif SC 的 otf 放进一个目录，写一个 fontconfig 文件（含 `Noto Sans CJK SC → Noto Sans SC` 的别名），用 `FONTCONFIG_FILE` 指向它；浏览器用环境变量 `FINANCIALS_CHROMIUM_EXECUTABLE` 指向 `chrome-headless-shell`（完整 chrome 在受限沙箱里会因 crashpad 崩溃），`scripts/qa_editorial_migration.py` 会采用它。先 `git fetch && git log origin/main -1` 确认当前 HEAD，并按仓库分支策略建分支。

## 1. 取得原件（P1）

查询巨潮公告：先 `POST http://www.cninfo.com.cn/new/information/topSearch/query`（`keyWord=<代码>`）取 `orgId`，再 `POST /new/hisAnnouncement/query`（`stock=<代码>,<orgId>`、`seDate=起~止`）列公告，按标题“XX年第三季度报告 / 半年度报告 / 年度报告”选择，`adjunctUrl` 前加 `https://static.cninfo.com.cn/`。只用 `stock=<代码>` 而不带 orgId 会返回全市场公告。

- 来源：巨潮资讯（`https://static.cninfo.com.cn/finalpage/<日期>/<公告ID>.PDF`）或交易所官网。只下载完整报告，不要摘要/英文版。
- 下载后确认文件以 `%PDF` 开头（服务器偶尔返回 HTML 错误页）。

同一公司的后续报告期：所有命令加 `--period 20269M`（或 `2026Q1`、`2026FY`），`init` 加 `--route /300394-2026q3.html`，文件落在 `research/issuers/<代码>/<期间>/`。

```
python $T init --code 300570 --pdf /path/report.pdf --url https://static.cninfo.com.cn/finalpage/.../xxx.PDF --short 太辰光
```
产出：`research/issuers/<code>/source/`（归档原件）、`extracted/pNNN.txt`、骨架 `source-ledger.json`、模板 `publication.json`。打开 JSON 补全 `issuer.short / industry / sector_adapter / accounting_route / income_figure_title`。

## 2. 建账本（P2）

**三张表：自动，不写规格。**
```
python $T auto --code <code>          # 格式（一般/银行/证券/保险）、费用符号口径、单位、恒等式、未映射行、原件异常
python $T auto --code <code> --write  # 恒等式闭合后写入；不会覆盖账本中已有的不同值
```
残差、未映射行和原件异常的处理见 `playbooks/06_GENERALIZATION.md` §2。下面的手写规格只用于附注表（分部、地区、非经常性损益、现金流补充资料、应收与存货附注）。

```
python $T find --code <code> --statements      # 定位三表、补充资料、收入成本附注、非经常损益
python $T scan --code <code> --page 40         # 列出该页每行的数字列 [1] [2] ...
```
写 `research/issuers/<code>/fact-spec.json`（示例 `templates/fact-spec.example.json`）：每个事实给 `page`、行标签正则 `row`、数字列 `column`、`type`（flow/stock）、`label`；比较期流量加 `"prior": true`；存量写 `period`（如 `2025-12-31`）；可加 `expect` 做双重核对。然后：

```
python $T facts --code <code> --spec research/issuers/<code>/fact-spec.json
```

列号按**表块**（纵向相邻的数字行）内数字的页面右边缘确定，不是“这一行的第几个数”：只有上期有数的行（如“偿还债务支付的现金”）不会把上期数当成本期。折行数字（`1,923,161` 与 `,156.63`）在 `scan` 里以 `*` 标出并自动拼合；破折号保留列位置但不能取数。标签被折行拆散、行内取不到名字时，用 `y: [低, 高]`（`scan` 打印的 y 值上下各留约 2.5）代替 `row`。每个事实的 `label` 至少 3 个字符，否则发布门拒绝。

工具拒绝：行标签多处命中（用更精确的正则或 `occurrence`）、目标列为空白（空白不是零）、期望值不符、改符号或非元单位（原表正数保持正数，会计方向在表达式里用 −1 系数表达）。

**标准键名**（与已上线报告一致，便于共享出版器与审计器复用；比较期加 `_prior`）：
- 利润表：`rev cogs tax_surcharge selling admin rd_expense finance other_income investment_income fair_value credit_impairment asset_impairment asset_disposal operating_profit nonop_income nonop_expense pretax income_tax net_profit parent_net nci adjusted_parent nonrecurring_net`
- 现金：`cfo cfi cff cash_fx cash_open cash_close sales_cash cash_capex` + 补充资料各行（`provisions depreciation rou_amort intangible_amort deferred_amort … operating_ar_change operating_ap_change cfo_other`，并列入 `cfo_adjustments`）
- 资产负债：`assets liabilities equity parent_equity nci_equity money_funds financial_assets ar ar_gross ar_allowance inventory inventory_gross inventory_allowance ap short_debt dividend_payable`
- 分部：`<segment>_rev <segment>_cost`，并写 `segments` 与 `income_partition`（`axis`、`period`、`scope: consolidated`、`completeness: SOURCE_EXHAUSTIVE_MUTUALLY_EXCLUSIVE`）

只有"两项同期披露值相减"可作为 DERIVED（`derivation: {operation: subtract, terms: [a, b]}`），其他计算放在 `quantified_claims` 或恒等式里。

## 3. 研究备忘录（P3，画图之前）

复制 `templates/analyst-memo.template.md` 到 `research/issuers/<code>/analyst-memo.md`，按 playbook 02 写完八个问题、驱动式、最强替代解释、证伪条件与 NOT_CHECKED 清单。备忘录决定图序；没有备忘录不进入 P4。

## 4. 出版稿（P4）

`publication.json` 字段：`title deck thesis metrics figures accounting_identities quantified_claims essays notes`。

- `accounting_identities`：至少覆盖两期的利润形成、税前、净利与归属、全部现金调节（H1/FY）、现金首尾、资产负债、权益归属、应收与存货原值净额、分部收入与成本闭合、扣非桥。
- `figures`：按 playbook 03 选择 family；每图写 `question takeaway analysis counter identity eyebrow nav`。
- 所有数字用 `{{claim}}` 占位符。
- `notes` ≥ 6 个主题，带页码与边界。

编辑清单：写一个小的 `editorial-spec.json`（`sources`、`stages`、`editorial` 的问题与结论、每图 `role/rationale`，范例 `research/issuers/300394/20269M/editorial-spec.json`），然后 `python $T editorial --code <code> [--period P] --spec …` 生成清单；事实、源格和重大附注都从账本与出版稿复制，不手抄。`material-notes-review.json` 由出版稿 `notes` 展开生成。账本 `issuer` 里补 `period_label`（读者看到的期间名）、`period_names`（期间码到图中标签的映射）、`route`。

**跨报告引用**（后续报告检验上一期判断，或对账同一日期）：出版稿加 `external_ledgers: {别名: {path, period, pdf_sha256}}`，占位符的事实键写成 `别名:事实键`，并声明 `cross_period`：`CUMULATIVE_FLOW_DIFFERENCE_SAME_FISCAL_YEAR`（同年度累计流量，如 9M − Q1）、`SAME_DATE_STOCK_RECONCILIATION`（同一资产负债表日的存量）、`SINGLE_EXTERNAL_REPORT_CITATION`（全部操作数来自同一份外部报告）。外部账本按期间与原件 SHA 固定，期间相同、哈希不符、未声明模式、流量存量混用都会被拒绝。每一期报告都应有“上期判断检验”一节：引用上期写下的证伪条件，区分“被推翻的部分”和“仍成立的部分”（范例：三季报 `prior-check`）。

**EDITORIAL_V2 设计**（推荐，范例 `research/issuers/300394/20269M/`）：出版稿设 `design: "EDITORIAL_V2"`、`story.glance`（6 条要点），第一张图 `family: kpi_board`；编辑清单设 `editorial.layout: "INCOME_FLOW_V3"`、`editorial.hero_position: "after_first"`。新图族 `kpi_board / period_columns / growth_bars / ratio_dumbbell / stock_delta` 的字段见 `research/shared/source_publication.py` 的 `EXHIBIT_FAMILIES` 与范例。单季同比跨两个会计年度时用 `cross_period: "YOY_OF_SAME_FISCAL_YEAR_DIFFERENCES"`（分子里的上年部分必须与分母逐项相同）。V3 需要上年同期源格（`fin_intake.py editorial` 自动从 `_prior` 事实生成 `comparatives`）。

出版稿可选字段：`title_lines`（用 `|` 标注短语单元，单元内不换行）；`essays[].after`（`<figure id>` 或 `end`）把研究长文插在对应图之后，形成图文交替；占位符 `times`/`less` 计算“变动额乘比率”与“差值”。

```
python $T preflight --code <code>     # 源格 + 恒等式 + 编辑 lint + 编辑清单存在
```
`PREFLIGHT_PASS` 之前不要出版。lint 只是下限，通过 lint 不代表文章好。

## 5. 出版（P5）

```
python research/shared/source_publication.py research/issuers/<code>
python research/shared/source_publication.py research/issuers/<code> /tmp/<code>.html && cmp /tmp/<code>.html public/<code>.html
```
在 `site/research_catalog.json` 增加条目（同一公司的新报告期写进 `period_reports`；`source_publication`、`figure_quality_contract: FULL_SOURCE_FIGURES_V1`、`editorial_contract: FULL_PROFIT_CHAIN_V1`、`editorial_manifest`、`figures` 等于实际财务图数），然后 `python site/portal_builder.py --out public`。同步 `project-status.json` 的 `site.company_codes / company_count`。

## 6. 验收（P6）

```
python -m unittest discover -s research/shared -p 'test_*.py'
python -m unittest discover -s skills/ashare-financial-storytelling/tools -p 'test_*.py'
python scripts/qa_editorial_migration.py --codes <code> --out /tmp/qa-<code>
python scripts/check_release_contract.py && python scripts/check_handoff.py
```
`qa_editorial_migration.py` 会在真实 Chromium 中逐图检查文字裁切、标签重叠、字号，并把每张导出的 SVG 交给独立审计器（利润主图 `profit_chain_audit` / `income_flow_audit`，图族 `editorial_geometry` + `source_publication_audit`）。任何 `ACTUAL_RENDER_BLOCKED` 都要看 `failure.json` 修版式，不能放宽检测。然后打开每张图 1440 与 390 截图，按 playbook 05 打分。写 `release-gates.json`（参照 300570 的结构：PDF_BYTES、SOURCE_ROW_COLUMN、ACCOUNTING_CORE、RESEARCH_COUNTERCASE、FIGURE_SEMANTICS、BROWSER、LIVE 等，每项 status/proof/scope）和 `material-notes-review.json`（审阅者写"AI 来源审阅，非人类二审"）。

## 7. 交接与发布（P7）

- 提交分支，开 PR；等待 CI 的干净重建与双浏览器全图验收通过。
- PR 的 Cloudflare 预览出来后：`gh workflow run verify-preview-webkit.yml -f origin=https://<hash>.financials-in-visuals.pages.dev`，WebKit 375 通过后再合并（2026-11-16 曾因漏掉这一步，生产锁定在 WebKit 下失败一次）。
- 合并后等 "V10 post-merge Cloudflare production release lock" 通过，再运行 `python scripts/promote_live_receipts.py --run <run id>`，然后开一个只含回执的 PR。
- 更新 `project-status.json`、`PROJECT_STATE.md` 顶部；其他入口文件只在规则变化时修改。

## 8. 常见卡点

| 症状 | 原因 | 处理 |
|---|---|---|
| `DOSSIER_SOURCE_CELL_FALSE` | bbox 不含该数字，或数字跨行换行 | 重新 `scan`；跨行数字设 `wrapped_number: true` 并手工核对 bbox |
| `DOSSIER_FLOW_PERIOD_COLUMN_MISMATCH` | 比较期事实没加 `prior` | 修正 fact-spec |
| `DOSSIER_ACCOUNTING_IDENTITY` | 漏项（资产处置收益、汇兑收益、净敞口套期等） | `scan` 利润表全部非空行补齐；空白行不入账 |
| `SECTOR_NONEXHAUSTIVE_OR_MIXED_SOURCE_COST_PARTITION` | 分部不完整或混用产品/地区 | 只用一个维度并闭合到集团收入与成本 |
| `SECTOR_SIGNED_OR_LOSS_BUSINESS_REQUIRES_SEPARATE_CHART` | 某业务负毛利 | 不用 TYPE A；改用 components/comparison 并说明 |
| 季报 preflight 要求分部 | figures 中包含 `income` | 季报去掉 `income` family |
| `EXHIBIT_TEXT_EXCEEDS_CANVAS` | 手机 330 宽放不下这一行（保守估计） | 缩短文字；不要放宽估计 |
| `EDITORIAL_UNREVIEWED_QUESTION n` | 编辑清单标题和展开后的问题不一致（问题里有占位符或改过） | 用 `v2_builder.py apply` 或重跑 `fin_intake.py editorial` 同步 |
| `V2_BRIDGE_PARADE_n` | 正文签名桥超过两张 | 把重叠的桥在 `roles` 设为 reference |
| `LIVE_CAPTURE_CURRENT_COMPLETE_FIGURE_COUNT` | 候选改变了图数 | 候选写 `base_figure_count` |
| `PROJECT_STATE_HAS_NO_ACTIVE_PR_HANDBACK` | PROJECT_STATE 顶部新增内容过长，把交接链接推出前 3500 字 | 合并为一段，旧条目移到下方 |
