"""Fail-closed regression tests for catalog release-byte HTTP preflight."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import qa_offline_candidate as qa


class FakeResponse:
    status = 200

    def __init__(self, body, *, status=200):
        self.body = body
        self.status = status
        self.headers = {'Content-Type': 'text/html; charset=utf-8',
                        'CF-Cache-Status': 'HIT'}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.body


class ExactReleaseByteTests(unittest.TestCase):
    def test_real_content_with_production_request_headers_passes(self):
        expected = b'<!doctype html><title>correct</title>'
        events = []
        with patch.object(qa, 'urlopen', return_value=FakeResponse(expected)) as fetch:
            result = qa.verify_remote_bytes('https://example.invalid/', expected,
                                            retries=1, observations=events)
        request = fetch.call_args.args[0]
        self.assertEqual(request.get_header('User-agent'), qa.RELEASE_HEADERS['User-Agent'])
        self.assertEqual(request.get_header('Cache-control'), 'no-cache')
        self.assertEqual(request.get_header('Accept'), 'text/html,*/*')
        self.assertEqual(result['result'], 'PASS_EXACT_BYTES')
        self.assertEqual(events[0]['actual_sha256'], hashlib.sha256(expected).hexdigest())

    def test_stale_then_current_html_requires_actual_convergence(self):
        expected = b'<!doctype html><title>new</title>'
        stale = b'<!doctype html><title>old</title>'
        events = []
        with patch.object(qa, 'urlopen',
                          side_effect=[FakeResponse(stale), FakeResponse(expected)]) as fetch:
            with patch.object(qa, 'sleep') as pause:
                qa.verify_remote_bytes('https://example.invalid/', expected, retries=2,
                                       interval_seconds=5, observations=events)
        self.assertEqual(fetch.call_count, 2)
        pause.assert_called_once_with(5)
        self.assertEqual([x['result'] for x in events], ['MISMATCH', 'PASS_EXACT_BYTES'])
        self.assertNotEqual(events[0]['actual_sha256'], events[-1]['actual_sha256'])

    def test_persistent_wrong_html_fails_with_sha_diagnostics(self):
        expected = b'<!doctype html><title>original</title>'
        wrong = b'<!doctype html><title>wrong</title>'
        events = []
        with patch.object(qa, 'urlopen', return_value=FakeResponse(wrong)):
            with patch.object(qa, 'sleep'):
                with self.assertRaisesRegex(ValueError, 'RELEASE_HTML_BYTES_MISMATCH') as caught:
                    qa.verify_remote_bytes('https://example.invalid/', expected,
                                           retries=2, observations=events)
        message = str(caught.exception)
        self.assertIn(hashlib.sha256(expected).hexdigest(), message)
        self.assertIn(hashlib.sha256(wrong).hexdigest(), message)
        self.assertEqual(len(events), 2)
        self.assertTrue(all(x['result'] == 'MISMATCH' for x in events))

    def test_even_identical_bytes_with_wrong_http_status_fail(self):
        expected = b'<!doctype html><title>original</title>'
        with patch.object(qa, 'urlopen', return_value=FakeResponse(expected, status=503)):
            with self.assertRaisesRegex(ValueError, 'RELEASE_HTML_BYTES_MISMATCH'):
                qa.verify_remote_bytes('https://example.invalid/', expected, retries=1)

    def test_http_error_never_converts_to_pass(self):
        expected = b'<!doctype html><title>correct</title>'
        events = []
        with patch.object(qa, 'urlopen', side_effect=OSError('refused')):
            with self.assertRaisesRegex(ValueError, 'RELEASE_HTML_BYTES_MISMATCH'):
                qa.verify_remote_bytes('https://example.invalid/', expected,
                                       retries=1, observations=events)
        self.assertEqual(events[0]['result'], 'FETCH_FAILED')
        self.assertIn('refused', events[0]['error'])

    def test_failed_live_preflight_preserves_json_evidence_before_browser(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            public = root / 'public'
            public.mkdir()
            (public / 'index.html').write_bytes(b'<!doctype html>index')
            article = public / '600206.html'
            article.write_bytes(b'<!doctype html>article')
            out = root / 'evidence'
            with patch.object(qa, 'urlopen', return_value=FakeResponse(b'wrong')):
                with patch.object(qa, 'sleep'):
                    with self.assertRaisesRegex(ValueError, 'RELEASE_HTML_BYTES_MISMATCH'):
                        qa.audit(article, out, 'chromium', (390,),
                                 origin='https://example.invalid')
            stored = json.loads((out / 'release-byte-preflight.json').read_text())
            self.assertEqual(stored['checks'][0]['route'], '/')
            self.assertEqual(stored['checks'][0]['result'], 'FAIL_CLOSED')
            self.assertEqual(len(stored['checks'][0]['observations']), 30)
            self.assertEqual(stored['checks'][0]['observations'][-1]['actual_sha256'],
                             hashlib.sha256(b'wrong').hexdigest())


if __name__ == '__main__':
    unittest.main()
