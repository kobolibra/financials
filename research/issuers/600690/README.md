# 海尔智家 600690 · 2026H1 原始财报研究

来源：CNINFO完整发行人中报，2026-08-28，192物理页，未经审计。归档PDF SHA256 `fe5814830fac441f9f71b77472c1090ee451d2cf411ad3ce0da469ffb898ed97`。本目录是新公司实际接入样本，不是把旧公司数字换名。

`source-ledger.json` 保留原元、原页坐标、期间、合并范围和推导；`publication.json` 是作者研究稿、全部图形规格、23项精确等式和12项重大附注主题。`figure-briefs.json`、`qa.json`、独立离线 `public/600690.html` 均由同一通用发布器生成，不以公司代码选择坐标。成本相减计算、主营产品与经营分部、净利润与CFO、2025年中与2025年末现金、研发费用与转损益分别处理。

复现：

```sh
python research/shared/source_publication.py research/issuers/600690
python -m unittest discover -s research/shared -p test_source_publication.py
python scripts/qa_editorial_migration.py --codes 600690 --out research/issuers/600690/visual-qa
python scripts/check_release_contract.py
python scripts/check_handoff.py
```

`visual-qa/result.json` 与33份实际可见SVG、33张逐图PNG绑定当前完整HTML字节；截图和源码检查不是人类审稿认证。所有新公司通过目录 `source_publication` 自动纳入同一云端确定性重建、全图源金额、几何和三屏导出检查。当前待真实合并及生产核验；不得借旧站点绿色。8–12季度、独立同行市场估值、独立人类二审尚未完成，不发布其结论或认证。
