# NEAR Flow Intelligence — submission kit (revised draft)

Update every link marked below after GitHub Pages is enabled and the demo video is published. Do not submit with placeholders.

## 1. X demo post

**Post (attach the demo video):**

NEAR's supply models count issuance and protocol buybacks. But one redeemable ETF can move NEAR into and out of staked custody at scale. NRR's net custody flow averaged +330,985 NEAR/day since launch, then -141,344 NEAR/day after its 28 Oct peak. @NEARProtocol #NEARHackathon

**Reply with the links:**

We rebuilt NRR's observed staking custody from NEAR mainnet, account by account. The reconstruction is within 0.15% of Bitwise's published figure on the three archived issuer dates. The dashboard compares signed net custody flow with issuance and the buyback-fund balance change. Custody movement is not proof of market buying or selling.

Dashboard: [ADD PUBLIC GITHUB PAGES URL]

Code and cached evidence: https://github.com/Gosho1992/near-flow-intelligence

## 2. Demo video script (about 90–100 seconds)

| Time | Show | Say |
|---|---|---|
| 0–12 s | Hero screen and four metric tiles | "This is NEAR Flow Intelligence. It reconstructs the NEAR held in Bitwise's NRR staking custody directly from mainnet transactions and compares its daily net flow with NEAR issuance." |
| 12–28 s | Show the launch-period and post-peak daily averages | "The direction matters. Since launch, NRR's signed net custody flow averaged about 331,000 NEAR per day. Since its 28 October peak, the average reversed to about 141,000 NEAR per day out of custody. The position is substantial, but its flow can reverse." |
| 28–44 s | Cumulative net-flow chart; switch Since launch / 30 days | "This chart starts all three series at zero. The dark line is NRR creations minus redemptions. The grey line is newly minted NEAR. The ochre line is the buyback fund's balance change. These are on-chain balance movements, not proof of market purchases." |
| 44–55 s | Switch NEAR / USD equivalent | "The USD view converts using the latest archived Bitwise NAV per NEAR. It is a dated valuation reference, not a live spot-price feed." |
| 55–68 s | Holdings chart and issuer dots | "The reconstructed staked balance is checked against Bitwise's dated holdings disclosures. We have three archived issuer snapshots, with the maximum difference below 0.2 percent. The dots are issuer observations; the intervening line is the chain reconstruction." |
| 68–82 s | Follow the NEAR; show the 4 Nov 785,418 NEAR redemption | "Here is a redemption: unstake, withdraw, return to the inferred custody hub, then the probable onward match. Beyond the hub, NEAR is fungible, so we never call that link certain and we do not claim that the tokens were sold." |
| 82–100 s | Terminal: make rebuild, make test; show METHOD.md | "The data can be rebuilt offline from cached public responses. The methodology explains the attribution rule, the one-hop candidate we have kept outside the main totals, and what the chain cannot prove. The thesis can be wrong, and the dashboard is designed to show that." |

## 3. "What they built" (form field idea, 20–2,000 characters)

NEAR Flow Intelligence independently reconstructs the observed staking custody of Bitwise's NEAR ETF (NRR) from NEAR mainnet transactions. It identifies 73 primary accounts using a transparent rule: an account receives funds from an inferred custody hub and then calls deposit_and_stake on the NRR pool. Their staked balances are compared with Bitwise's dated "NEAR in Trust" snapshots; the three archived issuer dates reconcile within 0.15%.

The project measures signed net custody flow (creations minus redemptions) and compares it with NEAR's gross issuance and the protocol buyback-fund balance change. The flow is reversible: its average was about +331,000 NEAR/day over the launch period and about -141,000 NEAR/day after the 28 October peak. Those are custody movements, not proof of exchange purchases, sales or price impact. The dashboard includes a cumulative comparison chart, dated USD-equivalent view, transaction-level traces, separate partial-holder context and explicit attribution limitations.

The pipeline uses NEAR archival RPC, FastNEAR transaction data and cached public responses. make rebuild reconstructs the data and dashboard offline; make test runs the offline checks. The repository includes source evidence, methodology, a frozen pre-registered prediction and a separate disclosure of a possible one-hop account that is excluded pending independent verification.

## 4. Submission form fields

- Project name: NEAR Flow Intelligence
- Lead name: [CONFIRM]
- Email: [USER TO ENTER]
- Team size: 1
- Track: Investment Thesis
- Mainnet NEAR payout account: [USER TO CREATE/ENTER — do not invent]
- Project URL: https://github.com/Gosho1992/near-flow-intelligence (only after making repository public)
- Demo URL: [ADD THE PUBLIC X POST URL]
- Dashboard URL: [ADD PUBLIC GITHUB PAGES URL]
- Consent: the user must review and accept the organizer's wording.

## 5. Pre-submit checklist

- [ ] Verify repository visibility and make it public if the rules require public access.
- [ ] Enable GitHub Pages with GitHub Actions and confirm the deployed URL loads in an incognito browser.
- [ ] Run make rebuild, make test and make verify-prediction from a clean checkout; inspect the generated diff.
- [ ] Confirm the dashboard data-through date and latest issuer snapshot date.
- [ ] Record and upload the demo video; make sure it shows the dashboard and a real transaction trace.
- [ ] Publish the X post with the video, @NEARProtocol and #NEARHackathon; then insert the actual post URL.
- [ ] Create/use the user's own mainnet NEAR payout account and enter it in the official form.
- [ ] Submit once only after all links and fields have been checked.
