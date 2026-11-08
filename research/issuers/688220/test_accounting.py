#!/usr/bin/env python3
"""Adversarial checks: all relevant money conservation tests must reject altered source facts.
No printed-page matching is used as independent semantic verification here.
"""
import copy,json,os,pathlib,shutil,subprocess,sys,tempfile
HERE=pathlib.Path(__file__).resolve().parent
original=json.loads((HERE/"source-ledger.json").read_text())
def call(ledger):
 with tempfile.TemporaryDirectory() as root:
  t=pathlib.Path(root)
  for name in ("report-template.html","publish.py","figure-briefs.json","native_mobile.py","shared_pnl.py","source-manifest.json"):
   (t/name).write_bytes((HERE/name).read_bytes())
  manifest=json.loads((HERE/"source-manifest.json").read_text())
  pdf=t/manifest["file"]
  pdf.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(HERE/manifest["file"],pdf)
  (t/"source-ledger.json").write_text(json.dumps(ledger,ensure_ascii=False),encoding="utf8")
  # The real shared compiler must be imported from the unchanged repository;
  # a temporary issuer test cannot substitute an unsourced fake renderer.
  env=dict(os.environ)
  env["PYTHONPATH"]=str(HERE.parents[1]/"shared")+os.pathsep+env.get("PYTHONPATH","")
  return subprocess.run([sys.executable,str(t/"publish.py"),"--out",str(t/"test.html"),"--qa",str(t/"qa.json")],capture_output=True,text=True,env=env)
s=call(original)
assert s.returncode==0,(s.stdout,s.stderr)
cases=[
 ("NONCONSERVING_REVENUE","chip_rev","2113622293.12"),
 ("SOURCE_COST_CLASSIFICATION","asic_cost","202918826.52"),
 ("UNBALANCED_BS","assets","7793957328.97"),
 ("NONCASH_SIGN_FLIP","indirect_cfo",None),
 ("NONRECURRING_TAX_SIGN_FLIP","nonrec_tax",None),
 ("FX_CASH_WRONG_SIGN","cash_fx","65719613.93"),
 ("GROSS_TO_NET_INVENTORY","inventory_reserve","139854986.56"),
 ("NEGATIVE_IP_GROSS_PROFIT_WITH_TOTAL_COSTS_STILL_BALANCED","negative_ip_gp",None)
]
for name,key,val in cases:
 d=copy.deepcopy(original)
 if key=="negative_ip_gp":
  from decimal import Decimal as D
  old=D(d["facts"]["ip_cost"]["yuan"])
  added=D(d["facts"]["ip_rev"]["yuan"])-old+D("0.01")
  d["facts"]["ip_cost"]["yuan"]=str(old+added)
  d["facts"]["chip_cost"]["yuan"]=str(D(d["facts"]["chip_cost"]["yuan"])-added)
 elif key=="indirect_cfo":d["cfo_indirect"]["parts"][13]["yuan"]="470674114.66"
 elif key=="nonrec_tax":d["nonrecurring"]["parts"][-1]["yuan"]="-42763995.13"
 else:d["facts"][key]["yuan"]=val
 r=call(d)
 assert r.returncode!=0,(name,"AN_UNBALANCED_LEDGER_WAS_ACCEPTED")
 print("SOURCE_NEGATIVE_TEST_REJECTED",name)
print("SOURCE_SIGNED_ACCOUNTING_TESTS_PASS",len(cases),"negative scenarios and intact baseline")
