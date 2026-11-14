"""Other institutional holders: partial on-chain observations, kept separate from NRR.

SVRN, Inc. (Nasdaq: SVRN) reports its NEAR treasury itself. The only part we can read on-chain with a known
link to it is Bitwise's `svrn_bitwise.poolv1.near` pool. We record that pool's delegators at the latest daily
height, account by account. This is NOT a reconstruction of SVRN's treasury: it is never added to NRR's
figures, never reconciled with SVRN's reported total, and never added to that total (it may be part of it).
"""
import json
from .net import ROOT
from .chain import pool_accounts

W = ROOT / "data" / "work"
SVRN = {
    "holder": "SVRN, Inc. (Nasdaq: SVRN)",
    "holder_type": "listed treasury company",
    "reported_holdings_near": 55_500_000,
    "reported_holdings_text": "more than 55.5 million NEAR",
    "reported_as_of": "2026-08-27",
    "reported_source": "https://www.sec.gov/Archives/edgar/data/1869467/000091957426005810/p15060228_ex99-1.htm",
    "observed_pool": "svrn_bitwise.poolv1.near",
}


def observe(height):
    pa = pool_accounts(SVRN["observed_pool"], height)
    if pa is None:
        return None
    return {a: {"staked": v[0], "unstaked": v[1]} for a, v in sorted(pa.items())}


def collect():
    H = json.loads((W / "heights.json").read_text())
    d, h = max(H.items())
    return {"date": d, "height": h, **SVRN, "accounts": observe(h)}


if __name__ == "__main__":
    (W / "institutional.json").write_text(json.dumps(collect(), indent=1, sort_keys=True))
    print("ok")
