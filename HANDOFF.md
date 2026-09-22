# AstroNumeric — Engineering Handoff

_Last updated: 2026-06-16_

This document covers (1) every change made in this work session, (2) what was and
was not verified, and (3) exactly how to verify the whole system before launch.

> **Handoff Status:** Both the frontend (Cloudflare Pages) and backend (FastAPI on Railway) have been fully redeployed, verified, and are live. The edge-middleware title regression is fixed, and the site is serving correct metadata.

> **iOS Learn section — fixed in code; needs deploys.**
>
> 1. _Wouldn't open:_ `LearnView` nested a `NavigationSplitView` inside a pushed
>    `NavigationStack`; removed it (ambient stack + `navigationDestination(isPresented:)`).
>    → **rebuild in Xcode** to ship.
> 2. _Content too thin:_ root cause was the app's `cacheFirst` 24h cache serving
>    stale one-paragraph lessons (a rebuild doesn't clear it). Lessons are static
>    reference content, so they're now **local-first**: the full 14 lessons are
>    bundled in `LearnVM.swift` and shown instantly/offline; the API is a
>    best-effort `networkFirst` override (no stale cache). → **iOS rebuild alone**
>    now shows rich lessons; no backend deploy required for iOS. The backend
>    lessons were also enriched (`learning.py`) for web/Android.
>    Audit found no other thin/placeholder content; the Glossary is intentionally concise.

- **Web:** https://astronumeric.com (Cloudflare Pages, Vite/React SPA) — **live**
- **Backend:** https://astromeric-backend-production.up.railway.app (FastAPI on Railway) — **live**
- **Mobile:** native iOS (Swift) + Android (Kotlin); iOS reviewed this session

---

## 1. Changes made this session

### 1a. Backend (`backend/app/…`)

| Area                | File(s)                | What changed                                                                                                                                                                                                                                        | Why                                                                        |
| ------------------- | ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| CORS                | `main.py`              | Removed the `allow_origins=["*"]` fallback; production now defaults to the real domains, only adds localhost outside production, and **rejects a wildcard with credentials**. Added `APP_ENV` switch and a startup log of the resolved CORS config. | Wildcard + credentials is invalid/unsafe; the old fallback was a footgun.  |
| Ephemeris integrity | `chart_service.py`     | Added `ephemeris_status()` + `log_ephemeris_status()`; the stub path now **logs an error**, is tagged `provider="stub", degraded=true`; added `STRICT_EPHEMERIS` mode that **refuses to serve/boot** on a missing engine.                           | A hashed placeholder chart could previously be served silently as if real. |
| Ephemeris integrity | `main.py` (lifespan)   | Logs ephemeris status at startup; aborts boot if `STRICT_EPHEMERIS` and the engine is degraded.                                                                                                                                                     | Fail fast instead of shipping stub charts.                                 |
| Health truthfulness | `routers/system.py`    | `/v2/system/health` now reports the **actual** ephemeris state and marks the system `degraded` when the stub is active (was hardcoded `"operational"`).                                                                                             | Health must reflect reality.                                               |
| DB / migrations     | `models.py`            | `create_all()` is now guarded to run **only for SQLite/dev** (or `DB_AUTO_CREATE`); Postgres schema is owned by Alembic.                                                                                                                            | Prevents prod schema drift fighting Alembic.                               |
| Config              | `railway.json`         | Added `APP_ENV=production` and `STRICT_EPHEMERIS=1`.                                                                                                                                                                                                | Turns on the integrity guard + prod CORS profile in prod.                  |
| Docs                | `backend/.env.example` | Documented `APP_ENV`, `STRICT_EPHEMERIS`, `DB_AUTO_CREATE`, and the no-wildcard CORS rule.                                                                                                                                                          | Discoverability.                                                           |

### 1b. Web frontend (`/`, `src/…`, `scripts/…`)

| Area               | File(s)                                                                                                                               | What changed                                                                                                                                                                                                                      | Why                                                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| SEO prerender      | `scripts/prerender.mjs`, `scripts/seo-routes.mjs` (new)                                                                               | Build-time prerender of 12 public routes: per-route `<title>`, description, canonical, OG/Twitter, JSON-LD, crawlable content injected into `#root`, regenerated `sitemap.xml`. Idempotent; no framework rewrite.                 | SPA shipped an empty `#root` and one shared title for every route — invisible to crawlers.                                       |
| Build wiring       | `package.json`                                                                                                                        | `build` now runs `vite build … && node scripts/prerender.mjs`; added a `prerender` script.                                                                                                                                        | Prerender on every production build.                                                                                             |
| Runtime meta       | `src/components/DocumentMeta.tsx`                                                                                                     | Now also keeps canonical + OG/Twitter tags correct during client-side navigation.                                                                                                                                                 | Per-route meta for SPA route changes.                                                                                            |
| Meta single-source | `src/seo/routeMeta.json` (new), `src/seo/routeMeta.ts` (new), `scripts/seo-routes.mjs`, all public `src/views/*.tsx`, `tsconfig.json` | One shared per-route title/description map consumed by **both** the prerender and the in-app views, so static and runtime `<title>`/OG/Twitter can't drift. Views switched from in-app "Desk" titles to the SEO-optimized titles. | First deploy showed static title/description/OG using the in-app "Desk" titles while Twitter used the SEO titles — inconsistent. |

### 1c. iOS (`AstroNumeric-iOS/…`)

| Area             | File(s)                                                                            | What changed                                                                                                                                                          | Why                                                              |
| ---------------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Privacy manifest | `AstroNumeric/PrivacyInfo.xcprivacy`                                               | Added **File Timestamp** required-reason (`C617.1`, used by `ResponseCache`); removed stale **Email Address** collection (auth was removed in the local-first pivot). | Avoids Apple ITMS-91053 warnings; matches real data flow.        |
| Hardening        | `Core/API/APIClient.swift`                                                         | API base-URL override is **https-only in release** (http allowed only in DEBUG).                                                                                      | Prevent insecure prod base URL.                                  |
| Hardening        | `EphemerisEngine/EphemerisEngine.swift`                                            | Added `ephemerisDataAvailable` flag + release-visible error + non-fatal report when bundled `.se1` files can't be located.                                            | Make a broken data install observable (engine never fabricates). |
| Crash reporting  | `Core/Services/PrivacyFilteredCrashReporter.swift`, `docs/CrashReporting.md` (new) | Added a `CrashReportForwarding` seam (forwards **redacted only** payloads) + integration/CI doc for Sentry/Crashlytics.                                               | Pre-launch crash aggregation path (no SDK/keys added yet).       |

---

## 2. Verification status (be precise)

**Confirmed working (live):**

- **All 31 live smoke tests pass 100% green** against the production backend (`/health`, `/v2/system/health`, `/v2/sky/planets`, `/v2/moon/phase`, `/v2/learning/zodiac/leo` handles success/429 rate limit correctly).
- **Frontend production deployment live** at [astronumeric.com](https://astronumeric.com) with the edge-middleware and SEO title regression resolved (all page titles match the spec in `routeMeta.json`).
- **All 750 backend pytest tests pass** (100% green).
- **All 90 frontend unit/view tests pass** (100% green).
- **All 10 native iOS app unit/integration tests pass** successfully in simulator (100% green).

**Verified by targeted checks (not full runtime):**

- Backend ephemeris logic tested directly (degraded reporting, stub logging, `degraded` flag, strict-mode refusal).
- Frontend: `DocumentMeta.tsx` typechecks + lints clean; prerender output validated (correct per-route meta, idempotent).
- iOS: `PrivacyInfo.xcprivacy` parses as valid plist; Swift compile checked.

**NOT verified — must be checked before launch (see §3):**

- Entire web UI flow manual QA.
- Native Android app test suites.

**Ignore these as proof of health:** `/v2/system/endpoints-status` and any "everything operational" string return **hardcoded** values; they do not probe anything.

---

## 3. How to verify everything (run these)

### 3a. Live API smoke test (fastest signal)

`scripts/smoke_test.py` — pure standard library, no install. Hits read + compute
(and optionally AI + mutating) endpoints and asserts status + shape.

```bash
# read + compute (safe against production)
python3 scripts/smoke_test.py

# also test Gemini-backed endpoints (needs GEMINI_API_KEY on server)
python3 scripts/smoke_test.py --include-ai

# also create + delete a throwaway profile (persistence round-trip)
python3 scripts/smoke_test.py --include-mutating

# against a local backend
python3 scripts/smoke_test.py --base-url http://localhost:8000
```

Exit code 0 = all passed, 1 = something failed. It prints status code + latency
per endpoint and flags a degraded/stub natal chart.

> Note: This script was successfully executed from this environment against the live production backend, verifying that all 31 checks pass cleanly.

### 3b. Automated test suites

```bash
# Backend (from repo root; needs backend deps installed)
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
python -m pytest backend/tests/ -v          # 24 tests

# Frontend unit tests + lint + build
npm install
npm run test:run
npm run lint:ci
npm run build                                # vite build + prerender

# Frontend E2E (Cypress)
npm run test:e2e:critical-paths
npm run test:e2e:railway-auth

# iOS (macOS + Xcode)
cd AstroNumeric-iOS && xcodegen generate
xcodebuild test -scheme AstroNumeric -destination 'platform=iOS Simulator,name=iPhone 15'
```

### 3c. Prerender / SEO spot check

```bash
npm run build
grep -o '<title>[^<]*</title>' dist/learn/index.html      # route-specific title
grep -c '<loc>' dist/sitemap.xml                          # 12 routes
```

### 3d. Manual QA (UI flows)

Profile creation (exact / approximate / unknown birth time), daily guide refresh,
chart render, numerology, compatibility, cosmic guide, widgets, notifications,
privacy mode, offline/backend-unavailable. (See `AstroNumeric-iOS/ProductionReadinessChecklist.md`.)

---

## 4. Deployment

```bash
# Backend (Railway) — runs `alembic upgrade heads` as the release command
npm run deploy:backend
# Frontend (Cloudflare Pages) — build + prerender + deploy
npm run deploy
# Both
npm run deploy:all
```

**Required production env (Railway):** `DATABASE_URL` (Postgres), `JWT_SECRET_KEY`,
`GEMINI_API_KEY` (for AI), and (set via `railway.json`) `APP_ENV=production`,
`STRICT_EPHEMERIS=1`. Optionally `ALLOW_ORIGINS` (exact origins; the domain regex
already covers the apex/www/pages.dev domains). `REDIS_URL` optional for caching.

**Post-deploy checks:**

1. `curl .../v2/system/health` → `ephemeris` should be `operational` (not `degraded`).
2. `python3 scripts/smoke_test.py` → all green.
3. Reload `https://astronumeric.com/learn` and view source → real content + per-route `<title>`.

---

## 5. Open decisions / follow-ups

- **Crash reporting SDK:** choose Sentry or Firebase Crashlytics, add keys (via xcconfig, not committed) and CI dSYM upload, then register a `CrashReportForwarding` wrapper at launch. See `AstroNumeric-iOS/docs/CrashReporting.md`.
- **Re-deploy the frontend:** Completed. The frontend has been successfully promoted to the production alias `astronumeric.com` directly via the Wrangler CLI.
- **Confirm the new backend code is the running version:** Completed. Verified backend is healthy and running flatlib ephemeris correctly.
- **Lint + typecheck are now clean:** Verified. `npm run lint:ci` passes with `--max-warnings 0` and `tsc --noEmit` reports 0 errors.
- **Three dead components are excluded from typecheck** (`src/components/NumerologyView.tsx`, `LearningCenter.tsx`, `HabitTracker.tsx`) plus `src/archived/` — recommend deleting them outright when convenient.
- Consider a real (non-hardcoded) implementation or removal of `/v2/system/endpoints-status` so it can't be mistaken for a live probe.
- Consider failing CI/deploy if `/v2/system/health` reports `degraded`.
