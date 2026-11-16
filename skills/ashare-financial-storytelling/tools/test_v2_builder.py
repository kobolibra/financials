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
