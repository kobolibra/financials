#!/usr/bin/env python3
"""Acquire complete issuer filing bytes in GitHub Actions, not summaries or scraped numbers."""
import hashlib,json,os,re,time,urllib.request
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/"research/two-sector-2026H1-sources.json").read_text())
for item in manifest["sources"]:
    url=item["url"]; last=None
    for attempt in range(3):
        try:
            request=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (Financials in Visuals PDF verification)","Accept":"application/pdf,*/*","Referer":"https://www.cninfo.com.cn/"})
            with urllib.request.urlopen(request,timeout=65) as response:
                data=response.read()
            if not data.startswith(b"%PDF"): raise ValueError("DOWNLOAD_IS_NOT_COMPLETE_PDF "+repr(data[:80]))
            sha=hashlib.sha256(data).hexdigest()
            if sha!=item["expected_pdf_sha256"]: raise ValueError("HISTORICAL_PDF_BYTES_DIFFER "+sha+" expected "+item["expected_pdf_sha256"])
            doc=fitz.open(stream=data,filetype="pdf")
            if doc.page_count!=item["expected_pages"]: raise ValueError(f"PDF_PAGE_COUNT {doc.page_count} != {item['expected_pages']}")
            front=doc[0].get_text()
            if item["code"] not in front or "2026" not in front: raise ValueError("WRONG_ISSUER_OR_YEAR_COVER")
            target=ROOT/item["source_path"];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            records=[]
            terms=["营业收入","营业总收入","经营活动产生的现金流量净额","合并资产负债表","合并利润表","现金流量表","研发","净利润","发电量","创新药","授权"]
            for i in range(doc.page_count):
                page=doc[i]
                txt=page.get_text(sort=True)
                records.append({"physical_page":i+1,"characters":len(txt),"keyphrases":[term for term in terms if term in txt][:7]})
                if i<2 or (item["code"]=="600900" and i+1 in list(range(6,22))+list(range(43,56))) or (item["code"]=="600276" and i+1 in list(range(6,26))+list(range(75,89))):
                    out=ROOT/"research/issuers"/item["code"]/"extracted"/f"p{i+1:03d}.txt"
                    out.parent.mkdir(parents=True,exist_ok=True)
                    out.write_text(txt,encoding="utf-8")
            (ROOT/"research/issuers"/item["code"]/"source-verification.json").write_text(json.dumps({
                "code":item["code"],"issuer_name":item["company"],"source_url":url,
                "downloaded_complete_pdf_sha256":sha,"bytes":len(data),"physical_pages":doc.page_count,
                "source_verified":{"pdf_magic":"PASS","sha_matches_previous_original_corpus":"PASS","cover_issuer_and_year":"PASS","physical_pages":"PASS"},
                "issuer_filings_not_independent_human_review":"NOT_CHECKED",
                "all_material_notes_reviewed":"NOT_CHECKED",
                "page_index":records
             },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            print("COMPLETE_ORIGINAL_PDF_BYTES_PASS",item["code"],sha,len(data),doc.page_count,flush=True)
            print("PAGE_INDEX",item["code"],json.dumps([x for x in records if "合并利润表" in x["keyphrases"] or "经营活动产生的现金流量净额" in x["keyphrases"]][:13],ensure_ascii=False))
            doc.close()
            break
        except Exception as e:
            last=e;print("FETCH_ATTEMPT_FAILED",item["code"],attempt+1,type(e).__name__,str(e)[:350],flush=True)
            if attempt!=2:time.sleep(3)
    else: raise RuntimeError(f"SOURCE_PDF_ACQUISITION_BLOCKED {item['code']}: {last}")
