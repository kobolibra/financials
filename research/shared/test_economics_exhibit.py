"""Real original-PDF facts, poisoned scopes, signed geometry and publication parity."""
import copy
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from economics_exhibit import compile_ledger_comparison, render_bridge, render_panel
from test_comparative_economics import period
from comparative_economics import gross_profit_bridge

ROOT=Path(__file__).resolve().parents[2]

class EconomicsPublicationTests(unittest.TestCase):
    def inputs(self,code):
        base=ROOT/'research/issuers'/code
        return json.loads((base/'source-ledger.json').read_text()),json.loads((base/'comparative-economics.json').read_text())

    def test_three_real_issuer_original_bytes_pages_and_published_panel(self):
        expected={'600900':'1362476231.26','600276':'-303990760.96','688220':'252363657.85'}
        import fitz
        for code,delta in expected.items():
            with self.subTest(code=code):
                ledger,brief=self.inputs(code)
                result=compile_ledger_comparison(ledger,brief)
                self.assertEqual(result['delta_gp_yuan'],delta)
                pdf=next(p for p in (ROOT/'research/issuers'/code/'source').glob('*.pdf')
                         if hashlib.sha256(p.read_bytes()).hexdigest()==ledger['source']['original_bytes_sha256'])
                doc=fitz.open(pdf)
                self.assertEqual(len(doc),ledger['source']['physical_pages_observed'])
                for key in ('rev_prior','cogs_prior','rev','cogs'):
                    f=ledger['facts'][key]
                    self.assertIn(format(D(f['yuan']),',.2f'),doc[f['page']-1].get_text().replace(' ',''))
                self.assertIn(render_panel(ledger,brief),(ROOT/'public'/f'{code}.html').read_text())

    def test_source_fact_poison_cannot_reach_publication(self):
        ledger,brief=self.inputs('600900')
        for field,value in [('period','2025H1'),('scope','parent'),('unit','亿元'),('currency','USD'),('type','stock'),('classification','DERIVED'),('page',True),('yuan',37929268927.18)]:
            bad=copy.deepcopy(ledger);bad['facts']['rev'][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):compile_ledger_comparison(bad,brief)
        for field,value in [('statement','bank_operating_income'),('question','同比如何'),('current_interval',['2026-01-01','2026-12-31'])]:
            bad=copy.deepcopy(brief);bad[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):compile_ledger_comparison(ledger,bad)

    def test_real_signed_and_zero_effects_use_exact_linear_geometry(self):
        for revenue,cost in [('150','90'),('80','100'),('100','70'),('50','10')]:
            result=gross_profit_bridge(period(2025,'100','70'),period(2026,revenue,cost),comparability_evidence='同一合并口径、同一会计定义、同一半年报告的可比上年同期。')
            for mobile in (True,False):
                root=ET.fromstring(render_bridge(result,mobile=mobile));rects=root.findall('{http://www.w3.org/2000/svg}rect')
                self.assertEqual(D(root.attrib['viewBox'].split()[2]),330 if mobile else 1040)
                for rect in rects:
                    a=rect.attrib;delta=D(a['data-after-yuan'])-D(a['data-before-yuan'])
                    self.assertEqual(delta,D(a['data-signed-yuan']))
                    self.assertLessEqual(abs(D(a['width'])-abs(delta)/D(a['data-scale-yuan-per-svg-unit'])),D('.001'))
                    self.assertGreaterEqual(D(a['width']),0)
                    if not delta:self.assertEqual(D(a['width']),0)
                bad=copy.deepcopy(result);bad['effects'][0]['yuan']='1000.00'
                with self.assertRaisesRegex(ValueError,'DISPLAY_BRIDGE_NOT_CLOSED'):render_bridge(bad,mobile=mobile)

if __name__=='__main__':unittest.main()
