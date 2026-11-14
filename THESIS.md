# Thesis: A redeemable ETF is now a major swing factor in NEAR's float; the long-term case depends on the sign and persistence of its net custody flow

**Project:** NEAR Flow Intelligence · **Track:** Investment Thesis · **Data through:** <!--n:data_through:-->2026-11-13<!--/n--> · Research, not investment advice.

## The claim in one paragraph

Bitwise's NEAR ETF (NRR) has become a measurable, reversible source of NEAR moving into and out of staked custody. Across the <!--n:days:int-->46<!--/n--> daily windows observed since its first staking activity, its signed net custody flow averaged **<!--n:launch_net_flow_per_day:sint-->+330,985<!--/n--> NEAR/day** (<!--n:launch_net_baskets_per_day:s1-->+6.3<!--/n--> approximate 10,000-share baskets/day). Since its holdings peak on <!--n:nrr_peak_date:-->2026-10-28<!--/n-->, across <!--n:since_peak_net_flow_days:int-->16<!--/n--> daily windows, the average reversed to **<!--n:since_peak_net_flow_per_day:sint-->-141,344<!--/n--> NEAR/day** (<!--n:since_peak_net_baskets_per_day:s1-->-2.7<!--/n--> baskets/day). This is the finding: a single redeemable product can move NEAR into custody at scale and can later release it at scale. It does **not** establish market purchases, sales, legal ownership or price impact. The long-term question is whether NRR's net flow stabilises, continues to reverse, or is joined by other independently attributable products.

## The long-term thesis (1 to 3 years)

**NEAR's float will be set more by regulated-product net flow than by issuance or buybacks, so the long-term case for NEAR is a bet on that flow turning, and staying, positive.** This is a claim about what will move NEAR's supply picture and what to watch, not a price forecast.

Why, in one unit (one basket = 10,000 NRR shares, about <!--n:basket_near:int-->52,331<!--/n--> NEAR):

1. **Issuance is falling.** NEAR mints about <!--n:issuance_baskets_per_day:1-->1.7<!--/n--> baskets' worth a day under today's 2.5% cap. HSP-029, approved on 2 Nov 2026 but not yet active, lowers the cap to 1.6%: about <!--n:issuance_hsp029_baskets_per_day:1-->1.1<!--/n--> a day at full target.
2. **The protocol's own offset is small.** The buyback fund's balance grows by about <!--n:buyback_baskets_per_day:1-->0.2<!--/n--> baskets a day.
3. **One redeemable fund already moves several times more, both ways.** NRR averaged <!--n:launch_net_baskets_per_day:s1-->+6.3<!--/n--> baskets a day over its first <!--n:days:int-->46<!--/n--> days and <!--n:since_peak_net_baskets_per_day:s1-->-2.7<!--/n--> a day since its 28 Oct peak.
4. **That flow can be watched daily, from the chain, account by account,** instead of waiting for issuer files or press coverage, and it already matches Bitwise's own figures (including one published after our method was frozen).

So, once issuance falls to about one basket a day, whether NEAR's liquid float grows or shrinks at the margin will depend mostly on the sign of regulated-product net flow. Today that rests on one product.

**Position today: not yet.** The bull case needs sustained net inflow. Over the last 30 days NRR averaged <!--n:last30_net_baskets_per_day:s1-->+0.2<!--/n--> baskets a day, against the <!--n:issuance_hsp029_baskets_per_day:1-->1.1<!--/n--> a day that would absorb all post-HSP-029 issuance, and the flow has been negative since 28 Oct.

| Signpost | Threshold, written in advance | Reading now |
|---|---|---|
| Turns bullish | NRR's 30-day net flow above +<!--n:issuance_hsp029_baskets_per_day:1-->1.1<!--/n--> baskets a day (it would absorb all post-HSP-029 issuance) for two consecutive 30-day windows, or a second product that can be rebuilt and reconciled | <!--n:last30_net_baskets_per_day:s1-->+0.2<!--/n--> baskets a day; <!--n:products_attributed_onchain:int-->1<!--/n--> product |
| Turns bearish | NRR's 30-day net outflow larger than issuance (below −<!--n:issuance_baskets_per_day:1-->1.7<!--/n--> baskets a day) for two consecutive windows | <!--n:last30_net_baskets_per_day:s1-->+0.2<!--/n--> baskets a day |
| Thesis wrong | NRR's absolute 30-day net flow smaller than the buyback fund's growth for two consecutive months: the ETF is no longer the swing. Prediction 2 tests the first month | 30-day net flow <!--n:last30_nrr_net:sint-->+297,710<!--/n--> NEAR against buyback growth <!--n:last30_buyback_fund_change:sint-->+302,826<!--/n--> NEAR |

## Verdict at the current data cut

**A large, observable position is established; persistent incremental buying is not.** NRR's attributed staking accounts held <!--n:nrr_holdings_latest:m-->15.31M<!--/n--> NEAR on <!--n:data_through:-->2026-11-13<!--/n-->, <!--n:change_since_peak_pct:spct-->-12.70%<!--/n--> below the <!--n:nrr_peak_date:-->2026-10-28<!--/n--> peak. The latest 30 daily windows show net custody flow of <!--n:last30_nrr_net:sint-->+297,710<!--/n--> NEAR in total, while the post-peak period is materially negative. A 46-day history of one product is not enough to establish a long-term pattern.

## Comparable flow units

One basket is 10,000 NRR shares. Its NEAR equivalent is calculated from the latest included issuer snapshot's NEAR-per-share figure. Basket equivalents are a scale unit, not a claim that each custody movement was a market trade.

| Flow measure | NEAR/day | Approx. baskets/day |
|---|---:|---:|
| NRR signed net custody flow, launch period average | <!--n:launch_net_flow_per_day:sint-->+330,985<!--/n--> | <!--n:launch_net_baskets_per_day:s1-->+6.3<!--/n--> |
| NRR signed net custody flow, after <!--n:nrr_peak_date:-->2026-10-28<!--/n--> peak average | <!--n:since_peak_net_flow_per_day:sint-->-141,344<!--/n--> | <!--n:since_peak_net_baskets_per_day:s1-->-2.7<!--/n--> |
| NRR signed net custody flow, latest 30-day average | <!--n:last30_net_flow_per_day:sint-->+9,924<!--/n--> | <!--n:last30_net_baskets_per_day:s1-->+0.2<!--/n--> |
| NEAR issuance, measured launch-period average | <!--n:issuance_per_day:int-->89,497<!--/n--> | <!--n:issuance_baskets_per_day:1-->1.7<!--/n--> |
| Buyback-fund balance change, launch-period average | <!--n:buyback_net_change_per_day:int-->9,935<!--/n--> | <!--n:buyback_baskets_per_day:1-->0.2<!--/n--> |
| Issuance scenario if the proposed 1.6% target is fully reached | <!--n:issuance_hsp029_target_per_day:int-->57,278<!--/n--> | <!--n:issuance_hsp029_baskets_per_day:1-->1.1<!--/n--> |

The periods differ by design: launch period is <!--n:days:int-->46<!--/n--> daily windows, post-peak is <!--n:since_peak_net_flow_days:int-->16<!--/n--> daily windows after the peak date, and latest 30 days is 30 daily windows. The table shows averages per complete daily window. Cumulative totals are reported separately below and on the dashboard.

The 1.6% line is a full-target scenario based on HSP-029 and a proportional scaling of the measured 2.5% issuance rate. The official forum record lists the proposal as Succeeded, but the 1.6% rate is not yet active in the observed protocol configuration: the change still requires the remaining governance/implementation steps, a grace period and validator adoption. The scenario is included to show how the ETF flow compares with a lower future issuance baseline, not to forecast either one.

## What we measure

This project reconstructs NRR's **observed NEAR staking custody**, account by account and transaction by transaction, from NEAR mainnet. It compares that reconstruction with Bitwise's own "NEAR in Trust" snapshots, then places NRR custody movements alongside NEAR issuance and the protocol buyback-fund balance change.

### 1. The issuer comparison

On the <!--n:issuer_gaps_count:int-->4<!--/n--> issuer dates currently archived, reconstructed NRR staked balances differ from Bitwise's published "NEAR in Trust" by no more than <!--n:max_abs_issuer_gap_pct:pct-->0.15%<!--/n-->. The source dates and retrieval timestamps are recorded in `data/issuer_snapshots.csv`. This is a dated comparison, not a claim that Bitwise independently verifies each unreported day.

### 2. The observed custody position and flows

- Latest attributed NRR staked position: <!--n:nrr_holdings_latest:int-->15,310,526<!--/n--> NEAR.
- Peak position: <!--n:nrr_peak:int-->17,537,598<!--/n--> NEAR on <!--n:nrr_peak_date:-->2026-10-28<!--/n-->.
- Cumulative creations since the first observed staking activity: <!--n:creations_total:int-->17,544,103<!--/n--> NEAR.
- Cumulative redemptions/withdrawals: <!--n:redemptions_total:int-->2,318,791<!--/n--> NEAR.
- Net custody movements over that period: **<!--n:custody_flow_net:sint-->+15,225,313<!--/n--> NEAR**, excluding staking rewards.
- The holdings balance also accrues staking rewards; cumulative measured rewards are <!--n:rewards_total:int-->84,844<!--/n--> NEAR. The unexplained residual is kept visible, not silently allocated.

Since the 28 Oct peak, across <!--n:since_peak_net_flow_days:int-->16<!--/n--> daily windows, the pipeline recorded <!--n:since_peak_creations_total:int-->57,281<!--/n--> NEAR in creations and <!--n:since_peak_redemptions_total:int-->2,318,791<!--/n--> NEAR in redemptions, for a cumulative signed net custody flow of <!--n:since_peak_net_flow_total:sint-->-2,261,510<!--/n--> NEAR. Dividing that total by the 16 windows gives the average daily rate shown above.

### Where NRR's NEAR came from

Of the <!--n:sources_external_total:m-->18.37M<!--/n--> NEAR sent to the custody hub from outside, <!--n:sources_exchange_style_pct:pct-->48.32%<!--/n--> came from exchange-style wallets and <!--n:sources_other_pct:pct-->51.68%<!--/n--> from <!--n:sources_other_wallets:int-->4<!--/n--> other wallets, including a single transfer of <!--n:sources_largest_transfer:int-->5,010,330<!--/n--> NEAR (`data/out/source_mix.csv`, every wallet and its largest transaction). Redeemed NEAR that we could trace past the hub went to <!--n:sources_onward_wallets:int-->2<!--/n--> wallets that had themselves delivered <!--n:sources_onward_wallets_also_delivered:m-->3.26M<!--/n--> NEAR of creations. That pattern fits authorised participants moving NEAR in and out in kind; it says nothing about market buying or selling, and wallet labels are a heuristic.

### 3. Attribution and the completeness boundary

The primary set contains <!--n:attributed_accounts:int-->73<!--/n--> accounts identified by Rule A: the inferred custody hub funds an account, and that account subsequently calls `deposit_and_stake` on `bitwise_2.poolv1.near`. This is a repeatable on-chain attribution rule, not a legal ownership assertion.

A review identified a one-hop candidate outside Rule A: account `9a00031933695207a60a3af95cfaaadcea863812ecbc30400c109417dadf21b3` appears to have received approximately 52,192.07 NEAR from a directly hub-funded account and then staked approximately 52,192.02 NEAR in the NRR pool. It is **not included** in the 73-account total pending independent reproduction of the intermediate transfer, chronology and account history. The account balance/sensitivity should be shown separately rather than silently added to the primary series.

The Google BigQuery comparison currently starts from direct recipients of the inferred custody hub. It finds the same 94 pool transactions as the pipeline, hash for hash, for that selected direct-recipient population. It is a useful completeness check within that population. It does **not** test accounts funded one hop downstream and therefore does not establish that no downstream account was missed.

### 4. Issuance and the buyback-fund balance

Gross issuance is derived from NEAR total-supply changes at epoch boundaries and checked against the protocol's configured inflation formula. The observed median mint is <!--n:issuance_ratio_median_pct:pct-->99.85%<!--/n--> of the formula's maximum across the checked epochs.

The buyback series is the combined native NEAR and wNEAR balance in the defined buyback-fund accounts. Its balance increased by <!--n:buyback_fund_change_total:int-->457,016<!--/n--> NEAR over the observed period, equivalent to <!--n:buyback_change_pct_of_issuance:pct-->11.10%<!--/n--> of measured gross issuance. This is a balance change, not executed market purchases, token burns or proof of price support.

### 5. Where redeemed NEAR goes

The trace panel follows observed unstake, withdrawal and return steps, then searches for a possible next hub outflow. Three of ten currently reconstructed redemption traces have probable onward matches to exchange-style wallets. NEAR is fungible and the hub pools balances; a match is not proof that the same units travelled onward. An exchange-style label is a transaction-pattern heuristic, not identification of an exchange, and does not prove a sale.

## Conditions to watch

| Condition | Measurement | Current interpretation |
|---|---|---|
| Does net custody flow remain positive after launch? | Signed NRR net custody flow over rolling 30-day windows; also compare with its post-peak direction | Latest 30-day total: <!--n:last30_nrr_net:sint-->+297,710<!--/n--> NEAR. The 28 Oct-to-cut period is materially negative. A single 30-day reading, in either direction, does not prove persistence. |
| How large is the flow against protocol supply? | Signed NRR flow and gross issuance, expressed in NEAR/day and basket equivalents | NRR has averaged <!--n:since_peak_net_flow_per_day:sint-->-141,344<!--/n--> NEAR/day since the peak; measured issuance averaged <!--n:issuance_per_day:int-->89,497<!--/n--> NEAR/day over the launch window. |
| Is the flow concentrated in one product? | Independently reconstructed and issuer-reconciled products; partial pool observations kept separate | One reconstructed and issuer-reconciled product (NRR). SVRN has a partial, un-reconciled one-pool observation only. |
| Where does redeemed NEAR go? | Onward matches after return to the custody hub | <!--n:redemption_traces_probable:int-->3<!--/n--> of <!--n:redemption_traces:int-->10<!--/n--> traces have probable onward matches. No claim of selling. |
| Does the protocol offset change? | Buyback-fund balance change against gross issuance | The balance increased by an amount equivalent to <!--n:buyback_change_pct_of_issuance:pct-->11.10%<!--/n--> of measured issuance; executed purchases are not measured. |

## Evidence against the thesis

- **Launch concentration:** the record is only <!--n:days:int-->46<!--/n--> daily windows for one product. A large early inflow can dominate the average.
- **Reversal:** NRR's holdings fell <!--n:change_since_peak_pct:spct-->-12.70%<!--/n--> from the 28 Oct peak. The same pool that accumulated NEAR can release it.
- **In-kind mechanics:** the prospectus allows creations and redemptions in cash or in kind through authorised participants. NEAR can arrive from existing inventory rather than a market purchase, and can leave to a redeeming participant without being sold.
- **Custody is not legal ownership:** the hub and basket-account attribution are inferred from transaction patterns and issuer reconciliation.
- **The buyback series is not executed purchases:** only the fund balance is measured.
- **Price impact is not estimated:** a 46-day series for one fund cannot establish a causal price effect.
- **Partial holder visibility:** the SVRN pool observation covers one named pool only and is not reconciled to the company's reported treasury.

## Bull case

NRR's net custody flow stabilises or returns to sustained positive levels after its launch period, while more NEAR investment products become independently attributable and reconcilable. In that case, the ETF is a persistent, observable component of NEAR's float dynamics, and the dashboard offers a useful daily measure of how its net flow compares with issuance.

## Bear case

The early inflow was a launch event. Redemptions continue, the fund becomes a net source of NEAR from staked custody, and no second independently attributable product appears. In that case, the position remains large but reversible; custody should not be described as persistent market demand.

## Pre-registered predictions

See [PREDICTION.md](PREDICTION.md), frozen on 13 Nov 2026 and protected by [PREDICTION.lock](PREDICTION.lock). Its 14 Nov–13 Dec test compares the **sum of absolute daily NRR custody movements** (creations plus redemptions) with the **sum of absolute daily buyback-fund balance changes**. It tests relative movement scale after the launch period. It does **not** test the sign of NRR's net flow, prove market buying or selling, or establish price impact. The original frozen file and lock are unchanged.

[PREDICTION-2.md](PREDICTION-2.md), frozen on 14 Nov 2026 before its window and protected by [PREDICTION-2.lock](PREDICTION-2.lock), is the sharper test: from 15 Nov to 14 Dec, the **absolute value of NRR's net custody flow** will exceed the **absolute value of the buyback fund's net balance change**. Over the 30 days before it was frozen the two were almost equal, so it can fail. It is the first test of the "thesis wrong" signpost above. Both are evaluated by `make verify-prediction`.


## What would change our mind

- NRR's rolling 30-day signed net custody flow remains negative for two consecutive windows/months.
- NRR's outflows persist at a rate comparable to or greater than gross issuance.
- A new issuer snapshot diverges materially from the pre-existing frozen reconstruction rule.
- Evidence shows that accounts attributed under Rule A serve another Bitwise product.
- A second independently reconstructed product demonstrates that the effect is not unique to NRR.

## Other NEAR holders: context only

SVRN, Inc. reported a treasury of more than <!--n:svrn_reported_holdings:m-->55.50M<!--/n--> NEAR on <!--n:svrn_reported_as_of:-->2026-08-27<!--/n-->. On 13 Nov 2026, the `svrn_bitwise.poolv1.near` pool showed <!--n:svrn_observed_staked:m-->10.36M<!--/n--> NEAR across <!--n:svrn_accounts_observed:int-->6<!--/n--> delegator accounts. This is a partial observation of one pool, not a reconstruction of SVRN's full treasury. The reported figure and pool observation are from different dates, may overlap, and are never added together or to NRR totals.

21Shares and Grayscale remain contextual references only; no account-level reconstruction is claimed for either.

## Sources and method

See [METHOD.md](METHOD.md) for attribution rules, flow definitions, date windows, calculations, missing-data handling and known limitations. See [SOURCES.md](SOURCES.md) for the dated source register and retrieval evidence.
