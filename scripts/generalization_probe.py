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

A failure is reported per report and per stage; nothing is patched for a specific issuer.
"""
import argparse, glob, hashlib, json, re, sys, traceback
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


def probe(pdf: Path):
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
    a = p.parse_args(argv)
    pdfs = [Path(x).resolve() for x in a.pdfs] or sorted(Path(x).resolve() for x in glob.glob(str(ROOT / 'research/issuers/**/*.pdf'), recursive=True))
    rows = []
    for pdf in pdfs:
        try:
            rows.append(probe(pdf))
        except Exception:  # noqa: BLE001
            rows.append({'pdf': str(pdf), 'crash': traceback.format_exc()[-600:]})
        r = rows[-1]
        print(r.get('code'), r.get('fiscal_period'), r.get('format'), json.dumps(r.get('stages', r.get('crash')), ensure_ascii=False), flush=True)
    passed = sum(1 for r in rows if r.get('stages', {}).get('ledger', '').startswith('PASS') and r['stages'].get('exhibits', '').startswith('PASS')
                 and (r['stages'].get('income_flow_v3') == 'PASS' or r['stages'].get('income_flow_v3', '').startswith('REFUSED_AS_DESIGNED→SIGNED_BRIDGE_PASS'))
                 and r['stages'].get('findings', '').startswith('PASS')
                 and not r['stages'].get('business_sankey', '').startswith('FAIL'))
    out = {'schema': 'financials.generalization_probe.v1', 'company_specific_input': 'NONE', 'reports': len(rows), 'all_stages_pass': passed,
           'scope': 'STATEMENTS_TO_AUDITED_EXHIBITS; segment notes, narrative and human review are outside this probe', 'rows': rows}
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print('GENERALIZATION_PROBE', passed, '/', len(rows))
    return 0 if passed == len(rows) else 1


if __name__ == '__main__':
    sys.exit(main())
