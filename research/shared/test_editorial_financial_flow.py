"""Real-ledger and hostile cross-business-model semantic flow tests.

This proves only source-type classification on existing actual source values.
It is NOT a picture geometry/whole report or independent human certification.
"""
from __future__ import annotations
import json
import unittest
from pathlib import Path
from editorial_financial_flow import FinanceFact, FlowSemanticError, assess_financial_income_flow

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'research/rebuild-v10/input-ledgers'


def load(code):
    return json.loads((SRC/f'{code}.json').read_text(encoding='utf8'))['facts']


def fact(code, key, *, statement='operating_revenue', period='2026H1',
         group_axis='business', level='top', parent_id=None):
    row=load(code)[key]
    return FinanceFact(key,str(row['yuan']),code,period,statement,'consolidated','CNY',
                       int(row.get('page',1)),group_axis,level,parent_id)


class FinancialFlowSemanticTests(unittest.TestCase):
    def test_kingsoft_true_own_business_gp_must_be_type_a(self):
        code='688111'
        source_keys=['wps_personal','wps365','wps_software','other_rev']
        cost_keys=['wps_personal_cost','wps365_cost','wps_software_cost','other_cost']
        sources=[fact(code,k) for k in source_keys]
        costs={k:fact(code,v) for k,v in zip(source_keys,cost_keys)}
        d=assess_financial_income_flow(sources,fact(code,'rev'),fact(code,'cogs'),
                                       costs_by_source=costs,individual_costs_disclosed=True)
        self.assertEqual(d.kind,'TYPE_A_SOURCE_OWN_COST_GP')
        self.assertEqual(len(d.source_own_cost_gp),4)
        self.assertEqual(sum((__import__('decimal').Decimal(x[3]) for x in d.source_own_cost_gp)),
                         __import__('decimal').Decimal(d.exact_yuan_group_gp))
        self.assertEqual(d.width('0'),0)

    def test_kingsoft_weak_group_only_cannot_pass_as_best_figure(self):
        code='688111'
        sources=[fact(code,k) for k in ['wps_personal','wps365','wps_software','other_rev']]
        with self.assertRaisesRegex(FlowSemanticError,'OWN_COGS_DISCLOSED'):
            assess_financial_income_flow(sources,fact(code,'rev'),fact(code,'cogs'),
                                         individual_costs_disclosed=True)

    def test_moutai_negative_product_gp_prevents_positive_source_gp_ribbon(self):
        code='600519'
        source_keys=['maotai_rev','series_rev','other_rev']
        sources=[fact(code,k) for k in source_keys]
        costs={k:fact(code,v) for k,v in zip(source_keys,['maotai_cogs','series_cogs','other_cogs'])}
        d=assess_financial_income_flow(sources,fact(code,'rev'),fact(code,'cogs'),
                                       costs_by_source=costs,individual_costs_disclosed=True)
        self.assertEqual(d.kind,'TYPE_C_SANKEY_OMITTED')
        self.assertIn('NEGATIVE_GROSS_PROFIT',d.reason)

    def test_midea_exclusive_top_level_only_group_cost_type_b(self):
        code='000333'
        sources=[fact(code,k) for k in ['home','industrial_solution','other_total']]
        d=assess_financial_income_flow(sources,fact(code,'rev'),fact(code,'cogs'))
        self.assertEqual(d.kind,'TYPE_B_GROUP_ONLY_GROSS_ALLOCATION')
        self.assertEqual(d.reason,'PRODUCT_LEVEL_GP_NOT_ESTABLISHED')

    def test_hierarchy_duplication_is_rejected_before_sankey(self):
        code='000333'
        src=[fact(code,'home'),fact(code,'industrial_solution',parent_id='parent'),
             fact(code,'other_total')]
        with self.assertRaisesRegex(FlowSemanticError,'PARENT_AND_CHILD'):
            assess_financial_income_flow(src,fact(code,'rev'),fact(code,'cogs'))

    def test_prior_period_cannot_be_money_stream(self):
        code='688111'
        src=[fact(code,k) for k in ['wps_personal','wps365','wps_software']]
        src.append(fact(code,'other_rev',period='2025H1'))
        with self.assertRaisesRegex(FlowSemanticError,'PERIOD_CONSOLIDATION'):
            assess_financial_income_flow(src,fact(code,'rev'),fact(code,'cogs'))

    def test_renewal_premiums_not_cas_earned_revenue(self):
        a=FinanceFact('renewal','300','601628','2026H1','premium','consolidated','CNY',10)
        b=FinanceFact('new','200','601628','2026H1','premium','consolidated','CNY',10)
        total=FinanceFact('service_revenue','500','601628','2026H1','cas_service_revenue','consolidated','CNY',47)
        cost=FinanceFact('expense','100','601628','2026H1','cas_service_revenue','consolidated','CNY',47)
        with self.assertRaisesRegex(FlowSemanticError,'PERIOD_CONSOLIDATION'):
            assess_financial_income_flow([a,b],total,cost)

    def test_source_residual_must_not_become_other_business(self):
        code='000333'
        sources=[fact(code,k) for k in ['home','industrial_solution']]
        with self.assertRaisesRegex(FlowSemanticError,'SOURCE_SUM_NOT_ACTUAL_REVENUE'):
            assess_financial_income_flow(sources,fact(code,'rev'),fact(code,'cogs'))

    def test_bank_double_interest_expense_is_rejected(self):
        base={'issuer':'600036','period':'2026H1','statement':'bank_operating_income',
              'scope':'consolidated','currency':'CNY','source_page':58}
        def v(k,amt):return FinanceFact(id=k,yuan=amt,**base)
        with self.assertRaisesRegex(FlowSemanticError,'BANK_NET_INTEREST_DOUBLE_DEDUCTION'):
            assess_financial_income_flow([v('nii','70'),v('fees_net','30')],
                                          v('bank_operating_income','100'),v('interest_expense','20'))

    def test_zero_and_micro_flow_width_exact_no_minimum(self):
        code='688111'
        sources=[fact(code,k) for k in ['wps_personal','wps365','wps_software','other_rev']]
        d=assess_financial_income_flow(sources,fact(code,'rev'),fact(code,'cogs'))
        self.assertEqual(d.width('0','400'),0)
        self.assertLess(d.width('0.01','400'),__import__('decimal').Decimal('0.00000001'))


if __name__ == '__main__':
    unittest.main()
