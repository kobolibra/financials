from pathlib import Path
import urllib.request,urllib.parse,json,re,concurrent.futures,hashlib,pymupdf
BASE=Path(__file__).resolve().parent
queries=[(c,n,y,p) for c,n in [('600900','长江电力'),('600276','恒瑞医药'),('688220','翱捷科技')] for y in [2024,2025,2026] for p in ['第一季度报告','半年度报告','第三季度报告','年度报告'] if not(y==2026 and p=='年度报告')]+[('600025','华能水电',2026,'半年度报告')]
def get(q):
 c,n,y,p=q; key=f'{c}_{y}'+{'第一季度报告':'Q1','半年度报告':'H1','第三季度报告':'Q3','年度报告':'FY'}[p]
 if (BASE/(key+'.pdf')).exists():return
 data=urllib.parse.urlencode({'pageNum':1,'pageSize':30,'column':'sse','tabName':'fulltext','searchkey':f'{n} {y}年{p}','seDate':'2024-01-01~2026-11-10','isHLtitle':'true'}).encode()
 try:
  req=urllib.request.Request('https://www.cninfo.com.cn/new/hisAnnouncement/query',data=data,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.cninfo.com.cn/'})
  j=json.load(urllib.request.urlopen(req,timeout=60)); (BASE/(key+'_query.json')).write_text(json.dumps(j,ensure_ascii=False,indent=2))
  choices=[a for a in j.get('announcements',[]) if a['secCode']==c and '摘要' not in a['announcementTitle'] and re.sub('<[^>]+>','',a['announcementTitle']).endswith(f'{y}年{p}')]
  if not choices:print('MISSING',key,flush=True);return
  a=choices[0];url='https://static.cninfo.com.cn/'+a['adjunctUrl']; b=urllib.request.urlopen(url,timeout=90).read();assert b[:4]==b'%PDF'
  path=BASE/(key+'.pdf');path.write_bytes(b);d=pymupdf.open(path)
  (BASE/(key+'.txt')).write_text('\n'.join(f'\n=== PHYSICAL PAGE {i+1} ===\n'+pg.get_text() for i,pg in enumerate(d)))
  (BASE/(key+'_source.json')).write_text(json.dumps(dict(id=key,url=url,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),pages=len(d),file=path.name),indent=2));print('OK',key,len(d),flush=True)
 except Exception as e:print('ERROR',key,str(e),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:list(ex.map(get,queries))
