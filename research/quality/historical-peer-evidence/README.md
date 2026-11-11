# 连续季度及同行原件证据包

已保存41份CNINFO官方原始PDF（含三家研究目标2024–2026各期、三家同行2025/2026H1，以及协助十一家二审取得的天孚/新易盛2026H1）。`all-source-manifest.json`绑定官方URL、SHA256、原字节大小及物理页数。`*_query.json`保存官方公告查询回应；`*.txt`为PyMuPDF逐物理页文本，仅辅助索引，不替代PDF。

## 读者结论和财务表

- `reader-conclusions.json`：三家公司各五段公司特定判断，检验2026H1判断与新Q3证据，并列最强替代解释、同行限制及重述隔离。论证区分会计差额、管理层经营解释和未识别的价格/销量因果。
- `quarterly-panel.json/csv`：2024Q4至2026Q3，每家八个连续单季、四项合并流量，共96项原元金额。Q1直接披露；Q2/H1-Q1、Q3/9M-H1、Q4/FY-9M按Decimal差分，每个操作数有原PDF物理页和SHA。2024Q4及2025全年各季度收入/CFO另由年报直接单季披露交叉核对，30项均相等。
- `peer-comparison.json`：华能水电、复星医药、晶晨股份2026H1/2025H1收入、成本、研发费用和CFO；9项直接附注研发/资本化证据及会计口径限制。
- `statement-facts.json`：原报合并流量两列事实（当前/同期），含页码和原行。非目标2024H1两个特殊分页收入格不自动提取，以免错列；不影响目标96项操作数。

## 版本与结论边界

五项实际版本差异保留在`quarterly-panel.json.comparative_revisions`：长江2024Q1收入、成本、CFO及2024H1 CFO；翱捷2024Q1营业成本。不能把这些原报和后来同期重述拼起来做旧期季度差分。本目标96项操作数均未引用这些有差异的旧报告；2024Q4收入/CFO又有年报单季原披露支持。仍不能把整段序列称作已完成恒定合并范围的因果面板，尤其长江同控合并/不同版本问题需要继续解释。翱捷旧Q1成本差异未获得完整注释解释，明确隔离其旧期毛利同比。

翱捷2026H1官方CNINFO下载原字节SHA `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`，与仓库原镜像相同。此事实证明CNINFO来源字节一致性；不替代SSE官网直接下载的字节核对。

## 可重复验证

使用具备PyMuPDF的Python：

```
python research/quality/historical-peer-evidence/extract_panel.py
python research/quality/historical-peer-evidence/build_panel.py
python research/quality/historical-peer-evidence/crosscheck_annual.py
python research/quality/historical-peer-evidence/build_peer.py
python research/quality/historical-peer-evidence/build_conclusions.py
python research/quality/historical-peer-evidence/test_evidence.py
```

实跑6项测试通过：41份原件SHA与页数；24季/96公式和原物理页操作数；30项年报独立单季核对；五项旧期版本差异隔离；三家公司2026Q1/H1/Q3全部36项同期列与2025原累计一致；三同行/结论/附注锚点。它们不代表全部附注审计、人类独立审稿或数量价格因果识别。
