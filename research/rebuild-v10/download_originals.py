#!/usr/bin/env python3
"""Fetch original V10 full-report PDF bytes and source ledger with original SHA-256.
Any mismatch fails the build; never replace original facts with a synthetic PDF.
"""
import pathlib, urllib.request, hashlib, time, sys, fitz
root=pathlib.Path('work')
urls={
 '600036':('additional/600036_2026H1_original.pdf','https://static.cninfo.com.cn/finalpage/2026-08-28/1225531453.PDF','0194f5122575ee8576dbce941fcc10fb171e0cd17c627dd63330da952c52b57c','招商银行'),
 '688111':('financials_v8_case_study/sources/688111_2026H1_original.pdf','https://static.cninfo.com.cn/finalpage/2026-08-20/1225482678.PDF','ec2322dc3a4461eef43045361391c0efe5673794302e329d03c7bbb8a3ad15a4','金山办公'),
 '600519':('financials_v8_case_study/sources/600519_2026H1_original.pdf','https://static.cninfo.com.cn/finalpage/2026-08-15/1225475868.PDF','0e10aa26be46b1cf3cd03f06e834c7fb98d5dd0d661b96f8fddd4af7e846a4f6','贵州茅台'),
 '000333':('financials_v8_case_study/sources/000333_2026H1_original.pdf','https://disc.static.szse.cn/disc/disk03/finalpage/2026-08-29/df25443f-d67a-4cc5-8bd6-6c3e681a9575.PDF','576dd80e353e53296a800b03e9889a9cbb2e8b91fa2ab3c1dace7c10159179b8','美的集团')
}
for code,(path,url,expected,company) in urls.items():
    target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/pdf,*/*'})
            with urllib.request.urlopen(req,timeout=75) as resp: data=resp.read()
            assert data.startswith(b'%PDF-') and hashlib.sha256(data).hexdigest()==expected,(code,'source PDF corrupted')
            pdf=fitz.open(stream=data,filetype='pdf');assert len(pdf)>90,(code,'not original full report')
            text=''.join(p.get_text() for p in list(pdf)[:min(8,len(pdf))]).replace(' ','').replace('\n','')
            assert '2026' in text and (company in text or code in text),(code,'issuer or period mismatch')
            target.write_bytes(data)
            print('ORIGINAL_PDF_PASS',code,'pages',len(pdf),'bytes',len(data),flush=True)
            break
        except Exception as err:
            print('SOURCE_DOWNLOAD_RETRY',code,attempt+1,repr(err),flush=True)
            if attempt==2:raise
            time.sleep(5)
for code in ('688111','600519','000333'):
    src=pathlib.Path('research/rebuild-v10/input-ledgers')/(code+'.json')
    target=root/'financials_v8_case_study/research'/(code+'_2026H1_ledger.json')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(src.read_bytes())
