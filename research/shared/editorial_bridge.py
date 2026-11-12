"""Common exact-money bridge art; issuer adapters retain accounting decisions.

Rows contain (label, exact CNY yuan, start|step|total, source reference).
Totals are independently checked nonadditive checkpoints. No sector, issuer,
period, financial result or minimum money size is inferred by this renderer.
"""
from decimal import Decimal as D, InvalidOperation
from html import escape as E
import re
import unicodedata
from unified_income_sankey import PALETTE as P


def number(v):
    try: x=D(str(v))
    except (InvalidOperation,ValueError,TypeError) as exc: raise ValueError('BRIDGE_INVALID_MONEY') from exc
    if not x.is_finite():raise ValueError('BRIDGE_NONFINITE_MONEY')
    return x


def money(v):
    x=number(v)
    if x==0:return '0 元'
    if abs(x)<10000:return f'{x:,.2f} 元'
    if abs(x)<1000000:return f'{x/D(10000):,.2f} 万元'
    return f'{x/D(100000000):,.2f} 亿'


def compile_rows(rows):
    if len(rows)<2 or rows[0][2]!='start' or rows[-1][2]!='total':
        raise ValueError('BRIDGE_START_AND_FINAL_CHECKPOINT_REQUIRED')
    current=D(0);out=[]
    for i,(label,value,kind,source) in enumerate(rows):
        if not isinstance(label,str) or not label.strip() or not isinstance(source,str) or not source.strip():
            raise ValueError('BRIDGE_LABEL_AND_SOURCE_REQUIRED')
        value=number(value)
        if kind=='start':
            if i:raise ValueError('BRIDGE_REPEATED_START')
            before=D(0);current=value;after=value
        elif kind=='step':before=current;current+=value;after=current
        elif kind=='total':
            if value!=current:raise ValueError('BRIDGE_CHECKPOINT_NOT_CLOSED '+label)
            before=D(0);after=current
        else:raise ValueError('BRIDGE_UNKNOWN_ROLE')
        out.append((label,value,kind,source,before,after,current))
    return tuple(out)


def wrap_label(label,limit):
    lines=[];line='';used=0
    for char in label:
        width=1 if unicodedata.east_asian_width(char) in ('W','F') else .6
        if line and used+width>limit:lines.append(line);line='';used=0
        line+=char;used+=width
    if line:lines.append(line)
    return lines


def check_identity(issuer,period,pdf_sha256,title):
    if not all(isinstance(x,str) and x.strip() for x in (title,issuer,period)):
        raise ValueError('BRIDGE_SOURCE_IDENTITY_REQUIRED')
    if not isinstance(pdf_sha256,str) or not re.fullmatch('[a-f0-9]{64}',pdf_sha256):
        raise ValueError('BRIDGE_PDF_FINGERPRINT_REQUIRED')


def render_bridge(rows,title,*,issuer,period,pdf_sha256,mobile=False):
    check_identity(issuer,period,pdf_sha256,title)
    values=compile_rows(rows)
    width=330 if mobile else 1040
    left,right=(D(16),D(314)) if mobile else (D(330),D(790))
    row_h=96 if mobile else 68;top=86
    wrapped=[wrap_label(r[0],22 if mobile else 18) for r in values]
    extras=[max(0,len(lines)-(1 if mobile else 2))*(18 if mobile else 20) for lines in wrapped]
    h=top+len(values)*row_h+sum(extras)+24
    low=min([D(0)]+[min(r[4],r[5]) for r in values]);high=max([D(0)]+[max(r[4],r[5]) for r in values])
    span=high-low;scale=span/(right-left) if span else None
    def x(v):return left+(v-low)/scale if scale else left
    def f(v):return format(number(v),'f')
    def text(xx,yy,label,size=13,anchor='start',color=None):
        return f'<text x="{f(xx)}" y="{yy}" text-anchor="{anchor}" fill="{color or P["ink"]}" font-size="{size}" style="font-size:{size}px" font-weight="600" font-family="Noto Sans CJK SC,PingFang SC,Arial,sans-serif">{E(label)}</text>'
    out=[text(16 if mobile else 32,24,'同一金额轴 · 有符号累计桥',14),text(16 if mobile else 32,48,'合计不重复加总；小额不放大',12,color=P['muted'])]
    if scale:out.append(f'<path d="M{f(x(0))},64 V{h-12}" stroke="{P["rule"]}" stroke-dasharray="4 5" data-zero-axis="0"/>')
    else:out.append(text(16 if mobile else 32,70,'全部原始金额为零；不绘制虚构比例尺',12,color=P['muted']))
    offset=0;previous_bar=None
    for i,(label,value,kind,source,before,after,cumulative) in enumerate(values):
        yy=top+i*row_h+offset;extra=extras[i];offset+=extra
        color=P['trunk'] if kind in ('start','total') else P['profit'] if value>=0 else P['cost']
        for j,label_line in enumerate(wrapped[i]):
            out.append(text(16 if mobile else 32,yy+j*(18 if mobile else 20),label_line,13 if mobile else 16))
        shown=('+' if kind=='step' and value>0 else '')+money(value)
        out.append(text(314 if mobile else 1008,yy+21+extra if mobile else yy,shown,13 if mobile else 16,'end',color))
        bar_y=yy+36+extra if mobile else yy+12
        if previous_bar is not None and kind=='step' and scale:
            out.append(f'<path d="M{f(x(before))},{previous_bar+16} V{bar_y}" stroke="{P["muted"]}" stroke-dasharray="3 4" fill="none"/>')
        previous_bar=bar_y
        out.append(f'<rect class="editorial-bridge-money" x="{f(x(min(before,after)))}" y="{bar_y}" width="{f(abs(after-before)/scale if scale else 0)}" height="16" fill="{color}" data-step="{i}" data-kind="{kind}" data-signed-yuan="{value}" data-before-yuan="{before}" data-after-yuan="{after}" data-cumulative-yuan="{cumulative}" data-scale-yuan-per-unit="{scale if scale else "ZERO_ONLY"}" data-source-reference="{E(source,quote=True)}"><title>{E(label)}；{value}元；{E(source)}</title></rect>')
        out.append(text(16 if mobile else 330,yy+76+extra if mobile else yy+52,'累计 '+money(cumulative),12,color=P['muted']))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" role="img" aria-label="{E(title,quote=True)}" data-editorial-grammar="SOURCE_SIGNED_BRIDGE_V1" data-design-system="FINANCIALS_UNIFIED_STORY_V1" data-issuer="{E(issuer,quote=True)}" data-period="{E(period,quote=True)}" data-original-pdf-sha256="{pdf_sha256}" data-layout="{"native-330" if mobile else "editorial-1040"}"><title>{E(title)}</title>'+''.join(out)+'</svg>'


def render_comparison(pairs,title,*,issuer,periods,pdf_sha256,mobile=False,percent=False):
    """Explicit two-period comparison; each pair has its own signed zero scale."""
    if len(periods)!=2 or periods[0]==periods[1] or not all(isinstance(p,str) and p.strip() for p in periods):raise ValueError('COMPARISON_TWO_PERIODS_REQUIRED')
    if not pairs:raise ValueError('COMPARISON_SOURCE_PAIRS_REQUIRED')
    # Reuse the source identity checks; no accounting bridge is implied here.
    check_identity(issuer,' / '.join(periods),pdf_sha256,title)
    width=330 if mobile else 1040;left=D(16) if mobile else D(310);right=D(314) if mobile else D(790)
    row_h=156 if mobile else 100;out=[]
    def txt(x,y,label,size=13,anchor='start',color=None):
        return f'<text x="{x}" y="{y}" font-size="{size}" style="font-size:{size}px" text-anchor="{anchor}" fill="{color or P["ink"]}" font-family="Noto Sans CJK SC,PingFang SC,Arial,sans-serif">{E(str(label))}</text>'
    out.append(txt(16 if mobile else 32,24,'两期对照 · 每项独立零基准',14))
    out.append(txt(16 if mobile else 32,47,'只比较同一项两期；不同项条长不可比',12,color=P['muted']))
    offset=0
    for i,pair in enumerate(pairs):
        if len(pair) not in (4,5):raise ValueError('COMPARISON_EXPLICIT_PAIR_SHAPE_REQUIRED')
        label,prior,now,source=pair[:4]
        unit=pair[4] if len(pair)==5 else ('percent' if percent else 'CNY_yuan')
        if not isinstance(unit,str) or not unit.strip():raise ValueError('COMPARISON_EXPLICIT_UNIT_REQUIRED')
        if not label or not source:raise ValueError('COMPARISON_LABEL_SOURCE_REQUIRED')
        prior,now=number(prior),number(now);low=min(D(0),prior,now);high=max(D(0),prior,now);span=high-low
        xx=lambda v:left+(v-low)/span*(right-left) if span else left
        lines=wrap_label(label,22 if mobile else 18)
        extra=max(0,len(lines)-(1 if mobile else 3))*(18 if mobile else 20)
        yy=83+i*row_h+offset;offset+=extra
        for line_index,line in enumerate(lines):out.append(txt(16 if mobile else 32,yy+line_index*(18 if mobile else 20),line,13 if mobile else 16))
        for j,(v,period,color) in enumerate(((prior,periods[0],P['source']),(now,periods[1],P['profit']))):
            y=yy+28+extra+j*56 if mobile else yy+13+j*37
            formatted=(f'{v:,.2f}%' if unit=='percent' else money(v) if unit=='CNY_yuan' else f'{v:,.2f} {unit}')
            out.append(txt(16 if mobile else 810,y,period+'  '+formatted,12 if mobile else 13,color=P['cost'] if v<0 else P['ink']))
            out.append(f'<rect x="{xx(min(D(0),v)):.8f}" y="{y+9 if mobile else y-11}" width="{abs(xx(v)-xx(D(0))):.8f}" height="12" fill="{P["cost"] if v<0 else color}" data-comparison-pair="{i}" data-domain-min="{low}" data-domain-max="{high}" data-exact-value="{v}" data-period="{E(period,quote=True)}" data-unit="{E(unit,quote=True)}" data-source-reference="{E(source,quote=True)}"/>')
        if span:out.append(f'<path d="M{xx(D(0)):.8f},{yy+28+extra if mobile else yy} V{yy+115+extra if mobile else yy+56}" stroke="{P["rule"]}" data-zero-axis="0"/>')
    h=83+len(pairs)*row_h+offset+16
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" role="img" aria-label="{E(title,quote=True)}" data-editorial-grammar="SOURCE_TWO_PERIOD_COMPARISON_V1" data-design-system="FINANCIALS_UNIFIED_STORY_V1" data-issuer="{E(issuer,quote=True)}" data-original-pdf-sha256="{pdf_sha256}" data-scale-policy="INDEPENDENT_PER_PAIR" data-layout="{"native-330" if mobile else "editorial-1040"}"><title>{E(title)}</title>'+''.join(out)+'</svg>'


def render_balance(dates,title,*,issuer,pdf_sha256,mobile=False):
    """Same-date asset=funding identity; no transfer edges between stocks."""
    if not dates:raise ValueError('BALANCE_SOURCE_DATES_REQUIRED')
    amounts=[]
    for date,assets,liabilities,equity,source in dates:
        a,l,e=map(number,(assets,liabilities,equity))
        if not date or not source or a!=l+e or min(a,l,e)<0 or a<=0:raise ValueError('BALANCE_POSITIVE_STOCK_IDENTITY_REQUIRED')
        amounts.append((date,a,l,e,source))
    check_identity(issuer,amounts[-1][0],pdf_sha256,title)
    width=330 if mobile else 1040;left=D(16) if mobile else D(260);right=D(314) if mobile else D(1008)
    scale=max(x[1] for x in amounts)/(right-left);rh=172 if mobile else 130;out=[]
    def txt(x,y,label,size=13,color=None):return f'<text x="{x}" y="{y}" font-size="{size}" style="font-size:{size}px" fill="{color or P["ink"]}" font-family="Noto Sans CJK SC,PingFang SC,Arial,sans-serif">{E(str(label))}</text>'
    out.append(txt(16 if mobile else 32,24,'同日资产＝负债＋权益',14));out.append(txt(16 if mobile else 32,48,'同一金额尺度的存量；不是资金流向',12,P['muted']))
    for i,(date,a,l,e,source) in enumerate(amounts):
        yy=82+i*rh;out.append(txt(16 if mobile else 32,yy,date,13 if mobile else 16))
        y=yy+18
        for kind,value,x,dy,color in [('assets',a,left,y,P['source_dark']),('liabilities',l,left,y+28,P['cost']),('equity',e,left+l/scale,y+28,P['profit'])]:
            out.append(f'<rect x="{x:.8f}" y="{dy}" width="{value/scale:.8f}" height="16" fill="{color}" data-stock-role="{kind}" data-exact-yuan="{value}" data-date="{E(date,quote=True)}" data-scale-yuan-per-unit="{scale}" data-source-reference="{E(source,quote=True)}"/>')
        out.append(txt(16 if mobile else 260,yy+89,'资产 '+money(a),12))
        out.append(txt(16 if mobile else 260,yy+115,'负债 '+money(l)+'；权益 '+money(e),12))
    h=82+rh*len(amounts)+16
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {h}" role="img" aria-label="{E(title,quote=True)}" data-editorial-grammar="SOURCE_EQUAL_STOCK_BALANCE_V1" data-design-system="FINANCIALS_UNIFIED_STORY_V1" data-issuer="{E(issuer,quote=True)}" data-original-pdf-sha256="{pdf_sha256}" data-layout="{"native-330" if mobile else "editorial-1040"}"><title>{E(title)}</title>'+''.join(out)+'</svg>'


def render_components(components,total,title,*,issuer,period,pdf_sha256,mobile=False,reference_total=None):
    """Nonnegative disclosed composition, not an income/cash transfer Sankey."""
    total=number(total)
    if not components or total<=0:raise ValueError('COMPONENT_NONZERO_TOTAL_REQUIRED')
    parts=[]
    for label,value,source in components:
        value=number(value)
        if value<0 or not label or not source:raise ValueError('COMPONENT_NONNEGATIVE_SOURCE_REQUIRED')
        parts.append((label,value,source))
    if sum((v for _,v,_ in parts),D(0))!=total:raise ValueError('COMPONENT_SOURCE_TOTAL_NOT_CLOSED')
    check_identity(issuer,period,pdf_sha256,title)
    width=330 if mobile else 1040;left=D(16) if mobile else D(32);right=D(314) if mobile else D(1008)
    domain=number(reference_total) if reference_total is not None else total
    if domain<total:raise ValueError('COMPONENT_REFERENCE_DOMAIN_TOO_SMALL')
    scale=domain/(right-left);colors=[P['source'],P['source_dark'],P['trunk'],'#899C93']
    def txt(x,y,label,size=13,anchor='start'):
        return f'<text x="{x}" y="{y}" font-size="{size}" style="font-size:{size}px" fill="{P["ink"]}" text-anchor="{anchor}" font-family="Noto Sans CJK SC,PingFang SC,Arial,sans-serif">{E(str(label))}</text>'
    out=[txt(left,24,'来源组成 · 原金额严格同尺度',14),txt(left,49,'合计 '+money(total),13)]
    cursor=left;yy=122
    for i,(label,value,source) in enumerate(parts):
        color=colors[i%len(colors)]
        out.append(f'<rect x="{cursor:.8f}" y="70" width="{value/scale:.8f}" height="23" fill="{color}" data-exact-yuan="{value}" data-scale-yuan-per-unit="{scale}" data-source-reference="{E(source,quote=True)}"/>');cursor+=value/scale
        lines=wrap_label(label,22 if mobile else 32)
        out.append(f'<rect x="{left}" y="{yy-10}" width="7" height="7" fill="{color}"/>')
        for j,line in enumerate(lines):out.append(txt(left+14,yy+j*18,line,13 if mobile else 16))
        amount_y=yy+len(lines)*18+4 if mobile else yy
        out.append(txt(right,amount_y,money(value)+' · 占合计 '+f'{value/total*100:.2f}%',12 if mobile else 16,'end'))
        yy+=len(lines)*18+39 if mobile else max(58,len(lines)*20+12)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {yy+16}" role="img" aria-label="{E(title,quote=True)}" data-total-yuan="{total}" data-reference-total-yuan="{domain}" data-editorial-grammar="SOURCE_NONNEGATIVE_COMPONENTS_V1" data-design-system="FINANCIALS_UNIFIED_STORY_V1" data-issuer="{E(issuer,quote=True)}" data-period="{E(period,quote=True)}" data-original-pdf-sha256="{pdf_sha256}" data-layout="{"native-330" if mobile else "editorial-1040"}"><title>{E(title)}</title>'+''.join(out)+'</svg>'


def render_metric_cards(entries,title,*,issuer,period,pdf_sha256,mobile=False):
    """Independent dimensions, directly labelled; no false common money scale."""
    check_identity(issuer,period,pdf_sha256,title)
    if not entries:raise ValueError('METRIC_SOURCE_ENTRIES_REQUIRED')
    width=330 if mobile else 1040;cols=1 if mobile else 3
    wrapped=[wrap_label(entry[0],22 if mobile else 18) for entry in entries]
    rh=max(152 if mobile else 180,max(len(x) for x in wrapped)*18+110);out=[]
    for i,(label,value,unit,source) in enumerate(entries):
        value=number(value)
        if not all(isinstance(x,str) and x.strip() for x in (label,unit,source)):raise ValueError('METRIC_LABEL_UNIT_SOURCE_REQUIRED')
        x=16 if mobile else 32+(i%cols)*325;yy=34+(i//cols)*rh
        lines=wrapped[i]
        for j,line in enumerate(lines):out.append(f'<text x="{x}" y="{yy+j*18}" font-size="13" style="font-size:13px" fill="{P["ink"]}" font-family="Noto Sans CJK SC,PingFang SC,Arial,sans-serif">{E(line)}</text>')
        shown=money(value) if unit=='CNY_yuan' else f'{value:,.2f} {unit}'
        out.append(f'<text x="{x}" y="{yy+len(lines)*18+28}" font-size="24" style="font-size:24px" font-weight="700" fill="{P["trunk"]}" font-family="Noto Sans CJK SC,PingFang SC,Arial,sans-serif" data-exact-value="{value}" data-unit="{E(unit,quote=True)}" data-source-reference="{E(source,quote=True)}">{E(shown)}</text>')
        out.append(f'<text x="{x}" y="{yy+len(lines)*18+60}" font-size="12" style="font-size:12px" fill="{P["muted"]}" font-family="Noto Sans CJK SC,PingFang SC,Arial,sans-serif">独立披露口径；来源见本图证据表</text>')
        out.append(f'<path d="M{x},{yy+rh-28} H{width-x if mobile else x+300}" stroke="{P["rule"]}"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {((len(entries)+cols-1)//cols)*rh+20}" role="img" aria-label="{E(title,quote=True)}" data-editorial-grammar="SOURCE_INDEPENDENT_METRICS_V1" data-design-system="FINANCIALS_UNIFIED_STORY_V1" data-issuer="{E(issuer,quote=True)}" data-period="{E(period,quote=True)}" data-original-pdf-sha256="{pdf_sha256}" data-layout="{"native-330" if mobile else "editorial-1040"}"><title>{E(title)}</title>'+''.join(out)+'</svg>'


def combine_panels(panels,title):
    """Separate semantic panels in one exportable vector, without transfer edges."""
    import xml.etree.ElementTree as ET
    if not panels:raise ValueError('EDITORIAL_PANELS_REQUIRED')
    roots=[ET.fromstring(p) for p in panels]
    keys=('data-issuer','data-original-pdf-sha256','data-layout')
    if any(tuple(r.get(k) for k in keys)!=tuple(roots[0].get(k) for k in keys) for r in roots):raise ValueError('EDITORIAL_PANEL_IDENTITY_OR_LAYOUT_DRIFT')
    width=roots[0].get('viewBox').split()[2];height=D(0)
    parent=ET.Element('{http://www.w3.org/2000/svg}svg',{'role':'img','aria-label':title,'data-editorial-grammar':'SOURCE_SEPARATE_PANELS_V1','data-design-system':'FINANCIALS_UNIFIED_STORY_V1',**{k:roots[0].get(k) for k in keys}})
    for r in roots:
        vb=r.get('viewBox').split()
        if vb[2]!=width:raise ValueError('EDITORIAL_PANEL_WIDTH_DRIFT')
        g=ET.SubElement(parent,'{http://www.w3.org/2000/svg}g',{'transform':f'translate(0 {height})',**{k:v for k,v in r.attrib.items() if k.startswith('data-')}})
        for child in r:g.append(child)
        height+=D(vb[3])+24
    parent.set('viewBox',f'0 0 {width} {height}')
    ET.register_namespace('','http://www.w3.org/2000/svg')
    return ET.tostring(parent,encoding='unicode')


def render_shares(entries,title,*,issuer,period,pdf_sha256,mobile=False):
    """Reported ratios with explicit denominators; no guessed company revenue share."""
    check_identity(issuer,period,pdf_sha256,title)
    if not entries:raise ValueError('SHARE_SOURCE_ROWS_REQUIRED')
    width=330 if mobile else 1040;left=D(16) if mobile else D(32);right=D(314) if mobile else D(1008)
    out=[];y=30
    def txt(x,yy,label,size=13,anchor='start'):
        return f'<text x="{x}" y="{yy}" text-anchor="{anchor}" font-size="{size}" style="font-size:{size}px" fill="{P["ink"]}" font-family="Noto Sans CJK SC,PingFang SC,Arial,sans-serif">{E(label)}</text>'
    for label,value,denominator,source in entries:
        value=number(value)
        if not D(0)<=value<=100 or not all(isinstance(x,str) and x.strip() for x in (label,denominator,source)):raise ValueError('SHARE_PERCENT_DENOMINATOR_SOURCE_REQUIRED')
        for j,line in enumerate(wrap_label(label,22 if mobile else 52)):out.append(txt(left,y+j*18,line,13 if mobile else 16))
        y+=len(wrap_label(label,22 if mobile else 52))*18+6
        out.append(txt(right,y,f'{value:.2f}%',16,'end'));y+=18
        out.append(f'<rect x="{left}" y="{y}" width="{right-left}" height="16" fill="{P["rule"]}"/>')
        out.append(f'<rect x="{left}" y="{y}" width="{(right-left)*value/100:.8f}" height="16" fill="{P["source_dark"]}" data-exact-percent="{value}" data-denominator="{E(denominator,quote=True)}" data-source-reference="{E(source,quote=True)}"/>');y+=43
        for line in wrap_label('分母：'+denominator,24 if mobile else 68):out.append(txt(left,y,line,12));y+=18
        y+=30
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {y}" role="img" aria-label="{E(title,quote=True)}" data-editorial-grammar="SOURCE_REPORTED_RATIO_V1" data-design-system="FINANCIALS_UNIFIED_STORY_V1" data-issuer="{E(issuer,quote=True)}" data-period="{E(period,quote=True)}" data-original-pdf-sha256="{pdf_sha256}" data-layout="{"native-330" if mobile else "editorial-1040"}"><title>{E(title)}</title>'+''.join(out)+'</svg>'
