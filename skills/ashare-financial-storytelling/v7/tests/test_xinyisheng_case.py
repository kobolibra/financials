"""Third real-issuer release regression: Eoptolink (300502.SZ) 2026H1."""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
from render_v7 import build, check  # noqa: E402

LEDGER = json.loads((ROOT / "examples/xinyisheng-2026H1-ledger.json").read_text(encoding="utf-8"))
MEMO = json.loads((ROOT / "examples/xinyisheng-2026H1-memo.json").read_text(encoding="utf-8"))

class EoptolinkReleaseQA(unittest.TestCase):
    def test_financial_reconciliations(self):
        self.assertNotEqual(check(LEDGER)["status"], "BLOCKED")
        self.assertEqual(len(LEDGER["facts"]), 80)
        self.assertEqual(len(LEDGER["indirect_cfo_adjustments"]), 15)

    def test_report_is_exactly_reproducible(self):
        generated, metadata = build(LEDGER, MEMO)
        published = (ROOT.parents[2] / "public/300502/2026-H1/index.html").read_text(encoding="utf-8")
        self.assertEqual(generated, published)
        self.assertEqual(hashlib.sha256(generated.encode()).digest(), hashlib.sha256(published.encode()).digest())
        catalog=json.loads((ROOT.parents[2]/'site/research_catalog.json').read_text())
        declared=next(r['figures'] for r in catalog['issuers'] if r['code']=='300502')
        self.assertEqual(metadata['charts'],declared)
        self.assertEqual(generated.count('data-chart-grammar="FULL_PROFIT_CHAIN_V1"'),2)

    def test_identity_and_source(self):
        html, _ = build(LEDGER, MEMO)
        self.assertIn("300502.SZ", html)
        self.assertIn("新易盛", html)
        self.assertIn(LEDGER["document"]["source_sha256"], html)
        self.assertNotIn("天孚通信", html)
        self.assertNotIn("无源光器件", html)

    def test_corrupt_cfo_is_blocked(self):
        corrupt = copy.deepcopy(LEDGER)
        from decimal import Decimal
        old = Decimal(corrupt["facts"]["cfo"]["amount"])
        corrupt["facts"]["cfo"]["amount"] = str(old + Decimal("0.01"))
        with self.assertRaises(ValueError):
            check(corrupt)

if __name__ == "__main__":
    unittest.main()
