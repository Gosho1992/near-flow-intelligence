# Pre-registered prediction

Frozen on 2026-11-13, before its window opens. The SHA-256 of this file, the commit that added it and an OpenTimestamps proof are in `PREDICTION.lock` and `PREDICTION.md.ots`. Any later edit changes the hash.

## Statement

From **2026-11-14 00:00 UTC** to **2026-12-13 23:59 UTC** (30 daily windows, the rows dated 2026-11-15 … 2026-12-14 in `data/out/daily.csv`), the sum of absolute daily **NRR custody moves** (`creations` + `redemptions`: NEAR staked into and withdrawn from the NRR pool by attributed accounts; staking rewards excluded) will be **greater than** the sum of absolute daily **buyback-fund balance changes** (`|buyback_fund_change|`), both in NEAR.

## Rules

- Data: the daily rows produced by this repository's pipeline (`make refresh`), with the definitions in METHOD.md as of the freezing commit.
- A window whose row is not `data_status = complete`, or has a missing value on either side, is excluded from **both** sums and listed. If more than 5 of the 30 windows are excluded, the prediction is **void**.
- Duplicate dates make the evaluation fail rather than count twice.
- This compares balances that moved, not purchases: custody moves are not proof of market buying or selling, and the buyback fund's balance is not executed buybacks.
- Evaluated by `make verify-prediction`, which prints both sums, the excluded windows and the verdict (PENDING until all 30 rows exist).

## What it would mean

- **Holds:** NRR's custody moves stay larger than the buyback fund's balance moves after the launch period, so the ETF remains a flow that NEAR supply models should not leave out.
- **Fails:** NRR's launch flows were a one-off, the buyback fund's movements are the larger of the two again, and the thesis's central claim weakens.

## History

A draft dated the window from 2026-11-12. It was not frozen before that date, so the window was moved to start after the freeze. Nothing else changed.
