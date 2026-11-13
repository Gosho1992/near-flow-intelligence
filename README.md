# NEAR Flow Intelligence

**Bitwise's NEAR ETF (NRR), rebuilt from the chain, and set against NEAR's supply.**

NEAR supply models track issuance and the protocol's buyback fund. This project adds what those models leave out: the NEAR held by a regulated investment product. We rebuild Bitwise NRR's holdings every day from NEAR staking accounts, check them against Bitwise's own published figures, follow every creation and redemption transaction by transaction, and compare the size of those moves with NEAR's new supply and buyback fund over the same days.

Built at NEAR HACKATHON 2026 — Investment Thesis track. Thesis: [THESIS.md](THESIS.md). Method: [METHOD.md](METHOD.md).

## What it found (data through <!--n:data_through:-->2026-11-13<!--/n-->)

- NRR's staking accounts held <!--n:nrr_holdings_latest:int-->15,310,526<!--/n--> NEAR, after a peak of <!--n:nrr_peak:int-->17,537,598<!--/n--> NEAR on <!--n:nrr_peak_date:-->2026-10-28<!--/n--> (<!--n:change_since_peak_pct:spct-->-12.70%<!--/n--> since).
- The chain reconstruction is within <!--n:max_abs_issuer_gap_pct:pct-->0.45%<!--/n--> of Bitwise's published "NEAR in Trust" on every date we have.
- Since <!--n:window_start:-->2026-09-28<!--/n-->: <!--n:creations_total:int-->17,544,103<!--/n--> NEAR moved into NRR's staking custody and <!--n:redemptions_total:int-->2,318,791<!--/n--> NEAR moved out. Each move is a validated sequence of transactions: <!--n:creations_confirmed_count:int-->74<!--/n--> of <!--n:creations_count:int-->74<!--/n--> creations (hub funding → stake) and <!--n:redemptions_confirmed_count:int-->7<!--/n--> of <!--n:redemptions_count:int-->10<!--/n--> redemptions (unstake → withdraw → back to the custody hub) are confirmed, across <!--n:attributed_accounts:int-->73<!--/n--> accounts.
- Over the same days the protocol minted <!--n:gross_issuance_total:int-->4,116,853<!--/n--> NEAR and the buyback fund's balance changed by <!--n:buyback_fund_change_total:int-->457,016<!--/n--> NEAR. NRR's custody moves were about <!--n:ratio_abs_custody_to_abs_buyback:x-->43×<!--/n--> the buyback fund's movement — a size comparison, not a claim of market buying or selling.
- NRR holds <!--n:nrr_share_staked_pct_latest:pct-->2.59%<!--/n--> of all staked NEAR.

## Try it in 60 seconds

Python 3.10+ only. No API key, wallet, paid service or mainnet transaction.

```bash
git clone https://github.com/Gosho1992/near-flow-intelligence && cd near-flow-intelligence
make data     # rebuild every number offline from the committed chain cache
make test     # 18 independent checks
make serve    # dashboard at http://127.0.0.1:8000
```

What to look at, in order:

1. **Do the chain numbers match Bitwise?** Open the dashboard: the dots on the holdings chart are Bitwise's published figures; the line is our reconstruction. `make test` fails if any gap exceeds 1%.
2. **Where did the NEAR go?** In "Follow the NEAR", pick a redemption: unstake → withdraw → custody hub → next accounts, each with a NearBlocks link, the rule that labels the account, and how sure the link is (observed, probable, ambiguous or unmatched).
3. **How big is it?** "How big are these moves?" shows NRR's custody moves next to NEAR minted and the buyback-fund change, daily or cumulative.
4. **What can't the chain prove?** The dashboard and THESIS.md list it: market trades inside exchanges, cash vs in-kind creations, legal ownership.

`make refresh` re-reads the chain up to today (network needed; ~1 hour because FastNEAR's transaction API is rate-limited). A GitHub Action does this daily and redeploys the dashboard only if all checks pass.

## How it works

| Step | Source | Output |
|---|---|---|
| Daily 00:00 UTC block heights | NEAR archival RPC `block` | `data/work/heights.json` |
| NRR accounts (rule: funded by the custody hub, then `deposit_and_stake`) | FastNEAR transaction API: hub + pool histories | `data/out/accounts.csv` (evidence per account) |
| Custody layers: staked, unstaked, liquid in basket accounts, liquid in hub | RPC `get_accounts`, `view_account` | `data/out/daily.csv` |
| Creations / redemptions from actual transactions | transaction actions, receipts, pool logs | `data/out/events.csv` |
| Staking rewards, measured | median growth of delegators with no transactions that day | `daily.csv` (`nrr_rewards`, `unexplained`) |
| Supply: minted per epoch, burn, net change; total stake | block-header `total_supply` at epoch boundaries; validator `locked` balances | `daily.csv` |
| Buyback fund | `buybacks.multisignature.near` + `1csfundsadmin.sputnik-dao.near`, native + wNEAR in `intents.near` | `daily.csv` |
| Redemption paths | hub and pass-through histories | `data/out/traces.json` |

Every number in this README, THESIS.md and the dashboard is generated into `data/out/headline.json`; a test fails if any document disagrees with the data.

## Limits

- The NRR attribution is rule-based and checked against Bitwise's figures; it is not a legal ownership proof.
- A move into custody is not proof of a market purchase; a move out is not proof of a sale. Trades inside exchanges are not on-chain.
- "Exchange-style wallet" is a published heuristic (≥10,000 transactions), not an identified exchange.
- The buyback series is the buyback fund's balance, not executed purchases or burns.
- One product so far. Other NEAR products (21Shares, Grayscale) are listed in THESIS.md with dated issuer figures, not attributed on-chain.

## Repository

```
nfi/          pipeline (Python standard library only)
data/raw/     cached RPC and transaction-API responses (offline rebuild)
data/work/    collected chain series
data/out/     published outputs: daily.csv, events.csv, accounts.csv, traces.json, headline.json
site/         static dashboard (Chart.js bundled)
tests/        18 checks
```

## Disclosure

Built by Zain Zia with AI coding assistance (Claude). Data: NEAR archival RPC (FastNEAR), FastNEAR transaction API, Bitwise's NRR page. The buyback-fund definition follows [nikolaskahris-png/near-thesis-data](https://github.com/nikolaskahris-png/near-thesis-data). Research, not investment advice. MIT licence.
