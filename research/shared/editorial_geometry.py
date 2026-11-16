"""Independent SVG accounting geometry audit; never imports a renderer."""
from decimal import Decimal as D, InvalidOperation
import re
import xml.etree.ElementTree as ET
NS='{http://www.w3.org/2000/svg}'

def check_editorial_svg(markup,*,issuer,pdf_sha256):
    root=ET.fromstring(markup)
    def require(test,reason):
        if not test:raise ValueError('EDITORIAL_GEOMETRY_'+reason)
    def num(value):
        try:n=D(value)
        except (InvalidOperation,TypeError):raise ValueError('EDITORIAL_GEOMETRY_BAD_MONEY')
        require(n.is_finite(),'NONFINITE');return n
    def close(a,b):return abs(num(a)-num(b))<D('.00001')
    def inspect(node):
        require(node.get('data-issuer')==issuer,'ISSUER')
        require(node.get('data-original-pdf-sha256')==pdf_sha256,'PDF_SHA')
        mobile=node.get('data-layout')=='native-330'
        require(node.get('data-layout') in ('native-330','editorial-1040'),'LAYOUT')
        grammar=node.get('data-editorial-grammar')
        rects=list(node.iter(NS+'rect'))
        canvas=D(330) if mobile else D(1040)
        def inside(r):require(num(r.get('x'))>=0 and num(r.get('x'))+num(r.get('width'))<=canvas,'BAR_OUTSIDE_CANVAS')
        if grammar=='SOURCE_SEPARATE_PANELS_V1':
            children=[g for g in node if g.get('data-editorial-grammar')]
            require(bool(children),'EMPTY_PANELS')
            return sum(inspect(g) for g in children)
        if grammar=='SOURCE_SIGNED_BRIDGE_V1':
            bars=[r for r in rects if r.get('data-signed-yuan') is not None]
            require(len(bars)>=2,'BRIDGE_ROWS')
            before=[num(r.get('data-before-yuan')) for r in bars];after=[num(r.get('data-after-yuan')) for r in bars]
            low=min([D(0)]+before+after);high=max([D(0)]+before+after)
            left,right=(D(16),D(314)) if mobile else (D(330),D(790))
            scale=(high-low)/(right-left) if high!=low else None
            running=D(0)
            for i,r in enumerate(bars):
                kind=r.get('data-kind');value=num(r.get('data-signed-yuan'))
                require(kind in ('start','step','total'),'BRIDGE_ROLE')
                if i==0:require(kind=='start','BRIDGE_START')
                if i:require(kind!='start','BRIDGE_RESTART')
                if kind=='step':
                    require(before[i]==running,'BRIDGE_DISCONNECTED');running+=value
                else:
                    require(before[i]==0,'CHECKPOINT_ZERO_ORIGIN')
                    if kind=='total':require(value==running,'CHECKPOINT_ADDED_OR_FALSE')
                    else:running=value
                require(after[i]==running and num(r.get('data-cumulative-yuan'))==running,'BRIDGE_CUMULATIVE')
                if scale:
                    require(num(r.get('data-scale-yuan-per-unit'))==scale,'BRIDGE_SCALE')
                    require(close(r.get('width'),abs(after[i]-before[i])/scale),'BRIDGE_WIDTH')
                    require(close(r.get('x'),left+(min(before[i],after[i])-low)/scale),'BRIDGE_POSITION')
                else:require(num(r.get('width'))==0 and r.get('data-scale-yuan-per-unit')=='ZERO_ONLY','ZERO_INFLATED')
                color='#263F47' if kind!='step' else '#239878' if value>=0 else '#CD7271'
                require(r.get('fill').upper()==color,'SIGNED_COLOR')
                require(bool(r.get('data-source-reference')),'BRIDGE_SOURCE')
            require(bars[-1].get('data-kind')=='total','BRIDGE_FINAL')
            return len(bars)
        if grammar=='SOURCE_EQUAL_STOCK_BALANCE_V1':
            bars=[r for r in rects if r.get('data-stock-role')]
            dates=sorted({r.get('data-date') for r in bars})
            require(bool(dates),'STOCK_DATES')
            assets=[]
            for date in dates:
                require(bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}',date or '')),'STOCK_DATE')
                items=[r for r in bars if r.get('data-date')==date]
                require(len(items)==3,'STOCK_ROLES')
                by_role={r.get('data-stock-role'):num(r.get('data-exact-yuan')) for r in items}
                require(set(by_role)=={'assets','liabilities','equity'},'STOCK_IDENTITY_ROLES')
                require(by_role['assets']==by_role['liabilities']+by_role['equity'],'STOCK_NOT_BALANCED')
                assets.append(by_role['assets'])
            left,right=(D(16),D(314)) if mobile else (D(260),D(1008));scale=max(assets)/(right-left)
            for r in bars:require(num(r.get('data-scale-yuan-per-unit'))==scale and close(r.get('width'),num(r.get('data-exact-yuan'))/scale),'STOCK_SCALE_WIDTH')
            return len(bars)
        if grammar=='SOURCE_NONNEGATIVE_COMPONENTS_V1':
            bars=[r for r in rects if r.get('data-exact-yuan') is not None]
            values=[num(r.get('data-exact-yuan')) for r in bars]
            require(bool(values) and min(values)>=0,'COMPONENT_VALUES')
            require(sum(values)==num(node.get('data-total-yuan')),'COMPONENT_SUM')
            left,right=(D(16),D(314)) if mobile else (D(32),D(1008));domain=num(node.get('data-reference-total-yuan'))
            require(domain>=sum(values) and domain>0,'COMPONENT_DOMAIN')
            scale=domain/(right-left);cursor=left
            for r,value in zip(bars,values):
                require(close(r.get('x'),cursor) and close(r.get('width'),value/scale),'COMPONENT_GEOMETRY')
                require(num(r.get('data-scale-yuan-per-unit'))==scale,'COMPONENT_SCALE');cursor+=value/scale
            return len(bars)
        if grammar=='SOURCE_TWO_PERIOD_COMPARISON_V1':
            bars=[r for r in rects if r.get('data-comparison-pair') is not None]
            require(bool(bars),'COMPARISON_EMPTY')
            left,right=(D(16),D(314)) if mobile else (D(310),D(790))
            for pair in {r.get('data-comparison-pair') for r in bars}:
                items=[r for r in bars if r.get('data-comparison-pair')==pair]
                require(len(items)==2 and len({r.get('data-period') for r in items})==2,'COMPARISON_PERIODS')
                require(len({r.get('data-unit') for r in items})==1 and bool(items[0].get('data-unit')),'COMPARISON_UNITS')
                values=[num(r.get('data-exact-value')) for r in items];low=min([D(0)]+values);high=max([D(0)]+values)
                for r,value in zip(items,values):
                    expected=abs(value)/(high-low)*(right-left) if high!=low else D(0)
                    require(close(r.get('width'),expected),'COMPARISON_WIDTH')
                    require(close(r.get('x'),left+(min(D(0),value)-low)/(high-low)*(right-left) if high!=low else left),'COMPARISON_POSITION')
            return len(bars)
        if grammar=='SOURCE_REPORTED_RATIO_V1':
            bars=[r for r in rects if r.get('data-exact-percent') is not None]
            span=D(298) if mobile else D(976)
            require(bool(bars),'SHARE_EMPTY')
            for r in bars:
                v=num(r.get('data-exact-percent'));require(0<=v<=100 and bool(r.get('data-denominator')),'SHARE_DENOMINATOR')
                require(close(r.get('width'),span*v/100),'SHARE_WIDTH')
            return len(bars)
        if grammar=='SOURCE_INDEPENDENT_METRICS_V1':
            items=[r for r in node.iter(NS+'text') if r.get('data-exact-value') is not None]
            require(bool(items),'METRICS_EMPTY')
            for r in items:num(r.get('data-exact-value'));require(bool(r.get('data-unit')) and bool(r.get('data-source-reference')),'METRIC_UNIT_SOURCE')
            return len(items)
        if grammar=='SOURCE_KPI_BOARD_V1':
            micro=[r for r in rects if r.get('data-micro-value') is not None]
            require(bool(micro) and len(micro)%2==0,'KPI_MICRO_BARS')
            for i in range(0,len(micro),2):
                pair=micro[i:i+2];vals=[num(r.get('data-micro-value')) for r in pair]
                domain=max([abs(v) for v in vals]+[D(1)])
                for r,v in zip(pair,vals):
                    require(num(r.get('data-micro-domain'))==domain,'KPI_MICRO_DOMAIN')
                    require(close(r.get('width'),abs(v)/domain*num(r.get('data-micro-span'))),'KPI_MICRO_WIDTH')
            values=[t for t in node.iter(NS+'text') if t.get('data-exact-value') is not None]
            require(len(values)*2==len(micro),'KPI_TILE_COUNT')
            return len(values)
        if grammar=='SOURCE_RATIO_DUMBBELL_V1':
            dots=[c for c in node.iter(NS+'circle') if c.get('data-ratio-role')]
            require(bool(dots) and len(dots)%2==0,'DUMBBELL_DOTS')
            domains={c.get('data-domain-percent') for c in dots};require(len(domains)==1,'DUMBBELL_ONE_AXIS')
            domain=num(dots[0].get('data-domain-percent'));values=[num(c.get('data-exact-percent-value')) for c in dots]
            require(min(values)>=0 and domain>=max(values),'DUMBBELL_DOMAIN')
            for c in dots:
                v=num(c.get('data-exact-percent-value'));require(close(c.get('cx'),num(c.get('data-axis-left'))+v/domain*num(c.get('data-axis-span'))),'DUMBBELL_POSITION')
            for i in range(0,len(dots),2):require([dots[i].get('data-ratio-role'),dots[i+1].get('data-ratio-role')]==['prior','current'],'DUMBBELL_PAIR')
            return len(dots)
        if grammar=='SOURCE_GROWTH_BARS_V1':
            bars=[r for r in rects if r.get('data-growth-percent') is not None]
            require(bool(bars),'GROWTH_EMPTY');domain=num(bars[0].get('data-domain-percent'))
            for r in bars:
                value,prior=num(r.get('data-exact-value')),num(r.get('data-exact-prior'));require(prior>0,'GROWTH_BASE')
                g=(value/prior-1)*100;require(num(r.get('data-growth-percent'))==g and abs(g)<=domain,'GROWTH_VALUE')
                w=abs(g)/domain*num(r.get('data-axis-half'));center=num(r.get('data-axis-center'))
                require(close(r.get('width'),w) and close(r.get('x'),center if g>=0 else center-w),'GROWTH_GEOMETRY');inside(r)
            return len(bars)
        if grammar=='SOURCE_PERIOD_COLUMNS_V1':
            bars=[r for r in rects if r.get('data-axis-base') is not None]
            require(len(bars)>=2,'COLUMNS_EMPTY');values=[num(r.get('data-exact-value')) for r in bars];top=max(values)
            require(min(values)>=0 and top>0,'COLUMNS_VALUES')
            for r,v in zip(bars,values):
                require(num(r.get('data-domain-max'))==top,'COLUMNS_DOMAIN');h=v/top*num(r.get('data-axis-height'))
                require(close(r.get('height'),h) and close(r.get('y'),num(r.get('data-axis-base'))-h),'COLUMNS_GEOMETRY')
            return len(bars)
        if grammar=='SOURCE_STOCK_DELTA_V1':
            bars=[r for r in rects if r.get('data-stock-delta') is not None]
            require(bool(bars),'DELTA_EMPTY');deltas=[num(r.get('data-exact-value'))-num(r.get('data-exact-prior')) for r in bars]
            m=max(abs(d) for d in deltas) or D(1)
            for r,d in zip(bars,deltas):
                require(num(r.get('data-stock-delta'))==d and num(r.get('data-domain-yuan'))==m,'DELTA_VALUE')
                w=abs(d)/m*num(r.get('data-axis-half'));center=num(r.get('data-axis-center'))
                require(close(r.get('width'),w) and close(r.get('x'),center if d>=0 else center-w),'DELTA_GEOMETRY');inside(r)
                uses=(d>0)==(r.get('data-stock-side')=='asset') and d!=0
                require(r.get('fill').upper()==('#C2362E' if uses else '#16824A'),'DELTA_CASH_COLOUR')
            return len(bars)
        raise ValueError('EDITORIAL_GEOMETRY_UNKNOWN_GRAMMAR '+str(grammar))
    return {'status':'PASS','observed_source_rows':inspect(root),'grammar':root.get('data-editorial-grammar')}
