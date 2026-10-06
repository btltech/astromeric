# iOS monetisation — decision brief

Work to start **after 1.0.1 is approved**. Nothing here is implemented:
`Products.storekit` is empty and the app contains no StoreKit code.

This is deliberately a decision brief, not an implementation plan. The commercial
model is settled first; StoreKit code follows it.

---

## Facts this decision rests on

Checked in the code rather than assumed:

1. **Every chart on iOS is computed server-side.** The app calls
   `/v2/charts/natal`, `/progressed`, `/composite` and `/synastry`. So chart
   features carry a per-user server cost for as long as that user keeps using
   them, even though the calculation itself is deterministic.
2. **A Swiss Ephemeris engine already ships inside the app**
   (`EphemerisEngine/`, with `swisseph`), but today it is used only for widgets,
   the Oracle and local timing — not for the charts the user looks at.
3. **The advanced techniques are not in the iOS app.** Solar arc directions,
   lunar returns, profections and relocation exist in the backend and in the
   Android client. iOS has no endpoints for them. Any plan that sells them on
   iOS is selling something that must first be built there.
4. **The AI path has a real marginal cost**, and is currently restricted to the
   owner's device by access code (#7).

Fact 3 corrects an earlier recommendation of mine: I proposed the advanced
techniques as the paid hook without checking that iOS actually has them.

## The decision: which model

| Model | Fits because | Costs you |
| --- | --- | --- |
| Subscription | Ongoing forecasts and AI have ongoing cost | Hardest sell; needs continuous perceived value; churn |
| One-time Pro unlock | Simple, no subscription fatigue, easy to market | No recurring income against server costs that recur per user (fact 1) |
| Hybrid: permanent unlock for calculation features, subscription for AI and continuously generated content | Maps price to actual marginal cost | More moving parts: two entitlement types, more states to test |

The hybrid is the most honest fit for this app **if** the calculation side stops
costing per use. The engine to do that is already in the bundle (fact 2): moving
chart calculation on-device would make a lifetime unlock economically safe, work
offline, and strengthen the privacy story, at the cost of a real piece of work to
reach parity with the backend's output.

Without that move, a lifetime unlock means selling perpetual access to a service
that keeps costing you per user.

## Settle before any StoreKit code

- What stays free permanently.
- What is unlocked once, and what — if anything — genuinely requires recurring
  payment.
- Price and currency, per product.
- Introductory or trial behaviour, and what happens when a trial ends.
- **Restore semantics**: what "restore" means for each entitlement type.
- **Lapse behaviour**: when a subscription ends, what happens to content already
  generated? Readings already saved? This needs an answer before the UI is built,
  not after.
- **Offline behaviour**: what a paying user sees with no network.
- **Existing users**: everyone who installs 1.0.1 gets today's features free.
  Decide whether they keep them, and say so in the App Store copy.
- **Failure states**: purchase interrupted, refunded, family-shared, billing
  retry, entitlement unavailable at launch.

## Then, implementation shape

- `StoreService` deriving entitlement from `Transaction.currentEntitlements` and
  observing `Transaction.updates` — offline-capable and restores through the
  Apple ID, which suits the app's no-accounts design.
- A single `PremiumGate` modifier so the check exists in one place.
- `PaywallView` with what Apple rejects for when missing: price and period on
  screen, **Restore Purchases**, terms and privacy links, localized in all five
  languages (the CI localization job enforces the last part).
- `StoreKitTest` unit tests against the local configuration — purchase grants,
  expiry revokes, restore re-grants, refund revokes, gate hides content — running
  in the `ios-tests` CI job from #14.

## Server-side entitlement (only if needed)

The paid API is public and unauthenticated. If that matters once there is
something to protect, the anonymous per-install key from #6 can carry a signed
transaction for the backend to verify against Apple's App Store Server API — no
account, no personal data. **Privacy consequence:** storing a transaction id adds
**Purchases** to the App Store privacy answers (collected, not linked), so the
declarations and `privacy-security-audit.md` would need updating first.

## Commission

Apple's standard commission is 30%. The Small Business Program offers 15% for
participants who **enrol and meet Apple's eligibility conditions**, which take
account of the developer and associated accounts' proceeds. Whether this account
qualifies is Apple's determination, not something inferable from this app.

## Sequencing

1. **Current release:** monetisation untouched. Finish review. Guideline 4.3(b)
   names fortune-telling as a saturated category needing a meaningfully
   different experience; adding a payment system now only widens what review can
   pick at without helping that argument.
2. **Next release:** monetisation as its own bounded project, with the
   commercial model settled first.

No effort estimate is given here on purpose. StoreKit 2 itself is small; the work
is entitlement design, restore and lapse semantics, failure states, purchase UI,
testing and App Store configuration. Estimating that before the model is decided
is how purchase architecture ends up built around a commercial model that then
changes.
