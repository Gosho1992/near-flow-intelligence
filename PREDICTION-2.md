# Pre-registered prediction 2: net against net

Frozen on 2026-11-14, before its window opens. The SHA-256 of this file, the commit that froze it and an OpenTimestamps proof are in `PREDICTION-2.lock` and `PREDICTION-2.md.ots`. Any later edit changes the hash. Prediction 1 (`PREDICTION.md`) is unchanged and is evaluated separately.

## Why a second prediction

Prediction 1 compares gross movement on both sides. It holds whenever NRR moves a lot in either direction, so it barely tests the thesis. This one compares **net against net**: is the ETF's net custody flow, in either direction, still larger than the protocol buyback fund's net balance change? Over the 30 daily windows before this freeze the two were almost equal (about +297,700 NEAR against +302,800 NEAR), so it can genuinely fail.

## Statement

From **2026-11-15 00:00 UTC** to **2026-12-14 23:59 UTC** (30 daily windows, the rows dated 2026-11-16 … 2026-12-15 in `data/out/daily.csv`), the **absolute value of NRR's net custody flow**, |Σ (`creations` − `redemptions`)|, will be **greater than** the **absolute value of the buyback fund's net balance change**, |Σ `buyback_fund_change`|, both in NEAR.

## Rules

- Data: the daily rows produced by this repository's pipeline (`make refresh`), with the definitions in METHOD.md as of the freezing commit. Staking rewards are excluded from NRR's net flow.
- A window whose row is not `data_status = complete`, or has a missing value on either side, is excluded from **both** sums and listed. If more than 5 of the 30 windows are excluded, the prediction is **void**.
- Duplicate dates make the evaluation fail rather than count twice.
- Custody moves are not purchases or sales, and the buyback fund's balance is not executed buybacks.
- Evaluated by `make verify-prediction` (`nfi/prediction2.py`), which prints both sums, the excluded windows and the verdict (PENDING until all 30 rows exist).

## What it would mean

- **Holds:** the ETF's net flow, whichever way it runs, is still a bigger force on NEAR's float than the protocol's own buyback fund. This supports the long-term thesis that regulated-product flow, not buybacks, sets the marginal supply picture.
- **Fails:** NRR's flows netted out to less than the buyback fund's growth. The ETF has stopped being the swing factor for now, and the thesis weakens.
