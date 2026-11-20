"""Failure cases for the offline authoring route and its shared source gates."""
import sys
import unittest
from copy import deepcopy
from pathlib import Path

import comparison_basis as cb
import research_capabilities as rc
import research_evidence as ev
import statement_extract as se
from coverage_review import check_dependencies

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'research' / 'shared'))
from source_publication import validate_offline_comparisons


def fact(period, amount='3000000'):
    return dict(period=period, yuan=amount, type='flow', scope='consolidated',
                currency='CNY', unit='元', source_cells=[{'printed': amount}],
                classification='DISCLOSED')


class OfflineCandidateTests(unittest.TestCase):
    def setUp(self):
        self.ledger = {'issuer': {'fiscal_period': '20249M', 'comparative_period': '20239M'},
                       'facts': {'rev': fact('20249M'), 'rev_prior': fact('20239M')}}
        self.story = {'figures': [{'id': 'rev', 'family': 'comparison',
                                  'periods': ['20239M', '20249M'],
                                  'pairs': [['收入', 'rev_prior', 'rev']]}]}

    def test_quarter_cannot_replace_ytd_in_figure_or_research(self):
        self.ledger['facts']['rev_prior']['period'] = '2023Q3'
        with self.assertRaisesRegex(ValueError, 'FLOW_INTERVAL_MISMATCH'):
            validate_offline_comparisons(self.ledger, self.story)
        with self.assertRaisesRegex(ValueError, 'PERIOD'):
            ev.evaluate_calculation(self.ledger, dict(id='rev', type='FLOW_YOY_DELTA',
                terms=[['rev', 1], ['rev_prior', -1]], expected_yuan='0'))

    def test_restatement_requires_archived_cell_and_correct_legend(self):
        facts = self.ledger['facts']
        facts['rev_prior']['disclosure_version'] = 'restated'
        with self.assertRaisesRegex(ValueError, 'RESTATEMENT_PROOF_REQUIRED'):
            validate_offline_comparisons(self.ledger, self.story)
        facts['rev_original'] = dict(fact('20239M', '3900000'), disclosure_version='original_before_restatement')
        self.ledger['comparison_basis'] = {'rev': {'status': 'restated', 'reason': '合并追溯',
            'original_fact': 'rev_original', 'evidence_pages': [3]}}
        with self.assertRaisesRegex(ValueError, 'LEGEND_MISMATCH'):
            validate_offline_comparisons(self.ledger, self.story)
        self.story['figures'][0]['periods'][0] += '（重述后）'
        validate_offline_comparisons(self.ledger, self.story)
        self.story['figures'][0]['pairs'][0][1] = 'rev_original'
        with self.assertRaisesRegex(ValueError, 'DIFFERENT_METRIC'):
            validate_offline_comparisons(self.ledger, self.story)

    def test_ratio_requires_matching_denominator_and_growth_refuses_small_base(self):
        self.story['quantified_claims'] = {'trend': {'expression': [['rev', 1], ['rev_prior', -1]],
                                                    'denominator': 'rev_prior'}}
        self.ledger['facts']['rev_prior']['yuan'] = '10'
        with self.assertRaisesRegex(ValueError, 'GROWTH_BASE_TOO_SMALL'):
            validate_offline_comparisons(self.ledger, self.story)
        self.story['quantified_claims']['trend']['denominator'] = 'unknown'
        with self.assertRaises(KeyError):
            validate_offline_comparisons(self.ledger, self.story)

    def test_material_amount_only_blocks_dependent_judgments(self):
        self.ledger['source'] = {'original_bytes_sha256': 'a' * 64}
        self.ledger['unmapped_review'] = {'source_sha256': 'a' * 64, 'items': [
            {'id': 'row', 'classification': 'MATERIAL_OMISSION',
             'review_evidence': {'affected_keys': ['rev']}}]}
        check_dependencies(self.ledger, ['parent_net'])
        with self.assertRaisesRegex(ValueError, 'UNMAPPED_DEPENDENCY_BLOCKED'):
            check_dependencies(self.ledger, ['rev_prior'])

    def test_bank_group_titles_and_evidence_route(self):
        self.assertIsNotNone(se.TITLE.fullmatch('合并及银行利润表-续'))
        self.assertIsNone(se.TITLE.fullmatch('合并及银行利润表的编制方法'))
        bank = deepcopy(self.ledger)
        bank['issuer'].update(offline_candidate=True, statement_format='bank')
        bank['source'] = {'original_bytes_sha256': 'a' * 64}
        for metric in ('nii', 'parent_net'):
            bank['facts'][metric] = fact('20249M')
            bank['facts'][metric + '_prior'] = fact('20239M')
        self.assertEqual(rc.assess(bank)['publication_route'], 'BANK_V2_AUTHORING_CANDIDATE')
        bank['issuer']['industry'] = '保险'
        self.assertIn('ISSUER_MODEL_CONFLICTS_WITH_ORIGINAL_STATEMENT_FORMAT', rc.assess(bank)['blockers'])

    def test_balance_compares_with_previous_year_end(self):
        self.ledger['facts']['assets'] = dict(fact('2024-09-30'), type='stock')
        self.ledger['facts']['assets_prior'] = dict(fact('2023-09-30'), type='stock')
        with self.assertRaisesRegex(ValueError, 'STOCK_OPENING_DATE_MISMATCH'):
            cb.require_pair(self.ledger, 'assets', 'assets_prior')
