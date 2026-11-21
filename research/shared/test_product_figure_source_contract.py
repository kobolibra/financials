"""Guard the exact original source formulas and geometry of product economics."""
from __future__ import annotations

import json
import pathlib
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/shared'))
from source_publication import chart
from source_publication_audit import check_vector_source
from editorial_geometry import check_editorial_svg

class ProductSourceFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d=ROOT/'research/issuers/600206'
        cls.ledger=json.loads((d/'source-ledger.json').read_text())
        story=json.loads((d/'publication.json').read_text())
        cls.fig=next(f for f in story['figures'] if f['id']=='product-profit')
        cls.sha=cls.ledger['source']['original_bytes_sha256']

    def test_each_product_revenue_and_gp_has_separate_exact_source(self):
        for mobile in (False,True):
            with self.subTest(mobile=mobile):
                raw=chart(self.ledger,self.fig,mobile)
                root=ET.fromstring(raw)
                bars=[x for x in root.iter() if x.get('data-exact-value') is not None]
                self.assertEqual(len(bars),6)
                self.assertEqual(len({x.get('data-source-reference') for x in bars}),6)
                self.assertEqual(check_vector_source(raw,self.ledger)['original_source_vector_values'],'PASS')
                self.assertEqual(check_editorial_svg(raw,issuer='600206',pdf_sha256=self.sha)['status'],'PASS')

    def test_wrong_product_source_cannot_pass(self):
        raw=chart(self.ledger,self.fig,False)
        root=ET.fromstring(raw)
        bar=next(x for x in root.iter() if x.get('data-exact-value') is not None)
        bar.set('data-source-reference','platinum_cost')
        with self.assertRaisesRegex(ValueError,'DOSSIER_VECTOR_SOURCE_AMOUNT_FALSE'):
            check_vector_source(ET.tostring(root,encoding='unicode'),self.ledger)

    def test_fake_width_position_or_separate_domain_rejected(self):
        for field,value in (('width','0.000001'),('x','-5'),('data-domain-max','123')):
            root=ET.fromstring(chart(self.ledger,self.fig,False))
            bar=next(x for x in root.iter() if x.get('data-exact-value') is not None)
            bar.set(field,value)
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'EDITORIAL_GEOMETRY_'):
                check_editorial_svg(ET.tostring(root,encoding='unicode'),issuer='600206',pdf_sha256=self.sha)

    def test_wrong_issuer_and_period_rejected(self):
        for field,value in (('data-issuer','600690'),('data-period','2026FY')):
            root=ET.fromstring(chart(self.ledger,self.fig,False))
            root.set(field,value)
            with self.subTest(field=field),self.assertRaises(ValueError):
                check_editorial_svg(ET.tostring(root,encoding='unicode'),issuer='600206',pdf_sha256=self.sha)

if __name__=='__main__':
    unittest.main()
