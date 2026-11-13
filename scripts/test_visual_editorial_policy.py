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
    def test_each_current_issuer_cannot_borrow_old_or_incomplete_evidence(self):
        catalog=json.loads((ROOT/'site/research_catalog.json').read_text())
        proof=catalog['figure_quality_contracts']['FULL_SOURCE_FIGURES_V1']['local_migration_receipt']
        original=Path.read_text
        for issuer in catalog['issuers']:
            for mode in ('sha','missing_phone','hidden_original','false_download','false_geometry','wrong_pdf','missing_primary','reading_layer','wrong_png'):
                def corrupt(path,*args,**kwargs):
                    raw=original(path,*args,**kwargs)
                    if str(path).endswith('site/research_catalog.json'):
                        scoped=json.loads(raw);scoped['issuers']=[issuer];return json.dumps(scoped)
                    if str(path).endswith(proof):
                        q=json.loads(raw);code=issuer['code'];cases=[c for c in q['cases'] if c['issuer']==code]
                        c=next(c for c in cases if c['width']==390)
                        if mode=='sha':c['html_sha256']='0'*64
                        if mode=='missing_phone':q['cases'].remove(c)
                        if mode=='hidden_original':c['figures'].pop()
                        if mode=='false_download':c['figures'][0]['visible_edition_download']='FAIL'
                        if mode=='false_geometry':c['figures'][0]['source_and_actual_geometry']='FAIL'
                        if mode=='wrong_pdf':q['issuers'][code]['pdf_sha256']='0'*64
                        if mode=='missing_primary':c['figures'][0]['grammar']='IMMUTABLE_PREEXISTING_SOURCE_V10_VECTOR'
                        if mode=='reading_layer':c['editorial_main_layer']='FAIL'
                        if mode=='wrong_png':c['figures'][0]['screenshot_sha256']='0'*64
                        return json.dumps(q)
                    return raw
                with self.subTest(code=issuer['code'],mode=mode),mock.patch.object(Path,'read_text',corrupt):
                    errors,_,_=validate_current_published_files(ROOT,self.census,self.debt)
                    self.assertIn('VISUAL_CURRENT_FULL_PROFIT_CHAIN_COMPLETE_PROOF_REQUIRED '+issuer['code'],errors)
    def test_changed_current_html_cannot_inherit_current_receipt(self):
        original=Path.read_bytes
        def changed(path):
            raw=original(path)
            return raw+b' FORGED' if str(path).endswith('/public/300394.html') else raw
        with mock.patch.object(Path,'read_bytes',changed):
            errors,_,_=validate_current_published_files(ROOT,self.census,self.debt)
        self.assertIn('VISUAL_CURRENT_FULL_PROFIT_CHAIN_COMPLETE_PROOF_REQUIRED 300394',errors)

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
