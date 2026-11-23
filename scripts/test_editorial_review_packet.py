import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from editorial_review_packet import assess, prepare, ROLES, STAGES


class EditorialReviewPacketTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.pdf = root / "original.pdf"
        self.pdf.write_bytes(b"%PDF-test")
        digest = hashlib.sha256(self.pdf.read_bytes()).hexdigest()
        embedded = json.dumps({"source":{"original_bytes_sha256":digest}})
        self.a, self.b, self.out = (root / x for x in ("old", "new", "run"))
        for version in (self.a, self.b):
            for stage in STAGES:
                p = version / stage
                p.mkdir(parents=True)
                (p / "report.html").write_text(
                    f'<html>{version.name}-{stage}<script id="ledger-data">{embedded}</script></html>')
                for name in ("desktop", "mobile"):
                    (p / f"{name}.png").write_bytes(b"\x89PNG\r\n\x1a\n" + name.encode())

    def test_pack_separates_key_and_unreviewed_packet_cannot_certify(self):
        prepare(self.pdf, self.a, self.b, self.out)
        self.assertFalse((self.out / "reviewer/private-key.json").exists())
        self.assertNotIn("baseline", (self.out / "reviewer/manifest.json").read_text())
        self.assertEqual(assess(self.out)["status"], "NOT_CHECKED")

    def test_filed_report_embeds_the_same_frozen_original(self):
        self.pdf.write_bytes(b"%PDF-different")
        with self.assertRaisesRegex(ValueError, "does not match"):
            prepare(self.pdf, self.a, self.b, self.out)

    def test_report_tampering_and_duplicate_branches_fail(self):
        with self.assertRaisesRegex(ValueError, "identical"):
            prepare(self.pdf, self.a, self.a, self.out)
        prepare(self.pdf, self.a, self.b, self.out)
        (self.out / "reviewer/A/final/mobile.png").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "changed"):
            assess(self.out)

    def test_preference_revealed_only_after_both_stages_and_roles_are_reviewed(self):
        prepare(self.pdf, self.a, self.b, self.out)
        path = self.out / "reviewer/review.json"
        review = json.loads(path.read_text())
        review["reviewer_independence"] = "DECLARED_INDEPENDENT_OF_AUTHORING"
        path.write_text(json.dumps(review))
        with self.assertRaisesRegex(ValueError, "reviewer identity"):
            assess(self.out)
        for role in ROLES:
            review["roles"][role]["reviewer"] = f"reviewer-{role}"
            for stage in STAGES:
                review["roles"][role][stage] = {
                    "preferred": "A", "locators": ["source p. 18, profit chart"],
                    "finding": "Sign of the contribution is shown against the original.",
                }
        path.write_text(json.dumps(review))
        result = assess(self.out)
        key = json.loads((self.out / "private-key.json").read_text())
        self.assertEqual(result["preference"]["visual"]["first"], key["labels"]["A"])
        self.assertFalse(result["certifies_generalization"])
