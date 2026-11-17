"""Adversarial machine evidence tests: arithmetic, dimensions, rival claims and falsifiers.

Passing is necessary, not proof that an economic hypothesis is correct.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import research_evidence as ev  # noqa: E402
import v2_builder as vb  # noqa: E402


def fact(value, kind, period, key):
    return {'yuan': str(value), 'type': kind, 'period': period,
            'scope': 'consolidated', 'currency': 'CNY', 'unit': '元',
            'classification': 'DISCLOSED', 'source_cells': [{'printed': str(value)}], 'page': 15,
            'label': key}


def ledger():
    f = {}
    for key, current, previous in [
        ('rev', 1000, 800), ('cogs', 600, 500), ('net_profit', 200, 150),
        ('cfo', 90, 100), ('parent_net', 190, 145)]:
        f[key] = fact(current, 'flow', '2026H1', key)
        f[key + '_prior'] = fact(previous, 'flow', '2025H1', key)
    f['ar'] = fact(300, 'stock', '2026-06-30', 'ar')
    f['ar_prior'] = fact(190, 'stock', '2025-12-31', 'ar')
    return {'issuer': {'code': '999999', 'fiscal_period': '2026H1',
                       'comparative_period': '2025H1', 'industry': 'manufacturing',
                       'accounting_route': 'industrial_own_cost_income'},
            'source': {'original_bytes_sha256': 'f' * 64},
            'facts': f}


def thesis():
    return {'id': 'profit-cash-divergence',
            'question': '为什么利润增长没有同步变成现金？',
            'conclusion': '本期经营现金净额低于归母利润，现金转换仍需反证。',
            'mechanism': '以法定本期经营现金净额和归母净利润作为现金差额观察，不推断具体回款原因。',
            'strongest_alternative': '也可能是季末交付和票据结算的时间差，而非客户付款能力下降。',
            'evidence_status': 'ACCOUNTING_ATTRIBUTION',
            'source_fact_keys': ['cfo', 'parent_net', 'ar', 'ar_prior'],
            'calculations': [
                {'id': 'cash-profit-gap', 'type': 'CURRENT_FLOW_LEVEL',
                 'terms': [['cfo', '1'], ['parent_net', '-1']], 'expected_yuan': '-100'},
                {'id': 'receivable-change', 'type': 'STOCK_SINCE_YEAR_START',
                 'terms': [['ar', '1'], ['ar_prior', '-1']], 'expected_yuan': '110'}],
            'discriminating_evidence': {'status': 'NOT_DISCLOSED',
                                        'limitation': '没有完整账龄与销售收现拆解，不能判断客户回款变化的原因。'},
            'next_disclosure_test': {'period': '20269M', 'metric': '经营现金净额与对应期销售收现',
                                     'falsifies_when': '下一披露期经营现金继续恶化且应收账龄显著拉长。'}}


def brief():
    d = ledger()
    return {'schema': ev.SCHEMA, 'issuer': '999999', 'fiscal_period': '2026H1',
            'sector_route': 'industrial',
            'source_pdf_sha256': d['source']['original_bytes_sha256'], 'theses': [thesis()]}


class ResearchEvidence(unittest.TestCase):
    def test_independent_math_and_structural_gate_only(self):
        r = ev.validate(ledger(), brief())
        self.assertEqual(r['status'], 'PASS_MACHINE_SOURCE_MATH_AND_STRUCTURAL_EVIDENCE_ONLY')
        self.assertEqual(r['theses'][0]['calculations'][0]['exact_yuan'], '-100')
        self.assertEqual(r['theses'][0]['calculations'][1]['exact_yuan'], '110')
        self.assertEqual(r['professional_causal_inference'], 'NOT_CHECKED')
        self.assertEqual(r['independent_financial_reviewer'], 'NOT_CHECKED')
        self.assertEqual(r['release_authorization'], 'NOT_GRANTED_BY_THIS_GATE')

    def test_original_sha_issuer_and_period_mismatch_rejected(self):
        for key, value in [('issuer', '888888'), ('fiscal_period', '20269M'),
                           ('source_pdf_sha256', 'a' * 64)]:
            b = brief()
            b[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'RESEARCH_BRIEF_WRONG_ISSUER'):
                ev.validate(ledger(), b)

    def test_source_math_basis_sign_and_exactness_fail_closed(self):
        mutations = [
            ('cash-amount', lambda d, b: b['theses'][0]['calculations'][0].update(expected_yuan='-99'),
             'RESEARCH_CALC_NOT_EXACT_YUAN'),
            ('stock-mixed-with-flow', lambda d, b: b['theses'][0]['calculations'][0]['terms'].append(['ar', '1']),
             'RESEARCH_FACT_BASIS_MISMATCH'),
            ('stock-comparative-date', lambda d, b: d['facts']['ar_prior'].update(period='2025-06-30'),
             'RESEARCH_FACT_BASIS_MISMATCH'),
            ('parent-scope', lambda d, b: d['facts']['parent_net'].update(scope='parent'),
             'RESEARCH_FACT_BASIS_MISMATCH'),
            ('missing-cell', lambda d, b: d['facts']['cfo'].update(source_cells=[]),
             'RESEARCH_FACT_WITHOUT_SOURCE_CELL'),
            ('duplicate-key', lambda d, b: b['theses'][0]['calculations'][0]['terms'].append(['cfo', '1']),
             'RESEARCH_DUPLICATE_CALC_FACT'),
            ('missing-prior-period', lambda d, b: b['theses'][0]['calculations'][1]['terms'].pop(),
             'RESEARCH_CALC_CROSS_PERIOD_INCOMPLETE'),
        ]
        for name, mutate, expected in mutations:
            with self.subTest(name=name):
                d, b = ledger(), brief()
                mutate(d, b)
                with self.assertRaisesRegex(ValueError, expected):
                    ev.validate(d, b)

    def test_competing_explanation_discriminator_and_future_falsifier_are_mandatory(self):
        cases = [
            ('same-alternative', lambda b: b['theses'][0].update(
                strongest_alternative=b['theses'][0]['mechanism']), 'RESEARCH_NO_INDEPENDENT_ALTERNATIVE'),
            ('empty-computation', lambda b: b['theses'][0].update(calculations=[]), 'RESEARCH_MUST_QUANTIFY_MECHANISM'),
            ('unsupported-cause', lambda b: b['theses'][0].update(evidence_status='DISCLOSED_CAUSAL'), 'RESEARCH_EVIDENCE_STATUS_INVALID'),
            ('fake-discriminator', lambda b: b['theses'][0].update(discriminating_evidence={
                'status': 'SOURCE_FACTS', 'source_fact_keys': ['invented']}), 'RESEARCH_DISCRIMINATOR_NOT_LINKED'),
            ('future-is-past', lambda b: b['theses'][0]['next_disclosure_test'].update(period='2026Q1'), 'RESEARCH_NEXT_TEST_NOT_FUTURE'),
            ('fake-year', lambda b: b['theses'][0]['next_disclosure_test'].update(period='2026FY22'), 'RESEARCH_NEXT_TEST_NOT_FUTURE'),
            ('manual-decimal', lambda b: b['theses'][0].update(conclusion='经营现金比例为32.14%，然而其驱动未知。'),
             'RESEARCH_HAND_TYPED_ROUNDED_NUMBER'),
            ('orphan-formula', lambda b: b['theses'][0].update(source_fact_keys=['cfo', 'ar', 'ar_prior']),
             'RESEARCH_CALC_NOT_LINKED_TO_CLAIM'),
        ]
        for name, mutate, error in cases:
            with self.subTest(name=name):
                b = brief()
                mutate(b)
                with self.assertRaisesRegex(ValueError, error):
                    ev.validate(ledger(), b)

    def test_ratio_and_period_basis_are_auditable_without_crossing_types(self):
        d = ledger()
        self.assertEqual(ev.evaluate_calculation(d, {
            'id': 'gross-profit-yoy', 'type': 'FLOW_YOY_DELTA',
            'terms': [['rev', '1'], ['cogs', '-1'], ['rev_prior', '-1'],
                      ['cogs_prior', '1']], 'expected_yuan': '100'})['exact_yuan'], '100')
        d['facts']['rev_prior']['period'] = '2025FY'
        with self.assertRaisesRegex(ValueError, 'RESEARCH_FACT_BASIS_MISMATCH'):
            ev.evaluate_calculation(d, {
                'id': 'gross-profit-yoy', 'type': 'FLOW_YOY_DELTA',
                'terms': [['rev', '1'], ['rev_prior', '-1']], 'expected_yuan': '200'})

    def test_v2_apply_requires_evidence_brief_before_any_write(self):
        d = ledger()
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / 'publication.json').write_text('{"figures": []}\n')
            (base / 'v2-draft.json').write_text('{"generation_scope": "EDITORIAL_AUTHORING_CANDIDATE"}\n')
            with patch.object(vb, 'load', return_value=(base, d, {'figures': []})):
                with self.assertRaisesRegex(SystemExit, 'V2_RESEARCH_BRIEF_NOT_READY'):
                    vb.cmd_apply(type('A', (), {'code': '999999', 'period': None})())
            self.assertEqual((base / 'publication.json').read_text(), '{"figures": []}\n')


if __name__ == '__main__':
    unittest.main()
