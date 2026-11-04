# Financials in Visuals — ACTIVE PROJECT STATE

**当前真实状态：2026-11-04。GitHub `main` 实际已包含 11 家公司，同一个唯一首页；中国人寿（601628）已通过真实 Cloudflare 线上报告与目录导航。现行 Skill `v8.6.0-rc1`。下一次新对话必须重新确认 `main` HEAD、现行 GitHub Actions 和官方原 PDF，而非把这里的 SHA 当永恒最新。**

> **一套统一目录**：<https://financials-in-visuals.pages.dev/>；第十一家公司中国人寿独立全文：<https://financials-in-visuals.pages.dev/601628>。原目录卡 href `/601628.html` 被 Cloudflare Pages 规范化为 `/601628`，是真正独立的 HTML 页面，不是首页回跳，也不是 iframe。其余十家公司的独立报告未被改动。研究仍为**源限制预览**，不等于已完成独立第二人类审稿。

## 最新完整生产证据：11 家／中国人寿保险新会计模型／实际 Cloudflare PASS

- **代码与真实上线**：经实际重新查 GitHub，在本轮交接修订之前 `main` 为 `d11638f0c76ff8aef2beb163a1028f176123bbdc`（中国人寿实际源码与修复后的最终 SVG 版本）。真实公网页面+唯一首页双全字节 SHA、真实 1440/768/390 Chromium 点击和返回、全部 11 条公司路径 / 原始来源表 / 10 个有效 SVG 的线上验收运行 [#41771178361](https://github.com/kobolibra/financials/actions/runs/41771178361) **PASS**。测试输出逐幅真实浏览器公司页 `https://financials-in-visuals.pages.dev/601628`，11家公司从首页点击并能返回 `/#companies`；**公司页 SHA-256 `051a8ecb56cb200f4c411bb53ad672096cfb299e297f149fd58aad334cbfb763`，首页 SHA-256 `f625453172a83b7db38d0c5a67ddbecd84fbf078bc9f78c2e20c45b00b23ab41`**。当前网页此时真实等于已发布主分支字节，而非仅提供 Cloudflare provider 成功通知。
- **其他同源 `main` PASS**：保险原始 PDF/专业财务/十张原创 SVG [#41771178355](https://github.com/kobolibra/financials/actions/runs/41771178355)，旧十公司完整统一目录真实浏览 [#41771178360](https://github.com/kobolibra/financials/actions/runs/41771178360)，发布路由 [#41771178350](https://github.com/kobolibra/financials/actions/runs/41771178350)，跨会话交接 Skill [#41771178406](https://github.com/kobolibra/financials/actions/runs/41771178406)，均在同一源 `d11638f` **PASS**。新的 PR/工具改动不凭旧绿色称为已验，须看本次提交新增的 CI。
- **官方原始 PDF 的真实物理证据**：中国人寿 `601628 2026H1` 真完整 CNINFO PDF：`https://static.cninfo.com.cn/finalpage/2026-08-28/1225516873.PDF`；原始文件 4,867,339 字节、104 物理页、SHA `b094bf337309e30564dda86ff4b3c4d66aeeb37ce0357a3568e246569f0e2943`，归档原件 `research/issuers/601628/source/601628_2026H1_complete_original.pdf`，[#41765739795](https://github.com/kobolibra/financials/actions/runs/41765739795) 下载证明。**133 条**带页码、期间、单位和合并范围的源事实、33 项被锁存并重新计算的源物理页 x/y 行列、**18 条**真实原始会计/直接 CFO/偿付资本及安永中期有限保证复核、10 组原创源证 SVG 与恶意财务变异测试。研究底稿/源码 `research/issuers/601628/`，正式独立文件 `public/601628.html`。原始合并资产负债表 p43–44、合并利润表 p47–48、直接法经营现金 p53–54、保险合同负债 p85、CSM 摊销 p87、安永华明中期审阅报告 p42、监管偿付能力 p21/p66。
- **行业源概念禁止混假**：总保费**536634**、法定保险服务收入**112525**、实际收取保险合同保费现金**626732**（人民币百万元）绝不串成“销售→盈利”桑基；只对原件 p10 四项互斥旧保费分组→新单/续期→总保费生成真正几何守恒的原始 SVG 数带。承保服务净结果 **41177**、本期投资收益 **112902**、公允价值变动收益 **135835** 与承保财务损益 **−188067** 联动，完整 signed P&L 最终归母净利润 **134489**；CFO 用原件实际**直接法**而非编造净利润→CFO 间接表。CSM期末**813253** 是保险服务未赚负债时点存量，本期摊销 **35155** 不等于存量；管理层 NBV **38167** 又是特定价值评估口径。监管核心/实际/最低资本和覆盖率来自 p21，而非合并所有者权益。
- **真实失败与纠偏已归入 Skill**：先纠正p44保险合同负债误抓附注p85、保费真桑基两阶段对金额重复误验，随后补安永**有限保证审阅而非审计意见**、监管资本的独立财务范围和零分母，最后线上真浏览器纠正 URL 后发现最终桑基汇总节点 `fill=money-sink` 的无效 SVG 属性并**回修原生成器**；新 1440/768/390 浏览器 QA 检查每个 rect 的填充、最终节点真实金额与高度，PR [#16](https://github.com/kobolibra/financials/pull/16) + 实际 `main` LIVE PASS。又发现线上 PASS 日志里的 `actual_dedicated_article_final_url` 在返回首页后才获取，虽然实际浏览的文章是 `/601628`，但证据字段错误；**本交接修订正在补通用 URL 分离取证模块 + hostile tests + 六张线上真截图 SHA**。不将这项新修订声称为已验，须跑新 `main` Actions。
- **质量门槛，不能混同**：原始PDF/部分关键原始附注与33行列/18项准确会计守恒/10张原创图/真实Sankey的来源及最终节点/本地3视口/离线一致重建/十一家公司独立路径/生产双全字节 SHA/真实三屏 Cloudflare 导航 **PASS**（对精确 d11638f 的上述 Actions）。**NOT_CHECKED**：104页重大附注及潜在精算敏感性完整独立审阅、源PDF与另一个上交所副本逐字节相等、8–12季度同业市场估值和利率/精算模型、独立第二名人类财报分析师及独立专业视觉审稿；保持 `source_limited_preview`，不得写 `verified_research`。早期 688220 的 90.50% 与自推 89.17% AR 客户集中度问题也仍是独立 FAIL，不能由601628通过覆盖。
- **现行跨会话入口**：先读 `START_HERE.md`、`project-status.json`、本文件；逐个读完整 `skills/ashare-financial-storytelling/SKILL.md`、`research/01–05`、`docs/REPORT_RELEASE_CHECKLIST.md`、`docs/HANDOFF_PROTOCOL.md`、`skills/ashare-financial-storytelling/quality-regressions.json`；从 GitHub 查询真实 `main` HEAD 与确切 commit 的五个 Actions；财务源、HTML、真截图、生产 HTTP 和提交SHA互不替代。本次新增通用模块 `research/shared/live_route_evidence.py` 及 `scripts/test_live_route_evidence.py`，live 证明代码 `research/issuers/601628/qa_cloudflare_live.py`，发布合同 `research/issuers/601628/release-gates.json`。再新增公司应下载本公司的**完整原始PDF字节**并独立运行其行业专有财务和图形门槛；本轮601628是单公司寿险 L1，不能自动宣称 L2跨保险或L3全行业泛化已证实。

---


## 历史实施记录（已被上方真实 MAIN 生产结果覆盖）· 2026-11-04 中国人寿零记忆实测和 PR #14/#15/#16

- **严格身份和范围**：本次实际以 GitHub `main` 初始 HEAD `07ea54b5d6e917623a87f6bad83f817d277c6e2d` 开始；真实 `main` 在正式合并前仍是原有 **10 家**；候选分支 `work/insurance-601628-original-2026h1-skill-stress` 提交第 **11** 家中国人寿（保险新经济模型）的唯一独立 `/601628.html` 和原有主页 `public/index.html` 的 **11家公司统一目录**。绝不改变旧十家公司任一家 HTML，也不另开四家公司首页。最新 Skill **v8.6.0-rc1**；新会话必须读本文件、project-status、实际 main HEAD、完整五研究手册、发布清单。
- **官方原件是真实字节，不是网络文字摘要**：巨潮 `https://static.cninfo.com.cn/finalpage/2026-08-28/1225516873.PDF`；GitHub 真实 Runner 下载、逐字节 SHA 与 `pymupdf` 封面/页数验证：[原件归档动作 #41765739795](https://github.com/kobolibra/financials/actions/runs/41765739795) **PASS**；文件 `research/issuers/601628/source/601628_2026H1_complete_original.pdf`，**4,867,339 bytes、104 物理页、SHA256 `b094bf337309e30564dda86ff4b3c4d66aeeb37ce0357a3568e246569f0e2943`**。逐页独立正文/主题索引在 `research/issuers/601628/extracted/`；`verify_source.py` 用真实原始 PDF 校验 **33 项选定 x/y 行锚+当前列来源格**；原报告合并 BS p43–44、合并 P&L p47–48、直接法现金流 p53–54、保险合同负债与 CSM p85、CSM 服务释放 p87。物理 p45–46、p49–50 为**母公司**，不能误当合并。SSE 单独 PDF URL 返回非 PDF，SSE/CNINFO 字节同一性 **NOT_CHECKED**。
- **完整的会计研究优先于画图**：`source-ledger.json` 原始报告 **133 带物理页/会计期间/原报表百万元换算元的事实**，`story.json` 研究论点与反证，`figure-briefs.json` **10 张原创图逐张设计简报**，`publish.py` 18 个 signed 财务恒等式 + `test_accounting.py` 对 wrong year、负数、漏保险财务、CSM 存量当收益、保费误等于服务收入、现金直接法被强换间接法、错母公司等有具体恶意变异测试。
- **行业会计最重要的三个互不等价**：p10旧保险合同统计的总保费 **536,634 百万元**（`101294+17696+61049+356595`）；p47新保险准则确认的保险服务收入 **112,525 百万元**；p53直接现金表实际签发保险合同收现 **626,732 百万元**。三者**禁止互联成盈利流**。管理层 NBV **38,167** 亦不是当前 IFRS/CAS 法定收入。
- **十张真正原创财务图不是通用 dashboard**：仅对同一统计口径四种互斥保费从来源→新单/续期→总保费做真实几何金额权重守恒 SVG 桑基，绝不连到新保险服务收入；五组成分保险服务确认、带符号保险服务结果、完整法定利润桥、两期利润增量桥、实际直接法 CFO 七项负数支出桥、现金开闭桥、CSM+精算负债同日存量构成、两时点合并资产融资、各不混基准 KPI。公允价值变动收益 **135,835**、投资收益 **112,902** 与承保财务损益 **−188,067**、OCI **−48,038**（均 RMB 百万元）必须并读。保费仅 +2.2%，服务收入 +5.3%，归母利润 +228.6%，同期 CFO **282,879 百万元**却同比 −5.8%；这种矛盾是研究主线，不是利润预测外推。
- **实跑失败→修正**：首轮财报坐标锁错源页（p85的保险合同负债附注与合并BS p44 行锚混淆）导致 Actions #41767214612 FAIL，修真实 ledger 后选定 33 项 x/y PASS；首轮桑基验证器错误将原始来源强制双重数带，Actions #41767325656 FAIL，修为 4一级原值 + 2聚合后出口实几何守恒，Actions [#41767495751](https://github.com/kobolibra/financials/actions/runs/41767495751) **PASS**，10 图、10 表、真实 CJK Chromium 1440/768/390、每图截图、实际 SVG 导出、2次字节一致重建。10 项真实失败与未覆盖披露锁进 `skills/ashare-financial-storytelling/quality-regressions.json`（INS-021..INS-030、VIS-027、PUB-028）并在 Skill v8.6.0 规定**L1 单一保险发行人实测 ≠ 保险行业 L2 或通用 L3**。
- **当前状态门槛严格拆开**：原件/选定行列/合并三表+直接现金/10图会计语义/真桑基几何/三视口本地浏览器/同源码重建 **PASS（对应 Actions 具体提交）**；全104页重大附注的专业独立穷尽、历史8–12季同行和估值、独立第二名人类财务及视觉审稿、SSE第二源原件字节相等仍 **NOT_CHECKED**。**在生产真正新路由主站导航完成之前，`CLOUDFLARE_LIVE=NOT_CHECKED`，分支截图不会被冒充为线上发布；绝不写`verified_research`。**每张图原始文件/源事实/研究反证与释放门槛见 `research/issuers/601628/release-gates.json`。
- **在新会话的下一步**：看候选分支最新 GitHub Actions、完成 `public/index.html` 同一个主页重建；原页10家公司全部 `git diff origin/main -- public/*.html`（排除本次新增 601628）应无变更；运行 `python scripts/check_release_contract.py`、`python scripts/check_handoff.py`、所有 issuer hostile/unified portal 测试、实际生产 Cloudflare 11 路由 Chromium 链接和指纹，随后真实 PR 合并 main 再更新本段。若任何一步失败应修原始源头和回归，而不是降级检查。无需让用户重新说明公司、技能和站点。

- **新增机构级源事实修正（重要）**：完整原件 **p42** 是安永华明2026-08-27有限保证审阅报告（审阅准则第2101号，非完整审计、无审计意见）；原摘要仅标“未经审计”会漏掉真实会计保证层级，`issuer.audit`/全文出版现已明确限度。原件 **p21/p66** 监管资本 **核心1,058,166、实际1,334,688、最低674,846** 百万元，核心与综合充足率 **156.80%/197.78%**，年末历史 **128.77%/174.01%**；监管资本与股东CAS权益并非同一会计量。已添加 **6 新事实、4项当前/比较期两位比例实际校验**和4个恶意测试（零分母不能以浮点异常冒充专业门槛），注册 INS-029/INS-030。p17总投资收益3,145.04亿元是管理层经营收益口径，亦不等于合并利润表投资收益1,129.02亿元。
- **当前校验最新状态（勿从过去绿色推定新提交）**：添加p42审阅与p21偿付能力后，机器状态显示候选强约束**正在等待新 133-fact、18-identity HTML 实际重新构建**；旧 [#41767901626](https://github.com/kobolibra/financials/actions/runs/41767901626) 绿色仅对应改动前代码。PR [#14](https://github.com/kobolibra/financials/pull/14) 正在跑新校验，未合并之前 `CLOUDFLARE_LIVE=NOT_CHECKED`。上游旧版`published_html_sha256`必须在新网页编译后按**实际字节**更新；新 PUB-028 反例会拦截指纹漂移，旧600900/600276的显式`NOT_CHECKED_PENDING_MAIN_DEPLOY`仍保留，不能假写已验。

## 2026-11-04 · 本次新发行人入库核验（等待明确的新原始披露对象，禁止虚构第十一家公司）

- **读取基线**：在本次会话通过 GitHub 连接读取实际 `main` `7ee99b608fc4d0376de80f89c20539698b051ba2`；完整 `SKILL.md v8.5.0-RC1`、研究手册 01–05、发布/交接协议、十公司目录、既有 600900/600276 原始账本与研究故事及最新 Actions 均已读取。项目当前是**十家公司**，不是历史七/八家；不要把旧 `AGENTS.md` 中八家公司快照当作现行规模。
- **本次第十一家公司来源门槛**：本会话未收到任何可识别为**新发行人**的证券代码、公司名、原始 PDF 附件或官方完整 PDF URL；会话文件列表为空，检查了现有 Library `/Financials-in-Visuals/`，仅能定位历史已覆盖公司的归档。**ISSUER_IDENTITY / NEW_ORIGINAL_PDF_BYTES / PERIOD_AND_REVISIONS / ORIGINAL_PAGE_ROW_COLUMN / NEW_ISSUER_ACCOUNTING / NEW_ISSUER_VISUAL / NEW_ISSUER_BROWSER / NEW_ISSUER_LIVE = NOT_CHECKED**。不拿历史 601628 作为用户这次指定的新公司，不生成猜测的数字或空公司卡。
- **本次已做的可迁移源修复**：`AGENTS.md` 中硬编码的八家公司描述与当前十公司目录矛盾；已改为从 `project-status.json` 和 `site/research_catalog.json` 动态读取，并在 `scripts/check_handoff.py` 增设 `AGENT_STALE_HARDCODED_ISSUER_COUNT` 检测及 `scripts/test_check_handoff.py` 的恶意回归。该修复仅覆盖交接误导，**不是**第十一家机构财报报告。
- **本次工程验证**：[PR #13](https://github.com/kobolibra/financials/pull/13) 在源提交 `797e27f75de1e4b4b4774dc85e1a31832ce84760` 上运行新的交接反例及源文件约束 [41763814988](https://github.com/kobolibra/financials/actions/runs/41763814988) **PASS**；旧两家水电/医药完整原始PDF、会计和真实三尺寸图形回归 [41763815011](https://github.com/kobolibra/financials/actions/runs/41763815011) **PASS**。这两个运行只证明此代码提交的旧公司和交接测试，不是新公司研究或本会话真人视觉审稿。
- **准确的既有 CI 时点**：`main` HEAD `7ee99b6` 交接 Actions [41738267454](https://github.com/kobolibra/financials/actions/runs/41738267454) PASS；财务/原 PDF/本地三屏 [41737976198](https://github.com/kobolibra/financials/actions/runs/41737976198) 对应 `0ed43ee45ad2aa52e44b11c6b4d371cc4bec5792` PASS；Cloudflare 公网 Chromium [41738152741](https://github.com/kobolibra/financials/actions/runs/41738152741) 对应 `93709bfcd5fe9d2008d12f62b14304c23a26700d` PASS。以上均为旧十公司确切范围；此会话独立 Cloudflare 直接 HTTP/本人新截图：**NOT_CHECKED**。
- **后续真实入库前提**：唯一待取得的对象是本次发行人的完整原始 PDF 或可以直接取到 PDF 字节的官方报告 URL，连同发行人标识；取得后重新核对原始 SHA/报告期/行列，研究全三表与重大附注，创建 `research/issuers/<code>/` 证据及 `public/<code>.html`，只扩容统一目录，再独立执行新公司的会计、视觉、1440/768/390、离线重建和真实 Cloudflare 检查。第二名真实独立人类审稿维持 NOT_CHECKED。

## 2026-11-04 · CURRENT · 两个真实新行业研究 + 十家公司唯一正式网站

**已完成生产合并/真实在线验收**：[PR #12](https://github.com/kobolibra/financials/pull/12) merge `7704ecc6c6a0f0470f7dd5f2c6fe71d5527de511`；只新增 `public/600900.html`、`public/600276.html` 两份各8图/8源证据表的**完整独立离线 HTML**，原八家公司HTML未改，唯一 `site/research_catalog.json`→`public/index.html` 变为**十家公司**。<https://financials-in-visuals.pages.dev/600900.html>（水电长江电力）、<https://financials-in-visuals.pages.dev/600276.html>（创新药恒瑞医药）；唯一入口 <https://financials-in-visuals.pages.dev/>。

**官方披露完整 PDF 字节、源码及样本**：600900 2026H1 完整214页，1,296,750 bytes，SHA256 `738de3b36a31646f344cefaf90b4f149d653c3f68e89f4f8d14bdf02fc9c65a2`；600276 2026H1 完整182页，4,594,202 bytes，SHA256 `ff6910663a9726acb889aa061a8bab1433f58890d81ebea013b8c637a097a7aa`，真实源获取 [41671538396](https://github.com/kobolibra/financials/actions/runs/41671538396) PASS，全物理页文本索引 [41735314032](https://github.com/kobolibra/financials/actions/runs/41735314032) PASS，原始 PDF/重要行列x-y/账本/图表简报/行业分析均在 `research/issuers/{600900,600276}/`。每家公司都有独立三态 `release-gates.json`；SHA 校验并不代替所有重大附注或第二名专业人类审稿。

**main 实际交付 QA（同源 SHA `7704ecc6c6a0f0470f7dd5f2c6fe71d5527de511`）**：财报原 PDF、选定20+26重大源单元格的物理行/列、签名完整三表及间接 CFO、现金等价物闭合、逐源金额加权桑基/有符号瀑布/两时点BS、16幅原生财务图和16份表、CJK浏览器1440/768/390、真 SVG ribbon 几何、独立HTML双次位对位生成 **PASS** [41736999153](https://github.com/kobolibra/financials/actions/runs/41736999153)。真实公开Cloudflare**10公司×3视口30实际URL检查**，两新页原PDF SHA、来源节点与成本/毛利流带、手机及主页回跳、原七页回归 **PASS** [41736999189](https://github.com/kobolibra/financials/actions/runs/41736999189)。老页面/站点规范 [41736999101](https://github.com/kobolibra/financials/actions/runs/41736999101) PASS；原 v10 桑基 [41736999269](https://github.com/kobolibra/financials/actions/runs/41736999269) PASS；零记忆Skill/handoff [41736999465](https://github.com/kobolibra/financials/actions/runs/41736999465) PASS。

**v8.5.0-RC1 原创行业研究/反馈迁移**：长江发电量1327.44亿千瓦时**不是**售电量/收入均价分母，2025H1比较期受2025年10月同控合并影响而追溯调整；投资收益、融资、利息与分红不可当售电现金。恒瑞创新药销售88.09亿元是商品收入**子集**，许可收入独立，7月才生效的BMS不是本期确认，p153非现金银行承兑汇票背书共19.94亿元，其中购建资产7.03亿元不能混入现金CapEx/FCF；研发费用与开发支出资产存量不同。2026版源会计/可视化红队反例存 `research/shared/test_two_sector_accounting.py`、`quality-regressions.json`（共20登记案例）。跨行业实测只足以证明两个L1原始公司样本，**不是**各行业两家L2或全行业自动研究认证。

**仍未完成/不能冒充**：600900/600276各自全部214/182页重大附注的完整独立语义审稿、外部8–12Q同业估值、第二名真正独立人类财务/视觉研究员、交易所SSE与CNINFO原始 PDF 逐字节同一性全部 **NOT_CHECKED**。旧688220 p137/p179原始附注差异仍在以前章节独立标明。发布的是来源限定研究预览，不是独立人类审稿签章的完整机构投资研究。

**下次聊天必须先取得最新实际 main SHA**；以下原始代码路径/执行命令是可重建起点而非仅靠记忆：`python scripts/check_release_contract.py`; `python scripts/check_handoff.py`; `python research/shared/verify_two_sector_cells.py --code 600900` 和 `--code 600276`; `python -m unittest research/shared/test_two_sector_accounting.py -v`; `python research/shared/build_two_sector.py --code <code> --out public/<code>.html`; `python research/shared/qa_two_sector_browser.py --code <code>`; `python site/portal_builder.py --out /tmp/financials-ten-issuer`。实际重跑需PyMuPDF、Playwright/CJK及完整原PDF归档。**未来每家继续按照同样标准验收且有新反馈即新增真实反例，不会自动获得独立研究认证。**

## 2026-11-03 · HISTORICAL CANDIDATE (NOW RELEASED): ZERO-MEMORY GENERICITY TEST: v8.5.0-RC1 · 水电+创新药两家真实 PDF / 十公司统一目录候选

**起始与隔离边界：** 按新聊天场景重新读取 2026-11-03 实际 `main` `2889046506890397082ec3896a057bed0b31d478`、START_HERE/PROJECT_STATE/project-status、唯一完整 Skill 和研究手册 01–05、质量检查和交接。独立分支 `work/two-sector-600900-600276-real-2026h1`，**不是另起四公司网站**；原八公司报告文件未改，本次新增 `public/600900.html`、`public/600276.html`，**十公司首页仍需候选自动生成、PR/main 合并和 Cloudflare 真实逐公司验证**，当前不能冒充线上完成。

- **实际完整新 PDF 已直接取得并归档**：长江电力 **600900** 2026H1，官方 CNINFO 原始 PDF **1,296,750 bytes / 214 物理页 / SHA256 `738de3b36a31646f344cefaf90b4f149d653c3f68e89f4f8d14bdf02fc9c65a2`**；恒瑞医药 **600276** 2026H1，官方 CNINFO 原始 PDF **4,594,202 bytes / 182 物理页 / SHA256 `ff6910663a9726acb889aa061a8bab1433f58890d81ebea013b8c637a097a7aa`**。真实 Runner [41671538396](https://github.com/kobolibra/financials/actions/runs/41671538396) **PASS** 完整 PDF 魔数/覆盖公告/发行人封面/年号/页数/真实 byte SHA；第二家不是截图或摘要文本。另一个上交所同一公告原 PDF 字节与 CNINFO 的一一同一性 **NOT_CHECKED**。
- **机构会计实证不是模拟财报**：`research/issuers/600900/source-ledger.json` 中 63 项原始披露或管理层经营指标，`source-critical-cells.json` 有 20 个**源 PDF 物理页和原始(x,y)列/行语义**硬验证；`600276` 75 项原数据/管理指标、26 个相同原页行列强核验。不只有页上字符串命中，还按本期/对比列原 x 坐标与行标验；其余金额也通过真实原 PDF 对应页金额定位，不表示全部 214/182 页重大附注全面独立审阅。
- **核心实际财务勾稽/原创视觉**：[41677614389](https://github.com/kobolibra/financials/actions/runs/41677614389) **PASS**（原 PDF 20+26 个源格；15+17 精确 Decimal 关系，含利润总额/归母+少数/资产=负债+权益/16+17 条 signed CFO/现金等价物变动/互斥收入→成本+毛利的真加权桑基，行业对抗反例；两家公司**各 8 张、共 16 张**原创研究图和各自八份源表，1440/768/390 真实 CJK Chromium 截图、逐条 Bézier/SVG 实际面积验、图形导出及离线 HTML 逐字节干净重建）。需确认最新变更覆盖新附注后的完整运行记录，以最新 GitHub Actions 为准，不能把较早跑次跨 commit 冒称最新版已通过。
- **真正跨行业发现、修源头、入 Skill v8.5**：水电发电量 1,327.44 亿千瓦时 ≠ 净售电量 ≠ 当期会计收入，缺全量上网售电电量不得倒算平均电价；2025 年 10 月同一控制下合并导致 2025H1 **追溯调整比较期**（原 p.7），水资源税本期约 9.00 亿与成本/财务费用/投资收益分别分析。恒瑞创新药销售88.09亿元是药品等商品销售的**子集**；p.145 商品/许可/其他为真正同维度收入分类；BMS 合同于 2026年7月才生效，潜在约152亿美元合同里程碑收入既非 H1 确认，也非确定未来现金；p.153 **承兑汇票背书支付19.94亿元**，其中材料12.91亿、购建长期资产7.03亿是非现金结算，不能混进现金 FCF；受限资金和研发开发支出存量均不同于可用现金及当期研发开支。可运行对抗测试 `research/shared/test_two_sector_accounting.py` 与 `research/shared/verify_two_sector_cells.py`；`quality-regressions.json` 新增 SRC-016/HYD-017/PHA-018/CSH-019/VIS-020。
- **实际失败不删**：首版 `41673697402` 在真实 **390px 手机报告页滚到 429px** **FAIL**，已经从 CSS 布局和正文/卡片 BoundingClientRect 源头改动，并增加“不允许根部隐藏超宽内容而伪通过”的真实 Chromium 核验。PDF 行列测试首次查出 `cash_end` 对应的源账本是**合并现金流量表 p.56**而非 p.161 现金补充资料; 已把源坐标证据实际改回 p.56。后续发现恒瑞 p.153 银行承兑票据材料字样跨行断字，保留物理切行原文而非做错误 OCR。水电 p.7 追溯比较期也在实际 story 的 countercase 中明确展示。
- **明确的研究边界**：审阅过原始报告重大实际财务/经营/许可/现金附注及关键数据，但全物理页/全部材料附注系统独立全文审计、8–12Q 长期同行估值、第二名真正人类财务/设计审稿仍 **NOT_CHECKED**；每家分类为 `SOURCE_LIMITED_PREVIEW` 而非经独立审稿的完成机构研报。二公司 Cloudflare **NOT_CHECKED**，除非真实新 URL 访问 200、连续导航、截图及本次独特源节点通过。
- **后续第三家独立模型**：计划 **601628 中国人寿保险** 2026H1 真实完整原始 PDF，重点测试保险准则保险服务收入 vs 实际保费、合同服务边际 CSM、金融资产负债、投资收益/OCI/新业务价值、偿付能力，不得照搬工业企业收入−COGS/Sankey；第三家公司不是借第一二家图形模板原样复制。

**新一轮验收需要依次**：分支双公司源+视觉 CI 再跑成功 → `site/research_catalog.json` 唯一首页 10 家 + 按同一 `site/portal_builder.py` 生成根页 → `scripts/check_handoff.py`、`scripts/check_release_contract.py` 与对抗测试 → PR/main 实际合并 → GitHub/main Actions → 真 Cloudflare 2 条独立 URL 和全旧网址点击+1440/768/390 → 三态交接。不得以质量合同 PASS 推断实时 Cloudflare 成功。

## 2026-11-03 · CURRENT: Skill v8.4.2-RC1 · 第 N 家独立质量合同与源→出版一致性

**实际已合并的 Skill（三次小步迭代）：** [PR #9](https://github.com/kobolibra/financials/pull/9) v8.4.0 merged `ffb57ac6142546a66233fa01741b54812422f40e`；[PR #10](https://github.com/kobolibra/financials/pull/10) v8.4.1 merged `d0eed02f7c3bb5bdffb3cb7cea6f4620d0e1bc96`；源账本真实内容修复 `f1e2343cb0b4c76d68b2c386218dde7a3d5bd403`；[PR #11](https://github.com/kobolibra/financials/pull/11) v8.4.2 merged `c2c8b15ab67cb91770b0e04818b181d38f567cfa`。**PR #11 真实 CI**：[41668925315](https://github.com/kobolibra/financials/actions/runs/41668925315) 交接/源与 20 个恶意反例 PASS，[41668925267](https://github.com/kobolibra/financials/actions/runs/41668925267) 统一目录本地 QA PASS；**main** [41669011190](https://github.com/kobolibra/financials/actions/runs/41669011190) 交接 PASS。合并后的主分支 **严格 Cloudflare** [41669011093](https://github.com/kobolibra/financials/actions/runs/41669011093) **PASS**（八家公司×三个视口，确认翱捷科技真实来源节点面积/小额分流/零毛利/桌面终点）；[41669011100](https://github.com/kobolibra/financials/actions/runs/41669011100) **PASS**（已有正式网址及导航）；前一源核验 [41667953097](https://github.com/kobolibra/financials/actions/runs/41667953097) **PASS**（29 会计检验、完整 PDF 镜像 SHA、9 图真实渲染、严格逐字节离线重建）。当前 v8.4.2 的测试入口、交接与线上 route 已在真实 GitHub Actions 执行，而不是未来计划；完整重大附注和真人第二研究员仍 **NOT_CHECKED**。

- **已有可复现自动化（不是口头方案）**：`scripts/check_release_contract.py` 在同一八家公司统一目录 `site/research_catalog.json` 上查每家新公司（原七家的历史欠账固定豁免，绝不扩张）的 `research/issuers/<code>/release-gates.json`；实际 PDF 字节、SHA/大小/魔数、Source Ledger 公司/期间/金额单位/物理页、Figure Briefs 事实 ID/来源哈希/原始分析问题、行业会计类型、个人审核与实时 Cloudflare 独立三态。不允许未经登记的新发行人通过；源限制预览不是研究全认证。
- **实际反馈→测试**：`skills/ashare-financial-storytelling/quality-regressions.json` 当前 11 个真实根因/修复/可执行标记（旧错误 p87 期别错列、跨轴加总、负毛利假流、微小来源节点放大、桌面图内隐藏、Cloudflare 滞后、账本哈希陈旧、Figure Briefs 借用事实、银行保险工业会计等），涵盖**单公司证据与跨发行人机制分级**；`scripts/test_check_release_contract.py` 已加入额外两项对原始来源说明／披露数值恶意篡改、而已发布 HTML 仍旧的测试，PR #11 的自动检查实际执行并通过；该 PASS 只证明结构性防线，不代替实图专业审美或原报告每一单元格的人工判断。
- **真实被 CI 抓住的 v8.4.1 回归**：[41667517537](https://github.com/kobolibra/financials/actions/runs/41667517537) **FAIL**，公司财务算术29项、浏览器三屏均 PASS，但源 `source-ledger.json` 的 `source.reason` 随新哈希说明被改，真实已发布 `public/688220.html` 的内嵌原始账本仍是旧说明，导致独立重建逐字节比对失败。已**从真实源账本修复**：保留验证过的完整 PDF 镜像 SHA `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc` 与镜像状态、将 `reason` 恢复成已发布且仍准确的原文，**不更改公司财务金额或已发布 HTML**。新回归会比对所有内嵌 `ledger-data` 的原始 `issuer/source/facts/segments` 字段，禁止下一家公司在重建时才暴露问题。
- **最新实际 QA 证据**：源账本修复后 [41667953097](https://github.com/kobolibra/financials/actions/runs/41667953097) **PASS**（完整 PDF/29 会计检查/九图原始渲染/真实1440、768、390/干净再次生成与已发布 HTML 逐字节比对）；真实 Cloudflare 八家公司目录与翱捷科技新四源节点金额几何 [41667952839](https://github.com/kobolibra/financials/actions/runs/41667952839) **PASS**；主分支交接 [41667952648](https://github.com/kobolibra/financials/actions/runs/41667952648) **PASS**。该线上 PASS 证明确实检查到了上次旧版没有的细来源节点，但**不能**冒充完整重大附注、独立金融/视觉研究编辑审查或整个 A 股行业的验证。
- **未解决 P0/P1 数据问题明确保留**：688220 p.137 应收集中度披露 90.50% vs 简单导出89.17% 分母 **FAIL**，p.179 剩余履约义务分类差 0.01 元 **FAIL（披露取整的有界例外）**；上交所官方 PDF 与归档镜像字节完全一致 **NOT_CHECKED**；全部重大附注完成复核、外部8–12季度/可比/估值、第二名真实独立研究员 **NOT_CHECKED**。这批工作没有以新文档替代这些需要原报告的深入追证。
- **真实公司目录/出版产物**：仍仅原八家公司+已有光通信专题，所有既有独立 URL 保留，未修改 `public/*.html`、未另起入口。未来新公司必须从原始 PDF → 行列和三表/附注 → 研究主线与反例 → AEI/FT 原创图形 → 截图 → 本地重建 → 本次 Cloudflare 逐级通过，并将所有失败转化为真正可运行的恶意回归，最后更新现行此文件和机器状态。精确协议见 [docs/SKILL_EVOLUTION_PROTOCOL.md](docs/SKILL_EVOLUTION_PROTOCOL.md)。

## 2026-11-03 · 历史故障复盘：桑基真实比例与早期 Cloudflare 旧版发布阻断（现已解决）

**以下 FAIL 是旧提交、旧检查时点的真实历史记录，必须保留作反例，不代表此刻的线上状态**。后续严格真实站点检查 [41667952839](https://github.com/kobolibra/financials/actions/runs/41667952839) 已 PASS，参见本文件最顶部 CURRENT 状态；不可重复将旧 FAIL 当成最新项目结论。

- **实际源工程已合并 `main`**：修复来自 [PR #8](https://github.com/kobolibra/financials/pull/8) 的提交 `3a1878fa127eb8f757d1da1b68c5d8c1985b0ec0`。原有九张独立财务研究图、全部八个公司独立 URL 保留，原七公司 HTML 没有被改写。主版本是 `public/688220.html`，源头是 `research/issuers/688220/report-template.html` 与 `publish.py`。
- **真正的 AEI/FT 图形错误**：旧版 p.178 “测试服务与其他”收入 79,769.92 元在桑基里按金额计算只有约 **0.011 SVG 单位**高，但来源节点 `span<1` 被换成固定 `stroke-width=1` 的线，视觉放大约 92 倍（流向 ribbon 原金额未变）。现移除最小 1px 线条，四类来源全按真实元金额构成节点，七条真正有金额的成本/毛利 Ribbon 与一条 **零毛利、零正面积**分流均如实处理。所有来源/终点源标签、期间、物理 p178、金额与图形几何有独立 browser 校验，不能只将 `data-value` 当成可视比例的证据。
- **桌面阅读修复**：原收入桑基 SVG 1190px，现金及资产负债图 1100/1090px，桌面 figure 可用区域约 1060px，虽然整页不溢出却会让部分成本/利润终点隐藏于图内滚动。上述三图现改为 1050px；Playwright 在 1440px 逐图强制内部 `scrollWidth <= clientWidth + 2` 并检查 SVG 文字 `getBBox()` 不出边界；768/390 保留图内滚动并确保第一层结论金额可直接阅读。
- **PASS / 真实运行证据**：旧完整原始 PDF 镜像 224 页/1,449,510 字节/SHA256 `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`，原始选定 118 项（109 连续文字+9 原单元格坐标）不变；`main` 会计/浏览器重建 [41660215226](https://github.com/kobolibra/financials/actions/runs/41660215226) **PASS**，线上现有 8 公司/24 路径尺寸 [41660215201](https://github.com/kobolibra/financials/actions/runs/41660215201) **PASS（仅已部署旧版的目录/路由层）**，主分支交接 [41660215142](https://github.com/kobolibra/financials/actions/runs/41660215142) PASS。真实 `1440/768/390` + 实图 Path 坐标、四来源、两个终点、零利润、不截断与 SVG 导出完成，21 张新图截图已在 [41659486482](https://github.com/kobolibra/financials/actions/runs/41659486482) 的 artifact 开卷检查。严格 Skill 条款与发布清单同步修正。
- **FAIL / 线上真正阻断**：新增 `main` live QA commit `ac588ebab444ec4510747ddcb46395b397ca9699` 后，[41660682930](https://github.com/kobolibra/financials/actions/runs/41660682930) 在 Cloudflare 线上 `/688220.html` 找不到修复版 `rect.money-source`，说明公网仍提供旧版图形；**LIVE_NEW_SVG=FAIL**，而不是“站点已全新通过”。对应 `3a1878...` 的 **Cloudflare Pages** GitHub provider check 仍 `in_progress`（检查时点），不能对外声称新代码的 Cloudflare 部署 PASS。新上线验收条件不能删除或放宽。
- **线上再次重试仍失败（已真实执行）**：GitHub Actions [41660682930](https://github.com/kobolibra/financials/actions/runs/41660682930) **run_attempt=2** 于 2026-11-03 15:14 UTC 再次结束 **FAIL**，报错仍为 `ASR source amounts not represented as geometric nodes`，证明部署公开页确实未变而非一过性的浏览器等待错误；对应 Cloudflare Pages provider 检查尚无完成结论。不能删掉严格断言来换绿色。
- **NOT_CHECKED / 不得冒充**：上交所官方静态 PDF 服务器与已核镜像的字节同一性、全部 224 页重大附注完整独立逐项复核、8–12 季度真实同行/估值、第二名真正独立人类财务或视觉审稿人；应收及合同资产附注集中度 p137 披露 90.50% 与简单披露分母回算 89.17% 仍 **FAIL_UNRECONCILED**，待履约义务 p179 明细相加比披露总额多 **0.01 元**，没有编造补差额。
- **此历史阻断已关闭**：后续真实 Chrome/Cloudflare 严格检查 [41667952839](https://github.com/kobolibra/financials/actions/runs/41667952839) 在八公司×三视口检验新版四个 `money-source`、7 条真实流带、极小源金额、零毛利和桌面图内不裁切 **PASS**。依然要求每个未来新 `main` 的部署重新验本次精确版本，不能用这次的通过替代未来所有提交。

## 2026-11-03 · 九图正式版增量原始 PDF 行列证据与图形通用财务关系

以实际 main 九图、Skill v8.3.3-RC1 为基准；不将旧开发八图版本覆盖九图发布页。原始 224 页 PDF 副本 SHA256 `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`，1,449,510 字节。交易所源文件 vs 镜像原字节同一性 NOT_CHECKED。

**原始源页重点**：`research/issuers/688220/source-cells.json` 定位 p.135 应收坏账准备，以及 p.146 八项库存原值、跌价、库存商品、委托加工及履约成本，包含原始 PDF words bbox、行名、列标题、2025-12-31 或 2026-06-30 日期。`verify_pages.py` 在完整 PDF 原字节直接复原，109 项连续原数字 + 9 项物理单元格 = **118/118 选定原金额可定位**。仍保留 p.87 上期列 15.30 元营业外支出的 x 坐标、本期空格核验。绝不等于全部 224 页重大附注独立全文审阅。

**可重用守恒与反例**：`research/shared/conserved_flow.py` 和 `research/shared/test_conserved_flow.py` 是一个源分类关系内核，要求同一分类轴、原币种、同合并期间、原始物理页，精确 Decimal 验证四类来源→成本/毛利，七条非零带与一条真实零毛利（不捏造可见面积）。八种故意错误的源关系必须被拒绝。单公司实例和合成反例并不认证跨行业 Level 2/3。

**旧目录元数据修复**：`site/research_catalog.json` 中 688220 原留七图，当前正式研究正文和 `figure-briefs.json` 为九图，已纠正为九图并用唯一 `site/portal_builder.py` 重新生成原 `public/index.html`；原七公司 HTML 未改动。

**独立门槛**：PDF 镜像 SHA、指定源金额/源格、三报表/全部 17 CFO 会计身份、九图本地源表、真实浏览器响应式分别 PASS（在对应运行的确切 SHA 上）；原 p.137 应收及合同资产集中度披露 90.50% vs 直接重算 89.17% 仍 FAIL_UNRECONCILED，p.179 RPO 拆分 0.01 元不闭合；SSE 与镜像原字节一致性、完整附注系统审阅、外部估值及第二名独立人类财务／设计审核 NOT_CHECKED。正式 Cloudflare 需以合并后最新 commit + GitHub Actions 真实八公司导航和 1440/768/390 为准，绝不从分支成功推定线上成功。

## 2026-11-03 · 现行正式状态：AEI/FT 源证据重构已上线；财务源边界仍明确保留

**唯一正式站点**：<https://financials-in-visuals.pages.dev/>，目前八家公司**在同一个**目录下各有完整独立 HTML。翱捷科技-U 688220：<https://financials-in-visuals.pages.dev/688220.html>。没有新增另一版四公司入口、没有改写旧七家 HTML。本次 AEI/FT 重构已通过 [PR #6](https://github.com/kobolibra/financials/pull/6) 合并真实 `main`，研究/HTML 源提交 `5f2cf82cd515e5e85a8a41a93ab4bcc0f10554d8`，Skill 为 **v8.3.3-RC1**。主分支新发布回归适配提交 `f9f3ac4377c98fb5d9390716531c023a4def1393` 与 `52c4a6f166451ef3a132f929ab1e776a1521e130`。

**真实执行并非口号**：从 `research/issuers/688220/source/688220_2026H1_20260829_original.pdf` 完整 PDF 镜像字节（2026-08-29，2026H1，224 物理页，1,449,510 bytes，SHA-256 `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`）读取合并三表、原始业务收入/成本及现金流全 17 条 signed 调节。4 类互斥业务来源分别以**其自己的 p.178 原始成本和推导毛利**绘制真实比例尺分流（四条正成本 + 三条正毛利；测试服务真实零毛利不制造假流量）；另有完整毛利→法定净利润 signed CAS 瀑布，以及共同金额尺度两期资产＝负债＋权益存量组成。总共九项不同研究问题、九张原始证据表与手机端独立数字结论，这些数目只表示技术覆盖而非审稿认证。逐图独立研究契约：`research/issuers/688220/figure-briefs.json`；发行人独有研究：`research-memo.md`；可重建 HTML：`public/688220.html`、`report-template.html`、`publish.py`。研究依 Skill v8.3.3/完整研究手册 01–05，重构实际插图和原文均已在本会话打开检查。

**本轮最关键的已解决源问题**：原始 PDF 物理第 87 页 `减：营业外支出 15.30 元` 在 **2025H1 对比右列**，**非 2026H1 本期**；本期该格空白，经营利润 54,945,406.18 + 营业外收入 256,125.37 = 税前利润 55,201,531.55，故本期贡献为**推导零，非发行人披露的 0.00 元**。旧账本错列已直接更正到 `source-ledger.json` 和 PDF 物理 x 列核验 `verify_pages.py`，完整带符号 P&L 测试使该错误显现并在真实发布前修复。只在同一页找到金额绝不等于行列语义检验。

**实际核实的 GitHub/Cloudflare**：

- 完整源/会计/SVG/移动端分支 [41652625378](https://github.com/kobolibra/financials/actions/runs/41652625378)：**PASS**，含 `scripts/check_handoff.py`、同目录单测、PDF SHA、原始 p.87 列坐标、29 项元精度身份、8 项 hostile 错误注入反例，9 图/9 证据表/21 张 1440/768/390 实截图及 3 SVG 导出，干净重建位对位一致。
- 新版主分支源财报与离线浏览器 [41653197855](https://github.com/kobolibra/financials/actions/runs/41653197855)，SHA `f9f3ac4377c98fb5d9390716531c023a4def1393`：**PASS**。
- 八家公司统一目录 **真实 Cloudflare 公共页面** Chromium 导航和三尺寸 [41653304202](https://github.com/kobolibra/financials/actions/runs/41653304202)，SHA `52c4a6f166451ef3a132f929ab1e776a1521e130`：**PASS**；原七家旧 URL 未改。
- 主分支 Skill 与交接 [41653016658](https://github.com/kobolibra/financials/actions/runs/41653016658)：**PASS**。最初主分支运行 `41653016669` 与 `41653016654` 曾因**测试仍硬编码七图**失败，现已直接修改测试为按图形 brief 动态计数，重新实际通过，不掩盖失败历史。
- 本会话 web 抓取对 Cloudflare 页面返回访问限制；以上 LIVE PASS 特指 GitHub-hosted Chromium **真实线上浏览器访问**，不是当前 web 工具自己直开成功，也不是人工独立设计编审签字。

**两套研究+视觉质量门槛并列，不能合并**：

| 门槛 | 当前实况 |
|---|---|
| 完整 224p PDF 镜像 SHA + 报表期间 | **PASS** |
| 上交所服务器原 PDF vs 归档镜像逐字节完全一致 | **NOT_CHECKED**（交易所静态主机返回挑战/无法取到完整 PDF 字节） |
| 重大原始行列语义 | **p.87 重大列错 PASS 修复；其他附注 PARTIAL**，9 项 PDF 窄表文字需更大覆盖 |
| 财务精确恒等式 / CFO 全 17 项 / 同维度真实分流 | **PASS**（元精度） |
| 机构级行业研究、反证与现金/资本逻辑 | **PASS 自审源限定研究；外部多年同业/估值 NOT_CHECKED** |
| AEI/FT 真实桑基、signed P&L、BS 语义与实际截图 | **PASS 技术/自审视觉纠错；独立高等级设计编审 NOT_CHECKED** |
| 原始附注 p.137 前五名应收+合同资产披露占比 90.50% 对 p.135+p.138 原值计算 89.17% | **FAIL（边界明确、不能捏造分母）** |
| p.179 RPO 拆分对合计差额 0.01 元 | **FAIL 有界原披露精度，禁做假守恒图** |
| 真实 Cloudflare 八家公司路由 1440/768/390 / 无 iframe | **PASS** |
| 第二位独立人类财务分析师签核 | **NOT_CHECKED** |

**当前发布类别：RESEARCH_PREVIEW / SOURCE_LIMITED**。不将技术通过或九图当作全附注、同行估值、独立研究签核通过。若进一步推进，按原始报告行列直接解决有争议的 p.137 比例分母、p.179 一分钱与剩余重大附注，再增加有真实披露的 8–12Q/同行数据。不能以这些遗留项为借口放弃已能完成的研究或设计迭代。

**当前可再现命令**：

```bash
python research/issuers/688220/verify_pages.py
python research/issuers/688220/test_accounting.py
python research/issuers/688220/publish.py --out public/688220.html --qa research/issuers/688220/qa.json
python research/issuers/688220/qa_browser.py --html public/688220.html --out research/issuers/688220/visual-qa
python scripts/check_handoff.py
```

## 2026-11-03 · 688220 翱捷科技-U · 第八家公司源限定研究预览

**发行人**：翱捷科技股份有限公司 688220.SH，2026H1，未经审计，2026-08-29 上交所公告。完整 224 物理页披露副本（新浪公告镜像、非上交所原始服务器字节认证），1,449,510 字节，SHA256 `9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc`。原件、源页文字/坐标、截图、原始附注行列证据：`research/issuers/688220/source/`、`extracted/`、`source-blocks/`、`source-images/`；`source-manifest.json` 和 `source-verification.json`。上交所静态直链在 GitHub runner 返回 3.8KB HTML，官方 URL vs 镜像完整字节同一性：**NOT_CHECKED**。

**新增的实际研究资产**：`research/issuers/688220/source-ledger.json`（93 原始金额/比例字段，合并/期间/元与物理页）；`research-memo.md`（商业模型、附注红队、会计分母差异）；`publish.py` + `report-template.html`（生成完整单公司独立、离线无外部 JS/CSS 的 `public/688220.html`）；`test_accounting.py`、`verify_pages.py`、`qa_browser.py`、`qa.json`。原七家公司报告和账本内容均保持不变；统一目录只由 `site/research_catalog.json` 扩容到八个条目，`site/portal_builder.py` 仍是原首页唯一生成器。

**机构财务核查（来源限制）**：
- PASS：四类互斥收入和成本精确合并、利润表带符号营业利润至归母、扣非 vs 非经常项目（税后）、合并 BS 本期/期初恒等式、合并净利润至经营现金流 **17 原始 signed 调整到元零差**、现金等价物期初至期末四项闭合、存货/应收账款净额、合同负债三类预收、收入时间分类。图形有真比例的收入流向桑基、有符号利润及现金瀑布、两期真实 BS 存量对比，原始表可追溯到源页。
- 原始物理页文本匹配：上一轮版本 109/118，9 项为 PDF 窄表拆分字符串，已对照 p.135、146 原始图像复核重要行/列；新 93 字段需要运行最终 `verify_pages.py` 后更新准确覆盖率。不能把页面上数字出现当作完成全部重大附注审核。
- **源披露差异不可造假修补**：p.137 前五名应收/合同资产原文占比 90.50%，但按 p.135 应收原值 464,113,067.29 + p.138 合同资产原值 1,113,000，得 **89.17%**；无法由同页披露表独立复现统计分母，`AR_TOP5_RATIO_DENOMINATOR = FAIL`。p.179 已签约尚未履约收入的时间拆分总额偏差 **0.01 元**，没有强制假“其他”平衡。报告保留两个异常、局部不可编审为通过。
- 本公司本期普通盈余的“扭亏”并非扣非扭亏：归母 +0.84 亿，扣非 −0.59 亿，CFO −3.77 亿。合同定制验收时点 p.126、合同履约成本 p.147、应收集中度 p.137、受限现金 p.189、短债期限 p.201、第三层次公允价值 p.203、单一经营分部 p.210 均进入研究及反证链。
- **未取得的认证**：全部重大附注逐项独立核验、官方服务器原件字节同一性、8–12 季度外部证据/估值、第二位独立专业财务研究员签字 = **NOT_CHECKED**。不得将本报告称为已正式“机构顶级认证”。

**技术与原创视觉**：七项不同研究问题图形，真实元金额宽度桑基，非负守恒、带符号会计桥、受限股权/公允价值口径分开；实际 Chromium 1440/768/390、SVG 导出、源表与移动端截图已经在 branch Actions <https://github.com/kobolibra/financials/actions/runs/41620029401> PASS（该运行时对应早于最新会计附注更新的提交）。本人已真正打开原始 PDF p.135、137、146 和图形截图，发现并在源码修正了桑基微型分类标签堆叠、毛利图数字压条及移动端标题孤行。最终新 commit 仍须独立测试后才能标 **PASS**。

**待发布验证**：`site/research_catalog.json` 八家公司、`public/index.html` 八卡、`public/688220.html` 单页、原七链接均进入**同一** <https://financials-in-visuals.pages.dev/>；必须运行 `python scripts/check_handoff.py`、目录回归和真实 Cloudflare GitHub Actions Playwright 1440/768/390。主分支已成功部署之前只能记录 **GITHUB/LIVE=NOT_CHECKED**。本轮没有创建独立新版本首页或破坏任何旧报告。

**可复现命令**：
```bash
python -m pip install pymupdf playwright
python research/issuers/688220/verify_pages.py
python research/issuers/688220/test_accounting.py
python research/issuers/688220/publish.py --out public/688220.html --qa research/issuers/688220/qa.json
python research/issuers/688220/qa_browser.py --html public/688220.html
python site/portal_builder.py --out /tmp/asr-portal
cmp public/index.html /tmp/asr-portal/index.html
python -m unittest discover -s site -p test_portal.py -v
python scripts/check_handoff.py
```

## 2026-11-03 · 本轮执行检查点（此前七家公司入口扩容工程的历史检查点）

**当前正式公司数仍为 7，绝无虚构的第八家公司。** GitHub `main` 代码增量提交 [`9f8cab1439`](https://github.com/kobolibra/financials/commit/9f8cab1439225bac3b25a431f85cbeae60487eba)，已合并 [PR #1](https://github.com/kobolibra/financials/pull/1)。修改：`site/portal_builder.py`、`site/test_portal.py`、`.github/workflows/verify-unified-research-library.yml`；没有修改任何既有七家公司独立 HTML、财务账本、`site/research_catalog.json` 或 `public/index.html`。这是一项 **N 家入库生成能力修复**，不是新公司财报研究或最终出版。

**可复现测试与确切结果：**
- `python -m unittest discover -s site -p test_portal.py -v`：模拟第八家公司、新行业、新报告期可进入同一目录；原七家首页重新生成与 `public/index.html` 字节完全一致。PR 运行 [41614961062](https://github.com/kobolibra/financials/actions/runs/41614961062) **PASS**。
- `python scripts/check_handoff.py`：在代码提交 `9f8cab1439` 的交接工作流 [41615024220](https://github.com/kobolibra/financials/actions/runs/41615024220) **PASS**。
- 统一网站原七家公司 GitHub Actions 真实 Cloudflare Chromium 1440/768/390 浏览器路线、检索/筛选、原有桑基、回程与截图采集：[41615024205](https://github.com/kobolibra/financials/actions/runs/41615024205) **PASS**，针对代码提交 `9f8cab1439`；**只覆盖当前七家，未做新增公司的视觉编审**。本会话的 Web 直接访问被禁用、容器 DNS 解析 Cloudflare 失败，所以本会话直接 HTTP/独立截图复核为 **NOT_CHECKED**；不得将 CI 截图存在等同本人逐张视觉审批。
- 老版本 `last_verified_release` 所载原 PDF 和附注会计检查仍只是对应旧提交的历史通过范围；本轮没有宣称重新完成七家全附注审计。

**新发行人取证阻碍：** 当前聊天的上传文件列表为空；已搜索本 Project/Library，仅发现此前七家公司和行业验证成果，**没有一个可确定身份的“新公司”原始 PDF 或官方完整报告链接**。故 `ISSUER_IDENTITY=NOT_CHECKED`、`ORIGINAL_PDF_BYTES=NOT_CHECKED`、`PDF_SHA256=NOT_CHECKED`、`PAGE_ROW_COLUMN_SEMANTICS=NOT_CHECKED`、`ACCOUNTING=NOT_CHECKED`、`COMPLETE_MATERIAL_NOTES=NOT_CHECKED`、`THESIS_RED_TEAM=NOT_CHECKED`、`AEI_VISUAL_EDITORIAL_NEW_ISSUER=NOT_CHECKED`、`CHART_CONSERVATION_NEW_ISSUER=NOT_CHECKED`、`BROWSER_NEW_ISSUER=NOT_CHECKED`、`GITHUB_AND_LIVE_NEW_ISSUER=NOT_CHECKED`、`INDEPENDENT_HUMAN_FINANCIAL_REVIEW=NOT_CHECKED`。不能据此开始猜数、生成财务报告或创建目录空卡。

**一旦收到新原件**：先核对 PDF 完整字节与公告/更正版本、发行人/期间/币种/审计/合并范围及 SHA、实际物理页；读取对应行业旧账本和出版器，建立原始行列证据账本、报表与附注复核、研究主线/反证和 figure brief；根据金额关系做严格守恒 Sankey 或明确不适用并采用带符号图形；仅在实际完成 HTML + 1440/768/390 本地及生产审查后向 **同一** `site/research_catalog.json` 和独立 URL 加入第 N 家，更新本文件与机器状态。该来源缺口无法靠已有七家数据补齐。

## 生产结构（经现场验证的现有基线）

原有独立光通信三篇：`/300394.html`、`/300308.html`、`/300502.html`；行业独立四篇：`/research/2026-h1-v10/600036.html`、`/688111.html`、`/600519.html`、`/000333.html`（完整路径见 [目录 JSON](site/research_catalog.json)）。完整专题 `/optical-2026h1.html` 不计入公司数。**新公司只能进入同一首页公司库，并保留旧 URL。**

当前唯一有效 Skill：`skills/ashare-financial-storytelling/SKILL.md` **v8.3.2-RC1**，并且 **01–05 研究规范全部必读**。两条研究基线并列验收：机构财报/行业深度与 App Economy Insights（AEI）/FT 风格的财务视觉叙事。Skill 是项目仓库文件，**不是自动加载的 ChatGPT 内置或已安装 Skill**。

## 最新已证实的修复

2026-11-03，已经对照原始半年度财报物理页确认：
- **300394** 合并收入中的 37,651,189.26 元确系 p.140 披露的其他业务收入，成本 9,087,378.57 元；另外两类光器件正好构成主营业务。
- **300502** 合并收入中的 27,106,113.32 元确系 p.104 按业务类型分类的“其他”，成本 17,534,949.75 元；它和同页另一分类维度的其他业务收入 21,528,572.02 元**不同，绝对不能混加**。

两篇独立 HTML、原始账本及相关收入桑基图已修复。图形引擎不再用“未列示差额（计算）”伪造财务流量。详见 `docs/2026H1_OPTICAL_REVENUE_NOTE_CLASSIFICATION_AUDIT.md`。本次仅解决**这两个分类问题**，不能外推为全部七家公司附注已复核。

## 上一次已知的实际 PASS（以后每次都须重新查看 HEAD）

上一次完整发布内容对应 GitHub commit：`4a734d60a40839c90d12a295c61be917783b7187`。

| 验收工作流 | GitHub Actions | 上次结果 |
|---|---|---|
| 原始收入分类精确重建与发布一致性 | [41599963892](https://github.com/kobolibra/financials/actions/runs/41599963892) | PASS |
| 统一七家公司真实 Cloudflare 浏览器 | [41599963800](https://github.com/kobolibra/financials/actions/runs/41599963800) | PASS |
| 老版、历史研究导航 | [41599963891](https://github.com/kobolibra/financials/actions/runs/41599963891) | PASS |

这些通过记录仅证明对应提交的测试范围；**不代表新公司/新报告/后续修改自动通过**。当前 HEAD 用 GitHub 即时读取，不把一个会随提交变化的 SHA 假写成永久“当前 commit”。

## 尚未完成（必须保留 NOT_CHECKED，不准自证）

- **七家公司完整重大附注系统复核**：NOT_CHECKED（重要性导向核查收入、往来、减值、现金流及行业特殊附注；已抽核的两个分类不代表完成）。
- **真正独立的第二名人类财务研究员签核**：NOT_CHECKED（助手自身的第二遍复查不得冒充独立人类）。
- **真实外部证据支持的 8–12 季度、行业同行/估值和市场数据**：大多数公司 NOT_CHECKED；无来源时不得出图。
- **每个行业完整可泛化的自动 PDF→出版引擎**：NOT_PROVEN。现有 v7 光通信及 v10 另外四公司是已验证案例，不代表任意新行业自动可用。

研究质量不能通过图表数、自动测试数、PDF 文本字符串匹配或站点 HTTP 200 来代替。发布流程与保守门槛见 [REPORT_RELEASE_CHECKLIST](docs/REPORT_RELEASE_CHECKLIST.md)。

## 新会话交接工作

**开始**：GitHub 读此文件、`START_HERE.md`、`project-status.json`，完整读 Skill 和五份研究手册，再检查最新 Actions；原 PDF 不在新会话里自动出现时必须取得真实字节、核实 SHA/报表期间与版本。

**执行**：对已有模块先复用、对新公司只添加一个真实公司条目与独立页面，不创建重复目录；每个财务/可视化关卡逐项 PASS/FAIL/NOT_CHECKED。

**结束**：将所改代码、来源、原始 PDF 归档引用、可复现命令、门槛状态、真正生产链接和可继续执行的下一步记录在 `PROJECT_STATE.md` 及机器状态中。绝不将未完成的问题笼统留给用户重新提醒。完整协议：[docs/HANDOFF_PROTOCOL.md](docs/HANDOFF_PROTOCOL.md)。

历史旧状态全文完整保存在 [docs/history/PROJECT_STATE_ARCHIVE_2026-11-03.md](docs/history/PROJECT_STATE_ARCHIVE_2026-11-03.md)，不是现行执行指令。

## 2026-11-03 · NEW-SESSION HANDOFF MECHANISM

Obsolete initial README and old 25k-character accumulated PROJECT_STATE are replaced by a single active seven-company status and preserved historical archive. Current source of truth: `START_HERE.md`, `project-status.json`, complete Skill v8.3.2-RC1 and five manuals. New Code/Agent entry: `AGENTS.md` and standard Codex `.agents/skills/ashare-financial-storytelling/SKILL.md` wrapper, which links to the ONE canonical full Skill. Ordinary ChatGPT new-session continuity: `docs/CHATGPT_PROJECT_INSTRUCTIONS.md` + `docs/SETUP_PERSISTENT_CONTEXT.md` for one-time user Project settings; this GitHub edit cannot modify the user's ChatGPT account automatically. Explicit copy-paste fallback: `docs/NEW_SESSION_PROMPT.md`.

First handoff validation PASS: GitHub Actions https://github.com/kobolibra/financials/actions/runs/41610923043, including manifest/Skill/manual/source/index checks, 6 adversarial handoff regressions and 9 independent portal tests. This run tested the earlier documentation-only commit; later edits need own checks. New handoff workflow `.github/workflows/verify-handoff.yml` triggers automatically on its own relevant content paths. Prior financial PDF/report browser QA remains separately logged as historical actual evidence; no new company finance report is certified by the handoff workflow.
