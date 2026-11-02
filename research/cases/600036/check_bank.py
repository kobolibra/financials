from pathlib import Path
import json,re,fitz,hashlib
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent
src=root/'cmb_verified_0194f512.pdf'; report=root/'600036.html'; html=report.read_text()
sha=hashlib.sha256(src.read_bytes()).hexdigest()
assert sha=='0194f5122575ee8576dbce941fcc10fb171e0cd17c627dd63330da952c52b57c'
d=fitz.open(src); assert len(d)==247
# Verify selected exact original values appear on mapped PDF pages; this is a literal source locator, not semantic review.
source_numbers={
 13:['112,022','39,855','26,304','52,912','29,177','90,737','76,919','76,445'],
 16:['8,279','(2,342)','5,937'],
 23:['2,878,139','2,638,367','2,335,473','2,310,519','10,162,498'],
 30:['267,222','25,463','6,698','(28,371)','(476)','270,536'],
 31:['14.07','14.16','7,928,939','7,540,202'],
 34:['42,888','45,703','2,146','52,036','37,057'],
}
for p,vals in source_numbers.items():
 s=d[p-1].get_text()
 for v in vals:
  assert v in s,(p,v)
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path="/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None)
 for width in (1440,768,390):
  page=browser.new_page(viewport={'width':width,'height':900},accept_downloads=True)
  errors=[]; page.on('pageerror', lambda e:errors.append(str(e)))
  page.set_content(html,wait_until='load')
  n=page.locator('figure').count();svg=page.locator('svg').count(); tables=page.locator('table').count()
  assert (n,svg,tables)==(9,9,9),(n,svg,tables)
  measure=page.evaluate('({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})')
  assert measure['sw']<=width+1,(width,measure)
  assert not errors,(width,errors)
  page.screenshot(path=str(root/f'bank_{width}_full.png'),full_page=True)
  if width==1440:
   page.locator('a[href="#credit"]').click()
   assert '#credit' in page.url
   with page.expect_download() as dl:page.locator('figure button.svg-export').first.click()
   assert dl.value.suggested_filename.endswith('.svg')
  results.append({'width':width,'figures':n,'svg':svg,'tables':tables,'overflow':False,'js_errors':errors})
  page.close()
 browser.close()
reportjson={'case':'CMB 2026H1','source_sha':sha,'pdf_pages':len(d),'figure_count':9,'literal_page_source_values':sum(map(len,source_numbers.values())),'browser':results,'actual_url_navigation':'NOT_CHECKED (requires served GitHub Action)'}
(root/'qa_bank_browser.json').write_text(json.dumps(reportjson,ensure_ascii=False,indent=2))
print(json.dumps(reportjson,ensure_ascii=False,indent=2))