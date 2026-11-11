"""Offline source-byte, arithmetic, annual corroboration and version-isolation checks."""
import unittest,json,hashlib,re
from pathlib import Path
from decimal import Decimal as D
import pymupdf
B=Path(__file__).resolve().parent
def read(name):return json.loads((B/name).read_text())
class OriginalEvidenceTests(unittest.TestCase):
 def test_all_manifest_source_bytes_and_physical_pages(self):
  sources=read('all-source-manifest.json');self.assertGreaterEqual(len(sources),39)
  self.assertEqual(len({r['id'] for r in sources}),len(sources))
  for r in sources:
   p=B/r['file'];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),r['sha256'],r['id'])
   with pymupdf.open(p) as doc:self.assertEqual(len(doc),r['pages'],r['id'])
   self.assertTrue(r['url'].startswith('https://static.cninfo.com.cn/'))
 def test_24_quarters_96_exact_formulas_and_source_operands(self):
  panel=read('quarterly-panel.json');self.assertEqual(len(panel['rows']),24)
  for issuer in ['600900','600276','688220']:
   rows=[r for r in panel['rows'] if r['issuer']==issuer]
   self.assertEqual([r['quarter'] for r in rows],['2024Q4','2025Q1','2025Q2','2025Q3','2025Q4','2026Q1','2026Q2','2026Q3'])
   for row in rows:
    self.assertEqual(set(row['facts']),{'revenue','cost','rd_expense','cfo'})
    for metric,fact in row['facts'].items():
     sources=fact['sources'];a=D(sources[0]['operand']);b=D(sources[1]['operand']) if len(sources)>1 else D(0)
     self.assertTrue(a.is_finite() and b.is_finite());self.assertEqual(D(fact['value']),a-b)
     expected=f"{sources[0]['operand']} - {sources[1]['operand'] if len(sources)>1 else '0'}";self.assertEqual(fact['formula'],expected)
     self.assertTrue(sources[0]['id'].startswith(issuer+'_'))
     for src in sources:
      p=B/(src['id']+'.pdf');self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),src['sha256'])
      with pymupdf.open(p) as doc:
       self.assertTrue(1<=src['page']<=len(doc));s=doc[src['page']-1].get_text().replace(',','').replace('−','-').replace('－','-')
       self.assertIn(src['operand'],s)
 def test_annual_independent_disclosed_quarter_crosschecks(self):
  checks=read('annual-quarter-crosscheck.json');self.assertEqual(len(checks),30)
  for row in checks:
   self.assertTrue(row['match']);self.assertEqual(D(row['annual_disclosed']),D(row['derived']))
   year=row['quarter'][:4]
   with pymupdf.open(B/f"{row['issuer']}_{year}FY.pdf") as doc:
    s=doc[row['physical_page']-1].get_text()+doc[row['physical_page']].get_text();self.assertIn(row['annual_disclosed'],s.replace(',',''))
 def test_old_restatements_are_recorded_and_not_spliced_into_target(self):
  p=read('quarterly-panel.json');rev=p['comparative_revisions'];self.assertEqual(len(rev),5)
  self.assertTrue(all(r['original']!=r['later_comparative'] for r in rev))
  old={r['original_source'] for r in rev}
  for row in p['rows']:
   for f in row['facts'].values():self.assertFalse(old.intersection(s['id'] for s in f['sources']))
  for c in ['600900','688220']:
   text=read('reader-conclusions.json')['issuers'][c]['restatement_limit'];self.assertIn('2024Q1',text)
 def test_current_q3_yoy_uses_confirmed_comparative_baseline(self):
  idx={r['id']:r for r in read('statement-facts.json')}
  for code in ['600900','600276','688220']:
   for period in ['Q1','H1','Q3']:
    current=idx[f'{code}_2026{period}']['facts'];prior=idx[f'{code}_2025{period}']['facts']
    for metric in ['revenue','cost','rd_expense','cfo']:
     self.assertEqual(D(current[metric]['values'][1]),D(prior[metric]['values'][0]),f'{code} {period} {metric} comparative revision would invalidate current YoY')
 def test_peers_conclusions_and_literal_note_anchors(self):
  peers=read('peer-comparison.json');self.assertEqual(len(peers['peers']),3)
  for row in peers['research_notes']:
   with pymupdf.open(B/(row['source']+'.pdf')) as doc:
    s=doc[row['physical_page']-1].get_text().replace(',','')
    for value in row['values']:
     if value and value!='0':self.assertIn(value,s)
  for code,row in read('reader-conclusions.json')['issuers'].items():
   for field in ['thesis_update','q3_test','strongest_alternative','peer_implication','restatement_limit']:self.assertGreater(len(row[field]),50)
   self.assertIn('2026Q3',row['evidence']);self.assertIn('2025Q3',row['evidence'])
   for src in row['source_pages']:
    p=B/(src['id']+'.pdf');self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),src['sha256'])
    with pymupdf.open(p) as doc:self.assertTrue(all(1<=v<=len(doc) for v in src['physical_pages']))
if __name__=='__main__':unittest.main(verbosity=2)
