#!/usr/bin/env python3
"""Proof that a new company cannot inherit a 900px mobile financial scroll box."""
import copy,json,unittest
from pathlib import Path
from check_visual_editorial_policy import validate_audit,ROOT

class VisualPublicationPolicyRedTeam(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=ROOT/"research/visual-audit"
        cls.census=json.loads((path/"cross-issuer-visual-audit.json").read_text())
        cls.debt=json.loads((path/"quality-debt.json").read_text())
    def fail_check(self,census,needle):
        errors,_=validate_audit(census,self.debt)
        self.assertTrue(any(needle in x for x in errors),errors)
    def test_original_ten_are_explicit_failed_visual_debt_not_pass(self):
        errors,legacy=validate_audit(self.census,self.debt)
        self.assertEqual(errors,[])
        self.assertEqual(len(legacy),10)
        self.assertEqual({x["code"] for x in legacy},
          {"300394","300308","300502","600036","688111","600519","000333","688220","600900","600276"})
        self.assertTrue(all(x["status"]=="FAIL_BASELINE_ONLY" for x in legacy))
    def test_one_cropped_390px_new_issuer_must_fail_even_when_body_not_scrolled(self):
        d=copy.deepcopy(self.census)
        subset=[copy.deepcopy(x) for x in d["records"] if x["code"]=="300394"]
        for row in subset:
            row["code"]="601919"
            row["source_html_sha256"]="1"*64
            row["evidenceTables"]=10
        d["records"]+=subset
        d["count_issuers"]+=1
        d["count_viewport_tests"]+=3
        self.fail_check(d,"VISUAL_NO_NEW_OR_CHANGED_COMPANY_MAY_HAVE_390_INNER_SCROLL 601919")
    def test_hardcoded_legacy_old_html_allowed_only_while_exact_source_bytes_unchanged(self):
        d=copy.deepcopy(self.census)
        for row in d["records"]:
            if row["code"]=="300394":row["source_html_sha256"]="a"*64
        self.fail_check(d,"VISUAL_NO_NEW_OR_CHANGED_COMPANY_MAY_HAVE_390_INNER_SCROLL 300394")
    def test_one_of_ten_issuer_mobile_reading_alternatives_lost(self):
        d=copy.deepcopy(self.census)
        for row in d["records"]:
            if row["code"]=="601628" and row["viewport"][0]==390:row["mobileAltFigures"]=0
        self.fail_check(d,"VISUAL_601628_MOBILE_MONEY_GRAMMAR_REGRESSED 601628")
    def test_new_company_cannot_call_source_free_cards_professional_finance_graphs(self):
        d=copy.deepcopy(self.census)
        subset=[copy.deepcopy(x) for x in d["records"] if x["code"]=="601628"]
        for row in subset:
            row["code"]="601919";row["source_html_sha256"]="1"*64;row["evidenceTables"]=0
        d["records"]+=subset;d["count_issuers"]+=1;d["count_viewport_tests"]+=3
        self.fail_check(d,"VISUAL_NEW_ISSUER_MUST_HAVE_SOURCE_LINKED_FIGURE_TABLES 601919")
    def test_no_company_can_hide_page_wide_mobile_overflow(self):
        d=copy.deepcopy(self.census)
        for row in d["records"]:
            if row["code"]=="601628" and row["viewport"][0]==390:
                row["body"]=590
        self.fail_check(d,"VISUAL_ROOT_OVERFLOW 601628")
    def test_new_single_family_zero_real_source_text_rejected(self):
        d=copy.deepcopy(self.census)
        subset=[copy.deepcopy(x) for x in d["records"] if x["code"]=="601628"]
        for row in subset:
            row["code"]="601919";row["source_html_sha256"]="1"*64;row["realSvgTextLabels"]=0
        d["records"]+=subset;d["count_issuers"]+=1;d["count_viewport_tests"]+=3
        self.fail_check(d,"VISUAL_NEW_ISSUER_HAS_NO_READABLE_ACTUAL_FINANCE_SVG_TEXT 601919")
    def test_missing_real_phone_viewport_not_replaced_by_fake_success(self):
        d=copy.deepcopy(self.census)
        d["records"]=[x for x in d["records"] if not(x["code"]=="300502" and x["viewport"][0]==390)]
        d["count_viewport_tests"]-=1
        self.fail_check(d,"VISUAL_MISSING_ACTUAL_THREE_CJK_VIEWPORTS 300502")

if __name__=="__main__":unittest.main(verbosity=2)
