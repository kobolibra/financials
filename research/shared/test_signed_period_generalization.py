"""Unseen synthetic issuer/period tests, not real-company research certification."""
from dataclasses import replace
from decimal import Decimal as D
import copy
import random
import unittest
import xml.etree.ElementTree as ET
from signed_statement_waterfall import SignedStage, SignedStatement, render_signed_statement


def fixture(issuer, period, revenue, cost, expense):
    gross=revenue-cost
    values={'revenue':revenue,'cost':cost,'expense':expense,'net':gross-expense}
    facts={k:{'yuan':str(v),'period':period,'scope':'consolidated','unit':'元',
              'currency':'CNY','issuer':issuer,'page':i+1} for i,(k,v) in enumerate(values.items())}
    plan=SignedStatement(issuer,'income', 'a'*64,'ORIGINAL_PDF_SHA256_VERIFIED',
         '毛利润',gross,('revenue','cost'),
         (SignedStage('gross','毛利润',gross,('revenue','cost'),'base'),
          SignedStage('expense','费用',-expense,('expense',))),(), 'net',gross-expense,period=period)
    return plan,facts


class SignedPeriodGeneralization(unittest.TestCase):
    def test_unseen_issuers_periods_scales_and_negative_positions(self):
        rng=random.Random(20261112)
        for i in range(60):
            issuer=f'synthetic_unseen_{i}'
            period=f'{2027+i//4}Q{1+i%4}'
            revenue=D(rng.randrange(1,10**12))/100
            cost=D(rng.randrange(0,10**12))/100
            expense=D(rng.randrange(-10**11,10**12))/100
            plan,facts=fixture(issuer,period,revenue,cost,expense)
            for mobile in (False,True):
                with self.subTest(issuer=issuer,period=period,mobile=mobile):
                    svg=ET.fromstring(render_signed_statement(plan,facts,mobile=mobile))
                    self.assertEqual(svg.get('data-period'),period)
                    self.assertEqual(svg.get('data-issuer'),issuer)
                    for bar in svg.findall('.//{http://www.w3.org/2000/svg}rect'):
                        before=D(bar.get('data-before-yuan'));after=D(bar.get('data-after-yuan'))
                        delta=D(bar.get('data-signed-yuan'));scale=D(bar.get('data-money-scale-yuan-per-unit'))
                        self.assertEqual(after-before,delta)
                        self.assertLess(abs(D(bar.get('width'))-abs(delta)/scale),D('0.0000001'))
    def test_borrowed_period_issuer_currency_scope_and_page_fail(self):
        plan,facts=fixture('new_company','2031H2',D(100),D(60),D(70))
        for field,value in [('period','2026H1'),('issuer','another_company'),('currency','USD'),
                            ('scope','parent'),('page',True),('yuan','NaN')]:
            with self.subTest(field=field),self.assertRaises(ValueError):
                bad=copy.deepcopy(facts);bad['expense'][field]=value;plan.check(bad)
        for value in ('',' ',None):
            with self.subTest(period=value),self.assertRaises(ValueError):replace(plan,period=value).check(facts)
    def test_period_change_requires_all_source_facts_to_change(self):
        plan,facts=fixture('new_company','2028FY',D(100),D(60),D(70))
        with self.assertRaises(ValueError):replace(plan,period='2029FY').check(facts)
        for row in facts.values():row['period']='2029FY'
        self.assertEqual(replace(plan,period='2029FY').check(facts)[-1][2],D(-30))

if __name__=='__main__':unittest.main()
