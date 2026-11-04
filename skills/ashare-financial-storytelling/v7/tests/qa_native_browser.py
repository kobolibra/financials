#!/usr/bin/env python3
"""Offline CJK 1440/768/390 QA for original-yuan native optical art."""
import argparse,hashlib,json,re
from pathlib import Path
from playwright.sync_api import sync_playwright

ap=argparse.ArgumentParser()
ap.add_argument("--out",default="optical-native-visual-qa")
out=Path(ap.parse_args().out);out.mkdir(parents=True,exist_ok=True)
ROOT=Path(__file__).resolve().parents[4]
records=[]
with sync_playwright() as p:
    browser=p.chromium.launch(args=["--no-sandbox"])
    for code in ("300394","300502"):
        file=ROOT/"public"/(code+".html")
        sha=hashlib.sha256(file.read_bytes()).hexdigest()
        for width in (1440,768,390):
            page=browser.new_page(viewport={"width":width,"height":900})
            page.goto(file.resolve().as_uri(),wait_until="load")
            n=page.locator("figure.has-native-finance").count()
            assert n>=9,(code,width,"MISSING_MONEY_NATIVE_FIGURES",n)
            assert page.locator(".hero-svg").count()==1,(code,"DESKTOP_ORIGINAL_LOST")
            assert page.evaluate("document.documentElement.scrollWidth")<=width+1,(code,width,"ROOT_OVERFLOW")
            graph=page.evaluate("""() => {
              const s=document.querySelector('.native-money-svg');
              return {sources:[...s.querySelectorAll('.native-money-source')].map(x=>[+x.dataset.exactYuan,+x.getAttribute('width')]),
              sinks:[...s.querySelectorAll('.native-money-sink')].map(x=>[+x.dataset.exactYuan,+x.getAttribute('width')]),
              ribbons:[...s.querySelectorAll('.native-money-ribbon')].map(x=>({yuan:+x.dataset.exactYuan,d:x.getAttribute('d')}))};
            }""")
            rev=sum(x[0] for x in graph["sources"])
            assert abs(sum(x[0] for x in graph["sinks"])-rev)<.001
            assert abs(sum(x["yuan"] for x in graph["ribbons"])-rev)<.001
            for value,width_svg in graph["sources"]+graph["sinks"]:
                assert abs(width_svg-value/rev*302)<1e-7,(code,"NODE_REAL_MONEY_AREA")
            for edge in graph["ribbons"]:
                m=re.match(r"M([0-9.]+),65 C.*?L([0-9.]+),276 C([0-9.]+),200 [0-9.]+,130 ([0-9.]+),65 Z",edge["d"])
                assert m,(code,"INVALID_RIBBON_PATH",edge["d"])
                assert abs(float(m.group(4))-float(m.group(1))-edge["yuan"]/rev*302)<1e-6,(code,"FALSE_RIBBON_AREA")
            if width in (768,390):
                figures=page.evaluate("""() => [...document.querySelectorAll('figure.has-native-finance')].map(f=>{
                  const n=f.querySelector('.native-finance'),old=f.querySelector('.chart-shell'),svg=n.querySelector('svg');
                  const graphic=svg||n;const r=graphic.getBoundingClientRect();
                  return {active:getComputedStyle(n).display!=='none',oldHidden:getComputedStyle(old).display==='none',
                    inner:n.scrollWidth,visible:n.clientWidth,width:r.width,
                    clipped:r.right>f.getBoundingClientRect().right+2};
                })""")
                assert all(z["active"] and z["oldHidden"] and z["inner"]<=z["visible"]+2 and z["width"]>220 and not z["clipped"] for z in figures),(code,width,"REAL_NATIVE_FIGURE_CLIP",figures)
            else:
                assert page.locator(".chart-shell .hero-svg:visible").count()==1
                with page.expect_download(timeout=10000) as event:
                    page.locator("figure.exhibit .svg-save").first.click()
                assert event.value.suggested_filename.endswith(".svg")
            img=out/(f"{code}_{width}.png");page.screenshot(path=str(img),full_page=True)
            page.locator("figure.exhibit").first.screenshot(path=str(out/f"{code}_figure01_{width}.png"))
            if width==390:
                for chart_idx in (2,5,8):
                    page.locator("figure.exhibit").nth(chart_idx).screenshot(path=str(out/f"{code}_figure{chart_idx+1:02d}_{width}.png"))
            records.append({"issuer":code,"width":width,"figures":n,"money_area":"PASS","sha256":sha,"screenshot_sha256":hashlib.sha256(img.read_bytes()).hexdigest()})
            page.close()
    browser.close()
(out/"result.json").write_text(json.dumps({"cases":records,"second_human_review":"NOT_CHECKED"},ensure_ascii=False,indent=2)+"\n")
assert len(records)==6
print("OPTICAL_NATIVE_MOBILE_REAL_CJK_SIX_SCREENSHOT_SOURCE_PASS")
