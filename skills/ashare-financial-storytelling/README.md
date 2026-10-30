# A-Share Financial Storytelling · Research Desk v4

**使用原则：先做可反驳的财务与商业研究，再设计图表。** 该 Skill 借鉴 App Economy Insights 公开披露的研究方法和可视化解释原则，但不复制其品牌与设计，不隶属于该网站。最终交付格式只需 **自包含、离线 HTML**；原财报 PDF 是输入而非输出。

## 安装与目录
- [SKILL.md](SKILL.md) — 完整执行规范、输入/输出、分级验收。
- [research-method.md](references/research-method.md) — 价值链、竞争壁垒、驱动拆解、争议假设与研究提纲。
- [ashare-accounting.md](references/ashare-accounting.md) — 中国会计准则、A 股年报附注、会计检验与法证审查。
- [sector-playbooks.md](references/sector-playbooks.md) — 不同行业的经济模型与适用指标；银行和保险不采用工业利润流强行建模。
- [visual-editorial.md](references/visual-editorial.md) — 原创出版设计、真正按量缩放的图形、交互和审美验收。
- [quality-gates.md](references/quality-gates.md) — 研究、财务、图形、浏览器、部署六类独立门槛。
- [tianfu-research-case.md](references/tianfu-research-case.md) — 185 页真实半年报的深度附注诊断和反面假设。

## 交付现状（准确说明）
- **v4 Skill**：完整研究与设计/审稿规范已入库。
- **天孚 2026H1 v3 正式版**：生产路径为 \`public/300394/2026-H1/index.html\`，原有 6 条金额比例流带等通过之前单公司测试。
- **天孚 2026H1 v4 深度研究预览**：\`public/preview/300394/2026-H1-research-v4/index.html\`，新增毛利润变化、库存原材料、前五名应收集中、研发/资本效率、正反假设与后续验证问题。**尚未覆盖生产网页**；GitHub 内容提交不等于公网渲染验收。
- 原有 \`scripts/render_tianfu_2026h1.py\` 仍是 **单公司生成器**；其产物是旧版 v3 正式案例，不能将其称作无人工干预、适用于任意 A 股 PDF 的通用自动分析程序。v4 新研究预览包含经人工审读原报告注释后的编辑扩充；通用生成工具与多公司自动化尚待工程化。

## 使用方式
把公司半年报/年报 PDF 交给使用此 Skill 的 Agent，执行：

> 使用 financials 仓库下 ashare-financial-storytelling Skill v4 分析这份 A 股财报。先完成公司商业模式与价值链研究、全三表与重要附注复核、精确会计校验、营运资本与盈利质量分析、管理层解释与事实的证据分级；提出核心投资研究假设与最强反面解释；按行业选择信息量最高的原创图表。输出一个响应式、离线、自包含 HTML 深度财务研究；提供页码、计算、未知项、观察指标和浏览器验收。不要生成 PDF，不要编造股价/估值/行业数据，不要修改生产站点，先上传 preview。

## 可执行的会计校验与图表选择（在仓库根目录运行）

~~~bash
python skills/ashare-financial-storytelling/scripts/audit.py \
  skills/ashare-financial-storytelling/examples/tianfu-2026h1-ledger.json \
  --out /tmp/tianfu-financial-qa.json

python skills/ashare-financial-storytelling/scripts/select_story.py \
  skills/ashare-financial-storytelling/examples/tianfu-2026h1-ledger.json \
  --out /tmp/tianfu-chart-plan.json

python -m unittest discover \
  -s skills/ashare-financial-storytelling/tests -v
~~~

以上仅验证源账本、会计勾稽和图表适用性，不是自动解析任意 PDF。新增的 \`examples/tianfu-2026h1-research-addendum.json\` 含客户应收、预付款集中、原材料库存与外汇等 29 项来源字段；\`outputs/tianfu-2026h1-v4-research-qa.json\` 为本轮附注/静态 HTML 复核记录。当前 v4 预览的独立浏览器测试及 Cloudflare 公网 HTTP 验收仍未完成，不能把本地 / GitHub 校验结果等同于线上质量验收。

## 下一阶段工程优先级
1. 从任意 PDF 自动建立页码/版面核实的 typed ledger，含人工核查队列；
2. 各行业模板与 A 股季度/半年度/年度一致性测试；
3. 自动计算 CFO 间接调整、收入/成本/分部报表残差和跨报告利润桥；
4. 可审计的 Chart Spec → SVG/HTML renderer（真实流带、正确负值语义、移动端可读性）；
5. 自动浏览器验收、截图对照、HTTP 公网验收；
6. 多报告跨公司回归案例和维护日志。

**重要：** source-based case study != 金融分析系统已经全行业通用。不要用没有证明的“顶级”“自动”“全通过”替代有证据的交付。
