# AstroNumeric iOS Production Readiness Checklist

This checklist tracks the work needed to make the iOS app feel competitive with top astrology and numerology apps in the areas that matter most after core features exist.

## Interpretation Quality

- Maintain an editorial style guide for generated guidance:
  - Lead with one emotionally specific insight.
  - Anchor every major claim to a chart, transit, numerology, journal, timing, or biometric signal.
  - Translate symbolism into practical action.
  - Avoid generic horoscope filler.
  - Avoid certainty claims, medical claims, financial advice, or predictions framed as facts.
- Run a weekly QA review of sample readings for at least:
  - Exact birth time profile.
  - Unknown birth time profile.
  - High-energy day.
  - Difficult transit day.
  - Relationship/compatibility question.
  - Career/timing question.
- Score each sample on:
  - Specificity.
  - Emotional resonance.
  - Technical accuracy.
  - Practical next step.
  - Safety and certainty boundaries.

## First 5 Minutes

- First launch should show the private profile prompt.
- After profile creation, the app should immediately show a proof snapshot:
  - Sun sign.
  - Moon sign when chart sync completes.
  - Life Path number.
  - Birth-data quality.
  - Clear next action into Daily Guide or Chart.
- QA the first-run path on:
  - Fresh install.
  - Unknown birth time.
  - Approximate birth time.
  - Exact birth time.
  - Offline or backend unavailable.

## Trust Layer

- Keep release UI free of debug-only labels and internal terminology.
- Keep privacy copy current with the actual iOS data flow.
- Support emails should include app and device context, but not birth details, chart data, journal text, or profile names.
- Add a production crash-reporting SDK before public launch, with:
  - No birth data in crash breadcrumbs.
  - User opt-out documented in privacy copy if analytics are added.
  - Symbol upload configured in CI.
- Maintain a manual release QA pass for:
  - Profile creation and editing.
  - Daily Guide refresh.
  - Chart rendering.
  - Numerology.
  - Cosmic Guide.
  - Widgets.
  - Notifications.
  - Privacy mode.
  - Support email link.

