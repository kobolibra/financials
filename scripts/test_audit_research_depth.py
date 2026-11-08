"""Hostile regression tests for source-bound analytical decision bridges."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_research_depth import ROOT, CODES, audit_repo, calculate, validate
from decimal import Decimal


def fixtures():
    read = lambda p: json.loads((ROOT / p).read_text(encoding="utf-8"))
    briefs = read("research/quality/pr35-hero-figure-briefs.json")
    ledgers = {
        c: read("research/rebuild-v10/input-ledgers/" + c + ".json")
        for c in CODES if c != "600036"
    }
    return briefs, ledgers, read("research/rebuild-v10/extras.json"), read("research/rebuild-v10/build-manifest.json")


class ResearchDepthSourceTests(unittest.TestCase):
    def test_real_four_source_bound_accounting_bridges(self):
        self.assertEqual(audit_repo(), [])

    def test_known_exact_source_arithmetic(self):
        self.assertEqual(calculate("GROSS_PROFIT_YOY_CHANGE", {
            "rev": Decimal("3313262599.20"),
            "cogs": Decimal("500458107.69"),
            "rev_prior": Decimal("2657121733.79"),
            "cogs_prior": Decimal("397720074.56"),
        }), Decimal("553402832.28"))
        self.assertEqual(calculate("OPERATING_CASH_YOY_CHANGE", {
            "cfo": Decimal("70690750119.06"),
            "cfo_prior": Decimal("13119061031.33"),
        }), Decimal("57571689087.73"))
        self.assertEqual(calculate("PARENT_VS_DEDUCTED_YOY_DIVERGENCE", {
            "parent_ni": Decimal("26446037000"),
            "parent_ni_prior": Decimal("26013690000"),
            "reg_ni": Decimal("19595179000"),
            "reg_ni_prior": Decimal("26235399000"),
        }), Decimal("7072567000"))
        self.assertEqual(calculate("BANK_NET_INTEREST_YOY_BRIDGE", {
            "interest_in": Decimal("172733000000"),
            "interest_in_prior": Decimal("177014000000"),
            "interest_out": Decimal("60711000000"),
            "interest_out_prior": Decimal("70929000000"),
            "nii": Decimal("112022000000"),
            "nii_prior": Decimal("106085000000"),
        }), Decimal("5937000000"))

    def test_altered_prior_period_fails_even_when_money_is_correct(self):
        args = fixtures()
        args[1]["688111"]["facts"]["rev_prior"]["period"] = "2026H1"
        self.assertIn("RESEARCH_PERIOD_COLUMN_DRIFT_688111_rev_prior", validate(*args))

    def test_off_by_one_yuan_bridge_fails(self):
        args = fixtures()
        args[0]["hero_figures"][0]["quantified_driver"]["expected_yuan"] = "553402833.28"
        self.assertIn("RESEARCH_QUANTIFIED_BRIDGE_NOT_RECONCILED_688111", validate(*args))

    def test_forged_original_pdf_hash_fails(self):
        args = fixtures()
        args[0]["hero_figures"][1]["quantified_driver"]["source_pdf_sha256"] = "0" * 64
        self.assertIn("RESEARCH_PDF_SHA_DRIFT_600519", validate(*args))

    def test_bank_double_subtraction_or_wrong_net_interest_fails(self):
        args = fixtures()
        args[2]["600036"]["nii"]["val"] = "172733000000"
        self.assertIn("RESEARCH_ACCOUNTING_FORMULA_INVALID_600036", validate(*args))

    def test_missing_actual_falsifier_fails(self):
        args = fixtures()
        args[0]["hero_figures"][2]["quantified_driver"]["next_disclosure_falsifier"] = "以后关注"
        self.assertIn("RESEARCH_DECISION_CHAIN_INCOMPLETE_000333_next_disclosure_falsifier", validate(*args))

    def test_independent_editorial_claim_without_review_fails(self):
        args = fixtures()
        args[0]["hero_figures"][3]["quantified_driver"]["independent_financial_review"] = "PASS"
        self.assertIn("RESEARCH_FAKE_INDEPENDENT_REVIEW_600036", validate(*args))

    def test_uncorroborated_causality_upgrade_fails(self):
        args = fixtures()
        args[0]["hero_figures"][0]["quantified_driver"]["causality_status"] = "CAUSALLY_PROVEN"
        self.assertIn("RESEARCH_UNSUPPORTED_CAUSAL_CERTIFICATION_688111", validate(*args))


if __name__ == "__main__":
    unittest.main()
