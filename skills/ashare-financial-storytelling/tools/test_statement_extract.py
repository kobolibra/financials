"""Company-agnostic statement extraction: real archived reports, no company-specific input.

Each case below is a variant that a per-company spec would have hidden; every one was met in a real
report and is solved by a general rule (see statement_extract.CANON and the probe receipt).
"""
import glob
import json
import sys
import unittest
from decimal import Decimal as D
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import fin_intake as fi  # noqa: E402
import statement_extract as se  # noqa: E402

ROOT = fi.ROOT
PDFS = sorted(glob.glob(str(ROOT / 'research/issuers/**/*.pdf'), recursive=True))
ALIAS = {'capex_cash': 'cash_capex'}


def run(pdf):
    return se.extract(fi.pymupdf().open(pdf), fi.rows_on_page, fi.squash)


class LabelsAndTitles(unittest.TestCase):
    def test_label_normalisation_handles_every_printed_variant(self):
        cases = {
            '一、营业总收入': '营业总收入', '其中：营业收入': '营业收入', '加：其他收益七、54': '其他收益',
            '投资收益（损失以“-”号填列）七、55': '投资收益', '营业收入四(46),十七(3)': '营业收入',
            '投资收益(损失以“()”填列)(五)46': '投资收益', '财务(费用)/收入四(52)': '财务费用',
            '公允价值变动收益/(损失)四(56)': '公允价值变动收益', '资产处置(损失)/收益四(58)': '资产处置损失',
            '三、营业利润（亏损以“—”号填列）': '营业利润', '五、净利润（净亏损以“－”号填列）': '净利润',
            '七、56': '', '56': '', '其他资产减值损失–': '其他资产减值损失',
        }
        for raw, want in cases.items():
            self.assertEqual(se.norm(raw), want, raw)

    def test_long_cash_capex_label_is_recovered_only_with_its_canonical_prefix(self):
        amount = {"printed": "2,073,906,530.23"}
        label = "期资产支付的现金"
        prefix = {"y": 100, "label": "购建固定资产、无形资产和其他长", "numbers": []}
        row = {"y": 114, "label": label, "numbers": [amount]}
        expected = prefix["label"] + label
        fixed, = se.labelled_rows([prefix, row], "cf")
        self.assertEqual(fixed["label"], expected)
        self.assertEqual(fixed["numbers"], [amount])
        isolated, = se.labelled_rows([dict(prefix, y=80), row], "cf")
        self.assertEqual(isolated["label"], label)
        outside_scope, = se.labelled_rows([prefix, row], "is")
        self.assertEqual(outside_scope["label"], label)

    def test_statement_titles_in_every_layout_seen(self):
        for t in ('1、合并资产负债表', '2、合并年初到报告期末利润表', '2026年6月30日合并资产负债表（续）', '截至2026年6月30日止6个月期间合并利润表',
                  '年半年度合并及公司利润表', '未经审计合并现金流量表', '合并及母公司资产负债表'):
            self.assertTrue(se.TITLE.match(t), t)
        for t in ('在本集团利润表中支出的所得税如下：', '值的变动计入合并利润表的公允价值变动损益', '附表二：集团口径的资产负债表（财务并表和监管并表）'):
            self.assertFalse(se.TITLE.match(t), t)

    def test_units(self):
        self.assertEqual(se.unit_of('（除特别注明外，金额单位为人民币百万元）'), D(1000000))
        self.assertEqual(se.unit_of('单位：千元币种：人民币'), D(1000))
        self.assertEqual(se.unit_of('人民币元', strict=False), D(1))
        self.assertIsNone(se.unit_of('项目附注', strict=False))


class RealReports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = {pdf: run(pdf) for pdf in PDFS}

    def test_every_archived_report_closes_every_identity_in_both_columns(self):
        self.assertGreaterEqual(len(PDFS), 10)
        for pdf, r in self.results.items():
            ok, bad = se.identities(r)
            with self.subTest(pdf=Path(pdf).name):
                self.assertEqual(r['notes'], [])
                self.assertEqual(bad, [])
                self.assertGreaterEqual(len(ok), 12)

    def test_extraction_reproduces_every_hand_built_ledger_value(self):
        compared = 0
        for pdf, r in self.results.items():
            led = Path(pdf.rsplit('/source/', 1)[0]) / 'source-ledger.json'
            if not led.exists():
                continue
            facts = json.loads(led.read_text())['facts']
            cur, pr = se.amounts(r, 'current'), se.amounts(r, 'prior')
            for k, f in facts.items():
                base = ALIAS.get(k.removesuffix('_prior'), k.removesuffix('_prior'))
                side = pr if k.endswith('_prior') else cur
                if base not in side:
                    continue
                want = D(f['yuan'])
                if se.flipped(r, base) and f.get('extraction') != 'STATEMENT_EXTRACT_CANON_V1':
                    # Only legacy hand-built ledgers retain the printed sign.
                    want = -want
                with self.subTest(pdf=Path(pdf).name, key=k):
                    self.assertEqual(side[base], want)
                compared += 1
        self.assertGreater(compared, 600)

    def test_formats_and_conventions_are_detected(self):
        by = {Path(p).name[:6]: r for p, r in self.results.items()}
        self.assertEqual(by['601628']['format'], 'insurance')
        self.assertEqual(by['601628']['convention'], 'expenses_negative')
        self.assertEqual(by['300570']['format'], 'general')
        self.assertEqual(by['300570']['convention'], 'expenses_positive')
        self.assertTrue(all(f['scale'] == D(1000000) for f in by['601628']['facts'].values()))

    def test_ledger_facts_keep_the_printed_cell_and_re_read_from_the_pdf(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        from generalization_probe import reread
        for pdf, r in self.results.items():
            issuer = {'fiscal_period': '2026H1', 'comparative_period': '2025H1'}
            facts = se.to_ledger_facts(r, issuer)
            with self.subTest(pdf=Path(pdf).name):
                self.assertEqual(reread(fi.pymupdf().open(pdf), facts), [])
                flips = [f for f in facts.values() if f['source_cells'][0].get('sign_flipped')]
                self.assertEqual(bool(flips), r['convention'] == 'expenses_negative')

    def test_a_missed_line_item_is_reported_never_absorbed(self):
        r = json.loads(json.dumps(self.results[next(p for p in PDFS if '300570' in p)], default=str))
        r = self.results[next(p for p in PDFS if '300570' in p)]
        dropped = dict(r, facts={k: v for k, v in r['facts'].items() if k != 'investment_income'})
        ok, bad = se.identities(dropped)
        self.assertTrue(any('营业利润' in b for b in bad), bad)


class Probe(unittest.TestCase):
    def test_pdf_only_chain_passes_for_every_archived_report(self):
        import tempfile
        sys.path.insert(0, str(ROOT / 'scripts'))
        import generalization_probe as gp
        with tempfile.TemporaryDirectory() as tmp:
            import os
            review_path = Path(os.environ.get('FINANCIALS_COVERAGE_QUEUE_OUT',
                                              str(Path(tmp) / 'unmapped-review.json')))
            technical = Path(tmp) / 'scope.json'
            self.assertEqual(gp.main(['--coverage-queue', str(review_path), '--out', str(technical), *PDFS]), 0)
            receipt = json.loads(technical.read_text())
            for row in receipt['rows']:
                if row.get('format') in ('bank', 'insurance', 'securities'):
                    with self.subTest(sector=row['format'], pdf=row['pdf']):
                        self.assertEqual(row['publisher_capability'], 'SECTOR_ADAPTER_OR_EVIDENCE_REQUIRED')
                        self.assertTrue(row['stages']['findings'].startswith('REFUSED_AS_DESIGNED_SECTOR_RESEARCH_REQUIRED'))
            queue = json.loads(review_path.read_text())
            self.assertEqual(queue['reports'], len(PDFS))
            self.assertEqual(queue['materiality_and_completeness'], 'NOT_CHECKED')
            reference = queue['reference_corpus']
            self.assertEqual(reference['matched_reference_reports'] + reference['missing_reference_reports'],
                             reference['reference_reports'])
            self.assertEqual(len(reference['missing_originals']), reference['missing_reference_reports'])
            self.assertLessEqual(reference['matched_reference_reports'], len(PDFS))
            if reference['missing_reference_reports']:
                self.assertEqual(reference['status'], 'INCOMPLETE_REFERENCE_CORPUS')
            self.assertEqual(queue['unmapped_rows_total'], sum(r['reported_unmapped_rows'] for r in queue['rows']))
            self.assertGreater(queue['unmapped_rows_total'], 0)
            self.assertTrue(all(item['classification'] == 'NOT_CHECKED' and item['materiality'] == 'NOT_CHECKED'
                                for r in queue['rows'] for item in r['items']))


if __name__ == '__main__':
    unittest.main()
