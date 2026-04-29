import warnings

from starlette.testclient import TestClient

from backend.app.main import app

warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)


def test_learning_modules_returns_legacy_and_v2_pagination_fields():
    resp = client.get("/v2/learning/modules?category=astrology")
    assert resp.status_code == 200

    body = resp.json()
    assert isinstance(body["data"], list)
    assert body["data"] == body["items"]
    assert body["page"] == 1
    assert body["page_size"] == 10
    assert body["pages"] >= 1
    assert isinstance(body["has_next"], bool)
    assert isinstance(body["has_prev"], bool)


def test_learning_glossary_returns_legacy_and_v2_pagination_fields():
    resp = client.get("/v2/learning/glossary")
    assert resp.status_code == 200

    body = resp.json()
    assert isinstance(body["data"], list)
    assert body["data"] == body["items"]
    assert body["page"] == 1
    assert body["page_size"] == 10
    assert body["pages"] >= 1
    assert isinstance(body["has_next"], bool)
    assert isinstance(body["has_prev"], bool)


def test_zodiac_guidance_uses_requested_sign_data():
    resp = client.get("/v2/learning/zodiac/Gemini")
    assert resp.status_code == 200

    body = resp.json()["data"]
    assert body["sign"] == "Gemini"
    assert body["date_range"] == "May 21 - June 20"
    assert body["element"] == "Air"
    assert body["ruling_planet"] == "Mercury"
