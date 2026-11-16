"""Regression: the intake CLI must reproduce hand-verified real ledger cells.

Uses the archived original 300570 2026H1 PDF and its published source ledger,
so the tool is proven against a genuine report rather than a synthetic page.
Run: python -m unittest discover -s skills/ashare-financial-storytelling/tools -p 'test_*.py' -v
"""
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fin_intake as fi  # noqa: E402

ROOT = fi.ROOT
CODE = "300570"


class RealLedgerReproduction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m, cls.doc, cls.ledger = fi.open_source(CODE)

    def assert_same(self, key, spec):
        built = fi.build_fact(self.doc, self.ledger, key, spec)
        ref = self.ledger["facts"][key]
        self.assertEqual(Decimal(built["yuan"]), Decimal(ref["yuan"]), key)
        self.assertEqual(built["period"], ref["period"], key)
        self.assertTrue(any(abs(a - b) < 0.6 for a, b in zip(built["source_cells"][0]["bbox"], ref["source_cells"][0]["bbox"])))

    def test_income_statement_current_prior_and_negative_cells(self):
        self.assert_same("rev", {"page": 40, "row": "其中：营业收入", "column": 1, "type": "flow", "label": "营业收入"})
        self.assert_same("rev_prior", {"page": 40, "row": "其中：营业收入", "column": 2, "type": "flow", "label": "营业收入", "prior": True})
        self.assert_same("cogs", {"page": 40, "row": "其中：营业成本", "column": 1, "type": "flow", "label": "营业成本"})
        self.assert_same("finance_prior", {"page": 40, "row": "^财务费用$", "column": 2, "type": "flow", "label": "财务费用", "prior": True})

    def test_ambiguous_row_blank_column_and_expect_mismatch_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "ROW_AMBIGUOUS"):
            fi.build_fact(self.doc, self.ledger, "x", {"page": 40, "row": "营业", "column": 1, "type": "flow", "label": "测试事实项"})
        with self.assertRaisesRegex(ValueError, "COLUMN_BLANK"):
            fi.build_fact(self.doc, self.ledger, "x", {"page": 40, "row": "其中：营业收入", "column": 3, "type": "flow", "label": "测试事实项"})
        with self.assertRaisesRegex(ValueError, "EXPECTED_VALUE_MISMATCH"):
            fi.build_fact(self.doc, self.ledger, "x", {"page": 40, "row": "其中：营业收入", "column": 1, "type": "flow", "label": "测试事实项", "expect": "1"})
        with self.assertRaisesRegex(ValueError, "STORE_PRINTED_YUAN_AS_IS"):
            fi.build_fact(self.doc, self.ledger, "x", {"page": 40, "row": "其中：营业成本", "column": 1, "type": "flow", "label": "测试事实项", "sign": -1})

    def test_tool_output_passes_the_publication_cell_validator(self):
        sys.path.insert(0, str(ROOT / "research" / "shared"))
        from source_publication import validate
        ledger = json.loads(json.dumps(self.ledger))
        ledger["facts"]["rev"] = fi.build_fact(self.doc, ledger, "rev", {"page": 40, "row": "其中：营业收入", "column": 1, "type": "flow", "label": "营业收入"})
        story = json.loads((ROOT / "research/issuers" / CODE / "publication.json").read_text())
        self.assertEqual(validate(ledger, story)["status"], "PASS")


class EditorialLint(unittest.TestCase):
    def test_lint_flags_weak_dossier(self):
        weak = {"figures": [{"id": "a", "family": "comparison", "question": "收入", "takeaway": "收入增长了12.30%，导致利润上升"}],
                "thesis": {"body": "增长"}, "essays": [], "notes": [], "metrics": []}
        issues = " ".join(fi.lint(weak))
        for code in ("MISSING_SIGNED_BRIDGE", "TITLE_NOT_A_QUESTION", "UNHEDGED_CAUSAL", "HAND_TYPED_NUMBER", "THESIS_TOO_THIN", "替代解释"):
            self.assertIn(code, issues)


class QuarterlyGeneralization(unittest.TestCase):
    def test_editorial_v2_lint_refuses_a_bridge_parade_and_passes_the_real_q3_story(self):
        q3 = json.loads((ROOT / "research/issuers/300394/20269M/publication.json").read_text())
        self.assertEqual(q3["design"], "EDITORIAL_V2")
        roles = {f["id"]: f["role"] for f in json.loads((ROOT / "research/editorial-20261113/300394-20269M.json").read_text())["editorial"]["figures"]}
        self.assertEqual(fi.lint_v2(q3["figures"], roles), [])
        parade = [dict(f, family="signed_bridge", chapter=None) for f in q3["figures"]]
        self.assertIn("V2_BRIDGE_PARADE", " ".join(fi.lint_v2(q3["figures"][:1] + parade[1:4], {})))
        issues = " ".join(fi.lint_v2(parade))
        for code in ("V2_FIRST_FIGURE_MUST_BE_KPI_BOARD", "V2_FAMILY_VARIETY", "V2_NO_TREND_EXHIBIT", "V2_BRIDGE_PARADE", "V2_TOO_FEW_CHAPTERS"):
            self.assertIn(code, issues)

    def test_nine_month_report_declares_single_quarter_columns(self):
        class Page:
            def __init__(self, t): self.t = t
            def get_text(self, *a): return self.t
        doc = [Page("某某股份有限公司 2026年第三季度报告"), Page("证券代码：300570")]
        ident = fi.detect_identity(doc, "300570")
        self.assertEqual(ident["fiscal_period"], "20269M")
        self.assertEqual(ident["comparative_period"], "20259M")
        self.assertEqual(ident["flow_columns"], {"本报告期": "2026Q3", "上年同期本报告期": "2025Q3"})

    def test_publication_without_income_figure_does_not_require_segments(self):
        sys.path.insert(0, str(ROOT / "research" / "shared"))
        from source_publication import validate
        ledger = json.loads((ROOT / "research/issuers" / CODE / "source-ledger.json").read_text())
        story = json.loads((ROOT / "research/issuers" / CODE / "publication.json").read_text())
        ledger["segments"] = []
        with self.assertRaises(ValueError):
            validate(ledger, story)
        story["figures"] = [f for f in story["figures"] if f["family"] != "income"]
        self.assertEqual(validate(ledger, story)["status"], "PASS")

    def test_extra_flow_column_must_be_declared_and_period_matched(self):
        sys.path.insert(0, str(ROOT / "research" / "shared"))
        from source_publication import validate
        ledger = json.loads((ROOT / "research/issuers" / CODE / "source-ledger.json").read_text())
        story = json.loads((ROOT / "research/issuers" / CODE / "publication.json").read_text())
        ledger["facts"]["rev"]["source_column"] = "本报告期"
        with self.assertRaisesRegex(ValueError, "FLOW_PERIOD_COLUMN_MISMATCH"):
            ledger["issuer"]["flow_columns"] = {"本报告期": "2026Q2"}
            validate(ledger, story)
        ledger["issuer"]["flow_columns"] = {"本期/期末": "2026H1"}
        with self.assertRaisesRegex(ValueError, "INVALID_EXTRA_FLOW_COLUMNS"):
            validate(ledger, story)


class RealQuarterlyReport(unittest.TestCase):
    """300394 2026 third-quarter report: wrapped headline cells, blank cells, dash placeholders."""
    PERIOD = "20269M"

    @classmethod
    def setUpClass(cls):
        cls.m, cls.doc, cls.ledger = fi.open_source("300394", cls.PERIOD)

    def build(self, spec):
        return fi.build_fact(self.doc, self.ledger, "x", {"type": "flow", "label": "测试事实项", **spec})

    def test_wrapped_headline_cells_are_rejoined_and_reproduce_printed_growth(self):
        q3 = self.build({"page": 1, "y": [583.8, 588.8], "column": 1, "source_column": "本报告期"})
        prior = self.build({"page": 1, "y": [583.8, 588.8], "column": 3, "source_column": "上年同期本报告期"})
        self.assertEqual(q3["yuan"], "1923161156.63")
        self.assertTrue(q3["source_cells"][0]["wrapped_number"])
        self.assertEqual((q3["period"], prior["period"]), ("2026Q3", "2025Q3"))
        growth = (Decimal(q3["yuan"]) / Decimal(prior["yuan"]) - 1) * 100
        self.assertEqual(f"{growth:.2f}", "31.50")  # printed 31.50%

    def test_blank_current_cell_is_not_filled_from_prior_year(self):
        with self.assertRaisesRegex(ValueError, "COLUMN_BLANK"):
            self.build({"page": 11, "y": [513.7, 518.7], "column": 1})
        prior = self.build({"page": 11, "y": [513.7, 518.7], "column": 2, "prior": True})
        self.assertEqual(prior["yuan"], "40000000.00")
        self.assertEqual(prior["period"], "20259M")

    def test_dash_placeholder_is_not_zero_and_short_labels_are_refused(self):
        with self.assertRaisesRegex(ValueError, "DASH_PLACEHOLDER"):
            self.build({"page": 1, "y": [746.4, 751.4], "column": 1})
        with self.assertRaisesRegex(ValueError, "LABEL_TOO_SHORT"):
            fi.build_fact(self.doc, self.ledger, "x", {"page": 1, "y": [583.8, 588.8], "column": 5, "type": "flow", "label": "收入"})

    def test_lone_table_row_borrows_columns_from_neighbouring_block(self):
        sales = self.build({"page": 10, "y": [514.1, 519.1], "column": 1})
        prior = self.build({"page": 10, "y": [514.1, 519.1], "column": 2, "prior": True})
        self.assertEqual((sales["yuan"], prior["yuan"]), ("4432650235.40", "3676244492.30"))


if __name__ == "__main__":
    unittest.main()
