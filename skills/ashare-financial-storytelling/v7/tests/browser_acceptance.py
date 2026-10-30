from pathlib import Path
import json, sys, hashlib
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];path=root/'outputs/tianfu-research-v7.html'
logs=[];errors=[];results=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in [1440,768,390]:
  page=browser.new_page(viewport={'width':width,'height':900 if width>400 else 844},device_scale_factor=1,accept_downloads=True)
  err=[];requests=[]
  page.on('pageerror',lambda e:err.append(str(e)))
  page.on('request',lambda r:requests.append(r.url) if r.url.startswith('http') else None)
  page.set_content(path.read_text(encoding='utf-8'),wait_until='load',timeout=30000)
  page.wait_for_timeout(250)
  geom=page.evaluate('''()=>({viewport:window.innerWidth,scroll:document.documentElement.scrollWidth,svg:document.querySelectorAll('svg').length,ribbons:document.querySelectorAll('.money-ribbon').length,chapters:document.querySelectorAll('.chapter').length,figures:document.querySelectorAll('figure.exhibit').length,links:[...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.getElementById(a.hash.substring(1))).map(a=>a.hash),svgSizes:[...document.querySelectorAll('svg')].map(s=>({w:Math.round(s.getBoundingClientRect().width),scroll:s.closest('.scroll-x')?.scrollWidth||0}))})''')
  assert geom['scroll']<=width, f"unexpected page overflow at {width}: {geom}"
  assert geom['svg']>=7 and geom['figures']>=9 and geom['ribbons']>=6
  assert not geom['links'], f"dead nav links {geom['links']}"
  focus=page.locator('.money-ribbon').first
  focus.focus();page.wait_for_timeout(120)
  assert page.locator('#floatTip').is_visible(), 'focus tooltip missing'
  page.keyboard.press('Escape');assert not page.locator('#floatTip').is_visible()
  with page.expect_download(timeout=15000) as dl:
   page.locator('button.svg-save').first.click()
  assert dl.value.suggested_filename.endswith('.svg')
  screenshot=root/'qa'/f'v7-{width}-full.png';page.screenshot(path=str(screenshot),full_page=True,animations='disabled')
  assert not err and not requests,f'{err} {requests}'
  result={'viewport':width,'passed':True,'geom':geom,'svg_export':True,'keyboard_tooltip':True,'errors':err,'requests':requests,'screenshot':str(screenshot)}
  results.append(result);print(f'PASS {width}px: {geom["figures"]} figures, {geom["svg"]} svgs, overflow={geom["scroll"]-width}')
  page.close()
 browser.close()
(root/'qa/browser-v7.json').write_text(json.dumps({'html_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cases':results},ensure_ascii=False,indent=2)+'\n',encoding='utf8')