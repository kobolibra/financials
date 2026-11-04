#!/usr/bin/env python3
"""中际旭创 300308 2026H1 original PDF *byte* and physical-page source audit.

This intentionally refuses to infer values from web snippets, fake report versions,
OCR guesses, or substitute the revenue-by-main/other classification for product type.
In the source p139 original double-printed "other" group total column differs by
RMB 1.00 from that row's income column, separately recorded as a disclosure
inconsistency; the primary "营业收入/成本" subcolumn still closes to the
consolidated income statement to the cent.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from decimal import Decimal as D
from pathlib import Path
try: import fitz
except ImportError: raise RuntimeError("Install pymupdf to inspect 184 physical pages")

ROOT=Path(__file__).resolve().parents[3]
TARGET_SHA="e0ecd7c365c65e90b1fa4b4616ba3f4649449d64451e0ba0b1b78ba9ce3170bf"
TARGET_BYTES=2_984_970
TARGET_PAGES=184
CODE="300308"
L=ROOT/"skills/ashare-financial-storytelling/v7/examples/zhongji-2026H1-ledger.json"
def read_json(p):return json.loads(p.read_text(encoding="utf-8"))
def val(f,k):return D(f[k]["amount"])
def digits(s):return re.sub(r"[,\s\u00a0]","",str(s)).replace("－","-").replace("−","-").replace("—","-")
def fail_if(condition,msg):
    if condition:raise AssertionError(msg)
def audit(source:Path, output:Path, allow_old_memo=True)->dict:
    b=source.read_bytes();sha=hashlib.sha256(b).hexdigest()
    fail_if(len(b)!=TARGET_BYTES or sha!=TARGET_SHA,
        f"ZJ_SOURCE_PDF_BYTES_OR_SHA_DIFFERENT bytes={len(b)} sha={sha} expected={TARGET_SHA}")
    d=fitz.open(stream=b,filetype="pdf")
    fail_if(len(d)!=TARGET_PAGES,"ORIGINAL_PDF_PHYSICAL_PAGE_MISMATCH")
    l=read_json(L);doc=l["document"];f=l["facts"]
    assert doc["ticker"]=="300308.SZ" and doc["period_key"]=="2026H1"
    assert doc["source_sha256"]==sha,"UNVERIFIED_OR_DIFFERENT_LEDGER_SOURCE_PDF_SHA"
    assert doc["scope"]=="consolidated" and doc["currency"]=="CNY" and not doc["audited"]
    assert doc["pages"]==len(d)
    p1=d[0].get_text()
    assert "中际旭创股份有限公司" in p1 and "2026" in p1 and "2026-081" in p1
    p51=d[50].get_text()
    assert "未经审计" in p51 and "合并资产负债表" in p51 and "单位：元" in p51
    texts={i:digits(d[i-1].get_text()) for i in range(1,len(d)+1)}
    missing=[];verified=[]
    for key,record in f.items():
        if record.get("status")!="reported":continue
        amt=record.get("amount")
        page=record.get("page")
        if amt is None or page is None:
            missing.append({"key":key,"page":page,"issue":"MISSING_REPORTED_SOURCE_RECORD"});continue
        expected=digits(f"{D(amt):,.2f}")
        if expected not in texts[int(page)]:
            missing.append({"key":key,"page":page,"value":amt,"issue":"PHYSICAL_PAGE_AMOUNT_NOT_PRESENT"})
        else:
            verified.append({"key":key,"physical_page":page,"exact_yuan":amt})
    fail_if(bool(missing),"SOURCE_LEDGER_FACT_PAGES_NOT_FOUND: "+json.dumps(missing,ensure_ascii=False))
    assert len(verified)>=48,("INSUFFICIENT_PDF_PRIMARY_SOURCE_FACTS",len(verified))
    rows=l["indirect_cfo_adjustments"]
    assert len(rows)==15
    for i,row in enumerate(rows):
        page=int(row["page"])
        assert page in (147,148),("CFO_PHYSICAL_PAGE",i,page)
        assert digits(f"{D(row['amount']):,.2f}") in texts[page],("CFO_VALUE_NOT_ON_REPORTED_PAGE",i,page,row)
    assert "现金流量表补充资料" in d[146].get_text()
    assert "存货的减少" in d[147].get_text()
    assert "经营活动产生的现金流量净额" in d[147].get_text()
    # Original paper geometry and explicitly nonexchangeable classification cuts.
    pg139=texts[139]
    assert digits(f"{D('41777861795.03'):,.2f}") in pg139
    assert digits(f"{D('422649612.97'):,.2f}") in pg139
    assert digits(f"{D('422649613.97'):,.2f}") in pg139
    assert digits(f"{D('41355212182.06'):,.2f}") in pg139
    assert digits(f"{D('41739023748.84'):,.2f}") in pg139
    assert digits(f"{D('38838046.19'):,.2f}") in pg139
    other_other=D('422649613.97')
    other_used=val(f,"other_product_revenue")
    assert other_used==D('422649612.97')
    assert other_other-other_used==D(1)
    assert val(f,"optical_revenue")+other_used==val(f,"revenue")
    assert val(f,"optical_cogs")+val(f,"other_product_cogs")==val(f,"cogs")
    assert D("41739023748.84")+D("38838046.19")==val(f,"revenue")
    assert D("22428583809.49")+D("26104330.95")==val(f,"cogs")
    assert val(f,"revenue")-val(f,"cogs")==val(f,"gross_profit")
    assert val(f,"operating_profit")+val(f,"nonop_income")-val(f,"nonop_expense")-val(f,"income_tax")==val(f,"net_profit")
    assert val(f,"net_profit")==val(f,"parent_profit")+val(f,"minority_profit")
    assert val(f,"assets")==val(f,"liabilities")+val(f,"equity")
    assert val(f,"assets")==val(f,"current_assets")+val(f,"noncurrent_assets")
    adj=sum((D(z["amount"]) for z in rows),D(0))
    assert val(f,"net_profit")+adj==val(f,"cfo"),("SIGNED_INDIRECT_CFO_NOT_CLOSED",adj)
    assert val(f,"cash_open")+val(f,"cfo")+val(f,"cfi")+val(f,"cff")+val(f,"fx_effect")==val(f,"cash_close")
    assert val(f,"monetary_funds")!=val(f,"cash_close"),"WRONG_CASH_EQUIVALENT_BOUNDARY"
    # Explicitly keep stock vs flow separate despite visual similarity.
    assert val(f,"inventory")-val(f,"inventory_prior") != -D(rows[-4]["amount"]), "CFO_VS_BS_INVENTORY_NOT_DISTINGUISHED"
    assert val(f,"accounts_receivable")-val(f,"accounts_receivable_prior") != -D(rows[-3]["amount"]), "CFO_VS_BS_AR_NOT_DISTINGUISHED"
    proof={
     "issuer":"中际旭创股份有限公司","ticker":"300308.SZ",
     "source_original_pdf_sha256":sha,"source_original_pdf_bytes":len(b),
     "physical_pdf_pages":len(d),"period":"2026H1","currency":"CNY",
     "consolidated_report":"PASS","unaudited_original":"PASS",
     "source_page_amount_checks":len(verified),"source_page_amounts_exact":"PASS",
     "indirect_CFO_all_original_signed_adjustments":len(rows),
     "indirect_CFO_calculation":"PASS",
     "income_gross_consolidated_and_product_group_sum":"PASS",
     "cash_movement_bs_and_net_income":"PASS",
     "original_page139_material_cross_print_one_yuan_discrepancy":{
        "status":"DISCLOSED_INCONSISTENCY__DO_NOT_SILENTLY_CORRECT_OR_FAKE_RESIDUAL",
        "physical_page":139,
        "original_business_type_revenue_cell_yuan":"422649612.97",
        "original_same_row_repeated_total_revenue_cell_yuan":"422649613.97",
        "difference_yuan":"1.00",
        "source_choice_for_graph":"422649612.97__SOURCE_ORIGINAL_CONTRACT_BUSINESS_TYPE_CELL_AND_FULL_CONSOLIDATED_SUM",
        "financial_meaning":"same p139 table repeated numeric column inconsistency; not a distinct business line or unreported residual"
     },
     "actual_reported_facts":verified,
     "independent_second_human_analyst":"NOT_CHECKED",
     "full_all_major_note_independent_reviews":"NOT_CHECKED",
     "current_11_issuer_cloudflare_new_version":"NOT_CHECKED",
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("ORIGINAL_300308_COMPLETE_184_PAGE_EXACT_BYTE_SIGNED_FINANCIAL_SOURCE_PASS",json.dumps({k:v for k,v in proof.items() if k not in ("actual_reported_facts",)},ensure_ascii=False),flush=True)
    return proof
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--pdf",required=True)
    parser.add_argument("--out",default="research/issuers/300308/source-verification.json")
    args=parser.parse_args()
    audit(Path(args.pdf),Path(args.out))
