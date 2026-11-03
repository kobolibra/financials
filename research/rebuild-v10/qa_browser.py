from pathlib import Path
import threading, http.server, json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).parent/'site';OUT=Path(__file__).parent/'screens';OUT.mkdir(exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def log_message(self,*args):pass
httpd=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=httpd.serve_forever,daemon=True).start()
BASE='http://127.0.0.1:'+str(httpd.server_address[1]);errors=[];report=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--disable-dev-shm-usage'])
 for code in ('688111','600519','000333','600036'):
  for w,h in ((1440,900),(768,960),(390,844)):
   page=b.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
   page.on('pageerror',lambda err:errors.append(str(err)))
   page.set_content((ROOT/(code+'.html')).read_text(),wait_until='load',timeout=20000)
   assert page.locator('figure.graphic').count()>=7,(code,w,'missing figures')
   assert page.locator('.evidence-table').count()==page.locator('figure.graphic').count()
   measures=page.evaluate('''() => ({cw:document.documentElement.clientWidth,sw:document.documentElement.scrollWidth,bw:document.body.scrollWidth,figures:document.querySelectorAll('figure').length,images:[...document.images].length,scripts:[...document.scripts].filter(x=>x.src).length})''')
   assert measures['sw']<=w+2,(code,w,measures)
   assert measures['scripts']==0,(code,'external scripts')
   nav=page.locator('a[href="#cash"]').first
   assert page.locator('#cash').count()==1
   assert nav.get_attribute('href')=='#cash'
   screenshot=OUT/f'{code}_{w}_hero.png';page.screenshot(path=str(screenshot),full_page=False)
   if w==1440:
    page.locator('figure.graphic').first.scroll_into_view_if_needed();page.screenshot(path=str(OUT/f'{code}_{w}_first_figure.png'),full_page=False)
    page.locator('figure.graphic').last.scroll_into_view_if_needed();page.screenshot(path=str(OUT/f'{code}_{w}_last_figure.png'),full_page=False)
   if w==390:
    page.locator('figure.graphic').first.scroll_into_view_if_needed();page.screenshot(path=str(OUT/f'{code}_{w}_first_figure.png'),full_page=False)
   report.append(dict(code=code,width=w,status='PASS',**measures))
   page.close()
 b.close()
httpd.shutdown()
assert not errors,errors
(Path(__file__).parent/'qa_browser.json').write_text(json.dumps({'report':report,'js_errors':errors,'result':'PASS'},indent=2))
print('ALL PASSED',len(report),json.dumps(report,indent=2))