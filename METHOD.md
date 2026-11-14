# Method

Chain data comes from NEAR mainnet through two public sources, cached (gzipped) in `data/raw/`. `make rebuild` reconstructs raw responses into `data/work/`, then builds the published outputs, documents and site offline. `make data` is the faster derived-data build from existing `data/work/` snapshots:

- NEAR archival RPC (`https://archival-rpc.mainnet.fastnear.com`): blocks, view calls, `view_account`, `validators`, `EXPERIMENTAL_protocol_config`.
- FastNEAR transaction API (`https://tx.main.fastnear.com/v0`): account transaction lists and transaction details with receipts and logs.

Plus the issuer's own figures from `https://nrretf.com/`, recorded with the retrieval time in `data/issuer_snapshots.csv`.

## 1. Daily heights

For each day from 25 Sep 2026, the first block at or after 00:00 UTC (`nfi/chain.py: daily_heights`). A day's row describes the state at that height; the flows in a row are the transactions between the previous day's height and this one (the row's "window").

## 2. Attribution (who is NRR)

- **Custody hub** `23ced4…684a`: funds every basket account and receives every redemption. Labelled "custody hub (inferred)", never "Bitwise's wallet".
- **Basket account, Rule A** (`nfi/attribution.py: apply_rule`): the inferred hub sent the account at least 1,000 NEAR, and **strictly after** that funding the account itself called `deposit_and_stake` on `bitwise_2.poolv1.near`. An account that staked before any direct hub funding, or never staked in this pool, is rejected and listed with the reason.
- **Evidence per account** (`data/out/accounts.csv`): funding transaction, height and amount; staking transaction, height and amount; delay in hours; amount difference. **Confidence** is "high" when the stake follows within 7 days and is within 1 NEAR of the direct funding, otherwise "medium". Rule A currently yields <!--n:attributed_accounts:int-->73<!--/n--> accounts, <!--n:attributed_high_confidence:int-->72<!--/n--> high.
- **One-hop sensitivity candidate (excluded from Rule A and all NRR headline totals):** the audit identified account `9a00031933695207a60a3af95cfaaadcea863812ecbc30400c109417dadf21b3`. The reported path is a 52,192.07 NEAR transfer from directly hub-funded account `432766610e6d7069916d5207202505f46244539b905bb73e66e7ff3094e7b4c5`, followed by a 52,192.02 NEAR `deposit_and_stake` into the NRR pool. This is a candidate for a separate medium-confidence Rule B, not a legal ownership finding. It stays excluded until the intermediate transfer, timing and account history are independently reproduced and added to tests. The audit's reported 52,502 NEAR sensitivity must not be mixed into the primary series.
- **Other Bitwise pools excluded:** delegators of `bitwise_1.poolv1.near` and `svrn_bitwise.poolv1.near` at the latest height are read and checked; none is in the Rule A set (test 14).
- Other delegators of the NRR pool (e.g. `meta-pool.near`) are excluded and reported separately (`pool_other_delegators`).
- **Issuer check:** Bitwise's "NEAR in Trust as of T" is compared with the NEAR staked by Rule A accounts at 00:00 UTC on T+1, i.e. the end of day T (test 1, tolerance 0.5%; largest gap <!--n:max_abs_issuer_gap_pct:pct-->0.15%<!--/n--> on <!--n:issuer_gaps_count:int-->4<!--/n--> archived dates). The comparison rule is based on the issuer's end-of-day holdings and the observed removal of NEAR from "NEAR in Trust" when unstaked for redemption, before the withdrawal reaches the chain. These dates are historical source snapshots, not daily issuer confirmation. **How the rule was set:** it was fixed on 13 Nov 2026 (commit `3673e632`) after the first three Bitwise figures, so those three were used to choose it and are not independent tests; the earlier same-day rule gave gaps of 0.45%, 0.18% and 2.2%. Bitwise's figure for 12 Nov, published after that commit and archived in `data/issuer_evidence/2026-11-12_nrretf.txt`, is the first out-of-sample test: gap <!--n:issuer_gap_oos_pct:spct-->-0.15%<!--/n-->. The rule will not be changed again; every later figure is another out-of-sample test.
- **Attribution boundary:** the current raw cache includes the inferred hub's history and the NRR pool's history. That is sufficient for Rule A evidence, but it is not an exhaustive crawl of all descendants of every hub recipient. The one-hop candidate above is disclosed separately. A broader candidate screen is prepared in `data/bigquery/completeness_onehop_candidates.sql`; it joins direct hub recipients to successful native `TRANSFER` actions and finds later NRR pool calls by the recipients. It returns the funding action arguments, but the amount and block ordering still require independent inspection. It is not a validation result or permission to change attribution.

Other inputs include the hub and pool histories, plus explicitly configured auxiliary accounts used by the trace logic. Rule A is a repeatable transaction-pattern attribution, not proof of legal or beneficial ownership.

**Other institutional holders (context, separate from NRR).** SVRN, Inc. reports its NEAR treasury itself (more than 55.5 million NEAR on 27 Aug 2026). The only part with a known on-chain link is Bitwise's `svrn_bitwise.poolv1.near` pool, whose delegators we read at the latest daily height (`nfi/institutional.py`; now <!--n:svrn_observed_staked:int-->10,358,783<!--/n--> NEAR across <!--n:svrn_accounts_observed:int-->6<!--/n--> accounts at block <!--n:svrn_observed_height:int-->224,285,093<!--/n-->). It is published in `data/out/institutional_holders.csv` with its own date, height and status ("partial observation"). It is never included in NRR's totals (test 20 checks there is no account overlap), never reconciled with SVRN's figure, and never added to it, since it may be part of it. The NRR exclusion check above still reads this pool, only to keep its delegators out of NRR.

## 3. Custody layers (never double counted)

| Layer | Definition | Read with |
|---|---|---|
| L1 staked | staked balance of attributed accounts | pool `get_accounts` |
| L2 unstaked | unstaked, waiting to be withdrawn | pool `get_accounts` |
| L3 basket liquid | NEAR sitting in attributed accounts outside the pool | `view_account` |
| L4 hub liquid | NEAR in the custody hub | `view_account` |

L1 is the figure compared with the issuer and the solid line on the dashboard. `nrr_holdings` = L1 + L2 (NRR's NEAR in the pool, including NEAR unstaked for redemptions until it is withdrawn). `nrr_custody_extended` = L1 + L2 + L3 (dashed line). `nrr_custody_total` adds L4, the hub's liquid NEAR, which is published but not presented as fund-owned.

## 4. Events and sequences

Observed events, from each attributed account's transactions: `creation_stake` (`deposit_and_stake` only; amount = attached deposit), `pool_deposit_only` (`deposit` without staking: reported as other activity, not as a creation), `unstake` (amount from the pool's log line), `redemption_withdraw` (amount = the pool's transfer receipt to the account), `return_to_hub` / `transfer_out`, `funded_by_hub`, and `failed` (kept, never counted).

Each creation and redemption is then validated as a sequence (`validate_sequences`):

- **Creation, confirmed:** an earlier hub funding to the same account, within 7 days, that covers the staked amount (a funding can back several stakes; each stake uses up part of it).
- **Redemption, confirmed:** an earlier `unstake`, then the `withdraw`, then the same amount (±1 NEAR) back at the custody hub within 7 days, directly or through one intermediate account.
- Anything else is **partially observed**, with the reason.

`creations` / `redemptions` in `daily.csv` are all pool movements of attributed accounts (needed to reconcile holdings); `creations_confirmed` / `redemptions_confirmed` are the confirmed subset. Now: <!--n:creations_confirmed_count:int-->74<!--/n--> of <!--n:creations_count:int-->74<!--/n--> creations and <!--n:redemptions_confirmed_count:int-->7<!--/n--> of <!--n:redemptions_count:int-->10<!--/n--> redemptions are confirmed sequences.

**Direct-recipient completeness check, run outside this pipeline:** the saved Google BigQuery query (`data/bigquery/completeness.sql`) starts from direct recipients of the inferred custody hub and lists their transactions to the NRR pool before 13 Nov 2026 00:00 UTC. The captured result contains the same pool-transaction hash set as the pipeline for that direct-recipient population, with matching hashes by method (`data/bigquery/completeness_result.json`). Test 19 checks the captured result against the expected hashes; it does not execute BigQuery. This check supports completeness **within the direct-recipient population only**. It does not examine one-hop descendants and cannot support a claim that no downstream account was missed.

## 5. Staking rewards (measured independently)

For each window, the reward probes are pool delegators with ≥ 1,000 NEAR staked, **no transaction of their own to the pool in the window** (from the pool's full history) and an unchanged unstaked balance. A staking pool pays every delegator through one share price, so every probe should grow at the same rate: the 25th and 75th percentiles of the probes' daily rate are identical to six decimals on every day (test 17). Median probes per day: <!--n:reward_probes_median:int-->66<!--/n-->. `nrr_rewards` = that rate × the previous day's L1 (a 10% trimmed mean gives <!--n:rewards_total_trimmed_mean:int-->84,844<!--/n--> NEAR against <!--n:rewards_total:int-->84,844<!--/n-->). `unexplained` = Δ`nrr_holdings` − custody flow − `nrr_rewards`; published, never relabelled (<!--n:unexplained_total:int-->369<!--/n--> NEAR net, <!--n:unexplained_abs_total:int-->527<!--/n--> NEAR absolute over the window). Annualised rate: <!--n:reward_rate_annualised_pct:pct-->4.62%<!--/n-->.

## 6. Supply

- `total_supply`: block header at each daily height.
- Epoch boundaries: found exactly by searching for the height where `epoch_id` changes, <!--n:epochs:int-->168<!--/n--> epochs.
- `gross_issuance` (minted): the jump in `total_supply` across each epoch's first block, summed per window. This includes the burn of that single block, which is negligible.
- **Independent check of minting** (`data/out/issuance_check.csv`, test 12): the protocol's own configuration (`max_inflation_rate` 1/40, `protocol_reward_rate` 0) caps each epoch's mint at total supply × 2.5% × epoch duration / 31,536,000 s. Measured mint is <!--n:issuance_ratio_median_pct:pct-->99.85%<!--/n--> of that cap at the median (<!--n:issuance_ratio_min_pct:pct-->95.02%<!--/n-->–<!--n:issuance_ratio_max_pct:pct-->99.95%<!--/n--> over <!--n:issuance_epochs_checked:int-->167<!--/n--> epochs); the shortfall is the reward withheld from validators that missed blocks.
- `net_supply_change`: Δ`total_supply` between daily heights. `burn_residual` = `gross_issuance` − `net_supply_change`. It is a residual, not an independent measurement of fee burns; the identity test (6) only guards against a negative residual.
- `total_staked`: sum of `locked` balances of every validator seen in the period, at each daily height. Checked against the `validators` RPC (sum of the epoch's current stakes) on every day: locked is never below the epoch's stake, and was within 1% on <!--n:staked_check_within_1pct:int-->44<!--/n--> of <!--n:staked_check_days:int-->50<!--/n--> days (median gap <!--n:staked_check_median_gap_pct:pct-->0.31%<!--/n-->). The larger gaps (up to <!--n:staked_check_max_gap_pct:pct-->6.03%<!--/n--> on <!--n:staked_check_max_gap_date:-->2026-10-15<!--/n-->) are days when a validator was kicked out of the epoch or new stake had not yet become active: that NEAR stays locked but is not in the epoch's validator stake.

## 7. Buyback fund (a balance, not purchases)

`buyback_fund` = native NEAR + wNEAR held inside `intents.near` (`mt_balance_of`, token `nep141:wrap.near`) of `buybacks.multisignature.near` and `1csfundsadmin.sputnik-dao.near`. Definition follows nikolaskahris-png/near-thesis-data. `fefundsadmin.sputnik-dao.near` is excluded: on revenue.near.org it is the front-end revenue account, not a buyback wallet.

`data/out/buyback_ledger.csv` gives every daily change by account and token (opening, closing, change, status); the lines add up to the daily `buyback_fund_change` (test 16). Not measured: which transactions caused each change (wNEAR moves inside the Intents contract are not account transactions) and whether any change was an executed market purchase.

## 8. Traces and labels

A redemption trace shows the observed steps (`unstake` → `withdraw` → return to the hub), then looks for the hub outflow that carried the NEAR on:

- **probable**: exactly one hub outflow within 72 h matches the returned amount (±2%), or, failing that, the sum of that day's returns;
- **ambiguous**: several outflows match, so none is shown as the next hop;
- **unmatched**: none matches; the hub's next outflow is shown as context only.

A link past the hub is never called confirmed: the hub pools fungible NEAR. Now: <!--n:redemption_traces_probable:int-->3<!--/n--> of <!--n:redemption_traces:int-->10<!--/n--> redemption traces are probable beyond the hub.

Labels: "exchange-style wallet" needs both ≥ 10,000 transactions (FastNEAR count) and ≥ 100 distinct counterparties among its 200 most recent transactions; an account meeting only the first is "high-activity account". A heuristic, not an identification.

## 9. Missing data

Every lookup has a state. An account that did not exist yet at a height is a true zero. Any other failed or malformed answer (timeout, error, a pool page that could not be read, a wNEAR balance that could not be read) is **missing**: blank in CSV, `null` in JSON, never 0. A day with a missing core value gets `data_status = incomplete: <fields>` and no derived changes; the dashboard shows it. Days with missing data now: <!--n:incomplete_days:int-->0<!--/n-->. Test 13 feeds failing responses through the collectors to check this.

## 10. Refresh

`make refresh` extends the daily heights to today and re-collects. Cached responses are reused; the last, partial page of each transaction history is always re-fetched so new transactions are seen. The refresh time is written to `data/work/refresh.json` and shown on the dashboard, which warns when data is more than two days old.

## 11. Signed net flow, periods and comparison units

- **Daily signed NRR net custody flow:** `creations - redemptions` for each daily window. It excludes staking rewards and does not infer a market purchase or sale.
- **Cumulative net custody flow:** sum of signed daily NRR net custody flow within the selected period.
- **Average per day:** cumulative signed net custody flow divided by the count of complete daily windows in that period. The launch-period, post-peak and latest-30-day windows are calculated separately; their cumulative totals must not be labelled as per-day rates.
- **Post-peak period:** starts with the first daily window after the recorded holdings peak date. The peak-date row itself is not counted as a post-peak flow window.
- **Basket equivalent:** one basket is 10,000 shares per the prospectus. The NEAR conversion is `10,000 × NEAR_per_share` from the latest included Bitwise issuer snapshot. NEAR/day divided by this amount gives approximate baskets/day; it is a scale unit only.
- **Issuance comparison:** gross issuance is measured per daily window at epoch boundaries. It is compared with NRR net custody flow using the same NEAR/day unit and same selected window.
- **Buyback comparison:** the balance change in native NEAR and wNEAR held in the defined buyback-fund accounts. It is not executed purchases or market demand. The balance-change series is plotted as its own measurement, not described as a purchase flow.
- **HSP-029 scenario:** the full 1.6% target is modelled by scaling the measured 2.5% issuance rate by `1.6 / 2.5`. It is a full-target scenario, not the active protocol rate in the current observations; implementation requires remaining governance/implementation steps, the grace period and validator adoption.
- **USD display:** cumulative NEAR series are multiplied by the latest archived issuer NAV divided by NEAR per share. This is a dated USD-equivalent conversion, not a live spot-price series.
- **Missing windows:** the chart excludes incomplete rows from all three series and labels the selected range. The published pipeline currently reports zero incomplete days.

## 12. Tests (`make test`)

1 issuer reconciliation · 2 balances re-read from raw RPC responses · 3 no duplicate accounts · 4 every event backed by its transaction and amount · 5 reward rate 3–7%/yr and residual small · 6 block-header match and no negative burn residual · 7 total stake vs validators RPC · 8 missing ≠ zero in outputs · 9 offline rebuild is byte-identical · 10 every number in the docs comes from the data · 11 attribution rejects staking before funding · 12 minting vs the protocol formula · 13 failed lookups become missing, not zero · 14 other Bitwise pools excluded · 15 sequence statuses and links · 16 buyback ledger adds up · 17 reward probes agree · 18 prediction evaluator (pending, void, duplicates) · 19 direct-recipient BigQuery hash comparison (against the captured result) · 20 SVRN observation kept separate from NRR · 21 signed-flow summary and basket-rate calculations.
