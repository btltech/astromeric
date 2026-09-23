# iOS release checklist

Run once per App Store submission, on a physical iPhone, after CI is green.

CI already covers what a machine can check: the app compiles, the unit tests
pass, and every localization key resolves in all five languages. Everything
below needs real hardware or human eyes, which is why it is a release gate
rather than a development step.

## 1. VoiceOver (physical device)

Settings → Accessibility → VoiceOver on.

- [ ] Swipe through Home: every control announces what it does, not its icon name.
- [ ] Relationships → open a relationship → the delete button announces "Delete relationship", not "trash".
- [ ] A filter row (Explore categories or reading scope) announces which option is selected.
- [ ] Use the rotor set to Headings: each screen offers headings to jump between.
- [ ] Start a load (pull to refresh): it announces loading rather than reading out an emoji.

## 2. Smallest supported iPhone

On an iPhone SE, or the SE simulator at 375pt.

- [ ] First-run screen shows its title and all three feature rows in full, no "…".
- [ ] Scroll each tab to the end: the last card clears the floating AI button.
- [ ] No horizontal clipping on chips, pills or card rows.

## 3. Largest Dynamic Type

Settings → Accessibility → Display & Text Size → Larger Text, at maximum.

- [ ] Home: the chip row wraps or scrolls rather than cutting off.
- [ ] Weekly pulse cards grow to fit their score row.
- [ ] Buttons stay tappable and labels stay inside their capsules.

## 4. Share-card export

- [ ] Open a reading → Share → the exported image is dark with legible text.
- [ ] Repeat for a chart and a numerology card.
- [ ] With Hide Sensitive Details on, the shared image shows no birth details.

(A unit test asserts the card renders dark, so this is confirmation, not discovery.)

## 5. Offline launch

Aeroplane mode on, app force-quit.

- [ ] The app launches and shows cached content or clear empty states.
- [ ] No raw error text appears as a headline anywhere.
- [ ] Re-enable the network: pull to refresh recovers without a restart.

## 6. Submission metadata

- [ ] Version and build incremented beyond the last upload.
- [ ] Privacy answers match `privacy-security-audit.md`: Precise Location, Other
      Data Types and Contacts collected but **not linked**; everything else not
      collected; tracking **No**.
- [ ] Privacy policy URL reachable: https://astronumeric.com/privacy-policy
- [ ] Review notes make the guideline 4.3 case: astrology and numerology
      together, real ephemeris calculations (solar arcs, lunar returns,
      profections, relocation), widgets, five languages.
