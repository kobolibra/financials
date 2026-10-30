import sys, unittest, json, copy, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'engine'))
from audit import audit
from render import render,svg_sankey
from probe_pdf import page_index
SAMPLE=json.loads((ROOT/'examples/tianfu-ledger.json').read_text())
MEMO=json.loads((ROOT/'examples/tianfu-memo.json').read_text())

class TestGenericPipeline(unittest.TestCase):
 def test_real_ledger_arithmetic(self):
  r=audit(SAMPLE)
  self.assertEqual(r['summary'],{'PASS':10,'FAIL':0,'NOT_CHECKED':0})
  self.assertFalse(r['issues'])
 def test_real_visual_semantics(self):
  h=render(SAMPLE,MEMO)
  self.assertEqual(h.count('class="ribbon"'),6)
  self.assertIn('15 项逐项调整',h)
  self.assertIn('前五名客户应收',h)
  self.assertIn('原材料积累',h)
  self.assertNotIn('src="https:',h)
 def test_one_cent_mutation_blocks(self):
  x=copy.deepcopy(SAMPLE);x['facts']['revenue']['amount']='2827938748.38'
  self.assertEqual(audit(x)['status'],'BLOCKED')
  with self.assertRaises(ValueError):render(x,MEMO)
 def test_product_cost_over_revenue_fails_closed(self):
  x=copy.deepcopy(SAMPLE);x['segments'][0]['revenue_key']='active_cogs';x['segments'][0]['cost_key']='passive_revenue'
  with self.assertRaises(ValueError):svg_sankey(x,MEMO)
 def test_banks_fail_closed(self):
  x=copy.deepcopy(SAMPLE);x['document']['business_type']='bank'
  with self.assertRaisesRegex(ValueError,'financial-sector renderer'):render(x,MEMO)
 def test_memo_unreviewed_marked_draft(self):
  x=copy.deepcopy(MEMO);x['review_status']='UNREVIEWED'
  self.assertIn('研究草稿：来源',render(SAMPLE,x))
 def test_missing_product_replaces_sankey_instead_of_fabricating(self):
  x=copy.deepcopy(SAMPLE);x['segments']=[]
  h=render(x,MEMO)
  self.assertIn('不能生成真实比例',h) if '不能生成真实比例' in h else self.assertIn('流向图不适用',h)
 def test_different_issuer_with_sparse_but_valid_ledgers(self):
  # Synthetic fixture tests *parameterization*, not scientific accuracy of fictitious issuer data.
  x={'document':{**SAMPLE['document'],'issuer':'合成工业测试公司','ticker':'999999.SZ','source_filename':'synthetic-fixture.pdf','pages':4,'source_sha256':'0'*64,'business_type':'industrial'},'facts':{},'segments':[{'dimension':'product','name':'测试材料','revenue_key':'segment_revenue','cost_key':'segment_cogs'}]}
  def fact(k,amount,kind='flow',prior=False):
   x['facts'][k]={'amount':str(amount),'source_label':k,'page':2,'period': ('2025H1' if prior else '2026H1') if kind=='flow' else ('2025-12-31' if prior else '2026-06-30'),'kind':kind,'scope':'consolidated','table':'synthetic','status':'reported','image_checked':True,'source_confidence':'pdf_page_checked'}
  for k,n in [('revenue',100000000),('cogs',60000000),('gross_profit',40000000),('revenue_prior',80000000),('cogs_prior',55000000),('net_profit',20000000),('cfo',15000000),('capex_cash',5000000),('segment_revenue',70000000),('segment_cogs',40000000)]:fact(k,n,prior=k.endswith('_prior'))
  for k,n in [('assets',200000000),('liabilities',80000000),('equity',120000000),('inventory',20000000),('inventory_prior',15000000),('accounts_receivable',12000000),('accounts_receivable_prior',10000000)]:fact(k,n,'stock',k.endswith('_prior'))
  m={**MEMO,'issuer_short':'合成测试公司','headline':'合成测试：可移植流水线','review_status':'UNREVIEWED'}
  h=render(x,m)
  self.assertIn('合成测试公司',h)
  self.assertIn('2026H1',h)
  self.assertEqual(h.count('class="ribbon"'),4)
  self.assertIn('研究草稿',h)
 def test_pdf_intake_underapproval(self):
  src=Path('/mnt/data/788b066c-b687-4f11-8ae4-c6197f019370.pdf')
  if not src.exists():self.skipTest('source PDF not distributed with skill')
  r=page_index(src,4)
  self.assertEqual(r['page_count'],185)
  self.assertFalse(r['publishing_allowed'])
  self.assertTrue(any(c['pdf_page']==65 for c in r['candidate_fields']['cfo']))
  self.assertEqual(r['sha256'],SAMPLE['document']['source_sha256'])

if __name__=='__main__':unittest.main()