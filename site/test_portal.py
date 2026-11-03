from pathlib import Path
from html.parser import HTMLParser
import unittest,json,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent/'public'
class Parser(HTMLParser):
 def __init__(self): super().__init__();self.links=[];self.company=[];self.filters=[];self.ids=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='a':self.links.append(d.get('href',''));self.company.extend([d.get('href')] if 'company' in d.get('class','').split() else [])
  if t=='button' and 'filter' in d.get('class','').split():self.filters.append(d.get('data-filter'))
  if 'id' in d:self.ids.append(d['id'])
class Tests(unittest.TestCase):
 def setUp(self):
  self.s=(ROOT/'index.html').read_text();self.data=json.loads((HERE/'research_catalog.json').read_text());self.p=Parser();self.p.feed(self.s)
 def test_catalogue_unique_company_routes(self):
  self.assertGreaterEqual(len(self.data['issuers']),7)
  self.assertEqual(len(self.data['issuers']),self.data['published_issuer_count'])
  self.assertEqual(len(self.p.company),len(self.data['issuers']))
  self.assertEqual(set(self.p.company),set(x['href'] for x in self.data['issuers']))
 def test_original_three_not_suppressed(self):
  self.assertEqual(set(self.p.company)&{'/300394.html','/300308.html','/300502.html'}, {'/300394.html','/300308.html','/300502.html'})
 def test_new_four_in_same_list(self):
  for k in ['600036','688111','600519','000333']:self.assertTrue(any(k in path for path in self.p.company))
 def test_comparative_is_topic_not_company(self):
  self.assertIn('/optical-2026h1.html',self.p.links)
  self.assertNotIn('/optical-2026h1.html',self.p.company)
 def test_old_four_not_featured(self):
  self.assertNotIn('./research/2026-h1-v10/index.html',self.p.links)
  self.assertNotIn('/research/2026-h1-v10/index.html',self.p.company)
 def test_one_primary_catalogue(self):
  self.assertIn('companies',self.p.ids)
  self.assertEqual(set(self.p.filters),{'all',*(x['industry'] for x in self.data['issuers'])})
  self.assertEqual(len(set(self.p.ids)),len(self.p.ids))
 def test_input_is_not_hardcoded_to_builder_source(self):
  for v in self.data['issuers']:
   self.assertTrue(v['name'] in self.s and v['code'] in self.s)
 def test_no_external_assets_or_iframe(self):
  self.assertNotIn('<iframe',self.s.lower())
  self.assertNotIn('<script src=',self.s.lower())
 def test_synthetic_next_issuer_in_same_home(self):
  with tempfile.TemporaryDirectory() as tmp:
   folder=Path(tmp)/'site';folder.mkdir()
   (folder/'portal_builder.py').write_text((HERE/'portal_builder.py').read_text())
   sample=dict(self.data['issuers'][0])
   sample.update(code='999999',name='验收模拟公司',exchange='SH',industry='新能源',
                 sub='行业拓展回归测试',href='/research/999999.html',
                 story='模拟公司仅用于目录泛化测试',deck='不属于实际财务研究',
                 period='2026Q3',rank=len(self.data['issuers'])+1,signal='NOT_CHECKED',signal_label='来源门槛',spark=None)
   catalog=dict(self.data)
   catalog['issuers']=[*self.data['issuers'],sample]
   catalog['published_issuer_count']=len(catalog['issuers'])
   (folder/'research_catalog.json').write_text(json.dumps(catalog,ensure_ascii=False))
   out=Path(tmp)/'built'
   subprocess.run([sys.executable,str(folder/'portal_builder.py'),'--out',str(out)],check=True,capture_output=True)
   page=(out/'index.html').read_text()
   parsed=Parser();parsed.feed(page)
   self.assertEqual(len(parsed.company),len(self.data['issuers'])+1)
   self.assertIn('/research/999999.html',parsed.company)
   self.assertIn('新能源',parsed.filters)
   self.assertIn('全部 '+str(len(self.data['issuers'])+1),page)
   self.assertIn('显示 '+str(len(self.data['issuers'])+1)+' / '+str(len(self.data['issuers'])+1)+' 家公司',page)
   self.assertIn('2026Q3',page)
   self.assertIn('/optical-2026h1.html',parsed.links)
   for route in self.p.company:self.assertIn(route,parsed.company)
 def test_clean_generator_matches_html(self):
  with tempfile.TemporaryDirectory() as tmp:
   subprocess.run([sys.executable,str(HERE/'portal_builder.py'),'--out',tmp],check=True,capture_output=True)
   self.assertEqual((Path(tmp)/'index.html').read_bytes(),(ROOT/'index.html').read_bytes())
if __name__=='__main__':unittest.main()