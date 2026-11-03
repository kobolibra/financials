#!/usr/bin/env python3
"""Cross-industry *financial relation* tests, not general sector certification."""
from pathlib import Path
import json,copy,sys
from decimal import Decimal as D
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"research"))
from shared.conserved_flow import build_conserved_income_flow
src=ROOT/"research/issuers/688220/source-ledger.json"
d=json.loads(src.read_text(encoding="utf8"))
g=build_conserved_income_flow(d)
assert len(g["nodes"])==4 and len(g["edges"])==8 and len(g["sinks"])==2
assert len([e for e in g["edges"] if D(e["yuan"])>0])==7
assert sum((D(e["yuan"]) for e in g["edges"]),D(0))==D(g["revenue_yuan"])
assert sum((D(e["yuan"]) for e in g["edges"] if e["kind"]=="cost"),D(0))==D(d["facts"]["cogs"]["yuan"])
assert sum((D(e["yuan"]) for e in g["edges"] if e["kind"]=="gp"),D(0))==D(d["facts"]["rev"]["yuan"])-D(d["facts"]["cogs"]["yuan"])
poisons=[
 ("mixed_product_geography",lambda x:x["segments"][1].update(dimension="region"),"SANKEY_CROSS_DIMENSION"),
 ("duplicate_source",lambda x:x["segments"][1].update(rev=x["segments"][0]["rev"]),"SANKEY_DUPLICATE_FACT"),
 ("stock_as_flow",lambda x:x["facts"]["chip_rev"].update(type="stock"),"SANKEY_STOCK"),
 ("parent_instead_of_group",lambda x:x["facts"]["chip_rev"].update(scope="parent"),"SANKEY_SCOPE"),
 ("usd_source",lambda x:x["facts"]["chip_rev"].update(currency="USD"),"SANKEY_CURRENCY"),
 ("missing_page",lambda x:x["facts"]["chip_rev"].update(page=0),"SANKEY_SOURCE_PAGE"),
 ("negative_gp",lambda x:x["facts"]["ip_cost"].update(yuan="20000000.00"),"SANKEY_NEGATIVE_FLOW"),
 ("fabricated_other",lambda x:x["segments"][0].update(label="未列示差额（计算）"),"SANKEY_NON_EXCLUSIVE"),
]
for name,mutate,reason in poisons:
 x=copy.deepcopy(d);mutate(x)
 try:build_conserved_income_flow(x)
 except ValueError as e:
  assert reason in str(e),(name,str(e),reason)
 else:raise AssertionError("fake conserved flow accepted: "+name)
print("REUSABLE_SOURCE_CONSERVED_FINANCE_FLOW_PASS",len(g["nodes"]),"source nodes",len(g["edges"]),"exact yuan edges",len(poisons),"poison rejects; zero GP is zero ribbon")
