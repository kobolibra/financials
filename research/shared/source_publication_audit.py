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
def check_vector_source(markup,ledger):
    root=ET.fromstring(markup);f=ledger['facts'];count=0
    if root.get('data-chart-grammar')=='FULL_PROFIT_CHAIN_V1':
        from profit_chain_audit import check_svg
        return check_svg(markup,ledger['issuer']['code'],ledger['source']['original_bytes_sha256'])
    if root.get('data-issuer')!=ledger['issuer']['code']:raise ValueError('DOSSIER_VECTOR_WRONG_ISSUER')
    for node in root.iter():
        ref=node.get('data-source-reference')
        if ref:
            expr=json.loads(ref) if ref.startswith(('[','{')) else ref
            if node.get('data-stock-role'):
                expr=expr[node.get('data-stock-role')];observed=node.get('data-exact-yuan')
            elif node.get('data-comparison-pair') is not None:
                i=expr['periods'].index(node.get('data-period'));expr=expr['prior' if i==0 else 'current'];observed=node.get('data-exact-value')
                for key in ([expr] if isinstance(expr,str) else [k for k,c in expr]):
                    if f[key]['period']!=node.get('data-period'):raise ValueError('DOSSIER_VECTOR_COMPARISON_WRONG_PERIOD')
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
