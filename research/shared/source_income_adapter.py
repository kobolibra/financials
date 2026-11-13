"""One literal-source Type A income flow compiler for semiconductor, power and pharma.

Hard requirement: all source categories are mutually exclusive, source ledger
has actual PDF SHA and physical pages, source-specific disclosed costs, and
the sum closes to the actual consolidated original-yuan revenue and COGS.
Do not substitute geography, contract stock, insurance premium or bank NII.
"""
from __future__ import annotations
from decimal import Decimal as D, InvalidOperation
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from unified_income_sankey import FlowPlan,render_income_sankey

TITLES={
    "688220":"芯片、定制和IP业务各自贡献多少营业毛利？",
    "600900":"主营业务和其他业务分别留下多少营业毛利？",
    "600276":"药品销售、许可收入和其他业务分别创造多少毛利？",
}
SECTOR_DIMENSIONS={
    "688220":"semiconductor_disclosed_product_and_service_axis",
    "600900":"contract_goods_type",
    "600276":"contract_goods_type",
}

def compile_disclosed_income(ledger: dict) -> FlowPlan:
    issuer=ledger.get("issuer",{})
    source=ledger.get("source",{})
    code=issuer.get("code")
    period=issuer.get('fiscal_period')
    legacy_profile=code in SECTOR_DIMENSIONS and not issuer.get('accounting_route')
    partition=ledger.get('income_partition',{})
    if not legacy_profile:
        if (issuer.get('accounting_route')!='industrial_own_cost_income'
            or issuer.get('sector_adapter') not in {'manufacturing','software','consumer','utility','pharma','semiconductor','energy','services'}
            or partition.get('completeness')!='SOURCE_EXHAUSTIVE_MUTUALLY_EXCLUSIVE'
            or partition.get('period')!=period or partition.get('scope')!='consolidated'
            or not isinstance(partition.get('axis'),str) or not partition['axis'].strip()):
            raise ValueError("SECTOR_CANNOT_REUSE_INDUSTRIAL_GROSS_FLOW")
    dimension=SECTOR_DIMENSIONS[code] if legacy_profile else partition['axis']
    if not isinstance(period,str) or not period.strip() or issuer.get("base_unit")!="人民币元":
        raise ValueError("SECTOR_ISSUER_PERIOD_UNIT_MISMATCH")
    sha=source.get("original_bytes_sha256","")
    gate=source.get("original_bytes_gate","")
    if not re.fullmatch("[0-9a-f]{64}",sha) or "SHA_PASS" not in gate:
        raise ValueError("SECTOR_ORIGINAL_COMPLETE_PDF_BYTES_NOT_PROVEN")
    facts=ledger.get("facts",{})
    def value(key: str, ancestry=(), allow_derived=False) -> D:
        if key in ancestry:
            raise ValueError('SECTOR_CYCLIC_SOURCE_DERIVATION')
        row=facts.get(key)
        if (not row or row.get("type")!="flow" or row.get("period")!=period
                or row.get("scope")!="consolidated" or row.get("unit")!="元"
                or row.get("currency")!="CNY" or row.get("classification") not in {"DISCLOSED","DERIVED"}):
            raise ValueError("SECTOR_ORIGINAL_TYPED_FACT_INCOMPATIBLE "+str(key))
        page=row.get("page")
        if type(page) is not int or page<1 or page>source.get("physical_pages_observed",0):
            raise ValueError("SECTOR_REAL_ORIGINAL_PDF_PHYSICAL_PAGE_MISSING "+key)
        try:
            val=D(str(row.get("yuan","NaN")))
        except InvalidOperation as exc:
            raise ValueError("SECTOR_INVALID_DECIMAL_FACT "+key) from exc
        if not val.is_finite():
            raise ValueError("SECTOR_NONFINITE_ORIGINAL_YUAN "+key)
        if row.get('classification')=='DERIVED':
            if not allow_derived:raise ValueError('SECTOR_DERIVED_REVENUE_OR_GROUP_TOTAL_NOT_DISCLOSED')
            derivation=row.get('derivation',{})
            terms=derivation.get('terms',[])
            if (derivation.get('operation')!='subtract' or len(terms)!=2
                    or len(set(terms))!=2 or any(facts.get(t,{}).get('classification')!='DISCLOSED' for t in terms)):
                raise ValueError('SECTOR_EXPLICIT_DISCLOSED_DIFFERENCE_REQUIRED')
            if value(terms[0],ancestry+(key,))-value(terms[1],ancestry+(key,))!=val:
                raise ValueError('SECTOR_SOURCE_DIFFERENCE_NOT_CLOSED')
        return val
    total=value("rev");cogs=value("cogs")
    if total<=0 or cogs<0 or cogs>total:
        raise ValueError("SECTOR_INVALID_GROUP_REVENUE_COGS")
    rows=ledger.get("segments",[])
    if not 2<=len(rows)<=8:
        raise ValueError("SECTOR_EXCLUSIVE_REVENUE_GROUPS_NOT_ESTABLISHED")
    seen=set();parts=[];allocs=[]
    rsum=csum=D(0)
    dims=set()
    pages=set()
    for seg in rows:
        rk,ck=seg.get("rev"),seg.get("cost")
        if not rk or not ck or rk==ck or rk in seen or ck in seen:
            raise ValueError("SECTOR_DUPLICATED_OR_OVERLAPPING_BUSINESS_FACT")
        seen.update((rk,ck))
        dim=seg.get("dimension",dimension if legacy_profile and code=="688220" else "")
        if dim!=dimension:
            raise ValueError("SECTOR_MIXED_BUSINESS_AND_GEOGRAPHY_OR_CHILD_GROUPS")
        dims.add(dim)
        if not seg.get("label"):
            raise ValueError("SECTOR_UNNAMED_FINANCIAL_SOURCE")
        r=value(rk);cost=value(ck,allow_derived=True)
        pages.add(facts[rk]["page"]);pages.add(facts[ck]["page"])
        if r<=0 or cost<0 or cost>r:
            raise ValueError("SECTOR_SIGNED_OR_LOSS_BUSINESS_REQUIRES_SEPARATE_CHART")
        rsum+=r;csum+=cost
        parts.append((rk,seg["label"],str(r)))
        allocs.extend(((rk,"group_cogs",str(cost)),(rk,"group_gp",str(r-cost))))
    if len(dims)!=1 or rsum!=total or csum!=cogs:
        raise ValueError("SECTOR_NONEXHAUSTIVE_OR_MIXED_SOURCE_COST_PARTITION")
    scope="；".join("p."+str(p) for p in sorted(pages))
    mirror="，完整源PDF与官方文件字节等价尚未证明" if code=="688220" else ""
    derived_costs=[seg['label']+'成本='+facts[facts[seg['cost']]['derivation']['terms'][0]]['label']+'减'+facts[facts[seg['cost']]['derivation']['terms'][1]]['label'] for seg in rows if facts[seg['cost']].get('classification')=='DERIVED']
    derivation_note=('；'+ '、'.join(derived_costs)+'；为原值相减的计算值，不是原文单列值') if derived_costs else ''
    plan=FlowPlan(issuer=code,period=period,cost_source_note="部分成本为披露原值相减的计算" if derived_costs else "",kind="TYPE_A_SOURCE_OWN_COST_GP",
        title=TITLES.get(code,issuer.get("income_figure_title") or "原始业务收入如何形成自身成本和毛利？"),source_label="原报告互斥业务来源",
        outcome_label="实际营业成本及毛利",
        sources=tuple(parts),
        outcomes=(("group_cogs","营业成本",str(cogs),"cost"),
                  ("group_gp","营业毛利",str(total-cogs),"profit")),
        allocations=tuple(allocs),
        footnote=f"原始财报物理页{scope}，仅各业务真实收入及本业务成本{mirror}；不含期间费用与净利润。{derivation_note}")
    plan.check()
    return plan

def render_sector_income(ledger:dict, *,mobile:bool=False,embedded:bool=True)->str:
    plan=compile_disclosed_income(ledger)
    # For two/three exclusive business sources, use native phone editorial
    # source-name and money rows. This is a data-structure driven layout
    # choice, never an issuer-specific invented cost/GP allocation.
    # Four-or-more-source reports retain their previously source-verified
    # layout until they are deliberately rebuilt and re-verified.
    readable=bool(mobile and (2<=len(plan.sources)<=3 or ledger["issuer"].get("accounting_route")=="industrial_own_cost_income"))
    return render_income_sankey(plan,mobile=mobile,embedded=embedded,
                                readable_source_rows=readable)
