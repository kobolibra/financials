#!/usr/bin/env python3
"""Independent source-driven original life-insurance 2026H1 research publisher.

Only reads archived typed issuer ledger and original authored figure briefs;
never assigns premiums to CAS insurance service revenue. Numbers are exact
Decimal RMB yuan / RMB million; SVG geometry is authored from the same amounts.
"""
from __future__ import annotations
import argparse,html,json,hashlib,math
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
import sys
sys.path.insert(0,str(ROOT/"research/shared"))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from unified_insurance_premium import render_insurance_premium
from quantified_decision import render as render_insurer_decision
BASE=ROOT/"research/issuers/601628"
LEDGER=json.loads((BASE/"source-ledger.json").read_text(encoding="utf-8"))
FIG=json.loads((BASE/"figure-briefs.json").read_text(encoding="utf-8"))
STORY=json.loads((BASE/"story.json").read_text(encoding="utf-8"))
FACTS=LEDGER["facts"]
SOURCE=LEDGER["source"]
PDF=SOURCE["official_announcement"]
D=Decimal
M=D(1000000)
def amount(k):
    assert k in FACTS,k
    return D(FACTS[k]["yuan"])/M
def eq(a,b,why):
    if a!=b:raise AssertionError(f"ACCOUNTING_NOT_CONSERVED:{why}:{a}!={b}")
def sum_keys(keys):
    return sum((amount(x) for x in keys),D(0))
def signed(k):
    v=amount(k)
    return f"{v:+,.0f}" if v else "0"
def yi(n):
    v=n if isinstance(n,D) else amount(n)
    return f"{v/D(100):,.2f}"
def big(n):
    v=n if isinstance(n,D) else amount(n)
    return f"{v:,.0f}"
def pct(current,prior):
    return f"{((amount(current)/amount(prior)-1)*100):+,.1f}%" if amount(prior)!=0 else "—"
def e(s):return html.escape(str(s),quote=True)
def group(*parts):return ''.join(parts)
def t(x,y,s,size=16,color="#1B393B",weight=500,anchor=None):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{color}" font-weight="{weight}"'+(f' text-anchor="{anchor}"' if anchor else "")+f'>{e(s)}</text>'
def rect(x,y,w,h,fill,klass="",extra=""):
    return f'<rect x="{x:.4f}" y="{y:.4f}" width="{max(0,w):.4f}" height="{max(0,h):.4f}" fill="{fill}"'+(f' class="{klass}"' if klass else "")+f' {extra}/>'
def line(x1,y1,x2,y2,stroke="#CBD8D1",stroke_width=1,dash=""):
    return f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{stroke}" stroke-width="{stroke_width}"'+(f' stroke-dasharray="{dash}"' if dash else "")+'/>'
def svg(content,h=360,w=1100,desc=""):
    return f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{e(desc)}" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid meet" data-original-coordinates="true"><g font-family="Noto Sans CJK SC,PingFang SC,Microsoft YaHei,Arial,sans-serif">{content}</g></svg>'
def check():
    eq(sum_keys(["premium_first_regular","premium_single","premium_short","premium_renew"]),amount("premium_total"),"INSURANCE_PREMIUM_FOUR_DISJOINT")
    eq(sum_keys(["premium_first_regular","premium_single","premium_short"]),amount("premium_new"),"INSURANCE_NEW_BUSINESS")
    eq(sum_keys(["premium_new","premium_renew"]),amount("premium_total"),"INSURANCE_NEW_PLUS_RENEW")
    eq(sum_keys(["service_expected_claims","service_risk_release","service_csm_release","service_acq_amort","service_paa"]),amount("service_revenue"),"CAS_SERVICE_REVENUE_COMPONENTS")
    eq(sum_keys(["service_revenue","service_cost","reinsurance_premium","reinsurance_recovered"]),D(41177),"INSURANCE_SERVICE_RESULT")
    inc=["service_revenue","interest_income","investment_income","other_income","fairvalue_income","fx_income","other_business_income","disposal_income"]
    exp=["service_cost","reinsurance_premium","reinsurance_recovered","insurance_finance","reinsurance_finance","interest_expense","commission_expense","tax_surcharge","administrative_expense","credit_impair","other_asset_impair","other_business_cost"]
    eq(sum_keys(inc),amount("total_revenue"),"ALL_CAS_REVENUE_ROWS")
    eq(sum_keys(exp),D(-271129),"ALL_CAS_EXPENSE_ROWS")
    eq(sum_keys(inc+exp),amount("op_profit"),"FULL_SIGNED_OPERATING_PROFIT")
    eq(sum_keys(["op_profit","nonoperating_income","nonoperating_expense"]),amount("pretax_profit"),"PRETAX")
    eq(sum_keys(["pretax_profit","income_tax"]),amount("net_profit"),"NET_PROFIT")
    eq(sum_keys(["parent_net","nci_profit"]),amount("net_profit"),"PARENT_NONCONTROLLING")
    eq(sum_keys(["net_profit","oci"]),amount("total_comprehensive"),"COMPREHENSIVE_INCOME")
    eq(sum_keys(["cfo_insurance_cash","cfo_reinsurance_cash","cfo_other_cash"]),amount("cfo_in"),"DIRECT_CFO_RECEIPTS")
    eq(sum_keys(["cfo_claims","cfo_loans","cfo_commission","cfo_staff","cfo_tax","cfo_other_out"]),amount("cfo_out"),"DIRECT_CFO_PAYMENTS")
    eq(sum_keys(["cfo_in","cfo_out"]),amount("cfo"),"DIRECT_CFO")
    eq(sum_keys(["cash_start","cfo","cfi","cff","cash_fx"]),amount("cash_end"),"CASH_CLOSE")
    eq(sum_keys(["liabilities","parent_equity","minority_equity"]),amount("assets"),"2026_BS")
    eq(sum_keys(["liabilities_prior","parent_equity_prior","minority_equity_prior"]),amount("assets_prior"),"2025_BS")
    eq(sum_keys(["future_cash_flow_liab","risk_adjustment_liab","csm","paa_liab"]),amount("insurance_contract_liab"),"INSURANCE_LIABILITY_COMPONENTS")
    eq(amount("insurance_contract_liab"),D(6910741),"ORIGINAL_P85")
    eq(amount("premium_total"),D(536634),"ORIGINAL_P10")
    # Regulatory insurer capital ratio is neither accounting equity nor cash.
    # The original disclosed capital amounts are rounded to RMB million;
    # display only the ratio precision (2 decimals) published at physical p21.
    def solvency(cap,min_cap):
        assert amount(min_cap)>0,"NONPOSITIVE_REGULATORY_MINIMUM_CAPITAL"
        assert amount(cap)>=0,"NEGATIVE_SOLVENCY_ELIGIBLE_CAPITAL"
        return (amount(cap)*D(100)/amount(min_cap)).quantize(D("0.01"))
    eq(solvency("reg_core_capital","reg_minimum_capital"),D("156.80"),"2026_REG_CORE_COVERAGE")
    eq(solvency("reg_actual_capital","reg_minimum_capital"),D("197.78"),"2026_REG_TOTAL_COVERAGE")
    eq(solvency("reg_core_capital_prior","reg_minimum_capital_prior"),D("128.77"),"2025_REG_CORE_COVERAGE")
    eq(solvency("reg_actual_capital_prior","reg_minimum_capital_prior"),D("174.01"),"2025_REG_TOTAL_COVERAGE")
    review=LEDGER["source"].get("independent_limited_review",{})
    assert review.get("physical_page")==42 and "审阅" in review.get("standard","") and "未发表审计意见" in review.get("opinion",""),"INSURER_INTERIM_REVIEW_NOT_FULL_AUDIT"
    # Product category, insurance service recognition and cash receipt are
    # fundamentally different universes; this assertion must prevent wiring them.
    assert amount("premium_total")!=amount("service_revenue")!=amount("cfo_insurance_cash")
    assert amount("parent_net")!=amount("net_profit"),"PARENT_VS_CONSOLIDATED"
    assert amount("net_profit")!=amount("cfo"),"DIRECT_CFO_NOT_NET_PROFIT"
    assert len(FIG["figure_briefs"])>=10 and FIG["source_sha256"]==SOURCE["original_bytes_sha256"]
    return {"checks":{
        "PREMIUM_4_SOURCE_CONSERVATION":"PASS",
        "PREMIUM_NEW_RENEW_HIERARCHY":"PASS",
        "INSURANCE_PREMIUM_NOT_CAS_SERVICE":"PASS",
        "INSURANCE_SERVICE_CSM_RECOGNITION":"PASS",
        "SERVICE_RESULT_WITH_REINSURANCE":"PASS",
        "ALL_SIGNED_CAS_PNL_ROWS":"PASS",
        "CAS_PRETAX_NET_PARENT_NCI":"PASS",
        "COMPREHENSIVE_INCOME_OCI":"PASS",
        "COMPLETE_DIRECT_CFO_RECEIPTS":"PASS",
        "COMPLETE_DIRECT_CFO_PAYMENTS":"PASS",
        "CASH_CLOSE_EXACT":"PASS",
        "TWO_DATE_BS_STOCK":"PASS",
        "CONTRACT_LIABILITY_FOUR_STOCK_PARTS":"PASS",
        "INSURER_NO_FAKE_INDIRECT_CFO":"PASS",
        "PARENT_AND_CONSOLIDATED_NOT_MIXED":"PASS",
        "ISSUER_INDEPENDENT_SOURCE_SHAPE":"PASS",
        "REGULATORY_SOLVENCY_CORE_TOTAL_AND_PRIOR_RATIOS":"PASS",
        "EY_LIMITED_REVIEW_EXPLICIT_NOT_FULL_AUDIT":"PASS"}}
def comparative():
    rows=[("旧口径总保费","premium_prior","premium_total"),
          ("法定保险服务收入","service_revenue_prior","service_revenue"),
          ("归母净利润","parent_net_prior","parent_net"),
          ("经营现金流","cfo_prior","cfo")]
    body=t(38,38,"四条独立会计时间序列 · 2025H1 / 2026H1",15,"#607974")
    for i,(title,old,new) in enumerate(rows):
        y=78+i*72
        body+=t(40,y,title,16,"#163C39",650)
        # Reserve disjoint, fixed x-zones for exact source values and YoY.
        # Former bars ended at x945 and value labels ran into the percentage
        # text at x1030; screenshots proved visible overlapping data.
        # Each comparable pair still shares its OWN independent zero baseline.
        scale=555/float(max(amount(old),amount(new)))
        for j,(k,c) in enumerate([(old,"#A7B6B0"),(new,"#087964")]):
            yy=y-17+j*23
            body+=rect(265,yy,float(amount(k))*scale,16,c,extra=f'data-exact-yuan="{FACTS[k]["yuan"]}"')
            body+=t(833,yy+13,("2025 " if j==0 else "2026 ")+yi(k)+"亿",12,"#1D403E")
        # Percentage lives in its own rightmost readable column.
        body+=t(1073,y+10,pct(new,old),17,"#077D64",700,"end")
    body+=t(40,358,"各指标独立从零起绘制、不同刻度不可比较条长；不允许保费→收入→净利润的虚假单线资金流",12,"#887359")
    return svg(body,h=380,desc="2025和2026保费、法定保险服务收入、归母净利润、CFO各自独立零基准的比较")
def premium_flow():
    # Genuine management premium source to new/renewal to gross total.
    # Never alias this to CAS25 insurance service income or cash receipt.
    return render_insurance_premium(LEDGER,mobile=False)

def service_comp():
    ks=[("预计当期赔付及相关","service_expected_claims","#17705F"),("非金融风险调整","service_risk_release","#A4B9AA"),("CSM本期摊销","service_csm_release","#B88642"),("保险获取现金流摊销","service_acq_amort","#568F87"),("保费分配法（PAA）","service_paa","#C89A79")]
    maxv=float(amount("service_revenue"));body=t(35,38,"保险服务确认 = 五个有披露来源的互斥成分",17,"#1B4440",700)
    for i,(label,key,color) in enumerate(ks):
        yy=74+i*49
        body+=t(30,yy+12,label,15,"#173B39")
        body+=rect(276,yy,750*float(amount(key))/maxv,24,color,extra=f'data-exact-yuan="{FACTS[key]["yuan"]}"')
        body+=t(1030,yy+17,yi(key)+"亿",15,"#173C38",700,"end")
    body+=t(30,347,"112,525 百万元 = 24,572 + 1,099 + 35,155 + 25,133 + 26,566；CSM 摊销≠期末 CSM 存量",13,"#6E7E72")
    return svg(body,h=373,desc="保险服务收入五项原始附注的金额大小与加总，不包含收到的保费")
def simple_waterfall(steps,desc,w=1100):
    # tuple: (label, signed delta or accumulated total, kind)
    balances=[];current=D(0)
    for lab,value,kind in steps:
        old=current
        if kind=="total":current=D(value)
        else:current+=D(value)
        balances.append((lab,old,current,D(value),kind))
    ymin=min(D(0),*[min(a,b) for _,a,b,_,_ in balances]);ymax=max(D(1),*[max(a,b) for _,a,b,_,_ in balances])
    span=float(ymax-ymin);left=55.;right=1045.;top=93.;bottom=273.;n=len(steps)
    bw=min(50,(right-left)/n*.60);dx=(right-left)/n
    def yy(x):return bottom-(float(x-ymin)/span)*(bottom-top)
    body=line(left,yy(D(0)),right,yy(D(0)),"#A9BDB3",1.6)
    for i,(label,a,b,val,kind) in enumerate(balances):
        x=left+i*dx+dx*.15;topval=max(a,b);lowval=min(a,b);h=yy(lowval)-yy(topval)
        col=("#173F3D" if kind=="total" else ("#087E68" if val>0 else "#BC654B"))
        body+=rect(x,yy(topval),bw,h,col,klass="signed-waterfall",extra=f'data-source-value-million="{val}" data-cumulative-million="{b}"')
        if i<n-1 and kind!="total":body+=line(x+bw,yy(b),x+dx*1.11,yy(b),"#BCCEC5",1,"4 4")
        if i<n-1 and kind=="total":body+=line(x+bw,yy(b),x+dx*1.11,yy(b),"#BCCEC5",1,"4 4")
        body+=t(x+bw/2,max(81,yy(topval)-11),yi(val)+"亿" if kind!="total" else yi(b)+"亿",12,col,650,"middle")
        parts=label.split("|")
        for j,p in enumerate(parts):body+=t(x+bw/2,309+j*18,p,12,"#375D58",550,"middle")
    body+=t(55,38,desc,16,"#1E4440",650)
    return svg(body,h=353,w=w,desc=desc+"；带符号零基线及逐项原数计算")
def service_result():
    start=amount("service_revenue")
    return simple_waterfall([
        ("服务收入",start,"total"),("服务费用",amount("service_cost"),"delta"),
        ("分出保费",amount("reinsurance_premium"),"delta"),
        ("摊回费用",amount("reinsurance_recovered"),"delta"),
        ("服务结果",D(41177),"total")],"保险服务结果 41,177 百万元：不包含承保财务损益")
def pnl_bridge():
    accounted=["service_revenue","service_cost","reinsurance_premium","reinsurance_recovered","interest_income","investment_income","fairvalue_income","insurance_finance"]
    otherkeys=["other_income","fx_income","other_business_income","disposal_income","reinsurance_finance","interest_expense","commission_expense","tax_surcharge","administrative_expense","credit_impair","other_asset_impair","other_business_cost"]
    other=sum_keys(otherkeys)
    eq(D(41177)+sum_keys(["interest_income","investment_income","fairvalue_income","insurance_finance"])+other,amount("op_profit"),"P_N_L_OTHER_DISCLOSED_12_ITEMS")
    return simple_waterfall([
        ("保险服务|净结果",D(41177),"total"),("利息收入",amount("interest_income"),"delta"),
        ("投资收益",amount("investment_income"),"delta"),("公允价值|变动",amount("fairvalue_income"),"delta"),
        ("承保财务|损益",amount("insurance_finance"),"delta"),("其余12行|披露净额",other,"delta"),
        ("营业利润",amount("op_profit"),"total"),
        ("营业外|净收支",sum_keys(["nonoperating_income","nonoperating_expense"]),"delta"),
        ("所得税",amount("income_tax"),"delta"),("少数股东", -amount("nci_profit"),"delta"),
        ("归母利润",amount("parent_net"),"total")],"原始完整CAS合并利润桥；“其余12行”逐项见源表")
def delta_bridge():
    d=lambda key:amount(key)-amount(key+"_prior")
    leading=["fairvalue_income","investment_income","insurance_finance","service_revenue","service_cost","interest_income"]
    all_cur=["service_revenue","interest_income","investment_income","other_income","fairvalue_income","fx_income","other_business_income","disposal_income",
             "service_cost","reinsurance_premium","reinsurance_recovered","insurance_finance","reinsurance_finance","interest_expense","commission_expense","tax_surcharge","administrative_expense","credit_impair","other_asset_impair","other_business_cost"]
    rest=[k for k in all_cur if k not in leading]
    other=sum((d(k) for k in rest),D(0))
    eq(amount("op_profit_prior")+sum((d(k) for k in leading),D(0))+other,amount("op_profit"),"OP_PROFIT_DELTA_2025_2026_SIGNED")
    return simple_waterfall([("2025营业|利润",amount("op_profit_prior"),"total"),("Δ公允价值",d("fairvalue_income"),"delta"),("Δ投资收益",d("investment_income"),"delta"),
        ("Δ承保财务",d("insurance_finance"),"delta"),("Δ服务收入",d("service_revenue"),"delta"),
        ("Δ服务费用",d("service_cost"),"delta"),("Δ利息收入",d("interest_income"),"delta"),
        ("剩余14行|逐项勾稽",other,"delta"),("2026营业|利润",amount("op_profit"),"total")],"2025H1 → 2026H1 营业利润变化的 signed CAS 行项目桥")
def cash_direct():
    return simple_waterfall([("经营现金|流入",amount("cfo_in"),"total"),
        ("保险赔付",amount("cfo_claims"),"delta"),("手续费|佣金",amount("cfo_commission"),"delta"),
        ("职工现金",amount("cfo_staff"),"delta"),("税费现金",amount("cfo_tax"),"delta"),
        ("保单贷款",amount("cfo_loans"),"delta"),("其他付现",amount("cfo_other_out"),"delta"),
        ("经营现金|净额",amount("cfo"),"total")],"报告仅有直接法 CFO，绝不伪造净利润→CFO间接附注")
def cash_close():
    return simple_waterfall([("期初现金",amount("cash_start"),"total"),("经营现金",amount("cfo"),"delta"),
        ("投资现金",amount("cfi"),"delta"),("筹资现金",amount("cff"),"delta"),
        ("汇率影响",amount("cash_fx"),"delta"),("期末现金",amount("cash_end"),"total")],"现金及现金等价物闭合 142,373 → 147,822（百万元）")
def stock_stack():
    keys=[("未来现金流现值","future_cash_flow_liab","#A0BEB2"),("非金融风险调整","risk_adjustment_liab","#D5B188"),
          ("CSM未赚服务","csm","#087B67"),("PAA负债","paa_liab","#C67755")]
    total=amount("insurance_contract_liab")
    bw=820.;body=t(45,37,"截至2026-06-30 · 保险合同负债（百万元）",17,"#143D3A",700)
    x=95;y=85
    for name,k,col in keys:
        w=bw*float(amount(k)/total)
        body+=rect(x,y,w,65,col,klass="contract-stock",extra=f'data-exact-yuan="{FACTS[k]["yuan"]}"')
        x+=w
    y=177
    body+=t(95,y,"未来现金流现值 60,184.22亿",14,"#4A6A63")
    body+=t(540,y,"合同服务边际 8,132.53亿",14,"#087B67",700)
    body+=t(95,207,"风险调整 410.39亿 ｜ PAA 380.27亿",14,"#9B7058")
    body+=rect(95,238,bw,23,"#E5ECE6")
    body+=rect(95,238,bw*float(amount("insurance_contract_liab_prior")/total),23,"#B3C9BC",klass="prior-stock")
    body+=t(95,280,"2025年末 63,761.14亿",14,"#627B71")
    body+=t(916,312,"2026年中 69,107.41亿",17,"#087B67",700,"end")
    body+=t(45,346,"这是保险责任的时点计量组成，不是可转出现金或未披露的 CSM 期初→期末滚动表。",13,"#717F74")
    return svg(body,h=363,desc="2026年6月末保险合同负债的有尺度存量组成及2025年末总量比较")
def balance():
    segments=[("合并负债","liabilities","#6D8D82"),("归母权益","parent_equity","#087D67"),("少数权益","minority_equity","#B48C5E")]
    scale=840/float(amount("assets"));body=t(42,38,"相同单位、相同横轴的两个资产负债时点",17,"#153D39",700)
    for idx,(tag,suffix,totalkey) in enumerate([("2025.12.31","_prior","assets_prior"),("2026.06.30","","assets")]):
        x=178;y=96+idx*116
        body+=t(42,y+23,tag,16,"#345A55",650)
        for label,key,col in segments:
            k=key+suffix;w=float(amount(k))*scale
            body+=rect(x,y,w,60,col,klass="funding-stock",extra=f'data-exact-yuan="{FACTS[k]["yuan"]}"')
            x+=w
        body+=t(1040,y+30,yi(totalkey)+"亿",17,"#173E3A",700,"end")
    body+=t(182,341,"灰绿：合并负债　深绿：归母股权　金色：少数股东股权　｜　资产 = 全部负债 + 全部权益",13,"#607872")
    return svg(body,h=362,desc="2025年末和2026年中合并资产负债表相同尺度资金来源，包含少数股东权益")
FIGS={
"clocks":comparative,"premium":premium_flow,"service":service_comp,"insurance":service_result,
"pnl":pnl_bridge,"delta":delta_bridge,"cash":cash_direct,"cashclose":cash_close,
"csm":stock_stack,"balance":balance}
def source_table(brief):
    rows=[]
    for k in brief["facts"]:
        f=FACTS[k]
        p=f["page"];period=f["period"];v=f["yuan"]
        val=D(v)/M
        class_="muted" if f["classification"]=="DERIVED" else ""
        rows.append(f'<tr class="{class_}"><th scope="row">{e(f["label"])}</th><td>{e(period)}</td><td class="number">{e(f"{val:+,.0f}")} 百万元</td><td><a href="{e(PDF)}#page={p}" target="_blank" rel="noopener noreferrer">原始 PDF p.{p}</a></td></tr>')
    return f'<details class="audit"><summary>逐图原始金额、合并/期间与来源行列 <span>展开 {len(rows)} 项</span></summary><div class="table-shell"><table><thead><tr><th>原报表行 / 注释</th><th>报告时点/期间</th><th>原报表单位</th><th>物理页</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></details>'

def mobile_signed_bridge(brief, rows, mobile=True):
    """Insurance adapter preserves its independent source IDs and checkpoints."""
    import xml.etree.ElementTree as ET
    from editorial_bridge import render_bridge
    fid=brief['id']
    checkpoints={'insurance':{len(rows)-1},'pnl':{6,len(rows)-1},'delta':{len(rows)-1},'cash':{len(rows)-1},'cashclose':{len(rows)-1}}[fid]
    staged=[]
    for i,(label,value,key,_) in enumerate(rows):
        staged.append((label,value*M,'start' if i==0 else 'total' if i in checkpoints else 'step',key or ','.join(brief['facts'])))
    period=(FACTS['op_profit_prior']['period']+'_TO_'+FACTS['op_profit']['period']) if fid=='delta' else LEDGER['issuer']['fiscal_period']
    markup=render_bridge(staged,brief['question'],issuer=LEDGER['issuer']['code'],period=period,pdf_sha256=SOURCE['original_bytes_sha256'],mobile=mobile)
    root=ET.fromstring(markup)
    root.set('data-chart-grammar','INSURANCE_SIGNED_CUMULATIVE_BRIDGE')
    root.set('data-accounting-scope','consolidated')
    bars=[x for x in root.iter('{http://www.w3.org/2000/svg}rect') if x.get('data-signed-yuan') is not None]
    for i,(bar,row) in enumerate(zip(bars,staged)):
        bar.set('data-checkpoint',str(i in checkpoints).lower())
        bar.set('data-source-fact-ids',row[3])
        bar.set('data-money-scale-yuan-per-unit',bar.get('data-scale-yuan-per-unit'))
    ET.register_namespace('','http://www.w3.org/2000/svg')
    return ET.tostring(root,encoding='unicode')


def common_insurance_figure(brief,mobile):
    from editorial_bridge import render_comparison,render_components,render_balance
    fid=brief['id'];identity=LEDGER['issuer']
    common=dict(issuer=identity['code'],pdf_sha256=SOURCE['original_bytes_sha256'],mobile=mobile)
    def v(key):return D(FACTS[key]['yuan'])
    def ref(*keys):return '; '.join(key+' p.'+str(FACTS[key]['page']) for key in keys)
    if fid=='clocks':
        entries=[]
        for label,prior,current in [('旧口径总保费','premium_prior','premium_total'),('法定保险服务收入','service_revenue_prior','service_revenue'),('归母净利润','parent_net_prior','parent_net'),('经营现金','cfo_prior','cfo')]:
            entries.append((label+' · 同比 '+pct(current,prior),v(prior),v(current),ref(prior,current)))
        return render_comparison(entries,brief['question'],periods=(FACTS['service_revenue_prior']['period'],FACTS['service_revenue']['period']),**common)
    if fid in ('service','csm'):
        keys=['service_expected_claims','service_risk_release','service_csm_release','service_acq_amort','service_paa'] if fid=='service' else ['future_cash_flow_liab','risk_adjustment_liab','csm','paa_liab']
        total='service_revenue' if fid=='service' else 'insurance_contract_liab'
        entries=[(FACTS[k]['label'],v(k),ref(k)) for k in keys]
        return render_components(entries,v(total),brief['question'],period=FACTS[total]['period'],**common)
    if fid=='balance':
        dates=[]
        for suffix in ('_prior',''):
            keys=[k+suffix for k in ('assets','liabilities','parent_equity','minority_equity')]
            dates.append((FACTS[keys[0]]['period'],v(keys[0]),v(keys[1]),v(keys[2])+v(keys[3]),ref(*keys)))
        return render_balance(dates,brief['question'],**common)
    raise ValueError('UNSUPPORTED_COMMON_INSURANCE_FAMILY '+fid)


def mobile_figure(brief,desktop=False):
    """A complete no-horizontal-scroll, original-ledger mobile figure.

    Same exact source values as desktop. Signed flows retain cumulative bridges;
    stock/comparison figures remain independent same-scale magnitude displays.
    """
    fid=brief["id"]
    if fid in {'clocks','service','csm','balance'}:
        result=common_insurance_figure(brief,mobile=not desktop)
        return result if desktop else '<section class="mobile-chart" data-mobile-figure="'+e(fid)+'">'+result+'</section>'
    def r(label,key,group="all"):
        return (label,amount(key),key,group)
    def calc(label,value,source_ids):
        assert isinstance(value,D) and value==value.to_integral_value(),"MOBILE_DERIVED_PRECISION"
        assert source_ids and all(k in FACTS for k in source_ids),"MOBILE_DERIVED_SOURCE_IDS_REQUIRED"
        return (label,value,",".join(source_ids),"all")
    service_keys=["service_revenue","service_cost","reinsurance_premium","reinsurance_recovered"]
    if fid=="clocks":
        rows=[]
        for title,prior,current in [
            ("管理层旧统计总保费","premium_prior","premium_total"),
            ("法定保险服务收入","service_revenue_prior","service_revenue"),
            ("归母净利润","parent_net_prior","parent_net"),
            ("经营现金流","cfo_prior","cfo")
        ]:
            rows.extend([r(title+" · 2025H1",prior,title),r(title+" · 2026H1",current,title)])
        note="每个指标的两年各有自己的零基准，不跨指标比较条形长度。总保费、法定服务收入、股东净利润、现金分别属于不同报表/统计宇宙。"
    elif fid=="premium":
        rows=[r("首年期交","premium_first_regular"),r("趸交","premium_single"),
              r("短期险","premium_short"),r("续期","premium_renew"),
              r("前三项合计 · 新单保费","premium_new"),
              r("新单+续期合计 · 总保费","premium_total")]
        note="真实互斥总保费来源：1,012.94+176.96+610.49=1,800.39亿元新单；加3,565.95亿元续期=5,366.34亿元总保费。仅是旧统计保费的内部组成，不是保险服务收入或现金收款。"
    elif fid=="service":
        rows=[r("预计当期赔款及相关","service_expected_claims"),r("非金融风险调整","service_risk_release"),
              r("CSM当期摊销","service_csm_release"),r("保险获取现金流摊销","service_acq_amort"),
              r("PAA合同服务收入","service_paa"),r("法定保险服务收入总计","service_revenue")]
        note="五项不重叠CAS保险服务收入项目准确加总112,525百万元；期末CSM是时点存量，不是当期已赚收入。"
    elif fid=="insurance":
        rows=[r("保险服务收入","service_revenue"),r("保险服务费用","service_cost"),
              r("分出保费","reinsurance_premium"),r("摊回保险服务费用","reinsurance_recovered"),
              calc("保险服务净结果（四项签名合计）",sum_keys(service_keys),service_keys)]
        note="经营服务结果41,177百万元不包括承保财务损益和投资，不能直接称归母利润。"
    elif fid=="pnl":
        otherkeys=["other_income","fx_income","other_business_income","disposal_income","reinsurance_finance",
            "interest_expense","commission_expense","tax_surcharge","administrative_expense","credit_impair","other_asset_impair","other_business_cost"]
        rows=[calc("保险服务净结果",sum_keys(service_keys),service_keys),r("利息收入","interest_income"),
              r("投资收益","investment_income"),r("公允价值变动损益","fairvalue_income"),
              r("承保财务损益","insurance_finance"),
              calc("其余12项法定损益行合计",sum_keys(otherkeys),otherkeys),
              r("营业利润","op_profit"),
              calc("营业外净收支",sum_keys(["nonoperating_income","nonoperating_expense"]),["nonoperating_income","nonoperating_expense"]),
              r("所得税费用","income_tax"),
              calc("归母利润需扣除的少数股东损益",-amount("nci_profit"),["nci_profit"]),
              r("最终归母净利润","parent_net")]
        note="全部合并CAS损益逐项有符号勾稽至归母：最显著的+公允价值收益并非孤立的可持续盈利，其相对方承保财务损益为大额负数。"
    elif fid=="delta":
        def delta(key):
            return amount(key)-amount(key+"_prior")
        leading=["fairvalue_income","investment_income","insurance_finance","service_revenue","service_cost","interest_income"]
        all_keys=["service_revenue","interest_income","investment_income","other_income","fairvalue_income","fx_income",
            "other_business_income","disposal_income","service_cost","reinsurance_premium","reinsurance_recovered",
            "insurance_finance","reinsurance_finance","interest_expense","commission_expense","tax_surcharge",
            "administrative_expense","credit_impair","other_asset_impair","other_business_cost"]
        rest=sum((delta(k) for k in all_keys if k not in leading),D(0))
        rows=[r("2025H1营业利润","op_profit_prior"),
              calc("公允价值变动 · 同比增量",delta("fairvalue_income"),["fairvalue_income","fairvalue_income_prior"]),
              calc("投资收益 · 同比增量",delta("investment_income"),["investment_income","investment_income_prior"]),
              calc("承保财务 · 同比增量",delta("insurance_finance"),["insurance_finance","insurance_finance_prior"]),
              calc("服务收入 · 同比增量",delta("service_revenue"),["service_revenue","service_revenue_prior"]),
              calc("服务费用 · 同比增量",delta("service_cost"),["service_cost","service_cost_prior"]),
              calc("利息收入 · 同比增量",delta("interest_income"),["interest_income","interest_income_prior"]),
              calc("剩余14法定行 · 同比净增量",rest,[item for k in all_keys if k not in leading for item in (k,k+"_prior")]),r("2026H1营业利润","op_profit")]
        note="2025H1至2026H1并非把四类数字直接加在一起；仅同一法定损益行的同比带符号变化构成营业利润桥。"
    elif fid=="cash":
        rows=[r("经营现金总流入","cfo_in"),
              r("支付保险赔付","cfo_claims"),r("支付手续费佣金","cfo_commission"),
              r("支付职工现金","cfo_staff"),r("支付税费现金","cfo_tax"),
              r("保单质押贷款净增加","cfo_loans"),r("其他经营付现","cfo_other_out"),
              r("实际经营现金净额","cfo")]
        note="630,015百万元流入，加六类带负号支付−347,136百万元 = CFO 282,879。只有报告真实直接法，不伪造净利润到CFO的间接桥。"
    elif fid=="cashclose":
        rows=[r("期初现金等价物","cash_start"),r("经营现金净额","cfo"),
              r("投资现金净额","cfi"),r("筹资现金净额","cff"),
              r("汇率对现金影响","cash_fx"),r("期末现金等价物","cash_end")]
        note="期初142,373+经营282,879−投资175,434−筹资101,937−汇率59=期末147,822百万元，真实闭合，不把投融资现金当作经营成本。"
    elif fid=="csm":
        rows=[r("未来履约现金流现值","future_cash_flow_liab"),r("非金融风险调整存量","risk_adjustment_liab"),
              r("未赚服务合同服务边际 · CSM","csm"),r("PAA短险负债","paa_liab"),
              r("期末保险合同负债总额","insurance_contract_liab")]
        note="截至2026-06-30同一时点四组成分总计6,910,741百万元；不是资金流，不是本期利润或可分配现金。"
    elif fid=="balance":
        rows=[r("2025年末 · 资产","assets_prior"),r("2025年末 · 全部负债","liabilities_prior"),
              r("2025年末 · 归母权益","parent_equity_prior"),r("2025年末 · 少数股东权益","minority_equity_prior"),
              r("2026年中 · 资产","assets"),r("2026年中 · 全部负债","liabilities"),
              r("2026年中 · 归母权益","parent_equity"),r("2026年中 · 少数股东权益","minority_equity")]
        note="同一时点资产 = 保险等全部负债 + 归母权益 + 少数股东权益；以2026年中最大资产为统一金额刻度，绝不混成现金流。"
    else:
        raise AssertionError("MOBILE_FIGURE_FAMILY_NOT_DEFINED:"+fid)

    if fid in {"insurance","pnl","delta","cash","cashclose"}:
        if desktop:return mobile_signed_bridge(brief,rows,mobile=False)
        return ('<section class="mobile-chart" data-mobile-figure="'+e(fid)+'">'
                '<p class="m-method">'+e(note)+'</p>'+mobile_signed_bridge(brief,rows)+'</section>')
    assert len(rows)>=5,(fid,len(rows))
    groups={}
    for lab,value,key,group in rows:
        if key is not None:
            assert int(D(FACTS[key]["yuan"]))==int(value*M),(fid,key,"MOBILE_SOURCE_DRIFT")
        groups[group]=max(groups.get(group,D(0)),abs(value))
    rendered=[]
    for label,value,key,group in rows:
        denominator=groups[group]
        assert denominator>0,(fid,"ZERO_MOBILE_SCALE",group)
        scale=float(abs(value)/denominator*D(100))
        assert 0<=scale<=100.000001,(fid,label,scale)
        sign="−" if value<0 else ("+" if value>0 else "0")
        formatted=f"{abs(value)/D(100):,.2f}"
        cls=("neg" if value<0 else ("prior" if "2025H1" in label or "2025年末" in label else "pos"))
        data_key=key or "derived"
        rendered.append(
          f'<div class="m-item {cls}" data-mobile-fact="{e(data_key)}" data-exact-yuan="{e(int(value*M))}" data-scale-group="{e(group)}">'
          f'<div class="m-item-line"><span class="m-item-name">{e(label)}</span>'
          f'<strong class="m-item-val">{sign}{formatted}亿</strong></div>'
          f'<div class="m-item-rail" aria-hidden="true"><i style="width:{scale:.6f}%"></i></div></div>'
        )
    # Same source facts and accessible optional item ledger, but the first
    # phone view is a true 330-unit financial Sankey, not a horizontal crop.
    primary = render_insurance_premium(LEDGER,mobile=True) if fid=="premium" else ""
    money_rows = ("<details class='premium-original-items'><summary>展开六项精确金额</summary>"
                  +'<div class="m-items">'+"".join(rendered)+"</div></details>"
                  if fid=="premium" else '<div class="m-items">'+"".join(rendered)+"</div>")
    return (
      f'<section class="mobile-chart" data-mobile-figure="{e(fid)}" aria-label="{e(brief["question"])}的完整手机金额图">'
      f'<div class="m-kicker">同源金额 · 手机阅读</div>'
      f'<p class="m-method">{e(note)}</p>'
      f'{primary}{money_rows}'
      f'<p class="m-unit">金额：亿元，保留两位；原始计算为人民币百万元精度。每组线段共用零起点、按该组最大绝对金额绘制；负号及砖红色表示负向金额。'
      f'小于一像素的极小金额不会人为放大，详细原始行项可在本图下方展开。</p></section>'
    )

def article(brief,num):
    fid=brief["id"];fam=brief["family"]
    display_family={"clocks":"四类指标 · 同比对照","premium":"管理层保费 · 来源结构","service":"保险服务收入 · 法定组成","insurance":"保险服务 · 有符号结果桥","pnl":"法定损益 · 有符号利润桥","delta":"营业利润 · 同比贡献桥","cash":"经营现金 · 直接法桥","cashclose":"现金等价物 · 余额闭合桥","csm":"保险合同负债 · 存量组成","balance":"资产负债 · 两个时点"}[fid]
    return f'''<figure class="figure" id="chart-{e(fid)}" data-family="{e(fam)}">
      <figcaption><span class="figure-num">{num:02d} / 10 · {e(display_family)}</span>
        <h2>{e(brief["question"])}</h2><p class="take">{e(brief["takeaway"])}</p></figcaption>
      <div class="figure-toolbar"><span>原始百万元事实 · 视觉按明确金额/时点比例绘制</span><button type="button" data-export="{e(fid)}" aria-label="导出当前可见 SVG">导出当前图 SVG</button></div>
      <div class="chart" role="region" aria-label="{e(brief["question"])}，桌面及平板的原始可编辑向量图">{FIGS[fid]() if fid=="premium" else mobile_figure(brief,desktop=True)}</div>
      {mobile_figure(brief)}
      <div class="caption"><strong>会计关系：</strong>{e(brief["identity"])}<br><strong>强制反证：</strong>{e(brief["counter"])} <br><strong>数据范围：</strong>合并/报告明确范围，原始 PDF 物理页 {", ".join(str(x) for x in brief["source_pages"])}。图外金额精确到亿元两位，底层按原始百万元计算。</div>
      {source_table(brief)}
    </figure>'''
CSS=r'''
:root{--paper:#FAF9F4;--ink:#183D3B;--muted:#667E76;--line:#D6DFD5;--green:#087B66;--rust:#BC654B;--bronze:#B38C5E;--font:-apple-system,BlinkMacSystemFont,"PingFang SC","Noto Sans CJK SC",Arial,sans-serif;--serif:Georgia,"Noto Serif CJK SC","Songti SC",serif}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.75 var(--font);-webkit-font-smoothing:antialiased}a{color:var(--green)}.wrap{max-width:1210px;width:calc(100% - 72px);margin:auto}.mast{background:#103C39;color:#F6F7EE}.topbar{display:flex;justify-content:space-between;align-items:center;gap:20px;min-height:76px;border-bottom:1px solid #47706A}.logo{font-weight:800;letter-spacing:.15em;font-size:12px;text-decoration:none;color:#D5EAE2}.topbar nav{display:flex;gap:24px;font-size:12px}.topbar nav a{color:#CFE5DC;text-decoration:none}.hero{padding:76px 0 74px}.eyebrow{font-size:11px;letter-spacing:.22em;text-transform:uppercase;font-weight:800;color:#A7D7C3}.hero h1{font:500 clamp(39px,5.5vw,78px)/1.22 var(--serif);letter-spacing:-.055em;margin:22px 0 27px;max-width:1120px}.hero h1 em{font-style:normal;color:#A8E4CC}.hero .dek{font-size:17px;line-height:1.9;max-width:860px;color:#D7E5E0}.meta{display:flex;gap:17px;flex-wrap:wrap;font-size:11px;color:#BBD3C7;margin-top:31px}.kpis{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:#476D60;margin-top:52px}.kpi{padding:25px 28px;background:#194A44}.kpi .label{display:block;font-size:12px;color:#B5D7CA;letter-spacing:.06em}.kpi b{display:block;font:500 clamp(32px,4vw,51px)/1.3 var(--serif);color:#F3F2DF;margin-top:9px}.kpi small{color:#AECBBF;font-size:12px}.contents{border-bottom:1px solid var(--line);padding:23px 0;display:flex;gap:8px;flex-wrap:wrap;align-items:center}.contents b{font-size:11px;color:#73877E;margin-right:10px}.contents a{font-size:11px;text-decoration:none;padding:7px 11px;border:1px solid #D8E1D8;color:#416C60}.contents a:hover,.contents a:focus{background:#DDEDE5}.intro{padding:58px 0 50px;border-bottom:1px solid var(--line);display:grid;grid-template-columns:1.1fr .9fr;gap:65px}.intro h2,.closing h2{font:500 clamp(29px,3.2vw,45px)/1.26 var(--serif);letter-spacing:-.035em;margin:0 0 20px}.intro p,.closing p{font-size:15px;color:#45645E}.thesis{padding:28px 31px;border-left:3px solid var(--green);background:#EEF3EA}.thesis strong{display:block;color:#076D5E;font-size:11px;letter-spacing:.13em}.thesis p{font:500 clamp(19px,2vw,27px)/1.58 var(--serif);color:#254641;margin:12px 0 0}.figures{padding-top:20px}.figure{padding:65px 0 78px;margin:0;border-bottom:1px solid var(--line);scroll-margin-top:20px}.figure figcaption{margin-bottom:28px;max-width:1030px}.figure-num{display:block;color:#0D846E;font-size:11px;font-weight:800;letter-spacing:.16em;text-transform:uppercase}.figure h2{font:500 clamp(27px,3vw,43px)/1.29 var(--serif);letter-spacing:-.04em;margin:11px 0 18px}.take{font-size:16px;color:#486962;max-width:960px}.figure-toolbar{display:flex;justify-content:space-between;gap:16px;padding:13px 0;color:#6C8178;font-size:11px;border-top:1px solid #CDD9D0}.figure-toolbar button{border:1px solid #B9CFC1;background:transparent;color:#237A68;font:inherit;padding:6px 11px;cursor:pointer}.figure-toolbar button:hover{background:#DCEEE3}.chart{width:100%;overflow-x:auto;overflow-y:hidden;background:#fff;border:1px solid #E2E8E0;padding:16px 14px}.chart svg{width:100%;height:auto;display:block;overflow:visible}.caption{font-size:12px;line-height:1.85;color:#71847B;padding:18px 1px}.caption strong{color:#3B5C52}.audit{border-top:1px solid #DAE1D9;padding:13px 0}.audit summary{cursor:pointer;color:#356D60;font-size:12px;font-weight:750}.audit summary span{float:right;color:#7E948B;font-weight:400}.table-shell{max-width:100%;overflow-x:auto;margin-top:12px}table{border-collapse:collapse;width:100%;min-width:720px;font-size:12px}th,td{text-align:left;border-bottom:1px solid #E6EAE4;padding:9px 9px}thead{background:#EAF0E8;color:#557167}th{font-weight:600}td.number{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}.muted{opacity:.55}.closing{padding:68px 0 85px;display:grid;grid-template-columns:1fr 1fr;gap:60px}.risk{padding:26px 30px;background:#E9EEE6;border-left:3px solid var(--rust)}.risk strong{color:#A3503C;font-size:11px;letter-spacing:.1em}.risk p{font-size:14px}.method{background:#F0F1EB;border-top:1px solid var(--line);padding:40px 0}.method h2{font:500 28px/1.4 var(--serif)}.method p{font-size:13px;color:#5C756E;overflow-wrap:anywhere}footer{background:#103C39;color:#C5DED1;font-size:12px;padding:32px 0}footer a{color:#BAE7D5}:focus-visible{outline:3px solid #16A888;outline-offset:3px}@media(max-width:850px){.wrap{width:calc(100% - 32px)}.topbar{min-height:60px}.topbar nav{gap:10px;font-size:10px}.hero{padding:52px 0}.hero h1{font-size:clamp(35px,10vw,48px)}.hero .dek{font-size:14px}.kpis{display:block}.kpi{padding:17px 22px;border-bottom:1px solid #416E62}.kpi b{font-size:36px}.intro,.closing{display:block;padding:42px 0}.thesis,.risk{margin-top:27px}.contents{gap:6px}.contents a{font-size:10px;padding:5px}.figure{padding:48px 0 54px}.figure h2{font-size:29px}.take{font-size:14px}.chart{padding:8px;overscroll-behavior-x:contain}.chart svg{width:900px;max-width:none;min-width:900px}.figure-toolbar{flex-wrap:wrap}.caption{font-size:11px}.closing p{font-size:14px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
'''
CSS += r'''
/* Genuine 390px first-class finance figures: never trap reading in a 900px
   horizontal SVG window. Desktop retains the full editable source SVG. */
.mobile-chart{display:none}
.mobile-chart svg{display:block;width:100%;height:auto}
.premium-original-items summary{font:700 11px/1.6 var(--font);color:#237A68;cursor:pointer;padding:12px 0}
.premium-original-items .m-items{margin:12px 0 0}
.mobile-chart[data-mobile-figure="premium"] svg[data-design-system="FINANCIALS_UNIFIED_STORY_V1"]{display:block;max-width:100%;width:100%;height:auto;overflow:visible}
@media(max-width:850px){
  .chart{display:none}
  .mobile-chart{display:block;width:100%;padding:17px 14px 20px;background:#fff;border:1px solid #E2E8E0;overflow:visible}
  .m-kicker{font:800 10px/1.5 var(--font);color:#0D806C;letter-spacing:.13em}
  .m-method{font:500 13px/1.73 var(--font);color:#416960;margin:13px 0 20px}
  .m-items{display:flex;flex-direction:column;gap:14px}
  .m-item{min-width:0}
  .m-item-line{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
  .m-item-name{font:500 12.5px/1.55 var(--font);color:#284E48;min-width:0;flex:1}
  .m-item-val{font:700 15px/1.4 var(--font);font-variant-numeric:tabular-nums;white-space:nowrap;flex-shrink:0;color:#087B66}
  .m-item.neg .m-item-val{color:#BA664C}
  .m-item.prior .m-item-val{color:#718D81}
  .m-item-rail{height:9px;background:#E7EDE8;margin-top:6px;border-radius:1px;overflow:hidden}
  .m-item-rail i{display:block;height:9px;background:#07816C}
  .m-item.neg .m-item-rail i{background:#C4785E}
  .m-item.prior .m-item-rail i{background:#A6BDB1}
  .m-unit{font:400 10.5px/1.68 var(--font);color:#789087;border-top:1px solid #E0EAE1;padding-top:14px;margin:20px 0 0}
}
'''
CSS += r'''
/* Separate verified CAS service, market, insurance finance and cash clocks. */
.insurance-decision{margin:35px 0 22px;padding:30px 37px;background:#fffefa;border:1px solid #d5e2d9;border-top:4px solid #087B66}
.insurance-decision-tag{font-size:10px;font-weight:800;color:#087B66;letter-spacing:.12em;margin:0 0 13px}
.insurance-decision h2{font:500 clamp(28px,3.1vw,42px)/1.26 var(--serif);max-width:1000px;margin:0 0 15px}
.insurance-decision-lead{font-size:15px;line-height:1.85;color:#416359;max-width:1000px}
.insurance-decision-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px;padding:24px 0;margin:27px 0;border-top:1px solid #dce5da;border-bottom:1px solid #dce5da}
.insurance-decision-card{min-width:0}
.insurance-decision-card small{font-size:11px;display:block;color:#637a71;line-height:1.55}
.insurance-decision-card strong{display:block;margin-top:7px;font-size:clamp(20px,2.4vw,30px);font-weight:700;line-height:1.38;color:#087B66;font-variant-numeric:tabular-nums}
.insurance-decision-counter{font-size:13px;color:#4c6b60;line-height:1.85}
.insurance-decision-evidence{margin:20px 0 15px;border-top:1px solid #dde7df;border-bottom:1px solid #dde7df}
.insurance-decision-evidence summary{padding:15px 0;cursor:pointer;font-size:12px;font-weight:700;color:#087B66}
.insurance-decision-table{max-width:100%;overflow-x:auto}.insurance-decision-table table{min-width:640px}
.insurance-decision-limit{font-size:11px;line-height:1.8;color:#6d8178}
@media(max-width:950px){.insurance-decision{padding:25px 23px}.insurance-decision-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:850px){.insurance-decision{margin:23px 0;padding:19px 16px}.insurance-decision h2{font-size:28px}.insurance-decision-lead{font-size:13px}.insurance-decision-grid{grid-template-columns:1fr;gap:0;padding:5px 0}.insurance-decision-card{padding:12px 0;border-bottom:1px solid #e2ebe4}.insurance-decision-card:last-child{border:0}.insurance-decision-card strong{font-size:28px}}
'''
def render():
    q=check()
    charts="\n".join(article(x,i) for i,x in enumerate(FIG["figure_briefs"],1))
    research_meta=json.dumps(LEDGER,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
    sourcehash=SOURCE["original_bytes_sha256"]
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="{e(STORY["lead"])}"><meta name="theme-color" content="#103C39"><title>中国人寿 2026H1 · 保费、保险服务与投资负债联动 — Financials in Visuals</title><style>{CSS}</style></head>
<body><header class="mast"><div class="wrap"><div class="topbar"><a href="/#companies" class="logo">FINANCIALS IN VISUALS</a><nav><a href="/#companies">返回公司研究库</a><a href="#chapter">研究图形</a><a href="#method">原始来源</a></nav></div>
<div class="hero"><div class="eyebrow">ISSUER 11 / 601628.SH / LIFE INSURANCE / SOURCE-LIMITED RESEARCH</div>
<h1>保费只增 <em>2.2%</em>。<br>利润却增 <em>228.6%</em>。<br>寿险真正赚的是什么钱？</h1>
<p class="dek">{e(STORY["dek"])}</p><div class="meta"><span>中国人寿保险股份有限公司 · 2026H1</span><span>完整原始 PDF 104 物理页</span><span>2026-08-27 · 安永华明审阅（有限保证，非审计意见）</span><span>原始报表单位：人民币百万元</span><span>研究状态：来源限制预览</span></div>
<div class="kpis"><div class="kpi"><span class="label">管理层口径总保费</span><b>{yi("premium_total")}亿</b><small>{pct("premium_total","premium_prior")} · 非保险服务收入</small></div>
<div class="kpi"><span class="label">合并保险服务收入</span><b>{yi("service_revenue")}亿</b><small>{pct("service_revenue","service_revenue_prior")} · CAS25 损益确认</small></div>
<div class="kpi"><span class="label">归母净利润</span><b>{yi("parent_net")}亿</b><small>{pct("parent_net","parent_net_prior")} · 资产收益/保险财务联动</small></div></div></div></div></header>
<main class="wrap">{render_insurer_decision(LEDGER)}<nav class="contents" id="chapter"><b>CHAPTERS</b>{"".join(f'<a href="#chart-{e(x["id"])}">{i:02d} {e(x["id"].upper())}</a>' for i,x in enumerate(FIG["figure_briefs"],1))}</nav>
<section class="intro"><div><h2>先区分三个世界，<br>再讨论一家寿险公司的回报。</h2><p>寿险公司的保单收现、按保险服务履行确认的收入、以及投资组合的公允价值/利率对保险负债的共同影响，属于不同的会计问题。2026H1 投资收益 {yi("investment_income")}亿元、公允价值损益 {yi("fairvalue_income")}亿元，同时承保财务损益为 −{yi(-amount("insurance_finance"))}亿元。任何一种单独“赚了多少”的说法都可能遮蔽资产负债匹配。</p><p>完整合并利润表位于原报告物理 p47–48，合并现金流 p53–54，保险合同负债组成附注 p85。物理 p45–46 和 p49–50 是母公司口径，不得误当合并三表。</p></div>
<aside class="thesis"><strong>EDITORIAL THESIS / 核心判断</strong><p>{e(STORY["thesis"])}</p></aside></section>
<section class="figures">{charts}</section>
<section class="closing"><div><h2>真正需要追问的不是“利润为何暴涨”，而是“赚来的钱能否跨市场周期持续”。</h2><p>{e(STORY["tension"])}</p><p>管理层上半年新业务价值 {yi("nbv")} 亿元（{pct("nbv","nbv_prior")}），但 NBV 是特定内含价值模型口径，不是本期利润也不是现金收款。本页不把市场回报变化自动归结为管理层选股能力。</p></div>
<div class="risk"><strong>COUNTERVIEW / 如果论点被推翻</strong><p>{e(STORY["counter"])}</p><p>其他综合收益税后净额 {yi("oci")} 亿元，说明资产端与保险负债相关的其他综合收益也须纳入权益与风险审查。期末卖出回购金融资产款 {yi("repo_liab")} 亿元，附注指出其短期到期及质押资产限制。</p><p><strong>偿付能力不是股东权益：</strong>公司报告物理 p21 的监管核心资本 {yi("reg_core_capital")}亿元、实际资本 {yi("reg_actual_capital")}亿元和最低资本 {yi("reg_minimum_capital")}亿元，构成核心偿付能力充足率 <strong>156.80%</strong>（上年末128.77%）及综合偿付能力充足率 <strong>197.78%</strong>（上年末174.01%）。两项监管资本指标不可混成合并净资产或可自由派发资本，未来资本质量仍应结合风险因子与偿付能力规则变化审视。<a href="{e(PDF)}#page=21" target="_blank" rel="noopener noreferrer">原始报告 p21</a>。</p></div></section>
<section class="method" id="method"><h2>来源、独立性与复核边界</h2>
<p>唯一原始报告：<a href="{e(PDF)}" target="_blank" rel="noopener noreferrer">中国人寿 2026 年半年度报告（CNINFO，PDF）</a>；真实源文件 SHA-256 <code>{e(sourcehash)}</code>；104 物理页，{int((ROOT/SOURCE["source_path"]).stat().st_size):,}字节，未经审计。全部金额在源账本保存为人民币元（原 PDF 披露单位人民币百万元），每张图附可追溯原始页和完整引用事实。</p>
<p>{e(STORY["evidence_disclaimer"])}</p><p><strong>审阅性质：</strong>原始 p42 载安永华明于2026-08-27签署的中期财务报表<strong>审阅报告</strong>，依中国注册会计师审阅准则第2101号提供<strong>有限保证</strong>。审阅主要是询问与分析程序，低于完整财务报表审计保证；审阅报告明确<strong>未实施审计，也不发表审计意见</strong>。<a href="{e(PDF)}#page=42" target="_blank" rel="noopener noreferrer">原始报告 p42</a>。</p><p>{e(STORY["sector_footer"])}</p>
<p>重大风险事项还需结合后续监管资本、利率资产负债敏感性、回购融资及保险精算假设进一步复核；未载入此104页半年报的独立精算工作底稿、完整全年披露及专项监管资本文件不在本轮原始报告范围，不能假称已经审阅。真正独立第二名人类财务/视觉审稿：NOT_CHECKED。上交所独立直链字节与巨潮原始文件完全同一：NOT_CHECKED。外部同行与8–12个季度估值：NOT_CHECKED。</p>
<p>本页原创可编辑 SVG 与逐图来源表由同一结构化账本生成，可离线打开，金融图形不复制 App Economy Insights / FT 原始作品。</p></section></main>
<footer><div class="wrap"><a href="/#companies">FINANCIALS IN VISUALS / 返回统一公司研究目录</a><p>© 2026 Financials in Visuals · 研究预览，非个性化投资建议</p></div></footer>
<script id="ledger-data" type="application/json">{research_meta}</script>
<script>(function(){{document.querySelectorAll('[data-export]').forEach(function(b){{b.addEventListener('click',function(){{var id=b.getAttribute('data-export'),svgs=Array.from(b.closest('figure').querySelectorAll('svg')),node=svgs.find(function(el){{var r=el.getBoundingClientRect(),s=getComputedStyle(el);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'}});if(!node){{node=b.closest('figure').querySelector('.chart svg');}}if(!node)return;var s=new XMLSerializer().serializeToString(node);var blob=new Blob([s],{{type:'image/svg+xml;charset=utf-8'}});var u=URL.createObjectURL(blob);var a=document.createElement('a');a.href=u;a.download='601628-2026H1-'+id+'.svg';document.body.appendChild(a);a.click();a.remove();setTimeout(function(){{URL.revokeObjectURL(u)}},1000)}})}})}})();</script></body></html>''',q
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default=str(ROOT/"public/601628.html"))
    args=p.parse_args()
    markup,checks=render()
    from research_context import render as render_research_context
    markup=markup.replace("</main>",render_research_context("601628")+"</main>",1)
    from publication_editorial import finalize_publication
    markup=finalize_publication('601628',markup,period=LEDGER['issuer']['fiscal_period'])
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(markup,encoding="utf-8")
    checks.update({"original_pdf_sha256":SOURCE["original_bytes_sha256"],"source_page_count":SOURCE["physical_pages_observed"],"figure_count":len(FIG["figure_briefs"]),"chart_ids":[x["id"] for x in FIG["figure_briefs"]],"output_sha256":hashlib.sha256(markup.encode()).hexdigest()})
    (BASE/"qa.json").write_text(json.dumps(checks,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("LIFE_INSURANCE_SIGNED_CAS_AND_SOURCE_SVG_PASS",out,checks["output_sha256"],len(FIG["figure_briefs"]),"charts",len(LEDGER["facts"]),"typed facts")
if __name__=="__main__":main()
