#!/usr/bin/env python3
"""Prepare a standalone research dossier from one complete, text-searchable A-share PDF."""
from argparse import ArgumentParser, Namespace
from pathlib import Path
import json
import os
import re

import editorial_discovery as discovery
import fin_intake as intake
import v2_builder as builder

IDENTITY = re.compile(r'(?:A股股票代码|A股代码|公司代码|证券代码|股票代码)[:：]\s*([036]\d{5})(?!\d)')
FALLBACK_CODE = re.compile(r'\b([036]\d{5})\.(?:SH|SZ)\b', re.IGNORECASE)
COMPANY = re.compile(
    r'[\u3400-\u9fff]{2,40}(?:[（(][\u3400-\u9fff]{1,20}[）)][\u3400-\u9fff]{0,20})?'
    r'(?:股份有限公司|集团有限公司)'
)


def identity(pdf, supplied_code=None, supplied_name=None):
    with intake.pymupdf().open(pdf) as doc:
        text = [page.get_text() for page in list(doc)[:12]]
        codes = set(IDENTITY.findall(''.join(intake.squash(t) for t in text)))
        if not codes:
            codes = set(FALLBACK_CODE.findall(' '.join(text)))
        if not supplied_code and len(codes) != 1:
            raise SystemExit('ISSUER_IDENTITY_REQUIRES_CODE: inspect the original cover and pass --code')
        code = supplied_code or next(iter(codes))
        ident = intake.detect_identity(doc, code)
        cover_lines = [intake.squash(line) for line in text[0].splitlines()]
        names = [line for line in cover_lines if COMPANY.fullmatch(line)]
        if not names:
            names = [name for line in cover_lines for name in COMPANY.findall(line)]
        if not supplied_name and not names:
            raise SystemExit('ISSUER_IDENTITY_REQUIRES_FULL_LEGAL_NAME: inspect the original cover and pass --name')
        return code, supplied_name or names[0], ident['fiscal_period']


def main(argv=None):
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--code')
    parser.add_argument('--name')
    parser.add_argument('--short')
    parser.add_argument('--url')
    parser.add_argument('--work-root', default='work/dossiers')
    args = parser.parse_args(argv)
    os.environ['FINANCIALS_DOSSIER_ROOT'] = args.work_root
    code, name, period = identity(args.pdf, args.code, args.name)
    dossier = Namespace(code=code, period=period, name=name, short=args.short or name,
                        pdf=args.pdf, url=args.url, candidate=True, route=None, force=False,
                        write=True, allow_residual=False, out=None, source_probe=False,
                        editorial_selection_version=2)
    intake.cmd_init(dossier)
    base = intake.folder(code, period)
    try:
        intake.cmd_auto(dossier)
    finally:
        ledger = json.loads((base / 'source-ledger.json').read_text())
        plan = builder.rc.assess(ledger)
        opportunities = discovery.build_index(base, plan, ledger['source']['physical_pages_observed'])
        (base / discovery.INDEX_FILE).write_text(
            json.dumps(opportunities, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('READING_LEADS', base / discovery.INDEX_FILE)
    (base / 'capabilities.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
    print('RESEARCH_DOSSIER', base, 'ROUTE', plan['publication_route'])
    if not (base / 'v2-draft.json').is_file() and plan['publication_route'] in builder.rc.AUTHORING_ROUTES.values():
        builder.cmd_scaffold(dossier)


if __name__ == '__main__':
    main()
