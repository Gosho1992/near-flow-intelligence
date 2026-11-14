"""Checks for the long-term layer: signpost rules, the HSP-029 model, absorption ratios, one-hop evidence."""
import csv, glob, gzip, json, os, sys, unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "out"
os.environ["NFI_OFFLINE"] = "1"
sys.path.insert(0, str(ROOT))

from nfi import model, signposts  # noqa: E402

H = json.loads((OUT / "headline.json").read_text())


def synth(ratios, start=date(2026, 11, 16), mint=1000.0, buyback=100.0, status="complete"):
    """30 rows per window; window k has net flow = ratios[k] x mint."""
    rows = []
    for k, a in enumerate(ratios):
        for j in range(30):
            d = start + timedelta(days=30 * k + j)
            rows.append({"date": d.isoformat(), "data_status": status, "gross_issuance": mint,
                         "creations": max(a, 0) * mint, "redemptions": max(-a, 0) * mint,
                         "buyback_fund_change": buyback, "issuer_gap_pct": None})
    return rows


class Signposts(unittest.TestCase):
    def test_pending_before_first_window(self):
        r = signposts.evaluate(synth([]) + [{"date": "2026-11-13", "data_status": "complete"}])
        self.assertEqual(r["state"], "NOT YET TESTABLE")
        self.assertEqual(r["windows"][0]["start"], "2026-11-16")
        self.assertEqual(r["windows"][0]["end"], "2026-12-15")

    def test_bullish_needs_two_consecutive(self):
        self.assertEqual(signposts.evaluate(synth([1.2]))["state"], "MONITORING")
        self.assertEqual(signposts.evaluate(synth([1.2, 0.5]))["state"], "MONITORING")
        self.assertEqual(signposts.evaluate(synth([1.2, 1.0]))["state"], "BULLISH")

    def test_bearish(self):
        self.assertEqual(signposts.evaluate(synth([-1.5, -1.0]))["state"], "BEARISH")

    def test_structurally_wrong(self):
        # |a| = 0.05 < buyback ratio 0.1 in two windows
        self.assertEqual(signposts.evaluate(synth([0.05, -0.05]))["state"], "STRUCTURALLY WRONG")

    def test_issuer_gap_in_one_window_is_enough(self):
        rows = synth([0.5, 0.5])
        rows[40]["issuer_gap_pct"] = 0.9          # one figure, second window only
        self.assertEqual(signposts.evaluate(rows)["state"], "STRUCTURALLY WRONG")
        rows = synth([0.5, 0.5])
        rows[5]["issuer_gap_pct"] = -0.6          # first window only, negative sign
        self.assertEqual(signposts.evaluate(rows)["state"], "STRUCTURALLY WRONG")
        rows = synth([0.5, 0.5])
        rows[5]["issuer_gap_pct"] = 0.4           # inside tolerance
        self.assertEqual(signposts.evaluate(rows)["state"], "MONITORING")

    def test_state_persists_until_another_rule_fires(self):
        # frozen text: the most recently fired rule sets the state
        self.assertEqual(signposts.evaluate(synth([1.5, 1.5, -0.5]))["state"], "BULLISH")
        self.assertEqual(signposts.evaluate(synth([1.5, 1.5, -1.5, -1.2]))["state"], "BEARISH")

    def test_base_after_six_quiet_windows(self):
        self.assertEqual(signposts.evaluate(synth([0.5, -0.5, 0.3, 1.5, -0.4, 0.6]))["state"], "BASE")

    def test_void_window_breaks_pair(self):
        rows = synth([1.5, 1.5, 1.5])
        for r in rows[30:40]:
            r["data_status"] = "incomplete"
        r = signposts.evaluate(rows)
        self.assertEqual(r["windows"][1]["status"], "VOID")
        self.assertEqual(r["state"], "MONITORING")

    def test_duplicates_raise(self):
        rows = synth([1.0])
        with self.assertRaises(ValueError):
            signposts.evaluate(rows + rows[:1])

    def test_live_state_matches_headline(self):
        rows = list(csv.DictReader((OUT / "daily.csv").open()))
        self.assertEqual(signposts.evaluate(rows)["state"], H["signposts_state"])


class Model(unittest.TestCase):
    def test_hsp029_path_matches_proposal_schedule(self):
        # HSP-029's own checkpoints: 2.275% at month 6, 2.05% at 12, 1.825% at 18, 1.6% at 24
        for m, cap in ((0, 2.5), (6, 2.275), (12, 2.05), (18, 1.825), (24, 1.6), (30, 1.6)):
            self.assertAlmostEqual(model.cap_pct(m, 0), cap, places=9)
        self.assertEqual(model.cap_pct(2, 3), 2.5)          # grace period: unchanged
        self.assertEqual(model.cap_pct(30, None), 2.5)      # no ramp

    def test_avoided_issuance_matches_proposal(self):
        # the proposal models ~11.8M NEAR avoided over the two ramp years; ours ends 3 months later (month 27)
        self.assertLess(abs(H["scen_avoided_issuance_m27"] / 11.8e6 - 1), 0.03)

    def test_hsp029_endpoint_matches_proposal(self):
        # proposal: ~57,300 NEAR a day at full implementation
        self.assertLess(abs(H["hsp029_m24_per_day"] / 57300 - 1), 0.01)

    def test_scenarios_consistent(self):
        rows = list(csv.DictReader((OUT / "scenarios.csv").open()))
        self.assertEqual(len(rows), 37)
        for r in rows:
            self.assertGreaterEqual(float(r["wrapper_bear"]), 0)
            self.assertLessEqual(float(r["wrapper_bear"]), float(r["wrapper_base"]) + 1e-6)
            self.assertLessEqual(float(r["wrapper_base"]), float(r["wrapper_bull"]) + 1e-6)
            self.assertLessEqual(float(r["cap_pct"]), 2.5)


class Ratios(unittest.TestCase):
    def test_absorption_ratios_from_daily(self):
        rows = list(csv.DictReader((OUT / "daily.csv").open()))
        last30 = rows[-30:]
        net = sum(float(r["creations"]) - float(r["redemptions"]) for r in last30)
        mint = sum(float(r["gross_issuance"]) for r in last30)
        self.assertAlmostEqual(H["absorption_last30"], net / mint, places=5)
        self.assertAlmostEqual(H["absorption_launch"], H["launch_net_flow_total"] / H["gross_issuance_total"], places=5)

    def test_protocol_cap_read_daily(self):
        p = json.loads((ROOT / "data" / "work" / "protocol.json").read_text())
        self.assertGreaterEqual(H["protocol_days_read"], len(p) - 1)
        self.assertEqual(H["hsp029_ramp_started"], any(v and v["max_inflation_pct"] < 2.5 for v in p.values()))


class OneHop(unittest.TestCase):
    ONE = "9a00031933695207a60a3af95cfaaadcea863812ecbc30400c109417dadf21b3"
    SRC = "432766610e6d7069916d5207202505f46244539b905bb73e66e7ff3094e7b4c5"

    def test_path_in_raw_cache(self):
        found = {}
        for f in glob.glob(str(ROOT / "data" / "raw" / "tx" / "*" / "*.json.gz")):
            raw = gzip.decompress(Path(f).read_bytes())
            if self.ONE.encode() not in raw:
                continue
            for t in json.loads(raw)["response"].get("transactions", []):
                tx = t["transaction"]
                if tx["signer_id"] == self.SRC and tx["receiver_id"] == self.ONE:
                    found["transfer"] = (t["execution_outcome"]["block_height"],
                                         int(tx["actions"][0]["Transfer"]["deposit"]) / 1e24)
                if tx["signer_id"] == self.ONE and tx["receiver_id"] == "bitwise_2.poolv1.near":
                    fc = tx["actions"][0]["FunctionCall"]
                    found["stake"] = (t["execution_outcome"]["block_height"], int(fc["deposit"]) / 1e24,
                                      fc["method_name"])
        self.assertIn("transfer", found)
        self.assertIn("stake", found)
        self.assertLess(found["transfer"][0], found["stake"][0])
        self.assertAlmostEqual(found["transfer"][1], 52192.0668, places=3)
        self.assertEqual(found["stake"][2], "deposit_and_stake")
        accts = {a["account"] for a in json.loads((ROOT / "data" / "work" / "attribution.json").read_text())["accounts"]}
        self.assertIn(self.SRC, accts)       # the sender is a rule A account
        self.assertNotIn(self.ONE, accts)    # the one-hop account is not counted



class Frozen(unittest.TestCase):
    def test_frozen_files_match_locks(self):
        import hashlib, re
        for doc, lock in (("PREDICTION.md", "PREDICTION.lock"), ("PREDICTION-2.md", "PREDICTION-2.lock"),
                          ("SIGNPOSTS.md", "SIGNPOSTS.lock")):
            want = re.search(r"SHA-256: ([0-9a-f]{64})", (ROOT / lock).read_text()).group(1)
            self.assertEqual(hashlib.sha256((ROOT / doc).read_bytes()).hexdigest(), want, doc)



class SecFiling(unittest.TestCase):
    """Bitwise NEAR ETF 10-Q (30 Sep 2026) against the chain at 20:00 UTC, the filing's 4 p.m. ET valuation."""
    def setUp(self):
        from nfi import sec_check
        self.r = sec_check.run()
        self.ev = (ROOT / "data" / "issuer_evidence" / "2026-09-30_sec_10q.txt").read_text()

    def test_valuation_block_is_at_4pm_eastern(self):
        self.assertTrue(self.r["valuation_block_time"].startswith("2026-09-30T19:59:59"))
        self.assertTrue(self.r["next_block_time"] >= "2026-09-30T20:00:00")

    def test_in_kind_creation_matches_to_four_decimals(self):
        self.assertIn("5,010,335.4989", self.ev)
        self.assertLess(abs(self.r["in_kind_diff"]), 1e-4)

    def test_staked_value_needs_exactly_the_two_accounts(self):
        self.assertIn("$553,300", self.ev)
        self.assertLess(abs(self.r["staked_diff_pct"]), 0.02)
        self.assertLess(self.r["staked_rule_a_only_diff_pct"], -45)    # Rule A alone is half
        self.assertGreater(self.r["staked_whole_pool_diff_pct"], 15)   # the whole pool is too much

    def test_undelivered_purchases_match_receivable(self):
        self.assertIn("$14,039,097", self.ev)
        self.assertLess(abs(self.r["receivable_diff_usd"]), 100)

    def test_headline_carries_the_check(self):
        self.assertAlmostEqual(H["sec_staked_diff_pct"], self.r["staked_diff_pct"], places=4)


class Dashboard(unittest.TestCase):
    def test_no_duplicate_element_ids(self):
        import re, collections
        html = (ROOT / "site" / "index.html").read_text()
        dup = [k for k, n in collections.Counter(re.findall(r'id="([^"]+)"', html)).items() if n > 1]
        self.assertEqual(dup, [], "duplicate ids break getElementById (the trace list once rendered into a chart)")

if __name__ == "__main__":
    unittest.main()
