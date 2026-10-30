import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit import audit
from select_story import plan

SAMPLE=json.loads((ROOT/'examples/tianfu-2026h1-ledger.json').read_text(encoding='utf-8'))

class TestFinancialGates(unittest.TestCase):
    def test_sample_reconciles(self):
        qa=audit(SAMPLE)
        self.assertFalse(qa['issues'])
        self.assertEqual(qa['summary']['FAIL'],0)
        self.assertEqual(qa['summary']['NOT_CHECKED'],0)
        self.assertGreaterEqual(qa['summary']['PASS'],9)
    def test_one_cent_corruption_blocks(self):
        a=copy.deepcopy(SAMPLE);a['facts']['assets']['amount']='7587829694.95'
        qa=audit(a)
        self.assertEqual(qa['status'],'BLOCKED')
        self.assertIn('FAIL',{c['status'] for c in qa['checks']})
    def test_cfo_missing_not_passed(self):
        a=copy.deepcopy(SAMPLE);del a['facts']['cfo']
        qa=audit(a)
        self.assertEqual(qa['status'],'CONDITIONAL_DRAFT')
        self.assertIn('NOT_CHECKED',{c['status'] for c in qa['checks']})
        plan_output=plan(a)
        self.assertFalse(next(x for x in plan_output['candidates'] if x['id']=='earnings_to_cash')['eligible'])
    def test_period_collision_blocks(self):
        a=copy.deepcopy(SAMPLE);a['facts']['revenue']['period']='2025H1'
        self.assertEqual(audit(a)['status'],'BLOCKED')
    def test_wrong_scope_blocks(self):
        a=copy.deepcopy(SAMPLE);a['facts']['net_profit']['scope']='parent'
        self.assertEqual(audit(a)['status'],'BLOCKED')
    def test_bad_source_page_blocks(self):
        a=copy.deepcopy(SAMPLE);a['facts']['capex_cash']['page']=9999
        self.assertEqual(audit(a)['status'],'BLOCKED')
    def test_product_overstatement_fails(self):
        a=copy.deepcopy(SAMPLE);a['facts']['passive_revenue']['amount']='3000000000'
        q=audit(a); c=next(x for x in q['checks'] if x['id']=='product-coverage')
        self.assertEqual(c['status'],'FAIL')
    def test_bank_income_chart_not_auto_approved(self):
        a=copy.deepcopy(SAMPLE);a['document']['business_type']='bank'
        result=plan(a)
        self.assertFalse(next(x for x in result['candidates'] if x['id']=='income_structure')['eligible'])
    def test_indirect_bridge_removed_blocks_that_chart(self):
        a=copy.deepcopy(SAMPLE);a.pop('indirect_cfo_adjustments')
        result=plan(a)
        self.assertFalse(next(x for x in result['candidates'] if x['id']=='earnings_to_cash')['eligible'])
    def test_segment_absent_blocks_mix(self):
        a=copy.deepcopy(SAMPLE);a['segments']=[]
        result=plan(a)
        self.assertFalse(next(x for x in result['candidates'] if x['id']=='revenue_mix')['eligible'])

if __name__=='__main__':unittest.main()