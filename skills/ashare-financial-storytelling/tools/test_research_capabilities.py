"""Cross-company/period/sector research capability tests: financial semantics before design.

These are adversarial contract tests, not claims of independent human financial
or visual acceptance. Real issuer fixtures keep the contract connected to this repo.
"""
import json
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import research_capabilities as rc  # noqa: E402
import v2_builder as vb  # noqa: E402

ROOT = vb.ROOT


def fact(value, kind='flow', period='2026H1', scope='consolidated'):
    return {'yuan': str(value), 'type': kind, 'period': period, 'scope': scope,
            'currency': 'CNY', 'classification': 'DISCLOSED',
            'source_cells': [{'printed': str(value)}]}


def industrial():
    d = {'issuer': {'code': '999999', 'industry': 'manufacturing',
                    'accounting_route': 'industrial_own_cost_income',
                    'fiscal_period': '2026H1', 'comparative_period': '2025H1'},
         'source': {'original_bytes_sha256': '1' * 64},
         'facts': {}, 'segments': [],
         'income_partition': {'axis': 'product', 'scope': 'consolidated',
                              'period': '2026H1',
                              'completeness': 'SOURCE_EXHAUSTIVE_MUTUALLY_EXCLUSIVE'}}
    for k, (cur, prev) in {
        'rev': (2000, 1600), 'cogs': (1000, 900), 'operating_profit': (500, 300),
        'pretax': (450, 250), 'net_profit': (400, 200),
        'parent_net': (380, 190), 'cfo': (300, 180),
    }.items():
        d['facts'][k] = fact(cur)
        d['facts'][k + '_prior'] = fact(prev, period='2025H1')
    for k, (cur, prev) in {'ar': (300, 220), 'inventory': (400, 350), 'ap': (180, 130)}.items():
        d['facts'][k] = fact(cur, 'stock', '2026-06-30')
        d['facts'][k + '_prior'] = fact(prev, 'stock', '2025-12-31')
    for key, amount in {'a_rev': 1200, 'a_cost': 600, 'b_rev': 800, 'b_cost': 400}.items():
        d['facts'][key] = fact(amount)
    d['segments'] = [{'dimension': 'product', 'rev': 'a_rev', 'cost': 'a_cost'},
                     {'dimension': 'product', 'rev': 'b_rev', 'cost': 'b_cost'}]
    return d


class ResearchCapabilities(unittest.TestCase):
    def test_all_four_reporting_periods_have_correct_stock_and_flow_dates(self):
        for period, expected_end, prior in (
                ('2026Q1', '2026-03-31', '2025Q1'),
                ('2026H1', '2026-06-30', '2025H1'),
                ('20269M', '2026-09-30', '20259M'),
                ('2025FY', '2025-12-31', '2024FY')):
            with self.subTest(period=period):
                p = rc.periods({'fiscal_period': period, 'comparative_period': prior})
                self.assertEqual(p['flow_current'], period)
                self.assertEqual(p['flow_prior'], prior)
                self.assertEqual(p['stock_current'], expected_end)
                self.assertEqual(p['stock_prior'], f"{int(period[:4]) - 1}-12-31")
                self.assertEqual(p['stock_comparison'],
                                 'REPORT_END_VS_PREVIOUS_YEAR_END_NOT_YOY')
        self.assertIsNone(rc.periods({'fiscal_period': '20269M',
                                      'comparative_period': '2025H1'}))
        self.assertIsNone(rc.periods({'fiscal_period': '2026Q4'}))

    def test_industrial_source_legal_exhibits_are_only_pending_audit(self):
        plan = rc.assess(industrial())
        self.assertEqual(plan['sector_route'], 'industrial')
        self.assertEqual(plan['publication_route'], 'INDUSTRIAL_V2_AUTHORING_CANDIDATE')
        self.assertEqual(plan['period_basis']['stock_comparison'],
                         'REPORT_END_VS_PREVIOUS_YEAR_END_NOT_YOY')
        visual = {x['family']: x for x in plan['visual_candidates']}
        for key in ('kpi_board', 'income_flow_v3', 'income', 'growth_bars',
                    'ratio_dumbbell', 'stock_delta'):
            self.assertEqual(visual[key]['status'], 'ELIGIBLE_PENDING_SOURCE_AND_VISUAL_AUDIT', key)
        self.assertEqual(visual['period_columns']['status'], 'OMIT_SOURCE_OR_ADAPTER_LIMITED')
        self.assertEqual(plan['independent_financial_and_visual_review'], 'NOT_CHECKED')
        self.assertEqual(plan['complete_footnote_materiality_review'], 'NOT_CHECKED')
        self.assertEqual(plan['production_source_byte_and_browser_acceptance'], 'NOT_CHECKED')

    def test_partition_requires_proved_nonoverlapping_same_period_cost_and_revenue(self):
        for mutation in ('wrong_axis', 'wrong_period', 'partial', 'overlap', 'negative_margin'):
            with self.subTest(mutation=mutation):
                d = industrial()
                if mutation == 'wrong_axis':
                    d['segments'][0]['dimension'] = 'region'
                elif mutation == 'wrong_period':
                    d['facts']['a_rev']['period'] = '2026Q2'
                elif mutation == 'partial':
                    d['segments'].pop()
                elif mutation == 'overlap':
                    d['segments'][1]['rev'] = 'a_rev'
                elif mutation == 'negative_margin':
                    d['facts']['a_cost']['yuan'] = '1300'
                ok, reason = rc.partition_evidence(d)
                self.assertFalse(ok, (mutation, reason))
                visual = {x['family']: x for x in rc.assess(d)['visual_candidates']}
                self.assertEqual(visual['income']['status'], 'OMIT_SOURCE_OR_ADAPTER_LIMITED')

    def test_negative_gross_margin_is_not_drawn_on_positive_only_ratio_axis(self):
        d = industrial()
        d['facts']['cogs']['yuan'] = '2100'
        plan = rc.assess(d)
        visual = {x['family']: x for x in plan['visual_candidates']}
        self.assertEqual(visual['ratio_dumbbell']['status'], 'OMIT_SOURCE_OR_ADAPTER_LIMITED')
        self.assertEqual(visual['income']['status'], 'OMIT_SOURCE_OR_ADAPTER_LIMITED')

    def test_sector_specific_scaffold_refuses_without_diagnostic_explicit_mode(self):
        with self.assertRaisesRegex(SystemExit, 'V2_SECTOR_OR_SOURCE_CAPABILITY_NOT_READY'):
            vb.main(['scaffold', '--code', '601628'])

    def test_wrong_stock_date_flow_period_or_scope_is_never_eligible(self):
        d = industrial()
        d['facts']['rev_prior']['period'] = '2025FY'
        d['facts']['ar']['period'] = '2025-12-31'
        d['facts']['inventory']['scope'] = 'parent'
        d['facts']['ap_prior']['type'] = 'flow'
        plan = rc.assess(d)
        visual = {x['family']: x for x in plan['visual_candidates']}
        self.assertEqual(visual['kpi_board']['status'], 'OMIT_SOURCE_OR_ADAPTER_LIMITED')
        self.assertEqual(visual['stock_delta']['status'], 'OMIT_SOURCE_OR_ADAPTER_LIMITED')
        self.assertIn('MINIMUM_CONSOLIDATED_FLOW_PAIRS_NOT_VERIFIED', plan['blockers'])
        with self.assertRaisesRegex(SystemExit, 'V2_SECTOR_OR_SOURCE_CAPABILITY_NOT_READY'):
            rc.require_editorial_v2(d)

    def test_industrial_group_with_financial_subsidiary_is_not_misrouted_as_bank(self):
        d = industrial()
        d['issuer']['accounting_format'] = 'general'
        d['facts']['deposits'] = fact(200, 'stock', '2026-06-30')
        d['facts']['nii'] = fact(30)
        plan = rc.assess(d)
        self.assertEqual(plan['sector_route'], 'industrial')
        self.assertIn('INDUSTRIAL_GROUP_FINANCIAL_SUBSIDIARY_SCOPE_NOT_SEGREGATED',
                      plan['blockers'])
        self.assertEqual(plan['publication_route'], 'SECTOR_ADAPTER_OR_EVIDENCE_REQUIRED')
        self.assertTrue(all(v['status'] == 'OMIT_SOURCE_OR_ADAPTER_LIMITED'
                            for v in plan['visual_candidates']))
        with self.assertRaisesRegex(SystemExit, 'V2_SECTOR_OR_SOURCE_CAPABILITY_NOT_READY'):
            rc.require_editorial_v2(d)

    def test_one_regulated_line_does_not_reclassify_generic_industrial_company(self):
        d = industrial()
        d['issuer'].pop('industry')
        d['issuer'].pop('accounting_route')
        d['facts']['deposits'] = fact(300, 'stock', '2026-06-30')
        self.assertEqual(rc.sector_of(d), 'industrial')
        self.assertIn('INDUSTRIAL_GROUP_FINANCIAL_SUBSIDIARY_SCOPE_NOT_SEGREGATED',
                      rc.assess(d)['blockers'])

        d['facts']['insurance_revenue'] = fact(50)
        self.assertEqual(rc.sector_of(d), 'industrial')
        self.assertIn('INDUSTRIAL_GROUP_FINANCIAL_SUBSIDIARY_SCOPE_NOT_SEGREGATED',
                      rc.assess(d)['blockers'])

    def test_original_statement_format_overrides_metadata_but_blocks_conflict(self):
        d = industrial()
        d['issuer']['accounting_format'] = 'bank'
        plan = rc.assess(d)
        self.assertEqual(plan['sector_route'], 'bank')
        self.assertIn('ISSUER_MODEL_CONFLICTS_WITH_ORIGINAL_STATEMENT_FORMAT',
                      plan['blockers'])
        self.assertEqual(plan['publication_route'], 'SECTOR_ADAPTER_OR_EVIDENCE_REQUIRED')

        d = industrial()
        d['issuer']['industry'] = 'life_insurance'
        d['issuer']['accounting_route'] = None
        d['issuer']['accounting_format'] = 'general'
        plan = rc.assess(d)
        self.assertEqual(plan['sector_route'], 'insurance')
        self.assertIn('FINANCIAL_ISSUER_WITH_GENERAL_STATEMENT_FORMAT_NEEDS_REVIEW',
                      plan['blockers'])
        self.assertTrue(all(v['status'] == 'OMIT_SOURCE_OR_ADAPTER_LIMITED'
                            for v in plan['visual_candidates']))

    def test_unrecognized_source_format_does_not_get_industrial_publication(self):
        d = industrial()
        d['issuer']['accounting_format'] = 'unverified_legacy_bank'
        plan = rc.assess(d)
        self.assertIn('UNRECOGNIZED_SOURCE_STATEMENT_FORMAT', plan['blockers'])
        self.assertEqual(plan['publication_route'], 'SECTOR_ADAPTER_OR_EVIDENCE_REQUIRED')

    def test_unsupported_sectors_need_specific_adapters_not_generic_visual_quotas(self):
        cases = [('bank', {'industry': 'retail_bank'}, {'nii': fact(20), 'deposits': fact(30, 'stock', '2026-06-30')}),
                 ('insurance', {'industry': 'life_insurance'}, {'premium_total': fact(50), 'service_revenue': fact(40)}),
                 ('securities', {'industry': 'securities_broker'}, {'fee_net': fact(10)}),
                 ('real_estate', {'industry': 'property_developer'}, {'rev': fact(100), 'cogs': fact(80)})]
        for name, info, facts in cases:
            with self.subTest(sector=name):
                d = industrial()
                d['issuer'].update(info)
                d['facts'].update(facts)
                plan = rc.assess(d)
                self.assertEqual(plan['sector_route'], name)
                self.assertEqual(plan['publication_route'], 'SECTOR_ADAPTER_OR_EVIDENCE_REQUIRED')
                self.assertTrue(all(x['status'] == 'OMIT_SOURCE_OR_ADAPTER_LIMITED'
                                    for x in plan['visual_candidates']))
                with self.assertRaisesRegex(SystemExit, 'V2_SECTOR_OR_SOURCE_CAPABILITY_NOT_READY'):
                    rc.require_editorial_v2(d)
                self.assertTrue(all(q['status'] == 'REQUIRES_ANALYST_REVIEW'
                                    for q in plan['research_questions']))

    def test_premium_is_not_cas25_insurance_service_revenue(self):
        d = {'issuer': {'industry': 'life_insurance', 'fiscal_period': '2026H1'},
             'source': {'original_bytes_sha256': '2' * 64},
             'facts': {'premium_total': fact(100), 'parent_net': fact(10)}}
        plan = rc.assess(d)
        self.assertEqual(plan['sector_route'], 'insurance')
        cas = next(q for q in plan['research_questions'] if q['id'] == 'CAS25_SERVICE_ECONOMICS')
        self.assertFalse(cas['available_fact_keys'])
        self.assertNotIn('premium_total', cas['available_fact_keys'])
        self.assertIn('service_revenue', cas['unavailable_fact_keys'])

    def test_missing_original_sha_and_invalid_period_fail_before_editorial_apply(self):
        for change in ('source', 'period', 'missing_cash'):
            with self.subTest(change=change):
                d = industrial()
                if change == 'source':
                    d['source']['original_bytes_sha256'] = 'unknown'
                elif change == 'period':
                    d['issuer']['comparative_period'] = '2025Q1'
                else:
                    d['facts'].pop('cfo_prior')
                plan = rc.assess(d)
                self.assertEqual(plan['publication_route'], 'SECTOR_ADAPTER_OR_EVIDENCE_REQUIRED')
                with self.assertRaisesRegex(SystemExit, 'V2_SECTOR_OR_SOURCE_CAPABILITY_NOT_READY'):
                    rc.require_editorial_v2(d)

    def test_scaffold_omits_unsupported_graph_families_instead_of_filling_quota(self):
        from tempfile import TemporaryDirectory
        from types import SimpleNamespace
        from unittest.mock import patch
        d = industrial()
        d['facts']['cogs']['yuan'] = '2100'  # no legal positive gross-margin dumbbell
        for k in ('ar', 'inventory', 'ap'):
            d['facts'][k + '_prior']['period'] = '2025-06-30'  # not previous year-end
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = base / 'draft.json'
            (base / 'source-ledger.json').write_text(json.dumps(d))
            self.assertFalse((base / 'publication.json').exists())
            with patch.object(vb.fi, 'folder', return_value=base):
                vb.cmd_scaffold(SimpleNamespace(code='999999', period=None, out=str(target)))
            draft = json.loads(target.read_text())
            self.assertEqual({f['family'] for f in draft['new_figures']},
                             {'kpi_board', 'growth_bars'})
            self.assertEqual({x['family'] for x in draft['omitted_for_evidence']},
                             {'ratio_dumbbell', 'stock_delta'})
            self.assertNotIn('stock-delta', draft['order'])
            self.assertNotIn('margins', draft['roles'])
            self.assertFalse(any(t.get('value') == 'ar'
                                 for f in draft['new_figures'] if f['family'] == 'kpi_board'
                                 for t in f['tiles']))

    def test_source_diagnostic_scaffold_cannot_be_applied_as_research(self):
        from tempfile import TemporaryDirectory
        from types import SimpleNamespace
        from unittest.mock import patch
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / 'v2-draft.json').write_text(json.dumps({
                'generation_scope': 'SOURCE_DIAGNOSTIC_ONLY_NOT_FOR_PUBLICATION'}))
            (base / 'publication.json').write_text(json.dumps({'figures': []}))
            with patch.object(vb, 'load', return_value=(base, industrial(), {'figures': []})):
                with self.assertRaisesRegex(SystemExit, 'V2_SOURCE_PROBE_NOT_PUBLISHABLE'):
                    vb.cmd_apply(SimpleNamespace(code='999999', period=None))
            self.assertEqual(json.loads((base / 'publication.json').read_text()), {'figures': []})

    def test_capability_cli_works_before_publication_json_exists(self):
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / 'source-ledger.json').write_text(json.dumps(industrial()))
            self.assertFalse((base / 'publication.json').exists())
            out = base / 'capabilities.json'
            with patch.object(vb.fi, 'folder', return_value=base):
                vb.main(['capabilities', '--code', '999999', '--out', str(out)])
            self.assertEqual(json.loads(out.read_text())['publication_route'],
                             'INDUSTRIAL_V2_AUTHORING_CANDIDATE')

    def test_real_industrial_and_insurance_ledgers_keep_distinct_routes(self):
        for code, per, sector in [('300570', None, 'industrial'),
                                  ('300394', '20269M', 'industrial'),
                                  ('601628', None, 'insurance')]:
            with self.subTest(code=code, period=per):
                path = ROOT / 'research/issuers' / code
                if per:
                    path = path / per
                d = json.loads((path / 'source-ledger.json').read_text())
                plan = rc.assess(d)
                self.assertEqual(plan['sector_route'], sector)
                if sector == 'industrial':
                    self.assertEqual(plan['publication_route'], 'INDUSTRIAL_V2_AUTHORING_CANDIDATE',
                                     plan['blockers'])
                else:
                    self.assertEqual(plan['publication_route'], 'SECTOR_ADAPTER_OR_EVIDENCE_REQUIRED')
        with __import__('tempfile').TemporaryDirectory() as tmp:
            out = Path(tmp) / 'draft.json'
            vb.main(['scaffold', '--code', '300570', '--out', str(out)])
            draft = json.loads(out.read_text())
            self.assertEqual(draft['capability_plan']['sector_route'], 'industrial')
            self.assertEqual(draft['capability_plan']['independent_financial_and_visual_review'], 'NOT_CHECKED')


if __name__ == '__main__':
    unittest.main()
