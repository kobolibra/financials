"""Guard the new authoring choices and the finance semantics behind them."""
import sys
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
