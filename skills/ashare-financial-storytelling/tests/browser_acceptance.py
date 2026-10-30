"""Real Chromium browser gate: desktop, mobile, hover/focus, export, semantics, no remote assets."""
from pathlib import Path
import sys,json,hashlib
from playwright.sync_api import sync_playwright
input=Path(sys.argv[1]);outdir=Path(sys.argv[2]);outdir.mkdir(parents=True,exist_ok=True)
html=input.read_text(encoding='utf-8');out={}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for name,(w,h) in {'desktop':(1440,900),'tablet':(768,1024),'mobile':(390,844)}.items():
  page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1,accept_downloads=True)
  js_errors=[];reqs=[]
  page.on('pageerror',lambda err:js_errors.append(str(err)))
  page.on('request',lambda r:reqs.append(r.url))
  page.set_content(html,wait_until='load')
  flow=page.locator('.ribbon'); count=flow.count()
  flow.first.hover(force=True);hover=page.locator('.tooltip').evaluate('(e)=>getComputedStyle(e).display!="none"')
  flow.first.focus();focus=page.locator('.tooltip').evaluate('(e)=>getComputedStyle(e).display!="none"')
  with page.expect_download() as dl:page.locator('button[data-export]').click()
  download=dl.value
  has_overflow=page.evaluate('document.documentElement.scrollWidth > window.innerWidth+2')
  figure_scroll=page.locator('.svg-scroller').evaluate('(e)=>e.scrollWidth>e.clientWidth')
  bad_anchors=page.locator('.nav a').evaluate_all('(xs)=>xs.filter(x=>!document.querySelector(x.hash)).map(x=>x.hash)')
  missing=page.locator('.stat-num').evaluate_all('(xs)=>xs.some(x=>!x.textContent.trim())')
  page.screenshot(path=str(outdir/f'{name}.png'),full_page=True)
  out[name]={'viewport':w,'ribbons':count,'tooltip_hover':hover,'tooltip_focus':focus,'svg_download':download.suggested_filename,'overflow':has_overflow,'chart_scrolled':figure_scroll,'bad_anchors':bad_anchors,'missing_key_metrics':missing,'console_errors':js_errors,'requests':reqs}
  page.close()
 browser.close()
passed=all(x['ribbons']>=4 and x['tooltip_hover'] and x['tooltip_focus'] and x['svg_download'].endswith('.svg') and not x['overflow'] and not x['bad_anchors'] and not x['console_errors'] and not x['requests'] for x in out.values())
(outdir/'acceptance.json').write_text(json.dumps({'passed':passed,'html_sha256':hashlib.sha256(html.encode()).hexdigest(),'tests':out},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':passed,'tests':out},ensure_ascii=False,indent=2))
if not passed:sys.exit(1)