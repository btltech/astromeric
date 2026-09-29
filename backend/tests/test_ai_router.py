import warnings
from types import SimpleNamespace
from unittest.mock import patch

from starlette.testclient import TestClient

from backend.app.ai_service import AIText
from backend.app.auth import get_current_user
from backend.app.main import app

warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)


def _paid_user():
    return SimpleNamespace(is_paid=True)


def test_ai_explain_uses_deterministic_provider_for_numerology_scope():
    app.dependency_overrides[get_current_user] = _paid_user
    try:
        with patch("backend.app.routers.ai.explain_with_ai") as mocked_explain:
            response = client.post(
                "/v2/ai/explain",
                json={
                    "scope": "numerology",
                    "headline": "Your Numerology",
                    "sections": [
                        {
                            "title": "Life Path 7",
                            "highlights": ["Trust quiet reflection"],
                        }
                    ],
                    "numerology_summary": "Life Path 7 asks for depth and honest inner work.",
                    "simple_language": True,
                },
            )

        assert response.status_code == 200
        payload = response.json()["data"]
        assert payload["provider"] == "deterministic"
        assert "Your Numerology" in payload["summary"]
        mocked_explain.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_ai_explain_uses_deterministic_provider_for_daily_scope():
    app.dependency_overrides[get_current_user] = _paid_user
    try:
        with patch("backend.app.routers.ai.explain_with_ai") as mocked_explain:
            response = client.post(
                "/v2/ai/explain",
                json={
                    "scope": "daily",
                    "headline": "Overall Energy: 7.8/10",
                    "sections": [
                        {
                            "title": "Career",
                            "highlights": ["Lead the charge", "Do: finish the pitch"],
                        }
                    ],
                    "simple_language": True,
                },
            )

        assert response.status_code == 200
        payload = response.json()["data"]
        assert payload["provider"] == "deterministic"
        assert "Overall Energy: 7.8/10" in payload["summary"]
        mocked_explain.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_ai_explain_passes_simple_language_to_gemini_for_non_deterministic_scope(
    monkeypatch,
):
    monkeypatch.setenv("AI_ACCESS_CODE", "owner-code")
    app.dependency_overrides[get_current_user] = _paid_user
    try:
        with patch(
            "backend.app.routers.ai.explain_with_ai",
            return_value=AIText(
                text="### TL;DR\nModel answer",
                provider="gemini",
                model="gemini-2.0-flash",
            ),
        ) as mocked_explain:
            response = client.post(
                "/v2/ai/explain",
                headers={"X-Client-Platform": "ios", "X-AI-Access": "owner-code"},
                json={
                    "scope": "compatibility",
                    "headline": "Overall Energy 7.8/10",
                    "sections": [
                        {"title": "Career", "highlights": ["Lead the charge"]}
                    ],
                    "simple_language": False,
                },
            )

        assert response.status_code == 200
        payload = response.json()["data"]
        assert payload["provider"] == "gemini"
        assert payload["summary"] == "### TL;DR\nModel answer"
        assert mocked_explain.call_args.kwargs["simple_language"] is False
    finally:
        app.dependency_overrides.clear()


def _post_compatibility():
    return client.post(
        "/v2/ai/explain",
        headers={"X-Client-Platform": "ios", "X-AI-Access": "owner-code"},
        json={"scope": "compatibility", "headline": "Overall Energy 7.8/10"},
    )


def test_ai_explain_reports_nvidia_when_nvidia_answered(monkeypatch):
    monkeypatch.setenv("AI_ACCESS_CODE", "owner-code")
    app.dependency_overrides[get_current_user] = _paid_user
    try:
        with patch(
            "backend.app.routers.ai.explain_with_ai",
            return_value=AIText(
                text="From NVIDIA", provider="nvidia", model="nvidia/some-model"
            ),
        ):
            response = _post_compatibility()
        payload = response.json()["data"]
        assert payload["provider"] == "nvidia"
        assert payload["summary"] == "From NVIDIA"
    finally:
        app.dependency_overrides.clear()


def test_ai_explain_falls_back_when_no_provider_answers(monkeypatch):
    monkeypatch.setenv("AI_ACCESS_CODE", "owner-code")
    app.dependency_overrides[get_current_user] = _paid_user
    try:
        with patch("backend.app.routers.ai.explain_with_ai", return_value=None):
            response = _post_compatibility()
        payload = response.json()["data"]
        assert payload["provider"] == "fallback"
        assert "### TL;DR" in payload["summary"]
    finally:
        app.dependency_overrides.clear()
