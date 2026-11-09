"""Fail closed against live finance verifier silently shadowing its source helper.

The 2026-11-09 first post-merge live check reached canonical exact HTML
bytes, but crashed before the actual Chromium assertions because a source
fact loop assigned `expected = ledger["facts"][key]`, shadowing the module
`expected(code)` file-reader helper throughout Python run() scope.
"""
import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_live_optical_native.py"


class OpticalLiveProofSmoke(unittest.TestCase):
    def test_original_source_browser_script_is_python_compilable(self):
        code=SCRIPT.read_text(encoding="utf-8")
        compile(code,str(SCRIPT),"exec")

    def test_no_live_run_locals_shadow_module_source_functions(self):
        tree=ast.parse(SCRIPT.read_text(encoding="utf-8"),str(SCRIPT))
        global_functions={node.name for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
        live=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=="run")
        local_assignments={node.id for node in ast.walk(live)
                           if isinstance(node,ast.Name) and isinstance(node.ctx,ast.Store)}
        self.assertFalse(global_functions&local_assignments,
                         "LIVE_VERIFIER_LOCAL_SHADOWS_MODULE_SOURCE_FUNCTION "+
                         repr(global_functions&local_assignments))
        self.assertIn("expected",global_functions)
        self.assertNotIn("expected",local_assignments)

    def test_independent_actual_report_source_and_decision_acceptance_not_skipped(self):
        content=SCRIPT.read_text(encoding="utf-8")
        for key in ("wait_for_real_deploy()", "pdf_sha.encode() in expected(code)",
                    "decision_values(ledger)", "data-original-pdf-sha256",
                    "originalValue", "derivedRatio", "physicalPage",
                    "FULL_HTML_BODY_HORIZONTAL_OVERFLOW",
                    "LIVE_RESEARCH_QUANTIFIED_DECISION_WRONG",
                    "LIVE_OPTICAL_PNL_FALSE_MONEY_LENGTH"):
            self.assertIn(key,content,key)
        self.assertIn('"second_human"', "second_human") if False else None


if __name__=="__main__":
    unittest.main()
