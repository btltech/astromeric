"""Live Gemini is limited to the owner's device via a private access code.

Gemini runs on an unpaid key, so other users' questions and chart data must never
reach it: without the code every caller gets the built-in fallback responses.
"""

from app.ai_service import has_ai_access
from app.main import app
from fastapi.testclient import TestClient

CODE = "test-access-code"


class _FakeRequest:
    def __init__(self, headers):
        self.headers = headers


def test_no_access_without_the_code_configured(monkeypatch):
    monkeypatch.delenv("AI_ACCESS_CODE", raising=False)
    assert has_ai_access(_FakeRequest({"x-ai-access": "anything"})) is False


def test_blank_access_code_is_treated_as_unset(monkeypatch):
    monkeypatch.setenv("AI_ACCESS_CODE", "   ")
    assert has_ai_access(_FakeRequest({"x-ai-access": ""})) is False
    assert has_ai_access(_FakeRequest({})) is False


def test_access_requires_an_exact_match(monkeypatch):
    monkeypatch.setenv("AI_ACCESS_CODE", CODE)
    assert has_ai_access(_FakeRequest({"x-ai-access": CODE})) is True
    assert has_ai_access(_FakeRequest({"x-ai-access": CODE + "x"})) is False
    assert has_ai_access(_FakeRequest({"x-ai-access": CODE.upper()})) is False
    assert has_ai_access(_FakeRequest({})) is False


def test_native_ios_alone_no_longer_unlocks_gemini(monkeypatch):
    """The old gate let every App Store install through; the platform header must not."""
    monkeypatch.setenv("AI_ACCESS_CODE", CODE)
    assert has_ai_access(_FakeRequest({"x-client-platform": "ios"})) is False


def test_chat_without_the_code_answers_from_fallbacks(monkeypatch):
    monkeypatch.setenv("AI_ACCESS_CODE", CODE)
    with TestClient(app) as client:
        response = client.post(
            "/v2/cosmic-guide/chat",
            json={"message": "What should I focus on?"},
            headers={"X-Client-Platform": "ios"},
        )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["provider"] == "fallback"
    assert data["response"]
