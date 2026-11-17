"""v2_builder generalizes: scaffolded exhibit specs render and pass both independent audits on every
source publication (four issuers, H1 / Q1 / 9M), and `apply` refuses TODO text and hand-typed numbers."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import v2_builder as vb  # noqa: E402

sys.path.insert(0, str(vb.ROOT / 'research' / 'shared'))
from source_publication import render_exhibit  # noqa: E402
from editorial_geometry import check_editorial_svg  # noqa: E402
from source_publication_audit import check_vector_source  # noqa: E402

REPORTS = (('300570', None), ('300548', None), ('600690', None), ('300394', '20269M'), ('300394', '2026Q1'))


class V2Builder(unittest.TestCase):
    def draft(self, code, period):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'draft.json'
            vb.main(['scaffold', '--code', code, '--out', str(out)] + (['--period', period] if period else []))
            return json.loads(out.read_text())

    def test_scaffolded_exhibits_render_and_pass_both_audits_for_every_report(self):
        for code, period in REPORTS:
            _, ledger, _ = vb.load(code, period)
            sha = ledger['source']['original_bytes_sha256']
            fams = set()
            for fg in self.draft(code, period)['new_figures']:
                fams.add(fg['family'])
                for mobile in (False, True):
                    with self.subTest(code=code, period=period, figure=fg['id'], mobile=mobile):
                        svg = render_exhibit(ledger, fg, mobile, {'issuer': code, 'pdf_sha256': sha}, fg['question'], ledger['issuer']['fiscal_period'])
                        check_editorial_svg(svg, issuer=code, pdf_sha256=sha)
                        check_vector_source(svg, ledger)
            self.assertEqual(fams, {'kpi_board', 'growth_bars', 'ratio_dumbbell', 'stock_delta'})

    def test_segments_and_regions_are_found_where_prior_cells_exist(self):
        g = next(f for f in self.draft('600690', None)['new_figures'] if f['id'] == 'growth')
        labels = [p[0] for p in g['pairs']]
        self.assertIn('智慧暖通方案', labels)
        self.assertIn('南亚', labels)
        q3 = next(f for f in self.draft('300394', '20269M')['new_figures'] if f['id'] == 'growth')
        self.assertNotIn('q3', json.dumps(q3['pairs']))  # a single quarter is not a segment

    def test_stock_findings_never_compare_snapshot_change_with_yoy_flow(self):
        def fact(x):
            return {'yuan': str(x * vb.YI)}
        base = {'ar': fact(150), 'ar_prior': fact(100),
                'inventory': fact(80), 'inventory_prior': fact(100),
                'rev': fact(200), 'rev_prior': fact(100)}
        for revenue, previous in ((200, 100), (50, 100), (100, 100)):
            with self.subTest(revenue=revenue):
                facts = {**base, 'rev': fact(revenue), 'rev_prior': fact(previous)}
                found = {x['id']: x for x in vb.findings(facts)}
                self.assertIn('receivables', found)
                self.assertIn('inventory', found)
                ar = found['receivables']['text']
                inv = found['inventory']['text']
                self.assertIn('[D:ar]', ar)
                self.assertIn('[D:inventory]', inv)
                self.assertNotIn('[g:rev]', ar)
                self.assertNotIn('应收增速', ar)
                self.assertNotIn('备货在增加', inv)
                self.assertNotIn('库存在释放', inv)
                self.assertIn('不能证明', ar)
                self.assertIn('不能证明', inv)
                self.assertEqual(found['receivables']['score'], 12.5)
        flat = {**base, 'ar': fact(100), 'inventory': fact(100)}
        ids = {x['id'] for x in vb.findings(flat)}
        self.assertNotIn('receivables', ids)
        self.assertNotIn('inventory', ids)

    def test_findings_avoid_equal_growth_zero_direction_and_unrenderable_stock_delta(self):
        fact = lambda x: {'yuan': str(x)}
        flat = {'rev': fact(100), 'rev_prior': fact(100),
                'cogs': fact(60), 'cogs_prior': fact(60),
                'operating_profit': fact(20), 'operating_profit_prior': fact(20),
                'net_profit': fact(15), 'net_profit_prior': fact(15),
                'cfo': fact(15), 'cfo_prior': fact(15)}
        ids = {x['id'] for x in vb.findings(flat)}
        for invalid in ('cost_vs_revenue', 'operating_leverage', 'cash_conversion'):
            self.assertNotIn(invalid, ids)

        tiny = {'ar': fact(12_400_000), 'ar_prior': fact(12_100_000),
                'inventory': fact(20_100_000), 'inventory_prior': fact(20_000_000)}
        ids = {x['id'] for x in vb.findings(tiny)}
        self.assertNotIn('receivables', ids)
        self.assertNotIn('inventory', ids)

        zero_finance = {'finance': fact(0), 'finance_prior': fact(1)}
        self.assertNotIn('finance_swing', {x['id'] for x in vb.findings(zero_finance)})
        reversed_finance = {'finance': fact(1), 'finance_prior': fact(-1)}
        self.assertIn('finance_swing', {x['id'] for x in vb.findings(reversed_finance)})

    def test_growth_claim_refuses_zero_or_negative_prior_and_nonrecurring_degrades(self):
        fact = lambda x: {'yuan': str(x)}
        for bad_base in (0, -10):
            with self.subTest(base=bad_base):
                claims = vb.Claims({'quantified_claims': {}}, {'rev': fact(20), 'rev_prior': fact(bad_base)})
                with self.assertRaisesRegex(SystemExit, 'V2_GROWTH_NONPOSITIVE_COMPARATIVE'):
                    claims.expand('收入[g:rev]%')
        nonrecurring = {'parent_net': fact(20), 'parent_net_prior': fact(15),
                        'adjusted_parent': fact(10), 'adjusted_parent_prior': fact(-2)}
        item = next(x for x in vb.findings(nonrecurring) if x['id'] == 'nonrecurring')
        self.assertIn('常规同比增速不适用', item['text'])
        self.assertNotIn('[g:adjusted_parent]', item['text'])

    def test_revenue_down_profit_up_is_not_called_a_smaller_decline(self):
        fact = lambda x: {'yuan': str(x)}
        facts = {'rev': fact(80), 'rev_prior': fact(100),
                 'operating_profit': fact(21), 'operating_profit_prior': fact(20)}
        item = next(x for x in vb.findings(facts) if x['id'] == 'operating_leverage')
        self.assertIn('收入同比下降而营业利润增长', item['text'])
        self.assertNotIn('降幅较小', item['text'])

    def test_apply_refuses_todo_and_hand_typed_numbers_and_expands_macros(self):
        _, ledger, story = vb.load('300570', None)
        c = vb.Claims({'quantified_claims': {}}, ledger['facts'])
        with self.assertRaisesRegex(SystemExit, 'TODO'):
            c.expand('TODO')
        with self.assertRaisesRegex(SystemExit, 'HAND_TYPED'):
            c.expand('收入增长20.81%')
        out = c.expand('收入[g:rev]%，毛利率[r:gm]%（[p:gm]个百分点），应收较年初[d:ar]亿元')
        self.assertEqual(out, '收入{{v2g_rev}}%，毛利率{{v2r_gm}}%（{{v2p_gm}}个百分点），应收较年初{{v2d_ar}}亿元')
        from source_publication import expand_claims
        st = {'quantified_claims': c.c, 'probe': out}
        self.assertEqual(expand_claims(st, ledger)['probe'], '收入+20.81%，毛利率34.81%（-4.13个百分点），应收较年初+3.54亿元')


if __name__ == '__main__':
    unittest.main()
