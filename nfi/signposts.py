"""Evaluate the frozen long-term signposts (SIGNPOSTS.md) on non-overlapping 30-day windows.

Window k covers 30 daily rows starting at row 2026-11-16 + 30k (row T = the day ending T 00:00 UTC, so window 1
is 15 Nov 00:00 to 14 Dec 23:59 UTC, the same convention as both predictions). For each complete window:
  absorption ratio a = sum(creations - redemptions) / sum(gross_issuance)
  buyback ratio    b = sum(buyback_fund_change) / sum(gross_issuance)
Rules (two consecutive complete windows each):
  BULLISH            a >= +1 in both
  BEARISH            a <= -1 in both
  STRUCTURALLY WRONG |a| < b in both, or any issuer figure in EITHER window differs from L1 by more than 0.5%
The most recently fired rule sets the state, which persists until another rule fires (frozen text).
  BASE (confirmed)   six complete windows with no bullish or bearish pair
A window with more than 5 rows missing or incomplete is VOID and breaks a consecutive pair.
"""
import csv, json
from datetime import date, timedelta
from .net import ROOT

FIRST = date(2026, 11, 16)
WINDOW, MAX_WINDOWS, MAX_EXCLUDED = 30, 36, 5
OUT = ROOT / "data" / "out"


def _f(v):
    return None if v in (None, "") else float(v)


def windows():
    return [(FIRST + timedelta(days=WINDOW * k), FIRST + timedelta(days=WINDOW * k + WINDOW - 1))
            for k in range(MAX_WINDOWS)]


def evaluate(rows):
    by = {}
    for r in rows:
        d = r["date"]
        if d in by:
            raise ValueError(f"duplicate row {d}")
        by[d] = r
    out = []
    for i, (s, e) in enumerate(windows(), 1):
        days = [(s + timedelta(days=j)).isoformat() for j in range(WINDOW)]
        have = [by[d] for d in days if d in by]
        if len(have) < WINDOW and (e.isoformat() > max(by) if by else True):
            out.append({"window": i, "start": s.isoformat(), "end": e.isoformat(), "status": "PENDING",
                        "rows": len(have)})
            continue
        ok = [r for r in have if r.get("data_status", "complete") == "complete" 
              and all(_f(r.get(k)) is not None for k in ("gross_issuance", "creations", "redemptions"))]
        excl = WINDOW - len(ok)
        w = {"window": i, "start": s.isoformat(), "end": e.isoformat(), "rows": len(have), "excluded": excl}
        if excl > MAX_EXCLUDED:
            out.append({**w, "status": "VOID"})
            continue
        net = sum(_f(r["creations"]) - _f(r["redemptions"]) for r in ok)
        iss = sum(_f(r["gross_issuance"]) for r in ok)
        bb = sum(_f(r["buyback_fund_change"]) or 0 for r in ok)
        gaps = [abs(_f(r["issuer_gap_pct"])) for r in ok if _f(r.get("issuer_gap_pct")) is not None]
        a, b = net / iss, bb / iss
        out.append({**w, "status": "COMPLETE", "net_flow": net, "issuance": iss, "buyback_change": bb,
                    "absorption": a, "buyback_ratio": b, "max_issuer_gap_pct": max(gaps) if gaps else None,
                    "bull": a >= 1, "bear": a <= -1, "below_buyback": abs(a) < b,
                    "issuer_off": bool(gaps) and max(gaps) > 0.5})
    state, fired = "NOT YET TESTABLE", []
    comp = [w for w in out if w["status"] in ("COMPLETE", "VOID")]
    for x, y in zip(comp, comp[1:]):
        if x["status"] == y["status"] == "COMPLETE":
            hits = {"bull": x["bull"] and y["bull"], "bear": x["bear"] and y["bear"],
                    # frozen rule: |a| < b in both windows, OR an issuer figure off by > 0.5% in EITHER window
                    "wrong": (x["below_buyback"] and y["below_buyback"]) or x["issuer_off"] or y["issuer_off"]}
            for k, hit in hits.items():
                if hit:
                    fired.append({"rule": k, "windows": [x["window"], y["window"]], "end": y["end"]})
    done = [w for w in out if w["status"] == "COMPLETE"]
    if fired:
        state = {"bull": "BULLISH", "bear": "BEARISH", "wrong": "STRUCTURALLY WRONG"}[fired[-1]["rule"]]
    elif len(done) >= 6:
        state = "BASE"
    elif done:
        state = "MONITORING"
    return {"state": state, "fired": fired, "complete": len(done), "windows": out}


def main():
    rows = list(csv.DictReader((OUT / "daily.csv").open()))
    r = evaluate(rows)
    print(f"signposts: {r['state']} ({r['complete']} complete windows; first ends {r['windows'][0]['end']})")
    for w in r["windows"]:
        if w["status"] != "PENDING":
            print(" ", json.dumps(w))


if __name__ == "__main__":
    main()
