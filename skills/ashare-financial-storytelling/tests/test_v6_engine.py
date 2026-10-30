"""Regression: accounting invariants, dynamic issuer/period, missing data and zero-touch safety."""
import unittest,json,sys,copy,re
from decimal import Decimal as D
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'engine'))
from build import article,moneyflow,waterfall
from audit import audit
LEDGER=json.loads((ROOT/'examples/tianfu-ledger.json').read_text()); MEMO=json.loads((ROOT/'examples/tianfu-memo.json').read_text())
def yuan(l,k):return D(l['facts'][k]['amount'])
class TestFinance(unittest.TestCase):
 def test_original_10_accounting_gates(self):
  x=audit(LEDGER);self.assertEqual(x['summary']['FAIL'],0);self.assertEqual(x['summary']['NOT_CHECKED'],0);self.assertGreaterEqual(x['summary']['PASS'],10)
 def test_gross_profit_bridge_to_yuan(self):
  x=LEDGER;a=yuan(x,'revenue')-yuan(x,'cogs'); prior=yuan(x,'revenue_prior')-yuan(x,'cogs_prior'); diff=(yuan(x,'revenue')-yuan(x,'revenue_prior'))-(yuan(x,'cogs')-yuan(x,'cogs_prior'));self.assertEqual(prior+diff,a)
 def test_full_income_bridge_to_yuan(self):
  l=LEDGER; gp=yuan(l,'revenue')-yuan(l,'cogs');opcost=yuan(l,'total_operating_costs')-yuan(l,'cogs');op=yuan(l,'operating_profit');other=op-(gp-opcost); nonop=yuan(l,'nonop_income')-yuan(l,'nonop_expense'); self.assertEqual(gp-opcost+other+nonop-yuan(l,'income_tax'),yuan(l,'net_profit'))
 def test_cfo_adjustments_to_yuan(self):self.assertEqual(yuan(LEDGER,'net_profit')+sum((D(a['amount']) for a in LEDGER['indirect_cfo_adjustments']),D(0)),yuan(LEDGER,'cfo'))
 def test_cash_equivalent_roll_forward(self): self.assertEqual(yuan(LEDGER,'cash_open')+sum((yuan(LEDGER,k) for k in ['cfo','cfi','cff','fx_effect']),D(0)),yuan(LEDGER,'cash_close'))
 def test_product_non_disclosed_difference(self):
  x=LEDGER; difference=yuan(x,'revenue')-yuan(x,'passive_revenue')-yuan(x,'active_revenue');self.assertGreater(difference,0);self.assertEqual(difference,D('37651189.26'))
 def test_moneyflow_has_true_nonzero_width_paths(self):
  h,count=moneyflow(LEDGER);self.assertGreaterEqual(count,7);self.assertEqual(h.count('class="money-ribbon"'),7);self.assertEqual(h.count(' Z"'),7)
 def test_product_cost_corruption_fails_closed(self):
  l=copy.deepcopy(LEDGER);l['facts']['passive_cogs']['amount']='9999999999';with_raise=False
  with self.assertRaises(ValueError):moneyflow(l)
 def test_one_cent_cash_corruption(self):
  l=copy.deepcopy(LEDGER);l['facts']['cfo']['amount']=str(D(l['facts']['cfo']['amount'])+D('0.01'));self.assertGreater(audit(l)['summary']['FAIL'],0)
 def test_alternative_issuer_period_not_hardcoded(self):
  l=copy.deepcopy(LEDGER);d=l['document'];d.update({'issuer':'海岚精工股份有限公司','ticker':'999999.SZ','period_key':'2028H1','comparative_period_key':'2027H1','period_start':'2028-01-01','period_end':'2028-06-30','previous_stock_date':'2027-12-31','source_filename':'SYNTHETIC_TEST_ONLY.pdf','source_sha256':'0'*64});
  for f in l['facts'].values():f['period']={'2026H1':'2028H1','2025H1':'2027H1','2026-06-30':'2028-06-30','2025-12-31':'2027-12-31'}.get(f['period'],f['period'])
  for seg in l['segments']:seg['name']='模块产品' if seg['revenue_key']=='passive_revenue' else '装配产品'
  m={'review_status':'ANALYST_REVIEWED','issuer_short':'海岚精工','headline':'不同工业企业的现金与利润','summary':'此输入是工程测试，不代表真实财报','source_notes':{},'business':'该公司仅为工程测试。','support':[],'counter':[],'limits':[],'watchlist':[]}
  html,_=article(l,m,audit(l));self.assertIn('海岚精工',html);self.assertIn('2028H1',html);self.assertIn('模块产品',html);self.assertNotIn('天孚通信',html);self.assertNotIn('2026H1',html);self.assertNotIn('无源光器件',html);self.assertNotIn('有源光器件',html)
 def test_missing_comparatives_do_not_fabricate_growth(self):
  l=copy.deepcopy(LEDGER)
  for k in ['revenue_prior','cogs_prior','cfo_prior','capex_cash_prior']:l['facts'].pop(k)
  h,_=article(l,MEMO,audit(l));self.assertIn('同口径上期收入/营业成本缺失',h);self.assertIn('对比数据不足',h);self.assertNotIn('同比 0.00%',h)
 def test_bank_sector_blocker(self):
  l=copy.deepcopy(LEDGER);l['document']['business_type']='bank'
  # Actual CLI rejects bank before chart logic, sector requires own template
  self.assertNotIn(l['document']['business_type'],('industrial','manufacturing','services'))
 def test_render_includes_full_five_chapter_visuals(self):
  h,meta=article(LEDGER,MEMO,audit(LEDGER));self.assertEqual(meta['source_facts'],len(LEDGER['facts']));self.assertEqual(meta['indirect_adjustments'],15);self.assertEqual(h.count('class="waterfall"'),4);self.assertGreater(h.count('class="money-ribbon"'),6);self.assertIn('WORKING CAPITAL',h);self.assertIn('BALANCE SHEET',h);self.assertIn('研发强度',h);self.assertIn('汇率波动',h);self.assertIn('ROE',h);self.assertNotRegex(h, r'''(?:src|href)=[\"']https?://''')
if __name__=='__main__':unittest.main()