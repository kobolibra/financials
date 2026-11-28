"""Construct optional explanatory exhibits from verified relationships in one dossier."""
from decimal import Decimal

from coverage_review import check_dependencies
from research_capabilities import fact_ok, pair_ok


def _current(ledger, keys):
    return all(fact_ok(ledger['facts'], k, 'flow', ledger['issuer']['fiscal_period'])
               and ledger['facts'][k].get('unit') == '元' for k in keys)


def _amount(ledger, key):
    return Decimal(ledger['facts'][key]['yuan'])


def gross_profit_change(ledger):
    if not _current(ledger, ('rev', 'cogs')) or not all(pair_ok(ledger, k) for k in ('rev', 'cogs')):
        return None
    return dict(id='gross-profit-change', family='signed_bridge', nav='毛利变动',
                eyebrow='同期收入与成本', question='收入与成本各影响了多少毛利？', rows=[
                    ['上期毛利', [['rev_prior', 1], ['cogs_prior', -1]], 'start'],
                    ['收入变化', [['rev', 1], ['rev_prior', -1]], 'step'],
                    ['成本变化影响', [['cogs_prior', 1], ['cogs', -1]], 'step'],
                    ['本期毛利', [['rev', 1], ['cogs', -1]], 'total']])


def cash_reconciliation(ledger):
    keys = ledger.get('cash_reconciliation_keys', [])
    if not keys or len(keys) != len(set(keys)) or {'cfo', 'net_profit'}.intersection(keys):
        return None
    if not _current(ledger, ['net_profit', *keys, 'cfo']):
        return None
    amounts = [_amount(ledger, k) for k in keys]
    if _amount(ledger, 'net_profit') + sum(amounts) != _amount(ledger, 'cfo'):
        return None

    # Expose the largest disclosed adjustments individually; never net opposite
    # signs in the remaining group. The source table retains every original row.
    prominent = sorted(range(len(keys)), key=lambda i: -abs(amounts[i]))[:3]
    short_labels = {'inventory_release': '存货调节', 'operating_ar_change': '经营性应收调节',
                    'operating_ap_change': '经营性应付调节', 'depreciation': '折旧',
                    'provisions': '资产减值准备', 'credit_provision': '信用减值准备'}
    rows = [['合并净利润', 'net_profit', 'start']]
    rows.extend([ledger['facts'][k]['label'], k, 'step'] for k in keys)
    rows.append(['经营现金净额', 'cfo', 'total'])
    groups = [{'label': short_labels.get(keys[i], rows[i + 1][0]), 'indices': [i + 1]}
              for i in prominent]
    for sign, label in ((1, '其余调增'), (-1, '其余调减'), (0, '零额调节')):
        indices = [i + 1 for i, amount in enumerate(amounts)
                   if i not in prominent and (amount > 0) - (amount < 0) == sign]
        if indices:
            groups.append({'label': label, 'indices': indices})
    return dict(id='cash-formation', family='signed_bridge', nav='利润兑现',
                eyebrow='现金流补充资料', question='哪些调节拉开了利润与经营现金？',
                rows=rows, editorial_groups=groups)


def bank_exhibits(ledger):
    from source_publication import volume_rate_rows
    facts = ledger['facts']
    ratios = []
    for key, base, ident, nav in (
            ('fin_interest_income', 'average_earning_assets', 'earning-scale', '生息资产规模'),
            ('fin_interest_expense', 'average_interest_bearing_liabilities', 'funding-scale', '付息负债成本')):
        if not all(pair_ok(ledger, k) for k in (key, base)) or not _current(ledger, (key, base)):
            continue
        fig = dict(id=ident, family='volume_rate', nav=nav, eyebrow='合并利率分析',
                   question=nav + '如何影响' + facts[key]['label'] + '？', flow=key, average_balance=base)
        try:
            volume_rate_rows(ledger, fig)
        except ValueError:
            continue
        yield fig
        if min(_amount(ledger, key), _amount(ledger, key + '_prior')) >= 0:
            ratios.append(dict(label='资产期间收益率' if key == 'fin_interest_income' else '负债期间成本率',
                               num=key, den=base, prior_num=key + '_prior', prior_den=base + '_prior',
                               lower_is_better=key == 'fin_interest_expense'))
    if len(ratios) == 2:
        yield dict(id='interest-rates', family='ratio_dumbbell', nav='资产与负债定价',
                   eyebrow='合并口径 · 未年化', question='资产收益与负债成本如何变化？',
                   periods=[ledger['issuer']['comparative_period'], ledger['issuer']['fiscal_period']],
                   rows=ratios)
    keys = ('fin_interest_income', 'fin_interest_expense', 'nii')
    if not _current(ledger, keys) or not all(pair_ok(ledger, k) for k in keys):
        return
    income, expense, net = keys
    for suffix in ('', '_prior'):
        if _amount(ledger, income + suffix) - _amount(ledger, expense + suffix) != _amount(ledger, net + suffix):
            return
    yield dict(id='nii-change', family='signed_bridge', nav='净利息变动', eyebrow='同期收支贡献',
               question='利息收支各贡献多少净利息变动？', rows=[
                   ['上期净利息收入', net + '_prior', 'start'],
                   ['利息收入变动', [[income, 1], [income + '_prior', -1]], 'step'],
                   ['利息支出影响', [[expense, -1], [expense + '_prior', 1]], 'step'],
                   ['本期净利息收入', net, 'total']])


def candidates(ledger, sector):
    from source_publication import cited
    if sector == 'bank':
        figures = bank_exhibits(ledger)
    elif sector == 'industrial':
        figures = [gross_profit_change(ledger), cash_reconciliation(ledger)]
    else:
        return []
    eligible = []
    for fig in figures:
        if fig is None:
            continue
        try:
            check_dependencies(ledger, cited(fig))
        except ValueError as exc:
            if not str(exc).startswith('UNMAPPED_DEPENDENCY_BLOCKED'):
                raise
            continue
        eligible.append(fig)
    return eligible
