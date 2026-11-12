"""Independent geometry and adverse checkpoint checks for the shared bridge."""
from decimal import Decimal as D
import random
import unittest
import xml.etree.ElementTree as ET
from editorial_bridge import compile_rows, render_bridge, money

class CommonBridgeTests(unittest.TestCase):
    def draw(self,rows,mobile=False):
        return ET.fromstring(render_bridge(rows,'现金闭合',issuer='unseen',period='2030Q2',pdf_sha256='b'*64,mobile=mobile))
    def test_nonadditive_checkpoint_and_negative_crossing(self):
        rows=[('开始',D(10),'start','p.1'),('支出',D(-20),'step','p.2'),('中间合计',D(-10),'total','p.2'),('收回',D(13),'step','p.3'),('期末',D(3),'total','p.3')]
        parsed=compile_rows(rows)
        self.assertEqual([r[-1] for r in parsed],[D(10),D(-10),D(-10),D(3),D(3)])
        for mobile in (False,True):
            svg=self.draw(rows,mobile)
            self.assertEqual(svg.get('data-period'),'2030Q2')
            bars=svg.findall('.//{http://www.w3.org/2000/svg}rect')
            for r,bar in zip(parsed,bars):
                self.assertEqual(D(bar.get('data-before-yuan')),r[4])
                self.assertEqual(D(bar.get('data-after-yuan')),r[5])
                self.assertLess(abs(D(bar.get('width'))-abs(r[5]-r[4])/D(bar.get('data-scale-yuan-per-unit'))),D('0.0000001'))
    def test_no_minimum_money_and_zero_only_state(self):
        svg=self.draw([('开始',D('1000000000'),'start','p.1'),('微小',D('.01'),'step','p.2'),('期末',D('1000000000.01'),'total','p.3')])
        tiny=svg.findall('.//{http://www.w3.org/2000/svg}rect')[1]
        self.assertLess(D(tiny.get('width')),D('.000001'))
        zero=self.draw([('开始',0,'start','p.1'),('期末',0,'total','p.2')])
        for b in zero.findall('.//{http://www.w3.org/2000/svg}rect'):self.assertEqual(b.get('data-scale-yuan-per-unit'),'ZERO_ONLY')
        self.assertEqual(money('.01'),'0.01 元')
    def test_hostile_rows_rejected(self):
        valid=[('开始',1,'start','p.1'),('支出',-2,'step','p.2'),('期末',-1,'total','p.3')]
        for idx,field,value in [(2,1,0),(1,1,'NaN'),(1,2,'unknown'),(1,3,''),(1,0,'')]:
            bad=[list(r) for r in valid];bad[idx][field]=value
            with self.subTest(value=value),self.assertRaises(ValueError):self.draw(bad)
    def test_many_unseen_exact_balances(self):
        rng=random.Random(734)
        for _ in range(80):
            start=D(rng.randrange(-10**9,10**9))/100
            changes=[D(rng.randrange(-10**9,10**9))/100 for _ in range(8)]
            rows=[('开始',start,'start','p.1')]+[(f'变动{i}',v,'step',f'p.{i+2}') for i,v in enumerate(changes)]+[('期末',start+sum(changes),'total','p.20')]
            self.assertEqual(compile_rows(rows)[-1][-1],start+sum(changes))
            self.draw(rows,True)

class CommonStockAndComparisonTests(unittest.TestCase):
    def test_signed_comparison_never_loses_negative_direction(self):
        from editorial_bridge import render_comparison
        root=ET.fromstring(render_comparison([('现金',D(-4),D(6),'p.1')],'现金比较',issuer='unseen',periods=('2030H1','2031H1'),pdf_sha256='b'*64,mobile=True))
        bars=root.findall('.//{http://www.w3.org/2000/svg}rect')
        self.assertLess(D(bars[0].get('x')),D(bars[1].get('x')))
        self.assertAlmostEqual(D(bars[0].get('width'))/D(bars[1].get('width')),D(4)/D(6),places=7)
        self.assertEqual(bars[0].get('fill'),'#CD7271')
    def test_balance_rejects_unbalanced_or_negative_funding(self):
        from editorial_bridge import render_balance
        for assets,liabilities,equity in [(100,60,41),(100,110,-10),(0,0,0)]:
            with self.subTest(assets=assets),self.assertRaises(ValueError):
                render_balance([('2030-06-30',assets,liabilities,equity,'p.2')],'资产',issuer='unseen',pdf_sha256='a'*64)
    def test_two_real_sector_adapters_keep_every_indirect_adjustment(self):
        import json
        from pathlib import Path
        from sector_editorial import figures
        for code in ('600900','600276'):
            ledger=json.loads((Path(__file__).resolve().parents[2]/'research/issuers'/code/'source-ledger.json').read_text())
            for mobile in (False,True):
                charts=figures(ledger,mobile=mobile)
                root=ET.fromstring(charts['cfo'])
                bars=root.findall('.//{http://www.w3.org/2000/svg}rect')
                self.assertEqual(len(bars),len(ledger['cfo_adjustments'])+2)
                for bar,key in zip(bars[1:-1],ledger['cfo_adjustments']):
                    self.assertEqual(D(bar.get('data-signed-yuan')),D(ledger['facts'][key]['yuan']))
                    self.assertIn(key,bar.get('data-source-reference'))
                balance=ET.fromstring(charts['balance'])
                self.assertEqual(len(balance.findall('.//{http://www.w3.org/2000/svg}rect')),6)

class IndependentGeometryTests(unittest.TestCase):
    def test_real_adapter_geometry_and_corrupt_width_are_independently_checked(self):
        import json
        from pathlib import Path
        from sector_editorial import figures
        from editorial_geometry import check_editorial_svg
        for code in ('600900','600276'):
            ledger=json.loads((Path(__file__).resolve().parents[2]/'research/issuers'/code/'source-ledger.json').read_text())
            sha=ledger['source']['original_bytes_sha256']
            for mobile in (False,True):
                for family,markup in figures(ledger,mobile=mobile).items():
                    with self.subTest(code=code,mobile=mobile,family=family):
                        self.assertEqual(check_editorial_svg(markup,issuer=code,pdf_sha256=sha)['status'],'PASS')
                        if family=='cfo':
                            root=ET.fromstring(markup)
                            bar=next(r for r in root.iter('{http://www.w3.org/2000/svg}rect') if r.get('data-signed-yuan'))
                            bar.set('width',str(D(bar.get('width'))+1))
                            with self.assertRaises(ValueError):check_editorial_svg(ET.tostring(root,encoding='unicode'),issuer=code,pdf_sha256=sha)
    def test_mixed_unit_pairs_and_out_of_range_shares_fail(self):
        from editorial_bridge import render_comparison,render_shares
        with self.assertRaises(ValueError):render_comparison([('比对',1,2,'p.1')],'比对',issuer='unseen',periods=('2030H1','2030H1'),pdf_sha256='a'*64)
        with self.assertRaises(ValueError):render_shares([('客户集中度',101,'应收及合同资产余额','p.1')],'比率',issuer='unseen',period='2030H1',pdf_sha256='a'*64)

if __name__=='__main__':unittest.main()
