"""Reconcile the Bitwise NEAR ETF's first 10-Q (30 Sep 2026) with the chain, at the filing's valuation time.

Three tests, all quantities read from the chain at the last block at or before 30 Sep 2026 20:00 UTC (16:00 ET):
  1. In-kind creations (5,010,335.4989 NEAR) vs hub inflows from the in-kind wallet.
  2. Staked value ($553,300 at the $5.30 principal-market price) vs staked balances in bitwise_2.poolv1.near.
  3. Purchased NEAR not yet on-chain at valuation time, valued at the $5.38 NAV reference, vs the
     $14,039,097 receivable for creations.
The filing names no addresses. This tests the reconstruction against an aggregate; it does not prove ownership,
and it does not change Rule A (the frozen attribution rule).
"""
import base64, json
from datetime import datetime, timezone
from .net import ROOT, rpc

W, OUT = ROOT / "data" / "work", ROOT / "data" / "out"
POOL = "bitwise_2.poolv1.near"
VALUATION_HEIGHT = 217960556          # last block at or before 2026-09-30 20:00:00 UTC (19:59:59.998)
SEED = "432766610e6d7069916d5207202505f46244539b905bb73e66e7ff3094e7b4c5"      # Rule A account
ONE_HOP = "9a00031933695207a60a3af95cfaaadcea863812ecbc30400c109417dadf21b3"   # funded by SEED
IN_KIND_WALLET = "60142764c4cd3239d7d6e1973e87073f9d25773af225a74b22f3f9c9761fe8a5"
F = {"in_kind": 5010335.4989, "purchases": 4801521.4703, "rewards": 13.2579, "total": 9811870.2271,
     "staked_usd": 553300, "price_principal": 5.30, "price_nav": 5.38,
     "receivable_creations": 14039097, "payable_purchased": 14044291}
FUND_MIN = 1000      # hub inflows below this are gas top-ups and test pennies, not fund NEAR


def _call(method, args, height=VALUATION_HEIGHT):
    r = rpc("query", {"request_type": "call_function", "block_id": height, "account_id": POOL,
                      "method_name": method,
                      "args_base64": base64.b64encode(json.dumps(args).encode()).decode()})["result"]
    return json.loads(bytes(r["result"]))


def block_time(height):
    return datetime.fromtimestamp(int(rpc("block", {"block_id": height})["result"]["header"]["timestamp"]) / 1e9,
                                  timezone.utc)


def run():
    A = json.loads((W / "attribution.json").read_text())
    accts = {a["account"] for a in A["accounts"]}
    t_val, t_next = block_time(VALUATION_HEIGHT), block_time(VALUATION_HEIGHT + 1)
    pool = {x["account_id"]: int(x["staked_balance"]) / 1e24 for x in _call("get_accounts", {"from_index": 0, "limit": 100})}
    staked_two = pool.get(SEED, 0) + pool.get(ONE_HOP, 0)
    staked_rule_a = sum(v for k, v in pool.items() if k in accts)
    staked_all = sum(pool.values())
    implied = F["staked_usd"] / F["price_principal"]
    ins = [i for i in A["hub_in"] if i["height"] <= VALUATION_HEIGHT]
    in_kind = sum(i["near"] for i in ins if i["from"] == IN_KIND_WALLET)
    fund_in = [i for i in ins if i["near"] >= FUND_MIN]
    purchased_onchain = sum(i["near"] for i in fund_in if i["from"] != IN_KIND_WALLET)
    undelivered = F["purchases"] - purchased_onchain
    out = {
        "valuation_height": VALUATION_HEIGHT, "valuation_block_time": t_val.isoformat(),
        "next_block_time": t_next.isoformat(), "filing": F,
        "in_kind_onchain": in_kind, "in_kind_diff": in_kind - F["in_kind"],
        "in_kind_transfers": [{"hash": i["hash"], "height": i["height"], "near": i["near"]}
                              for i in ins if i["from"] == IN_KIND_WALLET],
        "staked_implied": implied, "staked_seed_plus_one_hop": staked_two,
        "staked_rule_a_only": staked_rule_a, "staked_whole_pool": staked_all,
        "staked_diff": staked_two - implied, "staked_diff_pct": 100 * (staked_two - implied) / implied,
        "staked_rule_a_only_diff_pct": 100 * (staked_rule_a - implied) / implied,
        "staked_whole_pool_diff_pct": 100 * (staked_all - implied) / implied,
        "pool_accounts_at_valuation": len(pool),
        "purchased_onchain": purchased_onchain, "purchased_undelivered": undelivered,
        "undelivered_value_at_nav": undelivered * F["price_nav"],
        "receivable_diff_usd": undelivered * F["price_nav"] - F["receivable_creations"],
        "receivable_diff_pct": 100 * (undelivered * F["price_nav"] - F["receivable_creations"]) / F["receivable_creations"],
        "fund_inflows_onchain": in_kind + purchased_onchain,
    }
    return out


if __name__ == "__main__":
    r = run()
    (W / "sec_reconciliation.json").write_text(json.dumps(r, indent=1, sort_keys=True))
    print(f"in-kind diff {r['in_kind_diff']:+.6f} NEAR · staked diff {r['staked_diff']:+.2f} NEAR "
          f"({r['staked_diff_pct']:+.4f}%) · receivable diff ${r['receivable_diff_usd']:+,.0f}")
