"""INCOME_FLOW_V3 (AEI-grammar income flow): independent audit on real source bundles, both editions.

The renderer (income_flow_v3) and the auditor (income_flow_audit) share no code path for amounts,
annotations or geometry; these tests prove the auditor accepts the real renders and rejects tampering.
"""
from pathlib import Path
import copy, re, sys, unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from profit_chain_audit import bundle_for, check_svg
from income_flow_v3 import render
from income_flow_audit import check

# every report that carries prior-period source cells (comparatives)
KEYS = ('300394@20269M', '300394@2026Q1', '300570', '300548', '600690')


def v3(key):
    b = copy.deepcopy(bundle_for(key))
    b['editorial']['layout'] = 'INCOME_FLOW_V3'
    return b


class IncomeFlowV3(unittest.TestCase):
    def test_all_five_real_bundles_pass_the_independent_audit_in_both_editions(self):
        for key in KEYS:
            b = v3(key)
            for mobile in (False, True):
                with self.subTest(key=key, mobile=mobile):
                    svg = render(b, mobile=mobile)
                    self.assertIn('data-chain-layout="INCOME_FLOW_V3"', svg)
                    check(svg, b)

    def test_published_q3_hero_passes_through_the_profit_chain_gate(self):
        b = bundle_for('300394@20269M')
        self.assertEqual(b['editorial']['layout'], 'INCOME_FLOW_V3')
        for mobile in (False, True):
            check_svg(render(b, mobile=mobile), '300394@20269M', b['source_pdf']['source_sha256'])

    def test_aei_reading_of_the_q3_statement(self):
        svg = render(v3('300394@20269M'))
        # profit nodes carry margin with pp change and YoY; costs carry share of revenue
        for text in ('毛利率 62.6%（+10.7pp）', '同比 +21.3%', '占营收 37.4%（-10.7pp）', '研发费用', '所得税费用'):
            self.assertIn(text, svg)

    def test_tampered_annotation_ribbon_or_prior_amount_is_caught(self):
        b = v3('300394@20269M')
        for mobile in (False, True):
            svg = render(b, mobile=mobile)
            with self.subTest(mobile=mobile, tamper='annotation'):
                with self.assertRaises(ValueError):
                    check(svg.replace('62.6%', '72.6%', 1), b)
            with self.subTest(mobile=mobile, tamper='prior'):
                with self.assertRaises(ValueError):
                    check(re.sub(r'data-chain-prior-yuan="[0-9.\-]+"', 'data-chain-prior-yuan="1.00"', svg, count=1), b)
            with self.subTest(mobile=mobile, tamper='ribbon'):
                with self.assertRaises(ValueError):
                    check(re.sub(r'data-chain-yuan="([0-9]+)', lambda m: 'data-chain-yuan="9' + m.group(1), svg, count=1), b)

    def test_missing_prior_period_cells_are_refused(self):
        b = v3('300394@20269M')
        svg = render(b)
        del b['comparatives']
        with self.assertRaises(ValueError):
            check(svg, b)
        with self.assertRaises((ValueError, KeyError, TypeError)):
            render(b)

    def test_the_dispatcher_only_switches_reports_that_declare_v3(self):
        from unified_income_sankey import render_full_profit_chain
        b = copy.deepcopy(bundle_for('300570'))
        self.assertEqual(b['editorial'].get('layout'), 'INCOME_FLOW_V3')
        self.assertIn('data-chain-layout="INCOME_FLOW_V3"', render_full_profit_chain(b, mobile=False))
        b['editorial']['layout'] = 'PROFIT_CHAIN_LAYOUT_V2'
        self.assertIn('data-chain-layout="PROFIT_CHAIN_LAYOUT_V2"', render_full_profit_chain(b, mobile=False))

if __name__ == '__main__':
    unittest.main()
