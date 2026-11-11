"""Unseen synthetic boundary cases plus exact-byte real-issuer regression."""
from dataclasses import replace
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

from unified_income_sankey import FlowPlan,render_income_sankey
from editorial_financial_flow import FinanceFact,assess_financial_income_flow

ROOT=Path(__file__).resolve().parents[2]


def plan():
    return FlowPlan("unseen_issuer","TYPE_A_SOURCE_OWN_COST_GP","业务贡献","收入","成本与毛利",
        (("a","零收入业务","0"),("b","在营业务","100")),
        (("cost","成本","40","cost"),("gp","毛利","60","profit")),
        (("a","cost","0"),("a","gp","0"),("b","cost","40"),("b","gp","60")),
        "原始报告物理页1，停业业务收入成本均为零。",period="2027H1")


class IncomeGeneralizationTests(unittest.TestCase):
    def test_zero_revenue_has_no_fake_ribbon_or_margin_or_crash(self):
        for mobile in (False,True):
            svg=render_income_sankey(plan(),mobile=mobile,readable_source_rows=True)
            root=ET.fromstring(svg)
            self.assertIn("毛利率不适用",svg)
            ns={"s":"http://www.w3.org/2000/svg"}
            self.assertFalse(root.findall('.//s:path[@data-source-id="a"]',ns))
            self.assertEqual(D(root.find('.//s:rect[@data-node-id="a"]',ns).get("height")),0)
            self.assertNotIn("NaN",svg)
    def test_node_identity_roles_and_decimal_fail_closed(self):
        p=plan()
        cases=[replace(p,outcomes=(("cost","成本","40","cost"),("gp","毛利","60","cost"))),
               replace(p,sources=(("revenue-total","重复汇总","0"),("b","在营业务","100"))),
               replace(p,sources=((1,"机器数字键","0"),("b","在营业务","100"))),
               replace(p,sources=(("a","","0"),("b","在营业务","100"))),
               replace(p,sources=(("a","零收入","NaN"),("b","在营业务","100"))),
               replace(p,sources=(("a","零收入","missing"),("b","在营业务","100")))]
        for item in cases:
            with self.subTest(item=item),self.assertRaises(ValueError):item.check()
    def test_own_cost_requires_distinct_matching_classification(self):
        def f(key,n,**kwargs):
            return FinanceFact(key,n,"unseen","2027H1","operating_revenue","consolidated","CNY",1,**kwargs)
        src=[f("a","40"),f("b","60")]
        for costs in ({"a":f("same","20"),"b":f("same","20")},
                      {"a":f("ca","20",group_axis="geography"),"b":f("cb","20")}):
            with self.subTest(costs=costs),self.assertRaises(ValueError):
                assess_financial_income_flow(src,f("total","100"),f("cogs","40"),
                    costs_by_source=costs,individual_costs_disclosed=True)
        with self.assertRaises(ValueError):
            assess_financial_income_flow([replace(src[0],source_page=True),src[1]],f("total","100"),f("cogs","40"))
    def test_real_issuer_source_money_geometry_is_independent_of_readable_rows(self):
        from source_income_adapter import compile_disclosed_income
        for code in ('688220','600900','600276'):
            p=compile_disclosed_income(json.loads((ROOT/f'research/issuers/{code}/source-ledger.json').read_text()))
            for readable in (False,True):
                tree=ET.fromstring(render_income_sankey(p,mobile=True,embedded=True,readable_source_rows=readable))
                for r in tree.iter('{http://www.w3.org/2000/svg}rect'):
                    if r.get('data-node-yuan') is not None:
                        amount=D(r.get('data-node-yuan'))
                        self.assertGreaterEqual(amount,0)
                for path in tree.iter('{http://www.w3.org/2000/svg}path'):
                    if path.get('data-ribbon-yuan') is not None:
                        self.assertGreater(D(path.get('data-ribbon-yuan')),0)
                        scale=D(path.get('data-scale-yuan-per-svg-unit'))
                        self.assertGreater(scale,0)
                        import re
                        coords=[D(n) for n in re.findall(r'-?\d+(?:\.\d+)?',path.get('d'))]
                        self.assertEqual(len(coords),16)
                        expected=D(path.get('data-ribbon-yuan'))/scale
                        self.assertLess(abs(abs(coords[15]-coords[1])-expected),D('.001'))
                        self.assertLess(abs(abs(coords[9]-coords[7])-expected),D('.001'))
                self.assertNotIn('NaN',ET.tostring(tree,encoding='unicode'))


if __name__=="__main__":unittest.main()
