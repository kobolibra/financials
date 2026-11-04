#!/usr/bin/env python3
"""Adversarial original 688220 mobile art, no mocked PDF facts."""
import copy,importlib.util,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from native_mobile import make
L=json.loads((ROOT/"source-ledger.json").read_text())

class SourceNativeASR(unittest.TestCase):
    def test_all_nine_actual_original_finance_families(self):
        figs=make(L)
        self.assertEqual(set(figs),{"flow","segment","gp","pnl","earnings","cfo","cash","balance","capital"})
        self.assertEqual(figs["flow"].count('class="native-asr-source"'),4)
        self.assertEqual(figs["flow"].count('class="native-asr-ribbon"'),7)
        self.assertEqual(figs["flow"].count('class="native-asr-sink"'),2)
        self.assertIn("2025-12-31",figs["balance"])
        self.assertIn("经营性应收",figs["cfo"])
        self.assertIn("data-cumulative-yuan",figs["pnl"])
        self.assertNotIn("未披露差额",figs["flow"])
    def test_one_cent_false_source_amount_cannot_closure(self):
        fake=copy.deepcopy(L)
        k=fake["segments"][0]["rev"]
        fake["facts"][k]["yuan"]=str(float(fake["facts"][k]["yuan"])+.01)
        with self.assertRaises(AssertionError):make(fake)
    def test_one_cent_indirect_cfo_change_rejected(self):
        fake=copy.deepcopy(L)
        from decimal import Decimal as D
        x=fake["cfo_indirect"]["parts"][3]
        x["yuan"]=str(D(x["yuan"])+D(".02"))
        with self.assertRaisesRegex(AssertionError,"MOBILE_CAS_SIGNED_BRIDGE_ERROR"):make(fake)
    def test_same_date_balance_wrong_one_cent_rejected(self):
        fake=copy.deepcopy(L)
        from decimal import Decimal as D
        fake["facts"]["equity"]["yuan"]=str(D(fake["facts"]["equity"]["yuan"])+D(".01"))
        with self.assertRaises(AssertionError):make(fake)
    def test_unreviewed_original_ar_denominator_unchanged(self):
        self.assertIsNotNone(L["facts"]["ar_top5_ratio"])
        self.assertEqual(L["issuer"]["code"],"688220")
        self.assertEqual(len(L["cfo_indirect"]["parts"]),17)

if __name__=="__main__":unittest.main()
