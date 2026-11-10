"""Two native layouts for a signed, source-bound comparative GP bridge.

The exact Fraction decomposition is the analytical authority. Rounded cents
are explicitly reconciled, and no zero-value bar receives a decorative width.
"""
from decimal import Decimal as D
from html import escape as E
from unified_income_sankey import PALETTE,nu
from comparative_economics import EconomicsPeriod,gross_profit_bridge

EXPORT_SCRIPT='''<script>(()=>{const panel=document.currentScript.previousElementSibling;
panel.querySelector('[data-export-economics]').addEventListener('click',()=>{
const svg=[...panel.querySelectorAll('svg')].find(s=>s.getBoundingClientRect().width>0);
if(!svg)return;const copy=svg.cloneNode(true),v=svg.viewBox.baseVal;
copy.setAttribute('width',v.width);copy.setAttribute('height',v.height);
const blob=new Blob([new XMLSerializer().serializeToString(copy)],{type:'image/svg+xml;charset=utf-8'});
const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;
a.download=svg.dataset.issuer+'-gross-profit-'+svg.dataset.layout+'.svg';a.click();
setTimeout(()=>URL.revokeObjectURL(url),1000);
});})();</script>'''

PANEL_CSS='''<style>
.economics-panel{margin:36px 0 50px;padding:32px;background:#fffefa;border-top:3px solid #263F47;color:#19333C}
.economics-panel button{font:inherit;padding:9px 14px;border:1px solid #BAC7C8;border-radius:5px;background:#fff;color:#19333C;cursor:pointer;margin:10px 0}.economics-panel h2{font:600 clamp(25px,3vw,38px)/1.35 Georgia,"Songti SC",serif;margin:12px 0 18px}
.economics-panel .econ-intro{font-size:16px;line-height:1.9;max-width:900px}
.economics-panel .econ-kicker{font-size:11px;letter-spacing:.1em;color:#63747A}
.economics-panel .econ-phone{display:none}.economics-panel svg{display:block;width:100%;height:auto}
.economics-panel .econ-counter{border-left:3px solid #CD7271;padding:12px 16px;font-size:14px;line-height:1.85;background:#f8f3ef}
.economics-panel .econ-watch{font-size:14px;line-height:1.9}.economics-panel details{font-size:13px;line-height:1.9;margin-top:18px}
.economics-panel table{width:100%;min-width:0;border-collapse:collapse;font-size:12px}.economics-panel td,.economics-panel th{padding:9px 5px;border-bottom:1px solid #E4E4DE;text-align:left;overflow-wrap:anywhere}
.economics-panel .econ-formula{font-size:12px;color:#63747A;line-height:1.85;overflow-wrap:anywhere}
@media(max-width:850px){.economics-panel{padding:20px 16px;margin:25px 0}.economics-panel .econ-desktop{display:none}.economics-panel .econ-phone{display:block;max-width:460px;margin:auto}.economics-panel .econ-intro{font-size:15px}.economics-panel th,.economics-panel td{font-size:11px}}
</style>'''


def compile_ledger_comparison(ledger:dict,brief:dict)->dict:
    issuer,source=ledger["issuer"],ledger["source"]
    if issuer.get("base_unit")!="人民币元" or brief.get("statement")!="industrial_operating_income":
        raise ValueError("DECLARED_INDUSTRIAL_ORIGINAL_YUAN_ROUTE_REQUIRED")
    if brief.get("current_period")!=issuer.get("fiscal_period"):
        raise ValueError("COMPARISON_PERIOD_LEDGER_DRIFT")
    periods=[]
    for which,keys in (("prior",("rev_prior","cogs_prior")),("current",("rev","cogs"))):
        rows=[ledger["facts"][key] for key in keys]
        period=brief[which+"_period"]
        for row in rows:
            if (row.get("period")!=period or row.get("type")!="flow" or row.get("scope")!="consolidated"
                    or row.get("currency")!="CNY" or row.get("unit")!="元"
                    or row.get("classification") not in ("DISCLOSED","DISCLOSED_RESTATED")):
                raise ValueError("COMPARISON_ORIGINAL_FACT_TYPE_MISMATCH")
        start,end=brief[which+"_interval"]
        periods.append(EconomicsPeriod(issuer["code"],period,rows[0]["yuan"],rows[1]["yuan"],
            *keys,rows[0]["page"],rows[1]["page"],source["original_bytes_sha256"],
            source["physical_pages_observed"],"consolidated","CNY","yuan",brief["statement"],
            brief["definition"],"DISCLOSED_RESTATED" if which=="prior" and brief.get("prior_restated") else "DISCLOSED",start,end))
    for name in ("question","strongest_alternative","next_disclosure_falsifier"):
        if not isinstance(brief.get(name),str) or len(brief[name].strip())<15:
            raise ValueError("COMPARATIVE_EDITORIAL_CHAIN_REQUIRED "+name)
    return gross_profit_bridge(*periods,comparability_evidence=brief["comparability_evidence"])


def render_panel(ledger:dict,brief:dict)->str:
    result=compile_ledger_comparison(ledger,brief)
    source=ledger["source"];url=source["official_announcement"]
    facts=ledger["facts"]
    rows="".join(f'<tr data-fact-id="{key}" data-exact-yuan="{E(facts[key]["yuan"])}"><td>{E(facts[key]["period"])}</td>'
        f'<td>{"营业收入" if key.startswith("rev") else "营业成本"}</td><td>{E(facts[key]["yuan"])} 元</td>'
        f'<td><a href="{E(url,quote=True)}#page={facts[key]["page"]}" target="_blank" rel="noopener">p.{facts[key]["page"]}</a></td></tr>'
        for key in ("rev_prior","cogs_prior","rev","cogs"))
    effects=result["effects"]
    delta=D(result["delta_gp_yuan"])/D(100000000)
    intro=(f'同比毛利变化 {delta:+,.2f} 亿元；其中收入基数贡献 '
           f'{D(effects[0]["yuan"])/D(100000000):+,.2f} 亿元，综合毛利率贡献 '
           f'{D(effects[1]["yuan"])/D(100000000):+,.2f} 亿元。'
           f'综合毛利率由 {D(result["prior_margin_pct"]):.2f}% 变为 {D(result["current_margin_pct"]):.2f}%。')
    return (PANEL_CSS+f'<section class="economics-panel" id="comparative-economics" '
        f'data-comparative-economics="SYMMETRIC_GP_V1" data-source-pdf-sha256="{E(source["original_bytes_sha256"])}" '
        f'data-delta-gp-yuan="{E(result["delta_gp_yuan"])}">'
        '<p class="econ-kicker">经营拆解 · 收入基数 × 综合毛利率</p>'
        f'<h2>{E(brief["question"])}</h2><p class="econ-intro">{E(intro)}</p>'
        f'<div class="econ-desktop">{render_bridge(result)}</div><div class="econ-phone">{render_bridge(result,mobile=True)}</div>'
        f'<p class="econ-counter"><b>最强替代解释：</b>{E(brief["strongest_alternative"])}</p>'
        f'<p class="econ-watch"><b>下一份披露如何推翻判断：</b>{E(brief["next_disclosure_falsifier"])}</p>'
        '<button type="button" data-export-economics>导出当前尺寸 SVG</button>'
        '<p class="econ-formula">对称拆解：收入基数贡献＝收入变化×两期毛利率均值；'
        '毛利率贡献＝毛利率变化×两期收入均值。交互项各分一半，贡献加总精确等于毛利变化。'
        '此为会计归因；价格、销量、结构、汇率与并表的独立因果贡献仍未识别。</p>'
        f'<details><summary>核对四项原始事实与可比口径</summary><p>{E(brief["comparability_evidence"])}</p>'
        '<table><thead><tr><th>期间</th><th>原始科目</th><th>人民币元</th><th>物理页</th></tr></thead>'
        f'<tbody>{rows}</tbody></table><p>显示四舍五入差：{E(result["display_rounding_yuan"])} 元。'
        '完整重大附注、多季度与同行因果验证仍待完成。</p></details></section>'+EXPORT_SCRIPT)


def render_bridge(result:dict,*,mobile:bool=False)->str:
    if result.get("schema")!="financials.symmetric_gp_bridge.v1" or result.get("interpretation")!="ACCOUNTING_DECOMPOSITION_NOT_CAUSAL":
        raise ValueError("SOURCE_BOUND_COMPARATIVE_RESULT_REQUIRED")
    start=D(result["prior_gp_yuan"]);end=D(result["current_gp_yuan"])
    effects=result["effects"]
    if [x["id"] for x in effects]!=["revenue_base","margin"]:
        raise ValueError("UNKNOWN_COMPARATIVE_DRIVER")
    changes=[(x["id"],x["label"],D(x["yuan"])) for x in effects]
    rounding=D(result["display_rounding_yuan"])
    if rounding:changes.append(("rounding","分位四舍五入差",rounding))
    if start+sum((v for _,_,v in changes),D(0))!=end:
        raise ValueError("DISPLAY_BRIDGE_NOT_CLOSED")
    rows=[("prior",result["prior"]["period"]+" 毛利",D(0),start)]
    running=start
    for key,label,delta in changes:
        rows.append((key,label,running,running+delta));running+=delta
    rows.append(("current",result["current"]["period"]+" 毛利",D(0),end))
    width=D(330 if mobile else 1040);left=D(16 if mobile else 28)
    chart_left=left if mobile else D(280);right=width-left
    lo=min([D(0)]+[min(a,b) for _,_,a,b in rows]);hi=max([D(0)]+[max(a,b) for _,_,a,b in rows])
    if hi==lo:
        # A valid break-even company can have zero GP in both periods.
        # No artificial one-yuan domain, minimum bar or undefined scale.
        height=100+55*len(rows)
        zero_rows="".join(
            f'<text x="16" y="{100+i*55}" font-size="12">{E(label)}: 0</text>'
            for i,(_,label,_,_) in enumerate(rows))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {nu(width)} {height}" '
                f'role="img" data-comparative-grammar="SYMMETRIC_GP_SIGNED_V1" '
                f'data-comparative-zero-state="NO_NONZERO_MONEY_DOMAIN" data-issuer="{E(result["issuer"])}" '
                f'data-layout="{"native-330" if mobile else "editorial-1040"}" '
                f'data-current-pdf-sha256="{E(result["current"]["pdf_sha256"])}" '
                f'data-prior-pdf-sha256="{E(result["prior"]["pdf_sha256"])}" '
                'aria-label="Zero gross profit in both periods; no nonzero money scale.">'
                '<title>两期毛利及会计贡献均为零</title>'
                '<g fill="#19333C" font-family="Noto Sans CJK SC,PingFang SC,sans-serif">'
                '<text x="16" y="30" font-size="14">两期毛利与贡献均为零</text>'
                '<text x="16" y="55" font-size="11">人民币元 · 无非零金额比例尺</text>'
                +zero_rows+'</g></svg>')
    scale=(hi-lo)/(right-chart_left)
    zero=chart_left-lo/scale
    height=D(82)+D(88 if mobile else 69)*len(rows)+D(35)
    font=12 if mobile else 16
    def text(x,y,s,fill=PALETTE["ink"],anchor="start",size=font):
        return f'<text x="{nu(x)}" y="{nu(y)}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-family="Noto Sans CJK SC,PingFang SC,sans-serif">{E(s)}</text>'
    out=[text(left,25,"毛利变化的两因素会计拆解",size=13 if mobile else 20),
         text(left,48,"人民币亿元 · 同一金额比例尺 · 非因果归因",PALETTE["muted"],size=11 if mobile else 13),
         f'<line x1="{nu(zero)}" x2="{nu(zero)}" y1="65" y2="{nu(height-25)}" stroke="{PALETTE["muted"]}" stroke-dasharray="3 4" data-zero-yuan="0"/>']
    for i,(key,label,before,after) in enumerate(rows):
        y=D(85)+D(88 if mobile else 69)*i
        delta=after-before
        color=PALETTE["trunk"] if key in ("prior","current") else PALETTE["profit"] if delta>=0 else PALETTE["cost"]
        amount=delta/D(100000000)
        prefix="+" if delta>0 and key not in ("prior","current") else ""
        out.append(text(left,y,label))
        out.append(text(right,y+D(21 if mobile else 0),f"{prefix}{amount:,.2f} 亿",color,"end"))
        bar_y=y+D(35 if mobile else 14)
        x=chart_left+(min(before,after)-lo)/scale;w=abs(delta)/scale
        out.append(f'<rect x="{nu(x)}" y="{nu(bar_y)}" width="{nu(w)}" height="15" fill="{color}" '
                   f'data-bridge-step="{E(key)}" data-before-yuan="{before}" data-after-yuan="{after}" '
                   f'data-signed-yuan="{delta}" data-scale-yuan-per-svg-unit="{scale}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {nu(width)} {nu(height)}" '
            f'role="img" data-comparative-grammar="SYMMETRIC_GP_SIGNED_V1" data-issuer="{E(result["issuer"])}" '
            f'data-layout="{"native-330" if mobile else "editorial-1040"}" '
            f'data-prior-pdf-sha256="{E(result["prior"]["pdf_sha256"])}" '
            f'data-current-pdf-sha256="{E(result["current"]["pdf_sha256"])}" '
            'aria-label="上期毛利加收入基数贡献与综合毛利率贡献等于本期毛利；这不是价格或销量因果归因。">'
            '<title>同比毛利变化：收入基数与综合毛利率的对称会计贡献</title>'+"".join(out)+'</svg>')
