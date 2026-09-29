"""Beginner lessons for the Learn section.

One file, library/lessons.json, is the source for the API (and so the
website) and is bundled unchanged into the iOS app, so all three show the
same lessons. A test fails if the app's copy drifts from this one.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

LESSONS_PATH = Path(__file__).parent / "library" / "lessons.json"


@lru_cache(maxsize=1)
def load_lessons() -> List[Dict]:
    return json.loads(LESSONS_PATH.read_text(encoding="utf-8"))
