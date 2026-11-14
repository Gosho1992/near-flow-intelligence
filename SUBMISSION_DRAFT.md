# NEAR Flow Intelligence — submission kit

Update every link marked below after GitHub Pages is enabled and the demo video is published. Do not submit with placeholders. All figures: data through 13 Nov 2026.

## 1. X demo post

**Post (attach the demo video):**

Over 1–3 years, NEAR's supply-side case comes down to one number: do regulated wrappers absorb more NEAR than the protocol mints? Bitwise's NRR: 3.7× at launch, −1.6× since its peak. Rebuilt from the chain, judged by frozen rules. @NEARProtocol #NEARHackathon

**Reply with the links:**

NRR is rebuilt account by account from mainnet and matches Bitwise within 0.15% on four dates, one out of sample. Absorption ≥ +1 for two 30-day windows is bullish, ≤ −1 bearish. Rules hashed and timestamped. Today: not met.

Dashboard: [ADD PUBLIC GITHUB PAGES URL]
Code, evidence, long-term plan: https://github.com/Gosho1992/near-flow-intelligence

## 2. Demo video script (about 100–110 seconds)

| Time | Show | Say |
|---|---|---|
| 0–14 s | Hero question and the long-term thesis box | "This is NEAR Flow Intelligence. Our thesis is one condition. Over the next one to three years, do regulated wrappers like Bitwise's NEAR ETF take in more NEAR than the protocol mints? NEAR held in the ETF leaves only when shares are redeemed, so this decides who holds the new supply." |
| 14–28 s | The four tiles: +3.70, −1.59, +0.11, 15.31M | "We call it the absorption ratio: ETF net flow divided by NEAR minted. Over its first 46 days NRR absorbed 3.7 times the new supply. Since its 28 October peak it released 1.6 times. Over the latest 30 days it's 0.11. Today the bullish condition is not met." |
| 28–42 s | Holdings chart with the four Bitwise dots | "The numbers are rebuilt account by account from mainnet. They match Bitwise's own published holdings within 0.15% on four dates. The latest was published after we froze the comparison rule, so it's an out-of-sample test." |
| 42–58 s | Long-term test: state box, rules, window table | "This is the long-term test. The rules were frozen before the first window opened on 15 November, with a hash and an OpenTimestamps proof anchored in Bitcoin. Two windows at or above plus one is bullish, two at or below minus one is bearish. If the ETF stops out-moving even the buyback fund, the thesis is structurally wrong. A new window closes every 30 days until 2029." |
| 58–74 s | Issuance-path chart | "Issuance is scheduled to fall, not falling. HSP-029 ramps the cap from 2.5 to 1.6 percent over 24 months after a grace period, so the endpoint is in 2029. We read the cap from the chain every day, so the start will be observed, not assumed. Our model's avoided issuance matches the proposal's own 11.8 million." |
| 74–86 s | Scenario chart, then the boundary sentence | "These are mechanical scenarios, not forecasts. And the boundary: ordinary staking moves about 2.8 million NEAR a day, far more than the ETF. So we claim something narrower: among the supply terms, the ETF is the largest and the only one that reverses." |
| 86–96 s | Follow the NEAR: 4 Nov redemption | "Every movement traces to transactions. Past the custody hub NEAR is pooled, so those links are only probable, and we never claim a sale." |
| 96–110 s | Terminal: make rebuild, make test; LONG_TERM_PLAN.md | "Everything rebuilds offline from cached public data and runs 43 tests. The long-term plan sets out the calendar, the indicators and what would change our mind. The thesis can be wrong, and it's built to show that." |

## 3. "What they built" (form field, 20–2,000 characters; this text is about 1,600)

NEAR Flow Intelligence tests a long-term supply thesis for NEAR. The claim: over one to three years, NEAR's supply-side case depends on whether redeemable regulated wrappers absorb more NEAR than the protocol mints. We measure this with an absorption ratio (wrapper net custody flow ÷ NEAR minted, same window).

We rebuilt the staking custody of Bitwise's NEAR ETF (NRR) from mainnet, account by account. 73 accounts are identified by a transparent rule, and the result matches Bitwise's published holdings within 0.15% on four dates, one of them out of sample. NRR's absorption ratio was +3.70 at launch, −1.59 since its 28 Oct peak and +0.11 over the latest 30 days. HSP-029 is modelled as its real 24-month ramp, and the protocol cap is read daily. Ordinary staking, which moves far more NEAR, is stated as the boundary of the claim.

The long-term test is frozen with SHA-256 and OpenTimestamps: absorption ≥ +1 in two consecutive 30-day windows is bullish, ≤ −1 bearish, and below the buyback-fund ratio means structurally wrong. Windows run from 15 Nov 2026 to 2029. LONG_TERM_PLAN.md gives the calendar, scenarios, indicators and build order. Two pre-registered 30-day predictions are also locked.

Evidence: source-wallet analysis (more than a quarter of inflow in one transfer; redemptions returned to the wallets that delivered creations), transaction-level traces, and a one-hop account verified and shown as a sensitivity. make rebuild regenerates everything offline from cached public data; make test runs 43 checks. Custody flow is not proof of purchases, sales or price impact.

## 4. Submission form fields

- Project name: NEAR Flow Intelligence
- Lead name: [CONFIRM]
- Email: [USER TO ENTER]
- Team size: 1
- Track: Investment Thesis
- Mainnet NEAR payout account: gosho1992.near (exists on mainnet, checked 14 Nov 2026)
- Project URL: https://github.com/Gosho1992/near-flow-intelligence (must be public when you submit)
- Demo URL: [ADD THE PUBLIC X POST URL]
- Dashboard URL: [ADD PUBLIC GITHUB PAGES URL]
- Consent: the user must review and accept the organizer's wording.

## 5. Pre-submit checklist

- [ ] Make the repository public.
- [ ] Enable GitHub Pages and confirm the deployed URL loads in an incognito browser.
- [ ] Run make rebuild, make test and make verify-prediction from a clean checkout.
- [ ] Confirm the dashboard's data-through date and the signpost state.
- [ ] Record and upload the demo video showing the long-term test section and a real transaction trace.
- [ ] Publish the X post with the video, @NEARProtocol and #NEARHackathon; insert the post URL.
- [x] Payout account created: gosho1992.near. [ ] Seed phrase saved on paper.
- [ ] Submit once, after all links and fields are checked.
