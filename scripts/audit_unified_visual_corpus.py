#!/usr/bin/env python3
"""Reality-based 11-issuer visual design adoption census, never vanity green.

The positive-income Sankey grammar MUST have a real shared total-income node,
connected source→trunk and trunk→outcome ribbons, both desktop and mobile
editions, and exact original-yuan semantics. Signed non-Sankey C remains
legitimate in common financial grammar; old sector page builders are explicitly
LEGACY_NOT_UNIFIED until actually migrated and independently screenshot reviewed.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
V10={"688111","000333","600036","600519"}
POSITIVE={"688111","000333","600036"}
LEGACY={"300394","300308","300502","688220","600900","600276","601628"}


def inspect(catalog:dict,pages:dict[str,bytes])->dict:
    rows=[]
    seen=set()
    for item in catalog["issuers"]:
        code=item["code"]
        if code in seen:raise AssertionError("DUPLICATE_ISSUER")
        seen.add(code)
        if code not in pages:raise AssertionError("MISSING_PUBLISHED_ARTICLE "+code)
        html=pages[code].decode("utf8")
        row={"issuer":code,"route":item["href"],
             "actual_full_html_sha256":sha256(pages[code]).hexdigest(),
             "visual_grammar_status":"LEGACY_NOT_UNIFIED","issues":[]}
        if code in POSITIVE:
            for token in ('data-design-system="FINANCIALS_UNIFIED_STORY_V1"',
                          'data-chart-grammar="SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY"',
                          'data-node-id="revenue-total"',
                          'data-stage="source-to-revenue"',
                          'data-stage="revenue-to-outcome"'):
                if html.count(token)<2:
                    row["issues"].append("DISCONNECTED_OR_OLD_SANKEY_"+token.split('"')[0])
            if 'viewBox="0 0 1100' not in html or 'viewBox="0 0 330' not in html:
                row["issues"].append("DESKTOP_AND_PHONE_NOT_INDEPENDENTLY_REEDITED")
            row["visual_grammar_status"]="UNIFIED_FINANCIAL_INCOME_FLOW" if not row["issues"] else "FAIL_NEW_VISUAL_GRAMMAR"
        elif code=="600519":
            needed=('data-flow-omission="FINANCIAL_SANKEY_OMITTED_WITH_SOURCE_REASON"',
                    'data-local-inset-source="other_rev"',"独立金额比例尺","局部放大")
            row["issues"]=[f"SIGNED_NEGATIVE_INTEGRITY_MISSING_{i}" for i,t in enumerate(needed) if t not in html]
            row["visual_grammar_status"]="UNIFIED_SEMANTICS_SIGNED_EXCEPTION" if not row["issues"] else "FAIL_SIGNED_NEGATIVE_GRAMMAR"
        else:
            # A valid historical page can be financially correct without
            # complying with the new unified editorial visual renderer.
            row["issues"].append("NOT_YET_MIGRATED_TO_CANONICAL_V9_EDITORIAL_SYSTEM")
        rows.append(row)
    if len(rows)!=11 or set(x["issuer"] for x in rows)!=POSITIVE|LEGACY|{"600519"}:
        raise AssertionError("CANONICAL_11_COMPANY_SCOPE_CHANGED_WITHOUT_MIGRATION")
    adopted=[x["issuer"] for x in rows if x["visual_grammar_status"]=="UNIFIED_FINANCIAL_INCOME_FLOW"]
    legitimate_signed=[x["issuer"] for x in rows if x["visual_grammar_status"]=="UNIFIED_SEMANTICS_SIGNED_EXCEPTION"]
    old=[x["issuer"] for x in rows if x["visual_grammar_status"]=="LEGACY_NOT_UNIFIED"]
    failures=[x["issuer"] for x in rows if x["visual_grammar_status"].startswith("FAIL_")]
    return {"schema":"financials.visual_unification_census.v1",
            "scope":"CURRENT_REPOSITORY_ARTICLE_HTML_SHA_ONLY",
            "canonical_issuer_count":len(rows),
            "unified_positive_sankey_issuers":adopted,
            "lawful_signed_exception_issuers":legitimate_signed,
            "legacy_not_unified":old,
            "strict_all_11_visual_unification":"PASS" if not old and not failures else "NOT_ESTABLISHED",
            "failed_new_grammar":failures,
            "independent_visual_art_director":"NOT_CHECKED",
            "all_11_original_source_PDF_verified_and_in_same_renderer":"NOT_ESTABLISHED",
            "rows":rows}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--strict-all-11",action="store_true",help="MUST FAIL until all 11 are truly migrated, not just released")
    parser.add_argument("--out",default="")
    args=parser.parse_args()
    catalog=json.loads((ROOT/"site/research_catalog.json").read_text(encoding="utf8"))
    pages={x["code"]:(ROOT/"public"/x["href"].lstrip("/")).read_bytes() for x in catalog["issuers"]}
    verdict=inspect(catalog,pages)
    result=json.dumps(verdict,ensure_ascii=False,indent=2)+"\n"
    print(result)
    if args.out:
        Path(args.out).write_text(result,encoding="utf8")
    if verdict["failed_new_grammar"]:
        print("NEW_VISUAL_GRAMMAR_P0",verdict["failed_new_grammar"],file=sys.stderr)
        return 1
    if args.strict_all_11 and verdict["strict_all_11_visual_unification"]!="PASS":
        print("ALL_11_NOT_UNIFIED_DONT_CERTIFY",verdict["legacy_not_unified"],file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
