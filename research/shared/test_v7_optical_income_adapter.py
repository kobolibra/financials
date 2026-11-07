"""Two actual V7 optical ledgers must compile into canonical source-conserved Sankey."""
import copy
import json
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
from decimal import Decimal as D

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"research/shared"))
from v7_optical_income_adapter import optical_flow_plan,render_optical_candidate

FIXTURES=(
    "skills/ashare-financial-storytelling/v7/engine/sample-ledger.json",
    "skills/ashare-financial-storytelling/v7/examples/xinyisheng-2026H1-ledger.json",
    "skills/ashare-financial-storytelling/v7/examples/zhongji-2026H1-ledger.json",
)
SVG="{http://www.w3.org/2000/svg}"

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf8"))


class RealOpticalSankeyMigrationContract(unittest.TestCase):
    def test_two_independent_real_original_ledgers_desktop_and_mobile(self):
        for path in FIXTURES:
            with self.subTest(fixture=path):
                ledger=load(path)
                plan=optical_flow_plan(ledger)
                total=plan.check()
                self.assertEqual(total,D(ledger["facts"]["revenue"]["amount"]))
                self.assertEqual(len(plan.sources),len(ledger["segments"]))
                for mobile in (False,True):
                    svg=ET.fromstring(render_optical_candidate(ledger,mobile=mobile))
                    self.assertEqual(svg.get("data-design-system"),"FINANCIALS_UNIFIED_STORY_V1")
                    self.assertEqual(svg.get("data-revenue-yuan"),str(total))
                    self.assertEqual(svg.get("data-layout"),"mobile-editorial" if mobile else "desktop-editorial")
                    ribbons=[v for v in svg.iter(SVG+"path") if v.get("data-ribbon-yuan")]
                    incoming=[p for p in ribbons if p.get("data-stage")=="source-to-revenue"]
                    outgoing=[p for p in ribbons if p.get("data-stage")=="revenue-to-outcome"]
                    self.assertEqual(sum((D(p.get("data-ribbon-yuan")) for p in incoming),D(0)),total)
                    self.assertEqual(sum((D(p.get("data-ribbon-yuan")) for p in outgoing),D(0)),total)
                    self.assertEqual(len(outgoing),2*len(ledger["segments"]))
                    self.assertEqual(len([p for p in svg.iter(SVG+"rect") if p.get("data-node-id")=="revenue-total"]),1)
    def test_300308_one_yuan_repeated_column_must_never_become_a_source(self):
        ledger=load(FIXTURES[-1])
        self.assertEqual(ledger["document"]["pages"],184)
        self.assertEqual(ledger["verified_source_anomalies"][0]["physical_page"],139)
        self.assertEqual(optical_flow_plan(ledger).check(),
                         D(ledger["facts"]["revenue"]["amount"]))
        bad=copy.deepcopy(ledger)
        bad["facts"]["other_product_revenue"]["amount"]="422649613.97"
        with self.assertRaisesRegex(ValueError,"OPTICAL_ONE_YUAN_ALTERNATE_COLUMN_CANNOT_ENTER_SANKEY"):
            optical_flow_plan(bad)
        bad=copy.deepcopy(ledger)
        bad["verified_source_anomalies"][0]["source_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"OPTICAL_ORIGINAL_PDF_DISCREPANCY_NOT_SOURCED"):
            optical_flow_plan(bad)

    def test_reject_fabricated_or_cross_period_cost_revenue(self):
        for path in FIXTURES:
            with self.subTest(fixture=path):
                good=load(path);key=good["segments"][0]["cost_key"]
                bad=copy.deepcopy(good)
                bad["facts"][key]["amount"]=str(D(bad["facts"][key]["amount"])+1)
                with self.assertRaisesRegex(ValueError,"OPTICAL_SEGMENT_COGS_NOT_EXHAUSTIVE"):
                    optical_flow_plan(bad)
                bad=copy.deepcopy(good)
                bad["facts"][key]["period"]="2025H1"
                with self.assertRaisesRegex(ValueError,"OPTICAL_FACT_PERIOD_SCOPE_OR_KIND_MISMATCH"):
                    optical_flow_plan(bad)
                bad=copy.deepcopy(good)
                bad["segments"].append(copy.deepcopy(bad["segments"][0]))
                with self.assertRaisesRegex(ValueError,"OPTICAL_OVERLAPPING_OR_DUPLICATE_SOURCE_FACTS"):
                    optical_flow_plan(bad)
                bad=copy.deepcopy(good)
                bad["revenue_partition_assertion"]["completeness"]="UNKNOWN"
                with self.assertRaisesRegex(ValueError,"OPTICAL_EXHAUSTIVE_SOURCE_PARTITION_NOT_PROVEN"):
                    optical_flow_plan(bad)

if __name__=="__main__":
    unittest.main()
