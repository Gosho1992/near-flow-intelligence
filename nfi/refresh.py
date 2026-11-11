"""Network refresh: extend daily heights to today, re-collect chain series, attribution and custody."""
import json
from .net import ROOT, rpc
from . import chain, collect_chain, attribution, collect_custody, build

W = ROOT / "data" / "work"


def main():
    head = rpc("block", {"finality": "final"}, cacheable=False)["result"]["header"]["height"]
    H = chain.daily_heights(head_height=head)
    (W / "heights.json").write_text(json.dumps(H, indent=0))
    (W / "chain.json").write_text(json.dumps(collect_chain.collect(H), sort_keys=True))
    A = attribution.attribute()
    (W / "attribution.json").write_text(json.dumps(A, indent=1, sort_keys=True))
    (W / "custody_liquid.json").write_text(json.dumps(collect_custody.collect(), sort_keys=True))
    counts = collect_custody.tx_counts(build.trace_accounts(A))
    (W / "tx_counts.json").write_text(json.dumps(counts, sort_keys=True))
    print("refreshed through", max(H))


if __name__ == "__main__":
    main()
