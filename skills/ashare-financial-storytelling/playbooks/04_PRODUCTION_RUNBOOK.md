# Playbook 04 · 生产手册：从一份原始 PDF 到线上报告

以下命令都在仓库根目录执行。`T=skills/ashare-financial-storytelling/tools/fin_intake.py`。最新真实范例：`research/issuers/300570`（太辰光 2026H1，工业 TYPE A），可直接对照其 `source-ledger.json`、`publication.json` 和 `research/editorial-20261113/300570.json`。

## 0. 环境

```
python -m venv .venv && . .venv/bin/activate
pip install pymupdf playwright && python -m playwright install --with-deps chromium webkit
```
本地截图需要 Noto CJK 字体；没有中文字体时截图会出现方块，只能检查布局，不能作为视觉证据。先 `git fetch && git log origin/main -1` 确认当前 HEAD，并按仓库分支策略建分支。

## 1. 取得原件（P1）

- 来源：巨潮资讯（`https://static.cninfo.com.cn/finalpage/<日期>/<公告ID>.PDF`）或交易所官网。只下载完整报告，不要摘要/英文版。
- 下载后确认文件以 `%PDF` 开头（服务器偶尔返回 HTML 错误页）。

```
python $T init --code 300570 --pdf /path/report.pdf --url https://static.cninfo.com.cn/finalpage/.../xxx.PDF --short 太辰光
```
产出：`research/issuers/<code>/source/`（归档原件）、`extracted/pNNN.txt`、骨架 `source-ledger.json`、模板 `publication.json`。打开 JSON 补全 `issuer.short / industry / sector_adapter / accounting_route / income_figure_title`。

## 2. 建账本（P2）

```
python $T find --code <code> --statements      # 定位三表、补充资料、收入成本附注、非经常损益
python $T scan --code <code> --page 40         # 列出该页每行的数字列 [1] [2] ...
```
写 `research/issuers/<code>/fact-spec.json`（示例 `templates/fact-spec.example.json`）：每个事实给 `page`、行标签正则 `row`、数字列 `column`、`type`（flow/stock）、`label`；比较期流量加 `"prior": true`；存量写 `period`（如 `2025-12-31`）；可加 `expect` 做双重核对。然后：

```
python $T facts --code <code> --spec research/issuers/<code>/fact-spec.json
```

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

编辑清单：复制 `research/editorial-20261113/300570.json` 的结构，改写 `facts / sources / stages / editorial`，`editorial.figures` 与 `publication.json` 的 figures 一一对应并给出 role/rationale。

```
python $T preflight --code <code>     # 源格 + 恒等式 + 编辑 lint + 编辑清单存在
```
`PREFLIGHT_PASS` 之前不要出版。lint 只是下限，通过 lint 不代表文章好。

## 5. 出版（P5）

```
python research/shared/source_publication.py research/issuers/<code>
python research/shared/source_publication.py research/issuers/<code> /tmp/<code>.html && cmp /tmp/<code>.html public/<code>.html
```
在 `site/research_catalog.json` 增加条目（`source_publication`、`figure_quality_contract: FULL_SOURCE_FIGURES_V1`、`editorial_contract: FULL_PROFIT_CHAIN_V1`、`editorial_manifest`、`figures` 等于实际财务图数），然后 `python site/portal_builder.py --out public`。同步 `project-status.json` 的 `site.company_codes / company_count`。

## 6. 验收（P6）

```
python -m unittest discover -s research/shared -p 'test_*.py'
python -m unittest discover -s skills/ashare-financial-storytelling/tools -p 'test_*.py'
python scripts/qa_editorial_migration.py --codes <code> --out /tmp/qa-<code>
python scripts/check_release_contract.py && python scripts/check_handoff.py
```
然后打开每张图 1440 与 390 截图，按 playbook 05 打分。写 `release-gates.json`（参照 300570 的结构：PDF_BYTES、SOURCE_ROW_COLUMN、ACCOUNTING_CORE、RESEARCH_COUNTERCASE、FIGURE_SEMANTICS、BROWSER、LIVE 等，每项 status/proof/scope）和 `material-notes-review.json`（审阅者写"AI 来源审阅，非人类二审"）。

## 7. 交接与发布（P7）

- 提交分支，开 PR；等待 CI 的干净重建与双浏览器全图验收通过。
- 合并后核对生产站全文件字节与源码一致、首页往返、每图下载；回执写入 `live-release-receipt.json` 并更新 `release-gates.json` 的 LIVE 门。
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
