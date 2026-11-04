#!/usr/bin/env python3
"""Fail-closed acquisition of the original 601919 full report on a networked runner.

No screenshot/web snippet is accepted in place of PDF bytes. Original complete
PDF goes to version control with per-page extraction/sha and line/column QA.
"""
import hashlib,json,urllib.request,time
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]
cfg=json.loads((ROOT/"research/issuers/601919/source-manifest.json").read_text())
base=ROOT/"research/issuers/601919"
out=ROOT/cfg["source_path"]
out.parent.mkdir(parents=True,exist_ok=True)
url=cfg["main_2026h1_pdf"]
data=None
for attempt in range(3):
    try:
        q=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (Financials in Visuals filing verification)","Accept":"application/pdf,*/*","Referer":"https://www.cninfo.com.cn/"})
        with urllib.request.urlopen(q,timeout=75) as r: candidate=r.read()
        if candidate[:4]!=b"%PDF": raise RuntimeError("RESPONSE_NOT_PDF "+repr(candidate[:60]))
        doc=fitz.open(stream=candidate,filetype="pdf")
        if doc.page_count<150: raise RuntimeError("SUMMARY_NOT_COMPLETE_REPORT "+str(doc.page_count))
        if doc.page_count != cfg["expected_physical_pages_from_official_cover"]: raise RuntimeError("PHYSICAL_PAGE_COUNT_CONFLICT_WITH_OFFICIAL_COVER "+str(doc.page_count))
        front=" ".join(doc[i].get_text() for i in range(min(3,len(doc))))
        if "601919" not in front or "2026" not in front or "中远海控" not in front or "半年度报告" not in front:
            raise RuntimeError("WRONG_ISSUER_PERIOD_OR_DOCUMENT")
        data=candidate;break
    except Exception as ex:
        print("ORIGINAL_ACQUISITION_ATTEMPT",attempt+1,type(ex).__name__,str(ex)[:200],flush=True)
        if attempt==2: raise
        time.sleep(3)
if data is None: raise RuntimeError("ORIGINAL_PDF_NOT_ACQUIRED")
out.write_bytes(data)
sha=hashlib.sha256(data).hexdigest()
index=[]
terms={
 "statements":["合并资产负债表","合并利润表","合并现金流量表","现金流量表补充资料","合并股东权益变动表","分部信息"],
 "shipping":["国际航线单箱收入","运输货量","标准箱","TEU","单箱","运价","运量","运力","船舶","航线","燃油","供应链","集装箱航运","海运业务"],
 "terminals":["码头","吞吐量","装卸","泊位","港口投资"],
 "cash":["经营活动产生的现金流量净额","净利润调节为经营活动现金流量","现金及现金等价物","投资活动产生的现金流量净额","购建固定资产","船舶建造"],
 "capital":["使用权资产","租赁负债","融资租赁","分红","股利","股份回购","资本支出","合同负债","资产减值","公允价值"],
 "risk":["审阅报告","审计","重述","重列","追溯","关联方","受限","限制","诉讼","承诺","或有事项","资产负债表日后事项","外币折算"]
}
ext=base/"extracted";ext.mkdir(exist_ok=True)
for i,page in enumerate(doc):
    txt=page.get_text(sort=True)
    (ext/f"p{i+1:03d}.txt").write_text(txt,encoding="utf-8")
    index.append({"page":i+1,"chars":len(txt),"terms":{k:[t for t in terms[k] if t in txt] for k in terms if any(t in txt for t in terms[k])}})
(ext/"topic-index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n")
# Selected visual primary source captures: DO NOT pretend these cover every original note.
screens=base/"source-images";screens.mkdir(exist_ok=True)
image_pages=set([1,2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,90,100])
for r in index:
 if "statements" in r["terms"] or "cash" in r["terms"]:
    if 45<=r["page"]<=85:image_pages.add(r["page"])
for pg in sorted(p for p in image_pages if p<=len(doc)):
    pix=doc[pg-1].get_pixmap(matrix=fitz.Matrix(.85,.85),alpha=False)
    pix.save(screens/f"p{pg:03d}.png")
source={
 "code":"601919","company":cfg["company"],"period":"2026H1","official_full_pdf_url":url,"source_pdf":cfg["source_path"],
 "sha256":sha,"bytes":len(data),"physical_pages":len(doc),
 "checks":{"pdf_magic":"PASS","full_report_not_summary":"PASS","issuer_period_cover":"PASS","physical_page_count":"PASS","sse_exact_byte_identity":"NOT_CHECKED","all_notes_independent_review":"NOT_CHECKED"},
 "topics":index
}
# No second official exchange PDF bytes have been acquired; never infer equivalence.
source["checks"]["sse_exact_byte_identity"]="NOT_CHECKED"
source["source_unit_warning"]="BASIC_STOCK_FLOW_STATEMENTS_IN_YUAN_SHIPPING_SEGMENT_IN_RMB_THOUSANDS_AND_USD_THOUSANDS; TEU_VOLUME_AND_REVENUE_METRICS_MUST_NOT_BE_ADDED"
source["review_status_note"]="Original front calls half-year statements unaudited, but whether a specific limited-review report exists must be read and proven from the actual 178-page source before publishing"
(base/"source-verification.json").write_text(json.dumps(source,ensure_ascii=False,indent=2)+"\n")
print("SHIPPING_ORIGINAL_FULL_PDF_SHA_PHYSICAL_PAGES_PASS",sha,len(data),len(doc),flush=True)
print("SHIPPING_TOPIC_INDEX_HITS",json.dumps([x for x in index if "shipping" in x["terms"] or "cash" in x["terms"]][:60],ensure_ascii=False),flush=True)
print("OTHER_SOURCE_BYTES_EQUIVALENCE_NOT_CHECKED",flush=True)
