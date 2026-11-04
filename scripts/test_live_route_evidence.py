"""Hostile generic issuer live-route evidence, not bound to a single issuer."""
import unittest
from research.shared.live_route_evidence import (
    verify_issuer_article_url,verify_back_to_library,make_live_navigation_receipt
)
ORIGIN="https://financials-in-visuals.pages.dev"
class LiveRouteEvidenceTests(unittest.TestCase):
    def test_real_cloudflare_pretty_issuer(self):
        a=f"{ORIGIN}/601628"
        b=f"{ORIGIN}/#companies"
        self.assertEqual(make_live_navigation_receipt(report_url=a,back_url=b,code="601628",origin=ORIGIN),
            {"actual_dedicated_article_final_url":a,"actual_return_to_library_url":b})
    def test_legacy_html_route_also_is_true_company(self):
        self.assertEqual(verify_issuer_article_url(f"{ORIGIN}/601628.html",code="601628",origin=ORIGIN),
            f"{ORIGIN}/601628.html")
    def test_home_return_must_never_masquerade_as_article(self):
        with self.assertRaisesRegex(AssertionError,"ARTICLE_ROUTE_INCORRECT_OR_HOME_REDIRECT"):
            make_live_navigation_receipt(report_url=f"{ORIGIN}/#companies",
                back_url=f"{ORIGIN}/#companies",code="601628",origin=ORIGIN)
    def test_other_issuer_is_not_601628(self):
        with self.assertRaisesRegex(AssertionError,"ARTICLE_ROUTE_INCORRECT_OR_HOME_REDIRECT"):
            verify_issuer_article_url(f"{ORIGIN}/600276",code="601628",origin=ORIGIN)
    def test_third_party_domain_impostor(self):
        with self.assertRaisesRegex(AssertionError,"ARTICLE_ORIGIN_MISMATCH"):
            verify_issuer_article_url(f"{ORIGIN}.evil.com/601628",code="601628",origin=ORIGIN)
    def test_https_required(self):
        with self.assertRaisesRegex(AssertionError,"ARTICLE_URL_NOT_HTTPS"):
            verify_issuer_article_url("http://financials-in-visuals.pages.dev/601628",code="601628",origin=ORIGIN)
    def test_pretty_route_lookalike_not_accepted(self):
        with self.assertRaisesRegex(AssertionError,"ARTICLE_ROUTE_INCORRECT_OR_HOME_REDIRECT"):
            verify_issuer_article_url(f"{ORIGIN}/601628-copy",code="601628",origin=ORIGIN)
    def test_root_back_only_with_actual_anchor(self):
        for bad in [f"{ORIGIN}/",f"{ORIGIN}/601628#companies",f"{ORIGIN}/#top",f"{ORIGIN}/?page=11#companies"]:
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(AssertionError,"BACK_NOT_PRIMARY_DIRECTORY"):
                    verify_back_to_library(bad,origin=ORIGIN)
    def test_invalid_code_rejected(self):
        with self.assertRaisesRegex(AssertionError,"INVALID_ISSUER_CODE"):
            verify_issuer_article_url(f"{ORIGIN}/601628",code="60162",origin=ORIGIN)
if __name__=="__main__":unittest.main()
