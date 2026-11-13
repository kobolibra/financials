from pathlib import Path
import json,copy,unittest,sys,xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_publication import validate,chart,expand_claims,ROOT
from source_publication_audit import check_vector_source
from source_income_adapter import compile_disclosed_income
from editorial_geometry import check_editorial_svg
B=ROOT/'research/issuers/600690'
class OriginalUnseenIssuerDossier(unittest.TestCase):
 def setUp(self):
  self.l=json.loads((B/'source-ledger.json').read_text());self.s=json.loads((B/'publication.json').read_text())
 def test_real_original_new_issuer_all_source_cells_and_exact_equations(self):
  q=validate(self.l,self.s);self.assertEqual(q['status'],'PASS');self.assertGreaterEqual(q['facts'],180);self.assertGreaterEqual(q['accounting_identities'],23)
 def test_original_disclosed_difference_is_computed_never_invented(self):
  plan=compile_disclosed_income(self.l);self.assertIn('原值相减',plan.footnote);self.assertIn('计算',plan.cost_source_note)
  self.l['facts']['other_cost']['yuan']='587657218.47'
  with self.assertRaisesRegex(ValueError,'DIFFERENCE_NOT_CLOSED'):compile_disclosed_income(self.l)
 def test_source_derived_revenue_cannot_masquerade_as_disclosed(self):
  bad=copy.deepcopy(self.l);bad['facts']['rev']['classification']='DERIVED'
  with self.assertRaisesRegex(ValueError,'DERIVED_REVENUE'):compile_disclosed_income(bad)
 def test_poisoned_pdf_scope_period_and_physical_page_fail_before_publication(self):
  for key,value in [('scope','parent'),('period','2025H1'),('page',True),('yuan','NaN')]:
   bad=copy.deepcopy(self.l);bad['facts']['rev'][key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):validate(bad,self.s)
  bad=copy.deepcopy(self.l);bad['source']['original_bytes_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'BYTES_DRIFT'):validate(bad,self.s)
 def test_all_actual_figures_both_editions_match_independent_original_fact_audit(self):
  for f in self.s['figures']:
   for mobile in (False,True):
    raw=chart(self.l,f,mobile);q=check_vector_source(raw,self.l);self.assertEqual(q['original_source_vector_values'],'PASS')
    if f['family']!='income':self.assertEqual(check_editorial_svg(raw,issuer='600690',pdf_sha256=self.l['source']['original_bytes_sha256'])['status'],'PASS')
 def test_actual_vector_tampering_cannot_hide_behind_valid_internal_metadata(self):
  raw=chart(self.l,next(f for f in self.s['figures'] if f['id']=='capital'),True);root=ET.fromstring(raw)
  node=next(n for n in root.iter() if n.get('data-signed-yuan'));node.set('data-signed-yuan','1')
  with self.assertRaisesRegex(ValueError,'SOURCE_AMOUNT_FALSE'):check_vector_source(ET.tostring(root,encoding='unicode'),self.l)
 def test_original_half_year_cannot_be_relabelled_full_year_even_with_all_metadata_changed(self):
  bad=copy.deepcopy(self.l);bad['issuer']['fiscal_period']='2026FY';bad['issuer']['comparative_period']='2025FY';bad['income_partition']['period']='2026FY'
  for fact in bad['facts'].values():
   if fact['type']=='flow':fact['period']=fact['period'].replace('H1','FY')
  with self.assertRaisesRegex(ValueError,'ORIGINAL_REPORT_PERIOD'):validate(bad,self.s)
 def test_publication_numeric_claims_come_from_exact_source_expressions(self):
  result=expand_claims(self.s,self.l)
  claim=next(f for f in result['figures'] if f['id']=='product-gp-change')['takeaway']
  self.assertIn('27.44亿元',claim);self.assertNotIn('27.45亿元',claim);self.assertNotIn('{{',claim)
  bad=copy.deepcopy(self.s);bad['metrics'][0]['value']='{{invented}}'
  with self.assertRaisesRegex(ValueError,'UNSOURCED_QUANTIFIED_CLAIM'):validate(self.l,bad)
  bad=copy.deepcopy(self.s);bad['quantified_claims']['living_gp_change']['scale']='0'
  with self.assertRaisesRegex(ValueError,'INVALID_CLAIM_UNIT_SCALE'):validate(self.l,bad)
 def test_prior_stock_and_prior_flow_are_not_the_same_cash_date(self):
  self.assertEqual(self.l['facts']['cash_close_prior']['period'],'2025-06-30')
  self.assertEqual(self.l['facts']['cash_open']['period'],'2025-12-31')
  self.assertNotEqual(self.l['facts']['cash_close_prior']['yuan'],self.l['facts']['cash_open']['yuan'])
if __name__=='__main__':unittest.main()
