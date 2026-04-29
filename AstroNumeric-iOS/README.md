# AstroNumeric iOS

AstroNumeric is a privacy-first, local-first iOS app for astrology, numerology, practical timing, and AI-guided self-reflection. The current app stores core profile data on device, calculates charts locally where possible, and uses the backend for enrichment such as forecasts, compatibility, AI guidance, notifications, and widget brief refreshes.

## Product Positioning

- **Core promise:** private astrology and numerology guidance that helps users plan their day, understand their chart, and reflect without handing every interaction to a cloud account.
- **Primary differentiator:** local-first birth profiles plus Swiss Ephemeris chart calculation, blended with numerology, timing tools, widgets, journaling, and optional AI guidance.
- **Best App Store subtitle direction:** Private astrology and numerology.
- **Audience:** users who want more depth than generic horoscopes, but prefer practical language, privacy controls, and daily timing over a social-feed astrology experience.

See `AppStorePositioning.md` for draft App Store copy, keyword direction, and screenshot messaging.

## Current Product Model

- Native iOS app only. The web client is not part of the active product surface.
- Local-first and guest-first. Profiles, preferences, habits, most journal data, and saved relationship history are stored on-device.
- Backend-backed features are used when requested: readings, daily guidance, friend sync, compatibility APIs, AI guidance, and push registration.
- Widgets read from the shared app group container after the main app prepares fresh data.

## Project Layout

- `AstroNumeric/`: main iOS application target
- `AstroWidget/`: widget extension
- `AstroNumericTests/`: unit tests
- `AstroNumericUITests/`: UI test target
- `AstroNumeric.xcodeproj/`: checked-in Xcode project
- `project.yml`: XcodeGen source of truth for target settings

## Requirements

- Xcode 15 or later
- iOS 17.0 deployment target
- A reachable backend configured through `API_BASE_URL` in `project.yml`

## Open And Run

```bash
cd /Users/mobolaji/Downloads/astromeric/AstroNumeric-iOS
open AstroNumeric.xcodeproj
```

Or build/test from the command line:

```bash
xcodebuild -project AstroNumeric.xcodeproj -scheme AstroNumeric -destination 'platform=iOS Simulator,name=iPhone 17 Pro' test
```

## Active Capabilities

- Push notifications
- Background fetch / remote notification wake
- App Groups for widget data sharing
- HealthKit read access
- Location lookup for birthplace/timezone assist
- Microphone and speech recognition for voice journaling

The project also contains entitlements for Sign in with Apple and Apple Pay, but those are not currently part of the primary shipped user flow.

## Notes

- Widgets depend on the main app refreshing and on iOS widget scheduling.
- Cosmic Circle friends are backend-backed; saved relationship history in `Relationships` is local-only.
- `Hide Sensitive Details` is a UI/share redaction layer, not a separate offline mode.
- Debug builds include an in-app `Profile → System Diagnostics` screen for notification and widget freshness QA.
