"""Independent original-fact checks for shared industrial sector figures."""
from decimal import Decimal as D
import xml.etree.ElementTree as ET
from editorial_geometry import check_editorial_svg
NS='{http://www.w3.org/2000/svg}'

def check_sector_svg(markup,family,ledger):
    identity=ledger['issuer'];facts=ledger['facts'];v=lambda k:D(facts[k]['yuan'])
    result=check_editorial_svg(markup,issuer=identity['code'],pdf_sha256=ledger['source']['original_bytes_sha256'])
    root=ET.fromstring(markup)
    def require(test,reason):
        if not test:raise ValueError('SECTOR_SOURCE_'+family+'_'+reason)
    signed=[D(r.get('data-signed-yuan')) for r in root.iter(NS+'rect') if r.get('data-signed-yuan') is not None]
    if family=='pnl':
        expected=[v('rev')-v('cogs'),-v('tax_surcharge'),-v('selling')-v('admin'),-v('rd_expense'),-v('finance'),v('other_income')+v('investment_income'),v('fair_value'),v('credit_impairment')+v('asset_impairment')+v('asset_disposal'),v('nonop_income')-v('nonop_expense'),-v('income_tax'),-v('nci'),v('parent_net')]
        require(signed==expected,'FULL_SIGNED_PNL')
    elif family=='cfo':require(signed==[v('net_profit')]+[v(k) for k in ledger['cfo_adjustments']]+[v('cfo')],'ALL_INDIRECT_SOURCE_ROWS')
    elif family=='cash':require(signed==[v(k) for k in ('cash_start','cfo','cfi','cff','fx_cash','cash_end')],'CASH_CLOSE')
    elif family=='capital':
        require(signed==[v('cfo'),-v('cash_capex'),v('cfo')-v('cash_capex')],'EXACT_CASH_CAPEX_FCF')
        other=[D(t.get('data-exact-value')) for t in root.iter(NS+'text') if t.get('data-exact-value') is not None]
        expected=[v('dividend_interest_cash')]+([v('bill_endorse_capex')] if 'bill_endorse_capex' in facts else [])
        require(other==expected,'DISTRIBUTION_AND_NONCASH_SEPARATE')
    elif family=='balance':
        values=[D(r.get('data-exact-yuan')) for r in root.iter(NS+'rect') if r.get('data-stock-role')]
        require(values==[v(k) for k in ('assets_prior','liabilities_prior','equity_prior','assets','liabilities','total_equity')],'TWO_DATES')
    elif family=='trend':
        values=[D(r.get('data-exact-value')) for r in root.iter(NS+'rect') if r.get('data-comparison-pair') is not None]
        require(values==[v('rev_prior'),v('rev'),v('rev_prior')-v('cogs_prior'),v('rev')-v('cogs'),v('cfo_prior'),v('cfo')],'TWO_PERIOD_FACTS')
    elif family=='sector':
        if 'power_gen_100m_kwh' in facts:
            values=[D(t.get('data-exact-value')) for t in root.iter(NS+'text') if t.get('data-exact-value') is not None]
            require(values==[v('power_gen_100m_kwh'),v('rev'),v('cfo')],'POWER_REVENUE_CASH_SEPARATE')
            physical=next(t for t in root.iter(NS+'text') if 'power_gen_100m_kwh' in t.get('data-source-reference',''))
            require(physical.get('data-unit')=='亿千瓦时','PHYSICAL_UNIT')
        else:
            values=[D(r.get('data-exact-yuan')) for r in root.iter(NS+'rect') if r.get('data-exact-yuan') is not None]
            innovation=v('innovative_drug_sales_100m')*D(100000000)
            require(values==[v('drug_sales_rev'),v('licence_rev'),v('other_rev'),innovation,v('drug_sales_rev')-innovation],'CONTRACT_NESTED_SUBSET')
            groups=[g for g in root.iter(NS+'g') if g.get('data-editorial-grammar')=='SOURCE_NONNEGATIVE_COMPONENTS_V1']
            require(len(groups)==2 and all(D(g.get('data-reference-total-yuan'))==v('rev') for g in groups),'SHARED_REVENUE_SCALE')
            metrics=[D(t.get('data-exact-value')) for t in root.iter(NS+'text') if t.get('data-exact-value') is not None]
            require(metrics==[v('rpo')] and facts['rpo']['type']=='stock','RPO_NOT_REVENUE')
    else:raise ValueError('UNSUPPORTED_SECTOR_FAMILY '+family)
    return {'family':family,'original_fact_amounts':'PASS',**result}
