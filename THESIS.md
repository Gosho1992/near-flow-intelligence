# Thesis: Over one to three years, NEAR's supply-side case depends on one measurable condition: whether redeemable regulated wrappers absorb more NEAR than the protocol mints

**Project:** NEAR Flow Intelligence · **Track:** Investment Thesis · **Data through:** <!--n:data_through:-->2026-11-21<!--/n--> · Research, not investment advice.

## The thesis

**Over one to three years, NEAR's supply-side case depends on one measurable condition: whether redeemable regulated wrappers take in more NEAR than the protocol mints.** We measure that condition with the **absorption ratio**: wrapper net custody flow divided by NEAR minted in the same window. For Bitwise's NEAR ETF (NRR) it was <!--n:absorption_launch:s2-->+3.06<!--/n--> over its first <!--n:days:int-->54<!--/n--> daily windows, <!--n:absorption_since_peak:s2-->-1.25<!--/n--> in the <!--n:since_peak_net_flow_days:int-->24<!--/n--> windows since its <!--n:nrr_peak_date:-->2026-10-28<!--/n--> peak, and <!--n:absorption_last30:s2-->-0.82<!--/n--> over the latest 30. HSP-029, approved on 2 Nov 2026 and not yet active, would lower NEAR's maximum issuance from 2.5% to 1.6% along a 24-month ramp after a 90-day grace period, so the same wrapper flow becomes a larger multiple of new supply each month.

NEAR's supply-side case is therefore conditional. It strengthens if wrapper net creations stay above issuance, and weakens if wrappers keep returning NEAR faster than the protocol mints it. This is a hypothesis about what to watch, measured daily from the chain and judged by rules frozen before the first test window ([SIGNPOSTS.md](SIGNPOSTS.md)). It is not a price forecast and not a claim about NEAR's total float: stake held outside the wrapper moved about <!--n:other_stake_abs_daily_mean:m-->2.54M<!--/n--> NEAR on an average day in this period, far more than the wrapper did.

**Position today: the bullish condition is not met. Signpost state: <!--n:signposts_state:-->NOT YET TESTABLE<!--/n--> (the first window closes at row <!--n:signposts_first_window_end:-->2026-12-15<!--/n-->).**

The full test schedule, scenario model, indicators and build plan to 2029 are in **[LONG_TERM_PLAN.md](LONG_TERM_PLAN.md)**.

## Why it could matter for years, and what is only measured so far

| | Established at this data cut | Kept as hypothesis |
|---|---|---|
| Mechanism | Wrapper NEAR leaves only by redemption; NRR holds <!--n:nrr_holdings_latest:m-->14.91M<!--/n--> NEAR (<!--n:nrr_share_total_pct_latest:pct-->1.14%<!--/n--> of supply), reconciled with Bitwise on <!--n:issuer_gaps_count:int-->4<!--/n--> dates, one of them out of sample, and with Bitwise's SEC 10-Q at launch within the filing's published precision | That wrapper flow persists beyond one product's launch |
| Scale | NRR has out-moved issuance in both directions (ratios <!--n:absorption_launch:s2-->+3.06<!--/n--> and <!--n:absorption_since_peak:s2-->-1.25<!--/n-->), and the buyback fund grew by only <!--n:buyback_ratio_launch:2-->0.11<!--/n--> of issuance | The direction of future flow, and whether other products follow |
| Issuance | Measured at <!--n:issuance_per_day:int-->89,712<!--/n--> NEAR/day, <!--n:issuance_ratio_median_pct:pct-->99.85%<!--/n--> of the 2.5% cap | That HSP-029 takes effect, and when |
| Who delivered the NEAR | Nine wallets, more than a quarter in one transfer; redemptions went back to wallets that had delivered creations | Whether any of it was fresh market buying |

## The three supply terms, in one unit

| Supply term, same windows | Launch (<!--n:days:int-->54<!--/n--> days) | Since peak (<!--n:since_peak_net_flow_days:int-->24<!--/n--> days) | Latest 30 days |
|---|---:|---:|---:|
| NEAR minted | <!--n:mint_launch:int-->4,844,432<!--/n--> | <!--n:mint_since_peak:int-->2,152,486<!--/n--> | <!--n:mint_last30:int-->2,704,578<!--/n--> |
| NRR net custody flow | <!--n:launch_net_flow_total:sint-->+14,806,070<!--/n--> | <!--n:since_peak_net_flow_total:sint-->-2,680,753<!--/n--> | <!--n:last30_nrr_net:sint-->-2,210,536<!--/n--> |
| **Absorption ratio** (flow ÷ mint) | **<!--n:absorption_launch:s2-->+3.06<!--/n-->** | **<!--n:absorption_since_peak:s2-->-1.25<!--/n-->** | **<!--n:absorption_last30:s2-->-0.82<!--/n-->** |
| Buyback ratio (fund growth ÷ mint) | <!--n:buyback_ratio_launch:2-->0.11<!--/n--> | <!--n:buyback_ratio_since_peak:2-->0.13<!--/n--> | <!--n:buyback_ratio_last30:2-->0.12<!--/n--> |

A ratio of +1 means the wrapper absorbed all new NEAR. A ratio of −1 means it released as much again, doubling new supply. Both are economic break-evens, not fitted numbers. The rolling 30-day ratio peaked at <!--n:absorption_rolling_max:s2-->+6.50<!--/n--> on <!--n:absorption_rolling_max_date:-->2026-10-28<!--/n--> and has fallen since. On 13 Nov this thesis noted that the latest-30 reading was positive only because of creations between 15 and 27 Oct, and would turn negative as those days left the window. It turned negative in the next day's data (14 Nov). About 64% of all creations happened in the first five daily windows.

## Issuance is scheduled to fall, not falling

Today's 2.5% cap mints about <!--n:hsp029_m0_baskets_per_day:2-->1.71<!--/n--> baskets' worth a day (one basket = 10,000 NRR shares, about <!--n:basket_near:int-->52,331<!--/n--> NEAR). If HSP-029 takes effect, the cap falls by about 3.75 basis points a month: roughly <!--n:hsp029_m6_baskets_per_day:2-->1.56<!--/n--> baskets a day at month 6 of the ramp, <!--n:hsp029_m12_baskets_per_day:2-->1.41<!--/n--> at month 12, <!--n:hsp029_m18_baskets_per_day:2-->1.25<!--/n--> at month 18 and <!--n:hsp029_m24_baskets_per_day:2-->1.10<!--/n--> at month 24. Security Council ratification, a validator-adopted protocol upgrade and the grace period come first. So the 1.6% endpoint is in year 3 of this horizon (February 2029 at the earliest), not a near-term state. We read the cap from the chain at every daily height (<!--n:protocol_cap_pct_latest:pct-->2.50%<!--/n--> on protocol v<!--n:protocol_version_latest:int-->88<!--/n--> at the cut, unchanged across <!--n:protocol_versions_seen:int-->3<!--/n--> protocol versions in the window), so the ramp's start will be observed rather than assumed. The ratio's denominator is measured mint, so the ramp enters the test on the day it happens.

## What the wrapper does not set: staking outside it

About <!--n:staked_pct_of_supply:pct-->45.58%<!--/n--> of NEAR's supply is staked, and that stake moves far more than the wrapper does. Stake held by everyone other than NRR changed by <!--n:other_stake_abs_daily_mean:m-->2.54M<!--/n--> NEAR on an average day (median <!--n:other_stake_abs_daily_median:m-->0.99M<!--/n-->), against <!--n:nrr_stake_abs_daily_mean:m-->0.38M<!--/n--> for NRR and about 0.09M of issuance. It was the larger mover on <!--n:other_stake_bigger_days:int-->48<!--/n--> of <!--n:other_stake_days:int-->54<!--/n--> days. Over the latest 30 days it fell by <!--n:other_stake_last30_change:m-->-0.30M<!--/n--> NEAR while NRR's stake rose <!--n:nrr_stake_last30_change:m-->-2.41M<!--/n-->.

So the claim is narrower than "the ETF sets NEAR's float." Among the terms a supply model counts (issuance, buyback-fund accumulation and wrapper flow), the wrapper has been the largest, and the only one that has changed sign. Ordinary stake can be unstaked and stays with its owner. Wrapper NEAR leaves only through a redemption, which is why it is tracked as a separate quantity.

## Scenarios

`nfi/model.py` projects 36 months from the baseline, using measured mint efficiency, the measured burn share and the HSP-029 ramp starting at the earliest date. Each scenario holds one absorption ratio constant. Wrapper rewards compound at the pool's measured rate, ignoring the fund's sponsor fee and staking-expense share, so the base case is slightly high. These are arithmetic consequences of stated inputs, not forecasts or probabilities.

| | Bull: a = +1 | Base: a = 0 | Bear: a = −1 |
|---|---|---|---|
| Mechanism | Wrappers take in more NEAR than the falling issuance path creates | Wrapper flow oscillates around zero; the ramp is the main supply change | Launch demand was a one-off; wrappers return NEAR; or the ramp is delayed |
| Wrapper-held share of supply, month 12 / 24 / 36 | <!--n:scen_m12_bull_share_pct:pct-->3.54%<!--/n--> / <!--n:scen_m24_bull_share_pct:pct-->5.56%<!--/n--> / <!--n:scen_m36_bull_share_pct:pct-->7.26%<!--/n--> | <!--n:scen_m12_base_share_pct:pct-->1.14%<!--/n--> / <!--n:scen_m24_base_share_pct:pct-->1.16%<!--/n--> / <!--n:scen_m36_base_share_pct:pct-->1.17%<!--/n--> | Today's position gone by month <!--n:scen_bear_empty_month:int-->6<!--/n--> |
| Confirmed by | BULLISH signpost: a ≥ +1 in two consecutive windows | BASE signpost: six windows with no bull or bear pair | BEARISH signpost: a ≤ −1 in two consecutive windows |
| Would weaken it (not a frozen rule) | A complete window below zero | Two consecutive windows beyond ±1 | A complete window above zero with shares outstanding rising |

**The strongest competing reading is the bear case:** NRR is a small product that launched and faded. Authorised participants delivered existing inventory, including one 5.01M NEAR block, the fund peaked within a month, and it has been redeeming since. On this reading the dashboard accurately records a non-event for NEAR's supply. Our data cannot rule this out yet. The signposts are built to separate it from the other two cases within months, not years.

## Signposts (frozen)

Rules are frozen in [SIGNPOSTS.md](SIGNPOSTS.md) (SHA-256 in [SIGNPOSTS.lock](SIGNPOSTS.lock), OpenTimestamps proof attested in Bitcoin block 975,791). They are evaluated on **non-overlapping 30-day windows starting 15 Nov 2026 00:00 UTC**, so no launch-period window can trigger a rule. Flow and issuance are measured over the same window.

| State | Rule (two consecutive complete windows) | Reading at the data cut |
|---|---|---|
| Bullish | Absorption ratio ≥ +1 | Not testable yet; latest 30 days <!--n:absorption_last30:s2-->-0.82<!--/n--> |
| Bearish | Absorption ratio ≤ −1 | Not testable yet; <!--n:absorption_since_peak:s2-->-1.25<!--/n--> since the peak |
| Structurally wrong | \|absorption\| below the buyback ratio; or an issuer figure off the frozen rule by more than 0.5%; or Rule A accounts shown to serve another product | Latest 30 days: \|<!--n:absorption_last30:s2-->-0.82<!--/n-->\| against <!--n:buyback_ratio_last30:2-->0.12<!--/n-->, not below. On 13 Nov it was marginally below (0.111 vs 0.113), which shows the rule can fire. Neither period is a signpost window |
| Coverage, reported separately | Number of wrappers rebuilt from the chain and reconciled to an issuer | <!--n:products_attributed_onchain:int-->1<!--/n--> |

**A state persists until another rule fires** (frozen text: the most recently fired rule sets the state), so the latest window's ratio is always shown beside it on the dashboard and in `data/out/signposts.json`.

**Coverage is not a bullish signal.** A second reconstructed product raises confidence in the measurement. It is bullish only if the combined absorption ratio across covered products meets the bullish rule.

## Verdict at the current data cut

**A large, observable, reconciled position is established. Persistent net absorption is not.** NRR's attributed staking accounts held <!--n:nrr_holdings_latest:m-->14.91M<!--/n--> NEAR on <!--n:data_through:-->2026-11-21<!--/n-->, <!--n:change_since_peak_pct:spct-->-15.00%<!--/n--> below the <!--n:nrr_peak_date:-->2026-10-28<!--/n--> peak. Seven weeks of one product establish scale and reversibility. They do not establish any rate.

## Evidence

### 1. The issuer comparison

On the <!--n:issuer_gaps_count:int-->4<!--/n--> issuer dates archived, reconstructed NRR staked balances differ from Bitwise's published "NEAR in Trust" by no more than <!--n:max_abs_issuer_gap_pct:pct-->0.15%<!--/n-->. The comparison rule was fixed on 13 Nov 2026 after the first three figures. The 12 Nov figure, published afterwards, is the first out-of-sample test: <!--n:issuer_gap_oos_pct:spct-->-0.15%<!--/n-->. All four gaps share a sign. Sources and retrieval timestamps are in `data/issuer_snapshots.csv`. A 0.5% tolerance is about 77,000 NEAR, more than one basket, so a match supports the reconstruction but cannot prove that no account is missing.

### 1b. The regulator's filing at launch

Bitwise's first 10-Q (period ended 30 Sep 2026) values the fund at 4 p.m. Eastern, which is 20:00 UTC. We read the chain at the last block before that moment (block <!--n:sec_valuation_height:int-->217,960,556<!--/n-->). The filing names no addresses, so this tests our reconstruction against aggregates. It does not prove ownership.

| Filing figure | Filing | On-chain at 20:00 UTC | Difference |
|---|---:|---:|---:|
| In-kind creations | <!--n:sec_in_kind_filing:d4-->5,010,335.4989<!--/n--> NEAR | two transfers from wallet `60142764…` into the custody hub: <!--n:sec_in_kind_onchain:d4-->5,010,335.4990<!--/n--> NEAR | under 0.0001 NEAR (the filing shows four decimals) |
| Staked NEAR: $553,300 at the $5.30 principal-market price | <!--n:sec_staked_implied:int-->104,396<!--/n--> NEAR; with the published rounding ($100, one cent) anything from <!--n:sec_staked_band_low:int-->104,288<!--/n--> to <!--n:sec_staked_band_high:int-->104,504<!--/n--> | the Rule A seed account plus the one-hop account: <!--n:sec_staked_two_accounts:int-->104,409<!--/n--> NEAR | inside the band. The point estimate differs by <!--n:sec_staked_diff:sint-->+12<!--/n--> NEAR, but the filing's rounding cannot resolve differences that small |
| NEAR bought for creations but not yet delivered on-chain | Two balances describe it from opposite sides: **receivable for creations** $14,039,097 (NEAR owed to the Trust under binding creation orders, valued at the $5.38 NAV reference) and **payable for NEAR purchased** $<!--n:sec_payable_purchased:int-->14,044,291<!--/n--> (the Trust's unsettled purchase cost) | purchases in the filing minus purchased NEAR already on-chain: <!--n:sec_purchased_undelivered:int-->2,609,503<!--/n--> NEAR | implied prices $<!--n:sec_receivable_implied_price:d4-->5.3800<!--/n--> (receivable) and $<!--n:sec_payable_implied_price:d4-->5.3820<!--/n--> (payable). The first equals the published $5.38 NAV reference; the second is a trade price 0.04% higher. Consistent at the published price precision (±$<!--n:sec_receivable_band_usd:int-->13,048<!--/n--> for a half-cent), not to the dollar |

The in-kind test is exact. The staked test is the most informative: The Rule A account alone gives <!--n:sec_staked_rule_a_only_diff_pct:spct-->-49.99%<!--/n--> and the whole pool <!--n:sec_staked_whole_pool_diff_pct:spct-->+17.48%<!--/n-->. Only the Rule A seed account plus the one-hop account it funded falls inside the filing's precision band. This is independent evidence that the one-hop account belongs to NRR. We record it here, and the frozen Rule A count stays unchanged until the Rule B decision (LONG_TERM_PLAN.md, section 9). Check: `nfi/sec_check.py`, output `data/work/sec_reconciliation.json`, five tests in `tests/test_long_term.py`; transcribed filing figures in `data/issuer_evidence/2026-09-30_sec_10q.txt`.

### 2. The custody position and flows

- Latest attributed NRR staked position: <!--n:nrr_holdings_latest:int-->14,907,118<!--/n--> NEAR. Peak <!--n:nrr_peak:int-->17,537,598<!--/n--> NEAR on <!--n:nrr_peak_date:-->2026-10-28<!--/n-->.
- Cumulative creations <!--n:creations_total:int-->17,549,579<!--/n--> NEAR; redemptions <!--n:redemptions_total:int-->2,743,509<!--/n--> NEAR; net custody flow **<!--n:custody_flow_net:sint-->+14,806,070<!--/n--> NEAR**, excluding staking rewards (<!--n:rewards_total:int-->100,696<!--/n--> NEAR measured separately; the unexplained residual is kept visible).
- Since the peak: <!--n:since_peak_creations_total:int-->62,756<!--/n--> NEAR created, <!--n:since_peak_redemptions_total:int-->2,743,509<!--/n--> redeemed.
- **Not every event is a basket.** <!--n:creations_non_basket_count:int-->11<!--/n--> of the creation events (<!--n:creations_non_basket_near:int-->62,756<!--/n--> NEAR in total) and <!--n:redemptions_non_basket_count:int-->6<!--/n--> redemptions (<!--n:redemptions_non_basket_near:int-->18,713<!--/n--> NEAR) are not whole 10,000-share baskets. They look operational, not like investor creations. They are small and included in the totals, and an event-level flag is on the build plan.

### 3. Where NRR's NEAR came from

Of the <!--n:sources_external_total:m-->18.37M<!--/n--> NEAR sent to the custody hub from outside (gross inflow), a single transfer delivered <!--n:sources_largest_transfer:int-->5,010,330<!--/n--> NEAR, more than a quarter. Exchange-style wallets account for between <!--n:sources_exchange_style_low_pct:pct-->23.48%<!--/n--> and <!--n:sources_exchange_style_pct:pct-->48.32%<!--/n--> of the total. The range comes from <!--n:sources_edge_wallets:int-->2<!--/n--> wallets (<!--n:sources_edge_near:m-->4.56M<!--/n--> NEAR) that pass the heuristic by less than 5% on one threshold. The rest came from wallets that do not meet the test. Redeemed NEAR that we could trace past the hub went to <!--n:sources_onward_wallets:int-->2<!--/n--> wallets that had themselves delivered <!--n:sources_onward_wallets_also_delivered:m-->3.26M<!--/n--> NEAR of creations. That fits authorised participants moving existing inventory in and out in kind. It cannot separate inventory from fresh purchases, and wallet labels are a heuristic (`data/out/source_mix.csv`).

### 4. Attribution and the completeness boundary

The primary set is <!--n:attributed_accounts:int-->73<!--/n--> accounts under Rule A: the inferred custody hub funds an account, and that account then calls `deposit_and_stake` on `bitwise_2.poolv1.near`. This is a repeatable on-chain rule, not a finding of legal ownership.

**One account is outside Rule A and verified from our own raw cache.** Rule A account `432766…94e7b4c5` sent 52,192.07 NEAR to `9a000319…dadf21b3` at block 217,688,225. That account staked 52,192.02 NEAR in the NRR pool at block 217,690,243 and held <!--n:one_hop_staked_latest:int-->52,557<!--/n--> NEAR there on the data cut. Test `OneHop` in `tests/test_long_term.py` checks both transactions. Bitwise's 30 Sep 10-Q supports it independently: its staked figure matches the seed account plus this account, and neither alone (section 1b). We keep it out of the totals so that every published count follows one rule. Adding it would move the four issuer gaps from about −0.15% to between <!--n:one_hop_gap_min_pct:spct-->+0.19%<!--/n--> and <!--n:one_hop_gap_max_pct:spct-->+0.20%<!--/n-->. Either way the gaps stay well inside 0.5%, so the reconciliation cannot decide between 73 and 74 accounts. Whether to adopt a one-hop Rule B is decided in the first six months (LONG_TERM_PLAN.md, section 9).

The BigQuery comparison starts from direct recipients of the hub and finds the same 94 pool transactions, hash for hash. It checks completeness within that population only.

### 5. Issuance and the buyback-fund balance

Gross issuance comes from total-supply changes at epoch boundaries, checked against the protocol cap: the median epoch mints <!--n:issuance_ratio_median_pct:pct-->99.85%<!--/n--> of the maximum. The buyback series is the combined native NEAR and wNEAR balance of the defined buyback-fund accounts. It rose by <!--n:buyback_fund_change_total:int-->557,071<!--/n--> NEAR (<!--n:buyback_change_pct_of_issuance:pct-->11.50%<!--/n--> of issuance) and never fell on any observed day. It is a balance, not executed purchases, burns or price support.

### 6. Where redeemed NEAR goes

The trace panel follows unstake, withdrawal and return steps to the hub, then looks for a possible next hub outflow. <!--n:redemption_traces_probable:int-->7<!--/n--> of <!--n:redemption_traces:int-->14<!--/n--> redemption traces have probable onward matches to exchange-style wallets (counted by trace, not by value). The hub pools balances, so a match does not prove the same units moved onward. Links past the hub are at best probable and never imply a sale.

## Evidence against the thesis

- **Breadth:** one product, <!--n:days:int-->54<!--/n--> daily windows. This cannot be fixed before the first windows complete. It is stated here rather than disguised.
- **Launch concentration and reversal:** about 64% of creations fell in the first five days, and holdings are <!--n:change_since_peak_pct:spct-->-15.00%<!--/n--> from the peak.
- **Ordinary staking is far larger:** about 6 times NRR's average daily move. The thesis is about a narrower, redeemable quantity.
- **In-kind mechanics:** NEAR can arrive from authorised participants' existing inventory and leave to them without a market trade.
- **The structurally-wrong rule nearly fired on launch data:** 0.111 against 0.113 on 13 Nov, outside the signpost windows.
- **Custody is not ownership,** the buyback series is not purchases, and price impact is not estimated.
- **HSP-029 is not yet binding,** and was proposed by the chief executive of SVRN, a large NEAR holder (see below).

## Pre-registered predictions

[PREDICTION.md](PREDICTION.md) (frozen 13 Nov 2026, [lock](PREDICTION.lock), Bitcoin-attested proof). From 14 Nov to 13 Dec, gross NRR custody moves will exceed gross buyback-fund moves. It tests whether NRR stays active. It does not test direction.

[PREDICTION-2.md](PREDICTION-2.md) (frozen 14 Nov 2026 before its window, [lock](PREDICTION-2.lock), Bitcoin-attested proof). From 15 Nov to 14 Dec, the absolute value of NRR's net custody flow will exceed the absolute value of the buyback fund's net change. Over the 30 days before it was frozen the two were almost equal, so it can fail. **How to read it:** a pass caused by net redemptions supports the claim that the wrapper is the swing factor, and is negative for the bull case. A pass by net creations supports both. Neither prediction tests the wrapper against issuance. The signposts do, from the same start date. All three are evaluated by `make verify-prediction`. The frozen files are never edited.

## What would change our mind

Exactly the frozen signposts:

- **BEARISH:** absorption ratio ≤ −1 for two consecutive windows.
- **STRUCTURALLY WRONG:** |absorption| below the buyback ratio for two consecutive windows; or a new issuer figure off the frozen rule by more than 0.5%; or evidence that Rule A accounts serve another product.

One more condition sits outside the rules. If HSP-029 fails to take effect, the reason to expect the same flow to become a growing multiple of new supply is gone.

## Other NEAR holders: context only

SVRN, Inc. reported a treasury of more than <!--n:svrn_reported_holdings:m-->55.50M<!--/n--> NEAR on <!--n:svrn_reported_as_of:-->2026-08-27<!--/n-->. On 13 Nov 2026 the `svrn_bitwise.poolv1.near` pool held <!--n:svrn_observed_staked:m-->10.48M<!--/n--> NEAR. One account holds <!--n:svrn_largest_account_staked:int-->10,466,589<!--/n--> NEAR of it, more than 99.99%; the other five, including the pool owner and two probes, hold under 100 NEAR staked between them. That account's staked balance was identical on 11, 12 and 13 Nov while the pool owner's balance grew. This fits a pool that pays rewards to its owner, but it is an inference from three days. Beyond the pool's name, it is the only on-chain hint that the delegator and the operator are related. The reported figure is 79 days older than the observation. The two are never added together or to NRR totals. SVRN's chief executive authored HSP-029.

21Shares and Grayscale remain contextual references only. No account-level reconstruction is claimed for either.

## Sources and method

[METHOD.md](METHOD.md): rules, windows, calculations, limits. [SOURCES.md](SOURCES.md): dated source register. [LONG_TERM_PLAN.md](LONG_TERM_PLAN.md): test schedule to 2029.
