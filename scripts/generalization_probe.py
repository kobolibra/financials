#!/usr/bin/env python3
"""Generalization probe: original PDF in, audited visuals out — with NO company-specific input.

For every archived complete report in the repository (or the PDFs given on the command line) this
runs the Skill's generic chain and nothing else:

  cover → report type and periods (fin_intake.detect_identity)
  three consolidated statements → canonical ledger (statement_extract), every cell re-read from the PDF
  format-aware accounting identities (both columns)
  income-flow V3 stage definition from canonical keys (v2_builder.flow_stages) → render both editions →
      independent audit (income_flow_audit) — general format only; financial formats must be refused
  four exhibit families scaffolded from the ledger (v2_builder) → render both editions →
      geometry audit + original-value audit
  ranked generic findings (v2_builder.findings), every number an audited claim

    python scripts/generalization_probe.py [--out research/quality/generalization-probe/result.json] [pdf ...]
    python scripts/generalization_probe.py --coverage-queue /tmp/unmapped-review.json [pdf ...]

The optional review queue lists every unmapped monetary row with a stable ID tied to the
original PDF SHA, physical page, row position and printed amount. Classification and materiality
start at NOT_CHECKED. It is a triage input, NOT a clearance receipt. Human review against the
original report remains mandatory before any completeness claim.

A failure is reported per report and per stage; nothing is patched for a specific issuer.
"""
import argparse, glob, hashlib, json, re, sys, traceback
from collections import Counter
from decimal import Decimal as D
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/ashare-financial-storytelling/tools'))
sys.path.insert(0, str(ROOT / 'research/shared'))
import fin_intake as fi  # noqa: E402
import statement_extract as se  # noqa: E402
import v2_builder as vb  # noqa: E402

FAMILIES = ('kpi_board', 'growth_bars', 'ratio_dumbbell', 'stock_delta')


def code_of(path: Path) -> str:
    for p in reversed(path.parts):
        m = re.match(r'([0-9]{6})(?![0-9])', p)
        if m:
            return m.group(1)
    raise SystemExit('PROBE_NEEDS_SIX_DIGIT_CODE_IN_PATH ' + str(path))


def unmapped_review_items(unmapped, source_sha256):
    """Make every unrecognized amount row independently reviewable, never auto-clear it.

    The ID is bound to the original PDF bytes and physical row, not to which canonical
    key happened to precede it; mapping-rule changes must not silently erase a review.
    """
    items = []
    for u in unmapped:
        anchor = [source_sha256, u['statement'], u['page'], round(float(u['y']), 2),
                  u['label'], u.get('current'), u.get('prior')]
        stable_id = hashlib.sha256(json.dumps(anchor, ensure_ascii=False,
                                              separators=(',', ':')).encode('utf-8')).hexdigest()[:24]
        items.append({'id': stable_id, 'statement': u['statement'], 'physical_page': u['page'],
                      'position_y': round(float(u['y']), 2), 'printed_label': u['label'],
                      'printed_current': u.get('current'), 'printed_comparative': u.get('prior'),
                      'preceding_canonical_key': u.get('after'),
                      'classification': 'NOT_CHECKED', 'materiality': 'NOT_CHECKED',
                      'review_evidence': None})
    return items


def reference_corpus_coverage(rows, reference_rows=None):
    """Check exact original PDF SHA availability against the historical 30-report receipt.

    The reference is a historical snapshot, NOT proof that current code has re-tested it.
    Missing source bytes must stay visible rather than silently shrinking 30 to 10.
    """
    if reference_rows is None:
        receipt = ROOT / 'research/quality/generalization-probe/result.json'
        if not receipt.exists():
            return {'status': 'REFERENCE_RECEIPT_MISSING', 'reference_receipt': str(receipt),
                    'tested_reports': len(rows), 'missing_reference_reports': None}
        reference_rows = json.loads(receipt.read_text())['rows']
    available = Counter(r.get('sha256') for r in rows if r.get('sha256'))
    missing = []
    matched = 0
    for r in reference_rows:
        sha = r.get('sha256')
        if sha and available[sha] > 0:
            available[sha] -= 1
            matched += 1
        else:
            missing.append({'issuer': r.get('code'), 'fiscal_period': r.get('fiscal_period'),
                            'historical_pdf': r.get('pdf'), 'source_pdf_sha256': sha,
                            'historical_unmapped_rows': r.get('unmapped_rows')})
    return {'status': 'INCOMPLETE_REFERENCE_CORPUS' if missing else 'ALL_HISTORICAL_SOURCE_BYTES_PRESENT',
            'reference_type': 'HISTORICAL_PDF_SHA_SNAPSHOT_NOT_CURRENT_TEST_RECEIPT',
            'reference_reports': len(reference_rows), 'tested_reports': len(rows),
            'matched_reference_reports': matched, 'missing_reference_reports': len(missing),
            'missing_historical_unmapped_rows': sum(r.get('historical_unmapped_rows') or 0 for r in missing),
            'missing_originals': missing}


def build_coverage_queue(rows, reference_corpus=None):
    """Keep the unreviewed row-level audit separate from the compact technical probe."""
    reports = []
    for r in rows:
        items = r.pop('unmapped_review_items', [])
        if r.get('unmapped_rows') is not None and len(items) != r['unmapped_rows']:
            raise SystemExit('COVERAGE_QUEUE_ROW_COUNT_MISMATCH ' + str(r.get('pdf')))
        reports.append({'pdf': r.get('pdf'), 'source_pdf_sha256': r.get('sha256'),
                        'issuer': r.get('code'), 'fiscal_period': r.get('fiscal_period'),
                        'reported_unmapped_rows': r.get('unmapped_rows'),
                        'review_status': 'NOT_CHECKED',
                        'items': items,
                        'error': r.get('crash') or r.get('stages', {}).get('identity')})
    count = sum(len(r['items']) for r in reports)
    return {'schema': 'financials.unmapped_coverage_review.v1', 'reports': len(reports),
            'unmapped_rows_total': count, 'reference_corpus': reference_corpus or {'status': 'NOT_CHECKED'},
            'materiality_and_completeness': 'NOT_CHECKED',
            'instructions': 'Review every physical amount row with the original PDF; do not treat equation closure or an empty queue as independent completeness signoff.',
            'rows': reports}


def reread(doc, facts):
    """Independent cell check, same rule as the publication validator."""
    import pymupdf
    bad = []
    for k, f in facts.items():
        if f.get('classification') == 'DERIVED':
            t = f['derivation']['terms']
            if D(facts[t[0]]['yuan']) - D(facts[t[1]]['yuan']) != D(f['yuan']):
                bad.append(k)
            continue
        c = f['source_cells'][0]
        region = doc[f['page'] - 1].get_textbox(pymupdf.Rect(c['bbox']) + (-.5, -.5, .5, .5)).replace(',', '')
        printed = c['printed'].strip().replace(',', '')
        shown = se.value(c['printed']) * (-1 if c.get('sign_flipped') else 1)
        if printed.strip('()（）') not in region or shown * D(c.get('unit_scale', '1')) != D(f['yuan']):
            bad.append(k)
    return bad


def bundle_for(code, issuer, facts, sha):
    stages = vb.flow_stages(facts)
    keys = {k for s in stages for k, _ in s['terms']} | {k for s in stages for g in s['adjustments'] for k, _ in g['terms']}
    cell = lambda f: {**f, 'source_kind': 'ledger_typed', 'source_cells': [{'bbox': f['source_cells'][0]['bbox'], 'printed': f['source_cells'][0]['printed'],
                                                                           'original_number': f['yuan'], 'unit_scale': '1', 'normalization': 'SIGNED_ORIGINAL',
                                                                           'wrapped_number': False}]}
    return {'issuer': code, 'name': code, 'period': issuer['fiscal_period'], 'scope': 'consolidated', 'currency': 'CNY', 'unit': '元',
            'source_pdf': {'source_sha256': sha}, 'facts': {k: cell(facts[k]) for k in keys},
            'comparatives': {'period': issuer['comparative_period'], 'facts': {k + '_prior': cell(facts[k + '_prior']) for k in keys if k + '_prior' in facts}},
            'sources': [{'label': '营业收入', 'terms': [['rev', 1]]}], 'stages': stages,
            'editorial': {'layout': 'INCOME_FLOW_V3', 'primary_question': '收入如何变成归母净利润？', 'income_basis': '营业收入起点'}}


def probe(pdf: Path, include_unmapped_review=False):
    from income_flow_v3 import render as render_v3
    from income_flow_audit import check as audit_v3
    from source_publication import render_exhibit, expand_claims
    from editorial_geometry import check_editorial_svg
    from source_publication_audit import check_vector_source
    globals()['check_vector_source'] = check_vector_source
    code = code_of(pdf)
    raw = pdf.read_bytes(); sha = hashlib.sha256(raw).hexdigest()
    doc = fi.pymupdf().open(pdf)
    row = {'pdf': str(pdf.relative_to(ROOT)) if pdf.is_relative_to(ROOT) else pdf.name, 'sha256': sha, 'code': code, 'pages': len(doc), 'stages': {}}
    try:
        ident = fi.detect_identity(doc, code)
    except SystemExit as e:
        row['stages']['identity'] = 'FAIL ' + str(e); return row
    issuer = {'code': code, 'fiscal_period': ident['fiscal_period'], 'comparative_period': ident['comparative_period']}
    row.update(fiscal_period=ident['fiscal_period'], comparative_period=ident['comparative_period'])
    result = se.extract(doc, fi.rows_on_page, fi.squash)
    ok, bad = se.identities(result)
    facts = se.to_ledger_facts(result, issuer)
    row.update(source_anomalies=result.get('source_anomalies', []))
    row.update(format=result['format'], sign_convention=result['convention'], statement_pages=result['pages'], canonical_facts=len(facts),
               unmapped_rows=len(result['unmapped']), identities_passed=len(ok), identities_failed=bad)
    # Identities passing cannot certify every material disclosure was mapped.
    # This requires a separately evidenced review; a PDF-only probe never grants it.
    row['coverage_review'] = {'status': 'NOT_CHECKED', 'unmapped_rows': len(result['unmapped']),
                              'reason': 'Materiality and completeness of unmapped amount rows not independently reviewed'}
    if include_unmapped_review:
        row['unmapped_review_items'] = unmapped_review_items(result['unmapped'], sha)
    import notes_extract as ne
    note_facts, segments, partition, notes_report = ne.extract_notes(doc, fi.rows_on_page, fi.squash, se.unit_of, se.norm, facts)
    facts.update({k: f for k, f in note_facts.items() if k not in facts})
    row['notes'] = notes_report
    false_cells = reread(doc, facts)
    row['stages']['ledger'] = ('PASS' + (' 原件异常已列出' if result.get('source_anomalies') else '')) if not bad and not false_cells and not result['notes'] else f'FAIL identities={bad} cells={false_cells[:5]} {result["notes"]}'
    ledger = {'issuer': issuer, 'facts': facts, 'source': {'original_bytes_sha256': sha}, 'segments': segments, 'income_partition': partition or {}}
    # revenue -> gross profit Sankey by business, only when the notes proved a complete partition
    if partition:
        try:
            from source_income_adapter import compile_disclosed_income
            from source_publication import chart
            from source_publication_audit import check_vector_source as cvs
            led2 = dict(ledger, issuer=dict(issuer, sector_adapter='manufacturing', accounting_route='industrial_own_cost_income', base_unit='人民币元'),
                        source=dict(ledger['source'], physical_pages_observed=len(doc), source_path=str(pdf.relative_to(ROOT)) if pdf.is_relative_to(ROOT) else str(pdf), original_bytes_gate='COMPLETE_ARCHIVED_PDF_SHA_PASS'))
            compile_disclosed_income(led2)
            for mobile in (False, True):
                cvs(chart(led2, {'id': 'income', 'family': 'income', 'question': '哪个业务留下了毛利？'}, mobile), led2)
            row['stages']['business_sankey'] = 'PASS ' + partition['axis'] + f' {len(segments)} rows'
        except Exception as e:  # noqa: BLE001
            row['stages']['business_sankey'] = 'FAIL ' + type(e).__name__ + ' ' + str(e)[:160]
    else:
        row['stages']['business_sankey'] = 'NOT_AVAILABLE no complete revenue+cost partition proven in the notes'
    # income flow V3
    try:
        b = bundle_for(code, issuer, facts, sha)
        for mobile in (False, True):
            audit_v3(render_v3(b, mobile=mobile), b)
        row['stages']['income_flow_v3'] = 'PASS'
    except (SystemExit, ValueError) as e:
        # V3 refuses by design for financial formats, losses or gains larger than the carried profit:
        # the generic fallback is one signed income bridge, which must render and pass the source audit
        why = str(e)
        if result['format'] == 'general' and not re.search(r'(GAINS_EXCEED|NEGATIVE|USE_SIGNED_BRIDGE)', why):
            row['stages']['income_flow_v3'] = 'FAIL ' + why[:160]
        else:
            try:
                from source_publication import chart
                rows = vb.income_bridge(facts, result['convention'])
                fg = {'id': 'income-bridge', 'family': 'signed_bridge', 'question': '收入如何变成归母净利润？', 'rows': rows}
                for mobile in (False, True):
                    check_vector_source(chart(ledger, fg, mobile), ledger)
                row['stages']['income_flow_v3'] = 'REFUSED_AS_DESIGNED→SIGNED_BRIDGE_PASS (' + why[:80] + ')'
            except (Exception, SystemExit) as e2:  # noqa: BLE001
                row['stages']['income_flow_v3'] = 'FAIL fallback ' + str(e2)[:160]
    except Exception as e:  # noqa: BLE001
        row['stages']['income_flow_v3'] = 'FAIL ' + type(e).__name__ + ' ' + str(e)[:160]
    # exhibits
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            draft = scaffold_from(ledger, d)
        fams = []
        for fg in draft['new_figures']:
            for mobile in (False, True):
                svg = render_exhibit(ledger, fg, mobile, {'issuer': code, 'pdf_sha256': sha}, fg['question'], issuer['fiscal_period'])
                check_editorial_svg(svg, issuer=code, pdf_sha256=sha)
                check_vector_source(svg, ledger)
            fams.append(fg['family'])
        row['stages']['exhibits'] = 'PASS ' + '/'.join(fams)
    except Exception as e:  # noqa: BLE001
        row['stages']['exhibits'] = 'FAIL ' + type(e).__name__ + ' ' + str(e)[:200]
    # findings
    try:
        C = vb.Claims({'quantified_claims': {}}, facts)
        fl = vb.findings(facts)
        shown = [expand_claims({'quantified_claims': C.c, 'p': C.expand(x['text'])}, ledger)['p'] for x in fl[:5]]
        row['findings_top5'] = shown
        row['stages']['findings'] = f'PASS {len(fl)}'
    except (Exception, SystemExit) as e:  # noqa: BLE001
        row['stages']['findings'] = 'FAIL ' + str(e)[:200]
    return row


def scaffold_from(ledger, tmp):
    """v2_builder.scaffold on an in-memory ledger (no dossier folder needed)."""
    class A: pass
    a = A(); a.code = ledger['issuer']['code']; a.period = None; a.out = str(Path(tmp) / 'draft.json')
    orig = vb.load
    vb.load = lambda code, period: (Path(tmp), ledger, {'figures': []})
    try:
        vb.cmd_scaffold(a)
    finally:
        vb.load = orig
    return json.loads(Path(a.out).read_text())


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('pdfs', nargs='*'); p.add_argument('--out')
    p.add_argument('--coverage-queue', help='Write every available unmapped monetary row with source-stable ID')
    p.add_argument('--require-reference-corpus', action='store_true',
                   help='Fail if any original PDF SHA from the historical reference receipt is missing')
    a = p.parse_args(argv)
    pdfs = [Path(x).resolve() for x in a.pdfs] or sorted(Path(x).resolve() for x in glob.glob(str(ROOT / 'research/issuers/**/*.pdf'), recursive=True))
    rows = []
    for pdf in pdfs:
        try:
            rows.append(probe(pdf, include_unmapped_review=bool(a.coverage_queue)))
        except Exception:  # noqa: BLE001
            rows.append({'pdf': str(pdf), 'crash': traceback.format_exc()[-600:]})
        r = rows[-1]
        print(r.get('code'), r.get('fiscal_period'), r.get('format'), json.dumps(r.get('stages', r.get('crash')), ensure_ascii=False), flush=True)
    reference = reference_corpus_coverage(rows)
    print('REFERENCE_CORPUS', reference.get('matched_reference_reports'), '/',
          reference.get('reference_reports'), 'missing', reference.get('missing_reference_reports'),
          'status', reference['status'])
    if a.coverage_queue:
        queue = build_coverage_queue(rows, reference)
        path = Path(a.coverage_queue)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(queue, ensure_ascii=False, indent=1) + '\n')
        print('UNMAPPED_COVERAGE_QUEUE', queue['unmapped_rows_total'], 'all NOT_CHECKED', path)
    passed = sum(1 for r in rows if r.get('stages', {}).get('ledger', '').startswith('PASS') and r['stages'].get('exhibits', '').startswith('PASS')
                 and (r['stages'].get('income_flow_v3') == 'PASS' or r['stages'].get('income_flow_v3', '').startswith('REFUSED_AS_DESIGNED→SIGNED_BRIDGE_PASS'))
                 and r['stages'].get('findings', '').startswith('PASS')
                 and not r['stages'].get('business_sankey', '').startswith('FAIL'))
    out = {'schema': 'financials.generalization_probe.v1', 'company_specific_input': 'NONE', 'reports': len(rows), 'all_stages_pass': passed,
           'scope': 'STATEMENTS_TO_AUDITED_EXHIBITS; segment notes, narrative and human review are outside this probe',
           'unmapped_rows_total': sum(r.get('unmapped_rows', 0) for r in rows),
           'completeness_review': 'NOT_CHECKED', 'research_and_human_editorial_review': 'NOT_CHECKED',
           'reference_corpus': reference, 'rows': rows}
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print('GENERALIZATION_PROBE', passed, '/', len(rows))
    return 0 if passed == len(rows) and (not a.require_reference_corpus or reference['status'] == 'ALL_HISTORICAL_SOURCE_BYTES_PRESENT') else 1


if __name__ == '__main__':
    sys.exit(main())
