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
        self.assertGreaterEqual(len(issuer), 3)
        by = {r["date"]: r for r in self.rows}
        import datetime as dt
        checked = 0
        for s in issuer:
            # "as of T" = end of day T = our row T+1; NEAR unstaked for redemptions is already excluded -> staked (L1)
            nxt = (dt.date.fromisoformat(s["date"]) + dt.timedelta(days=1)).isoformat()
            if nxt not in by:
                continue
            chain = num(by[nxt]["l1_staked"])
            gap = abs(chain - float(s["near_in_trust"])) / float(s["near_in_trust"])
            self.assertLess(gap, 0.005, f"{s['date']}: chain {chain:,.0f} vs issuer {s['near_in_trust']}")
            checked += 1
        self.assertGreaterEqual(checked, 3)

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
            # burn is a residual (definitional identity); the independent checks are the header match below and
            # test 12 (minting vs the protocol's inflation formula). A negative residual would expose an error.
            self.assertAlmostEqual(num(r["gross_issuance"]) - num(r["burn_residual"]), num(r["net_supply_change"]), delta=1.0)
            self.assertGreaterEqual(num(r["burn_residual"]), -1.0, r["date"])
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
        for name in ("README.md", "THESIS.md", "METHOD.md", "LONG_TERM_PLAN.md"):
            text = (ROOT / name).read_text()
            self.assertEqual(text, render(text, self.head), f"{name} has stale numbers: run make docs")

    # 11 attribution rule: funding must come strictly before staking (synthetic histories)
    def test_attribution_rejects_reversed_order(self):
        from nfi.attribution import apply_rule
        pool = "bitwise_2.poolv1.near"
        def tx(h, signer, receiver, method=None, near=0.0):
            act = {"kind": "FunctionCall", "method": method, "near": near} if method else {"kind": "Transfer", "near": near}
            return {"hash": f"h{h}{signer}", "height": h, "ts": str(h * 10**9), "signer": signer, "receiver": receiver,
                    "ok": True, "actions": [act]}
        out_ = [{"to": "good", "near": 5000.0, "hash": "f1", "height": 10, "ts": str(10 * 10**9)},
                {"to": "reversed", "near": 5000.0, "hash": "f2", "height": 30, "ts": str(30 * 10**9)},
                {"to": "nostake", "near": 5000.0, "hash": "f3", "height": 10, "ts": str(10 * 10**9)},
                {"to": "otherpool", "near": 5000.0, "hash": "f4", "height": 10, "ts": str(10 * 10**9)}]
        hist = {"good": [tx(20, "good", pool, "deposit_and_stake", 4999.5)],
                "reversed": [tx(20, "reversed", pool, "deposit_and_stake", 5000.0)],
                "otherpool": [tx(20, "otherpool", "bitwise_1.poolv1.near", "deposit_and_stake", 5000.0)]}
        acc, rej = apply_rule(out_, hist, [pool])
        self.assertEqual([a["account"] for a in acc], ["good"])
        self.assertEqual(acc[0]["confidence"], "high")
        reasons = {r["account"]: r["reason"] for r in rej}
        self.assertEqual(reasons["reversed"], "staked before any hub funding")
        self.assertIn("no deposit_and_stake", reasons["nostake"])
        self.assertIn("no deposit_and_stake", reasons["otherpool"])
        for a in self.accounts:   # and on the real data
            self.assertLess(int(a["funding_height"]), int(a["stake_height"]))

    # 12 minting checked against the protocol's own formula (independent of our supply arithmetic)
    def test_issuance_matches_protocol_formula(self):
        rows_ = list(csv.DictReader(open(OUT / "issuance_check.csv")))
        self.assertGreater(len(rows_), 10)
        ratios = sorted(float(r["ratio"]) for r in rows_)
        self.assertGreaterEqual(ratios[0], 0.95)          # validators that miss blocks are paid less
        self.assertLessEqual(ratios[-1], 1.0005)          # never more than the 2.5%/yr maximum
        self.assertGreater(ratios[len(ratios) // 2], 0.99)

    # 13 failed lookups are missing (None), never zero; an account not yet created is a true zero
    def test_failed_lookups_are_missing_not_zero(self):
        from unittest import mock
        import nfi.net as net, nfi.chain as chain
        err = {"error": {"cause": {"name": "TIMEOUT_ERROR"}, "code": -32000}}
        unknown = {"error": {"cause": {"name": "UNKNOWN_ACCOUNT"}, "code": -32000}}
        with mock.patch.object(net, "_post", return_value=err):
            self.assertIsNone(net.view_account("x.near", 1))
            self.assertIsNone(chain.pool_accounts("p.near", 1))
            self.assertIsNone(chain.locked_sum(["v.near"], 1))
            self.assertIsNone(chain.buyback_fund(1)[0])
        with mock.patch.object(net, "_post", return_value=unknown):
            self.assertEqual(net.view_account("x.near", 1), 0)
        ok = {"result": {"amount": str(5 * 10**24), "locked": "0"}}
        def wnear_fails(kind, url, body, cacheable=True, force=False):
            return ok if body["params"].get("request_type") == "view_account" else err
        with mock.patch.object(net, "_post", side_effect=wnear_fails):
            self.assertIsNone(chain.buyback_fund(1)[0])   # native observed, wNEAR failed -> total missing
        for r in self.rows:
            if r["data_status"] == "complete":
                for k in ("nrr_holdings", "total_supply", "total_staked", "buyback_fund", "l3_basket_liquid", "l4_hub_liquid"):
                    self.assertIsNotNone(r[k], (r["date"], k))

    # 14 no attributed account belongs to Bitwise's other pools
    def test_other_bitwise_products_excluded(self):
        ex = json.loads((ROOT / "data" / "work" / "exclusion.json").read_text())
        mine = {a["account"] for a in self.accounts}
        self.assertTrue(all(a["pool"] == "bitwise_2.poolv1.near" for a in self.accounts))
        for pool, members in ex["pools"].items():
            self.assertIsNotNone(members, pool)
            self.assertFalse(mine & set(members), pool)

    # 15 every counted creation/redemption carries a sequence status; confirmed ones point at a real, correctly
    #    ordered linked transaction
    def test_event_sequences(self):
        txs = {t["hash"]: t for h in self.work["histories"].values() for t in h}
        for e in self.events:
            if e["type"] in ("creation_stake", "redemption_withdraw"):
                self.assertIn(e["status"], ("confirmed sequence", "partially observed"))
                if e["status"] == "confirmed sequence":
                    link = txs[e["linked_tx"]]
                    if e["type"] == "creation_stake":
                        self.assertLess(link["height"], int(e["height"]))
                    else:
                        self.assertGreaterEqual(link["height"], int(e["height"]))
        by = {r["date"]: r for r in self.rows}
        self.assertAlmostEqual(sum(num(r["creations_confirmed"]) for r in self.rows), self.head["creations_confirmed_total"], delta=1)

    # 16 buyback ledger explains every daily buyback-fund change, account by account
    def test_buyback_ledger(self):
        led = list(csv.DictReader(open(OUT / "buyback_ledger.csv")))
        per = {}
        for l in led:
            if l["status"] == "observed":
                per[l["date"]] = per.get(l["date"], 0) + float(l["change"])
        for r in self.rows[1:]:
            if r["buyback_fund_change"] is not None:
                self.assertAlmostEqual(per[r["date"]], num(r["buyback_fund_change"]), delta=0.01)

    # 17 rewards: all eligible delegators earn the pool's single share-price rate
    def test_reward_probes_agree(self):
        self.assertLess(self.head["reward_probe_max_spread"], 1e-6)
        self.assertGreaterEqual(self.head["reward_probes_median"], 20)

    # 18 the prediction evaluator handles pending, void, duplicate and complete windows
    def test_prediction_evaluator(self):
        from nfi.prediction import evaluate, START
        import datetime as dt
        d0 = dt.date.fromisoformat(START)
        mk = lambda i, c="10", b="1", st="complete": {"date": (d0 + dt.timedelta(i)).isoformat(), "creations": c,
                                                       "redemptions": "0", "buyback_fund_change": b, "data_status": st}
        self.assertEqual(evaluate([mk(i) for i in range(10)])[0], "PENDING")
        self.assertEqual(evaluate([mk(i) for i in range(30)])[0], "HOLDS")
        self.assertEqual(evaluate([mk(i, c="0") for i in range(30)])[0], "FAILS")
        self.assertEqual(evaluate([mk(i, st="incomplete: x" if i < 6 else "complete") for i in range(30)])[0], "VOID")
        with self.assertRaises(ValueError):
            evaluate([mk(0), mk(0)])

    # 19 completeness: an independent BigQuery query (data/bigquery/completeness.sql) found exactly the same pool
    #    transactions, method by method, as this pipeline (compared by SHA-256 of the sorted hash lists)
    def test_bigquery_completeness(self):
        import hashlib
        B = json.loads((ROOT / "data" / "bigquery" / "completeness_result.json").read_text())
        mine = {a["account"] for a in self.accounts}
        by = {}
        for h in self.work["histories"].values():
            for t in h:
                if t["receiver"] == "bitwise_2.poolv1.near" and t["signer"] in mine and t["height"] < B["max_block_height_exclusive"]:
                    for a in t["actions"]:
                        by.setdefault(a.get("method"), set()).add(t["hash"])
        self.assertEqual(set(by), set(B["by_method"]))
        for m, v in B["by_method"].items():
            hs = sorted(by[m])
            self.assertEqual(len(hs), v["transactions"], m)
            self.assertEqual(hashlib.sha256("\n".join(hs).encode()).hexdigest(), v["sha256_sorted_hashes"], m)

    # 20 SVRN is a separate, partial observation: never in NRR's accounts or totals, never reconciled,
    #    and its observed pool stake is recorded account by account
    def test_institutional_holders_separate(self):
        inst = json.loads((ROOT / "data" / "work" / "institutional.json").read_text())
        mine = {a["account"] for a in self.accounts}
        self.assertFalse(mine & set(inst["accounts"]))
        rows_ = list(csv.DictReader(open(OUT / "institutional_holders.csv")))
        nrr, svrn = rows_[0], rows_[1]
        self.assertEqual(svrn["counted_in_nrr_totals"], "no")
        self.assertTrue(svrn["issuer_reconciled"].startswith("no"))
        self.assertAlmostEqual(float(svrn["observed_staked_near"]), sum(v["staked"] for v in inst["accounts"].values()), delta=0.01)
        self.assertAlmostEqual(float(nrr["observed_staked_near"]), num(self.rows[-1]["l1_staked"]), delta=0.01)

    # 21 source mix: shares add up to the external inflow total, labels follow the stated heuristic
    def test_source_mix(self):
        mix = list(csv.DictReader(open(OUT / "source_mix.csv")))
        tot = sum(float(m["near"]) for m in mix)
        self.assertAlmostEqual(tot, self.head["sources_external_total"], delta=1)
        self.assertAlmostEqual(sum(float(m["share_pct"]) for m in mix), 100.0, delta=0.01)
        ex = sum(float(m["near"]) for m in mix if m["exchange_style"] == "True")
        self.assertAlmostEqual(100 * ex / tot, self.head["sources_exchange_style_pct"], delta=0.01)
        for m in mix:
            self.assertEqual(m["exchange_style"] == "True", m["label"].startswith("exchange-style"))


if __name__ == "__main__":
    unittest.main()
