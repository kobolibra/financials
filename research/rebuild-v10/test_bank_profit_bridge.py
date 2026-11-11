import json,sys,unittest
from decimal import Decimal as D
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/shared'))
from native_mobile import bank_profit_bridge,COPPER
class BankProfitTests(unittest.TestCase):
 def data(self):
  data=json.loads((ROOT/'research/rebuild-v10/extras.json').read_text())['600036']
  return {k:{'yuan':v['val'],'page':v['page'],'scope':'consolidated','period':'2026H1','unit':'元'} for k,v in data.items() if isinstance(v,dict)}
 def test_expenses_are_deducted_once_with_real_continuous_endpoints(self):
  f=self.data();get=lambda code,k:D(f[k]['yuan'])
  svg=ET.fromstring(bank_profit_bridge('600036',3,get,f,'a'*64))
  rows=svg.findall('{http://www.w3.org/2000/svg}rect');running=D(f['revenue']['yuan'])
  for r in rows[1:-1]:
   a=r.attrib;self.assertEqual(D(a['data-before-yuan']),running)
   running+=D(a['data-exact-signed-yuan']);self.assertEqual(D(a['data-after-yuan']),running)
   self.assertLess(abs(D(a['width'])-abs(D(a['data-exact-signed-yuan']))/D(a['data-money-scale-yuan-per-unit'])),D('.001'))
   if D(a['data-exact-signed-yuan'])<0:self.assertEqual(a['fill'],COPPER)
  self.assertEqual(running,D(f['parent_ni']['yuan']))
  self.assertNotIn('interest_out',[r.get('data-bank-profit-step') for r in rows])
 def test_wrong_source_scope_and_profit_do_not_render(self):
  f=self.data();get=lambda code,k:D(f[k]['yuan'])
  for field,value in [('scope','parent'),('unit','千元'),('period','2025H1'),('page',True)]:
   bad={k:dict(v) for k,v in f.items()};bad['revenue'][field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):bank_profit_bridge('600036',3,get,bad,'a'*64)
  bad={k:dict(v) for k,v in f.items()};bad['parent_ni']['yuan']='1'
  with self.assertRaisesRegex(ValueError,'BANK_PARENT_PROFIT_NOT_CLOSED'):
   bank_profit_bridge('600036',3,lambda c,k:D(bad[k]['yuan']),bad,'a'*64)
if __name__=='__main__':unittest.main()
