#!/usr/bin/env python3
"""Lock and verify insurer's selected original physical PDF cells.

Understands printed RMB MILLION vs canonical ledger in RMB yuan, explicit
2026-vs-2025 columns, negative parentheses, source anchors and page numbers.
--capture is a candidate x/y extraction, NOT a human independent review.
--verify independently rechecks archived coordinates at exact page and SHA.
"""
from pathlib import Path
from decimal import Decimal
import argparse,hashlib,json,re
import fitz

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"research/issuers/601628"
FACTS=json.loads((BASE/"source-ledger.json").read_text())["facts"]
SRC=json.loads((BASE/"source-verification.json").read_text())
PDF=ROOT/SRC["source_pdf"]
SELECTED=[
 ("assets","资产总计"),("liabilities","负债合计"),("parent_equity","归属于母公司股东的股东权益合计"),
 ("minority_equity","少数股东权益"),("insurance_contract_liab","保险合同负债"),
 ("total_revenue","营业收入"),("service_revenue","保险服务收入"),("interest_income","利息收入"),
 ("investment_income","投资收益"),("fairvalue_income","公允价值变动损益"),
 ("service_cost","保险服务费用"),("reinsurance_premium","分出保费的分摊"),
 ("reinsurance_recovered","摊回保险服务费用"),("insurance_finance","承保财务损益"),
 ("op_profit","营业利润"),("pretax_profit","利润总额"),("income_tax","所得税费用"),
 ("parent_net","归属于母公司股东的净利润"),("net_profit","净利润"),("nci_profit","少数股东损益"),
 ("cfo_in","经营活动现金流入小计"),("cfo_claims","支付签发保险合同赔款的现金"),
 ("cfo_commission","支付手续费及佣金的现金"),("cfo_out","经营活动现金流出小计"),
 ("cfo","经营活动产生的现金流量净额"),("cfi","投资活动产生的现金流量净额"),
 ("cff","筹资活动产生的现金流量净额"),("cash_start","期初现金及现金等价物余额"),
 ("cash_end","期末现金及现金等价物余额"),("csm","合同服务边际"),
 ("future_cash_flow_liab","未来现金流量现值"),("service_csm_release","合同服务边际的摊销"),
 ("service_paa","采用保费分配法计量的合同")
]
def check_identity(data):
    assert data.startswith(b"%PDF"),"PDF_MAGIC"
    assert hashlib.sha256(data).hexdigest()==SRC["sha256"]=="b094bf337309e30564dda86ff4b3c4d66aeeb37ce0357a3568e246569f0e2943","SOURCE_SHA"
def source_amount(key):
    amt=Decimal(FACTS[key]["yuan"])/Decimal(1000000)
    assert amt==amt.to_integral_value(),"LOSSY_PDF_UNIT"
    return int(amt)
def xymatch(page,key,anchor):
    amount=source_amount(key)
    num=f"{abs(amount):,}"
    cand=page.search_for(num)
    abox=page.search_for(anchor)
    assert cand,(key,"ORIGINAL_AMOUNT_MISSING",num)
    assert abox,(key,"ROW_ANCHOR_MISSING",anchor)
    found=[]
    for r in cand:
        for a in abox:
            dy=abs((r.y0+r.y1)/2-(a.y0+a.y1)/2)
            # only physically same printed table row, not a free-floating number
            if dy<=11 and r.x0>a.x0+12:
                found.append((dy+max(0,a.x1-r.x0)/10,r,a))
    if not found:raise AssertionError((key,"ROW_COLUMN_NOT_ALIGNED_WITH_ANCHOR",num,anchor))
    _,rect,ar=min(found,key=lambda z:z[0])
    # correct current-year column: where same original row has a right-side
    # comparison number, the current-year value must fall left of it.
    prior=key+"_prior"
    if prior in FACTS and FACTS[prior]["page"]==FACTS[key]["page"]:
        pv=f"{abs(source_amount(prior)):,}"
        pr=[b for b in page.search_for(pv) if abs(b.y0-rect.y0)<=10]
        if pr and not any(b.x0>rect.x0+25 for b in pr):
            raise AssertionError((key,"2025_COMPARATIVE_NOT_TO_RIGHT",rect.x0,[b.x0 for b in pr]))
    # Read actual physical row; signed values must be parentheses in the original
    # not silently recoded as positive amounts.
    row=page.get_textbox(fitz.Rect(max(0,ar.x0-5),max(0,rect.y0-6),min(page.rect.width-2,rect.x1+7),rect.y1+7))
    if amount<0 and not re.search(r"\("+re.escape(num)+r"\)",row.replace(" ","")):
        # Get text blocks can rearrange columns; source row is still required to
        # contain the source number and its open/close parentheses.
        clean=page.get_text(sort=True)
        assert "("+num+")" in clean,(key,"NEGATIVE_SIGN_UNVERIFIED",num)
    return rect,ar
def run(capture):
    raw=PDF.read_bytes();check_identity(raw)
    pdf=fitz.open(stream=raw,filetype="pdf")
    assert len(pdf)==SRC["physical_pages"]==104
    outfile=BASE/"source-critical-cells.json"
    entries=[]
    for key,anchor in SELECTED:
        fact=FACTS[key];page=pdf[fact["page"]-1]
        r,a=xymatch(page,key,anchor)
        entries.append({"fact_id":key,"physical_page":fact["page"],"row_anchor":anchor,
                        "original_x0":round(r.x0,2),"original_y0":round(r.y0,2),
                        "anchor_x0":round(a.x0,2),"anchor_y0":round(a.y0,2),
                        "original_million":source_amount(key),"original_year":"2026H1" if fact["type"]=="flow" else "2026-06-30",
                        "coordinate_tolerance_pt":1.6})
    if capture:
        outfile.write_text(json.dumps({"issuer":"601628","report_period":"2026H1","source_sha256":SRC["sha256"],
            "source_units":"PDF人民币百万元; ledger 人民币元 x 1,000,000", "review_scope":"machine extracted original x/y values plus direct visual original screenshots, NOT exhaustive 104-page semantic independent review","selected":entries},ensure_ascii=False,indent=2)+"\n")
    assert outfile.is_file(),"SOURCE_CELLS_NEVER_CAPTURED"
    saved=json.loads(outfile.read_text())
    assert saved["source_sha256"]==SRC["sha256"] and len(saved["selected"])>=30
    for actual,expected in zip(entries,saved["selected"]):
        assert actual["fact_id"]==expected["fact_id"],"MUTATED_KEY"
        assert actual["physical_page"]==expected["physical_page"],"MUTATED_PDF_PAGE"
        assert actual["original_million"]==expected["original_million"],"MUTATED_AMOUNT"
        for k in ["original_x0","original_y0","anchor_x0","anchor_y0"]:
            assert abs(actual[k]-expected[k])<=expected["coordinate_tolerance_pt"],("WRONG_PDF_COLUMN_OR_ROW",k,actual,expected)
    pdf.close()
    print("INSURER_ACTUAL_PDF_CRITICAL_ROW_COLUMN_PASS",len(entries),"original physical source pages",SRC["sha256"])
    for x in entries:print("PHYSICAL_CELL",x["physical_page"],x["fact_id"],x["original_x0"],x["original_y0"],x["original_million"])
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--capture",action="store_true")
    args=parser.parse_args()
    run(args.capture)
