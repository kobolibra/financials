import json,copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_publication import ROOT,validate,chart
from source_income_adapter import compile_disclosed_income
from source_publication_audit import check_vector_source
class TfcOriginalSource(unittest.TestCase):
 def setUp(self):
  b=ROOT/'research/issuers/300570';self.l=json.loads((b/'source-ledger.json').read_text());self.s=json.loads((b/'publication.json').read_text())
 def test_negative_cash_and_two_original_other_axes(self):
  self.assertEqual(validate(self.l,self.s)['accounting_identities'],27)
  self.assertEqual(self.l['facts']['cfo']['yuan'],'-72626209.38')
  bad=copy.deepcopy(self.l);bad['segments'][-1]['rev']='other_business_rev'
  with self.assertRaisesRegex(ValueError,'SIGNED_OR_LOSS_BUSINESS'):compile_disclosed_income(bad)
 def test_all_actual_figures_match_independent_original_values(self):
  for f in self.s['figures']:
   for m in (False,True):
    with self.subTest(figure=f['id'],mobile=m):self.assertEqual(check_vector_source(chart(self.l,f,m),self.l)['original_source_vector_values'],'PASS')
 def test_negative_cfo_cannot_be_silently_changed_to_positive(self):
  bad=copy.deepcopy(self.l);bad['facts']['cfo']['yuan']='72626209.38'
  with self.assertRaises(ValueError):validate(bad,self.s)
 def test_source_minus_sign_cannot_be_ignored_in_an_uncharted_note_fact(self):
  bad=copy.deepcopy(self.l);bad['facts']['fx_pnl_prior']['yuan']='1085630.22'
  with self.assertRaisesRegex(ValueError,'SOURCE_CELL_FALSE'):validate(bad,self.s)
if __name__=='__main__':unittest.main()
