"""Hostile original-PDF source tests for reader-visible V7 optical decisions."""
from __future__ import annotations

import copy
from decimal import Decimal as D
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
ENGINE = ROOT / "skills/ashare-financial-storytelling/v7/engine"
sys.path.insert(0, str(ENGINE))
from quantified_optical_decision import CONFIG, decision_values, render_optical_decision
from render_v7 import build


def data(code):
    if code == "300394":
        l, m = ENGINE/"sample-ledger.json", ENGINE/"sample-memo.json"
    elif code == "300502":
        l = ENGINE.parent/"examples/xinyisheng-2026H1-ledger.json"
        m = ENGINE.parent/"examples/xinyisheng-2026H1-memo.json"
    else:
        raise ValueError(code)
    return json.loads(l.read_text()), json.loads(m.read_text())


class DecisionReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.section = []
        self.rows = []
        self.metrics = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section" and a.get("id") == "quantified-decision":
            self.section.append(a)
        if tag == "tr" and a.get("data-fact-id"):
            self.rows.append(a)
        if a.get("class") == "optical-decision-metric":
            self.metrics.append(a)


class DecisionTests(unittest.TestCase):
    def test_source_bound_analysis_is_reader_visible_and_all_rows_original(self):
        for code in CONFIG:
            with self.subTest(code=code):
                l,m = data(code)
                d = decision_values(l)
                panel = render_optical_decision(l, m)
                parser = DecisionReader()
                parser.feed(panel)
                self.assertEqual(len(parser.section), 1)
                self.assertEqual(parser.section[0]["data-original-pdf-sha256"],
                                 l["document"]["source_sha256"])
                self.assertEqual(parser.section[0]["data-accounting-not-causal"], "true")
                self.assertEqual(parser.section[0]["data-issuer"], code)
                self.assertEqual(len(parser.metrics), 3)
                self.assertEqual(len(parser.rows), 8)
                self.assertEqual(set(x["data-fact-id"] for x in parser.rows),
                                 set(k for k,_,_,_ in CONFIG[code]))
                for row in parser.rows:
                    key = row["data-fact-id"]
                    original = l["facts"][key]
                    spec = next(v for v in CONFIG[code] if v[0]==key)
                    self.assertEqual(row["data-period"], spec[1])
                    self.assertEqual(row["data-statement-kind"], spec[2])
                    self.assertEqual(row["data-source-unit"], spec[3])
                    self.assertEqual(int(row["data-physical-page"]), original["page"])
                    self.assertEqual(D(row["data-original-value"]), D(original["amount"]))
                    self.assertIn("#page="+str(original["page"]),panel)
                self.assertIn("下一期可推翻",panel)
                self.assertIn("NOT_CHECKED",panel)
                self.assertIn("公开下载 URL 的字节等价未独立验证",panel)
                html,_ = build(l,m)
                self.assertEqual(html.count('id="quantified-decision"'),1)
                self.assertEqual(html.count('data-research-schema="financials.optical_decision.v1"'),1)
                self.assertIn(panel,html)

    def test_percentage_formulas_use_disclosed_original_decimal_money(self):
        l,_ = data("300394")
        x = {k:D(v["amount"]) for k,v in l["facts"].items() if v.get("amount") is not None}
        d = dict((k,v) for k,_,v in decision_values(l)["metrics"])
        gp = x["revenue"]-x["cogs"]
        prior = x["revenue_prior"]-x["cogs_prior"]
        self.assertEqual(d["gross_profit_yoy"],(gp-prior)/prior*D(100))
        self.assertEqual(d["cfo_yoy"],(x["cfo"]-x["cfo_prior"])/x["cfo_prior"]*D(100))
        self.assertEqual(d["inventory_since_year_end"],
                         (x["inventory"]-x["inventory_prior"])/x["inventory_prior"]*D(100))
        l,_ = data("300502")
        x = {k:D(v["amount"]) for k,v in l["facts"].items() if v.get("amount") is not None}
        d = dict((k,v) for k,_,v in decision_values(l)["metrics"])
        avg = x["revenue_optics"]/(x["product_volume_wan"]*D(10000))
        avg_prior = x["product_revenue_prior"]/(x["product_volume_wan_prior"]*D(10000))
        self.assertEqual(d["mixed_product_revenue_per_disclosed_unit"],
                         (avg-avg_prior)/avg_prior*D(100))
        self.assertEqual(d["cfo_to_net_profit"],x["cfo"]/x["net_profit"]*D(100))
        self.assertEqual(d["inventory_since_year_end"],
                         (x["inventory"]-x["inventory_prior"])/x["inventory_prior"]*D(100))

    def test_poisoned_period_kind_page_and_mixed_unit_block_publication(self):
        for code in CONFIG:
            l,m = data(code)
            item = CONFIG[code][0][0]
            for field, bad in [("period","2024H1"),("kind","stock"),
                               ("scope","parent"),("page",0),
                               ("status","estimated"),
                               ("source_confidence","not_checked")]:
                bad_ledger = copy.deepcopy(l)
                bad_ledger["facts"][item][field] = bad
                with self.subTest(code=code,field=field):
                    with self.assertRaisesRegex(ValueError,"DECISION_ORIGINAL_FACT_PROVENANCE_INVALID"):
                        render_optical_decision(bad_ledger,m)
            bad_ledger = copy.deepcopy(l)
            bad_ledger["facts"][item]["amount"] = "NaN"
            with self.assertRaisesRegex(ValueError,"DECISION_ORIGINAL_AMOUNT_NONFINITE"):
                render_optical_decision(bad_ledger,m)
            bad_ledger = copy.deepcopy(l)
            bad_ledger["document"]["audited"] = True
            with self.assertRaisesRegex(ValueError,"DECISION_PDF_IDENTITY_OR_AUDIT_SCOPE"):
                render_optical_decision(bad_ledger,m)
            bad_memo = copy.deepcopy(m)
            bad_memo["review_status"] = "DRAFT_NEEDS_SECOND_REVIEW"
            with self.assertRaisesRegex(ValueError,"DECISION_MEMO_SOURCE_STATUS"):
                render_optical_decision(l,bad_memo)

        l,m = data("300502")
        bad_ledger = copy.deepcopy(l)
        bad_ledger["facts"]["product_volume_wan"]["amount"]="0"
        with self.assertRaisesRegex(ValueError,"DECISION_PRODUCT_VOLUME"):
            render_optical_decision(bad_ledger,m)
        bad_ledger = copy.deepcopy(l)
        bad_ledger["facts"]["inventory_prior"]["period"]="2025H1"
        with self.assertRaisesRegex(ValueError,"DECISION_ORIGINAL_FACT_PROVENANCE"):
            render_optical_decision(bad_ledger,m)
        bad_ledger = copy.deepcopy(l)
        bad_ledger["document"]["source_public_url_bytes_sha_verification"]="PASS_UNPROVEN"
        with self.assertRaisesRegex(ValueError,"DECISION_PUBLIC_PDF_EQUIVALENCE_STATUS_DRIFT"):
            render_optical_decision(bad_ledger,m)

    def test_pending_third_issuer_is_not_backfilled_without_source_review(self):
        for method in (decision_values,):
            led, _ = data("300394")
            led["document"]["ticker"]="300308.SZ"
            with self.assertRaisesRegex(ValueError,"DECISION_UNSUPPORTED_ISSUER_OR_PERIOD"):
                method(led)


if __name__=="__main__":
    unittest.main()
