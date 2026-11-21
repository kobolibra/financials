"""Hostile, issuer-independent regression for the self-directed editorial loop."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from autonomous_editorial_audit import (
    ROOT, SELF_REVIEW_FIELDS, _peer_candidates, audit, audit_issuer,
    changed_issuers, figure_source_refs,
)

DOSSIER = ROOT / "research/issuers/600206"


def original():
    catalog = json.loads((ROOT / "site/research_catalog.json").read_text())
    issuer = next(x for x in catalog["issuers"] if x["code"] == "600206")
    record = json.loads((DOSSIER / "release-gates.json").read_text())
    ledger = json.loads((DOSSIER / "source-ledger.json").read_text())
    story = json.loads((DOSSIER / "publication.json").read_text())
    brief = json.loads((DOSSIER / "research-brief.json").read_text())
    review = json.loads((DOSSIER / "editorial-self-review.json").read_text())
    h = hashlib.sha256((ROOT / "public" / issuer["href"].lstrip("/")).read_bytes()).hexdigest()
    return [ROOT, issuer, record, ledger, story, brief, review, catalog, h]


def codes(report):
    return {x["code"] for x in report["issues"]}


class AutonomousEditorialAuditTest(unittest.TestCase):
    def test_full_year_reports_missing_author_peer_review_as_debt_not_excellence(self):
        args = original()
        out = audit(*args[:8], html_sha=args[8], strict=True)
        self.assertGreaterEqual(out["source_opportunities"], 7)
        self.assertEqual(out["schema"], "financials.autonomous_editorial_audit.v1")
        self.assertIn("PEER_CALIBRATION_MISSING", codes(out))
        self.assertIn("CHART_BY_CHART_REVIEW_MISSING", codes(out))
        self.assertNotEqual(out["verdict"], "READY_FOR_HUMAN_INDEPENDENT_REVIEW_NOT_CERTIFIED")
        self.assertEqual(out["independent_human_review"], "NOT_CHECKED")

    def test_four_chart_synopsis_does_not_get_credit_for_available_economics(self):
        args = original()
        args[4] = copy.deepcopy(args[4])
        args[4]["figures"] = args[4]["figures"][:4]
        out = audit(*args[:8], html_sha=args[8], strict=True)
        self.assertGreater(out["blocker_count"], 0)
        self.assertIn("MISSING_CASH_CLOSE", codes(out))
        self.assertIn("MISSING_BALANCE_STRUCTURE", codes(out))

    def test_display_words_or_family_labels_cannot_replace_exact_fact_operands(self):
        args = original()
        args[4] = copy.deepcopy(args[4])
        fake = next(x for x in args[4]["figures"] if x["id"] == "region-income")
        fake["facts"] = []
        fake["takeaway"] = "region1_rev region1_cost region2_rev region2_cost rev cogs"
        self.assertEqual(figure_source_refs(fake, set(args[3]["facts"])), set())
        out = audit(*args[:8], html_sha=args[8])
        self.assertIn("MISSING_DISCLOSED_INCOME", codes(out))

    def test_substring_cash_close_forgeries_fail(self):
        args = original()
        args[4] = copy.deepcopy(args[4])
        f = next(x for x in args[4]["figures"] if x["id"] == "cash-closure")
        f["rows"] = [["cfo and cash_close seem real", "cfo_fake", "start"],
                     ["cash closes here", "cash_close_fake", "total"]]
        out = audit(*args[:8], html_sha=args[8], strict=True)
        self.assertIn("MISSING_CASH_CLOSE", codes(out))

    def test_stale_pdf_and_html_are_blockers(self):
        for field, bad in (("reviewed_html_sha256", "0" * 64),
                           ("reviewed_source_pdf_sha256", "0" * 64)):
            args = original()
            args[6] = copy.deepcopy(args[6])
            args[6][field] = bad
            out = audit(*args[:8], html_sha=args[8])
            expect = "REVIEW_STALE_HTML" if "html" in field else "REVIEW_STALE_PDF"
            with self.subTest(field=field):
                self.assertIn(expect, codes(out))
                self.assertEqual(out["verdict"], "BLOCK")

    def test_peer_benchmark_requires_current_bytes_and_real_comparison(self):
        args = original()
        peers = _peer_candidates(args[0], args[1], args[2], args[7])
        self.assertGreaterEqual(len(peers), 2)
        args[6] = copy.deepcopy(args[6])
        args[6]["peer_calibration"] = {
            "peers": [
                dict(code=x["code"], html_sha256="0" * 64,
                     research_delta="A " * 40, visual_delta="B " * 40)
                for x in peers[:2]
            ]
        }
        out = audit(*args[:8], html_sha=args[8])
        self.assertIn("PEER_CALIBRATION_STALE_OR_VAGUE", codes(out))
        self.assertNotIn("PEER_CALIBRATION_MISSING", codes(out))

    def test_chart_by_chart_review_fields_are_a_real_checklist(self):
        args = original()
        args[6] = copy.deepcopy(args[6])
        ids = [f["id"] for f in args[4]["figures"]]
        args[6]["chart_reviews"] = {
            fid: {field: "For " + fid + ": source-bound five-second finding, period, and layout."
                  for field in SELF_REVIEW_FIELDS} for fid in ids
        }
        out = audit(*args[:8], html_sha=args[8])
        self.assertNotIn("CHART_BY_CHART_REVIEW_MISSING", codes(out))
        self.assertFalse(any(x.startswith("CHART_REVIEW_INCOMPLETE") for x in codes(out)))
        args[6]["chart_reviews"][ids[0]]["mobile_readability"] = ""
        out = audit(*args[:8], html_sha=args[8])
        self.assertIn("CHART_REVIEW_INCOMPLETE_" + ids[0], codes(out))

    def test_copy_paste_visual_praise_cannot_clear_the_review_queue(self):
        args = original()
        args[6] = copy.deepcopy(args[6])
        ids = [f["id"] for f in args[4]["figures"]]
        args[6]["chart_reviews"] = {
            fid: {field: "This generic page is beautiful and readable for everyone."
                  for field in SELF_REVIEW_FIELDS} for fid in ids
        }
        result = audit(*args[:8], html_sha=args[8])
        self.assertIn("CHART_REVIEW_COPYPASTE", codes(result))

    def test_same_peer_praise_repeated_does_not_prove_calibration(self):
        args = original()
        args[6] = copy.deepcopy(args[6])
        peers = _peer_candidates(args[0], args[1], args[2], args[7])
        generic = ("Both examples are well designed and analyzed, so this report "
                   "now has excellent visual and financial quality.")
        args[6]["peer_calibration"] = {"peers": [
            {"code": p["code"], "html_sha256": p["html_sha256"],
             "research_delta": generic, "visual_delta": generic}
            for p in peers[:2]]}
        result = audit(*args[:8], html_sha=args[8])
        self.assertIn("PEER_CALIBRATION_COPYPASTE", codes(result))

    def test_same_research_question_repeated_demands_revision(self):
        args = original()
        args[4] = copy.deepcopy(args[4])
        figs = args[4]["figures"]
        figs[1]["question"] = figs[0]["question"]
        out = audit(*args[:8], html_sha=args[8])
        self.assertIn("DUPLICATE_RESEARCH_QUESTION", codes(out))

    def test_no_auto_fake_human_signoff(self):
        args = original()
        args[2] = copy.deepcopy(args[2])
        args[2]["gates"]["INDEPENDENT_HUMAN_REVIEW"]["status"] = "PASS"
        out = audit(*args[:8], html_sha=args[8])
        self.assertIn("HUMAN_REVIEW_UNVERIFIED", codes(out))

    def test_new_period_beyond_industrial_basis_is_not_auto_certified(self):
        args = original()
        args[2] = copy.deepcopy(args[2])
        args[2]["period"] = "2026Q1"
        out = audit(*args[:8], html_sha=args[8])
        self.assertIn("SECTOR_OR_PERIOD_COVERAGE_NOT_ESTABLISHED", codes(out))

    def test_current_issuer_cli_loader_is_source_grounded(self):
        out = audit_issuer(ROOT, "600206")
        self.assertRegex(out["original_pdf_sha256"], "^[a-f0-9]{64}$")
        self.assertRegex(out["html_sha256"], "^[a-f0-9]{64}$")
        self.assertIn("CASH_CLOSE", {v["topic"] for v in out["source_topics"]})

    def test_period_issuer_is_not_silently_aliased_to_primary_period(self):
        result = audit_issuer(ROOT, "600036@2026Q1")
        self.assertEqual(result["period"], "2026Q1")
        self.assertEqual(result["issuer_period"], "600036@2026Q1")
        self.assertIn("SECTOR_OR_PERIOD_COVERAGE_NOT_ESTABLISHED", codes(result))
        self.assertNotEqual(result["verdict"], "READY_FOR_HUMAN_INDEPENDENT_REVIEW_NOT_CERTIFIED")

    def test_changed_period_dossier_and_explicit_catalog_route_discovered(self):
        with patch("autonomous_editorial_audit.subprocess.run") as cmd:
            cmd.return_value.stdout = (
                "research/issuers/600036/2026Q1/publication.json\n"
                "research/issuers/600206/figure-briefs.json\n"
                "public/600206.html\n"
            )
            self.assertEqual(changed_issuers(ROOT, "origin/main"),
                             ["600036@2026Q1", "600206"])


    def test_modified_real_issuer_files_are_detected_not_skill_docs(self):
        with patch("autonomous_editorial_audit.subprocess.run") as cmd:
            cmd.return_value.stdout = (
                "research/issuers/600206/publication.json\n"
                "public/600206.html\n"
                "skills/ashare-financial-storytelling/SKILL.md\n"
                "research/issuers/600690/source-ledger.json\n"
            )
            self.assertEqual(changed_issuers(ROOT, "origin/main"),
                             ["600206", "600690"])
            self.assertEqual(cmd.call_args.kwargs["check"], True)


if __name__ == "__main__":
    unittest.main()
