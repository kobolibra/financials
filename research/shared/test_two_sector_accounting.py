#!/usr/bin/env python3
"""Hostile PDF-backed sector adaptation tests: two genuinely different filings."""
import unittest,copy,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("two_sector_engine",ROOT/"research/shared/build_two_sector.py")
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
class TwoRealSectorHostileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data={}
        for code in ("600900","600276"):
            base=ROOT/"research/issuers"/code
            cls.data[code]={
                "ledger":json.loads((base/"source-ledger.json").read_text()),
                "briefs":json.loads((base/"figure-briefs.json").read_text()),
                "story":json.loads((base/"story.json").read_text()),
                "pdf":ROOT/json.loads((base/"source-ledger.json").read_text())["source"]["source_path"]
            }
    def validate(self,code,mutate):
        x=self.data[code]; d=copy.deepcopy(x["ledger"]);mutate(d)
        return mod.check(d,x["briefs"],x["story"],x["pdf"])
    def test_real_utilities_source_periods_and_16_signed_CFO_items(self):
        self.assertGreaterEqual(len(mod.check(**{
            "d":self.data["600900"]["ledger"],"briefs":self.data["600900"]["briefs"],
            "story":self.data["600900"]["story"],"pdf_path":self.data["600900"]["pdf"]
        })),12)
        self.assertEqual(len(self.data["600900"]["ledger"]["cfo_adjustments"]),16)
        self.assertIn("追溯调整",self.data["600900"]["story"]["counter"])
        self.assertIn("水资源税", " ".join(self.data["600900"]["story"]["other_notes"]))
    def test_real_pharma_source_note_and_non_cash_split(self):
        x=self.data["600276"]
        assert "NONCASH_BILLS_MATERIAL_PLUS_CAPEX" in mod.check(x["ledger"],x["briefs"],x["story"],x["pdf"])
        self.assertEqual(len(x["ledger"]["cfo_adjustments"]),17)
        self.assertIn("2026年7月",x["story"]["counter"])
        self.assertIn("非现金结算"," ".join(x["story"]["other_notes"]))
    def test_operating_subgroup_and_physical_output_source_rules(self):
        hydro=copy.deepcopy(self.data["600900"]["ledger"])
        pharma=copy.deepcopy(self.data["600276"]["ledger"])
        self.assertEqual(mod.check_sector_operating_story(hydro)["conversion"],"NOT_ADDITIVE")
        self.assertEqual(mod.check_sector_operating_story(pharma)["classification"],
                         "MANAGEMENT_SUBSET_OF_GOODS_NOT_EXTRA_SALES")
        hydro["facts"]["power_gen_100m_kwh"]["unit"]="亿元"
        with self.assertRaisesRegex(AssertionError,"OPERATING_SOURCE_SEMANTIC_MISMATCH"):
            mod.check_sector_operating_story(hydro)
        pharma["facts"]["innovative_drug_sales_100m"]["yuan"]="999.99"
        with self.assertRaisesRegex(AssertionError,"OPERATING_INNOVATION_NOT_GOODS_SUBSET"):
            mod.check_sector_operating_story(pharma)
        pharma=copy.deepcopy(self.data["600276"]["ledger"])
        pharma["facts"]["innovative_drug_sales_100m"]["scope"]="parent"
        with self.assertRaisesRegex(AssertionError,"OPERATING_SOURCE_SEMANTIC_MISMATCH"):
            mod.check_sector_operating_story(pharma)
        pharma=copy.deepcopy(self.data["600276"]["ledger"])
        pharma["facts"]["rpo"]["type"]="flow"
        with self.assertRaisesRegex(AssertionError,"PHARMA_RPO_STOCK_NOT_DISJOINT_FROM_REVENUE"):
            mod.check_sector_operating_story(pharma)

    def test_shared_industry_art_has_no_hardcoded_research_metrics_or_dead_sankey(self):
        src=(ROOT/"research/shared/build_two_sector.py").read_text()
        self.assertNotIn('function sankey(){',src)
        self.assertNotIn('var innovation=88.09*N',src)
        self.assertNotIn('text(245,236,"1327.44"',src)
        self.assertIn('sourceOperatingValue("innovative_drug_sales_100m","亿元")',src)
        self.assertIn('sourceOperatingValue("power_gen_100m_kwh","亿千瓦时")',src)
        self.assertIn('data-subset-yuan=',src)

    def test_fake_pharma_innovative_sales_as_additional_disjoint_source_rejected(self):
        def wrong(d):
            d["segments"].append({"label":"创新药重复收入", "rev":"innovative_drug_sales_100m","cost":"drug_sales_cost","dimension":"contract_goods_type"})
        with self.assertRaisesRegex(AssertionError,"CROSS_DIMENSION_DUPLICATE_SEGMENT"):
            self.validate("600276",wrong)
    def test_fake_hydro_power_generation_as_invoice_amount_rejected(self):
        def wrong(d):
            d["segments"][0]["rev"]="power_gen_100m_kwh"
        with self.assertRaisesRegex(AssertionError,"NESTED_OR_WRONG_PERIOD_SEGMENT"):
            self.validate("600900",wrong)
    def test_2025_restated_comparative_marked_as_current_rejected(self):
        def wrong(d):
            d["facts"]["rev_prior"]["period"]="2026H1"
        with self.assertRaisesRegex(AssertionError,"COMPARATIVE_PRIOR_PERIOD_CHANGED"):
            self.validate("600900",wrong)
    def test_license_and_product_geography_duplicate_dimension_rejected(self):
        def wrong(d):
            d["segments"][-1]["dimension"]="geography"
        with self.assertRaisesRegex(AssertionError,"GROUPS_DIFFERENT_AXES"):
            self.validate("600276",wrong)
    def test_bill_endorsement_cash_spend_blend_rejected(self):
        def wrong(d):
            d["facts"]["bill_endorse_capex"]["yuan"]="0.00"
        with self.assertRaisesRegex(AssertionError,"SOURCE_LITERAL_NOT_ON_ACTUAL_PHYSICAL_PDF_PAGE|NONCASH_BILLS_MATERIAL_PLUS_CAPEX"):
            self.validate("600276",wrong)
    def test_full_indirect_cfo_sign_reversal_rejected(self):
        def wrong(d):
            d["facts"]["cfo_adj_payables"]["yuan"]=str(-mod.val(d,"cfo_adj_payables"))
        with self.assertRaises(AssertionError):
            self.validate("600276",wrong)
    def test_out_of_period_bms_milestone_not_shown_as_h1_income(self):
        x=self.data["600276"]
        contract=x["ledger"]["facts"]["licence_rev"]
        self.assertEqual(contract["page"],145)
        self.assertNotIn("BMS 6亿美元",contract["label"])
        self.assertIn("2026年7月",x["story"]["counter"])
        self.assertEqual(x["ledger"]["facts"]["rpo"]["page"],146)

if __name__=="__main__":
    unittest.main()
