#!/usr/bin/env python3
"""EDITORIAL_V2 builder: AEI-style exhibits for any A-share source publication.

Three steps, one command each:

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
    tiles = [dict(label='营业收入', kind='money', value='rev', prior='rev_prior'),
             dict(label='毛利率', kind='ratio', num=GP, den='rev', prior_num=prior(GP), prior_den='rev_prior'),
             dict(label='归母净利润', kind='money', value='parent_net', prior='parent_net_prior')]
    for lab, k in (('经营现金净额', 'cfo'), ('销售商品收到的现金', 'sales_cash'), ('扣非归母净利润', 'adjusted_parent')):
        if has(f, k) and len(tiles) < 5:
            tiles.append(dict(label=lab, kind='money', value=k, prior=k + '_prior'))
    for lab, side, k in WC_ITEMS:
        if side == 'asset' and has(f, k) and len(tiles) < 6:
            tiles.append(dict(label=lab + '（期末余额）', kind='money', value=k, prior=k + '_prior', delta_label='较年初',
                              prior_period=f[k + '_prior']['period'], lower_is_better=True))
    segs = segments(f)
    pairs = [[lab, prior(expr_of(k)) if k == 'gp' else k + '_prior', expr_of(k)] + ([{'lower_is_better': True}] if low else [])
             for lab, k, low in PL_LINES if has(f, expr_of(k)) and val(f, prior(expr_of(k))) > 0 and k not in ('adjusted_parent',)][:8]
    seg_pairs = [[labels(f, s), s + '_rev_prior', s + '_rev'] for s in segs if val(f, s + '_rev_prior') > 0][:8]
    rows = [dict(label='毛利率', num=GP, den='rev', prior_num=prior(GP), prior_den='rev_prior')]
    for lab, k in (('营业利润率', 'operating_profit'), ('归母净利率', 'parent_net')):
        rows.append(dict(label=lab, num=k, den='rev', prior_num=k + '_prior', prior_den='rev_prior'))
    for s in segs:
        if s + '_cost' in f and s + '_cost_prior' in f and len(rows) < 6:
            rows.insert(1, dict(label=labels(f, s) + '毛利率', num=[[s + '_rev', 1], [s + '_cost', -1]], den=s + '_rev',
                                prior_num=[[s + '_rev_prior', 1], [s + '_cost_prior', -1]], prior_den=s + '_rev_prior'))
    for lab, k in (('研发费用率', 'rd_expense'), ('销售费用率', 'selling'), ('管理费用率', 'admin')):
        if has(f, k) and len(rows) < 7 and val(f, k) >= 0 and val(f, k + '_prior') >= 0:
            rows.append(dict(label=lab, num=k, den='rev', prior_num=k + '_prior', prior_den='rev_prior', lower_is_better=True))
    items = [[lab, side, k + '_prior', k] for lab, side, k in WC_ITEMS if has(f, k)]
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


# ---------------------------------------------------------------- apply
MACRO = re.compile(r'\[([grpyd]):([a-z0-9_]+)\]')


class Claims:
    def __init__(self, story, facts):
        self.c, self.f = story.setdefault('quantified_claims', {}), facts

    def _put(self, name, spec):
        if name in self.c and self.c[name] != spec:
            raise SystemExit('V2_CLAIM_NAME_CLASH ' + name)
        self.c[name] = spec
        return '{{' + name + '}}'

    def _num_den(self, key):
        if key in NAMED:
            return NAMED[key]
        if key.endswith('_gm'):
            s = key[:-3]
            return [[s + '_rev', 1], [s + '_cost', -1]], s + '_rev'
        return key, 'rev'

    def macro(self, kind, key):
        if kind == 'g':
            e = GP if key == 'gm' else expr_of(key)
            self._need(e)
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

    def expand(self, text):
        if TODO in text:
            raise SystemExit('V2_DRAFT_HAS_TODO: ' + text[:60])
        if re.search(r'[0-9]+\.[0-9]+\s*(亿|%|万)', MACRO.sub('', text)):
            raise SystemExit('V2_DRAFT_HAND_TYPED_NUMBER: ' + text[:80])
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
    for name in ('numbers', 'scaffold', 'apply'):
        s = sub.add_parser(name); s.add_argument('--code', required=True); s.add_argument('--period')
        if name == 'scaffold':
            s.add_argument('--out', help='draft path (default <folder>/v2-draft.json)')
    a = p.parse_args(argv)
    {'numbers': cmd_numbers, 'scaffold': cmd_scaffold, 'apply': cmd_apply}[a.cmd](a)


if __name__ == '__main__':
    main()
