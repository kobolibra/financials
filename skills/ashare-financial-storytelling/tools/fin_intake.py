#!/usr/bin/env python3
"""Source intake CLI for any A-share periodic report (Q1 / H1 / 9M / FY).

It removes the slow, error-prone hand work of a new dossier without making
analytical decisions for the analyst:

  init       archive the original PDF, hash it, detect issuer/report type,
             extract page text and write a skeleton dossier folder
  find       list pages that contain statement titles or a search phrase
  scan       print every numeric row on a page with column index and bbox
  facts      turn an explicit fact spec (page + row label + column) into
             source-ledger facts with exact PDF cell coordinates
  preflight  run the publication validator plus an editorial lint

Every fact still names its page, row and column explicitly. The tool never
guesses a missing number, fills a blank cell with zero or picks a column for
you. Run from the repository root:

  python skills/ashare-financial-storytelling/tools/fin_intake.py init --code 300570 --pdf /path/report.pdf --url https://static.cninfo.com.cn/...PDF
  python skills/ashare-financial-storytelling/tools/fin_intake.py find --code 300570 --statements
  python skills/ashare-financial-storytelling/tools/fin_intake.py scan --code 300570 --page 40
  python skills/ashare-financial-storytelling/tools/fin_intake.py facts --code 300570 --spec research/issuers/300570/fact-spec.json
  python skills/ashare-financial-storytelling/tools/fin_intake.py preflight --code 300570
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = Path(__file__).resolve().parents[1]
NUMBER = re.compile(r"^([-−(（]?[0-9][0-9,]*(\.[0-9]+)?[)）]?%?|[-−—]{1,2})$")
FULL_NUMBER = re.compile(r"^[-−]?([0-9]{1,3}(,[0-9]{3})+|[0-9]+)(\.[0-9]+)?$")
REPORT_KIND = {"半年度": "H1", "年度": "FY", "第一季度": "Q1", "第三季度": "9M"}
COMPARATIVE = {"H1": "H1", "FY": "FY", "Q1": "Q1", "9M": "9M"}
STATEMENT_TITLES = (
    "合并资产负债表", "合并利润表", "合并现金流量表", "现金流量表补充资料",
    "合并所有者权益变动表", "营业收入和营业成本", "主营业务分行业", "主营业务分产品",
    "营业收入构成", "非经常性损益", "主要会计数据和财务指标", "分季度主要财务指标",
)


def pymupdf():
    try:
        import pymupdf as m  # type: ignore
    except ImportError:  # pragma: no cover - environment guidance
        sys.exit("pymupdf is required: pip install pymupdf")
    return m


def folder(code: str, period: str | None = None) -> Path:
    """Issuer dossier folder. A later report period of an issuer that already
    has a dossier lives in research/issuers/<code>/<period>/ (e.g. 20269M)."""
    if not re.fullmatch(r"[0-9]{6}", code):
        sys.exit("issuer code must be six digits")
    base = ROOT / "research" / "issuers" / code
    if period:
        if not re.fullmatch(r"20[0-9]{2}(Q[1-4]|H1|9M|FY)", period):
            sys.exit("period must look like 2026Q1, 2026H1, 20269M or 2026FY")
        return base / period
    return base


def squash(text: str) -> str:
    return re.sub(r"\s+", "", text).replace("報告", "报告")


def to_decimal(printed: str) -> Decimal:
    """Exact signed value of a printed cell. Parentheses mean negative."""
    raw = printed.replace(",", "").replace("−", "-").strip()
    negative = raw.startswith(("(", "（")) and raw.endswith((")", "）"))
    raw = raw.strip("()（）")
    if raw.endswith("%"):
        raise ValueError("PERCENT_CELL_IS_NOT_A_MONEY_FACT " + printed)
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError("NOT_A_NUMBER " + printed) from exc
    return -value if negative else value


# ---------------------------------------------------------------- init
def detect_identity(doc, code: str) -> dict:
    cover = squash(doc[0].get_text())
    match = re.search(r"(20[0-9]{2})年(半年度|第一季度|第三季度|年度)报告", cover)
    if not match:
        sys.exit("COVER_REPORT_TYPE_NOT_FOUND: inspect page 1; abstracts (摘要) and English versions are not accepted")
    if "摘要" in cover[: cover.find("报告") + 6]:
        sys.exit("REPORT_ABSTRACT_NOT_ACCEPTED: use the complete report, not 摘要")
    year, kind = match.group(1), REPORT_KIND[match.group(2)]
    identity_page = next((i + 1 for i in range(min(len(doc), 12)) if code in doc[i].get_text()), None)
    if identity_page is None:
        sys.exit("ISSUER_CODE_NOT_FOUND_IN_FIRST_12_PAGES")
    audited = "NOT_DETERMINED"
    # Short quarterly reports state the audit status on the last page.
    text = squash("".join(doc[i].get_text() for i in (range(len(doc)) if len(doc) <= 40 else range(8))))
    if re.search(r"(半年度|季度)报告(是否)?(未经|未)审计|财务报告未经审计|未经审计", text):
        audited = "未经审计"
    elif "标准无保留意见" in text or kind == "FY":
        audited = "审计报告见财务报告章节（核对意见类型）"
    prior = str(int(year) - 1) + COMPARATIVE[kind]
    extra = {}
    if kind == "9M":
        extra = {"本报告期": year + "Q3", "上年同期本报告期": str(int(year) - 1) + "Q3"}
    return {"fiscal_period": year + kind, "comparative_period": prior,
            "identity_page": identity_page, "audit": audited, "flow_columns": extra}


def cmd_init(a) -> None:
    m = pymupdf()
    base = folder(a.code, a.period)
    pdf = Path(a.pdf)
    data = pdf.read_bytes()
    if not data.startswith(b"%PDF"):
        sys.exit("NOT_A_PDF: the download may be an HTML error page")
    sha = hashlib.sha256(data).hexdigest()
    doc = m.open(pdf)
    ident = detect_identity(doc, a.code)
    (base / "source").mkdir(parents=True, exist_ok=True)
    (base / "extracted").mkdir(exist_ok=True)
    target = base / "source" / f"{a.code}_{ident['fiscal_period']}_complete_original.pdf"
    if target.resolve() != pdf.resolve():
        shutil.copyfile(pdf, target)
    for i, page in enumerate(doc):
        (base / "extracted" / f"p{i + 1:03d}.txt").write_text(page.get_text())
    name = re.sub(r"\s+", "", doc[0].get_text()).split("20")[0][:40]
    ledger_path = base / "source-ledger.json"
    if ledger_path.exists() and not a.force:
        print("KEEP_EXISTING", ledger_path)
    else:
        issuer = {"code": a.code, "name": a.name or name, "short": a.short or "",
                  "industry": "", "sector_adapter": "", "accounting_route": "",
                  "fiscal_period": ident["fiscal_period"], "comparative_period": ident["comparative_period"],
                  "base_unit": "人民币元", "audit": ident["audit"], "income_figure_title": ""}
        if ident["flow_columns"]:
            issuer["flow_columns"] = ident["flow_columns"]
        if a.route:
            issuer["route"] = a.route
        ledger = {"issuer": issuer,
                  "source": {"official_announcement": a.url, "original_bytes_sha256": sha,
                             "original_bytes_gate": "COMPLETE_ARCHIVED_PDF_SHA_PASS",
                             "source_path": str(target.relative_to(ROOT)),
                             "physical_pages_observed": len(doc),
                             "issuer_identity_page": ident["identity_page"],
                             "source_provider": "CNINFO/交易所完整原始报告；封面全称与证券代码页交叉识别"},
                  "income_partition": {}, "facts": {}, "segments": [], "cfo_adjustments": []}
        ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
    pub = base / "publication.json"
    if not pub.exists():
        shutil.copyfile(SKILL / "templates" / "publication.template.json", pub)
    print(json.dumps({"code": a.code, "sha256": sha, "pages": len(doc), **ident,
                      "archived": str(target.relative_to(ROOT)),
                      "next": "find --statements, then scan pages and write fact-spec.json"},
                     ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- find / scan
def open_source(code: str, period: str | None = None):
    m = pymupdf()
    ledger = json.loads((folder(code, period) / "source-ledger.json").read_text())
    return m, m.open(ROOT / ledger["source"]["source_path"]), ledger


def merge_wrapped(words: list) -> list:
    """Re-join numbers a narrow table column wrapped onto two lines.

    Quarterly reports print the headline table in narrow right-aligned columns,
    e.g. "1,923,161" above ",156.63". A fragment pair is merged only when both
    are right-aligned in the same column, vertically adjacent, and the joined
    text is a well-formed number while at least one half is not valid alone.
    """
    used, out = set(), []
    for i, a in enumerate(words):
        if i in used:
            continue
        ta = a[4].strip()
        merged = None
        if re.fullmatch(r"[-−]?[0-9][0-9,]*", ta) and "." not in ta:
            for j, b in enumerate(words):
                if j in used or j == i:
                    continue
                tb = b[4].strip()
                if not (8 <= b[1] - a[1] <= 15 and abs(b[2] - a[2]) < 1.2):
                    continue
                if not re.fullmatch(r"[,0-9][0-9,]*(\.[0-9]+)?", tb):
                    continue
                joined = ta + tb
                if FULL_NUMBER.match(joined) and (not FULL_NUMBER.match(ta) or not FULL_NUMBER.match(tb)):
                    merged = (j, joined)
                    break
        if merged:
            j, joined = merged
            b = words[j]
            used.update((i, j))
            out.append((min(a[0], b[0]), a[1], max(a[2], b[2]), b[3], joined, "wrapped"))
        else:
            out.append(tuple(a[:5]) + (None,))
    return out


def rows_on_page(page) -> list[dict]:
    """Group words into visual rows; numeric tokens become indexed columns.

    Dash placeholders ("-") keep their column so indexes match the printed
    table; they are never numbers. Labels that a narrow column wrapped across
    several lines are attached to the nearest row that contains wrapped cells.
    """
    words = merge_wrapped(sorted(page.get_text("words"), key=lambda w: (round(w[1], 0), w[0])))
    words.sort(key=lambda w: ((w[1] + w[3]) / 2, w[0]))
    rows: list[list] = []
    for w in words:
        mid = (w[1] + w[3]) / 2
        if rows and abs(rows[-1][0] - mid) <= 2.5:
            rows[-1][1].append(w)
        else:
            rows.append([mid, [w]])
    # Columns are numbered per TABLE BLOCK (numeric rows within 85pt of each
    # other), from the right edges of numbers that line up. A page often holds
    # several tables with different geometry, and a row with a blank cell must
    # keep its other numbers in their true columns; counting "the 2nd number in
    # the row" would silently turn a blank current-year cell into the prior year.
    dash = re.compile(r"[-−—]{1,2}")
    out = []
    for mid, ws in rows:
        ws.sort(key=lambda w: w[0])
        label = "".join(w[4] for w in ws if not NUMBER.match(w[4].strip()))
        nums = [{"printed": w[4], "bbox": [w[0], w[1], w[2], w[3]], "wrapped": w[5] == "wrapped", "col": -1}
                for w in ws if NUMBER.match(w[4].strip())]
        out.append({"y": round(mid, 1), "label": label, "numbers": nums})
    numeric = [r for r in out if r["numbers"]]
    blocks: list[list[dict]] = []
    for r in numeric:
        if blocks and r["y"] - blocks[-1][-1]["y"] <= 85:
            blocks[-1].append(r)
        else:
            blocks.append([r])
    geometry: list[tuple[float, float, list[float]]] = []
    lonely: list[dict] = []
    for block in blocks:
        edges = sorted(n["bbox"][2] for r in block for n in r["numbers"] if not dash.fullmatch(n["printed"].strip()))
        clusters: list[list[float]] = []
        for x in edges:
            if clusters and x - clusters[-1][-1] <= 1.2:
                clusters[-1].append(x)
            else:
                clusters.append([x])
        right = [sum(c) / len(c) for c in clusters if len(c) >= 2]
        if len(block) < 2 or not right:
            lonely.extend(block)
            continue
        geometry.append((block[0]["y"], block[-1]["y"], right))
        centers = []
        for cx in right:
            xs = [(n["bbox"][0] + n["bbox"][2]) / 2 for r in block for n in r["numbers"] if abs(n["bbox"][2] - cx) <= 1.2]
            centers.append(sum(xs) / len(xs))
        for r in block:
            for n in r["numbers"]:
                mid_x = (n["bbox"][0] + n["bbox"][2]) / 2
                if dash.fullmatch(n["printed"].strip()):
                    k = min(range(len(right)), key=lambda i: abs(mid_x - centers[i]))
                    n["col"] = k + 1 if abs(mid_x - centers[k]) <= 12 else -1
                else:
                    k = min(range(len(right)), key=lambda i: abs(n["bbox"][2] - right[i]))
                    n["col"] = k + 1 if abs(n["bbox"][2] - right[k]) <= 2.5 else -1
    # A table row isolated by a tall gap (e.g. the first cash-flow line) borrows
    # the column geometry of the nearest table block on the same page, but only
    # when its right edge lines up with one of that block's columns.
    for r in lonely:
        if not geometry:
            break
        y0, y1, right = min(geometry, key=lambda g: min(abs(r["y"] - g[0]), abs(r["y"] - g[1])))
        for n in r["numbers"]:
            if dash.fullmatch(n["printed"].strip()):
                continue
            k = min(range(len(right)), key=lambda i: abs(n["bbox"][2] - right[i]))
            if abs(n["bbox"][2] - right[k]) <= 2.5:
                n["col"] = k + 1
    wrapped_rows = [r for r in out if any(n["wrapped"] for n in r["numbers"])]
    if wrapped_rows:
        lo, hi = wrapped_rows[0]["y"] - 45, wrapped_rows[-1]["y"] + 45
        orphans = [r for r in out if not r["numbers"] and r["label"] and lo <= r["y"] <= hi]
        for r in orphans:
            nearest = min(wrapped_rows, key=lambda w: abs(w["y"] - r["y"]))
            nearest.setdefault("_parts", [(nearest["y"], nearest["label"])]).append((r["y"], r["label"]))
        for w in wrapped_rows:
            if "_parts" in w:
                w["label"] = "".join(s for _, s in sorted(w.pop("_parts")))
        out = [r for r in out if r not in orphans]
    return out


def cmd_find(a) -> None:
    _, doc, _ = open_source(a.code, a.period)
    needles = list(STATEMENT_TITLES) if a.statements else [a.text]
    for i, page in enumerate(doc):
        text = squash(page.get_text())
        hits = [n for n in needles if n and squash(n) in text]
        if hits:
            scope = "母公司" if "母公司资产负债表" in text or "母公司利润表" in text or "母公司现金流量表" in text else ""
            print(f"p{i + 1:03d}", " | ".join(hits), ("⚠ 同页含" + scope + "报表") if scope else "")


def cmd_scan(a) -> None:
    _, doc, _ = open_source(a.code, a.period)
    page = doc[a.page - 1]
    text = squash(page.get_text())
    if re.search(r"母公司(资产负债表|利润表|现金流量表|所有者权益变动表)", text):
        print("⚠ 本页含母公司报表：确认所选行属于合并报表，而不是母公司报表")
    unit = re.search(r"单位[:：]\s*(元|千元|万元|百万元|亿元)", page.get_text())
    print("单位:", unit.group(1) if unit else "本页未印单位，向上翻页确认")
    for r in rows_on_page(page):
        if not r["numbers"] and not a.all:
            continue
        cells = "  ".join(f"[{n['col']}] {n['printed']}{'*' if n['wrapped'] else ''}" for n in r["numbers"] if n["col"] != -1)
        print(f"y={r['y']:>6}  {r['label'][:28]:<28}  {cells}")


# ---------------------------------------------------------------- facts
UNIT_SCALE = {"元": Decimal(1), "千元": Decimal(1000), "万元": Decimal(10000),
              "百万元": Decimal(1000000), "亿元": Decimal(100000000)}


def build_fact(doc, ledger: dict, key: str, spec: dict) -> dict:
    page_no = spec["page"]
    if len(spec.get("label", "")) < 3:
        raise ValueError(f"LABEL_TOO_SHORT {key}: release gates require a row label of at least 3 characters")
    rows = rows_on_page(doc[page_no - 1])
    if "y" in spec:
        # Rows whose label was wrapped away from the numbers: select by vertical position (from `scan`).
        lo, hi = spec["y"]
        matches = [r for r in rows if lo <= r["y"] <= hi and r["numbers"]]
        spec = {**spec, "row": "y=" + str(spec["y"])}
    else:
        pattern = re.compile(spec["row"])
        matches = [r for r in rows if pattern.search(r["label"]) and r["numbers"]]
    occurrence = spec.get("occurrence", 1)
    if len(matches) < occurrence:
        raise ValueError(f"ROW_NOT_FOUND {key}: p{page_no} /{spec['row']}/")
    if len(matches) > 1 and "occurrence" not in spec:
        raise ValueError(f"ROW_AMBIGUOUS {key}: p{page_no} /{spec['row']}/ matches {[m['label'] for m in matches]}; set occurrence or tighten regex")
    row = matches[occurrence - 1]
    col = spec["column"]
    found = [n for n in row["numbers"] if n["col"] == col]
    if not found:
        raise ValueError(f"COLUMN_BLANK_OR_MISSING {key}: row '{row['label']}' has no number in page column {col}; a blank cell is not a disclosed zero")
    cell = found[0]
    if re.fullmatch(r"[-−—]{1,2}", cell["printed"].strip()):
        raise ValueError(f"COLUMN_IS_DASH_PLACEHOLDER {key}: '-' means not applicable, not zero")
    printed = to_decimal(cell["printed"])
    if spec.get("unit", "元") != "元" or "sign" in spec:
        # The publication validator re-reads the printed cell and requires the
        # stored yuan string to appear there with its original sign.
        raise ValueError(f"STORE_PRINTED_YUAN_AS_IS {key}: keep the original sign and 元 unit; apply accounting signs with -1 coefficients in expressions")
    yuan = printed
    if spec.get("expect") is not None and to_decimal(str(spec["expect"])) != printed:
        raise ValueError(f"EXPECTED_VALUE_MISMATCH {key}: printed {cell['printed']}")
    issuer = ledger["issuer"]
    column_role = spec.get("source_column", "上期/期初" if spec.get("prior") else "本期/期末")
    if spec["type"] == "flow":
        period = issuer.get("flow_columns", {}).get(column_role) or (
            issuer["comparative_period"] if column_role == "上期/期初" else issuer["fiscal_period"])
    else:
        period = spec["period"]  # stocks need an explicit date, e.g. 2025-12-31
    fact = {"yuan": str(yuan), "label": spec["label"], "page": page_no,
            "type": spec["type"], "period": period, "scope": "consolidated",
            "classification": "DISCLOSED", "unit": "元", "currency": "CNY",
            "source_cells": [{"bbox": cell["bbox"], "printed": cell["printed"], "wrapped_number": bool(cell["wrapped"])}],
            "source_row_label": row["label"], "source_column": column_role}
    return fact


def cmd_facts(a) -> None:
    _, doc, ledger = open_source(a.code, a.period)
    spec = json.loads(Path(a.spec).read_text())
    built, errors = {}, []
    for key, s in spec.items():
        try:
            built[key] = build_fact(doc, ledger, key, s)
        except (ValueError, KeyError) as exc:
            errors.append(str(exc))
    for e in errors:
        print("FACT_FAIL", e, file=sys.stderr)
    if errors and not a.partial:
        sys.exit(2)
    ledger["facts"].update(built)
    (folder(a.code, a.period) / "source-ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
    print(f"FACTS_WRITTEN {len(built)} (errors {len(errors)})")


# ---------------------------------------------------------------- editorial manifest
def editorial_path(code: str, fiscal_period: str, period: str | None) -> Path:
    name = f"{code}.json" if not period else f"{code}-{period}.json"
    return ROOT / "research" / "editorial-20261113" / name


def cmd_editorial(a) -> None:
    """Build the profit-chain editorial manifest from the ledger + a small spec.

    The spec supplies only editorial decisions: revenue sources, stage terms,
    the primary question, takeaway/counter text and one role per figure.
    Facts, cells, hashes and notes are copied from the ledger and
    publication.json, never retyped.
    """
    base = folder(a.code, a.period)
    ledger = json.loads((base / "source-ledger.json").read_text())
    story = json.loads((base / "publication.json").read_text())
    spec = json.loads(Path(a.spec).read_text())
    issuer, source = ledger["issuer"], ledger["source"]
    used = {k for s in spec["stages"] for k, _ in s["terms"]}
    used |= {k for s in spec["stages"] for g in s["adjustments"] for k, _ in g["terms"]}
    used |= {k for g in spec["sources"] for k, _ in g["terms"]}
    facts = {}
    for k in sorted(used):
        f = ledger["facts"][k]
        cells = [{"bbox": c["bbox"], "printed": c["printed"], "original_number": f["yuan"], "unit_scale": "1",
                  "normalization": "SIGNED_ORIGINAL", "wrapped_number": c.get("wrapped_number", False)}
                 for c in f["source_cells"]]
        facts[k] = {"yuan": f["yuan"], "page": f["page"], "label": f["label"], "period": f["period"],
                    "source_kind": "ledger_typed", "classification": f["classification"], "source_cells": cells}
    comparatives = None
    if spec["editorial"].get("layout") == "PROFIT_CHAIN_LAYOUT_V2":
        # Margins and year-over-year come from the same issuer's prior-period source cells (fact key + "_prior").
        prior_facts = {}
        stage_keys = {k for s in spec["stages"] for k, _ in s["terms"]} | {k for s in spec["stages"] for g in s["adjustments"] for k, _ in g["terms"]}
        for k in sorted(stage_keys):
            f = ledger["facts"].get(k + "_prior")
            if f is None:
                sys.exit(f"LAYOUT_V2_NEEDS_PRIOR_FACT {k}_prior: add the comparative-period cell to the ledger")
            cells = [{"bbox": c["bbox"], "printed": c["printed"], "original_number": f["yuan"], "unit_scale": "1",
                      "normalization": "SIGNED_ORIGINAL", "wrapped_number": c.get("wrapped_number", False)} for c in f["source_cells"]]
            prior_facts[k + "_prior"] = {"yuan": f["yuan"], "page": f["page"], "label": f["label"], "period": f["period"],
                                         "source_kind": "ledger_typed", "classification": f["classification"], "source_cells": cells}
        comparatives = {"period": issuer["comparative_period"], "facts": prior_facts}
    roles = spec["figure_roles"]
    figures = []
    for i, fg in enumerate(story["figures"]):
        r = roles[fg["id"]]
        figures.append({"index": i, "id": fg["id"], "title": fg["question"], "role": r["role"],
                        "rationale": r["rationale"], "summary": r.get("summary", False), "focus": r.get("focus", [])})
    ed = dict(spec["editorial"])
    ed.update({"full_reconciliation": "REFERENCE_EXPANDABLE_NOT_PRIMARY", "human_review": "NOT_CHECKED", "figures": figures,
               "selection_rule": "QUESTION_MATERIALITY_COUNTERCASE_AND_NONREDUNDANCY_NOT_CHART_COUNT",
               "attention_standard": "正文主图贯通至归母；专题须有独立问题及重要性理由；全部原始行项在可展开核对层保留，不按图数评价研究深度。"})
    manifest = {"schema": "financials.editorial_profit_chain.v1", "issuer": a.code, "name": issuer.get("short") or issuer["name"],
                "period": issuer["fiscal_period"], **({"period_label": issuer["period_label"]} if issuer.get("period_label") else {}), "scope": "consolidated", "currency": "CNY", "unit": "元",
                "source_pdf": {"source_path": source["source_path"], "source_sha256": source["original_bytes_sha256"],
                               "physical_page_count": source["physical_pages_observed"], "topics": spec.get("topics", [])},
                "source_ledger": str((base / "source-ledger.json").relative_to(ROOT)), "facts": facts,
                "sources": spec["sources"], "stages": spec["stages"], "editorial": ed,
                "report_identity_page": source.get("issuer_identity_page", 1), "source_url": source["official_announcement"]}
    if comparatives:
        manifest["comparatives"] = comparatives
    out = editorial_path(a.code, issuer["fiscal_period"], a.period)
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print("EDITORIAL_MANIFEST_WRITTEN", out.relative_to(ROOT), "facts", len(facts), "figures", len(figures))


# ---------------------------------------------------------------- preflight
CAUSAL = re.compile(r"(导致|因为|由于|驱动了|得益于|主要原因是)")
HEDGE_OK = re.compile(r"(管理层|披露|原文|称|解释|可能|不能|不等于|假设|若|如果)")
REQUIRED_FIGURE_KEYS = ("id", "family", "nav", "question", "takeaway", "analysis", "counter", "identity", "eyebrow")


def lint(story: dict, expanded: dict | None = None) -> list[str]:
    """Editorial lint. Lengths are measured on the expanded text a reader sees;
    hand-typed numbers are detected on the authored text."""
    issues = []
    figs = story.get("figures", [])
    shown = {f["id"]: f for f in (expanded or story).get("figures", [])}
    if not 4 <= len(figs) <= 14:
        issues.append(f"FIGURE_COUNT_{len(figs)}: a full report usually needs 6-12 analytically distinct figures")
    families = {f.get("family") for f in figs}
    for need in ("signed_bridge",):
        if need not in families:
            issues.append("MISSING_SIGNED_BRIDGE: profit or cash formation needs a signed waterfall")
    questions = [f.get("question", "") for f in figs]
    if len(set(questions)) != len(questions):
        issues.append("DUPLICATE_FIGURE_QUESTION")
    for f in figs:
        for k in REQUIRED_FIGURE_KEYS:
            if not f.get(k):
                issues.append(f"FIGURE_{f.get('id')}_MISSING_{k}")
        q = f.get("question", "")
        if q and not q.endswith(("？", "?")):
            issues.append(f"FIGURE_{f.get('id')}_TITLE_NOT_A_QUESTION")
        q = shown.get(f.get("id"), f).get("question", q)
        if len(q) > 28:
            issues.append(f"FIGURE_{f.get('id')}_QUESTION_TOO_LONG_{len(q)}")
        if len(shown.get(f.get("id"), f).get("takeaway", "")) > 100:
            issues.append(f"FIGURE_{f.get('id')}_TAKEAWAY_TOO_LONG: answer in one sentence")
        for k in ("takeaway", "analysis"):
            s = f.get(k, "")
            if CAUSAL.search(s) and not HEDGE_OK.search(s):
                issues.append(f"FIGURE_{f.get('id')}_{k.upper()}_UNHEDGED_CAUSAL_CLAIM: cite the disclosure or call it accounting attribution")
        for text in (f.get("takeaway", ""), f.get("analysis", "")):
            if re.search(r"[0-9]+\.[0-9]+\s*(亿|%)", text) and "{{" not in text:
                issues.append(f"FIGURE_{f.get('id')}_HAND_TYPED_NUMBER: use a quantified_claims placeholder")
                break
    thesis = story.get("thesis", {}).get("body", "")
    if len(thesis) < 60:
        issues.append("THESIS_TOO_THIN: state a falsifiable company-specific judgement")
    essays = thesis + " ".join(e.get("title", "") + " ".join(e.get("paragraphs", [])) for e in story.get("essays", []))
    for term in ("替代解释", "下一"):
        if term not in essays:
            issues.append(f"ESSAY_MISSING_{term}: strongest alternative and next-disclosure falsifier are required")
    if len(story.get("notes", [])) < 6:
        issues.append("MATERIAL_NOTES_FEWER_THAN_6: review revenue, AR, inventory, CFO, debt/cash, nonrecurring at minimum")
    if len(story.get("metrics", [])) != 3:
        issues.append("HERO_METRICS_SHOULD_BE_3")
    return issues


def cmd_preflight(a) -> None:
    sys.path.insert(0, str(ROOT / "research" / "shared"))
    from source_publication import validate  # noqa: E402
    base = folder(a.code, a.period)
    ledger = json.loads((base / "source-ledger.json").read_text())
    story = json.loads((base / "publication.json").read_text())
    result = {"source_and_accounting": "NOT_RUN", "editorial_lint": []}
    try:
        result["source_and_accounting"] = validate(ledger, story)
    except (ValueError, KeyError) as exc:
        result["source_and_accounting"] = "FAIL " + str(exc)
    try:
        from source_publication import expand_claims  # noqa: E402
        result["editorial_lint"] = lint(story, expand_claims(story, ledger))
    except (ValueError, KeyError) as exc:
        result["editorial_lint"] = ["CLAIM_EXPANSION_FAILED " + str(exc)]
    used = set()
    blob = json.dumps(story, ensure_ascii=False)
    for k in ledger["facts"]:
        if re.search(r'"' + re.escape(k) + r'"', blob):
            used.add(k)
    result["facts_unused"] = sorted(set(ledger["facts"]) - used)[:40]
    result["editorial_manifest"] = editorial_path(a.code, ledger["issuer"]["fiscal_period"], a.period).exists()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    ok = isinstance(result["source_and_accounting"], dict) and not result["editorial_lint"] and result["editorial_manifest"]
    print("PREFLIGHT_PASS" if ok else "PREFLIGHT_NOT_READY")
    sys.exit(0 if ok else 1)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init"); i.add_argument("--code", required=True); i.add_argument("--pdf", required=True)
    i.add_argument("--url", required=True); i.add_argument("--name"); i.add_argument("--short"); i.add_argument("--route"); i.add_argument("--force", action="store_true")
    f = sub.add_parser("find"); f.add_argument("--code", required=True); f.add_argument("--statements", action="store_true"); f.add_argument("--text")
    s = sub.add_parser("scan"); s.add_argument("--code", required=True); s.add_argument("--page", type=int, required=True); s.add_argument("--all", action="store_true")
    x = sub.add_parser("facts"); x.add_argument("--code", required=True); x.add_argument("--spec", required=True); x.add_argument("--partial", action="store_true")
    q = sub.add_parser("preflight"); q.add_argument("--code", required=True)
    e = sub.add_parser("editorial"); e.add_argument("--code", required=True); e.add_argument("--spec", required=True)
    for sp in (i, f, s, x, q, e):
        sp.add_argument("--period", help="report period folder for a later period of an issuer, e.g. 20269M")
    a = p.parse_args(argv)
    {"init": cmd_init, "find": cmd_find, "scan": cmd_scan, "facts": cmd_facts, "preflight": cmd_preflight, "editorial": cmd_editorial}[a.cmd](a)


if __name__ == "__main__":
    main()
