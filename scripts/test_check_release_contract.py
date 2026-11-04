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

    def test_601628_release_gate_must_reflect_current_version_not_prior_green(self):
        insurer=next(x for x in self.catalog["issuers"] if x["code"]=="601628")
        current=json.loads((ROOT/"research/issuers/601628/release-gates.json").read_text())
        self.assertEqual(current["gates"]["INDEPENDENT_HUMAN_REVIEW"]["status"],"NOT_CHECKED")
        self.assertEqual(mod.validate_release(ROOT,insurer,current,check_bytes=False),[])
        live=current["gates"]["CLOUDFLARE_LIVE"]["status"]
        if live=="PASS":
            self.assertEqual(current["live_release_fingerprint"],current["published_html_sha256"])
            self.assertRegex(current["actual_main_release_commit"],r"^[a-f0-9]{40}$")
            self.assertTrue(current["gates"]["CLOUDFLARE_LIVE"]["proof"])
        else:
            # Updated HTML is only a candidate until this exact version has
            # a main commit and actual public Cloudflare HTTP/browser proof.
            self.assertEqual(live,"NOT_CHECKED")
            self.assertIsNone(current["live_release_fingerprint"])
            self.assertIsNone(current["actual_main_release_commit"])
            self.assertIsNone(current["gates"]["CLOUDFLARE_LIVE"]["proof"])
            old=current["historical_live_before_mobile_editorial_rebuild"]
            self.assertEqual(old["status"],"PASS")
            self.assertNotEqual(old["sha"],current["published_html_sha256"])

    def test_live_fingerprint_must_be_actual_report_html_hash(self):
        insurer=next(x for x in self.catalog["issuers"] if x["code"]=="601628")
        original=json.loads((ROOT/"research/issuers/601628/release-gates.json").read_text())
        # A true candidate NOT_CHECKED is valid. Turn it into an explicit
        # malicious LIVE PASS first, then verify the generic release gate fails
        # on both fabricated public HTML SHA and fake current main commit.
        fake=copy.deepcopy(original)
        fake["gates"]["CLOUDFLARE_LIVE"]={
            "status":"PASS",
            "proof":"https://github.com/kobolibra/financials/actions/runs/41771178361",
            "scope":"Deliberately forged previous HTML live proof to challenge the new version's cryptographic release gate."
        }
        fake["actual_main_release_commit"]="d11638f0c76ff8aef2beb163a1028f176123bbdc"
        fake["live_release_fingerprint"]="0"*64
        errors=mod.validate_release(ROOT,insurer,fake,check_bytes=False)
        self.assertIn("LIVE_FINGERPRINT_HTML_DRIFT 601628",errors)
        fake["live_release_fingerprint"]=original["published_html_sha256"]
        fake["actual_main_release_commit"]="NOT_CHECKED"
        errors=mod.validate_release(ROOT,insurer,fake,check_bytes=False)
        self.assertIn("LIVE_PROOF_MAIN_COMMIT_INVALID 601628",errors)

    def test_real_live_receipt_is_archived_and_has_exact_source_sha_3_viewports(self):
        insurer=next(x for x in self.catalog["issuers"] if x["code"]=="601628")
        current=json.loads((ROOT/"research/issuers/601628/release-gates.json").read_text())
        self.assertEqual(mod.validate_release(ROOT,insurer,current,check_bytes=False),[])
        receipt=json.loads((ROOT/"research/issuers/601628/live-release-receipt.json").read_text())
        self.assertEqual(receipt["status"],"PASS")
        self.assertEqual(len(receipt["screenshots"]),6)
        self.assertEqual({x["width"] for x in receipt["real_chromium_viewports"]},{1440,768,390})
        if current["gates"]["CLOUDFLARE_LIVE"]["status"]=="PASS":
            self.assertEqual(receipt["verified_git_commit"],current["actual_main_release_commit"])
            self.assertEqual(receipt["actual_full_content_sha256_equals_repository_main_601628"],current["published_html_sha256"])
        else:
            # Genuine modified standalone HTML is NOT_CHECKED until the new
            # report SHA has passed real Cloudflare after merging main.
            self.assertEqual(current["gates"]["CLOUDFLARE_LIVE"]["status"],"NOT_CHECKED")
            self.assertIsNone(current["live_release_fingerprint"])
            self.assertIsNone(current["live_receipt_file"])
            history=current["historical_live_before_1440_label_collision_qa_fix"]
            self.assertEqual(history["public_article_sha256"],
                receipt["actual_full_content_sha256_equals_repository_main_601628"])
            self.assertNotEqual(history["public_article_sha256"],current["published_html_sha256"])

    def test_live_proof_must_not_be_forged_home_report_or_screenshot(self):
        insurer=next(x for x in self.catalog["issuers"] if x["code"]=="601628")
        original=json.loads((ROOT/"research/issuers/601628/release-gates.json").read_text())
        # In-memory ONLY synthetic correct-shaped receipt for release-gate
        # adversarial tests. Never persist/describe it as actual Cloudflare!
        # This keeps hostile coverage during a genuine NOT_CHECKED candidate,
        # without falsely promoting that new article to a LIVE PASS.
        actual_historical=json.loads((ROOT/"research/issuers/601628/live-release-receipt.json").read_text())
        original=copy.deepcopy(original)
        original["gates"]["CLOUDFLARE_LIVE"]={
            "status":"PASS",
            "proof":actual_historical["actual_publication_action"],
            "scope":"SYNTHETIC UNIT TEST FIXTURE ONLY NOT REAL NEW DEPLOYMENT"
        }
        original["live_release_fingerprint"]=original["published_html_sha256"]
        original["actual_main_release_commit"]=actual_historical["verified_git_commit"]
        original["actual_directory_fingerprint"]=actual_historical["actual_full_content_sha256_equals_repository_main_index"]
        original["live_receipt_file"]="research/issuers/601628/live-release-receipt.json"
        original_read=mod.read_json
        cases=[
            ("LIVE_CAPTURE_MAIN_SHA_MISMATCH",lambda x:x.update(verified_git_commit="0"*40)),
            ("LIVE_CAPTURE_HTML_SHA_MISMATCH",lambda x:x.update(actual_full_content_sha256_equals_repository_main_601628="0"*64)),
            ("LIVE_CAPTURE_HOMEPAGE_SHA_MISMATCH",lambda x:x.update(actual_full_content_sha256_equals_repository_main_index="0"*64)),
            ("LIVE_CAPTURE_COMPANY_VS_HOME_ROUTE_INVALID",lambda x:x["real_chromium_viewports"][0].update(actual_dedicated_article_final_url="https://financials-in-visuals.pages.dev/#companies")),
            ("LIVE_CAPTURE_COMPANY_VS_HOME_ROUTE_INVALID",lambda x:x["real_chromium_viewports"][0].update(actual_return_to_library_url="https://financials-in-visuals.pages.dev/601628")),
            ("LIVE_CAPTURE_SCREENSHOT_SET_INVALID",lambda x:x["screenshots"].pop()),
            ("LIVE_CAPTURE_PHONE_FINANCE_FIGURES_INVALID",lambda x:next(y for y in x["real_chromium_viewports"] if y["width"]==390).update(mobile_ten_full_width_source_exact_money_exhibits="FAIL")),
        ]
        for marker,poison in cases:
            with self.subTest(marker=marker):
                def changed(path):
                    data=original_read(path)
                    if str(path).endswith("601628/live-release-receipt.json"):
                        data=copy.deepcopy(data)
                        data["actual_full_content_sha256_equals_repository_main_601628"]=original["published_html_sha256"]
                        poison(data)
                    return data
                with mock.patch.object(mod,"read_json",side_effect=changed):
                    actual=mod.validate_release(ROOT,insurer,original,check_bytes=False)
                self.assertTrue(any(marker in e for e in actual),actual)
        unlinked=copy.deepcopy(original)
        unlinked.pop("live_receipt_file",None)
        errs=mod.validate_release(ROOT,insurer,unlinked,check_bytes=False)
        self.assertIn("LIVE_CAPTURE_RECEIPT_MISSING 601628",errs)

    def test_two_sector_current_exact_live_html_and_real_receipts_are_source_bound(self):
        # These exact receipts were actually captured from current 9060 main
        # public Cloudflare Action 41804157527. Historic NOT_CHECKED metadata
        # must not keep this observed genuine published version stale.
        expected = {
            "600900": "d928676e87ff3d415de36931ee5706614d797264a88dc4980b94426f1492eef8",
            "600276": "cd4d0c694c2c1c36c5ba2b2d5028f7db157668139edfe0b00f310f9cd94bee0a",
        }
        for company_code, html_sha in expected.items():
            issuer=next(x for x in self.catalog["issuers"] if x["code"]==company_code)
            record=json.loads((ROOT/f"research/issuers/{company_code}/release-gates.json").read_text())
            self.assertEqual(record["published_html_sha256"], html_sha)
            self.assertEqual(record["live_release_fingerprint"], html_sha)
            self.assertEqual(record["actual_main_release_commit"], "9060bd2a0bf3ddc32d267c176388214ef3316f13")
            self.assertEqual(record["gates"]["CLOUDFLARE_LIVE"]["proof"],
                             "https://github.com/kobolibra/financials/actions/runs/41804157527")
            self.assertEqual(mod.validate_release(ROOT,issuer,record,check_bytes=False),[])
            poisoned=copy.deepcopy(record)
            poisoned["live_release_fingerprint"]="0"*64
            errors=mod.validate_release(ROOT,issuer,poisoned,check_bytes=False)
            self.assertIn(f"LIVE_FINGERPRINT_HTML_DRIFT {company_code}",errors)
            poisoned=copy.deepcopy(record)
            poisoned["actual_main_release_commit"]="0"*40
            errors=mod.validate_release(ROOT,issuer,poisoned,check_bytes=False)
            self.assertIn(f"LIVE_CAPTURE_MAIN_SHA_MISMATCH {company_code}",errors)

    def test_legacy_explicit_sha_not_checked_does_not_claim_new_live_fingerprint(self):
        # Historical receipts may be retained as dated claims, not backfilled.
        issuer=next(x for x in self.catalog["issuers"] if x["code"]=="600900")
        record=json.loads((ROOT/"research/issuers/600900/release-gates.json").read_text())
        historic=copy.deepcopy(record)
        historic["published_html_sha256"]="NOT_CHECKED_PENDING_MAIN_DEPLOY"
        historic["live_release_fingerprint"]="600900_SOURCE_PDF_SHA_738de3b36a31646f344cefaf90b4f149d653c3f68e89f4f8d14bdf02fc9c65a2_MAIN_7704ecc6c6a0f0470f7dd5f2c6fe71d5527de511_LIVE_CI_41736999189"
        historic["actual_main_release_commit"]="7704ecc6c6a0f0470f7dd5f2c6fe71d5527de511"
        historic.pop("live_receipt_file",None)
        self.assertFalse(any("LIVE_FINGERPRINT_HTML_DRIFT" in e
                             for e in mod.validate_release(ROOT,issuer,historic,check_bytes=False)))

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
