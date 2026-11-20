#!/usr/bin/env python3
"""Prepare a standalone research dossier from one complete, text-searchable A-share PDF."""
from argparse import ArgumentParser, Namespace
from pathlib import Path
import json
import os
import re

import fin_intake as intake
import v2_builder as builder

IDENTITY = re.compile(r'(?:A股股票代码|A股代码|公司代码|证券代码|股票代码)[:：]\s*([036]\d{5})(?!\d)')
FALLBACK_CODE = re.compile(r'\b([036]\d{5})\.(?:SH|SZ)\b', re.IGNORECASE)
COMPANY = re.compile(r'[\u3400-\u9fff]{2,40}(?:股份有限公司|集团有限公司)')


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
        names = COMPANY.findall(intake.squash(text[0]))
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
                        write=True, allow_residual=False, out=None, source_probe=False)
    intake.cmd_init(dossier)
    intake.cmd_auto(dossier)
    base = intake.folder(code, period)
    plan = builder.rc.assess(json.loads((base / 'source-ledger.json').read_text()))
    (base / 'capabilities.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
    print('RESEARCH_DOSSIER', base, 'ROUTE', plan['publication_route'])
    if not (base / 'v2-draft.json').is_file() and plan['publication_route'] in builder.rc.AUTHORING_ROUTES.values():
        builder.cmd_scaffold(dossier)


if __name__ == '__main__':
    main()
