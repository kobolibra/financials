from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
import threading
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'outputs/tianfu-h1-v6.html';OUT=ROOT/'qa/browser';OUT.mkdir(parents=True,exist_ok=True)
res={'html_sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),'cases':[]}
server=ThreadingHTTPServer(('127.0.0.1',18765),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for w,h in [(1440,900),(768,900),(390,844)]:
        page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
        errors=[];requests=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url) if r.url.startswith('http') else None)
        page.set_content(TARGET.read_text(encoding='utf-8'),wait_until='load')
        page.screenshot(path=str(OUT/f'{w}-full.png'),full_page=True)
        overview=page.locator('header').bounding_box(); main=page.locator('#economics').bounding_box()
        page.screenshot(path=str(OUT/f'{w}-hero.png'),full_page=False)
        doc=page.evaluate('''() => ({
          inner:innerWidth,scroll:document.documentElement.scrollWidth,
          stage:document.querySelectorAll('svg').length,
          ribbons:document.querySelectorAll('.money-ribbon').length,
          waterfalls:document.querySelectorAll('svg.waterfall').length,
          headings:Array.from(document.querySelectorAll('h2')).map(x=>x.textContent.trim()).slice(0,12),
          links:Array.from(document.querySelectorAll('a[href^="#"]')).map(x=>x.getAttribute('href').slice(1)).filter(id=>!document.getElementById(id)),
          svgWidths:Array.from(document.querySelectorAll('.viz-scroll svg')).map(x=>Math.round(x.getBoundingClientRect().width))
        })''')
        page.locator('.money-ribbon').first.hover(force=True)
        doc['hover']=page.locator('.tooltip').is_visible()
        page.locator('.money-ribbon').first.focus()
        doc['focus']=page.locator('.tooltip').is_visible()
        with page.expect_download() as dl:
            page.locator('button[data-export]').first.click()
        file=dl.value
        doc['export']=file.suggested_filename.endswith('.svg')
        doc['errors']=errors;doc['requests']=requests
        doc['passed']=all([doc['scroll']<=w+1,doc['ribbons']>=6,doc['waterfalls']>=4,doc['hover'],doc['focus'],doc['export'],not errors,not requests,not doc['links']])
        res['cases'].append({'viewport':w,**doc})
        page.close()
    browser.close()
server.shutdown()
(OUT/'acceptance.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
print(json.dumps(res,ensure_ascii=False,indent=2))