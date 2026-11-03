#!/usr/bin/env python3
"""Adversarial accounting + rendered-flow contract negative tests.

Every poisoned ledger must be rejected for the intended semantic/accounting
reason, never because the test workspace is missing PDF/figure-brief/modules.
"""
import copy,json,pathlib,subprocess,sys,tempfile,shutil
HERE=pathlib.Path(__file__).resolve().parent
original=json.loads((HERE/"source-ledger.json").read_text(encoding="utf-8"))
def call(ledger):
 with tempfile.TemporaryDirectory() as root:
  r=pathlib.Path(root)
  t=r/"research/issuers/688220"
  t.mkdir(parents=True)
  (r/"research/shared").mkdir(parents=True)
  shutil.copyfile(HERE.parents[1]/"shared/conserved_flow.py",r/"research/shared/conserved_flow.py")
  for name in ("report-template.html","publish.py","figure-briefs.json","source-manifest.json"):
   shutil.copyfile(HERE/name,t/name)
  (t/"source").mkdir()
  shutil.copyfile(HERE/"source/688220_2026H1_20260829_original.pdf",t/"source/688220_2026H1_20260829_original.pdf")
  (t/"source-ledger.json").write_text(json.dumps(ledger,ensure_ascii=False),encoding="utf8")
  return subprocess.run([sys.executable,str(t/"publish.py"),"--out",str(t/"test.html"),"--qa",str(t/"qa.json")],capture_output=True,text=True)
s=call(original)
assert s.returncode==0,(s.stdout,s.stderr)
cases=[
 ("NONCONSERVING_REVENUE","chip_rev","2113622293.12","INVARIANT_FAILED"),
 ("SOURCE_COST_CLASSIFICATION","asic_cost","202918826.52","INVARIANT_FAILED"),
 ("UNBALANCED_BS","assets","7793957328.97","INVARIANT_FAILED"),
 ("NONCASH_SIGN_FLIP","indirect_cfo",None,"INVARIANT_FAILED"),
 ("NONRECURRING_TAX_SIGN_FLIP","nonrec_tax",None,"INVARIANT_FAILED"),
 ("FX_CASH_WRONG_SIGN","cash_fx","65719613.93","INVARIANT_FAILED"),
 ("GROSS_TO_NET_INVENTORY","inventory_reserve","139854986.56","INVARIANT_FAILED"),
 ("CROSS_AXIS_PRODUCT_VS_REGION","mixed_axis",None,"SANKEY_CROSS_DIMENSION_NOT_ADDITIVE"),
 ("LOSS_AS_POSITIVE_RIBBON","segment_loss",None,"SANKEY_NEGATIVE_FLOW_USE_SIGNED_WATERFALL"),
 ("DUPLICATE_PRODUCT_COMPONENT","duplicate_class",None,"INVARIANT_FAILED"),
 ("WRONG_CURRENCY","wrong_currency",None,"SANKEY_CURRENCY_UNIT_MISMATCH"),
 ("WRONG_CONSOLIDATION","wrong_consolidation",None,"SANKEY_SCOPE_PERIOD_MISMATCH"),
 ("MISSING_DISCLOSURE","missing_disclosure",None,"SANKEY_SOURCE_DISCLOSURE_REQUIRED"),
 ("STOCK_AS_FLOW","stock_as_flow",None,"SANKEY_STOCK_CANNOT_FLOW"),
]
for name,key,val,error in cases:
 d=copy.deepcopy(original)
 if key=="indirect_cfo":d["cfo_indirect"]["parts"][13]["yuan"]="470674114.66"
 elif key=="nonrec_tax":d["nonrecurring"]["parts"][-1]["yuan"]="-42763995.13"
 elif key=="mixed_axis":d["segments"][1]["dimension"]="geography"
 elif key=="segment_loss":
  # Preserve totals by swapping the two COGS values in the two large categories;
  # negative GP cannot be drawn as a positive ribbon.
  d["facts"]["asic_cost"]["yuan"],d["facts"]["chip_cost"]["yuan"]=d["facts"]["chip_cost"]["yuan"],d["facts"]["asic_cost"]["yuan"]
 elif key=="duplicate_class":d["segments"][1]["rev"]=d["segments"][0]["rev"]
 elif key=="wrong_currency":d["facts"]["chip_rev"]["currency"]="USD"
 elif key=="wrong_consolidation":d["facts"]["chip_rev"]["scope"]="parent"
 elif key=="missing_disclosure":d["facts"]["chip_rev"]["classification"]="HYPOTHESIS"
 elif key=="stock_as_flow":d["facts"]["chip_rev"]["type"]="stock"
 else:d["facts"][key]["yuan"]=val
 r=call(d)
 assert r.returncode!=0,(name,"POISONED_LEDGER_WAS_ACCEPTED")
 assert error in r.stderr,(name,"MISSING_INTENDED_ERROR",r.stderr[-700:])
 print("SOURCE_NEGATIVE_TEST_REJECTED",name)
print("SOURCE_AND_SANKEY_ADVERSARIAL_TESTS_PASS",len(cases),"and intact baseline")
