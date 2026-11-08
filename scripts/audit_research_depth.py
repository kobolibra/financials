#!/usr/bin/env python3
"""Source-bound quantitative RESEARCH gate, not a claim of causal inference.

Four PR35 2026H1 cases are deliberate falsifiable worked examples. Values are
recomputed from immutable original-PDF-backed ledgers with Decimal, rather
than trusting editorial prose, a screenshot or a manually typed answer.
"""
from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CODES = ("688111", "600519", "000333", "600036")
MODELS = {
    "688111": ("GROSS_PROFIT_YOY_CHANGE", "ledger",
               ("rev", "cogs", "rev_prior", "cogs_prior")),
    "600519": ("OPERATING_CASH_YOY_CHANGE", "ledger",
               ("cfo", "cfo_prior")),
    "000333": ("PARENT_VS_DEDUCTED_YOY_DIVERGENCE", "ledger",
               ("parent_ni", "parent_ni_prior", "reg_ni", "reg_ni_prior")),
    "600036": ("BANK_NET_INTEREST_YOY_BRIDGE", "extras",
               ("interest_in", "interest_in_prior", "interest_out",
                "interest_out_prior", "nii", "nii_prior")),
}


def number(value):
    if not isinstance(value, str) or not re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value):
        raise ValueError("MONEY_MUST_BE_EXACT_DECIMAL_STRING")
    n = Decimal(value)
    if not n.is_finite():
        raise ValueError("NON_FINITE_AMOUNT")
    return n


def calculate(kind, values):
    v = values
    if kind == "GROSS_PROFIT_YOY_CHANGE":
        return (v["rev"] - v["cogs"]) - (v["rev_prior"] - v["cogs_prior"])
    if kind == "OPERATING_CASH_YOY_CHANGE":
        return v["cfo"] - v["cfo_prior"]
    if kind == "PARENT_VS_DEDUCTED_YOY_DIVERGENCE":
        return ((v["parent_ni"] - v["parent_ni_prior"])
                - (v["reg_ni"] - v["reg_ni_prior"]))
    if kind == "BANK_NET_INTEREST_YOY_BRIDGE":
        if (v["interest_in"] - v["interest_out"] != v["nii"]
                or v["interest_in_prior"] - v["interest_out_prior"] != v["nii_prior"]):
            raise ValueError("BANK_INTEREST_ACCOUNTING_BRIDGE_MISMATCH")
        return ((v["interest_in"] - v["interest_in_prior"])
                - (v["interest_out"] - v["interest_out_prior"]))
    raise ValueError("UNSUPPORTED_FORMULA")


def validate(briefs, ledgers, extras, manifest):
    issues = []
    rows = briefs.get("hero_figures", [])
    if briefs.get("schema") != "financials.editorial_hero_briefs.v1":
        issues.append("RESEARCH_BRIEF_SCHEMA")
    ids = [row.get("issuer") for row in rows if isinstance(row, dict)]
    if len(ids) != len(CODES) or len(set(ids)) != len(CODES) or set(ids) != set(CODES):
        issues.append("RESEARCH_ISSUER_SCOPE_MISMATCH")
    by_code = {row["issuer"]: row for row in rows if isinstance(row, dict) and "issuer" in row}
    source_checks = {item["ticker"]: item for item in manifest.get("source_check", [])}
    for code in CODES:
        formula, source_kind, keys = MODELS[code]
        brief = by_code.get(code, {}).get("quantified_driver")
        if not isinstance(brief, dict):
            issues.append("MISSING_QUANTIFIED_DECISION_DRIVER_" + code)
            continue
        if (brief.get("formula") != formula
                or brief.get("evidence_source") != source_kind
                or brief.get("fact_keys") != list(keys)):
            issues.append("WRONG_QUANTIFIED_FORMULA_OR_FACT_KEYS_" + code)
            continue
        source = source_checks.get(code, {})
        pdf_sha = source.get("sha256")
        if not isinstance(pdf_sha, str) or not re.fullmatch("[0-9a-f]{64}", pdf_sha):
            issues.append("MISSING_ORIGINAL_PDF_SHA_" + code)
            continue
        if brief.get("source_pdf_sha256") != pdf_sha:
            issues.append("RESEARCH_PDF_SHA_DRIFT_" + code)
        if code != "600036" and ledgers[code].get("source", {}).get("pdf_sha256") != pdf_sha:
            issues.append("RESEARCH_LEDGER_MANIFEST_PDF_CONFLICT_" + code)
        raw = (ledgers[code].get("facts", {}) if source_kind == "ledger"
               else extras.get(code, {}))
        values = {}
        pages = set()
        for key in keys:
            fact = raw.get(key)
            if not isinstance(fact, dict):
                issues.append("RESEARCH_FACT_ABSENT_" + code + "_" + key)
                continue
            try:
                values[key] = number(fact.get("yuan") if source_kind == "ledger" else fact.get("val"))
            except (ValueError, InvalidOperation):
                issues.append("RESEARCH_INVALID_EXACT_AMOUNT_" + code + "_" + key)
            page = fact.get("page")
            if type(page) is not int or not (1 <= page <= source.get("pdf_pages", 10000)):
                issues.append("RESEARCH_ORIGINAL_PHYSICAL_PAGE_MISSING_" + code + "_" + key)
            else:
                pages.add(page)
            if source_kind == "ledger":
                if fact.get("scope") != "consolidated" or fact.get("status") != "DISCLOSED":
                    issues.append("RESEARCH_UNDISCLOSED_OR_WRONG_CONSOLIDATION_" + code + "_" + key)
                expected_period = "2025H1" if key.endswith("_prior") else "2026H1"
                if fact.get("period") != expected_period:
                    issues.append("RESEARCH_PERIOD_COLUMN_DRIFT_" + code + "_" + key)
        if brief.get("physical_pdf_pages") != sorted(pages):
            issues.append("RESEARCH_PHYSICAL_PAGE_TRACE_MISMATCH_" + code)
        if len(values) == len(keys):
            try:
                actual = calculate(formula, values)
                if actual != number(brief.get("expected_yuan")):
                    issues.append("RESEARCH_QUANTIFIED_BRIDGE_NOT_RECONCILED_" + code)
            except (ValueError, InvalidOperation):
                issues.append("RESEARCH_ACCOUNTING_FORMULA_INVALID_" + code)
        if brief.get("unit") != "CNY_YUAN":
            issues.append("RESEARCH_ARITHMETIC_UNIT_MISMATCH_" + code)
        if brief.get("causality_status") != "ACCOUNTING_ARITHMETIC_ONLY_NOT_CAUSAL":
            issues.append("RESEARCH_UNSUPPORTED_CAUSAL_CERTIFICATION_" + code)
        if brief.get("independent_financial_review") != "NOT_CHECKED":
            issues.append("RESEARCH_FAKE_INDEPENDENT_REVIEW_" + code)
        for key in ("decision_use", "strongest_alternative", "next_disclosure_falsifier",
                    "scope_and_limitations"):
            value = brief.get(key)
            if not isinstance(value, str) or len(value.strip()) < 32:
                issues.append("RESEARCH_DECISION_CHAIN_INCOMPLETE_" + code + "_" + key)
    return issues


def audit_repo(root=ROOT):
    read = lambda p: json.loads((root / p).read_text(encoding="utf-8"))
    briefs = read("research/quality/pr35-hero-figure-briefs.json")
    ledgers = {c: read("research/rebuild-v10/input-ledgers/" + c + ".json")
               for c in CODES if c != "600036"}
    return validate(briefs, ledgers, read("research/rebuild-v10/extras.json"),
                    read("research/rebuild-v10/build-manifest.json"))


if __name__ == "__main__":
    try:
        errors = audit_repo()
    except (OSError, KeyError, ValueError) as exc:
        print("RESEARCH_DEPTH_INPUT_ERROR", repr(exc), file=sys.stderr)
        sys.exit(2)
    if errors:
        for issue in errors:
            print("RESEARCH_DEPTH_FAIL", issue, file=sys.stderr)
        sys.exit(1)
    print("RESEARCH_DEPTH_SOURCE_BOUND_ARITHMETIC_PASS",
          "4 issuer decisions / original PDF SHA / pages / periods / no causal or human certification")
