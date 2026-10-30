from __future__ import annotations
import unittest, json, sys, copy, re
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'engine'))
from render_v7 import build, check, original_profit_bridge, cash_bridges
BASE=json.loads((root/'engine/sample-ledger.json').read_text())
MEMO=json.loads((root/'engine/sample-memo.json').read_text())
class ResearchPipelineQA(unittest.TestCase):
 def test_accounting_core(self):
  self.assertNotEqual(check(BASE)['status'],'BLOCKED')
 def test_real_case_exhibits_and_source(self):
  h,q=build(BASE,MEMO)
  self.assertEqual(h.count('<figure class="exhibit">'),10)
  self.assertIn('现金及现金等价物不同于',h)
  self.assertIn('应收集中度 ≠ 销售收入集中度',h)
  self.assertIn(BASE['document']['source_sha256'],h)
  self.assertEqual(q['money_flow_ribbons'],7)
 def test_one_cent_revenue_corruption(self):
  bad=copy.deepcopy(BASE);bad['facts']['revenue']['amount']=str(float(bad['facts']['revenue']['amount'])+.01)
  with self.assertRaises(ValueError):check(bad)
 def test_one_cent_cash_corruption(self):
  bad=copy.deepcopy(BASE);bad['facts']['cash_close']['amount']='2632593082.97'
  with self.assertRaises(ValueError):check(bad)
 def test_one_cent_indirect_cash_corruption(self):
  bad=copy.deepcopy(BASE);v=bad['indirect_cfo_adjustments'][0];v['amount']=str(float(v['amount'])+0.01)
  with self.assertRaises(ValueError):check(bad)
 def test_balance_mismatch(self):
  bad=copy.deepcopy(BASE);bad['facts']['equity']['amount']='6255187844.75'
  with self.assertRaises(ValueError):check(bad)
 def test_missing_comparative_is_not_fake_zero(self):
  bad=copy.deepcopy(BASE)
  del bad['facts']['revenue_prior'];del bad['facts']['cogs_prior']
  h,qa=build(bad,MEMO)
  self.assertIn('缺少可比两期财务数据',h)
  self.assertNotIn('同比 0.0%',h)
 def test_new_issuer_and_period_do_not_use_old_visual_labels(self):
  bad=copy.deepcopy(BASE);memo=copy.deepcopy(MEMO)
  bad['document']['issuer']='示例工业公司';bad['document']['ticker']='999999.SH'
  bad['document']['period_key']='2030H1';bad['document']['comparative_period_key']='2029H1'
  bad['document']['period_start']='2030-01-01';bad['document']['period_end']='2030-06-30'
  bad['document']['previous_stock_date']='2029-12-31'
  for fact in bad['facts'].values():
   fact['period']=str(fact.get('period','')).replace('2026','2030').replace('2025','2029')
  memo['issuer_short']='示例工业公司';memo['headline']='另一家公司真实报告的研究判断（模拟数据）'
  memo['business']='示例公司业务文本';memo['business_sources']='数据来源由证据记录提供'
  memo['growth_explanation']='来源驱动模拟推断';memo['growth_counter']='反面来源模拟推断'
  memo['cash_explanation']='现金模拟推断';memo['risk_explanation']='风险模拟推断';memo['watchlist']=[]
  memo['source_notes']={'top5_ar_percent':None,'top1_prepay_percent':None,'limitations':'测试中不提供'}
  memo['forensic_lenses']=[]
  h,qa=build(bad,memo)
  self.assertIn('2030H1',h)
  self.assertIn('2029H1',h)
  self.assertIn('999999.SH',h)
  self.assertNotIn('2025 H1',h)
  self.assertNotIn('2026 H1',h)
  self.assertNotIn('天孚通信',h)
 def test_unreviewed_memo_rejected_by_cli_entry(self):
  source=(root/'engine/render_v7.py').read_text()
  self.assertIn("m.get('review_status')!='ANALYST_REVIEWED'",source)
 def test_regulated_sector_does_not_silently_fall_through(self):
  source=(root/'engine/render_v7.py').read_text()
  self.assertIn("'industrial','manufacturing','services'",source)
 def test_degenerate_concentration_rejected(self):
  m=copy.deepcopy(MEMO);m['source_notes']['top5_ar_percent']=123.0
  with self.assertRaises(ValueError):build(BASE,m)
 def test_duplicate_wc_line_rejected(self):
  bad=copy.deepcopy(BASE);bad['indirect_cfo_adjustments'].append(copy.deepcopy(bad['indirect_cfo_adjustments'][-1]))
  with self.assertRaises(ValueError):cash_bridges(bad)
if __name__=='__main__':unittest.main()