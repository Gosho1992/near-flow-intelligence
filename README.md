# NEAR Flow Intelligence

**A daily reconstruction of Bitwise's NEAR ETF (NRR), measured against NEAR issuance and the protocol buyback-fund balance.** Issuer-data trackers publish NRR flows from Bitwise's own files. This project rebuilds its observed staking custody account by account from NEAR mainnet, checks the reconstruction against issuer snapshots, and makes the direction and size of its net custody flow visible.

The investment question is not whether NRR is "demand" in the market. The chain cannot prove that. The question is how much NEAR moves into and out of this redeemable product's staked custody, how that flow compares with protocol issuance, and how quickly the direction can reverse.

## The finding

In the 46 measured daily windows from 2026-09-29 through 2026-11-13, NRR's signed net custody flow averaged **<!--n:launch_net_flow_per_day:sint-->+330,985<!--/n--> NEAR per day** (<!--n:launch_net_baskets_per_day:s1-->+6.3<!--/n--> approximate 10,000-share baskets per day). Since the 2026-10-28 holdings peak, across 16 daily windows, the average was **<!--n:since_peak_net_flow_per_day:sint-->-141,344<!--/n--> NEAR per day** (<!--n:since_peak_net_baskets_per_day:s1-->-2.7<!--/n--> baskets per day).

Those are signed averages across different periods, not cumulative totals and not forecasts. NRR's latest reconstructed staked position is <!--n:nrr_holdings_latest:m-->15.31M<!--/n--> NEAR as of <!--n:data_through:-->2026-11-13<!--/n-->, <!--n:change_since_peak_pct:spct-->-12.70%<!--/n--> below its peak. The position is large; its persistence is not established.

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

## Comparable flow readings (data through <!--n:data_through:-->2026-11-13<!--/n-->)

| Measure | Reading |
|---|---:|
| NRR signed net custody flow, launch-period average | <!--n:launch_net_flow_per_day:sint-->+330,985<!--/n--> NEAR/day · <!--n:launch_net_baskets_per_day:s1-->+6.3<!--/n--> baskets/day |
| NRR signed net custody flow, since 28 Oct peak average | <!--n:since_peak_net_flow_per_day:sint-->-141,344<!--/n--> NEAR/day · <!--n:since_peak_net_baskets_per_day:s1-->-2.7<!--/n--> baskets/day |
| NRR signed net custody flow, latest 30-day total | <!--n:last30_nrr_net:sint-->+297,710<!--/n--> NEAR across <!--n:last30_net_flow_days:int-->30<!--/n--> windows |
| Current-period issuance average | <!--n:issuance_per_day:int-->89,497<!--/n--> NEAR/day · <!--n:issuance_baskets_per_day:1-->1.7<!--/n--> baskets/day |
| Buyback-fund balance change, launch-period average | <!--n:buyback_net_change_per_day:int-->9,935<!--/n--> NEAR/day · <!--n:buyback_baskets_per_day:1-->0.2<!--/n--> baskets/day |
| Buyback-fund balance change as a share of measured issuance, launch to date | <!--n:buyback_change_pct_of_issuance:pct-->11.10%<!--/n--> |

The buyback series is a balance change, not a record of executed market purchases. The table compares measured on-chain quantities and their scale; it does not imply that NRR custody movements and buyback-fund balance changes have the same economic meaning.

### Issuance scenario

The current measured issuance rate averages <!--n:issuance_per_day:int-->89,497<!--/n--> NEAR/day (about <!--n:issuance_baskets_per_day:1-->1.7<!--/n--> NRR-sized baskets). If the proposed HSP-029 1.6% annual inflation target were fully reached, a simple proportional scenario at the same supply base would be about <!--n:issuance_hsp029_target_per_day:int-->57,278<!--/n--> NEAR/day (<!--n:issuance_hsp029_baskets_per_day:1-->1.1<!--/n--> baskets). The official forum record lists HSP-029 as Succeeded, but the 1.6% rate is not active in the observed protocol configuration; remaining governance/implementation steps, a grace period and validator adoption are required. This is a full-target scenario, not a current-rate claim.

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
3. **Sources and destinations.** The trace panel links observed transactions. A step beyond the custody hub is at best probable because NEAR is fungible and the hub pools balances.
4. **Re-run the evidence.** `make rebuild` reconstructs outputs from cached raw RPC and transaction-API responses. `make test` checks the pipeline invariants and offline reproducibility.

## What this does not prove

- A movement into NRR custody was bought on an exchange.
- A redemption was sold on an exchange.
- A holder is the legal or beneficial owner of an account.
- A buyback-fund balance increase was an executed market purchase.
- A partially observed pool represents an issuer's entire treasury.
- Custody flows caused NEAR's price to rise or fall.

## Current attribution boundary

The primary NRR series uses **Rule A**: an account is counted when the inferred custody hub funded it and it subsequently called `deposit_and_stake` on `bitwise_2.poolv1.near`. The project has identified a one-hop downstream candidate that Rule A does not include. It remains disclosed separately until its funding history, timing and pool transaction are reproduced and tested. The BigQuery check currently covers direct hub recipients only; it is not a global proof that no downstream account was missed.

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
| `METHOD.md` | Attribution, formulas, data states and limitations |
| `SOURCES.md` | Dated source register |

## Disclosure

Built by Zain Zia with AI coding assistance (Claude). Data sources include NEAR archival RPC (FastNEAR), the FastNEAR transaction API, Bitwise's NRR page, the Bitwise prospectus and NEAR's public BigQuery dataset. The buyback-fund account definition follows [nikolaskahris-png/near-thesis-data](https://github.com/nikolaskahris-png/near-thesis-data). Research, not investment advice. MIT licence.
