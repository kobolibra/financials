#!/usr/bin/env python3
"""Build reproducible page-preserving text and topic indexes from real PDF bytes."""
from pathlib import Path
import hashlib,json,re
import fitz
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/"research/two-sector-2026H1-sources.json").read_text())
topics={
 "utility_operation":["发电量","上网电量","售电量","上网电价","来水","利用小时","水电业务","分行业、分产品","境内六座","同一控制下","水资源","业绩驱动"],
 "pharma_operation":["创新药销售","创新药收入","创新药","授权许可","许可收入","对外许可","研发投入","开发支出","资本化","产品分类","分行业、分产品","合作款项","首付款","里程碑","营业收入构成"],
 "indirect_cash":["净利润调节为经营活动现金流量","将净利润调节","固定资产折旧","经营性应收项目","经营性应付项目","存货的减少","经营活动产生的现金流量净额"],
 "risk":["审计报告","同一控制下","现金流量表补充资料","减值准备","合同负债","确认收入","履约义务","业绩承诺"]
}
for x in m["sources"]:
 code=x["code"]; src=ROOT/x["source_path"]; raw=src.read_bytes()
 assert raw.startswith(b"%PDF") and hashlib.sha256(raw).hexdigest()==x["expected_pdf_sha256"]
 pdf=fitz.open(src)
 assert pdf.page_count==x["expected_pages"]
 target=ROOT/"research"/"issuers"/code/"extracted"
 target.mkdir(parents=True,exist_ok=True)
 index=[]
 for no,page in enumerate(pdf,1):
  text=page.get_text(sort=True)
  (target/f"p{no:03d}.txt").write_text(text,encoding="utf-8")
  terms={topic:[t for t in strings if t in text] for topic,strings in topics.items()}
  words=page.get_text("words")
  index.append({"physical_page":no,"text_length":len(text),"topics":{k:v for k,v in terms.items() if v},"word_count":len(words)})
 (target/"topic-index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 for topic in topics:
  matches=[r for r in index if topic in r["topics"]]
  matches.sort(key=lambda r:(-len(r["topics"][topic]),r["physical_page"]))
  print("TOPIC",code,topic,json.dumps(matches[:22],ensure_ascii=False),flush=True)
 for p in ([46,47,48,50,51,54,55,56,57,58,59,60] if code=="600900" else [75,76,77,78,79,80,81,82,83,84]):
  page=pdf[p-1]
  pix=page.get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False)
  path=ROOT/"research"/"issuers"/code/"source-images"/f"p{p:03d}.png"
  path.parent.mkdir(exist_ok=True,parents=True)
  pix.save(path)
 print("FULL_PDF_PAGE_INDEX_SUCCESS",code,pdf.page_count,"pdf-sha",x["expected_pdf_sha256"],flush=True)
