"""Profit-chain layout V2: adaptive spacing and independently audited margin / growth annotations.

Real source: the 300394 first-quarter report and its prior-year comparative cells. Published
reports moved to INCOME_FLOW_V3 (test_income_flow_v3.py); V2 stays a supported opt-in layout, so
these tests pin the manifest read by the auditor to V2 on the same source bundle.
"""
from pathlib import Path
import copy,re,sys,unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parent))
from full_profit_chain import render,load
import profit_chain_audit
from profit_chain_audit import validate_source,check_svg
def bundle_for(key):
 b=copy.deepcopy(_real(key));b['editorial']['layout']='PROFIT_CHAIN_LAYOUT_V2';return b
_real=profit_chain_audit.bundle_for
KEY='300394@2026Q1'
class LayoutV2(unittest.TestCase):
 def setUp(self):
  p=mock.patch.object(profit_chain_audit,'bundle_for',bundle_for);p.start();self.addCleanup(p.stop)
  self.b=bundle_for(KEY);self.sha=self.b['source_pdf']['source_sha256']
 def test_both_editions_pass_the_independent_audit_with_every_annotation_recomputed(self):
  self.assertEqual(self.b['editorial']['layout'],'PROFIT_CHAIN_LAYOUT_V2');validate_source(self.b)
  for mobile in (False,True):
   svg=render(self.b,mobile=mobile);self.assertIn('data-chain-layout="PROFIT_CHAIN_LAYOUT_V2"',svg)
   self.assertEqual(check_svg(svg,KEY,self.sha)['actual_path_geometry'],'PASS')
   self.assertIn('毛利率 56.6%（+3.6pp）',svg);self.assertIn('同比 +40.8%',svg)
 def test_a_tampered_annotation_or_prior_amount_is_caught(self):
  svg=render(self.b,mobile=False)
  with self.assertRaisesRegex(ValueError,'ANNOTATION_TEXT'):check_svg(svg.replace('毛利率 56.6%','毛利率 66.6%',1),KEY,self.sha)
  with self.assertRaisesRegex(ValueError,'PRIOR_NODE_AMOUNT'):check_svg(re.sub(r'data-chain-prior-yuan="[0-9.]+"','data-chain-prior-yuan="1.00"',svg,count=1),KEY,self.sha)
 def test_falsified_prior_period_source_cell_fails_source_validation(self):
  bad=copy.deepcopy(self.b);bad['comparatives']['facts']['rev_prior']['yuan']='3918403111.98'
  with self.assertRaises(ValueError):validate_source(bad)
 def test_layout_v2_without_prior_period_cells_is_refused_and_v1_layout_is_unchanged(self):
  bad=copy.deepcopy(self.b);del bad['comparatives']
  with self.assertRaisesRegex(ValueError,'REQUIRES_PRIOR_PERIOD'):render(bad)
  v1=copy.deepcopy(self.b);del v1['comparatives'];v1['editorial'].pop('layout')
  svg=render(v1);self.assertNotIn('data-chain-layout',svg);self.assertNotIn('同比 ',svg)
 def test_adaptive_spacing_gives_near_duplicate_layers_less_room_than_big_steps(self):
  svg=render(self.b,mobile=False)
  nodes={k:v for v,k in [(m.group(1),m.group(2)) for m in re.finditer(r'<rect x="([0-9.]+)"[^>]*data-chain-node="([a-z]+)"',svg)]}
  xs=[float(nodes[k]) for k in ('revenue','gross','operating','pretax','net','parent')]
  gaps=[b-a for a,b in zip(xs,xs[1:])]
  self.assertGreater(gaps[0],gaps[2]);self.assertGreaterEqual(min(gaps),99.9)
if __name__=='__main__':unittest.main()
