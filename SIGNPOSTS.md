# Long-term signposts (frozen)

**Frozen:** 14 Nov 2026, before the first window opens at 15 Nov 2026 00:00 UTC. This file is protected by `SIGNPOSTS.lock` (SHA-256, the commit that froze it) and an OpenTimestamps proof. It is never edited. If a rule ever needs to change, a new file with a new name and hash replaces it, and this one stays in the repository with its record.

**Evaluator:** `nfi/signposts.py`, run by `make verify-prediction` and on every daily refresh. Output: `data/out/signposts.json`.

## The quantity

For each window, from `data/out/daily.csv`:

- **Absorption ratio** a = Σ(creations − redemptions) ÷ Σ gross_issuance. Wrapper net custody flow divided by NEAR minted in the same window.
- **Buyback ratio** b = Σ buyback_fund_change ÷ Σ gross_issuance. Growth of the buyback fund's balance divided by NEAR minted in the same window.

a = +1 means the wrapper took in as much NEAR as the protocol minted. a = −1 means it released as much again. Both thresholds are break-evens against new supply, not numbers chosen to fit the data. Because the denominator is measured issuance, any change in the inflation cap (HSP-029) enters the ratio automatically, with no assumption about when it starts.

## Windows

Non-overlapping 30-day windows. Window k covers the 30 daily rows starting at row 2026-11-16 + 30(k − 1). A row dated T covers the day ending at T 00:00 UTC.

| Window | Activity covered (UTC) | Rows |
|---|---|---|
| 1 | 15 Nov – 14 Dec 2026 | 2026-11-16 – 2026-12-15 |
| 2 | 15 Dec 2026 – 13 Jan 2027 | 2026-12-16 – 2027-01-14 |
| 3 | 14 Jan – 12 Feb 2027 | 2027-01-15 – 2027-02-13 |
| 4 | 13 Feb – 14 Mar 2027 | 2027-02-14 – 2027-03-15 |
| 5 | 15 Mar – 13 Apr 2027 | 2027-03-16 – 2027-04-14 |
| 6 | 14 Apr – 13 May 2027 | 2027-04-15 – 2027-05-14 |
| … | every 30 days | through window 36 (ends at row 2029-10-30) |

A window with more than 5 of its 30 rows missing or not `complete` is **VOID**. A void window breaks a consecutive pair. Duplicate rows raise an error.

## Rules

Each rule needs **two consecutive complete windows**.

| State | Rule |
|---|---|
| **BULLISH** | a ≥ +1 in both windows |
| **BEARISH** | a ≤ −1 in both windows |
| **STRUCTURALLY WRONG** | \|a\| < b in both windows (the wrapper no longer out-moves even the buyback fund), or any issuer figure in either window differs from the reconstruction by more than 0.5% under the rule frozen on 13 Nov 2026 |
| **BASE** | six complete windows with none of the pairs above |
| **MONITORING** | at least one complete window, no rule met |
| **NOT YET TESTABLE** | no complete window |

The rule that fired most recently sets the state.

One condition cannot be checked automatically and is reviewed by hand each quarter: evidence that accounts attributed under Rule A serve a product other than NRR also counts as **STRUCTURALLY WRONG**.

## What these rules are not

- **Coverage is not a signal.** A second wrapper rebuilt from the chain raises confidence in the measurement. It is bullish only if the combined absorption ratio across all covered products meets the bullish rule.
- **Not a price rule.** No state says anything about price.
- **Not a demand rule.** A creation shows NEAR entering a vehicle that holds it until redemption. It does not show a purchase.
- **Not a statement about all of NEAR's float.** Ordinary staking outside the wrapper moved far more NEAR per day in the baseline period.

## Baseline at freeze (data through 13 Nov 2026; for reference, not part of any rule)

| Period | Absorption ratio | Buyback ratio |
|---|---:|---:|
| Launch to 13 Nov, 46 daily windows | +3.70 | 0.11 |
| Since the 28 Oct peak, 16 windows | −1.59 | 0.12 |
| Latest 30 windows (overlaps the launch) | +0.11 | 0.11 |

No baseline period is a signpost window. The latest-30 reading would sit marginally inside the structurally-wrong zone (0.111 against 0.113), and the rolling 30-day ratio was above +1 on every reading from 28 Oct to 8 Nov, falling from +6.50 to +0.11 by 13 Nov. Both are launch effects, and the windows start on 15 Nov so that neither can trigger a rule.

## After six windows

When window 6 completes (row 2027-05-14), the median and range of the six ratios will be published. Annual thresholds for "sustained" and for the wrapper-held share of supply will then be frozen in a new file, with a hash, in the same way as this one. Until then, the rules above are the only ones.
