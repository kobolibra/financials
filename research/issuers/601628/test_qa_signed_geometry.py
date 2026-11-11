"""Adversarial independent validation of downloaded/rendered insurer vectors."""
import copy, importlib.util, json, unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from qa_signed_geometry import check_signed_svg, FAMILIES, NS
BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('insurer_publisher_for_qa_test',BASE/'publish.py')
publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)
class IndependentSignedGeometry(unittest.TestCase):
    def rendered(self,family):
        brief=next(b for b in publisher.FIG['figure_briefs'] if b['id']==family)
        markup=publisher.mobile_figure(brief)
        return markup[markup.index('<svg'):markup.index('</svg>')+6]
    def test_all_five_source_signed_families(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                self.assertEqual(check_signed_svg(self.rendered(family),family,publisher.LEDGER)['source_signed_yuan'],'PASS')
    def test_forged_geometry_sign_source_and_subtotal_are_rejected(self):
        for attr,value in [('width','1'),('x','1'),('fill','#239878'),
                           ('data-signed-yuan','1'),('data-before-yuan','0'),
                           ('data-checkpoint','true'),('data-source-fact-ids','premium_total')]:
            root=ET.fromstring(self.rendered('cash'))
            bar=list(root.iter(NS+'rect'))[1]
            bar.set(attr,value)
            with self.subTest(attr=attr), self.assertRaises(ValueError):
                check_signed_svg(ET.tostring(root,encoding='unicode'),'cash',publisher.LEDGER)
        for attr,value in [('data-original-pdf-sha256','a'*64),('data-period','2025H1')]:
            root=ET.fromstring(self.rendered('cash'));root.set(attr,value)
            with self.subTest(attr=attr), self.assertRaises(ValueError):
                check_signed_svg(ET.tostring(root,encoding='unicode'),'cash',publisher.LEDGER)
if __name__=='__main__':unittest.main()
