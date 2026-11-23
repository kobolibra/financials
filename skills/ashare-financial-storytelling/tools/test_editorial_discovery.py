import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from editorial_discovery import build_index, index_pages
from fin_intake import rows_on_page
from research_evidence import validate_editorial_selection
from start_report import identity


class EditorialDiscoveryTest(unittest.TestCase):
    def test_discovery_preserves_physical_page_and_all_cooccurring_cues(self):
        self.assertEqual(index_pages(["目录", "平均生息\n资产、净息差和资产减值"]), [{
            "physical_page": 2,
            "signals": {
                "bank_economics": ["平均生息资产", "净息差"],
                "earnings_quality": ["资产减值"],
            },
        }])

    def test_issuer_identity_keeps_parentheses_in_the_complete_cover_name(self):
        cover = "公司代码：600196\n公司简称：复星医药\n上海复星医药（集团）股份有限公司"
        with patch("start_report.intake.pymupdf") as pdf, patch(
                "start_report.intake.detect_identity", return_value={"fiscal_period": "2025H1"}):
            doc = pdf.return_value.open.return_value.__enter__.return_value
            doc.__iter__.return_value = [type("Page", (), {"get_text": lambda self: cover})()]
            self.assertEqual(identity("report.pdf"), ("600196", "上海复星医药（集团）股份有限公司", "2025H1"))

    def test_detached_closing_parenthesis_stays_in_the_negative_source_cell(self):
        words = [
            (10, 20, 90, 30, "公允价值变动收益"),
            (330, 20, 400, 30, "(48,596,693.14"),
            (400.3, 20, 404, 30, ")"),
            (480, 20, 555, 30, "(282,397,883.66)"),
        ]
        page = type("Page", (), {"get_text": lambda self, mode: words})()
        row, = rows_on_page(page)
        self.assertEqual(row["label"], "公允价值变动收益")
        self.assertEqual(row["numbers"][0]["printed"], "(48,596,693.14)")
        self.assertEqual(row["numbers"][0]["bbox"], [330, 20, 404, 30])
        self.assertEqual(row["numbers"][1]["printed"], "(282,397,883.66)")

    def test_index_uses_only_pages_in_the_frozen_original(self):
        with tempfile.TemporaryDirectory() as folder:
            dossier = Path(folder)
            pages = dossier / "extracted"
            pages.mkdir()
            (pages / "p001.txt").write_text("合同服务边际", encoding="utf-8")
            (pages / "p002.txt").write_text("商誉减值测试", encoding="utf-8")
            plan = {"issuer": "601000", "fiscal_period": "2026H1",
                    "source_pdf_sha256": "a" * 64, "research_questions": []}
            index = build_index(dossier, plan, 1)
        self.assertEqual(index["status"], "READING_LEADS_ONLY")
        self.assertEqual(index["source_pdf_sha256"], plan["source_pdf_sha256"])
        self.assertEqual([page["physical_page"] for page in index["page_signals"]], [1])


class EditorialSelectionTest(unittest.TestCase):
    def setUp(self):
        self.ledger = {"facts": {"cfo": {}, "inventory": {}}}
        self.brief = {
            "theses": [{"id": "cash", "source_fact_keys": ["cfo"]}],
            "editorial_selection": {
                "version": 2,
                "lead_thesis_id": "cash",
                "candidates": [
                    {"question": "利润为何未变现？", "decision": "lead",
                     "source_fact_keys": ["cfo"], "rationale": "经营现金净流出。"},
                    {"question": "能否归因到订单？", "decision": "defer",
                     "source_fact_keys": [], "rationale": "缺期末在手订单及对应存货。"},
                ],
                "lead_exhibit": {"figure_id": "cash-bridge", "answer": "列出现金调节主因。",
                                 "alternative": "并列比较净利润和经营现金。",
                                 "tradeoff": "桥图可识别影响最大的调节项。"},
            },
        }

    def test_new_intake_requires_versioned_decision_while_old_briefs_remain_valid(self):
        legacy = copy.deepcopy(self.brief)
        legacy.pop("editorial_selection")
        self.assertIsNone(validate_editorial_selection(self.ledger, legacy))
        with self.assertRaisesRegex(ValueError, "V2_REQUIRED"):
            validate_editorial_selection(self.ledger, legacy, required=True)

    def test_unknown_source_and_disconnected_lead_fail(self):
        for key, error in [("missing", "UNKNOWN_SOURCE_FACTS"),
                           ("inventory", "LEAD_MUST_LINK")]:
            with self.subTest(key=key):
                brief = copy.deepcopy(self.brief)
                brief["editorial_selection"]["candidates"][0]["source_fact_keys"] = [key]
                with self.assertRaisesRegex(ValueError, error):
                    validate_editorial_selection(self.ledger, brief)

    def test_punctuation_cannot_make_one_question_two_candidates(self):
        champion, challenger = self.brief["editorial_selection"]["candidates"]
        challenger["question"] = champion["question"].replace("？", " ? ")
        with self.assertRaisesRegex(ValueError, "DUPLICATE_QUESTION"):
            validate_editorial_selection(self.ledger, self.brief)

    def test_recut_exhibit_cannot_leave_a_stale_lead_reference(self):
        with self.assertRaisesRegex(ValueError, "EXHIBIT_NOT_IN_PUBLICATION"):
            validate_editorial_selection(self.ledger, self.brief, figures=[{"id": "balance"}])
        result = validate_editorial_selection(self.ledger, self.brief,
                                              figures=[{"id": "cash-bridge"}])
        self.assertEqual(result["lead_thesis_id"], "cash")

    def test_sparse_source_can_use_a_text_led_answer(self):
        self.brief["editorial_selection"]["lead_exhibit"]["figure_id"] = None
        self.assertIsNotNone(validate_editorial_selection(self.ledger, self.brief, figures=[]))
