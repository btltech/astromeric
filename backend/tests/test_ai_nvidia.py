"""NVIDIA is tried first for AI text; Gemini is the fallback.

All HTTP is mocked with httpx.MockTransport: no test reaches the network.
"""

import asyncio
import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import httpx
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import ai_service
from app.ai_service import (
    NVIDIA_DEFAULT_MODEL,
    explain_with_gemini,
    generate_ai_text,
    generate_text,
    strip_thinking,
)
from app.engine.cosmic_guide import COSMIC_SYSTEM_PROMPT, ask_cosmic_guide

_REAL_CLIENT = httpx.Client


def _ok(text):
    return (200, {"choices": [{"message": {"role": "assistant", "content": text}}]})


class _Nvidia:
    """Serves queued (status, json) replies and records each request."""

    def __init__(self, monkeypatch, replies):
        self.replies = list(replies)
        self.requests = []
        self.sleeps = []

        def handler(request):
            self.requests.append(request)
            if not self.replies:
                raise AssertionError("unexpected extra NVIDIA request")
            status, body = self.replies.pop(0)
            return httpx.Response(status, json=body)

        def client_factory(**kwargs):
            self.timeout = kwargs.get("timeout")
            return _REAL_CLIENT(transport=httpx.MockTransport(handler), **kwargs)

        monkeypatch.setattr(
            ai_service,
            "httpx",
            SimpleNamespace(Client=client_factory),
        )
        monkeypatch.setattr(
            ai_service, "time", SimpleNamespace(sleep=self.sleeps.append)
        )

    def body(self, index=0):
        return json.loads(self.requests[index].content)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for name in (
        "NVIDIA_API_KEY",
        "NVIDIA_MODEL",
        "NVIDIA_API_URL",
        "GEMINI_API_KEY",
        "GEMINI_MODEL",
    ):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def gemini(monkeypatch):
    """A configured Gemini whose answer is 'From Gemini'."""
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-test-key")
    client = MagicMock()
    response = MagicMock()
    response.text = "From Gemini"
    client.models.generate_content.return_value = response
    fake_genai = MagicMock()
    fake_genai.Client.return_value = client
    monkeypatch.setattr(ai_service, "genai", fake_genai)
    return client


def test_nvidia_is_used_first_when_its_key_is_set(monkeypatch, gemini):
    monkeypatch.setenv("NVIDIA_API_KEY", "nv-test-key")
    nvidia = _Nvidia(monkeypatch, [_ok("From NVIDIA")])

    result = generate_ai_text("Question?", system="Be kind.")

    assert result.text == "From NVIDIA"
    assert result.provider == "nvidia"
    assert result.model == NVIDIA_DEFAULT_MODEL == "nvidia/nemotron-3-super-120b-a12b"
    gemini.models.generate_content.assert_not_called()

    request = nvidia.requests[0]
    assert str(request.url) == "https://integrate.api.nvidia.com/v1/chat/completions"
    assert request.headers["authorization"] == "Bearer nv-test-key"
    body = nvidia.body()
    assert body["model"] == NVIDIA_DEFAULT_MODEL
    assert body["chat_template_kwargs"]["enable_thinking"] is False
    assert body["messages"] == [
        {"role": "system", "content": "Be kind."},
        {"role": "user", "content": "Question?"},
    ]
    assert nvidia.timeout and nvidia.timeout <= 30


def test_model_and_url_come_from_env(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nv-test-key")
    monkeypatch.setenv("NVIDIA_MODEL", "nvidia/other-model")
    monkeypatch.setenv("NVIDIA_API_URL", "https://example.test/v9/")
    nvidia = _Nvidia(monkeypatch, [_ok("ok")])

    result = generate_ai_text("Q")

    assert result.model == "nvidia/other-model"
    assert nvidia.body()["model"] == "nvidia/other-model"
    assert str(nvidia.requests[0].url) == "https://example.test/v9/chat/completions"
    assert nvidia.body()["messages"] == [{"role": "user", "content": "Q"}]


def test_busy_503_then_200_retries_once(monkeypatch, gemini):
    monkeypatch.setenv("NVIDIA_API_KEY", "nv-test-key")
    nvidia = _Nvidia(monkeypatch, [(503, {"error": "busy"}), _ok("Second try")])

    result = generate_ai_text("Q")

    assert result.provider == "nvidia"
    assert result.text == "Second try"
    assert len(nvidia.requests) == 2
    assert nvidia.sleeps == [pytest.approx(2.0)]
    gemini.models.generate_content.assert_not_called()


def test_503_twice_falls_back_to_gemini(monkeypatch, gemini):
    monkeypatch.setenv("NVIDIA_API_KEY", "nv-test-key")
    nvidia = _Nvidia(monkeypatch, [(503, {}), (503, {})])

    result = generate_ai_text("Q")

    assert len(nvidia.requests) == 2
    assert result.provider == "gemini"
    assert result.text == "From Gemini"


def test_429_is_not_retried(monkeypatch, gemini):
    monkeypatch.setenv("NVIDIA_API_KEY", "nv-test-key")
    nvidia = _Nvidia(monkeypatch, [(429, {"error": "rate limited"})])

    result = generate_ai_text("Q")

    assert len(nvidia.requests) == 1
    assert nvidia.sleeps == []
    assert result.provider == "gemini"


def test_timeout_falls_back_without_retry(monkeypatch, gemini):
    monkeypatch.setenv("NVIDIA_API_KEY", "nv-test-key")
    calls = []

    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout("slow", request=request)

    monkeypatch.setattr(
        ai_service,
        "httpx",
        SimpleNamespace(
            Client=lambda **kw: _REAL_CLIENT(
                transport=httpx.MockTransport(handler), **kw
            )
        ),
    )

    result = generate_ai_text("Q")

    assert len(calls) == 1
    assert result.provider == "gemini"


def test_nvidia_failure_without_gemini_returns_none(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nv-test-key")
    _Nvidia(monkeypatch, [(500, {}), (500, {})])
    assert generate_text("Q") is None


def test_thinking_is_stripped_from_the_answer(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nv-test-key")
    _Nvidia(monkeypatch, [_ok("<think>\nLet me reason.\n</think>\n\nThe answer.")])
    assert generate_text("Q") == "The answer."


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("<think>a</think>Answer", "Answer"),
        ("reasoning with no opening tag</think>\nAnswer", "Answer"),
        ("<THINK>x</THINK> Answer <think>y</think>", "Answer"),
        ("Plain answer", "Plain answer"),
        ("<think>only thoughts</think>", None),
        ("", None),
        (None, None),
    ],
)
def test_strip_thinking(raw, expected):
    assert strip_thinking(raw) == expected


def test_only_thinking_falls_back_to_gemini(monkeypatch, gemini):
    monkeypatch.setenv("NVIDIA_API_KEY", "nv-test-key")
    _Nvidia(monkeypatch, [_ok("<think>hmm</think>")])
    assert generate_ai_text("Q").provider == "gemini"


def test_malformed_body_falls_back(monkeypatch, gemini):
    monkeypatch.setenv("NVIDIA_API_KEY", "nv-test-key")
    _Nvidia(monkeypatch, [(200, {"unexpected": True})])
    assert generate_ai_text("Q").provider == "gemini"


def test_without_nvidia_key_gemini_path_is_unchanged(monkeypatch, gemini):
    nvidia = _Nvidia(monkeypatch, [])

    result = generate_ai_text("Just the prompt")

    assert nvidia.requests == []
    assert result.provider == "gemini"
    gemini.models.generate_content.assert_called_once_with(
        model="gemini-2.0-flash", contents="Just the prompt"
    )
    gemini.close.assert_called_once()


def test_without_any_key_returns_none(monkeypatch):
    nvidia = _Nvidia(monkeypatch, [])
    assert generate_ai_text("Q") is None
    assert explain_with_gemini("daily", None, None, [], None) is None
    assert nvidia.requests == []


def test_explain_with_gemini_name_now_prefers_nvidia(monkeypatch, gemini):
    monkeypatch.setenv("NVIDIA_API_KEY", "nv-test-key")
    nvidia = _Nvidia(monkeypatch, [_ok("### What This Means\nGood day.")])

    text = explain_with_gemini("guidance", "Should I?", None, [], None)

    assert text == "### What This Means\nGood day."
    user_message = nvidia.body()["messages"][-1]["content"]
    assert "Headline: Should I?" in user_message
    gemini.models.generate_content.assert_not_called()


def test_cosmic_guide_chat_sends_guide_prompt_as_system(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nv-test-key")
    nvidia = _Nvidia(monkeypatch, [_ok("<think>x</think>Trust the process.")])

    result = asyncio.run(ask_cosmic_guide("What should I focus on?", tone="gentle"))

    assert result == {
        "response": "Trust the process.",
        "provider": "nvidia",
        "model": NVIDIA_DEFAULT_MODEL,
    }
    system, user = nvidia.body()["messages"]
    assert system["role"] == "system"
    assert system["content"].startswith(COSMIC_SYSTEM_PROMPT)
    assert "Tone override:" in system["content"]
    assert user == {"role": "user", "content": "What should I focus on?"}


def test_cosmic_guide_access_gate_still_skips_ai(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nv-test-key")
    nvidia = _Nvidia(monkeypatch, [])

    result = asyncio.run(ask_cosmic_guide("Hello?", use_ai=False))

    assert result["provider"] == "fallback"
    assert result["reason"] == "ai_not_enabled"
    assert nvidia.requests == []
