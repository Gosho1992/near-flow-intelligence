"""Liquid NEAR held by each attributed basket account at each daily height (custody layer L3),
plus transaction counts of trace counterparties (used for the exchange-style heuristic)."""
import json
from .net import ROOT, view_account, tx_account

W = ROOT / "data" / "work"


def collect():
    H = json.loads((W / "heights.json").read_text())
    A = json.loads((W / "attribution.json").read_text())
    accts = [a["account"] for a in A["accounts"]]
    liquid = {}
    for d, h in sorted(H.items()):
        vals = {a: view_account(a, h) for a in accts}
        liquid[d] = {a: (None if v is None else v / 1e24) for a, v in vals.items()}   # None = lookup failed
    return liquid


def exclusion_check():
    """Delegators of Bitwise's other pools at the latest daily height: none may be an attributed NRR account."""
    from .chain import pool_accounts
    from .attribution import OTHER_BITWISE_POOLS
    H = json.loads((W / "heights.json").read_text())
    d, h = max(H.items())
    out = {"date": d, "height": h, "pools": {}}
    for p in OTHER_BITWISE_POOLS:
        pa = pool_accounts(p, h)
        out["pools"][p] = None if pa is None else sorted(pa)
    return out


SAMPLE = 200   # most recent transactions inspected for distinct counterparties


def counterparties(account):
    """Distinct counterparties among the account's SAMPLE most recent transactions."""
    from .net import tx_details, _post, TX_URL
    r = _post("tx", TX_URL + "/account", {"account_id": account, "limit": SAMPLE, "desc": True})
    hashes = [x["transaction_hash"] for x in r.get("account_txs", [])]
    seen = set()
    for t in tx_details(hashes):
        tx = t["transaction"]
        other = tx["signer_id"] if tx["receiver_id"] == account else tx["receiver_id"]
        if other != account:
            seen.add(other)
    return len(hashes), len(seen)


def tx_counts(accounts, min_txs=10000):
    """Transaction count of each account; for accounts with at least min_txs, also the number of distinct
    counterparties in their most recent transactions (exchange-style heuristic needs both)."""
    out = {}
    for a in accounts:
        n = tx_account(a, 1).get("txs_count")
        rec = {"txs": n}
        if n is not None and n >= min_txs:
            rec["sample"], rec["counterparties"] = counterparties(a)
        out[a] = rec
    return out


if __name__ == "__main__":
    import sys
    from .build import trace_accounts
    if "--counts-only" not in sys.argv:
        (W / "custody_liquid.json").write_text(json.dumps(collect(), sort_keys=True))
    (W / "exclusion.json").write_text(json.dumps(exclusion_check(), sort_keys=True))
    A = json.loads((W / "attribution.json").read_text())
    acc = trace_accounts(A)
    print(len(acc), "counterparties")
    (W / "tx_counts.json").write_text(json.dumps(tx_counts(acc), sort_keys=True))
    print("ok")
