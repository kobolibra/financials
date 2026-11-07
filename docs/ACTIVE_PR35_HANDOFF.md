# PR #35 零记忆接续｜当前研究与视觉质量工程

> 本文是 **候选 PR 状态**，绝不等同 main 正式上线。每次新会话必须重新获取真正的 GitHub main HEAD、PR #35 HEAD、Actions 最新状态和 Cloudflare 当前完整 HTML SHA。不能把这里的历史观测当作现在。机器合同：research/quality/active-pr35.json、scripts/check_pr35_quality_handoff.py。

## 当前确定的研究/编辑目标

稳定输出有明确行业经营命题、可量化驱动、最强反证、同原始披露账本守恒的优秀金融可视化，尤其是能一眼看出业务赚钱机制的真实桑基图。App Economy Insights / FT 只作为公开方法、信息效率与视觉设计基准；不能用图表数或 CI 全绿宣称超越。

## 最新实际候选版源码及交接机测（2026-11-07，本段是 SHA 绑定记录）

四份新 SVG 已完成实际原 PDF 检查、按原始元重新生成和 1440/768/390 的 36 图 12 浏览器场景：源重建与截图 [Action #42347332430](https://github.com/kobolibra/financials/actions/runs/42347332430) PASS。对应精确 HTML SHA 存于 research/rebuild-v10/build-manifest.json 和 research/quality/active-pr35.json 的 latest_source_sha_bound_candidate；真正图片的人工式 AI 观察笔记及 PNG SHA 在 [真实 CJK 图证审阅](PR35_ACTUAL_CJK_FIGURE_REVIEW_2026-11-07.md)，不冒充独立视觉编辑签字。候选零记忆 SHA 与财经审计门 [Action #42347522657](https://github.com/kobolibra/financials/actions/runs/42347522657) PASS；真实 Cloudflare HTTPS 预览 [Action #42347520600](https://github.com/kobolibra/financials/actions/runs/42347520600) **已经以此次四篇实际 HTML SHA PASS**：11 家完整路由逐字节、16 个 Chromium/WebKit 视口、108 次所见即所得 SVG 导出、来源表与 PDF 页码。下载图与截图证据 Artifact #13564585854。此项只证明候选 preview，**main 仍未合并/正式新站点未上线**；下一次任何 HTML 变化都必须重新在线验证。

## 工作状态——必须区分三条线

- 唯一仓库：kobolibra/financials。工作 PR：https://github.com/kobolibra/financials/pull/35；分支 quality/aei-sankey-source-contract-v1；此交接创建时 **PR 未合并**。最初查验 main 为 9b70e1a4dad2c57cbbd26810dbd7ed9d3e5ddea9，仅为带日期历史快照，须重新获取。
- 生产： https://financials-in-visuals.pages.dev/ 对应 main，公司总数与路由从 site/research_catalog.json 读取。
- 候选： https://quality-aei-sankey-source-co.financials-in-visuals.pages.dev 对应 PR 分支；只有实际新 HTML SHA 等于候选源文件时，才能称预览该版本已验证。
- 四家真实候选报告：688111 金山办公 9 图（Type A）；600519 贵州茅台 9 图（Type C）；000333 美的集团 10 图（Type B）；600036 招商银行 8 图（BANK）。不改动另外七家生产报告，不创设第二目录。
- 唯一完整 Skill：skills/ashare-financial-storytelling/SKILL.md，版本 v8.8.0-rc1。GitHub 文件不是已装入 ChatGPT 全局的 Skill；Codex 使用 .agents/skills 包装器。当前没有真实独立财经和视觉第二审稿签字。

## 每个新 Agent 必读，按顺序，绝不以聊天记忆取代

1. START_HERE.md → project-status.json → PROJECT_STATE.md → AGENTS.md，取得最新 main 和 PR HEAD。
2. 完整 skills/ashare-financial-storytelling/SKILL.md + research 01–05 五册全文（AEI 方法、A股机构研究、视觉编辑、法证分析、跨行业泛化）。
3. docs/HANDOFF_PROTOCOL.md、docs/REPORT_RELEASE_CHECKLIST.md、docs/SKILL_EVOLUTION_PROTOCOL.md、skills/ashare-financial-storytelling/quality-regressions.json。
4. 本 PR 的 machine status research/quality/active-pr35.json、research/quality/pr35-hero-figure-briefs.json（四家财务主图的真实来源事实、最强反证与未证问题）、docs/AEI_RESEARCH_EDITORIAL_SCORECARD.md、V10 publisher.py、native_mobile.py、source type audit、QA 浏览器及源账本。
5. research/rebuild-v10/build-manifest.json、strict-semantic-audit.json、real-browser-qa/result.json 和四个新 public/research/2026-h1-v10/*.html 的 **本次 SHA**；绝不能复用先前版本绿灯。
6. PR 实际 Actions 和在线 Cloudflare 字节。2026-11-07 历史通过 #42344600791 原始 PDF 重建 / #42344715944 云预览全站路由和 108 真实 SVG 下载属于**旧候选 SHA**；不证明新图已被验收。

## 本轮真正修的图形问题

- **WPS 桑基**：过去桌面输出复用手机 330 单位图，信息布局是四个平行条。现在新 desktop 1040 独立三阶段：四业务收入 → 各自披露的成本及毛利 → 集团成本、毛利合计节点；原始元统一比例，四业务直接毛利率；移动版 330 图独立。必须运行最新 CJK 1440/768/390 和逐图 SVG 检查，实际判定标签/路径错位，不能继承旧截图。
- **茅台负毛利**：其他业务负 12,446,319.42 元，较主业巨额毛利在统一尺度下只有约 0.04 SVG 单位。桌面版本已经改为真正独立 1040 单位的编辑排版、手机为独立 330 单位；保留真实负值宽，不伪造最小条宽；新增明确另一比例尺的收入 vs 成本局部放大区，并显示负毛利与负毛利率。内部 Type C 错误识别理由只用 SVG data 属性，不在读者画面裸露机器代号。对这两条新代码已有源元单元对抗测试，但最新真正发布的 HTML 需要重编并验收。
- **美的、招商**：分别保留集团毛利仅 B 类型和银行专用净利息到营业利润类型，不允许虚构分部成本或重复扣息。
- **研究深度债**：金山办公续费及调整利润税后、茅台分实体现金与渠道价盘、美的套保 OCI 税后归属、招商银行日均收益率/迁徙资本真实驱动、多期/同行/估值全证据尚未完成。记录 NOT_CHECKED，不猜。
- 不清偿的外部源问题仍存在：翱捷 688220 p137 应收集中度报告 90.50% 与推算 89.17% 分母冲突、p179 0.01 元差异，未获得第二次独立来源结论。

## 真正的自动化交接门

scripts/check_pr35_quality_handoff.py 必须从实际候选 public HTML 字节重算 SHA，同 research/rebuild-v10/build-manifest.json、strict-semantic-audit.json 和 12 个真实三视口 Chromium 来源回执逐字节同源；检查 WPS 独立 1040 图、茅台真实极小负值放大、Skill / START_HERE / PROJECT_STATE / AGENTS / machine manifest 一致。任何旧截图、新网页、虚假人类认证都要 FAIL。

按顺序执行原项目 python scripts/check_handoff.py；然后 python scripts/check_pr35_quality_handoff.py；python -m unittest discover -s scripts -p test_check_pr35_quality_handoff.py -v；python -m unittest discover -s research/rebuild-v10 -p test_editorial_chart_quality.py -v；python scripts/audit_v10_flow_contract.py --strict，及现有跨行业测试。

候选重编：按 .github/workflows/verify-v10-native-rebuild.yml 真实下载原始四份 PDF 并 SHA 验证、verify.py、publisher.py、qa_native_browser.py、把四份新 HTML + exact SHA 回执一起提交，重新跑云端 Chromium/WebKit 和在线 SVG 出口。没有新原报告 PDF 字节就不能宣称源验证通过。

## 放行边界与立即下一动作

1. 立刻查看 PR HEAD 与各 Actions 是否真正对本轮新图返回成功；如果缺新 SHA 生成与浏览器回执，就执行真实重新构建而不是沿用老绿灯。
2. 让财经/视觉人员对最新 1440/768/390 每张主图做五秒审查，图优于表吗、核心驱动看得见吗、误解从何而来；保留明确 NOT_CHECKED 直到真审稿。
3. 不在未获合并授权的情况下改动 main 或生产。合并后独立执行 Cloudflare 正式 11 路由全 HTML SHA 和全部下载测试，之前的预览成功不等于生产 PASS。
4. 在任何交接时实际更新本文件、project-status.json、PROJECT_STATE.md 和机器回执，错误回到源代码/元金额/新 SVG 修复而不是只追加备忘；把当次 PR HEAD/CI 的真值与历史记录分开。

**质量等级：L0 已知本期证据在实测范围内；L1 新报告期/新公司复现、L2 20–30 个真正未见样本、L3 独立财经/视觉盲评均 NOT_ESTABLISHED。拒绝无证据的“已经顶级稳定”结论。**
