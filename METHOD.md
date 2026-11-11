# Method

All data comes from NEAR mainnet through two public sources, cached in `data/raw/` so that `make data` rebuilds everything offline:

- NEAR archival RPC (`https://archival-rpc.mainnet.fastnear.com`): blocks, view calls, `view_account`, `validators`.
- FastNEAR transaction API (`https://tx.main.fastnear.com/v0`): account transaction lists and transaction details with receipts and logs.

Plus the issuer's own figures from `https://nrretf.com/`, recorded with the retrieval time in `data/issuer_snapshots.csv`.

## 1. Daily heights

For each day from 25 Sep 2026, the first block at or after 00:00 UTC (`nfi/chain.py: daily_heights`). A day's row describes the state at that height; the flows in a row are the transactions between the previous day's height and this one (the row's "window").

## 2. Attribution (who is NRR)

- **Custody hub** `23ced4…684a`: funds every basket account and receives every redemption. Labelled "custody hub (inferred)", never "Bitwise's wallet".
- **Basket account, rule A:** received principal (> 1,000 NEAR) from the hub **and** later called `deposit_and_stake` on a staking pool. Evidence per account in `data/out/accounts.csv` (funding tx, staking tx, pool). Result: <!--n:attributed_accounts:int-->73<!--/n--> accounts, all in `bitwise_2.poolv1.near`.
- Other delegators of the same pool (e.g. `meta-pool.near`) are excluded and reported separately (`pool_other_delegators`).
- Check: the reconstruction is compared with Bitwise's "NEAR in Trust" on each published date (test 1, tolerance 1%; largest gap <!--n:max_abs_issuer_gap_pct:pct-->0.45%<!--/n-->).

Sources: the hub's full transaction history and the pool's full transaction history (every stake, unstake and withdraw is a transaction to the pool; every funding and return passes through the hub), plus the histories of the two accounts seen downstream of the hub.

## 3. Custody layers (never double counted)

| Layer | Definition | Read with |
|---|---|---|
| L1 staked | staked balance of attributed accounts | pool `get_accounts` |
| L2 unstaked | unstaked, waiting to be withdrawn | pool `get_accounts` |
| L3 basket liquid | NEAR sitting in attributed accounts outside the pool | `view_account` |
| L4 hub liquid | NEAR in the custody hub | `view_account` |

`nrr_holdings` = L1 + L2 (what matches the issuer). `nrr_custody_total` = L1 + L2 + L3 + L4 (NEAR in transit included). Both are published.

## 4. Events

From each attributed account's transactions: `creation_stake` (`deposit_and_stake`, amount = attached deposit), `unstake` (amount from the pool's log line), `redemption_withdraw` (amount = the pool's transfer receipt to the account), `return_to_hub` / `transfer_out` (transfers). `funded_by_hub` comes from the hub's transfers. Failed transactions are skipped. `creations` and `redemptions` in `daily.csv` are the sums of `creation_stake` and `redemption_withdraw` in each window.

## 5. Staking rewards (measured independently)

For each window: the median growth of staked balance among pool delegators with ≥ 1,000 NEAR staked, no transactions of their own in the window and unchanged unstaked balance. `nrr_rewards` = that rate × the previous day's L1. `unexplained` = Δ`nrr_holdings` − (creations − redemptions) − `nrr_rewards`; published, never relabelled. Annualised rate: <!--n:reward_rate_annualised_pct:pct-->4.62%<!--/n-->.

## 6. Supply

- `total_supply`: block header at each daily height.
- Epoch boundaries: found exactly by searching for the height where `epoch_id` changes (epochs are 43,200 heights, but skipped heights shift boundaries, so each one is searched).
- `gross_issuance` (minted): the jump in `total_supply` across each epoch's first block (minting happens once per epoch), summed per window. <!--n:epochs:int-->161<!--/n--> epochs.
- `net_supply_change`: Δ`total_supply` between daily heights. `burn` = `gross_issuance` − `net_supply_change` (fees burned inside epochs).
- `total_staked`: sum of `locked` balances of every validator seen in the period, at each daily height. Checked against the `validators` RPC (sum of the epoch's current stakes) on every day: locked is never below the epoch's stake, and was within 1% on <!--n:staked_check_within_1pct:int-->43<!--/n--> of <!--n:staked_check_days:int-->48<!--/n--> days (median gap <!--n:staked_check_median_gap_pct:pct-->0.31%<!--/n-->). The larger gaps (up to <!--n:staked_check_max_gap_pct:pct-->6.03%<!--/n--> on <!--n:staked_check_max_gap_date:-->2026-10-15<!--/n-->) are days when a validator was kicked out of the epoch or new stake had not yet become active: that NEAR stays locked but is not in the epoch's validator stake. We use locked balances because they count NEAR that is staked, whether or not its validator is active this epoch.

## 7. Buyback fund (a balance, not purchases)

`buyback_fund` = native NEAR + wNEAR held inside `intents.near` (`mt_balance_of`, token `nep141:wrap.near`) of `buybacks.multisignature.near` and `1csfundsadmin.sputnik-dao.near`. Definition follows nikolaskahris-png/near-thesis-data. `fefundsadmin.sputnik-dao.near` is excluded: on revenue.near.org it is the front-end revenue account, not a buyback wallet. Executed purchases and burns are not claimed; per the same sources, bought NEAR is held.

## 8. Traces and labels

A redemption trace follows: `unstake` → `redemption_withdraw` → `return_to_hub` → the hub's next transfer of a matching amount (±2%) → that account's next transfer. A creation trace shows `funded_by_hub` → `creation_stake`, with the hub's three preceding inflows as context (NEAR is fungible, so these are sources, not a one-to-one match). Labels: "exchange-style wallet" if the account has ≥ 10,000 transactions (FastNEAR count) — a heuristic, not an identification.

## 9. Missing data

A value that could not be read is blank in CSV and `null` in JSON, never 0. The first day has no changes.

## 10. Tests (`make test`)

1 issuer reconciliation · 2 balances re-read from raw RPC responses · 3 no duplicate accounts · 4 every event backed by its transaction and amount · 5 reward rate 3–7%/yr and residual small · 6 supply identity and block-header match, issuance ≤ cap · 7 total stake vs validators RPC · 8 missing ≠ zero · 9 offline rebuild is byte-identical · 10 every number in the docs comes from the data.
