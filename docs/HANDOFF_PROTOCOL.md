# Inter-conversation handoff protocol

Each substantial task starts with a 5-minute source check and ends with durable checkout state. This is **not memory-based** continuity.

## At the beginning
1. Fetch `PROJECT_STATE.md` from the actual current branch and verify HEAD; inspect main/working branches and recent commits.
2. Read real `skills/ashare-financial-storytelling/SKILL.md`, its mandatory four research files, implementation READMEs, source/QA manifests. If these were changed, do not rely on old summaries.
3. Check original issuer PDF bytes, SHA/page count and archive location. If missing, use the pinned Actions acquisition workflow; fail closed rather than substituting web snippets.
4. Classify claims and artifacts as verified Git state, CI artifact, local workspace, remote deployed site, or not checked.

## At the end
Update `PROJECT_STATE.md` with (a) mission and invariants, (b) branch+HEAD+SKILL blob, (c) original PDFs and SHA, (d) data & report paths, (e) tests PASS/FAIL/NOT_CHECKED, (f) site status and URL, (g) newly discovered P0/P1 regressions, (h) next execution-ready commands. Keep a `CHANGELOG.md` and issue/acceptance list; do not rely on previous conversation memory as the only record.

## Source/research/figure gates
`RAW_BYTES > PDF_IDENTITY > PAGE_NUMERIC_MATCH > SEMANTIC_SOURCE_REVIEW > EXACT_ACCOUNTING > RED_TEAM > FIGURE_DATA_CONTRACT > MOBILE_SVG > BROWSER_RENDER > REAL_HTTP_NAV > INDEPENDENT_EDITOR > PUBLIC_DEPLOYMENT`. Unknown is NOT_CHECKED, not PASS. Each newly found regression gets a failing test **before** or alongside the fix.

## Branch/release discipline
Use a feature branch for sample tests and Skill proposals, keep the existing three independent optical reports intact, preserve directory homepage, no iframe workarounds, and do not edit unrelated repositories. Promotion requires explicit verification of output and public route, not only GitHub commit success.
