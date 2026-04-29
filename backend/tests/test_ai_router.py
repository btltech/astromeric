import warnings
from types import SimpleNamespace
from unittest.mock import patch

from starlette.testclient import TestClient

from backend.app.auth import get_current_user
from backend.app.main import app

warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated")
client = TestClient(app)


def _paid_user():
    return SimpleNamespace(is_paid=True)


def test_ai_explain_uses_deterministic_provider_for_numerology_scope():
    app.dependency_overrides[get_current_user] = _paid_user
    try:
        with patch("backend.app.routers.ai.explain_with_gemini") as mocked_explain:
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
        with patch("backend.app.routers.ai.explain_with_gemini") as mocked_explain:
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


def test_ai_explain_passes_simple_language_to_gemini_for_non_deterministic_scope():
    app.dependency_overrides[get_current_user] = _paid_user
    try:
        with patch(
            "backend.app.routers.ai.explain_with_gemini",
            return_value="### TL;DR\nModel answer",
        ) as mocked_explain:
            response = client.post(
                "/v2/ai/explain",
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
        assert payload["provider"] == "gemini-flash"
        assert payload["summary"] == "### TL;DR\nModel answer"
        assert mocked_explain.call_args.kwargs["simple_language"] is False
    finally:
        app.dependency_overrides.clear()
