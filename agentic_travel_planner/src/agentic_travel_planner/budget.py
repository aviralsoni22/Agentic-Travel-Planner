"""Deterministic budget arithmetic.

The LLM decides the *ratios*; every number below is computed in Python so there
are no LLM calculation mistakes and `remaining_budget` never drifts.
"""
from __future__ import annotations

DEFAULT_RATIOS = (0.45, 0.40, 0.15)  # flight, hotel, activity — fallback only


def allocate(budget: float, flight: float, hotel: float, activity: float) -> dict:
    """Turn relative ratios into concrete allocations that sum to `budget`."""
    total = flight + hotel + activity
    if total <= 0:
        flight, hotel, activity = DEFAULT_RATIOS
        total = sum(DEFAULT_RATIOS)

    f = round(budget * flight / total, 2)
    h = round(budget * hotel / total, 2)
    a = round(budget - f - h, 2)  # absorb rounding remainder so the three sum exactly
    if a < 0:  # pathological ratios — claw back from hotel
        h = round(h + a, 2)
        a = 0.0
    return {
        "allocated_flight_budget": f,
        "allocated_hotel_budget": h,
        "allocated_activity_budget": a,
    }


def remaining(budget: float, *spent: float) -> float:
    """Budget minus everything spent so far. May go negative (caller decides)."""
    return round(budget - sum(spent), 2)


def totals(flight_cost: float, hotel_cost: float, activity_cost: float, budget: float) -> tuple[float, float]:
    """Return (total_cost, variance) where variance = budget - total_cost."""
    total = round(flight_cost + hotel_cost + activity_cost, 2)
    return total, round(budget - total, 2)


def _selfcheck() -> None:
    a = allocate(1500, 3, 4, 3)  # ratios 0.3/0.4/0.3
    assert round(sum(a.values()), 2) == 1500.0, a
    assert a["allocated_flight_budget"] == 450.0, a

    # zero/garbage ratios fall back and still sum exactly
    b = allocate(1000, 0, 0, 0)
    assert round(sum(b.values()), 2) == 1000.0, b

    assert remaining(1000, 300, 200) == 500.0
    total, variance = totals(400, 300, 100, 1000)
    assert total == 800.0 and variance == 200.0, (total, variance)

    # overspend produces a negative variance, not a crash
    _, v = totals(600, 500, 200, 1000)
    assert v == -300.0, v
    print("budget.py self-check passed")


if __name__ == "__main__":
    _selfcheck()
