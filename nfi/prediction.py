"""Evaluate the pre-registered prediction (PREDICTION.md) from data/out/daily.csv."""
import csv
from .net import ROOT

START, END = "2026-11-13", "2026-12-12"     # window-end dates covering 2026-11-12 00:00 .. 2026-12-11 23:59 UTC
WINDOWS = 30
MAX_EXCLUDED = 5


def evaluate(rows):
    """rows: dicts from daily.csv. Returns (verdict, custody_sum, buyback_sum, excluded_dates)."""
    rows = [r for r in rows if START <= r["date"] <= END]
    dates = [r["date"] for r in rows]
    if len(dates) != len(set(dates)):
        raise ValueError("duplicate dates in daily.csv")
    custody = buyback = 0.0
    excluded = []
    for r in rows:
        if (r.get("data_status", "complete") != "complete" or r["creations"] in ("", None)
                or r["redemptions"] in ("", None) or r["buyback_fund_change"] in ("", None)):
            excluded.append(r["date"])
            continue
        custody += abs(float(r["creations"])) + abs(float(r["redemptions"]))
        buyback += abs(float(r["buyback_fund_change"]))
    if len(rows) < WINDOWS:
        verdict = "PENDING"
    elif len(excluded) > MAX_EXCLUDED:
        verdict = "VOID"
    else:
        verdict = "HOLDS" if custody > buyback else "FAILS"
    return verdict, custody, buyback, excluded


def main():
    with open(ROOT / "data" / "out" / "daily.csv") as f:
        verdict, custody, buyback, excluded = evaluate(list(csv.DictReader(f)))
    print(f"excluded windows: {excluded or 'none'}")
    print(f"sum |NRR custody moves|: {custody:,.0f} NEAR")
    print(f"sum |buyback-fund change|: {buyback:,.0f} NEAR")
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
