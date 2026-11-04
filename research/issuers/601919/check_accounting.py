#!/usr/bin/env python3
"""COSCO Shipping 601919 2026H1 original source CAS and shipping-cycle invariants.

Precise RMB yuan, mixed original unit/period/ownership, consolidated direct AND
real disclosed indirect CFO. This script does not certify all notes or design.
"""
from decimal import Decimal, InvalidOperation
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/"research/issuers/601919"
LEDGER=json.loads((HERE/"source-ledger.json").read_text(encoding="utf-8"))
FACTS=LEDGER["facts"]
CENT=Decimal("0.01")
EQUATIONS=[]
CFO_ADJUSTMENTS=[
"indirect_asset_impair","indirect_credit_impair","indirect_depr_fixed",
"indirect_amort_right_of_use","indirect_amort_intangible","indirect_amort_longterm",
"indirect_disposal","indirect_scrapping","indirect_fairvalue","indirect_finance",
"indirect_invest","indirect_dta","indirect_dtl","indirect_inventory",
"indirect_receivable","indirect_payable"
]

def value(k,facts=None):
    x=(facts if facts is not None else FACTS)[k]
    try: n=Decimal(x["exact_value"])
    except (InvalidOperation,TypeError):raise AssertionError("NON_NUMERIC_OR_GUESSED_ORIGINAL_"+k)
    assert n.is_finite(),"NOT_FINITE_"+k
    if x["source_report_unit"] in ("CNY_yuan",):
        assert n==n.quantize(CENT),"ORIGINAL_YUAN_PRECISION_"+k
    if x["source_report_unit"] in ("TEU", "RMB_thousands"):
        assert n==n.to_integral_value(),"ORIGINAL_INTEGER_UNIT_"+k
    return n

def check(facts=None):
    F=FACTS if facts is None else facts
    checks={}
    def v(k):return value(k,F)
    def tot(*keys):return sum((v(k) for k in keys),Decimal(0))
    def eq(name,actual,expected):
        assert actual==expected,f"{name}: {actual} != {expected}"
        checks[name]="PASS"
    def cross(name,raw,scope,unit,page,period=None):
        f=F[raw]
        assert f["scope"]==scope and f["source_report_unit"]==unit and f["physical_page"]==page,(name,"SCOPE_UNIT_PAGE",f)
        if period is not None:assert f["period"]==period,(name,"PERIOD_COLUMN",f["period"])
        checks[name]="PASS"

    assert LEDGER["issuer"]=="601919" and LEDGER["period"]=="2026H1","WRONG_ISSUER_OR_PERIOD"
    assert LEDGER["source"]["sha256"]=="0265a4ca61fb24ff15e14b53b258d7febc03bdb7349f379e42e2c28476dd2ff1","SOURCE_ORIGINAL_SHA_DRIFT"
    assert len(F)>=140,"SHORT_ORIGINAL_SOURCE_LEDGER"
    for k,f in F.items():
        assert 1<=f["physical_page"]<=178,("INVALID_PHYSICAL_PAGE",k)
        assert f["period"] in ("2026H1","2025H1","2026-06-30","2025-12-31"),("INVALID_REPORT_PERIOD",k)
        assert f["source_report_unit"] in ("CNY_yuan","TEU","RMB_thousands","percent","USD_per_TEU"),("UNKNOWN_UNIT",k)
        value(k,F)
    checks["ALL_SOURCE_FACTS_HAVE_REAL_NUMBER_PHYSICAL_PAGE_PERIOD_AND_EXPLICIT_UNIT"]="PASS"

    # Full statutory consolidated income, both signed periods.
    for suffix in ("","_prior"):
        def p(k):return k+suffix
        eq("CAS_COST_SIX_LINES"+suffix,tot(*map(p,("cost","taxes_and_surcharges","selling_expense","admin_expense","rd_expense","finance_expense"))),v(p("operating_total_cost")))
        eq("CAS_STATUTORY_OPERATING_PROFIT"+suffix,v(p("revenue"))-v(p("operating_total_cost"))+tot(*map(p,("other_income","investment_income","fairvalue_income","credit_impairment","asset_impairment","asset_disposal_gain"))),v(p("operating_profit")))
        eq("CAS_PRETAX"+suffix,v(p("operating_profit"))+v(p("nonoperating_income"))-v(p("nonoperating_expense")),v(p("pretax_profit")))
        eq("CAS_NET"+suffix,v(p("pretax_profit"))-v(p("income_tax")),v(p("net_profit")))
        eq("CAS_PARENT_AND_MINORITIES"+suffix,tot(p("parent_profit"),p("minority_profit")),v(p("net_profit")))
        eq("CAS_ALL_COMPREHENSIVE"+suffix,tot(p("net_profit"),p("oci_total")),v(p("comprehensive_income")))
        eq("CONSOLIDATED_TOTAL_BALANCE"+suffix,tot(p("liabilities"),p("equity")),v(p("assets")))
        eq("EQUITY_PARENT_MINORITIES"+suffix,tot(p("parent_equity"),p("minority_equity")),v(p("equity")))
        eq("CASH_DIRECT_RECEIPTS"+suffix,tot(*map(p,("cash_from_customers","tax_refunds","other_operating_receipts"))),v(p("cfo_inflows")))
        eq("CASH_DIRECT_PAYMENTS"+suffix,tot(*map(p,("paid_suppliers","paid_staff","paid_taxes","paid_operating_other"))),v(p("cfo_outflows")))
        eq("CASH_DIRECT_CFO"+suffix,v(p("cfo_inflows"))-v(p("cfo_outflows")),v(p("cfo")))
        eq("CASH_BEGIN_TO_END"+suffix,tot(*map(p,("cash_begin","cfo","cfi","cff","fx_cash_effect"))),v(p("cash_end")))
        cross("BALANCE_STOCK_PERIOD"+suffix,p("assets"),"consolidated","CNY_yuan",52,"2025-12-31" if suffix else "2026-06-30")
        cross("CONSOLIDATED_INCOME_PERIOD"+suffix,p("revenue"),"consolidated","CNY_yuan",55,"2025H1" if suffix else "2026H1")
    # Specific shipping model: gross segment vs eliminations and gross profit.
    eq("GROSS_SHIPPING_COST_TRUE_FOUR_CATEGORY",tot("ship_cost_equipment","ship_cost_voyage","ship_cost_vessel","ship_cost_other"),v("ship_segment_cost"))
    eq("PRIOR_SHIPPING_COST_ORIGINAL_FOUR_CATEGORIES",tot("ship_cost_equipment_prior","ship_cost_voyage_prior","ship_cost_vessel_prior","ship_cost_other_prior"),v("ship_segment_cost_prior"))
    eq("PRIOR_GROUP_COGS_SIGNED_REAL_INTERCOMPANY_ELIMINATION",tot("ship_segment_cost_prior","port_segment_cost_prior","intersegment_cost_elimination_prior"),v("cost_prior"))
    lanes=("transpacific","europe_med","asia_oceania","other_international","china_mainland")
    for suffix in ("","_prior"):
        eq("FIVE_EXCLUSIVE_ROUTES_REVENUE_RMB_THOUSANDS"+suffix,
            tot(*("lane_revenue_rmb_thousands_"+x+suffix for x in lanes)),
            v("lane_revenue_total_rmb_thousands"+suffix))
        eq("FIVE_EXCLUSIVE_ROUTES_FREIGHT_TEU"+suffix,
            tot(*("lane_teu_"+x+suffix for x in lanes)),
            v("group_teu"+suffix))
        cross("LANES_FREIGHT_REVENUE_UNIT_AND_SCOPE"+suffix,"lane_revenue_rmb_thousands_transpacific"+suffix,"group_lanes","RMB_thousands",14,"2025H1" if suffix else "2026H1")
        cross("LANES_TEUS_UNIT_AND_SCOPE"+suffix,"lane_teu_transpacific"+suffix,"group_volume","TEU",13,"2025H1" if suffix else "2026H1")
    assert v("lane_revenue_total_rmb_thousands")*1000<v("ship_segment_revenue"),"FREIGHT_ROUTE_REVENUE_NOT_ALL_SHIPPING_SERVICES"
    checks["ROUTE_TEU_AND_FREIGHT_RMB_THOUSANDS_ARE_NOT_1000X_USD_PER_TEU"]="PASS"
    eq("GROSS_TWO_SEGMENTS_MINUS_INTERCOMPANY_TO_GROUP_REVENUE",tot("ship_segment_revenue","port_segment_revenue","intersegment_revenue_elimination"),v("revenue"))
    eq("GROSS_TWO_SEGMENTS_MINUS_INTERCOMPANY_TO_GROUP_COST",tot("ship_segment_cost","port_segment_cost","intersegment_cost_elimination"),v("cost"))
    assert v("intersegment_revenue_elimination")<0 and v("intersegment_cost_elimination")<0,"NEGATIVE_ELIMINATION_NOT_SIGNED"
    checks["NEVER_TREAT_NEGATIVE_SEGMENT_ELIMINATION_AS_POSITIVE_SANKEY_BUSINESS"]="PASS"
    assert v("ship_segment_revenue")>v("ship_segment_cost") and v("port_segment_revenue")>v("port_segment_cost"),"SEGMENT_EARNINGS_NOT_CHECKED"
    checks["UNMIXED_PRE_ELIMINATION_SEGMENT_GROSS_PROFIT"]="PASS"
    assert F["ship_supply_chain_revenue_rmb_thousands"]["classification"]=="DISCLOSED_SUBSET_DO_NOT_ADD","SUPPLY_CHAIN_DOUBLE_COUNTED_AS_EXTRA_SEGMENT_REVENUE"
    assert v("ship_supply_chain_revenue_rmb_thousands")*1000<v("ship_segment_revenue"),"SHIP_SUPPLY_CHAIN_INCLUDED_NOT_EXTRA"
    cross("RMB_THOUSAND_SHIPPING_SUBSET_SOURCE","ship_supply_chain_revenue_rmb_thousands","management_shipping","RMB_thousands",15)
    cross("USD_PER_TEU_INDEPENDENT_OF_RMB_REVENUE","international_yield_usd_per_teu","management_shipping","USD_per_TEU",15)
    eq("CONTROLLED_PLUS_ASSOCIATED_TERMINAL_TEU",tot("port_controlling_teu","port_participating_teu"),v("port_teu"))
    cross("PORT_VOLUME_NON_CONSOLIDATED_SCOPE","port_teu","management_port_volume","TEU",16)
    assert v("group_teu")!=v("port_teu"),"SHIPPING_AND_PORT_VOLUME_CONFUSED"
    checks["SHIP_FREIGHT_TEU_NOT_TERMINAL_HANDLED_TEU"]="PASS"
    # True disclosed net-profit->CFO p148, not an invented indirect flow.
    eq("INDIRECT_NET_PROFIT_TO_OPERATING_CFO",v("net_profit")+tot(*CFO_ADJUSTMENTS),v("cfo"))
    cross("P148_ORIGINAL_INDIRECT_CFO_BRIDGE","indirect_receivable","consolidated","CNY_yuan",148)
    eq("RESTRICTED_CASH_BALANCE_VS_CASH_EQUIVALENTS",v("cash_on_bs")-v("cash_end"),v("restricted_non_cash_funds"))
    cross("P167_UNFUNDED_VESSEL_NEWBUILDS_ARE_STOCK_NOT_CASH","capital_commit_shipbuilding","contract_commitment","CNY_yuan",167,"2026-06-30")
    cross("P167_SIGNED_FUTURE_LEASES_NOT_CURRENT_CFO","signed_lease_commitment","lease_commitment","CNY_yuan",167,"2026-06-30")
    assert v("capital_commit_shipbuilding")!=v("capex_cash"),"FUTURE_COMMITMENT_EQUALS_H1_PAID_CAPEX_FALSELY"
    checks["UNFUNDED_VESSEL_NEWBUILD_COMMITMENT_NOT_H1_CASH_CAPEX"]="PASS"
    # Currencies/financial statement units and periods deliberately cannot mix.
    assert F["international_yield_usd_per_teu"]["source_report_unit"]!="CNY_yuan","CURRENCY_RATE_UNIT_CONFUSION"
    checks["UNIT_SCOPE_AND_CURRENCY_GATES"]="PASS"
    return checks

def source_pdf_bytes():
    p=ROOT/LEDGER["source"]["path"]
    assert p.is_file() and p.read_bytes()[:4]==b"%PDF","REAL_ORIGINAL_PDF_MISSING"
    assert hashlib.sha256(p.read_bytes()).hexdigest()==LEDGER["source"]["sha256"],"ORIGINAL_BINARY_SHA_CHANGED"
    assert p.stat().st_size==LEDGER["source"]["bytes"],"ORIGINAL_BINARY_BYTES_CHANGED"
    return p

if __name__=="__main__":
    source_pdf_bytes()
    output={"source_sha256":LEDGER["source"]["sha256"],"code":"601919","research_status":"ORIGINAL_SOURCE_AND_ACCOUNTING_ONLY_NOT_AN_OFFLINE_HTML","checks":check(),"limits":{"all_material_notes_independent_review":"NOT_CHECKED","full_cell_xy_independent":"NOT_CHECKED","sector_peers":"NOT_CHECKED","independent_human":"NOT_CHECKED","cloudflare":"NOT_CHECKED"}}
    (HERE/"source-accounting-qa.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n")
    print("SHIPPING_CAS_SEGMENT_ELIMINATIONS_INDIRECT_CFO_CASH_SOURCE_PASS",len(output["checks"]),output["source_sha256"])
