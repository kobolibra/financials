# A股财报研究与可视化技能 · 目录说明

执行合同只有一个：[SKILL.md](SKILL.md)（v10）。本 README 只说明文件布局。

| 路径 | 作用 | 何时读 |
|---|---|---|
| `SKILL.md` | 质量线、七阶段工作流、图形合法性、验收门、拒绝清单 | 每次 |
| `playbooks/01_REPORT_TYPES.md` | Q1/H1/9M/FY 各自可用数据、比较期、可做的图 | 新公司/新期间 |
| `playbooks/02_ANALYSIS_FRAMEWORK.md` | AEI 问题顺序的 A 股化、驱动式、取证清单、行业路由与实现状态 | 写研究备忘录 |
| `playbooks/03_EXHIBIT_SYSTEM.md` | 图形清单、节点标注规范、设计 token、能力缺口、版式自评 | 选图/改图 |
| `playbooks/04_PRODUCTION_RUNBOOK.md` | 从 PDF 到上线的逐条命令 | 生产 |
| `playbooks/05_QUALITY_RUBRIC.md` | P0、评分表、逐图截图自评 | 发布前 |
| `tools/fin_intake.py` | `init / find / scan / facts / preflight` 原件入库与源格账本工具 | P1–P4 |
| `templates/` | 出版稿模板、事实规格示例、研究备忘录模板 | P2–P4 |
| `research/01–05` | 一手来源与推理依据的背景手册 | 判断有争议时 |
| `quality-regressions.json` | 历史真实错误的可执行回归登记 | 改进技能时 |

历史目录（不作为现行指令）：`engine/`、`scripts/`、`v7/`、`nextlevel/`、`examples/`、`outputs/`、`qa/` 是早期出版器与回归夹具，仍被旧报告的重建流程使用，不要删除；`references/` 中的 v7 文档已移至 `docs/history/skill-references-v7/`。新报告一律走 `research/shared/source_publication.py`。

技能不会自动安装到普通 ChatGPT 会话；Codex 在仓库内通过 `.agents/skills/` 入口发现它。
