# Method

All data comes from NEAR mainnet through two public sources, cached (gzipped) in `data/raw/` so that `make data` rebuilds everything offline:

- NEAR archival RPC (`https://archival-rpc.mainnet.fastnear.com`): blocks, view calls, `view_account`, `validators`, `EXPERIMENTAL_protocol_config`.
- FastNEAR transaction API (`https://tx.main.fastnear.com/v0`): account transaction lists and transaction details with receipts and logs.

Plus the issuer's own figures from `https://nrretf.com/`, recorded with the retrieval time in `data/issuer_snapshots.csv`.

## 1. Daily heights

For each day from 25 Sep 2026, the first block at or after 00:00 UTC (`nfi/chain.py: daily_heights`). A day's row describes the state at that height; the flows in a row are the transactions between the previous day's height and this one (the row's "window").

## 2. Attribution (who is NRR)

- **Custody hub** `23ced4…684a`: funds every basket account and receives every redemption. Labelled "custody hub (inferred)", never "Bitwise's wallet".
- **Basket account, rule A** (`nfi/attribution.py: apply_rule`): the hub sent the account at least 1,000 NEAR, and **strictly after** that funding the account itself called `deposit_and_stake` on `bitwise_2.poolv1.near`. An account that staked before any hub funding, or never staked in this pool, is rejected and listed with the reason.
- **Evidence per account** (`data/out/accounts.csv`): funding transaction, height and amount; staking transaction, height and amount; delay in hours; amount difference. **Confidence** is "high" when the stake follows within 7 days and is within 1 NEAR of the funding, otherwise "medium". Result: <!--n:attributed_accounts:int-->73<!--/n--> accounts, <!--n:attributed_high_confidence:int-->72<!--/n--> high. The medium one received more than it staked (the rest was forwarded).
- **Other Bitwise products excluded:** delegators of `bitwise_1.poolv1.near` and `svrn_bitwise.poolv1.near` at the latest height are read and checked: none is an attributed account (test 14).
- Other delegators of the NRR pool (e.g. `meta-pool.near`) are excluded and reported separately (`pool_other_delegators`).
- Check: the reconstruction is compared with Bitwise's "NEAR in Trust" on each published date (test 1, tolerance 1%; largest gap <!--n:max_abs_issuer_gap_pct:pct-->0.45%<!--/n-->).

Sources: the hub's full transaction history and the pool's full transaction history (every stake, unstake and withdraw is a transaction to the pool; every funding and return passes through the hub), plus the histories of the two accounts seen downstream of the hub.

## 3. Custody layers (never double counted)

| Layer | Definition | Read with |
|---|---|---|
| L1 staked | staked balance of attributed accounts | pool `get_accounts` |
| L2 unstaked | unstaked, waiting to be withdrawn | pool `get_accounts` |
| L3 basket liquid | NEAR sitting in attributed accounts outside the pool | `view_account` |
| L4 hub liquid | NEAR in the custody hub | `view_account` |

`nrr_holdings` = L1 + L2: the figure compared with the issuer, and the solid line on the dashboard. `nrr_custody_extended` = L1 + L2 + L3 (dashed line). `nrr_custody_total` adds L4, the hub's liquid NEAR, which is published but not presented as fund-owned.

## 4. Events and sequences

Observed events, from each attributed account's transactions: `creation_stake` (`deposit_and_stake` only; amount = attached deposit), `pool_deposit_only` (`deposit` without staking: reported as other activity, not as a creation), `unstake` (amount from the pool's log line), `redemption_withdraw` (amount = the pool's transfer receipt to the account), `return_to_hub` / `transfer_out`, `funded_by_hub`, and `failed` (kept, never counted).

Each creation and redemption is then validated as a sequence (`validate_sequences`):

- **Creation, confirmed:** an earlier hub funding to the same account, within 7 days, that covers the staked amount (a funding can back several stakes; each stake uses up part of it).
- **Redemption, confirmed:** an earlier `unstake`, then the `withdraw`, then the same amount (±1 NEAR) back at the custody hub within 7 days, directly or through one intermediate account.
- Anything else is **partially observed**, with the reason.

`creations` / `redemptions` in `daily.csv` are all pool movements of attributed accounts (needed to reconcile holdings); `creations_confirmed` / `redemptions_confirmed` are the confirmed subset. Now: <!--n:creations_confirmed_count:int-->74<!--/n--> of <!--n:creations_count:int-->74<!--/n--> creations and <!--n:redemptions_confirmed_count:int-->7<!--/n--> of <!--n:redemptions_count:int-->7<!--/n--> redemptions are confirmed sequences.

## 5. Staking rewards (measured independently)

For each window, the reward probes are pool delegators with ≥ 1,000 NEAR staked, **no transaction of their own to the pool in the window** (from the pool's full history) and an unchanged unstaked balance. A staking pool pays every delegator through one share price, so every probe should grow at the same rate: the 25th and 75th percentiles of the probes' daily rate are identical to six decimals on every day (test 17). Median probes per day: <!--n:reward_probes_median:int-->65<!--/n-->. `nrr_rewards` = that rate × the previous day's L1 (a 10% trimmed mean gives <!--n:rewards_total_trimmed_mean:int-->82,415<!--/n--> NEAR against <!--n:rewards_total:int-->82,415<!--/n-->). `unexplained` = Δ`nrr_holdings` − custody flow − `nrr_rewards`; published, never relabelled (<!--n:unexplained_total:int-->369<!--/n--> NEAR net, <!--n:unexplained_abs_total:int-->527<!--/n--> NEAR absolute over the window). Annualised rate: <!--n:reward_rate_annualised_pct:pct-->4.60%<!--/n-->.

## 6. Supply

- `total_supply`: block header at each daily height.
- Epoch boundaries: found exactly by searching for the height where `epoch_id` changes, <!--n:epochs:int-->165<!--/n--> epochs.
- `gross_issuance` (minted): the jump in `total_supply` across each epoch's first block, summed per window. This includes the burn of that single block, which is negligible.
- **Independent check of minting** (`data/out/issuance_check.csv`, test 12): the protocol's own configuration (`max_inflation_rate` 1/40, `protocol_reward_rate` 0) caps each epoch's mint at total supply × 2.5% × epoch duration / 31,536,000 s. Measured mint is <!--n:issuance_ratio_median_pct:pct-->99.85%<!--/n--> of that cap at the median (<!--n:issuance_ratio_min_pct:pct-->95.02%<!--/n-->–<!--n:issuance_ratio_max_pct:pct-->99.95%<!--/n--> over <!--n:issuance_epochs_checked:int-->164<!--/n--> epochs); the shortfall is the reward withheld from validators that missed blocks.
- `net_supply_change`: Δ`total_supply` between daily heights. `burn_residual` = `gross_issuance` − `net_supply_change`. It is a residual, not an independent measurement of fee burns; the identity test (6) only guards against a negative residual.
- `total_staked`: sum of `locked` balances of every validator seen in the period, at each daily height. Checked against the `validators` RPC (sum of the epoch's current stakes) on every day: locked is never below the epoch's stake, and was within 1% on <!--n:staked_check_within_1pct:int-->44<!--/n--> of <!--n:staked_check_days:int-->49<!--/n--> days (median gap <!--n:staked_check_median_gap_pct:pct-->0.31%<!--/n-->). The larger gaps (up to <!--n:staked_check_max_gap_pct:pct-->6.03%<!--/n--> on <!--n:staked_check_max_gap_date:-->2026-10-15<!--/n-->) are days when a validator was kicked out of the epoch or new stake had not yet become active: that NEAR stays locked but is not in the epoch's validator stake.

## 7. Buyback fund (a balance, not purchases)

`buyback_fund` = native NEAR + wNEAR held inside `intents.near` (`mt_balance_of`, token `nep141:wrap.near`) of `buybacks.multisignature.near` and `1csfundsadmin.sputnik-dao.near`. Definition follows nikolaskahris-png/near-thesis-data. `fefundsadmin.sputnik-dao.near` is excluded: on revenue.near.org it is the front-end revenue account, not a buyback wallet.

`data/out/buyback_ledger.csv` gives every daily change by account and token (opening, closing, change, status); the lines add up to the daily `buyback_fund_change` (test 16). Not measured: which transactions caused each change (wNEAR moves inside the Intents contract are not account transactions) and whether any change was an executed market purchase.

## 8. Traces and labels

A redemption trace shows the observed steps (`unstake` → `withdraw` → return to the hub), then looks for the hub outflow that carried the NEAR on:

- **probable**: exactly one hub outflow within 72 h matches the returned amount (±2%), or, failing that, the sum of that day's returns;
- **ambiguous**: several outflows match, so none is shown as the next hop;
- **unmatched**: none matches; the hub's next outflow is shown as context only.

A link past the hub is never called confirmed: the hub pools fungible NEAR. Now: <!--n:redemption_traces_probable:int-->3<!--/n--> of <!--n:redemption_traces:int-->7<!--/n--> redemption traces are probable beyond the hub.

Labels: "exchange-style wallet" needs both ≥ 10,000 transactions (FastNEAR count) and ≥ 100 distinct counterparties among its 200 most recent transactions; an account meeting only the first is "high-activity account". A heuristic, not an identification.

## 9. Missing data

Every lookup has a state. An account that did not exist yet at a height is a true zero. Any other failed or malformed answer (timeout, error, a pool page that could not be read, a wNEAR balance that could not be read) is **missing**: blank in CSV, `null` in JSON, never 0. A day with a missing core value gets `data_status = incomplete: <fields>` and no derived changes; the dashboard shows it. Days with missing data now: <!--n:incomplete_days:int-->0<!--/n-->. Test 13 feeds failing responses through the collectors to check this.

## 10. Refresh

`make refresh` extends the daily heights to today and re-collects. Cached responses are reused; the last, partial page of each transaction history is always re-fetched so new transactions are seen. The refresh time is written to `data/work/refresh.json` and shown on the dashboard, which warns when data is more than two days old.

## 11. Tests (`make test`)

1 issuer reconciliation · 2 balances re-read from raw RPC responses · 3 no duplicate accounts · 4 every event backed by its transaction and amount · 5 reward rate 3–7%/yr and residual small · 6 block-header match and no negative burn residual · 7 total stake vs validators RPC · 8 missing ≠ zero in outputs · 9 offline rebuild is byte-identical · 10 every number in the docs comes from the data · 11 attribution rejects staking before funding · 12 minting vs the protocol formula · 13 failed lookups become missing, not zero · 14 other Bitwise pools excluded · 15 sequence statuses and links · 16 buyback ledger adds up · 17 reward probes agree · 18 prediction evaluator (pending, void, duplicates).
