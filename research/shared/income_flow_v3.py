"""INCOME_FLOW_V3: an original income-statement flow in the App Economy Insights grammar.

Reading order (left to right): revenue sources -> revenue -> gross profit (rises) and cost of
revenue (falls) -> operating profit (rises) and operating costs (falls) -> net profit to parent.
Operating costs and final-stage deductions split into named leaves (R&D, selling, tax ...), each
annotated with its share of revenue. Profit nodes carry margin, margin change (pp) and growth.

Accounting rules are unchanged from the full profit chain: every number is an original disclosed
source cell or an explicit signed sum of them; gains enter as inflows, costs leave as outflows; no
balancing node; zero is zero. This module only *draws*; ``income_flow_audit.py`` independently
re-derives every node, ribbon width and printed annotation without importing this file.
"""
from decimal import Decimal as D
from html import escape as H
import json

GRAMMAR_LAYOUT = 'INCOME_FLOW_V3'
# Original palette: neutral revenue, green profit, red cost, ochre gains. Bars solid, ribbons light.
COL = {
    'source': ('#5B6470', '#CDD2D8'), 'revenue': ('#3F4650', '#CDD2D8'),
    'profit': ('#16824A', '#A6D9B8'), 'cost': ('#C2362E', '#F0AAA4'), 'gain': ('#B07D12', '#EDD394'),
}
INK = '#1D2B33'
MUTED = '#5E6B73'
RATE = {'gross': '毛利率', 'operating': '营业利润率', 'parent': '归母净利率'}
SMALL_LEAF_SHARE = D('0.01')
SOURCE_SHADES = ('#3F4650', '#6B7480', '#959DA7', '#B9BFC6', '#525A64', '#838B95')


def amount(bundle, terms):
    return sum((D(bundle['facts'][k]['yuan']) * D(str(c)) for k, c in terms), D(0))


def prior(bundle, terms):
    """Same terms in the comparative period, or None when any prior source cell is absent."""
    comp = bundle['comparatives']['facts']
    if any(k + '_prior' not in comp for k, _ in terms):
        return None
    return sum((D(comp[k + '_prior']['yuan']) * D(str(c)) for k, c in terms), D(0))


def q1(x):
    return D(x).quantize(D('0.1'), rounding='ROUND_HALF_UP')


def yi(v):
    v = D(v)
    if abs(v) >= D(100000000):
        return f'{v / D(100000000):,.2f}亿'
    if abs(v) >= D(10000):
        return f'{v / D(10000):,.2f}万'
    return f'{v:,.2f}元'


def split(bundle, groups):
    """Split every source term by its real sign: (gains, costs) lists of (label, terms, value)."""
    gains, costs = [], []
    for g in groups:
        if g.get('net'):  # a rounding tail is ONE signed amount; splitting its large offsetting terms would be meaningless
            v = amount(bundle, g['terms'])
            if v > 0:
                gains.append((g['label'], g['terms'], v))
            elif v < 0:
                costs.append((g['label'], [[k, -c] for k, c in g['terms']], -v))
            continue
        pos = [[k, c] for k, c in g['terms'] if amount(bundle, [[k, c]]) > 0]
        neg = [[k, -c] for k, c in g['terms'] if amount(bundle, [[k, c]]) < 0]
        if pos:
            gains.append((g['label'], pos, amount(bundle, pos)))
        if neg:
            costs.append((g['label'], neg, amount(bundle, neg)))
    return gains, costs


def plan(bundle):
    """Nodes and ribbons in exact yuan. Raises when the statement cannot be drawn honestly."""
    stages = {s['id']: s for s in bundle['stages']}
    if [s['id'] for s in bundle['stages']] != ['revenue', 'gross', 'operating', 'pretax', 'net', 'parent']:
        raise ValueError('FLOW_V3_REQUIRES_GROSS_PROFIT_STAGE')
    if not bundle.get('comparatives'):
        raise ValueError('FLOW_V3_REQUIRES_PRIOR_PERIOD_SOURCE_CELLS')
    rev = amount(bundle, stages['revenue']['terms'])
    gp = amount(bundle, stages['gross']['terms'])
    op = amount(bundle, stages['operating']['terms'])
    parent = amount(bundle, stages['parent']['terms'])
    if min(rev, gp, op, parent) <= 0:
        raise ValueError('FLOW_V3_NEGATIVE_OR_ZERO_SUBTOTAL_USE_SIGNED_BRIDGE')
    cogs = rev - gp
    op_gains, op_costs = split(bundle, stages['operating']['adjustments'])
    fin_groups = stages['pretax']['adjustments'] + stages['net']['adjustments'] + stages['parent']['adjustments']
    fin_gains, fin_costs = split(bundle, fin_groups)
    g_op = sum((v for _, _, v in op_gains), D(0))
    c_op = sum((v for _, _, v in op_costs), D(0))
    g_fin = sum((v for _, _, v in fin_gains), D(0))
    c_fin = sum((v for _, _, v in fin_costs), D(0))
    if gp + g_op - c_op != op or op + g_fin - c_fin != parent:
        raise ValueError('FLOW_V3_STAGE_NOT_CLOSED')
    if op - g_op < 0 or parent - g_fin < 0:
        raise ValueError('FLOW_V3_GAINS_EXCEED_CARRIED_PROFIT_USE_SIGNED_BRIDGE')

    nodes, edges = {}, []

    def node(i, label, terms, role, value):
        if value < 0:
            raise ValueError('FLOW_V3_NEGATIVE_NODE ' + i)
        nodes[i] = {'id': i, 'label': label, 'terms': terms, 'role': role, 'value': value}
        return nodes[i]

    def edge(a, b, v):
        if v < 0:
            raise ValueError('FLOW_V3_NEGATIVE_RIBBON')
        if v:
            edges.append({'source': a, 'target': b, 'value': v})

    sources = bundle['sources']
    if len(sources) > 1:
        for i, s in enumerate(sources):
            node('source-' + str(i), s['label'], s['terms'], 'source', amount(bundle, s['terms']))
            edge('source-' + str(i), 'revenue', amount(bundle, s['terms']))
        if sum((nodes['source-' + str(i)]['value'] for i in range(len(sources))), D(0)) != rev:
            raise ValueError('FLOW_V3_REVENUE_PARTITION')
    node('revenue', '营业收入', stages['revenue']['terms'], 'revenue', rev)
    node('gross', '营业毛利', stages['gross']['terms'], 'profit', gp)
    cogs_terms = [t for g in stages['gross']['adjustments'] for t in [[k, -c] for k, c in g['terms']]]
    node('cogs', '营业成本', cogs_terms, 'cost', cogs)
    if amount(bundle, cogs_terms) != cogs:
        raise ValueError('FLOW_V3_COGS_TERMS')
    edge('revenue', 'gross', gp)
    edge('revenue', 'cogs', cogs)
    cost_sources = bundle.get('cost_sources') or []
    if cost_sources:
        if sum((amount(bundle, c['terms']) for c in cost_sources), D(0)) != cogs:
            raise ValueError('FLOW_V3_COST_PARTITION')
        for i, c in enumerate(cost_sources):
            node('cogs-' + str(i), c['label'], c['terms'], 'cost-leaf', amount(bundle, c['terms']))
            edge('cogs', 'cogs-' + str(i), nodes['cogs-' + str(i)]['value'])
    node('operating', '营业利润', stages['operating']['terms'], 'profit', op)
    edge('gross', 'operating', op - g_op)
    if c_op:
        node('opex', '期间费用及损失', [t for _, ts, _ in op_costs for t in ts], 'cost', c_op)
        edge('gross', 'opex', c_op)
        big = [x for x in op_costs if x[2] >= rev * SMALL_LEAF_SHARE]
        small = [x for x in op_costs if x[2] < rev * SMALL_LEAF_SHARE]
        if len(small) == 1:
            big, small = big + small, []
        big.sort(key=lambda x: -x[2])
        for j, (label, terms, v) in enumerate(big):
            node('opex-' + str(j), label, terms, 'cost-leaf', v)
            edge('opex', 'opex-' + str(j), v)
        if small:
            terms = [t for _, ts, _ in small for t in ts]
            node('opex-other', f'其他费用及损失（{len(small)}项）', terms, 'cost-leaf', sum((v for *_, v in small), D(0)))
            edge('opex', 'opex-other', nodes['opex-other']['value'])
    if g_op:
        node('gain-op', '其他收益等', [t for _, ts, _ in op_gains for t in ts], 'gain', g_op)
        edge('gain-op', 'operating', g_op)
    node('parent', '归母净利润', stages['parent']['terms'], 'profit', parent)
    edge('operating', 'parent', parent - g_fin)
    for j, (label, terms, v) in enumerate(fin_costs):
        node('final-' + str(j), label, terms, 'cost-leaf', v)
        edge('operating', 'final-' + str(j), v)
    if g_fin:
        node('gain-final', '营业外及归属调整', [t for _, ts, _ in fin_gains for t in ts], 'gain', g_fin)
        edge('gain-final', 'parent', g_fin)
    for n in nodes.values():
        inflow = sum((e['value'] for e in edges if e['target'] == n['id']), D(0))
        outflow = sum((e['value'] for e in edges if e['source'] == n['id']), D(0))
        has_in = any(e['target'] == n['id'] for e in edges)
        has_out = any(e['source'] == n['id'] for e in edges)
        if has_in and inflow != n['value'] and n['role'] not in ('source', 'gain'):
            raise ValueError('FLOW_V3_NODE_INFLOW_NOT_CONSERVED ' + n['id'])
        if has_out and outflow != n['value'] and n['id'] != 'parent':
            raise ValueError('FLOW_V3_NODE_OUTFLOW_NOT_CONSERVED ' + n['id'])
        if n['id'] in ('gross', 'operating', 'opex') and (not has_out or outflow != n['value']):
            raise ValueError('FLOW_V3_NODE_NOT_CONSERVED ' + n['id'])
    return {'nodes': nodes, 'edges': edges, 'revenue': rev}


def annotations(bundle, nodes):
    """Printed reading aids per node; the audit recomputes the same strings from source cells."""
    rev = nodes['revenue']['value']
    prev = prior(bundle, nodes['revenue']['terms'])
    out = {}
    for n in nodes.values():
        lines = []
        p = prior(bundle, n['terms'])
        if p is None:
            if n['role'] in ('cost', 'cost-leaf') and n['value'] / rev * 100 >= D('0.05'):
                lines.append(f"占营收 {q1(n['value'] / rev * 100)}%")
            out[n['id']] = {'lines': lines, 'prior': None}
            continue
        if n['id'] in RATE:
            m = n['value'] / rev * 100
            lines.append(f"{RATE[n['id']]} {q1(m)}%（{q1(m - p / prev * 100):+}pp）")
        if n['role'] in ('revenue', 'profit') and p > 0:
            lines.append(f"同比 {q1((n['value'] / p - 1) * 100):+}%")
        if n['role'] in ('cost', 'cost-leaf') and n['value'] / rev * 100 < D('0.05'):
            out[n['id']] = {'lines': [], 'prior': p}
            continue
        if n['role'] in ('cost', 'cost-leaf'):
            share = n['value'] / rev * 100
            text = f'占营收 {q1(share)}%'
            if p >= 0 and prev > 0:
                text += f'（{q1(share - p / prev * 100):+}pp）'
            lines.append(text)
        if n['role'] == 'source' and p > 0:
            lines.append(f"同比 {q1((n['value'] / p - 1) * 100):+}%")
        out[n['id']] = {'lines': lines, 'prior': p}
    return out


def layout(p):
    nodes, edges = p['nodes'], p['edges']
    rev = p['revenue']
    scale = rev / D(300)
    has_src = any(n['role'] == 'source' for n in nodes.values())
    X = ({'source': 160, 'revenue': 326, 'gross': 506, 'operating': 686, 'final': 864} if has_src else
         {'revenue': 150, 'gross': 370, 'operating': 590, 'final': 860})
    h = lambda n: n['value'] / scale

    def put(i, x, y):
        n = nodes[i]
        n.update(x=D(x), y=D(y), w=D(12), h=h(n))

    put('revenue', X['revenue'], 230)
    R = nodes['revenue']
    put('gross', X['gross'], R['y'] - 52)
    G = nodes['gross']
    put('cogs', X['gross'], G['y'] + G['h'] + 96)
    put('operating', X['operating'], G['y'] - 40)
    O = nodes['operating']
    if 'opex' in nodes:
        put('opex', X['operating'], O['y'] + O['h'] + 92)
    put('parent', X['final'], O['y'] - 32)
    P = nodes['parent']
    if has_src:
        y = D(150)
        srcs = [n for n in nodes.values() if n['role'] == 'source']
        span = sum((h(n) for n in srcs), D(0)) + D(60) * (len(srcs) - 1)
        y = R['y'] + R['h'] / 2 - span / 2
        for n in srcs:
            put(n['id'], X['source'], y)
            y += h(n) + 60
    if 'gain-op' in nodes:
        put('gain-op', X['gross'] + 108, G['y'] + G['h'] + 22)
    # final-stage deductions (tax, non-operating, minority) under the parent node
    y = P['y'] + P['h'] + 70
    for i in sorted((k for k in nodes if k.startswith('final-')), key=lambda k: int(k.split('-')[1])):
        put(i, X['final'], y)
        y = nodes[i]['y'] + nodes[i]['h'] + 54
    if 'gain-final' in nodes:
        put('gain-final', X['operating'] + 104, O['y'] + O['h'] + 26)
    # operating-cost leaves below the final-stage deductions, aligned with the opex node
    leaves = [k for k in nodes if k.startswith('opex-')]
    if leaves:
        y = max(y + 16, nodes['opex']['y'])
        for i in leaves:
            put(i, X['final'], y)
            y = nodes[i]['y'] + nodes[i]['h'] + 54
    cy = nodes['cogs']['y']
    if 'opex' in nodes:
        cy = max(cy, nodes['opex']['y'] + nodes['opex']['h'] + 92)
    for i in sorted((k for k in nodes if k.startswith('cogs-')), key=lambda k: int(k.split('-')[1])):
        put(i, X['operating'], cy)
        cy = nodes[i]['y'] + nodes[i]['h'] + 54
    bottom = max(n['y'] + n['h'] for n in nodes.values())
    return scale, int(bottom + 110)


LEAF_PREFIXES = ('opex-', 'cogs-')


def is_leaf_detail(node_id):
    """Cost breakdown leaves. The phone edition lists them as rows instead of ribbons."""
    return node_id.startswith(LEAF_PREFIXES)


def render_phone(bundle):
    """Native 330-wide edition: the same flow top-to-bottom, profit on the left, costs peel right."""
    p = plan(bundle)
    nodes = {k: v for k, v in p['nodes'].items() if not is_leaf_detail(k)}
    edges = [e for e in p['edges'] if not is_leaf_detail(e['target'])]
    leaves = [v for k, v in p['nodes'].items() if is_leaf_detail(k)]
    notes = annotations(bundle, p['nodes'])
    rev = p['revenue']
    left, span = D(16), D(298)
    scale = rev / span
    w = lambda n: n['value'] / scale
    f = lambda x: format(D(str(x)).quantize(D('.000001')), 'f')
    out = []

    def text(x, y, t, size, anchor='start', color=INK, weight=600):
        out.append(f'<text x="{f(x)}" y="{f(y)}" fill="{color}" font-size="{size}" style="font-size:{size}px" '
                   f'font-family="Noto Sans CJK SC,PingFang SC,Arial,sans-serif" text-anchor="{anchor}" '
                   f'font-weight="{weight}" stroke="#FFFFFF" stroke-width="3" paint-order="stroke" stroke-linejoin="round">{H(t)}</text>')

    def put(i, x, y):
        nodes[i].update(x=D(x), y=D(y), w=w(nodes[i]), h=D(10))

    srcs = [n for n in nodes.values() if n['role'] == 'source']
    y = D(44) + 16 * len(srcs) if srcs else D(12)
    if srcs:
        x = left
        for n in srcs:
            n.update(x=x, y=y, w=w(n), h=D(10))
            x += w(n)
        y += 120
    rows = [('revenue', []), ('gross', ['cogs']), ('operating', ['opex'] if 'opex' in nodes else []),
            ('parent', sorted((k for k in nodes if k.startswith('final-')), key=lambda k: int(k.split('-')[1])))]
    tops = {}
    for main, costs in rows:
        y += 84 if main != 'revenue' else 0
        lines = notes[main]['lines']
        tops[main] = y
        y += 30 + 17 * len(lines)
        put(main, left, y)
        x = left + w(nodes[main]) + 10
        for c in costs:
            put(c, x, y)
            x += w(nodes[c]) + 8
        y += 10
        if main == 'gross' and 'gain-op' in nodes:
            put('gain-op', left + span - w(nodes['gain-op']), y + 58)
        if main == 'operating' and 'gain-final' in nodes:
            put('gain-final', left + span - w(nodes['gain-final']), y + 58 + 32 * max(0, len(costs) - 1))
    so = {i: D(0) for i in nodes}
    ti = {i: D(0) for i in nodes}
    for e in edges:
        a, b, v = nodes[e['source']], nodes[e['target']], e['value']
        th = v / scale
        tha = th
        x1 = a['x'] + so[a['id']]
        x2 = b['x'] + ti[b['id']]
        so[a['id']] += tha
        ti[b['id']] += th
        y1, y2 = a['y'] + a['h'], b['y']
        m = (y1 + y2) / 2
        key = 'cost' if b['role'] in ('cost', 'cost-leaf') else 'gain' if a['role'] == 'gain' else 'source' if b['role'] == 'revenue' else 'profit'
        d = (f'M{f(x1)},{f(y1)} C{f(x1)},{f(m)} {f(x2)},{f(m)} {f(x2)},{f(y2)} '
             f'L{f(x2 + th)},{f(y2)} C{f(x2 + th)},{f(m)} {f(x1 + tha)},{f(m)} {f(x1 + tha)},{f(y1)} Z')
        out.append(f'<path d="{d}" fill="{COL[key][1]}" fill-opacity=".6" data-chain-source="{a["id"]}" '
                   f'data-chain-target="{b["id"]}" data-chain-yuan="{v}"><title>{H(a["label"])} → {H(b["label"])}：{v}元</title></path>')
    for n in nodes.values():
        key = {'source': 'source', 'revenue': 'revenue', 'profit': 'profit', 'cost': 'cost', 'cost-leaf': 'cost', 'gain': 'gain'}[n['role']]
        out.append(f'<rect x="{f(n["x"])}" y="{f(n["y"])}" width="{f(n["w"])}" height="{f(n["h"])}" fill="{SOURCE_SHADES[srcs.index(n) % 6] if n in srcs else COL[key][0]}" '
                   f'data-chain-node="{n["id"]}" data-chain-role="{n["role"]}" data-chain-node-yuan="{n["value"]}" '+
                   (f'data-chain-prior-yuan="{notes[n["id"]]["prior"]}" ' if notes[n["id"]]["prior"] is not None else '')+
                   f'data-chain-terms="{H(json.dumps(n["terms"], ensure_ascii=False, separators=(",", ":")), quote=True)}">'
                   f'<title>{H(n["label"])}：{n["value"]}元</title></rect>')
    for k, n in enumerate(srcs):
        # one legend row per source keeps long Chinese names readable on a phone
        out.append(f'<rect x="{f(left)}" y="{f(D(24) + 16 * k - 8)}" width="8" height="8" fill="{SOURCE_SHADES[k % 6]}"/>')
        text(left + 12, D(24) + 16 * k, n['label'] + '　' + yi(n['value']) + ('　' + notes[n['id']]['lines'][0] if notes[n['id']]['lines'] else ''), 11, 'start', INK, 600)
    for main, costs in rows:
        n = nodes[main]
        color = COL['profit'][0] if n['role'] == 'profit' else INK
        top = tops[main]
        text(left, top + 14, n['label'] + '　' + yi(n['value']), 15, 'start', color, 700)
        for k, line in enumerate(notes[main]['lines']):
            text(left, top + 32 + 17 * k, line, 12, 'start', MUTED, 500)
        for j, c in enumerate(costs):
            cn = nodes[c]
            # under the bar, right-aligned: that strip carries no ribbon on the phone edition
            base = n['y'] + n['h'] + 16 + 32 * j
            text(left + span, base, '减：' + cn['label'] + '　' + yi(cn['value']), 11, 'end', COL['cost'][0], 700)
            if notes[c]['lines']:
                text(left + span, base + 15, notes[c]['lines'][0], 10, 'end', MUTED, 500)
    for g in ('gain-op', 'gain-final'):
        if g in nodes:
            n = nodes[g]
            text(left + span, n['y'] + 24, '加：' + n['label'] + '　' + yi(n['value']), 11, 'end', COL['gain'][0], 700)
    finals = [k for k in nodes if k.startswith('final-')]
    y = max(n['y'] + n['h'] for n in nodes.values()) + 46 + 32 * len(finals)
    if leaves:
        text(left, y, '费用与成本构成', 13, 'start', INK, 700)
        y += 14
        top_leaf = max(l['value'] for l in leaves)
        for l in leaves:
            y += 30
            bw = l['value'] / top_leaf * D(130)
            out.append(f'<rect x="{f(left)}" y="{f(y - 9)}" width="{f(bw)}" height="8" fill="{COL["cost"][1]}" '
                       f'data-chain-leaf="{l["id"]}" data-chain-leaf-yuan="{l["value"]}" data-chain-leaf-scale="{top_leaf / D(130)}"/>')
            text(left + D(138), y - 2, l['label'], 11, 'start', COL['cost'][0], 700)
            text(left + D(138), y + 12, yi(l['value']) + ('　' + notes[l['id']]['lines'][0] if notes[l['id']]['lines'] else ''), 10, 'start', MUTED, 500)
            y += 8
    height = int(y + 46)
    text(left, height - 16, '宽度按人民币原始元同一比例；会计形成关系，非现金流。', 10, 'start', MUTED, 500)
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 {height}" role="img" aria-label="利润表流向图" '
            f'data-chart-grammar="FULL_PROFIT_CHAIN_V1" data-chain-layout="{GRAMMAR_LAYOUT}" data-design-system="FINANCIALS_UNIFIED_STORY_V1" '
            f'data-issuer="{bundle["issuer"]}" data-period="{bundle["period"]}" '
            f'data-original-pdf-sha256="{bundle["source_pdf"]["source_sha256"]}" data-chain-axis="width" data-chain-scale="{scale}">'
            f'<title>利润表流向：收入、成本、利润与股东归属</title>')
    return head + ''.join(out) + '</svg>'


def render(bundle, mobile=False):
    if mobile:
        return render_phone(bundle)
    p = plan(bundle)
    nodes, edges = p['nodes'], p['edges']
    notes = annotations(bundle, nodes)
    scale, height = layout(p)
    rev = next(n['value'] for n in nodes.values() if n['role'] == 'revenue')
    f = lambda x: format(D(str(x)).quantize(D('.000001')), 'f')
    out = []

    def text(x, y, t, size, anchor='middle', color=INK, weight=600):
        out.append(f'<text x="{f(x)}" y="{f(y)}" fill="{color}" font-size="{size}" style="font-size:{size}px" '
                   f'font-family="Noto Sans CJK SC,PingFang SC,Arial,sans-serif" text-anchor="{anchor}" '
                   f'font-weight="{weight}" stroke="#FFFFFF" stroke-width="3" paint-order="stroke" stroke-linejoin="round">{H(t)}</text>')

    so = {i: D(0) for i in nodes}
    ti = {i: D(0) for i in nodes}
    # draw ribbons first; ports stack in edge order (profit first, then costs) on each side
    for e in edges:
        a, b, v = nodes[e['source']], nodes[e['target']], e['value']
        th = v / scale
        y1 = a['y'] + so[a['id']]
        y2 = b['y'] + ti[b['id']]
        so[a['id']] += th
        ti[b['id']] += th
        x1, x2 = a['x'] + a['w'], b['x']
        m = (x1 + x2) / 2
        role = b['role'] if b['role'] in ('cost', 'cost-leaf') else a['role']
        key = 'cost' if role in ('cost', 'cost-leaf') else 'gain' if a['role'] == 'gain' else 'source' if a['role'] in ('source', 'revenue') and b['role'] == 'revenue' else 'profit'
        fill = COL[key][1]
        d = (f'M{f(x1)},{f(y1)} C{f(m)},{f(y1)} {f(m)},{f(y2)} {f(x2)},{f(y2)} '
             f'L{f(x2)},{f(y2 + th)} C{f(m)},{f(y2 + th)} {f(m)},{f(y1 + th)} {f(x1)},{f(y1 + th)} Z')
        out.append(f'<path d="{d}" fill="{fill}" fill-opacity=".9" data-chain-source="{a["id"]}" '
                   f'data-chain-target="{b["id"]}" data-chain-yuan="{v}"><title>{H(a["label"])} → {H(b["label"])}：{v}元</title></path>')
    for n in nodes.values():
        key = {'source': 'source', 'revenue': 'revenue', 'profit': 'profit', 'cost': 'cost', 'cost-leaf': 'cost', 'gain': 'gain'}[n['role']]
        out.append(f'<rect x="{f(n["x"])}" y="{f(n["y"])}" width="{f(n["w"])}" height="{f(n["h"])}" fill="{COL[key][0]}" '
                   f'data-chain-node="{n["id"]}" data-chain-role="{n["role"]}" data-chain-node-yuan="{n["value"]}" '+
                   (f'data-chain-prior-yuan="{notes[n["id"]]["prior"]}" ' if notes[n["id"]]["prior"] is not None else '')+
                   f'data-chain-terms="{H(json.dumps(n["terms"], ensure_ascii=False, separators=(",", ":")), quote=True)}">'
                   f'<title>{H(n["label"])}：{n["value"]}元</title></rect>')
    # labels
    for n in nodes.values():
        lines = notes[n['id']]['lines']
        cx = n['x'] + n['w'] / 2
        if n['role'] in ('revenue', 'profit'):
            color = COL['profit'][0] if n['role'] == 'profit' else INK
            top = n['y'] - 22 - 17 * len(lines) - 22
            text(cx, top, n['label'], 15, color=color, weight=700)
            text(cx, top + 22, yi(n['value']), 17, color=color, weight=700)
            for k, line in enumerate(lines):
                text(cx, top + 42 + 17 * k, line, 12, color=MUTED, weight=500)
        elif n['role'] == 'cost':
            y = n['y'] + n['h'] + 22
            text(cx, y, n['label'], 14, color=COL['cost'][0], weight=700)
            text(cx, y + 20, '（' + yi(n['value']) + '）', 14, color=COL['cost'][0], weight=700)
            for k, line in enumerate(lines):
                text(cx, y + 38 + 16 * k, line, 12, color=MUTED, weight=500)
        elif n['role'] == 'cost-leaf':
            x = n['x'] + n['w'] + 10
            y = n['y'] + min(n['h'], D(12)) / 2 + 2
            faint = n['value'] / rev < D('0.001')  # no visible bar: keep the line, mute the colour
            text(x, y - 6, n['label'], 12 if faint else 13, 'start', MUTED if faint else COL['cost'][0], 600 if faint else 700)
            text(x, y + 11, '（' + yi(n['value']) + '）' + ('　' + lines[0] if lines else ''), 11, 'start', MUTED, 500)
        elif n['role'] == 'source':
            x = n['x'] - 12
            y = n['y'] + n['h'] / 2
            text(x, y - 8, n['label'], 13, 'end', INK, 700)
            text(x, y + 9, yi(n['value']) + ('　' + lines[0] if lines else ''), 12, 'end', MUTED, 500)
        elif n['role'] == 'gain':
            x = n['x'] - 8
            text(x, n['y'] + n['h'] + 16, '加：' + n['label'], 12, 'end', COL['gain'][0], 700)
            text(x, n['y'] + n['h'] + 32, yi(n['value']), 12, 'end', COL['gain'][0], 700)
    text(24, height - 26, '图形宽度按人民币原始元同一比例；会计形成关系，不是现金流。完整科目与来源见下方核对表。', 12, 'start', MUTED, 500)
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 {height}" role="img" aria-label="利润表流向图" '
            f'data-chart-grammar="FULL_PROFIT_CHAIN_V1" data-chain-layout="{GRAMMAR_LAYOUT}" data-design-system="FINANCIALS_UNIFIED_STORY_V1" '
            f'data-issuer="{bundle["issuer"]}" data-period="{bundle["period"]}" '
            f'data-original-pdf-sha256="{bundle["source_pdf"]["source_sha256"]}" data-chain-axis="height" data-chain-scale="{scale}">'
            f'<title>利润表流向：收入、成本、利润与股东归属</title>')
    return head + ''.join(out) + '</svg>'
