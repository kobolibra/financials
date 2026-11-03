"""Adversarial tests prevent regressions that made prior-chat handoff unreliable."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from check_handoff import check_skill, check_catalog, check_current_state, check_repo, check_discovery

STATUS=json.loads((ROOT/"project-status.json").read_text())
CATALOG=json.loads((ROOT/"site/research_catalog.json").read_text())
HTML=(ROOT/"public/index.html").read_text()
SKILL=(ROOT/"skills/ashare-financial-storytelling/SKILL.md").read_text()
STATE=(ROOT/"PROJECT_STATE.md").read_text()
README=(ROOT/"README.md").read_text()


class HandoffGateTests(unittest.TestCase):
    def test_current_tree_is_consistent(self):
        self.assertEqual(check_repo(),[])
    def test_rejects_broken_codex_discovery_entry(self):
        wrapper=(ROOT/".agents/skills/ashare-financial-storytelling/SKILL.md").read_text()
        broken=wrapper.replace("description:","missing_description:",1)
        project=(ROOT/"docs/CHATGPT_PROJECT_INSTRUCTIONS.md").read_text()
        self.assertTrue(any("CODEX_SKILL_MISSING_DESCRIPTION" in e for e in check_discovery(STATUS,broken,project)))
    def test_rejects_fake_chatgpt_auto_skill_install(self):
        m=copy.deepcopy(STATUS)
        m["skill"]["discovery"]["ordinary_new_chat_auto_installation"]="GUARANTEED"
        wrapper=(ROOT/".agents/skills/ashare-financial-storytelling/SKILL.md").read_text()
        project=(ROOT/"docs/CHATGPT_PROJECT_INSTRUCTIONS.md").read_text()
        self.assertTrue(any("FALSE_CLAIM_SKILL_AUTO_INSTALLED" in e for e in check_discovery(m,wrapper,project)))
    def test_rejects_wrong_skill_version(self):
        m=copy.deepcopy(STATUS);m["skill"]["version"]="0.0.0"
        self.assertTrue(any("SKILL_VERSION_MISMATCH" in e for e in check_skill(m,SKILL)))
    def test_rejects_old_v9_top_header(self):
        bad="LATEST ACTUAL PRODUCTION IS 2026-11-03 V9\n"+STATE
        self.assertTrue(any("STALE_" in e for e in check_current_state(bad,README,STATUS)))
    def test_rejects_four_company_front_page(self):
        four=HTML.replace('href="/300394.html"','href="/not-real-ticker.html"',1)
        self.assertTrue(any("ROOT_CATALOG_DRIFT" in e for e in check_catalog(STATUS,CATALOG,four)))
    def test_rejects_missing_original_three(self):
        bad=copy.deepcopy(CATALOG);bad["issuers"]=bad["issuers"][3:]
        self.assertTrue(any("CATALOG_STATUS_DRIFT" in e for e in check_catalog(STATUS,bad,HTML)))
    def test_rejects_inaccurate_issuer_status(self):
        bad=copy.deepcopy(STATUS);bad["site"]["company_count"]=4
        self.assertTrue(any("CATALOG_STATUS_DRIFT" in e for e in check_catalog(bad,CATALOG,HTML)))


if __name__=="__main__":
    unittest.main()
