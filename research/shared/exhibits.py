"""Exhibit library v2: the chart families of an AEI-grade earnings read, drawn from exact source values.

Families (each with a 1040-wide desktop and a native 330-wide phone edition):
  kpi_board     本期一览: big numbers with year-over-year change and a two-period micro bar
  ratio_dumbbell 利润率/费用率: prior vs current position on one percentage axis, pp change
  growth_bars   增速对比: year-over-year growth of several lines on one diverging axis
  period_columns 季度走势: one column per reporting period, with year-over-year labels
  stock_delta   资本占用: change of balance-sheet items since the opening date, coloured by cash effect

Inputs are already-resolved exact Decimals plus their source expressions; this module never reads a
ledger and never infers a number. Each drawn element carries the exact value, its expression and the
geometry constants, so ``editorial_geometry.py`` re-measures shapes and ``source_publication_audit.py``
re-derives every value from the original ledger without importing this file.
"""
from decimal import Decimal as D
from html import escape as E
import json

INK, MUTED, GRID = '#1D2B33', '#5E6B73', '#E3E6E8'
GREEN, RED, GREY, DARK, OCHRE = '#16824A', '#C2362E', '#AEB5BC', '#3F4650', '#B07D12'
FONT = 'Noto Sans CJK SC,PingFang SC,Arial,sans-serif'


def q(x, places=1):
    return D(x).quantize(D(1).scaleb(-places), rounding='ROUND_HALF_UP')


def yi(v):
    v = D(v)
    if abs(v) >= D(100000000):
        return f'{v / D(100000000):,.2f}亿'
    if abs(v) >= D(10000):
        return f'{v / D(10000):,.2f}万'
    return f'{v:,.2f}元'


def f(x):
    return format(D(str(x)).quantize(D('.000001')), 'f')


def ref(expr):
    return E(json.dumps(expr, ensure_ascii=False, separators=(',', ':')), quote=True)


class Canvas:
    def __init__(self, grammar, title, *, issuer, period, pdf_sha256, mobile, external=None):
        self.out, self.grammar, self.title, self.mobile = [], grammar, title, mobile
        self.meta = (f'data-editorial-grammar="{grammar}" data-design-system="FINANCIALS_UNIFIED_STORY_V1" '
                     f'data-issuer="{E(issuer, quote=True)}" data-period="{E(period, quote=True)}" '
                     f'data-original-pdf-sha256="{pdf_sha256}" data-layout="{"native-330" if mobile else "editorial-1040"}"')
        if external:
            self.meta += f' data-external-ledgers="{ref(external)}"'
        self.width = 330 if mobile else 1040

    def text(self, x, y, t, size=12, anchor='start', color=INK, weight=500, **attrs):
        # Conservative width estimate (CJK and full-width = 1em, other glyphs 0.62em, bold +4%).
        # Browsers differ (WebKit renders CJK wider than Chromium), so refuse text that cannot fit.
        em = sum(1 if ord(ch) > 0x2E7F else 0.62 for ch in str(t)) * size * (1.04 if int(weight) >= 600 else 1)
        lo = {'start': D(x), 'middle': D(x) - D(str(em)) / 2, 'end': D(x) - D(str(em))}[anchor]
        if lo < 0 or lo + D(str(em)) > self.width:
            raise ValueError(f'EXHIBIT_TEXT_EXCEEDS_CANVAS {t}')
        extra = ''.join(f' data-{k.replace("_", "-")}="{E(str(v), quote=True)}"' for k, v in attrs.items())
        self.out.append(f'<text x="{f(x)}" y="{f(y)}" fill="{color}" font-size="{size}" style="font-size:{size}px" '
                        f'font-family="{FONT}" text-anchor="{anchor}" font-weight="{weight}"{extra}>{E(t)}</text>')

    def raw(self, s):
        self.out.append(s)

    def svg(self, height):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {int(height)}" role="img" '
                f'aria-label="{E(self.title, quote=True)}" {self.meta}><title>{E(self.title)}</title>' + ''.join(self.out) + '</svg>')


def growth(cur, prior):
    if prior is None or prior <= 0:
        return None
    return (cur / prior - 1) * 100


# ---------------------------------------------------------------- KPI board
def render_kpi_board(tiles, title, *, mobile=False, **ident):
    """tiles: dicts {label, kind: money|ratio, value, prior, value_ref, prior_ref, period, prior_period}.
    money: value/prior are exact yuan.  ratio: value/prior are exact percentages (already num/den*100),
    with value_ref/prior_ref = {"num": expr, "den": expr}."""
    c = Canvas('SOURCE_KPI_BOARD_V1', title, mobile=mobile, **ident)
    cols = 2 if mobile else 3
    tw, th, gap = ((149, 126, 16) if mobile else (320, 132, 20))
    x0, y0 = (16, 8) if mobile else (20, 8)
    for i, t in enumerate(tiles):
        col, row = i % cols, i // cols
        x, y = x0 + col * (tw + gap), y0 + row * (th + gap)
        c.raw(f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="10" fill="#F6F7F8"/>')
        c.text(x + 14, y + 26, t['label'], 12 if mobile else 13, color=MUTED, weight=600)
        if t['kind'] == 'money':
            # headline figure: 亿 from 0.1亿 up keeps the tile short enough for a 149-wide phone tile
            shown = f"{q(D(t['value']) / D(100000000), 2)}亿" if abs(D(t['value'])) >= D(10000000) else yi(t['value'])
            delta = growth(t['value'], t['prior'])
            dtext = (f'{t.get("delta_label", "同比")} {q(delta):+}%' if delta is not None else '上期为负或零，不计算增速')
            good = delta is None or delta >= 0
            if t.get('lower_is_better') and delta is not None:
                good = delta <= 0
        else:
            shown = f'{q(t["value"])}%'
            delta = t['value'] - t['prior']
            dtext = f'{t.get("delta_label", "同比")} {q(delta):+}pp'
            good = delta >= 0 if not t.get('lower_is_better') else delta <= 0
        c.text(x + 14, y + (64 if mobile else 70), shown, 22 if mobile else 30, color=INK, weight=700,
               exact_value=t['value'], source_reference=json.dumps(t['value_ref'], ensure_ascii=False, separators=(',', ':')),
               kpi_kind=t['kind'], period=t['period'], unit='元' if t['kind'] == 'money' else '%')
        c.text(x + 14, y + (88 if mobile else 98), dtext, 11 if mobile else 13, color=GREEN if good else RED, weight=700,
               delta_label=t.get('delta_label', '同比'), exact_prior=t['prior'], prior_reference=json.dumps(t['prior_ref'], ensure_ascii=False, separators=(',', ':')),
               prior_period=t['prior_period'])
        # two-period micro bars, own scale per tile (stated in the legend line)
        top = max(abs(t['value']), abs(t['prior']), D(1))
        bw = D(tw - 28)
        for j, (v, colr, per) in enumerate(((t['prior'], GREY, t['prior_period']), (t['value'], DARK, t['period']))):
            w = abs(v) / top * bw
            colr = RED if v < 0 else colr  # a negative amount is drawn by length but never in the positive colour
            c.raw(f'<rect x="{x + 14}" y="{f(y + (100 if mobile else 108) + j * 9)}" width="{f(w)}" height="6" rx="2" fill="{colr}" '
                  f'data-micro-value="{v}" data-micro-domain="{top}" data-micro-span="{bw}" data-period="{E(per, quote=True)}"/>')
    rows = (len(tiles) + cols - 1) // cols
    h = y0 + rows * (th + gap) + 18
    # phone: 330 wide at 10px leaves ~28 CJK characters once WebKit metrics are counted
    c.text(x0, h - 8, '小条：深色本期，浅色对比期；各格独立比例。' if mobile else '每格小条：深色为本期，浅色为对比期（见各格标注），各格独立比例。', 10 if mobile else 11, color=MUTED)
    return c.svg(h)


# ---------------------------------------------------------------- ratio dumbbell
def render_ratio_dumbbell(rows, title, *, periods, mobile=False, **ident):
    """rows: dicts {label, value, prior (percent), value_ref, prior_ref ({num,den}), lower_is_better}."""
    c = Canvas('SOURCE_RATIO_DUMBBELL_V1', title, mobile=mobile, **ident)
    hi = max([r['value'] for r in rows] + [r['prior'] for r in rows] + [D(1)])
    lo = min([r['value'] for r in rows] + [r['prior'] for r in rows] + [D(0)])
    if lo < 0:
        raise ValueError('RATIO_DUMBBELL_NEGATIVE_RATIO_USE_SIGNED_CHART')
    domain = (int(hi * D('1.12') / 10) + 1) * 10
    left, right = (D(16), D(300)) if mobile else (D(300), D(880))
    span = right - left
    x = lambda v: left + v / domain * span
    y = 40
    c.text(16 if mobile else 24, 18, f'○ {periods[0]}　● {periods[1]}　横轴 0–{domain}%', 11, color=MUTED, weight=600)
    for k in range(0, domain + 1, 10 if domain <= 60 else 20):
        c.raw(f'<line x1="{f(x(D(k)))}" x2="{f(x(D(k)))}" y1="32" y2="{32 + len(rows) * (70 if mobile else 54)}" stroke="{GRID}" stroke-width="1"/>')
    for r in rows:
        better = (r['value'] >= r['prior']) != bool(r.get('lower_is_better'))
        colr = GREEN if better else RED
        if mobile:
            c.text(16, y + 4, r['label'], 13, weight=700)
            c.text(314, y + 4, f'{q(r["prior"])}% → {q(r["value"])}%（{q(r["value"] - r["prior"]):+}pp）', 12, 'end', colr, 700)
            cy = y + 26
        else:
            c.text(24, y + 5, r['label'], 14, weight=700)
            c.text(1016, y + 5, f'{q(r["prior"])}% → {q(r["value"])}%（{q(r["value"] - r["prior"]):+}pp）', 13, 'end', colr, 700)
            cy = y
        a, b = sorted((x(r['prior']), x(r['value'])))
        c.raw(f'<line x1="{f(a)}" x2="{f(b)}" y1="{cy}" y2="{cy}" stroke="{colr}" stroke-width="4" stroke-opacity=".45"/>')
        for v, refv, kind in ((r['prior'], r['prior_ref'], 'prior'), (r['value'], r['value_ref'], 'current')):
            fill = '#FFFFFF' if kind == 'prior' else colr
            c.raw(f'<circle cx="{f(x(v))}" cy="{cy}" r="7" fill="{fill}" stroke="{colr if kind == "current" else DARK}" stroke-width="2" '
                  f'data-ratio-role="{kind}" data-exact-percent-value="{v}" data-ratio-reference="{ref(refv)}" '
                  f'data-axis-left="{left}" data-axis-span="{span}" data-domain-percent="{domain}" '
                  f'data-period="{E(periods[0] if kind == "prior" else periods[1], quote=True)}"/>')
        y += 70 if mobile else 54
    return c.svg(y + 10)


# ---------------------------------------------------------------- growth bars
def _axis(values, mobile, desktop):
    """Zero line and half-length. Phone: one-signed data uses the full width from the edge."""
    if not mobile:
        return desktop
    if all(v >= 0 for v in values):
        return D(16), D(298)
    if all(v <= 0 for v in values):
        return D(314), D(298)
    return D(165), D(140)


def render_growth_bars(rows, title, *, periods, mobile=False, **ident):
    """rows: dicts {label, value, prior (exact yuan), value_ref, prior_ref}. Growth needs a positive base."""
    c = Canvas('SOURCE_GROWTH_BARS_V1', title, mobile=mobile, **ident)
    gs = []
    for r in rows:
        g = growth(r['value'], r['prior'])
        if g is None:
            raise ValueError('GROWTH_BARS_NONPOSITIVE_BASE ' + r['label'])
        gs.append(g)
    m = max(abs(g) for g in gs)
    domain = max(10, (int(m * D('1.1') / 10) + 1) * 10)
    center, half = _axis(gs, mobile, (D(620), D(300)))
    y = 46
    c.text(16 if mobile else 24, 18, f'{periods[1]} 同比　轴 ±{domain}%' if mobile else f'{periods[1]} 相对 {periods[0]} 的同比增速　轴范围 ±{domain}%', 11, color=MUTED, weight=600)
    height = len(rows) * (52 if mobile else 40) + 40
    c.raw(f'<line x1="{center}" x2="{center}" y1="30" y2="{height}" stroke="{DARK}" stroke-width="1.5"/>')
    for r, g in zip(rows, gs):
        w = abs(g) / domain * half
        x0 = center if g >= 0 else center - w
        colr = GREEN if (g >= 0) != bool(r.get('lower_is_better')) else RED
        if mobile:
            c.text(16, y, r['label'], 12, weight=700)
            by = y + 8
        else:
            c.text(24, y + 13, r['label'], 14, weight=700)
            c.text(250, y + 13, f'{yi(r["prior"])} → {yi(r["value"])}', 12, color=MUTED)
            by = y
        c.raw(f'<rect x="{f(x0)}" y="{by}" width="{f(w)}" height="18" rx="3" fill="{colr}" fill-opacity=".85" '
              f'data-growth-percent="{g}" data-exact-value="{r["value"]}" data-exact-prior="{r["prior"]}" '
              f'data-value-reference="{ref(r["value_ref"])}" data-prior-reference="{ref(r["prior_ref"])}" '
              f'data-axis-center="{center}" data-axis-half="{half}" data-domain-percent="{domain}"/>')
        if mobile:  # the value rides on the label line so long bars never push it off the canvas
            c.text(314, y, f'{q(g):+}%', 12, 'end', colr, 700)
        else:
            lx = (x0 + w + 6) if g >= 0 else (x0 - 6)
            c.text(lx, by + 14, f'{q(g):+}%', 13, 'start' if g >= 0 else 'end', colr, 700)
        y += 52 if mobile else 40
    return c.svg(y + 6)


# ---------------------------------------------------------------- period columns
def render_period_columns(series, title, *, unit_label, mobile=False, **ident):
    """series: list of {label, value, value_ref, compare (index of the same period a year earlier or None), highlight}."""
    c = Canvas('SOURCE_PERIOD_COLUMNS_V1', title, mobile=mobile, external=ident.pop('external', None), **ident)
    if any(s['value'] < 0 for s in series):
        raise ValueError('PERIOD_COLUMNS_NEGATIVE_VALUE_USE_SIGNED_CHART')
    top = max(s['value'] for s in series)
    base, height = (D(250), D(170)) if mobile else (D(300), D(220))
    left, right = (D(16), D(314)) if mobile else (D(60), D(1000))
    slot = (right - left) / len(series)
    bw = slot * D('0.56')
    c.text(16 if mobile else 24, 18, unit_label + '　高亮为本报告期；柱顶为同比', 11, color=MUTED, weight=600)
    c.raw(f'<line x1="{left}" x2="{right}" y1="{base}" y2="{base}" stroke="{DARK}" stroke-width="1"/>')
    for i, s in enumerate(series):
        hgt = s['value'] / top * height
        x = left + slot * i + (slot - bw) / 2
        colr = DARK if s.get('highlight') else GREY
        c.raw(f'<rect x="{f(x)}" y="{f(base - hgt)}" width="{f(bw)}" height="{f(hgt)}" rx="3" fill="{colr}" '
              f'data-exact-value="{s["value"]}" data-value-reference="{ref(s["value_ref"])}" data-period="{E(s["label"], quote=True)}" '
              f'data-axis-base="{base}" data-axis-height="{height}" data-domain-max="{top}"/>')
        g = growth(s['value'], series[s['compare']]['value']) if s.get('compare') is not None else None
        # value sits on the bar; the growth line, when present, sits between them with a full line of air
        c.text(x + bw / 2, base - hgt - ((24 if mobile else 28) if g is not None else 9), yi(s['value']), 10 if mobile else 12, 'middle', INK, 700)
        if s.get('compare') is not None:
            if g is not None:
                c.text(x + bw / 2, base - hgt - 8, f'{q(g):+}%', 10 if mobile else 12, 'middle', GREEN if g >= 0 else RED, 700,
                       growth_of=i, growth_base=s['compare'])
        c.text(x + bw / 2, base + 18, s['label'], 10 if mobile else 12, 'middle', MUTED, 600)
    return c.svg(base + 34)


# ---------------------------------------------------------------- stock delta
def render_stock_delta(rows, title, *, dates, mobile=False, **ident):
    """rows: {label, side: asset|liability, value, prior (exact yuan stocks), value_ref, prior_ref}.
    Asset increase absorbs cash (red); liability increase supplies funding (green)."""
    c = Canvas('SOURCE_STOCK_DELTA_V1', title, mobile=mobile, **ident)
    deltas = [r['value'] - r['prior'] for r in rows]
    m = max(abs(d) for d in deltas) or D(1)
    center, half = _axis(deltas, mobile, (D(560), D(300)))
    c.text(16 if mobile else 24, 18, f'{dates[0]} → {dates[1]}　红=占用 绿=提供' if mobile else f'{dates[0]} → {dates[1]} 余额变化　红=占用资金　绿=提供资金', 11, color=MUTED, weight=600)
    y = 46
    total_h = len(rows) * (52 if mobile else 40) + 40
    c.raw(f'<line x1="{center}" x2="{center}" y1="30" y2="{total_h}" stroke="{DARK}" stroke-width="1.5"/>')
    for r, d in zip(rows, deltas):
        uses_cash = (d > 0) == (r['side'] == 'asset') and d != 0
        colr = RED if uses_cash else GREEN
        w = abs(d) / m * half
        x0 = center if d >= 0 else center - w
        if mobile:
            c.text(16, y, r['label'] + ('（资产）' if r['side'] == 'asset' else '（负债）'), 12, weight=700)
            by = y + 8
        else:
            c.text(24, y + 13, r['label'], 14, weight=700)
            c.text(170, y + 13, '资产' if r['side'] == 'asset' else '负债', 11, color=MUTED, weight=600)
            by = y
        c.raw(f'<rect x="{f(x0)}" y="{by}" width="{f(w)}" height="18" rx="3" fill="{colr}" fill-opacity=".85" '
              f'data-stock-delta="{d}" data-stock-side="{r["side"]}" data-exact-value="{r["value"]}" data-exact-prior="{r["prior"]}" '
              f'data-value-reference="{ref(r["value_ref"])}" data-prior-reference="{ref(r["prior_ref"])}" '
              f'data-axis-center="{center}" data-axis-half="{half}" data-domain-yuan="{m}"/>')
        pct = f'（{q((r["value"] / r["prior"] - 1) * 100, 0):+}%）' if r['prior'] > 0 else ''
        label = f'{"+" if d > 0 else ""}{yi(d)}{pct}'
        if mobile:
            c.text(314, y, label, 12, 'end', colr, 700)
        else:
            lx = (x0 + w + 6) if d >= 0 else (x0 - 6)
            c.text(lx, by + 14, label, 12, 'start' if d >= 0 else 'end', colr, 700)
        y += 52 if mobile else 40
    return c.svg(y + 6)
