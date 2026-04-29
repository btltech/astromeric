"""Tests for backend/app/engine/cosmic_guide.py."""

import asyncio
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.engine.cosmic_guide import ask_cosmic_guide, get_quick_insight


def test_ask_cosmic_guide_uses_client_chat_api():
    mock_client = MagicMock()
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "The stars suggest patience."
    mock_client.chats.create.return_value = mock_chat
    mock_chat.send_message.return_value = mock_response

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch(
            "app.engine.cosmic_guide.create_gemini_client",
            return_value=mock_client,
        ), patch("app.engine.cosmic_guide.close_gemini_client") as mock_close:
            result = asyncio.run(ask_cosmic_guide("What should I focus on?"))

    assert result["provider"] == "gemini"
    assert result["response"] == "The stars suggest patience."
    mock_client.chats.create.assert_called_once()
    mock_chat.send_message.assert_called_once()
    mock_close.assert_called_once_with(mock_client)


def test_ask_cosmic_guide_applies_system_prompt_and_tone_override():
    mock_client = MagicMock()
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Direct cosmic answer."
    mock_client.chats.create.return_value = mock_chat
    mock_chat.send_message.return_value = mock_response

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch(
            "app.engine.cosmic_guide.create_gemini_client",
            return_value=mock_client,
        ), patch("app.engine.cosmic_guide.close_gemini_client"):
            result = asyncio.run(
                ask_cosmic_guide(
                    "Tell me the truth.",
                    system_prompt="SYSTEM CONTEXT",
                    tone="direct",
                )
            )

    sent_prompt = mock_chat.send_message.call_args.args[0]
    assert "SYSTEM CONTEXT" in sent_prompt
    assert "Tone override:" in sent_prompt
    assert "straightforward" in sent_prompt
    assert result["response"] == "Direct cosmic answer."


def test_get_quick_insight_uses_models_generate_content():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "A bright opening is near. ✨"
    mock_client.models.generate_content.return_value = mock_response

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch(
            "app.engine.cosmic_guide.create_gemini_client",
            return_value=mock_client,
        ), patch("app.engine.cosmic_guide.close_gemini_client") as mock_close:
            result = asyncio.run(get_quick_insight("career", sun_sign="Gemini"))

    assert result == "A bright opening is near. ✨"
    mock_client.models.generate_content.assert_called_once()
    mock_close.assert_called_once_with(mock_client)
