#!/usr/bin/env python3
"""Independent, pinned FY/Q1/9M original-PDF generalization benchmark.

This is deliberately NOT the historical 30-PDF result.json and cannot make the
missing 20 originals reappear. Existing tracked peer PDFs have *never* been
counted as 30/30 source reproductions by changing a denominator.

No company-specific extraction hints are passed to the three-statement,
footnote, signed-flow, or exhibit pipelines. The cohort is only a holdout input
selection with immutable Git blob IDs and expected period types.

Run:
  python scripts/check_independent_period_generalization.py --out /tmp/period-holdout.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import traceback
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generalization_probe as gp  # noqa: E402

# Different listed companies and previously under-tested fiscal periods.
# The Git blob hash freezes exact original bytes, NOT the accounting result.
HOLDOUTS = (
    {"path": "research/quality/historical-peer-evidence/600900_2025FY.pdf",
     "git_blob_sha1": "e77d1673c70279a4e21f0150722290de5b903adc",
     "fiscal_period": "2025FY", "industry_context": "utilities"},
    {"path": "research/quality/historical-peer-evidence/600276_2026Q1.pdf",
     "git_blob_sha1": "8c0088700a0b0193dd84005c3f513abe92ce84f6",
     "fiscal_period": "2026Q1", "industry_context": "pharmaceuticals"},
    {"path": "research/quality/historical-peer-evidence/688220_2026Q3.pdf",
     "git_blob_sha1": "d0dd38fca4607cc0e8f39de203cf3b78f197e1ea",
     "fiscal_period": "20269M", "industry_context": "semiconductors"},
)


def git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload).hexdigest()


def check_row(r: dict, expected: dict) -> list[str]:
    errors = []
    if r.get("crash"):
        return ["UNHANDLED_PROBE_EXCEPTION"]
    if r.get("fiscal_period") != expected["fiscal_period"]:
        errors.append("WRONG_REPORT_PERIOD")
    stages = r.get("stages", {})
    for name in ("ledger", "exhibits"):
        if not stages.get(name, "").startswith("PASS"):
            errors.append("FAIL_" + name.upper())
    income = stages.get("income_flow_v3", "")
    if income != "PASS" and not income.startswith("REFUSED_AS_DESIGNED→SIGNED_BRIDGE_PASS"):
        errors.append("FAIL_INCOME_FLOW_OR_AUDITED_SIGNED_FALLBACK")
    findings = stages.get("findings", "")
    if not (findings.startswith("PASS") or
            findings.startswith("REFUSED_AS_DESIGNED_SECTOR_RESEARCH_REQUIRED")):
        errors.append("FAIL_FINDINGS_OR_SUPPORTED_SECTOR_REFUSAL")
    business = stages.get("business_sankey", "")
    if not (business.startswith("PASS") or business.startswith("NOT_AVAILABLE")):
        errors.append("FAIL_SEGMENTED_SANKEY_OR_PROVEN_SOURCE_LIMITATION")
    if r.get("coverage_review", {}).get("status") != "NOT_CHECKED":
        errors.append("COVERAGE_REVIEW_MUST_NOT_AUTO_PASS")
    return errors


def run(cohort=HOLDOUTS):
    records = []
    for case in cohort:
        path = ROOT / case["path"]
        record = {"path": case["path"], "expected_period": case["fiscal_period"],
                  "git_blob_sha1_expected": case["git_blob_sha1"],
                  "business_model": case["industry_context"],
                  "materiality_review": "NOT_CHECKED",
                  "independent_human_finance_and_art_review": "NOT_CHECKED"}
        try:
            payload = path.read_bytes()
            actual_blob = git_blob_sha1(payload)
            record["git_blob_sha1_actual"] = actual_blob
            record["pdf_sha256"] = hashlib.sha256(payload).hexdigest()
            if actual_blob != case["git_blob_sha1"]:
                record["stage_errors"] = ["ORIGINAL_PDF_BYTES_CHANGED"]
            else:
                r = gp.probe(path)
                record.update(report=r)
                record["stage_errors"] = check_row(r, case)
        except Exception:  # noqa: BLE001
            record["stage_errors"] = ["UNHANDLED_INPUT_OR_PROBE_ERROR"]
            record["error_traceback"] = traceback.format_exc()[-1500:]
        record["technical_status"] = "PASS_PDF_ONLY" if not record["stage_errors"] else "FAIL"
        records.append(record)
        print("HOLDOUT", case["path"], record["technical_status"],
              record["stage_errors"], flush=True)
    by_period = Counter(r.get("report", {}).get("fiscal_period", "UNKNOWN") for r in records)
    status = Counter(r["technical_status"] for r in records)
    return {"schema": "financials.independent_period_holdout.v1",
            "scope": "PINNED_2025FY_2026Q1_20269M_ORIGINAL_PDFS_NOT_HISTORICAL_30",
            "company_specific_extraction_input": "NONE",
            "reports": len(records), "technical_pass": status["PASS_PDF_ONLY"],
            "technical_fail": status["FAIL"], "observed_period_counts": dict(by_period),
            "original_pdf_bytes_verification": "GIT_BLOB_SHA1_PER_INPUT_AND_SHA256_RECEIPT",
            "original_30_reference_corpus": "SEPARATE_UNCHANGED_UNDER_REVIEW",
            "material_unmapped_fact_coverage": "NOT_CHECKED",
            "human_financial_research": "NOT_CHECKED",
            "independent_aesthetic_editor": "NOT_CHECKED",
            "production_browser_release": "NOT_CHECKED",
            "rows": records}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", help="JSON receipt with all supported, degraded and failed stages")
    a = p.parse_args(argv)
    result = run()
    if a.out:
        target = Path(a.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print("INDEPENDENT_HOLDOUT_RECEIPT", target)
    print("INDEPENDENT_HOLDOUT", result["technical_pass"], "/",
          result["reports"], "FAIL", result["technical_fail"],
          "ORIGINAL_30_UNCHANGED", flush=True)
    return 0 if result["technical_fail"] == 0 and result["technical_pass"] == len(HOLDOUTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
