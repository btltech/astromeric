# AstroNumeric parity plan: iOS app, website, Android app

_Drawn up 2026-09-30, from audits of all three against `main` (plus open PRs #33–#35). This replaces `AstroNumeric-Android/PARITY_PLAN.md` (June 2026)._

The iOS app is the reference. The website and the Android app should do what it does, apart from the deliberate exceptions below. Each gap lists where to port from, so it can be picked up as a PR on its own.

## Deliberate differences (not gaps)

| Area | Rule |
| --- | --- |
| Oracle | **App only.** The website shows what it does and links to the App Store (`OracleAppShowcase`, PR #35). Android gets the same horary Oracle as iOS. |
| AI | Unlimited AI only on the owner's device, unlocked with the access code. Other app users get the built-in guide. Website visitors get **one free Gemini answer a day**, first come first served while Gemini's free quota lasts (PR #34, `backend/app/free_ai.py`). NVIDIA is never used for the public. Prompts never carry a name or birth date, time or place. |
| Device-only | Widgets, notifications, Siri / app shortcuts, calendar context, the journal voice recorder and live activities have no website equivalent. |

## Status at a glance

✅ matches iOS · ⚠️ works but differs or has bugs · ❌ missing or broken

| Feature | Website | Android |
| --- | --- | --- |
| Daily / weekly / monthly reading | ⚠️ reads an old response shape, so the headline, score and transits don't show | ✅ |
| Weekly days you can tap | ❌ | ❌ |
| Home daily brief | ❌ marketing page with a sample "today's signal" | ✅ (error text needs work) |
| Natal chart | ❌ cast at 0°, 0° UTC (birthplace dropped) | ✅ |
| Advanced charts (progressions, synastry, composite) | ❌ | ✅ |
| Numerology | ⚠️ month/day numbers missing, no method toggle | ⚠️ none of the new library (daily, lifelong, yearly, karmic debt) |
| Compatibility | ⚠️ saved profiles only; strengths/challenges hidden | ✅ |
| Relationships / Friends | ❌ | ❌ Friends broken against the current server |
| Year Ahead | ⚠️ no year picker or life phase | ✅ |
| Timing advisor | ✅ | ✅ |
| Tarot | ✅ | ✅ |
| Moon phase, ritual, events | ⚠️ no ritual or events list | ❌ ritual screen fails to load |
| Affirmation, birthstones | ❌ | ✅ |
| Oracle | ✅ showcase (app-only) | ⚠️ old random server answer |
| Learn (22 lessons, 3 courses) | ⚠️ lessons ✅, courses ❌ | ⚠️ lessons online only, courses ❌ |
| Journal | ✅ (more than iOS) | ✅ |
| Habits | ❌ | ✅ |
| Profiles (edit, delete, time confidence, export) | ❌ | ⚠️ birthplace search takes the first match |
| AI rules and prompt privacy | ✅ after PR #34 | ❌ AI shown to everyone; name and birth details sent |
| Help / FAQ / user guide | ❌ | ✅ |
| Auto-scroll to results | ❌ | ❌ |
| Translations (es, fr, ne, ro) | ⚠️ files exist, no language switcher shown | ❌ about 95% missing |
| Store / release | n/a | ❌ no release signing, R8 or CI |

## Website gaps

Paths are relative to the repo root. iOS paths are under `AstroNumeric-iOS/AstroNumeric/`.

### P0: wrong or broken for users

| # | Gap | Port from (iOS) | Change |
| --- | --- | --- | --- |
| W1 | **Natal chart ignores the birthplace.** `fetchNatalProfile` sends a nested `location`, but the server's `ProfilePayload` is flat, so the chart is cast at 0°, 0° UTC and the rising sign and houses are wrong. | `Chart/ChartVM.swift` | `src/api/client.ts` `fetchNatalProfile`: send flat `latitude`, `longitude`, `timezone` |
| W2 | **Every new website profile gets timezone "UTC".** `LocationAutocomplete` calls `/geocode/timezone`, which returns 404 (it only existed in the old `main_legacy.py`). Birth times are then read as UTC. | `Profile/EditProfileVM.swift` (placemark time zone) | add a v2 timezone route in the backend (or look it up in the browser); `src/components/LocationAutocomplete.tsx` |
| W3 | **A sample person fills in missing details.** When a profile has no birth time or place, the chart, year-ahead and numerology pages quietly use "Amara Lewis, 08:30, London". | – | `src/views/ProductExperienceView.tsx`, `YearAheadView.tsx`, `NumerologyDeskView.tsx`: say what's missing instead |
| W4 | **Reading page reads an old response shape.** The title is always "Daily outlook ready"; the summary, score, transits, section ratings and daily guidance never show; chat context is empty. | `Reading/ReadingResultView.swift` | `src/types.ts`, `client.ts` `fetchForecast`, `FortuneResult.tsx`, `SectionGrid.tsx` |
| W5 | **Share card shows "Star", "Shadow", "Aether".** It also always prints the name (iOS can hide it). | `Reading/ShareCardView.swift` | `src/components/CosmicCard.tsx` |
| W6 | **"Explain This Reading" fails silently for everyone.** The endpoint needs a paid, signed-in user and only returns built-in text for daily, weekly and monthly anyway. | iOS hides it without the owner code | remove the button (`FortuneResult.tsx`) |
| W7 | **Follow-up chat says "your reading is already loaded" but sends none of it.** | – | `FortuneResult.tsx`: send the reading's headline and signs as context, or change the wording |
| W8 | **Shared comparison links go nowhere and carry birth data in the URL.** The page was deleted; the iOS weekly view also shares these links. | `Reading/WeeklyVibeView.swift` | `WeeklyVibe.tsx`, `src/utils/comparison.ts`, `App.tsx`; iOS share URL |
| W9 | "(OPTIONAL)" shown twice on the birth-time field. | – | `FortuneForm.tsx` |
| W10 | Dates shift back a day west of UTC (`new Date('YYYY-MM-DD')`). | – | `WeeklyVibe.tsx`, `FortuneResult.tsx` |
| W11 | Readings claim an exact birth time: missing times are sent as 12:00 and location 0, 0. | `ReadingVM` sends nil | `src/hooks/useReading.ts` |
| W12 | Notification preferences always get 401 (no sign-in header sent). | – | `client.ts` alert preferences, `NotificationSettings.tsx` |

### P1: missing core features

| # | Gap | Port from (iOS) | Change |
| --- | --- | --- | --- |
| W13 | Home daily brief: today's snapshot, next move, personal day and moon cards, quick actions, weekly card, ±7-day scrubber. | `Home/HomeView.swift`, `HomeVM.swift` | `src/views/HomeSupportView.tsx` (the unused `HomeLiveDesk`, `HomeChartStrip`, `HomeTimingRail` can be reused) |
| W14 | Tap a weekly day for its forecast (the server already sends it). | `Reading/WeeklyVibeView.swift` | `WeeklyVibe.tsx`, `client.ts` `ForecastDay` |
| W15 | Advanced charts: progressions, synastry, composite. | `Charts/AdvancedChartsView.swift` and friends | new views under /charts |
| W16 | Full natal detail: every placement, dignity, house, retrograde, aspects, houses. | `Chart/ChartView.swift` | `ProductExperienceView.tsx` (salvage the unused `components/ChartView.tsx`) |
| W17 | Numerology: show personal month and day numbers; Pythagorean / Chaldean toggle. | `Numerology/NumerologyView.swift` | `NumerologyDeskView.tsx`, `client.ts` |
| W18 | Compatibility: compare with anyone (not just saved profiles); strengths, challenges, advice; save a relationship; data-quality note. | `Compatibility/CompatibilityView.swift` | `ProductExperienceView.tsx` |
| W19 | Relationships list (filter, detail, delete) and Friends ("Cosmic Circle") with the per-install owner key. | `Relationships/*`, `Core/Utilities/FriendsOwnerKey.swift` | `src/views/RelationshipsView.tsx`, new client calls |
| W20 | Habits, kept in the browser (the server's habit list is shared by everyone, see B2). | `Habits/*` | new view; delete the dead habit calls in `client.ts` |
| W21 | Profiles: edit, delete, switch; time confidence; keep profiles saved (not per session); hide sensitive details; export and import. | `Profile/*`, `Core/ProfileExporter.swift` | `ProfileView.tsx`, `ProfileSelector.tsx`, `useProfiles.ts`, `store/useStore.ts` |
| W22 | Daily guide: do's and don'ts, morning brief; stop using "Guest" and a sample birth date. | `Tools/DailyFeaturesView.swift` | `DailyFeaturesCard.tsx`, `CosmicToolsView.tsx` |
| W23 | Year Ahead: year picker and life-phase card. | `Tools/YearAheadView.swift`, `LifePhaseCard.swift` | `YearAheadView.tsx` |
| W24 | Moon: ritual, moon sign, events list. | `Tools/MoonPhaseView.swift`, `MoonEventsView.swift` | `MoonPhaseCard.tsx`, `client.ts` |
| W25 | Affirmation page and birthstone guide. | `Tools/AffirmationView.swift`, `BirthstoneGuidanceView.swift` | new components |
| W26 | Scroll to results, scroll to top on page change, working `#section` links. | `SharedComponents/RevealAnimations.swift` (`scrollsIntoView`) | `ReadingView.tsx`, `ProductExperienceView.tsx`, `App.tsx` |

### P2: polish

- W27 Learn: the three named courses with per-course progress (`Explore/ExploreView.swift`).
- W28 Help: FAQ and user guide (`Profile/HelpView.swift`, `UserGuideView.swift`).
- W29 Settings: send the reading tone; show the language switcher (translations already exist); high-contrast and large-text options.
- W30 Remove developer wording shown to users ("The iOS benchmark leads with…", "Phase 1 keeps auth…").
- W31 Label the home page's "today's signal" as a sample until W13 replaces it; add Journal to the navigation.
- W32 Mount the error boundary so one broken panel doesn't blank the site.
- W33 Birthplace: keep the region, offer every timezone in the manual fallback, and mention the OpenStreetMap lookup in the privacy policy.
- W34 Delete dead code with wrong response shapes: about 20 unused components and hooks, the old relationship and course calls, and the leftover Oracle strings.

## Android gaps

Kotlin paths are under `AstroNumeric-Android/app/src/main/kotlin/com/astromeric/android/`.

### P0: broken today or blocks release

| # | Gap | Port from (iOS) | Change |
| --- | --- | --- | --- |
| A1 | **Friends fails against the current server.** It sends the profile id in the URL instead of the per-install key in `X-Owner-Key`, so list, add and remove fail. | `Core/Utilities/FriendsOwnerKey.swift`, `Core/API/Endpoints.swift` | new `FriendsOwnerKey.kt`; `core/data/remote/AstroRemoteData.kt`, `FriendModels.kt`, `FriendsScreen.kt`, `RelationshipsScreen.kt` |
| A2 | **Moon ritual fails to load.** The server now sends `avoid` as one string; Android expects a list. | – | `core/model/ToolModels.kt` and the moon screens |
| A3 | **Support email can't receive mail** (support@ and privacy@astromeric.app, 8 places). | `Profile/HelpView.swift` | `res/values/strings.xml`, `SupportScreens.kt`, `PrivacyScreen.kt`, `ProfileScreens.kt` |
| A4 | **Health data.** Android reads heart rate, sleep and steps from Health Connect and puts them in AI prompts; iOS removed Apple Health. **Decision needed** (see below). | commit 0de31b4 | manifest, `feature/guide/*Health*`, `BioCosmicCorrelator.kt`, `PrivacyScreen.kt` |
| A5 | **Release setup:** no signing config, R8 off, no Android job in CI, Play Data Safety form not filled in. Version 1.0.0 (2). | `.github/workflows/ci.yml` iOS jobs | `app/build.gradle.kts`, `proguard-rules.pro`, `ci.yml` |

### P1: privacy, AI and core features

| # | Gap | Port from (iOS) | Change |
| --- | --- | --- | --- |
| A6 | **AI shown to everyone.** No access code or `X-AI-Access` header; built-in replies look like AI answers. | `Core/Utilities/AIAccessCode.swift`, `Features/Profile/AIAccessCodeView.swift`, `SharedComponents/FloatingAIButton.swift` | new `AIAccessCode.kt` + OkHttp header; gate the guide button and "explain" buttons; 7 taps on the version line |
| A7 | **Name and birth details sent** in Guide prompts (masked only if a setting is on, default off) and with every Oracle question. | `CosmicGuide/CosmicGuideVM.swift` | `feature/guide/GuidePromptBuilder.kt`, `OracleScreen.kt` |
| A8 | **Birthplace search takes the first match** ("Lagos" can become Portugal). | `Profile/EditProfileVM.swift` | `feature/profile/ProfileEditorScreen.kt` |
| A9 | **Oracle:** port the horary Oracle (topic detection, horary chart, "how it decided", location on device). Needs a new JNI call for house cusps and planet speeds. | `EphemerisEngine/HoraryJudge.swift`, `EphemerisEngine.swift` `calculateHoraryChart`, `Features/Tools/OracleView.swift` | new `core/ephemeris/HoraryJudge.kt`; `LocalSwissEphemerisEngine.kt`, `SwissEphemerisBridge.kt`, `cpp/swiss_ephemeris_jni.cpp`, `OracleScreen.kt`; remove the duplicate card in `ToolsScreen.kt` |
| A10 | **Numerology library:** daily written reading, lifelong, yearly and monthly readings, karmic debts, each number beside its text; stop recomputing month and day on the phone (it collapses 11/22/33). | `Core/API/Models/NumerologyModels.swift`, `Features/Numerology/NumerologyView.swift` | `core/model/NumerologyModels.kt`, `NumerologyChartTab.kt`, `NumerologyScreen.kt` |
| A11 | **Translations:** 1,592 of 1,672 strings missing in each of es, fr, ne, ro; add a CI check like iOS. | `scripts/check_ios_localization.py` | `res/values-*/strings.xml` |

### P2: polish

- A12 Learn: bundle `lessons.json` for offline use and group into the three courses.
- A13 Scroll to results (a shared modifier like iOS `scrollsIntoView`).
- A14 The small AI dot that expands on tap (after PR #33).
- A15 Weekly days you can tap; show `birth_time_assumed` and `data_confidence`; written error messages on Home.
- A16 TalkBack pass matching iOS #13.
- A17 Check the iOS fixes in #12, #24 and #30 (silent failures in Habits, Journal and Year Ahead; share-card contrast) against Android.
- A18 Premium: `isPremiumUser` is hard-coded to true; remove billing or decide on it (see decisions).

## Backend issues found along the way

| # | Issue | Change |
| --- | --- | --- |
| B1 | No v2 timezone lookup for the website (W2). | add `GET /v2/geocode/timezone` |
| B2 | `/v2/habits/list` keeps one in-memory list shared by every caller, and it's lost on deploy. | make habits device-local on every platform, or key them per install |
| B3 | `/v2/daily/yes-no` seeds its pick with Python `hash()`, which changes per server process. It is used only by Android until A9. | retire after A9 |
| B4 | Six advanced-chart routes (solar arc, relocation, lunar return, profections, declinations, fixed stars) are used by Android but not by iOS or the website. | decide whether iOS and the website get them or Android drops them |

## Things the website or Android have that iOS doesn't

- **Website:** email accounts with cloud sync; reading history; PDF, copy and share of a reading; thumbs up/down per section; journal patterns; a timing week view; web push alerts; light/dark toggle.
- **Android:** Play Billing with a Premium screen (not active); Health Connect; exact-transit alarms; six extra advanced charts.

## Order of work

Each step is one or more PRs. Website fixes deploy on merge; Android needs disk space first (about 10 GB free for builds and an emulator).

1. **Website correctness (W1–W12, B1).** Birthplace, timezone, reading shape, share card, sample-profile removal, dead "explain" button, dates, notification sign-in. This is the most urgent: website charts are wrong today.
2. **Android broken and privacy (A1–A3, A6–A8, and A4 once decided).**
3. **Core features, both platforms:** website home brief, profiles, weekly days (W13, W14, W21, A15); numerology (W17, A10); relationships and friends on the website (W18, W19); Android Oracle (A9).
4. **Remaining features:** website advanced charts, natal detail, habits, daily guide, Year Ahead, moon, affirmation, birthstones (W15, W16, W20, W22–W25); scrolling (W26, A13); Learn courses (W27, A12); Android translations (A11).
5. **Release and clean-up:** Android release setup (A5, A18); website polish and dead-code removal (W28–W34); backend clean-up (B2–B4).

## Decisions needed from the owner

1. **Health Connect on Android (A4):** remove it to match iOS (recommended), or keep it and complete Google's health-data declaration and in-app disclosure.
2. **Premium / billing on Android (A18):** remove it, or plan paid features on iOS too.
3. **Website accounts:** keep email sign-in and cloud sync (the app has none), or remove them to match the app.
4. **Extra advanced charts (B4):** add them to iOS and the website, or drop them from Android.
5. **Disk space:** free about 10 GB so Android can be built and tested.

## How each fix is checked

- **Website:** `npx vitest run`, a type-check, and a look in the browser against a local API.
- **Backend:** `pytest` (and Postgres for migrations).
- **iOS:** unit tests on the one iPhone 17 Pro simulator.
- **Android:** `./gradlew assembleDebug testDebugUnitTest lint`, then the emulator.
- **Tracking:** each PR ticks off its row in this file.
