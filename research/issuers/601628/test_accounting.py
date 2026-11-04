#!/usr/bin/env python3
"""Real original-filing insurer invariants and hostile wrong-grammar mutations."""
from __future__ import annotations
import unittest,sys
from decimal import Decimal
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
HERE=Path(__file__).resolve().parent
spec=spec_from_file_location("life_601628",HERE/"publish.py")
mod=module_from_spec(spec);spec.loader.exec_module(mod)
class LifeInsurance2026H1(unittest.TestCase):
    def test_original_original_cas_insurance_accounting(self):
        r=mod.check()
        self.assertEqual(len(r["checks"]),16)
        self.assertTrue(all(v=="PASS" for v in r["checks"].values()))
    def mutate(self,key,value):
        original=mod.FACTS[key]["yuan"]
        try:
            mod.FACTS[key]["yuan"]=str(value)
            with self.assertRaises((AssertionError,ValueError)):
                mod.check()
        finally:
            mod.FACTS[key]["yuan"]=original
    def test_premium_is_disjoint_and_no_fake_service_recognition(self):
        self.mutate("premium_total",str(int(mod.FACTS["service_revenue"]["yuan"])))
    def test_premium_new_and_renewal_cannot_overlap(self):
        self.mutate("premium_new",str(int(mod.FACTS["premium_new"]["yuan"])+1000000))
    def test_csm_is_stock_not_revenue(self):
        self.mutate("csm",str(int(mod.FACTS["service_csm_release"]["yuan"])))
    def test_insurer_direct_cfo_has_real_signed_claims(self):
        self.mutate("cfo_claims",str(-233887*1000000))
    def test_report_income_2026_comparative_swapped(self):
        self.mutate("service_revenue",str(int(mod.FACTS["service_revenue_prior"]["yuan"])))
    def test_insurance_finance_liability_cannot_be_ignored(self):
        self.mutate("insurance_finance","0")
    def test_insurer_consolidated_parent_profit_cannot_be_mixed(self):
        self.mutate("parent_net",str(int(mod.FACTS["net_profit"]["yuan"])))
    def test_balance_sheet_consolidated_not_parent(self):
        self.mutate("assets",str(7873637*1000000))
    def test_reported_premium_receipt_is_not_premium_kpi(self):
        self.mutate("cfo_insurance_cash",str(int(mod.FACTS["premium_total"]["yuan"])))
    def test_cash_close_no_static_bs_delta(self):
        self.mutate("cfi","0")
    def test_fairvalue_not_cash(self):
        self.mutate("fairvalue_income","0")
    def test_service_cost_2025_comparative_not_current(self):
        self.mutate("service_cost",str(int(mod.FACTS["service_cost_prior"]["yuan"])))
    def test_original_pdf_sha_not_unrelated_issuer(self):
        wrong=mod.FIG["source_sha256"]
        try:
            mod.FIG["source_sha256"]="ff6910663a9726acb889aa061a8bab1433f58890d81ebea013b8c637a097a7aa"
            with self.assertRaises(AssertionError):mod.check()
        finally:mod.FIG["source_sha256"]=wrong
    def test_no_fake_indirect_cash_bridge(self):
        self.assertEqual(mod.amount("net_profit"),Decimal(136003))
        self.assertEqual(mod.amount("cfo"),Decimal(282879))
        self.assertNotEqual(mod.amount("cfo"),mod.amount("net_profit"))
        self.assertEqual(mod.amount("cfo_in")+mod.amount("cfo_out"),mod.amount("cfo"))
if __name__=="__main__":unittest.main()
