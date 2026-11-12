"""Insurance-specific true Sankey is not industrial revenue/COGS and no tiny fake ribbon."""
import copy,json,sys,unittest
from pathlib import Path
from decimal import Decimal as D
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"research/shared"))
from unified_insurance_premium import render_insurance_premium
def load():
    return json.loads((ROOT/"research/issuers/601628/source-ledger.json").read_text())
SVG="{http://www.w3.org/2000/svg}"
class RealOriginalChinaLifePremium(unittest.TestCase):
    def test_actual_pdf_p10_insurance_not_cash_or_service(self):
        data=load()
        self.assertNotEqual(data["facts"]["premium_total"]["yuan"],data["facts"]["service_revenue"]["yuan"])
        for mobile in (False,True):
            svg=ET.fromstring(render_insurance_premium(data,mobile=mobile))
            self.assertEqual(svg.get("data-design-system"),"FINANCIALS_UNIFIED_STORY_V1")
            self.assertEqual(svg.get("data-chart-grammar"),"INSURANCE_PREMIUM_SOURCE_NEW_RENEW_TOTAL")
            self.assertEqual(D(svg.get("data-premium-yuan")),D("536634000000"))
            self.assertIsNone(svg.get("data-revenue-yuan"))
            self.assertEqual(D(svg.get("viewBox").split()[2]),D(330 if mobile else 1100))
            nodes=[x for x in svg.iter(SVG+"rect") if x.get("data-node-id")]
            paths=[x for x in svg.iter(SVG+"path") if x.get("data-ribbon-yuan")]
            self.assertEqual(len(nodes),7)
            self.assertEqual(len(paths),6)
            self.assertEqual(len([n for n in nodes if n.get("data-node-id")=="premium-total"]),1)
            for stage in ("premium-source-to-new-or-renew","new-or-renew-to-premium-total"):
                self.assertEqual(sum((D(p.get("data-ribbon-yuan")) for p in paths if p.get("data-stage")==stage),D(0)),D("536634000000"))
            self.assertNotIn("营业成本",ET.tostring(svg,encoding="unicode"))
    def test_unseen_insurer_period_and_explicit_source_page_profile(self):
        # Synthetic schema transfer, not a second real insurance source audit.
        data=load();data['issuer'].update(code='999998',short='示例寿险',fiscal_period='2031H1',accounting_route='insurance_premium_statistics')
        data['source'].update(physical_pages_observed=130,original_bytes_gate='ORIGINAL_PDF_SHA256_VERIFIED')
        data['insurance_premium_profile']={'basis':'MANAGEMENT_LEGACY_PREMIUM_STATISTICS_NOT_CAS25','source_taxonomy':'FIRST_REGULAR_SINGLE_SHORT_RENEW','service_basis':'CAS25_INSURANCE_SERVICE_REVENUE','period':'2031H1','scope':'consolidated','premium_physical_pages':[12],'service_physical_pages':[44]}
        for key in ('premium_first_regular','premium_single','premium_short','premium_renew','premium_new','premium_total'):
            data['facts'][key].update(page=12,period='2031H1')
        data['facts']['service_revenue'].update(page=44,period='2031H1')
        for mobile in (False,True):
            root=ET.fromstring(render_insurance_premium(data,mobile=mobile))
            self.assertEqual(root.get('data-issuer'),'999998');self.assertEqual(root.get('data-period'),'2031H1')
            self.assertNotIn('中国人寿',ET.tostring(root,encoding='unicode'))
        same_value=copy.deepcopy(data);same_value['facts']['service_revenue']['yuan']=same_value['facts']['premium_total']['yuan']
        self.assertIsNotNone(ET.fromstring(render_insurance_premium(same_value)))
        fake=copy.deepcopy(data);fake['insurance_premium_profile']['premium_physical_pages']=[True]
        with self.assertRaises(ValueError):render_insurance_premium(fake)
        fake=copy.deepcopy(data);fake['insurance_premium_profile']['basis']='CAS25_SERVICE_REVENUE'
        with self.assertRaises(ValueError):render_insurance_premium(fake)
        fake=copy.deepcopy(data);fake['facts']['premium_short']['period']='2030H1'
        with self.assertRaises(ValueError):render_insurance_premium(fake)

    def test_mobile_type_hierarchy_and_source_lanes_are_readable(self):
        svg=ET.fromstring(render_insurance_premium(load(),mobile=True))
        width,height=map(D,svg.get("viewBox").split()[2:])
        for text in svg.iter(SVG+"text"):
            size=D(text.get("font-size"))
            self.assertGreaterEqual(size,D(11),text.text)
            if text.get("data-editorial-role") in ("premium-source-name","premium-source-money"):
                self.assertGreaterEqual(size,D(12))
            y=D(text.get("y"))
            self.assertGreaterEqual(y-size,D(0))
            self.assertLessEqual(y+size/D(4),height)
        source_labels=[t for t in svg.iter(SVG+"text") if t.get("data-editorial-role")=="premium-source-name"]
        source_nodes=[n for n in svg.iter(SVG+"rect") if n.get("data-node-role")=="premium-source"]
        self.assertGreater(D(source_nodes[0].get("y"))-D(source_labels[-1].get("y")),D(30))
        visible=" ".join(t.text or "" for t in svg.iter(SVG+"text"))
        self.assertIn("不是法定保险服务收入",visible)
        self.assertIn("不等于实际收现",visible)

    def test_hostile_source_forgery_fails_before_render(self):
        data=load()
        for field in ("premium_first_regular","premium_new","premium_total"):
            fake=copy.deepcopy(data)
            fake["facts"][field]["yuan"]=str(D(fake["facts"][field]["yuan"])+D(1000000))
            with self.assertRaisesRegex(ValueError,"INSURANCE_PREMIUM_4_TO_2_TO_1"):
                render_insurance_premium(fake)
        fake=copy.deepcopy(data)
        fake["facts"]["premium_single"]["page"]=47
        with self.assertRaisesRegex(ValueError,"MANAGEMENT_PREMIUM_TYPED_FACT_MISMATCH"):
            render_insurance_premium(fake)
        fake=copy.deepcopy(data)
        fake["source"]["original_bytes_sha256"]="0"
        with self.assertRaisesRegex(ValueError,"P104_SOURCE_BYTES"):
            render_insurance_premium(fake)
if __name__=="__main__":unittest.main()
