#!/usr/bin/env python3
"""Fail-closed, source-typed V10 financial-flow publication contract.

Checks the actual committed issuer ledgers and the exact published figure-02
HTML bytes. A conserved group Sankey is NOT evidence of product gross profit.
This static gate never certifies source PDF row/column identity, browser
legibility, ribbon geometry, editorial quality, or an independent human review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research/shared"))
from editorial_financial_flow import FinanceFact, assess_financial_income_flow

CODES = ("688111", "600519", "000333", "600036")
SOURCES = {
    "688111": ("wps_personal", "wps365", "wps_software", "other_rev"),
    "600519": ("maotai_rev", "series_rev", "other_rev"),
    "000333": ("home", "industrial_solution", "other_total"),
    "600036": ("nii", "fees_net", "other_net"),
}
COSTS = {
    "688111": ("wps_personal_cost", "wps365_cost", "wps_software_cost", "other_cost"),
    "600519": ("maotai_cogs", "series_cogs", "other_cogs"),
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _raw(root: Path, code: str) -> dict:
    if code == "600036":
        extras = json.loads((root / "research/rebuild-v10/extras.json").read_text(encoding="utf8"))
        return {
            k: {"yuan": v["val"], "page": v["page"], "period": "2026H1"}
            for k, v in extras[code].items()
            if isinstance(v, dict) and "val" in v and "page" in v
        }
    data = json.loads(
        (root / "research/rebuild-v10/input-ledgers" / (code + ".json")).read_text(encoding="utf8")
    )
    return data["facts"]


def _fact(code: str, rows: dict, key: str, statement: str) -> FinanceFact:
    row = rows[key]
    if row.get("period", "2026H1") != "2026H1":
        raise ValueError("NON_2026H1_FACT " + code + "/" + key)
    if row.get("scope", "consolidated") != "consolidated":
        raise ValueError("NON_CONSOLIDATED_FACT " + code + "/" + key)
    return FinanceFact(
        id=key, yuan=str(row["yuan"]), issuer=code,
        period="2026H1", statement=statement, scope="consolidated",
        currency="CNY", source_page=int(row["page"]),
        group_axis="exclusive_issuer_business", hierarchy_level="top",
    )


def _assert_yuan_equal(a, b, message: str):
    from decimal import Decimal
    if Decimal(str(a)) != Decimal(str(b)):
        raise ValueError(message + " " + str(Decimal(str(a)) - Decimal(str(b))))


def classify(root: Path, code: str) -> dict:
    """Compute expected published grammar from exact-yuan committed facts."""
    if code not in CODES:
        raise ValueError("NOT_A_V10_ISSUER " + code)
    rows = _raw(root, code)
    from decimal import Decimal as D
    if code == "600036":
        # Bank net interest is ALREADY net of interest expense; a second
        # deduction in an industrial revenue/COGS/gross-profit flow is false.
        def v(key):
            return D(str(rows[key]["yuan"]))
        _assert_yuan_equal(v("interest_in") - v("interest_out"), v("nii"),
                           "BANK_NET_INTEREST_FALSE")
        _assert_yuan_equal(sum((v(k) for k in SOURCES[code]), D(0)),
                           v("revenue"), "BANK_NET_REVENUE_FALSE")
        expense_keys = ("administrative_expense", "credit_impairment_expense",
                        "other_operating_cost")
        _assert_yuan_equal(v("revenue") - sum((v(k) for k in expense_keys), D(0)),
                           v("operating_profit"), "BANK_OPERATING_PROFIT_FALSE")
        return {
            "kind": "BANK_NET_INCOME_TO_OPERATING_PROFIT",
            "reason": "BANK_NET_INTEREST_ALREADY_AFTER_INTEREST_EXPENSE",
            "source_keys": list(SOURCES[code]),
            "expense_keys": list(expense_keys),
            "exact_yuan_total": str(v("revenue")),
            "exact_yuan_result": str(v("operating_profit")),
            "product_gp_claim_allowed": False,
        }
    src = [_fact(code, rows, key, "operating_revenue") for key in SOURCES[code]]
    total = _fact(code, rows, "rev", "operating_revenue")
    cogs = _fact(code, rows, "cogs", "operating_revenue")
    own = None
    if code in COSTS:
        own = {src_key: _fact(code, rows, cost_key, "operating_revenue")
               for src_key, cost_key in zip(SOURCES[code], COSTS[code])}
    decision = assess_financial_income_flow(
        src, total, cogs, costs_by_source=own,
        individual_costs_disclosed=own is not None,
    )
    return {
        "kind": decision.kind,
        "reason": decision.reason,
        "source_keys": list(SOURCES[code]),
        "exact_yuan_total": decision.exact_yuan_total,
        "exact_yuan_cogs": decision.exact_yuan_group_cost,
        "exact_yuan_group_gp": decision.exact_yuan_group_gp,
        "source_own_cost_gp": [list(t) for t in decision.source_own_cost_gp],
        "product_gp_claim_allowed": decision.kind == "TYPE_A_SOURCE_OWN_COST_GP",
    }


def _figure_two(text: str) -> str:
    m = re.search(r'<figure\b[^>]*\bid="fig-02"[^>]*>.*?</figure>', text, re.I | re.S)
    if not m:
        raise ValueError("EXHIBIT_02_INDEPENDENT_FIGURE_MISSING")
    return m.group(0)


def inspect_published_figure(code: str, expected: dict, figure_html: str) -> list[str]:
    """A future upgraded renderer must supply *visible* provenance claims.

    These are static preconditions, not substitutes for genuine source-bound
    Playwright/Chromium SVG path/width/text and human art-direction tests.
    """
    kind = expected["kind"]
    issues = []
    visible = re.sub(r"<details\b.*?</details>", "", figure_html, flags=re.I | re.S)
    marker = 'data-flow-kind="' + kind + '"'
    if marker not in figure_html:
        issues.append("FLOW_TYPE_NOT_SERIALIZED_IN_PUBLISHED_FIGURE")
    sankey = bool(re.search(r"sankey-svg|会计守恒财务桑基图", figure_html))
    if kind == "TYPE_A_SOURCE_OWN_COST_GP":
        if not sankey:
            issues.append("SOURCE_OWN_COST_GP_REQUIRES_TRUE_PER_PRODUCT_FLOW")
        for sid, revenue, cost, gp in expected["source_own_cost_gp"]:
            pattern = (r'<[^>]+\bdata-source-id="' + re.escape(sid) +
                       r'"[^>]+\bdata-revenue-yuan="' + re.escape(revenue) +
                       r'"[^>]+\bdata-cost-yuan="' + re.escape(cost) +
                       r'"[^>]+\bdata-gp-yuan="' + re.escape(gp) + r'"')
            if not re.search(pattern, figure_html):
                issues.append("SOURCE_OWN_COST_GP_PATH_OR_SOURCE_METADATA_MISSING:" + sid)
    elif kind == "TYPE_B_GROUP_ONLY_GROSS_ALLOCATION":
        if not sankey:
            issues.append("GROUP_GROSS_ALLOCATION_FIGURE_MISSING")
        if "PRODUCT_LEVEL_GP_NOT_ESTABLISHED" not in visible:
            issues.append("GROUP_ONLY_NO_VISIBLE_PRODUCT_GP_LIMITATION")
    elif kind == "TYPE_C_SANKEY_OMITTED":
        if sankey:
            issues.append("NEGATIVE_PRODUCT_GP_ILLEGAL_POSITIVE_SANKEY")
        if "FINANCIAL_SANKEY_OMITTED_WITH_SOURCE_REASON" not in visible:
            issues.append("MISSING_SOURCE_BASED_SIGNED_ALTERNATIVE_DISCLOSURE")
        if expected["reason"] not in visible:
            issues.append("MISSING_TYPED_OMISSION_REASON")
    elif kind == "BANK_NET_INCOME_TO_OPERATING_PROFIT":
        if not sankey:
            issues.append("BANK_NET_REVENUE_TO_PROFIT_FIGURE_MISSING")
        if "银行" not in visible and "净利息" not in visible:
            issues.append("BANK_ACCOUNTING_NOT_VISIBLE")
        if "毛利" in visible:
            issues.append("BANK_FALSE_INDUSTRIAL_GROSS_PROFIT_LABEL")
    else:
        issues.append("UNKNOWN_FLOW_TYPE")
    return issues


def audit(root: Path = ROOT, *, strict: bool = False) -> dict:
    catalog = json.loads((root / "site/research_catalog.json").read_text(encoding="utf8"))
    hrefs = {r["code"]: r["href"] for r in catalog["issuers"]}
    frozen = json.loads((root / "research/visual-audit/quality-debt.json").read_text(encoding="utf8"))
    frozen = frozen["legacy_source_frozen_allowlist_for_preexisting_only"]
    results, violations = [], []
    for code in CODES:
        expected = classify(root, code)
        path = root / "public" / hrefs[code].lstrip("/")
        data = path.read_bytes()
        source_hash = _sha(data)
        figure = _figure_two(data.decode("utf8"))
        issues = inspect_published_figure(code, expected, figure)
        historical = bool(issues and source_hash == frozen.get(code))
        if issues and (strict or not historical):
            violations.append({"issuer": code, "reason": issues,
                               "source_sha256": source_hash})
        results.append({
            "issuer": code, "actual_html_sha256": source_hash,
            "expected_semantics": expected, "published_figure_issues": issues,
            "historical_exact_source_waiver": historical,
            "current_figure_semantic_status": "FAIL" if issues else "PASS_STATIC_SCOPE_ONLY",
            "actual_source_pdf_row_and_column": "NOT_CHECKED",
            "actual_1440_768_390_chromium": "NOT_CHECKED",
            "actual_svg_path_geometric_widths": "NOT_CHECKED",
            "independent_human_editorial_review": "NOT_CHECKED",
        })
    return {
        "schema": "financials.v10.typed_flow_published_contract.v1",
        "scope": "Four real published V10 issuer EXHIBIT 02 HTML bytes and committed source ledger",
        "count": len(results),
        "strict": strict,
        "records": results,
        "blocking_violations": violations,
        "conclusion": ("FAIL" if violations else
            "KNOWN_HISTORICAL_FLOW_DEBT_NOT_CERTIFIED" if any(r["published_figure_issues"] for r in results)
            else "STATIC_SCOPE_PASS_BROWSER_GEOMETRY_AND_HUMAN_NOT_CHECKED"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--strict", action="store_true",
                        help="Reject every old defect, including SHA-frozen historical four")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = audit(args.root, strict=args.strict)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf8")
    print(payload)
    return 1 if report["blocking_violations"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
