# Editorial & Financial Information Design — original system

## Goal
Make complex accounting relationships immediately intelligible without sacrificing rigor. App Economy Insights is useful as **an example of business-model-first, legible money-flow explanation**, not a graphic style guide to clone. Build an independent, restrained, high-information publication with unmistakable Chinese typography and clear attribution.

## Information architecture
A. Opening visual thesis (the reader understands the key change within 5 seconds) + one sentence "why now".
B. Two-sided thesis / counter-thesis evidence, not generic KPI dashboard.
C. One large signature chart to explain business economics; 1–3 contextual charts to explain drivers, earnings-cash divergence and risk.
D. A short qualitative interpretation adjacent to each plot: **What happened / What evidence says / Alternative / Next evidence**.
E. Bottom methods, source tables, assumptions and disclosure gaps. Each chart references exact printed pages.

## Choose appropriate visual grammar
- **Conserved non-negative split / aggregation:** truthful Sankey, bands scale to numbers; arrows mean allocation, not movement of literal cash unless cash is truly modeled. Source and destination nodes must be exactly balanced with explicit differences/unallocated amounts.
- **Signed add/subtract:** waterfall with positive and negative steps separated and end-total reconciliation; earnings-to-CFO signed adjustments. Never run an absolute negative path in a Sankey.
- **Two points / periods:** slope/dumbbell or paired bars; percentage-point change separated from percent growth.
- **Concentration:** ranked bars plus coverage share and named-unreported if source anonymizes; Top-5 AR concentration is **not** revenue concentration.
- **Change in product mix and gross margin:** stacked proportions and price/mix bridge if inputs justify; otherwise show disclosed current mix and product margin change; uncertain prior-segment reconstruction clearly approximate.
- **Balance composition:** nested bars or an equal-total paired assets vs debt/equity diagram, NOT a cash-transfer Sankey.
- **Trade-off matrix:** questions on growth, return, capital, risk; no invented ordinal ranking.
- **Threshold/risk:** diverging bands or indexed charts with a clear baseline and meaningful denominator.
- If interactivity does not add real utility, use accurate static SVG; never create pointless hover.

## Art direction & quality standards
- Original editorial, not a finance dashboard. Quiet paper background, ink/navy text, restrained emerald value, neutral cost/financing, muted rust negative/caution. Strong typographic rhythm, purposeful whitespace and direct figure annotation.
- Accessible semantic color AND text (not red/green alone), WCAG AA approximate contrast for legible text; use system Chinese font fallbacks (PingFang SC, Noto Sans CJK SC if installed, Microsoft YaHei) and serif only for optional Latin display.
- Desktop content 1050–1240 px max with big figure breathing room; 390px mobile uses reflow/figure scrolling, chart minimum readable size and visible scroll affordance. Do not render 1600px SVG shrunk to 350px with 9px text.
- Lead with point, not a technical title: "原材料备货翻倍，经营现金流却在改善" is stronger than "存货结构分析". Always specify period, units, and comparison basis.
- Figure caption source format: "来源：天孚通信 2026H1 报告第 22、61 页；无源/有源为披露数据，其余为计算差额。图表为解释性分配，不代表实际现金流向。" Source p must map to PDF.
- Data labels: Chinese 亿元 two decimals, raw yuan on focus/hover; percentage changes with signed sign; % vs percentage points explicitly.
- Important title must be supported by visual. Avoid decoration: 3D, gradients that distort area, perspective, screenshots of tables, stock imagery.
- Corporate logos or artwork from other publishers are not copied.
- Desktop screenshots should demonstrate: hero hierarchy; one entire flagship chart; an annotated key diagnostic; footnotes and sources. Mobile test verifies horizontal scroll, not only top screen.

## Interactive behavior
- Each major figure keyboard-focusable with aria label; focused ribbon/bar displays same details as hover (including p., unit, formula where calculated). Provide table/text equivalent.
- SVG export optional; if provided it must output a functioning, self-contained SVG (with font fallback), correct extension and scale. No external network at page load or interaction.
- An independent source/method disclosure in the report is mandatory even when tooltips exist.
- Semantic heading nesting, document lang zh-CN, page title, visible focus outline, responsive chart treatment and escape key for modal.
- Browser QA: 1440/900, 390/844 and 768; screenshot full page; no overflow clipped meaningfully; console zero uncaught exceptions; navigation, tooltip, focus, export pass; note failing claims.

## Five-second tests
For each chart ask reviewer (1) what's the question (2) main conclusion without reading prose (3) values/period visible (4) all flows add up (5) can I follow source? If any no, redesign or remove.
