#!/usr/bin/env python3
"""Independent financial chart *meaning* tests, not just clipping/screenshot success.

All tests use original exact-yuan committed 2026H1 source ledgers. Human
five-second comprehension, editorial distinctiveness and full notes remain
NOT_CHECKED. No PDF/network/Playwright is required for the unit-level cases.
"""
from __future__ import annotations

from decimal import Decimal as D
import html
import json
from pathlib import Path
import re
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"research/rebuild-v10"))
sys.path.insert(0,str(ROOT/"scripts"))
from native_mobile import signed_product_profit
from audit_v10_flow_contract import classify, _raw

LEDGER=json.loads((ROOT/"research/rebuild-v10/input-ledgers/600519.json").read_text())["facts"]
def RAW_GET(code,key):
    return D(str(_raw(ROOT,code)[key]["yuan"]))
GET=lambda code,key:LEDGER[key]["yuan"]
XMLNS="{http://www.w3.org/2000/svg}"


def _paths(svg:str):
    tree=ET.fromstring(svg)
    return [node for node in tree.iter(XMLNS+"path")
            if node.get("data-ribbon-yuan") is not None]


def _rects(svg:str, attribute:str):
    tree=ET.fromstring(svg)
    return [node for node in tree.iter(XMLNS+"rect")
            if node.get(attribute) is not None]


class OriginalVisualGrammarTests(unittest.TestCase):
    def test_moutai_tiny_loss_must_not_be_fake_width_or_invisible_story(self):
        kind=classify(ROOT,"600519")
        self.assertEqual(kind["kind"],"TYPE_C_SANKEY_OMITTED")
        svg=signed_product_profit("600519",kind,GET,{
            "maotai_rev":"茅台酒","series_rev":"系列酒",
            "other_rev":"其他业务"},mobile=True)
        root=ET.fromstring(svg)
        self.assertEqual(root.get("data-flow-omission"),
                         "FINANCIAL_SANKEY_OMITTED_WITH_SOURCE_REASON")
        # The loss is 12,446,319.42 CNY against the first product's
        # 71.7bn CNY GP, only 0.0416 SVG units at true 232-unit scale.
        items=_rects(svg,"data-signed-yuan")
        self.assertEqual(len(items),3)
        loss=items[-1]
        loss_yuan=D(LEDGER["other_rev"]["yuan"])-D(LEDGER["other_cogs"]["yuan"])
        self.assertLess(loss_yuan,0)
        self.assertEqual(D(loss.get("data-signed-yuan")),loss_yuan)
        exact_true_width=(abs(loss_yuan)/(
            D(LEDGER["maotai_rev"]["yuan"])-D(LEDGER["maotai_cogs"]["yuan"]))*D(232))
        self.assertEqual(D(loss.get("width")).quantize(D(".0001")),
                         exact_true_width.quantize(D(".0001")))
        self.assertLess(D(loss.get("width")),D(".05"))
        # A visible separate scale, never an invented minimum for the main bar.
        zoom=_rects(svg,"data-local-inset-source")
        self.assertEqual(len(zoom),2)
        self.assertEqual(sum((D(z.get("data-original-yuan")) for z in zoom),D(0)),
                         D(LEDGER["other_rev"]["yuan"])+D(LEDGER["other_cogs"]["yuan"]))
        self.assertNotEqual(D(zoom[0].get("data-inset-yuan-per-svg-unit")),
                            D(loss.get("data-scale-yuan-per-svg-unit")))
        text=" ".join(x.text or "" for x in root.iter(XMLNS+"text"))
        for phrase in ("负毛利","局部放大","独立金额比例尺","毛利率"):
            self.assertIn(phrase,text)
        self.assertNotIn("FINANCIAL_SANKEY_OMITTED_WITH_SOURCE_REASON",text)
        self.assertNotIn(kind["reason"],text)

    def test_moutai_desktop_is_an_independent_wide_original_yuan_signed_figure(self):
        kind=classify(ROOT,"600519")
        desktop=signed_product_profit("600519",kind,GET,{
            "maotai_rev":"茅台酒","series_rev":"系列酒",
            "other_rev":"其他业务"})
        phone=signed_product_profit("600519",kind,GET,{},mobile=True)
        graph=ET.fromstring(desktop)
        self.assertEqual(graph.get("data-layout"),"desktop-editorial")
        self.assertIn("1040",graph.get("viewBox"))
        self.assertNotEqual(desktop,phone)
        self.assertIn("独立比例尺的局部放大",desktop)
        self.assertEqual(len(_rects(desktop,"data-signed-yuan")),3)
        self.assertEqual(len(_rects(desktop,"data-local-inset-source")),2)
        body=" ".join(node.text or "" for node in graph.iter(XMLNS+"text"))
        self.assertIn("717",body)
        self.assertIn("毛利率",body)
        self.assertNotIn("FINANCIAL_SANKEY_OMITTED_WITH_SOURCE_REASON",body)

    def test_unified_financials_three_stage_source_trunk_and_outcome_geometry(self):
        from unified_finance import render_typed_finance, plan_for
        for code,nsource,nsink in (("688111",4,2),("000333",3,2),("600036",3,4)):
            with self.subTest(code=code):
                typed=classify(ROOT,code)
                plan=plan_for(code,typed,RAW_GET,{})
                total=plan.check()
                for mobile in (False,True):
                    graph=ET.fromstring(render_typed_finance(code,typed,RAW_GET,{},mobile=mobile))
                    self.assertEqual(graph.get("data-design-system"),"FINANCIALS_UNIFIED_STORY_V1")
                    self.assertEqual(graph.get("data-chart-grammar"),"SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY")
                    self.assertEqual(D(graph.get("data-revenue-yuan")),total)
                    nodes=[r for r in graph.iter(XMLNS+"rect") if r.get("data-node-role")]
                    self.assertEqual(len(nodes),nsource+nsink+1)
                    self.assertEqual([n.get("data-node-id") for n in nodes if n.get("data-node-role")=="total"],["revenue-total"])
                    paths=[p for p in graph.iter(XMLNS+"path") if p.get("data-ribbon-yuan")]
                    inflows=[p for p in paths if p.get("data-stage")=="source-to-revenue"]
                    outflows=[p for p in paths if p.get("data-stage")=="revenue-to-outcome"]
                    self.assertEqual(len(inflows),nsource)
                    self.assertEqual(sum((D(p.get("data-ribbon-yuan")) for p in inflows),D(0)),total)
                    self.assertEqual(sum((D(p.get("data-ribbon-yuan")) for p in outflows),D(0)),total)
                    self.assertEqual(len(outflows),8 if code=="688111" else nsink)
                    if code=="688111":
                        for sid,rev,c,gp in typed["source_own_cost_gp"]:
                            own=[p for p in outflows if p.get("data-source-id")==sid]
                            self.assertCountEqual([D(p.get("data-ribbon-yuan")) for p in own],[D(c),D(gp)])
                            self.assertEqual({p.get("data-revenue-yuan") for p in own},{rev})
                    if code=="000333":
                        self.assertEqual(graph.get("data-gp-limitation"),"PRODUCT_LEVEL_GP_NOT_ESTABLISHED")
                    if code=="600036":
                        self.assertEqual(graph.get("data-bank-interest-already-net"),"true")

    def test_mobile_source_stage_and_outcome_footer_have_nonoverlapping_original_yuan_rows(self):
        from unified_finance import render_typed_finance
        for code in ("688111","000333","600036"):
            with self.subTest(code=code):
                typed=classify(ROOT,code)
                svg=render_typed_finance(code,typed,RAW_GET,{},mobile=True)
                root=ET.fromstring(svg)
                grouped={}
                for t in root.iter(XMLNS+"text"):
                    grouped.setdefault(t.get("data-editorial-role"),[]).append(D(t.get("y")))
                source=max(grouped["source-summary"])
                header=min(grouped["source-stage-header"])
                self.assertGreater(header-source,D(18),
                                   "Source legend must never touch the real Sankey stage label")
                last_outcome=max(grouped["outcome-value"])
                warning=grouped["accounting-limitation"][0]
                note=grouped["source-caveat"][0]
                self.assertGreaterEqual(warning-last_outcome,D(25))
                self.assertGreaterEqual(note-warning,D(18))
                self.assertLess(note+D(12),D(root.get("viewBox").split()[-1]))
                self.assertEqual(len(grouped["outcome-value"]),len(
                    [x for x in root.iter(XMLNS+"rect") if x.get("data-node-role") in ("cost","profit")])*2)
                if code=="688111":
                    # 330px card must not discard the issuer's key insight:
                    # different product gross-margin rates.
                    summary=" ".join(t.text or "" for t in root.iter(XMLNS+"text")
                                     if t.get("data-editorial-role")=="source-summary")
                    self.assertEqual(summary.count("毛利"),4)

    def test_unified_flow_rejects_fake_allocations_and_negative_amounts(self):
        from unified_finance import plan_for
        from dataclasses import replace
        a=plan_for("688111",classify(ROOT,"688111"),RAW_GET,{})
        b=plan_for("000333",classify(ROOT,"000333"),RAW_GET,{})
        bank=plan_for("600036",classify(ROOT,"600036"),RAW_GET,{})
        with self.assertRaisesRegex(ValueError,"SOURCE_AND_OUTCOME_TOTAL_MISMATCH"):
            replace(b,sources=b.sources[:-1]).check()
        with self.assertRaisesRegex(ValueError,"NEGATIVE_IN_POSITIVE_FLOW"):
            replace(b,outcomes=(("fake","fake","-1","profit"),)+b.outcomes).check()
        with self.assertRaisesRegex(ValueError,"MUST_NOT_INVENT_PRODUCT_GP"):
            replace(b,allocations=(("home","group_gp","1"),)).check()
        with self.assertRaisesRegex(ValueError,"SOURCE_OWN_COST_CANNOT_BE_INFERRED"):
            replace(a,allocations=()).check()
        with self.assertRaisesRegex(ValueError,"MUST_NOT_INVENT_PRODUCT_GP"):
            replace(bank,allocations=(("nii","operating_profit","1"),)).check()

    def test_a_chart_cannot_pass_by_compressing_large_magnitude_into_1px(self):
        kind=classify(ROOT,"600519")
        svg=signed_product_profit("600519",kind,GET,{},mobile=True)
        other=_rects(svg,"data-signed-yuan")[-1]
        altered=svg.replace('width="'+other.get("width")+'"',
                            'width="1.0000"',1)
        # Demonstrate the current width contract actually catches visual fraud.
        rogue=_rects(altered,"data-signed-yuan")[-1]
        actual=D(rogue.get("width"))
        amount=abs(D(rogue.get("data-signed-yuan")))
        scale=D(rogue.get("data-scale-yuan-per-svg-unit"))
        self.assertGreater(abs(actual-amount/scale),D(".5"))


if __name__=="__main__":
    unittest.main()
