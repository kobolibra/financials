from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from delivery_quality_suite import ROOT, source_preview_evidence_errors


def current_source_preview():
    catalog=json.loads((ROOT/'site/research_catalog.json').read_text(encoding='utf8'))
    issuer=next(x for x in catalog['issuers'] if x['code']=='600206')
    folder=ROOT/'research/issuers'/issuer['code']
    record=json.loads((folder/'release-gates.json').read_text(encoding='utf8'))
    receipt=json.loads((folder/'visual-qa/result.json').read_text(encoding='utf8'))
    html_sha=hashlib.sha256((ROOT/'public'/issuer['href'].lstrip('/')).read_bytes()).hexdigest()
    return issuer,html_sha,record,receipt


class NewSourcePreviewFigureContractTests(unittest.TestCase):
    def test_current_report_has_distinct_source_limited_contract(self):
        issuer,sha,record,receipt=current_source_preview()
        self.assertNotEqual(issuer.get('figure_quality_contract'),'FULL_SOURCE_FIGURES_V1')
        self.assertEqual(source_preview_evidence_errors(issuer,sha,record,receipt),[])

    def test_old_or_stale_browser_evidence_is_rejected(self):
        issuer,sha,record,receipt=current_source_preview()
        for kind in ('html','receipt','width','figure','ids','source','primary','gate','class'):
            r=copy.deepcopy(record)
            q=copy.deepcopy(receipt)
            expected=sha
            if kind=='html': expected='0'*64
            elif kind=='receipt': q['sha256']='0'*64
            elif kind=='width': q['viewports'].pop()
            elif kind=='figure': q['viewports'][0]['figures'].pop()
            elif kind=='ids': q['viewports'][0]['figures'][1]['id']=q['viewports'][0]['figures'][0]['id']
            elif kind=='source': q['viewports'][0]['figures'][0]['values'][0]['source']=None
            elif kind=='primary': q['viewports'][0]['figures'][0]['role']='secondary'
            elif kind=='gate': r['gates']['VISUAL_EDITORIAL_SELF']['status']='NOT_CHECKED'
            elif kind=='class': r['release_class']='verified_research'
            with self.subTest(poison=kind):
                self.assertTrue(source_preview_evidence_errors(issuer,expected,r,q),kind)

    def test_fresh_browser_must_match_its_own_engine_and_widths(self):
        issuer,sha,record,receipt=current_source_preview()
        self.assertIn('NEW_SOURCE_PREVIEW_BROWSER_SOURCE_SHA_DRIFT',
                      source_preview_evidence_errors(issuer,sha,record,receipt,engine='webkit',widths=(375,)))


if __name__ == '__main__':
    unittest.main()
