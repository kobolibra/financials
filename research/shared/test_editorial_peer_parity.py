"""Regression: a rich full-year filing may not degrade to four-chart synopsis."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import unittest

from editorial_peer_parity import evaluate, eligible

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/"research/issuers/600206"


def current():
    catalog=json.loads((ROOT/"site/research_catalog.json").read_text())
    issuer=next(x for x in catalog["issuers"] if x["code"]=="600206")
    record=json.loads((FOLDER/"release-gates.json").read_text())
    ledger=json.loads((FOLDER/"source-ledger.json").read_text())
    pub=json.loads((FOLDER/"publication.json").read_text())
    raw=(FOLDER/"research-brief.json").read_bytes()
    brief=json.loads(raw)
    review=json.loads((FOLDER/"editorial-self-review.json").read_text())
    sha=hashlib.sha256((ROOT/"public"/issuer["href"].lstrip("/")).read_bytes()).hexdigest()
    return issuer,record,ledger,pub,brief,raw,review,sha


class FullResearchParityTest(unittest.TestCase):
    def test_current_industrial_annual_has_all_eligible_questions(self):
        x=current()
        self.assertTrue(eligible(x[1],x[2]))
        self.assertEqual(evaluate(*x),[])

    def test_old_four_chart_synopsis_cannot_claim_peer_parity(self):
        x=list(current())
        x[3]=copy.deepcopy(x[3])
        # Simulate a historical four-figure synopsis with valid source facts.
        x[3]["figures"]=x[3]["figures"][:4]
        x[3]["essays"]=x[3]["essays"][:2]
        x[3]["glance"]=x[3]["glance"][:2]
        x[0]=dict(x[0],figures=4)
        self.assertTrue(any("ELIGIBLE_QUESTION_MISSING" in e for e in evaluate(*x)))
        self.assertTrue(any("RESEARCH_NARRATIVE_COVERAGE" in e for e in evaluate(*x)))

    def test_stale_review_and_missing_source_falsification_rejected(self):
        x=list(current())
        x[6]=dict(x[6],reviewed_html_sha256="0"*64)
        self.assertTrue(any("STALE_AUTHOR_REVIEW_BYTES" in e for e in evaluate(*x)))
        x=list(current());x[4]=dict(x[4],theses=x[4]["theses"][:1])
        self.assertTrue(any("SOURCE_BACKED_FALSIFIABLE_THESES" in e for e in evaluate(*x)))

    def test_self_scores_cannot_fake_independent_review(self):
        x=list(current())
        x[6]=copy.deepcopy(x[6]);x[6]["scores"]["V5"]["score"]=1
        self.assertTrue(any("RUBRIC_MINIMUM" in e for e in evaluate(*x)))
        x=list(current());x[1]=copy.deepcopy(x[1])
        x[1]["gates"]["INDEPENDENT_HUMAN_REVIEW"]["status"]="PASS"
        self.assertTrue(any("SELF_REVIEW_MISREPRESENTS_INDEPENDENT_HUMAN" in e for e in evaluate(*x)))

    def test_constrained_quarterly_source_not_forced_to_make_full_year_figures(self):
        x=list(current());record=dict(x[1],period="2026Q1")
        self.assertFalse(eligible(record,x[2]))


if __name__=="__main__":
    unittest.main()
