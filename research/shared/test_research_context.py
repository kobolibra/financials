import copy,json,unittest
from research_context import ROOT,render,validate_note_record
class ResearchContextTests(unittest.TestCase):
 def test_current_note_reviews_have_bound_pages_and_visible_exceptions(self):
  d=json.loads((ROOT/'research/quality/material-notes-review-20261110.json').read_text())
  for code,note in d['issuers'].items():
   with self.subTest(code=code):
    validate_note_record(note);html=render(code)
    self.assertIn(note['source_sha256'],html)
    for row in note['topics']:
     if row['status'] in ('EXCEPTION','EXTERNAL_UNRESOLVED'):
      self.assertIn(row['topic'],html)
 def test_broken_source_or_missing_evidence_cannot_be_rendered(self):
  note=json.loads((ROOT/'research/quality/material-notes-review-20261110.json').read_text())['issuers']['688220']
  for field,value in [('source_sha256','fake'),('physical_page_count',True)]:
   bad=copy.deepcopy(note);bad[field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):validate_note_record(bad)
  for field,value in [('physical_pages',[True]),('physical_pages',[99999]),('conclusion_and_limit','')]:
   bad=copy.deepcopy(note);bad['topics'][0][field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):validate_note_record(bad)
if __name__=='__main__':unittest.main()
