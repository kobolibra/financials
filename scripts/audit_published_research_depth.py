#!/usr/bin/env python3
"""Fail-closed proof that published V10 theses exist in readers' actual HTML.

An internal editorial JSON does not count as delivery. Verify the rendered
source-fact rows, physical pages, amounts, reported period, original-PDF SHA,
exact signed bridge, countercase and next-disclosure falsifier in public HTML.
No assertion here purports to certify causality or an independent analyst.
"""
from __future__ import annotations
from decimal import Decimal
from html.parser import HTMLParser
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from audit_research_depth import MODELS, calculate, audit_repo

class DecisionElements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.section=[]
        self.depth=0
        self.facts=[]
        self.text=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="section" and a.get("id")=="quantified-decision":
            self.depth=1
            self.section.append(a)
        elif self.depth:
            if tag=="section":self.depth+=1
            if a.get("class")=="decision-fact":self.facts.append(a)
    def handle_endtag(self,tag):
        if tag=="section" and self.depth:self.depth-=1
    def handle_data(self,data):
        if self.depth:self.text.append(data)

def money(x):
    try:
        value=Decimal(str(x))
    except Exception as exc:
        raise ValueError("INVALID_DECIMAL_IN_PUBLISHED_RESEARCH") from exc
    if not value.is_finite():raise ValueError("NONFINITE_PUBLISHED_RESEARCH")
    return value

def verify(issuer,html,brief,ledger,manifest,extras):
    errors=[]
    parsed=DecisionElements()
    parsed.feed(html)
    if len(parsed.section)!=1:
        return [f"{issuer}: EXACTLY_ONE_RESEARCH_DECISION_SECTION_REQUIRED"]
    section=parsed.section[0]
    formula,source_type,keys=MODELS[issuer]
    expected_pdf=next((row["sha256"] for row in manifest["source_check"] if row["ticker"]==issuer),None)
    checks={
        "data-research-schema":"financials.source_bound_decision.v1",
        "data-issuer":issuer,
        "data-formula":formula,
        "data-accounting-not-causal":"true",
        "data-original-pdf-sha256":expected_pdf,
    }
    for k,v in checks.items():
        if section.get(k)!=v:errors.append(f"{issuer}: {k}_MISMATCH")
    if brief["formula"]!=formula or brief["fact_keys"]!=list(keys):
        errors.append(f"{issuer}: EDITORIAL_FORMULA_DRIFT")
    actual={}
    facts=ledger.get("facts",{}) if source_type=="ledger" else extras[issuer]
    if len(parsed.facts)!=len(keys):
        errors.append(f"{issuer}: WRONG_RENDERED_SOURCE_FACT_COUNT")
    rendered={x.get("data-fact-id"):x for x in parsed.facts}
    if set(rendered)!=set(keys):
        errors.append(f"{issuer}: MISSING_OR_EXTRA_PUBLISHED_SOURCE_FACT_ID")
    if len(rendered)!=len(parsed.facts):
        errors.append(f"{issuer}: DUPLICATE_PUBLISHED_FACT_ROW")
    for key in keys:
        row=facts[key]
        actual[key]=money(row["yuan"] if source_type=="ledger" else row["val"])
        shown=rendered.get(key,{})
        period="2025H1" if key.endswith("_prior") else "2026H1"
        if shown.get("data-period")!=period:
            errors.append(f"{issuer}: PUBLISHED_FACT_PERIOD_WRONG_{key}")
        if shown.get("data-physical-page")!=str(row["page"]):
            errors.append(f"{issuer}: PUBLISHED_FACT_ORIGINAL_PAGE_WRONG_{key}")
        try:
            if money(shown.get("data-exact-yuan"))!=actual[key]:
                errors.append(f"{issuer}: PUBLISHED_FACT_MONEY_WRONG_{key}")
        except ValueError:
            errors.append(f"{issuer}: MISSING_PUBLISHED_EXACT_MONEY_{key}")
    difference=calculate(formula,actual)
    try:
        if money(section.get("data-result-yuan"))!=difference or money(brief["expected_yuan"])!=difference:
            errors.append(f"{issuer}: PUBLISHED_DECISION_BRIDGE_NOT_RECONCILED")
    except ValueError:
        errors.append(f"{issuer}: NO_EXACT_PUBLISHED_DECISION_RESULT")
    text="".join(parsed.text)
    for k in ("decision_use","strongest_alternative","next_disclosure_falsifier","scope_and_limitations"):
        if brief[k] not in text:
            errors.append(f"{issuer}: EDITORIAL_REASON_OR_FALSIFIER_NOT_PUBLISHED_{k}")
    if "NOT_CHECKED" not in text or "不是业务驱动因果证明" not in text:
        errors.append(f"{issuer}: FALSE_FINANCE_OR_CAUSAL_APPROVAL")
    return errors

def check_repo(root=ROOT):
    import sys
    issues=list(audit_repo())
    brief=json.loads((root/"research/quality/pr35-hero-figure-briefs.json").read_text())["hero_figures"]
    briefs={b["issuer"]:b["quantified_driver"] for b in brief}
    manifest=json.loads((root/"research/rebuild-v10/build-manifest.json").read_text())
    extras=json.loads((root/"research/rebuild-v10/extras.json").read_text())
    for code in MODELS:
        ledger={} if code=="600036" else json.loads((root/f"research/rebuild-v10/input-ledgers/{code}.json").read_text())
        html=(root/f"public/research/2026-h1-v10/{code}.html").read_text()
        issues.extend(verify(code,html,briefs[code],ledger,manifest,extras))
    return issues

if __name__=="__main__":
    try: issues=check_repo()
    except (OSError,KeyError,ValueError) as exc:
        print("PUBLISHED_RESEARCH_DEPTH_INPUT_ERROR",repr(exc),file=sys.stderr)
        sys.exit(2)
    if issues:
        for issue in issues:print("PUBLISHED_RESEARCH_DEPTH_FAIL",issue,file=sys.stderr)
        sys.exit(1)
    print("PUBLISHED_RESEARCH_DEPTH_EXACT_SOURCE_BRIDGE_PASS 4 source-typed companies; causality and human signoff NOT_CHECKED")
