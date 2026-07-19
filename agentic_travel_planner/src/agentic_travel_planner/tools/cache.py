"""Tiny TTL cache + call counter shared by the search tools.

Purpose: keep the budget self-correction loops cheap on the rate-limited
Booking.com / Geoapify APIs. A retry that re-searches the *same* params is served
from cache; only genuinely new params hit the network. `API_CALLS` counts real
network fetches so a node can record it into graph state.
"""
from __future__ import annotations

import time
from typing import Any, Callable

_TTL_SECONDS = 600
_CACHE: dict[Any, tuple[float, Any]] = {}

# Mutable counter (dict so callers can read/reset by reference).
API_CALLS = {"count": 0}


def cached_get(key: Any, fetch: Callable[[], Any]) -> Any:
    """Return a cached value for `key`, or call `fetch()` (counted) and cache it."""
    now = time.time()
    hit = _CACHE.get(key)
    if hit is not None and (now - hit[0]) < _TTL_SECONDS:
        return hit[1]
    API_CALLS["count"] += 1
    value = fetch()
    _CACHE[key] = (now, value)
    return value


def evict(key: Any) -> None:
    """Drop a cached entry (e.g. an empty/bad response that shouldn't poison retries)."""
    _CACHE.pop(key, None)


def reset_counter() -> None:
    API_CALLS["count"] = 0


def _selfcheck() -> None:
    reset_counter()
    calls = {"n": 0}

    def fetch():
        calls["n"] += 1
        return "data"

    assert cached_get(("x", 1), fetch) == "data"
    assert cached_get(("x", 1), fetch) == "data"  # served from cache
    assert calls["n"] == 1, calls          # fetch ran once
    assert API_CALLS["count"] == 1, API_CALLS
    cached_get(("x", 2), fetch)            # new key -> new fetch
    assert calls["n"] == 2 and API_CALLS["count"] == 2
    print("cache.py self-check passed")


if __name__ == "__main__":
    _selfcheck()
