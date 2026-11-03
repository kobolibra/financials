#!/usr/bin/env python3
"""Real offline Chromium + graphic source-flow QA; no claim of independent human approval."""
from __future__ import annotations
import argparse, json, pathlib
from decimal import Decimal as D
from playwright.sync_api import sync_playwright
P=argparse.ArgumentParser()
P.add_argument("--html",default="public/688220.html")
P.add_argument("--out",default="research/issuers/688220/visual-qa")
a=P.parse_args()
html=pathlib.Path(a.html).resolve()
out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
ledger=json.loads((pathlib.Path(__file__).parent/"source-ledger.json").read_text(encoding="utf-8"))
facts=ledger["facts"]
expected_cost=sum((D(facts[q["cost"]]["yuan"]) for q in ledger["segments"]),D(0))
expected_profit=sum((D(facts[q["rev"]]["yuan"])-D(facts[q["cost"]]["yuan"]) for q in ledger["segments"]),D(0))
assert html.exists() and html.stat().st_size>20000,html
errors=[];statuses=[];screenshots=0
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True)
 for width,height in ((1440,960),(768,1024),(390,844)):
  page=browser.new_page(viewport={"width":width,"height":height},accept_downloads=True)
  page.on("pageerror",lambda e:errors.append("JS "+str(e)))
  page.on("console",lambda m:errors.append("CONSOLE "+m.text) if m.type=="error" else None)
  page.goto(html.as_uri(),wait_until="load")
  page.wait_for_selector("#chart-flow svg",timeout=15000)
  info=page.evaluate("""() => ({
    scrollWidth:document.documentElement.scrollWidth,
    clientWidth:document.documentElement.clientWidth,
    figures:document.querySelectorAll('figure.figure').length,
    svg:document.querySelectorAll('.vizscroll svg').length,
    tables:document.querySelectorAll('table.evidence-table').length,
    exports:document.querySelectorAll('[data-export]').length,
    mobilePanels:document.querySelectorAll('.mobile-facts').length,
    mobileVisible:[...document.querySelectorAll('.mobile-facts')].filter(e=>getComputedStyle(e).display!=='none').length,
    navPosition:getComputedStyle(document.querySelector('.chapters')).position,
    bodyExternalScripts:document.querySelectorAll('script[src]').length,
    ribbon:[...document.querySelectorAll('#chart-flow path.money-ribbon')].map(e=>({
      source:e.dataset.source, kind:e.dataset.kind, amount:e.dataset.valueYuan, bboxHeight:e.getBBox().height,
      title:e.querySelector('title')?.textContent||''
    })),
    semanticFigures:[...document.querySelectorAll('figure[data-accounting-family]')].map(e=>e.dataset.accountingFamily)
  })""")
  assert info["scrollWidth"]<=width+1,(width,"document scrolls horizontally",info)
  assert info["figures"]==info["svg"]==info["tables"]==info["exports"]==9,(width,info)
  assert info["mobilePanels"]==9 and info["mobileVisible"]==(0 if width==1440 else 9),(width,"invisible financial answer on phone",info)
  assert info["navPosition"]==("static" if width==390 else "sticky"),(width,info)
  assert info["bodyExternalScripts"]==0,(width,"offline must need no external JS",info)
  assert len(info["ribbon"])==7,(width,"4 cost ribbons and 3 nonzero GP ribbons required",info["ribbon"])
  assert len({r["source"] for r in info["ribbon"]})==4
  assert all(D(r["amount"])>0 and r["bboxHeight"]>0 and r["title"] for r in info["ribbon"]),(width,"fake/empty ribbon")
  cost=sum((D(r["amount"]) for r in info["ribbon"] if r["kind"]=="cost"),D(0))
  profit=sum((D(r["amount"]) for r in info["ribbon"] if r["kind"]=="profit"),D(0))
  assert abs(cost-expected_cost)<=D("0.02") and abs(profit-expected_profit)<=D("0.02"),(width,"money-flow totals wrong",cost,profit)
  assert "signed-pnl" in info["semanticFigures"] and "equal-total-date-stock" in info["semanticFigures"]
  assert page.locator("a.brand[href='/#companies']").count()==1
  assert page.locator("a[href='#cash']").count()>=1
  page.screenshot(path=str(out/f"full_{width}.png"),full_page=True)
  screenshots+=1
  if width in (1440,390):
   for figure in ("flow","segment","gp","pnl","earnings","cfo","cash","balance","capital"):
    page.locator("#fig-"+figure).screenshot(path=str(out/f"{figure}_{width}.png"))
    screenshots+=1
  page.locator('a[href="#cash"]').first.click()
  assert page.url.endswith("#cash"),page.url
  if width==1440:
   for name in ("flow","pnl","balance"):
    with page.expect_download(timeout=12000) as item:
     page.locator('button[data-export="'+name+'"]').click()
    assert item.value.suggested_filename=="688220_2026H1_"+name+".svg"
  statuses.append({"width":width,"financial_figures":9,"money_flow_positive_ribbons":7,
                   "source_tables":9,"mobile_numeric_answers":info["mobileVisible"],
                   "horizontal_body_overflow":False,"result":"PASS"})
  page.close()
 browser.close()
assert not errors,errors
(out/"result.json").write_text(json.dumps({
 "technical_browser":"PASS","accounting_source_flow_visual_structure":"PASS",
 "source_pdf_manual_review":"SELECTED_PAGES_ONLY",
 "full_design_editorial":"NOT_CHECKED_INDEPENDENT_REVIEW",
 "production_route":"NOT_CHECKED_LOCAL_TEST",
 "viewport":statuses,"errors":errors,"screenshots":screenshots
},ensure_ascii=False,indent=2)+"\n")
print("ASR_AEI_REDESIGN_BROWSER_PASS",statuses,"screenshots",screenshots,flush=True)
