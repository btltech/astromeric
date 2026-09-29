"""The Learn lessons: complete, beginner-shaped, and identical on app and web."""

import re
import warnings
from pathlib import Path

from starlette.testclient import TestClient

from backend.app.interpretation.lessons import LESSONS_PATH, load_lessons
from backend.app.main import app

warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)

IOS_COPY = (
    Path(__file__).resolve().parents[2]
    / "AstroNumeric-iOS"
    / "AstroNumeric"
    / "Resources"
    / "lessons.json"
)

EXPECTED = {
    "astrology": [f"astro-{n}" for n in range(1, 8)],
    "zodiac": [f"zodiac-{n}" for n in range(1, 5)],
    "elements": [f"elem-{n}" for n in range(1, 5)],
    "numerology": [f"num-{n}" for n in range(1, 8)],
}
BANNED = re.compile(
    r"\byou will\b|\bdestined\b|\bguaranteed\b|\buniverse\b|\bmanifest|\bcosmic\b|\bvibes?\b",
    re.IGNORECASE,
)


def test_the_app_bundles_exactly_the_lessons_the_api_serves():
    # One source for app and website: if this fails, copy
    # backend/app/interpretation/library/lessons.json over the app's file.
    assert IOS_COPY.read_bytes() == LESSONS_PATH.read_bytes()


def test_every_expected_lesson_exists_once():
    lessons = load_lessons()
    ids = [lesson["id"] for lesson in lessons]
    assert len(ids) == len(set(ids))
    for category, expected in EXPECTED.items():
        assert [m["id"] for m in lessons if m["category"] == category] == expected


def test_lessons_are_long_enough_structured_and_in_voice():
    ids = {lesson["id"] for lesson in load_lessons()}
    for lesson in load_lessons():
        content = lesson["content"]
        words = len(content.split())
        assert 600 <= words <= 1400, (lesson["id"], words)
        headings = re.findall(r"(?m)^## (.+)$", content)
        assert 3 <= len(headings) <= 7, (lesson["id"], headings)
        assert headings[-1] == "Try it in AstroNumeric", lesson["id"]
        assert "!" not in content and "**" not in content, lesson["id"]
        assert not re.search(r"(?m)^#(?!# )", content), lesson["id"]
        assert not BANNED.search(content), (lesson["id"], BANNED.search(content))
        assert lesson["description"] and len(lesson["description"].split()) <= 30
        assert set(lesson["related_modules"]) <= ids, lesson["id"]


def test_api_serves_lessons_with_honest_reading_times():
    resp = client.get("/v2/learning/modules", params={"category": "numerology"})
    assert resp.status_code == 200, resp.text
    modules = resp.json()["items"]
    assert [m["id"] for m in modules] == EXPECTED["numerology"]
    for module in modules:
        assert module["duration_minutes"] == max(
            1, round(len(module["content"].split()) / 200)
        )

    one = client.get("/v2/learning/module/num-2").json()["data"]
    assert one["title"] == "Your Life Path Number"
