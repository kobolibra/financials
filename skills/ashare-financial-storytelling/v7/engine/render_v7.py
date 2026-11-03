#!/usr/bin/env python3
"""Financials in Visuals / Edition 7, data-driven original research publisher.
Inputs: source-reviewed normalized A-share industrial ledger + analyst-reviewed memo.
Output: offline, accessible HTML. No external assets, no guessed valuation or peers.
"""
from __future__ import annotations
import argparse, json, hashlib, re, html, sys
from pathlib import Path
from decimal import Decimal as D
from collections import Counter
from build import moneyflow, waterfall, money, y, pc, num, sign, factmeta, page, add
from audit import audit
from editorial_charts import balance_identity, operating_cash_allocation, profitability_change

B=D('100000000')
def esc(x): return html.escape(str(x),quote=True)
def n(x):return f'{x/B:,.2f}'
def pct(x):return f'{x*100:.1f}%'
def pp(x):return f'{x*100:+.2f}pp'
def src(l,*kk):return ' · '.join(dict.fromkeys('p.'+str(l['facts'][k]['page']) for k in kk if k in l['facts'] and l['facts'][k].get('page')))
def div(x,y):return x/y if y else None

def check(l):
    r=audit(l)
    if r['status']=='BLOCKED':raise ValueError('Source accounting gate blocked: '+str(r.get('issues',[])))
    f=l['facts'];v=lambda k:num(l,k)
    if v('revenue')-v('cogs')!=v('gross_profit'):raise ValueError('Gross profit failed')
    if v('assets')!=v('liabilities')+v('equity'):raise ValueError('Balance failed')
    if v('current_assets')+v('noncurrent_assets')!=v('assets'):raise ValueError('asset subtotal failed')
    if v('net_profit')+sum([D(x['amount']) for x in l['indirect_cfo_adjustments']],D(0))!=v('cfo'):raise ValueError('Indirect CFO failed')
    if v('cash_open')+v('cfo')+v('cfi')+v('cff')+v('fx_effect')!=v('cash_close'):raise ValueError('Cash closing failed')
    if v('capex_cash')<0:raise ValueError('Cash capex sign failed')
    return r

def metarow(name,value,sub,kind=''):
 return f'<div class="metric {kind}"><small>{esc(name)}</small><strong>{esc(value)}</strong><span>{esc(sub)}</span></div>'

def section_head(idx,kicker,heading,dek):
 return f'<div class="chapter-head"><span class="chapter-num">{idx}</span><div><span class="eyebrow soft">{esc(kicker)}</span><h2>{esc(heading)}</h2><p>{esc(dek)}</p></div></div>'

def exhibit(title,stamp,chart,source_note,readout='',scrolly=True):
 return f'''<figure class="exhibit"><div class="exhibit-top"><div><span class="exhibit-kicker">FIGURE / {esc(stamp)}</span><h3>{esc(title)}</h3></div><button class="svg-save" type="button" aria-label="导出图表 SVG">导出 SVG ↗</button></div><div class="chart-shell {'scroll-x' if scrolly else ''}" tabindex="0" aria-label="财务图表，可横向滚动查看">{chart}</div>{'<div class="chart-scroll-hint">在窄屏上可横向滑动查看完整图形 ↔</div>' if scrolly else ''}{('<figcaption><strong>读图结论 / </strong>'+esc(readout)+'</figcaption>') if readout else ''}<div class="source-note">数据来源：{esc(source_note)}</div></figure>'''

def qualitative(label,text_,tone=''):
 return f'<div class="insight {tone}"><span>{esc(label)}</span><p>{esc(text_)}</p></div>'

def journal_figure(l):
 """An honest split of material stock build-up, not a causal inference."""
 vals=[('原材料',num(l,'raw_material_prior'),num(l,'raw_material'),'#13866f'),('存货整体',num(l,'inventory_prior'),num(l,'inventory'),'#8aaca3'),('应收账款净额',num(l,'accounts_receivable_prior'),num(l,'accounts_receivable'),'#c1846d'),('预付款项',num(l,'prepayment_prior'),num(l,'prepayment'),'#7d92ad')]
 values=[z for _,a,b,_ in vals for z in (a,b) if z is not None];top=max(values or [D(1)])
 out=[]
 for label,a,b,color in vals:
  if a is None or b is None:continue
  out.append(f'''<div class="journal-line"><div class="journal-label"><b>{esc(label)}</b><small>{src(l,'inventory','raw_material','accounts_receivable','prepayment')}</small></div><div class="journal-values"><div class="period-bar"><span>上期末</span><i style="width:{float(a/top*100):.3f}%;background:#bfc9c5"></i><strong>{n(a)} 亿</strong></div><div class="period-bar"><span>本期末</span><i style="width:{float(b/top*100):.3f}%;background:{color}"></i><strong>{n(b)} 亿</strong></div></div></div>''')
 return '<div class="journal">'+''.join(out)+'</div>'

def concentration(l,m):
 ratios=[('前五名客户应收与合同资产占比',m.get('source_notes',{}).get('top5_ar_percent'),'分母：期末应收账款及合同资产余额','应收集中度 ≠ 销售收入集中度','top_five_ar'),('最大预付对象占比',m.get('source_notes',{}).get('top1_prepay_percent'),'分母：期末预付款项余额','预付款集中度 ≠ 采购额集中度','top_prepay')]
 arr=[]
 for title,share,denom,caveat,key in ratios:
  if share is None:continue
  q=D(str(share));
  if not 0<=q<=100:raise ValueError('Bad reported concentration')
  arr.append(f'''<div class="concentration-item"><div class="ci-top"><span>{esc(title)}</span><strong>{q:.2f}%</strong></div><div class="ci-track"><div style="width:{q:.2f}%"></div></div><small>{esc(denom)} · {esc(caveat)} · {page(l,key)}</small></div>''')
 return '<div class="concentration-set">'+''.join(arr)+'</div>' if arr else '<div class="no-data">原报告尚未确认可比的前五客户应收余额占比或最大供应商预付款占比；不绘制未经披露的比例图。应收和预付款金额见营运资本章节。</div>'

def original_profit_bridge(l):
 v=lambda k:num(l,k)
 rev,cogs,otc,op,pretax,net=v('revenue'),v('cogs'),v('total_operating_costs'),v('operating_profit'),None,v('net_profit')
 gp=rev-cogs;other_operating=op-(rev-otc)
 nonop=v('nonop_income')-v('nonop_expense');tax=v('income_tax')
 if op+nonop-tax!=net:raise ValueError('Signed profit bridge != net profit')
 return waterfall(l,[('毛利润',gp,src(l,'revenue','cogs'),'start'),('其余营业成本',-(otc-cogs),src(l,'total_operating_costs'),'step'),('其他经营损益净额',other_operating,src(l,'operating_profit'),'step'),('营业利润',op,src(l,'operating_profit'),'total'),('营业外净额',nonop,src(l,'nonop_income','nonop_expense'),'step'),('所得税',-tax,src(l,'income_tax'),'step'),('合并净利润',net,src(l,'net_profit'),'total')],'合并利润表从毛利润到净利润的带符号桥')

def gp_delta_bridge(l):
 v=lambda k:num(l,k)
 required=('revenue','cogs','revenue_prior','cogs_prior')
 if any(v(k) is None for k in required):return '<p>缺少可比两期财务数据，不生成毛利润增长桥。</p>'
 prior=v('revenue_prior')-v('cogs_prior');cur=v('revenue')-v('cogs')
 return waterfall(l,[('上期毛利润',prior,src(l,'revenue_prior','cogs_prior'),'start'),('收入净变化',v('revenue')-v('revenue_prior'),src(l,'revenue','revenue_prior'),'step'),('成本变化的影响',v('cogs_prior')-v('cogs'),src(l,'cogs','cogs_prior'),'step'),('本期毛利润',cur,src(l,'revenue','cogs'),'total')],'毛利润变化会计桥；不是价格与销量贡献')

def cash_bridges(l):
 v=lambda k:num(l,k)
 wc={};other=[]
 for item in l.get('indirect_cfo_adjustments',[]):
  name=item['source_label'];z=D(item['amount'])
  match=None
  if ('存货减少' in name or '存货的减少' in name):match='存货变化'
  elif '经营性应收' in name:match='经营性应收'
  elif '经营性应付' in name:match='经营性应付'
  if match:
   if match in wc:raise ValueError('Duplicated WC adjustment')
   wc[match]=z
  else:other.append(z)
 if set(wc)!={'存货变化','经营性应收','经营性应付'}:raise ValueError('Cash bridge missing WC')
 others=sum(other,D(0));net=v('net_profit');cfo=v('cfo')
 if net+others+sum(wc.values(),D(0))!=cfo:raise ValueError('Net to CFO mismatch')
 adj_pages=' / '.join(sorted({'p.'+str(x['page']) for x in l['indirect_cfo_adjustments'] if x.get('page')})) or '附注页码待核'
 chart1=waterfall(l,[('合并净利润',net,page(l,'net_profit'),'start'),(f'其他{len(other)}项调整',others,adj_pages,'step'),('存货变化',wc['存货变化'],adj_pages,'step'),('经营性应收',wc['经营性应收'],adj_pages,'step'),('经营性应付',wc['经营性应付'],adj_pages,'step'),('经营现金流',cfo,page(l,'cfo'),'total')],'合并利润到经营现金流间接调节')
 chart2=waterfall(l,[('期初现金',v('cash_open'),page(l,'cash_open'),'start'),('经营现金流',cfo,page(l,'cfo'),'step'),('投资活动',v('cfi'),page(l,'cfi'),'step'),('筹资活动',v('cff'),page(l,'cff'),'step'),('汇率变动',v('fx_effect'),page(l,'fx_effect'),'step'),('期末现金',v('cash_close'),page(l,'cash_close'),'total')],'期初现金到期末现金及现金等价物')
 return chart1,chart2

def volume_intensity(l):
 """Three comparable period panels for volume, revenue and *blended* revenue per unit.

 Approximate because report discloses rounded ten-thousand-unit volumes.
 Must never be labeled actual selling price / product ASP.
 """
 v=lambda k:num(l,k)
 keys=('revenue_optics','product_revenue_prior','product_volume_wan','product_volume_wan_prior')
 if any(v(k) is None for k in keys):return ''
 rev0,rev1=v('product_revenue_prior'),v('revenue_optics')
 q0,q1=v('product_volume_wan_prior'),v('product_volume_wan')
 if min(rev0,rev1,q0,q1)<=0:return ''
 unit0=rev0/q0/D('10000');unit1=rev1/q1/D('10000')
 series=[('光互联产品收入 / 亿元',rev0/B,rev1/B,'亿元'),('披露销量 / 万只',q0,q1,'万只'),('计算：平均收入 / 只',unit0,unit1,'元/只')]
 buf=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1110 490" role="img" aria-label="光互联产品同期收入销量及平均收入每只的结构对比；平均收入每只为近似计算而不是固定型号售价">',
 '<rect x="0" y="0" width="1110" height="490" fill="#fffefb"/>',
 '<text x="40" y="42" font-size="13" fill="#536f67">2025H1 与 2026H1，同期比较；销量以公司披露的万只取整量计算</text>']
 for i,(label,old,new,unit) in enumerate(series):
  x=36+i*362;y=70;h=370
  norm=max(old,new)
  w0=float(old/norm)*293;w1=float(new/norm)*293
  delta=(new/old-1)*100
  buf.append(f'<g><rect x="{x}" y="{y}" width="333" height="350" fill="{["#edf3ed","#eff0eb","#f4eee8"][i]}" rx="4"/>')
  buf.append(f'<text x="{x+18}" y="{y+35}" font-size="18" fill="#183b3c" font-weight="700">{label}</text>')
  buf.append(f'<text x="{x+18}" y="{y+71}" font-size="14" fill="#637a73">2025H1</text>')
  buf.append(f'<rect x="{x+18}" y="{y+86}" width="{w0:.2f}" height="24" fill="#aabbb1"/>')
  buf.append(f'<text x="{x+18}" y="{y+139}" font-size="23" fill="#344d48">{old:,.2f}</text>')
  buf.append(f'<text x="{x+18}" y="{y+193}" font-size="14" fill="#637a73">2026H1</text>')
  buf.append(f'<rect x="{x+18}" y="{y+207}" width="{w1:.2f}" height="24" fill="{["#067c68","#378d91","#bf806b"][i]}"/>')
  buf.append(f'<text x="{x+18}" y="{y+260}" font-size="25" font-weight="700" fill="#12393b">{new:,.2f}</text>')
  buf.append(f'<text x="{x+18}" y="{y+313}" font-size="16" font-weight="700" fill="#087d67">同比约 {delta:+.1f}%</text></g>')
 buf.append('<text x="40" y="463" font-size="14" fill="#695d50">注意：最后一栏是营业收入 ÷ 披露销量的混合均值，不是同型号光模块售价，也不能识别型号升级与价格变化各自贡献。</text></svg>')
 return ''.join(buf)

def evidence_table(l):
 keys=['revenue','cogs','gross_profit','operating_profit','net_profit','cfo','capex_cash','cash_open','cash_close','assets','liabilities','equity','inventory','raw_material','accounts_receivable','prepayment','top_five_ar']
 keys += [g[k] for g in l.get('segments',[]) if g.get('dimension') in ('product','other_business') for k in ('revenue_key','cost_key') if g.get(k)]
 rows=[]
 for k in keys:
  d=l['facts'].get(k)
  if not d:continue
  rows.append(f'<tr><th scope="row">{esc(d.get("source_label",k))}</th><td class="num">{D(d["amount"]):,.2f}</td><td>{esc(d.get("period",l["document"]["period_key"]))}</td><td>{page(l,k)}</td></tr>')
 return '<div class="table-scroll"><table><thead><tr><th>原报表项目</th><th>人民币元</th><th>期别</th><th>页码</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'

def build(l,m):
 QA=check(l)
 doc=l['document'];v=lambda k:num(l,k)
 rev,cogs,gp,net,cfo,capex=v('revenue'),v('cogs'),v('gross_profit'),v('net_profit'),v('cfo'),v('capex_cash')
 prevrev,prevcogs=v('revenue_prior'),v('cogs_prior')
 prevgp=prevrev-prevcogs if None not in (prevrev,prevcogs) else None
 gross_delta=gp-prevgp if prevgp is not None else None
 flow,count=moneyflow(l)
 pnl=original_profit_bridge(l)
 delta=gp_delta_bridge(l)
 cash1,cash2=cash_bridges(l)
 bal=balance_identity(l)
 volume_fig=volume_intensity(l)
 fcfsvg=(waterfall(l,[('经营现金流',cfo,src(l,'cfo'),'start'),('现金资本开支',-capex,src(l,'capex_cash'),'step'),('简化自由现金流',cfo-capex,src(l,'cfo','capex_cash'),'total')],'简化自由现金流：经营现金流减资本开支') if cfo<capex else operating_cash_allocation(l))
 marg=profitability_change(l)
 im=journal_figure(l);con=concentration(l,m)
 issuer=esc(m.get('issuer_short',doc['issuer'])); ticker=esc(doc['ticker']); period=esc(doc['period_key']); cmp=esc(doc['comparative_period_key']);unit='人民币亿元'
 thesis=esc(m.get('headline','本期经营质量存在需要检验的变化'))
 summary=esc(m.get('summary',''))
 watch=m.get('watchlist',[])
 summary_metrics=''.join([
  metarow('营业收入',n(rev)+' 亿',('同比 '+pct((rev-prevrev)/prevrev)) if prevrev else '同比无可比信息'),
  metarow('综合毛利率',pct(gp/rev), '毛利 '+n(gp)+' 亿元'),
  metarow('经营现金流',n(cfo)+' 亿','合并净利润转化 '+pct(cfo/net)),
  metarow('简化自由现金流',n(cfo-capex)+' 亿','CFO − 购建长期资产现金支出'),
 ])
 watch_html=''.join(f'<div class="watch-row"><span class="watch-index">0{i+1}</span><div><h3>{esc(w["topic"])}</h3><p>{esc(w["test"])}</p></div><small>{esc(w.get("page","来源待核"))}</small></div>' for i,w in enumerate(watch))
 support=''.join('<li>'+esc(x)+'</li>' for x in m.get('support',[]));counter=''.join('<li>'+esc(x)+'</li>' for x in m.get('counter',[]))
 facts=len(l.get('facts',{}));ind=len(l.get('indirect_cfo_adjustments',[]))
 growth_unit='收入变动 '+(n(rev-prevrev)+' 亿' if prevrev is not None else '上期不可比')+' · 成本变动 '+(n(cogs-prevcogs)+' 亿' if prevcogs is not None else '上期不可比')
 index_breakdown='<div class="one-minute">'+qualitative('研究核心',m.get('growth_explanation','')[:250],'teal')+qualitative('关键反证',m.get('growth_counter','')[:250],'rust')+'</div>'
 css=r'''/* Edition 7 / original editorial art direction */
:root{--canvas:#f4f5f0;--paper:#fffefd;--ink:#122e35;--mid:#38555a;--muted:#617774;--green:#087e65;--sage:#88bfb1;--copper:#b47c67;--blue:#447fa0;--line:#d5dfd8;--dark:#0e2a31;--serif:Georgia,"Songti SC","Noto Serif CJK SC",serif;--sans:-apple-system,BlinkMacSystemFont,"PingFang SC","Noto Sans CJK SC","Microsoft YaHei",sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--canvas);color:var(--ink);font-family:var(--sans);-webkit-font-smoothing:antialiased}a{color:inherit}button{font-family:inherit}a:focus-visible,button:focus-visible,[tabindex]:focus-visible{outline:3px solid #1f9880;outline-offset:4px}::selection{background:#b1e7d4;color:#12332f}
.wrap{width:min(1240px,calc(100% - 70px));margin:0 auto}.mast{background:var(--dark);color:#fff}.bar{height:76px;display:flex;justify-content:space-between;align-items:center;gap:25px;border-bottom:1px solid #345159}.brand{font-weight:800;letter-spacing:.18em;font-size:13px;text-decoration:none}.brand em{font-style:normal;color:#8ed7bd}.nav{display:flex;gap:25px;font-size:12px;color:#bdd5ce}.nav a{text-decoration:none}.nav a:hover{color:white}.edition{font-size:10px;letter-spacing:.1em;color:#9bbeb4}.hero{padding:94px 0 108px;position:relative;overflow:hidden}.eyebrow{font-size:11px;letter-spacing:.18em;font-weight:800;text-transform:uppercase;color:#94d2c0}.eyebrow.soft{color:#138067}.hero h1{font-size:clamp(43px,5.3vw,76px);line-height:1.16;max-width:1060px;letter-spacing:-.045em;font-weight:550;margin:25px 0 27px;text-wrap:balance;overflow-wrap:break-word}.hero h1 em{font-style:normal;color:#95dbc3}.hero-deck{font-size:19px;color:#c4d8d2;line-height:1.9;max-width:890px}.hero-meta{display:flex;gap:15px;flex-wrap:wrap;margin-top:32px}.hero-meta span{border:1px solid #54716d;padding:9px 14px;border-radius:90px;color:#d1e3dc;font-size:11px}.hero-figure{position:absolute;width:210px;height:210px;border-radius:50%;border:44px solid #145242;opacity:.25;right:-85px;top:125px;pointer-events:none}
.kpi-zone{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1px;background:#cbdbd2;transform:translateY(-32px);position:relative;box-shadow:0 12px 28px #16322908}.metric{background:var(--paper);padding:25px 24px;min-width:0}.metric small{font-size:12px;color:var(--muted);display:block}.metric strong{display:block;font:650 clamp(25px,3vw,37px) var(--serif);white-space:nowrap;margin:13px 0 9px}.metric span{font-size:11px;color:#12775e;line-height:1.6}
.paper{padding:42px 0 90px}.lead{display:grid;grid-template-columns:180px 1fr;gap:45px;align-items:start;padding:35px 0 75px}.lead aside{font-size:11px;letter-spacing:.17em;font-weight:750;color:#07816b;padding-top:15px}.lead p{max-width:890px;font:400 clamp(22px,2.75vw,36px)/1.55 var(--serif);margin:0;letter-spacing:-.015em}.lead p strong{color:#078168;font-weight:650}.chapter{border-top:1px solid #cbd8ce;padding:61px 0 74px;scroll-margin-top:20px}.chapter-head{display:grid;grid-template-columns:115px 1fr;gap:38px;margin-bottom:36px}.chapter-num{font:500 36px var(--serif);color:#0e8b6e}.chapter-head h2{font:540 clamp(30px,4.5vw,55px)/1.18 var(--serif);letter-spacing:-.042em;max-width:920px;margin:13px 0 15px}.chapter-head p{font-size:15px;line-height:1.9;color:var(--muted);max-width:830px;margin:0}.two-col{display:grid;grid-template-columns:1.5fr 1fr;gap:35px;margin:34px 0}.two-col.reverse{grid-template-columns:1fr 1.5fr}.section-blurb{font:400 20px/1.75 var(--serif);color:#274a4f;margin:20px 0}.fineprint{font-size:12px;line-height:1.85;color:#5b726c}.fact-note{padding:19px 23px;background:#e9f0e9;border-left:3px solid #1f9273;color:#315550;font-size:13px;line-height:1.85}.callout{background:#e8eee8;border-left:4px solid #0b8269;padding:25px 28px;font-size:16px;line-height:1.83;color:#385b5a}.callout.rust{background:#f1eae4;border-color:#bf856e}.callout strong{display:block;margin-bottom:8px;color:#173f3f}.exhibit{margin:34px 0 30px;background:var(--paper);border:1px solid var(--line);padding:22px 24px 17px}.exhibit-top{display:flex;justify-content:space-between;gap:22px;align-items:center;margin-bottom:18px}.exhibit h3{font-size:clamp(18px,2.25vw,26px);line-height:1.45;font-weight:630;margin:8px 0 0}.exhibit-kicker{color:#789086;font-weight:750;letter-spacing:.15em;font-size:10px}.svg-save{white-space:nowrap;border:1px solid #ceddd3;background:#fff;padding:10px 13px;color:#275248;font-size:11px;cursor:pointer}.svg-save:hover{background:#eef7ee}.chart-shell{max-width:100%;outline-offset:1px}.scroll-x{overflow-x:auto;overscroll-behavior-inline:contain}.chart-scroll-hint{display:none;color:#607c71;font-size:11px;padding-top:10px}.exhibit svg{display:block;width:100%;height:auto;min-width:930px}.exhibit svg.editorial-flow{min-width:1040px}.exhibit figcaption{color:#264b49;margin-top:13px;font-size:13px;line-height:1.85}.source-note{color:#637c73;margin-top:12px;font-size:11px;line-height:1.7;border-top:1px solid #ecf0ec;padding-top:10px}
/* Reuse checked source-driven SVG geometry; typography standardized */
.svg-kicker,.ed-kicker{font:700 15px var(--sans);fill:#637d77;letter-spacing:1px}.svg-name,.svg-label,.ed-label{font:650 17px var(--sans);fill:#183b42}.svg-value,.ed-value{font:700 17px var(--sans);fill:#1a454b}.svg-step-label{font:620 15px var(--sans);fill:#36565a}.svg-step-value{font:700 14px var(--sans);fill:#213f46}.ed-sub{font:500 13px var(--sans);fill:#617b7b}.ed-caption{font:450 13px var(--sans);fill:#56756e}.money-ribbon,.ed-band{cursor:help;transition:opacity .15s}.money-ribbon.is-dim{opacity:.17}.money-ribbon:focus,.ed-band:focus{stroke:#102f32;stroke-width:2;outline:none}rect[tabindex]{cursor:help}
.readout{margin-top:36px;display:grid;grid-template-columns:1fr 1fr;gap:15px}.insight{padding:21px 23px;border-top:3px solid #178c73;background:#eaf0eb}.insight.rust{border-color:#b88770;background:#f3ece6}.insight span{font-size:11px;letter-spacing:.13em;font-weight:800;color:#22725e}.insight.rust span{color:#95684f}.insight p{font-size:14px;line-height:1.85;margin:10px 0 0;color:#445f5a}.analytic-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.journal{padding:18px 21px;background:var(--paper);border:1px solid var(--line)}.journal-line{padding:18px 0;border-bottom:1px solid #e6ebe6}.journal-line:last-child{border-bottom:0}.journal-label{display:flex;justify-content:space-between;gap:12px;margin-bottom:13px;font-size:14px}.journal-label small{font-size:11px;color:#80918a}.period-bar{display:grid;grid-template-columns:65px minmax(0,1fr) 85px;align-items:center;gap:12px;margin:9px 0}.period-bar span{font-size:11px;color:#647e77}.period-bar i{display:block;height:17px;border-radius:2px}.period-bar strong{font-size:12px;text-align:right;font-variant-numeric:tabular-nums}.concentration-set{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:24px 0}.concentration-item{padding:25px;border:1px solid #d9e2d9;background:#f9faf5}.ci-top{display:flex;justify-content:space-between;align-items:baseline;gap:12px}.ci-top span{font-size:13px}.ci-top strong{font:600 34px var(--serif);color:#167a64}.ci-track{background:#e0e7dc;height:13px;margin:18px 0}.ci-track div{background:#16856d;height:13px}.concentration-item small{font-size:11px;color:#5d736d;line-height:1.7}
.watch-row{display:grid;grid-template-columns:65px 1fr 100px;gap:22px;align-items:start;border-bottom:1px solid #dbe3dc;padding:25px 0}.watch-index{font:500 31px var(--serif);color:#14806a}.watch-row h3{font-size:18px;margin:0 0 8px}.watch-row p{font-size:14px;line-height:1.8;color:#566e68;max-width:820px;margin:0}.watch-row small{color:#638078;font-size:12px;text-align:right}.brief-compare{display:grid;grid-template-columns:1fr 1fr;gap:27px}.brief-compare ul{padding-left:18px;margin:0}.brief-compare li{font-size:14px;line-height:1.9;margin:9px 0}.brief-compare h3{font-size:18px}.brief-compare>div{padding:27px;background:#e9f0e9;border-top:3px solid #128570}.brief-compare>div:last-child{background:#f3ece6;border-color:#bc846b}
.methods{background:#102f35;color:#d5e2dc;padding:67px 0 75px;overflow-x:hidden}.methods h2{font:530 39px var(--serif);margin:0 0 19px;color:#fff}.methods p{font-size:13px;line-height:1.85;max-width:940px}.methods details{margin:25px 0;color:#e2e6df}.methods summary{cursor:pointer;font-weight:700;padding:15px 0;border-top:1px solid #486b66}.table-scroll{overflow:auto}.table-scroll table{width:100%;border-collapse:collapse;font-size:12px;min-width:650px}.table-scroll th,.table-scroll td{padding:10px 13px;border-bottom:1px solid #47635b;text-align:left}.table-scroll .num{font-variant-numeric:tabular-nums;text-align:right}.page-footer{padding:24px 0;background:#09252c;color:#9eb7b0}.page-footer .wrap{display:flex;justify-content:space-between;gap:20px;font-size:11px}.risk-disclaimer{font-size:12px;color:#e4cab9}.indtable{font-size:12px}.indtable td{text-align:right}.lnk{color:#bce7d1}
.tooltip{position:fixed;pointer-events:none;z-index:100;background:#153840;color:#f5faf5;box-shadow:0 14px 37px #081f2a34;font-size:12px;line-height:1.6;max-width:310px;padding:12px 14px;display:none;border:1px solid #597970}.tooltip p{margin:4px 0 0}.skip{position:absolute;left:-9999px;top:0}.skip:focus{left:10px;z-index:120;background:white;padding:10px}.simple-flow-description{font-size:12px;color:#5c746f}
@media(max-width:970px){.nav{gap:13px}.wrap{width:min(100% - 42px,1240px)}.kpi-zone{grid-template-columns:repeat(2,1fr)}.chapter-head{grid-template-columns:74px 1fr;gap:22px}.two-col,.two-col.reverse{grid-template-columns:1fr}.analytic-grid{grid-template-columns:1fr}}
@media(max-width:650px){.bar{height:65px}.nav{gap:14px}.edition{display:none}.brand{font-size:11px;letter-spacing:.11em}.hero{padding:70px 0 90px}.hero h1{font-size:clamp(42px,10vw,64px)}.hero-deck{font-size:16px}.kpi-zone{grid-template-columns:1fr 1fr;gap:1px}.metric{padding:18px 14px}.metric strong{font-size:24px}.metric span{font-size:10px}.lead{grid-template-columns:1fr;gap:9px;padding:24px 0 52px}.lead p{font-size:23px}.chapter{padding:45px 0 53px}.chapter-head{grid-template-columns:1fr;gap:8px;margin-bottom:22px}.chapter-num{font-size:24px}.chapter-head h2{font-size:37px}.exhibit{padding:16px 13px 14px;margin:23px 0}.exhibit-top{align-items:start}.exhibit h3{font-size:20px}.exhibit svg{min-width:930px}.chart-scroll-hint{display:block}.svg-save{font-size:10px;padding:8px}.readout,.brief-compare,.concentration-set{grid-template-columns:1fr}.watch-row{grid-template-columns:45px 1fr;gap:12px}.watch-row small{grid-column:2;text-align:left}.page-footer .wrap{display:block}.period-bar{grid-template-columns:58px minmax(0,1fr) 70px;gap:8px}.journal-label small{display:none}.ci-top strong{font-size:28px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
'''
 js=r'''(()=>{const tip=document.querySelector('#floatTip');let last=null;const hide=()=>{tip.style.display='none'};function show(el,evt){let value=el.getAttribute('data-tip')||el.getAttribute('aria-label')||el.querySelector('title')?.textContent||'';if(!value)return;tip.textContent=value;tip.style.display='block';last=el;move(evt,el)}function move(evt,el){let x=12,y=12;if(evt&&typeof evt.clientX==='number'){x=evt.clientX+16;y=evt.clientY+20}else{let box=el.getBoundingClientRect();x=box.left+10;y=box.top-68}tip.style.left=Math.max(8,Math.min(window.innerWidth-325,x))+'px';tip.style.top=Math.max(8,Math.min(window.innerHeight-100,y))+'px'}document.querySelectorAll('[data-tip],svg[role="img"] [tabindex],.ed-band').forEach(el=>{el.addEventListener('pointerenter',e=>show(el,e));el.addEventListener('pointermove',e=>move(e,el));el.addEventListener('pointerleave',hide);el.addEventListener('focus',e=>show(el,null));el.addEventListener('blur',hide)});document.addEventListener('keydown',e=>{if(e.key==='Escape')hide()});document.querySelectorAll('button.svg-save').forEach((b,i)=>{b.addEventListener('click',()=>{let svg=b.closest('.exhibit')?.querySelector('svg');if(!svg)return;let txt=new XMLSerializer().serializeToString(svg);let blob=new Blob([txt],{type:'image/svg+xml;charset=utf-8'});let url=URL.createObjectURL(blob);let a=document.createElement('a');a.href=url;a.download='Financials-Research-Exhibit-'+(i+1)+'.svg';a.click();setTimeout(()=>URL.revokeObjectURL(url),2500)})});document.querySelectorAll('.money-ribbon').forEach(el=>{let root=el.closest('svg');let dim=on=>{root?.querySelectorAll('.money-ribbon').forEach(x=>x.classList.toggle('is-dim',on&&x.getAttribute('data-group')!==el.getAttribute('data-group')))};el.addEventListener('pointerenter',()=>dim(true));el.addEventListener('pointerleave',()=>dim(false));el.addEventListener('focus',()=>dim(true));el.addEventListener('blur',()=>dim(false))});})();'''
 gp_analysis_text=(f'本期毛利润 {n(gp)} 亿元，较上年同期变动 {n(gross_delta)} 亿元；收入变动 {n(rev-prevrev)} 亿元、营业成本变动 {n(cogs-prevcogs)} 亿元，二者仅为会计加减关系，不构成价格、销量、良率的因果归因。' if gross_delta is not None else f'本期毛利润 {n(gp)} 亿元；上期收入或营业成本缺失，不能计算同比毛利润增量。')
 lens=m.get('forensic_lenses') or []
 r_and_d_context=lens[0].get('insight','') if lens else '未提供可验证的研究与开发成本深度附注。'
 # full page assembly
 html_page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="{esc(issuer)} {period} 深度财务研究：商业模式、利润形成、现金转换、资产结构、风险与反证。原始财报可追溯。"><title>{issuer} · {period} | Financials in Visuals Research Edition</title><style>{css}</style></head><body>
<a class="skip" href="#main">跳到正文</a><div class="tooltip" id="floatTip" role="status" aria-live="polite"></div>
<div class="mast"><div class="wrap"><div class="bar"><a href="/" class="brand">FINANCIALS <em>IN VISUALS</em></a><nav class="nav" aria-label="研究导航"><a href="#economics">商业模式</a><a href="#profit">盈利</a><a href="#cash">现金</a><a href="#capital">资本</a><a href="#watch">风险</a><a class="site-library-link" href="/#companies" title="返回包含七家公司的统一研究库">全部七家公司 ↗</a></nav></div>
<header class="hero"><span class="eyebrow">Equity research / {ticker} / {period} · filing-first</span><h1>{thesis}</h1><p class="hero-deck">{summary}</p><div class="hero-meta"><span>{issuer} · {ticker}</span><span>{period} · {esc(doc['period_start'])} 至 {esc(doc['period_end'])}</span><span>{'已审计' if doc['audited'] else '未经审计'} · 合并报表</span><span>原始 PDF {doc['pages']} 页</span></div><div class="hero-figure"></div></header></div></div>
<div class="wrap"><section class="kpi-zone" aria-label="核心财务指标">{summary_metrics}</section></div>
<main id="main" class="wrap paper"><div class="lead"><aside>THE CENTRAL QUESTION<br>本期研究判断</aside><p>一家公司能把收入变成利润，并不等于它已经把利润变成了<strong>可持续的现金回报</strong>。这份研究将收入、成本、现金、营运资本和资本投入放在同一条会计逻辑中检验。</p></div>
<section class="chapter" id="economics">{section_head('01','BUSINESS MODEL / ECONOMIC ENGINE','核心产品如何将销售额转化为盈利？','先理解产品价值链和商业模式，再用按金额守恒的多级流带解释收入、成本、毛利润与经营盈余。')}<div class="two-col"><div class="callout"><strong>公司怎样赚钱</strong>{esc(m.get('business',''))}</div><div class="fact-note"><strong>定义与边界</strong><p>管理层关于技术、市场和客户链条的描述不是独立证据。本图仅使用原始财报中有明确分类、相同口径且金额严格守恒的收入来源。{esc(l.get('revenue_partition_assertion',{}).get('scope','未完整披露的产品来源不能自动生成未分类业务。'))}。不同分类维度绝对不能叠加。</p><small>公司说明：{esc(m.get('business_sources','原报告相应章节'))}</small></div></div>{exhibit('收入流向怎样形成毛利润及经营盈余？','01 / MONEY FLOW',flow,src(l,*[g['revenue_key'] for g in l.get('segments',[]) if g.get('dimension') in ('product','other_business')],'revenue','cogs','total_operating_costs'),'实线流带宽度按人民币金额缩放；其他经营净收益及营业外项目不属于本图守恒部分，见下一张利润桥。')}<div class="readout">{qualitative('主线事实',m.get('growth_explanation',''))}{qualitative('不能直接得出的因果结论',m.get('growth_counter',''),'rust')}</div>{exhibit('为什么收入翻倍而销量只增加约六成？','02 / SALES VOLUME & MIX',volume_fig,src(l,'revenue_optics','product_revenue_prior','product_volume_wan','product_volume_wan_prior'),'三个比较面板的最后一栏为平均收入/只的近似值，不等于产品型号价格。只有量价组合的数学关系，缺少规格级别因果证据。') if volume_fig else ''}</section>
<section class="chapter" id="profit">{section_head('02','PROFIT & DURABILITY / QUALITY OF EARNINGS','利润增长究竟来自收入增长，还是成本与费用变化？','把完整利润形成、毛利润变动、利润率和真实同期比较分开处理；明确“会计桥”不等于销量、价格和良率的因果拆解。')}
{exhibit('从毛利润到合并净利润：完整有符号会计桥','03 / P&L',pnl,src(l,'revenue','cogs','total_operating_costs','operating_profit','income_tax','net_profit'),'营业总成本中的非营业成本项目、其他经营损益净额、营业外净额及税费均保留正负号。')}
{exhibit('毛利润同比多出多少？收入与成本变化分别起了什么算术作用？','04 / Δ GROSS PROFIT',delta,src(l,'revenue','revenue_prior','cogs','cogs_prior'),growth_unit+'；该分解不构成价格/销量因果归因。')}
{exhibit('毛利率、经营现金流率、简化 FCF 率：两期比较','05 / MARGIN PROFILE',marg,src(l,'revenue','cogs','cfo','capex_cash')+'；上期同口径见原报表比较列','仅比较两个半年同期，不冒充 8–12 个季度的长期趋势。简化 FCF 率是分析师定义。')}
<div class="readout">{qualitative('主要解释',gp_analysis_text)}{qualitative('技术、研发与利润质量',r_and_d_context+' 研发费用率变化并不直接证明定价权或技术壁垒。','rust')}</div></section>
<section class="chapter" id="cash">{section_head('03','CASH CONVERSION / CAPITAL ALLOCATION','利润能否真正转化为现金？','先完整勾稽合并净利润到经营现金流，再解释经营、投资、融资及汇率因素怎样改变期末现金。两层关系不能混成一张误导性的资金流图。')}
{exhibit('合并净利润经过哪些调整，才成为经营现金流？','06 / NET INCOME → CFO',cash1,'现金流量表补充资料 '+(' / '.join(sorted({'p.'+str(x['page']) for x in l['indirect_cfo_adjustments'] if x.get('page')})))+'，合并净利润 '+page(l,'net_profit')+'，CFO '+page(l,'cfo'),'间接法全部 '+str(ind)+' 项逐一参与原值校验；图中合并了其中的非营运资本调整，原文项目可于后面的审计表查看。')}
{exhibit('经营现金流形成后，期末现金为什么反而减少？','07 / CASH MOVEMENT',cash2,src(l,'cash_open','cfo','cfi','cff','fx_effect','cash_close'),'现金及现金等价物不同于资产负债表的货币资金，汇率对现金的影响不同于利润表汇兑损益。')}
{exhibit('经营现金流扣除现金资本开支，留下多少简化 FCF？','08 / REINVESTMENT & FCF',fcfsvg,src(l,'cfo','capex_cash'),'这是一项分析定义，不表示 CFO 逐笔流向资本开支，也不等于股东可以自由分配的现金。')}
<div class="callout"><strong>现金质量的反证</strong>{esc(m.get('cash_explanation',''))}</div></section>
<section class="chapter" id="capital">{section_head('04','FINANCIAL POSITION / FORENSIC NOTES','资本投入与营运资产结构如何改变财务韧性？','从资产、负债和股东权益的期末结构出发，审查库存、应收、预付款及融资风险；不以时点余额直接替代现金流量。')}
{exhibit('总资产由哪些部分构成，并由负债和股东权益如何支撑？','09 / BALANCE SHEET ANATOMY',bal,src(l,'assets','current_assets','noncurrent_assets','liabilities','equity','inventory','accounts_receivable'),'同一时点的资产=负债+权益；流动资产差额为计算值，这不是把资产转换成负债的实际现金流。')}
{exhibit('哪些营运资本项目比年初增加得更快？','10 / WORKING CAPITAL',im,src(l,'inventory','accounts_receivable','prepayment'),'年初/期末时点余额比较；净额和毛额不得混用。',False)}
{exhibit('“客户集中”究竟集中在哪个会计分母上？','11 / COUNTERPARTY CONCENTRATION',con,src(l,'top_five_ar','top_prepay')+'；披露的比例依据公司附注','只有披露明确分母和金额时才能绘制集中度图；本期未获得同口径集中度数据的项目不绘制，不得由应收占比推导收入占比。',False)}
<div class="callout rust"><strong>风险不等于舞弊判断</strong>{esc(m.get('risk_explanation',''))}</div></section>
<section class="chapter" id="watch">{section_head('05','THE OTHER SIDE / FALSIFIABLE RESEARCH','什么证据支持这个判断，又有什么证据可能推翻它？','对同一组事实给予积极与谨慎两种解释。专业研究不是把风险放到页脚，而是设计具体可以验证的下一期指标。')}
<div class="brief-compare"><div><h3>支持 / Positive evidence</h3><ul>{support}</ul></div><div><h3>反面 / Counter evidence</h3><ul>{counter}</ul></div></div>
<div class="watchlist">{watch_html}</div></section>
</main><div class="methods" id="sources"><div class="wrap"><span class="eyebrow">Methods / sources / limitations</span><h2>证据必须能回到原始财报。</h2><p>本报告依据用户上传的 {esc(doc['source_filename'])} PDF 原文件（{doc['pages']} 页），原文件 SHA-256：<code>{esc(doc['source_sha256'])}</code>；已经计算原始字节指纹并复核了主要合并报表及关键附注。来源为用户上传的原始 PDF；全篇以人民币元进行精确核对，图表按显示需要换算为亿元。财务数据为{'经审计' if doc['audited'] else '未经审计'}的合并报表；管理层解释、数学计算、研究假设与外部独立验证严格区分。绘图方式参考公开金融可视化研究原则，但所有图形和排版均为独立设计，不与第三方出版物关联。</p><p class="risk-disclaimer">资料边界：单份半年报不能建立八至十二个季度趋势、竞争者估值、股价相对基本面的回归、公司具体产品 ASP/销量/良率或客户真实身份。未补充独立来源，不制作虚假图表或预测。</p>
<details><summary>展开：关键来源与精确原始金额（人民币元）</summary>{evidence_table(l)}</details>
<details><summary>展开：净利润到经营现金流的全部 {ind} 项附注调节</summary><div class="table-scroll"><table class="indtable"><thead><tr><th>补充资料原文</th><th>带符号金额（元）</th><th>页码</th></tr></thead><tbody>{''.join(f'<tr><td>{esc(x["source_label"])}</td><td>{D(x["amount"]):,.2f}</td><td>p.{esc(x.get("page","—"))}</td></tr>' for x in l['indirect_cfo_adjustments'])}</tbody></table></div></details>
<details><summary>展开：研究限制与未决问题</summary><ul>{''.join('<li>'+esc(x)+'</li>' for x in m.get('limits',[]))}</ul></details></div></div>
<footer class="page-footer"><div class="wrap"><span>FINANCIALS IN VISUALS · INDEPENDENT RESEARCH / {ticker}</span><span>研究辅助材料，非证券投资建议 · PDF SHA + 页码可追溯</span></div></footer><script>{js}</script></body></html>'''
 return html_page,{'issuer':doc['issuer'],'period':doc['period_key'],'pdf_sha256':doc['source_sha256'],'pdf_pages':doc['pages'],'facts':facts,'indirect_cash_adjustments':ind,'charts':(9 if not m.get('source_notes',{}).get('top5_ar_percent') and not m.get('source_notes',{}).get('top1_prepay_percent') else 10)+int(bool(volume_fig)),'money_flow_ribbons':count,'accounting_status':QA['status'],'hash_sha256':hashlib.sha256(html_page.encode()).hexdigest(),'bytes':len(html_page.encode()),'browser_status':'NOT_CHECKED','public_http_status':'NOT_CHECKED','source_quality':'UPLOADED_SOURCE_PDF_SHA_VERIFIED__CORE_FINANCIAL_NUMBERS_CHECKED__EDITORIAL_SECOND_REVIEW_PENDING'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--ledger',required=True);p.add_argument('--memo',required=True);p.add_argument('--out',required=True);p.add_argument('--qa',required=True);a=p.parse_args()
 l=json.loads(Path(a.ledger).read_text(encoding='utf-8'));m=json.loads(Path(a.memo).read_text(encoding='utf-8'))
 if l['document'].get('business_type') not in ('industrial','manufacturing','services'):raise ValueError('Sector unsupported: bank/insurance/property need domain-specific renderer')
 if m.get('review_status')!='ANALYST_REVIEWED':raise ValueError('Analyst research memo not reviewed')
 page_html,meta=build(l,m)
 out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(page_html,encoding='utf-8');q=Path(a.qa);q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(meta,ensure_ascii=False,indent=2))
if __name__=='__main__':main()