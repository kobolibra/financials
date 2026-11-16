"""Notes extraction (segments / regions / 主营与其他业务 / 现金流量表补充资料 / 扣非) on real reports.

No column is trusted from its header: every role is proven by the report's own totals, and every
fact must re-read from its PDF cell. These tests pin the proofs and the refusals."""
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
import notes_extract as ne  # noqa: E402

ROOT = fi.ROOT


def run(code, period=None):
    led = json.loads((fi.folder(code, period) / 'source-ledger.json').read_text())
    pdf = led['source'].get('source_path') or glob.glob(str(fi.folder(code, period) / 'source' / '*.pdf'))[0]
    doc = fi.pymupdf().open(ROOT / pdf)
    issuer = dict(led['issuer'], comparative_period=led['issuer'].get('comparative_period', '2025H1'))
    facts = se.to_ledger_facts(se.extract(doc, fi.rows_on_page, fi.squash), issuer)
    return led, doc, facts, ne.extract_notes(doc, fi.rows_on_page, fi.squash, se.unit_of, se.norm, facts)


class Notes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = {c: run(c) for c in ('300570', '600690', '688220')}

    def test_cash_flow_reconciliation_closes_and_matches_the_hand_ledgers(self):
        for code in ('300570', '600690'):
            led, doc, facts, (nf, segs, part, rep) = self.r[code]
            with self.subTest(code=code):
                self.assertEqual(rep['cash_reconciliation']['status'], 'CLOSED')
                self.assertTrue(rep['cash_reconciliation']['prior_closed'])
                lines = [k for k in nf if (k in dict(ne.RECON) or k.startswith('recon_'))]
                total = D(facts['net_profit']['yuan']) + sum(D(nf[k]['yuan']) for k in lines)
                self.assertEqual(total, D(facts['cfo']['yuan']))
                for k in ('depreciation', 'inventory_release', 'operating_ar_change', 'operating_ap_change'):
                    if k in led['facts']:
                        self.assertEqual(D(nf[k]['yuan']), D(led['facts'][k]['yuan']), k)

    def test_adjusted_parent_uses_columns_proven_by_the_parent_row(self):
        for code in ('300570', '600690', '688220'):
            led, doc, facts, (nf, segs, part, rep) = self.r[code]
            with self.subTest(code=code):
                self.assertTrue(rep['adjusted_parent'])
                if 'adjusted_parent' in led['facts']:
                    self.assertEqual(D(nf['adjusted_parent']['yuan']), D(led['facts']['adjusted_parent']['yuan']))

    def test_segment_partition_closes_on_revenue_and_cost_against_the_statements(self):
        for code in ('600690', '688220'):
            led, doc, facts, (nf, segs, part, rep) = self.r[code]
            with self.subTest(code=code):
                self.assertIsNotNone(part)
                self.assertEqual(sum(D(nf[s['rev']]['yuan']) for s in segs), D(facts['rev']['yuan']))
                self.assertEqual(sum(D(nf[s['cost']]['yuan']) for s in segs), D(facts['cogs']['yuan']))
        led, doc, facts, (nf, segs, part, rep) = self.r['600690']
        self.assertEqual([s['label'] for s in segs], ['智慧生活电器', '智慧暖通方案', '智慧家庭生态及其他', '其他业务'])
        for s in segs:  # identical to the hand-built Haier ledger, cell by cell
            hand = next(h for h in led['segments'] if h['label'] == s['label'])
            self.assertEqual(D(nf[s['rev']]['yuan']), D(led['facts'][hand['rev']]['yuan']))

    def test_every_note_fact_re_reads_from_its_pdf_cell(self):
        for code, (led, doc, facts, (nf, *_)) in self.r.items():
            for k, f in nf.items():
                if f['classification'] == 'DISCLOSED':
                    with self.subTest(code=code, key=k):
                        self.assertTrue(ne.rereads(doc, f))

    def test_a_partial_or_negative_partition_is_refused(self):
        rows = [{'page': 1, 'y': 10 * i, 'label': l, 'dim': 'product', 'amts': [{'printed': a}, {'printed': c}], 'unit': D(1), 'kind': 'plain',
                 'total': False, 'header': None} for i, (l, a, c) in enumerate((('A', '60.00', '30.00'), ('B', '30.00', '40.00')))]
        # A + B = 90 is not 营业收入 100: not a partition
        self.assertEqual(ne.partitions(rows, {'rev': D(100), 'cogs': D(70)}), [])
        # when it does add up, B (cost > revenue) still keeps the dimension out of the gross-profit Sankey
        found = ne.partitions(rows, {'rev': D(90), 'cogs': D(70)})
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['roles'], {'rev': 0, 'cost': 1})

    def test_percentages_must_be_reproduced_to_their_printed_precision(self):
        self.assertTrue(ne.close_pct(D('35.284'), '35.28%'))
        self.assertFalse(ne.close_pct(D('35.30'), '35.28%'))
        self.assertFalse(ne.close_pct(D('1'), '不适用'))


if __name__ == '__main__':
    unittest.main()
