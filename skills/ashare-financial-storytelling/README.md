# Financial Storytelling · A 股财报视觉研究

**演示对象：** 天孚通信 300394.SZ，2026 年半年度报告，185 页。

**核心交付：** [独立预览 HTML](../../public/preview/300394/2026-H1/index.html)。源数据与自动生成脚本保留在 `skills/ashare-financial-storytelling/` 目录，生产站首页和既有报告未改动。

## 当前实际能力

- 已实现：根据经过原文检查的证据账本，生成自包含 HTML；6 条真实按金额比例缩放的 Sankey 流带；带符号利润桥；从报告第 148 页精确计算的现金流瀑布；资产/资金来源结构；电脑和移动端浏览器、悬停和 SVG 导出检查。
- 已完成：算术账本 10 项 PASS、回归测试 10 项通过（在工作环境中运行；不代表部署后线上测试）。生成器基于该具体公司的已核验账本，不是任意 PDF 的自动数据抽取器。
- **尚未完成：** 自动读取任意 A 股 PDF、银行/保险行业自动识别与渲染、跨公司批量回归及 Cloudflare 生产部署的独立实测。不可据此声称无人工干预的通用 Skill 已正式投产。

## 从仓库复现此案例

```
python skills/ashare-financial-storytelling/scripts/render_tianfu_2026h1.py
```

读取 `skills/ashare-financial-storytelling/examples/tianfu-2026h1-ledger.json`，输出 `skills/ashare-financial-storytelling/outputs/tianfu-story-v3.html` 及 `checks.json`。仅需 Python 标准库。无需 Node.js、D3 CDN 或 API Token。

注：生成器目前是经过天孚通信案例验证的 **单公司模板**。`SKILL.md` 是向更多公司扩展时必须执行的研究、会计、设计和发布质量规范，不能用它替代 PDF 解析与人工证据复核。

## 授权与安全

源数据为报告公开数据及人工计算结果。未复制 App Economy Insights 的图表作品；仅借鉴其公开的商业模式优先、三表交叉、现金转换与简洁图形叙事方法。

本站推送至 Cloudflare Pages 后，依赖 GitHub `main` 自动部署，不需要在聊天里分享账户密码或 API Token。**新修改应先提交 preview 路径，不得自动覆盖生产路径。**