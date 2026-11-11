from pathlib import Path
import json,pymupdf,hashlib
B=Path(__file__).resolve().parent
idx={r['id']:r for r in json.loads((B/'statement-facts.json').read_text())}
peers=[]
for target,peer,why in [('600900','600025','长江梯级水电对比澜沧江水电及新能源；地域来水、电价、机组投产/折旧、海外收入与合并范围不同，集团毛利率不得简单排名'),('600276','600196','恒瑞药品销售及许可对比复星制药、器械诊断、医疗服务混合集团；复星创新药口径含生物类似药等，许可收入、投资收益及研发资本化口径须分开，不按集团毛利率评药品竞争力'),('688220','688099','无晶圆芯片设计共性；翱捷蜂窝通信/ASIC定制，对比晶晨电视/多媒体SoC和连接芯片，产品周期、客户、设计服务、美元敞口与存货不同，毛利/CFO不同不识别售价或竞争力因果')]:
 a=idx[peer+'_2026H1'];peers.append(dict(target=target,peer=peer,periods=['2026H1','2025H1'],scope='consolidated',unit='CNY yuan',facts=a['facts'],sha256=a['sha256'],comparability=why))
# Direct note values, not development-asset stock changes.
notes=[
 ('600025_2026H1',170,'capitalized_rd',['71902.65',None],'2025 comparative cell blank; total equals expensed amount, zero is an inference rather than a printed zero'),
 ('600025_2026H1',170,'total_rd',['7644409.72','23150531.05'],'合计研发支出'),
 ('600196_2026H1',174,'capitalized_rd',['1159896194.49','867234864.06'],'财务附注直接披露资本化研发支出，优先使用元额而非MD&A四舍五入亿元'),
 ('600196_2026H1',174,'total_rd',['3246821510.71','2583897109.08'],'合计研发支出'),
 ('600276_2026H1',157,'capitalized_rd',['1112206487.83','643223722.37'],'直接披露资本化研发支出；不等于内部开发毛增加1143485781.64，后者包括随后转费用31279293.81'),
 ('600276_2026H1',157,'total_rd',['4605118095.21','3871157204.47'],'合计研发支出'),
 ('688099_2026H1',19,'capitalized_rd',[None,None],'资本化投入行空白；费用化=合计，支持无当期资本化但不伪造字面0；万元单位'),
 ('688220_2026H1',31,'capitalized_rd_ratio',['0','0'],'报告直接列资本化占比0，元额资本化投入行空白'),
 ('600900_2026H1',165,'internal_development_gross_additions',['328588864.64',None],'本期内部开发增加；同时转当期损益327570293.83，确认为无形资产4623678.49；不能把增加毛额当作扣除费用后的资本化研发投入')]
out=[]
for sid,page,metric,values,note in notes:
 p=B/(sid+'.pdf');d=pymupdf.open(p);s=d[page-1].get_text().replace(',','')
 for value in values:
  if value and value!='0':assert value in s,(sid,page,value)
 out.append(dict(source=sid,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),physical_page=page,metric=metric,values=values,note=note))
(B/'peer-comparison.json').write_text(json.dumps(dict(peers=peers,research_notes=out,status='original PDF selected facts verified; sector/note audit partial; independent HUMAN review NOT_CHECKED'),ensure_ascii=False,indent=2))
manifest={}
for p in B.glob('*_source.json'):
 r=json.loads(p.read_text());manifest[r['id']]=r
for r in json.loads((B/'manifest.json').read_text()):manifest[r['id']]=r
(B/'all-source-manifest.json').write_text(json.dumps(sorted(manifest.values(),key=lambda r:r['id']),ensure_ascii=False,indent=2))
print('PASS',len(manifest),'PDF source records;',len(out),'note rows;',len(peers),'peer comparisons')
