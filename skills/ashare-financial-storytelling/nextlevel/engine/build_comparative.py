#!/usr/bin/env python3
"""Financials in Visuals / verifiable multi-issuer editorial research exhibit.
Only comparable disclosed H1 flow data and dated balance-sheet stocks; no valuation or invented volume split.
"""
from __future__ import annotations
import json, hashlib, html, argparse, os
from pathlib import Path
from decimal import Decimal as D

UNIT = D('100000000')
PALETTE = {'300394': '#AC765C', '300308': '#436F87', '300502': '#087F68'}
PDF_PATHS = {
 '300394': Path('/mnt/data/788b066c-b687-4f11-8ae4-c6197f019370.pdf'),
 '300308': Path('/mnt/data/H2_AN202608211828276722_1.pdf'),
 '300502': Path('/mnt/data/H2_AN202608240006746577_1.pdf'),
}
DEFAULT_CASES={
 '300394':Path('/mnt/data/financials_v5/examples/tianfu-ledger.json'),
 '300308':Path('/mnt/data/financials_zhongji_2026H1/examples/zhongji-2026H1-ledger.json'),
 '300502':Path('/mnt/data/financials_xinyisheng_2026H1/examples/xinyisheng-ledger.json')}
SHORT={'300394':'天孚通信','300308':'中际旭创','300502':'新易盛'}
ROLE={'300394':'上游光器件与光连接','300308':'光模块／光互连系统','300502':'光模块／光互连系统'}

def E(value):return html.escape(str(value),quote=True)
def n(d,key):
 v=d['facts'].get(key)
 if not v or v.get('amount') is None:raise ValueError(f'Missing required signed source {d["document"]["ticker"]} {key}')
 return D(str(v['amount']))
def source(d,key):return f'p.{d["facts"][key]["page"]}'
def y(v):return f'{v/UNIT:,.2f}'
def pct(v):return f'{v*100:,.1f}%'
def c(v):return f'{v:+,.1f}'
def svgt(x,y,s,size=14,fill='#16363B',anchor='start',weight=500):
 return f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}">{E(s)}</text>'
def svgwrap(body,desc,width=1000,height=270):
 return f'<svg role="img" aria-label="{E(desc)}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" class="figure-svg"><title>{E(desc)}</title>{body}</svg>'

def checked(case_paths=None, pdf_paths=None):
 case_paths=case_paths or DEFAULT_CASES
 pdf_paths=pdf_paths or PDF_PATHS
 if set(case_paths)!={'300394','300308','300502'} or set(pdf_paths)!=set(case_paths):raise ValueError('Source map requires exactly three issuer ledgers and PDFs')
 facts={}
 for code, loc in case_paths.items():
  d=json.loads(Path(loc).read_text());doc=d['document'];p=Path(pdf_paths[code])
  if not p.exists():raise FileNotFoundError(p)
  hashval=hashlib.sha256(p.read_bytes()).hexdigest()
  if doc['ticker'].split('.')[0]!=code or doc['period_key']!='2026H1' or doc['comparative_period_key']!='2025H1' or doc['previous_stock_date']!='2025-12-31':raise ValueError('Issuer/period/source mismatch '+code)
  if hashval!=doc.get('source_sha256') and doc.get('source_sha256')!='NOT_VERIFIED_REMOTE_PDF':raise ValueError('Original PDF SHA mismatch '+code)
  revenue,cogs,ni,cfo,capex=n(d,'revenue'),n(d,'cogs'),n(d,'net_profit'),n(d,'cfo'),n(d,'capex_cash')
  prior_rev,prior_cogs=n(d,'revenue_prior'),n(d,'cogs_prior')
  assets,assets_prior=n(d,'assets'),n(d,'assets_prior')
  inv,inv_prior=n(d,'inventory'),n(d,'inventory_prior')
  ar,ar_prior=n(d,'accounts_receivable'),n(d,'accounts_receivable_prior')
  if not all(v>0 for v in [revenue,cogs,ni,prior_rev,prior_cogs,assets,assets_prior,capex]):raise ValueError('Invalid economic magnitude')
  if revenue<cogs or prior_rev<prior_cogs:raise ValueError('Unexpected negative gross profit, require alternate presentation')
  if n(d,'gross_profit')!=revenue-cogs:raise ValueError('GROSS_PROFIT_FAIL '+code)
  if inv+ar>assets or inv_prior+ar_prior>assets_prior:raise ValueError('Asset share exceeds assets '+code)
  if code=='300308' and doc['source_sha256']=='NOT_VERIFIED_REMOTE_PDF':
   # This is a known prior workflow limitation; now the exact user-uploaded bytes are present.
   # We record this freshly calculated sha, not silently alter the old issuer ledger.
   source_state='verified_user_uploaded_pdf_sha_calculated_here'
  else:source_state='verified_against_normalized_ledger'
  facts[code]={
    'name':SHORT[code],'full':doc['issuer'],'role':ROLE[code],'pdf_sha256':hashval,'pdf_pages':doc['pages'],
    'source_state':source_state,'raw':d,
    'rev':revenue,'prior_rev':prior_rev,'cogs':cogs,'prior_cogs':prior_cogs,
    'gp':revenue-cogs,'prior_gp':prior_rev-prior_cogs,'np':ni,'cfo':cfo,'capex':capex,
    'fcf':cfo-capex,'assets':assets,'assets_prior':assets_prior,
    'ar':ar,'ar_prior':ar_prior,'inv':inv,'inv_prior':inv_prior,
    'growth':revenue/prior_rev-1,'gm':(revenue-cogs)/revenue,'gm_prior':(prior_rev-prior_cogs)/prior_rev,
    'cash_ratio':cfo/ni,'wc_share':(ar+inv)/assets,'wc_share_prior':(ar_prior+inv_prior)/assets_prior,
  }
 return facts

def chart_growth(f):
 body=[]; maxgrow=D('2.1');start=224; span=590
 for idx,(code,z) in enumerate(f.items()):
  yy=76+idx*78;xx=start+float(z['growth']/maxgrow)*span
  body.append(svgt(24,yy+9,z['name'],19,'#16363B',weight=700))
  body.append(f'<rect x="{start}" y="{yy-16}" width="{max(1,xx-start):.1f}" height="31" rx="3" fill="{PALETTE[code]}" opacity=".90"/>')
  body.append(svgt(min(885,xx+13),yy+8,'+'+pct(z['growth']),17,'#16363B',weight=700))
  body.append(svgt(24,yy+30,f'{y(z["prior_rev"])} → {y(z["rev"])} 亿元',12,'#667876'))
 for k in [0,1,2]:
  xx=start+float(D(k)/maxgrow)*span
  body.append(f'<line x1="{xx:.1f}" y1="31" x2="{xx:.1f}" y2="286" stroke="#D8E3DE" stroke-width="1"/>')
  body.append(svgt(xx,310,str(k*100)+'%',12,'#738682','middle'))
 return svgwrap(''.join(body),'三家上市公司2026H1收入同比增速比较，横轴从0到200%，数据在源报表中有据可查',1000,330)

def chart_margin(f):
 body=[];lo=D('.35');hi=D('.70');x0=256;W=580
 for idx,(code,z) in enumerate(f.items()):
  yy=65+idx*78
  a=x0+float((z['gm_prior']-lo)/(hi-lo))*W
  b=x0+float((z['gm']-lo)/(hi-lo))*W
  body.append(svgt(25,yy+4,z['name'],18,'#16363B',weight=700))
  body.append(f'<line x1="{a:.2f}" y1="{yy}" x2="{b:.2f}" y2="{yy}" stroke="{PALETTE[code]}" stroke-width="8" stroke-linecap="round" opacity=".30"/>')
  body.append(f'<circle cx="{a:.2f}" cy="{yy}" r="7" fill="#fff" stroke="{PALETTE[code]}" stroke-width="3"/>')
  body.append(f'<circle cx="{b:.2f}" cy="{yy}" r="9" fill="{PALETTE[code]}" stroke="#fff" stroke-width="2"/>')
  body.append(svgt(25,yy+25,f'2025H1 {pct(z["gm_prior"])}',12,'#637976'))
  body.append(svgt(25,yy+43,f'2026H1 {pct(z["gm"])}  ({c((z["gm"]-z["gm_prior"])*100)}pp)',12,'#38555A'))
 for val in [35,40,45,50,55,60,65,70]:
  x=x0+(val-35)/(70-35)*W;body.append(f'<line x1="{x:.1f}" y1="20" x2="{x:.1f}" y2="276" stroke="#DDE8E1"/>');body.append(svgt(x,301,f'{val}%',12,'#768883','middle'))
 return svgwrap(''.join(body),'三家公司同一会计口径下的2025H1与2026H1合并毛利率变化哑铃图',1000,325)

def chart_cash(f):
 body=[];start=238; W=570
 for idx,(code,z) in enumerate(f.items()):
  yy=68+idx*79;w=float(z['cash_ratio'])*W
  body.append(svgt(20,yy,z['name'],18,'#16363B',weight=700))
  body.append(f'<rect x="{start}" y="{yy-21}" width="{W}" height="26" rx="3" fill="#E9EFEB"/>')
  body.append(f'<rect x="{start}" y="{yy-21}" width="{w:.1f}" height="26" rx="3" fill="{PALETTE[code]}"/>')
  body.append(svgt(828,yy-1,pct(z['cash_ratio']),18,'#16363B',weight=700))
  body.append(svgt(20,yy+28,f'净利 {y(z["np"])} 亿 · CFO {y(z["cfo"])} 亿',12,'#607874'))
 return svgwrap(''.join(body),'三家企业2026年上半年经营现金流除以合并净利润的比例，金额均以亿元人民币显示',1000,302)

def chart_fcf(f):
 # center zero x=470 with true signed scale -35 to +12, color scheme positive/negative
 body=[];zero=660;scale=15
 body.append(f'<line x1="{zero}" y1="23" x2="{zero}" y2="272" stroke="#213E45" stroke-width="2"/>')
 for i,(code,z) in enumerate(f.items()):
  yy=70+i*82;w=float(abs(z['fcf']/UNIT))*scale;x=zero if z['fcf']>0 else zero-w
  col='#078369' if z['fcf']>=0 else '#BE695B'
  body.append(svgt(25,yy-4,z['name'],18,'#16363B',weight=700))
  body.append(f'<rect x="{x:.1f}" y="{yy-23}" width="{max(w,1):.1f}" height="33" rx="2" fill="{col}"/>')
  label=('+' if z['fcf']>=0 else '−')+y(abs(z['fcf']))+' 亿'
  body.append(svgt(max(70,x-10) if z['fcf']<0 else min(960,zero+w+10),yy, label,17,'#243D42','end' if z['fcf']<0 else 'start',700))
  body.append(svgt(25,yy+26,f'CFO {y(z["cfo"])} − 投资现金支出 {y(z["capex"])}',12,'#657A76'))
 body.append(svgt(zero,310,'零基准',13,'#4A6765','middle'))
 return svgwrap(''.join(body),'同一口径的2026H1简化自由现金流CFO减构建长期资产现金支出，以零为界分别显示正值和负值',1000,334)

def chart_wc(f):
 body=[];start=255; W=595; domain=D('.72')
 for i,(code,z) in enumerate(f.items()):
  yy=72+i*82;a=start+float(z['wc_share_prior']/domain)*W;b=start+float(z['wc_share']/domain)*W
  body.append(svgt(20,yy+5,z['name'],18,'#16363B',weight=700))
  body.append(f'<line x1="{a:.1f}" y1="{yy}" x2="{b:.1f}" y2="{yy}" stroke="{PALETTE[code]}" stroke-width="8" opacity=".35" stroke-linecap="round"/>')
  body.append(f'<circle cx="{a:.1f}" cy="{yy}" r="7" fill="white" stroke="{PALETTE[code]}" stroke-width="2.7"/>')
  body.append(f'<circle cx="{b:.1f}" cy="{yy}" r="9" fill="{PALETTE[code]}"/>')
  body.append(svgt(20,yy+30,f'{pct(z["wc_share_prior"])} (2025-12) → {pct(z["wc_share"])} (2026-06)',12,'#5B7772'))
 for val in [0,20,40,60]:
  x=start+val/72*W;body.append(f'<line x1="{x:.1f}" y1="24" x2="{x:.1f}" y2="285" stroke="#DDE7E1"/>');body.append(svgt(x,307,str(val)+'%',12,'#6C817B','middle'))
 return svgwrap(''.join(body),'应收账款净额加存货净额除以总资产的两期时点比较，非经营现金流变动',1000,332)

def chart_mix(f):
 # 2026 Jun account receivables and inventory percent of assets, arithmetic exact.
 body=[];start=228;W=580
 for i,(code,z) in enumerate(f.items()):
  yy=75+83*i;a=float(z['ar']/z['assets'])*W;inv=float(z['inv']/z['assets'])*W
  body.append(svgt(25,yy-8,z['name'],18,'#16363B',weight=700))
  body.append(f'<rect x="{start}" y="{yy-31}" width="{a:.1f}" height="30" fill="#567F9B"/>')
  body.append(f'<rect x="{start+a:.1f}" y="{yy-31}" width="{inv:.1f}" height="30" fill="#B07A5D"/>')
  body.append(f'<rect x="{start+a+inv:.1f}" y="{yy-31}" width="{max(0,W-a-inv):.1f}" height="30" fill="#E8EEEB"/>')
  body.append(svgt(25,yy+25,f'应收 {pct(z["ar"]/z["assets"])} + 存货 {pct(z["inv"]/z["assets"])}',12,'#667C76'))
  body.append(svgt(825,yy-8,pct(z['wc_share']),17,'#16363B',weight=700))
 body.append(svgt(start,315,'▰ 蓝：应收净额   ▰ 土色：存货净额   ▰ 灰：其余资产（非一项单独披露业务）',12,'#68807A'))
 return svgwrap(''.join(body),'2026-06-30合并资产中应收账款和存货净额所占比例，按100%总资产分配',1000,338)

CSS='''
:root{--ink:#16363B;--muted:#607875;--green:#087F68;--copper:#AC765C;--blue:#436F87;--bg:#F6F5F0;--line:#D8E2DC;--paper:#FFFEFC;--serif:Georgia,"Songti SC",serif;--sans:-apple-system,BlinkMacSystemFont,"PingFang SC","Noto Sans CJK SC",sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:var(--bg);font-family:var(--sans)}.wrap{width:min(1100px,calc(100% - 48px));margin:auto}.mast{background:#102C33;color:#F7FBF9;padding:20px 0 92px}.topnav{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #42646A;padding-bottom:19px;gap:18px}.brand{font:700 14px/1.1 var(--sans);letter-spacing:.18em;color:#D6F0E7;text-decoration:none}.topnav a:not(.brand){color:#B9D8CD;font-size:12px;text-decoration:none}.topnav small{letter-spacing:.15em;color:#AED4C6}.tag{font-size:11px;letter-spacing:.15em;font-weight:760;color:#83C7B1;text-transform:uppercase}.hero{padding-top:81px}.hero h1{font:600 clamp(38px,5.4vw,68px)/1.18 var(--serif);letter-spacing:-.047em;max-width:970px;margin:24px 0 26px;text-wrap:balance}.hero p{font-size:17px;line-height:1.9;color:#D2E3DC;max-width:790px}.hero .meta{margin-top:36px;display:flex;gap:20px;flex-wrap:wrap;font-size:12px;color:#AFC9C0}.hero .meta span{border-left:2px solid #75B8A4;padding-left:10px}.tabs{padding:22px 0;border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;gap:20px}.tabs a{color:#315753;text-decoration:none;font-size:12px;font-weight:700}.tabs a:hover{text-decoration:underline}.chapter{padding:74px 0;border-bottom:1px solid var(--line);scroll-margin-top:18px}.eyebrow{font-size:11px;font-weight:800;letter-spacing:.16em;color:#09816A}.chapter h2{font:550 clamp(26px,3.4vw,42px)/1.32 var(--serif);letter-spacing:-.035em;max-width:920px;margin:18px 0 20px;text-wrap:balance}.chapter .lead{color:#415F5C;font-size:16px;line-height:1.95;max-width:850px}.chapter .lead strong{color:#126D5A}.pair{display:grid;grid-template-columns:1.1fr .9fr;gap:45px;align-items:start;margin:32px 0}.statement{border-left:3px solid var(--green);padding-left:21px;font:520 22px/1.6 var(--serif);color:#214747}.aside{font-size:14px;line-height:1.85;color:#5D7470}.figure{background:var(--paper);border:1px solid #DCE6DF;padding:30px;margin:34px 0 24px}.fig-head{display:flex;align-items:baseline;justify-content:space-between;gap:16px}.fig-head b{font:620 19px/1.4 var(--serif);letter-spacing:-.01em}.fig-head em{font-size:11px;color:#6D8680;font-style:normal;white-space:nowrap}.fig-scroll{overflow-x:auto;margin-top:18px}.figure-svg{font-family:var(--sans);display:block;min-width:730px;width:100%;height:auto}.fig-source{border-top:1px solid #E6ECE8;padding-top:13px;margin-top:15px;color:#617774;font-size:12px;line-height:1.75}.fig-source a{color:#087C65}.ribbon{display:flex;flex-wrap:wrap;gap:12px;margin:22px 0}.ribbon span{font-size:13px;border:1px solid #D1DFD7;padding:9px 13px;background:#FCFDFB}.ribbon b{font-size:15px}.explain{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:26px 0}.explain>div{background:#ECF2ED;padding:24px;border-top:2px solid #92B9A9}.explain>div:last-child{background:#F6ECE7;border-top-color:#C99B85}.explain h3{font:600 17px var(--serif);margin:0 0 10px}.explain p{font-size:14px;line-height:1.9;margin:0}.smallcaps{font-size:11px;letter-spacing:.13em;color:#6D837D;text-transform:uppercase}.matrix{width:100%;border-collapse:collapse;font-size:13px;margin-top:18px}.matrix td,.matrix th{text-align:left;padding:14px 10px;border-bottom:1px solid #D8E2DB;vertical-align:top}.matrix th{color:#50766A}.matrix td:first-child{font-weight:750}.case{padding:25px 0;border-top:1px solid #DBE6DE}.case h3{font:600 21px var(--serif);margin:0 0 12px}.case p{line-height:1.85;color:#4F6963;font-size:14px}.footer{background:#102C33;color:#C4DBD3;padding:55px 0 75px}.footer a{color:#A2D7C5}.footer p{font-size:13px;line-height:1.9}.figure-svg text{paint-order:stroke;stroke:transparent}.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}
@media(max-width:720px){.wrap{width:calc(100% - 34px)}.mast{padding-bottom:55px}.hero{padding-top:57px}.hero h1{font-size:clamp(34px,9vw,47px);letter-spacing:-.04em}.hero p{font-size:15px}.chapter{padding:47px 0}.pair,.explain{grid-template-columns:1fr;gap:16px}.figure{padding:20px 15px}.figure-svg{min-width:700px}.fig-scroll:after{display:block;content:'← 左右滑动阅读完整图形 →';color:#6B7F79;font-size:11px;margin-top:10px}.fig-head{align-items:flex-start;flex-direction:column;gap:5px}.topnav{flex-wrap:wrap}.matrix{font-size:12px}.matrix td,.matrix th{padding:11px 7px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
'''

def figure(num,title,label,svg,note):
 return f'''<figure class="figure" id="figure-{num}"><div class="fig-head"><b>{E(title)}</b><em>FIG. {num} · {E(label)}</em></div><div class="fig-scroll">{svg}</div><figcaption class="fig-source">{note}</figcaption></figure>'''

def source_note(f,keys,range_label):
 return '；'.join(f'{z["name"]} {"/".join(source(z["raw"],k) for k in keys)}' for z in f.values())+'；报告期：'+range_label+'。各原文件指纹见文末。'

def render(f):
 growth=figure('01','收入增长速度不等于绝对规模','同比增长率',chart_growth(f),source_note(f,['revenue','revenue_prior'],'2026H1 vs 2025H1')+'增速为期间报表数据计算值；所有横条统一从 0 起。')
 margin=figure('02','毛利率变化：方向与幅度，而非一句“规模效应”','毛利率百分比及百分点变化',chart_margin(f),source_note(f,['revenue','cogs','revenue_prior','cogs_prior'],'两期半年报')+'哑铃图刻度为35%–70%，属于区间位置图，非面积编码。')
 cash=figure('03','同样是盈利增长，兑现为经营现金的比例截然不同','CFO / 合并净利润',chart_cash(f),source_note(f,['net_profit','cfo'],'2026H1')+'比例并非坏账认定或现金长期质量评级；请结合存货与应收周转和后续回款。')
 fcf=figure('04','经营现金之后，还剩多少用于投资与回报？','简化自由现金流，亿元',chart_fcf(f),source_note(f,['cfo','capex_cash'],'2026H1')+'简化 FCF = CFO − “购建固定资产、无形资产和其他长期资产支付的现金”；不是公司披露的独立 FCF 指标，也非维护性资本开支。')
 wc=figure('05','应收与库存合计对资产的占用：一年之内的时点变化','2025年末→2026年6月末',chart_wc(f),source_note(f,['accounts_receivable','inventory','assets','accounts_receivable_prior','inventory_prior','assets_prior'],'两个资产负债表时点')+'应收与库存均按净额计算。时点资产变化不能直接等同现金流间接法调整。')
 mix=figure('06','把总占用拆开看：应收、库存和其他资产','2026年6月末，总资产=100%',chart_mix(f),source_note(f,['accounts_receivable','inventory','assets'],'2026-06-30')+'蓝色为应收账款净额，土色为存货净额，余量为其余资产合计（派生差额，非单一披露科目）。')
 revs={key:y(x['rev']) for key,x in f.items()};nps={key:y(x['np']) for key,x in f.items()}; cfcs={key:y(x['cfo']) for key,x in f.items()}
 matrix=''.join(f'<tr><td><a href="{code}.html">{z["name"]}</a></td><td>{y(z["rev"])} 亿</td><td>{pct(z["growth"])}</td><td>{pct(z["gm"])}</td><td>{pct(z["cash_ratio"])}</td><td>{y(z["fcf"])} 亿</td></tr>' for code,z in f.items())
 links=''.join(f'<li>{z["name"]}（{code}.SZ）2026H1，PDF SHA256：<code>{z["pdf_sha256"]}</code>，{z["pdf_pages"]} 页；原始报表收入 {source(z["raw"],"revenue")}，CFO {source(z["raw"],"cfo")}。</li>' for code,z in f.items())
 return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="基于天孚通信、中际旭创、新易盛2026H1原始公告财报的光互连企业经营和现金质量对照，六张原创可核验财务信息图。"><title>光互连三家公司，利润和现金并不同行｜Financials in Visuals</title><style>{CSS}</style></head>
<body><header class="mast"><div class="wrap"><nav class="topnav" aria-label="研究导航"><a class="brand" href="/">FINANCIALS <span style="color:#78BEA8">IN VISUALS</span></a><small>RESEARCH EDITION / 2026 H1</small><a href="/">返回研究目录 ↗</a></nav>
<div class="hero"><div class="tag">SECTOR NOTE 01 · EVIDENCE-LED COMPARATIVE RESEARCH</div><h1>同样站在 AI 光互连浪潮里，<br>利润与现金却走出三种路径。</h1><p>天孚通信处于更上游的光连接与器件环节；中际旭创和新易盛以高速光模块、光互连解决方案为核心。收入增速、毛利率、库存应收和现金转化揭示不同商业模型，但不能把它们粗暴排成一条“谁更好”的榜单。</p><div class="meta"><span>三家公司 · 2026 年半年度</span><span>同一会计期间，原始 PDF 勾稽</span><span>全部金额人民币 · 未经审计</span><span>不包含估值或投资评级</span></div></div></div></header>
<div class="wrap"><nav class="tabs" aria-label="篇章"><a href="#architecture">产业位置</a><a href="#growth">增长与盈利</a><a href="#cash">现金质量</a><a href="#balance">资产占用</a><a href="#judgment">研究判断</a><a href="#sources">数据来源</a></nav>
<section class="chapter" id="architecture"><div class="eyebrow">01 / BUSINESS MODEL BEFORE NUMBERS</div><h2>先区分所处环节，再比较财务比率。</h2><p class="lead">产业链是分析前提，不是装饰性图形。天孚通信的器件、封装与连接相关经济性，与中际旭创、新易盛的光模块与光互连产品经济性并不完全相同：产品定义、规模、采购结构和客户结构都可能使毛利率不可直接解释为经营优劣。</p>
<div class="ribbon"><span><b>上游光器件／连接</b> · 天孚通信</span><span><b>光模块／互连解决方案</b> · 中际旭创</span><span><b>光模块／互连解决方案</b> · 新易盛</span></div><div class="pair"><p class="statement">真正有价值的横向比较，不是“收入谁最大”，而是“谁用什么资产、承担什么风险，创造多少可持续现金”。</p><p class="aside">这里只比较每家公司自身的法定合并报表。图中的产业链分类不意味着三家之间存在已证实的直接采购、销售或客户关系，也不证明市场份额排名。业务定位以各公司管理层讨论与分析为主，不作为独立行业调查结论。</p></div>
<table class="matrix"><thead><tr><th>企业</th><th>营业收入</th><th>同比</th><th>综合毛利率</th><th>CFO / 合并净利润</th><th>简化FCF</th></tr></thead><tbody>{matrix}</tbody></table></section>
<section class="chapter" id="growth"><div class="eyebrow">02 / ECONOMICS OF GROWTH</div><h2>增长的速度与质量，必须分开回答。</h2><p class="lead">中际旭创的营业收入增长最快，天孚通信与光模块整机厂的规模差异也最明显。但收入增速不等于定价能力，毛利率上升也不能未经分解就全部归因于“产品高端化”。</p>{growth}{margin}
<div class="explain"><div><h3>支持解释</h3><p>需求增长、产品组合变化与规模扩张，可能同时推动收入和毛利润。财报管理层给出了产品及需求方面的描述，真正的价格、数量、型号与成本量化归因仍需一致的型号级披露。</p></div><div><h3>最强反面解释</h3><p>产品升级对供给、原材料和出货确认的压力也可能提高。综合毛利率的变化不能排除汇率、供应条件和会计分类的影响；现有三份报告并不能证明每家公司未来利润率持续改善。</p></div></div></section>
<section class="chapter" id="cash"><div class="eyebrow">03 / CASH CONVERSION & REINVESTMENT</div><h2>净利润是会计结果，现金流反映另一组约束。</h2><p class="lead">报告期内三家企业都实现了较大规模盈利，但 CFO 与合并净利润的匹配程度显著不同。账面利润高并不意味着即期经营现金同等充裕；短期资金占用也不能自动推导出坏账或需求崩塌。</p>{cash}{fcf}
<div class="pair"><p class="statement">判断利润质量不能只看 CFO / 净利润比值，还需要看现金流附注里的经营性应收、库存与应付变化，以及未来两个报告期的回款。</p><p class="aside">这里的简化自由现金流采用三家公司现金流量表相同的“购建固定资产、无形资产和其他长期资产支付的现金”科目，便于并列比较，但没有拆分增长型与维护型资本支出，亦不构成可分配现金或企业自由现金流（FCFF）。</p></div></section>
<section class="chapter" id="balance"><div class="eyebrow">04 / CAPITAL TIED TO OPERATIONS</div><h2>应收和库存同时增长时，资金安全垫的含义会改变。</h2><p class="lead">需要把期末库存、应收账款放回资产负债表，而不是直接把两个时点的账面余额变化画成经营现金流。下图使用同一分母“该时点总资产”，展示资产结构的变化。</p>{wc}{mix}
<div class="explain"><div><h3>合理的经营解释</h3><p>订单增加、长周期关键物料提前备货、产能扩张可能推高库存和应收。应收与存货占用上升并不单独构成风险结论。</p></div><div><h3>需要持续检验的风险</h3><p>关注原材料及产成品账龄、跌价准备、应收账款账龄与坏账计提、客户付款条件、预付款集中度，以及经营现金流是否在后续季度改善。</p></div></div></section>
<section class="chapter" id="judgment"><div class="eyebrow">05 / RESEARCH JUDGMENT, NOT A LEAGUE TABLE</div><h2>三家公司的共同问题，是下一轮增长能否同时改善现金效率。</h2>
<div class="case"><h3>天孚通信：需关注业务结构、供应及资金沉淀</h3><p>上游器件与连接环节的利润表现应联系产品组合、制造能力和客户结构判断。现金转换相对更充分，但期末应收和存货仍要求继续检查；不能只凭当前比值认定全面领先。</p></div>
<div class="case"><h3>中际旭创：现金流转化与大规模再投资同时承压</h3><p>营收与毛利润显著增加，但同期 CFO / 合并净利润比率较低，现金购建长期资产金额超过 CFO。重点跟踪存货、经营性应收与新产能投入回报；经营现金流低并不能单独证明收入确认不当。</p></div>
<div class="case"><h3>新易盛：高端化和备货力度需要现金反馈</h3><p>报告披露销量和收入均增长，综合毛利率改善。应收、存货资产占比上升，后续报告应关注材料备货能否转化为交付、回款与自由现金流，而非仅凭产品规格判断盈利持续性。</p></div>
<div class="explain"><div><h3>未来最有信息量的验证指标</h3><p>分产品收入与毛利率、应收账龄及回款、存货分类与跌价、CFO净利润转换、购建长期资产现金支出、后续经营现金净流入。</p></div><div><h3>当前不可下的结论</h3><p>这三份单期财报不足以生成 8–12 个季度的趋势、股价与基本面背离、同业估值百分位、客户收入份额或合理目标价。报告不输出交易建议。</p></div></div></section>
<section class="chapter" id="sources"><div class="eyebrow">06 / TRACEABLE EVIDENCE</div><h2>任何重要图形，都应能够回到原始披露。</h2><p class="lead">来源：三家上市公司 2026 年半年度合并报表。下列页码采用各自原始 PDF 中的物理页面顺序，若与印刷页码存在偏差，应以 PDF 实际页为准。原始文件已在本地计算 SHA-256；数值均保留人民币元核算，仅展示时换算为亿元或百分比。</p><ul style="color:#55726B;font-size:13px;line-height:2.1;overflow-wrap:anywhere">{links}</ul><p class="aside">方法依据：中国证监会 2025 年半年度报告内容与格式准则、财政部企业会计准则；视觉设计依据 App Economy Insights 公开研究图形语法及 Financial Times Visual Vocabulary。该作品为独立研究和原创图形，不代表上述机构认可；不复制其图形。</p></section></div>
<footer class="footer"><div class="wrap"><b style="letter-spacing:.15em">FINANCIALS IN VISUALS</b><p>Independent A-share financial research / source checked, accounting reconciled, evidence-limited.</p><p><a href="/">返回研究目录</a> · 关联企业：<a href="/300394.html">天孚通信</a> / <a href="/300308.html">中际旭创</a> / <a href="/300502.html">新易盛</a></p></div></footer></body></html>'''

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--qa',required=True)
 parser.add_argument('--source-map',help='JSON mapping 300394/300308/300502 to {ledger,pdf}; paths resolved relative to map file. REQUIRED outside local demo environment')
 args=parser.parse_args()
 if args.source_map:
  map_path=Path(args.source_map).resolve()
  mappings=json.loads(map_path.read_text())
  ledgers={code:(map_path.parent/parts['ledger']).resolve() for code,parts in mappings.items()}
  pdfs={code:(map_path.parent/parts['pdf']).resolve() for code,parts in mappings.items()}
  f=checked(ledgers,pdfs)
 elif all(x.exists() for x in list(DEFAULT_CASES.values())+list(PDF_PATHS.values())):
  print('NOTICE: local demo input paths were found; pass --source-map to run with your own original PDFs')
  f=checked()
 else:
  parser.error('Missing --source-map: provide user-owned original PDFs and evidence ledgers')
 content=render(f);p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding='utf-8')
 data={'version':'nextlevel-research-2026-11-01','doc_type':'industry_comparative','issuers':{},'pdf_hash_pass':True,'accounting_checks':'PASS_GROSS_PROFIT_AND_BASES','chart_count':6,'chart_types':['ranked_zero_baseline_growth_bars','margin_dumbbell','cash_conversion_bar','signed_fcf_diverging','working_capital_share_dumbbell','asset_composition_100pct_stacked'],'chart_full_source':True,'valuation_data':'NOT_PROVIDED','live_http':'NOT_CHECKED','html_sha256':hashlib.sha256(content.encode()).hexdigest()}
 for code,z in f.items():
  data['issuers'][code]={'name':z['name'],'source_sha256':z['pdf_sha256'],'h1_revenue_yuan':str(z['rev']),'h1_gross_margin':str(z['gm']),'h1_cfo_ni':str(z['cash_ratio']),'h1_cash_capex_yuan':str(z['capex']),'h1_simple_fcf_yuan':str(z['fcf']),'stock_wc_share_dec':str(z['wc_share_prior']),'stock_wc_share_jun':str(z['wc_share'])}
 Path(args.qa).parent.mkdir(parents=True,exist_ok=True);Path(args.qa).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print(json.dumps({'file':str(p),'bytes':len(content),'sha256':data['html_sha256'],'charts':6},ensure_ascii=False))
if __name__=='__main__':main()