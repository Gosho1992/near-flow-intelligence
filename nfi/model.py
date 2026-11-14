"""Mechanical 36-month supply scenarios: what NEAR's issuance path and a wrapper's share of supply look like
under fixed absorption ratios. These are arithmetic consequences of stated inputs, not forecasts.

Inputs are all measured in this repository except two governance facts from HSP-029 (2.5% -> 1.6% cap, a linear
ramp of 3.75 bp a month over 24 months after a ~90-day grace period). The ramp's start is unknown, so it is a
parameter: `ramp_start` months after the baseline. The pipeline reads the live cap daily (nfi/protocol.py), so
when month 0 happens it is observed, and this parameter is replaced by the observed date.
"""
DAYS_PER_MONTH = 365 / 12
CAP_NOW, CAP_TARGET, RAMP_MONTHS = 2.5, 1.6, 24
ABSORPTION = {"bull": 1.0, "base": 0.0, "bear": -1.0}


def cap_pct(month, ramp_start):
    """HSP-029 cap (% a year) in a given month after baseline; flat at 2.5% if ramp_start is None."""
    if ramp_start is None or month < ramp_start:
        return CAP_NOW
    k = min(month - ramp_start, RAMP_MONTHS)
    return CAP_NOW - (CAP_NOW - CAP_TARGET) * k / RAMP_MONTHS


def project(supply0, holdings0, mint_efficiency, burn_share, reward_rate_pct, basket_near,
            ramp_start=3, months=36):
    """One row per month. Mint = supply x cap x efficiency (measured median, ~99.85%); burn is the measured share
    of mint; wrapper staking rewards scale with the cap (fewer new tokens, lower yield). Wrapper flow each
    month = absorption ratio x that month's mint. Holdings are floored at zero."""
    rows, sup, sup_flat = [], supply0, supply0
    h = {k: holdings0 for k in ABSORPTION}
    cum_ramp = cum_flat = 0.0
    for m in range(months + 1):
        cap, capf = cap_pct(m, ramp_start), CAP_NOW
        mint = sup * cap / 100 * mint_efficiency * DAYS_PER_MONTH / 365
        mint_f = sup_flat * capf / 100 * mint_efficiency * DAYS_PER_MONTH / 365
        row = {"month": m, "cap_pct": cap, "cap_pct_without_hsp029": capf,
               "mint_per_day": mint / DAYS_PER_MONTH, "mint_baskets_per_day": mint / DAYS_PER_MONTH / basket_near,
               "mint_per_day_without_hsp029": mint_f / DAYS_PER_MONTH,
               "breakeven_wrapper_flow_per_day": mint / DAYS_PER_MONTH,
               "supply": sup, "supply_without_hsp029": sup_flat,
               "cumulative_mint": cum_ramp, "cumulative_mint_without_hsp029": cum_flat}
        for k, a in ABSORPTION.items():
            row[f"wrapper_{k}"] = h[k]
            row[f"wrapper_share_{k}_pct"] = 100 * h[k] / sup
        rows.append(row)
        rr = reward_rate_pct / 100 * cap / CAP_NOW * DAYS_PER_MONTH / 365
        for k, a in ABSORPTION.items():
            h[k] = max(0.0, h[k] * (1 + rr) + a * mint)
        sup += mint * (1 - burn_share)
        sup_flat += mint_f * (1 - burn_share)
        cum_ramp += mint
        cum_flat += mint_f
    return rows
