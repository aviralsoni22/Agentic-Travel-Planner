"""LLM provider toggle: open-source (Groq, default) or OpenAI.

Flip with `LLM_PROVIDER=openai` (default `groq`). Two roles:
  worker  -> tool-calling flight/hotel/activity search (fast, low temp)
  reasoning -> budget split, itinerary assembly, critic (better judgment)

Groq uses one GROQ_API_KEY; OpenAI uses OPENAI_API_KEY. Override any model id with
WORKER_MODEL / REASONING_MODEL. ChatOpenAI is imported lazily so the default Groq
path doesn't require langchain-openai to be installed.
"""
from __future__ import annotations

import os
from functools import lru_cache

from langchain_groq import ChatGroq

PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

# (worker, reasoning) defaults per provider
_DEFAULTS = {
    "groq": ("llama-3.3-70b-versatile", "openai/gpt-oss-120b"),
    "openai": ("gpt-4.1-mini", "gpt-4.1"),
}
_worker_default, _reasoning_default = _DEFAULTS.get(PROVIDER, _DEFAULTS["groq"])

WORKER_MODEL = os.getenv("WORKER_MODEL") or os.getenv("GROQ_WORKER_MODEL") or _worker_default
REASONING_MODEL = os.getenv("REASONING_MODEL") or os.getenv("GROQ_REASONING_MODEL") or _reasoning_default


def _chat(model: str, temperature: float):
    if PROVIDER == "openai":
        from langchain_openai import ChatOpenAI  # lazy: only needed when toggled on
        return ChatOpenAI(model=model, temperature=temperature, max_retries=2)
    return ChatGroq(model=model, temperature=temperature, max_retries=2)


@lru_cache(maxsize=2)
def worker_llm():
    """Tool-calling workhorse: fast, low temperature for consistent extraction."""
    return _chat(WORKER_MODEL, 0.1)


@lru_cache(maxsize=2)
def reasoning_llm():
    """Judgment model for budget split, itinerary synthesis and the critic."""
    return _chat(REASONING_MODEL, 0.2)
