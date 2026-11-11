"""Offline checks of the published outputs (run: make test). Each test checks something independent
of the calculation it guards, so a wrong number cannot pass by construction."""
import csv, json, math, os, re, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "out"
os.environ["NFI_OFFLINE"] = "1"
sys.path.insert(0, str(ROOT))

from nfi.net import view, view_account, block, OfflineMiss  # noqa: E402
from nfi.attribution import HUB  # noqa: E402


def rows():
    with open(OUT / "daily.csv") as f:
        return [{k: (None if v == "" else v) for k, v in r.items()} for r in csv.DictReader(f)]


def num(x):
    return None if x is None else float(x)


class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = rows()
        cls.head = json.loads((OUT / "headline.json").read_text())
        cls.events = list(csv.DictReader(open(OUT / "events.csv")))
        cls.accounts = list(csv.DictReader(open(OUT / "accounts.csv")))
        cls.work = json.loads((ROOT / "data" / "work" / "attribution.json").read_text())

    # 1 issuer reconciliation
    def test_issuer_reconciliation(self):
        with open(ROOT / "data" / "issuer_snapshots.csv") as f:
            issuer = list(csv.DictReader(f))
        self.assertGreaterEqual(len(issuer), 2)
        by = {r["date"]: r for r in self.rows}
        for s in issuer:
            chain = num(by[s["date"]]["nrr_holdings"])
            gap = abs(chain - float(s["near_in_trust"])) / float(s["near_in_trust"])
            self.assertLess(gap, 0.01, f"{s['date']}: chain {chain:,.0f} vs issuer {s['near_in_trust']}")

    # 2 per-account history re-read straight from the cached RPC responses (independent of build.py)
    def test_account_balances_match_rpc(self):
        heights = json.loads((ROOT / "data" / "work" / "heights.json").read_text())
        by = {r["date"]: r for r in self.rows}
        for d in ("2026-10-15", "2026-10-29", "2026-11-09"):
            h = heights[d]
            n = view("bitwise_2.poolv1.near", "get_number_of_accounts", {}, h)
            accs = []
            for i in range(0, n, 100):
                accs += view("bitwise_2.poolv1.near", "get_accounts", {"from_index": i, "limit": 100}, h)
            mine = {a["account"] for a in self.accounts}
            tot = sum(int(a["staked_balance"]) + int(a["unstaked_balance"]) for a in accs if a["account_id"] in mine) / 1e24
            self.assertAlmostEqual(tot, num(by[d]["nrr_holdings"]), delta=1.0)

    # 3 no duplicates
    def test_no_duplicate_accounts(self):
        ids = [a["account"] for a in self.accounts]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn(HUB, ids)

    # 4 every event is backed by a transaction in the cached history with the same amount
    def test_events_backed_by_transactions(self):
        txs = {t["hash"]: t for h in self.work["histories"].values() for t in h}
        for e in self.events:
            self.assertIn(e["hash"], txs)
            t = txs[e["hash"]]
            if e["type"] == "creation_stake":
                dep = sum(a.get("near", 0) for a in t["actions"] if a.get("method") in ("deposit_and_stake", "deposit"))
                self.assertAlmostEqual(dep, float(e["near"]), delta=0.01)
            if e["type"] == "redemption_withdraw":
                paid = sum(x["near"] for x in t["receipt_transfers"] if x["to"] == e["account"])
                self.assertAlmostEqual(paid, float(e["near"]), delta=0.01)

    # 5 rewards sanity and unexplained residual stays small
    def test_rewards_and_residual(self):
        apr = self.head["reward_rate_annualised_pct"]
        self.assertTrue(3.0 <= apr <= 7.0, apr)
        bad = []
        for r in self.rows:
            if r["unexplained"] is None or num(r["nrr_holdings"]) < 100_000:
                continue
            if abs(num(r["unexplained"])) > 0.0005 * num(r["nrr_holdings"]) + 5:
                bad.append(r["date"])
        self.assertLessEqual(len(bad), max(1, int(0.05 * len(self.rows))), f"unexplained too large on {bad}")

    # 6 supply identity: gross issuance - burn = net change; total_supply equals the block header
    def test_supply_identity_and_headers(self):
        heights = json.loads((ROOT / "data" / "work" / "heights.json").read_text())
        for r in self.rows[1:]:
            self.assertAlmostEqual(num(r["gross_issuance"]) - num(r["burn"]), num(r["net_supply_change"]), delta=1.0)
            self.assertGreaterEqual(num(r["burn"]), -1.0, r["date"])
            hdr = block(heights[r["date"]])
            self.assertAlmostEqual(int(hdr["total_supply"]) / 1e24, num(r["total_supply"]), delta=0.01)
        yearly = 100 * 365 * self.head["gross_issuance_total"] / self.head["days"] / num(self.rows[-1]["total_supply"])
        self.assertTrue(2.0 <= yearly <= 2.6, yearly)   # NEAR's issuance cap is 2.5%/yr

    # 7 total staked by locked balances agrees with the validators RPC. Locked balances stay locked while a
    #   validator is kicked out for an epoch, so locked >= current-epoch stake, and close to it on most days.
    def test_total_staked_cross_check(self):
        chain = json.loads((ROOT / "data" / "work" / "chain.json").read_text())
        heights = json.loads((ROOT / "data" / "work" / "heights.json").read_text())
        E = chain["epochs"]
        close = checked = 0
        gaps = []
        for i, e in enumerate(E[:-1]):
            if not e["validators_stake"]:
                continue
            for d, h in heights.items():
                if e["start"] <= h < E[i + 1]["start"] and chain["days"][d].get("locked_sum"):
                    ls, vs = chain["days"][d]["locked_sum"], e["validators_stake"]
                    self.assertGreaterEqual(ls, 0.995 * vs, d)
                    close += abs(ls - vs) <= 0.01 * vs
                    gaps.append(abs(ls - vs) / vs)
                    checked += 1
        self.assertGreater(checked, 3)
        self.assertGreaterEqual(close / checked, 0.85, f"{close}/{checked} days within 1%")
        self.assertLess(sorted(gaps)[len(gaps) // 2], 0.005)   # median gap under 0.5%

    # 8 missing observations are blank, never zero
    def test_missing_not_zero(self):
        self.assertIsNone(self.rows[0]["net_supply_change"])
        for r in self.rows:
            if r["buyback_fund"] is None:
                self.assertIsNone(r["buyback_fund_change"])

    # 9 offline rebuild reproduces the published outputs byte for byte
    def test_offline_rebuild_is_deterministic(self):
        before = {p.name: p.read_bytes() for p in OUT.iterdir()}
        subprocess.run([sys.executable, "-m", "nfi.build"], cwd=ROOT, check=True, capture_output=True,
                       env={**os.environ, "NFI_OFFLINE": "1"})
        after = {p.name: p.read_bytes() for p in OUT.iterdir()}
        self.assertEqual(before.keys(), after.keys())
        for k in before:
            self.assertEqual(before[k], after[k], k)

    # 10 every number in the docs comes from headline.json
    def test_docs_numbers_from_data(self):
        sys.path.insert(0, str(ROOT))
        from nfi.docs import render
        for name in ("README.md", "THESIS.md", "METHOD.md"):
            text = (ROOT / name).read_text()
            self.assertEqual(text, render(text, self.head), f"{name} has stale numbers: run make docs")


if __name__ == "__main__":
    unittest.main()
