"""Independent source-value auditor for the generic dossier's ACTUAL SVG.

This never imports the publisher or calls a renderer. It resolves original
source references and compares them to values physically encoded in geometry.
"""
import json,xml.etree.ElementTree as ET
from decimal import Decimal as D
N='{http://www.w3.org/2000/svg}'
def expected(ledger,expr):
    if isinstance(expr,str):return D(ledger['facts'][expr]['yuan'])
    return sum((D(str(c))*D(ledger['facts'][k]['yuan']) for k,c in expr),D(0))
EXHIBIT_GRAMMARS={'SOURCE_KPI_BOARD_V1','SOURCE_RATIO_DUMBBELL_V1','SOURCE_GROWTH_BARS_V1','SOURCE_PERIOD_COLUMNS_V1','SOURCE_STOCK_DELTA_V1'}
def _resolver(root,ledger):
    """Resolve plain, signed-sum, ratio and 'alias:key' expressions from original ledgers only."""
    from pathlib import Path
    import hashlib
    base=Path(__file__).resolve().parents[2];ext={}
    for alias,spec in json.loads(root.get('data-external-ledgers') or '{}').items():
        other=json.loads((base/spec['path']).resolve().read_text())
        if other['issuer']['code']!=ledger['issuer']['code'] or other['source']['original_bytes_sha256']!=spec['pdf_sha256'] or other['issuer']['fiscal_period']!=spec['period']:
            raise ValueError('DOSSIER_VECTOR_EXTERNAL_LEDGER_IDENTITY '+alias)
        ext[alias]=other
    def fact(key):
        if ':' in key:
            a,k=key.split(':',1);return D(ext[a]['facts'][k]['yuan'])
        return D(ledger['facts'][key]['yuan'])
    def value(expr):
        if isinstance(expr,str):return fact(expr)
        if isinstance(expr,dict):
            den=value(expr['den'])
            if not den:raise ValueError('DOSSIER_VECTOR_RATIO_ZERO_DENOMINATOR')
            return value(expr['num'])/den*100
        return sum((D(str(c))*fact(k) for k,c in expr),D(0))
    return value
def check_exhibit_values(root,ledger):
    grammar=root.get('data-editorial-grammar');value=_resolver(root,ledger);count=0
    def need(ok,why):
        if not ok:raise ValueError('DOSSIER_VECTOR_'+why)
    def q1(x):return D(x).quantize(D('0.1'),rounding='ROUND_HALF_UP')
    if grammar=='SOURCE_KPI_BOARD_V1':
        texts=list(root.iter(N+'text'))
        for i,t in enumerate(texts):
            if t.get('data-exact-value') is None:continue
            cur=value(json.loads(t.get('data-source-reference')));need(D(t.get('data-exact-value'))==cur,'KPI_VALUE')
            nxt=texts[i+1];prior=value(json.loads(nxt.get('data-prior-reference')));need(D(nxt.get('data-exact-prior'))==prior,'KPI_PRIOR')
            label=nxt.get('data-delta-label')
            need(label in ('同比','较年初','较上期','较上年末'),'KPI_DELTA_LABEL')
            if t.get('data-kpi-kind')=='money':
                want=f'{label} {q1((cur/prior-1)*100):+}%' if prior>0 else '上期≤0，不计增速'
            else:want=f'{label} {q1(cur-prior):+}pp'
            need(nxt.text==want,'KPI_DELTA_TEXT');count+=2
    elif grammar=='SOURCE_RATIO_DUMBBELL_V1':
        for c in root.iter(N+'circle'):
            if c.get('data-ratio-role'):need(D(c.get('data-exact-percent-value'))==value(json.loads(c.get('data-ratio-reference'))),'RATIO_VALUE');count+=1
    elif grammar in ('SOURCE_GROWTH_BARS_V1','SOURCE_STOCK_DELTA_V1','SOURCE_PERIOD_COLUMNS_V1'):
        for r in root.iter(N+'rect'):
            if r.get('data-value-reference') is None:continue
            need(D(r.get('data-exact-value'))==value(json.loads(r.get('data-value-reference'))),'EXHIBIT_VALUE')
            if r.get('data-prior-reference') is not None:need(D(r.get('data-exact-prior'))==value(json.loads(r.get('data-prior-reference'))),'EXHIBIT_PRIOR')
            count+=1
    need(count>0,'NO_ORIGINAL_FACT_VALUES')
    return {'original_source_vector_values':'PASS','observed_values':count}
def check_vector_source(markup,ledger):
    root=ET.fromstring(markup);f=ledger['facts'];count=0
    if root.get('data-editorial-grammar') in EXHIBIT_GRAMMARS:
        if root.get('data-issuer')!=ledger['issuer']['code']:raise ValueError('DOSSIER_VECTOR_WRONG_ISSUER')
        return check_exhibit_values(root,ledger)
    if root.get('data-chart-grammar')=='FULL_PROFIT_CHAIN_V1':
        from profit_chain_audit import check_svg,key_for
        return check_svg(markup,key_for(ledger['issuer']['code'],ledger['issuer']['fiscal_period']),ledger['source']['original_bytes_sha256'])
    if root.get('data-issuer')!=ledger['issuer']['code']:raise ValueError('DOSSIER_VECTOR_WRONG_ISSUER')
    for node in root.iter():
        ref=node.get('data-source-reference')
        if ref:
            expr=json.loads(ref) if ref.startswith(('[','{')) else ref
            if node.get('data-stock-role'):
                expr=expr[node.get('data-stock-role')];observed=node.get('data-exact-yuan')
            elif node.get('data-comparison-pair') is not None:
                i=expr['periods'].index(node.get('data-period'));expr=expr['prior' if i==0 else 'current'];observed=node.get('data-exact-value')
                # Reader-facing labels (e.g. 2026年前三季度) map to ledger period codes
                # only through the ledger's own declared `period_names`; unknown labels
                # are compared literally, so a mislabelled column still fails.
                names={v:k for k,v in ledger['issuer'].get('period_names',{}).items()}
                wanted=names.get(node.get('data-period'),node.get('data-period'))
                for key in ([expr] if isinstance(expr,str) else [k for k,c in expr]):
                    if f[key]['period']!=wanted:raise ValueError('DOSSIER_VECTOR_COMPARISON_WRONG_PERIOD')
            else:observed=node.get('data-signed-yuan') or node.get('data-exact-yuan') or node.get('data-exact-value')
            if observed is not None:
                if D(observed)!=expected(ledger,expr):raise ValueError('DOSSIER_VECTOR_SOURCE_AMOUNT_FALSE')
                count+=1
    if root.get('data-chart-grammar')=='SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY':
        for node in root.iter(N+'rect'):
            key=node.get('data-node-id');raw=node.get('data-node-yuan')
            if raw is None:continue
            if key in f:want=D(f[key]['yuan'])
            elif key=='revenue-total':want=D(f['rev']['yuan'])
            elif key=='group_cogs':want=D(f['cogs']['yuan'])
            elif key=='group_gp':want=D(f['rev']['yuan'])-D(f['cogs']['yuan'])
            else:raise ValueError('DOSSIER_VECTOR_UNKNOWN_INCOME_NODE '+str(key))
            if D(raw)!=want:raise ValueError('DOSSIER_VECTOR_INCOME_SOURCE_FALSE')
            count+=1
    if not count:raise ValueError('DOSSIER_VECTOR_NO_ORIGINAL_FACT_VALUES')
    return {'original_source_vector_values':'PASS','observed_values':count}
