# Pre-registered prediction

> **Status: DRAFT — awaiting the author's approval. Not yet frozen; no hash recorded.**

Frozen before the window opens. Its SHA-256 and the commit that added it are recorded below; any later edit changes the hash.

## Statement

From **2026-11-12 00:00 UTC** to **2026-12-11 23:59 UTC** (30 daily windows ending 2026-11-13 … 2026-12-12 in `data/out/daily.csv`), the sum of absolute daily **event-classified NRR custody moves** (`creations` + `redemptions`, staking rewards excluded) will be **greater than** the sum of absolute daily **buyback-fund balance changes** (`|buyback_fund_change|`), both measured in NEAR.

## Rules

- Data: the daily rows produced by this repository's pipeline (`make refresh`), unchanged definitions (METHOD.md as of the freezing commit).
- A window with a missing value on either side is excluded from **both** sums and counted. If more than 5 of the 30 windows are excluded, the prediction is **void**.
- This compares balances that moved, not purchases: custody moves are not proof of market buying or selling, and the buyback fund's balance is not executed buybacks.
- Evaluated by `make verify-prediction`, which prints both sums, the excluded windows and the verdict.

## What it would mean

- **Holds:** fund custody movements remain a larger driver of NEAR's liquid supply than the protocol's buyback fund, after the launch period.
- **Fails:** NRR's launch flows were a one-off; buyback-fund movements are the larger flow again, and the thesis's central claim weakens.
