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
Q1=ROOT/'research/issuers/300394/2026Q1'
class CrossPeriodClaims(unittest.TestCase):
 """A report may quote another report of the same issuer, but only inside strict, declared arithmetic."""
 def setUp(self):
  self.l=json.loads((B/'source-ledger.json').read_text());self.s=json.loads((B/'publication.json').read_text())
  self.q1l=json.loads((Q1/'source-ledger.json').read_text());self.q1s=json.loads((Q1/'publication.json').read_text())
 def test_prior_thesis_check_numbers_come_from_two_pinned_ledgers(self):
  x=json.dumps(expand_claims(self.s,self.l),ensure_ascii=False)
  self.assertIn('占比96.1%，一季度为86.1%',x);self.assertIn('占同期合并净利润80.4%，一季度为37.0%',x)
  self.assertEqual(validate(self.l,self.s)['status'],'PASS')
 def test_changed_external_source_hash_or_same_period_is_refused(self):
  bad=copy.deepcopy(self.s);bad['external_ledgers']['qone']['pdf_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'EXTERNAL_LEDGER_IDENTITY'):expand_claims(bad,self.l)
  bad=copy.deepcopy(self.s);bad['external_ledgers']['qone']['path']='research/issuers/300394/20269M/source-ledger.json';bad['external_ledgers']['qone']['period']='20269M'
  bad['external_ledgers']['qone']['pdf_sha256']=self.l['source']['original_bytes_sha256']
  with self.assertRaisesRegex(ValueError,'EXTERNAL_LEDGER_IDENTITY'):expand_claims(bad,self.l)
 def test_external_fact_without_declared_mode_or_mode_without_external_fact_fails(self):
  bad=copy.deepcopy(self.s);del bad['quantified_claims']['q23_sales_ratio']['cross_period']
  with self.assertRaisesRegex(ValueError,'CROSS_PERIOD_CLAIM_NOT_DECLARED'):validate(self.l,bad)
  bad=copy.deepcopy(self.s);bad['quantified_claims']['rev_yi']['cross_period']='CUMULATIVE_FLOW_DIFFERENCE_SAME_FISCAL_YEAR'
  with self.assertRaisesRegex(ValueError,'DECLARED_WITHOUT_EXTERNAL_FACT'):validate(self.l,bad)
 def test_stock_and_flow_or_unknown_alias_cannot_be_mixed(self):
  bad=copy.deepcopy(self.s);bad['quantified_claims']['q23_sales_ratio']['expression']=[['sales_cash',1],['qone:cash_close',-1]]
  with self.assertRaisesRegex(ValueError,'MIXED_FISCAL_YEARS_OR_NONFLOW'):validate(self.l,bad)
  bad=copy.deepcopy(self.s);bad['quantified_claims']['q23_sales_ratio']['expression']=[['sales_cash',1],['ghost:sales_cash',-1]]
  with self.assertRaises((KeyError,ValueError)):validate(self.l,bad)
 def test_same_date_stock_reconciliation_requires_one_balance_date(self):
  x=json.dumps(expand_claims(self.q1s,self.q1l),ensure_ascii=False);self.assertIn('29.40亿元',x);self.assertIn('28.64亿元',x);self.assertIn('0.76亿元',x)
  bad=copy.deepcopy(self.q1s);bad['quantified_claims']['cash_open_gap_yi']['expression']=[['cash_close',1],['qthree:cash_open',-1]]
  with self.assertRaisesRegex(ValueError,'STOCKS_MUST_SHARE_ONE_DATE'):validate(self.q1l,bad)
 def test_citation_must_use_a_single_external_report(self):
  bad=copy.deepcopy(self.s);bad['quantified_claims']['q1_sales_ratio']['expression']=[['sales_cash',1]]
  with self.assertRaisesRegex(ValueError,'CITATION_MUST_USE_ONE_EXTERNAL_REPORT'):validate(self.l,bad)
class QuarterlyOne(unittest.TestCase):
 def test_q1_report_validates_and_rebuilds_on_its_own_route(self):
  import tempfile
  from source_publication import publish
  l=json.loads((Q1/'source-ledger.json').read_text());s=json.loads((Q1/'publication.json').read_text())
  self.assertEqual(validate(l,s)['status'],'PASS');self.assertEqual(l['issuer']['fiscal_period'],'2026Q1');self.assertEqual(l['issuer'].get('flow_columns',{}),{})
  self.assertEqual(validate_source(bundle_for('300394@2026Q1'))['status'],'PASS')
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'q1.html';publish(Q1,out);self.assertEqual(out.read_bytes(),(ROOT/'public/300394-2026q1.html').read_bytes())
 def test_fx_channels_use_one_sign_convention_and_are_never_added(self):
  s=json.loads((Q1/'publication.json').read_text());fx=next(f for f in s['figures'] if f['id']=='fx')
  self.assertEqual(fx['pairs'][0][1:],[[['finance_prior',-1]],[['finance',-1]]]);self.assertIn('不能相加',fx['analysis'])
if __name__=='__main__':unittest.main()
