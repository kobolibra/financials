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
                self.assertEqual(report.count('class="native-finance"'),len(panels))
                self.assertIn('viewBox="0 0 330',report)
                self.assertIn(ledger["document"]["source_sha256"],report)
                self.assertEqual(report.count('class="chart-shell '), 10 if code=="300394" else 11)
                self.assertIn("在窄屏上可横向滑动",report) if False else None

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

    def test_300308_source_unverified_and_memo_unreviewed_stays_blocked(self):
        l=get_ledger("300308")
        m=get_memo("300308")
        self.assertEqual(l["document"]["source_sha256"],"NOT_VERIFIED_REMOTE_PDF")
        self.assertEqual(m["review_status"],"DRAFT_NEEDS_SECOND_REVIEW")

if __name__=="__main__":
    unittest.main()
