#!/usr/bin/env python3
"""Fail-closed acquisition of the original 601628 full report on a networked runner.

No screenshot/web snippet is accepted in place of PDF bytes. Original complete
PDF goes to version control with per-page extraction/sha and line/column QA.
"""
import hashlib,json,urllib.request,time
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]
cfg=json.loads((ROOT/"research/issuers/601628/source-manifest.json").read_text())
base=ROOT/"research/issuers/601628"
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
        if doc.page_count<75: raise RuntimeError("SUMMARY_NOT_COMPLETE_REPORT "+str(doc.page_count))
        front=" ".join(doc[i].get_text() for i in range(min(3,len(doc))))
        if "601628" not in front or "2026" not in front or "中国人寿" not in front or "半年度报告" not in front:
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
 "statements":["合并资产负债表","合并利润表","合并现金流量表","资产负债表","现金流量表","保险服务收入","承保财务损益"],
 "insurance":["合同服务边际","新业务价值","未到期责任负债","保险合同负债","分出再保险","浮动收费法","非金融风险调整","保险获取现金流量"],
 "cash":["经营活动产生的现金流量净额","净利润调节为经营活动现金流量","现金及现金等价物","现金流量表补充资料"],
 "investments":["公允价值变动损益","其他权益工具投资","总投资收益","投资收益率","金融资产减值","利率风险","偿付能力"],
 "risks":["审计","重述","重列","追溯","关联方","风险","限制","受限","诉讼"]
}
ext=base/"extracted";ext.mkdir(exist_ok=True)
for i,page in enumerate(doc):
    txt=page.get_text(sort=True)
    (ext/f"p{i+1:03d}.txt").write_text(txt,encoding="utf-8")
    index.append({"page":i+1,"chars":len(txt),"terms":{k:[t for t in terms[k] if t in txt] for k in terms if any(t in txt for t in terms[k])}})
(ext/"topic-index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n")
# Selected visual primary source captures: DO NOT pretend these cover every original note.
screens=base/"source-images";screens.mkdir(exist_ok=True)
image_pages=set([1,2,3,4,5,6,8,13,17,18,19,20,21,22,23,40,41,42,43,44,45,46,47,48,49,50])
for r in index:
 if "statements" in r["terms"] or "cash" in r["terms"]:
    if 35<=r["page"]<=65: image_pages.add(r["page"])
for pg in sorted(p for p in image_pages if p<=len(doc)):
    page=doc[pg-1]
    if pg not in (1,2,3,4,5,6,8,17,18,19,20,21,22,23) and not (35<=pg<=65):continue
    pix=page.get_pixmap(matrix=fitz.Matrix(.9,.9),alpha=False)
    pix.save(screens/f"p{pg:03d}.png")
source={
 "code":"601628","company":cfg["company"],"period":"2026H1","official_full_pdf_url":url,"source_pdf":cfg["source_path"],
 "sha256":sha,"bytes":len(data),"physical_pages":len(doc),
 "checks":{"pdf_magic":"PASS","full_report_not_summary":"PASS","issuer_period_cover":"PASS","physical_page_count":"PASS","sse_exact_byte_identity":"NOT_CHECKED","all_notes_independent_review":"NOT_CHECKED"},
 "topics":index
}
# Optional SSE cross-identity: it is not proof if blocked or emits HTML.
try:
 q=urllib.request.Request(cfg["sse_disclosure_full_pdf"],headers={"User-Agent":"Mozilla/5.0","Accept":"application/pdf","Referer":"https://www.sse.com.cn/"})
 with urllib.request.urlopen(q,timeout=25) as r: sse=r.read()
 if sse[:4]==b"%PDF":
    source["sse_sha256"]=hashlib.sha256(sse).hexdigest()
    source["checks"]["sse_exact_byte_identity"]="PASS" if sse==data else "FAIL"
 else: source["sse_fetch_status"]="RETURNED_NON_PDF"
except Exception as e: source["sse_fetch_status"]="BLOCKED_"+type(e).__name__
(base/"source-verification.json").write_text(json.dumps(source,ensure_ascii=False,indent=2)+"\n")
print("PDF_BYTE_SHA_AND_PHYSICAL_PAGES_PASS",sha,len(data),len(doc),flush=True)
print("SOURCE_TOPICS",json.dumps([x for x in index if "cash" in x["terms"] or "insurance" in x["terms"]][:50],ensure_ascii=False),flush=True)
print("SSE_EQUIVALENCE",source["checks"]["sse_exact_byte_identity"],flush=True)
