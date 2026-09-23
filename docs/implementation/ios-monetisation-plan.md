# iOS monetisation plan

Planned work, to start **after 1.0.1 is approved**. Nothing here is implemented
yet: `Products.storekit` is empty, and the app contains no StoreKit code.

The one thing worth doing before approval is the paperwork in step 0, because it
gates everything and is slow when it goes wrong.

---

## 0. Before any code (yours, in App Store Connect)

- [ ] **Paid Apps agreement** signed under Business → Agreements, Tax and Banking,
      with bank and tax details complete. Until this is active, paid products
      cannot be created, tested in sandbox, or sold. This is the usual reason a
      monetisation push stalls.
- [ ] Decide the price and period (see step 1).

## 1. Product decisions (yours)

Three decisions I cannot make for you.

**a. What stays free.** My recommendation, based on what the app already does:

| Free | Paid |
| --- | --- |
| Natal chart and the big three | Weekly and monthly forecasts |
| Core numbers, personal day | Cosmic Circle and compatibility reports |
| One profile | Solar arcs, lunar returns, profections, relocation |
| Daily reading, moon widget | Journal history and pattern analysis |

The advanced techniques are the strongest paid hook: they are genuinely rare in
consumer apps, expensive to build, and they are the same argument that answers
guideline 4.3.

**b. Price.** The category sits around £8–12/month with an annual discount.
A reasonable start: **£4.99/month, £34.99/year** — undercutting the
subscription-heavy competition while leaving room to raise later.

**c. Free trial.** A 7-day introductory offer is standard and lifts conversion,
at the cost of some churn. Recommended.

## 2. App Store Connect setup

- Subscription group "AstroNumeric Premium" with monthly and annual products.
- Localized display names and descriptions in all five languages.
- A review screenshot of the paywall, which Apple requires for each product.
- Mirror the same products into `Resources/StoreKit/Products.storekit` so the
  app can be run and tested without the sandbox.

## 3. Client implementation

**`StoreService`** (new, `Core/Services`)
- Load products with `Product.products(for:)`.
- Purchase, and listen to `Transaction.updates` for renewals and refunds.
- Derive entitlement from `Transaction.currentEntitlements` — this works
  offline, survives reinstall, and restores through the Apple ID, which fits the
  app's local-first, no-accounts design.
- Expose `isSubscribed` as observable state for the UI.

**`PaywallView`** (new, `Features/Premium`)
- Both products with prices from StoreKit, never hardcoded.
- Apple requires on the same screen: price, period, what auto-renews, a
  **Restore Purchases** button, and links to terms and the privacy policy.
- Localized in all five languages; the localization CI job will enforce that.

**Gating**
- One `PremiumGate` modifier so the check is written once rather than per screen.
- Applied to the paid features listed in step 1.

## 4. Server-side entitlement (phase 2, optional)

The forecasts a subscriber pays for are computed by our API, which is public. If
that becomes worth protecting:

- The app already holds an anonymous per-install key (`FriendsOwnerKey`, from
  #6). Send the signed transaction (JWS) with that key; the backend verifies it
  against Apple's App Store Server API and records an entitlement against the
  key. No account, no personal data.
- **Privacy consequence:** storing a transaction id makes **Purchases** a
  collected data type — not linked, app functionality. The App Privacy answers
  and `privacy-security-audit.md` would need updating before that ships.

Phase 1 can ship without this. Client-side entitlement is normal for a
local-first app, and the exposure is an unauthenticated API that is already
public today.

## 5. Tests

- `StoreKitTest` unit tests against the local `.storekit` file: purchase grants
  entitlement, expiry revokes it, restore re-grants, a refund revokes.
- A gating test: the premium modifier hides content when `isSubscribed` is false.
- These run in the `ios-tests` CI job added in #14, so the paywall cannot
  silently break.

## 6. Submission

- Ship as **1.1**, after 1.0.1 is approved. Never in a first submission.
- Review notes: how to reach the paywall, that sandbox purchases need no demo
  account, and what free users still get.
- Expect scrutiny of the paywall itself: Apple rejects unclear pricing, missing
  restore buttons and missing terms links more often than it rejects the app.

## Rough effort

| Step | Effort |
| --- | --- |
| ASC setup and paperwork | yours, mostly waiting |
| StoreService and entitlement | 1 day |
| Paywall, localized | 1–2 days |
| Gating and tests | 1 day |
| Server verification (phase 2) | 2 days |

About a week for phase 1, once the Paid Apps agreement is active.
