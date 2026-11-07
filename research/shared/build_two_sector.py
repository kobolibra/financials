#!/usr/bin/env python3
"""Issuer-independent, original-source-first CAS finance publication.

Two different real business models, same typed evidence contract; charts are
selected by authored questions, not by issuer ID in the common renderer.
Never pretend successful local browser QA = full notes or second human review.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from decimal import Decimal as D
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SITE=ROOT
CENT=D("100000000")
NAMES={
"tax_surcharge":"税费附加","selling":"销售","admin":"管理",
"rd_expense":"研发","finance":"财务费用","other_income":"其他收益",
"investment_income":"投资收益","fair_value":"公允价值变动",
"credit_impairment":"信用减值","asset_impairment":"资产减值",
"asset_disposal":"资产处置","nonop_income":"营业外收入",
"nonop_expense":"营业外支出","income_tax":"所得税",
"nci":"少数股东"
}

def read(path): return json.loads(path.read_text(encoding="utf-8"))
def val(d,k): return D(str(d["facts"][k]["yuan"]))
def check(d,briefs,story,pdf_path):
    f=d["facts"];checks={}
    def ck(label,x,y):
        if x != y: raise AssertionError(label+" "+str(x)+" vs "+str(y))
        checks[label]="PASS_EXACT_DECIMAL"
    code=d["issuer"]["code"]
    assert briefs["issuer"]==code and briefs["source_sha256"]==d["source"]["original_bytes_sha256"]
    assert tuple(x["id"] for x in briefs["figure_briefs"])==tuple(story["figure_order"])
    assert all(x["facts"] and x["source_pages"] and x["question"] and x["counter"] for x in briefs["figure_briefs"])
    raw=pdf_path.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    assert raw.startswith(b"%PDF") and sha == d["source"]["original_bytes_sha256"],"PDF_REAL_BYTE_HASH"
    import fitz
    pdf=fitz.open(stream=raw,filetype="pdf")
    assert len(pdf)==d["source"]["physical_pages_observed"],"PDF_PHYSICAL_PAGES"
    ck("PDF_ACTUAL_BYTE_HASH",D(int(sha==d["source"]["original_bytes_sha256"])),D(1))
    assert code in pdf[0].get_text() and "2026" in pdf[0].get_text(),"PDF_COVER_IDENTITY"
    inspected={}
    for key,item in f.items():
        if item["classification"] not in {"DISCLOSED","MANAGEMENT_REPORTED"}:continue
        p=item["page"]
        assert isinstance(p,int) and 1<=p<=len(pdf),("ORIGINAL_PAGE_OUT_OF_RANGE",key,p)
        text=inspected.setdefault(p,pdf[p-1].get_text(sort=True))
        amount=item["yuan"]
        num=("%.2f" % float(amount)) if False else f"{D(amount):,.2f}"
        if not (num in text or amount in text):
            raise AssertionError("SOURCE_LITERAL_NOT_ON_ACTUAL_PHYSICAL_PDF_PAGE "+key+" p"+str(p)+" "+num)
    checks["ACTUAL_ORIGINAL_PDF_PAGE_AMOUNTS"]="PASS_"+str(len(f))+"_PHYSICAL_PAGE_LITERALS"
    # Sector invariant: original independently disclosed contract categories,
    # not overlapping management 'innovative drugs' subset or geography axis.
    src_ids=[x["rev"] for x in d["segments"]]
    cost_ids=[x["cost"] for x in d["segments"]]
    assert len(set(src_ids))==len(src_ids) and len(set(cost_ids))==len(cost_ids),"CROSS_DIMENSION_DUPLICATE_SEGMENT"
    assert len(d["segments"])>=2 and len({x["dimension"] for x in d["segments"]})==1,"GROUPS_DIFFERENT_AXES"
    for seg in d["segments"]:
        for k in (seg["rev"],seg["cost"]):
            vfact=f[k]
            assert vfact["classification"]=="DISCLOSED" and vfact["unit"]=="元" and vfact["scope"]=="consolidated" and vfact["period"]=="2026H1",(code,"NESTED_OR_WRONG_PERIOD_SEGMENT",k)
    for prior in ("rev_prior","cogs_prior","cfo_prior"):
        assert f[prior]["period"]=="2025H1" and f[prior]["type"]=="flow",(code,"COMPARATIVE_PRIOR_PERIOD_CHANGED",prior)
    assert f["rev"]["period"]=="2026H1" and f["rev"]["type"]=="flow"
    ck("EXCLUSIVE_REVENUE_GROUPS",sum((val(d,s["rev"]) for s in d["segments"]),D(0)),val(d,"rev"))
    ck("EXCLUSIVE_COST_GROUPS",sum((val(d,s["cost"]) for s in d["segments"]),D(0)),val(d,"cogs"))
    for s in d["segments"]:
        assert val(d,s["rev"])>0 and val(d,s["cost"])>=0 and val(d,s["rev"])-val(d,s["cost"])>=0,"NEGATIVE_MARGIN_SANKY_FORBIDDEN"
    gp=val(d,"rev")-val(d,"cogs")
    amounts=[-val(d,k) for k in ("tax_surcharge","selling","admin","rd_expense","finance")]
    amounts += [val(d,k) for k in ("other_income","investment_income","fair_value","credit_impairment","asset_impairment","asset_disposal")]
    ck("COMPLETE_PNL_OPERATING",gp+sum(amounts,D(0)),val(d,"operating_profit"))
    ck("PRETAX",val(d,"operating_profit")+val(d,"nonop_income")-val(d,"nonop_expense"),val(d,"pretax"))
    ck("CONSOLIDATED_NET",val(d,"pretax")-val(d,"income_tax"),val(d,"net_profit"))
    ck("NET_PARENT_AND_NCI",val(d,"parent_net")+val(d,"nci"),val(d,"net_profit"))
    ck("CURRENT_BALANCE",val(d,"liabilities")+val(d,"total_equity"),val(d,"assets"))
    ck("CURRENT_EQUITY_PARENT_NCI",val(d,"parent_equity")+val(d,"nci_equity"),val(d,"total_equity"))
    ck("PRIOR_BALANCE",val(d,"liabilities_prior")+val(d,"equity_prior"),val(d,"assets_prior"))
    ck("ALL_SIGNED_INDIRECT_CFO",val(d,"net_profit")+sum((val(d,k) for k in d["cfo_adjustments"]),D(0)),val(d,"cfo"))
    ck("CASH_CLOSE",val(d,"cash_start")+sum((val(d,k) for k in ("cfo","cfi","cff","fx_cash")),D(0)),val(d,"cash_end"))
    ck("SECTOR_FLOW_GROSS_PROFIT",sum((val(d,s["rev"])-val(d,s["cost"]) for s in d["segments"]),D(0)),gp)
    if "rpo" in f and "contract_liab" in f:
        ck("PHARMA_RPO_NOT_UNRECOGNIZED_FORECAST",val(d,"rpo")-val(d,"rpo_over_year"),val(d,"contract_liab"))
    if "bill_endorse_total" in f:
        ck("NONCASH_BILLS_MATERIAL_PLUS_CAPEX",val(d,"bill_endorse_material")+val(d,"bill_endorse_capex"),val(d,"bill_endorse_total"))
        assert val(d,"bill_endorse_capex")>0 and val(d,"cash_capex")>0,"NONCASH_CAPEX_HAS_TO_BE_SEPARATE_FROM_CASH_FCF"
    if "restricted_non_cash" in f:
        assert val(d,"restricted_non_cash")>0 and val(d,"cash_end")>0,"CASH_EQUIVALENTS_MUST_BE_SEPARATE_FROM_RESTRICTED_DEPOSITS"
        checks["RESTRICTED_CASH_NOT_CASH_EQUIVALENTS"]="PASS_SOURCE_NOTE_DIFFERENT_CASH_BASE"
    pdf.close()
    return checks

HTML=r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ | Financials in Visuals</title>
<meta name="description" content="__DESCRIPTION__">
<style>
:root{--bg:#f5f4ef;--paper:#fffefb;--ink:#15363b;--soft:#597173;--line:#d7dfd8;--green:#0c806c;--copper:#b47852;--blue:#487a93;--muted:#edf1ec;--red:#aa5949}
*{box-sizing:border-box}html{max-width:100%;overflow-x:clip}body{margin:0;max-width:100%;overflow-x:clip;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Noto Sans CJK SC","PingFang SC","Microsoft YaHei",sans-serif;line-height:1.68}
a{color:inherit}button{font:inherit}.wrap{max-width:1190px;margin:auto;padding:0 30px}
.topbar{height:76px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line)}.topbar .logo{font-size:15px;letter-spacing:.16em;text-decoration:none;font-weight:800}.topbar .back{color:var(--green);font-size:13px;text-decoration:none}
.hero{padding:95px 0 68px;display:grid;grid-template-columns:minmax(0,1.8fr) minmax(250px,.8fr);gap:56px}
.eyebrow{letter-spacing:.17em;font-size:11px;font-weight:800;color:var(--green)}h1,h2,h3{font-family:"Noto Serif CJK SC","Songti SC",STSong,serif;font-weight:650}h1{font-size:clamp(37px,5.1vw,66px);line-height:1.23;letter-spacing:-.055em;margin:20px 0 27px;max-width:15em}.dek{font-size:17px;line-height:1.95;color:#405b5e;max-width:660px}.heroaside{border-left:2px solid var(--green);padding-left:27px;align-self:start;margin-top:28px}.heroaside b{font-size:12px;letter-spacing:.08em;color:var(--green)}.heroaside p{margin:15px 0 0;font-size:15px;line-height:1.9}
.nav{max-width:100%;padding:20px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);display:flex;gap:12px;overflow-x:auto;white-space:nowrap}.nav a{font-size:12px;text-decoration:none;padding:9px 14px;border-radius:20px;background:#e8eee7}
.numbers{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;margin-top:35px}.number{border-top:1px solid var(--ink);padding-top:17px}.number label{display:block;font-size:11px;color:var(--soft);letter-spacing:.07em}.number strong{display:block;margin-top:8px;font-size:clamp(20px,2.7vw,35px);letter-spacing:-.055em;font-variant-numeric:tabular-nums}.number small{color:var(--soft);font-size:11px}
.chapter{padding:82px 0 68px;border-bottom:1px solid var(--line);scroll-margin-top:35px}.chaptermark{font-size:11px;color:var(--green);font-weight:900;letter-spacing:.17em}.chapter h2{font-size:clamp(27px,3.4vw,42px);line-height:1.44;letter-spacing:-.035em;max-width:1000px;margin:18px 0}.chapter .answer{font-size:17px;max-width:870px;color:var(--soft);margin-bottom:30px}
.figure{min-width:0;max-width:100%;margin:28px 0;background:var(--paper);border:1px solid var(--line);border-radius:5px;overflow:hidden}.figure-head{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:23px 30px 17px;border-bottom:1px solid var(--line)}.figure-head b{font-size:12px;letter-spacing:.08em}.export{background:transparent;border:1px solid var(--line);border-radius:4px;padding:7px 12px;color:var(--soft);cursor:pointer;font-size:11px}.plot{width:100%;max-width:100%;min-width:0;padding:18px 23px 17px;overflow-x:auto;scrollbar-width:thin}.plot svg{width:100%;height:auto;display:block;min-width:760px}.native-mobile-finance{display:none}.native-mobile-finance-supplement{padding:14px;background:#eef4ed;font-size:12px;color:#395c50;line-height:1.8;border-top:1px solid var(--line)}.native-mobile-finance-supplement p{margin:0 0 10px}.native-mobile-finance-supplement strong{color:var(--green);font-variant-numeric:tabular-nums}.chart-label{font-size:12px;fill:var(--ink)}.chart-tiny{font-size:10.5px;fill:var(--soft)}.chart-value{font-weight:700;font-size:13px;fill:var(--ink)}.chart-title{font-size:12px;fill:var(--ink);font-weight:700}
.counter{font-size:13px;color:#784e3b;background:#f4eee7;padding:18px 24px;border-left:3px solid var(--copper)}.sourcebar{padding:15px 27px 20px;border-top:1px solid var(--line);color:var(--soft);font-size:12px}
details{margin-top:10px}summary{cursor:pointer;color:var(--green);font-weight:700;list-style:disclosure-closed;font-size:12px}
table{border-collapse:collapse;width:100%;font-size:12px;margin-top:16px;background:white}td,th{border-bottom:1px solid var(--line);padding:9px 8px;text-align:left}td:nth-child(2),td:nth-child(3){font-variant-numeric:tabular-nums;white-space:nowrap}th{color:var(--soft);font-weight:600}td a{color:var(--green)}.tablewrap{max-width:100%;min-width:0;overflow:auto}
.disclaimer{padding:54px 0}.disclaimer h2{font-size:27px}.notes{display:grid;grid-template-columns:1fr 1fr;gap:16px}.note{font-size:14px;padding:20px 24px;background:#eef1eb;color:#456366}.actions{padding:50px 0 85px;background:#eaf0ea;margin-top:35px}.actions h2{font-size:30px}.actions li{margin:13px 0}.footer{display:flex;justify-content:space-between;gap:16px;padding:35px 0;border-top:1px solid var(--line);font-size:11px;color:var(--soft)}
@media(max-width:740px){.plot{overflow-x:visible!important;overflow-y:visible!important;padding:10px}.plot>svg{display:none!important}.plot .native-mobile-finance{display:block;min-width:0;max-width:100%;width:100%}.plot .native-mobile-finance svg{width:100%;max-width:100%;min-width:0;height:auto;display:block;overflow:visible}.wrap{padding:0 17px}.topbar{height:60px}.topbar .logo{font-size:11px}.hero{padding:53px 0 40px;grid-template-columns:1fr;gap:8px}h1{font-size:37px;max-width:99%;line-height:1.32}.dek{font-size:15px}.heroaside{margin:16px 0 0}.numbers{grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.number strong{font-size:20px}.number label{font-size:10px}.chapter{padding:54px 0 45px}.chapter h2{font-size:26px}.chapter .answer{font-size:15px}.figure-head{padding:17px}.plot{padding:10px}.sourcebar{padding:14px 16px}.notes{grid-template-columns:1fr}.footer{flex-direction:column}.figure{border-radius:0}.counter{font-size:12px}.nav{margin:0 -17px;padding-left:17px}}
</style></head><body>
<div class="wrap"><div class="topbar"><a class="logo" href="/#companies">FINANCIALS / IN VISUALS</a><a class="back" href="/#companies">返回唯一公司研究目录 ↗</a></div>
<header class="hero"><div><div class="eyebrow">__EYEBROW__ · 2026 H1 · ORIGINAL FINANCIAL RESEARCH</div><h1>__TITLE__</h1><p class="dek">__DEK__</p>
<div class="numbers" id="hero-numbers"></div></div><div class="heroaside"><b>THE CONTRADICTION / 关键矛盾</b><p>__TENSION__</p><b style="display:block;margin-top:25px">STRONGEST COUNTERCASE</b><p>__COUNTER__</p></div></header>
<div class="nav" id="nav"></div><main id="article"></main>
<div class="disclaimer"><h2>方法、来源与明确的边界</h2><p>__DISCLAIMER__</p><div class="notes" id="notes"></div><p>本稿为来源限定的独立研究预览；所载研究与图表源于发行人原始完整 PDF，并不意味着已经取得另一名独立人类财务分析师、独立视觉编辑、机构买卖评级或完整的全部附注鉴证。每张图都附有原始事实与物理 PDF 页码。PDF 的全部重大附注独立核对仍为 NOT_CHECKED；与交易所原始主机字节同一性另作验证。</p></div></div>
<div class="actions"><div class="wrap"><div class="eyebrow">FALSIFIABILITY / 下一轮证伪</div><h2>下一份披露应该回答的三个问题</h2><ol id="followups"></ol></div></div>
<div class="wrap footer"><span>FINANCIALS IN VISUALS · 2026 H1 · SOURCE-LIMITED RESEARCH PREVIEW</span><a href="/#companies">返回统一公司研究库</a></div>
<script id="ledger-data" type="application/json">__LEDGER__</script>
<script id="figure-briefs" type="application/json">__BRIEFS__</script>
<script id="story-data" type="application/json">__STORY__</script>
<script>
(function(){"use strict";
var d=JSON.parse(document.querySelector("#ledger-data").textContent);
var briefs=JSON.parse(document.querySelector("#figure-briefs").textContent);
var story=JSON.parse(document.querySelector("#story-data").textContent);
var f=d.facts,code=d.issuer.code, N=100000000;
function v(k){return Number(f[k].yuan)}
function y(k){return v(k)/N}
function fmt(x){return (x<0?"−":"") + Math.abs(x).toLocaleString("zh-CN",{minimumFractionDigits:2,maximumFractionDigits:2})}
function yi(x){return fmt(x/N)+" 亿"}
function e(t){return String(t).replace(/[&<>"']/g,function(s){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[s]})}
function svg(w,h,body){return '<svg viewBox="0 0 '+w+' '+h+'" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="'+e(story.thesis)+'">'+body+'</svg>'}
function text(x,y,s,cls,extra){return '<text x="'+x+'" y="'+y+'" class="'+(cls||"chart-label")+'" '+(extra||"")+'>'+e(s)+'</text>'}
function rect(x,y,w,h,fill,cls,extra){return '<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+Math.max(0,h)+'" fill="'+fill+'" class="'+(cls||"")+'" '+(extra||"")+'/>'}
var green="#0c806c",copper="#b47852",blue="#487a93",muted="#aab8b1",ink="#15363b",red="#aa5949";
function headlineNumber(k,label){return '<div class="number"><label>'+e(label)+'</label><strong>'+fmt(y(k))+' 亿</strong><small>人民币 · 合并口径 · 2026H1</small></div>'}
document.querySelector("#hero-numbers").innerHTML=headlineNumber("rev","法定营业收入")+headlineNumber("parent_net","归母净利润")+headlineNumber("cfo","经营现金净流入");
document.querySelector("#nav").innerHTML=briefs.figure_briefs.map(function(x,i){return '<a href="#'+x.id+'">'+String(i+1).padStart(2,"0")+' '+e(x.id.toUpperCase())+'</a>'}).join("");
document.querySelector("#notes").innerHTML=story.other_notes.map(function(x){return '<div class="note">'+e(x)+'</div>'}).join("");
document.querySelector("#followups").innerHTML=story.followups.map(function(x){return '<li>'+e(x)+'</li>'}).join("");
function sankey(){
 var S=d.segments,H=420,gap=14,available=H-gap*(S.length-1),scale=available/v("rev");
 var yy=85, costY=85, gpY=85+v("cogs")*scale+28,out="";
 out+=text(20,34,"每一类来源 → 各自披露营业成本 + 推导毛利 | 元金额比例", "chart-title");
 out+=text(20,54,"不是客户付款路线；条带厚度按本期原始元金额，严禁最小 1px 放大","chart-tiny");
 S.forEach(function(seg,i){
  var rv=v(seg.rev),cs=v(seg.cost),gp=rv-cs,sY=yy,srcH=rv*scale;
  out+=rect(192,sY,13,srcH,blue,"money-source",'data-source-key="'+seg.rev+'" data-yuan="'+rv.toFixed(2)+'"');
  if(srcH>17)out+=text(12,sY+Math.min(16,srcH/2+5),seg.label,"chart-label");
  var edges=[["cogs",cs,costY,copper],["gross_profit",gp,gpY,green]],offset=0;
  edges.forEach(function(edge){var kind=edge[0],value=edge[1],targetY=edge[2],color=edge[3],t=value*scale;
   if(value>0){var d0="M205 "+(sY+offset)+" C420 "+(sY+offset)+" 700 "+targetY+" 938 "+targetY+
   " L938 "+(targetY+t)+" C700 "+(targetY+t)+" 420 "+(sY+offset+t)+" 205 "+(sY+offset+t)+" Z";
   out+='<path class="money-ribbon" data-source-key="'+seg.rev+'" data-target-key="'+kind+'" data-yuan="'+value.toFixed(2)+'" data-thickness="'+t+'" d="'+d0+'" fill="'+color+'" opacity=".42"/>';}
   if(kind==="cogs")costY+=t;else gpY+=t;offset+=t;
  });
  yy+=srcH+gap;
 });
 out+=rect(938,85,14,v("cogs")*scale,copper,"money-sink",'data-target-key="cogs" data-yuan="'+v("cogs").toFixed(2)+'"');
 out+=rect(938,85+v("cogs")*scale+28,14,(v("rev")-v("cogs"))*scale,green,"money-sink",'data-target-key="gross_profit" data-yuan="'+(v("rev")-v("cogs")).toFixed(2)+'"');
 out+=text(967,101,"营业成本","chart-title")+text(967,123,yi(v("cogs")),"chart-value");
 out+=text(967,85+v("cogs")*scale+47,"毛利","chart-title")+text(967,85+v("cogs")*scale+68,yi(v("rev")-v("cogs")),"chart-value");
 out+=text(20,555,"业务分组口径：真实收入与真实成本，非按总毛利率分摊；小额来源请查看本图元金额附表。","chart-tiny");
 return svg(1120,579,out);
}
function PNLsteps(){
 var steps=[
 ["营业毛利",null],["税金及附加",-v("tax_surcharge")],["销售+管理",-v("selling")-v("admin")],
 ["研发费用",-v("rd_expense")],["财务费用",-v("finance")],["其他+投资",v("other_income")+v("investment_income")],
 ["公允价值",v("fair_value")],["减值+处置",v("credit_impairment")+v("asset_impairment")+v("asset_disposal")],
 ["营业外收支",v("nonop_income")-v("nonop_expense")],["所得税",-v("income_tax")],["少数股东",-v("nci")],
 ["归母净利",null]];
 return {start:v("rev")-v("cogs"),steps:steps,end:v("parent_net")};
}
function cfoSteps(){
 var groups={
 "折旧与摊销":d.cfo_adjustments.filter(function(k){return /deprec|depreciation|rou|amort|long_defer/.test(k)}),
 "减值及处置":d.cfo_adjustments.filter(function(k){return /impair|credit|disposal|scrap/.test(k)}),
 "金融与财务":d.cfo_adjustments.filter(function(k){return /fair|finance|investment/.test(k)}),
 "递延税项":d.cfo_adjustments.filter(function(k){return /tax/.test(k)}),
 "经营性营运资本":d.cfo_adjustments.filter(function(k){return /inventory|receivables|payables/.test(k)}),
 "其他调整":d.cfo_adjustments.filter(function(k){return /_other$/.test(k)})
 };
 var steps=[["合并净利润",null]];
 Object.entries(groups).forEach(function(item){if(item[1].length)steps.push([item[0],item[1].reduce(function(a,k){return a+v(k)},0)])});
 steps.push(["经营现金",null]);
 return {start:v("net_profit"),steps:steps,end:v("cfo")};
}
function cashSteps(){return {start:v("cash_start"),steps:[["期初现金",null],["经营活动",v("cfo")],["投资活动",v("cfi")],["筹资活动",v("cff")],["现金汇率",v("fx_cash")],["期末现金",null]],end:v("cash_end")}}
function waterfall(o,name){
 var steps=o.steps,current=o.start,levels=[0,current],bounds=[];
 steps.forEach(function(st,i){if(i===0||i===steps.length-1)return;current+=st[1];levels.push(current);bounds.push(current)});
 var lo=Math.min.apply(null,levels),hi=Math.max.apply(null,levels),pad=(hi-lo)*.18+N;
 var ymin=Math.min(0,lo-pad),ymax=hi+pad,top=78,plotH=390;
 var Y=function(value){return top+(ymax-value)/(ymax-ymin)*plotH};
 var n=steps.length,w=960/n,barW=Math.min(57,w*.56),out="";
 out+=text(20,32,name,"chart-title");
 out+=text(20,52,"所有变动保留原始正负号；纵轴为同一人民币金额尺度。详见逐项源证据表。","chart-tiny");
 out+='<line x1="20" x2="1090" y1="'+Y(0)+'" y2="'+Y(0)+'" stroke="'+muted+'" stroke-dasharray="4 5"/>';
 current=o.start;
 steps.forEach(function(step,i){var x=95+i*w,cy,ny,h,fill,amount;
 if(i===0){cy=0;ny=o.start;fill=blue;amount=o.start}
 else if(i===steps.length-1){cy=0;ny=o.end;fill=green;amount=o.end}
 else{cy=current;ny=current+step[1];fill=step[1]>=0?green:copper;amount=step[1];current=ny}
 var a=Y(Math.max(cy,ny)),bb=Y(Math.min(cy,ny)),height=Math.max(.65,bb-a);
 out+=rect(x,a,barW,height,fill,"waterfall-step",'data-step="'+i+'" data-value="'+amount.toFixed(2)+'"');
 var labelY=i===0||i===steps.length-1?Math.max(70,a-10):(amount>=0?Math.max(70,a-10):Math.min(503,bb+15));
 out+=text(x+barW/2,labelY,yi(amount),"chart-value",'text-anchor="middle"');
 var txt=step[0];if(txt.length>7)txt=txt.slice(0,6)+"…";
 out+=text(x+barW/2,532,txt,"chart-tiny",'text-anchor="middle"');
 if(i>0&&i<steps.length-1&&i<steps.length-2){out+='<path d="M'+(x+barW)+' '+Y(current)+' L'+(x+w)+' '+Y(current)+'" stroke="'+muted+'" stroke-dasharray="3 4"/>'}
 });
 return svg(1120,560,out);
}
function balance(){
 var curr=[v("liabilities"),v("parent_equity"),v("nci_equity")],old=[v("liabilities_prior"),v("equity_prior")],max=Math.max(v("assets"),v("assets_prior")),w=840,x=190,scale=w/max,out="";
 out+=text(20,34,"资产＝负债＋全部所有者权益｜两期均为同一金额尺度的时点存量","chart-title");
 var rows=[{date:"2025·12",amounts:old,labels:["负债","权益合计"],colors:[copper,green],total:v("assets_prior")},{date:"2026·06",amounts:curr,labels:["负债","归母权益","少数股东"],colors:[copper,green,blue],total:v("assets")}];
 rows.forEach(function(r,i){var yy=129+i*168,xx=x;out+=text(24,yy+35,r.date,"chart-title");
  r.amounts.forEach(function(a,j){var ww=a*scale;out+=rect(xx,yy,ww,72,r.colors[j],"balance-part",'data-date="'+r.date+'" data-yuan="'+a.toFixed(2)+'"');if(ww>135){out+=text(xx+8,yy+28,r.labels[j],"chart-title",'style="fill:#fff"');out+=text(xx+8,yy+51,yi(a),"chart-tiny",'style="fill:#fff"')}xx+=ww});
  out+=text(190,yy+100,"资产合计 "+yi(r.total)+"　/　负债与所有者权益一致","chart-tiny");
 });
 out+=text(20,500,"负债（铜）　/　母公司权益（绿）　/　少数股东权益（蓝）。上期总权益仍包含少数股东，见来源附表。","chart-tiny");
 return svg(1120,530,out);
}
function trend(){
 var rows=[["营业收入","rev_prior","rev"],["归母净利润",null,"parent_net"],["经营现金流","cfo_prior","cfo"]];
 if(!f["parent_net_prior"])rows[1]=["营业毛利",null,null];
 var out=text(20,31,"两期现金与盈利信号（注意：不将不同指标以同一跨指标面积比较）","chart-title");
 var metrics=[["营业收入",v("rev_prior"),v("rev")],["营业毛利",v("rev_prior")-v("cogs_prior"),v("rev")-v("cogs")],["经营现金",v("cfo_prior"),v("cfo")]];
 metrics.forEach(function(a,i){var yy=90+i*142,den=Math.max(a[1],a[2]),s=530/den,change=(a[2]-a[1])/a[1]*100;
 out+=text(20,yy+9,a[0],"chart-title");
 out+=text(20,yy+33,(change>=0?"+":"")+change.toFixed(2)+"%","chart-value");
 out+=rect(205,yy-16,a[1]*s,24,muted,"trend-prior");
 out+=rect(205,yy+19,a[2]*s,24,i===2?copper:green,"trend-current");
 out+=text(747,yy+2,"2025H1  "+yi(a[1]),"chart-tiny");
 out+=text(747,yy+36,"2026H1  "+yi(a[2]),"chart-value");
 });
 out+=text(20,517,"同一行内两期零基线比例可比较，不同指标每行采用独立零基线；不暗示 8—12 个季度的趋势。","chart-tiny");
 return svg(1120,540,out);
}
function capital(){
 var cfo=v("cfo"),cap=v("cash_capex"),free=cfo-cap,paid=v("dividend_interest_cash"),out="";
 var a=[["经营现金",cfo,green],["长期资产现金投入",cap,copper],["简易自由现金",free,blue],["股利利润及利息",paid,muted]];
 if(f["bill_endorse_capex"]){a.push(["非现金票据购建",v("bill_endorse_capex"),"#8a7390"])}
 var max=Math.max.apply(null,a.map(function(x){return x[1]})),S=308/max;
 out+=text(20,35,"现金投资、非现金票据结算与利润表费用必须分开，不能伪造资本回报","chart-title");
 a.forEach(function(q,i){var x=a.length===5?65+i*210:118+i*248,hh=Math.max(0,q[1])*S;
 out+=rect(x,442-hh,102,hh,q[2],"capital-bar",'data-amount="'+q[1].toFixed(2)+'" data-cash-kind="'+(i===4?"NONCASH_NOT_IN_CFO":"CASH_FLOW_OR_DERIVED")+'"');
 out+=text(x+51,430-hh,yi(q[1]),"chart-value",'text-anchor="middle"');out+=text(x+51,476,q[0],"chart-tiny",'text-anchor="middle"');});
 out+=text(20,518,"简易 FCF＝CFO − 购建固定资产、无形资产及其他长期资产所付现金（非公司法定口径）。","chart-tiny");
 out+=text(20,542,"股利利润及利息支付合并计列，不能在未拆分前称作纯股息。","chart-tiny");
 if(f["bill_endorse_capex"]){out+=text(20,568,"原始现金附注 p.153：银行承兑汇票背书非现金结算 "+yi(v("bill_endorse_total"))+"，其中用于购建资产 "+yi(v("bill_endorse_capex"))+"，不计入上述现金 FCF。","chart-tiny");}
 return svg(1120,f["bill_endorse_capex"]?592:567,out);
}
function sector(){
 if(story.theme==="hydro"){
  var out=text(18,36,"水电物理产出 × 现金回收：不同计量单位必须分图、不能按一条假因果流连接。","chart-title");
  out+='<circle cx="245" cy="248" r="165" fill="#e5f1e9" stroke="'+green+'" stroke-width="1"/>';
  out+=text(245,236,"1327.44","chart-title",'text-anchor="middle" style="font-size:63px;fill:'+green+'"');
  out+=text(245,270,"亿千瓦时","chart-label",'text-anchor="middle"');
  out+=text(245,300,"六座梯级水电站发电量","chart-tiny",'text-anchor="middle"');
  out+='<path d="M440 250 L645 250" stroke="'+copper+'" stroke-dasharray="6 8" stroke-width="2"/>';
  out+=text(544,227,"不可直接换算为电价","chart-tiny",'text-anchor="middle"');
  out+=rect(664,128,32,242,green,"");
  out+=text(725,177,"营业收入","chart-title");
  out+=text(725,216,yi(v("rev")),"chart-value",'style="font-size:27px"');
  out+=text(725,255,"经营现金流","chart-title");
  out+=text(725,290,yi(v("cfo")),"chart-value",'style="font-size:26px"');
  out+=text(20,509,"缺净售电量/合同电价组合/水文和调度信息；历史合并比较期本报告已追溯调整。","chart-tiny");
  return svg(1120,537,out);
 }
 var rv=v("rev"),prod=v("drug_sales_rev"),lic=v("licence_rev"),other=v("other_rev");
 var w=975,sc=w/rv,x=75,out=text(20,32,"收入合同类别：商品销售、许可、其他互斥分流；创新药是商品销售的内部子集","chart-title");
 [["药品等商品",prod,green],["知识产权许可",lic,copper],["其他",other,blue]].forEach(function(a){var ww=a[1]*sc;out+=rect(x,102,ww,94,a[2],"sector-revenue");if(ww>125){out+=text(x+10,128,a[0],"chart-title",'style="fill:#fff"');out+=text(x+10,158,yi(a[1]),"chart-value",'style="fill:#fff"')}x+=ww});
 var innovation=88.09*N,prodResidual=prod-innovation;
 out+=text(20,250,"商品销售中的创新药（管理层披露子集），绝不再加到集团收入总额","chart-label");
 out+=rect(75,278,innovation*sc,70,green,"sector-nested");
 out+=rect(75+innovation*sc,278,prodResidual*sc,70,muted,"sector-nested");
 out+=text(90,317,"创新药 88.09亿元","chart-title",'style="fill:#fff"');
 out+=text(75+innovation*sc+15,317,"其他药品等商品","chart-tiny");
 out+=text(20,413,"许可收入 "+yi(lic)+" ≠ 经常性药品销售；2026年7月生效的BMS合作不属于本期收入。","chart-label");
 out+=text(20,460,"剩余履约义务 "+yi(v("rpo"))+"：合同已签但非已实现收入，且变动里程碑未必纳入。","chart-label");
 return svg(1120,496,out);
}
__NATIVE_MOBILE_SVG__
function draw(id){if(id==="flow")return sankey();if(id==="pnl")return waterfall(PNLsteps(),"完整 CAS：营业毛利 → 营业利润 → 税后净利 → 归母");
 if(id==="cfo")return waterfall(cfoSteps(),"合并净利润 + 原始全部调节项 → 经营现金流");
 if(id==="cash")return waterfall(cashSteps(),"现金及现金等价物：真实四项带符号现金变动");
 if(id==="balance")return balance();if(id==="trend")return trend();if(id==="capital")return capital();if(id==="sector")return sector();throw Error("UNKNOWN_FIGURE "+id)}
function sourceTable(q){
 var keys=q.facts,html='<details><summary>查看本图全部原始人民币元数据和物理 PDF 页码（'+keys.length+' 个事实）</summary><div class="tablewrap"><table><thead><tr><th>事实 / 原始行列</th><th>原始金额 / 单位</th><th>期间 / 类型</th><th>原始 PDF</th></tr></thead><tbody>';
 keys.forEach(function(k){var z=f[k],number=DUMMY(z);html+='<tr><td>'+e(z.label)+' <small>('+e(k)+')</small></td><td>'+e(number)+'</td><td>'+e(z.period+' / '+z.type)+'</td><td><a href="'+e(d.source.official_announcement)+'#page='+z.page+'" target="_blank" rel="noopener noreferrer">p.'+z.page+'</a></td></tr>'});
 return html+"</tbody></table></div></details>";
}
function DUMMY(z){return Number(z.yuan).toLocaleString("zh-CN",{minimumFractionDigits:2,maximumFractionDigits:2})+" "+z.unit}
var article=document.querySelector("#article");
briefs.figure_briefs.forEach(function(q,i){
var section=document.createElement("section");section.className="chapter";section.id=q.id;
section.innerHTML='<div class="chaptermark">FIGURE '+String(i+1).padStart(2,"0")+' / '+e(q.family.toUpperCase())+'</div>'+
 '<h2>'+e(q.question)+'</h2><p class="answer">'+e(q.takeaway)+'</p>'+
 '<figure class="figure" id="fig-'+q.id+'"><div class="figure-head"><b>'+e(q.id.toUpperCase())+'　·　2026H1　·　合并人民币元 / 如注</b><button class="export" data-export="'+q.id+'" type="button">导出 SVG</button></div>'+
 '<div class="plot" id="chart-'+q.id+'"></div><figcaption class="sourcebar">真实原报告 2026H1；<span>物理页 '+q.source_pages.join(", ")+'</span>。<p class="counter"><b>反证/边界：</b>'+e(q.counter)+'</p>'+
 '<div id="table-'+q.id+'">'+sourceTable(q)+'</div></figcaption></figure>';
 article.appendChild(section);
 document.querySelector("#chart-"+q.id).innerHTML=draw(q.id)+
  '<div class="native-mobile-finance" data-native-mobile-id="'+e(q.id)+'" role="group" aria-label="财报原数据驱动的手机原生财务图，完整纵向阅读">'+nativeMoneyFigure(q.id)+'</div>';
});
document.querySelectorAll("[data-export]").forEach(function(button){button.addEventListener("click",function(){
var id=button.getAttribute("data-export"),svgs=Array.from(button.closest("figure").querySelectorAll("svg")),s=svgs.find(function(el){var r=el.getBoundingClientRect(),v=getComputedStyle(el);return r.width>0&&r.height>0&&v.display!=="none"&&v.visibility!=="hidden"});if(!s)return;var file=new Blob([new XMLSerializer().serializeToString(s)],{type:"image/svg+xml;charset=utf-8"});
var url=URL.createObjectURL(file),a=document.createElement("a");a.href=url;a.download=code+"-2026H1-"+id+".svg";a.click();URL.revokeObjectURL(url);
})});
})();
</script></body></html>'''

def build(code,out):
    base=SITE/"research"/"issuers"/code
    d=read(base/"source-ledger.json")
    briefs=read(base/"figure-briefs.json")
    story=read(base/"story.json")
    archive=SITE/d["source"]["source_path"]
    checks=check(d,briefs,story,archive)
    def compact(x):return json.dumps(x,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
    # Native mobile original finance grammar is INLINED: one offline standalone HTML per issuer.
    article=HTML.replace("__NATIVE_MOBILE_SVG__", (ROOT/"research/shared/mobile_finance.js").read_text(encoding="utf-8"))
    for a,b in (("__TITLE__",story["lead"]),("__DESCRIPTION__",story["thesis"]),("__EYEBROW__",story["eyebrow"]),
                ("__DEK__",story["dek"]),("__TENSION__",story["tension"]),("__COUNTER__",story["counter"]),
                ("__DISCLAIMER__",story["evidence_disclaimer"]),("__LEDGER__",compact(d)),
                ("__BRIEFS__",compact(briefs)),("__STORY__",compact(story))):
        import html
        if a in {"__LEDGER__","__BRIEFS__","__STORY__"}:article=article.replace(a,b)
        else:article=article.replace(a,html.escape(b,quote=True))
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(article,encoding="utf-8")
    qa=base/"qa.json"
    qa.write_text(json.dumps({"company":code,"report":"2026H1","source_sha256":d["source"]["original_bytes_sha256"],
      "checks":checks,"figure_count":len(briefs["figure_briefs"]), "full_material_notes":"NOT_CHECKED",
      "second_human_independent_editor":"NOT_CHECKED","external_8_to_12_quarters":"NOT_CHECKED",
      "actual_browser":"PENDING_REAL_CHROMIUM","publication_class":"SOURCE_LIMITED_PREVIEW",
      "pdf_bytes":archive.stat().st_size},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TWO_SECTOR_RESEARCH_AUDIT_PASS",code,"source",d["source"]["original_bytes_sha256"],"checks",len(checks),"figures",len(briefs["figure_briefs"]),"html_bytes",out.stat().st_size)
    return checks

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--code",choices=["600900","600276"],required=True);p.add_argument("--out",type=Path)
    a=p.parse_args();build(a.code,a.out or SITE/"public"/(a.code+".html"))
