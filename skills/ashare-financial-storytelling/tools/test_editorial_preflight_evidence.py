"""New V2 editorial preflight must recheck *current* source evidence and capability.

Legacy published reports remain explicitly NOT_CHECKED, never silently marked
machine-approved. Strict mode is mandatory when promoting a new V2 report.
"""
import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fin_intake as fi  # noqa: E402
import research_capabilities as rc  # noqa: E402
import research_evidence as ev  # noqa: E402
from test_research_evidence import ledger, brief  # noqa: E402

sys.path.insert(0, str(fi.ROOT / 'research' / 'shared'))
import source_publication as sp  # noqa: E402


class EditorialPreflightEvidence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.ledger = ledger()
        self.brief = brief()
        self.manifest = self.base / 'editorial.json'
        self.manifest.write_text(json.dumps({'editorial': {'figures': [{'id': 'f', 'role': 'primary'}]}}))
        (self.base / 'source-ledger.json').write_text(json.dumps(self.ledger))
        self.brief_path = self.base / 'research-brief.json'
        self.brief_path.write_text(json.dumps(self.brief, ensure_ascii=False))
        self.story = {'design': 'EDITORIAL_V2', 'figures': [{'id': 'f'}]}
        self.write_receipt()

    def write_receipt(self):
        review = ev.validate(self.ledger, self.brief)
        self.story['capability_plan'] = rc.assess(self.ledger)
        self.story['research_evidence_gate'] = {
            'status': review['status'],
            'brief_sha256': hashlib.sha256(self.brief_path.read_bytes()).hexdigest(),
            'source_pdf_sha256': review['source_pdf_sha256'],
            'professional_causal_inference': review['professional_causal_inference'],
            'independent_financial_reviewer': review['independent_financial_reviewer'],
            'independent_visual_editor': review['independent_visual_editor'],
            'release_authorization': review['release_authorization'],
        }

    def run_preflight(self, strict=True):
        (self.base / 'publication.json').write_text(json.dumps(self.story, ensure_ascii=False))
        stdout = io.StringIO()
        with (patch.object(fi, 'folder', return_value=self.base),
              patch.object(fi, 'editorial_path', return_value=self.manifest),
              patch.object(fi, 'lint', return_value=[]),
              patch.object(sp, 'validate', return_value={'status': 'PASS'}),
              patch.object(sp, 'expand_claims', side_effect=lambda story, book: story),
              contextlib.redirect_stdout(stdout),
              self.assertRaises(SystemExit) as outcome):
            fi.cmd_preflight(SimpleNamespace(code='999999', period=None,
                                             require_research_evidence=strict))
        return outcome.exception.code, stdout.getvalue()

    def test_strict_preflight_passes_a_current_ledger_bound_receipt(self):
        code, out = self.run_preflight()
        self.assertEqual(code, 0, out)
        self.assertIn('PASS_MACHINE_PROOF_ONLY_HUMAN_NOT_CHECKED', out)
        self.assertIn('PREFLIGHT_PASS', out)

    def test_changed_brief_or_original_accounting_data_invalidates_the_receipt(self):
        for mutation in ('brief-byte-change', 'ledger-source-change', 'stale-plan'):
            with self.subTest(mutation=mutation):
                self.setUp()
                if mutation == 'brief-byte-change':
                    self.brief_path.write_text(self.brief_path.read_text() + '\n')
                elif mutation == 'ledger-source-change':
                    altered = json.loads((self.base / 'source-ledger.json').read_text())
                    altered['facts']['cfo']['yuan'] = '95'
                    (self.base / 'source-ledger.json').write_text(json.dumps(altered))
                else:
                    self.story['capability_plan']['visual_candidates'] = []
                code, out = self.run_preflight()
                self.assertEqual(code, 1, (mutation, out))
                self.assertIn('PREFLIGHT_NOT_READY', out)

    def test_legacy_not_checked_is_visible_and_new_v2_can_require_evidence(self):
        self.story.pop('research_evidence_gate')
        self.story.pop('capability_plan')
        code, out = self.run_preflight(strict=True)
        self.assertEqual(code, 1)
        self.assertIn('NEW_V2_RESEARCH_BRIEF_REQUIRED', out)
        code, out = self.run_preflight(strict=False)
        self.assertEqual(code, 0)
        self.assertIn('NOT_CHECKED_LEGACY', out)
        self.assertNotIn('PASS_MACHINE_PROOF_ONLY_HUMAN_NOT_CHECKED', out)


if __name__ == '__main__':
    unittest.main()
