"""Network refresh: extend daily heights to today, re-collect chain series, attribution and custody.

Idempotent: cached answers are reused, so re-running after a failure continues where it stopped.
Writes data/work/refresh.json (time of the last successful refresh) only when every step succeeded."""
import json, sys, time
from datetime import datetime, timezone
from .net import ROOT, rpc
from . import chain, collect_chain, attribution, collect_custody, build, institutional

W = ROOT / "data" / "work"


def log(msg):
    print(f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ} {msg}", flush=True)


def main():
    t0 = time.time()
    head = rpc("block", {"finality": "final"}, cacheable=False)["result"]["header"]["height"]
    log(f"head {head}")
    H = chain.daily_heights(head_height=head)
    (W / "heights.json").write_text(json.dumps(H, indent=0))
    log(f"{len(H)} daily heights, through {max(H)}")
    C = collect_chain.collect(H)
    (W / "chain.json").write_text(json.dumps(C, sort_keys=True))
    log(f"chain: {len(C['epochs'])} epochs")
    A = attribution.attribute()
    (W / "attribution.json").write_text(json.dumps(A, indent=1, sort_keys=True))
    log(f"attribution: {len(A['accounts'])} accounts")
    (W / "custody_liquid.json").write_text(json.dumps(collect_custody.collect(), sort_keys=True))
    (W / "exclusion.json").write_text(json.dumps(collect_custody.exclusion_check(), sort_keys=True))
    (W / "institutional.json").write_text(json.dumps(institutional.collect(), indent=1, sort_keys=True))
    counts = collect_custody.tx_counts(build.trace_accounts(A))
    (W / "tx_counts.json").write_text(json.dumps(counts, sort_keys=True))
    (W / "refresh.json").write_text(json.dumps({"refreshed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                                "head_height": head, "data_through": max(H)}, sort_keys=True))
    log(f"refreshed through {max(H)} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:   # leave refresh.json untouched so the dashboard shows the last good refresh
        log(f"REFRESH FAILED: {type(e).__name__}: {e}")
        sys.exit(1)
