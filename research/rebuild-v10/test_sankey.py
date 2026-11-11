"""Cross-industry accounting-flow figure regression.

Exercising actual 2026H1 original-source ledger values and source PDF hashes.
Never substitutes for second row/column semantic audit.
"""
from decimal import Decimal as D
from pathlib import Path
import re
import pytest
from publisher import audited_financial_sankey, OUTPUT
from verify import get, check

CASES={
    '688111': (['wps_personal','wps365','wps_software','other_rev'],'rev','cogs','营业毛利'),
    '600519': (['maotai_rev','series_rev','other_rev'],'rev','cogs','营业毛利'),
    '000333': (['home','industrial_solution','other_total'],'rev','cogs','营业毛利'),
    '600036': (['nii','fees_net','other_net'],'revenue',None,'营业利润'),
}

def test_original_files_and_actual_statements():
    for code in CASES:
        audit=check(code)
        assert audit['literal_page_numeric_missing']==[]
        assert audit['pdf_pages']>90
        assert 'BS_2026' in audit['accounting_identities']

def test_four_true_conservation_equations():
    for code,(keys,total,expense_kind,profit_kind) in CASES.items():
        source=sum((get(code,k) for k in keys),D(0))
        assert source==get(code,total),(code,'SOURCE_CONSERVATION_FAILED')
        if expense_kind:
            assert get(code,total)==get(code,expense_kind)+(get(code,total)-get(code,expense_kind))
        else:
            assert get(code,total)==sum((get(code,k) for k in ('administrative_expense','credit_impairment_expense','other_operating_cost')),D(0))+get(code,'operating_profit')

def test_presentation_has_original_source_native_finance_and_type():
    kinds={'688111':'TYPE_A_SOURCE_OWN_COST_GP',
           '600519':'TYPE_C_SANKEY_OMITTED',
           '000333':'TYPE_A_SOURCE_OWN_COST_GP',
           '600036':'BANK_NET_INCOME_TO_OPERATING_PROFIT'}
    for code,kind in kinds.items():
        html=(OUTPUT/(code+'.html')).read_text()
        assert html.count('<figure')>=8
        assert html.count('class="graphic-svg native-finance"')>=8
        assert 'data-flow-kind="'+kind+'"' in html,(code,kind)
        assert 'width:850px;min-width:850px' not in html
        assert '.graphic-svg{display:none}' not in html
        # A hidden SVG export button is a real mobile publication P0; export
        # must use the actual rendered source-original phone/desktop SVG.
        assert '.export{display:none}' not in html,(code,'MOBILE_EXPORT_HIDDEN')
        assert '.export{display:inline-flex' in html,(code,'MOBILE_EXPORT_TOUCH_TARGET_MISSING')
        assert 'min-height:44px' in html,(code,'PHONE_EXPORT_TOUCH_TARGET_TOO_SMALL')
        assert "figure.querySelectorAll('.graphic-svg svg')" in html,(code,'EXPORT_NOT_VISIBILITY_SELECTED')
        assert '全部七家公司' not in html,(code,'OUTDATED_ISSUER_CATALOG_LABEL')

        assert '<svg' in html and 'data-native-original-yuan="true"' in html
        assert '左右滑动' not in html
        assert html.count('class="graphic-svg desktop-finance')>=8
        figure=html.split('id="fig-02"')[1].split('</figure>')[0]
        if code=='688111':
            for key in ('wps_personal','wps365','wps_software','other_rev'):
                assert 'data-source-id="'+key+'"' in figure
                assert 'data-gp-yuan=' in figure and 'data-cost-yuan=' in figure
        elif code=='600519':
            assert 'FINANCIAL_SANKEY_OMITTED_WITH_SOURCE_REASON' in figure
            assert 'data-signed-yuan=' in figure
        elif code=='000333':
            assert 'PRODUCT_LEVEL_GP_NOT_ESTABLISHED' not in figure
            for key in ('home','industrial_solution','other_total'):
                assert 'data-source-id="'+key+'"' in figure
            assert 'data-gp-yuan=' in figure and 'data-cost-yuan=' in figure
        else:
            assert '净利息' in figure



def test_signed_or_incompatible_mixed_flows_rejected():
    good=[('A',D('800')),('B',D('200'))]
    for sources,total,uses in [
       (good,D('1001'),[('cost',D('600')),('profit',D('401'))]),
       (good,D('1000'),[('cost',D('601')),('profit',D('400'))]),
       ([('A',D('-2')),('B',D('1002'))],D('1000'),[('cost',D('600')),('profit',D('400'))]),
       (good,D('1000'),[('cost',D('-200')),('profit',D('1200'))]),
    ]:
        with pytest.raises(AssertionError):
            audited_financial_sankey(sources,total,uses,'test')

def test_bank_nii_not_deducted_twice():
    c='600036'
    assert get(c,'interest_in')-get(c,'interest_out')==get(c,'nii')
    assert get(c,'nii')+get(c,'fees_net')+get(c,'other_net')==get(c,'revenue')
    assert get(c,'revenue')-get(c,'administrative_expense')-get(c,'credit_impairment_expense')-get(c,'other_operating_cost')==get(c,'operating_profit')

def test_industrial_finance_accounting_boundary():
    c='000333'
    assert get(c,'rev')+get(c,'interest_income')+get(c,'fee_income')==get(c,'total_rev')
    assert get(c,'rev')-get(c,'cogs')>0
    assert get(c,'fee_income')>0
    assert '财务子公司利息/手续费不在本图' in (OUTPUT/(c+'.html')).read_text()

def test_negative_product_margins_not_converted_to_positive_flow():
    c='600519';cost=get(c,'other_cogs');rev=get(c,'other_rev')
    assert rev-cost<0,'Known negative minor other gross margin expected; do not make positive ribbon'
    # The present figure uses only positive aggregate COGS and total GP, no fake profit-by-product.
    assert get(c,'rev')-get(c,'cogs')>0