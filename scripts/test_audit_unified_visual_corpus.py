from __future__ import annotations

import json
from pathlib import Path
import unittest

from audit_unified_visual_corpus import ROOT, inspect


def actual():
    catalog=json.loads((ROOT/"site/research_catalog.json").read_text(encoding="utf8"))
    pages={x["code"]:(ROOT/"public"/x["href"].lstrip("/")).read_bytes() for x in catalog["issuers"]}
    return catalog,pages


class VisualMigrationEvidenceTests(unittest.TestCase):
    def test_incomplete_11_issuers_must_not_be_presented_as_unified(self):
        catalog,pages=actual()
        census=inspect(catalog,pages)
        self.assertEqual(census["canonical_issuer_count"],11)
        self.assertEqual(set(census["unified_positive_sankey_issuers"]),{"688111","000333","600036"})
        self.assertEqual(census["lawful_signed_exception_issuers"],["600519"])
        self.assertEqual(set(census["legacy_not_unified"]),
                         set())
        self.assertEqual(set(census["partial_hero_only_unified_remaining_art_legacy"]),
                         {"300394","300502","300308","688220","600900","600276","601628"})
        self.assertEqual(census["strict_all_11_visual_unification"],"NOT_ESTABLISHED")
        self.assertEqual(census["failed_new_grammar"],[])
        self.assertEqual(census["independent_visual_art_director"],"NOT_CHECKED")

    def test_actual_optical_main_flow_cannot_disappear_behind_partial_migration_claim(self):
        catalog,pages=actual()
        for code in ("300394","300502","300308"):
            with self.subTest(code=code):
                tampered=dict(pages)
                tampered[code]=tampered[code].replace(
                    b'data-node-id="revenue-total"',b'data-node-id="fake-total"',2)
                census=inspect(catalog,tampered)
                self.assertIn(code,census["failed_new_grammar"])

    def test_zj_original_p139_printed_conflict_remains_visible(self):
        catalog,pages=actual()
        tampered=dict(pages)
        tampered["300308"]=tampered["300308"].replace(b"422,649,613.97",b"422,649,612.97")
        self.assertIn("300308",inspect(catalog,tampered)["failed_new_grammar"])

    def test_current_sector_connected_flow_cannot_be_replaced_by_cute_ribbons(self):
        catalog,pages=actual()
        for code in ("688220","600900","600276"):
            with self.subTest(code=code):
                bad=dict(pages)
                raw=pages[code]
                bad[code]=(raw.replace(b'data-node-id="revenue-total"',b'data-node-id="forged-total"')
                           .replace(b'data-node-id=\\\"revenue-total\\\"',b'data-node-id=\\\"forged-total\\\"'))
                self.assertIn(code,inspect(catalog,bad)["failed_new_grammar"])

    def test_insurer_premium_can_never_become_industrial_revenue(self):
        catalog,pages=actual()
        bad=dict(pages)
        bad["601628"]=pages["601628"].replace(
            b'data-chart-grammar="INSURANCE_PREMIUM_SOURCE_NEW_RENEW_TOTAL"',
            b'data-chart-grammar="SOURCE_REVENUE_OUTCOME_CONNECTED_SANKEY"')
        self.assertIn("601628",inspect(catalog,bad)["failed_new_grammar"])

    def test_false_disconnected_software_source_to_revenue_is_rejected(self):
        catalog,pages=actual()
        tampered=dict(pages)
        tampered["688111"]=tampered["688111"].replace(
            b'data-node-id="revenue-total"',b'data-node-id="decorative-block"',2)
        census=inspect(catalog,tampered)
        self.assertIn("688111",census["failed_new_grammar"])

    def test_missing_bank_outcome_stage_is_rejected(self):
        catalog,pages=actual()
        tampered=dict(pages)
        tampered["600036"]=tampered["600036"].replace(
            b'data-stage="revenue-to-outcome"',b'data-stage="fake-bank-cost"',20)
        self.assertIn("600036",inspect(catalog,tampered)["failed_new_grammar"])

    def test_moutai_signed_negative_loss_cannot_be_replaced_with_fake_sankey(self):
        catalog,pages=actual()
        tampered=dict(pages)
        tampered["600519"]=tampered["600519"].replace(
            b'data-local-inset-source="other_rev"',b'data-invented-loss="other_rev"')
        self.assertIn("600519",inspect(catalog,tampered)["failed_new_grammar"])


if __name__=="__main__":
    unittest.main()
