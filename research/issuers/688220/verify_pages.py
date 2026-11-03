#!/usr/bin/env python3
"""Real PDF byte / physical page literal verification. Numbers matching a page
are *not* row+column semantic validation; keep the gates independent.
"""
from __future__ import annotations
import hashlib,json,pathlib,re
from decimal import Decimal as D
import fitz
ROOT=pathlib.Path(__file__).resolve().parent
ledger=json.loads((ROOT/"source-ledger.json").read_text())
manifest=json.loads((ROOT/"source-manifest.json").read_text())
pdfbytes=(ROOT/manifest["file"]).read_bytes()
sha=hashlib.sha256(pdfbytes).hexdigest()
assert sha==manifest["pdf_sha256"]=="9d276876a4341bc3c8d2735be43c7f70cb5dc0f4e7c669b16e96a11a814d1bdc"
assert pdfbytes.startswith(b"%PDF-") and len(pdfbytes)==manifest["pdf_bytes"]==1449510
pdf=fitz.open(stream=pdfbytes,filetype="pdf")
assert len(pdf)==224==manifest["pdf_physical_page_count"]
pages=[re.sub(r"[\s,]","",page.get_text(sort=True)).replace("－","-").replace("−","-") for page in pdf]
def normalized_abs(y):
    n=D(y).copy_abs()
    return f"{n:.2f}"
items={}
for k,f in ledger["facts"].items():
    p=int(f["page"])
    if f.get("classification")=="DERIVED_BLANK_CURRENT_CELL":
        items[k]={"physical_page":p,"original_label_in_ledger":f["label"],
                  "amount_yuan":f["yuan"],"status":"DERIVED_NOT_DISCLOSED_LITERAL",
                  "semantic_note":"Current column physically empty; compare prior column separately"}
        continue
    found=normalized_abs(f["yuan"]) in pages[p-1]
    items[k]={"physical_page":p,"original_label_in_ledger":f["label"],"amount_yuan":f["yuan"],"literal_match":found}
# Original page 87 table row: 15.30 is in 2025 H1 RIGHT column,
# 2026 H1 middle column is BLANK. Prevent a 1-column shift.
original_pnl_words=pdf[86].get_text("words")
prior_expense=[w for w in original_pnl_words if w[4]=="15.30" and 230<w[1]<255]
assert len(prior_expense)==1 and prior_expense[0][0]>460,("PRIOR_COLUMN_PROOF_MISSING",prior_expense)
assert not any(300<=w[0]<450 and 230<w[1]<255 and
               any(ch.isdigit() for ch in w[4]) for w in original_pnl_words), "2026H1_NONOPERATING_EXPENSE_COLUMN_NOT_BLANK"
gf=ledger["facts"]
assert (D(gf["operating_profit"]["yuan"])+D(gf["nonoperating_income"]["yuan"])-
        D(gf["pretax_profit"]["yuan"])==D("0.00")), "DERIVED_EMPTY_CURRENT_EXPENSE_NOT_ZERO"
assert D(gf["nonoperating_expense_prior"]["yuan"])==D("15.30") and gf["nonoperating_expense_prior"]["period"]=="2025H1"

for i,f in enumerate(ledger["cfo_indirect"]["parts"]):
    p=int(f["page"]);k=f"cfo_signed_part_{i+1:02d}"
    value=f["yuan"];num=normalized_abs(value)
    text=pages[p-1]
    found=("-"+num in text if D(value)<0 else num in text)
    items[k]={"physical_page":p,"original_label_in_ledger":f["label"],"amount_yuan":value,"signed_literal_match":found}
for i,f in enumerate(ledger["nonrecurring"]["parts"]):
    p=int(f["page"]);k=f"nonrec_part_{i+1:02d}"
    num=normalized_abs(f["yuan"])
    items[k]={"physical_page":p,"original_label_in_ledger":f["label"],"amount_yuan":f["yuan"],"literal_match":num in pages[p-1]}
# Stage B: explicitly reviewed PDF cell rectangles for the nine monetary figures
# fragmented into two vertical text lines by the issuer's narrow p.135/p.146 tables.
# Never infer a row's cell by searching a complete page alone.
cell_manifest=json.loads((ROOT/"source-cells.json").read_text(encoding="utf-8"))
assert cell_manifest["source_sha256"]==sha and len(cell_manifest["cells"])==9
cell_results={}
for key,spec in cell_manifest["cells"].items():
    assert key in ledger["facts"],("UNKNOWN_SOURCE_CELL",key)
    physical=spec["physical_page"]
    assert ledger["facts"][key]["page"]==physical,("CELL_PHYSICAL_PAGE_MISMATCH",key)
    p=pdf[physical-1]
    rect=spec["rect"]
    assert len(rect)==4 and 0<=rect[0]<rect[2]<=p.rect.width and 0<=rect[1]<rect[3]<=p.rect.height
    source_page_text=re.sub(r"\s+","",p.get_text(sort=True))
    for token in (spec["row_label"],spec["top_heading"],spec["column_heading"]):
        assert re.sub(r"\s+","",token) in source_page_text,("SOURCE_ROW_OR_COLUMN_HEADER_NOT_FOUND",key,token)
    clipped_words=[
        w for w in p.get_text("words",sort=True)
        if w[0]>=rect[0] and w[2]<=rect[2] and w[1]>=rect[1] and w[1]<=rect[3]
    ]
    reconstructed="".join(w[4] for w in sorted(clipped_words,key=lambda w:(w[1],w[0])))
    expected=f"{D(ledger['facts'][key]['yuan']).copy_abs():,.2f}"
    assert reconstructed==expected,("REVIEWED_CELL_ORIGINAL_BYTES_MISMATCH",key,expected,reconstructed,rect)
    if key.endswith("_prior"):
        assert spec["period"]=="2025-12-31",("PRIOR_PERIOD_COLUMN_MISMATCH",key)
    else:
        assert spec["period"]=="2026-06-30",("CURRENT_PERIOD_COLUMN_MISMATCH",key)
    result={"physical_page":physical,"row_label":spec["row_label"],
            "column_heading":spec["column_heading"],"top_heading":spec["top_heading"],
            "bbox_pdf_pt":rect,"extracted_original_cell":reconstructed,
            "original_yuan":expected,"method":"REVIEWED_PHYSICAL_PAGE_COORDINATE_AND_TABLE_ROW_COLUMN",
            "semantic_limit":"Source table coordinates and same-page header verified, not an independent second human review."}
    cell_results[key]=result
    items[key]["positional_source_cell_match"]=True
    items[key]["source_cell"]=result
# Persist the actual source-page images accompanying table-cell bounding proofs.
image_dir=ROOT/"source-images"
image_dir.mkdir(exist_ok=True)
for number in [135,146]:
    pdf[number-1].get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False).save(str(image_dir/f"p{number:03d}.png"))
raw_page_literal=sum(bool(v.get("literal_match") or v.get("signed_literal_match")) for v in items.values())
critical={"rev","rev_prior","cogs","cogs_prior","consolidated_net_profit","parent_ni","deducted_parent_ni","nonrec_parent_net","assets","liabilities","equity","cash_cfo","cash_cfi","cash_cff","cash_start","cash_end","chip_rev","chip_cost","asic_rev","asic_cost","ip_rev","ip_cost"}
missing=[key for key,v in items.items() if v.get("status")!="DERIVED_NOT_DISCLOSED_LITERAL" and not (v.get("literal_match") or v.get("signed_literal_match") or v.get("positional_source_cell_match"))]
crit_missing=sorted(critical & set(missing))
out={"issuer":"688220","report":"2026H1","pdf_sha256":sha,"pdf_bytes":len(pdfbytes),"physical_pages":len(pdf),
 "source_file":"research/issuers/688220/"+manifest["file"],
 "source_get":"COMPLETE_PDF_MIRROR_BYTES_AND_ORIGINAL_REPORT_IDENTITY_PASS",
 "sse_mirror_byte_equivalence":"NOT_CHECKED",
 "page_literal_matched":raw_page_literal,"page_coordinate_reconstructed":len(cell_results),"page_amount_or_cell_matched":len(items)-len(missing)-1,"page_literal_total":len(items)-1,"verified_source_cells":cell_results,
 "physical_row_column_exception_p87":"PASS_PRIOR_2025H1_EXPENSE_15_30_IN_RIGHT_COLUMN__2026H1_BLANK_DERIVED_0","critical_source_row_literal_missing":crit_missing,
 "missing_page_literals":missing,
 "page_amount_check_not_row_col_semantics":"The fact a number occurs on a cited physical page does NOT prove table row, column, consolidation scope or currency.",
 "manual_semantic_review":"SELECTED_ORIGINAL_PAGES_REVIEWED_NOT_COMPLETE_MATERIAL_NOTES",
 "full_independent_human_review":"NOT_CHECKED",
 "facts":items
}
(ROOT/"source-verification.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("ASR_SOURCE_BYTES_PASS",sha,len(pdfbytes),len(pdf),flush=True)
print("SOURCE_PAGE_LITERAL_AND_COORDINATES",raw_page_literal,"raw","+",len(cell_results),"cells","=",len(items)-len(missing)-1,"/",len(items)-1,"UNPROVEN",missing,flush=True)
assert not missing,("UNPROVEN_NUMERIC_SOURCE_CELL",missing)
assert not crit_missing,("CRITICAL_ROW_PAGE_AMOUNT_MISMATCH",crit_missing)
assert all(items[f"cfo_signed_part_{i+1:02d}"]["signed_literal_match"] for i in range(17)), "SIGNED_CFO_PAGE_FAILED"
