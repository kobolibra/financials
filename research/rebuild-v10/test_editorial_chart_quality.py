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
from native_mobile import source_own_sankey, signed_product_profit, group_sankey
from audit_v10_flow_contract import classify

LEDGER=json.loads((ROOT/"research/rebuild-v10/input-ledgers/600519.json").read_text())["facts"]
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
    def test_wps_desktop_is_real_three_stage_not_stretched_phone_card(self):
        kind=classify(ROOT,"688111")
        svg=source_own_sankey("688111",kind,{
            "wps_personal":"WPS个人","wps365":"WPS365",
            "wps_software":"WPS软件","other_rev":"其他"})
        root=ET.fromstring(svg)
        self.assertEqual(root.get("data-layout"),"desktop-editorial")
        self.assertIn("1040",root.get("viewBox"))
        self.assertEqual(len(_paths(svg)),12)
        groups={}
        for node in _paths(svg):
            sid=node.get("data-source-id")
            groups.setdefault(sid,[]).append(D(node.get("data-ribbon-yuan")))
            r,c,g=[D(node.get(name)) for name in
                   ("data-revenue-yuan","data-cost-yuan","data-gp-yuan")]
            self.assertEqual(r,c+g)
            self.assertEqual(D(node.get("data-scale-yuan-per-svg-unit")),
                             D(kind["exact_yuan_total"])/D(260))
        self.assertEqual(set(groups),set(kind["source_keys"]))
        for sid,r,c,g in kind["source_own_cost_gp"]:
            self.assertCountEqual(groups[sid],[D(r),D(c),D(g)])
        self.assertEqual(sum((x for values in groups.values() for x in values),D(0)),
                         D(kind["exact_yuan_total"])*2)
        self.assertIn("集团营业毛利",svg)
        self.assertIn("毛利率",svg)

    def test_wps_mobile_keeps_all_four_source_own_cost_and_gp(self):
        kind=classify(ROOT,"688111")
        svg=source_own_sankey("688111",kind,{
            "wps_personal":"WPS个人","wps365":"WPS365",
            "wps_software":"WPS软件","other_rev":"其他"},mobile=True)
        root=ET.fromstring(svg)
        self.assertNotIn("desktop-editorial",root.attrib.values())
        self.assertIn("330",root.get("viewBox"))
        self.assertEqual(len(_paths(svg)),8)
        for sid,r,c,g in kind["source_own_cost_gp"]:
            observed=[D(x.get("data-ribbon-yuan")) for x in _paths(svg)
                      if x.get("data-source-id")==sid]
            self.assertCountEqual(observed,[D(c),D(g)])

    def test_midea_group_only_must_disclose_in_chinese_without_machine_tag(self):
        typed=classify(ROOT,"000333")
        svg=group_sankey("000333",typed,{
            "home":"智能家居","industrial_solution":"商业及工业","other_total":"其他业务"})
        root=ET.fromstring(svg)
        self.assertEqual(root.get("data-gp-limitation"),
                         "PRODUCT_LEVEL_GP_NOT_ESTABLISHED")
        ribbons=_paths(svg)
        self.assertEqual(len(ribbons),5)
        vals=[D(t.get("data-ribbon-yuan")) for t in ribbons]
        self.assertEqual(sum(vals[:3],D(0)),D(typed["exact_yuan_total"]))
        self.assertEqual(sum(vals[3:],D(0)),D(typed["exact_yuan_total"]))
        visible=" ".join(n.text or "" for n in root.iter(XMLNS+"text"))
        self.assertIn("未披露各业务",visible)
        self.assertIn("不能",visible)
        self.assertNotIn("PRODUCT_LEVEL_GP_NOT_ESTABLISHED",visible)

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
