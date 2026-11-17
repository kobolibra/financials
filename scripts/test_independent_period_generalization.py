"""Poison tests for the independent cross-period original-PDF cohort and gate."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_independent_period_generalization as ip  # noqa: E402


class PeriodHoldout(unittest.TestCase):
    def test_frozen_original_pdf_blob_bytes_and_distinct_periods(self):
        self.assertEqual({x['fiscal_period'] for x in ip.HOLDOUTS},
                         {'2025FY', '2026Q1', '20269M'})
        self.assertEqual(len({x['path'].split('/')[-1][:6] for x in ip.HOLDOUTS}), 3)
        for item in ip.HOLDOUTS:
            with self.subTest(path=item['path']):
                path = ip.ROOT / item['path']
                self.assertTrue(path.exists(), item['path'])
                raw = path.read_bytes()
                self.assertEqual(ip.git_blob_sha1(raw), item['git_blob_sha1'])
                self.assertEqual(len(hashlib.sha256(raw).hexdigest()), 64)
        self.assertNotIn('30', {str(len(ip.HOLDOUTS))})

    def good(self):
        return {'fiscal_period': '2026Q1', 'coverage_review': {'status': 'NOT_CHECKED'},
                'stages': {'ledger': 'PASS', 'exhibits': 'PASS kpi_board',
                           'income_flow_v3': 'PASS', 'findings': 'PASS 2',
                           'business_sankey': 'NOT_AVAILABLE no proven costs'}}

    def test_technical_success_keeps_coverage_review_unchecked(self):
        case = {'fiscal_period': '2026Q1'}
        self.assertEqual(ip.check_row(self.good(), case), [])
        r = self.good()
        r['stages']['income_flow_v3'] = 'REFUSED_AS_DESIGNED→SIGNED_BRIDGE_PASS (negative)'
        self.assertEqual(ip.check_row(r, case), [])
        r['coverage_review']['status'] = 'PASS'
        self.assertIn('COVERAGE_REVIEW_MUST_NOT_AUTO_PASS', ip.check_row(r, case))

    def test_wrong_period_and_error_stages_cannot_be_reclassified_as_success(self):
        case = {'fiscal_period': '2026Q1'}
        cases = [('wrong_period', {'fiscal_period': '2025FY'}, 'WRONG_REPORT_PERIOD'),
                 ('ledger_error', {'stages': {'ledger': 'FAIL residual'}}, 'FAIL_LEDGER'),
                 ('figure_error', {'stages': {'exhibits': 'FAIL geometry'}}, 'FAIL_EXHIBITS'),
                 ('income_failure', {'stages': {'income_flow_v3': 'FAIL unsupported'}},
                  'FAIL_INCOME_FLOW_OR_AUDITED_SIGNED_FALLBACK'),
                 ('sankey_failure', {'stages': {'business_sankey': 'FAIL residual'}},
                  'FAIL_SEGMENTED_SANKEY_OR_PROVEN_SOURCE_LIMITATION'),
                 ('disclosure_not_checked', {'coverage_review': {'status': 'PASS'}},
                  'COVERAGE_REVIEW_MUST_NOT_AUTO_PASS')]
        for name, fields, expected in cases:
            with self.subTest(name=name):
                r = self.good()
                r.update(fields)
                errors = ip.check_row(r, case)
                self.assertIn(expected, errors)

    def test_report_never_claims_complete_historical_corpus_or_human_review(self):
        import unittest.mock as mock
        records = [{
            'fiscal_period': case['fiscal_period'],
            'coverage_review': {'status': 'NOT_CHECKED'},
            'stages': {'ledger': 'PASS', 'exhibits': 'PASS', 'income_flow_v3': 'PASS',
                       'findings': 'PASS', 'business_sankey': 'NOT_AVAILABLE'},
            'unmapped_rows': 2
        } for case in ip.HOLDOUTS]
        with mock.patch.object(ip.gp, 'probe', side_effect=records):
            result = ip.run()
        self.assertEqual(result['technical_pass'], len(ip.HOLDOUTS))
        self.assertEqual(result['technical_fail'], 0)
        self.assertEqual(result['original_30_reference_corpus'], 'SEPARATE_UNCHANGED_UNDER_REVIEW')
        self.assertEqual(result['material_unmapped_fact_coverage'], 'NOT_CHECKED')
        self.assertEqual(result['human_financial_research'], 'NOT_CHECKED')
        self.assertEqual(result['production_browser_release'], 'NOT_CHECKED')


if __name__ == '__main__':
    unittest.main()
