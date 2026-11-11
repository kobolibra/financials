"""Negative labels occupy their own line; tiny/zero cash never gain fake width."""
import unittest
import xml.etree.ElementTree as ET
from publisher import signed_cash_bars,change_lollipop
NS={'s':'http://www.w3.org/2000/svg'}
class SignedLabelGeometryTests(unittest.TestCase):
 def test_zero_tiny_and_large_cash_keep_the_same_scale(self):
  root=ET.fromstring(signed_cash_bars([('large',100),('tiny',-.001),('zero',0)],'cash'))
  widths=[float(r.attrib['width']) for r in root.findall('s:rect',NS)]
  self.assertAlmostEqual(widths[1]/widths[0],.00001,places=8)
  self.assertEqual(widths[2],0)
 def test_negative_amounts_are_below_label_baseline(self):
  for svg in [signed_cash_bars([('negative',-379.44)],'cash'),change_lollipop([('negative',-25.31)],'growth')]:
   root=ET.fromstring(svg);texts=root.findall('s:text',NS)
   label=next(t for t in texts if t.text=='negative')
   value=next(t for t in texts if t.text and t.text.startswith('-'))
   self.assertGreaterEqual(float(value.attrib['y'])-float(label.attrib['y']),24)
if __name__=='__main__':unittest.main()
