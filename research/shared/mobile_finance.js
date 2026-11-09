/* VIS-044: source-ledger-derived NATIVE vertical editorial finance art.
   Self-contained inline HTML after Python build; no network/chart libraries.
   All coordinates and values derive from exact already-PDF-verified source ledger.
   Browser QA validates genuine painted money widths / signed waterfalls. */
function mb(x){return Number(x).toFixed(5)}
function mtxt(x,y,s,size,color,weight,anchor){
 return '<text x="'+mb(x)+'" y="'+mb(y)+'" font-size="'+(size||12)+'" fill="'+(color||ink)+'" font-weight="'+(weight||500)+'"'+(anchor?' text-anchor="'+anchor+'"':'')+'>'+e(s)+'</text>';
}
function mrect(x,y,w,h,c,extra){
 return '<rect x="'+mb(x)+'" y="'+mb(y)+'" width="'+mb(Math.max(0,w))+'" height="'+mb(Math.max(0,h))+'" fill="'+c+'" '+(extra||'')+'/>';
}
function msvg(id,height,body,desc){
 return '<svg xmlns="http://www.w3.org/2000/svg" data-native-finance="'+id+'" viewBox="0 0 330 '+height+'" role="img" aria-label="'+e(desc)+'"><g font-family="Noto Sans CJK SC,PingFang SC,Microsoft YaHei,Arial,sans-serif">'+body+'</g></svg>';
}
function mhead(label,sub){
 return mtxt(12,26,label,16,ink,750)+mtxt(12,48,sub,10.5,"#607974",450);
}
function mline(x1,y1,x2,y2,color,width,dashed){
 return '<line x1="'+mb(x1)+'" y1="'+mb(y1)+'" x2="'+mb(x2)+'" y2="'+mb(y2)+'" stroke="'+(color||muted)+'" stroke-width="'+(width||1)+'"'+(dashed?' stroke-dasharray="4 5"':'')+'/>';
}
function moneyNotes(items,y,normalizer){
 var s="";
 items.forEach(function(z,i){
   var yy=y+i*47;
   s+=mline(12,yy-17,318,yy-17,"#e0e7e0",.9);
   s+=mtxt(12,yy,z.label,11,ink,620);
   s+=mtxt(317,yy+17,yi(z.value),12,z.color||green,700,"end");
   s+='<rect x="12" y="'+mb(yy+23)+'" height="3" width="'+mb(306*Math.abs(z.value)/normalizer)+'" fill="'+(z.color||green)+'" opacity=".75" data-exact-money-yuan="'+z.value.toFixed(2)+'"/>';
 });
 return s;
}
function nativeWeightedMoneyFlow(){
 var S=d.segments,total=v("rev"),cost=v("cogs"),gp=total-cost,top=102;
 var H=298,gap=14,usable=H-gap*(S.length-1),scale=usable/total;
 if(!(total>0&&gp>=0&&cost>=0))throw Error("NATIVE_MOBILE_FLOW_ACCOUNTING_INVALID");
 var srcY=top,costY=top,profitY=top+cost*scale+16,body=mhead("收入结构 → 成本 / 毛利","互斥同口径来源 · 按真实元金额缩放 · 2026H1");
 body+=mtxt(12,77,"合并营收 "+yi(total),15,ink,700);
 var actual=0,edgeTotal=0;
 S.forEach(function(z,i){
   var rv=v(z.rev),co=v(z.cost),gm=rv-co,h=rv*scale,srcStart=srcY;
   body+=mrect(25,srcStart,11,h,blue,'class="m-flow-source" data-source-key="'+e(z.rev)+'" data-exact-yuan="'+rv.toFixed(2)+'" data-geometry-height="'+mb(h)+'"');
   var allocated=0;
   [[co,"cogs",copper,costY],[gm,"gross_profit",green,profitY]].forEach(function(target){
     var vv=target[0],kind=target[1],col=target[2],yy=target[3],thick=vv*scale;
     if(vv>0){
       var a=srcStart+allocated,b=a+thick,bot=yy+thick;
       var path='M36 '+mb(a)+' C107 '+mb(a)+' 180 '+mb(yy)+' 268 '+mb(yy)+
          ' L268 '+mb(bot)+' C180 '+mb(bot)+' 107 '+mb(b)+' 36 '+mb(b)+' Z';
       body+='<path class="m-flow-band" data-source-key="'+e(z.rev)+'" data-target-key="'+kind+'" data-exact-yuan="'+vv.toFixed(2)+'" data-geometry-height="'+mb(thick)+'" fill="'+col+'" opacity=".52" d="'+path+'"/>';
       edgeTotal+=vv;
     }
     if(kind==="cogs")costY+=thick;else profitY+=thick;
     allocated+=thick;
   });
   srcY+=h+gap;
   actual+=rv;
 });
 if(Math.abs(actual-total)>Math.max(.005,total*1e-12)||Math.abs(edgeTotal-total)>Math.max(.005,total*1e-12))throw Error("NATIVE_FLOW_LOSS_OF_EXACT_MONEY");
 body+=mrect(268,top,12,cost*scale,copper,'class="m-flow-sink" data-target-key="cogs" data-exact-yuan="'+cost.toFixed(2)+'"');
 body+=mrect(268,top+cost*scale+16,12,gp*scale,green,'class="m-flow-sink" data-target-key="gross_profit" data-exact-yuan="'+gp.toFixed(2)+'"');
 body+=mtxt(12,427,"营业成本",13,copper,750);
 body+=mtxt(318,427,yi(cost),13,copper,750,"end");
 body+=mtxt(12,454,"毛利",13,green,750);
 body+=mtxt(318,454,yi(gp),13,green,750,"end");
 body+=mline(12,470,318,470,"#d8e1db");
 body+=mtxt(12,492,"独立收入分类及金额（图内极小类不人为放大）",11,ink,650);
 body+=moneyNotes(S.map(z=>({label:z.label,value:v(z.rev),color:blue})),520,total);
 body+=mtxt(12,520+S.length*47+14,"验证：所有来源＝合并收入＝成本＋毛利",10.2,"#637a72");
 return msvg("flow",520+S.length*47+38,body,
   "独立原始财报收入来源到营业成本和毛利的真正金额加权手机桑基，不同收入分类不重叠，金额保留真实比例");
}
function nativeSignedWaterfall(id,values,title,remark){
 var start=values.start,steps=values.steps,end=values.end,items=[];
 var current=start;
 items.push({name:steps[0][0],a:0,b:start,delta:start,kind:"opening"});
 var points=[0,start];
 for(var i=1;i<steps.length-1;i++){
   var dlt=steps[i][1],before=current;
   current+=dlt;points.push(current);
   items.push({name:steps[i][0],a:before,b:current,delta:dlt,kind:"delta"});
 }
 if(Math.abs(current-end)>Math.max(.03,Math.abs(end)*1e-11))throw Error("SOURCE_SIGNED_BRIDGE_NOT_CLOSED "+id+" "+current+" "+end);
 items.push({name:steps[steps.length-1][0],a:0,b:end,delta:end,kind:"ending"});
 var lo=Math.min.apply(null,points),hi=Math.max.apply(null,points);
 if(hi-lo<1)hi=lo+1;
 var shift=16,range=292,sc=range/(hi-lo),X=function(z){return shift+(z-lo)*sc};
 var yy=78,bh=78,out=mhead(title,remark);
 out+=mtxt(13,66,"原始人民币元计算 · 同一金额轴 · 有符号逐项结转",10,"#738780");
 items.forEach(function(z,i){
   var y0=yy+i*bh,pa=X(z.a),pb=X(z.b),col=z.kind==="ending"?green:z.kind==="opening"?blue:z.delta<0?red:green;
   out+=mtxt(13,y0+10,z.name,12,ink,660);
   out+=mtxt(317,y0+10,(z.kind==="delta"&&z.delta>0?"+":"")+(z.kind==="delta"&&z.delta<0?"−":"")+yi(Math.abs(z.delta)),11.5,col,700,"end");
   out+=mline(16,y0+29,308,y0+29,"#e0e6e1",.9);
   out+=mline(X(0),y0+18,X(0),y0+44,"#8da59c",1.25);
   if(Math.abs(pb-pa)>0){
     out+=mrect(Math.min(pa,pb),y0+23,Math.abs(pb-pa),13,col,
        'class="m-signed-bridge" data-step="'+i+'" data-kind="'+z.kind+'" data-start-yuan="'+z.a.toFixed(2)+'" data-end-yuan="'+z.b.toFixed(2)+'" data-delta-yuan="'+z.delta.toFixed(2)+'"');
   }
   out+='<circle cx="'+mb(pb)+'" cy="'+mb(y0+29.5)+'" r="2.25" fill="'+col+'"/>';
   out+=mtxt(317,y0+62,"累计 "+yi(z.b),11,"#657c72",550,"end");
   if(i<items.length-1)out+=mline(pb,y0+43,X(items[i+1].a),y0+bh+19,"#b6c8c0",.75,true);
 });
 out+=mtxt(12,yy+items.length*bh+2,"每条增减的真实宽度＝变动金额 ÷ 全桥共同金额尺度",10.3,"#637a72");
 out+=mtxt(12,yy+items.length*bh+23,"期末必须由全部原始有符号调整严格勾稽",10.3,"#637a72");
 return msvg(id,yy+items.length*bh+45,out,title+"，真实原始金额守恒的逐项有符号竖向瀑布，负值为扣减");
}
function nativeTrend(){
 var out=mhead("收入、毛利、经营现金为什么不同步？","2025H1 对比 2026H1，各指标独立比例尺");
 var series=[
  {name:"营业收入",old:v("rev_prior"),now:v("rev")},
  {name:"营业毛利",old:v("rev_prior")-v("cogs_prior"),now:v("rev")-v("cogs")},
  {name:"经营现金流",old:v("cfo_prior"),now:v("cfo")}
 ];
 series.forEach(function(z,i){
   var y0=90+i*180,m=Math.max(Math.abs(z.old),Math.abs(z.now),1),w=286/m;
   var growth=z.old!==0?(z.now/z.old-1)*100:null;
   out+=mtxt(12,y0,z.name,15,ink,700);
   out+=mtxt(318,y0, growth===null?"不可计算":(growth>=0?"+":"")+growth.toFixed(2)+"%",12,growth>=0?green:red,740,"end");
   [[z.old,"2025 H1",muted],[z.now,"2026 H1",green]].forEach(function(r,j){
     var yy=y0+27+j*62;
     out+=mtxt(12,yy,r[1],11,ink,560);
     out+=mtxt(318,yy,yi(r[0]),12,r[2],740,"end");
     out+=mrect(12,yy+11,Math.abs(r[0])*w,17,r[2],
       'class="m-trend-pair" data-metric="'+i+'" data-period="'+j+'" data-source-yuan="'+r[0].toFixed(2)+'"');
   });
 });
 out+=mtxt(12,640,"绝不跨单位比较条长，不暗示不存在的多季度趋势",10.1,"#637a72");
 return msvg("trend",663,out,"三项会计口径各自从零基准进行的两期原始收入、毛利和经营现金比较");
}
function nativeBalance(){
 var total1=v("assets_prior"),total2=v("assets"),max=Math.max(total1,total2),S=286/max;
 var rows=[
 {name:"2025 年 12 月",total:total1,components:[["负债",v("liabilities_prior"),copper],["股东权益合计",v("equity_prior"),green]]},
 {name:"2026 年 06 月",total:total2,components:[["负债",v("liabilities"),copper],["归属母公司权益",v("parent_equity"),green],["少数股东权益",v("nci_equity"),blue]]}
 ];
 var out=mhead("资产的资金来源结构如何变化？","法定合并资产＝负债＋全部股东权益｜2025末 vs 2026H1");
 rows.forEach(function(z,i){
   var yy=82+i*243,x=17,sum=0;
   out+=mtxt(12,yy,z.name,14,ink,730);
   out+=mtxt(318,yy,yi(z.total),12,ink,730,"end");
   z.components.forEach(function(vz){
     var ww=vz[1]*S;sum+=vz[1];
     out+=mrect(x,yy+17,ww,29,vz[2],
      'class="m-balance-component" data-period="'+i+'" data-amount-yuan="'+vz[1].toFixed(2)+'"');
     x+=ww;
   });
   if(Math.abs(sum-z.total)>Math.max(.005,z.total*1e-12))throw Error("MOBILE_BALANCE_SOURCE_NOT_CONSERVED");
   z.components.forEach(function(vz,j){
     out+=mrect(13,yy+65+j*43,10,10,vz[2]);
     out+=mtxt(30,yy+75+j*43,vz[0],12,ink,580);
     out+=mtxt(317,yy+75+j*43,yi(vz[1]),12,vz[2],690,"end");
   });
 });
 out+=mtxt(12,574,"同一共同金额尺度，两期总资产宽度可比较",10.1,"#637a72");
 return msvg("balance",603,out,"两日期末合并资产由负债和股东权益构成的真实源金额平衡表结构");
}
function nativeSectorOperating(key,unit){
 var fact=f[key];
 if(!fact||fact.type!=="operating_metric"||fact.classification!=="MANAGEMENT_REPORTED"||fact.unit!==unit||
    fact.period!==d.issuer.fiscal_period||fact.scope!=="consolidated")throw Error("PHONE_OPERATING_SOURCE_SEMANTIC_MISMATCH "+key);
 var v0=Number(fact.yuan);
 if(!Number.isFinite(v0)||v0<=0)throw Error("PHONE_OPERATING_METRIC_NONPOSITIVE "+key);
 return v0;
}
function nativeSector(){
 var out="";
 if(story.theme==="hydro"){
   var power=nativeSectorOperating("power_gen_100m_kwh","亿千瓦时");
   out=mhead("水电真实产出不是账面现金流","两种不同计量单位，绝不画虚构人民币资金箭头");
   out+=mrect(12,75,306,118,"#edf5ed",'rx="9" data-source-fact="power_gen_100m_kwh" data-original-value="'+power+'"');
   out+=mtxt(23,105,"六座梯级电站 · 发电量",12,ink,620);
   out+=mtxt(23,151,Number(power).toLocaleString("zh-CN",{maximumFractionDigits:2})+" 亿千瓦时",23,green,760);
   out+=mtxt(13,229,"法定营业收入（确认口径）",12,ink,610);
   out+=mtxt(317,256,yi(v("rev")),21,blue,720,"end");
   out+=mline(12,275,318,275);
   out+=mtxt(13,307,"经营现金净流入（收付口径）",12,ink,610);
   out+=mtxt(317,337,yi(v("cfo")),21,green,720,"end");
   out+=mrect(12,375,3,77,copper);
   out+=mtxt(23,391,"这三个量不在同一个加总维度",12,ink,690);
   out+=mtxt(23,417,"缺净售电量、合同电价和调度数据",11,"#637a72");
   out+=mtxt(23,440,"不能从“发电量÷收入”构造伪电价",11,"#637a72");
   return msvg("sector",471,out,"水电发电量、法定收入和经营现金流是三种不同统计口径，不得虚构同金额的加总资金流");
 }
 var rv=v("rev"),prod=v("drug_sales_rev"),lic=v("licence_rev"),other=v("other_rev");
 var innov=nativeSectorOperating("innovative_drug_sales_100m","亿元"); // managed subset, not independently additive revenue
 if(!(rv>0&&prod>0))throw Error("MOBILE_PHARMA_REVENUE_DENOM");
 var parts=[["药品等商品",prod,green],["知识产权许可",lic,copper],["其他合同收入",other,blue]],sc=286/rv;
 var w=0;
 out=mhead("创新药是药品销售内部的子集","合同收入分类互斥；管理层创新药统计不再累加");
 out+=mtxt(12,86,"本期合并营业收入 "+yi(rv),14,ink,700);
 parts.forEach(function(z){out+=mrect(16+w,105,z[1]*sc,35,z[2],
     'class="m-pharma-contract" data-source-yuan="'+z[1].toFixed(2)+'"');w+=z[1]*sc});
 parts.forEach(function(z,i){
   out+=mrect(12,163+i*39,9,9,z[2]);
   out+=mtxt(27,172+i*39,z[0],11,ink,600);
   out+=mtxt(318,172+i*39,yi(z[1]),11.5,z[2],750,"end");
 });
 var innovRMB=innov*100000000;
 if(innovRMB>prod||innovRMB<0)throw Error("INNOVATION_SUBSET_NOT_IN_GOODS");
 out+=mtxt(12,317,"商品销售内部分：创新药并非新增一条营收",10.5,ink,670);
 out+=mrect(16,334,innovRMB/prod*286,28,green,'class="m-pharma-innovation" data-operating-fact="innovative_drug_sales_100m" data-subset-yuan="'+innovRMB.toFixed(2)+'"');
 out+=mrect(16+innovRMB/prod*286,334,(prod-innovRMB)/prod*286,28,muted);
 out+=mtxt(13,399,"创新药（管理层口径）",11,ink,620);
 out+=mtxt(318,399,yi(innovRMB),13,green,700,"end");
 out+=mtxt(12,433,"许可收入不能当成可重复药品销售",11,"#637a72");
 out+=mtxt(12,451,"RPO未履约金额不属于本期已确认收入",11,"#637a72");
 out+=mtxt(12,469,"数据详见本图原始PDF页码/未缩约人民币表",10.5,"#637a72");
 return msvg("sector",494,out,"药品合同收入分组全部守恒及创新药按原管理层口径为药品销售内嵌子集的竖向原生图");
}
function nativeCapital(){
 var cfo=v("cfo"),cap=v("cash_capex"),free=cfo-cap;
 var bridge={start:cfo,steps:[["经营现金",null],["购建长期资产", -cap],["简易自由现金",null]],end:free};
 var s=nativeSignedWaterfall("capital",bridge,"CFO支付真正现金投入之后","合并经营现金−购建长期资产现金，不是法定FCF");
 // Keep a separately identified source cash vs noncash supplemental panel,
 // not mixed into the signed cash waterfall.
 var panel='<div class="native-mobile-finance-supplement" data-capital-supplement="true">'+
 '<p>真实支付与非现金结算分开：股利、利润及利息合计现金支付 <strong>'+e(yi(v("dividend_interest_cash")))+'</strong>，不得当成纯股息。</p>';
 if(f.bill_endorse_capex){
    panel+='<p>背书票据用于长期资产购建 <strong>'+e(yi(v("bill_endorse_capex")))+'</strong>，属于非现金支付，不能计入上述现金FCF。</p>';
 }
 return s+panel+'</div>';
}
function nativeMoneyFigure(id){
 if(id==="flow")return nativeWeightedMoneyFlow();
 if(id==="pnl")return nativeSignedWaterfall("pnl",PNLsteps(),"毛利如何成为归母净利润？","原始 CAS 利润表加减与真实正负号");
 if(id==="cfo")return nativeSignedWaterfall("cfo",cfoSteps(),"净利润为什么没有全部变成现金？","净利润 + 原报告间接调整 → CFO");
 if(id==="cash")return nativeSignedWaterfall("cash",cashSteps(),"现金怎样从期初走到期末？","经营 / 投资 / 筹资 / 汇率，真实符号");
 if(id==="balance")return nativeBalance();
 if(id==="trend")return nativeTrend();
 if(id==="sector")return nativeSector();
 if(id==="capital")return nativeCapital();
 throw Error("UNKNOWN_NATIVE_ACCOUNTING_CHART "+id);
}
