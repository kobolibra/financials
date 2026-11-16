#!/usr/bin/env python3
"""Promote unmerged candidates after a real post-merge production run.

  python scripts/promote_live_receipts.py --run <Actions run id of "V10 post-merge Cloudflare production release lock">

Downloads the run's artifact with `gh api`, and for every release-gates.json that still carries an
`unmerged_candidate`: requires the artifact's live receipt to be PASS and its full-content SHA to equal
the current repository HTML, archives the receipt next to the report, removes the candidate, and
records the production fingerprint, main commit, artifact id/SHA and CLOUDFLARE_LIVE proof.
Nothing is promoted on a mismatch; the script exits non-zero and lists what failed.
"""
import argparse, hashlib, io, json, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = 'kobolibra/financials'


def gh(*args, raw=False):
    out = subprocess.run(['gh', 'api', *args], capture_output=True, check=True)
    return out.stdout if raw else json.loads(out.stdout)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--run', required=True); p.add_argument('--artifact-zip', help='use a downloaded artifact instead of gh'); p.add_argument('--artifact-id', type=int)
    a = p.parse_args(argv)
    run = gh(f'repos/{REPO}/actions/runs/{a.run}')
    if run.get('conclusion') != 'success':
        sys.exit(f'RUN_NOT_SUCCESS {a.run} {run.get("conclusion")}')
    if a.artifact_zip:
        blob = Path(a.artifact_zip).read_bytes(); art_id = a.artifact_id
    else:
        art = gh(f'repos/{REPO}/actions/runs/{a.run}/artifacts')['artifacts'][0]; art_id = art['id']
        blob = gh(f'repos/{REPO}/actions/artifacts/{art_id}/zip', raw=True)
    z = zipfile.ZipFile(io.BytesIO(blob)); zsha = hashlib.sha256(blob).hexdigest(); names = set(z.namelist())
    catalog = json.loads((ROOT / 'site/research_catalog.json').read_text())
    rows = {r['code']: r for r in catalog['issuers']}
    rows.update({r['code'] + '@' + r['period']: r for r in catalog.get('period_reports', [])})
    promoted, failed = [], []
    for gates in sorted((ROOT / 'research/issuers').glob('**/release-gates.json')):
        d = json.loads(gates.read_text())
        if not isinstance(d.get('unmerged_candidate'), dict):
            continue
        folder = gates.parent
        rel = folder.relative_to(ROOT / 'research/issuers').parts
        key = rel[0] if len(rel) == 1 else rel[0] + '@' + rel[1]
        art_key = key.replace('@', '-')
        html = ROOT / 'public' / rows[key]['href'].lstrip('/')
        sha = hashlib.sha256(html.read_bytes()).hexdigest()
        name = f'source-publications/{art_key}/live-release-receipt.json'
        if name not in names:
            failed.append(f'{key} NO_RECEIPT_IN_ARTIFACT'); continue
        raw = z.read(name); rec = json.loads(raw)
        live = next((v for k, v in rec.items() if k.startswith('actual_full_content_sha256_equals_repository_main_') and not k.endswith('_index')), None)
        if rec.get('status') != 'PASS' or live != sha or d['unmerged_candidate'].get('candidate_full_html_sha256') != sha:
            failed.append(f'{key} RECEIPT_OR_SHA_MISMATCH'); continue
        (folder / 'live-release-receipt.json').write_bytes(raw)
        change = d.pop('unmerged_candidate').get('change', '')
        d.update(published_html_sha256=sha, live_release_fingerprint=sha, actual_main_release_commit=rec['verified_git_commit'],
                 actual_directory_fingerprint=rec['actual_full_content_sha256_equals_repository_main_index'],
                 production_artifact={'id': art_id, 'zip_sha256': zsha})
        if 'CLOUDFLARE_LIVE' in d.get('gates', {}):
            d['gates']['CLOUDFLARE_LIVE'].update(status='PASS', proof=f'https://github.com/{REPO}/actions/runs/{a.run}',
                                                 scope=f'合并后主分支真实Actions对公开生产站（{change[:60]}）：整页字节与仓库一致，Chromium 1440/768/390全部图形与WebKit 375的真实SVG下载、首页往返通过。不含独立人类审稿。')
        gates.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
        promoted.append(key)
    print('PROMOTED', promoted)
    if failed:
        sys.exit('NOT_PROMOTED ' + ' '.join(failed))


if __name__ == '__main__':
    main()
