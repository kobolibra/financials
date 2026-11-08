#!/usr/bin/env python3
"""Adversarial original-finance signed stage tests.

The whole article figure is one shared 1040/330 CNY grammar, not two silently
divergent JS and mobile implementations. Human art approval remains separate.
"""
from __future__ import annotations
import copy,json,sys,unittest,xml.etree.ElementTree as ET
from decimal import Decimal as D
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from shared_pnl import original_plan,render_asr_pnl

LEDGER=json.loads((ROOT/"source-ledger.json").read_text())
SVG="{http://www.w3.org/2000/svg}"

class SignedFullOriginalProfit(unittest.TestCase):
    def test_all_ten_signed_income_steps_with_negative_interim_and_exact_report_net(self):
        plan=original_plan(LEDGER)
        facts=LEDGER["facts"]
        stages={x.id:x for x in plan.stages}
        self.assertEqual(len(stages),10)
        self.assertEqual(plan.start_yuan,D("721516109.28"))
        self.assertEqual(stages["rnd"].delta,-D("663322721.74"))
        self.assertEqual(stages["nonoperating"].delta,D("256125.37"))
        self.assertEqual(stages["income_tax"].delta,D("29042237.12"))
        cumulative=[v for _,_,v,_ in plan.check(facts)]
        self.assertTrue(any(v<0 for v in cumulative))
        self.assertEqual(cumulative[-3],D("54945406.18"))
        self.assertEqual(cumulative[-2],D("55201531.55"))
        self.assertEqual(cumulative[-1],D("84243768.67"))
        self.assertEqual(plan.source_status,
            "MIRROR_COMPLETE_PDF_SHA_PASS__OFFICIAL_EQUIVALENCE_NOT_CHECKED")
        for mobile in (False,True):
            with self.subTest(mobile=mobile):
                svg=ET.fromstring(render_asr_pnl(LEDGER,mobile=mobile))
                self.assertEqual(svg.attrib["data-original-pdf-sha256"],
                                 LEDGER["source"]["original_bytes_sha256"])
                self.assertEqual(svg.attrib["data-end-net-yuan"],"84243768.67")
                self.assertEqual(svg.attrib["data-layout"],"native-330" if mobile else "editorial-1040")
                self.assertEqual(svg.attrib["data-negative-intervals-preserved"],"true")
                bars=[x for x in svg.findall(".//"+SVG+"rect") if x.get("data-stage-id")]
                self.assertEqual(len(bars),10)
                for bar in bars:
                    before=D(bar.attrib["data-before-yuan"])
                    delta=D(bar.attrib["data-signed-yuan"])
                    after=D(bar.attrib["data-after-yuan"])
                    scale=D(bar.attrib["data-money-scale-yuan-per-unit"])
                    self.assertEqual(before+delta,after)
                    self.assertLess(abs(D(bar.attrib["width"])-abs(delta)/scale),D(".0000002"))
                    self.assertTrue(bar.attrib["data-source-fact-ids"])
                    self.assertIn("86",bar.attrib["data-physical-pages"] if bar.get("data-stage-id")=="gross" else "86,87")
                self.assertTrue(any(D(x.attrib["data-after-yuan"])<0 for x in bars))

    def test_period_and_scope_tampering_or_profit_gap_rejected(self):
        for key,mutate,reason in [
            ("rnd_expense",{"period":"2025H1"},"CROSS_PERIOD_SCOPE_UNIT"),
            ("fair_value_income",{"scope":"parent"},"CROSS_PERIOD_SCOPE_UNIT"),
            ("income_tax_expense",{"page":None},"MISSING_SOURCE_PAGE"),
            ("operating_profit",{"yuan":"54945406.19"},"CHECKPOINT_ACCOUNTING_WRONG"),
            ("consolidated_net_profit",{"yuan":"84243768.68"},"END_NET_PROFIT_NOT_CLOSED"),
        ]:
            with self.subTest(key=key):
                changed=copy.deepcopy(LEDGER)
                changed["facts"][key].update(mutate)
                with self.assertRaisesRegex(ValueError,reason):
                    original_plan(changed)

    def test_mirror_status_must_not_claim_official_exchange_same_bytes(self):
        changed=copy.deepcopy(LEDGER)
        changed["source"]["original_bytes_gate"]="OFFICIAL_EQUIVALENCE_VERIFIED"
        with self.assertRaisesRegex(ValueError,"UNVERIFIED_ORIGIN_STATUS"):
            original_plan(changed)
        changed=copy.deepcopy(LEDGER)
        changed["source"]["original_bytes_sha256"]="0"*64
        # The complete-PDF manifest verifier is responsible for comparing
        # PDF bytes to this SHA. This layer requires unambiguous SHA shape,
        # while published equality is guarded by full-source reproduction.
        self.assertEqual(original_plan(changed).source_sha256,"0"*64)
        changed["source"]["original_bytes_sha256"]="not-sha"
        with self.assertRaisesRegex(ValueError,"SOURCE_SHA_NOT_PROVEN"):
            original_plan(changed)

    def test_derivative_zero_row_cannot_pretend_printed_disclosed_zero(self):
        plan=original_plan(LEDGER)
        z=next(x for x in plan.stages if x.id=="nonoperating")
        self.assertIn("SOURCE_BLANK_DERIVED_ZERO",z.provenance)
        self.assertIn("nonoperating_expense",z.source_ids)

if __name__=="__main__":unittest.main()
