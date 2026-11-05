#!/usr/bin/env python3
"""Source-anchored AEI/FT visual delivery guard, not a human art-direction certificate.

This checks real checked-in independent HTML bytes, not historical screenshots
or merely the number of SVG elements. A static review cannot prove legibility;
it fails closed as NOT_CHECKED for browser/aesthetic judgement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWN_CURRENT_P0 = frozenset({"600036", "688111", "600519", "000333"})
P0 = "FAIL"
UNCHECKED = "NOT_CHECKED"


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def extract_css(text: str) -> str:
    return "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", text, re.I | re.S))


def inspect_html(code: str, source: bytes) -> dict:
    text = source.decode("utf-8")
    css = extract_css(text)
    mobile = css[css.find("@media(max-width:560px)"):] if "@media(max-width:560px)" in css else ""
    # V10 P0: hides ALL non-Sankey financial diagrams and keeps only
    # an 850px-wide flow in a 320px phone chart viewport. Historical CI
    # explicitly asserted the internal scroll as a success condition.
    hides_finance = bool(re.search(r"\.graphic-svg\s*\{\s*display\s*:\s*none", mobile))
    exception_sankey = bool(re.search(
        r"\.graphic-svg\.sankey-svg\s*\{\s*display\s*:\s*block", mobile))
    forces_wide = bool(re.search(
        r"\.graphic-svg\.sankey-svg\s+svg\s*\{[^}]*min-width\s*:\s*(\d{3,4})px",
        mobile))
    m = re.search(
        r"\.graphic-svg\.sankey-svg\s+svg\s*\{[^}]*min-width\s*:\s*(\d{3,4})px", mobile)
    wide_px = int(m.group(1)) if m else None
    has_figure = "<figure" in text
    has_table = "<table" in text
    has_svg = "<svg" in text
    uses_iframe = bool(re.search(r"<iframe\b", text, re.I))
    source_sankey = "财务桑基图" in text or "sankey-svg" in text
    failures = []
    if uses_iframe:
        failures.append("STANDALONE_REPORT_HAS_IFRAME")
    if not has_figure or not has_svg or not has_table:
        failures.append("NO_INDEPENDENT_FIGURE_SVG_AND_ACCESSIBLE_SOURCE_TABLE")
    if hides_finance and exception_sankey:
        failures.append("MOBILE_OMITS_ALL_NON_SANKEY_FINANCIAL_GRAPHS")
    if source_sankey and forces_wide and wide_px >= 700:
        failures.append("MOBILE_SANKEY_FIXED_WIDE_IN_SMALL_HORIZONTAL_PANE")
    return {
        "code": code,
        "html_sha256": sha256(source),
        "html_bytes": len(source),
        "figure_count_for_inventory_only": text.count("<figure"),
        "svg_count_for_inventory_only": text.count("<svg"),
        "has_source_table": has_table,
        "has_sankey_term": source_sankey,
        "forced_min_width_px": wide_px,
        "source_code_structural_failures": failures,
        "structural_status": P0 if failures else "PASS_STATIC_SCOPE_ONLY",
        "actual_1440_768_390_chromium": UNCHECKED,
        "sankey_exact_yuan_geometry": UNCHECKED,
        "editorial_visual_5_second_read": UNCHECKED,
        "real_second_human_art_director": UNCHECKED,
    }


def audit(root: Path, *, fail_known: bool = False) -> dict:
    catalog = json.loads((root / "site/research_catalog.json").read_text(encoding="utf-8"))
    assert catalog["published_issuer_count"] == len(catalog["issuers"])
    records = []
    violations = []
    immutable_legacy = json.loads((root / 'research/visual-audit/quality-debt.json').read_text(encoding='utf-8'))['legacy_source_frozen_allowlist_for_preexisting_only']
    for issuer in catalog["issuers"]:
        code = issuer["code"]
        html = root / "public" / issuer["href"].lstrip("/")
        if not html.is_file():
            violations.append(f"{code}: INDEPENDENT_REPORT_MISSING {html}")
            continue
        item = inspect_html(code, html.read_bytes())
        records.append(item)
        if item["source_code_structural_failures"]:
            # Waive only the exact source SHA of each historical old-FAIL report.
            # Any changed HTML remains a *new* publication that must fix P0.
            exact_historical_bytes = (code in KNOWN_CURRENT_P0 and
                                      immutable_legacy.get(code) == item['html_sha256'])
            if fail_known or not exact_historical_bytes:
                violations.append(f"{code}: {item['source_code_structural_failures']}")
    codes = {item["code"] for item in records}
    if len(records) != len(catalog["issuers"]) or len(codes) != len(records):
        violations.append("CATALOG_DOES_NOT_MAP_ONE_TO_ONE_TO_INDEPENDENT_HTML")
    # Never waive a new structural failure by adding an issuer to the
    # historical waiver. The fixed set is 2026-11-05 existing production debt.
    return {
        "schema_version": 1,
        "basis": "checked-in real main/branch HTML bytes; no live browser or human endorsement",
        "canonical_issuer_count": len(catalog["issuers"]),
        "known_existing_visual_p0": sorted(
            x["code"] for x in records
            if x["code"] in KNOWN_CURRENT_P0 and x["source_code_structural_failures"]
        ),
        "new_or_unwaived_p0": violations,
        "records": records,
        "conclusion": "FAIL" if violations else
            ("KNOWN_LEGACY_VISUAL_FAIL_NOT_CERTIFIED" if any(x["source_code_structural_failures"] for x in records)
             else "STATIC_ONLY_PASS_BROWSER_AND_AESTHETICS_NOT_CHECKED"),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--fail-known", action="store_true",
                   help="Strict editorial release: the existing four legacy P0s also block")
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()
    report = audit(args.root, fail_known=args.fail_known)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 1 if report["new_or_unwaived_p0"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
