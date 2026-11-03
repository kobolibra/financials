# Financials in Visuals — 零猜测跨对话交接协议

> 有效入口：[START_HERE.md](../START_HERE.md) → [project-status.json](../project-status.json) → [PROJECT_STATE.md](../PROJECT_STATE.md) → 完整 Skill + 五份研究规范。历史记录在 `docs/history/`，不作为现行命令来源。

## 开始新对话（必须）

1. 读取 GitHub **实际 main HEAD**，而非本对话的记忆。核对 `project-status.json` 与 `site/research_catalog.json` 和 `public/index.html`。
2. 全文读取 Skill 和 01–05 手册，知道两条并列基线：**中国会计/行业机构研究** 与 **AEI/FT 启发的原创高水准财务视觉出版**；明确“不用柱状图代替本应出现的财务桑基图”。
3. 取得用户提供的新发行人原始完整 PDF 文件或交易所官方完整 PDF 字节。检查发行人、期别、合并/母公司、单位、审计/修订和 SHA。私人文件无法取得时 `SOURCE_BYTES=NOT_CHECKED`。
4. 读取最相关的**原有完整报告/账本/生成器**和最新 Actions 的真正结果。所有已经发布的公司报告（含初始七家和后续扩容）不得被新文件覆盖或失去统一目录入口。
5. 用 5–8 行写明当前公司、数据可得性、已经读过哪些规范、将用什么行业会计方式、针对哪些重大附注工作、将输出何种独立 HTML 和 QA。这不是冗长计划，而是缺失信息确认。

## 执行中（实际质量）

遵守 [发布清单](REPORT_RELEASE_CHECKLIST.md)：来源原文行/列/页 → 数据单位和范围 → 全三表、附注、正负调节 → 行业指标和对立观点 → 每一张图的研究问题/图形语法/金额守恒/零点/来源 → 大小屏截图 → 原网页真实跳转。**任何发现的错误应该直接追原始来源并修正**，不能只登记为“待复核”而继续宣称顶级交付。确实缺原始证据就公开标记 `NOT_CHECKED` 并尽最大努力完成安全范围内的工作。

## 结束本次（交接就绪的最低记录）

在 `PROJECT_STATE.md` 留下一个最新、清晰且在顶部可见的活动状态；同步更新 `project-status.json` 结构化字段；必要时把大量历史增量迁到历史文档，不能堆 30k 字的“最新”互相矛盾。

交接信息必须写清：
- 仓库/分支/当前提交（读取获得，不能猜）及实际修改文件；
- 公司、源报告来源、PDF SHA/页数/交易所公告日期及是否重编；
- 真正改动过的源账本/生成器/HTML/正文；
- 来源分类、账目勾稽、重大附注、研究反证、图形语法、视觉、浏览器、Git 与公开站点**各自** PASS/FAIL/NOT_CHECKED；
- 未解决的问题**具体到下一份原始附注或下一条测试**，不得笼统地写“还需优化”；
- 最近 GitHub Actions 对应的**确切提交**；若新提交尚未经过线上验证，不能沿用旧 CI 绿色状态；
- ChatGPT Library 或仓库内原始文件位置（不假定上轮 `/mnt/data` 文件仍在），独立新会话可用的具体阅读命令；
- 发布后独立公司路由，本站首页目录是否同步，是否破坏以前内容；
- 立即可执行的下一个行动。

执行 `python scripts/check_handoff.py`；提交交接文档、源码和回归测试。优先核验真正生产 HTTP/浏览器，而不是只报 GitHub API `success`。

## 关于 Skill 的真实可发现性

`AGENTS.md` 和 `.github/copilot-instructions.md` 为支持这些协议的仓库编码助手提供入口，但**不能保证任意 ChatGPT 新聊天自动检索你的私有/公开 GitHub 仓库**。新聊天必须有 GitHub 访问，或收到直接链接/上传的 Skill。不要声称已完成 ChatGPT Skills 目录安装。推荐使用 [新会话启动消息](NEW_SESSION_PROMPT.md)。

## 状态分级

`PASS`：有当前提交、原始来源/测试结果与真实输出支持；`FAIL`：明确不一致或测试失败；`NOT_CHECKED`：没有检验；`NOT_PROVEN`：通用性等尚缺独立验证。**已显示的 10 图、11 图、36 图或 21 屏检查不能用来暗示全套机构级研究通过。**

## 用户层持久上下文

普通 ChatGPT 请优先在名为 Financials in Visuals 的 Project 内开新会话，并一次性将 `docs/CHATGPT_PROJECT_INSTRUCTIONS.md` 的内容粘贴到 **Project settings**。这项个人账户 UI 配置不能由 GitHub commit 代替；Codex 仓库工作环境使用 `.agents/skills/ashare-financial-storytelling/SKILL.md` 自动发现包装器，仍需实际执行全文 Skill。详见 `docs/SETUP_PERSISTENT_CONTEXT.md`。


## v8.4 持续迭代的额外交接事务

新增发行人时，除了现行 `PROJECT_STATE.md` 和 `project-status.json`，必须提交该公司的 `research/issuers/<code>/release-gates.json`：实际 PDF 归档及 SHA、源页面行列含义、行业独立会计模型、源附注异常、图形真实宽度、三屏截图、HTML 重建、GitHub main/Actions 与 Cloudflare 本次版本指纹。不可把复制自另一家公司的 PASS 当作本公司的 PASS。

新的研究/会计/视觉/发布失误必须反向更新唯一 Skill、`skills/ashare-financial-storytelling/quality-regressions.json`，新增正常+恶意反例，并在 CI 执行。每次写清 **根因修复是否可迁移到其他公司**（单个发行人测试 ≠ 泛化）。必须跑 `python scripts/check_release_contract.py` 和其对抗测试，再跑 `python scripts/check_handoff.py`。完整流程详见 [SKILL_EVOLUTION_PROTOCOL.md](SKILL_EVOLUTION_PROTOCOL.md)。

上一份报告旧 Cloudflare 的 PASS 不适用于当前代码版本；任何 LIVE FAIL 需保存 exact run id 与尚未部署的实际结构差异，不能在下一次新聊天淡化成 `NOT_CHECKED` 或历史成功。
