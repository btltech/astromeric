#!/usr/bin/env python3
"""Fail when the iOS app references a localization key it cannot resolve.

A missing key is not a silent fallback: `LocalizationService.localized` returns
the key itself and the UI draws it verbatim, which is how a badge reading
"LABEL.S-TARTHERE" reached a build. This check compares every `"key".localized`
site in the Swift sources against all supported catalogs.

Run from the repo root:  python3 scripts/check_ios_localization.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SOURCE_ROOT = Path("AstroNumeric-iOS/AstroNumeric")
CATALOG_ROOT = SOURCE_ROOT / "Resources/Localizable"
# Catalogs that ship with the app; each must define every key the code uses, so a
# translated build never falls back to a raw key.
LANGUAGES = ("en", "es", "fr", "ro", "ne")

KEY_IN_SWIFT = re.compile(r'"([A-Za-z0-9_.]+)"\.localized')
KEY_IN_CATALOG = re.compile(r'^\s*"([^"]+)"\s*=', re.M)


def keys_used() -> dict[str, list[str]]:
    """Every localization key referenced in Swift, with the files using it."""
    used: dict[str, list[str]] = {}
    for path in sorted(SOURCE_ROOT.rglob("*.swift")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for key in KEY_IN_SWIFT.findall(text):
            used.setdefault(key, []).append(str(path))
    return used


def keys_defined(language: str) -> set[str]:
    catalog = CATALOG_ROOT / f"{language}.lproj" / "Localizable.strings"
    if not catalog.exists():
        print(f"error: missing catalog {catalog}")
        sys.exit(1)
    return set(
        KEY_IN_CATALOG.findall(catalog.read_text(encoding="utf-8", errors="replace"))
    )


def main() -> int:
    if not SOURCE_ROOT.is_dir():
        print(f"error: run from the repo root (no {SOURCE_ROOT})")
        return 1

    used = keys_used()
    defined = {language: keys_defined(language) for language in LANGUAGES}
    failures: list[str] = []

    for key, files in sorted(used.items()):
        missing = [language for language in LANGUAGES if key not in defined[language]]
        if missing:
            where = ", ".join(sorted({Path(f).name for f in files})[:3])
            failures.append(
                f'  "{key}" missing from: {", ".join(missing)}  (used in {where})'
            )

    print(f"checked {len(used)} keys against {len(LANGUAGES)} catalogs")
    if failures:
        print(f"\n{len(failures)} key(s) would render as raw text on screen:\n")
        print("\n".join(failures))
        return 1

    print("all keys resolve in every language")
    return 0


if __name__ == "__main__":
    sys.exit(main())
