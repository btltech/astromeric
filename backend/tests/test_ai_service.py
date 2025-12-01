"""Unit tests for backend/app/ai_service.py."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ai_service import build_prompt, fallback_summary


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
