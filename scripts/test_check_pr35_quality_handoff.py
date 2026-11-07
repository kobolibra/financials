"""Hostile zero-memory handoff contract: reject stale screenshot or source reuse."""
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path
from check_pr35_quality_handoff import (
    ROOT, CODES, MANIFEST, check_repo,
    jread, validate_artifact_integrity, validate_handoff_documents,
)


def evidence():
    active=jread(ROOT,MANIFEST)
    build=jread(ROOT,"research/rebuild-v10/build-manifest.json")
    browser=jread(ROOT,"research/rebuild-v10/real-browser-qa/result.json")
    typed=jread(ROOT,"research/rebuild-v10/strict-semantic-audit.json")
    catalog=jread(ROOT,"site/research_catalog.json")
    pages={c:(ROOT/"public/research/2026-h1-v10"/(c+".html")).read_bytes()
           for c in CODES}
    return active,build,browser,typed,pages,catalog


class ActivePR35HandoffTests(unittest.TestCase):
    def test_repo_candidate_has_one_current_sha_bound_contract(self):
        self.assertEqual(check_repo(),[])

    def test_changed_published_page_revokes_original_build_and_browser_receipt(self):
        args=list(evidence())
        pages=dict(args[4])
        pages["688111"]=pages["688111"]+b"\n<!-- unreviewed production edit -->\n"
        args[4]=pages
        errors=validate_artifact_integrity(*args)
        self.assertIn("SOURCE_REBUILD_MANIFEST_SHA_DRIFT_688111",errors)
        self.assertIn("FINANCIAL_SEMANTICS_NOT_EXACT_PR_HTML_688111",errors)
        self.assertIn("STALE_SOURCE_SHA_CJK_BROWSER_688111_390",errors)

    def test_forged_visual_screenshot_receipt_rejected(self):
        args=list(evidence())
        browser=copy.deepcopy(args[2])
        for record in browser["cases"]:
            if record["code"]=="600519" and record["width"]==390:
                record["html_sha256"]="0"*64
        args[2]=browser
        errors=validate_artifact_integrity(*args)
        self.assertIn("STALE_SOURCE_SHA_CJK_BROWSER_600519_390",errors)

    def test_missing_research_original_money_inset_rejected(self):
        args=list(evidence())
        pages=dict(args[4])
        pages["600519"]=pages["600519"].replace(
            b'data-local-inset-source="other_rev"',
            b'data-synthetic-decoration="other_rev"')
        args[4]=pages
        errors=validate_artifact_integrity(*args)
        self.assertTrue(any(e.startswith("MOUTAI_TINY_NEGATIVE_GP_EDITORIAL_MISSING_")
                            for e in errors))

    def test_wrong_wps_desktop_layout_rejected(self):
        args=list(evidence())
        pages=dict(args[4])
        pages["688111"]=pages["688111"].replace(
            b'data-layout="desktop-editorial"',
            b'data-layout="mobile-stretched"',1)
        args[4]=pages
        errors=validate_artifact_integrity(*args)
        self.assertIn("WPS_NO_INDEPENDENT_THREE_STAGE_DESKTOP",errors)

    def test_stretched_330_desktop_moutai_cannot_be_certified(self):
        args=list(evidence())
        pages=dict(args[4])
        pages["600519"]=pages["600519"].replace(
            b'data-layout="desktop-editorial"',
            b'data-layout="stretched-mobile"',1)
        args[4]=pages
        errors=validate_artifact_integrity(*args)
        self.assertIn("MOUTAI_DESKTOP_IS_ONLY_A_STRETCHED_330_PHONE_CHART",errors)

    def test_false_human_and_main_deployment_certification_rejected(self):
        args=list(evidence())
        active=copy.deepcopy(args[0])
        active["review_state"]="HUMAN_AEI_CERTIFIED_AND_ON_MAIN"
        active["current_art_direction"]["status"]="PASS"
        args[0]=active
        errors=validate_artifact_integrity(*args)
        self.assertIn("PREMATURE_RESEARCH_OR_DEPLOYMENT_CERTIFICATION",errors)
        self.assertIn("HUMAN_OR_GENERALIZATION_CERTIFICATION_NOT_PROVEN",errors)

    def test_no_handoff_anchor_or_main_belongs_to_branch_rejected(self):
        active=jread(ROOT,MANIFEST)
        status=jread(ROOT,"project-status.json")
        texts=lambda p:(ROOT/p).read_text(encoding="utf8")
        args=[
            active,status,
            texts("START_HERE.md"),texts("PROJECT_STATE.md"),texts("AGENTS.md"),
            texts("skills/ashare-financial-storytelling/SKILL.md"),
            texts("docs/HANDOFF_PROTOCOL.md"),
            texts("docs/AEI_RESEARCH_EDITORIAL_SCORECARD.md"),
        ]
        self.assertEqual(validate_handoff_documents(*args),[])
        args[2]=args[2].replace("ACTIVE_PR35_HANDOFF.md","OLD_CHAT_MEMORY")
        self.assertIn("START_HERE_HAS_NO_ACTIVE_PR_HANDBACK",
                      validate_handoff_documents(*args))
        args[2]=texts("START_HERE.md")
        args[1]=copy.deepcopy(status)
        args[1]["production_branch"]="quality/aei-sankey-source-contract-v1"
        self.assertIn("IMPROPER_PRODUCTION_BRANCH_CHANGE",
                      validate_handoff_documents(*args))


if __name__=="__main__":
    unittest.main()
