"""Original issuer reported revenue/cost partitions, no calculated fake Sankey category."""
from pathlib import Path
from decimal import Decimal
import copy, json, sys, unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'engine'))
from build import moneyflow
from audit import audit
T=json.loads((ROOT/'engine/sample-ledger.json').read_text())
X=json.loads((ROOT/'examples/xinyisheng-2026H1-ledger.json').read_text())
D=lambda x:Decimal(str(x))
class ReportedPartitionTests(unittest.TestCase):
    def sums(self,j):
        part=[s for s in j['segments'] if s.get('dimension') in ('product','other_business')]
        self.assertEqual(sum((D(j['facts'][s['revenue_key']]['amount']) for s in part),D(0)),D(j['facts']['revenue']['amount']))
        self.assertEqual(sum((D(j['facts'][s['cost_key']]['amount']) for s in part),D(0)),D(j['facts']['cogs']['amount']))
        return moneyflow(j)[0]
    def test_tianfu_other_business_from_note_not_fabricated(self):
        text=self.sums(T)
        self.assertIn('其他业务（附注）',text)
        self.assertNotIn('未列示差额（计算）',text)
        self.assertEqual(D(T['facts']['passive_revenue']['amount'])+D(T['facts']['active_revenue']['amount']),D(T['facts']['disclosed_main_business_revenue']['amount']))
        self.assertEqual(D(T['facts']['passive_cogs']['amount'])+D(T['facts']['active_cogs']['amount']),D(T['facts']['disclosed_main_business_cogs']['amount']))
        self.assertEqual(T['facts']['disclosed_other_business_revenue']['page'],140)
        self.assertFalse(any(z['status']=='FAIL' for z in audit(T)['checks']))
    def test_xinyisheng_contract_other_not_other_business(self):
        text=self.sums(X)
        self.assertIn('其他（业务类型）',text)
        self.assertNotIn('未列示差额（计算）',text)
        self.assertEqual(X['facts']['disclosed_other_contract_revenue']['page'],104)
        self.assertNotEqual(D(X['facts']['disclosed_other_contract_revenue']['amount']),D(X['facts']['disclosed_other_business_revenue']['amount']))
        self.assertFalse(any(z['status']=='FAIL' for z in audit(X)['checks']))
    def test_corrupt_source_by_one_cent_fails_closed(self):
        j=copy.deepcopy(X);j['facts']['disclosed_other_contract_revenue']['amount']='27106113.31'
        with self.assertRaisesRegex(ValueError,'UNVERIFIED_REVENUE_PARTITION'):moneyflow(j)
    def test_incomplete_source_does_not_invent_other(self):
        j=copy.deepcopy(T);j['segments']=j['segments'][:-1]
        with self.assertRaisesRegex(ValueError,'UNVERIFIED_REVENUE_PARTITION'):moneyflow(j)
    def test_wrong_dimension_not_added_as_fake_revenue(self):
        j=copy.deepcopy(X);j['segments'].append({'dimension':'product','name':'其他业务（另一个分类维度）','revenue_key':'disclosed_other_business_revenue','cost_key':'disclosed_other_business_cogs'})
        with self.assertRaises(ValueError):moneyflow(j)
if __name__=='__main__':unittest.main()
