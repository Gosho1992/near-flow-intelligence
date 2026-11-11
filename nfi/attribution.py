"""Attribute NRR custody accounts from the custody hub's transaction history, with evidence.

Rule A (basket account): received principal (>= 1,000 NEAR) from the hub AND, strictly after that
funding, itself called deposit_and_stake on the NRR pool. Each account gets an evidence record (funding + staking tx).
"""
import json
from .history import account_history
from .net import ROOT

HUB = "23ced4300a4bf282bf94a4fcd2b0af32ad291ef531f544f6d7d283e8ff1e684a"
FEE_PAYER = "3fb56deeaa026afe28210136c1198d05a16b00e5eae9648e151b6fe0e3846721"
MIN_PRINCIPAL = 1000.0


def hub_transfers():
    hist = account_history(HUB)
    out_, in_ = [], []
    for t in hist:
        if not t["ok"]:
            continue
        for a in t["actions"]:
            if a["kind"] != "Transfer":
                continue
            if t["signer"] == HUB:
                out_.append({"to": t["receiver"], "near": a["near"], "hash": t["hash"], "height": t["height"], "ts": t["ts"]})
            elif t["receiver"] == HUB:
                in_.append({"from": t["signer"], "near": a["near"], "hash": t["hash"], "height": t["height"], "ts": t["ts"]})
    return hist, out_, in_


POOLS = ["bitwise_2.poolv1.near"]
EXTRA = ["fb79675c31abbbb3cc52c47007378305ca2be8a5e2fb68ac1e54fb696ebdcb91",
         "508a5b6d2747f3dee3d38d467fadb6376e43723de4fb42e7cb32d1450d6960bd"]   # pass-through / side account seen in traces


OTHER_BITWISE_POOLS = ["bitwise_1.poolv1.near", "svrn_bitwise.poolv1.near"]   # other Bitwise products: excluded
HIGH_MAX_DELAY_H = 168        # funding -> stake within 7 days ...
HIGH_MAX_GAP = 1.0            # ... and stake within 1 NEAR of the funding (gas, dust) => "high"


def apply_rule(out_, histories, pools):
    """Rule A, as a pure function so it can be tested: an account is attributed only if the hub funded it
    with >= MIN_PRINCIPAL NEAR and, strictly AFTER that funding, the account itself called deposit_and_stake
    on one of `pools`. Returns (accounts, rejected)."""
    candidates = sorted({o["to"] for o in out_ if o["near"] >= MIN_PRINCIPAL})
    accounts, rejected = [], []
    for acct in candidates:
        fundings = sorted((o for o in out_ if o["to"] == acct and o["near"] >= MIN_PRINCIPAL),
                          key=lambda o: o["height"])
        stakes = [t for t in histories.get(acct, []) if t["signer"] == acct and t["ok"]
                  and t["receiver"] in pools and any(a.get("method") == "deposit_and_stake" for a in t["actions"])]
        pair = None
        for st in sorted(stakes, key=lambda t: t["height"]):
            before = [f for f in fundings if f["height"] < st["height"]]
            if before:
                pair = (before[-1], st)
                break
        if not pair:
            reason = ("no deposit_and_stake into the NRR pool" if not stakes
                      else "staked before any hub funding")
            rejected.append({"account": acct, "reason": reason, "received_near": sum(f["near"] for f in fundings),
                             "first_funding_tx": fundings[0]["hash"]})
            continue
        f, st = pair
        stake_near = sum(a.get("near", 0) for a in st["actions"] if a.get("method") == "deposit_and_stake")
        delay_h = (int(st["ts"]) - int(f["ts"])) / 3.6e12
        gap = f["near"] - stake_near
        high = delay_h <= HIGH_MAX_DELAY_H and abs(gap) <= HIGH_MAX_GAP
        accounts.append({
            "account": acct, "pool": st["receiver"], "rule": "A",
            "confidence": "high" if high else "medium",
            "confidence_reason": (f"staked {stake_near:,.2f} NEAR {delay_h:.1f} h after receiving {f['near']:,.2f} "
                                  f"NEAR from the hub (difference {gap:,.2f} NEAR)"),
            "funding_tx": f["hash"], "funding_near": f["near"], "funding_height": f["height"],
            "stake_tx": st["hash"], "stake_near": stake_near, "stake_height": st["height"],
            "delay_hours": delay_h, "amount_gap_near": gap, "first_height": f["height"]})
    return accounts, rejected


def attribute():
    hist, out_, in_ = hub_transfers()
    # Histories of the pool(s) and hub contain every stake/unstake/withdraw and every funding/return.
    pool_txs = [t for p in POOLS for t in account_history(p)]
    everything = {t["hash"]: t for t in pool_txs + hist}
    for a in EXTRA:
        for t in account_history(a):
            everything[t["hash"]] = t
    histories = {}
    for t in everything.values():
        for a in {t["signer"], t["receiver"]}:
            histories.setdefault(a, []).append(t)
    for a in histories:
        histories[a].sort(key=lambda x: (x["height"], x["hash"]))
    accounts, rejected = apply_rule(out_, histories, POOLS)
    # every delegator's own pool transactions (heights), so reward probes can exclude any active account
    activity = {}
    for t in pool_txs:
        if t["receiver"] in POOLS:
            activity.setdefault(t["signer"], set()).add(t["height"])
    keep = {a["account"] for a in accounts} | set(EXTRA) | {HUB}
    return {"hub": HUB, "fee_payer": FEE_PAYER, "accounts": accounts, "hub_counterparties_out": rejected,
            "hub_in": in_, "hub_out": out_, "histories": {a: h for a, h in histories.items() if a in keep},
            "pool_activity": {a: sorted(v) for a, v in sorted(activity.items())},
            "sources": {"pools": POOLS, "extra_accounts": EXTRA, "excluded_pools": OTHER_BITWISE_POOLS}}


if __name__ == "__main__":
    r = attribute()
    p = ROOT / "data" / "work"; p.mkdir(parents=True, exist_ok=True)
    (p / "attribution.json").write_text(json.dumps(r, indent=1, sort_keys=True))
    print(len(r["accounts"]), "attributed;", len(r["hub_counterparties_out"]), "other hub recipients;",
          len(r["hub_in"]), "hub inflows")
