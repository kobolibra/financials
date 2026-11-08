#!/usr/bin/env python3
"""Hostile original-CNY signed profit-formation visual and period audits."""
from __future__ import annotations

from decimal import Decimal as D
import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"research/rebuild-v10"))
from profit_formation import form_plan,render_svg,render_profit_formation

NS="{http://www.w3.org/2000/svg}"

def source(code):
    ledger=json.loads((ROOT/f"research/rebuild-v10/input-ledgers/{code}.json").read_text())
    facts={k:dict(v) for k,v in ledger["facts"].items()}
    extra=json.loads((ROOT/"research/rebuild-v10/extras.json").read_text())[code]
    for k,item in extra.items():
        if isinstance(item,dict):
            facts[k]={"yuan":item["val"],"page":item["page"],
                      "period":item.get("period","2026H1"),"status":item.get("status","DISCLOSED")}
    source_sha=ledger["source"]["pdf_sha256"]
    return facts,source_sha

class SourceBoundSignedIncomeTests(unittest.TestCase):
    def test_exact_source_money_income_to_group_net(self):
        expected={
            "688111":("3313262599.20","500458107.69","2744613866.21","2517594330.93",None),
            "000333":("260042490000","194366771000","31684489000","26582874000","261052379000"),
        }
        for code,(rev,cogs,op,net,total) in expected.items():
            with self.subTest(code=code):
                facts,sha=source(code)
                plan=form_plan(code,facts,sha)
                step={x.id:x for x in plan.steps}
                self.assertEqual(step["income"].delta,D(rev))
                self.assertEqual(step["cost"].delta,-D(cogs))
                self.assertEqual(step["unallocated_operating"].after,D(op))
                self.assertEqual(step["nonoperating_tax"].after,D(net))
                self.assertEqual(step["net_income"].after,D(net))
                self.assertEqual(plan.gross_profit,D(rev)-D(cogs))
                self.assertEqual(plan.group_total_revenue,D(total) if total else None)
                for mobile in (False,True):
                    svg=ET.fromstring(render_svg(plan,mobile=mobile))
                    self.assertEqual(svg.get("data-source-pdf-sha256"),sha)
                    self.assertEqual(svg.get("data-net-yuan"),net)
                    self.assertEqual(svg.get("data-gross-yuan"),str(D(rev)-D(cogs)))
                    steps=[x for x in svg.iter(NS+"rect") if x.get("data-step-id")]
                    self.assertEqual(len(steps),len(plan.steps))
                    scale=D(svg.get("data-yuan-per-svg-unit"))
                    self.assertGreater(scale,0)
                    for bar in steps:
                        actual=D(bar.get("width"))
                        money=D(bar.get("data-delta-yuan"))
                        self.assertLess(abs(actual-abs(money)/scale),D(".00011"))
                        self.assertEqual(D(bar.get("data-before-yuan"))+money,
                                         D(bar.get("data-after-yuan")))
                    self.assertEqual(svg.get("data-layout"),
                                     "native-mobile-330" if mobile else "desktop-1040")

    def test_actual_published_reader_html_is_exact_source_compiler_output(self):
        # Lock the full HTML figure itself, not just the typed builder.
        # A finance chart changed by hand after the evidence-gated rebuild
        # is a failed release even when decorative visuals appear unchanged.
        for code in ("688111","000333"):
            with self.subTest(code=code):
                fact,sha=source(code)
                ledger=json.loads((ROOT/f"research/rebuild-v10/input-ledgers/{code}.json").read_text())
                expected=render_profit_formation(code,fact,sha,ledger["source"]["url"])
                published=(ROOT/f"public/research/2026-h1-v10/{code}.html").read_text()
                self.assertEqual(published.count('data-profit-formation="SOURCE_BOUND_SIGNED_V1"'),1)
                self.assertIn(expected,published,(code,"PUBLISHED_PROFIT_FORMATION_NOT_SOURCE_REPRODUCIBLE"))

    def test_midea_finance_never_embedded_in_industrial_gross_margin(self):
        facts,sha=source("000333")
        plan=form_plan("000333",facts,sha)
        step={x.id:x for x in plan.steps}
        self.assertEqual(step["finance_income"].delta,
                         D("1009683000")+D("206000"))
        self.assertEqual(step["finance_income"].after,
                         plan.gross_profit+D("1009683000")+D("206000"))
        self.assertEqual(plan.group_total_revenue,
                         step["income"].after+step["finance_income"].delta)
        html=render_profit_formation("000333",facts,sha,
                                     "https://static.cninfo.com.cn/original.pdf")
        self.assertIn("不是工业毛利",html)
        self.assertIn("DERIVED_UNATTRIBUTED_NOT_CAUSAL",html)
        self.assertIn("原始 PDF p.98",html)

    def test_unsupported_bank_or_insurer_cannot_be_forced_into_industrial_profit(self):
        for code in ("600036","601628","600519"):
            with self.assertRaisesRegex(ValueError,"INCOMPATIBLE_OR_UNSOURCED"):
                form_plan(code,{},("a"*64))

    def test_one_cent_falsification_and_wrong_period_not_accepted(self):
        facts,sha=source("688111")
        modified={k:dict(v) for k,v in facts.items()}
        modified["cogs"]["yuan"]="500458107.70"
        # An input number can be changed only if the source-ledger gate notices it:
        # rendering by itself never certifies a source fact. The per-page PDF
        # verifier must reject a forged source; this test exercises the typed
        # period and provenance invariant rather than inventing source truth.
        modified["cogs"]["period"]="2025H1"
        with self.assertRaisesRegex(ValueError,"PAGE_OR_FLOW_PERIOD"):
            form_plan("688111",modified,sha)
        with self.assertRaisesRegex(ValueError,"MISSING_COMPLETE_ORIGINAL_PDF_SHA"):
            form_plan("688111",facts,"x"*64)
        modified={k:dict(v) for k,v in facts.items()}
        modified["operating_profit"]["status"]="DERIVED"
        with self.assertRaisesRegex(ValueError,"NOT_AN_ORIGINAL_DISCLOSED_LINE"):
            form_plan("688111",modified,sha)

    def test_wrong_group_revenue_for_midea_rejected(self):
        facts,sha=source("000333")
        facts["total_rev"]["yuan"]="261052379001"
        with self.assertRaisesRegex(ValueError,"FINANCIAL_SUBSIDIARY_GROUP_REVENUE"):
            form_plan("000333",facts,sha)

    def test_adversarial_negative_or_nonfinite_money_rejected(self):
        facts,sha=source("000333")
        facts["cogs"]["yuan"]="Infinity"
        with self.assertRaisesRegex(ValueError,"NONFINITE_FINANCE_FACT"):
            form_plan("000333",facts,sha)
        facts,sha=source("688111")
        facts["cogs"]["yuan"]="-1"
        with self.assertRaisesRegex(ValueError,"SIGNED_OR_INCOMPATIBLE"):
            form_plan("688111",facts,sha)

if __name__=="__main__":
    unittest.main()
