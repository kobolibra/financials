#!/usr/bin/env python3
"""Reproduce the reviewed offline reports from pinned disclosure PDFs and authored briefs."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from time import perf_counter
from urllib.request import urlopen
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROOF = Path('research/quality/pdf-generalization-20261120')
TOOLS = Path('skills/ashare-financial-storytelling/tools')
SPECS = {
    '600036': ('2026Q1', '招商银行', '2026-04-29/1225231394',
               '2802004753a3bf4899ebebd55a8bd80d0704390cb791775d528565009d99802d'),
    '600206': ('2025FY', '有研新材', '2026-04-25/1225177379',
               'eded66de7b33183bd34917268852bf862b322e7f7f0d7d35d94b97f003e9df0b'),
    '600919': ('2025H1', '江苏银行', '2025-08-23/1224558839',
               'a5136fb013db4b301aac6a5c423570afb7ca45ca7ee9384f7dc160d00dc887df'),
}


def rebuild(code, input_dir, out, proof=PROOF):
    period, short, endpoint, expected = SPECS[code]
    url = 'https://static.cninfo.com.cn/finalpage/' + endpoint + '.PDF'
    pdf = input_dir / f'{code}-{period}.pdf'
    if not pdf.exists():
        with urlopen(url, timeout=45) as response:
            data = response.read()
        if sha256(data).hexdigest() != expected:
            raise ValueError('EXAMPLE_SOURCE_BYTES_DRIFT ' + code)
        pdf.write_bytes(data)
    if sha256(pdf.read_bytes()).hexdigest() != expected:
        raise ValueError('EXAMPLE_SOURCE_BYTES_DRIFT ' + code)
    dossier_root = (out / 'dossiers').relative_to(ROOT)
    base = dossier_root / code / period
    env = {**os.environ, 'FINANCIALS_DOSSIER_ROOT': str(dossier_root)}
    durations = {}
    args = ['--code', code, '--period', period]

    def run(stage, *params):
        start = perf_counter()
        with (out / f'{code}-{stage}.log').open('w') as log:
            subprocess.run([sys.executable, *map(str, params)], cwd=ROOT, env=env, check=True, stdout=log)
        durations[stage] = round(perf_counter() - start, 3)

    run('intake', TOOLS / 'start_report.py', pdf, '--url', url, '--short', short, '--work-root', dossier_root)
    for name, command in (('facts', 'facts'), ('coverage', 'coverage')):
        spec = proof / code / (name + '.json')
        if (ROOT / spec).exists():
            run(name, TOOLS / 'fin_intake.py', command, *args, '--spec', spec)
    for name in ('v2-draft.json', 'research-brief.json'):
        shutil.copyfile(ROOT / proof / code / name, ROOT / base / name)
    run('apply', TOOLS / 'v2_builder.py', 'apply', *args)
    run('preflight', TOOLS / 'fin_intake.py', 'preflight', *args, '--require-research-evidence')
    html = out / f'{code}.html'
    run('publish', 'research/shared/source_publication.py', base, html)
    return {'issuer': code, 'period': period, 'pdf_sha256': expected, 'html_sha256': sha256(html.read_bytes()).hexdigest(),
            'seconds': durations, 'authorship': 'replay of reviewed evidence specs and article'}


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--specs', type=Path, default=PROOF, help='Directory containing reviewed issuer specifications')
    parser.add_argument('--inputs', type=Path, default=ROOT / 'work' / 'example-inputs')
    parser.add_argument('--codes', nargs='+', choices=SPECS, default=['600036', '600206'])
    a = parser.parse_args()
    out, inputs = a.out.resolve(), a.inputs.resolve()
    if ROOT / 'work' not in out.parents:
        parser.error('--out must use a new directory under the repository work/')
    out.mkdir(parents=True, exist_ok=True)
    inputs.mkdir(parents=True, exist_ok=True)
    receipt = [rebuild(code, inputs, out, a.specs) for code in a.codes]
    (out / 'rebuild.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
