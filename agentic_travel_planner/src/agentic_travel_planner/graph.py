"""LangGraph pipeline for the travel planner.

Deterministic edges replace the old CrewAI manager. Each research node is a ReAct
agent that thinks (searches, re-selects) and is followed by a Python budget
checkpoint: if the component is over budget it loops back (bounded), and if it stays
stuck it re-plans the budget split. All money is computed in Python.
"""
from __future__ import annotations

import json
import re
from typing import Literal, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from . import budget
from . import tools
from .state import TripState
from .llms import worker_llm, reasoning_llm
from .models import (
    BudgetRatios,
    FlightResearchTaskOutput,
    HotelResearchTaskOutput,
    ActivityPlanningTaskOutput,
    FinalItineraryOutput,
    FlightSummary,
    HotelSummary,
    ActivitySummary,
    DayPlan,
    AssemblyFailure,
    CriticVerdict,
)
from .prompts import (
    ALLOCATE_SYSTEM, allocate_user,
    FLIGHT_SYSTEM, flight_user,
    HOTEL_SYSTEM, hotel_user,
    ACTIVITY_SYSTEM, activity_user,
    ASSEMBLE_SYSTEM, assemble_user,
    CRITIC_SYSTEM, critic_user,
)

PER_NODE_RETRIES = 2      # self-corrections per research node
MAX_REVISIONS = 2         # full budget re-plans (global)
FLIGHT_CAP_FRACTION = 0.6  # flights may use up to 60% of total budget (leaves 40%)

_SAME_NODE = {"flight_retries": "flight_node", "hotel_retries": "hotel_node", "activity_retries": "activity_node"}


# ---------------------------------------------------------------- helpers

def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()  # qwen reasoning
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def _extract_json(text: str) -> Optional[str]:
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return None


def coerce(text: str, model):
    """Parse an agent's text answer into a Pydantic model, robustly."""
    if not text:
        raise ValueError("empty model output")
    cleaned = _strip_fences(text)
    for candidate in (cleaned, _extract_json(cleaned)):
        if not candidate:
            continue
        try:
            return model.model_validate_json(candidate)
        except Exception:
            try:
                return model.model_validate(json.loads(candidate))
            except Exception:
                pass
    # last resort: have the *reasoning* model reshape into the schema. We prompt for
    # raw JSON and parse it ourselves rather than using with_structured_output(), which
    # relies on forced tool-calling that Groq's gpt-oss models handle unreliably
    # ("Tool choice is required, but model did not call a tool").
    schema = json.dumps(model.model_json_schema())
    resp = reasoning_llm().invoke([
        ("system", "Output ONLY a JSON object that matches this JSON Schema exactly — no prose, "
                   "no markdown fences. Preserve all values from the content.\nSchema:\n" + schema),
        ("human", text),
    ])
    reshaped = _extract_json(_strip_fences(resp.content)) or resp.content
    return model.model_validate_json(reshaped)


def _gather_with_tools(system: str, user: str, tool_obj, max_steps: int = 5):
    """Let the worker model call the tool as many times as it wants and collect the raw
    results. We drive the loop ourselves (instead of create_react_agent) because Groq's
    server-side tool enforcement crashes when a model emits a final JSON answer while
    tools are bound ('tool_use_failed'). Here, a failure on the answer turn just ends the
    loop — we keep whatever tool results we already gathered."""
    base = worker_llm()
    messages = [SystemMessage(content=system), HumanMessage(content=user)]
    tool_results: list[str] = []
    last_content = ""
    for step in range(max_steps):
        # Force the search on the first turn (models sometimes skip it and answer blind);
        # allow the model to choose on later turns (e.g. the flight return leg, or to stop).
        tool_choice = tool_obj.name if step == 0 else "auto"
        llm = base.bind_tools([tool_obj], tool_choice=tool_choice)
        try:
            ai = llm.invoke(messages)
        except Exception:
            break  # answer-turn tool_use_failed etc. — proceed with gathered results
        messages.append(ai)
        last_content = ai.content or last_content
        calls = getattr(ai, "tool_calls", None) or []
        if not calls:
            break
        for tc in calls:
            try:
                out = tool_obj.invoke(tc["args"])
            except Exception as ex:  # noqa: BLE001
                out = json.dumps({"status": "error", "error": str(ex)})
            tool_results.append(str(out))
            messages.append(ToolMessage(content=str(out), tool_call_id=tc.get("id", "")))
    return last_content, tool_results


# How the reasoning model should treat tool results. Flights/hotels are real bookings, so the
# data is authoritative. Activities use Geoapify only as a location reference — the model is
# expected to add famous, interest-matching attractions from its own knowledge (see ACTIVITY_SYSTEM).
_AUTHORITATIVE = "TOOL RESULTS (authoritative data — use these exact values)"
_REFERENCE = "TOOL RESULTS (reference for real locations/addresses — supplement per the instructions above)"


def _structure_from(system: str, user: str, tool_results: list[str], model, tool_label: str = _AUTHORITATIVE):
    """Build the Pydantic result from the raw tool data with a NO-TOOLS reasoning call,
    so Groq's tool enforcement can't reject it."""
    schema = json.dumps(model.model_json_schema())
    context = user + f"\n\n{tool_label}:\n" + "\n---\n".join(tool_results)
    resp = reasoning_llm().invoke([
        SystemMessage(content=system + "\n\nNow output ONLY a JSON object matching this JSON "
                      "Schema exactly — no prose, no markdown fences:\n" + schema),
        HumanMessage(content=context),
    ])
    text = _extract_json(_strip_fences(resp.content)) or resp.content
    return model.model_validate_json(text)


def _run_and_parse(system: str, user: str, tool_list: list, model, tool_label: str = _AUTHORITATIVE):
    """Gather tool data, then structure it. Returns (model_or_None, error_or_None)."""
    try:
        content, tool_results = _gather_with_tools(system, user, tool_list[0])
        # if the worker's own answer already validates, take it (cheapest path)
        if content:
            try:
                return coerce(content, model), None
            except Exception:
                pass
        if not tool_results:
            return None, "no tool results produced"
        return _structure_from(system, user, tool_results, model, tool_label), None
    except Exception as e:  # noqa: BLE001 - surface as feedback, don't crash the graph
        return None, str(e)


def flight_cost(fr: FlightResearchTaskOutput) -> float:
    return float(fr.flights[0].total_price) if fr and fr.flights else float("inf")


def hotel_cost(hr: HotelResearchTaskOutput) -> float:
    if hr and isinstance(hr.hotels, list) and hr.hotels:
        return float(hr.hotels[0].total_cost)
    return float("inf")


def activity_cost(ar: ActivityPlanningTaskOutput) -> float:
    if ar and isinstance(ar.activities, list):
        return round(sum(float(a.cost) for a in ar.activities), 2)
    return 0.0


def _hotel_location(hr: HotelResearchTaskOutput) -> Optional[str]:
    if hr and isinstance(hr.hotels, list) and hr.hotels:
        h = hr.hotels[0]
        return f"{h.name}, {h.address}"
    return None


def _retry_or_escalate(state: TripState, retry_key: str, component: str, feedback_msg: str,
                       accept_goto: str, accept_update: Optional[dict]) -> Command:
    """Loop back into the same node, else re-plan the budget, else accept best-effort."""
    fb_list = state.get("feedback", []) + [feedback_msg]
    retries = state.get(retry_key, 0)
    if retries < PER_NODE_RETRIES:
        return Command(goto=_SAME_NODE[retry_key], update={retry_key: retries + 1, "feedback": fb_list})

    revisions = state.get("revision_count", 0)
    if revisions < MAX_REVISIONS:
        return Command(goto="allocate_budget", update={
            "revision_count": revisions + 1,
            "failed_component": component,
            "feedback": fb_list,
        })

    # out of revisions: continue with whatever we have (honest best-effort)
    if accept_update is None:
        return Command(goto="assemble", update={"failed_component": component, "feedback": fb_list})
    return Command(goto=accept_goto, update=accept_update)


# ---------------------------------------------------------------- nodes

def allocate_budget(state: TripState) -> Command[Literal["flight_node"]]:
    human = allocate_user(state)
    if state.get("failed_component"):
        human += (
            f"\n\nA previous attempt failed on '{state['failed_component']}'. Rebalance the "
            f"split to fix it: " + " ".join(state.get("feedback", []))
        )
    ratios = reasoning_llm().with_structured_output(BudgetRatios).invoke(
        [("system", ALLOCATE_SYSTEM), ("human", human)]
    )
    alloc = budget.allocate(state["budget"], ratios.flight, ratios.hotel, ratios.activity)
    return Command(goto="flight_node", update={
        "allocation": alloc,
        "remaining_budget": float(state["budget"]),
        # fresh pass — reset per-node retries and stale feedback
        "flight_retries": 0, "hotel_retries": 0, "activity_retries": 0,
        "feedback": [], "failed_component": None,
    })


def flight_node(state: TripState) -> Command[Literal["flight_node", "hotel_node", "allocate_budget", "assemble"]]:
    fr, err = _run_and_parse(FLIGHT_SYSTEM, flight_user(state), [tools.FlightSearchTool], FlightResearchTaskOutput)
    if err or fr is None:
        return _retry_or_escalate(state, "flight_retries", "flights",
                                  f"Flight output could not be produced/parsed: {err}",
                                  accept_goto="hotel_node", accept_update=None)
    cost = flight_cost(fr)
    cap = state["budget"] * FLIGHT_CAP_FRACTION
    if cost <= cap:
        return Command(goto="hotel_node", update={
            "flight_result": fr,
            "remaining_budget": budget.remaining(state["budget"], cost),
            "feedback": [], "failed_component": None,
        })
    fb = f"Flight total {cost:.0f} exceeds the {cap:.0f} cap (60% of budget). Pick cheaper flights — the return leg is often the costly one."
    return _retry_or_escalate(state, "flight_retries", "flights", fb, accept_goto="hotel_node",
                              accept_update={"flight_result": fr, "remaining_budget": budget.remaining(state["budget"], cost)})


def hotel_node(state: TripState) -> Command[Literal["hotel_node", "activity_node", "allocate_budget", "assemble"]]:
    hr, err = _run_and_parse(HOTEL_SYSTEM, hotel_user(state), [tools.HotelSearchTool], HotelResearchTaskOutput)
    if err or hr is None or not isinstance(hr.hotels, list) or not hr.hotels:
        return _retry_or_escalate(state, "hotel_retries", "hotel",
                                  f"No usable hotel within {state['remaining_budget']}: {err or 'no results'}",
                                  accept_goto="activity_node", accept_update=None)
    cost = hotel_cost(hr)
    cap = state["remaining_budget"]
    if cost <= cap:
        return Command(goto="activity_node", update={
            "hotel_result": hr,
            "remaining_budget": budget.remaining(cap, cost),
            "feedback": [], "failed_component": None,
        })
    fb = f"Hotel total {cost:.0f} exceeds the {cap:.0f} remaining. Choose a cheaper hotel or area."
    return _retry_or_escalate(state, "hotel_retries", "hotel", fb, accept_goto="activity_node",
                              accept_update={"hotel_result": hr, "remaining_budget": budget.remaining(cap, cost)})


def activity_node(state: TripState) -> Command[Literal["activity_node", "assemble", "allocate_budget"]]:
    location = _hotel_location(state.get("hotel_result"))
    if not location:
        # no hotel to anchor on — skip activities honestly
        return Command(goto="assemble", update={"failed_component": "activities",
                       "feedback": state.get("feedback", []) + ["No hotel anchor; activities skipped."]})

    ar, err = _run_and_parse(ACTIVITY_SYSTEM, activity_user(state, location), [tools.ActivitySearchTool],
                             ActivityPlanningTaskOutput, tool_label=_REFERENCE)
    if err or ar is None:
        return _retry_or_escalate(state, "activity_retries", "activities",
                                  f"Activity output could not be produced/parsed: {err}",
                                  accept_goto="assemble", accept_update=None)
    cost = activity_cost(ar)
    cap = state["remaining_budget"]
    if cost <= cap:
        return Command(goto="assemble", update={
            "activity_result": ar,
            "remaining_budget": budget.remaining(cap, cost),
            "feedback": [], "failed_component": None,
        })
    fb = f"Activities total {cost:.0f} exceed the {cap:.0f} remaining. Trim to the best few that fit."
    return _retry_or_escalate(state, "activity_retries", "activities", fb, accept_goto="assemble",
                              accept_update={"activity_result": ar, "remaining_budget": budget.remaining(cap, cost)})


def _interests_list(state: TripState) -> list[str]:
    return [i.strip() for i in str(state.get("interests", "")).split(",") if i.strip()]


def _deterministic_final(state: TripState, fr, hr, ar, failures) -> FinalItineraryOutput:
    """Safety-net assembly used only if the LLM structured call fails."""
    flights = hotel = None
    try:
        if fr and fr.flights:
            flights = FlightSummary(**fr.flights[0].model_dump())
    except Exception:
        pass
    try:
        if hr and isinstance(hr.hotels, list) and hr.hotels:
            h = hr.hotels[0]
            hotel = HotelSummary(
                name=h.name, address=h.address, check_in=h.check_in, check_out=h.check_out,
                total_cost=h.total_cost, booking_url=h.booking_url, discount_info=h.discount_info,
                rating=h.rating, image_url=h.image_url, nightly_rate=h.nightly_rate,
            )
    except Exception:
        pass
    days = None
    if ar and isinstance(ar.activities, list) and ar.activities:
        acts = [ActivitySummary(name=a.name, description=a.description, category=a.category,
                                cost=a.cost, location=a.location, scheduled_time=a.scheduled_time,
                                booking_url=a.booking_url, discount_info=a.discount_info)
                for a in ar.activities]
        days = [DayPlan(day=state["start_date"], activities=acts, notes="Auto-assembled (fallback).")]
    return FinalItineraryOutput(
        source=state["source"], destination=state["destination"],
        start_date=state["start_date"], end_date=state["end_date"],
        num_travelers=state["num_travelers"], group_category=state["group_category"],
        interests=_interests_list(state), failures=failures or None,
        flights=flights, hotel=hotel, itinerary_by_day=days,
    )


def assemble(state: TripState) -> Command[Literal["final_critic"]]:
    fr = state.get("flight_result")
    hr = state.get("hotel_result")
    ar = state.get("activity_result")

    failures = []
    if fr is None:
        failures.append(AssemblyFailure(component="flights", reason="No flight found within budget"))
    if hr is None:
        failures.append(AssemblyFailure(component="hotel", reason="No hotel found within budget"))
    if ar is None:
        failures.append(AssemblyFailure(component="activities", reason="No activities found within budget"))

    try:
        # Raw-JSON + coerce() instead of with_structured_output(): Groq's forced tool-calling
        # chokes on this large nested schema ('tool_use_failed'), silently dropping to the
        # fallback. Same proven path as _run_and_parse/_structure_from.
        schema = json.dumps(FinalItineraryOutput.model_json_schema())
        resp = reasoning_llm().invoke([
            SystemMessage(content=ASSEMBLE_SYSTEM + "\n\nOutput ONLY a JSON object matching this "
                          "JSON Schema exactly — no prose, no markdown fences:\n" + schema),
            HumanMessage(content=assemble_user(
                state,
                fr.model_dump_json() if fr else "N/A",
                hr.model_dump_json() if hr else "N/A",
                ar.model_dump_json() if ar else "N/A",
            )),
        ])
        final = coerce(resp.content, FinalItineraryOutput)
        if failures and not final.failures:
            final.failures = failures
    except Exception:
        final = _deterministic_final(state, fr, hr, ar, failures)

    # authoritative Python money — overwrite whatever the LLM produced
    fc = flight_cost(fr) if fr else 0.0
    hc = hotel_cost(hr) if hr else 0.0
    ac = activity_cost(ar)
    fc = 0.0 if fc == float("inf") else fc
    hc = 0.0 if hc == float("inf") else hc
    total, variance = budget.totals(fc, hc, ac, state["budget"])
    final.total_cost = total or None
    final.remaining_budget = variance
    final.trace = {
        **(final.trace or {}),
        "revisions": str(state.get("revision_count", 0)),
        "api_calls": str(tools.API_CALLS["count"]),
    }
    return Command(goto="final_critic", update={"final_itinerary": final, "api_calls": tools.API_CALLS["count"]})


def final_critic(state: TripState) -> Command[Literal["allocate_budget", "__end__"]]:
    final: FinalItineraryOutput = state["final_itinerary"]
    over_budget = (final.remaining_budget or 0) < 0

    try:
        verdict = reasoning_llm().with_structured_output(CriticVerdict).invoke(
            [("system", CRITIC_SYSTEM), ("human", critic_user(final.model_dump_json()))]
        )
    except Exception:
        verdict = CriticVerdict(passed=True, worst_component=None, notes="critic unavailable")

    needs_rework = over_budget or not verdict.passed
    revisions = state.get("revision_count", 0)
    if needs_rework and revisions < MAX_REVISIONS:
        worst = "hotel" if over_budget else (verdict.worst_component or "hotel")
        note = ("Total exceeds budget. " if over_budget else "") + (verdict.notes or "")
        return Command(goto="allocate_budget", update={
            "revision_count": revisions + 1, "failed_component": worst, "feedback": [note],
        })

    if over_budget and not final.failures:
        final.failures = [AssemblyFailure(component="hotel", reason="Best plan still exceeds budget")]
        return Command(goto=END, update={"final_itinerary": final})
    return Command(goto=END)


# ---------------------------------------------------------------- build

def build_graph():
    g = StateGraph(TripState)
    g.add_node("allocate_budget", allocate_budget)
    g.add_node("flight_node", flight_node)
    g.add_node("hotel_node", hotel_node)
    g.add_node("activity_node", activity_node)
    g.add_node("assemble", assemble)
    g.add_node("final_critic", final_critic)
    g.add_edge(START, "allocate_budget")
    return g.compile()
