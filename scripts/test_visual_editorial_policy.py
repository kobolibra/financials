#!/usr/bin/env python3
"""Proof that a new company cannot inherit a 900px mobile financial scroll box."""
import copy,json,unittest
from pathlib import Path
from unittest import mock
from check_visual_editorial_policy import validate_audit,validate_current_published_files,ROOT

class VisualPublicationPolicyRedTeam(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=ROOT/"research/visual-audit"
        cls.census=json.loads((path/"cross-issuer-visual-audit.json").read_text())
        cls.debt=json.loads((path/"quality-debt.json").read_text())
    def fail_check(self,census,needle):
        errors,_=validate_audit(census,self.debt)
        self.assertTrue(any(needle in x for x in errors),errors)
    def test_current_issuer_hashes_are_not_conflated_with_historical_fail_screenshots(self):
        errors,fixed,stale=validate_current_published_files(ROOT,self.census,self.debt)
        self.assertEqual(errors,[])
        expected={"300308","300394","300502","600900","600276","601628"}
        old=self.debt["legacy_source_frozen_allowlist_for_preexisting_only"]["688220"]
        import hashlib
        if hashlib.sha256((ROOT/"public/688220.html").read_bytes()).hexdigest()!=old:expected.add("688220")
        v10={"600036","688111","600519","000333"}
        for code in v10:
            source_hash=hashlib.sha256(
                (ROOT/"public/research/2026-h1-v10"/(code+".html")).read_bytes()).hexdigest()
            if source_hash!=self.debt["legacy_source_frozen_allowlist_for_preexisting_only"][code]:
                expected.add(code)
        catalog=json.loads((ROOT/"site/research_catalog.json").read_text())
        expected.update(r["code"] for r in catalog["issuers"] if r.get("source_publication"))
        self.assertEqual({x["code"] for x in fixed},expected)
        self.assertEqual(set(stale),
            (v10-expected) | ({"688220"} if "688220" not in expected else set()))
    def test_new_dossier_cannot_inherit_historical_census_or_stale_current_proof(self):
        catalog=json.loads((ROOT/'site/research_catalog.json').read_text())
        for issuer in catalog['issuers']:
            if not issuer.get('source_publication'):continue
            original=Path.read_text
            def corrupt(path,*args,**kwargs):
                raw=original(path,*args,**kwargs)
                if str(path).endswith(issuer['source_publication']+'/visual-qa/result.json'):
                    d=json.loads(raw);d['cases']=[c for c in d['cases'] if c['width']!=390]
                    return json.dumps(d)
                return raw
            with mock.patch.object(Path,'read_text',corrupt):
                errors,_,_=validate_current_published_files(ROOT,self.census,self.debt)
            self.assertIn('VISUAL_NEW_SOURCE_DOSSIER_CURRENT_COMPLETE_PROOF_REQUIRED '+issuer['code'],errors)
    def test_new_v10_report_cannot_steal_wrong_CJK_sha_receipt(self):
        code="688111"
        import hashlib
        page=ROOT/"public/research/2026-h1-v10/688111.html"
        old=self.debt["legacy_source_frozen_allowlist_for_preexisting_only"][code]
        if hashlib.sha256(page.read_bytes()).hexdigest()==old:
            self.skipTest("Old source remains deliberately failed; no new V10 receipt to poison yet")
        original=Path.read_text
        def corrupt(path,*args,**kwargs):
            data=original(path,*args,**kwargs)
            if str(path).endswith("research/rebuild-v10/real-browser-qa/result.json"):
                doc=json.loads(data)
                for x in doc["cases"]:
                    if x["code"]==code and x["width"]==390:
                        x["html_sha256"]="0"*64
                return json.dumps(doc)
            return data
        with mock.patch.object(Path,"read_text",new=corrupt):
            errors,_,_=validate_current_published_files(ROOT,self.census,self.debt)
        self.assertIn("VISUAL_CHANGED_V10_ORIGINAL_SOURCE_ALL_FINANCE_3_VIEWPORT_RECEIPT_INVALID "+code,errors)

    def test_new_v10_report_cannot_hide_a_phone_finance_exhibit(self):
        code="600519"
        import hashlib
        page=ROOT/"public/research/2026-h1-v10/600519.html"
        old=self.debt["legacy_source_frozen_allowlist_for_preexisting_only"][code]
        if hashlib.sha256(page.read_bytes()).hexdigest()==old:
            self.skipTest("Old source remains deliberately failed; no new V10 receipt to poison yet")
        original=Path.read_text
        def corrupt(path,*args,**kwargs):
            data=original(path,*args,**kwargs)
            if str(path).endswith("research/rebuild-v10/real-browser-qa/result.json"):
                doc=json.loads(data)
                for x in doc["cases"]:
                    if x["code"]==code and x["width"]==390:
                        x["figures"][0]["scroll_free"]="FAIL"
                return json.dumps(doc)
            return data
        with mock.patch.object(Path,"read_text",new=corrupt):
            errors,_,_=validate_current_published_files(ROOT,self.census,self.debt)
        self.assertIn("VISUAL_CHANGED_V10_ORIGINAL_SOURCE_ALL_FINANCE_3_VIEWPORT_RECEIPT_INVALID "+code,errors)

    def test_insurer_new_original_decision_table_and_source_money_cannot_be_falsified(self):
        original=Path.read_text
        def falsify_11th_original_source_table(path,*args,**kwargs):
            raw=original(path,*args,**kwargs)
            if str(path).endswith("research/issuers/601628/visual-qa/result.json"):
                obj=json.loads(raw)
                # Ten original graph source tables are not enough after
                # a new independently sourced 13-fact investment decision.
                obj["source_table_count"]=10
                return json.dumps(obj)
            return raw
        with mock.patch.object(Path,"read_text",new=falsify_11th_original_source_table):
            errors,_,_=validate_current_published_files(ROOT,self.census,self.debt)
        self.assertIn("VISUAL_601628_CURRENT_CANDIDATE_THREE_CJK_WIDTHS_OR_SHA_MISMATCH",errors)

        def falsify_decision_source(path,*args,**kwargs):
            raw=original(path,*args,**kwargs)
            if str(path).endswith("/public/601628.html"):
                return raw.replace('data-source-key="insurance_finance"','data-hidden-source-key="insurance_finance"')
            return raw
        with mock.patch.object(Path,"read_text",new=falsify_decision_source):
            errors,_,_=validate_current_published_files(ROOT,self.census,self.debt)
        self.assertIn("VISUAL_601628_CURRENT_CANDIDATE_THREE_CJK_WIDTHS_OR_SHA_MISMATCH",errors)

    def test_old_report_changed_after_census_must_have_new_three_view_source_proof(self):
        original=Path.read_bytes
        def changed(path):
            data=original(path)
            if str(path).endswith("/public/300394.html"):return data+b"\nFORGED_NEW_ARTICLE_CHANGE"
            return data
        with mock.patch.object(Path,"read_bytes",new=changed):
            errors,fixed,unresolved=validate_current_published_files(ROOT,self.census,self.debt)
        self.assertTrue(any("VISUAL_CHANGED_OPTICAL_ISSUER_ORIGINAL_MONEY_SOURCE_390_BROWSER_RECEIPT_INVALID 300394" in x for x in errors),errors)
    def test_manufactured_bogus_issuer_finance_receipt_SHA_must_fail(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            data=original(path,*args,**kwargs)
            if str(path).endswith("research/issuers/600900/visual-qa/result.json"):
                doc=json.loads(data)
                doc["html_sha256"]="f"*64
                return json.dumps(doc)
            return data
        with mock.patch.object(Path,"read_text",new=changed):
            errors,_,_=validate_current_published_files(ROOT,self.census,self.debt)
        self.assertTrue(any("VISUAL_CHANGED_ISSUER_BROWSER_SOURCE_SHA_OR_390_NATIVE_MONEY_EVIDENCE_INVALID 600900" in x for x in errors),errors)
    def test_source_matched_report_cannot_fake_screenshot_mobile_native_figure_visibility(self):
        original=Path.read_text
        def changed(path,*args,**kwargs):
            data=original(path,*args,**kwargs)
            if str(path).endswith("research/issuers/600276/visual-qa/result.json"):
                doc=json.loads(data)
                doc["all_eight_390px_native_money_visuals_readable_and_source_reconciled"]="FAIL"
                return json.dumps(doc)
            return data
        with mock.patch.object(Path,"read_text",new=changed):
            errors,_,_=validate_current_published_files(ROOT,self.census,self.debt)
        self.assertTrue(any("VISUAL_CHANGED_ISSUER_BROWSER_SOURCE_SHA_OR_390_NATIVE_MONEY_EVIDENCE_INVALID 600276" in x for x in errors),errors)

    def test_optical_source_receipt_cannot_be_rebound_to_a_forged_article(self):
        original=Path.read_text
        def corrupt(path,*args,**kwargs):
            data=original(path,*args,**kwargs)
            if str(path).endswith("optical-native-visual-qa/result.json"):
                obj=json.loads(data)
                for z in obj["cases"]:
                    if z["issuer"]=="300394":z["sha256"]="0"*64
                return json.dumps(obj)
            return data
        with mock.patch.object(Path,"read_text",new=corrupt):
            errors,_,_=validate_current_published_files(ROOT,self.census,self.debt)
        self.assertIn("VISUAL_CHANGED_OPTICAL_ISSUER_ORIGINAL_MONEY_SOURCE_390_BROWSER_RECEIPT_INVALID 300394",errors)

    def test_optical_true_signed_geometry_missing_on_390_must_fail(self):
        original=Path.read_text
        def corrupt(path,*args,**kwargs):
            data=original(path,*args,**kwargs)
            if str(path).endswith("optical-native-visual-qa/result.json"):
                obj=json.loads(data)
                for z in obj["cases"]:
                    if z["issuer"]=="300502" and z["width"]==390:
                        z["signed_accounting_and_svg_geometry"]="FAIL"
                return json.dumps(obj)
            return data
        with mock.patch.object(Path,"read_text",new=corrupt):
            errors,_,_=validate_current_published_files(ROOT,self.census,self.debt)
        self.assertIn("VISUAL_CHANGED_OPTICAL_ISSUER_ORIGINAL_MONEY_SOURCE_390_BROWSER_RECEIPT_INVALID 300502",errors)

    def test_300308_rebuilt_original_pdf_page_cannot_accept_old_390_mobile_receipts(self):
        original=Path.read_text
        def corrupt(path,*args,**kwargs):
            data=original(path,*args,**kwargs)
            if str(path).endswith("optical-native-visual-qa-300308/result.json"):
                obj=json.loads(data)
                for z in obj["cases"]:
                    if z["issuer"]=="300308" and z["width"]==390:
                        z["native_mobile_finance_no_inner_scroll"]="FAIL"
                return json.dumps(obj)
            return data
        with mock.patch.object(Path,"read_text",new=corrupt):
            errors,_,_=validate_current_published_files(ROOT,self.census,self.debt)
        self.assertIn("VISUAL_CHANGED_OPTICAL_ISSUER_ORIGINAL_MONEY_SOURCE_390_BROWSER_RECEIPT_INVALID 300308",errors)

    def test_300308_different_pdf_sha_report_fingerprint_must_not_reclassify_old_fail(self):
        original=Path.read_text
        def corrupt(path,*args,**kwargs):
            data=original(path,*args,**kwargs)
            if str(path).endswith("optical-native-visual-qa-300308/result.json"):
                obj=json.loads(data)
                for z in obj["cases"]:
                    if z["issuer"]=="300308": z["sha256"]="f"*64
                return json.dumps(obj)
            return data
        with mock.patch.object(Path,"read_text",new=corrupt):
            errors,_,_=validate_current_published_files(ROOT,self.census,self.debt)
        self.assertIn("VISUAL_CHANGED_OPTICAL_ISSUER_ORIGINAL_MONEY_SOURCE_390_BROWSER_RECEIPT_INVALID 300308",errors)

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
