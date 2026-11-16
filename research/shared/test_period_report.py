"""Later report periods of an existing issuer: routing, period-code audit, claims engine, titles.

Real source: 300394 2026 third-quarter report (12 pages). The H1 report keeps its own row,
route and manifest; the two never share an identity.
"""
from pathlib import Path
import copy,json,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_publication import validate,chart,expand_claims,title_markup,ROOT
from source_publication_audit import check_vector_source
from profit_chain_audit import bundle_for,key_for,validate_source
B=ROOT/'research/issuers/300394/20269M'
class PeriodReport(unittest.TestCase):
 def setUp(self):
  self.l=json.loads((B/'source-ledger.json').read_text());self.s=json.loads((B/'publication.json').read_text())
 def test_real_quarterly_report_validates_without_segments(self):
  q=validate(self.l,self.s);self.assertEqual(q['status'],'PASS');self.assertGreaterEqual(q['facts'],150)
  self.assertFalse(any(f['family']=='income' for f in self.s['figures']))
 def test_h1_and_q3_resolve_to_different_manifests(self):
  self.assertEqual(bundle_for('300394')['period'],'2026H1');self.assertEqual(bundle_for('300394@20269M')['period'],'20269M')
  self.assertEqual(key_for('300394','20269M'),'300394@20269M');self.assertEqual(key_for('300394','2026H1'),'300394')
  self.assertEqual(validate_source(bundle_for('300394@20269M'))['status'],'PASS')
 def test_unknown_period_key_has_no_manifest(self):
  with self.assertRaises(ValueError):bundle_for('300394@2026FY')
 def test_flow_column_must_match_declared_period(self):
  bad=copy.deepcopy(self.l);bad['facts']['q3_rev']['period']='2026H1'
  with self.assertRaisesRegex(ValueError,'FLOW_PERIOD_COLUMN_MISMATCH'):validate(bad,self.s)
  bad=copy.deepcopy(self.l);del bad['issuer']['flow_columns']
  with self.assertRaisesRegex(ValueError,'FLOW_PERIOD_COLUMN_MISMATCH'):validate(bad,self.s)  # undeclared extra column fails closed
 def test_reader_period_labels_map_to_ledger_codes_and_swaps_are_caught(self):
  fig=next(f for f in expand_claims(self.s,self.l)['figures'] if f['id']=='earnings')
  raw=chart(self.l,fig,False);self.assertEqual(check_vector_source(raw,self.l)['original_source_vector_values'],'PASS')
  swapped=copy.deepcopy(self.l);swapped['issuer']['period_names']={'20269M':'2025年前三季度','20259M':'2026年前三季度'}
  with self.assertRaisesRegex(ValueError,'COMPARISON_WRONG_PERIOD'):check_vector_source(raw,swapped)
 def test_claims_engine_scale_and_margin_effects_sum_to_gross_profit_change(self):
  x=expand_claims(self.s,self.l);c=lambda n:self.s['quantified_claims'][n]
  self.assertIn('times',c('scale_effect_yi'));self.assertEqual(c('margin_effect_yi')['less'],'scale_effect_yi')
  text=json.dumps(x,ensure_ascii=False);self.assertIn('4.32亿元',text);self.assertIn('5.08亿元',text);self.assertIn('9.40亿元',text);self.assertNotIn('{{',text)
  bad=copy.deepcopy(self.s);bad['quantified_claims']['loop']={'expression':[['rev',1]],'less':'loop'}
  bad['metrics'][0]['value']='{{loop}}'
  with self.assertRaisesRegex(ValueError,'UNSOURCED_QUANTIFIED_CLAIM'):expand_claims(bad,self.l)
 def test_title_lines_must_reassemble_the_title_and_never_split_inside_a_unit(self):
  x=expand_claims(self.s,self.l);html=title_markup(x);self.assertIn('display:inline-block',html)
  bad=copy.deepcopy(x);bad['title_lines']=['完全不同的|标题','另一行']
  with self.assertRaisesRegex(ValueError,'TITLE_LINES'):title_markup(bad)
  plain=copy.deepcopy(x);del plain['title_lines'];self.assertNotIn('<span',title_markup(plain))
 def test_published_report_rebuilds_byte_for_byte_on_its_own_route(self):
  import tempfile
  from source_publication import publish
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'x.html';publish(B,out);self.assertEqual(out.read_bytes(),(ROOT/'public/300394-2026q3.html').read_bytes())
  self.assertNotEqual((ROOT/'public/300394-2026q3.html').read_bytes(),(ROOT/'public/300394.html').read_bytes())
if __name__=='__main__':unittest.main()
