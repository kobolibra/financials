"""Three source-original different industry income partitions use one strict v9 compiler."""
import copy
import json
import sys
import unittest
from decimal import Decimal as D
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"research/shared"))
from source_income_adapter import compile_disclosed_income,render_sector_income

def read(code):
    return json.loads((ROOT/f"research/issuers/{code}/source-ledger.json").read_text())
SVG="{http://www.w3.org/2000/svg}"
CODES=("688220","600900","600276")

class OriginalThreeSectorMoneyCompiler(unittest.TestCase):
    def test_three_different_industry_real_original_source_yuan_flows(self):
        for code in CODES:
            with self.subTest(code=code):
                ledger=read(code)
                plan=compile_disclosed_income(ledger)
                total=D(ledger["facts"]["rev"]["yuan"])
                self.assertEqual(total,plan.check())
                for mobile in (False,True):
                    svg=ET.fromstring(render_sector_income(ledger,mobile=mobile))
                    self.assertEqual(svg.get("data-design-system"),"FINANCIALS_UNIFIED_STORY_V1")
                    self.assertEqual(svg.get("data-editorial-placement"),"embedded-article")
                    self.assertEqual(D(svg.get("data-revenue-yuan")),total)
                    flows=[p for p in svg.iter(SVG+"path") if p.get("data-ribbon-yuan")]
                    inbound=[p for p in flows if p.get("data-stage")=="source-to-revenue"]
                    outbound=[p for p in flows if p.get("data-stage")=="revenue-to-outcome"]
                    self.assertEqual(len(inbound),len(ledger["segments"]))
                    self.assertEqual(sum((D(p.get("data-ribbon-yuan")) for p in inbound),D(0)),total)
                    self.assertEqual(sum((D(p.get("data-ribbon-yuan")) for p in outbound),D(0)),total)
                    self.assertEqual(len([x for x in svg.iter(SVG+"rect") if x.get("data-node-id")=="revenue-total"]),1)
                if code=="688220":
                    self.assertIn("字节等价尚未证明",plan.footnote)

    def test_reject_counterfeit_source_and_forged_per_segment_cost(self):
        for code in CODES:
            with self.subTest(code=code):
                good=read(code)
                bad=copy.deepcopy(good)
                bad["source"]["original_bytes_sha256"]="0"
                with self.assertRaisesRegex(ValueError,"ORIGINAL_COMPLETE_PDF_BYTES_NOT_PROVEN"):
                    compile_disclosed_income(bad)
                bad=copy.deepcopy(good)
                ck=bad["segments"][0]["cost"]
                bad["facts"][ck]["yuan"]=str(D(bad["facts"][ck]["yuan"])+D("1.00"))
                with self.assertRaisesRegex(ValueError,"NONEXHAUSTIVE_OR_MIXED"):
                    compile_disclosed_income(bad)
                bad=copy.deepcopy(good)
                bad["segments"].append(copy.deepcopy(bad["segments"][0]))
                with self.assertRaisesRegex(ValueError,"DUPLICATED_OR_OVERLAPPING"):
                    compile_disclosed_income(bad)
                bad=copy.deepcopy(good)
                rk=bad["segments"][0]["rev"]
                bad["facts"][rk]["period"]="2025H1"
                with self.assertRaisesRegex(ValueError,"ORIGINAL_TYPED_FACT_INCOMPATIBLE"):
                    compile_disclosed_income(bad)
                bad=copy.deepcopy(good)
                bad["segments"][0]["dimension"]="geography"
                with self.assertRaisesRegex(ValueError,"MIXED_BUSINESS_AND_GEOGRAPHY"):
                    compile_disclosed_income(bad)

if __name__=="__main__":
    unittest.main()
