"""Independent insurer source-to-rendered-SVG bridge audit; no publisher imports."""
from decimal import Decimal as D
import xml.etree.ElementTree as ET

FAMILIES={'insurance','pnl','delta','cash','cashclose'}
NS='{http://www.w3.org/2000/svg}'

def expected_steps(family,facts):
    v=lambda key:D(facts[key]['yuan'])
    def raw(key):return (v(key),{key})
    def summed(keys):return (sum((v(k) for k in keys),D(0)),set(keys))
    service=['service_revenue','service_cost','reinsurance_premium','reinsurance_recovered']
    if family=='insurance':rows=[raw(k) for k in service]+[summed(service)]; totals={4}
    elif family=='pnl':
        others=['other_income','fx_income','other_business_income','disposal_income','reinsurance_finance','interest_expense','commission_expense','tax_surcharge','administrative_expense','credit_impair','other_asset_impair','other_business_cost']
        rows=[summed(service)]+[raw(k) for k in ['interest_income','investment_income','fairvalue_income','insurance_finance']]+[summed(others),raw('op_profit'),summed(['nonoperating_income','nonoperating_expense']),raw('income_tax'),(-v('nci_profit'),{'nci_profit'}),raw('parent_net')];totals={6,10}
    elif family=='delta':
        lead=['fairvalue_income','investment_income','insurance_finance','service_revenue','service_cost','interest_income']
        allkeys=['service_revenue','interest_income','investment_income','other_income','fairvalue_income','fx_income','other_business_income','disposal_income','service_cost','reinsurance_premium','reinsurance_recovered','insurance_finance','reinsurance_finance','interest_expense','commission_expense','tax_surcharge','administrative_expense','credit_impair','other_asset_impair','other_business_cost']
        diff=lambda keys:(sum((v(k)-v(k+'_prior') for k in keys),D(0)),set(keys)|{k+'_prior' for k in keys})
        rows=[raw('op_profit_prior')]+[diff([k]) for k in lead]+[diff([k for k in allkeys if k not in lead]),raw('op_profit')];totals={8}
    elif family=='cash':rows=[raw(k) for k in ['cfo_in','cfo_claims','cfo_commission','cfo_staff','cfo_tax','cfo_loans','cfo_other_out','cfo']];totals={7}
    elif family=='cashclose':rows=[raw(k) for k in ['cash_start','cfo','cfi','cff','cash_fx','cash_end']];totals={5}
    else:raise ValueError('UNSUPPORTED_INSURANCE_BRIDGE '+family)
    running=D(0);out=[]
    for index,(value,sources) in enumerate(rows):
        total=index in totals
        if total:
            if running!=value:raise ValueError('SOURCE_CHECKPOINT_NOT_RECONCILED')
            before,after=D(0),running
        else:before=running;running+=value;after=running
        out.append((value,sources,total,before,after))
    return out

def check_signed_svg(markup,family,ledger,mobile=True):
    root=ET.fromstring(markup); facts=ledger['facts']
    def require(test,why):
        if not test:raise ValueError(family+':'+why)
    require(root.get('data-chart-grammar')=='INSURANCE_SIGNED_CUMULATIVE_BRIDGE','GRAMMAR')
    require(root.get('data-original-pdf-sha256')==ledger['source']['original_bytes_sha256'],'PDF_SHA')
    require(root.get('data-layout')==('native-330' if mobile else 'editorial-1040') and root.get('data-accounting-scope')=='consolidated','SCOPE_LAYOUT')
    require(root.get('data-period')==('2025H1_TO_2026H1' if family=='delta' else '2026H1'),'PERIOD')
    expected=expected_steps(family,facts)
    bars=[r for r in root.iter(NS+'rect') if r.get('data-signed-yuan') is not None]
    require(len(bars)==len(expected),'COMPLETE_SOURCE_STAGE_COUNT')
    lo=min([D(0)]+[min(z[3],z[4]) for z in expected]);hi=max([D(0)]+[max(z[3],z[4]) for z in expected]);left=D(16) if mobile else D(330);span=D(298) if mobile else D(460);scale=(hi-lo)/span
    for i,(bar,(value,source,total,before,after)) in enumerate(zip(bars,expected)):
        require(D(bar.get('data-signed-yuan'))==value,'SOURCE_YUAN_'+str(i))
        require(D(bar.get('data-before-yuan'))==before and D(bar.get('data-after-yuan'))==after,'CUMULATIVE_OR_SUBTOTAL_'+str(i))
        require(bar.get('data-checkpoint')==str(total).lower(),'SUBTOTAL_NOT_ADDITIVE_'+str(i))
        keys=set(bar.get('data-source-fact-ids','').split(','))
        require(source==keys and keys<=set(facts),'SOURCE_IDS_'+str(i))
        require(D(bar.get('data-money-scale-yuan-per-unit'))==scale,'EXACT_YUAN_SCALE_'+str(i))
        require(abs(D(bar.get('width'))-abs(after-before)/scale)<D('.00011'),'ACTUAL_WIDTH_'+str(i))
        require(abs(D(bar.get('x'))-(left+(min(before,after)-lo)/scale))<D('.00011'),'ACTUAL_CUMULATIVE_POSITION_'+str(i))
        color='#263F47' if i==0 or total else '#CD7271' if value<0 else '#239878'
        require(bar.get('fill').upper()==color,'SIGN_COLOR_'+str(i))
    return {'family':family,'stage_count':len(bars),'source_signed_yuan':'PASS','cumulative_and_nonadditive_checkpoints':'PASS','source_ids':'PASS','negative_cost_color':'PASS','actual_vector_x_width_proportional':'PASS','original_pdf_sha':'PASS'}

COMMON_FAMILIES={'clocks','service','csm','balance'}

def check_common_insurance_svg(markup,family,ledger):
    """Source-ledger audit independent of publisher and chart adapters."""
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'shared'))
    from editorial_geometry import check_editorial_svg
    checked=check_editorial_svg(markup,issuer=ledger['issuer']['code'],pdf_sha256=ledger['source']['original_bytes_sha256'])
    root=ET.fromstring(markup);facts=ledger['facts'];v=lambda k:D(facts[k]['yuan'])
    def require(test,why):
        if not test:raise ValueError('INSURANCE_COMMON_'+family+'_'+why)
    if family=='clocks':
        values=[D(r.get('data-exact-value')) for r in root.iter(NS+'rect') if r.get('data-comparison-pair') is not None]
        require(values==[v(k) for k in ('premium_prior','premium_total','service_revenue_prior','service_revenue','parent_net_prior','parent_net','cfo_prior','cfo')],'DISTINCT_SOURCE_METRICS')
    elif family in ('service','csm'):
        keys=['service_expected_claims','service_risk_release','service_csm_release','service_acq_amort','service_paa'] if family=='service' else ['future_cash_flow_liab','risk_adjustment_liab','csm','paa_liab']
        bars=[r for r in root.iter(NS+'rect') if r.get('data-exact-yuan') is not None]
        require([D(r.get('data-exact-yuan')) for r in bars]==[v(k) for k in keys],'ORIGINAL_COMPONENTS')
        for bar,key in zip(bars,keys):require(key in bar.get('data-source-reference',''),'SOURCE_FACT_REFERENCE')
        total='service_revenue' if family=='service' else 'insurance_contract_liab'
        require(D(root.get('data-total-yuan'))==v(total),'ORIGINAL_TOTAL')
        require(root.get('data-period')==facts[total]['period'],'FLOW_VS_STOCK_PERIOD')
    elif family=='balance':
        bars=[r for r in root.iter(NS+'rect') if r.get('data-stock-role')]
        values=[D(r.get('data-exact-yuan')) for r in bars]
        require(values==[v('assets_prior'),v('liabilities_prior'),v('parent_equity_prior')+v('minority_equity_prior'),v('assets'),v('liabilities'),v('parent_equity')+v('minority_equity')],'ASSET_AND_COMPLETE_EQUITY')
    else:raise ValueError('UNSUPPORTED_COMMON_INSURANCE_FAMILY '+family)
    return {'family':family,'independent_original_fact_values':'PASS',**checked}
