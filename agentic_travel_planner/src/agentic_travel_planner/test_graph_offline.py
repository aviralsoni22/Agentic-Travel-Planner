"""Offline verification of the graph's feedback loop — no API keys, no network.

Mocks the LLM (budget ratios, critic) and the ReAct workers so we can drive the real
StateGraph through: (1) happy path, (2) hotel over budget then fits on retry,
(3) flight permanently over budget -> re-plan -> bounded best-effort. Proves the
budget checkpoints fire, loops are taken, Python money is authoritative, and the
graph always terminates.

Run: python -m agentic_travel_planner.test_graph_offline
"""
from __future__ import annotations

from . import graph as G
from .models import (
    BudgetRatios, CriticVerdict,
    FlightResearchTaskOutput, FlightOffer,
    HotelResearchTaskOutput, HotelOffer,
    ActivityPlanningTaskOutput, ActivityItem, HotelAnchor,
)

BASE_INPUTS = {
    "source": "New Delhi, India", "destination": "Goa, India",
    "start_date": "2026-03-10", "end_date": "2026-03-13",
    "num_travelers": 2, "budget": 1500, "interests": "food, beaches",
    "group_category": "Boys only", "currency": "USD",
}


def _state():
    return {**BASE_INPUTS, "feedback": [], "revision_count": 0,
            "flight_retries": 0, "hotel_retries": 0, "activity_retries": 0, "api_calls": 0}


def _flight(cost):
    return FlightResearchTaskOutput(
        source="DEL", destination="GOI", start_date="2026-03-10", end_date="2026-03-13",
        num_travelers=2,
        flights=[FlightOffer(
            outbound_departure_time="2026-03-10T08:00:00", outbound_arrival_time="2026-03-10T10:00:00",
            outbound_price=cost / 2,
            return_departure_time="2026-03-13T21:00:00", return_arrival_time="2026-03-13T23:00:00",
            return_price=cost / 2, total_price=cost,
        )],
        updated_remaining_budget=1500 - cost,
    )


def _hotel(cost):
    return HotelResearchTaskOutput(
        destination="Goa", start_date="2026-03-10", end_date="2026-03-13", interests=[],
        num_travelers=2, group_category="Boys only",
        hotels=[HotelOffer(name="Test Hotel", address="Panaji, Goa",
                           check_in="2026-03-10T14:00:00", check_out="2026-03-13T11:00:00",
                           nightly_rate=cost / 3, total_cost=cost)],
        updated_remaining_budget=0.0,
    )


def _activity(cost):
    return ActivityPlanningTaskOutput(
        destination="Goa", interests=[], group_category="Boys only",
        hotel_anchor=HotelAnchor(name="Test Hotel", address="Panaji, Goa"),
        activities=[ActivityItem(name="Beach tour", description="Sunset", cost=cost, location="Baga Beach")],
        final_remaining_budget=0.0,
    )


class _FakeStructured:
    def __init__(self, obj_or_exc):
        self.obj_or_exc = obj_or_exc

    def invoke(self, messages):
        if isinstance(self.obj_or_exc, Exception):
            raise self.obj_or_exc
        return self.obj_or_exc


class _FakeLLM:
    """with_structured_output(Model) -> canned object; FinalItinerary raises to force
    the deterministic fallback (also under test)."""
    def with_structured_output(self, model):
        if model is BudgetRatios:
            return _FakeStructured(BudgetRatios(flight=0.45, hotel=0.40, activity=0.15))
        if model is CriticVerdict:
            return _FakeStructured(CriticVerdict(passed=True, worst_component=None, notes="ok"))
        return _FakeStructured(RuntimeError("force deterministic assembly"))


def _install_mocks(flight_seq, hotel_seq, activity_seq):
    """flight_seq/hotel_seq/activity_seq: lists of costs; each call pops the next (last repeats)."""
    G.reasoning_llm = lambda: _FakeLLM()
    seqs = {
        FlightResearchTaskOutput: (list(flight_seq), _flight),
        HotelResearchTaskOutput: (list(hotel_seq), _hotel),
        ActivityPlanningTaskOutput: (list(activity_seq), _activity),
    }

    def fake_run_and_parse(system, user, tool_list, model, tool_label=None):
        costs, builder = seqs[model]
        cost = costs.pop(0) if len(costs) > 1 else costs[0]
        return builder(cost), None

    G._run_and_parse = fake_run_and_parse


def run():
    compiled = G.build_graph()

    # --- Scenario 1: happy path (everything fits) ---
    _install_mocks(flight_seq=[600], hotel_seq=[500], activity_seq=[200])
    out = compiled.invoke(_state(), config={"recursion_limit": 60})
    fin = out["final_itinerary"]
    assert fin.total_cost == 1300.0, fin.total_cost
    assert fin.remaining_budget == 200.0, fin.remaining_budget
    assert out.get("revision_count", 0) == 0
    print("scenario 1 (happy path): total=1300 remaining=200  OK")

    # --- Scenario 2: hotel over budget first, fits on retry ---
    #   after flight 600 -> remaining 900. Hotel 1000 (>900) fails, retry hotel 500 fits.
    _install_mocks(flight_seq=[600], hotel_seq=[1000, 500], activity_seq=[100])
    out = compiled.invoke(_state(), config={"recursion_limit": 60})
    fin = out["final_itinerary"]
    assert out["hotel_retries"] >= 1, out["hotel_retries"]
    assert fin.total_cost == 1200.0, fin.total_cost          # 600+500+100
    assert fin.remaining_budget == 300.0, fin.remaining_budget
    print(f"scenario 2 (hotel retry): hotel_retries={out['hotel_retries']} total=1200  OK")

    # --- Scenario 3: flight always over the 60% cap (900) -> retries -> re-plan -> best-effort ---
    _install_mocks(flight_seq=[1200], hotel_seq=[300], activity_seq=[100])
    out = compiled.invoke(_state(), config={"recursion_limit": 100})
    fin = out["final_itinerary"]
    assert out["revision_count"] == G.MAX_REVISIONS, out["revision_count"]   # bounded, didn't spin
    assert fin.total_cost == 1600.0, fin.total_cost                          # 1200+300+100, over budget
    assert fin.remaining_budget == -100.0, fin.remaining_budget             # honest negative
    assert fin.failures, "expected a recorded failure on overspend"
    print(f"scenario 3 (stuck -> replan): revisions={out['revision_count']} "
          f"remaining={fin.remaining_budget} failures={len(fin.failures)}  OK (terminated)")

    print("\nAll offline graph scenarios passed.")


if __name__ == "__main__":
    run()
