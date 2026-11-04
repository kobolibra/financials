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

    def test_only_insurance_adapter_may_use_issuer_regulatory_scope(self):
        original_read = mod.read_json
        def wrong_sector_reg_scope(path):
            data = original_read(path)
            if str(path).endswith("688220/source-ledger.json"):
                data = copy.deepcopy(data)
                data["facts"]["rev"]["scope"] = "issuer_regulatory"
            return data
        with mock.patch.object(mod, "read_json", side_effect=wrong_sector_reg_scope):
            errs = mod.validate_release(ROOT, self.issuer, self.original, check_bytes=False)
        self.assertTrue(any("LEDGER_FACT_SCOPE_INVALID 688220/rev" in x for x in errs), errs)

    def test_published_html_sha_cannot_silently_lag_generated_insurance_article(self):
        insurance = next(x for x in self.catalog["issuers"] if x["code"] == "601628")
        record = json.loads((ROOT / "research/issuers/601628/release-gates.json").read_text())
        poisoned = copy.deepcopy(record)
        poisoned["published_html_sha256"] = "0" * 64
        errors = mod.validate_release(ROOT, insurance, poisoned, check_bytes=False)
        self.assertTrue(any("PUBLISHED_REPORT_SHA_MISMATCH 601628" in x for x in errors), errors)

    def test_real_601628_live_and_source_limited_receipt_is_exactly_source_bound(self):
        insurer=next(x for x in self.catalog["issuers"] if x["code"]=="601628")
        original=json.loads((ROOT/"research/issuers/601628/release-gates.json").read_text())
        self.assertEqual(original["gates"]["CLOUDFLARE_LIVE"]["status"],"PASS")
        self.assertEqual(original["gates"]["INDEPENDENT_HUMAN_REVIEW"]["status"],"NOT_CHECKED")
        self.assertEqual(mod.validate_release(ROOT,insurer,original,check_bytes=False),[])

    def test_live_fingerprint_must_be_actual_report_html_hash(self):
        insurer=next(x for x in self.catalog["issuers"] if x["code"]=="601628")
        original=json.loads((ROOT/"research/issuers/601628/release-gates.json").read_text())
        fake=copy.deepcopy(original)
        fake["live_release_fingerprint"]="0"*64
        errors=mod.validate_release(ROOT,insurer,fake,check_bytes=False)
        self.assertIn("LIVE_FINGERPRINT_HTML_DRIFT 601628",errors)
        fake=copy.deepcopy(original)
        fake["actual_main_release_commit"]="NOT_CHECKED"
        errors=mod.validate_release(ROOT,insurer,fake,check_bytes=False)
        self.assertIn("LIVE_PROOF_MAIN_COMMIT_INVALID 601628",errors)

    def test_historical_issuer_explicit_sha_not_checked_is_preserved(self):
        for company_code in ("600900","600276"):
            issuer=next(x for x in self.catalog["issuers"] if x["code"]==company_code)
            record=json.loads((ROOT/f"research/issuers/{company_code}/release-gates.json").read_text())
            self.assertEqual(record["published_html_sha256"],"NOT_CHECKED_PENDING_MAIN_DEPLOY")
            self.assertFalse(any("LIVE_FINGERPRINT_HTML_DRIFT" in e for e in mod.validate_release(ROOT,issuer,record,check_bytes=False)))

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


    def test_ledger_pdf_identity_cannot_be_stale(self):
        original_read = mod.read_json
        def wrong_source(path):
            data = original_read(path)
            if str(path).endswith("688220/source-ledger.json"):
                data = copy.deepcopy(data)
                data["source"]["original_bytes_sha256"] = "0" * 64
            return data
        with mock.patch.object(mod, "read_json", side_effect=wrong_source):
            errors = mod.validate_release(ROOT, self.issuer, self.original, check_bytes=False)
        self.assertTrue(any("LEDGER_PDF_PROVENANCE_STALE" in x for x in errors), errors)

    def test_filing_issuer_or_period_not_borrowed_from_another_company(self):
        original_read = mod.read_json
        def wrong_issuer(path):
            data = original_read(path)
            if str(path).endswith("688220/source-ledger.json"):
                data = copy.deepcopy(data)
                data["issuer"]["fiscal_period"] = "2025H1"
            return data
        with mock.patch.object(mod, "read_json", side_effect=wrong_issuer):
            errors = mod.validate_release(ROOT, self.issuer, self.original, check_bytes=False)
        self.assertTrue(any("LEDGER_ISSUER_PERIOD_MISMATCH" in x for x in errors), errors)

    def test_pdf_number_without_real_row_or_period_is_not_disclosed_fact(self):
        original_read = mod.read_json
        def wrong_cell(path):
            data = original_read(path)
            if str(path).endswith("688220/source-ledger.json"):
                data = copy.deepcopy(data)
                data["facts"]["rev"]["page"] = 999
                data["facts"]["rev"]["period"] = ""
                data["facts"]["rev"]["label"] = ""
            return data
        with mock.patch.object(mod, "read_json", side_effect=wrong_cell):
            errors = mod.validate_release(ROOT, self.issuer, self.original, check_bytes=False)
        self.assertTrue(any("LEDGER_FACT_SOURCE_PAGE_INVALID" in x for x in errors))
        self.assertTrue(any("LEDGER_FACT_PERIOD_MISSING" in x for x in errors))
        self.assertTrue(any("LEDGER_FACT_ROW_LABEL_MISSING" in x for x in errors))

    def test_figure_brief_cannot_use_another_pdf_or_undocumented_fact(self):
        original_read = mod.read_json
        def wrong_figure(path):
            data = original_read(path)
            if str(path).endswith("688220/figure-briefs.json"):
                data = copy.deepcopy(data)
                data["source_sha256"] = "0" * 64
                data["figure_briefs"][0]["facts"] = ["borrowed_issuer_revenue"]
            return data
        with mock.patch.object(mod, "read_json", side_effect=wrong_figure):
            errors = mod.validate_release(ROOT, self.issuer, self.original, check_bytes=False)
        self.assertTrue(any("FIGURE_BRIEFS_PDF_IDENTITY_MISMATCH" in x for x in errors))
        self.assertTrue(any("FIGURE_UNGROUNDED_FACT_ID" in x for x in errors))

    def test_bank_and_insurer_cannot_inherit_industrial_reporting_basis(self):
        for sector in ("bank", "insurance", "insurance_group"):
            errors = self.poisoned(lambda x: x.update(
                sector_adapter=sector, accounting_basis="industrial_revenue_cogs_cash_flow_proxy"))
            self.assertTrue(any("WRONG_INDUSTRY_ACCOUNTING_GRAMMAR" in x for x in errors), (sector,errors))

    def test_ratio_disclosure_cannot_masquerade_as_money(self):
        original_read = mod.read_json
        def wrong_ratio(path):
            data = original_read(path)
            if str(path).endswith("688220/source-ledger.json"):
                data = copy.deepcopy(data)
                data["facts"]["ar_top5_ratio"]["unit"] = "元"
            return data
        with mock.patch.object(mod, "read_json", side_effect=wrong_ratio):
            errors = mod.validate_release(ROOT, self.issuer, self.original, check_bytes=False)
        self.assertTrue(any("LEDGER_RATIO_WRONGLY_MONEY" in x for x in errors))


    def test_embedded_html_source_reason_cannot_silently_lag_source_ledger(self):
        read_actual = mod.read_json
        def changed_source(path):
            data = read_actual(path)
            if str(path).endswith("688220/source-ledger.json"):
                data = copy.deepcopy(data)
                data["source"]["reason"] = "changed in original ledger but not yet rebuilt into published HTML"
            return data
        with mock.patch.object(mod, "read_json", side_effect=changed_source):
            errors = mod.validate_release(ROOT, self.issuer, self.original, check_bytes=False)
        self.assertTrue(any("PUBLISHED_LEDGER_FIELD_DRIFT 688220/source" in x for x in errors), errors)

    def test_embedded_html_financial_fact_cannot_silently_lag_source_ledger(self):
        read_actual = mod.read_json
        def changed_fact(path):
            data = read_actual(path)
            if str(path).endswith("688220/source-ledger.json"):
                data = copy.deepcopy(data)
                data["facts"]["rev"]["yuan"] = "2451275102.26"
            return data
        with mock.patch.object(mod, "read_json", side_effect=changed_fact):
            errors = mod.validate_release(ROOT, self.issuer, self.original, check_bytes=False)
        self.assertTrue(any("PUBLISHED_LEDGER_FIELD_DRIFT 688220/facts" in x for x in errors), errors)


if __name__ == "__main__":
    unittest.main()
