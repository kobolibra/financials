"""Static regression for genuinely two-layout 601628 live source verification.

The full production HTML passed its exact SHA, original 13-source decision
values and four CAS formulas, but an older live test miscounted 10 source
desktop SVGs + premium + five signed bridges as an old fixed 11 count.
"""
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
        self.assertNotRegex(s,r'page\.locator\("figure\.figure svg"\)\.count\(\)==(?:10|11),')
        self.assertIn('count()==10+1+len(FAMILIES)',s)
        self.assertIn('figure.figure details.audit',s)
        self.assertIn('figure.figure .mobile-chart',s)
        self.assertIn('SOURCE_PREMIUM_NOT_CLOSED',s)
        self.assertIn('LIVE_ORIGINAL_YUAN_RIBBON_GEOMETRY_FALSE',s)
        self.assertNotIn('rect.money-source',s)
        self.assertNotIn('rect.money-sink',s)

    def test_live_signed_bridges_keep_independent_source_and_export_checks(self):
        s=LIVE.read_text()
        for required in ('from qa_signed_geometry import FAMILIES,check_signed_svg,expected_steps',
                         'if family["family"] in FAMILIES:',
                         'check_signed_svg(svg.evaluate',
                         'LIVE_SOURCE_TABLE_DEPENDENCIES_INCOMPLETE',
                         'LIVE_SOURCE_TABLE_EXACT_YUAN',
                         'LIVE_SOURCE_TABLE_PDF_PHYSICAL_PAGE',
                         'LIVE_EXPORTED_HIDDEN_LAYOUT',
                         'LIVE_EXPORT_VISIBLE_VECTOR_DRIFT',
                         'check_signed_svg(raw,family,report)',
                         'assert len(family["rows"])>=5',
                         'LIVE_MOBILE_MONEY_BAR_INFLATED'):
            self.assertIn(required,s)
        self.assertIn('if width<=850:',s)

    def test_verified_commit_uses_actual_ci_sha_or_local_git_and_rejects_bad_values(self):
        # Load only the pure resolver; importing the live script would browse
        # production and is intentionally not a unit-test side effect.
        import ast, os, re
        tree=ast.parse(LIVE.read_text())
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='verified_git_commit')
        env={'os':os,'re':re}
        exec(compile(ast.Module(body=[function],type_ignores=[]),str(LIVE),'exec'),env)
        resolve=env['verified_git_commit']
        actual='e72bae81a9df22f54db7ba365f25bb8160c34111'
        self.assertEqual(resolve({'GITHUB_SHA':actual},lambda:'a'*40),actual)
        self.assertEqual(resolve({},lambda:'b'*40),'b'*40)
        for bad in ('short','x'*40,'a'*39,'a'*40+'\n'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                resolve({'GITHUB_SHA':bad},lambda:'a'*40)

    def test_live_release_checks_exact_html_source_decision_and_layout(self):
        s=LIVE.read_text(encoding="utf-8")
        for required in (
            "expected_sha", "expected_home", "b.body()", "decisions(report)",
            "LIVE_INSURER_SOURCE_MONEY_FALSE", "LIVE_INSURER_DECISION_FORMULA_FALSE",
            "LIVE_390_MOBILE_FULL_TEN_FIGURES_NOT_VISIBLE",
            "SOURCE_PREMIUM_NOT_CLOSED", "LIVE_ORIGINAL_YUAN_RIBBON_GEOMETRY_FALSE",
            "all_11_issuer_external_routes", "MISSING_PRODUCTION_THREE_VIEWS",
        ):
            self.assertIn(required,s)
        self.assertIn('assert len(results["screenshots"])==9',s)

if __name__=="__main__":
    unittest.main()
