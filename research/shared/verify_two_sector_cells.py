#!/usr/bin/env python3
"""Source-cell hostile verification against the actual complete original PDF.

A number occurring somewhere on a PDF page is not enough: enforce original
physical page, exact amount, original x/y location (correct row and period or
revenue/cost column), original row label, issuer and period in PDF itself.
"""
from __future__ import annotations
import argparse,json
from decimal import Decimal
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[2]
def run(code):
    base=ROOT/"research/issuers"/code
    d=json.loads((base/"source-ledger.json").read_text(encoding="utf-8"))
    checklist=json.loads((base/"source-critical-cells.json").read_text(encoding="utf-8"))
    assert code==d["issuer"]["code"]==checklist["issuer"] and d["issuer"]["fiscal_period"]==checklist["report_period"]
    p=ROOT/d["source"]["source_path"]
    doc=fitz.open(p)
    assert len(doc)==d["source"]["physical_pages_observed"]
    assert code in doc[0].get_text() and "2026" in doc[0].get_text()
    assert len(checklist["selected"])>=20 and len(set(x["fact_id"] for x in checklist["selected"]))==len(checklist["selected"])
    records=[]
    for cell in checklist["selected"]:
        k=cell["fact_id"];f=d["facts"][k]
        page_num=cell["physical_page"]; assert f["page"]==page_num,(k,"WRONG_PDF_PAGE")
        page=doc[page_num-1]
        s=format(Decimal(f["yuan"]),",.2f")
        candidates=page.search_for(s)
        assert candidates,(code,k,"EXACT_AMOUNT_NOT_ON_PHYSICAL_PAGE",page_num,s)
        # Manually inspected pair (x,y) is part of immutable original source,
        # so selecting the wrong comparative 2025 column fails even if same
        # number occurs in another label or table on this page.
        chosen=min(candidates,key=lambda r: abs(r.x0-cell["original_x0"])+abs(r.y0-cell["original_y0"]))
        tolerance=cell["coordinate_tolerance"]
        assert abs(chosen.x0-cell["original_x0"])<=tolerance,(code,k,"WRONG_REPORTING_COLUMN",chosen.x0,cell["original_x0"])
        assert abs(chosen.y0-cell["original_y0"])<=tolerance,(code,k,"WRONG_ORIGINAL_ROW",chosen.y0,cell["original_y0"])
        row=page.get_textbox(fitz.Rect(25,chosen.y0-26,min(page.rect.width-5,max(520,chosen.x1+5)),chosen.y1+24))
        assert cell["row_anchor"] in row,(code,k,"WRONG_ROW_LABEL",repr(row[:250]),cell["row_anchor"])
        records.append({"key":k,"physical_page":page_num,"x0":round(chosen.x0,2),"y0":round(chosen.y0,2),"label":cell["row_anchor"],"original_amount":f["yuan"],"period":f["period"],"unit":f["unit"]})
    doc.close()
    print("ACTUAL_PDF_ROW_COLUMN_VERIFIED",code,len(records),"unique physical source records")
    return records
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--code",required=True,choices=["600900","600276"])
    a=parser.parse_args();run(a.code)
