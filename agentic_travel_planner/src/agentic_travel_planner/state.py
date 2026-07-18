"""LangGraph state for the travel planner.

One typed object flows through every node. `remaining_budget` is Python-owned and
is the single source of truth for budget threading (no more free-text drift).
"""
from __future__ import annotations

from typing import Optional, TypedDict

from .models import (
    FlightResearchTaskOutput,
    HotelResearchTaskOutput,
    ActivityPlanningTaskOutput,
    FinalItineraryOutput,
)


class TripState(TypedDict, total=False):
    # --- request inputs (from the API) ---
    source: str
    destination: str
    start_date: str
    end_date: str
    num_travelers: int
    budget: float
    interests: str
    group_category: str
    currency: str

    # --- filled progressively by nodes ---
    allocation: dict
    flight_result: FlightResearchTaskOutput
    hotel_result: HotelResearchTaskOutput
    activity_result: ActivityPlanningTaskOutput
    remaining_budget: float
    final_itinerary: FinalItineraryOutput

    # --- feedback loop bookkeeping ---
    feedback: list[str]          # critic/checkpoint notes injected into the next node run
    revision_count: int          # number of full budget re-plans (global cap)
    failed_component: Optional[str]
    flight_retries: int
    hotel_retries: int
    activity_retries: int
    api_calls: int               # external API calls actually made this run
