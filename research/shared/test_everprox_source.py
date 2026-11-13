import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_publication import ROOT,validate,chart
from source_publication_audit import check_vector_source
class EverproxRealOriginal(unittest.TestCase):
 def setUp(self):
  b=ROOT/'research/issuers/300548';self.l=json.loads((b/'source-ledger.json').read_text());self.s=json.loads((b/'publication.json').read_text())
 def test_real_wrapped_cost_and_explicit_identity_page(self):
  self.assertEqual(validate(self.l,self.s)['accounting_identities'],26)
  self.assertEqual(self.l['facts']['interconnect_cost']['yuan'],'697347164.01')
  for identity in (1,6,True,144):
   bad=copy.deepcopy(self.l);bad['source']['issuer_identity_page']=identity
   with self.subTest(page=identity),self.assertRaisesRegex(ValueError,'PDF_IDENTITY'):validate(bad,self.s)
  bad=copy.deepcopy(self.l);bad['issuer']['name']='另一家公司股份有限公司'
  with self.assertRaisesRegex(ValueError,'PDF_IDENTITY'):validate(bad,self.s)
 def test_wrong_column_and_changed_wrapped_cell_amount_are_rejected(self):
  for value in ('162980482.18','697347164.02','697347164.0'):
   bad=copy.deepcopy(self.l);bad['facts']['interconnect_cost']['yuan']=value
   with self.subTest(value=value),self.assertRaisesRegex(ValueError,'SOURCE_CELL_FALSE'):validate(bad,self.s)
 def test_all_actual_company_figures_match_independent_original_source_audit(self):
  for f in self.s['figures']:
   for mobile in (False,True):
    with self.subTest(figure=f['id'],mobile=mobile):self.assertEqual(check_vector_source(chart(self.l,f,mobile),self.l)['original_source_vector_values'],'PASS')
if __name__=='__main__':unittest.main()
