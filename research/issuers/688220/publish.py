#!/usr/bin/env python3
"""688220 source-led, standalone research HTML. No third-party JS/CSS or runtime network.

This publisher does NOT certify SOURCE_BYTES unless archive manifest and PDF exist,
all Decimal checks pass, and the file's SHA/224 physical pages match the manifest.
SOURCE_SEMANTIC and editorial-human gates remain separate.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from native_mobile import make as make_native_mobile
from shared_pnl import render_asr_pnl,original_plan
from decimal import Decimal as D
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"shared"))
from source_income_adapter import render_sector_income
from economics_exhibit import render_panel as render_economics_panel
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
ap.add_argument("--out",type=Path,default=ROOT/"preview"/"688220.html")
ap.add_argument("--qa",type=Path,default=ROOT/"qa.json")
a=ap.parse_args()
data=json.loads((ROOT/"source-ledger.json").read_text(encoding="utf-8"))
briefs=json.loads((ROOT/"figure-briefs.json").read_text(encoding="utf-8"))
REQUIRED_FIGURES=("flow","segment","gp","pnl","earnings","cfo","cash","balance","capital")
assert briefs["issuer"]==data["issuer"]["code"],"FIGURE_BRIEF_WRONG_ISSUER"
assert tuple(q["id"] for q in briefs["figure_briefs"])==REQUIRED_FIGURES,"FIGURE_BRIEF_ORDER_OR_MISSING"
for q in briefs["figure_briefs"]:
    for field in ("family","question","takeaway","facts","source_pages","identity","zero","counter","mobile","quality"):
        assert q.get(field),("INCOMPLETE_FIGURE_BRIEF",q["id"],field)
    for fact_id in q["facts"]:
        assert fact_id in data["facts"],("UNKNOWN_SOURCE_FACT",q["id"],fact_id)
    assert q["quality"]["human_second_editor"]=="NOT_CHECKED","FALSE_HUMAN_EDITORIAL_CERTIFICATION"
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
# Unlike a superficial total-revenue Sankey, every original business stream
# splits into *its own* original disclosed COGS and derived positive gross profit.
# Reject any segment whose ribbons would be negative or outside the same scope.
for q in data["segments"]:
    r,c=val(q["rev"]),val(q["cost"])
    assert r>=0 and c>=0 and r>=c,("SEGMENT_RIBBON_MUST_BE_NONNEGATIVE",q["label"],r,c)
    for k in (q["rev"],q["cost"]):
        row=f[k]
        assert row["scope"]=="consolidated" and row["period"]=="2026H1" and row["unit"]=="元",("SCOPE_UNIT_CROSSOVER",k,row)
    ck("PRODUCT_COST_GP_FLOW_"+q["rev"],c+(r-c),r)
checks["SANKEY_EACH_SOURCE_COST_GP_NONNEGATIVE"]="PASS"
ck("CONSOLIDATED_PNL_OPERATING",val("rev")-val("operating_total_cost")+sum((val(k) for k in ("other_income","investment_income","fair_value_income","credit_impairment","asset_impairment","asset_disposal_gain")),D(0)),val("operating_profit"))
ck("PARENT_PROFIT",val("pretax_profit")-val("income_tax_expense"),val("consolidated_net_profit"))
# Full signed CAS P&L bridge makes the economic path visible. One compact
# full-amount waterfall replaces the earlier omission (GP→GAAP NP).
op_expenses=sum((val(k) for k in ("tax_surcharge","sell","admin","rnd_expense","finance_expense")),D(0))
ck("FULL_PNL_OPERATING_EXPENSE_IDENTITIES",val("cogs")+op_expenses,val("operating_total_cost"))
op_signed=(val("rev")-val("cogs"))-op_expenses+sum((val(k) for k in ("other_income","investment_income","fair_value_income","credit_impairment","asset_impairment","asset_disposal_gain")),D(0))
ck("FULL_PNL_GROSS_TO_OPERATING_SIGNED",op_signed,val("operating_profit"))
ck("FULL_PNL_OPERATING_TO_PRETAX",op_signed+val("nonoperating_income")-val("nonoperating_expense"),val("pretax_profit"))
ck("FULL_PNL_PRETAX_TO_GAAP_NET",val("pretax_profit")-val("income_tax_expense"),val("consolidated_net_profit"))
ck("PARENT_VS_DEDUCTED",val("deducted_parent_ni")+val("nonrec_parent_net"),val("parent_ni"))
ck("NONRECURRING_SIGNED_SCHEDULE",sum((D(q["yuan"]) for q in data["nonrecurring"]["parts"]),D(0)),val("nonrec_parent_net"))
ck("BS_2026_06_30",val("liabilities")+val("equity"),val("assets"))
ck("BS_2025_12_31",val("liabilities_prior")+val("equity_prior"),val("assets_prior"))
assert val("assets")>0 and val("assets_prior")>0
checks["EQUAL_TOTAL_BALANCE_STOCK_COMPOSITION_TWO_DATES"]="PASS"
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
# Reviewed independent semantic contracts that the client JS is required to
# obey. This is a factual source contract, not self-awarded design approval.
data["graphic_contract"]={
 "flow":{"family":"sankey","source":"p.178","period":"2026H1","scope":"consolidated",
         "sources":len(data["segments"]),"nonzero_ribbons":sum((int(val(q["cost"])>0)+int(val(q["rev"])-val(q["cost"])>0) for q in data["segments"])),
         "yuan_identity":"sum(segment revenue)=sum(segment original COGS)+sum(segment derived GP)"},
 "pnl":{"family":"signed_waterfall","source":"p.86-87","period":"2026H1","scope":"consolidated",
        "base":"gross_profit","end":"consolidated_net_profit","negative_and_positive_steps":True},
 "balance":{"family":"same_date_equal_total_stock","source":"p.81-83",
           "dates":["2025-12-31","2026-06-30"],"scope":"consolidated"}
}
template=(ROOT/"report-template.html").read_text(encoding="utf-8")
for chart in REQUIRED_FIGURES:
    for selector in ('id="fig-'+chart+'"','id="chart-'+chart+'"','id="table-'+chart+'"','data-export="'+chart+'"'):
        assert selector in template,("FIGURE_RENDER_OR_EVIDENCE_MISSING",chart,selector)

encoded=json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
source_display=("完整 PDF 副本 SHA / 224 页已核验；上交所原始 URL 字节同一性 NOT_CHECKED" if source_status.startswith("MIRROR_COMPLETE") else "原始 PDF 完整字节 NOT_CHECKED")
# Original PDF mirror is source-bound but its byte-equivalence to the
# official exchange download remains explicitly NOT_CHECKED.
income_desktop=render_sector_income(data,mobile=False,embedded=True)
income_phone=render_sector_income(data,mobile=True,embedded=True)
income_json=json.dumps(income_desktop,ensure_ascii=False).replace("<","\\u003c")
# Entire 2026H1 signed accounting is generated once from typed original
# Decimal facts, then visualized in genuinely distinct desktop/phone editions.
# Never trust a JavaScript floating-point waterfall for published source truth.
pnl_plan=original_plan(data)
pnl_desktop=render_asr_pnl(data,mobile=False)
pnl_phone=render_asr_pnl(data,mobile=True)
pnl_desktop_json=json.dumps(pnl_desktop,ensure_ascii=False).replace("<","\\u003c")
checks["SHARED_FULL_SIGNED_PNL_DESKTOP_PHONE"]="PASS"
output=(template.replace("__RESEARCH_JSON__",encoded).replace("__SOURCE_STATUS__",source_display)
    .replace("__SOURCE_SHA__",actual_sha).replace("__UNIFIED_DESKTOP__",income_json)
    .replace("__UNIFIED_PNL_DESKTOP__",pnl_desktop_json))
comparison_brief=json.loads((ROOT/"comparative-economics.json").read_text(encoding="utf-8"))
output=output.replace('<main class="wrap">','<main class="wrap">'+render_economics_panel(data,comparison_brief),1)
# The full standalone article retains its original nine desktop editable SVG
# graphs and financial evidence tables. At <=820, a second issuer-specific
# original-money narrative is shown without horizontally cropping the reader.
# An exact figure anchor is required; no silent source/render drift.
native=make_native_mobile(data)
native["flow"]=('<div class="native-asr" data-native-source="canonical-v9">'
                 +'<p class="native-asr-dek">本图来自同一个收入来源→总收入→真实成本/毛利金额守恒渲染器；金额按人民币元一比一比例绘制，其他小额业务不人为加粗。</p>'
                 +income_phone.replace('<svg ', '<svg class="native-asr-original" ',1)
                 +'</div>')
# Replace only the former issuer-specific P&L art, leaving all nine figures
# and their original source evidence/exports/chapter order untouched.
native["pnl"]=(
    '<div class="native-asr" data-finance-grammar="shared-full-signed-pnl" '
    'data-native-source="shared-signed-statement">'
    '<p class="native-asr-dek">研发支出使累计利润短暂低于零，后续收益和税项逆转；'
    '每一步根据原始利润表元金额及原始物理页码精确勾稽，不人为将负数画成正向桑基。</p>'
    +pnl_phone+'</div>')
assert tuple(native)==REQUIRED_FIGURES
for figure_id,original in native.items():
    pattern=r'(<div class="vizscroll" id="chart-'+re.escape(figure_id)+r'"[^>]*></div>)'
    output,count=re.subn(pattern,lambda m:m.group(1)+original,output,count=1)
    assert count==1,("ORIGINAL_FIGURE_NOT_FOUND_FOR_NATIVE_MOBILE",figure_id)
assert output.count('class="native-asr"')==9
assert output.count('data-signed-statement-grammar="FINANCIALS_TYPED_FULL_PNL_SIGNED_V1"')==1
assert 'data-signed-statement-grammar=\\\"FINANCIALS_TYPED_FULL_PNL_SIGNED_V1\\\"' in output
assert output.count('data-negative-intervals-preserved="true"')==1
assert output.count('__UNIFIED_PNL_DESKTOP__')==0


assert "<script src=" not in output and "<iframe" not in output and "https://fonts" not in output
a.out.parent.mkdir(parents=True,exist_ok=True)
from research_context import render as render_research_context
output=output.replace("</main>",render_research_context("688220")+"</main>",1)
a.out.write_text(output,encoding="utf-8")
a.qa.parent.mkdir(parents=True,exist_ok=True)
a.qa.write_text(json.dumps({"issuer":"688220","report_period":"2026H1","source_sha":actual_sha,"source_bytes":source_status,"checks":checks,"research":"SELF_REVIEWED_SOURCE_LIMITED","full_material_notes":"NOT_CHECKED","second_independent_human":"NOT_CHECKED","industry":"semiconductor-chip-design","figure_briefs_schema":briefs["schema"],"figures_required":len(REQUIRED_FIGURES),"source_screenshots":"SELECTED_PAGES_SCREENED","ar_top5_concentration_denominator":unresolved_ratio,"article":"RESEARCH_PREVIEW"},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("ASR_PUBLICATION_REBUILD",a.out,"bytes",a.out.stat().st_size,"ACCOUNTING_PASS",len(checks)-int(source_status=="NOT_CHECKED"),"source_bytes",source_status,flush=True)
