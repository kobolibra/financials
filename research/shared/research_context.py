"""Reader-visible independent note exceptions and source-bound temporal context."""
from pathlib import Path
import json
from html import escape as E
from decimal import Decimal as D
ROOT=Path(__file__).resolve().parents[2]
CSS='''<style>.research-context{overflow-wrap:anywhere;min-width:0;max-width:1160px;margin-left:auto;margin-right:auto;padding:28px 24px;margin:36px 0;border-top:3px solid #263f47;background:#fffefa;color:#19333c}.research-context h2{font-size:28px;line-height:1.5}.research-context h3{font-size:20px;line-height:1.5}.research-context p,.research-context li{font-size:14px;line-height:1.9}.research-context details{margin:15px 0}.research-context summary{cursor:pointer;font-weight:650;font-size:14px}.research-context .rc-scroll{overflow-x:auto}.research-context table{font-size:12px;min-width:620px;width:100%;border-collapse:collapse}.research-context td,.research-context th{padding:10px;border-bottom:1px solid #dde2db;text-align:left;vertical-align:top}.research-context .rc-exception{border-left:3px solid #cd7271;padding:12px 16px;background:#f8f0ea}.research-context code{font-size:11px;overflow-wrap:anywhere}@media(max-width:850px){.research-context{overflow-wrap:anywhere;min-width:0;max-width:1160px;margin-left:auto;margin-right:auto;padding:20px 14px}.research-context h2{font-size:25px}}</style>'''
def load(p):return json.loads((ROOT/p).read_text())
def yi(s):return f'{D(str(s))/D(100000000):,.2f}'
def validate_note_record(note):
    import re
    if not re.fullmatch('[0-9a-f]{64}',note.get('source_sha256','')):raise ValueError('NOTE_SOURCE_FINGERPRINT_REQUIRED')
    count=note.get('physical_page_count')
    if type(count) is not int or count<1:raise ValueError('NOTE_SOURCE_PAGECOUNT_REQUIRED')
    for row in note['topics']:
        if row['status'] not in ('PASS','EXCEPTION','NOT_APPLICABLE','EXTERNAL_UNRESOLVED'):raise ValueError('UNKNOWN_NOTE_REVIEW_STATUS')
        if not row['physical_pages'] or any(type(v) is not int or not 1<=v<=count for v in row['physical_pages']):raise ValueError('NOTE_PHYSICAL_PAGE_OUT_OF_BOUNDS')
        for k in ('topic','accounting_and_cash_meaning','checks_and_source_evidence','conclusion_and_limit'):
            if not isinstance(row.get(k),str) or not row[k].strip():raise ValueError('NOTE_REVIEW_MISSING_EVIDENCE '+k)
    return note

def render(issuer):
    path=ROOT/'research/quality/material-notes-review-20261110.json'
    if not path.is_file():raise ValueError('MATERIAL_NOTE_REVIEW_EVIDENCE_MISSING')
    note=load('research/quality/material-notes-review-20261110.json')['issuers'].get(issuer)
    if note is None:return ''
    validate_note_record(note)
    topics=note['topics'];exceptions=[x for x in topics if x['status'] in ('EXCEPTION','EXTERNAL_UNRESOLVED')]
    out=[CSS,f'<section id="research-context" class="research-context" data-research-context="SOURCE_NOTES_AND_HISTORY_V1" data-issuer="{E(issuer)}" data-note-pdf-sha256="{E(note["source_sha256"])}"><h2>附注穿透：哪些结论成立，哪些仍有例外？</h2>',
         '<p>独立AI二审按重大主题复核原始附注、期间、口径与会计及现金含义。以下逐项披露原始证据和限制；AI复核不等于独立人类审计签署。</p>']
    for row in exceptions:
        out.append(f'<div class="rc-exception"><h3>{E(row["topic"])}</h3><p>{E(row["checks_and_source_evidence"])}</p><p>{E(row["conclusion_and_limit"])}</p><p>原报告物理页：{E(", ".join(map(str,row["physical_pages"])))}</p></div>')
    out.append(f'<details><summary>展开{len(topics)}项重大主题的原始证据与判断</summary><div class="rc-scroll"><table><thead><tr><th>主题/物理页</th><th>会计与现金含义</th><th>原文与复算</th><th>结论及限制</th></tr></thead><tbody>')
    for row in topics:
        out.append(f'<tr><td>{E(row["topic"])}<br>p.{E(", ".join(map(str,row["physical_pages"])))}</td><td>{E(row["accounting_and_cash_meaning"])}</td><td>{E(row["checks_and_source_evidence"])}</td><td>{E(row["conclusion_and_limit"])}</td></tr>')
    out.append('</tbody></table></div></details>')
    hist=ROOT/'research/quality/historical-peer-evidence/quarterly-panel.json'
    if hist.is_file():
        panel=load('research/quality/historical-peer-evidence/quarterly-panel.json');rows=[r for r in panel['rows'] if r['issuer']==issuer]
        if rows:
            out.extend(['<h2>连续季度检验：收入、毛利与现金是否同向？</h2>','<p>单位：亿元。单季度金额由原报告累计值差分；每项操作数保留原PDF指纹、物理页及金额。跨版本重述不自动当作可比增长，不能把季节性或会计归因视为因果。</p><div class="rc-scroll"><table><thead><tr><th>单季度</th><th>收入</th><th>毛利</th><th>研发费用</th><th>经营现金流</th></tr></thead><tbody>'])
            for r in rows:
                f=r['facts'];out.append(f'<tr data-period="{E(r["quarter"])}"><td>{E(r["quarter"])}</td><td>{yi(f["revenue"]["value"])}</td><td>{yi(D(f["revenue"]["value"])-D(f["cost"]["value"]))}</td><td>{yi(f["rd_expense"]["value"])}</td><td>{yi(f["cfo"]["value"])}</td></tr>')
            out.append('</tbody></table></div><details><summary>逐项核对季度差分的原始操作数</summary>')
            for r in rows:
                for key,f in r['facts'].items():
                    refs='；'.join(f'{v["id"]} p.{v["page"]}：{v["operand"]}元；PDF {v["sha256"]}' for v in f['sources'])
                    out.append(f'<p><b>{E(r["quarter"])} / {E({"revenue":"收入","cost":"营业成本","rd_expense":"研发费用","cfo":"经营现金流"}.get(key,key))}</b>：{E(f["formula"])} = {E(f["value"])}元<br><code>{E(refs)}</code></p>')
            out.append('</details>')
    conclusions=ROOT/'research/quality/historical-peer-evidence/reader-conclusions.json'
    if conclusions.is_file():
        c=load('research/quality/historical-peer-evidence/reader-conclusions.json')['issuers'].get(issuer)
        if c:
            out.append('<h2>最新三季报：半年报判断是否经得住后续披露？</h2>')
            for key,label in [('thesis_update','判断更新'),('q3_test','单季度与累计检验'),('strongest_alternative','仍需排除的解释'),('peer_implication','同行证据的启示与边界'),('restatement_limit','重述与可比限制')]:
                out.append(f'<h3>{label}</h3><p>{E(c[key])}</p>')
            out.append('<details><summary>展开三季报核验所用原始证据</summary>')
            for page in c.get('source_pages',[]):out.append(f'<p>{E(page["id"])}，物理页 {E(", ".join(map(str,page["physical_pages"])))}；PDF指纹 <code>{E(page["sha256"])}</code></p>')
            out.append('</details>')
    peers=ROOT/'research/quality/historical-peer-evidence/peer-comparison.json'
    if peers.is_file():
        for peer in load('research/quality/historical-peer-evidence/peer-comparison.json')['peers']:
            if peer['target']!=issuer:continue
            f=peer['facts'];r0,r1=map(D,f['revenue']['values']);c0,c1=map(D,f['cost']['values'])
            out.append(f'<h3>同业参照：{E({"600025":"华能水电","600196":"复星医药","688099":"晶晨股份"}.get(peer["peer"],peer["peer"]))}，2026H1与2025H1</h3><p>{E(peer["comparability"])}</p><p>同业收入{yi(r0)} / {yi(r1)}亿元；毛利率{(r0-c0)/r0*100:.2f}% / {(r1-c1)/r1*100:.2f}%。本组仅作口径明确的背景比较，不作企业优劣排名。</p>')
            out.append(f'<p>来源PDF <code>{E(peer["sha256"])}</code>；收入物理p.{f["revenue"]["physical_page"]}、成本物理p.{f["cost"]["physical_page"]}。</p>')
    out.append('</section>');return ''.join(out)
