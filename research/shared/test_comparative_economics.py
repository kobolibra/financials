"""Accounting attribution, not a causal or external-source certification."""
from dataclasses import replace
from decimal import localcontext
from fractions import Fraction
import unittest

from comparative_economics import EconomicsPeriod, gross_profit_bridge, money


def period(year,revenue,cost):
    return EconomicsPeriod("unseen_issuer",f"{year}H1",revenue,cost,"rev","cogs",2,3,
        "a"*64,10,"consolidated","CNY","yuan","industrial_operating_income",
        "operating revenue excluding finance-subsidiary interest and fees","DISCLOSED",
        f"{year}-01-01",f"{year}-06-30")


class ComparativeEconomicsTests(unittest.TestCase):
    def setUp(self):
        self.prior=period(2025,"100.00","70.00")
        self.current=period(2026,"150.00","90.00")
    def bridge(self,a=None,b=None):
        return gross_profit_bridge(a or self.prior,b or self.current,
            comparability_evidence="同一报告列示可比上年同期、同一合并口径与收入成本定义，重述另行保留。")
    def test_symmetric_interaction_is_split_not_hidden_in_residual(self):
        result=self.bridge()
        self.assertEqual([x["yuan"] for x in result["effects"]],["17.50","12.50"])
        self.assertEqual(result["delta_gp_yuan"],"30.00")
        self.assertEqual(result["display_rounding_yuan"],"0.00")
    def test_losses_declining_sales_and_turnaround_are_signed(self):
        for revenue,cost in (("80","100"),("50","10"),("100","100"),("150","180")):
            with self.subTest(revenue=revenue,cost=cost):
                r=self.bridge(b=period(2026,revenue,cost))
                exact=sum((Fraction(int(x["exact"]["numerator"]),int(x["exact"]["denominator"]))
                           for x in r["effects"]),Fraction(0))
                self.assertEqual(exact,money(r["delta_gp_yuan"]))
    def test_repeating_ratios_do_not_depend_on_decimal_context(self):
        with localcontext() as ctx:
            ctx.prec=4
            r=self.bridge(period(2025,"3","2"),period(2026,"7","3"))
        self.assertEqual(sum((money(x["yuan"]) for x in r["effects"]),money(r["display_rounding_yuan"])),money(r["delta_gp_yuan"]))
        self.assertEqual(r["interpretation"],"ACCOUNTING_DECOMPOSITION_NOT_CAUSAL")
    def test_unseen_scale_loss_and_margin_combinations_reconcile(self):
        import random
        rng=random.Random(20261110)
        for i in range(120):
            r0,r1=[str(rng.randint(1,10**16))+'.'+str(rng.randint(0,99)).zfill(2) for _ in range(2)]
            c0,c1=[str(rng.randint(0,10**16))+'.'+str(rng.randint(0,99)).zfill(2) for _ in range(2)]
            result=self.bridge(period(2025,r0,c0),period(2026,r1,c1))
            self.assertEqual(sum((Fraction(int(x['exact']['numerator']),int(x['exact']['denominator'])) for x in result['effects']),Fraction(0)),money(result['delta_gp_yuan']))
            self.assertEqual(sum((money(x['yuan']) for x in result['effects']),money(result['display_rounding_yuan'])),money(result['delta_gp_yuan']))
        with self.assertRaises(ValueError):self.bridge(b=period(2027,'150','90'))

    def test_source_and_comparability_poison_cases(self):
        changes=[{"issuer":"someone_else"},{"currency":"USD"},{"unit":"million_yuan"},
                 {"scope":"parent"},{"statement":"bank_operating_income"},
                 {"statement":"insurance_service_income"},{"revenue_yuan":"0"},
                 {"revenue_yuan":"NaN"},{"cost_yuan":"-1"},{"cost_yuan":"1.001"},
                 {"revenue_yuan":100.0},{"classification":"DERIVED"},
                 {"revenue_page":True},{"cost_page":11},{"pdf_sha256":"x"*64},
                 {"revenue_fact":"cogs"},{"definition":"total revenue includes financial interest"},
                 {"period_start":"2026-01-01","period_end":"2026-12-31"},
                 {"period":"2025H1"}]
        for change in changes:
            with self.subTest(change=change),self.assertRaises(ValueError):
                self.bridge(b=replace(self.current,**change))
        with self.assertRaises(ValueError):
            gross_profit_bridge(self.prior,self.current,comparability_evidence="")


if __name__=="__main__":unittest.main()
