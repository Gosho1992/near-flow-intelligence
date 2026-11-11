"""Attribute NRR custody accounts from the custody hub's transaction history, with evidence.

Rule A (basket account): received principal (> 1,000 NEAR) from the hub AND later called
deposit_and_stake on a staking pool. Each account gets an evidence record (funding + staking tx).
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


def attribute():
    hist, out_, in_ = hub_transfers()
    candidates = sorted({o["to"] for o in out_ if o["near"] >= MIN_PRINCIPAL})
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
    accounts, others = [], []
    for acct in candidates:
        h = histories.get(acct, [])
        funding = [o for o in out_ if o["to"] == acct and o["near"] >= MIN_PRINCIPAL]
        stakes = [t for t in h if t["signer"] == acct and t["ok"] and any(
            a.get("method") == "deposit_and_stake" for a in t["actions"])]
        if funding and stakes:
            accounts.append({"account": acct, "pool": stakes[0]["receiver"], "rule": "A",
                             "confidence": "high: hub funding + deposit_and_stake observed",
                             "funding_tx": funding[0]["hash"], "funding_near": funding[0]["near"],
                             "stake_tx": stakes[0]["hash"], "first_height": funding[0]["height"]})
        else:
            others.append({"account": acct, "received_near": sum(f["near"] for f in funding),
                           "staked": bool(stakes), "first_tx": funding[0]["hash"] if funding else None})
    keep = {a["account"] for a in accounts} | set(EXTRA) | {HUB}
    return {"hub": HUB, "fee_payer": FEE_PAYER, "accounts": accounts, "hub_counterparties_out": others,
            "hub_in": in_, "hub_out": out_, "histories": {a: h for a, h in histories.items() if a in keep},
            "sources": {"pools": POOLS, "extra_accounts": EXTRA}}


if __name__ == "__main__":
    r = attribute()
    p = ROOT / "data" / "work"; p.mkdir(parents=True, exist_ok=True)
    (p / "attribution.json").write_text(json.dumps(r, indent=1, sort_keys=True))
    print(len(r["accounts"]), "attributed;", len(r["hub_counterparties_out"]), "other hub recipients;",
          len(r["hub_in"]), "hub inflows")
