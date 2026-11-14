"""Evaluate pre-registered prediction 2 (PREDICTION-2.md): |NRR net custody flow| vs |buyback-fund net change|."""
import csv
from .net import ROOT

START, END = "2026-11-16", "2026-12-15"     # window-end dates covering 2026-11-15 00:00 .. 2026-12-14 23:59 UTC
WINDOWS = 30
MAX_EXCLUDED = 5


def evaluate(rows):
    """rows: dicts from daily.csv. Returns (verdict, nrr_net, buyback_net, excluded_dates)."""
    rows = [r for r in rows if START <= r["date"] <= END]
    dates = [r["date"] for r in rows]
    if len(dates) != len(set(dates)):
        raise ValueError("duplicate dates in daily.csv")
    nrr = buyback = 0.0
    excluded = []
    for r in rows:
        if (r.get("data_status", "complete") != "complete" or r["creations"] in ("", None)
                or r["redemptions"] in ("", None) or r["buyback_fund_change"] in ("", None)):
            excluded.append(r["date"])
            continue
        nrr += float(r["creations"]) - float(r["redemptions"])
        buyback += float(r["buyback_fund_change"])
    if len(rows) < WINDOWS:
        verdict = "PENDING"
    elif len(excluded) > MAX_EXCLUDED:
        verdict = "VOID"
    else:
        verdict = "HOLDS" if abs(nrr) > abs(buyback) else "FAILS"
    return verdict, nrr, buyback, excluded


def main():
    with open(ROOT / "data" / "out" / "daily.csv") as f:
        verdict, nrr, buyback, excluded = evaluate(list(csv.DictReader(f)))
    print("Prediction 2 (net against net)")
    print(f"excluded windows: {excluded or 'none'}")
    print(f"NRR net custody flow: {nrr:+,.0f} NEAR")
    print(f"buyback-fund net change: {buyback:+,.0f} NEAR")
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
