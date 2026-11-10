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
    def test_current_real_issuers_retain_byte_identical_svg(self):
        # Frozen pre-fix SVG bytes: protect valid existing source output.
        expected={'688220:False:False': 'f9c8f35d624eaeb8afe98d5afcb5d332c1efa3d393fa2c2abf36a3b294936432', '688220:False:True': 'f9c8f35d624eaeb8afe98d5afcb5d332c1efa3d393fa2c2abf36a3b294936432', '688220:True:False': '39a6a87525da5f4b89cca8f467e2ee4fd95c6dc37bad8cffcff4e655f0ab9d3e', '688220:True:True': 'ba226349913c46e00192b15882c91f7447ccd676971a8ef21cfc5f90201c5dd3', '600900:False:False': '176fcfa145c02dce6f1acf3f295d412978eda737ab723228c765cb34251ee361', '600900:False:True': '176fcfa145c02dce6f1acf3f295d412978eda737ab723228c765cb34251ee361', '600900:True:False': '89530b4da692c324500b5796078d31e8b71427345d9c11e180a9857c37d36a84', '600900:True:True': '3db7f6f948b3cd85f2eeb1bfb9b2417209cd44c3cffc7aa90377184f15d2a9af', '600276:False:False': 'c9f97ad7fed0a247e934e1eb65ba95904a23825ebd4da59c14422fc90fd7a255', '600276:False:True': 'c9f97ad7fed0a247e934e1eb65ba95904a23825ebd4da59c14422fc90fd7a255', '600276:True:False': 'ecd819dad1c902825abcb21bff5b39ef16f59ef8341bad980c06491f23677f06', '600276:True:True': '363b44a87e3aef3dbbcdcece61cb3447e862f036dd75d27160bd5319accf8788'}
        from source_income_adapter import compile_disclosed_income
        for code in ("688220","600900","600276"):
            p=compile_disclosed_income(json.loads((ROOT/f"research/issuers/{code}/source-ledger.json").read_text()))
            for mobile in (False,True):
                for readable in (False,True):
                    digest=hashlib.sha256(render_income_sankey(p,mobile=mobile,embedded=True,
                        readable_source_rows=readable).encode()).hexdigest()
                    self.assertEqual(digest,expected[f"{code}:{mobile}:{readable}"])


if __name__=="__main__":unittest.main()
