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
                         {"300394","300308","300502","688220","600900","600276","601628"})
        self.assertEqual(census["strict_all_11_visual_unification"],"NOT_ESTABLISHED")
        self.assertEqual(census["failed_new_grammar"],[])
        self.assertEqual(census["independent_visual_art_director"],"NOT_CHECKED")

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
