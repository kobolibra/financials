"""One final editorial composition for all original-source publishers.

Inputs remain the original deterministic article and a source-bound profit-chain
bundle. Authored figure roles are explicit, validated at runtime, and portable to
new issuers. Full original vectors remain expandable; no financial fact is erased.
"""
from pathlib import Path
from html import escape as H
from decimal import Decimal as D
import hashlib,json,re
from full_profit_chain import load,amount,compile_chain
from unified_income_sankey import render_full_profit_chain
ROOT=Path(__file__).resolve().parents[2]

def figure(bundle):
 code=bundle['issuer'];pdf=bundle['source_pdf'];pages=sorted({f['page'] for f in bundle['facts'].values()});table=[]
 for stage in bundle['stages']:
  table.append('<tr><th>'+H(stage['label'])+'</th><td>'+H(str(amount(bundle,stage['terms'])))+'</td><td>合并小计；不重复累加</td></tr>')
  for a in stage['adjustments']:
   for key,c in a['terms']:
    f=bundle['facts'][key];v=D(f['yuan'])*D(str(c));table.append('<tr><td>'+H(f['label'])+'</td><td>'+H(str(v))+'</td><td>p.'+str(f['page'])+(' · 原值计算' if f.get('classification')=='DERIVED' else ' · 原文金额/统一符号')+'</td></tr>')
 drivers=[]
 operating=next(s for s in bundle['stages'] if s['id']=='operating')
 ranked=sorted(operating['adjustments'],key=lambda a:abs(amount(bundle,a['terms'])),reverse=True)
 # The author declares emphasis and trigger rationale. The main text summarises
 # the largest level components as LEVELS, never pretends these are YoY causes.
 for a in ranked[:bundle['editorial'].get('level_component_count',3)]:
  v=amount(bundle,a['terms']);drivers.append('<li><span>'+H(a['label'])+'</span><strong data-chain-level-yuan="'+str(v)+'">'+H(_money(v))+'</strong></li>')
 return '<figure id="profit-chain-overview" class="editorial-profit-chain" data-editorial-role="primary" data-editorial-need="complete-group-profit-backbone"><div class="editorial-chain-heading"><div class="editorial-kicker">THE PROFIT STORY / 完整利润主线</div><h2>'+H(bundle['editorial']['primary_question'])+'</h2><p>'+H(bundle['name']+' · '+bundle['period']+' · 合并口径；'+bundle['editorial']['income_basis'])+'。</p><button type="button" data-chain-export>导出当前利润主图 SVG ↗</button></div><div class="editorial-chain-desktop">'+render_full_profit_chain(bundle,mobile=False)+'</div><div class="editorial-chain-phone">'+render_full_profit_chain(bundle,mobile=True)+'</div><div class="editorial-components"><p>本期营业层主要金额构成 · 不等于同比因果贡献</p><ul>'+''.join(drivers)+'</ul></div><figcaption><b>读图结论</b> / '+H(bundle['editorial']['takeaway'])+'<br><b>反证与边界</b> / '+H(bundle['editorial']['counter'])+'<br>来源：<a href="'+H(bundle['source_url'],quote=True)+'">完整原始财报 ↗</a>；物理页 '+', '.join(map(str,pages))+'；人民币元逐层闭合。图示为会计形成关系，不是现金流，不分摊产品税后利润。</figcaption><details><summary>核对完整利润科目、符号与来源</summary><div class="table-scroll"><table><thead><tr><th>原始项目 / 层级</th><th>人民币元</th><th>来源及分类</th></tr></thead><tbody>'+''.join(table)+'</tbody></table></div></details></figure>'

def _money(v):
 from editorial_bridge import money
 return ('+' if v>0 else '')+money(v)

STYLE='''<style id="editorial-profit-chain-style">
.editorial-profit-chain{width:100%;max-width:1180px;margin:45px auto 70px;background:#fffefb;border-top:2px solid #239878;color:#17393d}.editorial-chain-heading{padding:24px 20px 8px}.editorial-chain-heading h2{font-size:29px;line-height:1.45;margin:12px 0}.editorial-chain-heading p{font-size:14px;line-height:1.9;color:#617875}.editorial-kicker{font-size:11px;letter-spacing:.1em;color:#087f68}.editorial-profit-chain svg{display:block;width:100%;height:auto!important;max-width:none}.editorial-chain-phone{display:none}.editorial-chain-desktop{display:block}.editorial-profit-chain button{cursor:pointer;padding:10px 14px;background:transparent;color:#087f68;border:1px solid #b7cac0;font-size:12px}.editorial-profit-chain figcaption{padding:20px;font-size:13px;line-height:1.9;border-top:1px solid #d8e0d5}.editorial-profit-chain details{padding:18px 20px}.editorial-profit-chain table{width:100%;font-size:12px;border-collapse:collapse}.editorial-profit-chain td,.editorial-profit-chain th{padding:10px;border-bottom:1px solid #d8e0d5;text-align:left}.editorial-components{padding:12px 20px 24px;border-top:1px solid #e1e7de;font-size:12px}.editorial-components>p{color:#617875}.editorial-components ul{list-style:none;margin:0;padding:0;display:flex;gap:18px;flex-wrap:wrap}.editorial-components li{flex:1;min-width:170px}.editorial-components li span,.editorial-components li strong{display:block}.editorial-components strong{font-size:21px;color:#17393d}.editorial-reconciliation{margin:55px 0 20px;padding-top:30px;border-top:1px solid #cbd8ce}.editorial-reconciliation>h2{font-size:26px}.editorial-reference{margin:18px 0;border:1px solid #d6ded4;padding:0;background:#f8f8f2}.editorial-reference>summary{padding:16px;cursor:pointer;font-size:14px;line-height:1.8;color:#087f68}.editorial-reference figure{margin:24px 0!important}.editorial-reading-card{background:#f1f3eb;border-left:3px solid #239878;margin:28px 0;padding:18px 22px;color:#17393d}.editorial-reading-card h3{font-size:22px;line-height:1.6;margin:0 0 12px}.editorial-reading-card figcaption{display:block;font-size:14px;line-height:1.9;padding:0;border:0;background:transparent}.editorial-reading-card ul{list-style:none;padding:0;font-size:14px;line-height:1.9}.editorial-reading-card li{padding:5px 0}.editorial-reading-card a{color:#087f68}.editorial-failure{border:2px solid #CD7271;padding:20px;color:#9c3636}
@media(min-width:851px){.chapter-body:has(figure.graphic){max-width:960px}}
@media(max-width:850px){.editorial-chain-desktop{display:none}.editorial-chain-phone{display:block;max-width:390px;margin:auto}.editorial-chain-heading{padding:20px 12px 6px}.editorial-chain-heading h2{font-size:25px}.editorial-profit-chain figcaption,.editorial-profit-chain details{padding:16px 12px}.editorial-components{padding:12px}.editorial-components li{min-width:130px}.editorial-components strong{font-size:19px}.editorial-reference{padding:0}.editorial-reference>summary{padding:12px}.editorial-reading-card{padding:16px}.editorial-reading-card h3{font-size:21px}}
</style>'''
SCRIPT=r'''<script id="editorial-profit-chain-runtime">
(()=>{const spec=JSON.parse(document.getElementById('editorial-profit-chain-contract').textContent);const normalized=s=>(s||'').replace(/\s+/g,'').trim();
function apply(){try{
 const originals=[...document.querySelectorAll('figure')];if(originals.length!==spec.figures.length)throw Error('EDITORIAL_ORIGINAL_FIGURE_CENSUS '+originals.length);
 for(let i=0;i<originals.length;i++){const heading=originals[i].querySelector('h2,h3');if(heading&&normalized(heading.textContent)!==normalized(spec.figures[i].title))throw Error('EDITORIAL_UNREVIEWED_QUESTION '+i);}
 const anchor=originals[0];if(!anchor)throw Error('EDITORIAL_NO_SOURCE_ARTICLE');const template=document.getElementById('editorial-profit-chain-template');const article=document.querySelector('main')||anchor.parentNode;let insertion=anchor;while(insertion.parentNode!==article&&insertion.parentNode)insertion=insertion.parentNode;article.insertBefore(template.content.cloneNode(true),insertion);
 const refs=document.createElement('section');refs.id='full-reconciliation';refs.className='editorial-reconciliation';refs.innerHTML='<h2>完整核对：原始图表与逐项对账</h2><p>正文突出关键判断；下列完整源图保留全部会计行项，可逐图展开、核对与导出。</p>';
 const main=document.querySelector('main')||anchor.parentNode;main.appendChild(refs);
 for(let i=0;i<originals.length;i++){const f=originals[i],d=spec.figures[i];f.dataset.editorialRole=d.role;f.dataset.editorialRationale=d.rationale;
 if(d.role!=='reference')continue;
 const host=document.createElement('details');host.className='editorial-reference';host.dataset.referenceIndex=i;host.id='reconcile-'+i;
 const sum=document.createElement('summary');sum.textContent='核对原始图 / '+d.title+' — '+d.rationale;host.appendChild(sum);
 if(d.summary){const card=document.createElement('section');card.className='editorial-reading-card';card.dataset.referenceIndex=i;const h=document.createElement('h3');h.textContent=d.title;card.appendChild(h);
 const caption=f.querySelector('figcaption');if(caption){const short=caption.cloneNode(true);short.querySelectorAll('table,details,[id^="table-"]').forEach(e=>e.remove());short.removeAttribute('id');short.querySelectorAll('[id]').forEach(e=>e.removeAttribute('id'));card.appendChild(short);}
 const canonical=f.querySelector('svg');const rows=canonical?[...canonical.querySelectorAll('rect[data-signed-yuan]')].filter(r=>r.getAttribute('data-kind')==='step'):[];
 const chosen=rows.filter(r=>d.focus.some(q=>(r.querySelector('title')?.textContent||'').includes(q)));
 if(chosen.length){const u=document.createElement('ul');for(const r of chosen){const li=document.createElement('li');const raw=r.getAttribute('data-signed-yuan');li.dataset.summaryYuan=raw;li.dataset.summarySource=r.getAttribute('data-source-reference')||'';li.textContent=(r.querySelector('title')?.textContent||'').split('；')[0]+'：'+(Number(raw)>=0?'+':'')+(Number(raw)/1e8).toFixed(2)+'亿元';u.appendChild(li);}card.appendChild(u);}
 const a=document.createElement('a');a.href='#'+host.id;a.textContent='展开核对全部原始项目 ↗';a.addEventListener('click',()=>{host.open=true;});card.appendChild(a);f.parentNode.insertBefore(card,f);}
 host.appendChild(f);refs.appendChild(host);}
 for(const panel of [...document.querySelectorAll('section[data-profit-formation]')]){const d=document.createElement('details');d.className='editorial-reference';d.innerHTML='<summary>核对补充签名利润桥及完整原始口径</summary>';d.appendChild(panel);refs.appendChild(d);}
 document.querySelector('[data-chain-export]').addEventListener('click',()=>{const f=document.getElementById('profit-chain-overview');const s=[...f.querySelectorAll('svg')].find(s=>s.getBoundingClientRect().width>0);if(!s)throw Error('CHAIN_VISIBLE_EXPORT_REQUIRED');const t=new XMLSerializer().serializeToString(s),u=URL.createObjectURL(new Blob([t],{type:'image/svg+xml'})),a=document.createElement('a');a.href=u;a.download=spec.issuer+'-完整利润链.svg';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);});
 document.addEventListener('click',e=>{const a=e.target.closest('a[href^="#"]');if(!a)return;const id=a.getAttribute('href').slice(1),target=document.getElementById(id);if(target){let d=target.closest('details.editorial-reference');if(d)d.open=true;}});
 const marker=document.createElement('span');marker.hidden=true;marker.id='editorial-composition-ready';marker.dataset.issuer=spec.issuer;marker.dataset.manifestSha=spec.manifest_sha;document.body.appendChild(marker);
 }catch(e){document.body.dataset.editorialFailure=String(e);const alert=document.createElement('p');alert.className='editorial-failure';alert.textContent='本页编辑层校验失败，请核对原始版本。'+e;document.body.prepend(alert);throw e;}}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',apply);else apply();})();
</script>'''

def finalize_publication(code,markup,*,period):
 if 'id="editorial-profit-chain-contract"' in markup:raise ValueError('EDITORIAL_DOUBLE_COMPOSITION')
 bundle=load(code)
 if bundle['issuer']!=code or bundle['period']!=period:raise ValueError('EDITORIAL_SOURCE_PERIOD_OR_ISSUER_MISMATCH')
 compile_chain(bundle)
 decisions=bundle['editorial']['figures'];raw=json.dumps(bundle,ensure_ascii=False,separators=(',',':'));manifest_sha=hashlib.sha256(raw.encode()).hexdigest()
 contract={'issuer':code,'manifest_sha':manifest_sha,'figures':decisions}
 payload=STYLE+'<template id="editorial-profit-chain-template">'+figure(bundle)+'</template><script type="application/json" id="editorial-profit-chain-contract">'+json.dumps(contract,ensure_ascii=False).replace('</','<\\/')+'</script><script type="application/json" id="editorial-profit-chain-data">'+raw.replace('</','<\\/')+'</script>'+SCRIPT
 if '</body>' not in markup:raise ValueError('EDITORIAL_STANDALONE_HTML_REQUIRED')
 return markup.replace('</body>',payload+'</body>')
