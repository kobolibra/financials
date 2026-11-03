#!/usr/bin/env python3
"""Hostile regression tests for future issuers' publication evidence."""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_release_contract", ROOT / "scripts/check_release_contract.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class IssuerReleaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(
            (ROOT / "site/research_catalog.json").read_text(encoding="utf-8"))
        cls.issuer = next(x for x in cls.catalog["issuers"] if x["code"] == "688220")
        cls.original = json.loads(
            (ROOT / "research/issuers/688220/release-gates.json").read_text(encoding="utf-8"))

    def poisoned(self, change, *, check_bytes=False):
        value = copy.deepcopy(self.original)
        change(value)
        return mod.validate_release(ROOT, self.issuer, value, check_bytes=check_bytes)

    def test_existing_real_pdf_sha_and_exact_contract(self):
        self.assertEqual(mod.validate_release(ROOT, self.issuer, self.original), [])
        self.assertEqual(mod.validate_registry(ROOT), [])

    def test_current_live_failure_is_not_hidden_by_local_passes(self):
        self.assertEqual(self.original["gates"]["CLOUDFLARE_LIVE"]["status"], "FAIL")
        self.assertEqual(self.original["gates"]["INDEPENDENT_HUMAN_REVIEW"]["status"], "NOT_CHECKED")
        self.assertEqual(self.original["gates"]["REPORTED_NOTE_TIES"]["status"], "FAIL")

    def test_pdf_corruption_and_source_version_fail_closed(self):
        errors = self.poisoned(
            lambda x: x["source_pdf"].update(sha256="0" * 64), check_bytes=True)
        self.assertTrue(any("PDF_BYTE_HASH_MISMATCH" in x for x in errors), errors)

    def test_report_route_cannot_point_to_second_directory(self):
        errors = self.poisoned(lambda x: x.update(report_route="/new-four-companies/688220.html"))
        self.assertTrue(any("ISSUER_ROUTE_MISMATCH" in x for x in errors))

    def test_missing_scope_cannot_be_pass(self):
        errors = self.poisoned(lambda x: x["gates"]["ACCOUNTING_CORE"].update(scope="yes"))
        self.assertTrue(any("AMBIGUOUS_GATE_SCOPE" in x for x in errors))

    def test_forged_pass_without_evidence_rejected(self):
        errors = self.poisoned(lambda x: x["gates"]["CLOUDFLARE_LIVE"].update(status="PASS",proof=None))
        self.assertTrue(any("UNSUPPORTED_GATE" in x for x in errors))
        self.assertTrue(any("LIVE_PASS_WITHOUT_DEPLOYED_FINGERPRINT" in x for x in errors))

    def test_signed_sankey_decision_must_be_source_grounded(self):
        errors = self.poisoned(lambda x: x["sankey"].update(
            decision="OMITTED_WITH_SOURCE_REASON", omission_reason="not necessary"))
        self.assertTrue(any("SANKEY_OMISSION_NOT_SOURCE_GROUNDED" in x for x in errors))

    def test_preview_cannot_use_missing_source_as_acceptable(self):
        errors = self.poisoned(lambda x: x["gates"]["SOURCE_ROW_COLUMN"].update(
            status="NOT_CHECKED",proof=None))
        self.assertTrue(any("PREVIEW_P0_BLOCKED" in x for x in errors))

    def test_source_exceptions_remain_explicit_in_preview(self):
        self.assertEqual(self.original["gates"]["REPORTED_NOTE_TIES"]["status"], "FAIL")
        errors = self.poisoned(lambda x: x.update(blockers=[]))
        self.assertTrue(any("FAIL_WITHOUT_DISCLOSED_BLOCKER" in x for x in errors))

    def test_cannot_fake_full_professional_certification(self):
        errors = self.poisoned(lambda x: x.update(release_class="verified_research"))
        self.assertTrue(any("VERIFIED_RESEARCH_HAS_OPEN_GATE" in x for x in errors))

    def test_future_issuer_requires_own_contract(self):
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(mod, "validate_registry", return_value=[]):
                with mock.patch.object(mod, "read_json", return_value={
                    "issuers":[{"code":c} for c in sorted(mod.LEGACY_PRE_CONTRACT)]
                    + [{"code":"999999", "href":"/999999.html"}]
                }):
                    errors = mod.validate_repository(Path(d), check_bytes=False)
        self.assertIn("UNREGISTERED_NEW_ISSUER 999999", errors)

    def test_unrelated_external_file_path_cannot_pass_as_evidence(self):
        errors = self.poisoned(lambda x: x["gates"]["BROWSER_LOCAL"].update(
            proof="../../outside/green.txt"))
        self.assertTrue(any("OUTSIDE_REPOSITORY_PATH" in x for x in errors))


if __name__ == "__main__":
    unittest.main()
