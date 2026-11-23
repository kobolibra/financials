#!/usr/bin/env python3
"""Source intake CLI for any A-share periodic report (Q1 / H1 / 9M / FY).

It removes the slow, error-prone hand work of a new dossier without making
analytical decisions for the analyst:

  init       archive the original PDF, hash it, detect issuer/report type,
             extract page text and write a skeleton dossier folder
  find       list pages that contain statement titles or a search phrase
  scan       print every numeric row on a page with column index and bbox
  auto       company-agnostic: find the three consolidated statements, map every row to a
             canonical key (CAS 一般企业 / 银行 / 保险 / 证券 formats), read current and prior
             columns and the unit, run format-aware identities, list unmapped rows; --write
             merges the facts into the ledger (never overwrites a different existing value)
  facts      turn an explicit fact spec (page + row label + column) into
             source-ledger facts with exact PDF cell coordinates (notes, segments, anything
             outside the three statements)
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
import os
import re
import shutil
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = Path(__file__).resolve().parents[1]
NUMBER = re.compile(r"^([-−(（]?[0-9][0-9,]*(\.[0-9]+)?[)）]?%?|[-−—]{1,2})$")
FULL_NUMBER = re.compile(r"^[-−]?([0-9]{1,3}(,[0-9]{3})+|[0-9]+)(\.[0-9]+)?$")
REPORT_KIND = {"半年度": "H1", "中期": "H1", "年度": "FY", "第一季度": "Q1", "第三季度": "9M"}
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
    override = os.environ.get("FINANCIALS_DOSSIER_ROOT")
    directory = (ROOT / override).resolve() if override else ROOT / "research" / "issuers"
    if override and ROOT / "work" not in directory.parents and directory != ROOT / "work":
        sys.exit("FINANCIALS_DOSSIER_ROOT must be under the repository work directory")
    base = directory / code
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
    # A+H issuers put an HKEX disclaimer page first: read the first three pages for the report type.
    cover = "".join(squash(doc[i].get_text()) for i in range(min(3, len(doc))))
    match = re.search(r"(20[0-9]{2})年?(半年度|中期|第一季度|第三季度|年度)报告", cover)  # "2026年半年度报告" and "2026半年度报告"
    if not match:  # covers without a year ("中信证券半年度报告"): the running header of the next pages carries it
        cover = "".join(squash(doc[i].get_text()) for i in range(min(8, len(doc))))
        match = re.search(r"(20[0-9]{2})年?(半年度|中期|第一季度|第三季度|年度)报告", cover)
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
        audited = "审计意见见原件审计报告"
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
    ledger_path = base / "source-ledger.json"
    if getattr(a, "candidate", False):
        if a.period and a.period != ident["fiscal_period"]:
            sys.exit("DOSSIER_FOLDER_PERIOD_MISMATCH")
        if ledger_path.exists():
            existing = json.loads(ledger_path.read_text())
            if existing["source"]["original_bytes_sha256"] != sha or not existing["issuer"].get("offline_candidate"):
                sys.exit("CANDIDATE_DOSSIER_ALREADY_BOUND: use an unused period dossier")
    elif not a.url:
        sys.exit("SOURCE_URL_REQUIRED_FOR_CATALOG_PUBLICATION")
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
        if getattr(a, "candidate", False):
            issuer["offline_candidate"] = True
            if (version := getattr(a, "editorial_selection_version", None)) is not None:
                issuer["editorial_selection_version"] = version
            text = squash("".join(page.get_text() for page in list(doc)[:30]))
            issuer["restatement_review_required"] = (
                "调整前" in text and "调整后" in text
                and any(word in text for word in ("追溯调整", "重述")))
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


def join_accounting_parentheses(words):
    """Keep a detached closing parenthesis inside the amount's source cell."""
    result = []
    for word in words:
        glyph = word[4].strip()
        if result and glyph in (")", "）"):
            previous = result[-1]
            amount = previous[4].strip()
            opening = "(" if glyph == ")" else "（"
            if amount.startswith(opening) and FULL_NUMBER.fullmatch(amount[1:]) and 0 <= word[0] - previous[2] <= 2:
                result[-1] = (previous[0], min(previous[1], word[1]), word[2],
                              max(previous[3], word[3]), amount + glyph, previous[5])
                continue
        result.append(word)
    return result


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
        ws = join_accounting_parentheses(sorted(ws, key=lambda w: w[0]))
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
    scale = Decimal(str(spec.get("unit_scale", "1")))
    if scale not in (1, 1000, 10000, 1000000):
        raise ValueError(f"INVALID_SOURCE_UNIT_SCALE {key}")
    if spec.get("unit", "元") != "元" or "sign" in spec:
        # The publication validator re-reads the printed cell and requires the
        # stored yuan string to appear there with its original sign.
        raise ValueError(f"STORE_PRINTED_YUAN_AS_IS {key}: keep the original sign and 元 unit; apply accounting signs with -1 coefficients in expressions")
    yuan = printed * scale
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
    if "product" in spec or "measure" in spec:
        if not spec.get("product") or spec.get("measure") not in ("revenue", "cost"):
            raise ValueError("PRODUCT_SOURCE_TAGS_REQUIRED " + key)
        fact.update(product=spec["product"], measure=spec["measure"])
    if spec.get("denominator_definition"):
        fact["denominator_definition"] = spec["denominator_definition"]
    if scale != 1 or cell["printed"].startswith(("(", "（")):
        fact["source_cells"][0]["unit_scale"] = str(scale)
    return fact


def cmd_basis(a) -> None:
    """Bind each reviewed comparative to a source page and, if restated, to its original value."""
    _, doc, ledger = open_source(a.code, a.period)
    from comparison_basis import require_pair
    rules = json.loads(Path(a.spec).read_text())
    for key, entry in rules.items():
        status = entry["status"]
        if status not in ("unchanged", "restated", "unconfirmed"):
            raise ValueError("UNKNOWN_COMPARISON_BASIS " + key)
        if (not entry.get("reason") or not entry.get("evidence_pages")
                or any(type(p) is not int or not 1 <= p <= len(doc) for p in entry["evidence_pages"])):
            raise ValueError("COMPARISON_REVIEW_PAGE_OR_REASON_REQUIRED " + key)
        rule = {k: entry[k] for k in ("status", "reason", "evidence_pages")}
        if status == "restated":
            oldkey = key + "_original"
            archive_spec = entry["original"]
            external = archive_spec.get("external")
            archive_doc = doc
            if external:
                base = folder(a.code, a.period)
                path = (base / "source" / external["filename"]).resolve()
                path.relative_to((base / "source").resolve())
                if hashlib.sha256(path.read_bytes()).hexdigest() != external["sha256"]:
                    raise ValueError("COMPARISON_ORIGINAL_BYTES_DRIFT " + key)
                archive_doc = pymupdf().open(path)
                expected_period = ledger["issuer"]["comparative_period"]
                if detect_identity(archive_doc, a.code)["fiscal_period"] != expected_period:
                    raise ValueError("COMPARISON_ARCHIVE_PERIOD_MISMATCH " + key)
                evidence = {**external, "path": str(path.relative_to(ROOT)), "period": expected_period,
                            "physical_pages": len(archive_doc), "printed_column": "本期/期末"}
            original = build_fact(archive_doc, ledger, oldkey, {**archive_spec, "prior": True})
            if external:
                original["archival_source"] = evidence
            original["disclosure_version"] = "original_before_restatement"
            ledger["facts"][oldkey] = original
            ledger["facts"][key + "_prior"]["disclosure_version"] = "restated"
            rule["original_fact"] = oldkey
        ledger.setdefault("comparison_basis", {})[key] = rule
        if status != "unconfirmed":
            require_pair(ledger, key, key + "_prior")
    (folder(a.code, a.period) / "source-ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")


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


def cmd_coverage(a) -> None:
    base = folder(a.code, a.period)
    path = base / "source-ledger.json"
    ledger = json.loads(path.read_text())
    review = ledger["unmapped_review"]
    if not a.spec:
        print(json.dumps(review, ensure_ascii=False, indent=2))
        return
    spec = json.loads(Path(a.spec).read_text())
    if spec["source_sha256"] != review["source_sha256"]:
        raise ValueError("UNMAPPED_REVIEW_SOURCE_DRIFT")
    records = {row["id"]: row for row in review["items"]}
    for ident, item in spec["decisions"].items():
        row = records[ident]
        classification = item["classification"]
        if classification not in ("DUPLICATE_SUBTOTAL", "NON_AMOUNT", "COVERED", "NONMATERIAL", "MATERIAL_OMISSION", "PENDING"):
            raise ValueError("UNMAPPED_REVIEW_CLASSIFICATION " + ident)
        if not all(item.get(field) for field in ("reviewer", "date", "reason", "affected_conclusions")):
            raise ValueError("UNMAPPED_REVIEW_EVIDENCE_REQUIRED " + ident)
        if classification in ("MATERIAL_OMISSION", "PENDING") and not item.get("affected_keys"):
            raise ValueError("UNMAPPED_REVIEW_AFFECTED_KEYS_REQUIRED " + ident)
        row.update(classification=classification, materiality=classification, review_evidence=item)
    path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")


def cmd_auto(a) -> None:
    import statement_extract as se
    _, doc, ledger = open_source(a.code, a.period)
    result = se.extract(doc, rows_on_page, squash)
    ok, bad = se.identities(result)
    facts = se.to_ledger_facts(result, ledger["issuer"])
    import notes_extract as ne
    note_facts, segments, partition, notes_report = ne.extract_notes(doc, rows_on_page, squash, se.unit_of, se.norm, facts)
    facts.update({k: f for k, f in note_facts.items() if k not in facts})
    conflicts = [k for k, f in facts.items() if k in ledger["facts"] and Decimal(ledger["facts"][k]["yuan"]) != Decimal(f["yuan"])]
    report = {"format": result["format"], "sign_convention": result["convention"], "pages": result["pages"],
              "mapped_keys": len(result["facts"]), "facts": len(facts), "identities_passed": len(ok), "identities_failed": bad,
              "unmapped_rows": [f"{u['statement']} p{u['page']} {u['label']} = {u['current']}" for u in result["unmapped"]],
              "conflicts_with_existing_ledger": conflicts, "notes": result["notes"],
              "source_anomalies": result.get("source_anomalies", []), "notes_tables": notes_report}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if bad:
        print("AUTO_IDENTITY_RESIDUAL: a residual means a line item was missed or mis-signed; inspect the unmapped rows of that "
              "statement and add a synonym to statement_extract.CANON (with a regression test), never a company-specific patch", file=sys.stderr)
    if conflicts:
        sys.exit("AUTO_CONFLICTS_WITH_EXISTING_LEDGER " + " ".join(conflicts))
    if a.write:
        if not result["facts"]:
            sys.exit("AUTO_NOT_WRITTEN: no consolidated statement facts found")
        if bad and not a.allow_residual:
            sys.exit("AUTO_NOT_WRITTEN: identities must close first (or pass --allow-residual and record why)")
        ledger["facts"].update({k: f for k, f in facts.items() if k not in ledger["facts"]})
        ledger["issuer"]["statement_format"] = result["format"]
        if ledger["issuer"].get("offline_candidate"):
            from coverage_review import unmapped_review_items
            sha = ledger["source"]["original_bytes_sha256"]
            items = unmapped_review_items(result["unmapped"], sha)
            previous = ledger.get("unmapped_review", {})
            reviewed = {row["id"]: row for row in previous.get("items", [])} if previous.get("source_sha256") == sha else {}
            ledger["unmapped_review"] = {"source_sha256": sha, "items": [reviewed.get(row["id"], row) for row in items]}
        if partition and not ledger.get("segments"):
            ledger["segments"], ledger["income_partition"] = segments, partition
        (folder(a.code, a.period) / "source-ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
        print("AUTO_FACTS_WRITTEN", len(facts))


# ---------------------------------------------------------------- editorial manifest
def editorial_path(code: str, fiscal_period: str, period: str | None) -> Path:
    name = f"{code}.json" if not period else f"{code}-{period}.json"
    candidate = folder(code, period) / "editorial-manifest.json"
    if candidate.exists():
        return candidate
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
    if spec["editorial"].get("layout") in ("PROFIT_CHAIN_LAYOUT_V2", "INCOME_FLOW_V3"):
        # Margins and year-over-year come from the same issuer's prior-period source cells (fact key + "_prior").
        prior_facts = {}
        stage_keys = {k for s in spec["stages"] for k, _ in s["terms"]} | {k for s in spec["stages"] for g in s["adjustments"] for k, _ in g["terms"]}
        for k in sorted(stage_keys):
            f = ledger["facts"].get(k + "_prior")
            if f is None:
                # a blank comparative cell: the renderer omits that annotation, the auditor expects none
                print(f"NOTE_NO_PRIOR_CELL {k}_prior: annotation omitted", file=sys.stderr)
                continue
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


def lint(story: dict, expanded: dict | None = None, roles: dict | None = None,
         capabilities: dict | None = None) -> list[str]:
    """Editorial lint. Lengths are measured on the expanded text a reader sees;
    hand-typed numbers are detected on the authored text."""
    issues = []
    figs = story.get("figures", [])
    shown = {f["id"]: f for f in (expanded or story).get("figures", [])}
    candidate = story.get("composition") == "OFFLINE_RESEARCH_CANDIDATE_V1"
    if not (1 if candidate else 4) <= len(figs) <= 14:
        issues.append(f"FIGURE_COUNT_{len(figs)}: a full report usually needs 6-12 analytically distinct figures")
    families = {f.get("family") for f in figs}
    for need in ("signed_bridge",):
        if need not in families and not candidate:
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
    if len(story.get("notes", [])) < (1 if candidate else 6):
        issues.append("MATERIAL_NOTES_FEWER_THAN_6: review revenue, AR, inventory, CFO, debt/cash, nonrecurring at minimum")
    if len(story.get("metrics", [])) != 3 and not candidate:
        issues.append("HERO_METRICS_SHOULD_BE_3")
    if story.get("design") == "EDITORIAL_V2":
        issues += lint_v2(figs, roles, capabilities, candidate=candidate)
    return issues


TREND_FAMILIES = {"period_columns", "ratio_dumbbell", "growth_bars"}


def lint_v2(figs, roles=None, capabilities=None, *, candidate=False) -> list:
    """V2 editorial audit: preserve legacy receipts, but make new figure choices evidence-led.

    A chart family is not a goal. For new source-bound reports, reject families whose
    actual source proof is absent and require independent research relationships.
    Legacy published dossiers retain their original five-family editorial test until
    they are explicitly regenerated with the auditable research capability contract.
    """
    issues = []
    fams = [f.get("family") for f in figs]
    if not candidate and (not figs or fams[0] != "kpi_board"):
        issues.append("V2_FIRST_FIGURE_MUST_BE_KPI_BOARD: open with the at-a-glance numbers")
    if capabilities is None:
        if len(set(fams)) < 5:
            issues.append(f"V2_FAMILY_VARIETY_{len(set(fams))}: use at least 5 distinct exhibit families")
        if not TREND_FAMILIES & set(fams):
            issues.append("V2_NO_TREND_EXHIBIT: add quarterly columns, a margin dumbbell or growth bars")
    else:
        if (capabilities.get("schema") != "financials.research_capabilities.v1"
                or capabilities.get("publication_route") not in ("INDUSTRIAL_V2_AUTHORING_CANDIDATE", "BANK_V2_AUTHORING_CANDIDATE")):
            issues.append("V2_UNVERIFIED_SECTOR_OR_SOURCE_CAPABILITY")
        status = {v["family"]: v["status"] for v in capabilities.get("visual_candidates", [])}
        for f in figs:
            family = f.get("family")
            if (family in status
                    and status[family] != "ELIGIBLE_PENDING_SOURCE_AND_VISUAL_AUDIT"):
                issues.append(f"V2_SOURCE_INELIGIBLE_FIGURE_{f.get('id')}:{family}")
        # Distinct research relationships are a minimum quality requirement, not
        # a demand to manufacture five graphic types from absent evidence.
        if not candidate and len(set(fams)) < 3:
            issues.append("V2_SOURCE_LIMITED_RELATIONSHIPS: fewer than three distinct audited financial views")
        # Omit trends when no comparable single-period or ratio evidence exists.
        # An eligible trend is a candidate, not a mandate to draw a redundant chart.
    # body = figures the editorial manifest keeps in the main reading layer (all figures when roles are unknown)
    body = [f for f in figs if (roles or {}).get(f.get("id")) != "reference"]
    bridges = sum(1 for f in body if f.get("family") == "signed_bridge")
    if bridges > 2 or (not candidate and bridges * 2 > len(body)):
        issues.append(f"V2_BRIDGE_PARADE_{bridges}: keep at most 2 signed bridges in the body; move the rest to reference")
    if not candidate and sum(1 for f in figs if f.get("chapter")) < 3:
        issues.append("V2_TOO_FEW_CHAPTERS: group figures into 3-4 themed takeaways")
    for f in figs:
        ch = f.get("chapter")
        if ch and not all(ch.get(k) for k in ("kicker", "title", "summary")):
            issues.append(f"V2_FIGURE_{f.get('id')}_CHAPTER_INCOMPLETE")
    return issues


def cmd_preflight(a) -> None:
    sys.path.insert(0, str(ROOT / "research" / "shared"))
    from source_publication import validate  # noqa: E402
    base = folder(a.code, a.period)
    ledger = json.loads((base / "source-ledger.json").read_text())
    story = json.loads((base / "publication.json").read_text())
    result = {"source_and_accounting": "NOT_RUN", "editorial_lint": [],
              "research_evidence": "NOT_CHECKED_LEGACY", "source_capability": "NOT_CHECKED_LEGACY"}
    capabilities = None
    if story.get("design") == "EDITORIAL_V2":
        if story.get("research_evidence_gate") is not None:
            try:
                import research_evidence as ev
                import research_capabilities as rc
                path = base / "research-brief.json"
                review = ev.validate_file(ledger, path)
                capabilities = rc.assess(ledger)
                expected = {
                    "status": review["status"],
                    "brief_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "source_pdf_sha256": review["source_pdf_sha256"],
                    "professional_causal_inference": review["professional_causal_inference"],
                    "independent_financial_reviewer": review["independent_financial_reviewer"],
                    "independent_visual_editor": review["independent_visual_editor"],
                    "release_authorization": review["release_authorization"],
                }
                if story["research_evidence_gate"] != expected:
                    raise ValueError("RESEARCH_EVIDENCE_RECEIPT_NOT_CURRENT")
                if story.get("capability_plan") != capabilities:
                    raise ValueError("CAPABILITY_PLAN_NOT_CURRENT_LEDGER")
                result["research_evidence"] = "PASS_MACHINE_PROOF_ONLY_HUMAN_NOT_CHECKED"
                result["source_capability"] = capabilities["publication_route"]
            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                result["research_evidence"] = "FAIL " + str(exc)
        elif getattr(a, "require_research_evidence", False):
            result["research_evidence"] = "FAIL NEW_V2_RESEARCH_BRIEF_REQUIRED"
    elif getattr(a, "require_research_evidence", False):
        result["research_evidence"] = "FAIL RESEARCH_GATE_ONLY_DEFINED_FOR_EDITORIAL_V2"
    try:
        result["source_and_accounting"] = validate(ledger, story)
    except (ValueError, KeyError) as exc:
        result["source_and_accounting"] = "FAIL " + str(exc)
    try:
        from source_publication import expand_claims  # noqa: E402
        mpath = editorial_path(a.code, ledger["issuer"]["fiscal_period"], a.period)
        roles = {f["id"]: f.get("role") for f in json.loads(mpath.read_text())["editorial"]["figures"]} if mpath.exists() else None
        result["editorial_lint"] = lint(story, expand_claims(story, ledger), roles,
                                        capabilities=capabilities)
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
    ok = (isinstance(result["source_and_accounting"], dict)
          and not result["editorial_lint"] and result["editorial_manifest"]
          and not result["research_evidence"].startswith("FAIL"))
    print("PREFLIGHT_PASS" if ok else "PREFLIGHT_NOT_READY")
    sys.exit(0 if ok else 1)


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init"); i.add_argument("--code", required=True); i.add_argument("--pdf", required=True)
    i.add_argument("--candidate", action="store_true"); i.add_argument("--url"); i.add_argument("--name"); i.add_argument("--short"); i.add_argument("--route"); i.add_argument("--force", action="store_true")
    f = sub.add_parser("find"); f.add_argument("--code", required=True); f.add_argument("--statements", action="store_true"); f.add_argument("--text")
    s = sub.add_parser("scan"); s.add_argument("--code", required=True); s.add_argument("--page", type=int, required=True); s.add_argument("--all", action="store_true")
    x = sub.add_parser("facts"); x.add_argument("--code", required=True); x.add_argument("--spec", required=True); x.add_argument("--partial", action="store_true")
    cv = sub.add_parser("coverage"); cv.add_argument("--code", required=True); cv.add_argument("--spec")
    b = sub.add_parser("basis"); b.add_argument("--code", required=True); b.add_argument("--spec", required=True)
    q = sub.add_parser("preflight"); q.add_argument("--code", required=True)
    q.add_argument("--require-research-evidence", action="store_true",
                   help="strict for new V2 editions; legacy reports retain explicit NOT_CHECKED status")
    e = sub.add_parser("editorial"); e.add_argument("--code", required=True); e.add_argument("--spec", required=True)
    au = sub.add_parser("auto"); au.add_argument("--code", required=True); au.add_argument("--write", action="store_true")
    au.add_argument("--allow-residual", action="store_true")
    for sp in (i, f, s, x, b, cv, q, e, au):
        sp.add_argument("--period", help="report period folder for a later period of an issuer, e.g. 20269M")
    a = p.parse_args(argv)
    {"init": cmd_init, "find": cmd_find, "scan": cmd_scan, "facts": cmd_facts, "basis": cmd_basis, "coverage": cmd_coverage, "preflight": cmd_preflight, "editorial": cmd_editorial, "auto": cmd_auto}[a.cmd](a)


if __name__ == "__main__":
    main()
