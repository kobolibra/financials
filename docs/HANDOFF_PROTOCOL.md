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

## 2026-11-04 · 新行业压力测试交接（601628 保险）

通过同一零上下文入库流程：`main`→完整 Skill/研究手册→官方原始104物理页PDF字节/源SHA→133条类型化事实→33项原PDF(x,y)→保险合同服务及投资负债关联→CAS带符号三表与**仅直接法**CFO→真实只含同口径互斥总保费来源的加权桑基→10张具原始页码原创图→1440/768/390实Chrome与每图截图→完全离线HTML→唯一目录新增路由。机器检查：`python research/issuers/601628/verify_source.py`、`python -m unittest research/issuers/601628/test_accounting.py -v`、`python research/issuers/601628/publish.py --out public/601628.html`、`python research/issuers/601628/qa_browser.py`、`python scripts/check_handoff.py`、`python scripts/check_release_contract.py`。已复核原始源 SHA `b094bf337309e30564dda86ff4b3c4d66aeeb37ce0357a3568e246569f0e2943`；官方 SSE 二次比对、完整重大附注独立复核、第二人类审稿、外部多期同业估值明确未完成。**每次跨对话重新读真实 main、行动结果与 `project-status.json`，不要假称一个 PR 的动作证明下一个提交，亦不得将 Skill 库文件声称自动安装在 ChatGPT。**

## 2026-11-04 · 第11家公司正式上线与可移植 LIVE 取证闭环（v8.6.1）

中国人寿601628 2026H1独立公司报告已在生产线上真实可达 `https://financials-in-visuals.pages.dev/601628`。最近确切已验证的真实 `main` `d11638f0c76ff8aef2beb163a1028f176123bbdc`，GitHub Actions [41771178361](https://github.com/kobolibra/financials/actions/runs/41771178361) 实际 Cloudflare Chromium 1440/768/390 + 11条独立路由 + 10张 SVG + 10张原始证据表 + 返回唯一主目录 PASS；网页完整 SHA `051a8ecb56cb200f4c411bb53ad672096cfb299e297f149fd58aad334cbfb763`，主目录 SHA `f625453172a83b7db38d0c5a67ddbecd84fbf078bc9f78c2e20c45b00b23ab41`。金融研究仍只称 source_limited_preview（完整附注独立审查/同行估值/真正第二名人类编辑/上交所第二源文件字节一致 NOT_CHECKED）。

**新的真实失误及防复发**：虽然上一轮真网页点击 PASS，源代码一度在返回 `/#companies` 之后才填写 `actual_dedicated_article_final_url`，造成公司页 URL 被错误保存成首页 URL。新增统一纯工具 `research/shared/live_route_evidence.py`、`scripts/test_live_route_evidence.py` 正面/恶意测试；在文章页上独立抓取真实 URL，再抓返回 URL，严格同域/同 ticker，正式网页已出现过最终保费桑基节点绘制错误，`qa_cloudflare_live.py` 也须对源节点、最终汇总金额、真实填充和高度复核；六张真实线上完整截图记录 SHA 与本次准确 main commit。公开 `CLOUDFLARE_LIVE` 通过状态与编译的完整 HTML 64位指纹要在 `scripts/check_release_contract.py` 绑定，篡改即 FAIL（PUB-033、VIS-034、PUB-035）。

**下一次新会话最重要**：`START_HERE.md` 不能声称固定 10/11 家，从 `project-status.json` 与 `site/research_catalog.json` 的**真实最新 main**算；新手动反例 HND-036。上述新 8.6.1 代码只有在本次新增 Git commit 上通过 Actions 且真实线上验收后才可将其作为新版本 PASS，不能引用旧 #41771178361 代替新代码验收。

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


**v8.4.2 新增切实的跨窗口一致性**：新会话不能仅看 Skill 的版本号。核对本次原 PDF SHA、source ledger 真实字段、figure briefs、已发布页面内嵌的事实和源说明相同；执行 `scripts/check_release_contract.py`，且更改原始事实/来源后重新运行发行人出版社，并确认 `public/<code>.html` 逐字节重建。前次 688220 第一次 MAIN 重建 [41667517537](https://github.com/kobolibra/financials/actions/runs/41667517537) 失败、修复后 [41667953097](https://github.com/kobolibra/financials/actions/runs/41667953097) 通过，是不可丢的反例证据。不同跑次要记录各自发生于哪个 SHA，避免过期 FAIL/PASS 冒充最新结果。
