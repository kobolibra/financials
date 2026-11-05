#!/usr/bin/env python3
"""Hostile cases: a passing figure count cannot hide the V10 mobile P0."""
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("aei_policy", HERE / "audit_aei_editorial_delivery.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def html(css: str, body="<figure><svg></svg><table></table></figure>") -> bytes:
    return ("<!doctype html><html><head><style>" + css
            + "</style></head><body>" + body + "</body></html>").encode()


class AeiEditorialDeliveryTests(unittest.TestCase):
    def test_old_v10_sankey_scroll_is_explicit_fail(self):
        bad = ("@media(max-width:560px){.graphic-svg{display:none}"
               ".graphic-svg.sankey-svg{display:block;overflow-x:auto}"
               ".graphic-svg.sankey-svg svg{width:850px;min-width:850px;max-width:none}}")
        result = mod.inspect_html("600036", html(bad, "<figure><svg aria-label='财务桑基图'></svg><table></table></figure>"))
        self.assertIn("MOBILE_OMITS_ALL_NON_SANKEY_FINANCIAL_GRAPHS", result["source_code_structural_failures"])
        self.assertIn("MOBILE_SANKEY_FIXED_WIDE_IN_SMALL_HORIZONTAL_PANE", result["source_code_structural_failures"])
        self.assertEqual(result["actual_1440_768_390_chromium"], "NOT_CHECKED")

    def test_not_all_mobile_graphs_are_hidden_in_safe_structure(self):
        good = ("@media(max-width:560px){.finance-desktop{display:none}"
                ".finance-mobile{display:block;overflow:visible}"
                ".finance-mobile svg{max-width:100%;width:100%}}")
        result = mod.inspect_html("600036", html(good, "<figure><svg></svg><table></table></figure>"))
        self.assertEqual(result["structural_status"], "PASS_STATIC_SCOPE_ONLY")
        self.assertEqual(result["editorial_visual_5_second_read"], "NOT_CHECKED")

    def test_a_fabricated_mobile_fix_with_hidden_other_figures_fails(self):
        bad = ("@media(max-width:560px){.graphic-svg{display:none}"
               ".graphic-svg.sankey-svg{display:block}"
               ".graphic-svg.sankey-svg svg{width:330px;min-width:330px}}")
        result = mod.inspect_html("688111", html(bad))
        self.assertIn("MOBILE_OMITS_ALL_NON_SANKEY_FINANCIAL_GRAPHS", result["source_code_structural_failures"])

    def test_figure_count_cannot_replace_accessible_source(self):
        bad = "<figure><svg></svg></figure>" * 12
        result = mod.inspect_html("688111", html("", bad))
        self.assertIn("NO_INDEPENDENT_FIGURE_SVG_AND_ACCESSIBLE_SOURCE_TABLE", result["source_code_structural_failures"])

    def test_iframe_embedded_company_report_is_forbidden(self):
        result = mod.inspect_html("688111", html("", "<figure><svg></svg><table></table></figure><iframe></iframe>"))
        self.assertIn("STANDALONE_REPORT_HAS_IFRAME", result["source_code_structural_failures"])

    def test_no_synthetic_browser_pass(self):
        good = mod.inspect_html("688111", html("", "<figure><svg></svg><table></table></figure>"))
        self.assertEqual(good["sankey_exact_yuan_geometry"], "NOT_CHECKED")
        self.assertEqual(good["real_second_human_art_director"], "NOT_CHECKED")


if __name__ == "__main__":
    unittest.main()
