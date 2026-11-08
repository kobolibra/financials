#!/usr/bin/env python3
"""Hostile tests ensure quantitative research reaches actual reader-facing HTML."""
import json
from pathlib import Path
import sys
import unittest
from decimal import Decimal
from html import escape

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from audit_published_research_depth import verify
from audit_research_depth import MODELS, calculate

def fake_case(code):
    load=lambda path:json.loads((ROOT/path).read_text(encoding="utf8"))
    ledger={} if code=="600036" else load(f"research/rebuild-v10/input-ledgers/{code}.json")
    extras=load("research/rebuild-v10/extras.json")
    brief=next(row["quantified_driver"] for row in load("research/quality/pr35-hero-figure-briefs.json")["hero_figures"] if row["issuer"]==code)
    manifest=load("research/rebuild-v10/build-manifest.json")
    formula,source_type,keys=MODELS[code]
    rows=ledger["facts"] if source_type=="ledger" else extras[code]
    amounts={k:Decimal(str(rows[k]["yuan"] if source_type=="ledger" else rows[k]["val"])) for k in keys}
    result=calculate(formula,amounts)
    sha=brief["source_pdf_sha256"]
    opening=f'<section id="quantified-decision" data-research-schema="financials.source_bound_decision.v1" data-issuer="{code}" data-formula="{formula}" data-result-yuan="{result}" data-original-pdf-sha256="{sha}" data-accounting-not-causal="true">'
    parts=[opening]
    for k in keys:
        row=rows[k]
        parts.append(f'<div class="decision-fact" data-fact-id="{k}" data-exact-yuan="{amounts[k]}" data-period="{row["period"]}" data-physical-page="{row["page"]}">金额</div>')
    for k in ("decision_use","strongest_alternative","next_disclosure_falsifier","scope_and_limitations"):
        parts.append(f'<p>{escape(brief[k])}</p>')
    parts.append('<p>独立财务专业审阅：NOT_CHECKED；仅为会计金额勾稽，不是业务驱动因果证明。</p></section>')
    return "".join(parts),brief,ledger,manifest,extras

class ReaderFacingQuantifiedThesisTests(unittest.TestCase):
    def test_four_real_original_source_bridges_can_be_published(self):
        for code in MODELS:
            with self.subTest(code=code):
                self.assertEqual(verify(code,*fake_case(code)),[])

    def test_tampering_with_exact_yuan_is_rejected(self):
        args=list(fake_case("688111"))
        args[0]=args[0].replace('data-exact-yuan="3313262599.20"',
                                  'data-exact-yuan="3313262599.21"')
        self.assertIn("688111: PUBLISHED_FACT_MONEY_WRONG_rev",verify("688111",*args))

    def test_forged_research_result_not_equal_to_original_finance(self):
        args=list(fake_case("000333"))
        args[0]=args[0].replace('data-result-yuan="7072567000"',
                                  'data-result-yuan="7072566999"')
        self.assertIn("000333: PUBLISHED_DECISION_BRIDGE_NOT_RECONCILED",verify("000333",*args))

    def test_prior_year_period_mislabeled_current_is_blocked(self):
        args=list(fake_case("600036"))
        args[0]=args[0].replace('data-fact-id="nii_prior" data-exact-yuan="106085000000" data-period="2025H1"',
                                  'data-fact-id="nii_prior" data-exact-yuan="106085000000" data-period="2026H1"')
        self.assertIn("600036: PUBLISHED_FACT_PERIOD_WRONG_nii_prior",verify("600036",*args))

    def test_future_disclosure_falsifier_cannot_be_dropped_from_public_article(self):
        args=list(fake_case("600519"))
        args[0]=args[0].replace(escape(args[1]["next_disclosure_falsifier"]),"已证实")
        self.assertIn("600519: EDITORIAL_REASON_OR_FALSIFIER_NOT_PUBLISHED_next_disclosure_falsifier",verify("600519",*args))

    def test_false_second_analyst_or_causal_certification_not_accepted(self):
        args=list(fake_case("688111"))
        args[0]=args[0].replace("NOT_CHECKED","INDEPENDENTLY_CERTIFIED")
        self.assertIn("688111: FALSE_FINANCE_OR_CAUSAL_APPROVAL",verify("688111",*args))

    def test_duplicate_fake_fact_cannot_hide_in_article(self):
        args=list(fake_case("688111"))
        fragment='<div class="decision-fact" data-fact-id="rev" data-exact-yuan="3313262599.20" data-period="2026H1" data-physical-page="6">金额</div>'
        args[0]=args[0].replace(fragment,fragment+fragment)
        errors=verify("688111",*args)
        self.assertIn("688111: WRONG_RENDERED_SOURCE_FACT_COUNT",errors)
        self.assertIn("688111: DUPLICATE_PUBLISHED_FACT_ROW",errors)

    def test_wrong_original_pdf_sha_not_publication(self):
        args=list(fake_case("000333"))
        args[0]=args[0].replace('data-original-pdf-sha256="'+args[1]["source_pdf_sha256"]+'"',
                                  'data-original-pdf-sha256="'+'0'*64+'"')
        self.assertIn("000333: data-original-pdf-sha256_MISMATCH",verify("000333",*args))

if __name__=="__main__":
    unittest.main()
