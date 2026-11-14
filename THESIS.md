# Thesis: NEAR's long-term case now rests on institutional demand more than on its buybacks, and on whether that demand stays

**Project:** NEAR Flow Intelligence · **Track:** Investment Thesis · **Data through:** <!--n:data_through:-->2026-11-13<!--/n--> · Research, not financial advice.

## The long-term case in one paragraph

NEAR's supply grows by about 2.5% a year, roughly <!--n:annual_issuance_estimate:m-->32.67M<!--/n--> NEAR at the current pace. The protocol's own answer to that dilution, the Intents-funded buyback fund, grew by the equivalent of only <!--n:buyback_change_pct_of_issuance:pct-->11.10%<!--/n--> of the NEAR minted over the same days. Since September 2026 a second, much larger counterweight has appeared, and it can be checked on-chain: regulated fund demand. Bitwise's NEAR ETF (NRR) holds <!--n:nrr_holdings_latest:m-->15.31M<!--/n--> NEAR in staked custody, equal to <!--n:nrr_holdings_pct_of_annual_issuance:pct-->46.87%<!--/n--> of a year's new NEAR, and since launch its custody grew <!--n:nrr_net_to_net_supply_x:1-->3.8<!--/n--> times as much as NEAR's total supply did. NRR is not alone: SVRN, a Nasdaq-listed company that holds NEAR as its treasury, reported more than 55.5 million NEAR on 27 Aug 2026, mostly staked. Our long-term case: **NEAR's investability now depends less on its buybacks and more on whether institutional demand (regulated funds and listed treasury companies), which can be checked from the chain, proves sticky and spreads.** The demand is real and large. It is not yet proven to stay: holdings are <!--n:change_since_peak_pct:spct-->-12.70%<!--/n--> from their peak.

## Verdict today: constructive, not proven

| What has to be true for the long-term case | How we measure it (daily, on the dashboard) | Reading now |
|---|---|---|
| 1. Fund demand is sticky, not a launch effect | NRR's net change over the last 30 days | <!--n:last30_nrr_net:int-->297,710<!--/n--> NEAR (<!--n:last30_nrr_net_pct_of_issuance:pct-->11.08%<!--/n--> of the NEAR minted in those 30 days); holdings <!--n:change_since_peak_pct:spct-->-12.70%<!--/n--> from the peak |
| 2. Fund flows stay larger than buyback flows | NRR custody moves against buyback-fund moves (sum of absolute daily moves on each side); the pre-registered prediction tests it for 14 Nov to 13 Dec | <!--n:last30_abs_custody_to_abs_buyback:1-->16.3<!--/n-->× over the last 30 days, <!--n:ratio_abs_custody_to_abs_buyback:x-->43×<!--/n--> since launch |
| 3. Institutional demand spreads beyond one product | Products whose holdings we rebuild from the chain and reconcile with the issuer; other holders we can only partly see | Rebuilt and reconciled: <!--n:products_attributed_onchain:int-->1<!--/n--> (NRR). Partly visible: SVRN (10.36M NEAR staked in its Bitwise pool on 14 Nov, against more than 55.5M reported). Not attributable: 21Shares, Grayscale |
| 4. Redeemed NEAR is not routed straight to exchanges | Redemptions traced past the custody hub (whether it was sold cannot be seen on-chain) | <!--n:redemption_traces_probable:int-->3<!--/n--> of <!--n:redemption_traces:int-->10<!--/n--> traceable, all to exchange-style wallets (probable links only) |
| 5. The protocol's own offset grows | Buyback-fund growth against NEAR minted | <!--n:last30_buyback_pct_of_issuance:pct-->11.27%<!--/n--> over the last 30 days, <!--n:buyback_change_pct_of_issuance:pct-->11.10%<!--/n--> since launch |

Current readings, not forecasts. As of <!--n:data_through:-->2026-11-13<!--/n-->: condition 2 currently holds (the frozen prediction that tests it is pending until 13 Dec); condition 1 is undecided (over the last 30 days NRR's net inflow was <!--n:last30_nrr_net_pct_of_issuance:pct-->11.08%<!--/n--> of new supply, about the same as the buyback fund's <!--n:last30_buyback_pct_of_issuance:pct-->11.27%<!--/n-->, while holdings are still below their peak); conditions 3 to 5 are open. Hence constructive, not proven.

## The claim we tested

Issuer-data trackers already report NRR's holdings and daily flows (for example CryptoKeyhole and SoSoValue) by copying Bitwise's own files. This project does something different: it rebuilds the holdings independently from NEAR's chain, account by account and transaction by transaction, checks the result against Bitwise's figures, and sets it against NEAR's supply.

A third flow is now larger than the buyback fund and visible on-chain: NEAR moving into and out of the staked custody of Bitwise's NRR ETF. We rebuild that custody daily from the chain, it matches Bitwise's own published figures, and since NRR launched its custody moves have been about <!--n:ratio_abs_custody_to_abs_buyback:x-->43×<!--/n--> the buyback fund's movement, in both directions.

This is a claim about the **size and reversibility of custody movements**, not about market buying or selling. NEAR moving into a fund's staked custody is out of liquid circulation while it stays there; it is not removed from supply.

## Evidence

1. **The reconstruction matches the issuer.** On every date Bitwise has published (<!--n:issuer_gaps_count:int-->3<!--/n--> so far), its "NEAR in Trust" and the NEAR staked by the attributed accounts at the end of that day differ by at most <!--n:max_abs_issuer_gap_pct:pct-->0.15%<!--/n-->.
2. **Every account is attributed by a rule with evidence.** <!--n:attributed_accounts:int-->73<!--/n--> accounts received principal from one custody hub and then, strictly afterwards, called `deposit_and_stake` (funding and staking transactions stored per account in `data/out/accounts.csv`). Basket sizes repeat, consistent with ETF creation units.
3. **Nothing was missed.** An independent Google BigQuery query, starting from every account the hub ever sent a transaction to, finds exactly the same 94 transactions into and out of the pool as our pipeline, hash for hash (test 19).
4. **Every movement is a transaction, checked as a sequence.** <!--n:creations_confirmed_count:int-->74<!--/n--> of <!--n:creations_count:int-->74<!--/n--> creations (hub funding, then stake) and <!--n:redemptions_confirmed_count:int-->7<!--/n--> of <!--n:redemptions_count:int-->10<!--/n--> redemptions (unstake, withdraw, back to the hub) are complete sequences; the rest are recent and still settling.
5. **Supply is measured and checked.** NEAR minted per epoch is <!--n:issuance_ratio_median_pct:pct-->99.85%<!--/n--> of the protocol formula's maximum at the median; staking rewards are measured from the pool's share price (<!--n:reward_rate_annualised_pct:pct-->4.62%<!--/n--> a year), and NRR's holdings are explained to within <!--n:unexplained_total:int-->369<!--/n--> NEAR over the window.

Over the window: the protocol minted <!--n:gross_issuance_total:int-->4,116,853<!--/n--> NEAR, about <!--n:burn_residual_total:int-->45,427<!--/n--> NEAR was burned, the buyback fund's balance changed by <!--n:buyback_fund_change_total:int-->457,016<!--/n--> NEAR, and NRR moved <!--n:creations_total:int-->17,544,103<!--/n--> NEAR into staked custody and <!--n:redemptions_total:int-->2,318,791<!--/n--> out. NRR's accounts hold <!--n:nrr_share_staked_pct_latest:pct-->2.59%<!--/n--> of all staked NEAR, in one validator pool.

## Evidence against, and alternative explanations

- **Launch effect.** One product, about <!--n:days:int-->46<!--/n--> days, starting at launch. The inflow may be a one-off; holdings are already <!--n:change_since_peak_pct:spct-->-12.70%<!--/n--> from the peak.
- **In-kind mechanics.** Bitwise's prospectus (24 Sep 2026) allows creations in cash or in NEAR, and redemptions in kind or for cash, in baskets of 10,000 shares, through pre-approved authorised participants only. NEAR arriving from exchange-style wallets may be existing inventory, not fresh buying; NEAR leaving to them may be delivered to a redeeming party, not sold.
- **Exchange inventory is not a sale.** Exchange-internal trades are not on-chain.
- **Size is not price impact.** Larger custody moves than buyback moves say nothing by themselves about which moves the price.
- **Buybacks are measured as a balance.** We do not trace executed purchases; the fund's tokens are held, not burned.
- **Staking costs.** The prospectus sets staking expenses at 33% of rewards, so NRR keeps about 67% of what its NEAR earns; our reward figure is the pool's gross rate.
- **Concentration cuts both ways.** <!--n:nrr_share_staked_pct_latest:pct-->2.59%<!--/n--> of all stake in one pool makes NRR's demand easy to audit, and its exits large.

## What the chain cannot prove

Legal ownership of the accounts; cash vs in-kind; whether redeemed NEAR was sold; executed buyback purchases; other products' holdings.

## Bull case

Institutional demand that anyone can audit from the chain becomes a standing source of NEAR demand several times larger than the protocol's buyback. If NRR's holdings stabilise and more products stake through identifiable pools, a large share of each year's new NEAR sits in long-term staked custody, and NEAR's float can be tracked with evidence rather than press releases.

## Bear case

The same demand reverses on a few days' notice, is concentrated in one pool, and has already fallen <!--n:change_since_peak_pct:spct-->-12.70%<!--/n--> from its peak. Redeemed NEAR that we can trace went to exchange-style wallets. If fund demand fades, the protocol's own offset covers only about <!--n:buyback_change_pct_of_issuance:pct-->11.10%<!--/n--> of new supply, and dilution is back to being the story.

## Prediction (pre-registered)

See [PREDICTION.md](PREDICTION.md) (frozen 13 Nov 2026, SHA-256 and OpenTimestamps proof in `PREDICTION.lock`): from 14 Nov to 13 Dec 2026, NRR's absolute custody moves will exceed the buyback fund's absolute balance moves. It is the first test of condition 2 and resolves after judging; it is here so the thesis can fail.

## What would change our mind

- The prediction failing: NRR custody moves below buyback-fund moves for 30 days (condition 2 fails).
- NRR's 30-day net change staying negative for two consecutive months (condition 1 fails).
- Issuer figures diverging from the chain reconstruction by more than 1%.
- Evidence that the attributed accounts serve another product.

## Other institutional NEAR holders (context; only partly attributed on-chain)

- SVRN, Inc. (Nasdaq: SVRN): reported more than 55.5 million NEAR on 27 Aug 2026, with institutional staking and qualified custody (press release, SEC exhibit). On-chain, its Bitwise pool `svrn_bitwise.poolv1.near` held 10.36M NEAR staked at block 224,459,746 (14 Nov 2026), almost all by one account; the rest is staked elsewhere and not attributed here.

- 21Shares NEAR Protocol Staking ETP: €9.8M assets as of 24 Sep 2026 (Trackinsight). Custodians Coinbase Custody and Copper (21Shares product page).
- Grayscale NEAR Trust (GSNR): staking not permitted at the time of its S-1 filing; holdings not attributed here.

## Sources

Full register with dates and what each source establishes: [SOURCES.md](SOURCES.md). Main ones: NEAR archival RPC and FastNEAR (all chain data); Bitwise's NRR holdings page (issuer figures, 3 dated snapshots); Bitwise NEAR ETF prospectus, SEC Form 424B3 dated 24 Sep 2026 (custody, staking, creation and redemption); Google BigQuery public NEAR dataset (completeness check); SVRN press release of 27 Aug 2026 (SVRN holdings).
