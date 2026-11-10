"""Static regression for genuinely two-layout 601628 live source verification.

The full production HTML passed its exact SHA, original 13-source decision
values and four CAS formulas, but an older live test miscounted 10 source
desktop SVGs + 1 independent mobile SVG as exactly 10 all-descendant SVGs.
"""
import ast
from pathlib import Path
import unittest

BASE=Path(__file__).resolve().parent
LIVE=BASE/"qa_cloudflare_live.py"

class LiveInsurerTwoLayoutContract(unittest.TestCase):
    def test_live_script_compiles_and_enforces_per_layout_finance_figures(self):
        s=LIVE.read_text(encoding="utf-8")
        compile(s,str(LIVE),"exec")
        self.assertIn('figure.figure .chart svg',s)
        self.assertIn("LIVE_TEN_ORIGINAL_DESKTOP_FINANCE_SVGS_MISSING",s)
        self.assertIn("LIVE_SOURCE_CONSERVED_NATIVE_INSURANCE_PREMIUM_SVG_MISSING",s)
        self.assertIn("LIVE_UNEXPECTED_DESKTOP_OR_MOBILE_SVG_FAMILY_COUNT",s)
        self.assertNotIn('page.locator("figure.figure svg").count()==10',s)
        self.assertIn('figure.figure details.audit',s)
        self.assertIn('figure.figure .mobile-chart',s)
        self.assertIn('figure.figure .chart .money-ribbon',s)

    def test_live_release_checks_exact_html_source_decision_and_layout(self):
        s=LIVE.read_text(encoding="utf-8")
        for required in (
            "expected_sha", "expected_home", "b.body()", "decisions(report)",
            "LIVE_INSURER_SOURCE_MONEY_FALSE", "LIVE_INSURER_DECISION_FORMULA_FALSE",
            "LIVE_390_MOBILE_FULL_TEN_FIGURES_NOT_VISIBLE",
            "LIVE_FINAL", "LIVE_WRONG_PREMIUM_TOTAL_GEOMETRY",
            "all_11_issuer_external_routes", "MISSING_PRODUCTION_THREE_VIEWS",
        ):
            if required=="LIVE_FINAL":
                self.assertIn("LIVE_WRONG_PREMIUM_TOTAL_SOURCE",s)
            else:
                self.assertIn(required,s)
        self.assertIn('assert len(results["screenshots"])==9',s)

if __name__=="__main__":
    unittest.main()
