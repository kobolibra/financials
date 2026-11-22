"""Independent acceptance for INCOME_FLOW_V3 vectors. Never imports the renderer.

From the editorial manifest's source facts it re-derives which nodes must exist, their exact yuan,
every ribbon amount, the common money scale, and every printed margin / growth / share-of-revenue
string; then it measures the actual SVG geometry (rect sizes, path thickness, port stacking).
"""
from decimal import Decimal as D
import json
import re
import xml.etree.ElementTree as ET

NS = '{http://www.w3.org/2000/svg}'
RATE = {'gross': '毛利率', 'operating': '营业利润率', 'parent': '归母净利率'}


def _v(b, terms, prior=False):
    src = b['comparatives']['facts'] if prior else b['facts']
    total = D(0)
    for k, c in terms:
        key = k + '_prior' if prior else k
        if key not in src:
            return None
        total += D(src[key]['yuan']) * D(str(c))
    return total


def _r(x):
    return D(x).quantize(D('0.1'), rounding='ROUND_HALF_UP')


def expected(b):
    """(nodes, ribbons) as plain dicts: id -> (role, yuan, terms); (src, dst) -> yuan."""
    st = {s['id']: s for s in b['stages']}
    rev, gp = _v(b, st['revenue']['terms']), _v(b, st['gross']['terms'])
    op, parent = _v(b, st['operating']['terms']), _v(b, st['parent']['terms'])
    nodes, ribbons = {}, {}

    def signed(groups):
        plus, minus = [], []
        for g in groups:
            if g.get('net'):
                v = _v(b, g['terms'])
                if v > 0:
                    plus.append((g['label'], g['terms']))
                elif v < 0:
                    minus.append((g['label'], [[k, -c] for k, c in g['terms']]))
                continue
            p = [[k, c] for k, c in g['terms'] if _v(b, [[k, c]]) > 0]
            m = [[k, -c] for k, c in g['terms'] if _v(b, [[k, c]]) < 0]
            if p:
                plus.append((g['label'], p))
            if m:
                minus.append((g['label'], m))
        return plus, minus

    def add_ribbon(a, z, value):
        assert value >= 0, 'NEGATIVE'
        if value:
            ribbons[(a, z)] = value

    srcs = b['sources']
    if len(srcs) > 1:
        for i, s in enumerate(srcs):
            nodes['source-%d' % i] = ('source', _v(b, s['terms']), s['terms'])
            add_ribbon('source-%d' % i, 'revenue', _v(b, s['terms']))
    nodes['revenue'] = ('revenue', rev, st['revenue']['terms'])
    nodes['gross'] = ('profit', gp, st['gross']['terms'])
    cogs_terms = [[k, -c] for g in st['gross']['adjustments'] for k, c in g['terms']]
    nodes['cogs'] = ('cost', rev - gp, cogs_terms)
    add_ribbon('revenue', 'gross', gp)
    add_ribbon('revenue', 'cogs', rev - gp)
    for i, c in enumerate(b.get('cost_sources') or []):
        nodes['cogs-%d' % i] = ('cost-leaf', _v(b, c['terms']), c['terms'])
        add_ribbon('cogs', 'cogs-%d' % i, _v(b, c['terms']))
    plus, minus = signed(st['operating']['adjustments'])
    gain_op = sum((_v(b, t) for _, t in plus), D(0))
    cost_op = sum((_v(b, t) for _, t in minus), D(0))
    nodes['operating'] = ('profit', op, st['operating']['terms'])
    add_ribbon('gross', 'operating', op - gain_op)
    if cost_op:
        nodes['opex'] = ('cost', cost_op, [t for _, ts in minus for t in ts])
        add_ribbon('gross', 'opex', cost_op)
        threshold = rev / 100
        big = [x for x in minus if _v(b, x[1]) >= threshold]
        small = [x for x in minus if _v(b, x[1]) < threshold]
        if len(small) == 1:
            big, small = big + small, []
        big.sort(key=lambda x: -_v(b, x[1]))
        for j, (label, ts) in enumerate(big):
            nodes['opex-%d' % j] = ('cost-leaf', _v(b, ts), ts)
            add_ribbon('opex', 'opex-%d' % j, _v(b, ts))
        if small:
            ts = [t for _, x in small for t in x]
            nodes['opex-other'] = ('cost-leaf', _v(b, ts), ts)
            add_ribbon('opex', 'opex-other', _v(b, ts))
    if gain_op:
        nodes['gain-op'] = ('gain', gain_op, [t for _, ts in plus for t in ts])
        add_ribbon('gain-op', 'operating', gain_op)
    fp, fm = signed(st['pretax']['adjustments'] + st['net']['adjustments'] + st['parent']['adjustments'])
    gain_f = sum((_v(b, t) for _, t in fp), D(0))
    nodes['parent'] = ('profit', parent, st['parent']['terms'])
    add_ribbon('operating', 'parent', parent - gain_f)
    for j, (label, ts) in enumerate(fm):
        nodes['final-%d' % j] = ('cost-leaf', _v(b, ts), ts)
        add_ribbon('operating', 'final-%d' % j, _v(b, ts))
    if gain_f:
        nodes['gain-final'] = ('gain', gain_f, [t for _, ts in fp for t in ts])
        add_ribbon('gain-final', 'parent', gain_f)
    return nodes, ribbons


def expected_lines(b, nodes):
    rev = nodes['revenue'][1]
    prev = _v(b, nodes['revenue'][2], True)
    lines = {}
    for i, (role, value, terms) in nodes.items():
        p = _v(b, terms, True)
        out = []
        share = value / rev * 100
        if role in ('cost', 'cost-leaf') and share < D('0.05'):
            lines[i] = out
            continue
        if p is None:
            if role in ('cost', 'cost-leaf'):
                out.append(f'占营收 {_r(share)}%')
            lines[i] = out
            continue
        if i in RATE:
            out.append(f'{RATE[i]} {_r(share)}%（{_r(share - p / prev * 100):+}pp）')
        if role in ('revenue', 'profit', 'source') and p > 0:
            out.append(f'同比 {_r((value / p - 1) * 100):+}%')
        if role in ('cost', 'cost-leaf'):
            s = f'占营收 {_r(share)}%'
            if p >= 0 and prev > 0:
                s += f'（{_r(share - p / prev * 100):+}pp）'
            out.append(s)
        lines[i] = out
    return lines


def check(markup, b):
    root = ET.fromstring(markup)

    def need(ok, why):
        if not ok:
            raise ValueError('INCOME_FLOW_V3_' + why)

    close = lambda a, c: abs(D(a) - D(c)) < D('.00001')
    need(root.get('data-chain-layout') == 'INCOME_FLOW_V3', 'LAYOUT')
    need(b.get('comparatives') is not None, 'PRIOR_PERIOD_CELLS_REQUIRED')
    axis = root.get('data-chain-axis')
    need(axis in ('height', 'width'), 'AXIS')
    nodes, ribbons = expected(b)
    phone = axis == 'width'
    leaves = {k: v for k, v in nodes.items() if k.startswith(('opex-', 'cogs-'))}
    drawn = {k: v for k, v in nodes.items() if not (phone and k in leaves)}
    drawn_r = {k: v for k, v in ribbons.items() if not (phone and k[1] in leaves)}
    rev = nodes['revenue'][1]
    scale = D(root.get('data-chain-scale'))
    need(scale == rev / (D(298) if phone else D(300)), 'COMMON_SCALE')
    rects = {r.get('data-chain-node'): r for r in root.iter(NS + 'rect') if r.get('data-chain-node')}
    need(set(rects) == set(drawn), 'NODE_SET')
    for i, (role, value, terms) in drawn.items():
        r = rects[i]
        need(r.get('data-chain-role') == role and D(r.get('data-chain-node-yuan')) == value, 'NODE_AMOUNT ' + i)
        need(json.loads(r.get('data-chain-terms')) == terms, 'NODE_TERMS ' + i)
        need(close(r.get(axis), value / scale), 'NODE_MONEY_SIZE ' + i)
        p = _v(b, terms, True)
        need((r.get('data-chain-prior-yuan') is None) == (p is None), 'PRIOR_ATTRIBUTE ' + i)
        if p is not None:
            need(D(r.get('data-chain-prior-yuan')) == p, 'PRIOR_AMOUNT ' + i)
    seen = {}
    ports_out, ports_in = {}, {}
    for path in root.iter(NS + 'path'):
        if path.get('data-chain-yuan') is None:
            continue
        a, z, v = path.get('data-chain-source'), path.get('data-chain-target'), D(path.get('data-chain-yuan'))
        need((a, z) in drawn_r and drawn_r[(a, z)] == v and (a, z) not in seen, 'RIBBON ' + str((a, z)))
        seen[(a, z)] = v
        n = [D(x) for x in re.findall(r'-?\d+(?:\.\d+)?', path.get('d'))]
        need(len(n) == 16, 'PATH_SHAPE')
        th = v / scale
        A, Z = rects[a], rects[z]
        if phone:
            need(close(n[1], D(A.get('y')) + D(A.get('height'))) and close(n[7], Z.get('y')), 'PATH_ENDPOINTS')
            need(close(n[8] - n[6], th) and close(n[14] - n[0], th), 'PATH_THICKNESS')
            ports_out.setdefault(a, []).append((n[0] - D(A.get('x')), th))
            ports_in.setdefault(z, []).append((n[6] - D(Z.get('x')), th))
        else:
            need(close(n[0], D(A.get('x')) + D(A.get('width'))) and close(n[6], Z.get('x')), 'PATH_ENDPOINTS')
            need(close(n[9] - n[7], th) and close(n[15] - n[1], th), 'PATH_THICKNESS')
            ports_out.setdefault(a, []).append((n[1] - D(A.get('y')), th))
            ports_in.setdefault(z, []).append((n[7] - D(Z.get('y')), th))
    need(seen == drawn_r, 'RIBBON_SET')
    for ports in (ports_out, ports_in):
        for i, items in ports.items():
            cursor = D(0)
            for start, th in sorted(items):
                need(close(start, cursor), 'PORT_GAP_OR_OVERLAP ' + i)
                cursor += th
            need(cursor <= D(rects[i].get(axis)) + D('.00001'), 'PORT_EXCEEDS_NODE ' + i)
    lines = expected_lines(b, nodes)
    texts = [t.text or '' for t in root.iter(NS + 'text')]
    pieces = [p for t in texts for p in re.split('　', t)]
    for i, want in lines.items():
        if phone and i in leaves:
            continue
        for w in want:
            need(w in pieces or any(w in t for t in texts), 'ANNOTATION_MISSING ' + i + ' ' + w)
    allowed = {w for ws in lines.values() for w in ws}
    printed = [p for t in texts for p in re.findall(r'(?:毛利率|营业利润率|归母净利率) [-0-9.]+%（[+-][0-9.]+pp）|同比 [+-][0-9.]+%|占营收 [0-9.]+%(?:（[+-][0-9.]+pp）)?', t)]
    need(all(p in allowed for p in printed), 'ANNOTATION_NOT_RECOMPUTED')
    if b.get('editorial', {}).get('show_disclosed_checkpoints'):
        stages = {stage['id']: stage for stage in b['stages']}
        def check_amount(key):
            v = _v(b, stages[key]['terms'])
            if abs(v) >= D('100000000'):
                return f"{v / D('100000000'):,.2f}亿"
            if abs(v) >= D('10000'):
                return f"{v / D('10000'):,.2f}万"
            return f"{v:,.2f}元"
        label = '税前利润 ' + check_amount('pretax') + ' · 合并净利润 ' + check_amount('net')
        need(label in texts, 'DISCLOSED_SUBTOTAL_LABEL_MISSING_OR_FALSE')
    if phone:
        bars = {r.get('data-chain-leaf'): r for r in root.iter(NS + 'rect') if r.get('data-chain-leaf')}
        need(set(bars) == set(leaves), 'PHONE_LEAF_SET')
        if leaves:
            top = max(v[1] for v in leaves.values())
            for i, r in bars.items():
                need(D(r.get('data-chain-leaf-yuan')) == leaves[i][1], 'PHONE_LEAF_AMOUNT ' + i)
                need(close(r.get('width'), leaves[i][1] / top * 130), 'PHONE_LEAF_WIDTH ' + i)
    return {'status': 'PASS', 'grammar': 'FULL_PROFIT_CHAIN_V1', 'layout': 'INCOME_FLOW_V3', 'original_source_vector_values': 'PASS',
            'source_rows': len(drawn), 'edges': len(drawn_r), 'endpoint': 'parent', 'actual_path_geometry': 'PASS'}
