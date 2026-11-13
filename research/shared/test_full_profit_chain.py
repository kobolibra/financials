"""Original14 filings, independent geometry poisons, unseen lawful profit chains."""
import copy,json,re,unittest
from decimal import Decimal as D
from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as ET
from full_profit_chain import compile_chain,render,load,ROOT
from profit_chain_audit import validate_source,check_svg
NS='{http://www.w3.org/2000/svg}'
class FullProfitChainTests(unittest.TestCase):
 def test_all14_original_source_cells_and_both_actual_vectors(self):
  codes=[r['code'] for r in json.loads((ROOT/'site/research_catalog.json').read_text())['issuers']]
  self.assertTrue({'300394','300308','300502','600036','688111','600519','000333','688220','600900','600276','601628','600690','300548','300570'}.issubset(codes))
  for code in codes:
   b=load(code)
   with self.subTest(code=code):
    self.assertEqual(validate_source(b)['status'],'PASS')
    for mobile in (False,True):self.assertEqual(check_svg(render(b,mobile=mobile),code,b['source_pdf']['source_sha256'])['status'],'PASS')
 def test_new_period_cannot_borrow_old_issuer_manifest(self):
  from publication_editorial import finalize_publication
  with self.assertRaisesRegex(ValueError,'EDITORIAL_SOURCE_PERIOD_OR_ISSUER_MISMATCH'):
   finalize_publication('300394','<html><body></body></html>',period='2030H1')
 def test_geometry_poison_nodes_ribbon_controls_and_source_terms_rejected(self):
  b=load('688111');raw=render(b)
  for what in ('node','path','terms','sha','period'):
   tree=ET.fromstring(raw)
   if what=='node':r=next(r for r in tree.iter(NS+'rect') if r.get('data-chain-node')=='net');r.set('height',str(D(r.get('height'))+1))
   if what=='path':
    r=next(tree.iter(NS+'path'));r.set('d',re.sub(r'C([0-9.]+)',lambda m:'C'+str(D(m[1])+1),r.get('d'),count=1))
   if what=='terms':next(tree.iter(NS+'rect')).set('data-chain-terms','[["FAKE",1]]')
   if what=='sha':tree.set('data-original-pdf-sha256','0'*64)
   if what=='period':tree.set('data-period','2027H1')
   with self.subTest(what=what),self.assertRaises(ValueError):check_svg(ET.tostring(tree,encoding='unicode'),'688111',b['source_pdf']['source_sha256'])
 def test_source_column_sign_period_derivation_and_unit_poison_rejected(self):
  original=load('300570')
  key=next(k for k,f in original['facts'].items() if f.get('source_cells'))
  for what in ('cell','sign','period','unit','derived'):
   b=copy.deepcopy(original);f=b['facts'][key]
   if what=='cell':f['source_cells'][0]['bbox']=[0,0,1,1]
   if what=='sign':f['source_cells'][0]['original_number']=str(-D(f['source_cells'][0]['original_number']))
   if what=='period':f['period']='2025H1'
   if what=='unit':f['source_cells'][0]['unit_scale']='1000'
   if what=='derived':f['classification']='DERIVED';f['terms']=[[key,1]]
   with self.subTest(what=what),self.assertRaises(ValueError):validate_source(b)
 def test_additional_gains_do_not_inflate_reported_checkpoint(self):
  b=load('688111');p=compile_chain(b);nodes={n['id']:n for n in p['nodes']}
  self.assertGreater(nodes['pool-operating']['value'],nodes['gross']['value'])
  self.assertEqual(nodes['gross']['value'],sum(D(b['facts'][k]['yuan'])*D(c) for k,c in b['stages'][1]['terms']))
 def test_bank_insurer_use_statutory_basis_without_industrial_gp(self):
  for code in ('600036','601628'):
   b=load(code);p=compile_chain(b)
   self.assertNotIn('gross',[n['id'] for n in p['mains']]);self.assertEqual(p['mains'][-1]['id'],'parent')
  self.assertNotIn('536634',str(load('601628')['sources']))
 def test_unseen_synthetic_tax_refunds_nci_losses_zero_edges_and_other_periods(self):
  # Synthetic mechanism tests do not certify an unseen original filing.
  for i in range(60):
   b={'issuer':'unseen-'+str(i),'period':str(2027+i%4)+'H1','scope':'consolidated','currency':'CNY','unit':'元','source_pdf':{'source_sha256':'1'*64},'facts':{},'sources':[],'stages':[]}
   def fact(k,v):b['facts'][k]={'yuan':str(v),'period':b['period']};return [[k,1]]
   factor=D(i+1);prev=100*factor
   b['sources']=[{'label':'真实分类A','terms':fact('a',60*factor)},{'label':'真实分类B','terms':fact('b',40*factor)}]
   b['stages']=[{'id':'revenue','label':'收入','terms':fact('r',prev),'adjustments':[]}]
   for j,(id,delta) in enumerate([('gross',-40),('operating',-5),('pretax',1),('net',2 if i%2 else -6),('parent',3 if i%3 else -4)]):
    adjustment=fact('d'+id,D(delta)*factor);prev+=D(delta)*factor
    b['stages'].append({'id':id,'label':id,'terms':fact(id,prev),'adjustments':[{'label':id,'terms':adjustment}]})
   if i%5==0:
    # A true zero component carries no invented minimum-width ribbon.
    b['sources'].append({'label':'零业务','terms':fact('zero',0)})
   with patch('profit_chain_audit.bundle_for',return_value=b):
    for mobile in (False,True):self.assertEqual(check_svg(render(b,mobile=mobile),b['issuer'],'1'*64)['status'],'PASS')
 def test_negative_subtotal_missing_endpoint_mixed_scope_and_zero_domain_fail_closed(self):
  b=load('300570')
  for mode in ('negative','missing','scope','period'):
   x=copy.deepcopy(b)
   if mode=='negative':x['facts'][x['stages'][-1]['terms'][0][0]]['yuan']='-1'
   if mode=='missing':x['stages'].pop()
   if mode=='scope':x['scope']='parent'
   if mode=='period':x['facts'][x['stages'][0]['terms'][0][0]]['period']='2025H1'
   with self.subTest(mode=mode),self.assertRaises(ValueError):compile_chain(x)
 def test_compact_change_groups_cannot_drop_or_repeat_original_rows(self):
  from source_publication import presentation_rows
  for code in ('300570','600690'):
   story=json.loads((ROOT/'research/issuers'/code/'publication.json').read_text());f=next(x for x in story['figures'] if x.get('editorial_groups'))
   self.assertLess(len(presentation_rows(f)),len(f['rows']))
   for mutation in ('drop','repeat'):
    bad=copy.deepcopy(f)
    if mutation=='drop':bad['editorial_groups'][0]['indices'].pop()
    else:bad['editorial_groups'][0]['indices'].append(bad['editorial_groups'][0]['indices'][0])
    with self.assertRaises(ValueError):presentation_rows(bad)
if __name__=='__main__':unittest.main()
