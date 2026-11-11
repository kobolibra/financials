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

def check_signed_svg(markup,family,ledger):
    root=ET.fromstring(markup); facts=ledger['facts']
    def require(test,why):
        if not test:raise ValueError(family+':'+why)
    require(root.get('data-chart-grammar')=='INSURANCE_SIGNED_CUMULATIVE_BRIDGE','GRAMMAR')
    require(root.get('data-original-pdf-sha256')==ledger['source']['original_bytes_sha256'],'PDF_SHA')
    require(root.get('data-layout')=='native-330' and root.get('data-accounting-scope')=='consolidated','SCOPE_LAYOUT')
    require(root.get('data-period')==('2025H1_TO_2026H1' if family=='delta' else '2026H1'),'PERIOD')
    expected=expected_steps(family,facts)
    bars=[r for r in root.iter(NS+'rect') if r.get('data-signed-yuan') is not None]
    require(len(bars)==len(expected),'COMPLETE_SOURCE_STAGE_COUNT')
    lo=min([D(0)]+[min(z[3],z[4]) for z in expected]);hi=max([D(0)]+[max(z[3],z[4]) for z in expected]);scale=(hi-lo)/D(298)
    for i,(bar,(value,source,total,before,after)) in enumerate(zip(bars,expected)):
        require(D(bar.get('data-signed-yuan'))==value,'SOURCE_YUAN_'+str(i))
        require(D(bar.get('data-before-yuan'))==before and D(bar.get('data-after-yuan'))==after,'CUMULATIVE_OR_SUBTOTAL_'+str(i))
        require(bar.get('data-checkpoint')==str(total).lower(),'SUBTOTAL_NOT_ADDITIVE_'+str(i))
        keys=set(bar.get('data-source-fact-ids','').split(','))
        require(source==keys and keys<=set(facts),'SOURCE_IDS_'+str(i))
        require(D(bar.get('data-money-scale-yuan-per-unit'))==scale,'EXACT_YUAN_SCALE_'+str(i))
        require(abs(D(bar.get('width'))-abs(after-before)/scale)<D('.00011'),'ACTUAL_WIDTH_'+str(i))
        require(abs(D(bar.get('x'))-(D(16)+(min(before,after)-lo)/scale))<D('.00011'),'ACTUAL_CUMULATIVE_POSITION_'+str(i))
        color='#263F47' if i==0 or total else '#CD7271' if value<0 else '#239878'
        require(bar.get('fill').upper()==color,'SIGN_COLOR_'+str(i))
    return {'family':family,'stage_count':len(bars),'source_signed_yuan':'PASS','cumulative_and_nonadditive_checkpoints':'PASS','source_ids':'PASS','negative_cost_color':'PASS','actual_vector_x_width_proportional':'PASS','original_pdf_sha':'PASS'}
