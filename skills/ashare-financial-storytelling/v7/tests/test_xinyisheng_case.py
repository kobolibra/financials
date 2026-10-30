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
        self.assertEqual(len(LEDGER["facts"]), 76)
        self.assertEqual(len(LEDGER["indirect_cfo_adjustments"]), 15)

    def test_report_is_exactly_reproducible(self):
        generated, metadata = build(LEDGER, MEMO)
        published = (ROOT / "outputs/xinyisheng-2026H1-research-preview.html").read_text(encoding="utf-8")
        self.assertEqual(generated, published)
        self.assertEqual(hashlib.sha256(generated.encode()).hexdigest(), "5e5dea09b377d182d69fb587f8a30b9cce8928194fe0358c0b")
        self.assertEqual(metadata["charts"], 11)

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
