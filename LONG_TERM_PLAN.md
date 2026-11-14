# Long-term plan: how this thesis will be tested from November 2026 to 2029

**Horizon:** 1 to 3 years from the baseline (data through <!--n:data_through:-->2026-11-14<!--/n-->). **Status today:** <!--n:signposts_state:-->NOT YET TESTABLE<!--/n-->; the first signpost window closes at row <!--n:signposts_first_window_end:-->2026-12-15<!--/n-->. Research, not investment advice.

This file turns the thesis into a schedule: what is measured, on which dates it is judged, what each outcome means, and what gets built along the way. The rules themselves are frozen in [SIGNPOSTS.md](SIGNPOSTS.md) (hash in [SIGNPOSTS.lock](SIGNPOSTS.lock)), and this plan only refers to them.

## 1. The question the plan answers

> Over one to three years, do redeemable regulated wrappers take in more NEAR than the protocol mints?

That is NEAR's supply-side case in one condition. NEAR held in a redeemable wrapper leaves only when shares are redeemed. The protocol is scheduled to mint less (HSP-029). The buyback fund's balance grows by a small fraction of new issuance. If wrappers keep absorbing more than the mint, the marginal new NEAR ends up in vehicles that hold it until redemption. If they keep releasing NEAR, they add to new supply instead. Our data shows both have already happened within 46 days.

This is a thesis about **NEAR's holder base and new supply**. It does not cover usage, fees, valuation or all of NEAR's float. Ordinary staking moves more NEAR per day (section 4).

## 2. The instruments

| Instrument | Definition | Baseline | Where |
|---|---|---:|---|
| **Absorption ratio** (the thesis variable) | Wrapper net custody flow ÷ NEAR minted, same window | launch <!--n:absorption_launch:s2-->+3.63<!--/n-->; since peak <!--n:absorption_since_peak:s2-->-1.50<!--/n-->; latest 30 days <!--n:absorption_last30:s2-->-0.18<!--/n--> | `nfi/signposts.py`, `data/out/signposts.json` |
| Buyback ratio | Buyback-fund balance change ÷ NEAR minted | <!--n:buyback_ratio_launch:2-->0.11<!--/n--> | same |
| Inflation cap | `max_inflation_rate` read from the protocol at every daily height | <!--n:protocol_cap_pct_latest:pct-->2.50%<!--/n--> on protocol v<!--n:protocol_version_latest:int-->88<!--/n--> | `nfi/protocol.py`, `data/work/protocol.json` |
| Measured mint | Supply change at epoch boundaries, checked against the cap | <!--n:issuance_per_day:int-->89,233<!--/n--> NEAR/day; <!--n:issuance_ratio_median_pct:pct-->99.85%<!--/n--> of cap | `data/out/issuance_check.csv` |
| Wrapper-held share of supply | NRR staked ÷ total supply | <!--n:nrr_share_total_pct_latest:pct-->1.17%<!--/n--> | `data/out/daily.csv` |
| Staking outside the wrapper | Total stake minus NRR, daily change | mean <!--n:other_stake_abs_daily_mean:m-->2.74M<!--/n--> NEAR/day moved | `data/out/daily.csv` |
| Issuer reconciliation | Reconstruction vs Bitwise "NEAR in Trust", frozen rule | <!--n:issuer_gaps_count:int-->4<!--/n--> dates, max <!--n:max_abs_issuer_gap_pct:pct-->0.15%<!--/n-->, <!--n:issuer_oos_count:int-->1<!--/n--> out of sample | `data/issuer_snapshots.csv` |
| Scenario model | 36-month mechanical projection under fixed ratios | see section 5 | `nfi/model.py`, `data/out/scenarios.csv` |

Absorption is the one number to remember. It needs no basket conversion and no price. Because it divides by measured issuance, the HSP-029 ramp enters through the denominator on the day it happens, with no assumption about when.

## 3. The issuance path: HSP-029 as a ramp, not a switch

HSP-029 passed the House of Stake vote on 2 Nov 2026. Three steps remain before it binds: Security Council ratification, a protocol upgrade that validators must adopt, and a grace period of about 90 days. Then the cap falls linearly by about 3.75 basis points a month for 24 months. Cap and mint along the proposal's own schedule, on today's supply:

| Ramp month | Cap | Mint, NEAR/day | Baskets/day | Earliest calendar date* |
|---:|---:|---:|---:|---|
| 0 | <!--n:hsp029_m0_cap_pct:pct3-->2.5%<!--/n--> | <!--n:hsp029_m0_per_day:int-->89,233<!--/n--> | <!--n:hsp029_m0_baskets_per_day:2-->1.71<!--/n--> | Feb 2027 |
| 6 | <!--n:hsp029_m6_cap_pct:pct3-->2.275%<!--/n--> | <!--n:hsp029_m6_per_day:int-->81,202<!--/n--> | <!--n:hsp029_m6_baskets_per_day:2-->1.55<!--/n--> | Aug 2027 |
| 12 | <!--n:hsp029_m12_cap_pct:pct3-->2.05%<!--/n--> | <!--n:hsp029_m12_per_day:int-->73,171<!--/n--> | <!--n:hsp029_m12_baskets_per_day:2-->1.40<!--/n--> | Feb 2028 |
| 18 | <!--n:hsp029_m18_cap_pct:pct3-->1.825%<!--/n--> | <!--n:hsp029_m18_per_day:int-->65,140<!--/n--> | <!--n:hsp029_m18_baskets_per_day:2-->1.24<!--/n--> | Aug 2028 |
| 24 | <!--n:hsp029_m24_cap_pct:pct3-->1.6%<!--/n--> | <!--n:hsp029_m24_per_day:int-->57,109<!--/n--> | <!--n:hsp029_m24_baskets_per_day:2-->1.09<!--/n--> | Feb 2029 |

\*If ratification and the upgrade were immediate, so the 90-day grace period ran from mid-November 2026. The real start is later by however long those steps take. **The plan does not depend on this date.** `nfi/protocol.py` reads the cap at every daily height (<!--n:protocol_days_read:int-->51<!--/n--> heights so far, <!--n:protocol_versions_seen:int-->3<!--/n--> protocol versions, cap unchanged), so month 0 will be observed, not guessed. Ramp started at the latest reading: <!--n:hsp029_ramp_started:yn-->no<!--/n-->.

Two checks tie our model to the proposal: our month-24 mint matches its 57,300 NEAR a day, and the issuance avoided by month 27 in our model (<!--n:scen_avoided_issuance_m27:m-->11.87M<!--/n--> NEAR) matches its 11.8M over two years (tests in `tests/test_long_term.py`).

**Consequence for the thesis:** the 1.6% endpoint falls in year 3 of a one-to-three-year horizon. In years 1 and 2 the wrapper is compared with a mint of roughly 1.4 to 1.7 baskets a day, not 1.1.

Disclosure: HSP-029 was proposed by SVRN's chief executive. SVRN reports a NEAR treasury of more than <!--n:svrn_reported_holdings:m-->55.50M<!--/n--> NEAR (section 8).

## 4. The boundary: what the wrapper does not set

Stake held by everyone other than NRR moved <!--n:other_stake_abs_daily_mean:m-->2.74M<!--/n--> NEAR on an average day (median <!--n:other_stake_abs_daily_median:m-->1.09M<!--/n-->), against <!--n:nrr_stake_abs_daily_mean:m-->0.42M<!--/n--> for NRR. It was the larger mover on <!--n:other_stake_bigger_days:int-->41<!--/n--> of <!--n:other_stake_days:int-->47<!--/n--> days. Over the latest 30 days it fell by <!--n:other_stake_last30_change:m-->-7.74M<!--/n--> NEAR while NRR's stake rose by <!--n:nrr_stake_last30_change:m-->-0.42M<!--/n-->. About <!--n:staked_pct_of_supply:pct-->45.05%<!--/n--> of supply is staked.

So the plan never claims that the wrapper sets NEAR's float. It claims something narrower that can be tested. Among the supply terms a tokenomics model counts (issuance, buyback-fund accumulation and wrapper flow), the wrapper is the largest and the only one that has changed sign. Ordinary staking is far larger but is not a supply term: unstaked NEAR stays with its owner, while wrapper NEAR leaves only through redemption. Staking outside the wrapper stays on the dashboard as context, and the plan reviews it each year (section 7).

## 5. Three scenarios, made mechanical

`nfi/model.py` projects 36 months from the baseline. Mint = supply × cap × the measured mint efficiency (<!--n:scen_mint_efficiency_pct:pct-->99.85%<!--/n-->), less the measured burn share (<!--n:scen_burn_share_pct:pct-->1.11%<!--/n-->). The ramp starts at month <!--n:scen_ramp_start_month:int-->3<!--/n-->, the earliest possible. Wrapper rewards scale with the cap. Each scenario holds one absorption ratio for the whole period. These are arithmetic consequences of stated inputs, not forecasts, and no probabilities are given: 46 days cannot support them.

| | Bull: a = +1 | Base: a = 0 | Bear: a = −1 |
|---|---|---|---|
| Mechanism | Wrappers absorb all new NEAR along the falling issuance path | Wrapper flow nets to zero; the HSP-029 ramp is the main supply change | Launch demand was a one-off; wrappers return NEAR as fast as it is minted |
| NRR-type holdings at month 12 | <!--n:scen_m12_bull_near:m-->48.25M<!--/n--> (<!--n:scen_m12_bull_share_pct:pct-->3.59%<!--/n--> of supply) | <!--n:scen_m12_base_near:m-->16.00M<!--/n--> (<!--n:scen_m12_base_share_pct:pct-->1.19%<!--/n-->) | <!--n:scen_m12_bear_near:m-->0.00M<!--/n--> |
| At month 24 | <!--n:scen_m24_bull_near:m-->76.92M<!--/n--> (<!--n:scen_m24_bull_share_pct:pct-->5.62%<!--/n-->) | <!--n:scen_m24_base_near:m-->16.59M<!--/n--> (<!--n:scen_m24_base_share_pct:pct-->1.21%<!--/n-->) | <!--n:scen_m24_bear_near:m-->0.00M<!--/n--> |
| At month 36 | <!--n:scen_m36_bull_near:m-->101.83M<!--/n--> (<!--n:scen_m36_bull_share_pct:pct-->7.32%<!--/n-->) | <!--n:scen_m36_base_near:m-->17.09M<!--/n--> (<!--n:scen_m36_base_share_pct:pct-->1.23%<!--/n-->) | <!--n:scen_m36_bear_near:m-->0.00M<!--/n--> |
| What it would look like | a ≥ +1 in consecutive windows; shares outstanding rising on the issuer's page | \|a\| < 1 in most windows; holdings roughly flat | a ≤ −1 in consecutive windows; shares outstanding falling. At a = −1, today's position would be gone by month <!--n:scen_bear_empty_month:int-->6<!--/n--> |
| Confirms | BULLISH signpost (two windows) after launch effects have left the windows | BASE signpost (six windows) | BEARISH signpost (two windows) |
| Would weaken it (not a frozen rule) | A complete window below zero | Two consecutive windows beyond ±1 | A complete window above zero with shares outstanding rising |
| Indicators | Net creations, shares outstanding, premium to NAV, measured mint | Same, plus the cap | Net redemptions, discount to NAV, HSP-029 status |

A signpost state persists until another rule fires (the most recently fired rule sets the state), so the latest window's ratio is always published beside it. Wrapper rewards in the model compound at the pool's measured rate and ignore the fund's sponsor fee and staking-expense share, so the base case is slightly high.

The bull column shows the scale required: absorbing all new issuance means taking in about 2.4M NEAR a month. NRR's rolling 30-day net flow has been below that level since 9 Nov. The bear column shows that the position NRR has built is small next to the mint, and could be released in about half a year.

**The strongest competing interpretation, stated as the bear case:** NRR could be a small product that launched and faded. Authorised participants delivered existing inventory, including one block of <!--n:sources_largest_transfer:m-->5.01M<!--/n--> NEAR. The fund peaked within a month and has been redeeming since. On that reading the dashboard is an accurate record of a non-event for NEAR's supply. Today's data cannot rule this out. The signposts are built to tell this case apart from the others.

## 6. Calendar

Signpost windows are listed in [SIGNPOSTS.md](SIGNPOSTS.md). Window 1 covers 15 Nov – 14 Dec 2026, and a new one closes every 30 days.

| Stage | Dates | What arrives | What is decided |
|---|---|---|---|
| **Baseline** | 13–14 Nov 2026 | 46 daily windows; 4 issuer checks, 1 out of sample; cap 2.5%; signposts, both predictions and this plan frozen | Nothing. Measurement starts |
| **Month 1** | to 15 Dec 2026 | Window 1; Prediction 1 resolves (row 2026-12-14) and Prediction 2 (row 2026-12-15); about 30 new out-of-sample issuer days available | Does the frozen issuer rule hold on fresh data (any gap > 0.5% is a STRUCTURALLY WRONG input)? Record both predictions' verdicts as they fall |
| **Months 2–6** | to 14 May 2027 | Windows 2–6; HSP-029 ratification, upgrade and grace period, if on schedule; quarterly 13F holder filings for NRR (due about 45 days after each quarter end: mid-Feb and mid-May 2027) | Is the sign of a stable? Publish the median and range of the six ratios. Freeze annual thresholds for "sustained" and for wrapper-held share (SIGNPOSTS-2027.md, hashed). Decide Rule B (one-hop accounts) |
| **Months 7–12** | to Nov 2027 | Windows 7–12; ramp months 0–9 at the earliest (cap down to about 2.16%); any second NEAR wrapper that can be rebuilt and reconciled | First annual review (section 7). Does the combined ratio across covered products meet the bullish rule? |
| **Year 2** | Nov 2027 – Nov 2028 | Windows 13–24; cap falling from about 2.2% to 1.7% if the ramp starts at the earliest date; a full year of ratios, likely including one change in market conditions | Second annual review. Does wrapper-held share of supply trend, or revert to the mean? Do holders stay through a drawdown? |
| **Year 3** | Nov 2028 – Nov 2029 | Windows 25–36; cap at 1.6% if on schedule (Feb 2029 at the earliest) | **Final verdict:** has cumulative wrapper net flow since baseline exceeded cumulative mint since baseline (cumulative a ≥ +1)? |

## 7. Review routine

- **Daily (automatic, `daily-refresh` workflow):** custody balances and events, measured mint, buyback-fund balance, total stake, the protocol cap, rebuilt dashboard, signpost status. A failed refresh leaves the last good state and timestamp in place.
- **Each 30-day window:** the evaluator writes the window's a and b, and its status, to `data/out/signposts.json`. A state change is committed with the data that caused it.
- **Quarterly:** issuer filings and holder disclosures; SVRN's reports; HSP-029 implementation status (forum, release notes, the cap reading); a manual review of the attribution rule (new hub recipients, one-hop accounts, any sign that Rule A accounts serve another product).
- **Annually (Nov 2027, Nov 2028, Nov 2029):** re-read the thesis against all windows to date. Check whether staking outside the wrapper has become a supply term (for example, a liquid-staking token that is itself wrapped). Publish a dated verdict, and change nothing that is frozen.

## 8. Indicators

| Variable | Role | Source | Status |
|---|---|---|---|
| Wrapper creations, redemptions, net custody flow | Moves with the thesis; this is the thesis variable | this pipeline | have |
| Measured mint and the inflation cap | Leading: the path is scheduled | `issuance_check.csv`, `protocol.json` | have |
| HSP-029 implementation status | Leading | governance forum, protocol releases | dated note, quarterly |
| Total stake outside the wrapper | Context that bounds the claim | `daily.csv` | have |
| Shares outstanding, premium or discount to NAV | Leading for creations and redemptions | Bitwise's page (already in each snapshot row) | capture daily: build item 2 |
| Buyback-fund balance | Slow, lagging | this pipeline | have |
| Treasury-company holdings (SVRN) | Lagging, quarterly, company-reported | company filings | context only |
| NEAR Intents volume | Leading for buyback-fund growth and usage | Intents Explorer, DefiLlama | out of scope; other entries cover it |
| Daily active accounts, transactions | Usage demand, not a supply term | BigQuery | out of scope |
| Price and spot volume | Lagging confirmation | market data | year 2, after a year of ratios |

## 9. What gets built, in order

1. **Done (14 Nov 2026):** absorption and buyback ratios; protocol cap read daily; HSP-029 path and 36-month scenario model; frozen signposts with evaluator and tests; one-hop sensitivity shown separately.
2. **Month 1:** daily capture of shares outstanding and premium/discount from the issuer page, archived as evidence the same way as issuer snapshots.
3. **Months 2–6:** run `data/bigquery/completeness_onehop_candidates.sql` and decide on Rule B. Bitwise's 30 Sep 10-Q already supports the one known one-hop account: its staked figure matches Rule A plus that account to 0.01%, and Rule A alone is half (adopting it changes every count, so it is announced and versioned, never folded in silently). Add a basket-multiple flag to events (<!--n:creations_non_basket_count:int-->10<!--/n--> creations and <!--n:redemptions_non_basket_count:int-->4<!--/n--> redemptions are not whole baskets today).
4. **Months 7–12:** reconstruct a second NEAR wrapper with the same method and reconciliation test, and report coverage separately from the ratio. Candidates in order: **Bitwise NEAR Staking ETP** (Europe, launched mid-2025; physically backed, with weekly proof-of-holdings reports to reconcile against), then **21Shares NEAR Staking ETP** (launched Nov 2024). The main risk is shared custody: if a product's NEAR sits in a custodian's omnibus wallets with other clients' coins, it cannot be separated on-chain and is reported as not reconstructable. Grayscale's NEAR trust stays context only, because redemptions are not currently authorised. These products' age is not usable data until their accounts are identified and reconciled.
5. **Year 2:** model the sponsor fee and accrued staking expenses, to explain why every issuer gap so far has the same sign. Add a price series and test the lagging relation, only once a year of ratios exists.

## 10. Thresholds not yet defensible

Two judgements cannot be made honestly from 46 days, and the plan does not pretend otherwise: how many windows count as "sustained", and what level of wrapper-held share of supply matters. Both are left open until window 6. They will then be set from the observed distribution and frozen with a hash before they are used. The break-evens at ±1 are the only thresholds in force now, because they come from the economics, not from the data.

## 11. Risks to the plan itself

| Risk | Effect | Mitigation |
|---|---|---|
| Data provider outage or API change | Missing rows | Raw cache; incomplete rows are marked; more than 5 in a window voids it |
| Issuer page changes or stops publishing | Reconciliation stalls | Evidence files archived per snapshot; prospectus filings as fallback |
| Attribution drift (new custody pattern) | Undercount | Quarterly rule review; one-hop sensitivity published; reconciliation would show a growing gap |
| HSP-029 delayed, changed or rejected at upgrade | Ramp later or absent | Cap read from the chain; the ratio needs no assumption; "HSP-029 does not take effect" is listed in the thesis as a reason to change our mind |
| NRR changes its structure (staking share, custodian, pool) | Breaks continuity | Reconciliation catches level breaks; the change gets a dated note |
| Other wrappers launch but cannot be reconstructed | Coverage gap | Reported as coverage, never treated as a signal |

## 12. What would change our mind

Exactly the frozen rules: **BEARISH** (a ≤ −1 for two consecutive windows), or **STRUCTURALLY WRONG** (|a| below the buyback ratio for two consecutive windows, an issuer figure off the frozen rule by more than 0.5%, or Rule A accounts shown to serve another product). One more condition sits outside the rules: HSP-029 failing to take effect, which would remove the reason to expect the same wrapper flow to become a larger multiple of new supply over time.
