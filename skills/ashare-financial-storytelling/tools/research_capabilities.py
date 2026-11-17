#!/usr/bin/env python3
"""Evidence-first sector, period and visualization capability planner.

This does NOT pronounce a report researched, charts attractive, or a PDF reverified.
It makes the missing adapter/evidence visible before applying the editorial V2 draft.
Each visual is only a CANDIDATE: the source and independent geometry audits still decide.
No issuer-code tables, guessed financial ratios, or artificial chart-family quotas.
"""
from __future__ import annotations

import json
import re
from decimal import Decimal as D


STOCK_KEYS = frozenset({
    'ar', 'inventory', 'ap', 'contract_assets', 'contract_liabilities',
    'loans', 'deposits', 'insurance_liabilities', 'insurance_contract_liabilities',
    'assets', 'liabilities', 'equity', 'cash', 'cash_equivalents',
})
WORKING_CAPITAL = ('ar', 'inventory', 'ap', 'contract_assets', 'contract_liabilities')
PROFIT_CHAIN = ('rev', 'cogs', 'operating_profit', 'pretax', 'net_profit', 'parent_net')
SUPPORTED_PUBLISHER = 'industrial'
SECTOR_TOPICS = {
    'industrial': (
        ('BUSINESS_ECONOMICS', ('rev', 'cogs'), 'Product/channel economics: require a proven mutually exclusive partition'),
        ('PROFIT_QUALITY', ('parent_net', 'adjusted_parent'), 'Reconcile exceptional gains, tax and minority interest'),
        ('CASH_CONVERSION', ('net_profit', 'cfo'), 'Use full CFO reconciliation if disclosed; never infer causality from stocks'),
        ('CAPITAL_INTENSITY', ('assets', 'liabilities'), 'Investigate working capital, capex and restricted cash'),
    ),
    'bank': (
        ('NET_INTEREST_ECONOMICS', ('nii',), 'NII is not interest income; NIM needs average earning assets'),
        ('ASSET_QUALITY', ('loans',), 'Nonperforming ratio, provisioning and writeoffs require own disclosures'),
        ('FUNDING_AND_CAPITAL', ('deposits',), 'Deposit structure, LCR and regulatory capital require separate disclosure'),
    ),
    'insurance': (
        ('CAS25_SERVICE_ECONOMICS', ('service_revenue', 'insurance_revenue'), 'Insurance service revenue is NOT management gross premiums'),
        ('CONTRACT_VALUE', ('nbv',), 'NBV/CSM movements require actuarial definitions and reconciliation'),
        ('SOLVENCY', ('insurance_liabilities', 'insurance_contract_liabilities'), 'Regulatory capital must not be inferred from balance-sheet equity'),
    ),
    'securities': (
        ('BUSINESS_MIX', ('fee_net', 'investment_income'), 'Separate brokerage, investment banking, asset management and proprietary activities'),
        ('CAPITAL_RISK', ('trading_assets',), 'Net capital, margin finance and leverage require regulatory disclosures'),
    ),
    'real_estate': (
        ('CONTRACT_DELIVERY', ('contract_liabilities',), 'Contract liabilities are not interchangeable with cash presales'),
        ('DEBT_LIQUIDITY', ('liabilities',), 'Maturity wall, encumbered cash and going concern need note evidence'),
    ),
    'unknown': (
        ('ACCOUNTING_ROUTE', (), 'Identify the actual economic and accounting model before selecting figures'),
    ),
}


def sector_of(ledger):
    issuer, facts = ledger.get('issuer', {}), ledger.get('facts', {})
    hint = ' '.join(str(issuer.get(k) or '').lower() for k in
                    ('industry', 'sector_adapter', 'accounting_route', 'accounting_format'))
    if any(x in hint for x in ('insurance', 'insur', '寿险', '财险', '保险')) or {'service_revenue', 'insurance_revenue', 'premium_total'} & facts.keys():
        return 'insurance'
    if any(x in hint for x in ('real_estate', 'property_developer', '房地产', '地产')):
        return 'real_estate'
    if any(x in hint for x in ('securities', 'security_broker', 'broker_dealer', '证券', '券商')):
        return 'securities'
    if any(x in hint for x in ('commercial_bank', 'banking', 'bank', '银行')) or {'nii', 'deposits'} & facts.keys():
        return 'bank'
    if issuer.get('accounting_route') == 'industrial_own_cost_income' or (
            'rev' in facts and 'cogs' in facts):
        return 'industrial'
    return 'unknown'


def periods(issuer):
    current = str(issuer.get('fiscal_period') or '')
    if not re.fullmatch(r'20\d{2}(?:Q1|H1|9M|FY)', current):
        return None
    year, suffix = int(current[:4]), current[4:]
    reported_prior = str(issuer.get('comparative_period') or '')
    flow_prior = f'{year-1}{suffix}'
    if reported_prior and reported_prior != flow_prior:
        return None  # A restatement must retain the correct comparative period identity.
    end = {'Q1': '03-31', 'H1': '06-30', '9M': '09-30', 'FY': '12-31'}[suffix]
    return {'flow_current': current, 'flow_prior': flow_prior,
            'stock_current': f'{year}-{end}', 'stock_prior': f'{year-1}-12-31',
            'flow_comparison': 'SAME_CUMULATIVE_PERIOD_YOY',
            'stock_comparison': 'REPORT_END_VS_PREVIOUS_YEAR_END_NOT_YOY'}


def fact_ok(facts, key, kind, period):
    f = facts.get(key)
    if not isinstance(f, dict):
        return False
    if f.get('type') != kind or f.get('period') != period:
        return False
    if f.get('scope') != 'consolidated' or f.get('currency') != 'CNY':
        return False
    if f.get('classification') not in ('DISCLOSED', 'DERIVED'):
        return False
    if 'yuan' not in f or not f.get('source_cells') and f.get('classification') != 'DERIVED':
        return False
    try:
        return D(str(f['yuan'])).is_finite()
    except (ValueError, ArithmeticError):
        return False


def pair_ok(ledger, key, kind='flow'):
    p = periods(ledger.get('issuer', {}))
    if not p:
        return False
    f = ledger.get('facts', {})
    return fact_ok(f, key, kind, p[kind + '_current']) and fact_ok(
        f, key + '_prior', kind, p[kind + '_prior'])


def available(ledger, keys, kind='flow'):
    return [k for k in keys if pair_ok(ledger, k, kind)]


def _candidate(family, question, evidence, reason, eligible):
    return {'family': family, 'question': question, 'evidence': evidence,
            'status': 'ELIGIBLE_PENDING_SOURCE_AND_VISUAL_AUDIT' if eligible else 'OMIT_SOURCE_OR_ADAPTER_LIMITED',
            'rationale': reason}


def partition_evidence(ledger):
    """Eligibility is only a *necessary* condition; actual partition closure is independently audited."""
    sec = sector_of(ledger)
    if sec != 'industrial':
        return False, 'An industrial income Sankey is not a financial-sector or real-estate chart'
    par = ledger.get('income_partition') or {}
    issuer = ledger.get('issuer', {})
    if (par.get('completeness') != 'SOURCE_EXHAUSTIVE_MUTUALLY_EXCLUSIVE'
            or par.get('scope') != 'consolidated' or par.get('period') != issuer.get('fiscal_period')):
        return False, 'No declared exhaustive, same-period consolidated revenue/cost partition'
    segs = ledger.get('segments') or []
    facts = ledger.get('facts', {})
    if len(segs) < 2 or not pair_ok(ledger, 'rev') or not pair_ok(ledger, 'cogs'):
        return False, 'Missing separate segment rows or paired parent statement amounts'
    try:
        sum_rev = D(0)
        sum_cost = D(0)
        for s in segs:
            if s.get('dimension') != par.get('axis'):
                return False, 'Segment dimensions overlap or do not match declared axis'
            r, c = s.get('rev'), s.get('cost')
            if not r or not c or not fact_ok(facts, r, 'flow', issuer['fiscal_period']) or not fact_ok(facts, c, 'flow', issuer['fiscal_period']):
                return False, 'One or more segment revenue/cost source cells are unproven'
            value_r, value_c = D(facts[r]['yuan']), D(facts[c]['yuan'])
            if value_r < 0 or value_c < 0 or value_c > value_r:
                return False, 'A negative amount or segment gross loss needs signed treatment'
            sum_rev += value_r
            sum_cost += value_c
        if sum_rev != D(facts['rev']['yuan']) or sum_cost != D(facts['cogs']['yuan']):
            return False, 'Segment rows do not close to original statement revenue and cost'
    except (KeyError, ValueError, ArithmeticError):
        return False, 'Segment source values could not be reproduced'
    return True, 'Source-declared partition numerically closes; still requires the independent SVG audit'


def assess(ledger):
    """Compile cross-sector research questions, lawful exhibit candidates, and hard publication limits.

    Machine evidence merely licenses an editor to investigate. It does not generate a thesis or
    certify independent analysis, aesthetics, deployment or complete disclosures.
    """
    issuer, facts = ledger.get('issuer', {}), ledger.get('facts', {})
    sector, p = sector_of(ledger), periods(issuer)
    source = ledger.get('source', {})
    source_sha = source.get('original_bytes_sha256') or ''
    source_metadata = bool(re.fullmatch('[0-9a-f]{64}', str(source_sha)))
    needs = []
    if not p:
        needs.append('MISSING_OR_INCOHERENT_FISCAL_AND_COMPARATIVE_PERIOD')
    if not source_metadata:
        needs.append('SOURCE_PDF_SHA256_NOT_RECORDED')
    if sector != SUPPORTED_PUBLISHER:
        needs.append('SECTOR_SPECIFIC_EDITORIAL_ADAPTER_NOT_PROVEN')
    required = [k for k in PROFIT_CHAIN if pair_ok(ledger, k)]
    chain = sector == 'industrial' and len(required) == len(PROFIT_CHAIN)
    if sector == 'industrial' and not all(pair_ok(ledger, k) for k in ('rev', 'parent_net', 'cfo')):
        needs.append('MINIMUM_CONSOLIDATED_FLOW_PAIRS_NOT_VERIFIED')
    bus, bus_reason = partition_evidence(ledger)
    growth_keys = available(ledger, ('rev', 'cogs', 'operating_profit', 'parent_net'))
    money = all(pair_ok(ledger, k) for k in ('rev', 'parent_net'))
    margin = all(pair_ok(ledger, k) for k in ('rev', 'cogs')) and (
        D(facts['rev']['yuan']) > 0 and D(facts['rev_prior']['yuan']) > 0)
    wc = available(ledger, WORKING_CAPITAL, 'stock') if sector == 'industrial' else []
    quarter_keys = [key for key in ('q1_rev', 'q2_rev', 'q3_rev', 'q4_rev') if (
        fact_ok(facts, key, 'flow', f"{str(issuer.get('fiscal_period', ''))[:4]}Q{key[1]}")
        and fact_ok(facts, key + '_prior', 'flow',
                    f"{int(str(issuer.get('fiscal_period', '2000'))[:4]) - 1}Q{key[1]}"))] if p else []
    # Single Q3 data plus 9M cumulative income is NOT a three-quarter trend.
    visuals = [
        _candidate('kpi_board', '这一期可比较的核心指标是什么？',
                   [k for k in ('rev', 'parent_net') if pair_ok(ledger, k)],
                   'Both flow years and balance dates must be explicit', sector == 'industrial' and money),
        _candidate('income_flow_v3', '法定收入如何逐层形成归母利润？', required,
                   'All six consolidated source lines required; V3 can still refuse negative layouts', chain),
        _candidate('income', '哪些互斥业务真实留下毛利？',
                   [s.get('rev') for s in ledger.get('segments', []) if s.get('rev')] if bus else [],
                   bus_reason, bus),
        _candidate('growth_bars', '在同一累计期间，哪些损益项目增速分化？', growth_keys,
                   'Require comparable positive reference-year flow values; this does not imply a quarterly trend',
                   sector == 'industrial' and len(growth_keys) >= 2
                   and sum(D(facts[k + '_prior']['yuan']) > 0 for k in growth_keys) >= 2),
        _candidate('ratio_dumbbell', '利润率和费用率如何变化？', ['rev', 'cogs'] if margin else [],
                   'Negative ratios must fall back to signed bridges, not positive-only dumbbells',
                   sector == 'industrial' and margin),
        _candidate('stock_delta', '资产和负债余额相对年初怎样变化？', wc,
                   'Balance changes are snapshots, not CFO components or Y/Y flow growth',
                   sector == 'industrial' and len(wc) >= 2),
        _candidate('period_columns', '单季走势是在加速还是放缓？', quarter_keys,
                   'At least three distinct, independently sourced single quarters are needed',
                   sector == 'industrial' and len(quarter_keys) >= 3),
    ]
    questions = []
    for name, alternatives, warning in SECTOR_TOPICS[sector]:
        matched = [key for key in alternatives if key in facts]
        # Topic facts are cues for human review, not affirmative proof of the narrative.
        questions.append({'id': name, 'status': 'REQUIRES_ANALYST_REVIEW',
                          'available_fact_keys': matched, 'unavailable_fact_keys': [key for key in alternatives if key not in facts],
                          'source_caveat': warning})
    return {'schema': 'financials.research_capabilities.v1',
            'issuer': issuer.get('code'), 'fiscal_period': issuer.get('fiscal_period'),
            'sector_route': sector, 'period_basis': p,
            'source_pdf_sha256': source_sha or None,
            'source_gate': 'HASH_RECORDED_BYTES_NOT_REVERIFIED' if source_metadata else 'MISSING_SHA',
            'publication_route': 'INDUSTRIAL_V2_AUTHORING_CANDIDATE' if sector == 'industrial' and not needs
                                 else 'SECTOR_ADAPTER_OR_EVIDENCE_REQUIRED',
            'blockers': needs, 'visual_candidates': visuals,
            'research_questions': questions,
            'independent_financial_and_visual_review': 'NOT_CHECKED',
            'complete_footnote_materiality_review': 'NOT_CHECKED',
            'production_source_byte_and_browser_acceptance': 'NOT_CHECKED'}


def require_editorial_v2(ledger):
    """Fail closed before writing EDITORIAL_V2 for an unsupported sector or invalid source basis."""
    plan = assess(ledger)
    if plan['publication_route'] != 'INDUSTRIAL_V2_AUTHORING_CANDIDATE':
        raise SystemExit('V2_SECTOR_OR_SOURCE_CAPABILITY_NOT_READY ' + json.dumps(
            {'route': plan['sector_route'], 'blockers': plan['blockers']}, ensure_ascii=False))
    return plan
