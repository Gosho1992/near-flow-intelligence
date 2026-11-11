"""Evaluate the pre-registered prediction (PREDICTION.md) from data/out/daily.csv."""
import csv
from .net import ROOT

START, END = "2026-11-13", "2026-12-12"     # window-end dates covering 2026-11-12 00:00 .. 2026-12-11 23:59 UTC


def main():
    rows = [r for r in csv.DictReader(open(ROOT / "data" / "out" / "daily.csv")) if START <= r["date"] <= END]
    custody = buyback = 0.0
    excluded = []
    for r in rows:
        if r["creations"] == "" or r["redemptions"] == "" or r["buyback_fund_change"] == "":
            excluded.append(r["date"])
            continue
        custody += abs(float(r["creations"])) + abs(float(r["redemptions"]))
        buyback += abs(float(r["buyback_fund_change"]))
    have = len(rows) - len(excluded)
    print(f"windows available: {len(rows)} of 30; excluded: {excluded or 'none'}")
    print(f"sum |NRR custody moves|: {custody:,.0f} NEAR")
    print(f"sum |buyback-fund change|: {buyback:,.0f} NEAR")
    if len(rows) < 30:
        print("verdict: PENDING (window not complete)")
    elif len(excluded) > 5:
        print("verdict: VOID (more than 5 windows missing)")
    else:
        print("verdict:", "HOLDS" if custody > buyback else "FAILS")


if __name__ == "__main__":
    main()
