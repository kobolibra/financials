#!/usr/bin/env python3
"""EDITORIAL_V2 builder: AEI-style exhibits for any A-share source publication.

Commands (any issuer, any industry whose ledger uses the canonical keys of statement_extract):

  flowspec  write the income-flow stage definition (sources / stages / adjustments) for the V3 hero
            from canonical keys, closing every stage exactly; residuals become one explicit
            "其他营业收支" group of named terms, never a silent plug.
  findings  rank generic analytical findings (cost vs revenue, operating leverage, cash conversion,
            working-capital absorption, expense ratios, financing swing, impairment, NCI share,
            non-recurring share, segment divergence, leverage) with direction-checked sentences.

  numbers   print every computable growth / ratio / pp / balance change from the ledger, so the
            narrative is written against real directions (never "逐季提速" when a quarter fell).
  scaffold  write <folder>/v2-draft.json: data specs for kpi_board, growth_bars (P&L lines and every
            segment / region that has a prior-period cell), ratio_dumbbell (margins, cost ratios,
            segment gross margins), stock_delta (operating working-capital items), with TODO texts.
  apply     merge the authored draft into publication.json (design EDITORIAL_V2, glance, figure
            order, removals), every number as a quantified claim; update the editorial manifest
            (roles, hero after the KPI board, expanded titles) and the catalogue figure count.

Texts in the draft may use claim macros instead of numbers; `apply` turns them into audited
placeholders:  [g:rev]  growth %  [r:gm]  ratio %  [p:gm]  pp change  [y:parent_net]  亿元
[d:ar]  balance change 亿元 (signed).  Keys: ledger fact keys, or the built-in names gm / gp / op /
np / parent / opex3 / fin.  `apply` refuses any TODO, hand-typed decimal amount, or unknown macro.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal as D
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import fin_intake as fi  # noqa: E402

YI = D(100000000)
E = lambda k: [[k, 1]] if isinstance(k, str) else k
def diff(a, b): return E(a) + [[k, -c] for k, c in E(b)]
def prior(expr): return [[k + '_prior', c] for k, c in E(expr)]

# named expressions every industrial issuer has
NAMED = {'gm': ([['rev', 1], ['cogs', -1]], 'rev'), 'op': ('operating_profit', 'rev'), 'np': ('net_profit', 'rev'),
         'parent': ('parent_net', 'rev'), 'fin': ('finance', 'rev'),
         'opex3': ([['rd_expense', 1], ['admin', 1], ['selling', 1]], 'rev')}
GP = NAMED['gm'][0]
PL_LINES = [('营业收入', 'rev', False), ('营业成本', 'cogs', True), ('营业毛利', 'gp', False), ('销售费用', 'selling', True),
            ('管理费用', 'admin', True), ('研发费用', 'rd_expense', True), ('营业利润', 'operating_profit', False),
            ('归母净利润', 'parent_net', False), ('扣非归母净利润', 'adjusted_parent', False),
            ('销售商品收到的现金', 'sales_cash', False), ('经营现金净额', 'cfo', False)]
WC_ITEMS = [('应收账款', 'asset', 'ar'), ('应收票据', 'asset', 'notes_receivable'), ('应收款项融资', 'asset', 'receivable_financing'),
            ('合同资产', 'asset', 'contract_assets'), ('存货', 'asset', 'inventory'), ('预付款项', 'asset', 'prepayments'),
            ('应付账款', 'liability', 'ap'), ('应付票据', 'liability', 'notes_payable'), ('合同负债', 'liability', 'contract_liabilities')]
FIN_LINES = [('营业收入', 'rev', False), ('利息净收入', 'nii', False), ('手续费及佣金净收入', 'fee_net', False),
             ('保险服务收入', 'insurance_revenue', False), ('投资收益', 'investment_income', False), ('营业支出', 'opex_total', True),
             ('业务及管理费', 'admin_fin', True), ('营业利润', 'operating_profit', False), ('归母净利润', 'parent_net', False),
             ('经营现金净额', 'cfo', False)]
FIN_BS_ITEMS = [('发放贷款和垫款', 'asset', 'loans'), ('交易性金融资产', 'asset', 'trading_assets'), ('债权投资', 'asset', 'debt_investments'),
                ('其他债权投资', 'asset', 'other_debt_investments'), ('吸收存款', 'liability', 'deposits'),
                ('保险合同负债', 'liability', 'insurance_liabilities'), ('卖出回购金融资产款', 'liability', 'repo')]
REGION_WORDS = ('mainland', 'overseas', 'domestic', 'export', 'americas', 'europe', 'asia', 'north_america', 'southasia')


def load(code, period):
    base = fi.folder(code, period)
    return base, json.loads((base / 'source-ledger.json').read_text()), json.loads((base / 'publication.json').read_text())


def val(facts, expr):
    return sum((D(facts[k]['yuan']) * c for k, c in E(expr)), D(0))


def has(facts, expr):
    return all(k in facts and k + '_prior' in facts for k, _ in E(expr))


def expr_of(key):
    return GP if key == 'gp' else NAMED[key][0] if key in NAMED else key


def segments(facts):
    """Segment / region revenue keys with a prior-period cell (skips totals main_/other_)."""
    out = []
    for k in facts:
        if (k.endswith('_rev') and k + '_prior' in facts and k != 'rev' and not k.startswith(('main_', 'other_rev', 'other_business'))
                and not re.match(r'q\d_', k)):  # q3_rev is a single quarter, not a segment
            out.append(k[:-4])
    return out


def labels(facts, s):
    lab = re.sub(r'[（(].*?[）)]', '', facts[s + '_rev']['label']).strip()
    changed = True
    while changed:  # strip stacked suffixes such as 南亚对外交易收入 -> 南亚
        changed = False
        for w in ('地区对外交易', '对外交易', '主营业务收入', '主营收入', '营业收入', '收入', '主营', '地区'):
            if lab.endswith(w) and len(lab) > len(w) + 1:
                lab, changed = lab[:-len(w)], True
    return lab


# ---------------------------------------------------------------- numbers
def cmd_numbers(a):
    _, ledger, _ = load(a.code, a.period)
    f = ledger['facts']
    pct = lambda x: f'{x:+.1f}%'
    print(f"== {ledger['issuer']['name']} {ledger['issuer']['fiscal_period']} vs {ledger['issuer']['comparative_period']}")
    for lab, k, _ in PL_LINES:
        e = expr_of(k)
        if not has(f, e):
            continue
        cur, pr = val(f, e), val(f, prior(e))
        g = pct((cur / pr - 1) * 100) if pr > 0 else '上期≤0'
        print(f'  {lab:<10} {cur / YI:>10.2f}亿  上期 {pr / YI:>10.2f}亿  同比 {g:>8}  占收入 {cur / val(f, "rev") * 100:6.2f}% → 上期 {pr / val(f, "rev_prior") * 100:6.2f}%')
    for s in segments(f):
        cur, pr = val(f, s + '_rev'), val(f, s + '_rev_prior')
        gm = ''
        if s + '_cost' in f and s + '_cost_prior' in f:
            gm = f'  毛利率 {(1 - val(f, s + "_cost") / cur) * 100:.1f}% ← {(1 - val(f, s + "_cost_prior") / pr) * 100:.1f}%'
        kind = '地区' if s.startswith(REGION_WORDS) else '分部'
        print(f'  [{kind}] {labels(f, s):<12} {cur / YI:>10.2f}亿  同比 {pct((cur / pr - 1) * 100) if pr > 0 else "上期≤0":>8}{gm}')
    for lab, side, k in WC_ITEMS:
        if has(f, k):
            d = val(f, k) - val(f, k + '_prior')
            print(f'  [余额] {lab:<8} {val(f, k) / YI:>9.2f}亿  较{f[k + "_prior"]["period"]} {d / YI:+.2f}亿  {"占用" if (d > 0) == (side == "asset") and d else "提供"}资金')


# ---------------------------------------------------------------- scaffold
TODO = 'TODO'


def text_block(**extra):
    return dict(question='TODO？', takeaway=TODO, trend=TODO, analysis=TODO, counter=TODO, **extra)


def cmd_scaffold(a):
    base, ledger, story = load(a.code, a.period)
    f = ledger['facts']
    names = ledger['issuer'].get('period_names', {})
    periods = [names.get(ledger['issuer']['comparative_period'], ledger['issuer']['comparative_period']),
               names.get(ledger['issuer']['fiscal_period'], ledger['issuer']['fiscal_period'])]
    general = has(f, 'cogs')  # 一般企业格式; financial formats have no 营业成本 / gross margin
    tiles = [dict(label='营业收入', kind='money', value='rev', prior='rev_prior')]
    tiles.append(dict(label='毛利率', kind='ratio', num=GP, den='rev', prior_num=prior(GP), prior_den='rev_prior') if general else
                 dict(label='营业利润率', kind='ratio', num='operating_profit', den='rev', prior_num='operating_profit_prior', prior_den='rev_prior'))
    tiles.append(dict(label='归母净利润', kind='money', value='parent_net', prior='parent_net_prior'))
    for lab, k in (('经营现金净额', 'cfo'), ('销售商品收到的现金', 'sales_cash'), ('扣非归母净利润', 'adjusted_parent')):
        if has(f, k) and len(tiles) < 5:
            tiles.append(dict(label=lab, kind='money', value=k, prior=k + '_prior'))
    for lab, side, k in WC_ITEMS:
        if side == 'asset' and has(f, k) and len(tiles) < 6:
            tiles.append(dict(label=lab + '（期末余额）', kind='money', value=k, prior=k + '_prior', delta_label='较年初',
                              prior_period=f[k + '_prior']['period'], lower_is_better=True))
    segs = segments(f)
    lines = PL_LINES if general else FIN_LINES
    pairs = [[lab, prior(expr_of(k)) if k == 'gp' else k + '_prior', expr_of(k)] + ([{'lower_is_better': True}] if low else [])
             for lab, k, low in lines if has(f, expr_of(k)) and val(f, prior(expr_of(k))) > 0 and k not in ('adjusted_parent',)][:8]
    seg_pairs = [[labels(f, s), s + '_rev_prior', s + '_rev'] for s in segs if val(f, s + '_rev_prior') > 0][:8]
    rows = [dict(label='毛利率', num=GP, den='rev', prior_num=prior(GP), prior_den='rev_prior')] if general else []
    for lab, k in (('营业利润率', 'operating_profit'), ('归母净利率', 'parent_net')):
        rows.append(dict(label=lab, num=k, den='rev', prior_num=k + '_prior', prior_den='rev_prior'))
    for s in segs:
        if s + '_cost' in f and s + '_cost_prior' in f and len(rows) < 6:
            rows.insert(1, dict(label=labels(f, s) + '毛利率', num=[[s + '_rev', 1], [s + '_cost', -1]], den=s + '_rev',
                                prior_num=[[s + '_rev_prior', 1], [s + '_cost_prior', -1]], prior_den=s + '_rev_prior'))
    for lab, k in (('研发费用率', 'rd_expense'), ('销售费用率', 'selling'), ('管理费用率', 'admin')):
        if has(f, k) and len(rows) < 7 and val(f, k) >= 0 and val(f, k + '_prior') >= 0:
            rows.append(dict(label=lab, num=k, den='rev', prior_num=k + '_prior', prior_den='rev_prior', lower_is_better=True))
    # a dumbbell shows non-negative ratios only (loss makers: margins below zero go to the bridge instead)
    rows = [r for r in rows if val(f, r['num']) >= 0 and val(f, r['prior_num']) >= 0 and val(f, E(r['den'])) > 0 and val(f, E(r['prior_den'])) > 0]
    items = [[lab, side, k + '_prior', k] for lab, side, k in (WC_ITEMS if general else FIN_BS_ITEMS) if has(f, k)]
    dates = sorted({f[k[2]]['period'] for k in items} | {f[k[3]]['period'] for k in items}) if items else []
    draft = {
        'glance': [TODO] * 6,
        'new_figures': [
            dict(id='glance', family='kpi_board', nav='本期一览', eyebrow='AT A GLANCE', periods=periods, tiles=tiles,
                 chapter=dict(kicker='01 / 本期一览', title=TODO, summary=TODO), **text_block()),
            dict(id='growth', family='growth_bars', nav='增速对比', eyebrow='GROWTH', periods=periods,
                 pairs=(seg_pairs + pairs)[:8] if seg_pairs else pairs, chapter=dict(kicker='02 / 增长与盈利', title=TODO, summary=TODO), **text_block()),
            dict(id='margins', family='ratio_dumbbell', nav='利润率', eyebrow='MARGINS & COST RATIOS', periods=periods, rows=rows, **text_block()),
            dict(id='stock-delta', family='stock_delta', nav='资本占用', eyebrow='WHERE THE CASH WENT', dates=dates, items=items,
                 chapter=dict(kicker='03 / 现金与资本', title=TODO, summary=TODO), **text_block()),
        ],
        'order': ['glance', 'growth', 'margins'] + [x['id'] for x in story['figures']][:0] + ['stock-delta'] + [x['id'] for x in story['figures']],
        'remove': [x['id'] for x in story['figures'] if x['id'] in ('working-capital',)],
        'roles': {'glance': 'secondary', 'growth': 'secondary', 'margins': 'secondary', 'stock-delta': 'secondary'},
        'existing_chapters': {},
        'notes': 'Edit texts; reorder `order` (references may sit anywhere, they move to the reconciliation layer); '
                 'keep at most 2 signed bridges in the body (set others to reference in `roles`); macros: [g:key] [r:key] [p:key] [y:key] [d:key].',
    }
    out = Path(a.out) if getattr(a, 'out', None) else base / 'v2-draft.json'
    out.write_text(json.dumps(draft, ensure_ascii=False, indent=1) + '\n')
    print('V2_DRAFT_WRITTEN', out, 'figures', len(draft['new_figures']), 'segments', len(segs), 'wc', len(items))


# ---------------------------------------------------------------- flowspec (V3 income flow, general format)
OP_GROUPS = [('销售及管理费用', [['selling', -1], ['admin', -1]]), ('研发费用', [['rd_expense', -1]]), ('财务净损益', [['finance', -1]]),
             ('税金及附加', [['tax_surcharge', -1]]), ('投资及公允价值损益', [['investment_income', 1], ['fair_value', 1], ['fx_gain', 1], ['hedge_gain', 1]]),
             ('信用及资产减值', [['credit_impairment', 1], ['asset_impairment', 1]]), ('其他收益及处置', [['other_income', 1], ['asset_disposal', 1]])]


# lines that 营业总收入 / 营业总成本 carry besides 营业收入 and the standard costs (finance subsidiaries, insurers)
FIN_BLOCK = [['fin_interest_income', 1], ['fee_income', 1], ['earned_premium', 1], ['fin_interest_expense', -1], ['fee_expense', -1],
             ['surrender', -1], ['claims_net', -1], ['reserve_net', -1], ['policy_dividend', -1], ['reinsurance_cost', -1]]


def unit_scale(facts):
    """Printed unit of the statements (元 = 1, 千元 = 1000, 百万元 = 1e6)."""
    for k in ('rev', 'operating_profit', 'assets'):
        if k in facts:
            return D(facts[k]['source_cells'][0].get('unit_scale', '1'))
    return D(1)


def rounding_terms(facts, groups):
    """Statements printed in 千元/百万元 do not add up to the last unit. The tail is expressed as a
    combination of disclosed cells (operating profit minus gross profit minus every named group),
    so it stays auditable; only a tail within two printed units is accepted."""
    terms = [['operating_profit', 1]] + [[k, -c] for k, c in GP]
    for g in groups:
        terms += [[k, -c] for k, c in g['terms']]
    merged = {}
    for k, c in terms:
        merged[k] = merged.get(k, 0) + c
    return [[k, c] for k, c in merged.items() if c]


def flow_stages(facts):
    """Six closed stages from canonical keys. Raises when the statement is not in the general format."""
    for k in ('rev', 'cogs', 'operating_profit', 'pretax', 'net_profit', 'parent_net'):
        if k not in facts:
            raise SystemExit(f'FLOWSPEC_NEEDS_{k}: income flow V3 is defined for the 一般企业 format; financial formats use signed bridges')
    present = lambda terms: [[k, c] for k, c in terms if k in facts]
    groups = [{'label': lab, 'terms': present(t)} for lab, t in OP_GROUPS if present(t)]
    gross = val(facts, GP)
    residual = val(facts, 'operating_profit') - gross - sum((val(facts, g['terms']) for g in groups), D(0))
    if residual:
        # 营业总收入 / 营业总成本 also hold a finance subsidiary's or insurer's own lines: name them term by term
        extra = [[k, c] for k, c in FIN_BLOCK if k in facts]
        if extra:
            groups.append({'label': '金融及其他营业收支', 'terms': extra})
        left = val(facts, 'operating_profit') - gross - sum((val(facts, g['terms']) for g in groups), D(0))
        if left and abs(left) <= 2 * unit_scale(facts):
            groups.append({'label': '报表尾差（四舍五入）', 'terms': rounding_terms(facts, groups), 'net': True})
        elif left:
            raise SystemExit(f'FLOWSPEC_OPERATING_RESIDUAL {left}: run fin_intake auto and map the missing line items')
    pre = [[k, c] for k, c in (('operating_profit', 1), ('nonop_income', 1), ('nonop_expense', -1)) if k in facts]
    stages = [
        {'id': 'revenue', 'label': '营业收入', 'terms': [['rev', 1]], 'adjustments': []},
        {'id': 'gross', 'label': '营业毛利', 'terms': GP, 'adjustments': [{'label': '营业成本', 'terms': [['cogs', -1]]}]},
        {'id': 'operating', 'label': '营业利润', 'terms': [['operating_profit', 1]], 'adjustments': groups},
        {'id': 'pretax', 'label': '税前利润', 'terms': pre, 'adjustments': [{'label': l, 'terms': [[k, c]]} for l, k, c in (('营业外收益', 'nonop_income', 1), ('营业外支出', 'nonop_expense', -1)) if k in facts]},
        {'id': 'net', 'label': '合并净利润', 'terms': [['net_profit', 1]], 'adjustments': [{'label': '所得税费用', 'terms': [['income_tax', -1]]}]},
        {'id': 'parent', 'label': '归母净利润', 'terms': [['parent_net', 1]], 'adjustments': [{'label': '少数股东归属调整', 'terms': [['nci', -1]]}] if 'nci' in facts else []},
    ]
    for prev, st in zip(stages, stages[1:]):
        left = val(facts, st['terms']) - val(facts, prev['terms']) - sum((val(facts, a['terms']) for a in st['adjustments']), D(0))
        if left and abs(left) <= 2 * unit_scale(facts):
            tail = [[k, c] for k, c in st['terms']] + [[k, -c] for k, c in prev['terms']] + [[k, -c] for a in st['adjustments'] for k, c in a['terms']]
            merged = {}
            for k, c in tail:
                merged[k] = merged.get(k, 0) + c
            st['adjustments'].append({'label': '报表尾差（四舍五入）', 'terms': [[k, c] for k, c in merged.items() if c], 'net': True})
        elif left:
            raise SystemExit('FLOWSPEC_STAGE_NOT_CLOSED ' + st['id'])
    return stages


def income_bridge(facts, convention='expenses_positive'):
    """Fallback when the V3 income flow is refused (financial formats, losses, gains larger than the
    carried profit): one signed bridge from 营业收入 to 归母净利润 built from canonical keys, closed exactly."""
    d = lambda k: [[k, -1]]  # canonical ledger: expenses positive (statement_extract normalises at intake)
    rows = [['营业收入', 'rev', 'start']]
    if 'cogs' in facts:
        rows.append(['营业成本', d('cogs'), 'step'])
        for g in flow_stages_groups(facts):
            rows.append([g['label'], g['terms'], 'step'])
    elif 'opex_total' in facts:
        rows.append(['营业支出', d('opex_total'), 'step'])
    for lab, k, sign in (('营业外收入', 'nonop_income', 1), ('营业外支出', 'nonop_expense', -1), ('所得税费用', 'income_tax', -1)):
        if k in facts:
            rows.append([lab, [[k, 1]] if sign > 0 else d(k), 'step'])
    if 'nci' in facts:  # an attribution, not an expense line: always subtracted as printed
        rows.append(['少数股东损益', [['nci', -1]], 'step'])
    rows.append(['归母净利润', 'parent_net', 'total'])
    total = val(facts, 'rev') + sum((val(facts, r[1]) for r in rows[1:-1]), D(0))
    left = val(facts, 'parent_net') - total
    if left and abs(left) <= 3 * unit_scale(facts):
        terms = {'parent_net': 1, 'rev': -1}
        for r in rows[1:-1]:
            for k, c in E(r[1]):
                terms[k] = terms.get(k, 0) - c
        rows.insert(-1, ['报表尾差（四舍五入）', [[k, c] for k, c in terms.items() if c], 'step'])
        total = val(facts, 'parent_net')
    if total != val(facts, 'parent_net'):
        raise SystemExit(f'INCOME_BRIDGE_NOT_CLOSED residual {val(facts, "parent_net") - total}: map the missing line items (fin_intake auto)')
    return rows


def flow_stages_groups(facts):
    present = lambda terms: [[k, c] for k, c in terms if k in facts]
    groups = [{'label': lab, 'terms': present(t)} for lab, t in OP_GROUPS if present(t)]
    gross = val(facts, GP)
    if val(facts, 'operating_profit') - gross - sum((val(facts, g['terms']) for g in groups), D(0)):
        extra = [[k, c] for k, c in FIN_BLOCK if k in facts]
        if extra:
            groups.append({'label': '金融及其他营业收支', 'terms': extra})
    return groups


def cmd_flowspec(a):
    base, ledger, story = load(a.code, a.period)
    f = ledger['facts']
    stages = flow_stages(f)
    segs = [s for s in ledger.get('segments', []) if s.get('revenue')] if ledger.get('segments') else []
    sources = [{'label': s['label'], 'terms': [[s['revenue'], 1]]} for s in segs] or [{'label': '营业收入', 'terms': [['rev', 1]]}]
    spec = {'sources': sources, 'stages': stages,
            'editorial': {'primary_question': 'TODO？', 'income_basis': 'TODO', 'takeaway': 'TODO', 'counter': 'TODO',
                          'layout': 'INCOME_FLOW_V3', 'hero_position': 'after_first'},
            'figure_roles': {x['id']: {'role': 'secondary', 'rationale': 'TODO'} for x in story['figures']}, 'topics': []}
    out = Path(a.out) if a.out else base / 'editorial-spec.json'
    if out.exists() and not a.out:
        old = json.loads(out.read_text())
        old['stages'] = stages
        spec = old
    out.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + '\n')
    print('FLOWSPEC_WRITTEN', out, 'operating groups', len(stages[2]['adjustments']))


# ---------------------------------------------------------------- findings (generic analysis rules)
def growth_of(f, e):
    cur, pr = val(f, e), val(f, prior(e))
    return (cur / pr - 1) * 100 if pr > 0 else None


def ratio_pp(f, num, den='rev'):
    if not (has(f, num) and has(f, den)) or not val(f, den) or not val(f, prior(den)):
        return None
    return (val(f, num) / val(f, den) - val(f, prior(num)) / val(f, prior(den))) * 100


def findings(f):
    """Generic, industry-neutral rules. Each finding: id, score (materiality), and a sentence with macros
    whose direction words are chosen from the measured sign (so `apply` re-checks and audits them)."""
    out = []
    add = lambda i, score, text: out.append({'id': i, 'score': round(float(score), 2), 'text': text})
    up = lambda x, a='上升', b='下降': a if x > 0 else b
    gr = growth_of(f, 'rev') if has(f, 'rev') else None
    gc = growth_of(f, 'cogs') if has(f, 'cogs') else None
    if gr is not None and gc is not None:
        pp = ratio_pp(f, GP)
        # The publication renders pp to two decimals: never claim a 0.00pp decline.
        if pp is not None and abs(pp) >= D('0.005'):
            add('cost_vs_revenue', abs(gc - gr), f"营业收入同比[g:rev]%，营业成本同比[g:cogs]%，毛利率{up(pp)}[P:gm]个百分点。")
    go = growth_of(f, 'operating_profit') if has(f, 'operating_profit') else None
    if gr is not None and go is not None and abs(go - gr) >= D('0.01'):
        if gr > 0:
            tail = '营业利润同比增速高于收入，原因仍需核对费用及非经营项目' if go > gr else '营业利润同比增速低于收入，需核对成本、费用及减值'
        elif gr < 0:
            if go > 0:
                tail = '收入同比下降而营业利润增长，需核对非主营、费用及减值项目'
            elif go == 0:
                tail = '收入同比下降而营业利润基本持平'
            else:
                tail = '两者同比均下降，营业利润降幅更大' if go < gr else '两者同比均下降，营业利润降幅较小'
        else:
            tail = '收入同比持平而营业利润增长' if go > 0 else '收入同比持平而营业利润下降'
        add('operating_leverage', abs(go - gr) / 2, f"营业利润同比[g:operating_profit]%，营业收入同比[g:rev]%：{tail}。")
    if has(f, 'cfo') and has(f, 'net_profit') and val(f, 'net_profit') > 0 and val(f, 'net_profit_prior') > 0:
        cur, pr = val(f, 'cfo') / val(f, 'net_profit') * 100, val(f, 'cfo_prior') / val(f, 'net_profit_prior') * 100
        # A sub-0.01pp difference cannot justify a direction when both ratios print to two decimals.
        if abs(cur - pr) >= D('0.01'):
            add('cash_conversion', abs(cur - pr) / 5, f"经营现金净额相当于净利润的[r:cfo_np]%（上年同期[r:cfo_np_p]%），利润的现金含量{up(cur - pr, '提高', '下降')}。")
    # Balance-sheet comparisons are end-date vs previous year-end snapshots, not Y/Y
    # flow growth. Never rank or narrate an AR-vs-revenue "growth gap" across these bases.
    if has(f, 'ar') and val(f, 'ar_prior') > 0:
        ga = (val(f, 'ar') / val(f, 'ar_prior') - 1) * 100
        if ga and abs(val(f, 'ar') - val(f, 'ar_prior')) > YI / 200:
            add('receivables', abs(ga) / 4,
                f"应收账款较年初{up(ga, '增加', '减少')}[D:ar]亿元；余额变化本身不能证明回款效率改善或恶化，需结合账龄、销售收现及可比期间收入核验。")
    if has(f, 'inventory') and val(f, 'inventory_prior') > 0:
        gi = (val(f, 'inventory') / val(f, 'inventory_prior') - 1) * 100
        if gi and abs(val(f, 'inventory') - val(f, 'inventory_prior')) > YI / 200:
            add('inventory', abs(gi) / 4,
                f"存货较年初{up(gi, '增加', '减少')}[D:inventory]亿元；余额变化本身不能证明备货或去库存原因，需结合存货构成、跌价准备及周转核验。")
    for k, lab in (('selling', '销售费用率'), ('admin', '管理费用率'), ('rd_expense', '研发费用率')):
        pp = ratio_pp(f, k)
        if pp is not None and abs(pp) >= 0.3:
            add('ratio_' + k, abs(pp), f"{lab}{up(pp)}[P:{k}]个百分点。")
    if has(f, 'finance') and val(f, 'finance') * val(f, 'finance_prior') < 0:
        add('finance_swing', abs(ratio_pp(f, 'finance') or 0), f"财务费用由上年同期的{'净收益转为净支出' if val(f, 'finance') > 0 else '净支出转为净收益'}，本期为[y:finance]亿元。")
    imp = [k for k in ('credit_impairment', 'asset_impairment') if has(f, k)]
    if imp and has(f, 'rev'):
        cur = sum(val(f, k) for k in imp); pr = sum(val(f, k + '_prior') for k in imp)
        if cur < pr:
            add('impairment', abs(cur - pr) / val(f, 'rev') * 100, '信用及资产减值损失合计比上年同期增加。')
    if has(f, 'nci') and has(f, 'net_profit') and val(f, 'net_profit') > 0:
        share = val(f, 'nci') / val(f, 'net_profit') * 100
        if share >= 10:
            add('nci_share', share / 5, '少数股东损益占净利润的[r:nci_np]%，归母利润明显低于合并利润。')
    if has(f, 'adjusted_parent') and has(f, 'parent_net') and val(f, 'parent_net') > 0:
        gap = (val(f, 'parent_net') - val(f, 'adjusted_parent')) / val(f, 'parent_net') * 100
        if abs(gap) >= 5:
            tail = ('；扣非同比[g:adjusted_parent]%，归母同比[g:parent_net]%。'
                    if val(f, 'adjusted_parent_prior') > 0 and val(f, 'parent_net_prior') > 0
                    else '；比较期利润基数非正，常规同比增速不适用。')
            add('nonrecurring', abs(gap) / 3,
                f"非经常性损益使归母净利润{'高于' if gap > 0 else '低于'}扣非利润{tail}")
    if has(f, 'liabilities') and has(f, 'assets'):
        pp = (val(f, 'liabilities') / val(f, 'assets') - val(f, 'liabilities_prior') / val(f, 'assets_prior')) * 100
        if abs(pp) >= 1:
            add('leverage', abs(pp), f"资产负债率较年初{up(pp)}[P:leverage]个百分点。")
    segs = [s for s in segments(f) if not s.startswith(REGION_WORDS) and val(f, s + '_rev_prior') > 0]
    if len(segs) >= 2:
        gs = sorted(((growth_of(f, s + '_rev'), s) for s in segs), key=lambda x: x[0])
        if gs[-1][0] - gs[0][0] >= 5:
            add('segment_divergence', (gs[-1][0] - gs[0][0]) / 3, f"{labels(f, gs[-1][1])}同比[g:{gs[-1][1]}_rev]%，{labels(f, gs[0][1])}同比[g:{gs[0][1]}_rev]%，分部走势分化。")
    return sorted(out, key=lambda x: -x['score'])


def cmd_findings(a):
    _, ledger, story = load(a.code, a.period)
    C = Claims({'quantified_claims': {}}, ledger['facts'])
    sys.path.insert(0, str(ROOT / 'research' / 'shared'))
    from source_publication import expand_claims  # noqa: E402
    for x in findings(ledger['facts']):
        shown = expand_claims({'quantified_claims': C.c, 'p': C.expand(x['text'])}, ledger)['p']
        print(f"[{x['score']:6.2f}] {x['id']:<20} {shown}\n{'':29}{x['text']}")


# ---------------------------------------------------------------- apply
MACRO = re.compile(r'\[([grpydGPD]):([a-z0-9_]+)\]')  # upper case = absolute value, for use after a direction word


class Claims:
    def __init__(self, story, facts):
        self.c, self.f = story.setdefault('quantified_claims', {}), facts

    def _put(self, name, spec):
        if name in self.c and self.c[name] != spec:
            raise SystemExit('V2_CLAIM_NAME_CLASH ' + name)
        self.c[name] = spec
        return '{{' + name + '}}'

    def _num_den(self, key):
        special = {'cfo_np': ('cfo', 'net_profit'), 'nci_np': ('nci', 'net_profit'), 'leverage': ('liabilities', 'assets')}
        if key.endswith('_p') and key[:-2] in special:  # prior-period version of a ratio
            n, d = special[key[:-2]]
            return prior(n), prior(d)
        if key in special:
            return special[key]
        if key in NAMED:
            return NAMED[key]
        if key.endswith('_gm'):
            s = key[:-3]
            return [[s + '_rev', 1], [s + '_cost', -1]], s + '_rev'
        return key, 'rev'

    def macro(self, kind, key):
        if kind in 'GPD':  # magnitude after a direction word (上升/下降): same formula, absolute value
            name = self.macro(kind.lower(), key)[2:-2]
            spec = {k: v for k, v in self.c[name].items() if k != 'signed'}
            spec['absolute'] = True
            return self._put(name + '_abs', spec)
        if kind == 'g':
            e = GP if key == 'gm' else expr_of(key)
            self._need(e)
            if val(self.f, prior(e)) <= 0:
                raise SystemExit('V2_GROWTH_NONPOSITIVE_COMPARATIVE ' + key)
            return self._put('v2g_' + key, {'expression': diff(e, prior(e)), 'denominator': prior(e), 'scale': '1', 'multiplier': '100', 'decimals': 2, 'signed': True})
        if kind == 'y':
            e = expr_of(key)
            return self._put('v2y_' + key, {'expression': E(e), 'scale': '100000000', 'decimals': 2})
        if kind == 'd':
            self._need(key)
            return self._put('v2d_' + key, {'expression': diff(key, key + '_prior'), 'scale': '100000000', 'decimals': 2, 'signed': True})
        num, den = self._num_den(key)
        if kind == 'r':
            return self._put('v2r_' + key, {'expression': E(num), 'denominator': E(den), 'scale': '1', 'multiplier': '100', 'decimals': 2})
        base = 'v2b_' + key
        self._need(num); self._need(den)
        self.c[base] = {'expression': prior(num), 'denominator': prior(den), 'scale': '1', 'multiplier': '100', 'decimals': 2}
        return self._put('v2p_' + key, {'expression': E(num), 'denominator': E(den), 'less': base, 'scale': '1', 'multiplier': '100', 'decimals': 2, 'signed': True})

    def _need(self, e):
        for k, _ in E(e):
            if k not in self.f or k + '_prior' not in self.f:
                raise SystemExit(f'V2_MACRO_NEEDS_PRIOR_CELL {k}')

    UP = re.compile(r'(增长|增加|上升|提高|扩大|改善|回升|提速|加速)[^，。；、]{0,6}$')
    DOWN = re.compile(r'(下降|减少|下滑|降低|收缩|恶化|放缓|回落)[^，。；、]{0,6}$')

    def direction_check(self, text):
        """A direction word right before a signed macro must agree with the measured sign."""
        for m in MACRO.finditer(text):
            kind, key = m.groups()
            if kind.lower() not in 'gpd':
                continue
            head = text[:m.start()]
            name = self.macro(kind.lower(), key)[2:-2]
            spec = self.c[name]
            sys.path.insert(0, str(ROOT / 'research' / 'shared'))
            from source_publication import expand_claims  # noqa: E402
            shown = expand_claims({'quantified_claims': self.c, 'p': '{{' + name + '}}'}, {'facts': self.f, 'issuer': {}, 'source': {}})['p']
            neg = shown.startswith('-')
            if kind.isupper() and not (self.UP.search(head) or self.DOWN.search(head)):
                raise SystemExit(f'V2_ABSOLUTE_MACRO_NEEDS_DIRECTION_WORD: “{head[-12:]}{m.group(0)}”')
            if self.UP.search(head) and neg or self.DOWN.search(head) and not neg and shown not in ('+0.00', '0.00'):
                raise SystemExit(f'V2_DIRECTION_CONTRADICTS_DATA: “{head[-12:]}{m.group(0)}” but the value is {shown}')

    def expand(self, text):
        if TODO in text:
            raise SystemExit('V2_DRAFT_HAS_TODO: ' + text[:60])
        if re.search(r'[0-9]+\.[0-9]+\s*(亿|%|万)', MACRO.sub('', text)):
            raise SystemExit('V2_DRAFT_HAND_TYPED_NUMBER: ' + text[:80])
        self.direction_check(text)
        return MACRO.sub(lambda m: self.macro(m.group(1), m.group(2)), text)


def cmd_apply(a):
    sys.path.insert(0, str(ROOT / 'research' / 'shared'))
    from source_publication import expand_claims  # noqa: E402
    base, ledger, story = load(a.code, a.period)
    draft = json.loads((base / 'v2-draft.json').read_text())
    C = Claims(story, ledger['facts'])
    walk = lambda v: C.expand(v) if isinstance(v, str) else [walk(x) for x in v] if isinstance(v, list) else {k: walk(x) for k, x in v.items()} if isinstance(v, dict) else v
    TEXT = ('question', 'takeaway', 'trend', 'analysis', 'counter', 'chapter')
    old = {f['id']: f for f in story['figures']}
    new = {}
    for fg in draft['new_figures']:
        fg = dict(fg)
        for k in TEXT:
            if k in fg:
                fg[k] = walk(fg[k])
        fg.setdefault('identity', {'kpi_board': '各格为合并口径；流量与上年同期比较，余额与年初比较。', 'growth_bars': '各条为本期相对上年同期的同比增速；成本费用类增加标红。',
                                   'ratio_dumbbell': '空心点为上年同期，实心点为本期。', 'stock_delta': '各条为期末余额减年初余额；资产增加或负债减少占用资金。'}[fg['family']])
        new[fg['id']] = fg
    for fid, ch in draft.get('existing_chapters', {}).items():
        old[fid]['chapter'] = walk(ch)
    for fid in draft.get('remove', []):
        old.pop(fid)
    order = list(dict.fromkeys(draft['order']))
    missing = set(old) - set(order)
    if missing:
        raise SystemExit('V2_ORDER_MISSING ' + ','.join(sorted(missing)))
    story['figures'] = [new.get(i) or old[i] for i in order if i in new or i in old]
    story['design'] = 'EDITORIAL_V2'
    story['glance'] = walk(draft['glance'])
    for e in story.get('essays', []):
        if e.get('after') in draft.get('remove', []):
            e['after'] = 'stock-delta'
    # manifest roles, hero position, expanded titles
    mpath = fi.editorial_path(a.code, ledger['issuer']['fiscal_period'], a.period)
    m = json.loads(mpath.read_text())
    shown = {f['id']: f['question'] for f in expand_claims(story, ledger)['figures']}
    before = {f['id']: f for f in m['editorial']['figures']}
    figs = []
    for i, f in enumerate(story['figures']):
        r = dict(before.get(f['id'], {'summary': False, 'focus': []}))
        if f['id'] in draft['roles']:
            r['role'] = draft['roles'][f['id']]
            r['rationale'] = r.get('rationale') or 'EDITORIAL_V2 图族：' + f['nav']
        if 'role' not in r:
            raise SystemExit('V2_ROLE_MISSING ' + f['id'])
        r.update(index=i, id=f['id'], title=shown[f['id']])
        figs.append({k: r[k] for k in ('index', 'id', 'title', 'role', 'rationale', 'summary', 'focus') if k in r})
    roles = {f['id']: f['role'] for f in figs}
    issues = fi.lint(story, expand_claims(story, ledger), roles)
    if issues:
        raise SystemExit('V2_LINT ' + json.dumps(issues, ensure_ascii=False))
    (base / 'publication.json').write_text(json.dumps(story, ensure_ascii=False, indent=1) + '\n')
    m['editorial']['figures'] = figs
    m['editorial']['hero_position'] = 'after_first'
    mpath.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n')
    spec = base / 'editorial-spec.json'  # period reports regenerate the manifest from the spec: keep it in step
    if spec.exists():
        s = json.loads(spec.read_text())
        s['figure_roles'] = {f['id']: {k: f[k] for k in ('role', 'rationale', 'summary', 'focus') if k in f} for f in figs}
        s['editorial']['hero_position'] = 'after_first'
        spec.write_text(json.dumps(s, ensure_ascii=False, indent=1) + '\n')
    print('V2_APPLIED', a.code, a.period or '', len(figs), 'figures; next: publish, set catalogue figures = qa.json figures, browser QA')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    for name in ('numbers', 'scaffold', 'apply', 'flowspec', 'findings'):
        s = sub.add_parser(name); s.add_argument('--code', required=True); s.add_argument('--period')
        if name in ('scaffold', 'flowspec'):
            s.add_argument('--out', help='draft path (default <folder>/v2-draft.json)')
    a = p.parse_args(argv)
    {'numbers': cmd_numbers, 'scaffold': cmd_scaffold, 'apply': cmd_apply, 'flowspec': cmd_flowspec, 'findings': cmd_findings}[a.cmd](a)


if __name__ == '__main__':
    main()
