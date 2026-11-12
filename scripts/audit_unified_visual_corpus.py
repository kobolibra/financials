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


def has_native_pair(html:str,token:str)->bool:
    # Offline JS source in semiconductor/hydro/pharma is JSON-escaped,
    # while insurance and optical are literal HTML SVG markup.
    return html.count(token)+html.count(token.replace('"',chr(92)+'"'))>=2


def has_native_viewbox(html:str,width:int)->bool:
    token=f'viewBox="0 0 {width}'
    return token in html or token.replace('"',chr(92)+'"') in html


def verified_complete_migration(evidence,code,html_sha):
    """Current bytes and complete real browser/exports; never a profile badge."""
    if not isinstance(evidence,dict) or evidence.get('schema')!='financials.complete_figure_migration.v1' or evidence.get('status') not in ('PASS_LOCAL','PASS_PRODUCTION'):return False
    row=evidence.get('issuers',{}).get(code,{})
    if row.get('html_sha256')!=html_sha or row.get('complete_figure_migration') not in ('PASS_LOCAL','PASS_PRODUCTION'):return False
    if not re.fullmatch('[a-f0-9]{64}',row.get('pdf_sha256','')):return False
    count=row.get('figure_count')
    if type(count) is not int or count<1:return False
    cases=[c for c in evidence.get('cases',[]) if c.get('issuer')==code]
    if len(cases)!=3 or {c.get('width') for c in cases}!={1440,768,390}:return False
    known={'SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY','INSURANCE_PREMIUM_SOURCE_NEW_RENEW_TOTAL','FINANCIALS_TYPED_FULL_PNL_SIGNED_V1','SOURCE_SIGNED_BRIDGE_V1','SOURCE_EQUAL_STOCK_BALANCE_V1','SOURCE_NONNEGATIVE_COMPONENTS_V1','SOURCE_TWO_PERIOD_COMPARISON_V1','SOURCE_REPORTED_RATIO_V1','SOURCE_INDEPENDENT_METRICS_V1','SOURCE_SEPARATE_PANELS_V1'}
    for case in cases:
        figures=case.get('figures',[])
        if case.get('html_sha256')!=html_sha or len(figures)!=count or {f.get('index') for f in figures}!=set(range(count)):return False
        for figure in figures:
            if figure.get('grammar') not in known or figure.get('source_and_actual_geometry')!='PASS' or figure.get('visible_edition_download')!='PASS':return False
            if any(not re.fullmatch('[a-f0-9]{64}',figure.get(key,'')) for key in ('vector_sha256','screenshot_sha256')):return False
    return True


def inspect(catalog:dict,pages:dict[str,bytes],migration_evidence=None)->dict:
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
        elif code in {"300394","300502","300308"}:
            # Actual original-source optical publishers now use the canonical
            # connected money compiler for their HERO income graph on both
            # desktop and phone. The other figures and editorial art direction
            # are still from the V7 family; do not upgrade to all-unified.
            required=('data-design-system="FINANCIALS_UNIFIED_STORY_V1"',
                      'data-chart-grammar="SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY"',
                      'data-node-id="revenue-total"',
                      'data-stage="source-to-revenue"',
                      'data-stage="revenue-to-outcome"')
            if any(html.count(token)<2 for token in required):
                row["visual_grammar_status"]="FAIL_OPTICAL_HERO_UNIFIED_GRAMMAR"
                row["issues"].append("OPTICAL_MAIN_SANKEY_MISSING_OR_DISCONNECTED")
            elif 'viewBox="0 0 1100' not in html or 'viewBox="0 0 330' not in html:
                row["visual_grammar_status"]="FAIL_OPTICAL_HERO_UNIFIED_GRAMMAR"
                row["issues"].append("OPTICAL_PHONE_DESKTOP_BOTH_MUST_BE_NATIVE")
            elif code=="300308" and any(token not in html for token in (
                    '<aside class="disclosure-conflict"',
                    "422,649,612.97","422,649,613.97",
                    "e0ecd7c365c65e90b1fa4b4616ba3f4649449d64451e0ba0b1b78ba9ce3170bf")):
                row["visual_grammar_status"]="FAIL_OPTICAL_HERO_UNIFIED_GRAMMAR"
                row["issues"].append("ORIGINAL_P139_ONE_YUAN_PRINTED_CONTRADICTION_WAS_SUPPRESSED")
            else:
                row["visual_grammar_status"]="HERO_SANKEY_UNIFIED_OTHER_FIGURES_LEGACY"
                row["issues"].append("REMAINDER_OF_V7_ISSUER_ART_NOT_YET_UNIFIED")
        elif code in {"688220","600900","600276"}:
            # Source-typed originals now render SAME v9 connected main income
            # flow in native 1100 desktop and 330 phone SVG. Their other
            # corporate graphics are still sector publisher legacy.
            required=('data-design-system="FINANCIALS_UNIFIED_STORY_V1"',
                      'data-chart-grammar="SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY"',
                      'data-node-id="revenue-total"',
                      'data-stage="source-to-revenue"',
                      'data-stage="revenue-to-outcome"')
            if any(not has_native_pair(html,token) for token in required):
                row["visual_grammar_status"]="FAIL_SECTOR_HERO_NOT_SHARED_V9"
                row["issues"].append("SEMICONDUCTOR_UTILITY_PHARMA_HERO_GRAPH_NOT_CONNECTED")
            elif any(not has_native_viewbox(html,w) for w in (1100,330)):
                row["visual_grammar_status"]="FAIL_SECTOR_HERO_NOT_SHARED_V9"
                row["issues"].append("SECTOR_DESKTOP_AND_PHONE_SANKKY_NOT_INDEPENDENT")
            elif code=="688220" and ("OFFICIAL_EQUIVALENCE_NOT_CHECKED" not in html or "7.98万" not in html):
                row["visual_grammar_status"]="FAIL_SECTOR_HERO_NOT_SHARED_V9"
                row["issues"].append("ASR_ORIGINAL_MIRROR_CAVEAT_OR_TINY_SOURCE_WAS_HIDDEN")
            else:
                row["visual_grammar_status"]="HERO_SANKEY_UNIFIED_OTHER_FIGURES_LEGACY"
                row["issues"].append("REMAINDER_OF_ORIGINAL_SECTOR_PUBLISHER_ART_NOT_YET_UNIFIED")
        elif code=="601628":
            # Original insurance premiums are management old-contract
            # statistics. A shared COST/GP industrial income flow would be
            # financially false. This is a distinct but same-palette lawful
            # 4-source -> new/renew -> total insurance Sankey.
            required=('data-design-system="FINANCIALS_UNIFIED_STORY_V1"',
                      'data-chart-grammar="INSURANCE_PREMIUM_SOURCE_NEW_RENEW_TOTAL"',
                      'data-node-id="premium-total"',
                      'data-stage="premium-source-to-new-or-renew"',
                      'data-stage="new-or-renew-to-premium-total"')
            if any(html.count(x)<2 for x in required):
                row["visual_grammar_status"]="FAIL_INSURANCE_PREMIUM_SEMANTIC_GRAMMAR"
                row["issues"].append("INSURER_FOUR_NEW_RENEW_TOTAL_CONNECTED_GRAPH_MISSING")
            elif any(not has_native_viewbox(html,w) for w in (1100,330)):
                row["visual_grammar_status"]="FAIL_INSURANCE_PREMIUM_SEMANTIC_GRAMMAR"
                row["issues"].append("INSURER_MOBILE_OR_DESKTOP_NOT_NATIVE")
            elif 'data-accounting-basis="MANAGEMENT_LEGACY_PREMIUM_STATISTICS_NOT_CAS25"' not in html or "保险服务收入" not in html:
                row["visual_grammar_status"]="FAIL_INSURANCE_PREMIUM_SEMANTIC_GRAMMAR"
                row["issues"].append("PREMIUM_IS_NOT_CAS25_SERVICE_REVENUE_DISCLOSURE_MISSING")
            else:
                row["visual_grammar_status"]="HERO_SANKEY_UNIFIED_OTHER_FIGURES_LEGACY"
                row["issues"].append("INSURANCE_TEN_FIGURES_MONEY_EDITION_PRESERVED_BUT_OTHER_ART_NOT_UNIFIED")
        else:
            row["issues"].append("NOT_YET_MIGRATED_TO_CANONICAL_V9_EDITORIAL_SYSTEM")
        if item.get('figure_quality_contract')=='FULL_SOURCE_FIGURES_V1' and not row['visual_grammar_status'].startswith('FAIL_'):
            if verified_complete_migration(migration_evidence,code,row['actual_full_html_sha256']):
                row['visual_grammar_status']='UNIFIED_FULL_ARTICLE_SOURCE_FIGURES'
                row['issues']=[]
                row['proof_scope']='CURRENT_HTML_SHA_ALL_FINANCIAL_FIGURES_THREE_VIEWPORTS_REAL_EXPORTS_NOT_HUMAN_SIGNOFF'
        rows.append(row)
    if len(rows)!=len(catalog['issuers']) or len({x['issuer'] for x in rows})!=len(rows):
        raise AssertionError('CANONICAL_CATALOG_SCOPE_OR_DUPLICATE_CHANGED')
    adopted=[x["issuer"] for x in rows if x["visual_grammar_status"]=="UNIFIED_FINANCIAL_INCOME_FLOW"]
    legitimate_signed=[x["issuer"] for x in rows if x["visual_grammar_status"]=="UNIFIED_SEMANTICS_SIGNED_EXCEPTION"]
    old=[x["issuer"] for x in rows if x["visual_grammar_status"]=="LEGACY_NOT_UNIFIED"]
    partial=[x["issuer"] for x in rows if x["visual_grammar_status"]=="HERO_SANKEY_UNIFIED_OTHER_FIGURES_LEGACY"]
    failures=[x["issuer"] for x in rows if x["visual_grammar_status"].startswith("FAIL_")]
    return {"schema":"financials.visual_unification_census.v1",
            "scope":"CURRENT_REPOSITORY_ARTICLE_HTML_SHA_ONLY",
            "canonical_issuer_count":len(rows),
            "unified_positive_sankey_issuers":adopted,
            "fully_migrated_source_article_issuers":[x["issuer"] for x in rows if x["visual_grammar_status"]=="UNIFIED_FULL_ARTICLE_SOURCE_FIGURES"],
            "lawful_signed_exception_issuers":legitimate_signed,
            "legacy_not_unified":old,
            "partial_hero_only_unified_remaining_art_legacy":partial,
            "strict_all_11_visual_unification":"PASS" if not old and not partial and not failures else "NOT_ESTABLISHED",
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
    profile=catalog.get('figure_quality_contracts',{}).get('FULL_SOURCE_FIGURES_V1',{})
    receipt=ROOT/profile['local_migration_receipt'] if profile.get('local_migration_receipt') else None
    evidence=json.loads(receipt.read_text()) if receipt and receipt.is_file() else None
    verdict=inspect(catalog,pages,evidence)
    result=json.dumps(verdict,ensure_ascii=False,indent=2)+"\n"
    print(result)
    if args.out:
        Path(args.out).write_text(result,encoding="utf8")
    if verdict["failed_new_grammar"]:
        print("NEW_VISUAL_GRAMMAR_P0",verdict["failed_new_grammar"],file=sys.stderr)
        return 1
    if args.strict_all_11 and verdict["strict_all_11_visual_unification"]!="PASS":
        print("ALL_11_NOT_UNIFIED_DONT_CERTIFY",verdict["legacy_not_unified"]+verdict["partial_hero_only_unified_remaining_art_legacy"],file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
