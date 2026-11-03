#!/usr/bin/env python3
"""Local rendered-document QA; passing does NOT mean subjective visual or financial editorial PASS."""
from __future__ import annotations
import argparse,json,pathlib
from playwright.sync_api import sync_playwright
P=argparse.ArgumentParser();P.add_argument("--html",default="public/688220.html");P.add_argument("--out",default="research/issuers/688220/visual-qa");a=P.parse_args()
html=pathlib.Path(a.html).resolve();out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
assert html.exists() and html.stat().st_size>20000,html
bad=[];statuses=[];screenshot_count=0
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for width,height in [(1440,960),(768,1024),(390,844)]:
        page=browser.new_page(viewport={"width":width,"height":height},accept_downloads=True)
        page.on("pageerror",lambda e:bad.append("PAGE_ERROR "+str(e)))
        page.on("console",lambda m:bad.append("CONSOLE_ERROR "+m.text) if m.type=="error" else None)
        page.goto(html.as_uri(),wait_until="load")
        page.wait_for_selector("#chart-flow svg",timeout=15000)
        info=page.evaluate("""() => ({
          scrollWidth:document.documentElement.scrollWidth,
          clientWidth:document.documentElement.clientWidth,
          svg:document.querySelectorAll('.vizscroll svg').length,
          exportButtons:document.querySelectorAll('[data-export]').length,
          evidenceTables:document.querySelectorAll('table.evidence-table').length,
          figures:document.querySelectorAll('figure.figure').length,
          amounts:Array.from(document.querySelectorAll('.vizscroll svg text')).filter(x=>/亿/.test(x.textContent)).length,
          title:document.title,
          mobileFactPanels:document.querySelectorAll('.mobile-facts').length,
          mobileFactsVisible:Array.from(document.querySelectorAll('.mobile-facts')).filter(e=>getComputedStyle(e).display!=='none').length,
          chapterPosition:getComputedStyle(document.querySelector('.chapters')).position,
          images:document.images.length,
          externalScripts:document.querySelectorAll('script[src]').length,
          tofu:document.body.textContent.includes('□')?document.body.textContent.match(/□/g).length:0
        })""")
        assert info["scrollWidth"]<=width+1,(width,"page overflow",info)
        assert info["figures"]==7 and info["svg"]==7 and info["evidenceTables"]==7,(width,info)
        # Verify the actual rendered graphic's semantic edges, NOT just an SVG count
        # or a separate ledger reconciliation. Any aggregate trunk is rejected.
        flow=page.evaluate("""() => {
          const data=JSON.parse(document.getElementById('ledger-data').textContent);
          const edges=[...document.querySelectorAll('#chart-flow svg path[data-flow-role="edge"]')];
          const source=[...document.querySelectorAll('#chart-flow svg rect[data-flow-role="source"]')];
          const sinks=[...document.querySelectorAll('#chart-flow svg rect[data-flow-role="sink"]')];
          const toCents=s => {const parts=String(s).split('.'),neg=parts[0][0]==='-';
            const whole=BigInt(parts[0]); const fraction=BigInt((parts[1]||'').padEnd(2,'0'));
            return whole*100n+(neg?-fraction:fraction);};
          const centsToStr=n=>n.toString();
          const total=toCents(data.facts.rev.yuan);
          let sourceTotal=0n, costTotal=0n,gpTotal=0n;
          const actual={};
          const failures=[];
          for(const x of source){ const key=x.dataset.business; sourceTotal+=toCents(x.dataset.yuan);
            if(!data.facts[key]) failures.push('source key missing: '+key);
          }
          for(const link of edges){
            const key=link.dataset.business; const segment=data.segments.find(s=>s.rev===key);
            if(!segment){failures.push('unmatched segment: '+key);continue;}
            const revenue=toCents(data.facts[segment.rev].yuan);
            const cost=toCents(data.facts[segment.cost].yuan);
            const expected=link.dataset.kind==='cost'?cost:revenue-cost;
            const amount=toCents(link.dataset.yuan);
            if(amount!==expected) failures.push(key+'/'+link.dataset.kind+' wrong ribbon amount');
            const height=Number(link.dataset.width);
            const expHeight=Number(expected)/Number(total)*338;
            if(Math.abs(height-expHeight)>0.00001) failures.push(key+'/'+link.dataset.kind+' falsely scaled width '+height+' versus '+expHeight);
            if(link.dataset.to!==(link.dataset.kind==='cost'?'cogs':'gross_profit')) failures.push('wrong target for '+key);
            if(link.dataset.sourcePage!=='178'||link.dataset.period!=='2026H1'||link.dataset.scope!=='consolidated')failures.push('unverifiable source/scope');
            actual[key+'::'+link.dataset.kind]=(actual[key+'::'+link.dataset.kind]||0)+1;
            if(link.dataset.kind==='cost')costTotal+=amount;else gpTotal+=amount;
          }
          for(const item of data.segments)
            for(const type of ['cost','gp'])if(actual[item.rev+'::'+type]!==1)failures.push('missing/duplicate '+item.rev+'/'+type);
          if(sourceTotal!==total)failures.push('source total mismatch');
          if(costTotal!==toCents(data.facts.cogs.yuan))failures.push('sink cost mismatch');
          if(costTotal+gpTotal!==total)failures.push('all sink mismatch');
          if(sinks.length!==2)failures.push('sink node count '+sinks.length);
          return {edges:edges.length,sources:source.length,sinks:sinks.length,
            costYuan:centsToStr(costTotal),gpYuan:centsToStr(gpTotal),sumYuan:centsToStr(total),
            microscale:edges.filter(x=>x.dataset.business==='other_service_rev').map(x=>Number(x.dataset.width)),
            failures};
        }""")
        assert flow["edges"]==8 and flow["sources"]==4 and flow["sinks"]==2,(width,"real Sankey graph roles",flow)
        assert not flow["failures"],(width,"rendered Sankey invariant violated",flow)
        assert max(flow["microscale"])<0.02,(width,"tiny disclosed test business inflated for visual effect",flow)
        assert info["exportButtons"]==7 and info["externalScripts"]==0 and info["amounts"]>=10
        assert info["mobileFactPanels"]==7,(width,"each graphic requires independent first-order values on mobile",info)
        assert info["mobileFactsVisible"]==(0 if width==1440 else 7),(width,"missing visible amount headlines for mobile/tablet",info)
        assert info["chapterPosition"]==("static" if width==390 else "sticky"),(width,"sticky navigation may obscure phone chart titles",info)
        assert page.locator('a.brand[href="/#companies"]').count()==1
        assert page.locator('a[href="#cash"]').count()>=1
        page.screenshot(path=str(out/f"full_{width}.png"),full_page=True)
        screenshot_count+=1
        if width in (1440,390):
            for figure in ("flow","segment","gp","earnings","cfo","cash","capital"):
                page.locator("#fig-"+figure).screenshot(path=str(out/f"{figure}_{width}.png"))
                screenshot_count+=1
        page.locator('a[href="#cash"]').first.click()
        assert page.url.endswith("#cash"),page.url
        if width==1440:
            with page.expect_download(timeout=10000) as download:
                page.locator('button[data-export="flow"]').click()
            assert download.value.suggested_filename=="688220_2026H1_flow.svg"
        statuses.append({"viewport":width,"scroll_width":info["scrollWidth"],"figures":info["figures"],"svg":info["svg"],"source_tables":info["evidenceTables"],"result":"PASS","editorial_human_view":"NOT_CHECKED"})
        page.close()
    browser.close()
assert not bad,bad
(out/"result.json").write_text(json.dumps({"technical_browser":"PASS","source_pdf_manual_review":"NOT_CHECKED","full_design_editorial":"NOT_CHECKED","production_route":"NOT_CHECKED","viewport":statuses,"errors":bad,"screenshots":screenshot_count},ensure_ascii=False,indent=2)+"\n")
print("ASR_LOCAL_RENDER_QA_PASS",statuses,"screenshots",screenshot_count,flush=True)
