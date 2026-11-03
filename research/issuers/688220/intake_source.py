#!/usr/bin/env python3
"""Source intake only: preserve unmodified SSE 688220 2026H1 report bytes and source text.
Run via GitHub Actions branch; fail closed on issuer, PDF type and date. No financial claim
is certified by token presence. Manual source-coordinate verification is required.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, time, urllib.request
import fitz

ROOT=pathlib.Path(__file__).resolve().parent
URL="https://static.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-08-29/688220_20260829_CEMF.pdf"
OUT=ROOT/"source"; OUT.mkdir(parents=True,exist_ok=True)
TARGET=OUT/"688220_2026H1_20260829_original.pdf"
def download():
    failures=[]
    # First-party SSE gives an anti-bot HTML challenge on GitHub runners; never mistake it for PDF.
    # Verified 224-page complete filing link from Sina's literal '下载公告' action.
    mirror="https://file.finance.sina.com.cn/211.154.219.97:9494/MRGG/CNSESH_STOCK/2026/2026-8/2026-08-29/12571888.PDF"
    for candidate,attempts in ((URL,1),(mirror,3)):
        for attempt in range(attempts):
            try:
                request=urllib.request.Request(candidate,headers={"User-Agent":"Mozilla/5.0 (compatible; FinancialsInVisualsSourceAudit/1.0)","Accept":"application/pdf,*/*","Referer":"https://www.sse.com.cn/"})
                with urllib.request.urlopen(request,timeout=90) as resp:
                    b=resp.read()
                    final=resp.geturl()
                    typ=resp.headers.get("Content-Type","")
                if not b.startswith(b"%PDF-") or len(b)<200_000:
                    raise ValueError("NOT_COMPLETE_PDF: "+str((len(b),typ,final)))
                return b,final
            except Exception as e:
                failures.append(f"{candidate} attempt {attempt+1}: {str(e)[:300]}")
                time.sleep(4)
    raise RuntimeError("ALL_PRIMARY_PDF_DOWNLOADS_FAILED: "+repr(failures))
def normalized(s):
    return re.sub(r"\s+","",s)
def main():
    b,landed=download()
    h=hashlib.sha256(b).hexdigest()
    pdf=fitz.open(stream=b,filetype="pdf")
    assert len(pdf)==224,("EXPECTED_224_PAGE_FULL_REPORT",len(pdf))
    cover=normalized("".join(pdf[i].get_text() for i in range(min(6,len(pdf)))))
    assert "翱捷科技" in cover and "2026" in cover and "半年度报告" in cover, "WRONG_PDF_ISSUER_OR_PERIOD"
    TARGET.write_bytes(b)
    texts=[page.get_text(sort=True) for page in pdf]
    texts_dir=ROOT/"extracted";texts_dir.mkdir(exist_ok=True)
    for start in range(0,len(texts),15):
        parts=[]
        for j in range(start,min(start+15,len(texts))):
            parts.extend((f"\n\n=========== PHYSICAL PDF PAGE {j+1} ===========\n",texts[j]))
        (texts_dir/f"physical_{start+1:03d}_{min(start+15,len(texts)):03d}.txt").write_text("".join(parts),encoding="utf-8")
    terms=[
        "合并资产负债表","合并利润表","合并现金流量表","现金流量表补充资料",
        "营业收入和营业成本","营业收入、营业成本","主营业务分产品",
        "按产品分类","按业务类型","分产品情况","营业收入构成",
        "存货跌价准备","应收账款坏账准备","商誉减值","信用减值损失",
        "研发投入","芯片定制","在手订单","非经常性损益项目",
        "固定资产","无形资产","货币资金","应收账款","存货",
        "与关联方交易","关联交易","前五名客户",
        "总资产","经营活动产生的现金流量净额","资产减值损失",
        "现金及现金等价物的构成","合同负债","开发支出",
    ]
    hits={t:[i+1 for i,s in enumerate(texts) if normalized(t) in normalized(s)] for t in terms}
    index={
        "issuer":"翱捷科技股份有限公司","ticker":"688220","report":"2026年半年度报告",
        "announcement_date":"2026-08-29","official_source_url":URL,
        "download_final_url":landed,"pdf_sha256":h,
        "pdf_bytes":len(b),"pdf_physical_page_count":len(pdf),
        "pdf_header":b[:8].decode("ascii","replace"),"file":"source/"+TARGET.name,
        "cover_issuer_period_match":True,
        "note":"SSE official primary URL linked to this report returned non-PDF HTML on runner; full original filing COPY acquired from exact report download mirror. SSE-vs-mirror byte equivalence NOT_CHECKED; source text search is not row/column semantic verification.",
        "keyword_hits_physical_pdf_pages":hits,
        "pdf_metadata":{k:str(v) for k,v in pdf.metadata.items()}
    }
    (ROOT/"source-manifest.json").write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    statement=set()
    for term in ("合并资产负债表","合并利润表","合并现金流量表","现金流量表补充资料","营业收入和营业成本","非经常性损益项目"):
        statement.update(hits.get(term,[])[:4])
    statement=sorted(set([1]+list(statement)))[:24]
    blockdir=ROOT/"source-blocks";blockdir.mkdir(exist_ok=True)
    for physical in statement:
        page=pdf[physical-1]
        items=[]
        for block in page.get_text("blocks",sort=True):
            x0,y0,x1,y1,text,*_=block
            if text.strip():items.append({"bbox":[round(q,1) for q in (x0,y0,x1,y1)],"text":text})
        (blockdir/f"p{physical:03d}.json").write_text(json.dumps({"physical_page":physical,"page_width_pt":page.rect.width,"blocks":items},ensure_ascii=False,indent=2),encoding="utf-8")
    renderdir=ROOT/"source-images";renderdir.mkdir(exist_ok=True)
    for physical in statement[:10]:
        p=pdf[physical-1]
        pix=p.get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False)
        pix.save(str(renderdir/f"p{physical:03d}.png"))
    print("ORIGINAL_PDF_BYTES_PASS",h,len(b),"physical_pages",len(pdf),"source",landed,flush=True)
    print("INDEX",json.dumps({k:hit[:20] for k,hit in hits.items() if hit},ensure_ascii=False),flush=True)
    print("WRITTEN_TEXT_PAGE_BATCHES",len(list(texts_dir.glob("*.txt"))),"BLOCKS",len(statement),"RENDERS",min(10,len(statement)),flush=True)
if __name__=="__main__": main()
