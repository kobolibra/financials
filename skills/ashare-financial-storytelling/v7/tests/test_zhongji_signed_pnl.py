#!/usr/bin/env python3
"""Original 184p 300308 V7 signed profit-formation hostile tests."""
from __future__ import annotations
from decimal import Decimal as D
from pathlib import Path
import copy,json,sys,unittest,xml.etree.ElementTree as ET

ENGINE=Path(__file__).resolve().parents[1]/"engine"
sys.path.insert(0,str(ENGINE))
from zhongji_signed_pnl import original_plan,render_original_signed_pnl

LEDGER=json.loads((ENGINE.parent/"examples/zhongji-2026H1-ledger.json").read_text())
SVG="{http://www.w3.org/2000/svg}"

class SourceTypedOriginal300308SignedTests(unittest.TestCase):
    def test_seven_real_signed_flow_stages_from_source_to_group_net(self):
        p,facts=original_plan(LEDGER)
        self.assertEqual(p.source_sha256,"e0ecd7c365c65e90b1fa4b4616ba3f4649449d64451e0ba0b1b78ba9ce3170bf")
        self.assertEqual(len(p.stages),7)
        self.assertEqual(p.start_yuan,D("19323173654.59"))
        self.assertEqual(p.end_yuan,D("14733426763.13"))
        self.assertEqual(p.stages[1].delta,-D("1153028870.98"))
        self.assertEqual(p.stages[2].delta,-D("562247445.89"))
        self.assertEqual(p.stages[3].delta,
                         -(D("25266330732.20")-D("22454688140.44")
                           -D("1153028870.98")-D("562247445.89")))
        amounts=p.check(facts)
        self.assertEqual(amounts[4][2],D("17231320005.52"))
        self.assertEqual(amounts[-1][2],D("14733426763.13"))
        for mobile in (False,True):
            with self.subTest(mobile=mobile):
                svg=ET.fromstring(render_original_signed_pnl(LEDGER,mobile=mobile))
                self.assertEqual(svg.get("data-signed-statement-grammar"),
                    "FINANCIALS_TYPED_FULL_PNL_SIGNED_V1")
                self.assertEqual(svg.get("data-layout"),"native-330" if mobile else "editorial-1040")
                self.assertEqual(svg.get("data-end-net-yuan"),"14733426763.13")
                bars=[el for el in svg.iter(SVG+"rect") if el.get("data-stage-id")]
                self.assertEqual(len(bars),7)
                for bar in bars:
                    a=D(bar.get("data-before-yuan"))
                    delta=D(bar.get("data-signed-yuan"))
                    b=D(bar.get("data-after-yuan"))
                    scale=D(bar.get("data-money-scale-yuan-per-unit"))
                    self.assertEqual(a+delta,b)
                    self.assertLess(abs(D(bar.get("width"))-abs(delta)/scale),D(".0000002"))
                    self.assertTrue(bar.get("data-source-fact-ids"))
                    self.assertTrue(bar.get("data-physical-pages"))

    def test_poisoned_period_scope_missing_original_sha_or_accounting_does_not_render(self):
        for label,key,change,needle in [
            ("prior_in_current","research_expenses",{"period":"2025H1"},"REPORTED_CONSOLIDATED_FINANCE_FIELD"),
            ("parent_in_group","financial_expenses",{"scope":"parent"},"INCOMPATIBLE_FINANCIAL_FACT"),
            ("wrong_statement","net_profit",{"table":"parent_income"},"INCOMPATIBLE_FINANCIAL_FACT"),
            ("missing_page","operating_profit",{"page":0},"UNVERIFIED_ORIGINAL_PAGE"),
            ("fake_earnings","operating_profit",{"amount":"17231320005.53"},"SIGNED_END_NET_PROFIT_NOT_CLOSED"),
            ("missing_expense","research_expenses",{"status":"unavailable"},"REPORTED_CONSOLIDATED_FINANCE_FIELD"),
            ("cross_currency","revenue",{"amount":"NaN"},"SIGNED_NONFINITE_MONEY"),
        ]:
            with self.subTest(label=label):
                ledger=copy.deepcopy(LEDGER)
                ledger["facts"][key].update(change)
                with self.assertRaisesRegex(ValueError,needle):
                    original_plan(ledger)
        bad=copy.deepcopy(LEDGER)
        bad["document"]["source_archive_gate"]="NOT_CHECKED"
        with self.assertRaisesRegex(ValueError,"ORIGINAL_184P_SOURCE_SCOPE_NOT_VERIFIED"):
            original_plan(bad)
        bad=copy.deepcopy(LEDGER)
        bad["document"]["ticker"]="300394.SZ"
        with self.assertRaisesRegex(ValueError,"ORIGINAL_184P_SOURCE_SCOPE_NOT_VERIFIED"):
            original_plan(bad)

if __name__=="__main__":unittest.main()
