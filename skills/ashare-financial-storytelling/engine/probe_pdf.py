#!/usr/bin/env python3
"""A-share PDF -> document inventory and unapproved, page-anchored evidence candidates.

Never equate a lexical match with an accounting-approved financial fact.
This is a generic, source-verifiable intake tool for any searchable PDF; scanned pages
are flagged for manual/OCR review. No remote services, no LLM, no market data.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
import fitz

KEYWORDS = {
 'revenue':['其中：营业收入','营业收入'],
 'cogs':['其中：营业成本','营业成本'],
 'net_profit':['五、净利润','净利润'],
 'parent_profit':['归属于母公司股东的净利润','归属于上市公司股东的净利润'],
 'cfo':['经营活动产生的现金流量净额'],
 'cash_flow_investing':['投资活动产生的现金流量净额'],
 'cash_flow_financing':['筹资活动产生的现金流量净额'],
 'assets':['资产总计','总资产'],
 'liabilities':['负债合计','负债总计'],
 'equity':['所有者权益合计','股东权益合计'],
 'inventory':['存货'],
 'accounts_receivable':['应收账款'],
 'r_and_d':['研发费用','研发投入'],
 'capex':['购建固定资产','其他长期资产支付的现金'],
}
NUM = re.compile(r'(?<![\w])[-−－]?(?:\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d{1,4})?(?!\w)')
CURRENCY = re.compile(r'\d[\d,]*\.\d{2}')

def page_index(pdf:Path, max_rows:int=12):
    document=fitz.open(str(pdf)); sha=hashlib.sha256(pdf.read_bytes()).hexdigest()
    pages=[]; inventory={name:[] for name in KEYWORDS}
    page_notes=[]
    for no,page in enumerate(document,1):
        text=page.get_text('text',sort=True)
        lines=[re.sub(r'\s+',' ',s).strip() for s in text.splitlines() if s.strip()]
        # Scan ordinary textual lines and next 6 lines to survive multi-line CAS rows.
        for i,line in enumerate(lines):
            for key, labels in KEYWORDS.items():
                if not any(label in line for label in labels):continue
                following=' | '.join(lines[i:i+7])
                # capture exact tokens with 2 decimals; non-CNY amounts need later unit review
                nums=CURRENCY.findall(following)
                if not nums:continue
                structural = ('合并' in text[:600] and ('资产负债表' in text[:600] or '利润表' in text[:600] or '现金流量表' in text[:600]))
                score=min(3,2 if structural else 1) + int('单位：元' in text or '单位:元' in text)
                inventory[key].append({
                  'pdf_page':no,'reported_page':find_printed_page(lines,no),
                  'line_label':line[:115], 'nearby_original_text':following[:330],
                  'possible_amounts':nums[:6], 'candidate_score':score,
                  'approval':'UNREVIEWED',
                  'warning':'May contain next-row values, prior-year column, different unit/scope or ordinary discussion text; review page image.'
                })
        word_count=len(page.get_text('words'))
        if word_count<15: page_notes.append({'pdf_page':no,'status':'IMAGE_OR_NEAR_EMPTY','word_count':word_count})
        pages.append({'pdf_page':no,'printed_page':find_printed_page(lines,no),'chars':len(text),'words':word_count,
          'potential_chapters':[s[:65] for s in lines if re.search('合并资产负债表|合并利润表|合并现金流量表|经营情况讨论|财务报表附注|主要业务|公司主要',s)][:5]})
    document.close()
    return {'schema':'financials-pdf-intake-v1','file':pdf.name,'sha256':sha,'page_count':len(pages),
      'language_hint':'Chinese filing; verify original report language','pages':pages,'low_text_pages':page_notes,
      'candidate_fields':{k:sorted(v,key=lambda x:(-x['candidate_score'],x['pdf_page']))[:max_rows] for k,v in inventory.items()},
      'status':'SOURCE_CANDIDATES_ONLY_NOT_APPROVED','publishing_allowed':False,
      'instructions':'Select source images and original table cells, identify consolidation & column/period, normalize yuan, then sign off evidence ledger; no automatic candidate is a verified fact.'}

def find_printed_page(lines,default):
    for s in lines[:5]:
        if s.isdigit() and 1 <= int(s) <= 10000:return int(s)
    return None

def main():
    p=argparse.ArgumentParser();p.add_argument('pdf');p.add_argument('--out',required=True);p.add_argument('--max-candidates',type=int,default=12)
    a=p.parse_args();result=page_index(Path(a.pdf),a.max_candidates)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'pages':result['page_count'],'sha256':result['sha256'],'candidate_fields':{k:len(v) for k,v in result['candidate_fields'].items()},'needs_manual_approval':True},ensure_ascii=False))
if __name__=='__main__':main()