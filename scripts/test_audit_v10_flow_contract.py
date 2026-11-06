#!/usr/bin/env python3
"""Red-team: source-typed issuer financial flow and immutable publication debt."""
from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "v10_flow_audit", ROOT / "scripts/audit_v10_flow_contract.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def fixture_copy(tmp: Path) -> None:
    paths = [
        "research/rebuild-v10/extras.json",
        "research/rebuild-v10/input-ledgers/688111.json",
        "research/rebuild-v10/input-ledgers/600519.json",
        "research/rebuild-v10/input-ledgers/000333.json",
        "research/visual-audit/quality-debt.json",
        "site/research_catalog.json",
    ]
    for code in MOD.CODES:
        paths.append("public/research/2026-h1-v10/" + code + ".html")
    for path in paths:
        dst = tmp / path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, dst)


class TypedV10FlowContractTests(unittest.TestCase):
    def test_actual_issuer_types_are_industry_specific(self):
        expected = {
            "688111": "TYPE_A_SOURCE_OWN_COST_GP",
            "600519": "TYPE_C_SANKEY_OMITTED",
            "000333": "TYPE_B_GROUP_ONLY_GROSS_ALLOCATION",
            "600036": "BANK_NET_INCOME_TO_OPERATING_PROFIT",
        }
        for code, kind in expected.items():
            with self.subTest(code=code):
                row = MOD.classify(ROOT, code)
                self.assertEqual(row["kind"], kind)
        self.assertEqual(MOD.classify(ROOT, "600519")["reason"],
                         "AT_LEAST_ONE_PRODUCT_HAS_NEGATIVE_GROSS_PROFIT_OR_COST")

    def test_current_four_source_bound_published_figures_remain_unfixed(self):
        result = MOD.audit(ROOT)
        self.assertEqual(result["count"], 4)
        self.assertEqual(result["conclusion"], "KNOWN_HISTORICAL_FLOW_DEBT_NOT_CERTIFIED")
        self.assertFalse(result["blocking_violations"])
        for row in result["records"]:
            self.assertTrue(row["published_figure_issues"], row["issuer"])
            self.assertTrue(row["historical_exact_source_waiver"])
            self.assertEqual(row["current_figure_semantic_status"], "FAIL")
            self.assertEqual(row["actual_svg_path_geometric_widths"], "NOT_CHECKED")

    def test_strict_release_must_reject_all_legacy_defects(self):
        result = MOD.audit(ROOT, strict=True)
        self.assertEqual(len(result["blocking_violations"]), 4)
        self.assertEqual(result["conclusion"], "FAIL")

    def test_modifying_any_one_old_report_revokes_exact_sha_waiver(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            fixture_copy(tmp)
            page = tmp / "public/research/2026-h1-v10/688111.html"
            page.write_bytes(page.read_bytes() + b"\n<!-- revision, old SHA waiver expired -->\n")
            result = MOD.audit(tmp)
            self.assertEqual([v["issuer"] for v in result["blocking_violations"]], ["688111"])
            self.assertEqual(result["conclusion"], "FAIL")

    def test_kingsoft_a_requires_real_per_source_disclosed_cost_metadata(self):
        expected = MOD.classify(ROOT, "688111")
        before = '<figure data-flow-kind="TYPE_A_SOURCE_OWN_COST_GP">会计守恒财务桑基图'
        bad = MOD.inspect_published_figure("688111", expected, before + "</figure>")
        self.assertEqual(sum("PATH_OR_SOURCE_METADATA_MISSING" in x for x in bad), 4)
        paths = "".join(
            '<path data-source-id="{}" data-revenue-yuan="{}" data-cost-yuan="{}" data-gp-yuan="{}"/>'.format(*r)
            for r in expected["source_own_cost_gp"]
        )
        self.assertFalse(MOD.inspect_published_figure("688111", expected, before + paths + "</figure>"))

    def test_moutai_negative_product_profit_cannot_be_drawn_positive(self):
        expected = MOD.classify(ROOT, "600519")
        weak = ('<figure data-flow-kind="TYPE_C_SANKEY_OMITTED">'
                '会计守恒财务桑基图 FINANCIAL_SANKEY_OMITTED_WITH_SOURCE_REASON '
                + expected["reason"] + '</figure>')
        self.assertIn("NEGATIVE_PRODUCT_GP_ILLEGAL_POSITIVE_SANKEY",
                      MOD.inspect_published_figure("600519", expected, weak))
        correct = ('<figure data-flow-kind="TYPE_C_SANKEY_OMITTED">'
                   'FINANCIAL_SANKEY_OMITTED_WITH_SOURCE_REASON '
                   + expected["reason"] + ' 有符号产品毛利瀑布</figure>')
        self.assertFalse(MOD.inspect_published_figure("600519", expected, correct))

    def test_midea_group_only_needs_visible_no_product_gp_warning(self):
        expected = MOD.classify(ROOT, "000333")
        weak = ('<figure data-flow-kind="TYPE_B_GROUP_ONLY_GROSS_ALLOCATION">'
                '会计守恒财务桑基图<details>PRODUCT_LEVEL_GP_NOT_ESTABLISHED</details></figure>')
        self.assertIn("GROUP_ONLY_NO_VISIBLE_PRODUCT_GP_LIMITATION",
                      MOD.inspect_published_figure("000333", expected, weak))
        good = ('<figure data-flow-kind="TYPE_B_GROUP_ONLY_GROSS_ALLOCATION">'
                '会计守恒财务桑基图 · PRODUCT_LEVEL_GP_NOT_ESTABLISHED</figure>')
        self.assertFalse(MOD.inspect_published_figure("000333", expected, good))

    def test_bank_cannot_be_labeled_as_industrial_gross_profit(self):
        expected = MOD.classify(ROOT, "600036")
        bad = ('<figure data-flow-kind="BANK_NET_INCOME_TO_OPERATING_PROFIT">'
               '银行净利息收入 → 毛利的会计守恒财务桑基图</figure>')
        self.assertIn("BANK_FALSE_INDUSTRIAL_GROSS_PROFIT_LABEL",
                      MOD.inspect_published_figure("600036", expected, bad))
        good = ('<figure data-flow-kind="BANK_NET_INCOME_TO_OPERATING_PROFIT">'
                '银行净利息收入 → 支出与营业利润 · 会计守恒财务桑基图</figure>')
        self.assertFalse(MOD.inspect_published_figure("600036", expected, good))

    def test_original_cost_tamper_triggers_decimal_conservation_failure(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            fixture_copy(tmp)
            p = tmp / "research/rebuild-v10/input-ledgers/688111.json"
            doc = json.loads(p.read_text(encoding="utf8"))
            old = doc["facts"]["wps365_cost"]["yuan"]
            doc["facts"]["wps365_cost"]["yuan"] = str(
                __import__("decimal").Decimal(old) + __import__("decimal").Decimal("0.01"))
            p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf8")
            with self.assertRaisesRegex(ValueError, "SOURCE_COST_SUM_NOT_GROUP_COST"):
                MOD.classify(tmp, "688111")


if __name__ == "__main__":
    unittest.main()
