# Thesis: NEAR's largest measurable movements of supply now come from a fund, not the protocol

**Project:** NEAR Flow Intelligence · **Track:** Investment Thesis · **Data through:** <!--n:data_through:-->2026-11-13<!--/n-->

## Claim

Investors model NEAR's dilution with two protocol numbers: issuance and the Intents-funded buyback fund. A third flow is now larger than the buyback fund and visible on-chain: NEAR moving into and out of the staked custody of Bitwise's NRR ETF. We rebuild that custody daily from the chain, it matches Bitwise's own published figures, and since NRR launched its custody moves have been about <!--n:ratio_abs_custody_to_abs_buyback:x-->43×<!--/n--> the buyback fund's movement, in both directions.

This is a claim about **size and reversibility of custody movements**, not about market buying or selling.

## Why it matters to a NEAR holder

- **Dilution math is incomplete without it.** Over the window the protocol minted <!--n:gross_issuance_total:int-->4,116,853<!--/n--> NEAR and the buyback fund's balance changed by <!--n:buyback_fund_change_total:int-->457,016<!--/n--> NEAR. NRR moved <!--n:creations_total:int-->17,544,103<!--/n--> NEAR into staked custody and <!--n:redemptions_total:int-->2,318,791<!--/n--> out.
- **It reverses.** NRR's holdings peaked at <!--n:nrr_peak:int-->17,537,598<!--/n--> NEAR on <!--n:nrr_peak_date:-->2026-10-28<!--/n--> and are <!--n:change_since_peak_pct:spct-->-12.70%<!--/n--> from that peak. Redeemed NEAR leaves staking. <!--n:redemption_traces_probable:int-->3<!--/n--> of <!--n:redemption_traces:int-->10<!--/n--> redemptions can be followed past the custody hub with a probable link (the only matching outflow within 72 hours), and in those cases the NEAR went on to high-activity wallets that look like exchanges (heuristic). The hub pools NEAR, so no link beyond it is certain.
- **It concentrates stake.** NRR's accounts hold <!--n:nrr_share_staked_pct_latest:pct-->2.59%<!--/n--> of all staked NEAR, in one validator pool.

## Evidence

1. **The reconstruction matches the issuer.** Largest gap to Bitwise's "NEAR in Trust" on the dates it published: <!--n:max_abs_issuer_gap_pct:pct-->0.15%<!--/n-->.
2. **Every account is attributed by a rule with evidence.** <!--n:attributed_accounts:int-->73<!--/n--> accounts received principal from one custody hub and then called `deposit_and_stake` (funding and staking transactions stored per account in `data/out/accounts.csv`). Basket sizes repeat, consistent with ETF creation units.
3. **Every movement is a transaction, checked as a sequence.** <!--n:events:int-->184<!--/n--> classified events (stake, unstake, withdraw, return to hub) with hashes and amounts read from actions, receipts and pool logs.
4. **Rewards are measured, not assumed.** Median growth of delegators with no transactions each day gives a staking rate of <!--n:reward_rate_annualised_pct:pct-->4.62%<!--/n--> a year; NRR rewards over the window total <!--n:rewards_total:int-->84,844<!--/n--> NEAR; the unexplained residual is <!--n:unexplained_total:int-->369<!--/n--> NEAR.
5. **Redemptions are traced, with stated confidence.** <!--n:redemption_traces:int-->10<!--/n--> redemptions followed from the pool to the custody hub; <!--n:redemption_traces_probable:int-->3<!--/n--> of them on to the next accounts with a probable link, the rest stop at the hub.

## Evidence against, and alternative explanations

- **Launch effect.** One product, about <!--n:days:int-->46<!--/n--> days, starting at launch. The inflow may be a one-off.
- **In-kind mechanics.** Bitwise's prospectus allows NEAR or cash creations and redemptions. NEAR arriving from exchange-style wallets may be existing inventory, not fresh buying; NEAR leaving to them may be delivered to a redeeming party, not sold.
- **Exchange inventory is not a sale.** Exchange-internal trades are not on-chain.
- **Size is not price impact.** Larger custody moves than buyback moves say nothing by themselves about which moves the price.
- **Buybacks are measured as a balance.** We do not trace executed purchases; the fund's tokens are held, not burned.

## What the chain cannot prove

Legal ownership of the accounts; cash vs in-kind; whether redeemed NEAR was sold; executed buyback purchases; other products' holdings.

## Bull case

Regulated demand that is visible and auditable from the chain is a new, verifiable source of NEAR demand that is many times larger than the protocol's own buyback programme. If more products launch and stake through identifiable pools, NEAR's float can be monitored with evidence rather than press releases.

## Bear case

The same demand is reversible on a few days' notice, concentrated in one pool, and has already reversed by <!--n:change_since_peak_pct:spct-->-12.70%<!--/n--> from its peak. A protocol that counts on buybacks to offset issuance is outweighed by fund flows it does not control.

## Prediction (pre-registered)

See [PREDICTION.md](PREDICTION.md): over the 30 days after submission, NRR's absolute custody moves will exceed the buyback fund's absolute balance moves. It resolves after judging; it is here so the thesis can fail.

## What would change our mind

- NRR custody moves falling below buyback-fund moves for 30 days (the prediction failing).
- Issuer figures diverging from the chain reconstruction by more than 1%.
- Evidence that the attributed accounts serve another product.

## Other NEAR investment products (context, not attributed on-chain)

- 21Shares NEAR Protocol Staking ETP: €9.8M assets as of 24 Sep 2026 (Trackinsight). Custodians Coinbase Custody and Copper (21Shares product page).
- Grayscale NEAR Trust (GSNR): staking not permitted at the time of its S-1 filing; holdings not attributed here.
