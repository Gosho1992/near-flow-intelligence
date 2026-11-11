"""Daily chain series read from NEAR's archival RPC at 00:00 UTC block heights."""
import datetime as dt
from .net import rpc, view, view_account, account_state, block, near

START = dt.date(2026, 9, 25)
POOL = "bitwise_2.poolv1.near"
EPOCH_LEN = 43200
EPOCH_ANCHOR = 222061937          # verified epoch start height (validators RPC epoch_start_height)
BUYBACK_ACCOUNTS = ["buybacks.multisignature.near", "1csfundsadmin.sputnik-dao.near"]
WNEAR = "nep141:wrap.near"


def header(h):
    k = 0
    while True:
        b = block(h + k)
        if b:
            return b
        k += 1


def ts(h):
    return int(header(h)["timestamp"]) / 1e9


def daily_heights(end=None, head_height=None):
    """First block at or after 00:00 UTC of each day, found by interpolation + local search."""
    end = end or dt.datetime.now(dt.timezone.utc).date()
    a, b = 217118985, head_height or 223988378
    ta, tb = ts(a), ts(b)
    rate = (b - a) / (tb - ta)
    out = {}
    d = START
    while d <= end:
        target = dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp()
        if target > tb:
            break
        h = int(a + (target - ta) * rate)
        for _ in range(4):                       # refine
            h = int(h - (ts(h) - target) * rate)
        while ts(h) >= target:                   # step back to before midnight
            h -= 20
        while True:                              # walk forward to the first block at/after midnight
            hd = header(h)
            if int(hd["timestamp"]) / 1e9 >= target:
                break
            h = hd["height"] + 1
        out[d.isoformat()] = header(h)["height"]
        d += dt.timedelta(days=1)
    return out


def pool_accounts(pool, h):
    """{account: (staked, unstaked, can_withdraw)} or None if any page could not be read (missing, never empty)."""
    n = view(pool, "get_number_of_accounts", {}, h)
    if n is None:
        return None
    rows = []
    for i in range(0, n, 100):
        page = view(pool, "get_accounts", {"from_index": i, "limit": 100}, h)
        if page is None:
            return None
        rows += page
    if len(rows) != n:
        return None
    return {r["account_id"]: (near(r["staked_balance"]), near(r["unstaked_balance"]),
                              bool(r.get("can_withdraw", False))) for r in rows}


def _eid(h):
    return header(h)["epoch_id"]


def _boundary(lo, hi):
    """First height of the later epoch, given epoch(lo) != epoch(hi)."""
    e_hi = _eid(hi)
    while hi - lo > 1:
        m = (lo + hi) // 2
        hm = header(m)
        if hm["height"] >= hi:
            lo = m
            continue
        if hm["epoch_id"] == e_hi:
            hi = hm["height"]
        else:
            lo = hm["height"]
    return hi


def find_start_near(guess, span=3000):
    lo, hi = guess - span, guess + span
    while _eid(lo) == _eid(hi):
        span *= 2
        lo, hi = guess - span, guess + span
    return _boundary(lo, hi)


def epoch_starts(lo_h, hi_h):
    """Exact epoch start heights covering [lo_h, hi_h], searched from a verified anchor."""
    starts = [EPOCH_ANCHOR]
    while starts[0] > lo_h:
        starts.insert(0, find_start_near(starts[0] - EPOCH_LEN))
    while starts[-1] < hi_h:
        starts.append(find_start_near(starts[-1] + EPOCH_LEN))
    return starts


def supply_at(h):
    return near(header(h)["total_supply"])


def epoch_mint(start):
    """Supply jump across an epoch boundary = NEAR minted for the epoch (net of that one block's burn)."""
    before = int(header(start - 1)["total_supply"]) if block(start - 1) else None
    if before is None:  # missing block before the start: use the last existing block
        k = 2
        while not block(start - k):
            k += 1
        before = int(block(start - k)["total_supply"])
    first = int(header(start)["total_supply"])
    return near(first - before)


def validators_stake(next_epoch_start):
    """Sum of current validator stakes for the epoch ending at next_epoch_start-1 (archive keeps ~2 weeks)."""
    r = rpc("validators", {"block_id": next_epoch_start - 1}).get("result")
    if not r:
        return None, []
    vs = r.get("current_validators", [])
    return sum(int(v["stake"]) for v in vs) / 1e24, sorted(v["account_id"] for v in vs)


def locked_sum(accounts, h):
    """Total stake as the sum of `locked` balances of validator accounts at height h; None if any lookup failed."""
    tot = 0
    for a in accounts:
        st = account_state(a, h)
        if st is None:
            return None
        tot += int(st["locked"])
    return tot / 1e24


def buyback_fund(h):
    total, parts = 0.0, {}
    for a in BUYBACK_ACCOUNTS:
        native = view_account(a, h)
        w = view("intents.near", "mt_balance_of", {"account_id": a, "token_id": WNEAR}, h)
        native_n = near(native) if native is not None else None
        w_n = near(w) if w is not None else None          # a failed wNEAR lookup is missing, not zero
        parts[a] = {"native": native_n, "wnear_in_intents": w_n}
        if native_n is None or w_n is None:
            total = None
        if total is not None:
            total += native_n + w_n
    return total, parts
