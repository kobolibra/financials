#!/usr/bin/env python3
"""Fail-closed, issuer-independent publication-evidence and feedback regression contract.

New issuers must present a release-gates.json rather than inheriting the eight
historical pages' QA status. This checks data/proof consistency, NOT browser/live
service truth or the professional merits of source interpretation.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_PRE_CONTRACT = frozenset({
    "300394", "300308", "300502", "600036", "688111", "600519", "000333"
})
GATES = frozenset({
    "PDF_BYTES", "SOURCE_ROW_COLUMN", "ACCOUNTING_CORE",
    "RESEARCH_COUNTERCASE", "CHART_SEMANTICS", "VISUAL_EDITORIAL_SELF",
    "BROWSER_LOCAL", "OFFLINE_REBUILD", "MAJOR_NOTES_COMPLETE",
    "REPORTED_NOTE_TIES", "OFFICIAL_PDF_BYTE_EQUIVALENCE",
    "HISTORICAL_PEERS_VALUATION", "INDEPENDENT_HUMAN_REVIEW",
    "CLOUDFLARE_LIVE"
})
PREVIEW_BLOCKERS = frozenset({
    "PDF_BYTES", "SOURCE_ROW_COLUMN", "ACCOUNTING_CORE",
    "RESEARCH_COUNTERCASE", "CHART_SEMANTICS", "VISUAL_EDITORIAL_SELF",
    "BROWSER_LOCAL", "OFFLINE_REBUILD"
})
STATUSES = frozenset({"PASS", "FAIL", "NOT_CHECKED"})
RELEASE_CLASSES = frozenset({"source_limited_preview", "verified_research"})
REGRESSION_STATUSES = frozenset({
    "TESTED_ISSUER_ONLY", "TESTED_GENERIC_MECHANISM",
    "FAIL_LIVE_STILL_OPEN", "NEW_CONTRACT"
})
GITHUB_ACTION = re.compile(r"^https://github[.]com/kobolibra/financials/actions/runs/[0-9]+$")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def checked_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or value.startswith("/"):
        raise ValueError(f"INVALID_RELATIVE_PATH {value}")
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"OUTSIDE_REPOSITORY_PATH {value}") from exc
    return candidate


def validate_proof(root: Path, key: str, gate: dict) -> list[str]:
    errors: list[str] = []
    status, proof = gate.get("status"), gate.get("proof")
    if status not in STATUSES:
        return [f"INVALID_GATE_STATUS {key}: {status}"]
    if status != "NOT_CHECKED":
        if not isinstance(proof, str) or not proof:
            errors.append(f"UNSUPPORTED_GATE {key}: PASS/FAIL without proof")
        elif not GITHUB_ACTION.fullmatch(proof):
            try:
                if not checked_path(root, proof).is_file():
                    errors.append(f"MISSING_GATE_PROOF {key}: {proof}")
            except ValueError as exc:
                errors.append(str(exc))
    if not isinstance(gate.get("scope"), str) or len(gate["scope"].strip()) < 15:
        errors.append(f"AMBIGUOUS_GATE_SCOPE {key}")
    return errors


def validate_release(root: Path, catalog_issuer: dict, record: dict,
                     *, check_bytes: bool = True) -> list[str]:
    errors: list[str] = []
    code = catalog_issuer["code"]
    if record.get("schema_version") != 1 or record.get("code") != code:
        errors.append(f"ISSUER_RECORD_IDENTITY {code}")
    if record.get("report_route") != catalog_issuer["href"]:
        errors.append(f"ISSUER_ROUTE_MISMATCH {code}")
    route = catalog_issuer["href"]
    expected = "public/" + route.lstrip("/")
    if record.get("report_file") != expected or not (root / expected).is_file():
        errors.append(f"ISSUER_HTML_NOT_CANONICAL {code}")
    if not record.get("period") or record.get("release_class") not in RELEASE_CLASSES:
        errors.append(f"ISSUER_PERIOD_OR_CLASS_MISSING {code}")
    if record.get("release_class") == "verified_research" and catalog_issuer.get("stage") == "source-review":
        errors.append(f"FULL_RESEARCH_BUT_CATALOG_SOURCE_REVIEW {code}")

    pdf = record.get("source_pdf", {})
    path = pdf.get("path")
    sha = pdf.get("sha256")
    if not isinstance(sha, str) or not re.fullmatch("[a-f0-9]{64}", sha):
        errors.append(f"PDF_SHA_NOT_GROUNDED {code}")
    if pdf.get("official_original_byte_equivalence") not in STATUSES:
        errors.append(f"PDF_OFFICIAL_BYTE_GATE_MISSING {code}")
    if not isinstance(pdf.get("bytes"), int) or pdf["bytes"] < 10000:
        errors.append(f"PDF_BYTE_SIZE_INVALID {code}")
    if not isinstance(pdf.get("physical_pages"), int) or pdf["physical_pages"] < 2:
        errors.append(f"PDF_PAGE_CLAIM_INVALID {code}")
    try:
        original = checked_path(root, path)
        if original.suffix.lower() != ".pdf" or not original.is_file():
            errors.append(f"PDF_NOT_ARCHIVED {code}")
        elif check_bytes:
            data = original.read_bytes()
            if (not data.startswith(b"%PDF") or len(data) != pdf.get("bytes")
                    or hashlib.sha256(data).hexdigest() != sha):
                errors.append(f"PDF_BYTE_HASH_MISMATCH {code}")
    except ValueError as exc:
        errors.append(str(exc))

    sankey = record.get("sankey", {})
    if sankey.get("decision") not in {"USED_CONSERVED", "OMITTED_WITH_SOURCE_REASON"}:
        errors.append(f"SANKEY_RESEARCH_DECISION_MISSING {code}")
    if (sankey.get("decision") == "OMITTED_WITH_SOURCE_REASON"
            and len(str(sankey.get("omission_reason") or "")) < 25):
        errors.append(f"SANKEY_OMISSION_NOT_SOURCE_GROUNDED {code}")

    gates = record.get("gates")
    if not isinstance(gates, dict):
        return errors + [f"ISSUER_GATES_MISSING {code}"]
    for key in sorted(GATES - gates.keys()):
        errors.append(f"REQUIRED_GATE_MISSING {code}/{key}")
    for key in sorted(gates.keys() - GATES):
        errors.append(f"UNKNOWN_GATE {code}/{key}")
    for key in sorted(GATES & gates.keys()):
        errors += validate_proof(root, f"{code}/{key}", gates[key])
    if record.get("release_class") == "source_limited_preview":
        for key in sorted(PREVIEW_BLOCKERS & gates.keys()):
            if gates[key].get("status") != "PASS":
                errors.append(f"PREVIEW_P0_BLOCKED {code}/{key}")
        # Bounded exceptions cannot vanish from a preview merely because the
        # main accounting equation passes.
        for key, gate in gates.items():
            if gate.get("status") == "FAIL" and not any(
                b.get("kind") in {"SOURCE_NOTE", "RELEASE", "RESEARCH"}
                for b in record.get("blockers", [])
            ):
                errors.append(f"FAIL_WITHOUT_DISCLOSED_BLOCKER {code}/{key}")
    else:
        for key in sorted(GATES & gates.keys()):
            if gates[key].get("status") != "PASS":
                errors.append(f"VERIFIED_RESEARCH_HAS_OPEN_GATE {code}/{key}")
    # Never silently convert older Cloudflare browser green to new live PASS:
    # a source receipt is not the same thing as deployed production bytes.
    if gates.get("CLOUDFLARE_LIVE", {}).get("status") == "PASS" and not record.get("live_release_fingerprint"):
        errors.append(f"LIVE_PASS_WITHOUT_DEPLOYED_FINGERPRINT {code}")
    return errors


def validate_registry(root: Path) -> list[str]:
    errors = []
    path = root / "skills/ashare-financial-storytelling/quality-regressions.json"
    data = read_json(path)
    if data.get("schema_version") != 1:
        errors.append("REGRESSION_SCHEMA_UNSUPPORTED")
    cases = data.get("cases", [])
    if not cases:
        errors.append("REGRESSION_CASES_EMPTY")
    ids = [x.get("id") for x in cases]
    if len(set(ids)) != len(ids):
        errors.append("REGRESSION_DUPLICATE_ID")
    for case in cases:
        id_ = case.get("id")
        if not re.fullmatch(r"[A-Z]{3}-[0-9]{3}", str(id_)):
            errors.append(f"REGRESSION_ID_INVALID {id_}")
        if case.get("status") not in REGRESSION_STATUSES:
            errors.append(f"REGRESSION_STATUS_INVALID {id_}")
        if case.get("transfer_gate") not in GATES:
            errors.append(f"REGRESSION_WRONG_GATE {id_}")
        if case.get("scope") not in {"single_issuer", "cross_issuer_mechanism", "cross_issuer_process"}:
            errors.append(f"REGRESSION_SCOPE_INVALID {id_}")
        for field in ("root_cause", "correction", "assertion_marker", "proof_file"):
            if not isinstance(case.get(field), str) or len(case[field]) < 3:
                errors.append(f"REGRESSION_MISSING_{field} {id_}")
        try:
            test_path = checked_path(root, case.get("proof_file"))
            if not test_path.is_file():
                errors.append(f"REGRESSION_PROOF_FILE_MISSING {id_}")
            elif case.get("assertion_marker") not in test_path.read_text(encoding="utf-8"):
                errors.append(f"REGRESSION_MARKER_MISSING {id_}")
        except (ValueError, UnicodeError) as exc:
            errors.append(f"REGRESSION_PROOF_INVALID {id_}: {exc}")
    return errors


def validate_repository(root: Path = ROOT, *, check_bytes: bool = True) -> list[str]:
    errors = validate_registry(root)
    issuers = read_json(root / "site/research_catalog.json")["issuers"]
    codes = [x["code"] for x in issuers]
    if len(set(codes)) != len(codes):
        errors.append("DUPLICATE_CATALOG_CODE")
    if not LEGACY_PRE_CONTRACT.issubset(codes):
        errors.append("HISTORIC_SEVEN_REMOVED")
    for issuer in issuers:
        code = issuer["code"]
        if code in LEGACY_PRE_CONTRACT:
            continue  # explicit historical review debt, not retroactive certification
        record_path = root / "research" / "issuers" / code / "release-gates.json"
        if not record_path.is_file():
            errors.append(f"UNREGISTERED_NEW_ISSUER {code}")
            continue
        errors += validate_release(root, issuer, read_json(record_path),
                                   check_bytes=check_bytes)
    return errors


if __name__ == "__main__":
    try:
        problems = validate_repository()
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print("RELEASE_CONTRACT_CRASH", type(exc).__name__, str(exc), file=sys.stderr)
        raise SystemExit(2)
    if problems:
        for problem in problems:
            print("RELEASE_CONTRACT_FAIL", problem, file=sys.stderr)
        raise SystemExit(1)
    print("ISSUER_RELEASE_CONTRACT_PASS: existing seven legacy-review debt explicit; all new issuer records source-hashed and independently gated; regression inventory structurally verified")
