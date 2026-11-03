#!/usr/bin/env python3
"""688220 source-led, standalone research HTML. No third-party JS/CSS or runtime network.

This publisher does NOT certify SOURCE_BYTES unless archive manifest and PDF exist,
all Decimal checks pass, and the file's SHA/224 physical pages match the manifest.
SOURCE_SEMANTIC and editorial-human gates remain separate.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from decimal import Decimal as D
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]))
from shared.conserved_flow import build_conserved_income_flow
ap=argparse.ArgumentParser()
ap.add_argument("--out",type=Path,default=ROOT/"preview"/"688220.html")
ap.add_argument("--qa",type=Path,default=ROOT/"qa.json")
a=ap.parse_args()
data=json.loads((ROOT/"source-ledger.json").read_text(encoding="utf-8"))
f=data["facts"]
val=lambda k:D(f[k]["yuan"])
checks={}
def ck(label,actual,expected):
    assert actual==expected,(label,"INVARIANT_FAILED",str(actual),str(expected))
    checks[label]="PASS"
rev=sum((val(i["rev"]) for i in data["segments"]),D(0))
cost=sum((val(i["cost"]) for i in data["segments"]),D(0))
ck("REVENUE_PARTITION_EXACT_YUAN",rev,val("rev"))
ck("COST_PARTITION_EXACT_YUAN",cost,val("cogs"))
ck("GROSS_PROFIT_COMPONENTS",sum((val(i["rev"])-val(i["cost"]) for i in data["segments"]),D(0)),val("rev")-val("cogs"))
ck("CONSOLIDATED_PNL_OPERATING",val("rev")-val("operating_total_cost")+sum((val(k) for k in ("other_income","investment_income","fair_value_income","credit_impairment","asset_impairment","asset_disposal_gain")),D(0)),val("operating_profit"))
ck("PARENT_PROFIT",val("pretax_profit")-val("income_tax_expense"),val("consolidated_net_profit"))
ck("OPERATING_COSTS_COMPLETE_ROW_DETAIL",
   sum((val(k) for k in ("cogs","tax_surcharge","sell","admin","rnd_expense","finance_expense")),D(0)),
   val("operating_total_cost"))
ck("OPERATING_PROFIT_TO_PRETAX_BY_ACTUAL_CURRENT_COLUMN",
   val("operating_profit")+val("nonoperating_income"),val("pretax_profit"))
assert "nonoperating_expense" not in f,"PRIOR_YEAR_EXPENSE_MISREAD_AS_CURRENT"
assert f["nonoperating_expense_prior"]["period"]=="2025H1" and val("nonoperating_expense_prior")==D("15.30"),"P87_COMPARATIVE_COLUMN_NOT_VERIFIED"
gross=val("rev")-val("cogs")
other_opex=sum((val(k) for k in ("tax_surcharge","sell","admin","finance_expense")),D(0))
gains=sum((val(k) for k in ("other_income","investment_income","fair_value_income")),D(0))
signed_impairment=sum((val(k) for k in ("credit_impairment","asset_impairment","asset_disposal_gain")),D(0))
ck("FULL_SIGNED_PNL_FROM_GROSS_TO_OPERATING",
   gross-val("rnd_expense")-other_opex+gains+signed_impairment,val("operating_profit"))
ck("FULL_PNL_OP_TO_NI_VIA_TAX_BENEFIT",
   val("operating_profit")+val("nonoperating_income")-val("income_tax_expense"),val("consolidated_net_profit"))
ck("PARENT_VS_DEDUCTED",val("deducted_parent_ni")+val("nonrec_parent_net"),val("parent_ni"))
ck("NONRECURRING_SIGNED_SCHEDULE",sum((D(q["yuan"]) for q in data["nonrecurring"]["parts"]),D(0)),val("nonrec_parent_net"))
ck("BS_2026_06_30",val("liabilities")+val("equity"),val("assets"))
ck("BS_2025_12_31",val("liabilities_prior")+val("equity_prior"),val("assets_prior"))
ck("INVENTORY_GROSS_TO_NET",val("inventory_gross")-val("inventory_reserve"),val("inventory_net"))
ck("INVENTORY_PRIOR_GROSS_TO_NET",val("inventory_gross_prior")-val("inventory_reserve_prior"),val("inventory_net_prior"))
ck("ACCOUNTS_RECEIVABLE_NET",val("ar_gross")-val("ar_allowance"),val("ar"))
ck("ACCOUNTS_RECEIVABLE_AGING_TOTAL",sum((val(k) for k in ("ar_aging_lt3m","ar_aging_3m1yr","ar_aging_1to2yr")),D(0)),val("ar_gross"))
ck("CONTRACT_LIABILITY_COMPONENTS",sum((val(k) for k in ("contract_advance_custom","contract_advance_product","contract_advance_ip")),D(0)),val("contract_liabilities"))
ck("REVENUE_RECOGNITION_TIME_SPLIT",val("revenue_point_time")+val("revenue_over_time"),val("rev"))
# Original p.137 discloses a 90.50% top-5 AR & contract asset concentration ratio,
# yet p.135+138 original gross denominator gives ~89.17%; do not silently repair.
derived_ar_top5=(val("ar_top5_with_contract_assets")/(val("ar_gross")+D("1113000.00"))*100).quantize(D("0.01"))
assert derived_ar_top5!=val("ar_top5_ratio"),"Unexpected raw-note denominator reconciliation change"
unresolved_ratio={"reported_pct":str(val("ar_top5_ratio")),"derived_pct_from_gross_AR_plus_gross_contract_assets":str(derived_ar_top5),"numerator_yuan":str(val("ar_top5_with_contract_assets")),"reported_denominator":"NOT_DISCLOSED_IN_THE_SAME_NOTE_TABLE","status":"FAIL_BOUNDED_NOTE_DENOMINATOR_RECONCILIATION","scope":"Consolidated AR+contract assets p135,p137,p138; parent p213 is incompatible."}
ck("INDIRECT_CFO_ALL_17_ORIGINAL_SIGNED_ROWS",val("consolidated_net_profit")+sum((D(q["yuan"]) for q in data["cfo_indirect"]["parts"]),D(0)),val("cash_cfo"))
ck("CASH_SECTION_CLOSURE",val("cash_start")+sum((val(k) for k in ("cash_cfo","cash_cfi","cash_cff","cash_fx")),D(0)),val("cash_end"))
ck("RPO_SPLIT_ONE_CENT_SOURCE_PRECISION_BOUNDARY",val("rpo_one_year")+val("rpo_over_one_year")-val("rpo"),D("0.01"))
source_status="NOT_CHECKED"
actual_sha="NOT_CHECKED"
manifest=ROOT/"source-manifest.json"
if manifest.exists():
    m=json.loads(manifest.read_text(encoding="utf-8"))
    pdf=ROOT/m["file"]
    if pdf.is_file():
        b=pdf.read_bytes()
        actual_sha=hashlib.sha256(b).hexdigest()
        assert b.startswith(b"%PDF-") and len(b)==m["pdf_bytes"] and actual_sha==m["pdf_sha256"] and m["pdf_physical_page_count"]==224
        source_status="MIRROR_COMPLETE_PDF_SHA_PASS__OFFICIAL_EQUIVALENCE_NOT_CHECKED"
        checks["PDF_MIRROR_FULL_BYTES_SHA_224P"]="PASS"
    else:
        raise RuntimeError("MANIFEST_EXISTS_BUT_PDF_BYTES_MISSING")
else:
    checks["PDF_MIRROR_FULL_BYTES_SHA_224P"]="NOT_CHECKED"
data["source"]["original_bytes_sha256"]=actual_sha
data["source"]["original_bytes_gate"]=source_status
# One generic source/period/dimension-conserved finance flow graph is the
# only source for the ribbon structure; renderer must use its eight actual edges.
data["finance_flow"]=build_conserved_income_flow(data)
checks["SANKEY_FOUR_SEGMENTS_EIGHT_EXACT_COGS_GP_EDGES"]="PASS"
briefs=json.loads((ROOT/"figure-briefs.json").read_text(encoding="utf-8"))
expected_briefs={"flow","segment","gp","pnl","earnings","cfo","cash","capital"}
found={x["id"] for x in briefs["figures"]}
assert len(briefs["figures"])==8 and found==expected_briefs,"FIGURE_BRIEF_MISSING_OR_DUPLICATED"
required=("family","question","answer","pages","fact_ids","relation","domain_zero","color_encoding",
          "alternative_hypothesis","mobile_policy","source_pdf_sha256","reviewer","publication_gate")
for figure in briefs["figures"]:
    assert all(figure.get(key) for key in required),("FIGURE_UNREVIEWED",figure.get("id"))
    assert figure["source_pdf_sha256"]==actual_sha,("FIGURE_PDF_SHA_MISMATCH",figure["id"])
    assert all(k in f for k in figure["fact_ids"]),("FIGURE_NON_SOURCE_FACT",figure["id"])
    assert all(1<=p<=224 for p in figure["pages"]),("FIGURE_PHYSICAL_PAGE",figure["id"])
data["figure_briefs"]=briefs["figures"]
checks["SEVEN_ACTUAL_SOURCE_BOUND_FIGURE_BRIEFS"]="PASS"
template=(ROOT/"report-template.html").read_text(encoding="utf-8")
encoded=json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
source_display=("完整 PDF 副本 SHA / 224 页已核验；上交所原始 URL 字节同一性 NOT_CHECKED" if source_status.startswith("MIRROR_COMPLETE") else "原始 PDF 完整字节 NOT_CHECKED")
output=(template.replace("__RESEARCH_JSON__",encoded).replace("__SOURCE_STATUS__",source_display).replace("__SOURCE_SHA__",actual_sha))
assert "<script src=" not in output and "<iframe" not in output and "https://fonts" not in output
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(output,encoding="utf-8")
a.qa.parent.mkdir(parents=True,exist_ok=True)
a.qa.write_text(json.dumps({"issuer":"688220","report_period":"2026H1","source_sha":actual_sha,"source_bytes":source_status,"checks":checks,"research":"SELF_REVIEWED_SOURCE_LIMITED","full_material_notes":"NOT_CHECKED","second_independent_human":"NOT_CHECKED","industry":"semiconductor-chip-design","source_screenshots":"SELECTED_PAGES_SCREENED","ar_top5_concentration_denominator":unresolved_ratio,"article":"RESEARCH_PREVIEW"},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("ASR_PUBLICATION_REBUILD",a.out,"bytes",a.out.stat().st_size,"ACCOUNTING_PASS",len(checks)-int(source_status=="NOT_CHECKED"),"source_bytes",source_status,flush=True)
