#!/usr/bin/env python3
"""Restore historical probe PDFs by SHA, keeping different-byte variants separately."""
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen
import json

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'research/quality/generalization-probe/result.json'
ADDITIONAL = {
    ('600036', '2026H1'): 'https://static.cninfo.com.cn/finalpage/2026-08-28/1225531453.PDF',
    ('688111', '2026H1'): 'https://static.cninfo.com.cn/finalpage/2026-08-20/1225482678.PDF',
    ('600519', '2026H1'): 'https://static.cninfo.com.cn/finalpage/2026-08-15/1225475868.PDF',
    ('000333', '2026H1'): 'https://disc.static.szse.cn/disc/disk03/finalpage/2026-08-29/df25443f-d67a-4cc5-8bd6-6c3e681a9575.PDF',
}


def restore(out):
    snapshot = json.loads(SNAPSHOT.read_text())
    urls = {**ADDITIONAL}
    urls.update({(code, '2025FY'): url for code, url in snapshot['annual_sources'].items()})
    periods = {row['code']: row['fiscal_period'] for row in snapshot['rows']
               if row['fiscal_period'] != '2025FY'}
    urls.update({(code, periods[code]): url for code, url in snapshot['blind_sources'].items()})

    def fetch(row):
        key = row['code'], row['fiscal_period']
        url = urls.get(key)
        expected = row['sha256']
        target = out / ('_'.join(key) + '_original.pdf')
        if target.is_file() and sha256(target.read_bytes()).hexdigest() == expected:
            return dict(issuer=key[0], period=key[1], status='SHA_MATCH', sha256=expected, url=url)
        path = ROOT / row['pdf']
        if path.is_file() and sha256(path.read_bytes()).hexdigest() == expected:
            data = path.read_bytes()
        elif url:
            try:
                with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=40) as response:
                    data = response.read()
            except (OSError, ValueError) as error:
                return dict(issuer=key[0], period=key[1], status='DOWNLOAD_ERROR', url=url, error=str(error))
        else:
            return dict(issuer=key[0], period=key[1], status='ORIGINAL_UNLOCATED', sha256=expected)
        actual = sha256(data).hexdigest()
        status = 'SHA_MATCH' if actual == expected and data.startswith(b'%PDF-') else 'DIFFERENT_BYTES'
        if status == 'DIFFERENT_BYTES':
            if target.is_file():
                prior = sha256(target.read_bytes()).hexdigest()
                target.rename(out / (target.stem + '-' + prior + '.pdf'))
            if data.startswith(b'%PDF-'):
                (out / (target.stem + '-' + actual + '.pdf')).write_bytes(data)
        else:
            if target.is_file():
                prior = sha256(target.read_bytes()).hexdigest()
                target.rename(out / (target.stem + '-' + prior + '.pdf'))
            target.write_bytes(data)
        return dict(issuer=key[0], period=key[1], status=status, sha256=actual, expected=expected, url=url)

    out.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(fetch, snapshot['rows']))
    (out / 'recovery.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    matched = sum(row['status'] == 'SHA_MATCH' for row in rows)
    print(f'HISTORICAL_ORIGINALS {matched}/{len(rows)}')
    return matched == len(rows)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    raise SystemExit(0 if restore(parser.parse_args().out) else 1)
