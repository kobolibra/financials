"""Parallel orchestration must preserve every case and exact evidence bytes."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from qa_editorial_migration import audit
class ParallelEvidenceTests(unittest.TestCase):
 def worker(self,codes,out,origin=None):
  out.mkdir(parents=True,exist_ok=True);result={'status':'PASS_LOCAL','origin':origin or 'LOCAL_FILE_SOURCE','issuers':{c:{'complete_figure_migration':'PASS_LOCAL'} for c in codes},'cases':[]}
  for c in codes:
   for w in (1440,768,390):
    name=f'{c}-{w}.svg';(out/name).write_text(c+str(w));result['cases'].append({'issuer':c,'width':w,'figures':[{'export_file':name}]})
  return result
 def test_every_case_and_actual_file_is_preserved(self):
  with tempfile.TemporaryDirectory() as d,patch('qa_editorial_migration._audit_sequential',side_effect=self.worker):
   q=audit(['a','b','c','d','e'],Path(d));self.assertEqual(len(q['cases']),15);self.assertEqual(q['svg_exports'],15)
   self.assertEqual(q['execution_workers'],3)
   for c in q['cases']:self.assertEqual((Path(d)/c['figures'][0]['export_file']).read_text(),c['issuer']+str(c['width']))
 def test_missing_or_duplicate_viewport_is_rejected(self):
  def poison(codes,out,origin=None):
   q=self.worker(codes,out,origin);q['cases'][0]['width']=768;return q
  with tempfile.TemporaryDirectory() as d,patch('qa_editorial_migration._audit_sequential',side_effect=poison),self.assertRaisesRegex(ValueError,'INCOMPLETE_PARALLEL_RESULT'):audit(['a','b','c','d'],Path(d))
 def test_worker_error_cannot_leave_a_pass_receipt(self):
  with tempfile.TemporaryDirectory() as d:
   (Path(d)/'result.json').write_text('STALE_PREVIOUS_PASS')
   with patch('qa_editorial_migration._audit_sequential',side_effect=ValueError('REAL_RENDER_FAILED')),self.assertRaises(ValueError):audit(['a','b','c','d'],Path(d))
   self.assertFalse((Path(d)/'result.json').exists())
 def test_duplicate_issuer_rejected(self):
  with tempfile.TemporaryDirectory() as d,self.assertRaisesRegex(ValueError,'DUPLICATE_ISSUER'):audit(['a','a'],Path(d))
if __name__=='__main__':unittest.main()
