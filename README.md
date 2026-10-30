# financials

A 股上市公司财务报告可视化静态网站。所有财报作品为独立 HTML，网站部署目录为 `public/`。

## Cloudflare Pages 首次部署

1. Cloudflare Dashboard → Workers & Pages → Create application → Pages → Connect to Git。
2. 选择 GitHub 仓库 `kobolibra/financials`，生产分支 `main`。
3. Framework preset: `None`；Build command：留空（如必须填写，使用 `exit 0`）；Build output directory：`public`；Root directory 保持仓库根目录。
4. 点击 Save and Deploy。以 Cloudflare 实际生成的 `.pages.dev` 地址为准。

首页：`public/index.html`。
天孚通信 2026 H1：`public/300394/2026-H1/index.html`，部署后相对地址为 `/300394/2026-H1/`。

## 后续报告发布

将通过核验的单文件 HTML 上传到 `public/{证券代码}/{YYYY}-{H1|FY|Q1|Q3}/index.html`，更新首页列表并提交至 `main`；首次绑定 Cloudflare Pages GitHub 集成后可自动部署。禁止上传未经财务核验或尚未通过浏览器测试的作品。

不需要 GitHub Actions、Cloudflare API Token 或对其他现有项目进行任何修改。
