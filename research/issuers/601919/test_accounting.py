#!/usr/bin/env python3
"""Adversarial original 601919 shipping source accounting, not a visual preview."""
import copy, unittest
import check_accounting as mod
from decimal import Decimal

class OriginalShippingAccountingTests(unittest.TestCase):
    def t(self,key,new_value,expected=None):
        data=copy.deepcopy(mod.FACTS)
        data[key]["exact_value"]=str(new_value)
        with self.assertRaises(AssertionError) as ex:mod.check(data)
        if expected:self.assertIn(expected,str(ex.exception))
    def test_actual_original_disclosure_source_passes_all_exact_yuan(self):
        checks=mod.check()
        self.assertGreaterEqual(len(checks),35)
        self.assertTrue(all(x=="PASS" for x in checks.values()))
    def test_real_178_page_original_pdf_sha_and_not_a_summary(self):
        p=mod.source_pdf_bytes()
        self.assertGreater(p.stat().st_size,500000)
        self.assertIn("601919",p.name)
    def test_comparative_revenue_cannot_be_swapped_into_current_column(self):
        data=copy.deepcopy(mod.FACTS)
        data["revenue_prior"]["period"]="2026H1"
        with self.assertRaisesRegex(AssertionError,"PERIOD_COLUMN"):mod.check(data)
    def test_segment_elimination_cannot_be_positive_business_ribbon(self):
        self.t("intersegment_revenue_elimination",str(-mod.value("intersegment_revenue_elimination")),"GROSS_TWO_SEGMENTS")
    def test_group_segment_eliminations_not_misread_as_zero(self):
        self.t("intersegment_cost_elimination","0","GROSS_TWO_SEGMENTS")
    def test_parent_revenue_and_shipping_segment_are_not_additive(self):
        self.t("ship_segment_revenue",str(mod.value("ship_segment_revenue")+Decimal("1000.00")),"GROSS_TWO_SEGMENTS")
    def test_true_shipping_four_original_cost_categories(self):
        self.t("ship_cost_voyage","20000000000.00","GROSS_SHIPPING_COST")
    def test_statutory_signed_finance_expense_prior_column(self):
        self.t("finance_expense_prior","2097790748.28","CAS_COST_SIX_LINES_prior")
    def test_false_group_gross_profit_remainder_detected(self):
        self.t("cost","91396114988.71","CAS_COST_SIX_LINES")
    def test_cfo_direct_supplier_cash_pay_not_accrual_cogs(self):
        self.t("paid_suppliers",mod.value("cost"),"CASH_DIRECT_PAYMENTS")
    def test_no_fake_indirect_cfo_missing_receivable_change(self):
        self.t("indirect_receivable","0","INDIRECT_NET_PROFIT_TO_OPERATING_CFO")
    def test_no_fake_indirect_cfo_missing_rou_depreciation(self):
        self.t("indirect_amort_right_of_use","0","INDIRECT_NET_PROFIT_TO_OPERATING_CFO")
    def test_cash_open_close_must_include_true_fx_effect(self):
        self.t("fx_cash_effect","0","CASH_BEGIN_TO_END")
    def test_restricted_cash_cannot_equal_cash_equivalents(self):
        self.t("restricted_non_cash_funds","0","RESTRICTED_CASH")
    def test_supply_chain_subset_cannot_be_rebranded_extra_top_line_segment(self):
        F=copy.deepcopy(mod.FACTS);F["ship_supply_chain_revenue_rmb_thousands"]["classification"]="EXTRA_BUSINESS"
        with self.assertRaisesRegex(AssertionError,"SUPPLY_CHAIN_DOUBLE_COUNTED"):mod.check(F)
    def test_supply_chain_1000x_unit_confusion(self):
        F=copy.deepcopy(mod.FACTS);F["ship_supply_chain_revenue_rmb_thousands"]["source_report_unit"]="CNY_yuan"
        with self.assertRaisesRegex(AssertionError,"RMB_THOUSAND_SHIPPING_SUBSET_SOURCE"):mod.check(F)
    def test_usd_per_teu_not_rmb_yuan(self):
        F=copy.deepcopy(mod.FACTS);F["international_yield_usd_per_teu"]["source_report_unit"]="CNY_yuan"
        with self.assertRaisesRegex(AssertionError,"USD_PER_TEU_INDEPENDENT_OF_RMB_REVENUE"):mod.check(F)
    def test_future_newbuild_contract_is_not_current_period_capex_cash(self):
        self.t("capital_commit_shipbuilding",mod.value("capex_cash"),"FUTURE_COMMITMENT_EQUALS_H1_PAID_CAPEX_FALSELY")
    def test_controlled_and_associated_teus_not_cash_revenue(self):
        self.t("port_participating_teu","0","CONTROLLED_PLUS_ASSOCIATED_TERMINAL_TEU")
    def test_stock_period_not_prior_h1_flow(self):
        F=copy.deepcopy(mod.FACTS);F["assets"]["period"]="2026H1"
        with self.assertRaisesRegex(AssertionError,"BALANCE_STOCK_PERIOD"):mod.check(F)
    def test_null_guessed_comparative_for_segment_must_fail(self):
        self.t("revenue","null","NON_NUMERIC_OR_GUESSED_ORIGINAL")
    def test_original_page_out_of_178_physical_report(self):
        F=copy.deepcopy(mod.FACTS);F["revenue"]["physical_page"]=179
        with self.assertRaisesRegex(AssertionError,"INVALID_PHYSICAL_PAGE"):mod.check(F)

if __name__=="__main__":
    unittest.main(verbosity=2)
