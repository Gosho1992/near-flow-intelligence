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
        liquid[d] = {a: (view_account(a, h) or 0) / 1e24 for a in accts}
    return liquid


def tx_counts(accounts):
    return {a: tx_account(a, 1).get("txs_count") for a in accounts}


if __name__ == "__main__":
    import sys
    from .build import trace_accounts
    if "--counts-only" not in sys.argv:
        (W / "custody_liquid.json").write_text(json.dumps(collect(), sort_keys=True))
    A = json.loads((W / "attribution.json").read_text())
    acc = trace_accounts(A)
    print(len(acc), "counterparties")
    (W / "tx_counts.json").write_text(json.dumps(tx_counts(acc), sort_keys=True))
    print("ok")
