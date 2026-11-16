"""Exhibit library (AEI-style chart families): geometry + source-value audits on the real 300394 Q3 page.

Every exhibit SVG in the published article is checked by editorial_geometry (drawn shape follows the
declared exact values) and source_publication_audit (every declared value equals the archived ledger
cell or ratio). Tampering with either the value or the shape must be caught. The YOY cross-period
mode is exercised with hostile claims.
"""
from pathlib import Path
import copy, json, re, sys, unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from editorial_geometry import check_editorial_svg
from source_publication_audit import check_vector_source, EXHIBIT_GRAMMARS
from source_publication import check_cross_period_claims

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / 'research/issuers/300394/20269M'
PAGE = ROOT / 'public/300394-2026q3.html'


def exhibits():
    html = PAGE.read_text()
    svgs = re.findall(r'<svg\b.*?</svg>', html, flags=re.S)
    return [s for s in svgs if re.search(r'data-editorial-grammar="(' + '|'.join(EXHIBIT_GRAMMARS) + ')"', s)]


class Exhibits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads((FOLDER / 'source-ledger.json').read_text())
        cls.story = json.loads((FOLDER / 'publication.json').read_text())
        cls.sha = cls.ledger['source']['original_bytes_sha256']
        cls.svgs = exhibits()

    def audit(self, svg):
        check_editorial_svg(svg, issuer='300394', pdf_sha256=self.sha)
        return check_vector_source(svg, self.ledger)

    def grammar(self, name):
        return [s for s in self.svgs if f'data-editorial-grammar="{name}"' in s]

    def test_every_family_is_published_in_both_editions_and_passes(self):
        families = {re.search(r'data-editorial-grammar="([A-Z0-9_]+)"', s).group(1) for s in self.svgs}
        self.assertEqual(families, set(EXHIBIT_GRAMMARS))
        for svg in self.svgs:
            with self.subTest(grammar=re.search(r'data-editorial-grammar="([A-Z0-9_]+)"', svg).group(1)):
                self.assertEqual(self.audit(svg)['original_source_vector_values'], 'PASS')
        self.assertTrue(any('data-layout="native-330"' in s for s in self.svgs))
        self.assertTrue(any('data-layout="editorial-1040"' in s for s in self.svgs))

    def test_a_retyped_value_is_caught_against_the_ledger(self):
        svg = self.grammar('SOURCE_PERIOD_COLUMNS_V1')[0]
        bad = re.sub(r'data-exact-value="([0-9]+)', lambda m: 'data-exact-value="' + str(int(m.group(1)) + 1), svg, count=1)
        with self.assertRaises(ValueError):
            self.audit(bad)

    def test_a_bar_drawn_longer_than_its_value_is_caught(self):
        svg = self.grammar('SOURCE_GROWTH_BARS_V1')[0]
        bad = re.sub(r'(data-growth-percent[^>]*?)?width="([0-9.]+)"', lambda m: m.group(0).replace(m.group(2), str(float(m.group(2)) + 9)), svg, count=0)
        with self.assertRaises(ValueError):
            self.audit(bad)

    def test_a_falsified_kpi_delta_text_is_caught(self):
        svg = self.grammar('SOURCE_KPI_BOARD_V1')[0]
        bad = svg.replace('同比 +21.3%', '同比 +31.3%', 1)
        self.assertNotEqual(bad, svg)
        with self.assertRaises(ValueError):
            self.audit(bad)

    def test_a_bar_pushed_off_the_phone_canvas_is_caught(self):
        svg = next(s for s in self.grammar('SOURCE_STOCK_DELTA_V1') if 'native-330' in s)
        # a consistent shift of the zero line: geometry still matches its declaration, but the bar leaves the canvas
        self.assertIn('data-axis-center="16"', svg)
        bad = re.sub(r'<rect x="16(\.0+)?" ', '<rect x="100" ', svg).replace('data-axis-center="16"', 'data-axis-center="100"')
        with self.assertRaisesRegex(ValueError, 'BAR_OUTSIDE_CANVAS'):
            self.audit(bad)

    def test_phone_text_that_cannot_fit_is_refused_at_render_time(self):
        # WebKit 375 clipped this exact 32-character footnote on the live Q3 page (run 43823304600)
        from exhibits import Canvas
        c = Canvas('SOURCE_KPI_BOARD_V1', 't', mobile=True, issuer='300394', period='20269M', pdf_sha256='0' * 64)
        with self.assertRaisesRegex(ValueError, 'EXHIBIT_TEXT_EXCEEDS_CANVAS'):
            c.text(16, 100, '每格小条：深色为本期，浅色为对比期（见各格标注），各格独立比例。', 10)
        c.text(16, 100, '小条：深色本期，浅色对比期；各格独立比例。', 10)

    def test_a_negative_kpi_is_never_drawn_in_the_positive_colour(self):
        # 300570 H1: operating cash flow turned negative; its micro bar must be red, and the audit enforces it
        html = (ROOT / 'public/300570.html').read_text()
        svg = next(s for s in re.findall(r'<svg\b.*?</svg>', html, flags=re.S) if 'SOURCE_KPI_BOARD_V1' in s and 'editorial-1040' in s)
        check_editorial_svg(svg, issuer='300570', pdf_sha256=re.search(r'data-original-pdf-sha256="([a-f0-9]{64})"', svg).group(1))
        neg = re.search(r'<rect [^>]*fill="#C2362E"[^>]*data-micro-value="-[0-9.]+"', svg)
        self.assertIsNotNone(neg)
        with self.assertRaisesRegex(ValueError, 'KPI_NEGATIVE_COLOUR'):
            check_editorial_svg(svg.replace(neg.group(0), neg.group(0).replace('#C2362E', '#3F4650')), issuer='300570',
                                pdf_sha256=re.search(r'data-original-pdf-sha256="([a-f0-9]{64})"', svg).group(1))

    def test_wrong_issuer_is_refused(self):
        with self.assertRaises(ValueError):
            self.audit(self.svgs[0].replace('data-issuer="300394"', 'data-issuer="300308"'))

    def test_signed_claims_never_print_a_hand_typed_plus_before_a_negative(self):
        from source_publication import expand_claims
        page = PAGE.read_text()
        self.assertNotIn('+-', page)
        self.assertIn('-0.90%', page)  # 2026Q2 single-quarter revenue YoY is negative; narrative must say so
        story = copy.deepcopy(self.story)
        story['probe'] = '{{q2_rev_yoy}}|{{q1_rev_yoy}}'
        self.assertEqual(expand_claims(story, self.ledger)['probe'], '-0.90|+40.82')
        story['quantified_claims']['q2_rev_yoy']['signed'] = 'yes'
        with self.assertRaisesRegex(ValueError, 'CLAIM_SIGN'):
            expand_claims(story, self.ledger)

    def test_yoy_of_same_year_differences_rejects_hostile_claims(self):
        check_cross_period_claims(self.ledger, self.story)
        good = self.story['quantified_claims']['q2_rev_yoy']
        hostile = {
            # prior part of the numerator differs from the denominator
            'denominator_mismatch': dict(good, denominator=[['rev_prior', 1], ['qone:rev_prior', -1]]),
            # current part mixes in a prior-year cell: no longer one later fiscal year
            'mixed_years': dict(good, expression=[['rev', 1], ['qone:rev_prior', -1], ['q3_rev', -1],
                                                  ['rev_prior', -1], ['qone:rev_prior', 1], ['q3_rev_prior', 1]]),
        }
        for name, spec in hostile.items():
            story = copy.deepcopy(self.story)
            story['quantified_claims']['q2_rev_yoy'] = spec
            with self.subTest(case=name), self.assertRaises(ValueError):
                check_cross_period_claims(self.ledger, story)


if __name__ == '__main__':
    unittest.main()
