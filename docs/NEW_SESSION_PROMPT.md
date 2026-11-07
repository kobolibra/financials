# 开新 ChatGPT 对话时的启动指令（可直接复制）

**重要候选接续（2026-11-07）：** 如果目标是 financials PR #35、财务拆解深度、AEI 信息设计或桑基图稳定产出，必须在确认最新 main 与 PR 真实 HEAD 后阅读 docs/ACTIVE_PR35_HANDOFF.md、research/quality/active-pr35.json 和 docs/AEI_RESEARCH_EDITORIAL_SCORECARD.md；执行 python scripts/check_pr35_quality_handoff.py。旧 main 的“V10 四家公司 390 失败”是生产真旧状态，PR 改造是独立候选状态，不能混写。新 WPS 桑基/茅台负毛利放大图不能使用此前旧 SHA 通过截图；独立机构级人类财经和视觉评审尚 NOT_CHECKED。



请继续我的 **Financials in Visuals** 项目。GitHub 真实工作仓库：

https://github.com/kobolibra/financials

**在任何分析、编码、展示或发布前，必须通过 GitHub 连接或者网页访问，逐个实际读取 main 分支这些文件；不能凭对话记忆猜测已经读过：**

1. `START_HERE.md`
2. `project-status.json` + `PROJECT_STATE.md`（只采用现行状态，不要被历史 archive 的旧 “latest v9” 误导）
3. `AGENTS.md` + `docs/HANDOFF_PROTOCOL.md` + `docs/REPORT_RELEASE_CHECKLIST.md`
4. `skills/ashare-financial-storytelling/SKILL.md` **全文**
5. 该 Skill 的 `research/01`、`02`、`03`、`04`、`05` **五份全文**
6. `site/research_catalog.json`、最相关的原有真实公司报告、数据账本、最新 GitHub Actions 和 Cloudflare 实际状态

**不要假设 `SKILL.md` 已经装成 ChatGPT 全局 Skill。读不了就明确指出；绝不可说“我已经严格按 Skill”但实际上没读。**

我的新任务是：**按照原有完整 Skill 对我提供的这家公司的原始财报进行机构级财务研究、财报拆解、批判性复核与 App Economy Insights 水准的原创可视化出版。**

要求：
- 原始 PDF 完整字节、报告期/币种/合并口径/修订版/SHA 与原始行列、重大附注、三张报表勾稽必须准确；任何未知标为 NOT_CHECKED，不能猜。
- 两条基线并列：深入的公司/行业会计和经营实质研究，以及至少同等重视 AEI/FT 风格的高水平财务信息设计；研究论点和反证先于图表。
- 根据关系选择真财务桑基图（金额严格守恒才画）、带符号瀑布、完整利润/现金/资本/分部/增长/历史图等。不同会计维度不能相加，不能制造“未披露差额”业务；不是简单堆图表。
- 新公司要在**同一个** https://financials-in-visuals.pages.dev/ 七家公司（未来为 N 家）公司研究库添加新的**独立、离线可用的完整 HTML**。不得再次做独立四公司/新版本入口，不得破坏已有报告。
- 强制真实页面截图审查（1440/768/390），尤其中文字体、图形标注、Sankey 尺度/数据源、手机端阅读；测试导航、SVG、源码重新生成、GitHub 和 Cloudflare 公开部署。
- 财务研究审查、原创设计审查和工程/浏览器审查为不同的质量门槛；每项 PASS/FAIL/NOT_CHECKED。不能用“CI PASS”、“图表数量”冒充“顶级研究交付”，也不能假装另一名人类审稿人已经签字。

**开始时只需报告已经实际读取的关键规范、当前真实项目状态和此次财报如何进入既有系统，然后推进真实研究。** 不要让我重新讲述旧对话，也不要用方案和赞美代替作品。

结束前必须按照 `docs/HANDOFF_PROTOCOL.md` 更新长期交接文件；如果某项需继续追查，直接查原始文件完成，不要无谓地把它推给下一次对话。

> **更短的固定使用方式**：若已把 [Project 固定指令](CHATGPT_PROJECT_INSTRUCTIONS.md) 放进 ChatGPT Project settings，今后在**同一 Project 内**直接上传新 PDF 并说“按 Financials in Visuals Skill 分析并发布这家公司”。但每次仍须显式读取 GitHub main；Project 指令不能保证 GitHub 最新文件自动同步。一次性设置流程见 [SETUP_PERSISTENT_CONTEXT.md](SETUP_PERSISTENT_CONTEXT.md)。


**新增 Skill v8.4 质量闭环（所有新对话必读并执行）**：读取 `docs/SKILL_EVOLUTION_PROTOCOL.md` 与 `skills/ashare-financial-storytelling/quality-regressions.json`；先运行 `python scripts/check_release_contract.py` 和 `python scripts/check_handoff.py`，确认新公司的 `research/issuers/<code>/release-gates.json` 对本次原始 PDF/生成网页/逐图源证据一一对应，历史七家豁免不得延伸给未来公司。针对任何新的源会计、视觉或上线错误，先修源头和真实网页，加入可执行反例、更新唯一 Skill 和交接；不允许只有汇报没有复现与回归。
