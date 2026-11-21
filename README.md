# Financials in Visuals · A 股财报深度研究与可视化出版

**现在的正式入口：[START_HERE.md](START_HERE.md)。** 新 ChatGPT 对话、电脑代理、协作分析师都应从该文件开始，而不是从本项目历史对话或旧版样例推断现状。

**生产站点：** https://financials-in-visuals.pages.dev/ · **GitHub：** `kobolibra/financials` / `main`。

## 这是一个研究出版系统，不只是图表网站

独立研读上市公司原始披露与重大附注，精确勾稽三大报表，形成公司特有商业模式和反证分析，再采用受 [App Economy Insights](https://www.appeconomyinsights.com/) 和 FT 等公开方法启发的**原创**财务视觉叙事。严格执行 [完整 Skill](skills/ashare-financial-storytelling/SKILL.md) 及 [01–05 研究规范](skills/ashare-financial-storytelling/research/)；账户记忆不能代替实际读取这些文件。

公司数、公司与报告期路由及正式 HTML 的唯一实时来源是 `site/research_catalog.json`（2026-11-21 时主目录 15 家，另有跨期报告）。历史 11 家、旧 V10 与 PR #35 的图形状态属于历史记录，**不能作为今天的全库审美或研究深度认证**。本库现有 [自主主编闭环](skills/ashare-financial-storytelling/playbooks/09_SELF_DIRECTED_DELIVERY.md) 和 [证据驱动编辑审计](research/shared/autonomous_editorial_audit.py)：新增报告应主动核对重大研究问题、两份同库现时优秀报告、每张真实桌面/手机图及跨公司 SHA 回归，不需要用户替系统逐项查漏。独立人类财经、视觉二审仍是 NOT_CHECKED；不要把机器通过或 12 张图称为全部行业的顶级质量。

## 第一次加入公司 / 新对话继续工作

1. [新会话复制启动指令](docs/NEW_SESSION_PROMPT.md)；也可将新的公司原始 PDF 上传至新会话。
2. 读取 [现行状态](PROJECT_STATE.md)、[机器校验清单](project-status.json)、[Skill](skills/ashare-financial-storytelling/SKILL.md)、其五份手册、[交接规范](docs/HANDOFF_PROTOCOL.md) 和 [财报发布门槛](docs/REPORT_RELEASE_CHECKLIST.md)。
3. 先验证报告原始 PDF 字节/SHA/期别与来源，再生成精确账本、行业论文式财务解读、每张图的数据约束与反证。
4. 生成**独立离线 HTML**，实际查看桌面、平板、手机和来源表，再在当前唯一研究库增加公司。不能因为 CI 绿灯就说“超越 AEI”。
5. 结束前更新状态/证据，执行：`python scripts/check_handoff.py`，并核查新报告的独立财务及浏览器验收。

**已解决**：300394 p.140 其他业务与 300502 p.104 “按业务类型/其他”的真实收入分类，不能再把它们叫未知收入差额。详见 [附注复核报告](docs/2026H1_OPTICAL_REVENUE_NOTE_CLASSIFICATION_AUDIT.md)。

**仍未完成**：现有十家公司的完整重大附注独立系统复核、真正独立人类二次审阅、所有公司的多季度/同业估值，以及任意行业的完全自动复现。请以 `NOT_CHECKED` 标明，不可冒充已通过。

## 维护及部署

- `site/research_catalog.json` 定义唯一公司研究库；`site/portal_builder.py` 生成 `public/index.html`。修改公司目录后执行 `python site/portal_builder.py --out /tmp/financials-portal` 并与发布 HTML 比较。
- 旧光通信报告生成器在 `skills/ashare-financial-storytelling/v7/engine/`；后四家来源驱动研究引擎在 `research/rebuild-v10/`。
- 发布目录为 `public/`；Cloudflare Pages：`main`、Framework `None`、无构建命令、输出目录 `public`。
- GitHub Actions 已配置真实站点、财报来源与浏览器检查；**必须执行 GitHub Actions 的实际核验**，不能沿用早期版本的关闭验收说明。
- CI 和完整发布准则见 [docs/REPORT_RELEASE_CHECKLIST.md](docs/REPORT_RELEASE_CHECKLIST.md)；旧项目状态留档于 [docs/history/PROJECT_STATE_ARCHIVE_2026-11-03.md](docs/history/PROJECT_STATE_ARCHIVE_2026-11-03.md)。

`skills/ashare-financial-storytelling/SKILL.md` 是仓库中的项目 Skill，**不是自动安装到 ChatGPT 的全局 Skills**。普通新对话应使用 [新会话指令](docs/NEW_SESSION_PROMPT.md) 明确要求读 GitHub；安装或连接能力依 ChatGPT 实际当前功能决定，不在本仓库内虚构“已安装成功”。

### 自动发现范围的区别（Codex vs ChatGPT）

仓库已经提供 [Codex 仓库级 Skill 包装器](.agents/skills/ashare-financial-storytelling/SKILL.md)：Codex 在**已打开本仓库**时可以按官方约定发现它，再读取唯一完整 Skill。普通 ChatGPT 不会因为这些 Git 文件自动把它安装成全局 Skill。要让未来每个 ChatGPT 项目聊天具有固定指令，请按 [一次性 Project 设置说明](docs/SETUP_PERSISTENT_CONTEXT.md) 操作，复制 [Project 长期指令](docs/CHATGPT_PROJECT_INSTRUCTIONS.md)。**这一账户级 UI 操作尚未代替用户完成。**
