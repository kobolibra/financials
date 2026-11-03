# 让后续新聊天真正接续：ChatGPT Project + Codex Repo Skill

此文记录的是**两种不同的真实发现机制**，避免把“仓库里有 SKILL.md”误当成“所有 ChatGPT 新聊天会自动执行”。

## A. 普通 ChatGPT：一次设置 Project 上下文

官方机制允许把多次对话、资料文件、长期指令归到同一 ChatGPT Project；**Project 指令适用于该 Project 内的会话**，并不自动把 GitHub 仓库中的所有代码或 PDF 挂载进聊天。参考 [ChatGPT Projects 官方帮助](https://help.openai.com/en/articles/10169521-projects-in-chatgpt)。

1. 在 ChatGPT 侧边栏创建一个 Project，建议命名 **Financials in Visuals**。
2. 打开该 Project 的更多菜单（•••）→ **Project settings**，把 [固定 Project 指令](CHATGPT_PROJECT_INSTRUCTIONS.md) 全文粘贴进去。这是**一次性的用户界面设置**；GitHub 提交不能替你修改当前 ChatGPT 账户设置。
3. 可把关键参考资料放入 Project Sources，优先为 `START_HERE.md`、`SKILL.md`、五份研究手册提供可靠访问途径。**GitHub 会更新，所以每次仍要读取仓库最新 main；不要只依赖旧上传副本。**
4. 把目前这个已有的长对话（如果 UI 提供 **Move to project**）移动进去，以便项目中保留上下文；过去对话并不是替代文件事实的可靠来源。
5. 以后**从这个 Project 内**开新聊天，上传新的完整财报 PDF，直接说“按 Financials in Visuals Skill 完成这家公司研究并发布”；助手仍要显式检查 Skill 和相关仓库文件。也可以复制 [新会话完整启动提示](NEW_SESSION_PROMPT.md) 到任意普通聊天。

**这里已完成的只是仓库指令材料，未擅自声称替用户创建 Project、修改 Project settings 或安装全局 ChatGPT Skill。**

## B. Codex / 以仓库为工作目录的 Agent：标准技能自动发现

按 [OpenAI Codex 官方技能文档](https://learn.chatgpt.com/docs/build-skills) 的仓库级约定，Codex 从项目目录到 Git 仓库根扫描 `.agents/skills/`。已经在仓库中增加：

`.agents/skills/ashare-financial-storytelling/SKILL.md`

该文件具有标准的 `name` / `description` 元数据，准确触发条件包括 A 股公司财报、原始 PDF、来源核算、AEI 式视觉叙事、财务桑基图和既有七公司网站的持续工作。**这只是发现包装器**：它必须全文读取唯一正文 `skills/ashare-financial-storytelling/SKILL.md` 与 01–05 手册，而不能变成另一份漂移的 Skill。根目录的 `AGENTS.md` 和 `.github/copilot-instructions.md` 进一步对支持它们的编码助手生效。

使用：在 Codex 打开这个 Git 仓库，并在仓库内工作。工具确实支持发现时应看到 `ashare-financial-storytelling`；如果没有，请在 Codex 中显式指定该技能并检查版本/仓库工作目录，必要时重新加载。**发现可用不等于模型每次都一定选择执行；真正执行还由交接测试与本次运行证据验证。**

## C. 已实现自动回归

仓库 CI `.github/workflows/verify-handoff.yml` 在 Skill、现行状态、README、Agent 指令、发布清单与首页目录变动时阻断以下错误：

- 项目 Skill 版本与 manifest 不符、五份手册丢失；
- 七家原公司或路由在新首页缺失，四家公司专区重新占据首页；
- 已解决的天孚/新易盛收入差额被改回伪造的“未列示差额”流带；
- 文档宣称旧 v9 是最新、README 关闭真正 Actions；
- 未提供对应证据却声称七家重大附注全部人工复核/有独立人类审稿签字；
- 项目级 Codex Skill 发现包装器不存在或指向错误正文。

使用 `python scripts/check_handoff.py` 运行同一源检查；每次新增公司后需要同步公司研究目录和机器状态。

## 一句能长期复用的启动话术

> 按我这个 GitHub 仓库 `kobolibra/financials` 的 `START_HERE.md`、**完整最新版** `ashare-financial-storytelling` Skill 和五份研究手册，研究这份新上传的公司财报，复用原有源引擎，最终出独立精致 HTML 并加入统一网站。先实际读取当前项目状态，完整执行财务、视觉和生产验收，不要沿用历史摘要或自称已经完成未验证的工作。
