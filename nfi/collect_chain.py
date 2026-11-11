"""Collect daily chain series into data/work/chain.json (cached raw responses in data/raw)."""
import json
from .net import ROOT
from .chain import (POOL, pool_accounts, supply_at, epoch_starts, epoch_mint, validators_stake, locked_sum,
                    buyback_fund, view_account)
from .attribution import HUB

W = ROOT / "data" / "work"


def collect(heights):
    days = sorted(heights)
    out = {"pool": POOL, "days": {}, "epochs": []}
    for d in days:
        h = heights[d]
        bb, parts = buyback_fund(h)
        out["days"][d] = {"height": h, "pool_accounts": pool_accounts(POOL, h), "total_supply": supply_at(h),
                          "hub_liquid": (view_account(HUB, h) or 0) / 1e24, "buyback_fund": bb,
                          "buyback_parts": parts}
    lo, hi = heights[days[0]], heights[days[-1]]
    starts = epoch_starts(lo, hi)
    vset = set()
    for i, s in enumerate(starts):
        st, accts = validators_stake(starts[i + 1]) if i + 1 < len(starts) else (None, [])
        vset |= set(accts)
        out["epochs"].append({"start": s, "mint": epoch_mint(s), "supply_at_start": supply_at(s),
                              "validators_stake": st})
    out["validator_set"] = sorted(vset)
    for d in days:   # total stake by locked balances (works for any height; checked vs validators RPC)
        out["days"][d]["locked_sum"] = locked_sum(out["validator_set"], heights[d])
    return out


if __name__ == "__main__":
    H = json.loads((W / "heights.json").read_text())
    c = collect(H)
    (W / "chain.json").write_text(json.dumps(c, sort_keys=True))
    print(len(c["days"]), "days;", len(c["epochs"]), "epochs")
