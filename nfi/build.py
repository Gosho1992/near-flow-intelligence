"""Turn the cached chain data in data/work/ into the published outputs in data/out/.

Runs offline. Every number shown in the docs and on the site is written here, to
data/out/headline.json, and nowhere else.
"""
import csv, json, math, statistics
from collections import defaultdict
from datetime import datetime, timezone

from .net import ROOT
from .attribution import HUB, FEE_PAYER

W = ROOT / "data" / "work"
OUT = ROOT / "data" / "out"
POOL_EVENT_MIN = 1.0            # NEAR; ignore dust
PROBE_MIN = 1000.0              # reward-probe accounts need at least this much staked
EXCHANGE_STYLE_MIN_TXS = 10000  # published heuristic for "exchange-style wallet"


def load(name):
    return json.loads((W / name).read_text())


def utc(ts_ns):
    return datetime.fromtimestamp(int(ts_ns) / 1e9, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def window_of(height, heights_sorted):
    """Snapshot day whose 00:00 height is the first one strictly above `height`."""
    for d, h in heights_sorted:
        if h > height:
            return d
    return None


# ---------------------------------------------------------------- events
def classify_events(attr, heights_sorted):
    accts = {a["account"]: a for a in attr["accounts"]}
    pool_of = {a: v["pool"] for a, v in accts.items()}
    events = []
    for acct, hist in attr["histories"].items():
        if acct not in accts:
            continue
        pool = pool_of[acct]
        for t in hist:
            if not t["ok"]:
                continue
            base = {"account": acct, "hash": t["hash"], "height": t["height"], "time": utc(t["ts"]),
                    "window": window_of(t["height"], heights_sorted)}
            if t["receiver"] == acct and t["signer"] == HUB:
                amt = sum(a.get("near", 0) for a in t["actions"] if a["kind"] == "Transfer")
                events.append({**base, "type": "funded_by_hub", "near": amt})
            if t["signer"] != acct:
                continue
            for a in t["actions"]:
                m = a.get("method")
                if t["receiver"] == pool and m in ("deposit_and_stake", "deposit"):
                    events.append({**base, "type": "creation_stake", "near": a["near"], "pool": pool})
                elif t["receiver"] == pool and m in ("unstake", "unstake_all"):
                    amt = 0.0
                    for lg in t["logs"]:
                        if f"@{acct} unstaking" in lg:
                            try:
                                amt = int(lg.split("unstaking")[1].split(".")[0].strip().split()[0]) / 1e24
                            except (ValueError, IndexError):
                                pass
                    events.append({**base, "type": "unstake", "near": amt, "pool": pool})
                elif t["receiver"] == pool and m in ("withdraw", "withdraw_all"):
                    amt = sum(x["near"] for x in t["receipt_transfers"] if x["from"] == pool and x["to"] == acct)
                    events.append({**base, "type": "redemption_withdraw", "near": amt, "pool": pool})
                elif a["kind"] == "Transfer" and a["near"] >= POOL_EVENT_MIN:
                    events.append({**base, "type": "return_to_hub" if t["receiver"] == HUB else "transfer_out",
                                   "near": a["near"], "to": t["receiver"]})
    events.sort(key=lambda e: (e["height"], e["hash"], e["type"]))
    return events


# ---------------------------------------------------------------- traces
def follow(hub_out, after_height, amount, tol=0.02):
    """Hub transfers after `after_height` whose amount is within tol of `amount` (first match)."""
    for o in sorted(hub_out, key=lambda o: o["height"]):
        if o["height"] > after_height and abs(o["near"] - amount) <= tol * amount:
            return o
    return None


def build_traces(attr, events, counts):
    hist = attr["histories"]
    traces = []
    by_acct = defaultdict(list)
    for e in events:
        by_acct[e["account"]].append(e)
    for acct, evs in by_acct.items():
        wd = [e for e in evs if e["type"] == "redemption_withdraw"]
        for w in wd:
            hops = [e for e in evs if e["height"] >= w["height"] and e["type"] in ("return_to_hub", "transfer_out")][:1]
            steps = [e for e in evs if e["type"] == "unstake" and e["height"] <= w["height"]][-1:] + [w] + hops
            nxt = None
            if hops and hops[0]["type"] == "return_to_hub":
                nxt = follow(attr["hub_out"], hops[0]["height"], hops[0]["near"])
                if not nxt:   # the hub may forward several same-day returns as one transfer
                    grp = [e for e in events if e["type"] == "return_to_hub"
                           and abs(e["height"] - hops[0]["height"]) <= 86400]
                    if len(grp) > 1:
                        nxt = follow(attr["hub_out"], max(e["height"] for e in grp), sum(e["near"] for e in grp))
                        if nxt:
                            nxt = {**nxt, "combined_with": sorted({e["account"] for e in grp} - {acct})}
            elif hops:  # basket account sent elsewhere first (observed once): follow that account
                mid = hops[0]["to"]
                back = [t for t in hist.get(mid, []) if t["signer"] == mid and t["receiver"] == HUB]
                if back:
                    b = back[0]
                    steps.append({"type": "return_to_hub", "account": mid, "hash": b["hash"], "height": b["height"],
                                  "time": utc(b["ts"]), "near": sum(a.get("near", 0) for a in b["actions"]), "to": HUB})
                    nxt = follow(attr["hub_out"], b["height"], steps[-1]["near"])
            if not nxt and steps[-1].get("to") == HUB:
                later = [o for o in sorted(attr["hub_out"], key=lambda o: o["height"])
                         if o["height"] > steps[-1]["height"] and o["near"] >= 1000]
                if later:
                    o = later[0]
                    steps.append({"type": "hub_next_unmatched", "account": HUB, "hash": o["hash"], "height": o["height"],
                                  "time": utc(o["ts"]), "near": o["near"], "to": o["to"]})
            if nxt:
                steps.append({"type": "hub_to_next", "account": HUB, "hash": nxt["hash"], "height": nxt["height"],
                              "time": utc(nxt["ts"]), "near": nxt["near"], "to": nxt["to"],
                              "combined_with": nxt.get("combined_with", [])})
                onward = [t for t in hist.get(nxt["to"], []) if t["signer"] == nxt["to"] and t["height"] >= nxt["height"]]
                for t in onward[:1]:
                    amt = sum(a.get("near", 0) for a in t["actions"] if a["kind"] == "Transfer")
                    steps.append({"type": "onward", "account": nxt["to"], "hash": t["hash"], "height": t["height"],
                                  "time": utc(t["ts"]), "near": amt, "to": t["receiver"]})
            for s in steps:
                for k in ("account", "to"):
                    a = s.get(k)
                    if a:
                        s[k + "_label"] = label(a, attr, counts)
            traces.append({"kind": "redemption", "account": acct, "near": w["near"], "time": w["time"], "steps": steps})
    # creations: one per account (funding -> stake), with the hub's preceding inflows as context
    for acct, evs in by_acct.items():
        f = [e for e in evs if e["type"] == "funded_by_hub"][:1]
        s = [e for e in evs if e["type"] == "creation_stake"][:1]
        if f and s:
            steps = [{**f[0], "account": HUB, "to": acct}, {**s[0], "to": s[0]["pool"]}]
            for st in steps:
                for k in ("account", "to"):
                    st[k + "_label"] = label(st[k], attr, counts)
            prior = [i for i in attr["hub_in"] if i["height"] <= f[0]["height"]]
            ctx = sorted(prior, key=lambda i: -i["height"])[:3]
            traces.append({"kind": "creation", "account": acct, "near": s[0]["near"], "time": s[0]["time"],
                           "steps": steps, "hub_inflows_before": [
                               {**c, "time": utc(c["ts"]), "from_label": label(c["from"], attr, counts)} for c in ctx]})
    traces.sort(key=lambda t: (-t["near"], t["time"]))
    return traces


def label(a, attr, counts):
    accts = {x["account"] for x in attr["accounts"]}
    if a == HUB:
        return "custody hub (inferred: funds every basket account, receives every redemption)"
    if a == FEE_PAYER:
        return "fee payer (sends 0.15 NEAR for gas)"
    if a in accts:
        return "NRR basket account (rule A: hub funding + deposit_and_stake)"
    if a.endswith(".poolv1.near"):
        return "staking pool"
    n = counts.get(a)
    if n is not None and n >= EXCHANGE_STYLE_MIN_TXS:
        return f"exchange-style wallet (heuristic: {n:,} transactions)"
    if n is not None:
        return f"unlabelled account ({n:,} transactions)"
    return "unlabelled account"


def trace_accounts(attr, top_in=10):
    """Counterparties whose transaction counts feed the exchange-style label (kept small: one API call each)."""
    accts = {x["account"] for x in attr["accounts"]}
    out = {o["to"] for o in attr["hub_out"] if o["near"] >= 1000}
    ins = sorted(attr["hub_in"], key=lambda i: -i["near"])
    out |= {i["from"] for i in ins[:top_in]}
    for a, hist in attr["histories"].items():
        if a not in accts and a != HUB:
            out.add(a)
            out |= {t["receiver"] for t in hist if t["signer"] == a}
    return sorted(a for a in out if a not in accts and a not in (HUB, FEE_PAYER) and not a.endswith(".poolv1.near"))


# ---------------------------------------------------------------- main
def build():
    H = load("heights.json")
    hs = sorted(H.items())
    days = [d for d, _ in hs]
    C = load("chain.json")
    A = load("attribution.json")
    L3 = load("custody_liquid.json")
    counts = load("tx_counts.json")
    attributed = {a["account"] for a in A["accounts"]}

    events = classify_events(A, hs)
    ev_by_win = defaultdict(lambda: defaultdict(float))
    for e in events:
        if e["window"]:
            ev_by_win[e["window"]][e["type"]] += e["near"]

    # epochs -> gross issuance per window
    epochs = C["epochs"]
    mint_by_win = defaultdict(float)
    for ep in epochs:
        w = window_of(ep["start"] - 1, hs)   # mint lands at the epoch's first block
        if w:
            mint_by_win[w] += ep["mint"]

    issuer = {r["date"]: r for r in csv.DictReader(open(ROOT / "data" / "issuer_snapshots.csv"))}

    rows, prev = [], None
    for d in days:
        x = C["days"][d]
        pa = x["pool_accounts"]
        l1 = sum(v[0] for a, v in pa.items() if a in attributed)
        l2 = sum(v[1] for a, v in pa.items() if a in attributed)
        l3 = sum(L3.get(d, {}).values()) if d in L3 else None
        l4 = x["hub_liquid"]
        others = sum(v[0] + v[1] for a, v in pa.items() if a not in attributed)
        r = {"date": d, "height": x["height"], "l1_staked": l1, "l2_unstaked": l2, "l3_basket_liquid": l3,
             "l4_hub_liquid": l4, "nrr_holdings": l1 + l2,
             "nrr_custody_total": (l1 + l2 + (l3 or 0) + l4), "pool_other_delegators": others,
             "attributed_accounts_in_pool": sum(1 for a, v in pa.items() if a in attributed and v[0] + v[1] > 0),
             "total_supply": x["total_supply"], "total_staked": x.get("locked_sum"),
             "buyback_fund": x["buyback_fund"]}
        ev = ev_by_win.get(d, {})
        r["creations"] = ev.get("creation_stake", 0.0)
        r["redemptions"] = ev.get("redemption_withdraw", 0.0)
        r["custody_flow"] = r["creations"] - r["redemptions"]
        if prev:
            # reward rate from probe delegators: median staked growth among accounts with no own events
            busy = {e["account"] for e in events if e["window"] == d}
            ppa = C["days"][prev["date"]]["pool_accounts"]
            ratios = [pa[a][0] / ppa[a][0] - 1 for a in pa if a in ppa and a not in busy
                      and ppa[a][0] >= PROBE_MIN and pa[a][0] >= PROBE_MIN and pa[a][1] == ppa[a][1]]
            rate = statistics.median(ratios) if ratios else None
            r["reward_rate"] = rate
            r["reward_probes"] = len(ratios)
            r["nrr_rewards"] = rate * prev["l1_staked"] if rate is not None else None
            dh = r["nrr_holdings"] - prev["nrr_holdings"]
            r["holdings_change"] = dh
            r["unexplained"] = dh - r["custody_flow"] - (r["nrr_rewards"] or 0)
            r["net_supply_change"] = r["total_supply"] - prev["total_supply"]
            r["gross_issuance"] = mint_by_win.get(d, 0.0)
            r["burn"] = r["gross_issuance"] - r["net_supply_change"]
            r["buyback_fund_change"] = (r["buyback_fund"] - prev["buyback_fund"]
                                        if r["buyback_fund"] is not None and prev["buyback_fund"] is not None else None)
        else:
            for k in ("reward_rate", "reward_probes", "nrr_rewards", "holdings_change", "unexplained",
                      "net_supply_change", "gross_issuance", "burn", "buyback_fund_change"):
                r[k] = None
        r["nrr_share_total_supply_pct"] = 100 * r["nrr_holdings"] / r["total_supply"]
        r["nrr_share_staked_pct"] = 100 * r["l1_staked"] / r["total_staked"] if r["total_staked"] else None
        iss = issuer.get(d)
        r["issuer_near_in_trust"] = float(iss["near_in_trust"]) if iss else None
        r["issuer_gap_pct"] = (100 * (r["nrr_holdings"] - r["issuer_near_in_trust"]) / r["issuer_near_in_trust"]
                               if iss else None)
        rows.append(r)
        prev = r

    traces = build_traces(A, events, counts)
    head = rnd(headline(rows, events, issuer, A, traces, C))
    rows, events, traces = rnd(rows), rnd(events), rnd(traces)
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "daily.csv", rows)
    write_csv(OUT / "events.csv", [{k: e.get(k) for k in
                                    ("time", "window", "type", "account", "near", "pool", "to", "hash", "height")}
                                   for e in events])
    write_csv(OUT / "accounts.csv", A["accounts"])
    (OUT / "traces.json").write_text(json.dumps(traces, indent=1, sort_keys=True))
    (OUT / "headline.json").write_text(json.dumps(head, indent=1, sort_keys=True))
    (OUT / "site_data.json").write_text(json.dumps({"daily": rows, "events": events, "traces": traces[:40],
                                                    "headline": head, "issuer": list(issuer.values()),
                                                    "accounts": A["accounts"]}, sort_keys=True))
    return rows, head


def rnd(x):
    """Round floats to 6 decimals so outputs are identical across Python versions and platforms."""
    if isinstance(x, float):
        return round(x, 6)
    if isinstance(x, dict):
        return {k: rnd(v) for k, v in x.items()}
    if isinstance(x, list):
        return [rnd(v) for v in x]
    return x


def write_csv(path, rows):
    if not rows:
        path.write_text("")
        return
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else (round(r[k], 6) if isinstance(r[k], float) else r[k]))
                        for k in keys})


def headline(rows, events, issuer, A, traces, C):
    start = next(r for r in rows if r["nrr_holdings"] > 1000)        # first day with NRR stake
    base = rows[rows.index(start) - 1]
    last = rows[-1]
    peak = max(rows, key=lambda r: r["nrr_holdings"])
    win = [r for r in rows if r["date"] > base["date"]]
    s = lambda k, rr=win: sum(r[k] or 0 for r in rr)
    last30 = rows[-30:]
    abs_custody = sum(abs(r["creations"]) + abs(r["redemptions"]) for r in win)
    abs_buyback = sum(abs(r["buyback_fund_change"] or 0) for r in win)
    gaps = {d: rows[[r["date"] for r in rows].index(d)]["issuer_gap_pct"] for d in issuer if d in {r["date"] for r in rows}}
    rr = [r["reward_rate"] for r in win if r["reward_rate"] is not None]
    h = {
        "data_through": last["date"], "window_start": base["date"], "days": len(win),
        "attributed_accounts": len(A["accounts"]),
        "nrr_holdings_latest": last["nrr_holdings"], "nrr_peak": peak["nrr_holdings"], "nrr_peak_date": peak["date"],
        "change_since_peak": last["nrr_holdings"] - peak["nrr_holdings"],
        "change_since_peak_pct": 100 * (last["nrr_holdings"] / peak["nrr_holdings"] - 1),
        "creations_total": s("creations"), "redemptions_total": s("redemptions"),
        "custody_flow_net": s("custody_flow"), "rewards_total": s("nrr_rewards"), "unexplained_total": s("unexplained"),
        "gross_issuance_total": s("gross_issuance"), "burn_total": s("burn"), "net_supply_change_total": s("net_supply_change"),
        "buyback_fund_change_total": s("buyback_fund_change"),
        "abs_custody_moves": abs_custody, "abs_buyback_fund_moves": abs_buyback,
        "ratio_abs_custody_to_abs_buyback": abs_custody / abs_buyback if abs_buyback else None,
        "ratio_creations_to_gross_issuance": s("creations") / s("gross_issuance") if s("gross_issuance") else None,
        "last30_creations": s("creations", last30), "last30_redemptions": s("redemptions", last30),
        "last30_buyback_fund_change": s("buyback_fund_change", last30),
        "last30_gross_issuance": s("gross_issuance", last30),
        "reward_rate_annualised_pct": 100 * ((1 + statistics.median(rr)) ** 365 - 1) if rr else None,
        "nrr_share_staked_pct_latest": last["nrr_share_staked_pct"],
        "nrr_share_total_pct_latest": last["nrr_share_total_supply_pct"],
        "issuer_gaps_pct": gaps,
        "max_abs_issuer_gap_pct": max(abs(v) for v in gaps.values() if v is not None) if gaps else None,
        "redemption_traces": sum(1 for t in traces if t["kind"] == "redemption"),
        "creation_traces": sum(1 for t in traces if t["kind"] == "creation"),
        "events": len(events), "epochs": len(C["epochs"]),
    }
    # total stake cross-check: locked balances vs the validators RPC, per day
    E, gp = C["epochs"], []
    for i, e in enumerate(E[:-1]):
        for r in rows:
            if e["validators_stake"] and e["start"] <= r["height"] < E[i + 1]["start"] and r["total_staked"]:
                gp.append((abs(r["total_staked"] - e["validators_stake"]) / e["validators_stake"] * 100, r["date"]))
    if gp:
        gs = sorted(g for g, _ in gp)
        mx = max(gp)
        h.update({"staked_check_days": len(gp), "staked_check_within_1pct": sum(1 for g in gs if g <= 1),
                  "staked_check_median_gap_pct": gs[len(gs) // 2], "staked_check_max_gap_pct": mx[0],
                  "staked_check_max_gap_date": mx[1]})
    return h


if __name__ == "__main__":
    rows, h = build()
    print(json.dumps({k: (round(v, 2) if isinstance(v, float) else v) for k, v in h.items()}, indent=1))
