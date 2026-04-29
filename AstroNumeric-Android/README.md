# AstroNumeric Android

Native Android foundation for AstroNumeric, built from the parity audit in `docs/implementation/android-native-parity-audit.md`.

## Current Scope

- Jetpack Compose app shell with Home, Tools, Charts, and Profile tabs
- Local-first profile persistence using Room + DataStore
- Onboarding and profile editing with exact, approximate, and unknown birth time states
- Backend API foundation using Retrofit + OkHttp
- Home screen morning brief fetch wired to `/v2/daily/brief`

## Build

From this directory:

```bash
ANDROID_SDK_ROOT="$HOME/Library/Android/sdk" ./gradlew :app:assembleDebug
```

## Phase 1 Decisions

- Local-only profiles use negative ids to mirror the iOS local-first strategy.
- Birthplace entry supports manual text plus coordinate resolution via Android `Geocoder`.
- Timezone defaults to the device timezone but remains editable.
- Android now bundles the same Swiss Ephemeris core data and C sources used by iOS for on-device natal chart and exact-transit fallback when the backend is unavailable.
