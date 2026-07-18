#!/usr/bin/env python
from datetime import date, timedelta

from agentic_travel_planner.graph import build_graph
from agentic_travel_planner import tools


def run():
    """Run the planner graph once with sample inputs (CLI entry point)."""
    # Dates relative to today so the sample never goes stale (booking APIs reject past dates).
    start = date.today() + timedelta(days=45)
    end = start + timedelta(days=3)
    inputs = {
        "source": "New Delhi, India",
        "destination": "Mumbai, Maharashtra, India",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "num_travelers": 2,
        "budget": 1500,
        "interests": "clubs, food, forts, Beaches",
        "group_category": "Boys only",
        "currency": "USD",
    }
    state = {
        **inputs,
        "feedback": [], "revision_count": 0,
        "flight_retries": 0, "hotel_retries": 0, "activity_retries": 0, "api_calls": 0,
    }

    tools.reset_counter()
    result = build_graph().invoke(state, config={"recursion_limit": 60})
    itinerary = result.get("final_itinerary")

    print("\n\n=== FINAL PLAN ===\n")
    if itinerary is not None:
        print(itinerary.model_dump_json(indent=2))
    else:
        print("No itinerary produced.")
    print(f"\n[API calls made: {tools.API_CALLS['count']}]")


if __name__ == "__main__":
    run()
