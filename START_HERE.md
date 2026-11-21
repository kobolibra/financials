# 从一份原始财报开始

当前发布状态见 `project-status.json`，发行人和既有报告入口见 `site/research_catalog.json`。仓库方法见 `skills/ashare-financial-storytelling/SKILL.md`。历史入口保存在 [交接档案](docs/history/START_HERE_2026-11-20_ARCHIVE.md)。

新会话的最短启动指令：

> 用本仓库的财报 Skill，从附件这一份完整原始财报 PDF 生成一份中文离线研究报告，保留源格账本、研究简报和逐图验收。

本地启动：

```bash
python -m pip install pymupdf
T=skills/ashare-financial-storytelling/tools
python "$T/start_report.py" /absolute/path/filing.pdf
```

编稿前必须执行 [自主主编与视觉总监闭环](skills/ashare-financial-storytelling/playbooks/09_SELF_DIRECTED_DELIVERY.md)，再读 [研究与主编决策](skills/ashare-financial-storytelling/playbooks/08_EDITORIAL_DECISIONS.md)。前者会主动从原始账本识别没有被分析的重大问题、对照两份成熟同库报告、生成逐图真实浏览器审美返工清单，不要求用户逐条指出漏项。

```bash
python research/shared/autonomous_editorial_audit.py --code <code> \
  --out work/editorial/issues.json \
  --review-template work/editorial/tasks.json
# 自行处理所有缺漏、对照证据、真实截图并更新评审后：
python research/shared/autonomous_editorial_audit.py --code <code> --strict
```


入口在 `work/dossiers/<六位代码>/<报告期>/` 保留原件、页文本、账本、能力计划和可用的撰稿草案。继续按 [离线报告流程](skills/ashare-financial-storytelling/playbooks/07_EVIDENCE_TO_EDITORIAL.md#0-从单份-pdf-到离线成稿) 完成证据复核、研究和验收。本轮复测规格、结果、已知边界和准确命令见 [复验记录](research/quality/pdf-generalization-20261120/README.md)。

新会话从 `START_HERE.md` 启动。独立财务、视觉审阅和正式部署按各自证据登记，缺项为 `NOT_CHECKED`。

[PR35 历史交接](docs/ACTIVE_PR35_HANDOFF.md) 保留当时的来源与验收回执。
