from __future__ import annotations
import html, json, hashlib
from decimal import Decimal as D
from pathlib import Path
from collections import Counter

OUT=Path(__file__).resolve().parent
SOURCE=OUT/'cmb_verified_0194f512.pdf'
SHA='0194f5122575ee8576dbce941fcc10fb171e0cd17c627dd63330da952c52b57c'
URL='https://static.cninfo.com.cn/finalpage/2026-08-28/1225531453.PDF'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA

def n(x):return D(str(x))
def yi(x):return n(x)/D(100) # amounts in RMB million -> 亿

def s(x):return html.escape(str(x),quote=True)
def fmt(x,d=2):return f'{n(x):,.{d}f}'
def fyi(x):return fmt(yi(x))
def rect(x,y,w,h,color='#087f69',radius=3):return f'<rect x="{x:.2f}" y="{y:.2f}" width="{max(0,w):.2f}" height="{max(0,h):.2f}" rx="{radius}" fill="{color}"/>'
def label(x,y,t,sz=17,fill='#21443c',anchor='start',weight=500):return f'<text x="{x:.2f}" y="{y:.2f}" font-size="{sz}" font-family="Arial,Noto Sans CJK SC,sans-serif" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{s(t)}</text>'
def base(svg,height=420,desc='Financial source-checked chart'):return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 {height}" role="img" aria-label="{s(desc)}">{svg}</svg>'

def horizontal(rows,title,unit='亿元',colors=None,width=1000):
    vals=[float(n(q[1])) for q in rows];maxv=max(max(vals),1)
    out=label(40,30,title,19,'#143a3b',weight=650)
    for i,(name,v,desc) in enumerate(rows):
        y=73+i*72;col=(colors or ['#087f69','#5f8391','#ba8868','#8ba99c'])[i%4]
        out+=label(330,y+22,name,16,anchor='end')
        out+=rect(350,y,490*max(0,float(n(v)))/maxv,29,col)
        out+=label(min(910,358+490*max(0,float(n(v)))/maxv),y+22,fmt(v)+' '+unit,16,weight=700)
    return base(out,height=100+len(rows)*72,desc=title)

def waterfall(start,steps,final,subtitle,unit='亿元'):
    points=[('期初',n(start), 'total')]+[(str(a),n(b),'step') for a,b in steps]+[('期末',n(final),'total')]
    cumul=n(start)
    vals=[n(start)]
    for _,a in steps:cumul+=n(a);vals.append(cumul)
    assert cumul==n(final)
    vmax=max(vals+[n(final)])*D('1.15'); scale=290/float(vmax)
    gap=915/len(points);out=label(38,30,subtitle,19,weight=650)
    out+='<line x1="42" y1="370" x2="962" y2="370" stroke="#a5b9af"/>'
    running=n(0)
    for i,(name,value,t) in enumerate(points):
        x=47+i*gap;w=min(gap-18,155)
        if i==0:bottom=n(0);top=value;running=value
        elif i==len(points)-1:bottom=n(0);top=value
        else:prev=running;running+=value;bottom=min(prev,running);top=max(prev,running)
        height=float(top-bottom)*scale;y=370-float(top)*scale
        col='#113f3e' if i==0 else '#087f69' if t=='total' or value>0 else '#b9866b'
        out+=rect(x,y,w,max(height,1.5),col)
        out+=label(x+w/2,max(48,y-13),('+' if t=='step' and value>=0 else '')+fmt(value),15,anchor='middle',weight=750)
        out+=label(x+w/2,402,name,14,fill='#54716a',anchor='middle')
    return base(out,height=447,desc=subtitle)

def mini_dumbbells(items,title,domain=100):
    out=label(45,38,title,19,weight=650)
    for i,(name,old,new,unit) in enumerate(items):
        y=100+i*86
        out+=label(47,y-14,name,17,weight=650)
        lo=min(float(old),float(new));hi=max(float(old),float(new)); axis=450;maxv=max(hi*1.08,float(domain))
        def xx(v):return axis+480*float(v)/maxv
        out+=f'<line x1="{xx(0)}" y1="{y}" x2="{xx(maxv)}" y2="{y}" stroke="#c4d3cb" stroke-width="3"/>'
        out+=f'<line x1="{xx(lo)}" y1="{y}" x2="{xx(hi)}" y2="{y}" stroke="#a4bcb0" stroke-width="7"/>'
        out+=f'<circle cx="{xx(old)}" cy="{y}" r="10" fill="#bc9f8b" stroke="white" stroke-width="2"/>'
        out+=f'<circle cx="{xx(new)}" cy="{y}" r="10" fill="#087f69" stroke="white" stroke-width="2"/>'
        out+=label(47,y+20,f'基期 {fmt(old)}{unit}  →  本期 {fmt(new)}{unit}',14,fill='#58736c')
    return base(out,height=135+len(items)*86,desc=title)

def grouped_bridge():
    sectors=[('零售金融',52036,42888),('批发金融',37057,45703),('其他业务',-187,2146)]
    out=label(45,32,'分部税前利润的变动方向不同：零售降、批发升',19,weight=650)
    center=520;mx=11000
    out+=f'<line x1="{center}" y1="70" x2="{center}" y2="355" stroke="#8ba59c" stroke-width="2"/>'
    for i,(name,old,new) in enumerate(sectors):
        delta=new-old;y=90+i*93
        out+=label(160,y+20,name,18,anchor='middle',weight=650)
        x=center if delta>=0 else center-abs(delta)/mx*350
        out+=rect(x,y,abs(delta)/mx*350,32,'#087f69' if delta>=0 else '#bb8065')
        out+=label(900,y+22,('+' if delta>=0 else '')+fyi(delta)+' 亿元',17,anchor='end',weight=700)
        out+=label(160,y+45,f'{fyi(old)} → {fyi(new)} 亿元',13,anchor='middle',fill='#607670')
    return base(out,height=388,desc='零售、批发、其他分部税前利润变动：正负横向方向')

def deposit_mix():
    entries=[('公司活期',2878139,'#087f69'),('公司定期',2638367,'#6791a0'),('零售活期',2335473,'#bb9376'),('零售定期',2310519,'#9cafa2')]
    total=sum(x[1] for x in entries);assert total==10162498
    out=label(36,32,'存款结构：活期和定期接近各半（期末时点）',20,weight=650)
    x=42
    for name,v,c in entries:
        w=900*v/total
        out+=rect(x,100,w,65,c,0)
        if w>95: out+=label(x+w/2,139,f'{100*v/total:.1f}%',17,'white',anchor='middle',weight=750)
        x+=w
    for i,(name,v,c) in enumerate(entries):
        x=68+(i%2)*460;y=216+(i//2)*64
        out+=rect(x,y-18,20,20,c,3)
        out+=label(x+34,y,name+' · '+fyi(v)+' 亿元',17,weight=600)
    return base(out,height=354,desc='期末银行客户存款四个不重叠类别比例')

def ratio_points():
    points=[('净利息收益率 NIM',1.88,1.83,'%', '盈利'),('成本收入比',30.11,29.70,'%','费用'),('不良率',0.94,0.94,'%','信贷'),('拨备覆盖率',391.79,385.10,'%','信贷')]
    out=label(44,38,'盈利／资产质量关键指标：四个同类时间对照，不同横轴',19,weight=650)
    for i,(name,old,new,unit,_) in enumerate(points):
        y=87+i*84;delta=new-old
        out+=label(42,y+10,name,17,weight=650)
        out+=label(490,y+10,fmt(old)+unit+' → '+fmt(new)+unit,17)
        out+=label(925,y+10,('+' if delta>0 else '')+fmt(delta)+' pp',17,'#087f69' if delta>=0 else '#b67d60',anchor='end',weight=650)
        out+=f'<line x1="44" y1="{y+34}" x2="950" y2="{y+34}" stroke="#e1e8e2"/>'
    return base(out,height=442,desc='不同指标不共享百分比横轴的变化直接标记')

figures=[]
def figure(number,section,id,title,question,body,chart,raws,pg,readout,warning):
    rows=''.join(f'<tr><td>{s(label)}</td><td>{s(val)}</td><td>{s(units)}</td><td>PDF p.{p}</td></tr>' for label,val,units,p in raws)
    fig=f'''<figure id="fig-{number:02d}" class="exhibit"><div class="fig-head"><div><span class="fig-kicker">FIG {number:02d} / {s(section)}</span><h3>{s(title)}</h3><p class="fig-q">{s(question)}</p></div><button class="svg-export" type="button" aria-label="导出第{number}幅图 SVG">导出 SVG ↗</button></div><div class="chart-window" tabindex="0" aria-label="分析图形，窄屏可横向查看">{chart}</div><p class="direct"><strong>读图结论 · </strong>{s(readout)}</p><p class="source">来源：<a href="{URL}#page={pg}" target="_blank" rel="noopener">招商银行 2026H1 原始 A 股报告，PDF p.{pg}</a>。所涉其他行见展开明细。</p><div class="caution">{s(warning)}</div><details><summary>展开原始数值、来源页和计量单位</summary><div class="table-scroll"><table><thead><tr><th>原始字段</th><th>原值</th><th>原单位</th><th>物理页</th></tr></thead><tbody>{rows}</tbody></table></div></details></figure>'''
    figures.append((id,fig))
    return fig

raw=lambda *entries: [(z[0],str(z[1]),'人民币百万元' if len(z)<4 else z[3],z[2]) for z in entries]

# 1: core revenue economics
f1=figure(1,'EARNINGS','rev','银行的收入不是营业额','净利息收入与手续费等三类收入如何构成当期收入？',
   '银行通过资产与负债之间的利差、手续费和其他金融业务净收入创造利润。此处“净利息收入”已扣除利息支出，不能与工业企业营收/毛利混同。',
   horizontal([('净利息收入',yi(112022),'p.13'),('净手续费收入',yi(39855),'p.13'),('其他净收入',yi(26304),'p.13')], '1,781.81亿元收入的三个可加总来源'),
   raw(('营业收入',178181,8),('净利息收入',112022,13),('净手续费及佣金收入',39855,13),('其他净收入',26304,13)),
   13,'净利息收入 1,120.22 亿元（约62.9%）。非利息收入占37.1%，而非毛利“其他收入”。',
   '收入构成是银行集团同期间来源，不应与不同口径财富管理业务收入等交叉分类叠加。')

# 2: NII rate/scale 2025 to 2026
f2=figure(2,'NET INTEREST INCOME','rates','净息差继续下降，净利息收入为何仍增长？','官方披露的“规模贡献”和“利率贡献”各是多少？',
   '2026H1 平均生息资产收益率同比下降32基点，平均计息负债成本率下降30基点。资产端与负债端均再定价，净息差仍由1.88%降至1.83%。',
   waterfall(1060.85,[('规模效应',82.79),('利率效应',-23.42)],1120.22,'净利息收入同比桥 · 人民币亿元'),
   raw(('2025H1 净利息收入',106085,13),('规模因素对NII变动',8279,16),('利率因素对NII变动',-2342,16),('2026H1 净利息收入',112022,13)),
   16,'规模因素贡献 +82.79 亿元，利率因素拖累 −23.42 亿元，合计推动净利息收入 +59.37 亿元。',
   '规模/利率贡献采用发行人报告的归因方法，交互项按报告约定归入规模；不能把这一会计分解解读为精确经济因果。')

# 3: signed P&L source
f3=figure(3,'EARNINGS QUALITY','pl','从收入到净利润，钱在哪个环节消失？','银行营业支出和信用减值如何影响税后利润？',
   '最显著的费用是业务及管理费529.12亿元，信用减值损失291.77亿元。银行的信用成本具有周期性，不能仅用CFO/净利润评估利润质量。',
   waterfall(1781.81,[('经营管理费',-529.12),('税金及附加',-15.08),('信用减值',-291.77),('其他减值',-0.14),('其他业务成本',-37.87),('营业外净额',-0.46),('所得税',-138.18)],769.19,'营业收入 → 合并净利润，带符号的正式利润桥'),
   raw(('营业收入',178181,13),('业务及管理费',-52912,13),('税金及附加',-1508,13),('信用减值损失',-29177,13),('其他资产减值损失',-14,13),('其他业务成本',-3787,13),('营业外收支净额',-46,13),('所得税费用',-13818,13),('合并净利润',76919,13),('归母净利润',76445,13)),
   13,'合并净利润 769.19 亿元，归母净利润 764.45 亿元；两者差额 4.74 亿元属于少数股东损益。',
   '本桥严格使用合并利润表同期间带符号行，数值为集团口径；不能把归母数直接代入合并的所有损益环节。')

# 4: business segments of earnings
f4=figure(4,'SEGMENT ECONOMICS','segments','零售仍贡献大收入，但利润为什么承压？','零售、批发和其他分部税前利润的变动方向是什么？',
   '零售收入同比增长0.65%，但税前利润下降17.58%；批发收入及税前利润上升。两块业务的变化不应只以收入占比评价，需要结合零售资产质量、信用成本与经营费用。',
   grouped_bridge(),
   raw(('零售2025H1 税前利润',52036,34),('零售2026H1 税前利润',42888,34),('批发2025H1 税前利润',37057,34),('批发2026H1 税前利润',45703,34),('其他2025H1 税前利润',-187,34),('其他2026H1 税前利润',2146,34),('2026H1集团税前利润',90737,34)),
   34,'零售分部税前利润同比减少91.48亿元，批发分部增加86.46亿元；集团税前利润仅增18.31亿元。',
   '分部收益与税前利润的实际口径以报告附注46为准；“分部变化”不是个人存贷款客户盈利因果归因。')

# 5: funding deposit stock mix
f5=figure(5,'FUNDING','deposits','银行负债端的核心竞争力是什么？','客户存款的活期/定期与公司/零售结构如何？',
   '客户存款总额 10.16 万亿元，占负债81.74%。在资产端利率下行时期，负债结构决定存款成本调降能否抵消贷款重定价压力。',
   deposit_mix(),
   raw(('公司活期存款',2878139,23),('公司定期存款',2638367,23),('零售活期存款',2335473,23),('零售定期存款',2310519,23),('客户存款总额',10162498,23),('客户存款平均成本率2026H1',0.97,15,'百分比'),('2025H1平均成本率',1.26,15,'百分比')),
   23,'公司与零售活期合计超过5.21万亿元；日均存款成本率由1.26%降至0.97%。',
   '柱内各部分是6月30日期末余额，而存款平均成本率是整个上半年的日均余额口径；两者不可直接倒算融资费用。')

# 6: loan quality and allowance
f6=figure(6,'CREDIT QUALITY','quality','不良率看似稳定，风险缓冲有没有变？','不良贷款余额、拨备覆盖率、信用成本如何同时变化？',
   '不良贷款率维持0.94%，但不良贷款余额由682.06增至702.51亿元；拨备覆盖率由391.79%降至385.10%。逾期贷款占比也从1.25%升至1.31%。',
   ratio_points(),
   raw(('2025年末不良贷款余额',68206,9),('2026年6月不良贷款余额',70251,9),('2026H1不良贷款率',0.94,10,'百分比'),('2025年末不良率',0.94,10,'百分比'),('2026年6月拨备覆盖率',385.10,10,'百分比'),('2025年末拨备覆盖率',391.79,10,'百分比'),('2026H1信用成本',0.69,10,'百分比'),('2025H1信用成本',0.67,10,'百分比'),('2026年6月逾期贷款率',1.31,29,'百分比')),
   10,'不良率持平不等于不良贷款余额不变；覆盖率下降6.69个百分点，信用成本升2基点。',
   '本图将年化信用成本/净息差等期间指标与期末资产质量指标分列，不能在同一坐标轴或时间逻辑中加总。')

# 7: bank loss provision identity
f7=figure(7,'PROVISION FORENSICS','allowance','拨备变化：计提了多少、又核销了多少？','贷款损失准备由期初到期末如何精确勾稽？',
   '当期信用减值计提、回收已核销贷款、核销与汇率变动同时影响准备余额。不能拿不良贷款余额变化直接作为坏账费用。',
   waterfall(2672.22,[('本期计提',254.63),('收回已核销',66.98),('核销／处置',-283.71),('汇率及其他',-4.76)],2705.36,'贷款损失准备 · 真实会计期间变化桥'),
   raw(('上年末准备余额',267222,30),('本期计提',25463,30),('收回已核销贷款',6698,30),('期内核销／处置',-28371,30),('汇率及其他',-476,30),('期末余额',270536,30)),
   30,'2,672.22 +254.63 +66.98 −283.71 −4.76 = 2,705.36 亿元，逐元勾稽。',
   '本期计提与合并利润表信用减值损失291.77亿元口径不同（前者为贷款损失准备）；不可直接混同。')

# 8: capital and risk-weighted assets
f8=figure(8,'CAPITAL','capital','资本在增长，核心一级资本率为何仍小幅下降？','核心资本增长与风险加权资产增长，谁更快？',
   '高级法下核心一级资本净额同比上年末增长4.47%，风险加权资产增长5.16%。分母扩张略快于资本，CET1比率因此从14.16%降至14.07%。',
   mini_dumbbells([('核心一级资本充足率',14.16,14.07,'%'),('一级资本充足率',16.51,16.59,'%'),('总资本充足率',18.24,18.33,'%')],'资本率是三个不同资本层级，不相互相加',20),
   raw(('核心一级资本净额2026',1115273,31),('核心一级资本净额2025末',1067560,31),('风险加权资产2026',7928939,31),('风险加权资产2025末',7540202,31),('CET1率2026',14.07,31,'百分比'),('CET1率2025末',14.16,31,'百分比'),('监管最低要求',8.25,30,'百分比')),
   31,'CET1率14.07%，高于报告披露的8.25%集团适用要求；但比上年末低0.09个百分点。',
   '使用高级法并考虑资本底线的集团口径。披露的最低资本要求含特定缓冲要求，不等于所有银行统一监管线。')

# 9: CFO (bank-native caveat)
f9=figure(9,'CASH FLOW','cash','现金流为何猛增，却不能等于利润质量改善？','银行经营现金流、投资现金流和筹资现金流的方向如何？',
   '合并经营活动现金净流入由1,344.61亿元升至3,046.11亿元，管理层指出主要因同业往来净流入增加。银行的存放同业、客户存款与贷款等是经营资产负债，不应按工业企业“经营现金流/净利润”直接评分。',
   horizontal([('经营现金流净流入',3046.11,'+'),('投资现金净流出绝对额',1662.44,'-'),('筹资现金净流出绝对额',72.46,'-')],'三类现金流的规模（图示使用绝对值，正负以文字注明）',colors=['#087f69','#ba8868','#7b94a7']),
   raw(('2026H1 CFO净额',304611,8),('2025H1 CFO净额',134461,8),('2026H1 CFI净额',-166244,34),('2026H1 CFF净额',-7246,34)),
   34,'CFO +126.54%主要不是零售手续费同比增长的结果，不能等价于主营现金创造“翻倍”。',
   '图使用绝对柱长并独立标明现金流方向，不是可加总的现金余额闭合桥。完整现金及现金等价物闭合尚需原表汇率影响及货币资金口径。')

assert n(112022)+n(39855)+n(26304)==n(178181)
assert n(178181)-sum(map(n,[52912,1508,29177,14,3787,46]))==n(90737)
assert n(90737)-n(13818)==n(76919)
assert n(76919)-n(76445)==n(474)
assert n(8279)-n(2342)==n(112022)-n(106085)
assert n(42888)+n(45703)+n(2146)==n(90737)
assert n(96820)+n(75536)+n(5825)==n(178181)
assert n(2878139)+n(2638367)+n(2335473)+n(2310519)==n(10162498)
assert n(267222)+n(25463)+n(6698)-n(28371)-n(476)==n(270536)
assert abs(n(270536)/n(70251)*100-n('385.10'))<n('0.01')

CSS='''
:root{--ink:#123a3b;--accent:#087f69;--paper:#fffefd;--canvas:#f6f5f0;--muted:#62736e;--rule:#d6e1d9;--copper:#ba896e;--serif:Georgia,"Songti SC","Noto Serif CJK SC",serif;--sans:-apple-system,BlinkMacSystemFont,"PingFang SC","Noto Sans CJK SC",Arial,sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{background:var(--canvas);color:var(--ink);margin:0;font:15px/1.85 var(--sans)}a{color:inherit;text-underline-offset:3px}a:focus-visible,button:focus-visible{outline:3px solid var(--accent);outline-offset:3px}.wrap{width:min(1120px,calc(100% - 45px));margin:auto}.mast{background:#fdfcf8;border-bottom:1px solid var(--rule);position:sticky;top:0;z-index:10}.nav{display:flex;justify-content:space-between;flex-wrap:wrap;gap:20px;align-items:center;min-height:70px}.brand{text-decoration:none;font-size:12px;font-weight:800;letter-spacing:.12em}.nav-links{display:flex;gap:18px;flex-wrap:wrap;font-size:12px}.nav-links a{text-decoration:none;color:#456962}.hero{padding:88px 0 83px}.eyebrow{font-size:11px;font-weight:800;letter-spacing:.2em;text-transform:uppercase;color:#08826e}.hero h1{font:500 clamp(40px,6vw,74px)/1.24 var(--serif);letter-spacing:-.035em;max-width:1020px;margin:24px 0 25px}.deck{font-size:19px;line-height:1.8;max-width:930px;color:#50746b}.hero-meta{color:var(--muted);font-size:12px;margin-top:25px}.hero-meta code{overflow-wrap:anywhere;word-break:break-word}.keyline{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border-top:1px solid #789b90;border-bottom:1px solid #789b90;margin-top:50px}.keyline div{padding:22px 24px;border-right:1px solid var(--rule)}.keyline div:first-child{padding-left:0}.keyline div:last-child{border:0}.keyline small{display:block;color:var(--muted);font-size:12px}.keyline strong{font:600 35px/1.3 Georgia,var(--serif);display:block}.keyline span{font-size:11px;color:#698179}.chapter{padding:68px 0 0}.chapter-kicker{color:var(--accent);font-size:12px;font-weight:750;letter-spacing:.12em}.chapter h2{font:500 clamp(28px,3.8vw,48px)/1.25 var(--serif);margin:12px 0 22px;max-width:870px}.chapter .lead{color:#4a6560;font-size:17px;max-width:930px;line-height:1.85}.exhibit{margin:38px 0 25px;background:var(--paper);border:1px solid var(--rule);padding:32px 34px;box-shadow:0 14px 30px #18383209}.fig-head{display:flex;align-items:start;justify-content:space-between;gap:30px}.fig-kicker{font-size:11px;font-weight:850;letter-spacing:.13em;color:var(--accent)}.exhibit h3{font:600 clamp(23px,2.7vw,32px)/1.4 var(--serif);margin:9px 0 5px}.fig-q{color:var(--muted);margin:0;font-size:13px}.svg-export{border:1px solid var(--rule);background:#fff;color:#32534d;padding:8px 12px;border-radius:3px;cursor:pointer;font-size:12px;white-space:nowrap}.chart-window{width:100%;overflow-x:auto;max-width:100%;padding:25px 0 10px;margin-top:20px;border-top:1px solid var(--rule)}.chart-window svg{display:block;width:100%;min-width:680px;height:auto}.direct{font-size:14px;border-top:1px solid var(--rule);margin-top:15px;padding-top:14px;color:#365d54}.direct strong{color:var(--accent)}.source{font-size:12px;color:var(--muted)}.caution{background:#f8f2e9;border-left:3px solid #bb8968;padding:11px 15px;font-size:13px;color:#66544e}.exhibit details{margin-top:15px}summary{color:var(--accent);cursor:pointer;font-size:12px;font-weight:750}.table-scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px;margin-top:13px}th,td{padding:8px;border-bottom:1px solid var(--rule);text-align:left}td:nth-child(2){font-variant-numeric:tabular-nums}.insight{background:#edf3ed;border-left:3px solid var(--accent);padding:22px 26px;margin:32px 0;font-size:15px}.redteam{border-left:3px solid var(--copper);background:#f8f2e9;padding:23px 28px;margin:30px 0}.redteam h3{font-size:17px;margin:0 0 5px}.redteam p{margin:0}.conclusion{font-size:16px;line-height:2}.takeaway-list{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px}.takeaway-list article{background:#fffefa;border-top:3px solid #087f69;padding:20px 23px}.takeaway-list b{font-size:13px;color:#087f69}.takeaway-list p{color:#4a5f59;font-size:14px}.footnotes{padding:36px 0 70px;font-size:13px;color:var(--muted)}.footnotes code{overflow-wrap:anywhere;word-break:break-all}.footnotes h2{color:var(--ink)}.footer{border-top:1px solid var(--rule);padding:23px 0;font-size:12px;color:var(--muted)}@media(max-width:900px){.keyline{grid-template-columns:repeat(2,minmax(0,1fr))}.keyline div:nth-child(2){border-right:0}.keyline div:nth-child(-n+2){border-bottom:1px solid var(--rule)}.takeaway-list{grid-template-columns:1fr}}@media(max-width:600px){.wrap{width:calc(100% - 28px)}.hero{padding:46px 0}.hero h1{font-size:clamp(36px,10.5vw,50px)}.deck{font-size:16px}.keyline strong{font-size:29px}.keyline div{padding:16px 12px}.chapter{padding-top:45px}.chapter h2{font-size:32px}.exhibit{padding:20px 16px}.fig-head{gap:14px}.svg-export{padding:6px 8px;font-size:11px}.chart-window svg{min-width:760px}.nav-links{gap:10px}}
'''
DOC=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="招商银行2026H1原始A股财报深度研究预览：利率/规模桥、收益质量、零售、拨备、资本、现金流。"><title>招商银行2026H1｜净息差压缩下的利润与资产质量 · Financials in Visuals</title><style>{CSS}</style></head><body>
<div class="mast"><nav class="wrap nav" aria-label="研究章节导航"><a class="brand" href="../../index.html">FINANCIALS IN VISUALS</a><div class="nav-links"><a href="#economics">利率经济</a><a href="#profit">利润与分部</a><a href="#credit">信贷与拨备</a><a href="#capital">资本与现金</a><a href="#red-team">反证和来源</a></div></nav></div>
<header class="hero wrap"><div class="eyebrow">Financial research / Bank sector / 600036 · 2026 H1 / Filing-first preview</div><h1>净息差仍在收窄，<br>净利息收入<br>为何仍能增长？</h1><p class="deck">招行2026年上半年净利息收入增长5.60%，但净息差下降5个基点；零售分部税前利润下降17.58%，不良贷款余额和逾期占比上升，拨备覆盖率略降。答案需要把规模、资产重定价、存款成本、分部盈利与风险缓冲放在同一篇研究里。</p><p class="hero-meta">发行人：招商银行股份有限公司 · A股600036 · 2026年1月1日至6月30日 · 未经审计的半年度披露 · 本页面为研究预览，不含估值或评级。</p><div class="keyline"><div><small>集团营业收入</small><strong>1,781.81</strong><span>亿元 · +4.83%</span></div><div><small>集团归母净利润</small><strong>764.45</strong><span>亿元 · +2.02%</span></div><div><small>净息差 NIM</small><strong>1.83%</strong><span>同比 −5bp</span></div><div><small>核心一级资本率</small><strong>14.07%</strong><span>较上年末 −9bp</span></div></div></header>
<main class="wrap">
<section class="chapter" id="economics"><div class="chapter-kicker">01 / Bank economics, not industrial gross margin</div><h2>负债成本下降，抵消了部分资产端的重定价压力。</h2><p class="lead">银行经营是资金成本与资产收益之间的利差生意。招行 2026H1 生息资产年化收益率从3.14%降至2.82%，计息负债成本从1.35%降至1.05%；负债成本改善并没有完全抵消净息差下行，但规模增加支撑了净利息收入。这里的分析必须遵循平均余额与年化收益/成本口径，而不是把期末贷款数拿来直接推算利息收入。</p>{f1}<div class="insight"><strong>会计与经济解释：</strong>净利息收入是利息收入扣除利息支出后的净额。管理层将规模与利率作用分开披露，但企业融资需求、存款结构、债券投资配置和LPR重定价可能共同驱动，两种因素并非相互独立。</div>{f2}</section>
<section class="chapter" id="profit"><div class="chapter-kicker">02 / P&L quality and segment economics</div><h2>营业收入增长，但零售与批发的利润驱动力开始分化。</h2><p class="lead">集团营业收入同比增4.83%，税前利润仅增2.06%。利润表中的信用减值损失同比扩大，是评估利润质量不可回避的一环。更有意义的是：零售贡献了集团54.34%的营业收入，但分部税前利润下滑；批发的改善与零售承压发生在同一期间，不能把这看作“零售银行整体优势消失”，也不能只报全行稳定利润。</p>{f3}{f4}</section>
<section class="chapter" id="credit"><div class="chapter-kicker">03 / Lending, deposit economics and credit losses</div><h2>稳定的不良率，掩盖不了绝对不良余额和拨备覆盖的方向。</h2><p class="lead">集团贷款规模增2.69%，不良贷款余额增长3.00%，不良率仍为0.94%。逾期贷款率从上年末的1.25%上升至1.31%；覆盖率由391.79%降至385.10%。这并不自动意味着资产质量恶化已经显著加速，但足以要求研究继续检查零售与房地产等类别的迁徙率、不良生成和核销。</p>{f5}{f6}<div class="insight"><strong>为何要看拨备桥：</strong>拨备覆盖率只是存量损失准备与不良余额的比值。期末准备的变动来源于本期计提、收回核销、处置和汇率等；用完整的存量桥，才能避免用不良余额变动直接“猜”信用费用。</div>{f7}</section>
<section class="chapter" id="capital"><div class="chapter-kicker">04 / Resilience, regulatory capital & cash flow</div><h2>资本充足不等于资产风险可以忽略，经营现金流也不是工业式自由现金流。</h2><p class="lead">高级法下集团 CET1 比率仍明显高于披露的监管要求，但核心一级资本金额增长4.47%，慢于风险加权资产增长5.16%，令资本率边际下行。银行合并经营现金流规模大幅增长，主要受到同业往来收付驱动，因此不能把CFO大于净利润当成银行“盈利含金量”的简单结论。</p>{f8}{f9}</section>
<section class="chapter" id="red-team"><div class="chapter-kicker">05 / Independent assessment and falsifiability</div><h2>三个可能推翻当前解读的下一期证据。</h2><div class="takeaway-list"><article><b>01 · 利差与规模</b><p>如果生息资产收益率继续下降，存款重定价贡献耗尽，净利息收入可能失去规模与负债成本支撑。观察季度 NIM 与平均生息资产规模。</p></article><article><b>02 · 零售贷款风险</b><p>如果零售分部利润下降主要源自结构性信贷风险而非时点费用，零售不良生成、逾期、迁徙率与核销需要同期验证。</p></article><article><b>03 · 资本消耗</b><p>如果风险加权资产持续快于核心资本积累，资本约束和股东回报的权衡会更显著。关注监管资本、RWA和股息政策。</p></article></div><div class="redteam"><h3>反方解释：本期改善可能更稳健，也可能并不稳健</h3><p>正面解读是存款负债竞争力提高、利率下降环境下的净利息收入仍增长，批发经营改善，资本缓冲充足。谨慎解读是 NIM 继续下降、零售税前利润承压、逾期占比上行且拨备覆盖略降。单份半年报不能支持下一年度盈利预测，缺乏多个季度和同业净息差、风险调整回报的比较也不能证明估值低估。</p></div><p class="conclusion">本报告的优先问题不是“净利润是否同比增长2.02%”，而是：存款成本优势还能持续多久？零售业务减值与运营成本能否改善？资本增速能否覆盖风险加权资产扩张？这些问题决定银行经营质量，且可以在下一期披露中被证伪。</p></section>
<section class="footnotes"><h2>来源与可验证的研究边界</h2><p>唯一法定定期报告来源：<a href="{URL}" target="_blank" rel="noopener">招商银行股份有限公司2026年半年度报告（A股）</a>，247 PDF物理页，SHA-256：<code>{SHA}</code>。本研究的全部图形金额以合并集团口径和发行人原始图表为基础，原始披露单位人民币百万元，图中换算亿元；表格中的百分比保留原披露精度。已校验净利息收入与收入、税前/税后利润、分部加总、存款加总、拨备滚动、资本率四舍五入等精确会计关系。</p><p><strong>未完成：</strong>这是一份基于真实原始报告的银行行业研究预览，尚未实现所有资产负债表与现金流量表及全部重要附注的独立复核，也没有经第二位财务专家审阅，未使用后续季度、同业估值和资本市场数据，不能作为完整的投资建议或目标价依据。原始会计行与管理层披露的比率/归因须分别解释，不得将解释性假设冒充披露事实。</p></section>
</main><footer class="footer"><div class="wrap">FINANCIALS IN VISUALS · 2026H1 / 招商银行 · Research preview · Not investment advice</div></footer>
<script>(function(){{for(const b of document.querySelectorAll('.svg-export')){{b.addEventListener('click',()=>{{const svg=b.closest('figure')?.querySelector('svg');if(!svg)return;const xml=new XMLSerializer().serializeToString(svg);const blob=new Blob([xml],{{type:'image/svg+xml;charset=utf-8'}});const u=URL.createObjectURL(blob);const a=document.createElement('a');a.href=u;a.download='cmb-2026h1-'+b.closest('figure').id+'.svg';a.click();setTimeout(()=>URL.revokeObjectURL(u),250)}})}}}})();</script></body></html>'''
(OUT/'600036.html').write_text(DOC,encoding='utf-8')
qa={'pdf_sha256':SHA,'pdf_pages':247,'company':'招商银行','period':'2026H1','source':'official issuer original filing','figures':len(figures),'figure_families':['magnitude','rate-volume signed waterfall','P&L signed waterfall','segment profit delta','deposit stock composition','ratios direct labels','allowance stock bridge','capital ratio comparison','CFO context bars'],'arithmetic_checks':10,'original_source_pages':[8,9,10,13,15,16,23,29,30,31,34],'publication_class':'RESEARCH_PREVIEW','full_semantic_all_notes':'NOT_CHECKED','second_financial_reviewer':'NOT_CHECKED'}
(OUT/'qa_bank_research.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print('DONE',len(DOC),'chars, figures',len(figures),'source_sha',SHA)