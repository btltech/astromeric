import warnings

from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.routers import cosmic_guide as cosmic_guide_router

warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)


def test_cosmic_guidance_accepts_ios_body_contract(monkeypatch):
    monkeypatch.setattr(
        cosmic_guide_router,
        "explain_with_gemini",
        lambda **_: "Guidance from the stars.",
    )

    resp = client.post(
        "/v2/cosmic-guide/guidance",
        json={
            "topic": "career",
            "context": "Launch planning",
            "profile": {
                "name": "Test User",
                "date_of_birth": "1990-06-15",
                "time_of_birth": "14:30:00",
                "timezone": "America/New_York",
            },
        },
    )
    assert resp.status_code == 200

    body = resp.json()["data"]
    assert body["question"] == "career"
    assert "Guidance" in body["guidance"]


def test_cosmic_interpret_accepts_ios_body_contract(monkeypatch):
    monkeypatch.setattr(
        cosmic_guide_router,
        "explain_with_gemini",
        lambda **_: "Interpretation from the stars.",
    )

    resp = client.post(
        "/v2/cosmic-guide/interpret",
        json={
            "chart_data": "Sun in Gemini, Moon in Pisces",
            "reading_data": "Luck score 75",
            "question": "What does this suggest?",
        },
    )
    assert resp.status_code == 200

    body = resp.json()["data"]
    assert body["topic"] == "What does this suggest?"
    assert "Interpretation" in body["summary"]


def test_cosmic_chat_accepts_ios_tone_and_system_prompt(monkeypatch):
    captured = {}

    async def fake_ask_cosmic_guide(**kwargs):
        captured.update(kwargs)
        return {
            "response": "Direct answer from the stars.",
            "provider": "gemini",
            "model": "test-model",
        }

    monkeypatch.setattr(cosmic_guide_router, "ask_cosmic_guide", fake_ask_cosmic_guide)

    resp = client.post(
        "/v2/cosmic-guide/chat",
        json={
            "message": "Tell me plainly.",
            "sun_sign": "Gemini",
            "moon_sign": "Pisces",
            "history": [],
            "system_prompt": "SYSTEM CONTEXT",
            "tone": "direct",
        },
    )

    assert resp.status_code == 200
    assert captured["question"] == "Tell me plainly."
    assert captured["system_prompt"] == "SYSTEM CONTEXT"
    assert captured["tone"] == "direct"
    assert resp.json()["data"]["response"] == "Direct answer from the stars."
