"""Turn the cached chain data in data/work/ into the published outputs in data/out/.

Runs offline. Every number shown in the docs and on the site is written here, to
data/out/headline.json, and nowhere else.

Data states: a value that could not be observed is None (blank in CSV), never zero. A day with a
missing core value is published with data_status "incomplete: <fields>" and no derived changes.
"""
import csv, json, statistics
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from .net import ROOT
from .attribution import HUB, FEE_PAYER
from . import model, signposts

W = ROOT / "data" / "work"
OUT = ROOT / "data" / "out"
POOL_EVENT_MIN = 1.0             # NEAR; ignore dust transfers
PROBE_MIN = 1000.0               # reward-probe accounts need at least this much staked
SEQ_MAX_H = 168                  # a creation/redemption sequence must complete within 7 days
SEQ_TOL = 1.0                    # NEAR; gas and dust allowed between linked amounts
TRACE_WINDOW_H = 72              # hub outflow must follow the return(s) within 72 h
TRACE_TOL = 0.02                 # ... and match the amount within 2%
EXCHANGE_STYLE_MIN_TXS = 10000   # exchange-style heuristic: at least this many transactions ...
EXCHANGE_STYLE_MIN_CP = 100      # ... and this many distinct counterparties in the 200 most recent
SECONDS_PER_YEAR = 31_536_000    # NEAR protocol constant (num_blocks_per_year is used as seconds)
MAX_INFLATION = 1 / 40           # protocol config max_inflation_rate [1, 40], protocol_reward_rate 0


def load(name, default=None):
    p = W / name
    if not p.exists() and default is not None:
        return default
    return json.loads(p.read_text())


def utc(ts_ns):
    return datetime.fromtimestamp(int(ts_ns) / 1e9, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def hours(a, b):
    return (int(b) - int(a)) / 3.6e12


def window_of(height, heights_sorted):
    """Snapshot day whose 00:00 height is the first one strictly above `height`."""
    for d, h in heights_sorted:
        if h > height:
            return d
    return None


def add(*xs):
    return None if any(x is None for x in xs) else sum(xs)


def sub(a, b):
    return None if a is None or b is None else a - b


# ---------------------------------------------------------------- events
def observe_events(attr, heights_sorted):
    """Every transaction of an attributed account that touches the pool or the hub, typed by what it did."""
    accts = {a["account"]: a for a in attr["accounts"]}
    events = []
    for acct, hist in attr["histories"].items():
        if acct not in accts:
            continue
        pool = accts[acct]["pool"]
        for t in hist:
            base = {"account": acct, "hash": t["hash"], "height": t["height"], "ts": t["ts"], "time": utc(t["ts"]),
                    "window": window_of(t["height"], heights_sorted)}
            if not t["ok"]:
                if t["signer"] == acct or t["receiver"] == acct:
                    events.append({**base, "type": "failed", "near": 0.0, "status": "failed transaction"})
                continue
            if t["receiver"] == acct and t["signer"] == HUB:
                amt = sum(a.get("near", 0) for a in t["actions"] if a["kind"] == "Transfer")
                events.append({**base, "type": "funded_by_hub", "near": amt})
            if t["signer"] != acct:
                continue
            for a in t["actions"]:
                m = a.get("method")
                if t["receiver"] == pool and m == "deposit_and_stake":
                    events.append({**base, "type": "creation_stake", "near": a["near"], "pool": pool})
                elif t["receiver"] == pool and m == "deposit":
                    events.append({**base, "type": "pool_deposit_only", "near": a["near"], "pool": pool,
                                   "status": "other activity"})
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


def validate_sequences(events, attr):
    """Give each creation and redemption a status from the sequence around it:
    creation   = hub funding (earlier, within 7 days, covering the amount) -> deposit_and_stake
    redemption = unstake (earlier) -> withdraw -> return to the hub, directly or via one account (within 7 days)
    'confirmed sequence' when every step is observed, 'partially observed' otherwise. Supporting events
    (funding, unstake, returns) are marked 'supporting'."""
    hist = attr["histories"]
    by = defaultdict(list)
    for e in events:
        by[e["account"]].append(e)
    for acct, evs in by.items():
        funds = [dict(e, left=e["near"]) for e in evs if e["type"] == "funded_by_hub"]
        for e in evs:
            if e["type"] in ("funded_by_hub", "unstake", "return_to_hub", "transfer_out"):
                e.setdefault("status", "supporting")
            if e["type"] == "creation_stake":
                src = [f for f in funds if f["height"] < e["height"] and hours(f["ts"], e["ts"]) <= SEQ_MAX_H
                       and f["left"] >= e["near"] - SEQ_TOL]
                if src:
                    src[-1]["left"] -= e["near"]
                    e["status"], e["linked_tx"] = "confirmed sequence", src[-1]["hash"]
                else:
                    e["status"] = "partially observed"
                    e["status_reason"] = "no earlier hub funding within 7 days that covers this stake"
            if e["type"] == "redemption_withdraw":
                uns = [u for u in evs if u["type"] == "unstake" and u["height"] < e["height"]]
                ret = [r for r in evs if r["type"] in ("return_to_hub", "transfer_out") and r["height"] >= e["height"]
                       and hours(e["ts"], r["ts"]) <= SEQ_MAX_H and abs(r["near"] - e["near"]) <= SEQ_TOL][:1]
                back = None
                if ret and ret[0]["type"] == "return_to_hub":
                    back = ret[0]
                elif ret:  # via one intermediate account that sends the same amount to the hub
                    mid = ret[0]["to"]
                    cand = [t for t in hist.get(mid, []) if t["signer"] == mid and t["receiver"] == HUB
                            and t["height"] >= ret[0]["height"] and hours(ret[0]["ts"], t["ts"]) <= SEQ_MAX_H]
                    cand = [t for t in cand if abs(sum(a.get("near", 0) for a in t["actions"]) - ret[0]["near"]) <= SEQ_TOL]
                    back = cand[0] if cand else None
                if uns and back:
                    e["status"], e["linked_tx"] = "confirmed sequence", back["hash"]
                else:
                    e["status"] = "partially observed"
                    e["status_reason"] = ("no earlier unstake" if not uns else
                                          "NEAR not (yet) seen returning to the custody hub within 7 days")
    return events


# ---------------------------------------------------------------- traces
def hub_candidates(hub_out, after_height, after_ts, amount):
    return [o for o in sorted(hub_out, key=lambda o: o["height"])
            if o["height"] > after_height and 0 <= hours(after_ts, o["ts"]) <= TRACE_WINDOW_H
            and abs(o["near"] - amount) <= TRACE_TOL * amount]


def trace_next_hop(attr, events, ret):
    """Find the hub outflow that most plausibly carried this return onward. Never 'confirmed': the hub pools
    fungible NEAR. 'probable' needs exactly one candidate in the window; several candidates -> 'ambiguous'."""
    single = hub_candidates(attr["hub_out"], ret["height"], ret["ts"], ret["near"])
    if len(single) == 1:
        return single[0], "probable: the only hub outflow within 72 h matching the amount (±2%)", []
    if len(single) > 1:
        return None, f"ambiguous: {len(single)} hub outflows within 72 h match the amount", []
    grp = [e for e in events if e["type"] == "return_to_hub" and abs(hours(e["ts"], ret["ts"])) <= 24]
    if len(grp) > 1:
        last = max(grp, key=lambda e: e["height"])
        c = hub_candidates(attr["hub_out"], last["height"], last["ts"], sum(e["near"] for e in grp))
        if len(c) == 1:
            others = sorted({e["account"] for e in grp} - {ret["account"]})
            return c[0], ("probable: the only hub outflow within 72 h matching this return plus "
                          f"{len(others)} other same-day return(s) (±2%)"), others
        if len(c) > 1:
            return None, f"ambiguous: {len(c)} hub outflows match the same-day returns", []
    return None, "unmatched: no hub outflow within 72 h matches the amount", []


def build_traces(attr, events, counts):
    hist = attr["histories"]
    traces = []
    by_acct = defaultdict(list)
    for e in events:
        by_acct[e["account"]].append(e)

    def step(e, typ, status, **kw):
        return {"type": typ, "account": kw.pop("account", e.get("account")), "hash": e["hash"], "height": e["height"],
                "time": e.get("time") or utc(e["ts"]), "ts": e["ts"], "near": e["near"], "status": status, **kw}

    for acct, evs in by_acct.items():
        for w in [e for e in evs if e["type"] == "redemption_withdraw"]:
            uns = [e for e in evs if e["type"] == "unstake" and e["height"] <= w["height"]][-1:]
            steps = [step(u, "unstake", "observed") for u in uns] + [step(w, "redemption_withdraw", "observed")]
            hops = [e for e in evs if e["height"] >= w["height"] and e["type"] in ("return_to_hub", "transfer_out")][:1]
            ret = None
            if hops and hops[0]["type"] == "return_to_hub":
                ret = hops[0]
                steps.append(step(ret, "return_to_hub", "observed", to=HUB))
            elif hops:
                steps.append(step(hops[0], "transfer_out", "observed", to=hops[0]["to"]))
                mid = hops[0]["to"]
                back = [t for t in hist.get(mid, []) if t["signer"] == mid and t["receiver"] == HUB
                        and t["height"] >= hops[0]["height"]]
                if back:
                    b = back[0]
                    ret = {"account": mid, "hash": b["hash"], "height": b["height"], "ts": b["ts"], "time": utc(b["ts"]),
                           "near": sum(a.get("near", 0) for a in b["actions"])}
                    steps.append(step(ret, "return_to_hub", "observed", to=HUB))
            confidence = "observed to the custody hub" if ret else "observed to withdrawal"
            if ret:
                nxt, why, others = trace_next_hop(attr, events, ret)
                kind = why.split(":")[0]
                if nxt:
                    steps.append(step(nxt, "hub_to_next", kind, account=HUB, to=nxt["to"], reason=why,
                                      combined_with=others))
                    onward = [t for t in hist.get(nxt["to"], []) if t["signer"] == nxt["to"] and t["height"] >= nxt["height"]]
                    for t in onward[:1]:
                        amt = sum(a.get("near", 0) for a in t["actions"] if a["kind"] == "Transfer")
                        same = abs(amt - nxt["near"]) <= SEQ_TOL
                        steps.append(step({"account": nxt["to"], "hash": t["hash"], "height": t["height"], "ts": t["ts"],
                                           "near": amt}, "onward", "observed", to=t["receiver"],
                                          reason="forwards the same amount" if same else "next transfer (amount differs)"))
                else:
                    later = [o for o in sorted(attr["hub_out"], key=lambda o: o["height"])
                             if o["height"] > ret["height"] and o["near"] >= 1000]
                    if later:
                        steps.append(step(later[0], "hub_next_unmatched", "context only", account=HUB,
                                          to=later[0]["to"], reason=why))
                confidence = kind + " beyond the custody hub"
            for s in steps:
                for k in ("account", "to"):
                    if s.get(k):
                        s[k + "_label"] = label(s[k], attr, counts)
            traces.append({"kind": "redemption", "account": acct, "near": w["near"], "time": w["time"],
                           "status": w.get("status"), "confidence": confidence, "steps": steps})
    for acct, evs in by_acct.items():
        for s in [e for e in evs if e["type"] == "creation_stake"]:
            f = [e for e in evs if e["hash"] == s.get("linked_tx")]
            steps = ([step(f[0], "funded_by_hub", "observed", account=HUB, to=acct)] if f else []) + \
                    [step(s, "creation_stake", "observed", to=s["pool"])]
            for st in steps:
                for k in ("account", "to"):
                    st[k + "_label"] = label(st[k], attr, counts)
            ctx = []
            if f:
                prior = [i for i in attr["hub_in"] if i["height"] <= f[0]["height"]]
                ctx = [{**c, "time": utc(c["ts"]), "from_label": label(c["from"], attr, counts)}
                       for c in sorted(prior, key=lambda i: -i["height"])[:3]]
            traces.append({"kind": "creation", "account": acct, "near": s["near"], "time": s["time"],
                           "status": s.get("status"), "confidence": s.get("status"), "steps": steps,
                           "hub_inflows_before": ctx})
    traces.sort(key=lambda t: (-t["near"], t["time"], t["account"]))
    return traces


def label(a, attr, counts):
    accts = {x["account"] for x in attr["accounts"]}
    if a == HUB:
        return "custody hub (inferred: funds every rule A account, receives every redemption)"
    if a == FEE_PAYER:
        return "fee payer (sends 0.15 NEAR for gas)"
    if a in accts:
        return "NRR basket account (rule A: hub funding, then deposit_and_stake)"
    if a.endswith(".poolv1.near"):
        return "staking pool"
    c = counts.get(a)
    if isinstance(c, int):            # older format: count only
        c = {"txs": c}
    n = (c or {}).get("txs")
    cp = (c or {}).get("counterparties")
    if n is not None and n >= EXCHANGE_STYLE_MIN_TXS and cp is not None and cp >= EXCHANGE_STYLE_MIN_CP:
        return (f"exchange-style wallet (heuristic: {n:,} transactions, {cp} distinct counterparties "
                f"in its {c.get('sample')} most recent)")
    if n is not None and n >= EXCHANGE_STYLE_MIN_TXS and cp is not None:
        return (f"high-activity account ({n:,} transactions; counterparty test not met: {cp} distinct "
                f"counterparties in its {c.get('sample')} most recent)")
    if n is not None and n >= EXCHANGE_STYLE_MIN_TXS:
        return f"high-activity account ({n:,} transactions; counterparty test not run)"
    if n is not None:
        return f"unlabelled account ({n:,} transactions)"
    return "unlabelled account"


def _near_threshold(c):
    """True if a wallet passes the exchange-style test by less than 5% on either threshold."""
    if not isinstance(c, dict) or c.get("txs") is None or c.get("counterparties") is None:
        return False
    return c["txs"] < EXCHANGE_STYLE_MIN_TXS * 1.05 or c["counterparties"] < EXCHANGE_STYLE_MIN_CP * 1.05


def source_mix(attr, counts):
    """Where the NEAR that funded NRR's custody hub came from, by sending wallet.
    External senders only: attributed basket accounts, the two downstream accounts we follow, the fee payer and
    round trips (wallets that had first received the same NEAR from the hub) are excluded. Labels are the
    exchange-style heuristic; a delivery from a wallet is not evidence of a market purchase."""
    accts = {x["account"] for x in attr["accounts"]}
    skip = accts | set(attr["sources"].get("extra_accounts", [])) | {FEE_PAYER, HUB}
    first_out = {}
    for o in attr["hub_out"]:
        if o["near"] >= 1000:                         # a 1-NEAR test payment is not a round trip
            first_out[o["to"]] = min(first_out.get(o["to"], o["height"]), o["height"])
    rows = {}
    for i in attr["hub_in"]:
        a = i["from"]
        if a in skip:
            continue
        if a in first_out and first_out[a] < i["height"]:
            continue                                  # round trip: hub -> a -> hub
        r = rows.setdefault(a, {"wallet": a, "near": 0.0, "transfers": 0, "largest_transfer": 0.0, "largest_tx": None})
        r["near"] += i["near"]
        r["transfers"] += 1
        if i["near"] > r["largest_transfer"]:
            r["largest_transfer"], r["largest_tx"] = i["near"], i["hash"]
    total = sum(r["near"] for r in rows.values())
    out = []
    for r in sorted(rows.values(), key=lambda r: -r["near"]):
        lab = label(r["wallet"], attr, counts)
        out.append({**r, "share_pct": 100 * r["near"] / total if total else None,
                    "exchange_style": lab.startswith("exchange-style"), "label": lab})
    return out


def trace_accounts(attr, top_in=10):
    """Counterparties whose transaction counts feed the exchange-style label (kept small: one API call each)."""
    accts = {x["account"] for x in attr["accounts"]}
    out = {o["to"] for o in attr["hub_out"] if o["near"] >= 1000}
    ins = sorted(attr["hub_in"], key=lambda i: -i["near"])
    out |= {i["from"] for i in ins[:top_in]}
    out |= {i["from"] for i in attr["hub_in"] if i["from"] not in accts}   # every external sender (source mix)
    for a, hist in attr["histories"].items():
        if a not in accts and a != HUB:
            out.add(a)
            out |= {t["receiver"] for t in hist if t["signer"] == a}
    return sorted(a for a in out if a not in accts and a not in (HUB, FEE_PAYER) and not a.endswith(".poolv1.near"))


# ---------------------------------------------------------------- rewards
def probe_rates(pa, ppa, active):
    """Daily staked-balance growth of delegators with no pool transaction in the window and no change
    in their unstaked balance."""
    return sorted(pa[a][0] / ppa[a][0] - 1 for a in pa if a in ppa and a not in active
                  and ppa[a][0] >= PROBE_MIN and pa[a][0] >= PROBE_MIN and pa[a][1] == ppa[a][1])


def q(xs, p):
    return xs[min(len(xs) - 1, int(p * len(xs)))] if xs else None


def trimmed_mean(xs, cut=0.1):
    k = int(len(xs) * cut)
    ys = xs[k:len(xs) - k] if len(xs) > 2 * k else xs
    return sum(ys) / len(ys) if ys else None


# ---------------------------------------------------------------- main
def build():
    H = load("heights.json")
    hs = sorted(H.items())
    days = [d for d, _ in hs]
    C = load("chain.json")
    A = load("attribution.json")
    L3 = load("custody_liquid.json")
    counts = load("tx_counts.json")
    refresh = load("refresh.json", {})
    attributed = {a["account"] for a in A["accounts"]}
    activity = A.get("pool_activity", {})

    events = validate_sequences(observe_events(A, hs), A)
    ev_by_win = defaultdict(lambda: defaultdict(float))
    for e in events:
        if e["window"]:
            ev_by_win[e["window"]][e["type"]] += e["near"]
            if e.get("status") == "confirmed sequence":
                ev_by_win[e["window"]][e["type"] + "_confirmed"] += e["near"]

    epochs = C["epochs"]
    mint_by_win = defaultdict(float)
    for ep in epochs:
        w = window_of(ep["start"] - 1, hs)   # mint lands at the epoch's first block
        if w:
            mint_by_win[w] += ep["mint"]

    with open(ROOT / "data" / "issuer_snapshots.csv") as f:
        issuer = {r["date"]: r for r in csv.DictReader(f)}

    rows, ledger, prev = [], [], None
    for d in days:
        x = C["days"][d]
        pa = x["pool_accounts"]
        missing = []
        if pa is None:
            missing.append("pool_accounts")
            l1 = l2 = others = None
        else:
            l1 = sum(v[0] for a, v in pa.items() if a in attributed)
            l2 = sum(v[1] for a, v in pa.items() if a in attributed)
            others = sum(v[0] + v[1] for a, v in pa.items() if a not in attributed)
        liq = L3.get(d)
        l3 = None if liq is None or any(v is None for v in liq.values()) else sum(liq.values())
        if l3 is None:
            missing.append("basket_liquid")
        l4 = x["hub_liquid"]
        if l4 is None:
            missing.append("hub_liquid")
        for k in ("total_supply", "buyback_fund", "locked_sum"):
            if x.get(k) is None:
                missing.append(k)
        r = {"date": d, "height": x["height"],
             "data_status": "complete" if not missing else "incomplete: " + ",".join(missing),
             "l1_staked": l1, "l2_unstaked": l2, "l3_basket_liquid": l3, "l4_hub_liquid": l4,
             "nrr_holdings": add(l1, l2), "nrr_custody_extended": add(l1, l2, l3),
             "nrr_custody_total": add(l1, l2, l3, l4), "pool_other_delegators": others,
             "attributed_accounts_in_pool": (None if pa is None else
                                             sum(1 for a, v in pa.items() if a in attributed and v[0] + v[1] > 0)),
             "total_supply": x["total_supply"], "total_staked": x.get("locked_sum"), "buyback_fund": x["buyback_fund"]}
        ev = ev_by_win.get(d, {})
        r["creations"] = ev.get("creation_stake", 0.0)
        r["creations_confirmed"] = ev.get("creation_stake_confirmed", 0.0)
        r["redemptions"] = ev.get("redemption_withdraw", 0.0)
        r["redemptions_confirmed"] = ev.get("redemption_withdraw_confirmed", 0.0)
        r["other_pool_deposits"] = ev.get("pool_deposit_only", 0.0)
        r["custody_flow"] = r["creations"] + r["other_pool_deposits"] - r["redemptions"]
        for k in ("reward_rate", "reward_rate_p25", "reward_rate_p75", "reward_probes", "nrr_rewards",
                  "nrr_rewards_trimmed", "holdings_change", "unexplained", "net_supply_change", "gross_issuance",
                  "burn_residual", "buyback_fund_change"):
            r[k] = None
        if prev:
            ph = prev["height"]
            active = {a for a, hh in activity.items() if any(ph <= h < r["height"] for h in hh)}
            active |= {e["account"] for e in events if e["window"] == d}
            ppa = C["days"][prev["date"]]["pool_accounts"]
            rates = probe_rates(pa, ppa, active) if pa is not None and ppa is not None else []
            if rates:
                rate = statistics.median(rates)
                r.update({"reward_rate": rate, "reward_rate_p25": q(rates, .25), "reward_rate_p75": q(rates, .75),
                          "reward_probes": len(rates)})
                if prev["l1_staked"] is not None:
                    r["nrr_rewards"] = rate * prev["l1_staked"]
                    r["nrr_rewards_trimmed"] = trimmed_mean(rates) * prev["l1_staked"]
            r["holdings_change"] = sub(r["nrr_holdings"], prev["nrr_holdings"])
            if r["holdings_change"] is not None and r["nrr_rewards"] is not None:
                r["unexplained"] = r["holdings_change"] - r["custody_flow"] - r["nrr_rewards"]
            r["net_supply_change"] = sub(r["total_supply"], prev["total_supply"])
            r["gross_issuance"] = mint_by_win.get(d, 0.0)
            r["burn_residual"] = sub(r["gross_issuance"], r["net_supply_change"])
            r["buyback_fund_change"] = sub(r["buyback_fund"], prev["buyback_fund"])
            for acct, parts in sorted(x["buyback_parts"].items()):   # buyback ledger: per account and token
                pparts = C["days"][prev["date"]]["buyback_parts"].get(acct, {})
                for tok in ("native", "wnear_in_intents"):
                    o, c = pparts.get(tok), parts.get(tok)
                    ledger.append({"date": d, "height": x["height"], "account": acct,
                                   "token": "NEAR (native)" if tok == "native" else "wNEAR in intents.near",
                                   "opening": o, "closing": c, "change": sub(c, o),
                                   "status": "observed" if o is not None and c is not None else "missing"})
        r["nrr_share_total_supply_pct"] = (100 * r["nrr_holdings"] / r["total_supply"]
                                           if r["nrr_holdings"] is not None and r["total_supply"] else None)
        r["nrr_share_staked_pct"] = (100 * r["l1_staked"] / r["total_staked"]
                                     if r["l1_staked"] is not None and r["total_staked"] else None)
        # Bitwise's "NEAR in Trust as of T" is the end of day T (our row T+1 at 00:00 UTC) and already excludes
        # NEAR unstaked for redemptions, so it is compared with L1 (staked) of row T+1.
        prev_day = (datetime.fromisoformat(d) - timedelta(days=1)).date().isoformat()
        iss = issuer.get(prev_day)
        r["issuer_date"] = prev_day if iss else None
        r["issuer_near_in_trust"] = float(iss["near_in_trust"]) if iss else None
        r["issuer_gap_pct"] = (100 * (r["l1_staked"] - r["issuer_near_in_trust"]) / r["issuer_near_in_trust"]
                               if iss and r["l1_staked"] is not None else None)
        rows.append(r)
        prev = r

    traces = build_traces(A, events, counts)
    inst = load("institutional.json", {})
    issuance = issuance_check(epochs)
    head = rnd(headline(rows, events, issuer, A, traces, C, issuance, refresh))
    proto = load("protocol.json", {})
    lt, scen = long_term(rows, events, head, C, issuance, proto)
    head.update(rnd(lt))
    sec = load("sec_reconciliation.json", None)
    if sec:
        head.update(rnd({"sec_valuation_height": sec["valuation_height"], "sec_in_kind_filing": sec["filing"]["in_kind"], "sec_in_kind_onchain": sec["in_kind_onchain"],
                         "sec_in_kind_diff": sec["in_kind_diff"], "sec_staked_implied": sec["staked_implied"],
                         "sec_staked_two_accounts": sec["staked_seed_plus_one_hop"],
                         "sec_staked_diff": sec["staked_diff"], "sec_staked_diff_pct": sec["staked_diff_pct"],
                         "sec_staked_rule_a_only_diff_pct": sec["staked_rule_a_only_diff_pct"],
                         "sec_staked_whole_pool_diff_pct": sec["staked_whole_pool_diff_pct"],
                         "sec_purchased_undelivered": sec["purchased_undelivered"],
                         "sec_undelivered_value_at_nav": sec["undelivered_value_at_nav"],
                         "sec_receivable_creations": sec["filing"]["receivable_creations"],
                         "sec_receivable_diff_usd": sec["receivable_diff_usd"],
                         "sec_total_filing": sec["filing"]["total"], "sec_fund_inflows_onchain": sec["fund_inflows_onchain"],
                         "sec_rewards_accrued_two_accounts": sec["staked_seed_plus_one_hop"] - 104384.163097}))
    sp = signposts.evaluate(rows)
    head.update(rnd({"signposts_state": sp["state"], "signposts_windows_complete": sp["complete"],
                     "signposts_first_window_end": sp["windows"][0]["end"]}))
    holders = institutional_rows(rows, inst, attributed, head)
    head.update(rnd(institutional_headline(inst)))
    mix = source_mix(A, counts)
    tot = sum(m["near"] for m in mix)
    ex = sum(m["near"] for m in mix if m["exchange_style"])
    big = max(mix, key=lambda m: m["largest_transfer"]) if mix else None
    dest = {o["to"] for o in A["hub_out"] if o["to"] not in attributed}
    onward = set()
    for t in traces:
        for st in t["steps"]:
            if st["type"] == "onward" and st.get("to"):
                onward.add(st["to"])
    back = sum(m["near"] for m in mix if m["wallet"] in onward)
    head.update(rnd({"sources_external_total": tot, "sources_wallets": len(mix),
                     "sources_exchange_style_pct": 100 * ex / tot if tot else None,
                     "sources_other_pct": 100 * (tot - ex) / tot if tot else None,
                     "sources_other_wallets": sum(1 for m in mix if not m["exchange_style"]),
                     "sources_largest_transfer": big["largest_transfer"] if big else None,
                     "sources_onward_wallets_also_delivered": back,
                     "sources_onward_wallets": len(onward)}))
    # sensitivity of the exchange-style share to the heuristic's thresholds: wallets within 5% of a threshold
    edge = [m for m in mix if m["exchange_style"] and _near_threshold(counts.get(m["wallet"]))]
    head.update(rnd({"sources_exchange_style_low_pct": 100 * (ex - sum(m["near"] for m in edge)) / tot if tot else None,
                     "sources_edge_wallets": len(edge), "sources_edge_near": sum(m["near"] for m in edge)}))
    rows, events, traces, ledger, issuance = rnd(rows), rnd(events), rnd(traces), rnd(ledger), rnd(issuance)
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "daily.csv", rows)
    write_csv(OUT / "events.csv", [{k: e.get(k) for k in
                                    ("time", "window", "type", "status", "status_reason", "account", "near", "pool",
                                     "to", "linked_tx", "hash", "height")} for e in events])
    write_csv(OUT / "accounts.csv", A["accounts"])
    write_csv(OUT / "buyback_ledger.csv", ledger)
    write_csv(OUT / "issuance_check.csv", issuance)
    write_csv(OUT / "institutional_holders.csv", rnd(holders))
    write_csv(OUT / "source_mix.csv", rnd(mix))
    write_csv(OUT / "scenarios.csv", rnd(scen))
    (OUT / "signposts.json").write_text(json.dumps(rnd(sp), indent=1, sort_keys=True))
    (OUT / "traces.json").write_text(json.dumps(traces, indent=1, sort_keys=True))
    (OUT / "headline.json").write_text(json.dumps(head, indent=1, sort_keys=True))
    (OUT / "site_data.json").write_text(json.dumps({"daily": rows, "events": events, "traces": traces,
                                                    "headline": head, "issuer": list(issuer.values()),
                                                    "scenarios": rnd(scen), "signposts": rnd(sp),
                                                    "accounts": A["accounts"], "institutional": rnd(holders)},
                                                   sort_keys=True))
    return rows, head


# ---------------------------------------------------------------- long-term figures (THESIS.md, LONG_TERM_PLAN.md)
ONE_HOP = "9a00031933695207a60a3af95cfaaadcea863812ecbc30400c109417dadf21b3"   # funded by a rule A account
HSP029_MONTHS = (0, 6, 12, 18, 24)


def long_term(rows, events, h, C, issuance, proto):
    """Absorption ratios, the HSP-029 path, staking context, basket-multiple check, one-hop sensitivity and the
    36-month scenario table. Absorption ratio = NRR net custody flow / NEAR minted, same window."""
    base = next(r for r in rows if r["date"] == h["window_start"])
    win = [r for r in rows if r["date"] > base["date"]]
    post = [r for r in rows if r["date"] > h["nrr_peak_date"]]
    last30 = rows[-30:]
    net = lambda rr: sum((r["creations"] or 0) - (r["redemptions"] or 0) for r in rr)
    mint = lambda rr: sum(r["gross_issuance"] or 0 for r in rr)
    bb = lambda rr: sum(r["buyback_fund_change"] or 0 for r in rr)
    o = {}
    for k, rr in (("launch", win), ("since_peak", post), ("last30", last30)):
        o[f"absorption_{k}"] = net(rr) / mint(rr) if mint(rr) else None
        o[f"buyback_ratio_{k}"] = bb(rr) / mint(rr) if mint(rr) else None
        o[f"mint_{k}"] = mint(rr)
    # rolling 30-row absorption at every row with 30 rows behind it (for the dashboard and the signpost history)
    roll = []
    for i in range(29, len(rows)):
        rr = rows[i - 29:i + 1]
        if rr[0]["date"] > base["date"] and mint(rr):
            roll.append((rows[i]["date"], net(rr) / mint(rr)))
    o["absorption_rolling_max"] = max(v for _, v in roll) if roll else None
    o["absorption_rolling_max_date"] = max(roll, key=lambda x: x[1])[0] if roll else None
    # staking outside the wrapper: the larger mover (bounds the claim; "float" is not what we measure)
    d_other, d_nrr = [], []
    prev = base
    for r in win:
        if None not in (r["total_staked"], r["l1_staked"], prev["total_staked"], prev["l1_staked"]):
            d_other.append((r["total_staked"] - r["l1_staked"]) - (prev["total_staked"] - prev["l1_staked"]))
            d_nrr.append(r["l1_staked"] - prev["l1_staked"])
        prev = r
    o.update({"other_stake_abs_daily_mean": statistics.mean(abs(x) for x in d_other),
              "other_stake_abs_daily_median": statistics.median(abs(x) for x in d_other),
              "nrr_stake_abs_daily_mean": statistics.mean(abs(x) for x in d_nrr),
              "other_stake_bigger_days": sum(abs(a) > abs(b) for a, b in zip(d_other, d_nrr)),
              "other_stake_days": len(d_other),
              "other_stake_net_change": sum(d_other), "other_stake_last30_change": sum(d_other[-30:]),
              "nrr_stake_last30_change": sum(d_nrr[-30:]),
              "total_staked_latest": rows[-1]["total_staked"],
              "staked_pct_of_supply": 100 * rows[-1]["total_staked"] / rows[-1]["total_supply"]})
    # basket multiples: events that are not whole 10,000-share baskets are operational, not investor creations
    b = h["basket_near"]
    def odd(x):
        k = round(x / b)
        return k == 0 or abs(x / b - k) > 0.02 * k
    for typ, key in (("creation_stake", "creations"), ("redemption_withdraw", "redemptions")):
        xs = [e["near"] for e in events if e["type"] == typ and e.get("near") is not None]
        bad = [x for x in xs if odd(x)]
        o[f"{key}_non_basket_count"] = len(bad)
        o[f"{key}_non_basket_near"] = sum(bad)
    # one-hop sensitivity: the account is outside rule A; we show what adding it would do, never add it
    oh = {d: (x["pool_accounts"].get(ONE_HOP) or [None])[0] for d, x in C["days"].items()}
    gaps = []
    for r in rows:
        if r["issuer_date"] and oh.get(r["date"]) is not None:
            gaps.append(100 * (r["l1_staked"] + oh[r["date"]] - r["issuer_near_in_trust"]) / r["issuer_near_in_trust"])
    o.update({"one_hop_staked_latest": oh.get(rows[-1]["date"]), "one_hop_first_staked": oh.get("2026-09-29"),
              "one_hop_gap_min_pct": min(gaps) if gaps else None, "one_hop_gap_max_pct": max(gaps) if gaps else None})
    # protocol inflation setting, read daily: has HSP-029's ramp started?
    seen = {d: v for d, v in proto.items() if v}
    caps = sorted({v["max_inflation_pct"] for v in seen.values()})
    started = sorted(d for d, v in seen.items() if v["max_inflation_pct"] < model.CAP_NOW)
    o.update({"protocol_cap_pct_latest": seen[max(seen)]["max_inflation_pct"] if seen else None,
              "protocol_version_latest": seen[max(seen)]["protocol_version"] if seen else None,
              "protocol_versions_seen": len({v["protocol_version"] for v in seen.values()}),
              "protocol_days_read": len(seen), "hsp029_ramp_started": bool(started),
              "hsp029_ramp_first_day": started[0] if started else None, "protocol_caps_seen": len(caps)})
    # HSP-029 path at the proposal's own checkpoints, on today's supply
    ipd = h["issuance_per_day"]
    for m in HSP029_MONTHS:
        cap = model.cap_pct(m, 0)
        o[f"hsp029_m{m}_cap_pct"] = cap
        o[f"hsp029_m{m}_per_day"] = ipd * cap / model.CAP_NOW
        o[f"hsp029_m{m}_baskets_per_day"] = ipd * cap / model.CAP_NOW / b
    # 36-month mechanical scenarios; earliest ramp start = 3 months after baseline (the ~90-day grace period)
    ratios = sorted(i["ratio"] for i in issuance)
    eff = statistics.median(ratios)
    burn = h["burn_residual_total"] / h["gross_issuance_total"] if h["gross_issuance_total"] else 0.0
    scen = model.project(rows[-1]["total_supply"], rows[-1]["l1_staked"], eff, burn,
                         h["reward_rate_annualised_pct"], b, ramp_start=3)
    late = model.project(rows[-1]["total_supply"], rows[-1]["l1_staked"], eff, burn,
                         h["reward_rate_annualised_pct"], b, ramp_start=9)
    for row in scen:
        row["cap_pct_if_ramp_starts_month_9"] = late[row["month"]]["cap_pct"]
    # compounding over 36 months differs in the last float digits across platforms: publish at stable precision
    scen = [{k: (round(v, 4) if ("pct" in k or "baskets" in k) else round(v, 1)) if isinstance(v, float) else v
             for k, v in row.items()} for row in scen]
    for m in (12, 24, 36):
        s = scen[m]
        for k in model.ABSORPTION:
            o[f"scen_m{m}_{k}_share_pct"] = s[f"wrapper_share_{k}_pct"]
            o[f"scen_m{m}_{k}_near"] = s[f"wrapper_{k}"]
        o[f"scen_m{m}_cap_pct"] = s["cap_pct"]
        o[f"scen_m{m}_mint_per_day"] = s["mint_per_day"]
    o["scen_avoided_issuance_m27"] = scen[27]["cumulative_mint_without_hsp029"] - scen[27]["cumulative_mint"]
    o["scen_avoided_issuance_m36"] = scen[36]["cumulative_mint_without_hsp029"] - scen[36]["cumulative_mint"]
    o["scen_cum_mint_m36"] = scen[36]["cumulative_mint"]
    o["scen_bear_empty_month"] = next((r["month"] for r in scen if r["wrapper_bear"] == 0), None)
    o["scen_ramp_start_month"] = 3
    o["scen_mint_efficiency_pct"] = 100 * eff
    o["scen_burn_share_pct"] = 100 * burn
    return o, scen


def institutional_rows(rows, inst, attributed, head):
    """Evidence-status table: NRR (rebuilt and reconciled) and SVRN (partial observation, context only).
    The two rows have different measurement bases and dates and are never added together."""
    last = rows[-1]
    out = [{"holder": "Bitwise NEAR ETF (NRR)", "holder_type": "regulated fund (ETF)",
            "evidence_status": "rebuilt from the chain and reconciled with the issuer",
            "reported_holdings_near": None, "reported_as_of": None, "reported_source": "https://nrretf.com/",
            "observed_where": "bitwise_2.poolv1.near, 73 attributed accounts (rule A)",
            "observed_staked_near": last["l1_staked"], "observed_date": last["date"], "observed_height": last["height"],
            "accounts_observed": head["attributed_accounts"], "largest_account": None, "largest_account_staked_near": None,
            "issuer_reconciled": f"yes, {head['issuer_gaps_count']} dates, max gap {head['max_abs_issuer_gap_pct']:.2f}%",
            "counted_in_nrr_totals": "yes"}]
    acc = inst.get("accounts")
    if inst:
        top = max(acc.items(), key=lambda kv: kv[1]["staked"]) if acc else (None, {"staked": None})
        overlap = sorted(set(acc or {}) & attributed)
        out.append({"holder": inst["holder"], "holder_type": inst["holder_type"],
                    "evidence_status": "partial on-chain observation; company-reported total is context only",
                    "reported_holdings_near": inst["reported_holdings_near"], "reported_as_of": inst["reported_as_of"],
                    "reported_source": inst["reported_source"],
                    "observed_where": f"{inst['observed_pool']} (all delegators)",
                    "observed_staked_near": None if acc is None else sum(v["staked"] for v in acc.values()),
                    "observed_date": inst["date"], "observed_height": inst["height"],
                    "accounts_observed": None if acc is None else len(acc),
                    "largest_account": top[0], "largest_account_staked_near": top[1]["staked"],
                    "issuer_reconciled": "no (one pool only; may be part of the reported total, never added to it)",
                    "counted_in_nrr_totals": "no" if not overlap else "ERROR: overlaps NRR accounts"})
    return out


def institutional_headline(inst):
    acc = inst.get("accounts") if inst else None
    if not acc:
        return {}
    tot = sum(v["staked"] for v in acc.values())
    top = max(acc.items(), key=lambda kv: kv[1]["staked"])
    return {"svrn_observed_staked": tot, "svrn_observed_date": inst["date"], "svrn_observed_height": inst["height"],
            "svrn_accounts_observed": len(acc), "svrn_largest_account": top[0],
            "svrn_largest_account_share_pct": 100 * top[1]["staked"] / tot if tot else None,
            "svrn_largest_account_staked": top[1]["staked"],
            "svrn_reported_holdings": inst["reported_holdings_near"], "svrn_reported_as_of": inst["reported_as_of"]}


def issuance_check(epochs):
    """Independent check of minting: NEAR mints at most total_supply x 2.5%/yr x epoch duration per epoch
    (validators that miss blocks are paid less, so the minted amount is a little below the maximum)."""
    from .chain import header
    out = []
    for a, b in zip(epochs, epochs[1:]):
        dur = (int(header(b["start"])["timestamp"]) - int(header(a["start"])["timestamp"])) / 1e9
        mx = a["supply_at_start"] * MAX_INFLATION * dur / SECONDS_PER_YEAR
        out.append({"epoch_start": a["start"], "next_epoch_start": b["start"], "duration_s": dur,
                    "protocol_max_mint": mx, "measured_mint": b["mint"], "ratio": b["mint"] / mx})
    return out


def rnd(x):
    """Round floats to 6 decimals so outputs are identical across Python versions and platforms."""
    if isinstance(x, float):
        return round(x, 6) + 0.0   # + 0.0 also turns -0.0 into 0.0
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
            w.writerow({k: ("" if r.get(k) is None else r[k]) for k in keys})



def flow_summary(rows, basket_near=None):
    """Signed NRR custody flow per complete daily window, with optional basket equivalents.

    A basket is 10,000 shares converted at the latest issuer-published NEAR per share.
    This is a scale conversion, not a claim that each observed flow was a market purchase.
    """
    valid = [r for r in rows
             if r.get("data_status", "complete") == "complete"
             and r.get("creations") is not None and r.get("redemptions") is not None]
    if not valid:
        return {"net_total": None, "days": 0, "net_per_day": None, "baskets_per_day": None}
    net = sum(float(r["creations"]) - float(r["redemptions"]) for r in valid)
    per_day = net / len(valid)
    return {"net_total": net, "days": len(valid), "net_per_day": per_day,
            "baskets_per_day": per_day / basket_near if basket_near else None}

def headline(rows, events, issuer, A, traces, C, issuance, refresh):
    start = next(r for r in rows if (r["nrr_holdings"] or 0) > 1000)        # first day with NRR stake
    base = rows[rows.index(start) - 1]
    last = rows[-1]
    peak = max((r for r in rows if r["nrr_holdings"] is not None), key=lambda r: r["nrr_holdings"])
    win = [r for r in rows if r["date"] > base["date"]]
    s = lambda k, rr=win: sum(r[k] or 0 for r in rr)
    last30 = rows[-30:]
    abs_custody = sum(abs(r["creations"]) + abs(r["redemptions"]) for r in win)
    abs_buyback = sum(abs(r["buyback_fund_change"]) for r in win if r["buyback_fund_change"] is not None)
    gaps = {d: None for d in issuer}            # None = the end-of-day chain row is not collected yet
    gaps.update({r["issuer_date"]: r["issuer_gap_pct"] for r in rows if r["issuer_date"]})
    rr = [r["reward_rate"] for r in win if r["reward_rate"] is not None]
    probes = [r["reward_probes"] for r in win if r["reward_probes"]]
    ratios = sorted(i["ratio"] for i in issuance)
    st = lambda typ, status=None: [e for e in events if e["type"] == typ and (status is None or e.get("status") == status)]
    conf = {}
    for t in traces:
        if t["kind"] == "redemption":
            conf[t["confidence"]] = conf.get(t["confidence"], 0) + 1
    h = {
        "data_through": last["date"], "window_start": base["date"], "days": len(win),
        "last_refresh_utc": refresh.get("refreshed_at_utc"),
        "incomplete_days": sum(1 for r in rows if r["data_status"] != "complete"),
        "attributed_accounts": len(A["accounts"]),
        "attributed_high_confidence": sum(1 for a in A["accounts"] if a["confidence"] == "high"),
        "nrr_holdings_latest": last["nrr_holdings"], "nrr_peak": peak["nrr_holdings"], "nrr_peak_date": peak["date"],
        "change_since_peak": sub(last["nrr_holdings"], peak["nrr_holdings"]),
        "change_since_peak_pct": (None if last["nrr_holdings"] is None
                                  else 100 * (last["nrr_holdings"] / peak["nrr_holdings"] - 1)),
        "holdings_net_change": sub(last["nrr_holdings"], base["nrr_holdings"]),
        "creations_total": s("creations"), "redemptions_total": s("redemptions"),
        "creations_confirmed_total": s("creations_confirmed"), "redemptions_confirmed_total": s("redemptions_confirmed"),
        "creations_count": len(st("creation_stake")),
        "creations_confirmed_count": len(st("creation_stake", "confirmed sequence")),
        "redemptions_count": len(st("redemption_withdraw")),
        "redemptions_confirmed_count": len(st("redemption_withdraw", "confirmed sequence")),
        "other_pool_deposits_total": s("other_pool_deposits"),
        "failed_transactions": len(st("failed")),
        "custody_flow_net": s("custody_flow"), "rewards_total": s("nrr_rewards"),
        "rewards_total_trimmed_mean": s("nrr_rewards_trimmed"), "unexplained_total": s("unexplained"),
        "unexplained_abs_total": sum(abs(r["unexplained"]) for r in win if r["unexplained"] is not None),
        "reward_probes_min": min(probes) if probes else None,
        "reward_probe_max_spread": max((r["reward_rate_p75"] - r["reward_rate_p25"]) for r in win
                                       if r["reward_rate_p25"] is not None),
        "reward_probes_median": statistics.median(probes) if probes else None,
        "gross_issuance_total": s("gross_issuance"), "burn_residual_total": s("burn_residual"),
        "net_supply_change_total": s("net_supply_change"),
        "issuance_epochs_checked": len(ratios),
        "issuance_ratio_median_pct": 100 * statistics.median(ratios) if ratios else None,
        "issuance_ratio_min_pct": 100 * ratios[0] if ratios else None,
        "issuance_ratio_max_pct": 100 * ratios[-1] if ratios else None,
        "buyback_fund_change_total": s("buyback_fund_change"),
        "buyback_fund_latest": last["buyback_fund"],
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
        "issuer_latest_date": max(issuer) if issuer else None,
        "issuer_gaps_count": sum(1 for v in gaps.values() if v is not None),
        # issuer figures published after the rule was frozen (13 Nov 2026) are out-of-sample tests
        "issuer_gap_oos_pct": next((gaps[d] for d in sorted(gaps) if d >= "2026-11-12" and gaps[d] is not None), None),
        "issuer_oos_count": sum(1 for d, v in gaps.items() if d >= "2026-11-12" and v is not None),
        "redemption_traces": sum(1 for t in traces if t["kind"] == "redemption"),
        "redemption_trace_confidence": conf,
        "redemption_traces_probable": sum(v for k, v in conf.items() if k.startswith("probable")),
        "creation_traces": sum(1 for t in traces if t["kind"] == "creation"),
        "events": len(events), "epochs": len(C["epochs"]),
    }
    # figures for the long-term case (THESIS.md); scale comparisons only
    iss = s("gross_issuance")
    annual = iss / len(win) * 365 if win else None
    l30_net = s("creations", last30) - s("redemptions", last30)
    h.update({
        "annual_issuance_estimate": annual,
        "nrr_holdings_pct_of_annual_issuance": 100 * last["l1_staked"] / annual if annual and last["l1_staked"] else None,
        "buyback_change_pct_of_issuance": 100 * s("buyback_fund_change") / iss if iss else None,
        "nrr_net_to_net_supply_x": (h["holdings_net_change"] / s("net_supply_change")
                                    if h["holdings_net_change"] is not None and s("net_supply_change") else None),
        "last30_nrr_net": l30_net,
        "last30_nrr_net_pct_of_issuance": 100 * l30_net / s("gross_issuance", last30) if s("gross_issuance", last30) else None,
        "last30_buyback_pct_of_issuance": (100 * s("buyback_fund_change", last30) / s("gross_issuance", last30)
                                           if s("gross_issuance", last30) else None),
        "last30_abs_custody_to_abs_buyback": ((s("creations", last30) + s("redemptions", last30)) /
                                              sum(abs(r["buyback_fund_change"]) for r in last30 if r["buyback_fund_change"] is not None)
                                              if any(r["buyback_fund_change"] for r in last30) else None),
        "products_attributed_onchain": 1,
    })
    # Convert flows to one comparable unit: the latest issuer-published 10,000-share basket.
    latest_issuer = issuer[max(issuer)] if issuer else {}
    try:
        basket_near = float(latest_issuer.get("near_per_share") or 0) * 10000
    except (TypeError, ValueError):
        basket_near = 0.0
    try:
        basket_usd = float(latest_issuer.get("nav_usd") or 0) * 10000
    except (TypeError, ValueError):
        basket_usd = 0.0
    try:
        near_price_usd = (float(latest_issuer.get("nav_usd") or 0) /
                          float(latest_issuer.get("near_per_share") or 0))
    except (TypeError, ValueError, ZeroDivisionError):
        near_price_usd = None

    launch_flow = flow_summary(win, basket_near)
    recent_flow = flow_summary(last30, basket_near)
    post_peak_rows = [r for r in rows if r["date"] > peak["date"]]
    post_peak_flow = flow_summary(post_peak_rows, basket_near)
    issuance_per_day = iss / len(win) if win else None
    buyback_per_day = s("buyback_fund_change") / len(win) if win else None
    last30_buyback_per_day = (s("buyback_fund_change", last30) / len(last30)
                              if last30 else None)
    h.update({
        "basket_near": basket_near or None,
        "basket_usd": basket_usd or None,
        "near_price_usd": near_price_usd,
        "issuer_market_value_usd": float(latest_issuer.get("market_value_usd") or 0) or None,
        "issuer_value_date": latest_issuer.get("date"),
        "launch_net_flow_total": launch_flow["net_total"],
        "launch_net_flow_days": launch_flow["days"],
        "launch_net_flow_per_day": launch_flow["net_per_day"],
        "launch_net_baskets_per_day": launch_flow["baskets_per_day"],
        "since_peak_net_flow_total": post_peak_flow["net_total"],
        "since_peak_net_flow_days": post_peak_flow["days"],
        "since_peak_creations_total": sum(float(r["creations"]) for r in post_peak_rows if r["creations"] is not None),
        "since_peak_redemptions_total": sum(float(r["redemptions"]) for r in post_peak_rows if r["redemptions"] is not None),
        "since_peak_net_flow_per_day": post_peak_flow["net_per_day"],
        "since_peak_net_baskets_per_day": post_peak_flow["baskets_per_day"],
        "last30_net_flow_days": recent_flow["days"],
        "last30_net_flow_per_day": recent_flow["net_per_day"],
        "last30_net_baskets_per_day": recent_flow["baskets_per_day"],
        "issuance_per_day": issuance_per_day,
        "issuance_baskets_per_day": issuance_per_day / basket_near if issuance_per_day is not None and basket_near else None,
        "issuance_hsp029_target_per_day": issuance_per_day * 1.6 / 2.5 if issuance_per_day is not None else None,
        "issuance_hsp029_baskets_per_day": (issuance_per_day * 1.6 / 2.5 / basket_near
                                            if issuance_per_day is not None and basket_near else None),
        "buyback_net_change_per_day": buyback_per_day,
        "buyback_baskets_per_day": buyback_per_day / basket_near if buyback_per_day is not None and basket_near else None,
        "last30_buyback_change_per_day": last30_buyback_per_day,
    })
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
