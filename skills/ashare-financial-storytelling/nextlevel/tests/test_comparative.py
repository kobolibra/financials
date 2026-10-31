import unittest, json, subprocess, tempfile, sys, hashlib
from pathlib import Path
from decimal import Decimal as D
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'engine'))
import build_comparative as m

class EditorialTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.f=m.checked();cls.page=m.render(cls.f)
 def test_all_3_original_pdf_hashes(self):
  self.assertEqual(set(self.f),{'300394','300308','300502'})
  self.assertEqual(self.f['300308']['pdf_sha256'],'e0ecd7c365c65e90b1fa4b4616ba3f4649449d64451e0ba0b1b78ba9ce3170bf')
  for code,x in self.f.items():self.assertEqual(x['pdf_sha256'],hashlib.sha256(m.PDF_PATHS[code].read_bytes()).hexdigest())
 def test_revenue_growth(self):
  for z in self.f.values():self.assertEqual(z['growth'],z['rev']/z['prior_rev']-1)
 def test_gp_reconciliation(self):
  for z in self.f.values():
   self.assertEqual(z['gp'],z['rev']-z['cogs'])
   self.assertEqual(z['gp'],m.n(z['raw'],'gross_profit'))
 def test_balance_date_ratios(self):
  for z in self.f.values():
   self.assertEqual(z['wc_share'],(z['inv']+z['ar'])/z['assets'])
   self.assertEqual(z['wc_share_prior'],(z['inv_prior']+z['ar_prior'])/z['assets_prior'])
   self.assertLessEqual(z['wc_share'],1)
 def test_cfo_not_parent_net_profit(self):
  for z in self.f.values():self.assertEqual(z['cash_ratio'],z['cfo']/m.n(z['raw'],'net_profit'))
 def test_simple_fcf_not_cash_close(self):
  for z in self.f.values():self.assertEqual(z['fcf'],z['cfo']-z['capex'])
 def test_both_cash_signs(self):
  self.assertLess(self.f['300308']['fcf'],0)
  self.assertGreater(self.f['300394']['fcf'],0)
  self.assertGreater(self.f['300502']['fcf'],0)
 def test_unique_6_chart_types(self):
  for i in range(1,7):self.assertIn(f'id="figure-{i:02d}"',self.page)
  self.assertEqual(self.page.count('<svg role="img"'),6)
 def test_no_fabricated_valuation(self):
  self.assertIn('不包含估值',self.page)
  self.assertIn('不足以生成 8–12 个季度',self.page)
 def test_standalone_not_iframe(self):
  self.assertNotIn('<iframe',self.page)
  self.assertNotIn('document.write',self.page)
  self.assertIn('<a class="brand" href="/">',self.page)
 def test_document_is_offline(self):
  self.assertNotRegex(self.page,r'<script[^>]+src=')
  self.assertNotRegex(self.page,r'<link[^>]+href=')
  self.assertIn('</html>',self.page)
 def test_source_citations(self):
  for z in self.f.values():
   self.assertIn(z['pdf_sha256'],self.page)
   self.assertIn('p.'+str(z['raw']['facts']['cfo']['page']),self.page)
 def test_no_same_link_as_three_issuers(self):
  for code in self.f:self.assertIn(f'/{code}.html',self.page)

if __name__=='__main__':unittest.main()