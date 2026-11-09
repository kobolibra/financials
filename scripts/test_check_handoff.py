"""Adversarial tests prevent regressions that made prior-chat handoff unreliable."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from check_handoff import check_skill, check_catalog, check_current_state, check_repo, check_discovery, check_agent_source_of_truth, check_start_here_source_of_truth, check_active_release_authority

STATUS=json.loads((ROOT/"project-status.json").read_text())
CATALOG=json.loads((ROOT/"site/research_catalog.json").read_text())
HTML=(ROOT/"public/index.html").read_text()
SKILL=(ROOT/"skills/ashare-financial-storytelling/SKILL.md").read_text()
STATE=(ROOT/"PROJECT_STATE.md").read_text()
README=(ROOT/"README.md").read_text()


class HandoffGateTests(unittest.TestCase):
    def test_current_tree_is_consistent(self):
        self.assertEqual(check_repo(),[])
    def test_agent_instructions_must_use_current_catalog_not_stale_eight(self):
        agent = (ROOT/"AGENTS.md").read_text()
        self.assertEqual(check_agent_source_of_truth(agent), [])
        stale = agent + "\nProduct: site with eight independent issuer reports."
        self.assertIn("AGENT_STALE_HARDCODED_ISSUER_COUNT", check_agent_source_of_truth(stale))
        missing = agent.replace("site/research_catalog.json", "omitted-catalog.json")
        self.assertIn("AGENT_CATALOG_SOURCE_OF_TRUTH_MISSING", check_agent_source_of_truth(missing))

    def test_current_pr35_is_not_active_candidate_in_any_discovery_entry(self):
        wrapper=(ROOT/".agents/skills/ashare-financial-storytelling/SKILL.md").read_text()
        agent=(ROOT/"AGENTS.md").read_text()
        protocol=(ROOT/"docs/HANDOFF_PROTOCOL.md").read_text()
        self.assertEqual(check_active_release_authority(wrapper, agent, protocol), [])
        stale_wrapper=wrapper.replace(
            "seven HERO money grammar", "only the 4 PR35 V10 candidates"
        ) if "seven HERO money grammar" in wrapper else (
            wrapper + "\nonly the 4 PR35 V10 candidates are being migrated"
        )
        self.assertIn("CODEX_DISCOVERY_STALE_UNMERGED_PR35_VISUAL_STATUS",
                      check_active_release_authority(stale_wrapper,agent,protocol))
        stale_agent=agent + "\n**Active candidate overlay (2026-11-07):** This is an UNMERGED candidate;"
        self.assertIn("AGENT_HISTORICAL_PR35_MISLABELED_AS_ACTIVE",
                      check_active_release_authority(wrapper,stale_agent,protocol))
        stale_protocol=("四家新桑基候选只按真实当前 HTML SHA 验收，其他七家 LEGACY_NOT_UNIFIED\n"
                        +protocol)
        self.assertIn("HANDOFF_STALE_PR35_CANDIDATE_AS_CURRENT_RELEASE",
                      check_active_release_authority(wrapper,agent,stale_protocol))
        missing=wrapper.replace("audit_unified_visual_corpus.py","not-a-census.py")
        self.assertIn("CODEX_DISCOVERY_CURRENT_MACHINE_CENSUS_NOT_REFERENCED",
                      check_active_release_authority(missing,agent,protocol))

    def test_start_here_never_reverts_to_fixed_current_company_count(self):
        entry=(ROOT/"START_HERE.md").read_text()
        self.assertEqual(check_start_here_source_of_truth(entry),[])
        stale="当前有效版本：统一十家公司研究库（遗忘最新第十一家）。\\n"+entry
        self.assertIn("START_HERE_STALE_FIXED_ISSUER_COUNT",check_start_here_source_of_truth(stale))
        stale11="当前有效版本：统一十一家公司研究库。\\n"+entry
        self.assertIn("START_HERE_STALE_FIXED_ISSUER_COUNT",check_start_here_source_of_truth(stale11))
        missing=entry.replace("site/research_catalog.json","stale/static-number.json")
        self.assertIn("START_HERE_MISSING_CURRENT_MACHINE_CATALOG",check_start_here_source_of_truth(missing))

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
