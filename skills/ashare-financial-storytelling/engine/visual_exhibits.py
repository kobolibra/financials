#!/usr/bin/env python3
"""Generic verified-ledger balance composition and two-stage cash waterfall.

Builds original SVGs from a validated issuer ledger, never encodes issuer-specific
figures or page numbers in drawing functions. This does not extract PDFs or
substitute for a human research-editor review.
"""
from pathlib import Path
from decimal import Decimal as D
from html import escape
import json, sys

C= D('100000000')
TEAL='#078568'; LITE='#94cbb7'; DARK='#14393f'; RED='#ba7767'; GREY='#acbdb4'; BLUE='#547e9e'; LIGHT='#e6ede7'

def cy(v): return f'{(v/C):.2f}'
def F(v): return f'{float(v):.4f}'
def val(data,key): return D(data['facts'][key]['amount'])
def src(data,key): return 'p'+str(data['facts'][key].get('page','?'))

def ribbon(x1,x2,a,b,w,col,title):
    # Cubic edges bound a positive, nonzero-width conserved stream.
    m=(x1+x2)/2
    p=f'M {x1:.2f} {a:.2f} C {m:.2f} {a:.2f} {m:.2f} {b:.2f} {x2:.2f} {b:.2f} L {x2:.2f} {b+w:.2f} C {m:.2f} {b+w:.2f} {m:.2f} {a+w:.2f} {x1:.2f} {a+w:.2f} Z'
    return f'<path d="{p}" fill="{col}" opacity=".69" stroke="#fff" stroke-width="1" tabindex="0" role="img" aria-label="{escape(title)}"><title>{escape(title)}</title></path>'

def text(x,y,s,size=16,fill=DARK,bold=False,anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{700 if bold else 450}" fill="{fill}" text-anchor="{anchor}">{escape(str(s))}</text>'

def svg_balance(data):
    A=val(data,'assets'); L=val(data,'liabilities'); E=val(data,'equity')
    assert A==L+E
    cur=val(data,'current_assets'); noncur=val(data,'noncurrent_assets')
    items=[('货币资金',val(data,'monetary_funds'),BLUE,'monetary_funds'),('应收账款净额',val(data,'accounts_receivable'),TEAL,'accounts_receivable'),('存货净额',val(data,'inventory'),LITE,'inventory'),('其他流动资产（计算）',cur-val(data,'monetary_funds')-val(data,'accounts_receivable')-val(data,'inventory'),GREY,None),('非流动资产',noncur,'#99a6a9','noncurrent_assets')]
    assert sum(i[1] for i in items)==A and min(i[1] for i in items)>0
    k=5; a_y=145; dest_y=145; out=[]
    out += [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 700" role="img" aria-label="资产构成与负债权益配平，按{escape(data["document"]["period_end"])}金额比例，图形表示资产负债的时点组成而非现金流动" style="font-family:-apple-system,PingFang SC,Microsoft YaHei,sans-serif;min-width:980px;width:100%;height:auto;background:#fffefb">',
            text(24,50,'ASSET COMPOSITION   /   ACCOUNTING IDENTITY',15,TEAL,True), text(24,87,'金额对应面积 · 亿元人民币 · 期末余额，不是资金实际转移',16,'#647775')]
    for i,(name,amount,col,key) in enumerate(items):
        w=float(amount/C)*k; a=a_y; b=dest_y; label=f'{name} {cy(amount)}亿元 '+(src(data,key) if key else '计算残余')
        out.append(ribbon(346,704,a,b,w,col,label))
        out.append(f'<rect x="328" y="{a:.2f}" width="18" height="{w:.2f}" fill="{col}"/>')
        out.append(text(308,a+w/2-2,name,16,DARK,True,'end'))
        out.append(text(308,a+w/2+18,cy(amount)+' 亿',15,'#64817b',False,'end'))
        a_y += w + 21;dest_y += w
    total_h=float(A/C)*k
    out.append(f'<rect x="704" y="145" width="28" height="{total_h:.2f}" fill="{DARK}"/>')
    out.append(text(715,116,'总资产',18,DARK,True,'middle'))
    out.append(text(715,636,cy(A)+' 亿',23,DARK,True,'middle'))
    out.append(text(715,661,'= 总负债 + 所有者权益',12,'#647775',False,'middle'))
    source_y=145; right_y=153
    for name,amount,col in [('负债',L,RED),('所有者权益',E,TEAL)]:
        w=float(amount/C)*k
        out.append(ribbon(732,1054,source_y,right_y,w,col,f'{name} {cy(amount)} 亿元；资产=负债+权益'))
        out.append(f'<rect x="1054" y="{right_y:.2f}" width="23" height="{w:.2f}" fill="{col}"/>')
        out.append(text(1095,right_y+w/2-6,name,19,DARK,True))
        out.append(text(1095,right_y+w/2+18,cy(amount)+' 亿元',19,col,True))
        source_y+=w;right_y+=w+48
    out.append(text(328,608,'资产项目 →',14,'#6c7e7b'))
    out.append(text(1095,609,'资金来源结构 →',14,'#6c7e7b'))
    out.append('</svg>')
    return ''.join(out)

def svg_cash(data):
    F=data['facts']; NP=val(data,'net_profit'); CFO=val(data,'cfo'); OPEN=val(data,'cash_open'); CFI=val(data,'cfi'); CFF=val(data,'cff'); FX=val(data,'fx_effect'); CLOSE=val(data,'cash_close');ADJ=data['indirect_cfo_adjustments']
    v={x['source_label']:D(x['amount']) for x in ADJ}
    inv=v['存货减少（增加）']; ar=v['经营性应收项目减少（增加）']; ap=v['经营性应付项目增加（减少）']
    other=sum((D(x['amount']) for x in ADJ),D('0'))-inv-ar-ap
    assert NP+other+inv+ar+ap==CFO
    assert OPEN+CFO+CFI+CFF+FX==CLOSE
    out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 870" role="img" aria-label="从净利润到经营现金流，再从期初现金到期末现金的两层有符号财务瀑布，原值来源于现金流表及间接法附注" style="font-family:-apple-system,PingFang SC,Microsoft YaHei,sans-serif;min-width:1020px;width:100%;height:auto;background:#fffefb">',
        text(30,46,'I    EARNINGS → OPERATING CASH',15,TEAL,True),text(30,77,f'合并净利润 + {len(ADJ)} 项有符号调整 = CFO',15,'#647775')]
    def row(ybase,top,scale,labels,values,start=0,width=100,x_start=36,step=210):
        current=D(start)
        for i,(label,v) in enumerate(zip(labels,values)):
            x=x_start+i*step
            if i==0 and start==0:
                current=v
                yy=ybase-float(v/C)*scale
                hh=float(v/C)*scale
                out.append(f'<rect x="{x}" y="{yy:.1f}" width="{width}" height="{hh:.1f}" fill="{DARK}" rx="2"/>')
                out.append(text(x+width/2,yy-11,cy(v)+' 亿',18,DARK,True,'middle'))
            else:
                old=current;current+=v
                y_old=ybase-float(old/C)*scale;y_new=ybase-float(current/C)*scale
                yy=min(y_old,y_new);hh=abs(y_old-y_new)
                out.append(f'<rect x="{x}" y="{yy:.1f}" width="{width}" height="{max(hh,1):.1f}" fill="{TEAL if v>=0 else RED}" rx="2"><title>{escape(label)}：{cy(v)} 亿元</title></rect>')
                out.append(f'<path d="M {x-step+width} {y_old:.1f} L {x} {y_old:.1f}" stroke="#9eaea6" stroke-width="1.5" stroke-dasharray="6 5" fill="none"/>')
                out.append(text(x+width/2,yy-12 if v>=0 else yy+hh+23,('+' if v>=0 else '')+cy(v),16,TEAL if v>=0 else RED,True,'middle'))
            out.append(text(x+width/2,ybase+33,label,14,DARK,True,'middle'))
        return current
    labels=['合并净利润','其他非现金净调整','存货调整','经营应收调整','经营应付调整']
    vals=[NP,other,inv,ar,ap]
    end=row(340,90,16,labels,vals,x_start=45,step=245)
    x=1245; y=340-float(CFO/C)*16;out.append(f'<rect x="{x}" y="{y:.1f}" width="90" height="{float(CFO/C)*16:.1f}" fill="{DARK}"/>')
    out.append(text(x+45,y-12,cy(CFO)+' 亿',19,DARK,True,'middle'))
    out.append(text(x+45,374,'CFO',15,DARK,True,'middle'))
    assert end==CFO
    out.append(f'<path d="M 45 437 H 1344" stroke="{LIGHT}" stroke-width="2"/>')
    out.append(text(30,470,'II    OPENING CASH → CLOSING CASH',15,TEAL,True))
    out.append(text(30,500,'现金及现金等价物：经营 + 投资 + 筹资 + 汇率 = 期末',14,'#647775'))
    labels=['期初现金','经营活动','投资活动','筹资活动','汇率变动','期末现金']
    vals=[OPEN,CFO,CFI,CFF,FX]
    curr=D(0);last_y=0
    ybase=765;scale=6.1
    for i,(label,v) in enumerate(zip(labels,vals)):
        x=50+i*210
        if i==0:
            curr=v; y=ybase-float(curr/C)*scale; hh=float(curr/C)*scale
            out.append(f'<rect x="{x}" y="{y:.1f}" width="105" height="{hh:.1f}" fill="{DARK}"/>')
            out.append(text(x+53,y-12,cy(curr)+' 亿',18,DARK,True,'middle'))
        else:
            old=curr;curr+=v;y1=ybase-float(old/C)*scale;y2=ybase-float(curr/C)*scale; y=min(y1,y2);hh=abs(y1-y2)
            out.append(f'<path d="M {x-105} {y1:.1f} L {x} {y1:.1f}" stroke="#9eaea6" stroke-dasharray="5 5"/>')
            out.append(f'<rect x="{x}" y="{y:.1f}" width="105" height="{max(hh,1):.1f}" fill="{TEAL if v>=0 else RED}"/>')
            out.append(text(x+52,y-12 if v>=0 else y+hh+21,('+' if v>=0 else '')+cy(v),16,TEAL if v>=0 else RED,True,'middle'))
        out.append(text(x+52,803,label,14,DARK,True,'middle'))
    assert curr==CLOSE
    x=1100;y=ybase-float(CLOSE/C)*scale;hh=float(CLOSE/C)*scale
    out.append(f'<rect x="{x}" y="{y:.1f}" width="108" height="{hh:.1f}" fill="{DARK}"/>')
    out.append(text(x+54,y-13,cy(CLOSE)+' 亿',20,DARK,True,'middle'))
    out.append(text(x+54,803,'期末现金',15,DARK,True,'middle'))
    out.append(text(30,847,'数据：财务报表与现金流量表补充资料；括号内正负号保留；金额仅在呈现时取两位小数。',13,'#6a7877'))
    out.append('</svg>')
    return ''.join(out)

EXTRA_CSS='''\n.atlas-exhibit{border-top:1px solid #cbd9ce;padding:45px 0 58px}.atlas-exhibit h3{font:520 clamp(29px,3.6vw,43px)/1.22 Georgia,Songti SC,serif;max-width:920px;margin:12px 0 20px;letter-spacing:-.035em}.atlas-eyebrow{font-size:12px;letter-spacing:.18em;font-weight:750;color:#087c64}.atlas-exhibit .explainer{max-width:970px;color:#566d67;font-size:15px;line-height:1.86}.atlas-exhibit .atlas-sheet{background:#fffefb;border:1px solid #dce3dd;padding:24px 20px;margin:22px 0}.atlas-exhibit .atlas-scroll{overflow-x:auto}.atlas-exhibit .atlas-note{font-size:12px;color:#5a766d;line-height:1.85;margin:18px 0 0}.atlas-exhibit .atlas-caption{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;color:#618076;font-size:11px;margin-top:20px}@media(max-width:600px){.atlas-exhibit .atlas-sheet{padding:17px 12px}.atlas-exhibit{padding:32px 0 44px}.atlas-exhibit .atlas-scroll:after{content:'← 横向滑动查看完整财务图 →';display:block;font-size:11px;color:#6b7a75;padding:9px 0}}'''

def upgrade(data,original):
    b=svg_balance(data);c=svg_cash(data)
    if 'id="capital-anatomy"' in original or 'id="cash-architecture"' in original: raise ValueError('Already upgraded: duplicate exhibit is not allowed')
    b_sec=f'''<section class="atlas-exhibit" id="capital-anatomy"><div class="atlas-eyebrow">07 / CAPITAL ANATOMY · FINANCIAL POSITION</div><h3>这 {cy(val(data,'assets'))} 亿元资产，由哪些经营要素构成，又由谁提供资本？</h3><p class="explainer">不是把“资产”画成一根柱。将货币资金、应收、存货和剩余流动/长期资产按实际金额流带汇入总资产，再显示与负债及股东权益的会计恒等关系。<strong>这是一张时点资产构成图，不代表负债真的流进了哪类资产。</strong></p><div class="atlas-sheet"><div class="atlas-scroll">{b}</div><p class="atlas-note">来源：合并资产负债表 {src(data,'assets')}，货币资金 {src(data,'monetary_funds')}、应收账款 {src(data,'accounts_receivable')}、存货 {src(data,'inventory')}；详细科目请参见原披露附注。流动资产其他项由流动资产减去货币资金、应收账款净额及存货净额计算，不能据此认定是一项披露业务。资产＝负债＋所有者权益，以人民币原值精确校验。</p></div></section>'''
    c_sec=f'''<section class="atlas-exhibit" id="cash-architecture"><div class="atlas-eyebrow">08 / EARNINGS, REINVESTMENT & LIQUIDITY</div><h3>从净利润到经营现金，再到期末现金：两层桥接缺一不可。</h3><p class="explainer">第一层用报告附注完整的 {len(data['indirect_cfo_adjustments'])} 项有符号调整，区分非现金调整和营运资本变化；第二层以经营、投资、筹资和汇率变动解释现金净减少。<strong>不能把负值冒充正向桑基流带，也不能把利润表汇兑损益和现金汇率影响混为一谈。</strong></p><div class="atlas-sheet"><div class="atlas-scroll">{c}</div><p class="atlas-note">来源：合并净利润 {src(data,'net_profit')}、经营现金流 {src(data,'cfo')}、现金及现金等价物 {src(data,'cash_close')}、间接法附注 {', '.join(sorted(set('p'+str(x['page']) for x in data['indirect_cfo_adjustments'])))}。两座瀑布分别精确勾稽到 CFO 与现金及现金等价物期末余额。其他非现金净调整＝除存货、经营性应收、经营性应付外的全部剩余附注项目之和，不是任意平衡项。</p></div></section>'''
    if '<section class="method" id="methods">' not in original or '</style>' not in original: raise ValueError('Unknown template, no mutation')
    # Present dedicated exhibits beside related existing sections, not as unrelated dashboard cards.
    original=original.replace('</style>',EXTRA_CSS+'</style>')
    original=original.replace('<section class="story" id="balance">',c_sec+'<section class="story" id="balance">')
    original=original.replace('<section class="method" id="methods">',b_sec+'<section class="method" id="methods">')
    return original

if __name__=='__main__':
    source=Path(sys.argv[1]);html_path=Path(sys.argv[2]);out=Path(sys.argv[3]);d=json.loads(source.read_text());h=html_path.read_text(encoding='utf-8')
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(upgrade(d,h),encoding='utf-8');print('written',out)