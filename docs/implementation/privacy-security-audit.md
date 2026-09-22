# Privacy & security audit log

A record of privacy and security findings, the fixes shipped for them, and any
production data that was removed as part of a fix. Newest first.

## 2026-09-22 — pre-submission privacy review

### 1. Friend lists were readable across devices (fixed)

**Finding.** `/v2/friends/*` was unauthenticated and keyed only by `owner_id`,
and the iOS app sent its local profile id (`-1` on every device). Anyone could
read or change another install's friend list by guessing a small integer.

**Fix.**

- `a8bd727` (#5) — backend rejects guessable owner ids with `403
  FRIENDS_OWNER_KEY_REQUIRED`; only a UUID or 32–64 hex characters is accepted.
  Deployed and verified: `list/-1`, `list/-2` and `list/1` all return 403.
- `2579326` (#6) — iOS derives the owner key from a random 256-bit install
  secret held in the Keychain: `SHA-256(secret + ":" + profileId)`.

**Production data.** The `friends` table held 2 rows: one under a secure key and
one under the test owner `privacy-audit-owner`. No rows under `-1` or `-2` had
ever existed, so no real user's friend data was exposed. The guessable row was
deleted on 2026-09-22 (1 row; 1 remaining).

**Still open.** Android continues to send a guessable id to the old paths, which
the backend rejects. It needs the per-install key and the header ported before
release — tracked as its own pre-release batch.

### 2. The owner key travelled in the URL (fixed)

**Finding.** The key is a bearer secret for a whole friend list, but it sat in
the path (`/v2/friends/list/{owner_id}`), where access logs, proxies and error
reports record it. `logger.info("Friend added", owner_id=...)` also wrote it to
our own logs.

**Fix.** `9b67618` (#9) — the key moves to the `X-Owner-Key` header, the path
segment and the request-body field are gone, and the key is no longer logged.
Verified in production: old path 404, missing or guessable header 403, valid
header 200.

### 3. Every App Store user would have reached an unpaid Gemini key (fixed)

**Finding.** Live AI was gated on `is_native_ios`, so any App Store install
would have sent its questions and chart data to a free-tier Gemini key. On that
tier Google may use prompts to improve its products, including human review.

**Fix.** `5edfd88` (#7) — AI now requires the `X-AI-Access` header to match the
`AI_ACCESS_CODE` environment variable (`hmac.compare_digest`). With the variable
unset, nobody reaches Gemini. Other callers get the built-in localized
responses. The code is stored in the Keychain on the owner's device only.

Verified in production: no code and wrong code both return `provider: fallback`;
the configured code returns `provider: gemini`.

### 4. The APNs token was uploaded but never used (fixed)

**Finding.** The app uploaded its push token to `/v2/notifications/register`,
but pushes are matched by `user_id` and iOS has no accounts, so the token could
never be used. It was a device-level identifier held for nothing.

**Fix.** `0de31b4` (#4) — the token stays on the device. The endpoint remains
because Android still calls it.

**Production data.** On 2026-09-22 the 2 rows in `device_tokens` with
`platform = 'ios'` were deleted. Android (7) and web (1) rows were left
untouched; 8 rows remain.

### 5. Disclosures did not match the implementation (fixed)

`0de31b4` (#4) and `bd06dec` (#8) removed HealthKit entirely, corrected the
calendar and photo permission strings, and brought the in-app and website
privacy text in line with what is actually sent and stored.

### App Store privacy answers supported by the above

| Data type | Answer |
| --- | --- |
| Precise Location (birth coordinates) | Collected, **not linked**, App Functionality |
| Other Data Types (birth date/time, optional calendar day/time) | Collected, **not linked**, App Functionality |
| Contacts (friend and partner profiles) | Collected, **not linked**, App Functionality |
| Name | Not collected — sent for each calculation, never stored |
| Other User Content | Not collected — no third-party AI provider receives it |
| Device ID | Not collected — the APNs token stays on the device |
| Diagnostics, Usage Data | Not collected — no analytics or crash-reporting SDK |
| Tracking | No |

"Not linked" throughout, because the app has no accounts and uploads no device
identifier: stored rows hang off a random per-install key that identifies no one.
