"""Publish an authored source-fact dossier through shared financial grammars.

No issuer-name switches, inferred missing facts, or hardcoded reporting period.
The dossier supplies research questions and explicit exact source expressions.
"""
from pathlib import Path
from decimal import Decimal as D
from html import escape as H
import hashlib,json,re,sys
from editorial_bridge import render_bridge,render_comparison,render_balance,render_components
from source_income_adapter import render_sector_income,compile_disclosed_income
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(p.read_text())
def amount(ledger,expr):
    if isinstance(expr,str):return D(ledger['facts'][expr]['yuan'])
    if not isinstance(expr,list) or not expr:raise ValueError('EXPLICIT_FACT_EXPRESSION_REQUIRED')
    return sum((D(str(coef))*D(ledger['facts'][key]['yuan']) for key,coef in expr),D(0))
def reference(expr):return expr if isinstance(expr,str) else json.dumps(expr,separators=(',',':'),ensure_ascii=False)
def dependencies(expr):return [expr] if isinstance(expr,str) else [k for k,c in expr]
def expand_claims(story,ledger):
    """Render authored numeric placeholders directly from explicit source math."""
    def substitute(match):
        spec=story.get('quantified_claims',{}).get(match.group(1))
        if not isinstance(spec,dict):raise ValueError('DOSSIER_UNSOURCED_QUANTIFIED_CLAIM')
        value=amount(ledger,spec['expression'])
        if 'denominator' in spec:
            denominator=amount(ledger,spec['denominator'])
            if not denominator:raise ValueError('DOSSIER_UNDEFINED_CLAIM_RATIO')
            value/=denominator
        scale=D(str(spec.get('scale','1')));multiplier=D(str(spec.get('multiplier','1')))
        if not scale.is_finite() or scale<=0 or not multiplier.is_finite():raise ValueError('DOSSIER_INVALID_CLAIM_UNIT_SCALE')
        value=value/scale*multiplier
        if spec.get('absolute'):value=abs(value)
        if not value.is_finite():raise ValueError('DOSSIER_NONFINITE_QUANTIFIED_CLAIM')
        places=spec.get('decimals',2)
        if type(places) is not int or not 0<=places<=6:raise ValueError('DOSSIER_INVALID_CLAIM_PRECISION')
        return format(value,(',' if spec.get('grouping') else '')+'.'+str(places)+'f')
    def walk(value):
        if isinstance(value,str):return re.sub(r'\{\{([a-z0-9_]+)\}\}',substitute,value)
        if isinstance(value,list):return [walk(x) for x in value]
        if isinstance(value,dict):return {k:walk(v) for k,v in value.items()}
        return value
    return walk(story)
def validate(ledger,story,root=ROOT):
    expand_claims(story,ledger)
    source=ledger['source'];issuer=ledger['issuer'];path=(root/source['source_path']).resolve();path.relative_to(root.resolve())
    if not re.fullmatch(r'[0-9]{6}',issuer['code']):raise ValueError('DOSSIER_INVALID_ISSUER_CODE')
    from urllib.parse import urlsplit
    url=urlsplit(source['official_announcement'])
    if url.scheme!='https' or not url.hostname or url.username or url.password:raise ValueError('DOSSIER_SOURCE_REQUIRES_HTTPS_URL')
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=source['original_bytes_sha256'] or not data.startswith(b'%PDF'):raise ValueError('DOSSIER_ORIGINAL_PDF_BYTES_DRIFT')
    import pymupdf
    doc=pymupdf.open(path)
    identity_page=source.get('issuer_identity_page',1)
    if type(identity_page) is not int or not 1<=identity_page<=len(doc):raise ValueError('DOSSIER_ORIGINAL_PDF_IDENTITY')
    if (len(doc)!=source['physical_pages_observed']
        or issuer['code'] not in doc[identity_page-1].get_text()
        or re.sub(r'\s+','',issuer['name']) not in re.sub(r'\s+','',doc[0].get_text())):raise ValueError('DOSSIER_ORIGINAL_PDF_IDENTITY')
    cover=re.sub(r'\s+','',doc[0].get_text())
    report=re.search(r'(20[0-9]{2})年(半年度|第一季度|第三季度|年度)报告',cover)
    expected_kind={'H1':'半年度','FY':'年度','Q1':'第一季度','9M':'第三季度'}
    period=issuer['fiscal_period']
    if not report or report.group(1)!=period[:4] or expected_kind.get(period[4:])!=report.group(2):raise ValueError('DOSSIER_ORIGINAL_REPORT_PERIOD')
    for k,f in ledger['facts'].items():
        if f['type']=='flow' and f['classification']=='DISCLOSED':
            wanted=issuer['comparative_period'] if f.get('source_column')=='上期/期初' else issuer['fiscal_period']
            if f['period']!=wanted:raise ValueError('DOSSIER_FLOW_PERIOD_COLUMN_MISMATCH '+k)
        if f['scope']!='consolidated' or f['currency']!='CNY' or f['unit']!='元' or not D(f['yuan']).is_finite():raise ValueError('DOSSIER_FACT_BASIS '+k)
        if type(f['page']) is not int or not 1<=f['page']<=len(doc):raise ValueError('DOSSIER_PHYSICAL_PAGE '+k)
        if f['classification']=='DERIVED':
            d=f['derivation'];terms=d['terms']
            if d['operation']!='subtract' or len(terms)!=2 or any(ledger['facts'][t]['classification']!='DISCLOSED' or ledger['facts'][t]['period']!=f['period'] for t in terms):raise ValueError('DOSSIER_DERIVATION_REQUIRES_ORIGINAL_OPERANDS')
            if amount(ledger,terms[0])-amount(ledger,terms[1])!=D(f['yuan']):raise ValueError('DOSSIER_DERIVED_VALUE_FALSE '+k)
        elif f['classification']=='DISCLOSED':
            cells=f.get('source_cells',[])
            if not cells:raise ValueError('DOSSIER_PHYSICAL_SOURCE_CELLS_REQUIRED '+k)
            for cell in cells:
                region=doc[f['page']-1].get_textbox(pymupdf.Rect(cell['bbox'])+(-.5,-.5,.5,.5)).replace(',','')
                if cell.get('wrapped_number') is True:region=re.sub(r'\s+','',region)
                if not re.search(r'(?<![0-9.+-])'+re.escape(f['yuan'])+r'(?![0-9.])',region):raise ValueError('DOSSIER_SOURCE_CELL_FALSE '+k)
        else:raise ValueError('DOSSIER_CLASSIFICATION_UNKNOWN '+k)
    for test in story['accounting_identities']:
        if amount(ledger,test['left'])!=amount(ledger,test['right']):raise ValueError('DOSSIER_ACCOUNTING_IDENTITY '+test['name'])
    compile_disclosed_income(ledger)
    ids=[f['id'] for f in story['figures']]
    if len(ids)!=len(set(ids)) or any(not re.fullmatch('[a-z][a-z0-9-]*',i) for i in ids):raise ValueError('DOSSIER_DUPLICATE_OR_UNSAFE_FIGURE')
    return {'status':'PASS','facts':len(ledger['facts']),'accounting_identities':len(story['accounting_identities']),'pdf_sha256':source['original_bytes_sha256'],'source_cells':'EXACT_ARCHIVED_PDF_COORDINATES_NOT_HUMAN_AUDIT'}
def chart(ledger,figure,mobile):
    issuer=ledger['issuer'];kw=dict(issuer=issuer['code'],pdf_sha256=ledger['source']['original_bytes_sha256'],mobile=mobile);period=issuer['fiscal_period'];title=figure['question'];v=lambda e:amount(ledger,e);family=figure['family']
    if family=='income':return render_sector_income(ledger,mobile=mobile)
    if family=='signed_bridge':return render_bridge([(l,v(e),role,reference(e)) for l,e,role in figure['rows']],title,period=figure.get('period',period),**kw)
    if family=='comparison':return render_comparison([(l,v(p),v(n),json.dumps({'periods':figure['periods'],'prior':p,'current':n},ensure_ascii=False,separators=(',',':'))) for l,p,n in figure['pairs']],title,periods=figure['periods'],**kw)
    if family=='balance':return render_balance([(date,v(a),v(l),v(e),json.dumps({'assets':a,'liabilities':l,'equity':e},separators=(',',':'))) for date,a,l,e in figure['dates']],title,**kw)
    if family=='components':return render_components([(l,v(e),reference(e)) for l,e in figure['parts']],v(figure['total']),title,period=figure.get('period',period),**kw)
    raise ValueError('DOSSIER_UNKNOWN_FINANCIAL_GRAMMAR '+family)
def cited(figure):
    if 'facts' in figure:return figure['facts']
    expr=[]
    for l,e,role in figure.get('rows',[]):expr+=dependencies(e)
    for l,p,n in figure.get('pairs',[]):expr+=dependencies(p)+dependencies(n)
    for date,a,l,e in figure.get('dates',[]):expr += [a,l,e]
    for l,e in figure.get('parts',[]):expr+=dependencies(e)
    if 'total' in figure:expr+=dependencies(figure['total'])
    return list(dict.fromkeys(expr))
def publish(folder,out=None):
    folder=Path(folder);ledger=read(folder/'source-ledger.json');story=read(folder/'publication.json');qa=validate(ledger,story);story=expand_claims(story,ledger);issuer=ledger['issuer'];code=issuer['code'];source=ledger['source'];parts=[];briefs=[]
    for i,f in enumerate(story['figures']):
        keys=cited(f);pages=sorted({ledger['facts'][k]['page'] for k in keys})
        table=''.join('<tr><th>'+H(ledger['facts'][k]['label'])+'</th><td>'+H(ledger['facts'][k]['period'])+'</td><td class="number">'+H(ledger['facts'][k]['yuan'])+'</td><td>'+('原文披露' if ledger['facts'][k]['classification']=='DISCLOSED' else '原值计算')+'</td><td><a href="'+source['official_announcement']+'#page='+str(ledger['facts'][k]['page'])+'">原件 p.'+str(ledger['facts'][k]['page'])+'</a></td></tr>' for k in keys)
        parts.append(f'<figure id="{f["id"]}"><div class="figure-head"><span>FIGURE / {i+1:02d} · {H(f["eyebrow"])}</span><h2>{H(f["question"])}</h2><p>{H(f["takeaway"])}</p><button type="button" data-export="{f["id"]}">导出当前图 SVG ↗</button></div><div class="desktop-art">{chart(ledger,f,False)}</div><div class="native-art">{chart(ledger,f,True)}</div><figcaption><b>读图结论</b> / {H(f["analysis"])}<br><b>反证与边界</b> / {H(f["counter"])}<br><span>来源：原始披露报告 · 物理页 '+', '.join(map(str,pages))+' · 人民币原始元；图中金额适度舍入。</span></figcaption><details><summary>核对原始数据与计算口径</summary><div class="table-scroll"><table><thead><tr><th>原始项目</th><th>期间/时点</th><th>人民币元</th><th>性质</th><th>来源</th></tr></thead><tbody>'+table+'</tbody></table></div></details></figure>')
        briefs.append({'id':f['id'],'family':f['family'],'question':f['question'],'takeaway':f['takeaway'],'identity':f['identity'],'counter':f['counter'],'mobile':'桌面1040/1100与手机330独立绘制；全部金额与来源可见并可下载当前版本。','source_pages':pages,'facts':keys})
    sections=''.join('<section id="'+s['id']+'" class="essay"><div class="eyebrow">'+H(s['eyebrow'])+'</div><h2>'+H(s['title'])+'</h2>'+''.join('<p>'+H(p)+'</p>' for p in s['paragraphs'])+'</section>' for s in story['essays'])
    notes=''.join('<tr><th>'+H(n['theme'])+'</th><td>'+H(n['finding'])+'</td><td>'+H(n['boundary'])+'</td><td>'+''.join('<a href="'+source['official_announcement']+'#page='+str(p)+'">p.'+str(p)+'</a> ' for p in n['pages'])+'</td></tr>' for n in story['notes'])
    nav=''.join('<a href="#'+f['id']+'">'+H(f['nav'])+'</a>' for f in story['figures'])
    metrics=''.join('<div><span>'+H(m['label'])+'</span><strong>'+H(m['value'])+'</strong><small>'+H(m['context'])+'</small></div>' for m in story['metrics'])
    style='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f7f6f1;color:#17393d;font:16px/1.85 "Noto Sans CJK SC","PingFang SC",sans-serif}a{color:inherit}header{border-bottom:1px solid #ced8cf;padding:18px 5vw;display:flex;justify-content:space-between;font-size:12px;letter-spacing:.06em}main{max-width:1180px;margin:auto;padding:50px 28px}h1,h2{font-family:"Noto Serif CJK SC","Songti SC",serif;font-weight:550;line-height:1.4}h1{font-size:clamp(34px,4.5vw,62px);max-width:1000px;margin:22px 0}h2{font-size:30px}.eyebrow,.figure-head>span{font-size:11px;letter-spacing:.15em;font-weight:700;color:#087f68}.deck{font-size:21px;max-width:900px}.status{font-size:13px;color:#617875;max-width:950px}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;border-top:1px solid #cbd8ce;border-bottom:1px solid #cbd8ce;padding:28px 0;margin:38px 0}.metrics span,.metrics small{display:block;font-size:13px;color:#617875}.metrics strong{font-size:36px;font-weight:500}nav{display:flex;flex-wrap:wrap;gap:12px 22px;padding:0 0 35px;font-size:13px}.essay{max-width:860px;margin:55px 0}.essay p{margin:18px 0}.thesis{border-left:3px solid #087f68;padding:20px 28px;background:#eeeee6;margin:40px 0}.thesis h2{font-size:25px;margin-top:0}figure{margin:65px 0 90px;background:#fffefb;border-top:1px solid #b7cac0}.figure-head{padding:28px 30px 12px}.figure-head h2{font-size:29px;margin:12px 0}.figure-head p{max-width:930px;color:#536e6b}button{background:transparent;border:1px solid #b9cec2;color:#087f68;padding:10px 15px;font:inherit;font-size:12px;cursor:pointer}svg{display:block;width:100%;height:auto}.desktop-art{padding:12px 20px}.native-art{display:none}figcaption{padding:24px 30px;font-size:14px;border-top:1px solid #e2e7df}figcaption span{display:block;color:#647c73;font-size:12px;margin-top:12px}details{border-top:1px solid #d5dfd5;padding:16px 30px;font-size:13px}summary{cursor:pointer;color:#087f68}.table-scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;margin-top:20px;font-size:12px}th,td{border-bottom:1px solid #d8e0d5;padding:12px 10px;text-align:left;vertical-align:top}td.number{font-variant-numeric:tabular-nums;white-space:nowrap}footer{overflow-wrap:anywhere;border-top:1px solid #becfc3;margin-top:65px;padding:30px 0;color:#617875;font-size:12px}#notes table{min-width:650px}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #087f68;outline-offset:3px}@media(max-width:850px){main{padding:35px 18px}.desktop-art{display:none}.native-art{display:block;padding:20px 0}h1{font-size:36px}.deck{font-size:18px}.metrics{gap:12px}.metrics strong{font-size:25px}.metrics span,.metrics small{font-size:11px}.figure-head,figcaption,details{padding-left:16px;padding-right:16px}.figure-head h2{font-size:25px}.thesis{padding:18px}h2{font-size:27px}}'''
    scripts='''document.querySelectorAll('[data-export]').forEach(b=>b.addEventListener('click',()=>{const f=b.closest('figure'),s=[...f.querySelectorAll('svg')].find(s=>s.getBoundingClientRect().width>0);const text=new XMLSerializer().serializeToString(s),u=URL.createObjectURL(new Blob([text],{type:'image/svg+xml'})),a=document.createElement('a');a.href=u;a.download=document.body.dataset.issuer+'-'+document.body.dataset.period+'-'+b.dataset.export+'.svg';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)}));'''
    html='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+H(issuer['short']+'｜'+story['title'])+'</title><style>'+style+'</style><body data-issuer="'+code+'" data-period="'+issuer['fiscal_period']+'"><header><a href="/#companies">← 返回公司研究目录</a><span>FINANCIALS IN VISUALS</span></header><main><div class="eyebrow">'+H(issuer['short']+' / '+code+' / '+issuer['fiscal_period'])+'</div><h1>'+H(story['title'])+'</h1><p class="deck">'+H(story['deck'])+'</p><p class="status">来源限定研究 · '+H(issuer['audit'])+' · 原始披露、管理层解释和研究计算分列 · 独立人类二审尚未完成。</p><div class="metrics">'+metrics+'</div><nav aria-label="报告章节">'+nav+'<a href="#research">研究判断</a><a href="#notes">重大附注</a></nav><aside class="thesis"><h2>'+H(story['thesis']['title'])+'</h2><p>'+H(story['thesis']['body'])+'</p></aside>'+''.join(parts[:2])+sections+''.join(parts[2:])+'<section id="notes"><div class="eyebrow">SOURCE NOTES / COUNTEREVIDENCE</div><h2>重大附注：哪些事实会改变判断？</h2><p>逐项阅读范围及计算边界如下。源金额校验不等于审计意见或独立人类二审。</p><div class="table-scroll"><table><tr><th>主题</th><th>核查发现</th><th>影响与边界</th><th>原件</th></tr>'+notes+'</table></div></section><footer><a href="'+source['official_announcement']+'">完整原始报告 ↗</a><p>归档原件 SHA256：'+source['original_bytes_sha256']+'</p><p>本报告不提供未经来源支持的估值目标、价格预测、销量归因或行业认证，不构成投资建议。</p><a href="/#companies">返回同一公司研究目录</a></footer></main><script type="application/json" id="ledger-data">'+json.dumps(ledger,ensure_ascii=False).replace('</','<\\/')+'</script><script>'+scripts+'</script></body></html>'
    target=Path(out) if out else ROOT/'public'/f'{code}.html';target.parent.mkdir(exist_ok=True,parents=True);target.write_text(html)
    (folder/'figure-briefs.json').write_text(json.dumps({'issuer':code,'report':issuer['fiscal_period'],'source_sha256':source['original_bytes_sha256'],'figure_briefs':briefs},ensure_ascii=False,indent=2)+'\n')
    qa.update(html_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),figures=len(briefs));(folder/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n');print('SOURCE_DOSSIER_PUBLISHED',code,len(briefs),qa['html_sha256']);return target
if __name__=='__main__':publish(ROOT/sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None)
