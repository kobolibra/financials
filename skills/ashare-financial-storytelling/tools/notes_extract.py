#!/usr/bin/env python3
"""Company-agnostic extraction of the revenue / cost notes, the cash-flow reconciliation and the
key-figures table of any A-share periodic report.

Column meaning is never trusted from a header. Every table is proven by the report's OWN numbers:

  composition table (深市"营业收入构成"):  amount, share %, prior amount, share %, YoY %
        proof: share == amount / dimension total and YoY == amount / prior - 1, at printed precision
  margin table (10%以上 / 沪市"主营业务分行业、分产品、分地区"):  revenue, cost, margin %, three changes
        proof: margin == 1 - cost / revenue at printed precision
  decomposition note ("营业收入、营业成本的分解信息" / "营业收入和营业成本情况"):  revenue, cost
        [, prior revenue, prior cost]   proof: rows of one dimension add up to the printed 合计 or to
        营业收入 / 主营业务收入 from the statements
  cash-flow reconciliation ("将净利润调节为经营活动现金流量"):  proof: 净利润 + all lines == 经营活动现金流量净额
  key figures ("主要会计数据"):  prior column = the one that reproduces the printed YoY %

A dimension (product / industry / region / channel) is used as a revenue partition only when it is
EXHAUSTIVE: its rows add up exactly to 营业收入 (or to 主营业务收入, then 其他业务收入 is the remaining
source). Partial tables (only items above 10 %) never become a partition; their costs are attached to a
partition row only when the revenue cell is identical (same scope). Anything that cannot be proven is
reported, not used.
"""
from __future__ import annotations

import re
from decimal import Decimal as D, ROUND_HALF_UP

# dimension headers, searched inside short header lines ("（2）按产品类别列示主营业务收入和主营业务成本")
DIMS = [
    ('product', r'(分产品|按(商品|产品)(类型|类别)?|商品类型|产品类型|产品类别)'),
    ('industry', r'(分行业|按行业|行业类型)'),
    ('region', r'(分地区|按(经营)?地区|经营地区|地区信息|国家或地区|地区分布)'),
    ('channel', r'(分销售模式|按销售(渠道|模式)|销售渠道|销售模式)'),
    ('unlabelled', r'(市场信息|按市场|分市场|客户类型)'),
]
DIM_RE = [(k, re.compile(p)) for k, p in DIMS]
AMT = re.compile(r'^[(（]?-?[0-9][0-9,]*\.[0-9]{2}[)）]?$|^[(（]?-?[0-9]{1,3}(,[0-9]{3})+[)）]?$')
PCT = re.compile(r'^[(（]?[-+]?[0-9]+(\.[0-9]+)?%?[)）]?$')
SKIP = re.compile(r'(合计|小计|总计|抵销|抵消|分部间|内部交易)')


def num(p):
    t = p.strip().replace(',', '').replace('−', '-')
    neg = t.startswith(('(', '（'))
    t = t.strip('()（）%')
    if not re.fullmatch(r'[-+]?[0-9]+(\.[0-9]+)?', t):
        raise NotANumber(p)
    v = D(t)
    return -v if neg else v


def close_pct(computed, printed):
    """Printed percentage reproduced at its own precision (one unit of the last digit for rounding style)."""
    t = printed.strip().strip('()（）%')
    if not re.fullmatch(r'[-+]?[0-9]+(\.[0-9]+)?', t.replace(',', '')):
        return False
    places = len(t.split('.')[1]) if '.' in t else 0
    q = D(1).scaleb(-places)
    return abs(computed.quantize(q, rounding=ROUND_HALF_UP) - num(printed)) <= q


def dim_of(label):
    if len(label) > 40:
        return None
    for k, rx in DIM_RE:
        if rx.search(label):
            return k
    return None


def tables(doc, rows_on_page, squash, unit_of, pages=None):
    """Candidate segment rows: label, dimension (from the nearest header), amount cells, percentage cells.

    The meaning of each column is NOT decided here; `partitions` proves it with sums."""
    import statement_extract as se
    unit_line = lambda t: unit_of(t, strict=True) if re.search(r'单位', t) else None
    out, dim, unit, last_page, header = [], None, D(1), -9, None
    for p in (pages or range(1, len(doc) + 1)):
        text = squash(doc[p - 1].get_text())
        if not re.search(r'(营业收入|营业成本|主营业务)', text):
            continue
        raw = rows_on_page(doc[p - 1])
        lab_by_y = {x['y']: x for x in se.labelled_rows(raw)}
        if p - last_page != 1:
            dim, unit, header = None, D(1), None
        last_page = p
        for x in raw:
            t = squash(x['label'])
            words = re.findall(r'(收入|成本|毛利率|毛利)', t)
            if not x['numbers'] and len(words) >= 2 and len(t) <= 60:
                header = words  # column header line, e.g. 主营业务收入主营业务成本主营业务收入主营业务成本
            if not x['numbers']:
                u = unit_line(t)
                if u is not None:
                    unit = u
                d = dim_of(re.sub(r'^[（(]?[0-9一二三四五六七八九十]+[)）、.．]', '', t))
                if d:
                    dim = d
                elif len(t) > 40:
                    dim = None  # prose ends a table
                continue
            r = lab_by_y.get(x['y'], x)
            lab = re.sub(r'^(其中[:：])', '', squash(r['label']))
            lab = re.sub(r'(增加|减少)[0-9.]+个?百分点$', '', lab)
            d = dim_of(lab) if not re.search(r'[0-9]', lab) else None
            if d and lab in ('分行业', '分产品', '分地区', '分销售模式'):
                dim = d
            amts = [c for c in r['numbers'] if AMT.match(c['printed'].strip())]
            pcts = [c for c in r['numbers'] if c not in amts and PCT.match(c['printed'].strip())]
            if not amts or not lab or len(lab) > 30:
                continue
            kind = 'plain'
            if len(amts) >= 2 and pcts and r['numbers'].index(amts[1]) - r['numbers'].index(amts[0]) == 1:
                # revenue, cost, margin% ... : the margin must be reproduced
                try:
                    if close_pct((1 - num(amts[1]['printed']) / num(amts[0]['printed'])) * 100, pcts[0]['printed']):
                        kind = 'margin'
                except (NotANumber, ZeroDivisionError, ArithmeticError):
                    pass
            if len(amts) >= 2 and len(pcts) >= 3 and kind == 'plain':
                # amount, share%, prior amount, share%, YoY% : the YoY must be reproduced
                try:
                    if close_pct((num(amts[0]['printed']) / num(amts[1]['printed']) - 1) * 100, pcts[-1]['printed']):
                        kind = 'composition'
                except (NotANumber, ZeroDivisionError, ArithmeticError):
                    pass
            out.append({'page': p, 'y': r['y'], 'label': lab, 'dim': dim, 'amts': amts, 'unit': unit, 'kind': kind, 'header': header,
                        'total': bool(SKIP.search(lab)) or bool(dim_of(lab) and len(lab) <= 4)})
    return out


def cell_value(row, j):
    return num(row['amts'][j]['printed']) * row['unit']


MAIN_OTHER = re.compile(r'(主营业务|其他业务)(收入)?')
REGION_HINT = re.compile(r'(内销|外销|境内|境外|国内|国外|海外|中国大陆|大陆|港澳台|地区|洲|华东|华南|华北|华中|西南|西北|东北|欧洲|美洲|亚太|北美|南亚|东南亚|日本|韩国|美国|其他国家|其余)')


def partitions(rows, totals):
    """Exhaustive dimensions with every column role proven by sums.

    totals: {'rev','main_rev','cogs','main_cost', and *_prior}. A contiguous run of non-total rows of one
    table is a partition when some amount column adds up exactly to 营业收入 or 主营业务收入 (the scope).
    Each other column then gets a role only if it adds up to the matching total of the same scope:
    cost (营业成本 / 主营业务成本), prior revenue, prior cost. Unproven columns are ignored."""
    tabs, cur = [], []
    for r in rows:
        if cur and (r['page'] - cur[-1]['page'] > 1 or (r['page'] == cur[-1]['page'] and r['y'] - cur[-1]['y'] > 120)
                    or len(r['amts']) != len(cur[-1]['amts']) or (r['dim'] and cur[-1]['dim'] and r['dim'] != cur[-1]['dim'] and not cur[-1]['total'])):
            tabs.append(cur); cur = []
        cur.append(r)
    if cur:
        tabs.append(cur)
    scopes = {'rev': ('rev', 'cogs'), 'main_rev': ('main_rev', 'main_cost')}
    found = []
    for t in tabs:
        items = [r for r in t if not r['total']]
        n, taken = len(items), set()
        width = min((len(r['amts']) for r in items), default=0)
        for length in range(n, 1, -1):
            for i in range(0, n - length + 1):
                if any(j in taken for j in range(i, i + length)):
                    continue
                run = items[i:i + length]
                if len({r['dim'] for r in run if r['dim']}) > 1:
                    continue
                if all(MAIN_OTHER.fullmatch(r['label']) for r in run):
                    continue  # the 主营业务 / 其他业务 split is the note itself, not a business dimension
                if any(re.search(r'其中|分类其|[：:]$|百分点|(增加|减少)[0-9]', r['label']) for r in run):
                    continue  # labels broken by a nested layout cannot name a business
                col_sum = lambda j: sum((cell_value(r, j) for r in run), D(0))
                sums = [col_sum(j) for j in range(width)]
                hit = next(((sc, j) for j in range(width) for sc in scopes if totals.get(sc) is not None and sums[j] == totals[sc]), None)
                if hit is None:
                    continue
                scope, rj = hit
                rk, ck = scopes[scope]
                roles = {'rev': rj}
                for role, key in (('cost', ck), ('rev_prior', rk + '_prior'), ('cost_prior', ck + '_prior')):
                    j = next((j for j in range(width) if j not in roles.values() and totals.get(key) is not None and sums[j] == totals[key]), None)
                    if j is not None:
                        roles[role] = j
                # costs that no total can prove (主营业务成本 not disclosed): accept the header's column
                # meaning only when it agrees with every column proven by sums
                hdr = run[0].get('header')
                if 'cost' not in roles and hdr and len(hdr) == width and hdr[rj] == '收入' and all(hdr[j] == '收入' for r_, j in roles.items() if r_.startswith('rev')):
                    nxt = lambda j0: next((j for j in range(j0 + 1, width) if hdr[j] == '成本'), None)
                    cj = nxt(rj)
                    if cj is not None and cj not in roles.values() and (roles.get('rev_prior') is None or cj < roles['rev_prior']):
                        roles['cost'] = cj; roles['cost_proof'] = 'HEADER_CONSISTENT_WITH_PROVEN_REVENUE_COLUMNS'
                    if 'rev_prior' in roles:
                        pj = nxt(roles['rev_prior'])
                        if pj is not None and pj not in roles.values():
                            roles['cost_prior'] = pj
                dim = next((r['dim'] for r in run if r['dim']), None)
                if all(REGION_HINT.search(r['label']) for r in run):
                    dim = 'region'
                k_end = t.index(run[-1])
                total_row = next((x for x in t[k_end + 1:k_end + 2] if x['total'] and len(x['amts']) == width), None)
                if total_row is not None and any(cell_value(total_row, j) != sum((cell_value(r, j) for r in run), D(0)) for j in range(width)):
                    total_row = None  # a printed 合计 must equal the rows in every column
                found.append({'dim': dim or 'unlabelled', 'scope': scope, 'kind': run[0]['kind'], 'rows': run, 'roles': roles, 'total_row': total_row,
                              'has_prior': 'rev_prior' in roles, 'has_cost': 'cost' in roles})
                taken.update(range(i, i + length))
    return found


def extract_segments(doc, rows_on_page, squash, unit_of, facts):
    rows = tables(doc, rows_on_page, squash, unit_of)
    out = note_main_other(doc, rows_on_page, squash, unit_of, facts)
    tot = lambda k: D(out[k]['yuan']) if k in out else (D(facts[k]['yuan']) if k in facts else None)
    totals = {'rev': tot('rev'), 'cogs': tot('cogs'), 'rev_prior': tot('rev_prior'), 'cogs_prior': tot('cogs_prior'),
              'main_rev': tot('main_rev'), 'main_cost': tot('main_cost'), 'main_rev_prior': tot('main_rev_prior'), 'main_cost_prior': tot('main_cost_prior')}
    parts = partitions(rows, totals)
    chosen = {}
    for pt in sorted(parts, key=lambda x: (not x['has_cost'], not x['has_prior'], x['scope'] != 'rev')):
        chosen.setdefault(pt['dim'], pt)
    fy = facts['rev']['period'] if 'rev' in facts else None
    cp = facts.get('rev_prior', {}).get('period')
    summary = []
    for dim, pt in chosen.items():
        prefix = {'product': 'seg', 'industry': 'ind', 'region': 'region', 'channel': 'channel', 'unlabelled': 'part'}[dim]
        entries = []
        for i, r in enumerate(pt['rows'], 1):
            key = f'{prefix}{i}'
            entries.append({'key': key, 'label': r['label']})
            for role, j in pt['roles'].items():
                if not isinstance(j, int):
                    continue
                prior = role.endswith('_prior')
                kind = '收入' if role.startswith('rev') else '成本'
                c = r['amts'][j]
                out[f"{key}_{role}"] = _fact(c, r['unit'], f"{r['label']}（{DIM_NAME[dim]}{kind}）", r['page'], cp if prior else fy, prior, r['label'])
        tr = pt.get('total_row')
        if pt['scope'] == 'main_rev' and tr is not None and 'cost' in pt['roles'] and 'main_cost' not in out:
            out['main_cost'] = _fact(tr['amts'][pt['roles']['cost']], tr['unit'], '主营业务成本（分类表合计）', tr['page'], fy, False, tr['label'])
        if pt['scope'] == 'main_rev' and tr is not None and 'cost_prior' in pt['roles'] and 'main_cost_prior' not in out:
            out['main_cost_prior'] = _fact(tr['amts'][pt['roles']['cost_prior']], tr['unit'], '主营业务成本（分类表合计）', tr['page'], cp, True, tr['label'])
        summary.append({'dimension': dim, 'scope': pt['scope'], 'table': pt['kind'], 'page': pt['rows'][0]['page'], 'rows': len(entries),
                        'with_prior': pt['has_prior'], 'with_cost': len(entries) if 'cost' in pt['roles'] else 0,
                        'roles': sorted(k for k, v in pt['roles'].items() if isinstance(v, int)), 'cost_proof': pt['roles'].get('cost_proof', 'SUM_EQUALS_STATEMENT_TOTAL' if 'cost' in pt['roles'] else None),
                        'entries': entries})
    used = {id(r) for p in parts for r in p['rows']}
    rejected = sorted({(r['page'], r['kind']) for r in rows if id(r) not in used and not r['total']})
    return out, summary, rejected


DIM_NAME = {'product': '分产品', 'industry': '分行业', 'region': '分地区', 'channel': '分销售模式', 'unlabelled': '收入分类'}


def fact(r, field, period, label, prior=False):
    c = r['cells'][r[field]]
    cell = {'bbox': c['bbox'], 'printed': c['printed'], 'wrapped_number': bool(c.get('wrapped'))}
    if r['unit'] != 1:
        cell['unit_scale'] = str(r['unit'])
    return {'yuan': str(value(r, field)), 'label': label, 'page': r['page'], 'type': 'flow', 'period': period, 'scope': 'consolidated',
            'classification': 'DISCLOSED', 'unit': '元', 'currency': 'CNY', 'source_cells': [cell], 'source_row_label': r['label'],
            'source_column': '上期/期初' if prior else '本期/期末', 'extraction': 'NOTES_EXTRACT_V1'}


def note_main_other(doc, rows_on_page, squash, unit_of, facts):
    """营业收入和营业成本 note: rows 主营业务 / 其他业务 / 合计. Column roles are proven by the 合计 row:
    a column is current revenue / current cost / prior revenue / prior cost only when 合计 equals that
    statement figure (layouts with 2 or 4 columns, revenue-only tables, 收入 成本 收入 成本 all work)."""
    targets = {k: D(facts[k]['yuan']) for k in ('rev', 'cogs', 'rev_prior', 'cogs_prior') if k in facts}
    if 'rev' not in targets:
        return {}
    fy, cp = facts['rev']['period'], facts.get('rev_prior', {}).get('period')
    for p in range(1, len(doc) + 1):
        t = squash(doc[p - 1].get_text())
        if '主营业务' not in t or '其他业务' not in t:
            continue
        rows = rows_on_page(doc[p - 1])
        unit = D(1)
        for i, r in enumerate(rows):
            lab = squash(r['label'])
            if '单位' in lab and not r['numbers']:
                unit = unit_of(lab, strict=True)
            if lab not in ('主营业务', '主营业务收入'):
                continue
            block = {}
            for rr in rows[i:i + 4]:
                l2 = squash(rr['label'])
                amts = [n for n in rr['numbers'] if AMT.match(n['printed'].strip())]
                name = 'main' if l2.startswith('主营') else 'other' if l2.startswith('其他业务') else 'total' if l2 == '合计' else None
                if name and amts:
                    block[{'other': 'other_business'}.get(name, name)] = amts
            if 'main' not in block or 'total' not in block:
                continue
            tv = [num(c['printed']) * unit for c in block['total']]
            roles = {}
            for role, key in (('rev', 'rev'), ('cost', 'cogs'), ('rev_prior', 'rev_prior'), ('cost_prior', 'cogs_prior')):
                j = next((j for j in range(len(tv)) if j not in roles.values() and key in targets and tv[j] == targets[key]), None)
                if j is not None:
                    roles[role] = j
            if 'rev' not in roles:
                continue
            out = {}
            for part, name in (('main', '主营业务'), ('other_business', '其他业务')):
                if part not in block:
                    continue
                cells = block[part]
                # a row may omit a blank cell (其他业务 cost 0): only use it when the row has every column
                if len(cells) != len(block['total']):
                    continue
                for role, j in roles.items():
                    prior = role.endswith('_prior')
                    out[f"{part}_{role}"] = _fact(cells[j], unit, name + ('收入' if role.startswith('rev') else '成本'), p, cp if prior else fy, prior, name)
            # 主营 + 其他 must equal 合计 for every proven column
            if all(f"main_{ro}" in out and f"other_business_{ro}" in out and D(out[f"main_{ro}"]['yuan']) + D(out[f"other_business_{ro}"]['yuan']) == tv[j] for ro, j in roles.items()):
                return out
            return {k: v for k, v in out.items() if k.startswith('main_')} if all(f"main_{ro}" in out for ro in roles) else {}
    return {}


# ---------------------------------------------------------------- cash-flow reconciliation
RECON = [
    ('provisions', r'^(资产减值准备|资产减值损失|计提的资产减值准备|资产减值准备及信用减值损失|信用减值损失及资产减值损失)$'),
    ('credit_provision', r'^(信用减值损失|信用减值准备|计提的信用减值准备)$'),
    ('depreciation', r'^(固定资产折旧.*|投资性房地产折旧|折旧|固定资产及投资性房地产折旧)$'),
    ('rou_amort', r'^使用权资产(折旧|摊销)$'),
    ('intangible_amort', r'^无形资产摊销$'),
    ('deferred_amort', r'^长期待摊费用摊销$'),
    ('disposal_loss', r'^处置固定资产、?无形资产和其他长期资产的(损失|收益|净损失|净收益)(（收益）)?$'),
    ('scrap_loss', r'^固定资产报废损失(（收益）)?$'),
    ('fair_loss', r'^公允价值变动损失(（收益）)?$'),
    ('finance_adjustment', r'^财务费用(（收益）)?$'),
    ('investment_loss', r'^投资损失(（收益）)?$'),
    ('dta_decrease', r'^递延所得税资产(减少|的减少)(（增加）)?$'),
    ('dtl_increase', r'^递延所得税负债(增加|的增加)(（减少）)?$'),
    ('inventory_release', r'^存货的(减少|增加)(（增加）|（减少）)?$'),
    ('operating_ar_change', r'^经营性应收项目的(减少|增加)(（增加）|（减少）)?$'),
    ('operating_ap_change', r'^经营性应付项目的(增加|减少)(（减少）|（增加）)?$'),
    ('share_payment', r'^(股份支付费用|以权益结算的股份支付)$'),
    ('cfo_other', r'^其他$'),
]
RECON_RE = [(k, re.compile(p)) for k, p in RECON]


def _fact(c, unit, label, page, period, prior, row_label, flip=False):
    cell = {'bbox': c['bbox'], 'printed': c['printed'], 'wrapped_number': False}
    if unit != 1:
        cell['unit_scale'] = str(unit)
    return {'yuan': str(num(c['printed']) * unit), 'label': label + ('（比较期）' if prior else ''), 'page': page, 'type': 'flow', 'period': period,
            'scope': 'consolidated', 'classification': 'DISCLOSED', 'unit': '元', 'currency': 'CNY', 'source_cells': [cell],
            'source_row_label': row_label, 'source_column': '上期/期初' if prior else '本期/期末', 'extraction': 'NOTES_EXTRACT_V1'}


MARK = re.compile(r'将净(利润|亏损)(（亏损）|\(亏损\))?调节为经营活动(的)?现金')
END = re.compile(r'^经营活动(产生|使用)的现金流量净额$')
CELL = lambda t: AMT.match(t) or re.fullmatch(r'[(（]?[-−]?[0-9]+\.[0-9]{2}[)）]?', t)


def reconciliation(doc, rows_on_page, squash, unit_of, facts, norm):
    """净利润 → 经营活动现金流量净额. Accepted only when the table's 净利润 and result equal the
    consolidated statements (the parent-company table that follows never qualifies) and the lines add
    up exactly; the prior column is kept only if it closes too."""
    import statement_extract as se
    if not all(k in facts for k in ('net_profit', 'cfo')):
        return {}, None
    NP, CFO = D(facts['net_profit']['yuan']), D(facts['cfo']['yuan'])
    NPp = D(facts['net_profit_prior']['yuan']) if 'net_profit_prior' in facts else None
    CFOp = D(facts['cfo_prior']['yuan']) if 'cfo_prior' in facts else None
    fy, cp = facts['cfo']['period'], facts.get('cfo_prior', {}).get('period')
    last = None
    for p in range(1, len(doc) + 1):
        if not MARK.search(squash(doc[p - 1].get_text())):
            continue
        # rows from the marker to the result, over at most three pages
        seq, started, unit = [], False, None
        for q in range(p, min(len(doc), p + 2) + 1):
            raw = rows_on_page(doc[q - 1])
            lab = {r['y']: r for r in se.labelled_rows(raw)}
            for r in raw:
                t = squash(r['label'])
                if not started:
                    if '单位' in t:
                        unit = unit_of(t, strict=True)
                    if MARK.search(t):
                        started = True
                    continue
                seq.append(dict(lab.get(r['y'], r), page=q))
                if r['numbers'] and END.match(norm(lab.get(r['y'], r)['label'])):
                    break
            else:
                continue
            break
        if not started:
            continue
        unit = unit or D(1)
        num_rows = [r for r in seq if any(CELL(c['printed'].strip()) for c in r['numbers'])]
        bands = se.amount_columns(num_rows)
        if not bands:
            last = {'page': p, 'status': 'NO_COLUMNS'}
            continue
        def slots(r):
            out = [None, None]
            for c in r['numbers']:
                if not CELL(c['printed'].strip()):
                    continue
                for j, (lo, hi) in enumerate(bands):
                    if lo <= c['bbox'][2] <= hi and out[j] is None:
                        out[j] = c
            return out
        net = end = None
        lines, pending = [], ''
        for r in seq:
            l = norm(r['label'])
            cells = slots(r) if r['numbers'] else [None, None]
            if cells == [None, None]:
                pending = r['label'] if r['label'].strip() and not r['numbers'] else ''
                continue
            if not any(rx.match(l) for _, rx in RECON_RE) and pending and any(rx.match(norm(pending + r['label'])) for _, rx in RECON_RE):
                l = norm(pending + r['label'])
            pending = ''
            if l in ('净利润', '净利润亏损', '净亏损') and net is None:
                net = (cells, r)
            elif END.match(l):
                end = (cells, r)
                break
            elif net is not None:
                lines.append((l, cells, r))
        v = lambda c: num(c['printed']) * unit if c is not None else D(0)
        if not net or not end or net[0][0] is None or end[0][0] is None or v(net[0][0]) != NP or v(end[0][0]) != CFO:
            last = {'page': p, 'status': 'NOT_CONSOLIDATED_OR_INCOMPLETE'}
            continue
        residual = CFO - NP - sum((v(c[0]) for _, c, _ in lines), D(0))
        tail = residual if residual and unit > 1 and abs(residual) <= 2 * unit else D(0)  # 千元/百万元 rounding of the report
        if residual and not tail:
            return {}, {'page': p, 'status': 'NOT_CLOSED', 'residual': str(residual), 'lines': [l for l, _, _ in lines]}
        two = NPp is not None and net[0][1] is not None and end[0][1] is not None and v(net[0][1]) == NPp and v(end[0][1]) == CFOp
        if two and abs(CFOp - NPp - sum((v(c[1]) for _, c, _ in lines), D(0))) > (2 * unit if unit > 1 else 0):
            two = False
        out, used, unmapped = {}, set(), []
        for l, cells, r in lines:
            key = next((k for k, rx in RECON_RE if rx.match(l) and k not in used), None)
            if key is None:
                unmapped.append(l)
                key = 'recon_%d' % len(unmapped)
            used.add(key)
            if cells[0] is not None:
                out[key] = _fact(cells[0], unit, l, r['page'], fy, False, r['label'])
            if two and cells[1] is not None:
                out[key + '_prior'] = _fact(cells[1], unit, l, r['page'], cp, True, r['label'])
        return out, {'page': p, 'status': 'CLOSED', 'lines': len(lines), 'prior_closed': two, 'unmapped_lines': unmapped,
                     **({'rounding_tail': str(tail)} if tail else {})}
    return {}, last or {'status': 'NOT_FOUND'}


# ---------------------------------------------------------------- key figures (扣非)
def key_figures(doc, rows_on_page, squash, unit_of, facts, norm):
    """扣非归母净利润 from the key-figures table (主要会计数据).

    Columns are proven, not assumed: the 归属于上市公司股东的净利润 row must contain the statement's
    current and prior values; their column positions (e.g. YTD columns of a 9M report, 调整后 columns of a
    restated report) are then used for the 扣非 row of the same table. Units come from the row label
    （千元） or the page header."""
    if 'parent_net' not in facts:
        return {}
    PN = D(facts['parent_net']['yuan'])
    PNp = D(facts['parent_net_prior']['yuan']) if 'parent_net_prior' in facts else None
    # labels are matched loosely (tables wrap them over 3-4 lines and drop the last character); the
    # VALUES carry the proof: the 归母 row must equal the statements, the 扣非 row uses its columns
    is_pn = lambda l: '归属于' in l and '净利' in l and not re.search('扣除|每股|净资产|收益率|综合', l)
    is_adj = lambda l: '扣除非经常性损益' in l and '净利' in l and not re.search('每股|收益率|孰低', l)
    PN_RX = type('R', (), {'fullmatch': staticmethod(is_pn)})
    ADJ_RX = type('R', (), {'fullmatch': staticmethod(is_adj)})
    def clean(x):
        x = norm(re.sub(r'(不适用|增加[0-9.]+个百分点|减少[0-9.]+个百分点)', '', x))
        m = re.search(r'[（(](元|万元|千元|百万元)[)）]$', x)
        return re.sub(r'[（(](元|万元|千元|百万元)[)）]$', '', x), (dict(UNIT_NAMES)[m.group(1)] if m else None)
    carried, last_p = None, -9
    for p in range(1, min(len(doc), 40) + 1):
        text = squash(doc[p - 1].get_text())
        if '扣除非经常性损益' not in text and '净利润' not in text:
            continue
        raw = rows_on_page(doc[p - 1])
        page_unit = unit_of(text, strict=True)
        def cands(i):
            own = raw[i]['label']
            above = [raw[j]['label'] for j in (i - 2, i - 1) if j >= 0 and not raw[j]['numbers'] and raw[i]['y'] - raw[j]['y'] <= 16 * (i - j)]
            below = raw[i + 1]['label'] if i + 1 < len(raw) and not raw[i + 1]['numbers'] and raw[i + 1]['y'] - raw[i]['y'] <= 16 else ''
            ups = [''] + ([above[-1]] if above else []) + ([''.join(above)] if len(above) == 2 else [])
            return [clean(u + own + b) for u in ups for b in ('', below)]
        pn = carried if p == last_p + 1 else None  # the table may continue on the next page
        for i, r in enumerate(raw):
            amts = [c for c in r['numbers'] if AMT.match(c['printed'].strip())]
            if len(amts) < 2:
                continue
            labs = cands(i)
            unit = next((u for _, u in labs if u), page_unit)
            vals = [num(c['printed']) * unit for c in amts]
            if pn is None and any(PN_RX.fullmatch(l) for l, _ in labs):
                if PN in vals:
                    ci = vals.index(PN)
                    pj = next((j for j in range(ci + 1, len(vals)) if vals[j] == PNp), None) if PNp is not None else None
                    if PNp is None or pj is not None:
                        pn = (ci, pj, len(amts), unit)
                continue
            if pn and any(ADJ_RX.fullmatch(l) for l, _ in labs) and len(amts) == pn[2]:
                ci, pj, _, unit = pn
                fy, cp = facts['parent_net']['period'], facts.get('parent_net_prior', {}).get('period')
                out = {'adjusted_parent': _fact(amts[ci], unit, '扣非归母净利润', p, fy, False, r['label'])}
                if pj is not None and cp:
                    out['adjusted_parent_prior'] = _fact(amts[pj], unit, '扣非归母净利润', p, cp, True, r['label'])
                return out
        carried, last_p = pn, p
    return {}


UNIT_NAMES = [('百万元', D(1000000)), ('千元', D(1000)), ('万元', D(10000)), ('元', D(1))]


def bank_average_balances(doc, rows_on_page, squash, facts):
    """Recover matched group average balances from a two-period interest analysis table.

    Both period headers, the six column roles, currency unit, table perimeter
    and both interest amounts must be identified. Ambiguous layouts need review.
    """
    results = {}
    specs = (
        ('fin_interest_income', '平均生息资产', 'average_earning_assets', '生息资产', '利息收入', '收益率'),
        ('fin_interest_expense', '平均计息负债', 'average_interest_bearing_liabilities', '计息负债', '利息支出', '成本率'),
    )
    for flow, label, key, group, interest, rate in specs:
        if flow not in facts or flow + '_prior' not in facts:
            continue
        now, old = facts[flow], facts[flow + '_prior']
        months = {'Q1': 3, 'H1': 6, '9M': 9, 'FY': 12}
        period = now['period']
        end = months.get(period[4:])
        if not end or old['period'] != str(int(period[:4]) - 1) + period[4:]:
            continue
        periods = ''.join(f"{f['period'][:4]}年1-{end}月" for f in (now, old))
        headers = ('平均余额' + interest + rate + '%') * 2
        matches = []
        for page_no, page in enumerate(doc, 1):
            text = squash(page.get_text())
            if '平均余额' not in text or group not in text or interest not in text:
                continue
            rows = rows_on_page(page)
            for i, r in enumerate(rows):
                title = squash(r['label'])
                unit = re.fullmatch(r'[（(]人民币(元|千元|万元|百万元)[，,]百分比除外[）)]' + headers, title)
                if (not unit or not any(squash(x['label']) == '本集团' + periods for x in rows[max(0,i-3):i])
                        or i + 1 >= len(rows) or squash(rows[i+1]['label']) != group):
                    continue
                scale = {'元': 1, '千元': 1000, '万元': 10000, '百万元': 1000000}[unit[1]]
                # Stop at the first non-detail row. Never borrow a total from
                # the following table if this table spans another page.
                for row in rows[i+2:]:
                    cells = row['numbers']
                    if len(cells) != 6:
                        break
                    if squash(row['label']) != '合计':
                        continue
                    if all(num(cells[j]['printed']) * scale == D(f['yuan'])
                           for j, f in ((1, now), (4, old))):
                        pair = {}
                        for j, f, suffix in ((0, now, ''), (3, old, '_prior')):
                            value = _fact(cells[j], scale, label, page_no, f['period'], bool(suffix), '合计')
                            value['denominator_definition'] = '合并利率分析表内的当期平均余额'
                            if num(cells[j]['printed']) > 0 and rereads(doc, value):
                                pair[key + suffix] = value
                        if len(pair) == 2:
                            matches.append(pair)
                    break
        if len(matches) == 1:
            results.update(matches[0])
    return results


# ---------------------------------------------------------------- one call for intake
PREFER = ('product', 'industry', 'region', 'channel', 'unlabelled')
AXIS = {'product': 'disclosed_product_axis', 'industry': 'disclosed_industry_axis', 'region': 'disclosed_region_axis',
        'channel': 'disclosed_channel_axis', 'unlabelled': 'disclosed_revenue_axis'}


def extract_notes(doc, rows_on_page, squash, unit_of, norm, facts):
    """All note facts plus, when a dimension is complete with costs, the income partition used by
    the revenue → gross-profit Sankey. Returns (facts, segments, income_partition, report)."""
    seg, summary, rejected = extract_segments(doc, rows_on_page, squash, unit_of, facts)
    rec, rec_status = reconciliation(doc, rows_on_page, squash, unit_of, facts, norm)
    kf = key_figures(doc, rows_on_page, squash, unit_of, facts, norm)
    out = {**seg, **rec, **kf}
    # every note fact must re-read from its PDF cell (same rule as the publication validator); a table
    # whose cells do not re-read (interleaved or wrapped layouts) is dropped as a whole, never patched
    bad = {k for k, f in out.items() if f.get('classification') == 'DISCLOSED' and not rereads(doc, f)}
    if bad:
        groups = {re.sub(r'_(rev|cost)(_prior)?$', '', k) if re.match(r'(seg|ind|region|channel|part)[0-9]', k) else k for k in bad}
        prefixes = {re.match(r'[a-z]+', g).group(0) for g in groups if re.match(r'(seg|ind|region|channel|part)[0-9]', g)}
        out = {k: v for k, v in out.items() if k not in bad and not any(re.match(p + r'[0-9]+_', k) for p in prefixes)
               and not (k.startswith('adjusted_parent') and any(b.startswith('adjusted_parent') for b in bad))}
        summary = [x for x in summary if not any(e['key'].startswith(tuple(prefixes)) for e in x['entries'])]
    # Preserve the exact current-column membership, including unmapped but
    # disclosed rows. A rounding tail or a dropped cell cannot license a bridge.
    if rec_status and rec_status['status'] == 'CLOSED' and not rec_status.get('rounding_tail') and not (rec.keys() & bad):
        rec_status['current_keys'] = [k for k in rec if not k.endswith('_prior')]
    dropped = sorted(bad)
    segments, partition = [], None
    for s in sorted(summary, key=lambda x: PREFER.index(x['dimension'])):
        if s['with_cost'] != s['rows']:
            continue
        rows = [{'label': e['label'], 'rev': e['key'] + '_rev', 'cost': e['key'] + '_cost', 'dimension': AXIS[s['dimension']]} for e in s['entries']]
        if s['scope'] == 'main_rev':
            if 'other_business_cost' not in out and 'other_business_rev' in out and 'main_cost' in out and 'cogs' in facts:
                # 其他业务成本 not printed: 营业成本 − 主营业务成本, two disclosed cells of one period (a lawful DERIVED fact)
                v = D(facts['cogs']['yuan']) - D(out['main_cost']['yuan'])
                if v >= 0:
                    out['other_business_cost'] = {'yuan': str(v), 'label': '其他业务成本（营业成本减主营业务成本）', 'page': out['main_cost']['page'], 'type': 'flow',
                                         'period': facts['cogs']['period'], 'scope': 'consolidated', 'classification': 'DERIVED', 'unit': '元', 'currency': 'CNY',
                                         'derivation': {'operation': 'subtract', 'terms': ['cogs', 'main_cost']}, 'extraction': 'NOTES_EXTRACT_V1'}
            if not ('other_business_rev' in out and 'other_business_cost' in out):
                continue
            rows.append({'label': '其他业务', 'rev': 'other_business_rev', 'cost': 'other_business_cost', 'dimension': AXIS[s['dimension']]})
        # a business with negative gross profit cannot be a positive flow (Skill TYPE C): use the next dimension
        if any(r['rev'] not in out or r['cost'] not in out for r in rows):
            continue
        if any(D(out[r['rev']]['yuan']) <= 0 or D(out[r['rev']]['yuan']) < D(out[r['cost']]['yuan']) for r in rows):
            s['skipped'] = 'NEGATIVE_GROSS_ROW'
            continue
        # the partition must close on revenue AND cost against the statements
        rv = sum((D(out[r['rev']]['yuan']) for r in rows), D(0))
        cv = sum((D(out[r['cost']]['yuan']) for r in rows), D(0))
        if 'rev' in facts and 'cogs' in facts and rv == D(facts['rev']['yuan']) and cv == D(facts['cogs']['yuan']):
            segments = rows
            partition = {'axis': AXIS[s['dimension']], 'period': facts['rev']['period'], 'scope': 'consolidated',
                         'completeness': 'SOURCE_EXHAUSTIVE_MUTUALLY_EXCLUSIVE', 'proof': 'NOTES_EXTRACT_V1: revenue and cost rows add up to 营业收入 and 营业成本'}
            break
    report = {'dimensions': [{k: v for k, v in s.items() if k != 'entries'} | {'labels': [e['label'] for e in s['entries']]} for s in summary],
              'unproven_segment_tables': [f'p{p} {k}' for p, k in rejected][:12],
              'cash_reconciliation': rec_status, 'adjusted_parent': 'adjusted_parent' in kf,
              'income_partition': partition['axis'] if partition else None, 'dropped_unreadable_cells': dropped[:12]}
    return out, segments, partition, report


def rereads(doc, f):
    import pymupdf
    c = f['source_cells'][0]
    region = doc[f['page'] - 1].get_textbox(pymupdf.Rect(c['bbox']) + (-.5, -.5, .5, .5)).replace(',', '')
    p = c['printed'].strip().replace(',', '')
    try:
        shown = num(c['printed'])
    except NotANumber:
        return False
    return p.strip('()（）') in region and shown * D(c.get('unit_scale', '1')) == D(f['yuan'])
