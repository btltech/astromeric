"""Unit tests for backend/app/ai_service.py."""

import os
import sys
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ai_service import (
    build_prompt, 
    fallback_summary,
    explain_with_gemini,
    _get_model_name,
    _get_api_key,
    _configure_client,
)


class TestBuildPrompt:
    def test_includes_scope_and_headline(self):
        prompt = build_prompt(
            scope="daily",
            headline="Stay bold",
            theme="Solar",
            sections=[],
            numerology=None,
        )
        assert "Scope: daily" in prompt
        assert "Headline: Stay bold" in prompt
        assert "Theme: Solar" in prompt

    def test_includes_section_highlights(self):
        sections = [
            {"title": "Love", "highlights": ["Be honest", "Set limits"]},
            {"title": "Career", "highlights": ["Pitch ideas"]},
        ]
        prompt = build_prompt("weekly", None, None, sections, None)
        assert "Section Love" in prompt
        assert "Be honest" in prompt
        assert "Section Career" in prompt

    def test_includes_numerology(self):
        prompt = build_prompt(
            scope="daily",
            headline=None,
            theme=None,
            sections=[],
            numerology="Life Path 7: seek wisdom today"
        )
        assert "Life Path 7" in prompt

    def test_limits_sections_to_four(self):
        sections = [
            {"title": f"Section {i}", "highlights": [f"Highlight {i}"]}
            for i in range(10)
        ]
        prompt = build_prompt("daily", None, None, sections, None)
        
        assert "Section 0" in prompt
        assert "Section 3" in prompt
        assert "Section 5" not in prompt

    def test_limits_highlights_per_section(self):
        sections = [
            {"title": "Test", "highlights": [f"Highlight {i}" for i in range(10)]}
        ]
        prompt = build_prompt("daily", None, None, sections, None)
        
        assert "Highlight 0" in prompt
        assert "Highlight 2" in prompt

    def test_handles_empty_sections(self):
        sections = [{"title": "Empty", "highlights": []}]
        prompt = build_prompt("daily", None, None, sections, None)
        # Should not crash, section with no highlights is skipped
        assert "Section Empty" not in prompt or "Empty:" not in prompt

    def test_gemini_flash_identity(self):
        prompt = build_prompt("daily", None, None, [], None)
        assert "Gemini Flash" in prompt


class TestFallbackSummary:
    def test_basic_fallback(self):
        result = fallback_summary(
            headline="A bold start",
            sections=[{"title": "Love", "highlights": ["Speak truth"]}],
            numerology="Day 3 vibes",
        )
        assert "A bold start" in result
        assert "Love focus: Speak truth" in result
        assert "Day 3 vibes" in result

    def test_missing_sections(self):
        result = fallback_summary(
            headline="Grow together",
            sections=[],
            numerology=None,
        )
        assert "Grow together" in result
        assert "Trust your instincts" in result
        assert "Numerology insight:" in result

    def test_no_headline(self):
        result = fallback_summary(
            headline=None,
            sections=[{"title": "Career", "highlights": ["Lead the charge"]}],
            numerology="Personal Year 1",
        )
        assert "Fresh opportunities" in result
        assert "Career focus: Lead the charge" in result

    def test_never_empty(self):
        result = fallback_summary(None, [], None)
        assert len(result) > 10

    def test_multiple_sections(self):
        sections = [
            {"title": "Love", "highlights": ["Romance blooms"]},
            {"title": "Career", "highlights": ["Big opportunities"]},
            {"title": "Health", "highlights": ["Stay active"]},
        ]
        result = fallback_summary("Great day", sections, None)
        # Should include first two sections
        assert "Love" in result
        assert "Career" in result


class TestGetModelName:
    def test_default_model(self):
        with patch.dict('os.environ', {}, clear=True):
            old_val = os.environ.pop('GEMINI_MODEL', None)
            try:
                model = _get_model_name()
                assert model == "gemini-2.0-flash"
            finally:
                if old_val:
                    os.environ['GEMINI_MODEL'] = old_val

    def test_custom_model(self):
        with patch.dict('os.environ', {'GEMINI_MODEL': 'gemini-1.5-pro'}):
            model = _get_model_name()
            assert model == "gemini-1.5-pro"

    def test_strips_models_prefix(self):
        with patch.dict('os.environ', {'GEMINI_MODEL': 'models/gemini-2.0-flash'}):
            model = _get_model_name()
            assert model == "gemini-2.0-flash"


class TestConfigureClient:
    def test_no_api_key_returns_false(self):
        with patch.dict('os.environ', {}, clear=True):
            old_val = os.environ.pop('GEMINI_API_KEY', None)
            try:
                result = _configure_client()
                assert result is False
            finally:
                if old_val:
                    os.environ['GEMINI_API_KEY'] = old_val

    @patch('app.ai_service.genai')
    def test_with_api_key_configures(self, mock_genai):
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            mock_genai.configure = MagicMock()
            result = _configure_client()
            assert result is True
            mock_genai.configure.assert_called_once()


class TestExplainWithGemini:
    @patch('app.ai_service.genai')
    def test_successful_response(self, mock_genai):
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Today brings exciting cosmic energy."
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            result = explain_with_gemini(
                scope="daily",
                headline="Growth",
                theme="Jupiter",
                sections=[{"title": "Career", "highlights": ["Expansion"]}],
                numerology="Life Path 8"
            )
            
            assert result is not None
            assert "cosmic energy" in result

    @patch('app.ai_service.genai')
    def test_empty_response_returns_none(self, mock_genai):
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = None
            mock_response.candidates = []
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            result = explain_with_gemini("daily", None, None, [], None)
            assert result is None

    @patch('app.ai_service.genai')
    def test_extracts_from_candidates(self, mock_genai):
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = None
            
            mock_part = MagicMock()
            mock_part.text = "From candidate parts"
            mock_content = MagicMock()
            mock_content.parts = [mock_part]
            mock_candidate = MagicMock()
            mock_candidate.content = mock_content
            mock_response.candidates = [mock_candidate]
            
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            result = explain_with_gemini("daily", None, None, [], None)
            assert result == "From candidate parts"

    def test_no_api_key_returns_none(self):
        with patch.dict('os.environ', {}, clear=True):
            old_val = os.environ.pop('GEMINI_API_KEY', None)
            try:
                result = explain_with_gemini("daily", None, None, [], None)
                assert result is None
            finally:
                if old_val:
                    os.environ['GEMINI_API_KEY'] = old_val


class TestPromptSecurity:
    def test_no_api_key_in_prompt(self):
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'secret-key-12345'}):
            prompt = build_prompt("daily", "Test", "Theme", [], None)
            assert "secret-key" not in prompt
            assert "12345" not in prompt

    def test_no_system_paths_in_prompt(self):
        prompt = build_prompt("daily", "Test", "Theme", [], None)
        assert "/Users/" not in prompt
        assert "password" not in prompt.lower()

