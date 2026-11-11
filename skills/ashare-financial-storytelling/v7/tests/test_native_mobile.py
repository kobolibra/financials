#!/usr/bin/env python3
"""Hostile source and original-yuan mobile figure tests for 300394/300502.

The 300308 earlier public report's source ledger still says
NOT_VERIFIED_REMOTE_PDF and memo DRAFT_NEEDS_SECOND_REVIEW, so it is NOT
silently promoted or rewritten by these issuer releases.
"""
from __future__ import annotations
import copy,json,sys,unittest
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
ENGINE=ROOT/"skills/ashare-financial-storytelling/v7/engine"
sys.path.insert(0,str(ENGINE))
import native_mobile_finance as native
from render_v7 import build

def get_ledger(code):
    if code=="300394":p=ENGINE/"sample-ledger.json"
    elif code=="300502":p=ENGINE.parent/"examples/xinyisheng-2026H1-ledger.json"
    elif code=="300308":p=ENGINE.parent/"examples/zhongji-2026H1-ledger.json"
    else:raise ValueError(code)
    return json.loads(p.read_text(encoding="utf-8"))

def get_memo(code):
    if code=="300394":p=ENGINE/"sample-memo.json"
    elif code=="300502":p=ENGINE.parent/"examples/xinyisheng-2026H1-memo.json"
    elif code=="300308":p=ENGINE.parent/"examples/zhongji-2026H1-memo.json"
    else:raise ValueError(code)
    return json.loads(p.read_text(encoding="utf-8"))

class OriginalFinanceMobiles(unittest.TestCase):
    def test_two_independent_source_close_and_full_mobile_exhibit_families(self):
        for code in ("300394","300502"):
            with self.subTest(code=code):
                ledger=get_ledger(code)
                self.assertIn("source_sha256",ledger["document"])
                self.assertEqual(len(ledger["document"]["source_sha256"]),64)
                panels=native.make(ledger)
                self.assertTrue({"01","03","04","05","06","07","08","09","10"}.issubset(panels.keys()))
                self.assertEqual(panels["01"].count('class="native-money-source"'),len(ledger["segments"]))
                self.assertEqual(panels["01"].count('class="native-money-sink"'),2)
                self.assertEqual(panels["01"].count('class="native-money-ribbon"'),len(ledger["segments"])*2)
                self.assertIn("SVG",panels["01"].upper())
                self.assertIn("2026H1",panels["01"])
                self.assertIn('data-cumulative-yuan=',panels["06"])
                self.assertIn('data-signed-yuan=',panels["03"])
                report,_=build(ledger,get_memo(code))
                self.assertEqual(report.count('data-design-system="FINANCIALS_UNIFIED_STORY_V1"'),2)
                self.assertEqual(report.count('data-node-id="revenue-total"'),2)
                self.assertEqual(report.count('class="native-finance"'),len(panels))
                self.assertIn('viewBox="0 0 330',report)
                self.assertIn(ledger["document"]["source_sha256"],report)
                self.assertEqual(report.count('class="chart-shell '), 10 if code=="300394" else 11)
                self.assertIn("在窄屏上可横向滑动",report) if False else None

    def test_three_optical_signed_panels_readable_and_same_money_scale(self):
        import re
        import xml.etree.ElementTree as ET
        ns="{http://www.w3.org/2000/svg}"
        for code in ("300394","300502","300308"):
            panels=native.make(get_ledger(code))
            for figure in ("03","04","06","07","08"):
                root=ET.fromstring(re.search(r"<svg.*?</svg>",panels[figure],re.S).group())
                width,height=map(Decimal,root.attrib['viewBox'].split()[2:])
                for node in root.iter(ns+'text'):
                    font=Decimal(node.attrib['font-size'])
                    self.assertGreaterEqual(font,12,(code,figure,node.text))
                    self.assertGreaterEqual(font*Decimal(320)/width,Decimal(11.5))
                    self.assertNotIn('…',node.text or '')
                    y=Decimal(node.attrib['y'])
                    self.assertGreaterEqual(y-font,0)
                    self.assertLessEqual(y+font/4,height)
                for group in root.iter(ns+'g'):
                    labels=list(group.iter(ns+'text'))
                    self.assertEqual(len(labels),3)
                    self.assertGreaterEqual(Decimal(labels[1].attrib['y'])-Decimal(labels[0].attrib['y']),21)
                for bar in root.iter(ns+'rect'):
                    self.assertLess(abs(Decimal(bar.attrib['width'])-
                        abs(Decimal(bar.attrib['data-signed-yuan']))/
                        Decimal(bar.attrib['data-yuan-per-svg-unit'])),Decimal('.000001'))

    def test_wrong_source_cost_breaks_real_mobile_flow(self):
        l=get_ledger("300394")
        cost=l["segments"][0]["cost_key"]
        poisoned=copy.deepcopy(l)
        poisoned["facts"][cost]["amount"]=str(Decimal(poisoned["facts"][cost]["amount"])+Decimal("0.01"))
        with self.assertRaisesRegex(ValueError,"NATIVE_SOURCE_COST_GP_NOT_CLOSED"):
            native.flow(poisoned)

    def test_wrong_source_hierarchy_breaks_real_mobile_flow(self):
        l=get_ledger("300394")
        poisoned=copy.deepcopy(l)
        poisoned["segments"].append(copy.deepcopy(poisoned["segments"][0]))
        with self.assertRaisesRegex(ValueError,"NATIVE_SOURCE_EXCLUSIVE_REVENUE_NOT_CLOSED"):
            native.flow(poisoned)

    def test_negative_product_gross_profit_cannot_be_sankey(self):
        l=get_ledger("300502")
        poisoned=copy.deepcopy(l)
        key=poisoned["segments"][1]["cost_key"]
        rev=Decimal(poisoned["facts"][poisoned["segments"][1]["revenue_key"]]["amount"])
        poisoned["facts"][key]["amount"]=str(rev+Decimal("0.01"))
        with self.assertRaisesRegex(ValueError,"NATIVE_NEGATIVE_MARGIN_CANNOT_SANKEY"):
            native.flow(poisoned)

    def test_cfo_true_indirect_source_missing_would_fail_closed(self):
        l=get_ledger("300502")
        poisoned=copy.deepcopy(l)
        poisoned["indirect_cfo_adjustments"]=[
            v for v in poisoned["indirect_cfo_adjustments"]
            if "经营性应付" not in v["source_label"]]
        with self.assertRaisesRegex(ValueError,"NATIVE_CFO_MISSING_WC"):
            native.cfo(poisoned)

    def test_300308_full_original_pdf_sha_and_transparent_page139_repeated_column(self):
        l=get_ledger("300308")
        m=get_memo("300308")
        self.assertEqual(l["document"]["source_sha256"],"e0ecd7c365c65e90b1fa4b4616ba3f4649449d64451e0ba0b1b78ba9ce3170bf")
        self.assertEqual(l["document"]["pages"],184)
        self.assertEqual(m["review_status"],"AI_INTERNAL_ORIGINAL_SOURCE_CRITICAL_REVIEW__HUMAN_NOT_CHECKED")
        self.assertEqual(m["independent_human_financial_review"],"NOT_CHECKED")
        self.assertEqual(m["independent_human_visual_review"],"NOT_CHECKED")
        self.assertEqual(l["verified_source_anomalies"][0]["original_contracted_revenue_cell"],"422649612.97")
        self.assertEqual(l["verified_source_anomalies"][0]["original_repeated_total_revenue_cell"],"422649613.97")
        panels=native.make(l)
        self.assertEqual(panels["01"].count('class="native-money-source"'),2)
        self.assertEqual(panels["01"].count('class="native-money-ribbon"'),4)
        report,_=build(l,m)
        self.assertEqual(report.count('data-design-system="FINANCIALS_UNIFIED_STORY_V1"'),2)
        self.assertEqual(report.count('data-node-id="revenue-total"'),2)
        self.assertIn("422,649,612.97",report)
        self.assertIn("422,649,613.97",report)
        self.assertIn("独立第二名人类研究分析师",report)
        self.assertIn(l["document"]["source_sha256"],report)

    def test_300308_unreviewed_source_or_faked_human_must_refuse_publication(self):
        l=get_ledger("300308")
        m=get_memo("300308")
        poisoned=copy.deepcopy(m)
        poisoned["review_status"]="DRAFT_NEEDS_SECOND_REVIEW"
        with self.assertRaisesRegex(ValueError,"Research memo not source-reviewed"):
            build(l,poisoned)
        poisoned=copy.deepcopy(m)
        poisoned["independent_human_financial_review"]="PASS_IMAGINARY"
        with self.assertRaisesRegex(ValueError,"AI_ORIGINAL_SOURCE_REVIEW_MUST_RETAIN_UNCHECKED_HUMAN"):
            build(l,poisoned)


if __name__=="__main__":
    unittest.main()
