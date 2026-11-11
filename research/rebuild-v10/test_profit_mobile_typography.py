"""Native bridge reading at a 320 CSS-pixel visible width, not just SVG units."""
import sys
import unittest
import xml.etree.ElementTree as ET
from decimal import Decimal as D
from pathlib import Path
from test_profit_formation import source
from profit_formation import form_plan, render_svg, render_profit_formation

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/shared'))
from signed_statement_waterfall import SignedStage, SignedStatement, render_signed_statement
NS='{http://www.w3.org/2000/svg}'

class MobileProfitTypography(unittest.TestCase):
    def check_readable(self, markup):
        root=ET.fromstring(markup)
        width,height=map(D,root.attrib['viewBox'].split()[2:])
        self.assertEqual(width,D(330))
        for node in root.iter(NS+'text'):
            size=D(node.attrib['font-size']); x=D(node.attrib['x']); y=D(node.attrib['y'])
            self.assertGreaterEqual(size*D(320)/width,D(11))
            # Conservative full-em Chinese character envelope; avoids silently
            # fixing font size by letting a header or final row escape viewBox.
            span=D(len(node.text or ''))*size
            left=x-span if node.attrib.get('text-anchor')=='end' else x
            right=x if node.attrib.get('text-anchor')=='end' else x+span
            self.assertGreaterEqual(left,0,node.text)
            self.assertLessEqual(right,width,node.text)
            self.assertGreaterEqual(y-size,0,node.text)
            self.assertLessEqual(y+size/4,height,node.text)
            self.assertNotIn('SIGNED PROFIT',node.text or '')
        return root

    def test_all_four_industrial_panels_at_320_visible_pixels(self):
        for code in ('688111','000333','600900','600276'):
            if code in ('688111','000333'):
                facts,sha=source(code)
            else:
                import json
                ledger=json.loads((ROOT/f'research/issuers/{code}/source-ledger.json').read_text())
                facts=ledger['facts'];sha=ledger['source']['original_bytes_sha256']
            with self.subTest(code=code):
                self.check_readable(render_svg(form_plan(code,facts,sha),mobile=True))
                reader=render_profit_formation(code,facts,sha,'https://example.com/original.pdf')
                self.assertNotIn('<td>operating_profit</td>',reader)
                self.assertNotIn('VERIFIED SIGNED ACCOUNTING',reader)

    def test_shared_bridge_negative_interim_profit_and_tax_benefit_stay_readable(self):
        values={'rev':'10','cogs':'2','rnd':'9','tax':'-2','net':'1'}
        facts={key:dict(yuan=value,scope='consolidated',period='2026H1',unit='元',page=1)
               for key,value in values.items()}
        plan=SignedStatement('test','income','a'*64,'ORIGINAL_PDF_SHA256_VERIFIED',
             '合并毛利',D(8),('rev','cogs'),(
                 SignedStage('gross','合并毛利润',D(8),('rev','cogs'),'base'),
                 SignedStage('rnd','扣减：研发费用',D(-9),('rnd',)),
                 SignedStage('tax','减：所得税费用（本期负数为收益）',D(2),('tax',))),
             (), 'net',D(1))
        root=self.check_readable(render_signed_statement(plan,facts,mobile=True))
        bars=[n for n in root.iter(NS+'rect') if n.attrib.get('data-stage-id')]
        self.assertEqual(bars[1].attrib['data-after-yuan'],'-1')
        self.assertEqual(bars[2].attrib['data-after-yuan'],'1')
        self.assertLess(D(bars[1].attrib['data-signed-yuan']),0)

if __name__=='__main__': unittest.main()
