#!/usr/bin/env python3
"""Verify real 178-page 601919 original PDF row, current-column x/y positions.

--capture locks an original-PDF spatial candidate. Capturing is machine
provenance, NOT an independent human review or fully exhaustive 178-page notes
audit. --verify rejects wrong numbers/pages/columns, mutated captured x/y.
"""

from pathlib import Path
from decimal import Decimal
import argparse,hashlib,json,re
import fitz

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"research/issuers/601919"
LEDGER=json.loads((BASE/"source-ledger.json").read_text())
F=LEDGER["facts"]
SOURCE=json.loads((BASE/"source-verification.json").read_text())
PDF=ROOT/LEDGER["source"]["path"]
SHA="0265a4ca61fb24ff15e14b53b258d7febc03bdb7349f379e42e2c28476dd2ff1"
SELECTED=[
 ("ship_segment_revenue","集装箱航运",12),
 ("port_segment_revenue","码头业务",12),
 ("intersegment_revenue_elimination","分部间抵销",12),
 ("ship_cost_voyage","航程成本",13),
 ("ship_cost_vessel","船舶成本",13),
 ("group_teu","合计",13),
 ("ship_supply_chain_revenue_rmb_thousands","除海运以外的供应链收入",15),
 ("ship_ebit_rmb_thousands","息税前利润",15),
 ("international_yield_usd_per_teu","国际航线单箱收入",15),
 ("port_teu","总计",16),
 ("port_controlling_teu","控股码头",16),
 ("port_participating_teu","参股码头",16),
 ("cash_on_bs","货币资金",51),
 ("ar","应收账款",51),
 ("inventory","存货",51),
 ("assets","资产总计",52),
 ("right_of_use_assets","使用权资产",52),
 ("construction_in_progress","在建工程",51),
 ("liabilities","负债合计",53),
 ("parent_equity","归属于母公司所有者权益",53),
 ("minority_equity","少数股东权益",53),
 ("revenue","营业总收入",55),
 ("cost","营业成本",55),
 ("finance_expense","财务费用",56),
 ("investment_income","投资收益",56),
 ("operating_profit","营业利润",56),
 ("parent_profit","归属于母公司股东的净利",56),
 ("cfo_inflows","经营活动现金流入小计",59),
 ("paid_suppliers","购买商品、接受劳务支付的现金",59),
 ("cfo_outflows","经营活动现金流出小计",59),
 ("cfo","经营活动产生的现金流量净额",59),
 ("capex_cash","购建固定资产",60),
 ("cfi","投资活动产生的现金流量净额",60),
 ("cff","筹资活动产生的现金流量净额",60),
 ("cash_end","期末现金及现金等价物余额",60),
 ("indirect_amort_right_of_use","使用权资产摊销",148),
 ("indirect_depr_fixed","固定资产折旧",148),
 ("indirect_receivable","经营性应收项目的减少",148),
 ("indirect_payable","经营性应付项目的增加",148),
 ("capital_commit_shipbuilding","船舶建造",167),
 ("capital_commit_terminal","码头",167),
 ("signed_lease_commitment","船舶及集装箱等租赁项目",167),
]
def number_for(key):
    x=F[key]
    amt=Decimal(x["exact_value"])
    if x["source_report_unit"] in ("CNY_yuan","USD_per_TEU","percent"):
        return f"{abs(amt):,.2f}"
    if x["source_report_unit"] in ("TEU","RMB_thousands"):
        assert amt==amt.to_integral_value()
        return f"{abs(int(amt)):,}"
    raise AssertionError("UNSUPPORTED_SOURCED_UNIT:"+key)

def find_position(page,key,anchor):
    formatted=number_for(key)
    rects=page.search_for(formatted)
    # Some PyMuPDF fonts split original yuan thousand separators into tokens;
    # if and only if the exact printed value wasn't found, flag the missing
    # source rather than weaken the check to a guessed substring.
    assert rects,(key,"SOURCE_NUMBER_NOT_PRINTED_AT_PHYSICAL_PAGE",page.number+1,formatted)
    anchors=page.search_for(anchor)
    assert anchors,(key,"ORIGINAL_CHINESE_ROW_ANCHOR_MISSING",page.number+1,anchor)
    candidates=[]
    for num in rects:
        for row in anchors:
            dy=abs((num.y0+num.y1)/2-(row.y0+row.y1)/2)
            if dy<=13 and num.x0>row.x0+10:
                candidates.append((dy+max(0,row.x1-num.x0)/20,num,row))
    assert candidates,(key,"ORIGINAL_ROW_AND_AMOUNT_NOT_SAME_PRINTED_Y",page.number+1,formatted,anchor)
    _,n,a=min(candidates,key=lambda x:x[0])
    prior=key+"_prior"
    if prior in F and F[prior]["physical_page"]==F[key]["physical_page"]:
        pp=number_for(prior)
        old=[x for x in page.search_for(pp) if abs(x.y0-n.y0)<=12]
        if old:
            assert any(x.x0>n.x0+20 for x in old),(key,"CURRENT_2026_NUMBER_MUST_BE_LEFT_OF_2025_COMPARATIVE",[z.x0 for z in old],n.x0)
    # Do not accidentally select a subsidiary-only currency table or parent BS.
    assert F[key]["physical_page"]==page.number+1,(key,"WRONG_GROUP_OR_PARENT_PAGE")
    # Verify amount string itself and sign from the same physical source row.
    row_text=page.get_textbox(fitz.Rect(max(0,a.x0-8),max(0,n.y0-10),min(page.rect.width-2,n.x1+11),min(page.rect.height,n.y1+10))).replace(" ","")
    if Decimal(F[key]["exact_value"])<0:
        signed_match=("-"+formatted in row_text) or ("("+formatted+")" in row_text) or ("−"+formatted in row_text)
        # Rare wrapped original table text can put sign in a neighbor,
        # but never silently interpret a printed positive as an accounting negative.
        assert signed_match,(key,"NEGATIVE_SIGN_NOT_VERIFIED_SAME_ORIGINAL_ROW",formatted,row_text[:180])
    return n,a

def verify(capture:bool):
    data=PDF.read_bytes()
    assert data.startswith(b"%PDF") and len(data)==1207059 and hashlib.sha256(data).hexdigest()==SHA==SOURCE["sha256"]==LEDGER["source"]["sha256"],"SOURCE_BYTES_FINGERPRINT_MISMATCH"
    pages=fitz.open(stream=data,filetype="pdf")
    assert len(pages)==178==SOURCE["physical_pages"],"ORIGINAL_PHYSICAL_PAGE_COUNT"
    out=BASE/"source-critical-cells.json"
    results=[]
    for key,label,p in SELECTED:
        assert F[key]["physical_page"]==p,(key,"LEDGER_SOURCE_PAGE_NOT_ANCHOR")
        n,a=find_position(pages[p-1],key,label)
        results.append({"key":key,"physical_page":p,"row_anchor":label,"source_unit":F[key]["source_report_unit"],
                        "original_period":F[key]["period"],"original_display_value":number_for(key),
                        "original_raw_exact":F[key]["exact_value"],
                        "numeric_x0":round(n.x0,2),"numeric_y0":round(n.y0,2),
                        "anchor_x0":round(a.x0,2),"anchor_y0":round(a.y0,2),"tolerance_points":1.65})
    if capture:
        out.write_text(json.dumps({"issuer":"601919","period":"2026H1","source_sha256":SHA,
            "source_pages":178,"verification_class":"SELECTED_SPATIAL_CELLS_ONLY_NOT_178_PAGE_NOTES_AUDIT",
            "original_units":"RMB yuan, RMB thousands, USD per TEU, TEU must retain their original precision",
            "selected":results},ensure_ascii=False,indent=2)+"\n")
    assert out.is_file(),"MISSING_APPROVED_ORIGINAL_CELL_POSITIONS"
    old=json.loads(out.read_text())
    assert old["issuer"]=="601919" and old["period"]=="2026H1" and old["source_sha256"]==SHA
    assert len(results)==len(old["selected"])>=35,"NOT_ENOUGH_SOURCE_CELLS"
    for x,y in zip(results,old["selected"]):
        for k in ("key","physical_page","row_anchor","source_unit","original_period","original_display_value","original_raw_exact"):
            assert x[k]==y[k],("MUTATED_SOURCE",k,x,y)
        for k in ("numeric_x0","numeric_y0","anchor_x0","anchor_y0"):
            assert abs(x[k]-y[k])<=y["tolerance_points"],("ORIGINAL_PDF_SPATIAL_COLUMN_DRIFT",k,x,y)
    print("SHIPPING_REAL_178_PAGE_ORIGINAL_SELECTED_XY_CELLS_PASS",len(results),SHA,flush=True)
    for x in results:print("PDF_SOURCE_CELL",x["physical_page"],x["key"],x["numeric_x0"],x["numeric_y0"],x["original_display_value"],flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--capture",action="store_true")
    args=ap.parse_args()
    verify(args.capture)
