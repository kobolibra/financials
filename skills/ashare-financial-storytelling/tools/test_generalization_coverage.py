"""Unmapped financial amounts must be reviewable, stable and fail closed, not waved through by accounting equality."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import generalization_probe as gp  # noqa: E402


class UnmappedCoverage(unittest.TestCase):
    SOURCE = 'a' * 64

    def raw(self):
        return {'statement': 'is', 'page': 17, 'y': 132.12345,
                'label': '其他收益（待复核）', 'current': '1,234.56',
                'prior': '1,111.11', 'after': 'rev'}

    def test_stable_source_identity_does_not_depend_on_previous_mapped_key(self):
        first = gp.unmapped_review_items([self.raw()], self.SOURCE)[0]
        amended = dict(self.raw(), after='cogs')
        second = gp.unmapped_review_items([amended], self.SOURCE)[0]
        self.assertEqual(first['id'], second['id'])
        self.assertNotEqual(first['preceding_canonical_key'], second['preceding_canonical_key'])
        for name, new_value in (('statement', 'bs'), ('page', 18), ('y', 132.4),
                                ('label', '其他应收'), ('current', '1,234.57'), ('prior', '1,111.12')):
            other = dict(self.raw(), **{name: new_value})
            self.assertNotEqual(first['id'], gp.unmapped_review_items([other], self.SOURCE)[0]['id'])
        self.assertNotEqual(first['id'], gp.unmapped_review_items([self.raw()], 'b' * 64)[0]['id'])
        self.assertEqual(first['printed_comparative'], '1,111.11')
        self.assertEqual(first['classification'], 'NOT_CHECKED')
        self.assertEqual(first['materiality'], 'NOT_CHECKED')
        self.assertIsNone(first['review_evidence'])

    def test_queue_counts_every_unmapped_amount_and_never_approves_it(self):
        raw = self.raw()
        items = gp.unmapped_review_items([raw, dict(raw, page=18)], self.SOURCE)
        summary = {'pdf': 'original-2026h1.pdf', 'sha256': self.SOURCE,
                   'code': '300570', 'fiscal_period': '2026H1', 'unmapped_rows': 2,
                   'unmapped_review_items': items}
        queue = gp.build_coverage_queue([summary])
        self.assertEqual(queue['reports'], 1)
        self.assertEqual(queue['unmapped_rows_total'], 2)
        self.assertEqual(queue['materiality_and_completeness'], 'NOT_CHECKED')
        self.assertEqual(len(queue['rows'][0]['items']), 2)
        self.assertEqual(queue['rows'][0]['source_pdf_sha256'], self.SOURCE)
        self.assertNotIn('unmapped_review_items', summary)  # compact technical receipt remains compact

    def test_queue_refuses_any_missing_row(self):
        item = gp.unmapped_review_items([self.raw()], self.SOURCE)
        with self.assertRaisesRegex(SystemExit, 'COVERAGE_QUEUE_ROW_COUNT_MISMATCH'):
            gp.build_coverage_queue([{'pdf': 'test.pdf', 'unmapped_rows': 2, 'unmapped_review_items': item}])


if __name__ == '__main__':
    unittest.main()
