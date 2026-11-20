"""Metric-level comparison rules shared by research and publication."""
from decimal import Decimal
import re

ENDS = {'Q1': '03-31', 'Q2': '06-30', 'Q3': '09-30', 'Q4': '12-31',
        'H1': '06-30', '9M': '09-30', 'FY': '12-31'}
STARTS = {'Q2': '04-01', 'Q3': '07-01', 'Q4': '10-01'}


def interval(period):
    """Return the actual start, end and observation basis implied by a period."""
    if re.fullmatch(r'20\d{2}-\d{2}-\d{2}', period):
        return period, period, 'point'
    year, suffix = period[:4], period[4:]
    if not year.isdigit() or suffix not in ENDS:
        raise ValueError('UNSUPPORTED_COMPARISON_INTERVAL ' + period)
    mode = 'single_quarter' if suffix.startswith('Q') else 'cumulative'
    return year + '-' + STARTS.get(suffix, '01-01'), year + '-' + ENDS[suffix], mode


def require_pair(ledger, current, previous):
    facts = ledger['facts']
    now, old = facts[current], facts[previous]
    rule = ledger.get('comparison_basis', {}).get(current, {})
    if previous != current + '_prior':
        raise ValueError('COMPARISON_DIFFERENT_METRIC ' + current + ':' + previous)
    if any(now.get(k) != old.get(k) for k in ('type', 'scope', 'currency', 'unit', 'denominator_definition')):
        raise ValueError('COMPARISON_FACT_BASIS_MISMATCH ' + current)
    start, end, mode = interval(now['period'])
    pstart, pend, pmode = interval(old['period'])
    if now['type'] == 'flow':
        if (mode != pmode or mode == 'point' or int(start[:4]) != int(pstart[:4]) + 1
                or start[4:] != pstart[4:] or end[4:] != pend[4:]):
            raise ValueError('COMPARISON_FLOW_INTERVAL_MISMATCH ' + current)
    elif now['type'] != 'stock' or mode != 'point' or pmode != 'point' or pend != f'{int(end[:4])-1}-12-31':
        raise ValueError('COMPARISON_STOCK_OPENING_DATE_MISMATCH ' + current)
    if old.get('disclosure_version') == 'original_before_restatement' or rule.get('status') == 'unconfirmed' or (
            ledger.get('issuer', {}).get('restatement_review_required') and not rule):
        raise ValueError('COMPARISON_BASIS_UNCONFIRMED ' + current)
    if old.get('disclosure_version') == 'restated' or rule.get('status') == 'restated':
        archive = facts.get(rule.get('original_fact'), {})
        if (old.get('disclosure_version') != 'restated'
                or archive.get('disclosure_version') != 'original_before_restatement'
                or rule.get('original_fact') != current + '_original'
                or archive.get('period') != old['period']
                or any(archive.get(k) != old.get(k) for k in ('type', 'scope', 'currency', 'unit', 'denominator_definition'))
                or not archive.get('source_cells') or not rule.get('reason') or not rule.get('evidence_pages')):
            raise ValueError('COMPARISON_RESTATEMENT_PROOF_REQUIRED ' + current)
    return rule.get('status', 'same_report_comparative')


def require_growth_base(value, key):
    # Macros and growth bars present percentages to two decimals / amounts in 亿元.
    # An original amount under 50万元 rounds to 0.00亿元 at that presentation scale.
    if value < Decimal('500000'):
        raise ValueError('COMPARISON_GROWTH_BASE_TOO_SMALL ' + key)
