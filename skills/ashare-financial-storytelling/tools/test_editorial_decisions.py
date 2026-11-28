"""Guard the new authoring choices and the finance semantics behind them."""
import sys
import json
from copy import deepcopy
import unittest
from decimal import Decimal
from pathlib import Path

import v2_builder
from test_offline_candidate import fact
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'research/shared'))
from source_publication import product_rows, volume_rate_rows


class EditorialDecisions(unittest.TestCase):
    def setUp(self):
        self.ledger = {'issuer': {'fiscal_period': '2026Q1', 'comparative_period': '2025Q1'},
                       'facts': {}}
        f = self.ledger['facts']
        for key, old, now in [('income', '90', '85'), ('average', '900', '1000')]:
            for suffix, period, value in [('', '2026Q1', now), ('_prior', '2025Q1', old)]:
                f[key + suffix] = dict(fact(period, value), label=key)
                if key == 'average':
                    f[key + suffix]['denominator_definition'] = '同口径平均余额'
        self.figure = {'flow': 'income', 'average_balance': 'average'}

    def test_unknown_story_starts_without_chosen_hero(self):
        draft = v2_builder.offline_draft(self.ledger, {'sector_route': 'industrial'})
        self.assertEqual((draft['new_figures'], draft['order'], draft['roles']), ([], [], {}))

    def test_real_bank_average_balances_require_matching_group_interest_in_both_periods(self):
        import pymupdf
        import fin_intake as fi
        import notes_extract as ne
        folder = v2_builder.ROOT / 'research/issuers/600036/2026Q1'
        ledger = json.loads((folder / 'source-ledger.json').read_text())
        with pymupdf.open(next((folder / 'source').glob('*.pdf'))) as pdf:
            facts = ledger['facts']
            result = ne.bank_average_balances(pdf, fi.rows_on_page, fi.squash, facts)
            self.assertEqual(len(result), 4)
            for key, value in result.items():
                self.assertEqual(value['yuan'], facts[key]['yuan'])
                self.assertEqual(value['page'], facts[key]['page'])
            poisoned = deepcopy(facts)
            poisoned['fin_interest_income_prior']['yuan'] = '1'
            found = ne.bank_average_balances(pdf, fi.rows_on_page, fi.squash, poisoned)
            self.assertNotIn('average_earning_assets', found)
            self.assertIn('average_interest_bearing_liabilities', found)

    def test_dynamic_cash_groups_never_cancel_and_require_all_current_rows(self):
        from mechanism_exhibits import cash_reconciliation
        ledger = self.ledger
        keys = list('abcdefg')
        ledger['cash_reconciliation_keys'] = keys
        for k, n in zip(keys + ['net_profit', 'cfo'], [15, -9, 8, 1, -3, -1, 0, 9, 20]):
            ledger['facts'][k] = dict(fact('2026Q1', str(n)), label=k)
        fig = cash_reconciliation(ledger)
        indices = []
        for group in fig['editorial_groups']:
            indices.extend(group['indices'])
            values = [Decimal(ledger['facts'][fig['rows'][i][1]]['yuan']) for i in group['indices']]
            self.assertGreaterEqual(min(values) * max(values), 0)
        self.assertEqual(sorted(indices), list(range(1, 8)))
        ledger['facts']['a']['period'] = '2025Q1'
        self.assertIsNone(cash_reconciliation(ledger))

    def test_signed_gross_profit_change_survives_losses_and_excludes_incomparable_periods(self):
        from mechanism_exhibits import gross_profit_change
        f = self.ledger['facts']
        for k, current, prior in [('rev', 11, 10), ('cogs', 15, 12)]:
            f[k] = fact('2026Q1', str(current))
            f[k+'_prior'] = fact('2025Q1', str(prior))
        fig = gross_profit_change(self.ledger)
        self.assertEqual([v2_builder.val(f, expr) for _, expr, _ in fig['rows']], [-2,1,-3,-4])
        f['rev_prior']['period'] = '2025H1'
        self.assertIsNone(gross_profit_change(self.ledger))

    def test_new_pdf_disclosed_partition_without_curated_industry(self):
        from source_income_adapter import compile_disclosed_income
        folder = v2_builder.ROOT / 'research/issuers/600206'
        ledger = json.loads((folder / 'source-ledger.json').read_text())
        ledger['issuer'].update(code='999999', industry='', sector_adapter='', accounting_route='')
        self.assertEqual(compile_disclosed_income(ledger).check(), Decimal(ledger['facts']['rev']['yuan']))
        ledger['issuer']['statement_format'] = 'bank'
        with self.assertRaisesRegex(ValueError, 'SECTOR_CANNOT'):
            compile_disclosed_income(ledger)

    def test_apply_rechecks_candidate_and_forbids_value_overrides(self):
        draft = {'id': 'my-figure', 'from_candidate': 'x'}
        with self.assertRaisesRegex(ValueError, 'EVIDENCE_UNAVAILABLE'):
            v2_builder.resolve_candidate(draft, {})
        with self.assertRaisesRegex(ValueError, 'SOURCE_OVERRIDE'):
            v2_builder.resolve_candidate({**draft, 'rows': []}, {'x': {}})

    def test_small_rates_remain_distinguishable_at_phone_scale(self):
        from exhibits import render_ratio_dumbbell
        svg = render_ratio_dumbbell([dict(label='期间成本率', prior=Decimal('.343'),
            value=Decimal('.265'), value_ref='r', prior_ref='p')], '付息如何变化？',
            periods=['2025Q1','2026Q1'], issuer='999999', period='2026Q1',
            mobile=True, pdf_sha256='a'*64)
        self.assertIn('0.34% → 0.27%', svg)
        self.assertIn('data-domain-percent="0.4"', svg)

    def test_volume_and_residual_reconcile(self):
        rows = volume_rate_rows(self.ledger, self.figure)
        self.assertEqual([r[1] for r in rows], list(map(Decimal, ['90','10','-15','85'])))

    def test_closing_balance_cannot_impersonate_average(self):
        for key in ('average', 'average_prior'):
            self.ledger['facts'][key]['denominator_definition'] = '期末余额'
        with self.assertRaisesRegex(ValueError, 'DISCLOSED_AVERAGE'):
            volume_rate_rows(self.ledger, self.figure)

    def test_other_product_cost_rejected(self):
        self.ledger['facts']['income'].update(product='甲', measure='revenue')
        self.ledger['facts']['average'].update(product='乙', measure='cost')
        with self.assertRaisesRegex(ValueError, 'ROW_OR_MEASURE_MISMATCH'):
            product_rows(self.ledger, {'products': [['甲','income','average']]})
