"""Node prompts, migrated from the CrewAI agents.yaml / tasks.yaml.

Built as f-string helpers so the literal JSON braces in the original prompts don't
collide with templating. The important behavioural rules are preserved verbatim in
spirit: round-trip via two one-way searches, morning-out / night-return preference,
budget-overflow rule, price-string parsing, hotel priority order, activity anchoring.
"""
from __future__ import annotations


def _feedback_block(feedback: list[str]) -> str:
    if not feedback:
        return ""
    joined = "\n".join(f"- {f}" for f in feedback)
    return (
        "\n\nIMPORTANT — a previous attempt was rejected. You MUST fix these issues, "
        "preferring to re-select a cheaper option from results you already fetched "
        "before searching again (to save API calls):\n" + joined
    )


ALLOCATE_SYSTEM = (
    "You are a travel budgeting strategist. Given a trip, decide what FRACTION of the "
    "total budget should go to flights, hotels and activities. Use world knowledge: "
    "long-haul/international routes need a larger flight share; short/domestic trips "
    "need less. Flights are the priority, hotels secondary, activities least. "
    "Return only the relative weights — the exact arithmetic is done downstream."
)


def allocate_user(state: dict) -> str:
    return (
        f"Trip: {state['source']} -> {state['destination']}, "
        f"{state['start_date']} to {state['end_date']}, {state['num_travelers']} travelers, "
        f"group={state['group_category']}, interests={state['interests']}, "
        f"total budget={state['budget']} {state['currency']}."
    )


FLIGHT_SYSTEM = (
    "You are a resourceful flight researcher and an accurate assistant. You use the "
    "`search_flights` tool, which is STRICTLY ONE-WAY. To plan a round trip you MUST "
    "call it TWICE:\n"
    "  1. OUTBOUND: source -> destination on the start date. PREFER an EARLY MORNING "
    "departure (05:00-11:00) to maximize daytime at the destination.\n"
    "  2. RETURN: destination -> source on the end date (swap source/destination). "
    "PREFER a LATE NIGHT departure (after 20:00) to use the last day fully.\n"
    "The tool accepts only IATA airport codes — convert cities to their main IATA code.\n\n"
    "BUDGET RULE: target the allocated_flight_budget, but if the best flight exceeds it "
    "you MAY spend up to the TOTAL trip budget PROVIDED at least 40% of the total budget "
    "remains for hotel + activities. Do NOT fail just because the allocation is tight.\n\n"
    "DATA PARSING: the tool returns prices like '150.00 USD'. Extract the NUMERIC value "
    "(150.00) for price fields. If a field is missing (e.g. flight number), use 'Unknown' "
    "— never fail the task. total_price = outbound_price + return_price (one round-trip "
    "entry, not two). Report any discounts found.\n\n"
    "STOPS: copy the tool's 'stops' number into outbound_stops (outbound leg) and "
    "return_stops (return leg). 0 means non-stop.\n\n"
    "TIMEZONES: departure/arrival times from the tool are each in that airport's LOCAL time — "
    "keep the FULL ISO datetime including any UTC offset (do NOT strip '+05:30' etc.). Also fill "
    "the timezone label fields with the airport's zone (abbreviation like 'IST'/'GMT'/'BST' or "
    "IANA like 'Asia/Kolkata'): the ORIGIN city's zone for outbound_departure_timezone and "
    "return_arrival_timezone; the DESTINATION city's zone for outbound_arrival_timezone and "
    "return_departure_timezone."
)


def flight_user(state: dict) -> str:
    alloc = state.get("allocation", {})
    return (
        f"Find the optimal round-trip flights.\n"
        f"From: {state['source']}  To: {state['destination']}\n"
        f"Depart on {state['start_date']}, return on {state['end_date']}.\n"
        f"Travelers: {state['num_travelers']}, group: {state['group_category']}, "
        f"currency: {state['currency']}.\n"
        f"allocated_flight_budget = {alloc.get('allocated_flight_budget')}, "
        f"total_budget = {state['budget']}.\n"
        f"Return JSON matching FlightResearchTaskOutput with a single round-trip entry in "
        f"'flights' and updated_remaining_budget = total_budget - total_price."
        + _feedback_block(state.get("feedback", []))
    )


HOTEL_SYSTEM = (
    "You are a value-driven hotel specialist. Use the `search_hotels` tool. Choose the "
    "single best-value hotel that stays within the remaining budget, prioritizing in this "
    "order: safety of the neighborhood > proximity to key attractions > budget > guest "
    "ratings > amenities (wifi/breakfast). The hotel cost must NOT exceed the remaining "
    "budget (which must also cover activities). If nothing fits, say so clearly rather "
    "than overspending."
)


def hotel_user(state: dict) -> str:
    return (
        f"Find the best hotel in {state['destination']}.\n"
        f"Check-in {state['start_date']}, check-out {state['end_date']}, "
        f"{state['num_travelers']} guests, group {state['group_category']}, "
        f"interests {state['interests']}, currency {state['currency']}.\n"
        f"remaining budget for hotel + activities = {state['remaining_budget']}.\n"
        f"Return JSON matching HotelResearchTaskOutput; put your single best pick first in "
        f"'hotels' and set updated_remaining_budget = remaining - chosen hotel total_cost."
        + _feedback_block(state.get("feedback", []))
    )


ACTIVITY_SYSTEM = (
    "You are an expert local travel curator. Build a shortlist of the destination's BEST-KNOWN, "
    "must-visit attractions and experiences that match the traveler's interests — name specific "
    "iconic places, not generic ones. For history/culture: the famous forts, palaces, monuments and "
    "museums (e.g. in Jaipur: Amer Fort, City Palace, Hawa Mahal, Jantar Mantar, Nahargarh Fort). "
    "For food: the renowned local eateries and street-food institutions (e.g. in Jaipur: LMB, Rawat "
    "Mishtan Bhandar). The `search_activities` tool gives real nearby places, coordinates and "
    "addresses — use it as REFERENCE for location/verification, but you SHOULD add these iconic, "
    "interest-matching spots from your own knowledge even when they are not in the tool results, and "
    "prefer them over generic nearby cafes. COSTS (be realistic, in USD): monument/museum entry fees "
    "are SMALL — about $2-$25 per person, many under $10, and some sites are free (use 0); a sit-down "
    "meal is about $10-$40 per person. Compute cost = per-person figure × number of travelers (NOT "
    "hundreds of dollars for a fort). The SUM of all activity costs MUST stay within the remaining "
    "activity budget — trim or drop items if it would exceed. Aim for enough spots to fill the trip "
    "days. Never invent places that do not exist."
)


def activity_user(state: dict, hotel_location: str) -> str:
    return (
        f"Curate the top {state['interests']} attractions and experiences in "
        f"{state['destination']} for this trip. Anchor near the hotel: {hotel_location}, but "
        f"include the destination's iconic must-see spots even if a bit farther.\n"
        f"Interests: {state['interests']}, group {state['group_category']}, "
        f"{state['num_travelers']} travelers.\n"
        f"remaining budget for activities = {state['remaining_budget']}.\n"
        f"Return JSON matching ActivityPlanningTaskOutput; set final_remaining_budget = "
        f"remaining - total activity cost, and fill hotel_anchor from the hotel above."
        + _feedback_block(state.get("feedback", []))
    )


ASSEMBLE_SYSTEM = (
    "You are an itinerary synthesizer. Combine the confirmed flight, hotel and activities "
    "into a single coherent day-by-day plan (FinalItinerary). Build itinerary_by_day by "
    "spreading the activities across ALL trip days (do NOT cram them onto day 1) — group "
    "nearby or same-theme spots on the same day, 2-4 per day, and keep every activity from "
    "the provided list. Respect the flight arrival/departure times (don't schedule activities "
    "before landing on arrival day or after the return flight on the last day). "
    "Fill flights, hotel and interests from the provided data. Leave total_cost and "
    "remaining_budget as 0 — they are overwritten with exact Python-computed values."
)


def assemble_user(state: dict, flight_json: str, hotel_json: str, activity_json: str) -> str:
    return (
        f"Trip: {state['source']} -> {state['destination']}, {state['start_date']} to "
        f"{state['end_date']}, {state['num_travelers']} travelers, group "
        f"{state['group_category']}, interests {state['interests']}.\n\n"
        f"FLIGHTS:\n{flight_json}\n\nHOTEL:\n{hotel_json}\n\nACTIVITIES:\n{activity_json}\n\n"
        f"Produce the FinalItinerary JSON."
    )


CRITIC_SYSTEM = (
    "You are a meticulous trip-quality reviewer. Judge whether the assembled itinerary is "
    "coherent and good quality: activities match the stated interests, the schedule is "
    "realistic given flight times, and the hotel choice is sensible. You do NOT check the "
    "budget math (that is verified separately). If it should be reworked, name the single "
    "worst component (flights, hotel, or activities) and give one actionable note."
)


def critic_user(final_json: str) -> str:
    return f"Review this itinerary and return your verdict:\n{final_json}"
