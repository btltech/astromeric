"""Tests for backend/app/engine/cosmic_guide.py."""

import asyncio
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.engine.cosmic_guide import ask_cosmic_guide, get_quick_insight


@pytest.fixture(autouse=True)
def _no_nvidia(monkeypatch):
    """These tests cover the Gemini path, which runs when NVIDIA is not set."""
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)


def _gemini_client(text):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = text
    mock_client.models.generate_content.return_value = mock_response
    return mock_client


def test_ask_cosmic_guide_uses_gemini_when_nvidia_is_not_set():
    mock_client = _gemini_client("The stars suggest patience.")

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch("app.ai_service.genai") as mock_genai:
            mock_genai.Client.return_value = mock_client
            result = asyncio.run(ask_cosmic_guide("What should I focus on?"))

    assert result["provider"] == "gemini"
    assert result["response"] == "The stars suggest patience."
    mock_client.models.generate_content.assert_called_once()
    contents = mock_client.models.generate_content.call_args.kwargs["contents"]
    assert "You are the Cosmic Guide" in contents
    assert contents.endswith("User question: What should I focus on?")
    mock_client.close.assert_called_once()


def test_ask_cosmic_guide_applies_system_prompt_and_tone_override():
    mock_client = _gemini_client("Direct cosmic answer.")

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch("app.ai_service.genai") as mock_genai:
            mock_genai.Client.return_value = mock_client
            result = asyncio.run(
                ask_cosmic_guide(
                    "Tell me the truth.",
                    system_prompt="SYSTEM CONTEXT",
                    tone="direct",
                )
            )

    sent_prompt = mock_client.models.generate_content.call_args.kwargs["contents"]
    assert "SYSTEM CONTEXT" in sent_prompt
    assert "Tone override:" in sent_prompt
    assert "straightforward" in sent_prompt
    assert result["response"] == "Direct cosmic answer."


def test_ask_cosmic_guide_without_any_key_answers_from_fallbacks(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result = asyncio.run(ask_cosmic_guide("How is my love life?"))
    assert result["provider"] == "fallback"
    assert result["reason"] == "no_api_key"
    assert result["topic_detected"] == "love"
    assert result["response"]


def test_ask_cosmic_guide_falls_back_when_the_provider_fails():
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = RuntimeError("boom")

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch("app.ai_service.genai") as mock_genai:
            mock_genai.Client.return_value = mock_client
            result = asyncio.run(ask_cosmic_guide("Why am I stuck?"))

    assert result["provider"] == "fallback"
    assert result["reason"] == "ai_unavailable"
    assert result["topic_detected"] == "stuck"


def test_get_quick_insight_uses_models_generate_content():
    mock_client = _gemini_client("A bright opening is near. ✨")

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch("app.ai_service.genai") as mock_genai:
            mock_genai.Client.return_value = mock_client
            result = asyncio.run(get_quick_insight("career", sun_sign="Gemini"))

    assert result == "A bright opening is near. ✨"
    mock_client.models.generate_content.assert_called_once()
    mock_client.close.assert_called_once()
