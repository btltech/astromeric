# Android Native Parity Audit

## Goal

Build a full native Android version of AstroNumeric that matches the current iOS product feature-for-feature, behavior-for-behavior, and fallback-for-fallback rather than shipping a reduced companion app.

This audit is based on the current iOS code in `AstroNumeric-iOS/` and the current backend contracts in `backend/app/`.

## Executive Summary

- There is no Android client in this repository today.
- The iOS app is a substantial native product, not a thin API wrapper.
- Android parity is feasible because most user-facing product flows already map to explicit backend endpoints under `/v2`.
- The main parity risks are the iOS-only native surfaces:
  - local Swiss Ephemeris fallback
  - WidgetKit + App Group data sharing
  - HealthKit integration
  - Speech framework voice journaling
  - iOS background task scheduling
  - APNs-specific notification flow
- The Android implementation should be backend-first and local-first:
  - backend-first for charts, readings, compatibility, AI, learning, relationships, timing, and daily tools
  - local-first for profiles, cached content, habits fallback, journal fallback, privacy preferences, and offline behavior

## Parity Rules

These rules define what “pound for pound” means for this port.

1. The Android app must support the same primary product areas as iOS: Home, Tools, Charts, Profile, plus Explore/Learn/Habits/Relationships and the same supporting flows.
2. The same profile fields and data-quality rules must exist on Android: exact time, approximate time, unknown time, birthplace lookup, timezone, and privacy-safe payload handling.
3. The same backend endpoints and payload semantics should be used wherever they already exist instead of inventing Android-only behavior.
4. When iOS has local fallback behavior, Android must also degrade gracefully instead of failing hard.
5. Privacy behavior must match: local-first storage, “hide sensitive details”, redacted sharing, and optional health/calendar/speech contexts.
6. Where iOS labels a feature as calculated, hybrid, interpretive, or reference, Android should preserve the same product meaning, not just similar UI.

## Current Product Architecture

### iOS

- App shell: `AstroNumeric-iOS/AstroNumeric/ContentView.swift`
- App lifecycle/background work: `AstroNumeric-iOS/AstroNumeric/AstroNumericApp.swift`
- Global local-first state: `AstroNumeric-iOS/AstroNumeric/Core/Persistence/AppStore.swift`
- API client and typed endpoints:
  - `AstroNumeric-iOS/AstroNumeric/Core/API/APIClient.swift`
  - `AstroNumeric-iOS/AstroNumeric/Core/API/Endpoints.swift`
- Local ephemeris engine:
  - `AstroNumeric-iOS/AstroNumeric/EphemerisEngine/EphemerisEngine.swift`
  - `AstroNumeric-iOS/AstroNumeric/EphemerisEngine/swisseph/`

### Backend

- FastAPI app: `backend/app/main.py`
- Major route families:
  - profiles, charts, forecasts, numerology, compatibility, cosmic guide, friends, relationships, habits, journal, learning, timing, daily features, moon, transits, notifications

## Recommended Android Technical Stack

- Language: Kotlin
- UI: Jetpack Compose
- Navigation: Navigation Compose
- State: ViewModel + StateFlow
- Networking: Retrofit + OkHttp + Kotlinx Serialization or Moshi
- Persistence: Room + DataStore
- Background work: WorkManager
- Notifications: FCM + Notification Channels
- Widgets: Glance or AppWidget depending on complexity
- Speech: `SpeechRecognizer` with optional cloud fallback if needed
- Health: Health Connect as the Android equivalent for the optional biometric layer
- Location: Fused Location Provider + backend geocoding/location search where possible

## Feature Audit And Android Implementation Plan

### 1. App Shell And Navigation

Current iOS surface:

- Root tabs are defined in `AstroNumeric-iOS/AstroNumeric/ContentView.swift`
- Primary tabs: Home, Tools, Charts, Profile
- Overlay AI entry point: `AstroNumeric-iOS/AstroNumeric/SharedComponents/FloatingAIButton.swift`

Android implementation:

- Build a Compose app shell with the same four primary tabs.
- Preserve the floating Cosmic Guide entry point outside the Profile tab.
- Mirror first-run prompt and first-run completion flows before adding feature depth.

Parity requirements:

- Same default landing flow
- Same tab structure
- Same first-run modal behavior
- Same tab deep-linking behavior from notifications

Risk:

- Low

### 2. Profile Creation, Editing, And Data Quality

Current iOS surface:

- `AstroNumeric-iOS/AstroNumeric/Features/Profile/EditProfileView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Profile/EditProfileVM.swift`
- `AstroNumeric-iOS/AstroNumeric/Core/Persistence/AppStore.swift`

Behavior:

- Create/edit local profiles
- Support exact, approximate, and unknown birth time
- Use current location for birthplace assist
- Store profiles locally on disk
- Fetch natal signs after profile selection
- Use privacy-safe payloads when required

Backend dependencies:

- `/v2/profiles/`
- `/v2/charts/natal`

Android implementation:

- Implement the same profile model first, before building downstream features.
- Use Room for profile storage and DataStore for lightweight preferences.
- Preserve iOS profile semantics exactly, including unknown-time fallback and data-quality states.
- Implement Android location-based birthplace assist, but keep manual location entry fully supported.

Parity requirements:

- Same fields
- Same default/fallback logic for unknown birth time
- Same “local first, server optional” behavior
- Same redacted profile payload path

Risk:

- Medium due to birthplace/timezone UX and validation details

### 3. Home Dashboard

Current iOS surface:

- `AstroNumeric-iOS/AstroNumeric/Features/Home/HomeView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Home/HomeVM.swift`

Behavior:

- Daily dashboard
- Quick metrics
- Daily reading summary
- Weekly vibe preview
- Moon phase snapshot
- Quick tools
- Habits widget content
- Pull to refresh and preloading behavior

Backend dependencies:

- `/v2/forecasts/{daily,weekly,monthly}`
- `/v2/daily/reading`
- `/v2/daily/forecast`
- `/v2/daily/brief`

Android implementation:

- Build the Home screen after profile infrastructure and network layers are stable.
- Reuse the same backend-driven cards rather than recomputing home content on-device.
- Preserve refresh, caching, and profile-aware invalidation behavior.

Parity requirements:

- Same dashboard sections
- Same loading/error/empty behavior
- Same cache invalidation on profile change

Risk:

- Medium because it aggregates many feature slices

### 4. Readings And Forecasts

Current iOS surface:

- `AstroNumeric-iOS/AstroNumeric/Features/Reading/ReadingView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Reading/ReadingVM.swift`
- `AstroNumeric-iOS/AstroNumeric/Core/API/Endpoints.swift`

Behavior:

- Daily, weekly, monthly forecasts
- Reading history and scoped caching
- AI explanation support for readings

Backend dependencies:

- `/v2/forecasts/daily`
- `/v2/forecasts/weekly`
- `/v2/forecasts/monthly`
- `/v2/ai/explain`

Android implementation:

- Port this as a direct API-backed feature with local cache.
- Match iOS cache key behavior by day/week/month scope.
- Preserve tone-driven cache variation where the iOS app changes reading output by tone preference.

Parity requirements:

- Same scopes
- Same response rendering hierarchy
- Same explanation flow
- Same offline read-from-cache behavior

Risk:

- Low to medium

### 5. Charts

Current iOS surface:

- `AstroNumeric-iOS/AstroNumeric/Features/Chart/EmbeddedChartView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Chart/ChartVM.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Charts/ChartsView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Charts/SynastryChartView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Charts/CompositeChartView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Charts/ProgressionsView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Charts/AdvancedChartsView.swift`

Behavior:

- Natal chart is API-first and local-ephemeris fallback
- Support big three, placements, aspects, houses, points, chart metadata
- Support synastry, composite, progressed, and advanced views

Backend dependencies:

- `/v2/charts/natal`
- `/v2/charts/synastry`
- `/v2/charts/composite`
- `/v2/charts/progressed`

Android implementation:

- Treat backend chart responses as canonical on Android.
- Do not block the Android port on a local Swiss Ephemeris port.
- Ship local chart fallback only if it can match backend precision and metadata; otherwise use cached backend chart data for offline resilience.
- Preserve birth-time uncertainty messaging exactly.

Parity requirements:

- Same chart types
- Same metadata-driven uncertainty states
- Same interpretation of missing location or uncertain birth time
- Same big three, placements, houses, aspects, and chart point rendering depth

Risk:

- High because iOS has local ephemeris capability and Android currently would not

Decision:

- Phase 1 Android charts should be backend-canonical with persistent cache.
- Local ephemeris on Android is a later parity enhancement, not the initial blocker.

### 6. Numerology

Current iOS surface:

- `AstroNumeric-iOS/AstroNumeric/Features/Numerology/NumerologyView.swift`
- numerology entry point inside `AstroNumeric-iOS/AstroNumeric/Features/Charts/ChartsView.swift`

Backend dependencies:

- `/v2/numerology/core`
- `/v2/numerology/profile`
- `/v2/numerology/compatibility`

Android implementation:

- Port as API-backed with monthly cache semantics similar to iOS.
- Preserve support for numerology system selection where present.
- Match the existing information density, not just headline numbers.

Parity requirements:

- Same core numbers
- Same profile interpretation depth
- Same compatibility surface

Risk:

- Low

### 7. Compatibility And Relationships

Current iOS surface:

- `AstroNumeric-iOS/AstroNumeric/Features/Compatibility/CompatibilityView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Compatibility/CompatibilityVM.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Relationships/RelationshipsView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Relationships/FriendsView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Relationships/RelationshipsVM.swift`

Backend dependencies:

- `/v2/compatibility/romantic`
- `/v2/compatibility/friendship`
- `/v2/friends/add`
- `/v2/friends/list/{ownerId}`
- `/v2/friends/compare`
- `/v2/friends/compare-all`
- `/v2/relationships/timeline`
- `/v2/relationships/timing`
- `/v2/relationships/best-days/{sunSign}`
- `/v2/relationships/events`
- `/v2/relationships/venus-status`
- `/v2/relationships/phases`

Android implementation:

- Port compatibility first, then friends, then relationship timing/timeline layers.
- Preserve the ability to compare against either a saved profile or a manually entered second profile.
- Keep confidence notes and degraded-accuracy messaging when birth data is incomplete.

Parity requirements:

- Same romantic and friendship variants
- Same confidence scoring behavior
- Same friends management behavior
- Same relationship timeline and timing surfaces

Risk:

- Medium

### 8. Cosmic Guide AI

Current iOS surface:

- `AstroNumeric-iOS/AstroNumeric/Features/CosmicGuide/CosmicGuideView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/CosmicGuide/CosmicGuideVM.swift`

Behavior:

- Chat UI
- Tone selection
- Optional calendar context
- Optional biometric context
- Rich system prompt built from profile/chart context

Backend dependencies:

- `/v2/cosmic-guide/chat`

Android implementation:

- Match the full contextual prompt-building approach rather than a plain chat box.
- Support the same tone preference and the same opt-in context flags.
- Build Android-native calendar and health consent gates before enabling those contexts.

Parity requirements:

- Same message flow
- Same prompt context quality
- Same birth-time uncertainty rules
- Same consent gating for optional data sources

Risk:

- Medium to high because the prompt quality depends on local context assembly, not just the API call

### 9. Tools Hub And Daily Utility Features

Current iOS surface:

- `AstroNumeric-iOS/AstroNumeric/Features/Tools/ToolsView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Explore/ExploreView.swift`
- Tool screens include:
  - `DailyFeaturesView.swift`
  - `TimingAdvisorView.swift`
  - `TarotView.swift`
  - `OracleView.swift`
  - `AffirmationView.swift`
  - `MoonPhaseView.swift`
  - `MoonEventsView.swift`
  - `TemporalMatrixView.swift`
  - `YearAheadView.swift`
  - `BirthstoneGuidanceView.swift`

Backend dependencies:

- `/v2/daily/reading`
- `/v2/daily/forecast`
- `/v2/daily/do-dont`
- `/v2/daily/brief`
- `/v2/daily/affirmation`
- `/v2/daily/tarot`
- `/v2/daily/yes-no`
- `/v2/timing/advice`
- `/v2/timing/best-days`
- `/v2/timing/activities`
- `/v2/moon/phase`
- `/v2/moon/ritual`
- `/v2/year-ahead/life-phase`
- `/v2/sky/planets`

Android implementation:

- Build this hub from the same feature taxonomy used on iOS: calculated, hybrid, interpretive, reference.
- Reuse backend contracts wherever possible.
- Where iOS uses local calculations for live timing or moon state, prefer backend or cached-computed equivalents first, then add Android-local calculation later only if needed.

Parity requirements:

- Same tool set
- Same descriptions and product purpose
- Same live-timing vs interpretive distinction
- Same navigation entry points from Tools and Explore

Risk:

- Medium because this area spans many smaller features

### 10. Habits

Current iOS surface:

- `AstroNumeric-iOS/AstroNumeric/Features/Habits/HabitsView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Habits/HabitsVM.swift`

Behavior:

- Backend-backed habit CRUD and logging when available
- Local fallback when backend is unavailable
- Local categories and lunar guidance fallback

Backend dependencies:

- `/v2/habits/list`
- `/v2/habits/create`
- `/v2/habits/habit/{id}`
- `/v2/habits/log-entry`

Android implementation:

- Mirror the same mixed mode.
- Use Room for local cached habits and optimistic completion toggles.
- Keep lunar guidance fallback local if backend coverage remains partial.

Parity requirements:

- Same mixed online/offline behavior
- Same optimistic updates
- Same local fallback messaging

Risk:

- Medium because the backend is not the only source of truth here

### 11. Journal

Current iOS surface:

- `AstroNumeric-iOS/AstroNumeric/Features/Journal/JournalView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Journal/JournalVM.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Journal/VoiceRecorder.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Journal/JournalEmbedder.swift`

Behavior:

- Local-first journal entries in personal mode
- Backend reads/writes when authenticated/server-backed
- Optional prompts, stats, patterns, and report flows
- Voice-to-text journal capture

Backend dependencies:

- `/v2/journal/entry`
- `/v2/journal/outcome`
- `/v2/journal/prompts`
- `/v2/journal/readings/{profileId}`
- `/v2/journal/reading/{readingId}`
- `/v2/journal/stats/{profileId}`
- `/v2/journal/patterns/{profileId}`
- `/v2/journal/report`

Android implementation:

- Reproduce the same local-first storage policy using Room.
- Keep server sync conditional, not mandatory.
- Add Android speech capture only after the text-based journal flow is stable.

Parity requirements:

- Same local-mode behavior
- Same prompts and pattern surfaces
- Same outcome tracking
- Same ability to use the feature without cloud dependency

Risk:

- Medium because voice capture and local semantic indexing are platform-specific

### 12. Learn And Explore

Current iOS surface:

- `AstroNumeric-iOS/AstroNumeric/Features/Learn/LearnView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Learn/GlossaryView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Learn/LessonDetailView.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Explore/ExploreView.swift`
- `AstroNumeric-iOS/AstroNumeric/Core/Persistence/LearningProgressManager.swift`

Backend dependencies:

- `/v2/learning/modules`
- `/v2/learning/module/{id}`
- `/v2/learning/zodiac/{sign}`
- `/v2/learning/glossary`

Android implementation:

- Port Learn as a backend-backed content feature with local progress tracking.
- Port Explore as a curated discovery layer that links into Tools, Learn, Habits, and Relationships.

Parity requirements:

- Same module list and glossary access
- Same progress tracking concept
- Same curated Explore categories

Risk:

- Low

### 13. Notifications, Widgets, And Background Tasks

Current iOS surface:

- `AstroNumeric-iOS/AstroNumeric/AstroNumericApp.swift`
- `AstroNumeric-iOS/AstroNumeric/Core/Services/NotificationService.swift`
- `AstroNumeric-iOS/AstroNumeric/Core/Services/TransitNotificationScheduler.swift`
- `AstroNumeric-iOS/AstroNumeric/Core/Services/CachePrewarmScheduler.swift`
- `AstroNumeric-iOS/AstroNumeric/Core/Services/WidgetDataProvider.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Tools/NotificationSettingsView.swift`

Behavior:

- Daily reminder, moon events, habit reminders, timing alerts, transit alerts
- Background refresh and scheduling
- Widget data written by app process and read by widget process
- Transit scanning based on natal chart and settings

Backend dependencies:

- `/v2/transits/daily`
- `/v2/transits/subscribe`
- `/v2/notifications/register`

Android implementation:

- Replace APNs with FCM.
- Replace iOS background tasks with WorkManager.
- Replace WidgetKit/App Group data flow with Android widget update workers backed by Room/DataStore.
- Preserve user-facing alert types and frequency options exactly.

Parity requirements:

- Same notification categories
- Same alert preferences and cadence options
- Same proactive transit alert concept
- Same morning brief/widget refresh outcome even if the technical path differs

Risk:

- High because this area is tightly bound to Apple platform services today

### 14. Privacy, Sharing, Export, And Redaction

Current iOS surface:

- `AstroNumeric-iOS/AstroNumeric/Features/Profile/PrivacyView.swift`
- `AstroNumeric-iOS/AstroNumeric/Core/ProfileExporter.swift`
- `AstroNumeric-iOS/AstroNumeric/Features/Reading/ShareCardView.swift`

Behavior:

- Hide sensitive details preference
- Privacy explanation tied to actual data flow
- Export/import flows
- Share card generation with redaction-aware naming

Android implementation:

- Make this a first-class parity area, not post-launch polish.
- Preserve the hide-sensitive-details toggle globally.
- Build Android-native export/share flows only after the redaction behavior is defined and tested.

Parity requirements:

- Same redaction semantics
- Same privacy-first copy and behavior
- Same export/import capability where feasible

Risk:

- Medium

### 15. Localization And Accessibility

Current iOS surface:

- `AstroNumeric-iOS/AstroNumeric/Core/Services/LocalizationService.swift`
- `AstroNumeric-iOS/AstroNumeric/Core/Utilities/AccessibilityHelpers.swift`

Behavior:

- Language selection
- high contrast
- large text support
- reduced motion and accessible score/mood components

Android implementation:

- Preserve these settings explicitly in the app architecture, not as incidental Compose defaults.
- Mirror the same settings surface in Profile or app preferences.

Parity requirements:

- Same language support model
- Same large-text/high-contrast behavior intent
- Same accessible descriptions for chart/timing/score components

Risk:

- Medium if deferred too late

### 16. Health, Speech, Calendar, And Location

Current iOS surface:

- Health: `AstroNumeric-iOS/AstroNumeric/EphemerisEngine/HealthKitBridge.swift`
- Voice: `AstroNumeric-iOS/AstroNumeric/Features/Journal/VoiceRecorder.swift`
- Calendar: `AstroNumeric-iOS/AstroNumeric/Features/CosmicGuide/CosmicGuideVM.swift`, `CalendarOracle`
- Location: `AstroNumeric-iOS/AstroNumeric/Features/Profile/EditProfileVM.swift`

Android implementation:

- Health: Health Connect module, opt-in only
- Voice: Android SpeechRecognizer with on-device preference if available
- Calendar: Android calendar permission gate, same explicit opt-in model
- Location: Fused Location Provider for current-location birthplace assist

Parity requirements:

- Same optional/consent-based behavior
- Same ability to disable these integrations without breaking core app usage

Risk:

- High for health and speech if parity is defined as identical platform capability, medium if parity is defined as equivalent optional feature

## Features That Should Be Treated As Canonical Backend Contracts

These should be implemented on Android by consuming the same backend contracts as iOS:

- profiles
- forecasts/readings
- numerology
- compatibility
- charts
- cosmic guide
- learning
- relationships
- friends
- timing
- daily features
- transits
- notifications registration

## Features That Need Android-Specific Native Reimplementation

- app shell and navigation
- all UI components and animations
- local persistence layer
- widgets
- push plumbing
- background tasks
- health integration
- speech-to-text journaling
- location permission flow
- local chart fallback if we choose to support it

## Recommended Build Order

### Phase 0: Contract And Parity Baseline

- Freeze the iOS parity target from this document.
- Confirm profile schemas and endpoint models to reuse on Android.
- Define parity acceptance tests per feature before implementation begins.

### Phase 1: Foundation

- Create Android project structure
- Add networking, persistence, theming, navigation, and settings scaffolding
- Implement profile model, local storage, and app shell

Exit criteria:

- User can create/select/edit/delete profiles locally
- App has the same root navigation model as iOS

### Phase 2: Core Value Loop

- Home dashboard
- Daily/weekly/monthly readings
- numerology
- natal chart
- privacy-safe payload handling

Exit criteria:

- Android user can create a profile and get the same core guidance loop as iOS

### Phase 3: Depth Features

- compatibility
- relationships/friends
- advanced charts
- tools hub
- year ahead and timing
- learn and glossary

Exit criteria:

- Android covers the same content and analysis depth as the iOS middle-tier experience

### Phase 4: Local-First Lifestyle Features

- habits mixed mode
- journal mixed mode
- voice journaling
- sharing/export
- accessibility and localization

Exit criteria:

- Daily-use, retention, and privacy workflows match iOS expectations

### Phase 5: Native Platform Parity

- widgets
- background refresh
- proactive transit alerts
- Health Connect
- calendar context for Cosmic Guide

Exit criteria:

- Android closes the remaining platform-specific gap with iOS

## Hard Risks And Decisions

### Risk 1: Local Swiss Ephemeris Parity

Problem:

- iOS can fall back to on-device chart computation.
- Android currently has no equivalent implementation in this repo.

Decision:

- Do not block Android on a local ephemeris port.
- Use backend charts as the canonical source and persist them locally for offline reuse.
- Revisit Android local ephemeris only after core feature parity is stable.

### Risk 2: Widgets And Background Refresh

Problem:

- iOS widgets depend on app-computed shared data and Apple background mechanisms.

Decision:

- Rebuild widgets as Android-native widgets backed by Room/DataStore plus WorkManager refresh.
- Match outcomes, not the iOS internals.

### Risk 3: Health And Voice Feature Drift

Problem:

- Android platform equivalents exist, but they are not one-for-one with Apple frameworks.

Decision:

- Ship them as optional parity modules with the same user promise, not identical implementation details.

## Definition Of Done For “Pound-For-Pound” Parity

The Android app is not done when it merely reaches feature category parity. It is done when:

1. A user can complete the same primary journeys on Android that they can on iOS.
2. The same missing-data and uncertain-data warnings appear in the same situations.
3. The same privacy guarantees and redaction behavior exist.
4. The same local-first/offline behavior exists where iOS already supports it.
5. The same tool set exists with the same product meaning.
6. Notifications, widgets, and background refresh produce equivalent user-visible results.
7. Charts, numerology, compatibility, and AI responses are consistent with the same backend contracts.

## Recommended Next Step

Use this document as the source of truth and create the Android project against it in this order:

1. Foundation and profile infrastructure
2. Home, readings, numerology, natal chart
3. Tools, compatibility, learning, relationships
4. Habits, journal, privacy/export
5. Widgets, alerts, health, voice, calendar integrations

That sequence reaches meaningful product parity quickly while keeping the highest-risk platform-specific work isolated until the shared product surface is already stable.