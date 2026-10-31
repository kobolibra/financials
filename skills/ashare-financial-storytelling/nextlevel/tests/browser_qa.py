from playwright.sync_api import sync_playwright
from pathlib import Path
import json, argparse
parser=argparse.ArgumentParser()
parser.add_argument('--html',default=None,help='Path to generated standalone article; defaults to public/optical-2026h1.html')
parser.add_argument('--out',default=None,help='QA JSON path')
args=parser.parse_args()
root=Path(__file__).resolve().parents[4]
html_path=Path(args.html).resolve() if args.html else root/'public/optical-2026h1.html'
out=Path(args.out).resolve() if args.out else Path(__file__).resolve().parents[1]/'qa/browser.json'
assert html_path.exists(),f'Missing article: {html_path}'
results=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in [1440,768,390]:
  page=b.new_page(viewport={'width':width,'height':900},device_scale_factor=1)
  page.emulate_media(reduced_motion='reduce')
  errors=[];external=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('request',lambda r:external.append(r.url) if r.url.startswith('http') else None)
  page.set_content(html_path.read_text(encoding='utf-8'),wait_until='load')
  info=page.evaluate("""()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,svgs:document.querySelectorAll('svg.figure-svg').length,figures:document.querySelectorAll('figure.figure').length,iframes:document.querySelectorAll('iframe').length})""")
  page.locator('a[href="#cash"]').click()
  position=page.evaluate("""()=>({hash:location.hash,top:document.getElementById('cash').getBoundingClientRect().top})""")
  ok=info['width']==info['scroll'] and info['svgs']==6 and info['figures']==6 and info['iframes']==0 and position['hash']=='#cash' and abs(position['top'])<120 and not errors and not external
  results.append({'viewport':width,'passed':ok,'layout':info,'anchor':position,'errors':errors,'external_requests':external})
  page.close()
 b.close()
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({'cases':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(results,ensure_ascii=False))
if not all(x['passed'] for x in results):raise SystemExit('FAIL')
