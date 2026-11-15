# NEAR Flow Intelligence

**A daily reconstruction of Bitwise's NEAR ETF (NRR), measured against NEAR issuance and the protocol buyback-fund balance.** Issuer-data trackers publish NRR flows from Bitwise's own files. This project rebuilds its observed staking custody account by account from NEAR mainnet, checks the reconstruction against issuer snapshots, and makes the direction and size of its net custody flow visible.

The investment question is not whether NRR is "demand" in the market. The chain cannot prove that. The question is how much NEAR moves into and out of this redeemable product's staked custody, how that flow compares with protocol issuance, and how quickly the direction can reverse.

## The long-term thesis

**Over one to three years, NEAR's supply-side case depends on one measurable condition: whether redeemable regulated wrappers take in more NEAR than the protocol mints.** We call this the **absorption ratio** (wrapper net custody flow ÷ NEAR minted, same window). For NRR it was <!--n:absorption_launch:s2-->+3.54<!--/n--> over its first <!--n:days:int-->48<!--/n--> days, <!--n:absorption_since_peak:s2-->-1.41<!--/n--> since its 28 Oct peak, and <!--n:absorption_last30:s2-->-0.18<!--/n--> over the latest 30. HSP-029 would lower NEAR's issuance cap from 2.5% to 1.6% along a 24-month ramp after a 90-day grace period, so the same flow becomes a growing multiple of new supply. The endpoint is in year 3, February 2029 at the earliest. This is not a claim about NEAR's total float: ordinary staking outside the wrapper moved about <!--n:other_stake_abs_daily_mean:m-->2.69M<!--/n--> NEAR a day, far more. **Position today: the bullish condition is not met** (signposts: <!--n:signposts_state:-->NOT YET TESTABLE<!--/n-->).

- [THESIS.md](THESIS.md): the claim, the evidence for and against, and the scenarios.
- [SIGNPOSTS.md](SIGNPOSTS.md): bullish, bearish and structurally-wrong rules on non-overlapping 30-day windows from 15 Nov 2026. Frozen with a SHA-256 and an OpenTimestamps proof.
- [LONG_TERM_PLAN.md](LONG_TERM_PLAN.md): the test calendar to 2029, indicators, review routine and build order.
- Two pre-registered predictions: [PREDICTION.md](PREDICTION.md) and [PREDICTION-2.md](PREDICTION-2.md).

## The finding

In the <!--n:days:int-->48<!--/n--> measured daily windows from 2026-09-29 through <!--n:data_through:-->2026-11-15<!--/n-->, NRR's signed net custody flow averaged **<!--n:launch_net_flow_per_day:sint-->+317,250<!--/n--> NEAR per day** (<!--n:launch_net_baskets_per_day:s1-->+6.1<!--/n--> approximate 10,000-share baskets per day). Since the 2026-10-28 holdings peak, across <!--n:since_peak_net_flow_days:int-->18<!--/n--> daily windows, the average was **<!--n:since_peak_net_flow_per_day:sint-->-125,489<!--/n--> NEAR per day** (<!--n:since_peak_net_baskets_per_day:s1-->-2.4<!--/n--> baskets per day).

Those are signed averages across different periods, not cumulative totals and not forecasts. NRR's latest reconstructed staked position is <!--n:nrr_holdings_latest:m-->15.32M<!--/n--> NEAR as of <!--n:data_through:-->2026-11-15<!--/n-->, <!--n:change_since_peak_pct:spct-->-12.66%<!--/n--> below its peak. The position is large; its persistence is not established.

A basket conversion uses the latest included Bitwise snapshot's NEAR-per-share figure multiplied by 10,000 shares. It is a comparison unit, not evidence that a creation or redemption was a market purchase or sale.

## Why this is different

The chain reconstruction is within <!--n:max_abs_issuer_gap_pct:pct-->0.15%<!--/n--> of Bitwise's published "NEAR in Trust" on the <!--n:issuer_gaps_count:int-->4<!--/n--> issuer dates currently archived in the repository. Every snapshot is dated and retains its retrieval time. This is a historical comparison on those dates; it does not confirm every intervening daily value.

The project records:
- The attributed NRR staking accounts and the evidence used to identify them.
- Staked, unstaked and liquid custody layers without adding the same NEAR twice.
- Creation and redemption sequences with transaction links and confidence labels.
- NEAR issuance, total supply, validator stake and measured staking rewards.
- Changes in the protocol buyback-fund balance, separately from executed purchases (which are not measured).
- A separate, partial observation of SVRN's Bitwise pool, never included in NRR totals.

## Comparable flow readings (data through <!--n:data_through:-->2026-11-15<!--/n-->)

| Measure | Reading |
|---|---:|
| NRR signed net custody flow, launch-period average | <!--n:launch_net_flow_per_day:sint-->+317,250<!--/n--> NEAR/day · <!--n:launch_net_baskets_per_day:s1-->+6.1<!--/n--> baskets/day |
| NRR signed net custody flow, since 28 Oct peak average | <!--n:since_peak_net_flow_per_day:sint-->-125,489<!--/n--> NEAR/day · <!--n:since_peak_net_baskets_per_day:s1-->-2.4<!--/n--> baskets/day |
| NRR signed net custody flow, latest 30-day total | <!--n:last30_nrr_net:sint-->-482,948<!--/n--> NEAR across <!--n:last30_net_flow_days:int-->30<!--/n--> windows |
| Current-period issuance average | <!--n:issuance_per_day:int-->89,516<!--/n--> NEAR/day · <!--n:issuance_baskets_per_day:1-->1.7<!--/n--> baskets/day |
| Buyback-fund balance change, launch-period average | <!--n:buyback_net_change_per_day:int-->10,071<!--/n--> NEAR/day · <!--n:buyback_baskets_per_day:1-->0.2<!--/n--> baskets/day |
| Buyback-fund balance change as a share of measured issuance, launch to date | <!--n:buyback_change_pct_of_issuance:pct-->11.25%<!--/n--> |
| Bitwise SEC 10-Q at launch (30 Sep 2026, 4 p.m. ET) vs chain: in-kind creations · staked value · undelivered purchases | to four decimals · inside the filing's rounding band (only Rule A seed + one-hop account fit) · consistent at published price precision |
| **Absorption ratio** (NRR net flow ÷ NEAR minted): launch · since peak · latest 30 days | <!--n:absorption_launch:s2-->+3.54<!--/n--> · <!--n:absorption_since_peak:s2-->-1.41<!--/n--> · <!--n:absorption_last30:s2-->-0.18<!--/n--> |

The buyback series is a balance change, not a record of executed market purchases. The table compares measured on-chain quantities and their scale; it does not imply that NRR custody movements and buyback-fund balance changes have the same economic meaning.

### Issuance path

Issuance is scheduled to fall, not falling. Today's 2.5% cap mints about <!--n:hsp029_m0_baskets_per_day:2-->1.71<!--/n--> NRR-sized baskets a day. If HSP-029 takes effect, a ~90-day grace period is followed by a linear 24-month ramp: about <!--n:hsp029_m6_baskets_per_day:2-->1.56<!--/n--> baskets a day at ramp month 6, <!--n:hsp029_m12_baskets_per_day:2-->1.40<!--/n--> at 12, <!--n:hsp029_m18_baskets_per_day:2-->1.25<!--/n--> at 18 and <!--n:hsp029_m24_baskets_per_day:2-->1.09<!--/n--> at 24. Ratification and a validator-adopted upgrade come first. The pipeline reads the cap from the chain every day (<!--n:protocol_cap_pct_latest:pct-->2.50%<!--/n--> at the cut), so the start is observed, not assumed. `data/out/scenarios.csv` projects 36 months under absorption ratios of +1, 0 and −1. These are mechanical consequences, not forecasts.

## Run it

Python 3.10+ is required. No wallet, mainnet transaction, or paid API key is required for the committed offline rebuild.

```bash
git clone https://github.com/Gosho1992/near-flow-intelligence
cd near-flow-intelligence

make rebuild  # raw cached responses -> work datasets -> outputs, docs and site
make test     # offline checks
make serve    # dashboard at http://127.0.0.1:8000
```

For a faster rebuild from already collected `data/work/` snapshots, run `make data`. To fetch new chain data, `make refresh` requires network access and is subject to the FastNEAR API's rate limits.

## What to inspect

1. **Holdings and issuer checks.** The solid line is the reconstructed staked balance. The issuer dots are dated Bitwise observations. The archived comparison dates and differences are visible in the evidence data.
2. **Net flow against supply.** The dashboard plots signed NRR custody flow, NEAR issuance and the buyback-fund balance change in a common unit and a common date range. Cumulative lines are rebased at the selected range start.
3. **The long-term test.** The signpost panel shows each 30-day window's absorption ratio against the frozen rules, and the issuance path under HSP-029.
4. **Sources and destinations.** The trace panel links observed transactions. A step beyond the custody hub is at best probable because NEAR is fungible and the hub pools balances.
5. **Re-run the evidence.** `make rebuild` reconstructs outputs from cached raw RPC and transaction-API responses. `make test` checks the pipeline invariants and offline reproducibility.

## What this does not prove

- A movement into NRR custody was bought on an exchange.
- A redemption was sold on an exchange.
- A holder is the legal or beneficial owner of an account.
- A buyback-fund balance increase was an executed market purchase.
- A partially observed pool represents an issuer's entire treasury.
- Custody flows caused NEAR's price to rise or fall.

## Current attribution boundary

The primary NRR series uses **Rule A**: an account is counted when the inferred custody hub funded it and it subsequently called `deposit_and_stake` on `bitwise_2.poolv1.near`. One account outside Rule A, funded by a Rule A account and then staked in the NRR pool, is verified from the raw cache and shown as a sensitivity only (<!--n:one_hop_staked_latest:int-->52,516<!--/n--> NEAR; adding it would move the issuer gaps to about <!--n:one_hop_gap_max_pct:spct-->+0.20%<!--/n-->). The BigQuery check currently covers direct hub recipients only; it is not a global proof that no downstream account was missed.

SVRN is a separate contextual observation: a company-reported treasury figure and a partial on-chain view of one Bitwise-operated pool. The two are not reconciled, not summed, and not treated as new purchases.

## Repository guide

| Path | Purpose |
|---|---|
| `nfi/` | Python pipeline and offline collectors |
| `data/raw/` | Cached NEAR RPC and FastNEAR transaction responses |
| `data/work/` | Collected daily and attribution datasets |
| `data/out/` | Published CSV/JSON outputs |
| `data/bigquery/` | Independent completeness-check SQL and captured result |
| `site/` | Static dashboard and copied data |
| `tests/` | Offline unit and invariant checks |
| `THESIS.md` | Investment thesis, evidence for/against and falsifiers |
| `LONG_TERM_PLAN.md` | Test calendar to 2029, scenarios, indicators, review routine, build order |
| `SIGNPOSTS.md`, `SIGNPOSTS.lock` | Frozen long-term rules and their hash |
| `METHOD.md` | Attribution, formulas, data states and limitations |
| `SOURCES.md` | Dated source register |

## Disclosure

Built by Zain Zia with AI coding assistance (Claude). Data sources include NEAR archival RPC (FastNEAR), the FastNEAR transaction API, Bitwise's NRR page, the Bitwise prospectus and NEAR's public BigQuery dataset. The buyback-fund account definition follows [nikolaskahris-png/near-thesis-data](https://github.com/nikolaskahris-png/near-thesis-data). Research, not investment advice. MIT licence.
