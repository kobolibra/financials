from pathlib import Path
import urllib.request,hashlib,json,concurrent.futures,fitz
BASE=Path(__file__).resolve().parent
SOURCES={'600900_2025Q1':'2025-04-30/1223421165','600900_2026Q1':'2026-04-30/1225262110','600025_2026H1':'2026-08-26/1225504979','600900_2026Q3':'2026-10-31/1225648852','600276_2026Q3':'2026-10-28/1225629197','600900_2025Q3':'2025-10-31/1224776945','688220_2025Q3':'2025-10-31/1224769356','600900_2025FY':'2026-04-30/1225262036','688099_2026H1':'2026-08-20/1225482822','600196_2026H1':'2026-08-26/1225505529'}
def run(item):
 name, suffix=item; url='https://static.cninfo.com.cn/finalpage/'+suffix+'.PDF'; path=BASE/(name+'.pdf')
 b=path.read_bytes() if path.exists() else urllib.request.urlopen(url,timeout=90).read()
 assert b[:4]==b'%PDF'; path.write_bytes(b); d=fitz.open(path)
 (BASE/(name+'.txt')).write_text('\n'.join(f'\n=== PHYSICAL PAGE {i+1} ===\n'+p.get_text() for i,p in enumerate(d)))
 return dict(id=name,url=url,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),pages=len(d),file=path.name)
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as e:
 out=list(e.map(run,SOURCES.items()))
(BASE/'manifest.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
