#!/usr/bin/env python3
"""Fail-closed, issuer-independent evidence contract for research conclusions.

A linked formula, a rival hypothesis and a falsifier are necessary conditions for
high-grade research, not sufficient proof of a correct thesis. This validator checks
source/type/period and exact Decimal mathematics; independent financial and art
judgment remain NOT_CHECKED. It never guesses company economics from a code.
"""
from __future__ import annotations

import argparse
import json
import re
from decimal import Decimal as D, InvalidOperation
from pathlib import Path

import research_capabilities as rc

SCHEMA = 'financials.research_evidence.v1'
FORMULAS = {
    'FLOW_YOY_DELTA': ('flow', 'flow_current', 'flow_prior', True),
    'STOCK_SINCE_YEAR_START': ('stock', 'stock_current', 'stock_prior', True),
    'CURRENT_FLOW_LEVEL': ('flow', 'flow_current', None, False),
    'CURRENT_STOCK_LEVEL': ('stock', 'stock_current', None, False),
}
STATUSES = ('OBSERVATION', 'ACCOUNTING_ATTRIBUTION', 'HYPOTHESIS')
HAND_TYPED = re.compile(r'[0-9]+\.[0-9]+\s*(?:亿|万元|%|百分点)')
PERIOD_ORDER = {'Q1': 1, 'H1': 2, '9M': 3, 'FY': 4}


def _number(value, label):
    try:
        n = D(str(value))
        if not n.is_finite():
            raise ValueError('not finite')
        return n
    except (InvalidOperation, ValueError, TypeError) as e:
        raise ValueError('RESEARCH_NONFINITE_NUMBER ' + label) from e


def _future_period(cur, candidate):
    m = re.fullmatch(r'(20[0-9]{2})(Q1|H1|9M|FY)', str(candidate))
    now = re.fullmatch(r'(20[0-9]{2})(Q1|H1|9M|FY)', str(cur))
    return bool(m and now and (int(m[1]), PERIOD_ORDER[m[2]]) > (int(now[1]), PERIOD_ORDER[now[2]]))


def _fact(ledger, key, kind, allowed_periods, issue):
    f = ledger.get('facts', {}).get(key)
    if not isinstance(f, dict):
        raise ValueError('RESEARCH_FACT_MISSING ' + issue + ':' + key)
    if (f.get('type') != kind or f.get('period') not in allowed_periods
            or f.get('scope') != 'consolidated' or f.get('currency') != 'CNY'
            or f.get('unit') != '元'
            or f.get('classification') not in ('DISCLOSED', 'DERIVED')):
        raise ValueError('RESEARCH_FACT_BASIS_MISMATCH ' + issue + ':' + key)
    if f['classification'] == 'DISCLOSED' and not f.get('source_cells'):
        raise ValueError('RESEARCH_FACT_WITHOUT_SOURCE_CELL ' + issue + ':' + key)
    if f['classification'] == 'DERIVED' and not f.get('derivation'):
        raise ValueError('RESEARCH_DERIVATION_WITHOUT_PROOF ' + issue + ':' + key)
    return _number(f.get('yuan'), key), f['period']


def evaluate_calculation(ledger, calc):
    if not isinstance(calc, dict):
        raise ValueError('RESEARCH_CALC_RECORD_INVALID')
    ident = str(calc.get('id') or '')
    if not re.fullmatch('[a-z][a-z0-9_-]*', ident):
        raise ValueError('RESEARCH_CALC_ID_INVALID')
    kind = calc.get('type')
    spec = FORMULAS.get(kind)
    if not spec:
        raise ValueError('RESEARCH_CALC_TYPE_UNSUPPORTED ' + str(kind))
    basis = rc.periods(ledger.get('issuer', {}))
    if basis is None:
        raise ValueError('RESEARCH_UNVERIFIED_PERIOD_BASIS')
    ftype, current, previous, contrast = spec
    periods = {basis[current]} | ({basis[previous]} if previous else set())
    terms = calc.get('terms')
    if not isinstance(terms, list) or not terms:
        raise ValueError('RESEARCH_CALC_EMPTY ' + ident)
    used, visited = set(), set()
    total = D(0)
    for term in terms:
        if not isinstance(term, list) or len(term) != 2 or not isinstance(term[0], str):
            raise ValueError('RESEARCH_CALC_TERM_INVALID ' + ident)
        key, coeff = term
        if key in used:
            raise ValueError('RESEARCH_DUPLICATE_CALC_FACT ' + ident + ':' + key)
        used.add(key)
        factor = _number(coeff, ident + ':factor')
        if not factor:
            raise ValueError('RESEARCH_ZERO_FACTOR ' + ident + ':' + key)
        v, period = _fact(ledger, key, ftype, periods, ident)
        total += v * factor
        visited.add(period)
    if visited != periods:
        raise ValueError('RESEARCH_CALC_CROSS_PERIOD_INCOMPLETE ' + ident)
    reported = _number(calc.get('expected_yuan'), ident + ':expected_yuan')
    if total != reported:
        raise ValueError('RESEARCH_CALC_NOT_EXACT_YUAN ' + ident)
    return {'id': ident, 'basis': kind, 'exact_yuan': str(total), 'source_keys': sorted(used)}


def _validate_claim(ledger, claim):
    if not isinstance(claim, dict):
        raise ValueError('RESEARCH_THESIS_RECORD_INVALID')
    ident = str(claim.get('id') or '')
    if not re.fullmatch('[a-z][a-z0-9_-]*', ident):
        raise ValueError('RESEARCH_THESIS_ID_INVALID')
    for k in ('question', 'conclusion', 'mechanism', 'strongest_alternative'):
        t = claim.get(k)
        if not isinstance(t, str) or len(t.strip()) < 8:
            raise ValueError('RESEARCH_THESIS_TEXT_REQUIRED ' + ident + ':' + k)
        if HAND_TYPED.search(t):
            raise ValueError('RESEARCH_HAND_TYPED_ROUNDED_NUMBER ' + ident + ':' + k)
    if claim['mechanism'].strip() == claim['strongest_alternative'].strip():
        raise ValueError('RESEARCH_NO_INDEPENDENT_ALTERNATIVE ' + ident)
    if claim.get('evidence_status') not in STATUSES:
        raise ValueError('RESEARCH_EVIDENCE_STATUS_INVALID ' + ident)
    maths = claim.get('calculations')
    if not isinstance(maths, list) or not maths:
        raise ValueError('RESEARCH_MUST_QUANTIFY_MECHANISM ' + ident)
    calculations = [evaluate_calculation(ledger, c) for c in maths]
    ids = [c['id'] for c in calculations]
    if len(ids) != len(set(ids)):
        raise ValueError('RESEARCH_DUPLICATE_CALC_ID ' + ident)
    supporting = claim.get('source_fact_keys')
    if not isinstance(supporting, list) or not supporting or len(set(supporting)) != len(supporting):
        raise ValueError('RESEARCH_SOURCE_REFERENCES_REQUIRED ' + ident)
    math_keys = {k for c in calculations for k in c['source_keys']}
    if not math_keys.issubset(set(supporting)):
        raise ValueError('RESEARCH_CALC_NOT_LINKED_TO_CLAIM ' + ident)
    f = ledger['facts']
    basis = rc.periods(ledger.get('issuer', {}))
    if not basis:
        raise ValueError('RESEARCH_UNVERIFIED_PERIOD_BASIS')
    for key in supporting:
        item = f.get(key)
        if not isinstance(item, dict) or not isinstance(item.get('page'), int):
            raise ValueError('RESEARCH_UNVERIFIED_SOURCE_REFERENCE ' + ident + ':' + key)
        ftype = item.get('type')
        if ftype not in ('flow', 'stock'):
            raise ValueError('RESEARCH_UNVERIFIED_SOURCE_REFERENCE ' + ident + ':' + key)
        allowed = {basis[ftype + '_current'], basis[ftype + '_prior']}
        if ftype == 'flow':
            columns = ledger.get('issuer', {}).get('flow_columns') or {}
            allowed |= set(columns.values())  # e.g. 9M statement separately discloses 2026Q3/2025Q3
            if item.get('period') not in {basis['flow_current'], basis['flow_prior']}:
                if columns.get(item.get('source_column')) != item.get('period'):
                    raise ValueError('RESEARCH_EXTRA_FLOW_COLUMN_NOT_DECLARED ' + ident + ':' + key)
        _fact(ledger, key, ftype, allowed, ident)
    discriminator = claim.get('discriminating_evidence')
    if not isinstance(discriminator, dict):
        raise ValueError('RESEARCH_DISCRIMINATOR_REQUIRED ' + ident)
    state = discriminator.get('status')
    if state == 'SOURCE_FACTS':
        distinguishing = discriminator.get('source_fact_keys')
        if not isinstance(distinguishing, list) or not distinguishing:
            raise ValueError('RESEARCH_DISCRIMINATOR_FACTS_REQUIRED ' + ident)
        if not set(distinguishing).issubset(set(supporting)):
            raise ValueError('RESEARCH_DISCRIMINATOR_NOT_LINKED ' + ident)
    elif state == 'NOT_DISCLOSED':
        why = discriminator.get('limitation')
        if not isinstance(why, str) or len(why.strip()) < 8:
            raise ValueError('RESEARCH_SOURCE_LIMITATION_REQUIRED ' + ident)
    else:
        raise ValueError('RESEARCH_DISCRIMINATOR_STATUS_INVALID ' + ident)
    next_test = claim.get('next_disclosure_test')
    if not isinstance(next_test, dict) or not _future_period(ledger['issuer']['fiscal_period'], next_test.get('period')):
        raise ValueError('RESEARCH_NEXT_TEST_NOT_FUTURE ' + ident)
    for k in ('metric', 'falsifies_when'):
        if not isinstance(next_test.get(k), str) or len(next_test[k].strip()) < 8:
            raise ValueError('RESEARCH_FALSIFIER_UNSPECIFIED ' + ident + ':' + k)
    return {'id': ident, 'evidence_status': claim['evidence_status'], 'calculations': calculations,
            'discriminator_status': state, 'future_test_period': next_test['period'],
            'needs_independent_financial_judgment': True}


def validate(ledger, brief):
    if not isinstance(brief, dict) or not isinstance(ledger, dict):
        raise ValueError('RESEARCH_BRIEF_OBJECT_REQUIRED')
    if brief.get('schema') != SCHEMA:
        raise ValueError('RESEARCH_BRIEF_SCHEMA_INVALID')
    issuer = ledger.get('issuer', {})
    source = ledger.get('source', {})
    if (not re.fullmatch('[0-9]{6}', str(issuer.get('code') or ''))
            or not re.fullmatch('[0-9a-f]{64}', str(source.get('original_bytes_sha256') or ''))
            or brief.get('issuer') != issuer.get('code')
            or brief.get('fiscal_period') != issuer.get('fiscal_period')
            or brief.get('source_pdf_sha256') != source.get('original_bytes_sha256')):
        raise ValueError('RESEARCH_BRIEF_WRONG_ISSUER_PERIOD_OR_SOURCE_SHA')
    if brief.get('sector_route') != rc.sector_of(ledger):
        raise ValueError('RESEARCH_BRIEF_SECTOR_ROUTE_MISMATCH')
    claims = brief.get('theses')
    if not isinstance(claims, list) or not claims:
        raise ValueError('RESEARCH_BRIEF_NEEDS_SOURCE_LINKED_THESES')
    reviewed = [_validate_claim(ledger, c) for c in claims]
    if len({r['id'] for r in reviewed}) != len(reviewed):
        raise ValueError('RESEARCH_DUPLICATE_THESIS_ID')
    return {'schema': 'financials.research_evidence_review.v1',
            'status': 'PASS_MACHINE_SOURCE_MATH_AND_STRUCTURAL_EVIDENCE_ONLY',
            'issuer': brief['issuer'], 'fiscal_period': brief['fiscal_period'],
            'source_pdf_sha256': brief['source_pdf_sha256'], 'theses': reviewed,
            'professional_causal_inference': 'NOT_CHECKED',
            'independent_financial_reviewer': 'NOT_CHECKED',
            'independent_visual_editor': 'NOT_CHECKED',
            'release_authorization': 'NOT_GRANTED_BY_THIS_GATE'}


def validate_file(ledger, path):
    if not Path(path).is_file():
        raise ValueError('RESEARCH_BRIEF_REQUIRED ' + str(path))
    return validate(ledger, json.loads(Path(path).read_text()))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--code', required=True)
    p.add_argument('--period')
    p.add_argument('--brief')
    p.add_argument('--out')
    a = p.parse_args(argv)
    import fin_intake as fi
    base = fi.folder(a.code, a.period)
    ledger = json.loads((base / 'source-ledger.json').read_text())
    try:
        result = validate_file(ledger, a.brief or base / 'research-brief.json')
    except (ValueError, KeyError) as e:
        print('RESEARCH_BRIEF_NOT_READY', str(e))
        return 1
    content = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if a.out:
        Path(a.out).write_text(content)
    print('RESEARCH_BRIEF_MACHINE_EVIDENCE_PASS', result['issuer'], result['fiscal_period'],
          'independent review', result['independent_financial_reviewer'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
