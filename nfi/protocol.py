"""Protocol inflation setting at every daily height: the switch that tells us when HSP-029's ramp starts.

HSP-029 (approved 2 Nov 2026) lowers `max_inflation_rate` from 1/40 (2.5%) toward 1.6% only after Security
Council ratification, a validator-adopted protocol upgrade and a ~90-day grace period. We do not assume a
start date: we read the parameter from the chain each day, so month 0 of the ramp is observed, not guessed.
"""
import json
from .net import ROOT, rpc

W = ROOT / "data" / "work"


def at(height):
    r = (rpc("EXPERIMENTAL_protocol_config", {"block_id": height}) or {}).get("result")
    if not r or "max_inflation_rate" not in r:
        return None
    num, den = r["max_inflation_rate"]
    return {"protocol_version": r["protocol_version"], "max_inflation_rate": [num, den],
            "max_inflation_pct": round(100 * num / den, 6)}


def collect():
    H = json.loads((W / "heights.json").read_text())
    return {d: at(h) for d, h in sorted(H.items())}


if __name__ == "__main__":
    (W / "protocol.json").write_text(json.dumps(collect(), indent=1, sort_keys=True))
    print("ok")
