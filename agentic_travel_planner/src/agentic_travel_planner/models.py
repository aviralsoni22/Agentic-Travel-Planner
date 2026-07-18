"""Structured output models for the travel planner.

These were previously defined inside crew.py. They are the single source of truth
for every node's structured output and are unchanged from the CrewAI version so the
frontend contract stays identical.
"""
from __future__ import annotations

from enum import Enum
from datetime import date, datetime
from typing import List, Optional, Union, Literal

from pydantic import BaseModel, Field, PositiveFloat, PositiveInt, conlist


class GroupCategory(str, Enum):
    couple = "couple"
    family = "family"
    girls_only = "Girls only"
    boys_only = "Boys only"
    mixed = "Boys and Girls both"
    business = "business"
    students = "students"
    other = "other"


class BudgetRatios(BaseModel):
    """Fractions of the total budget to spend on each component.

    The LLM supplies the *judgment* (these ratios); Python does the arithmetic.
    Values need not sum to 1.0 — they are normalized in budget.allocate().
    """
    flight: float = Field(..., gt=0, description="Relative weight for flights/transport.")
    hotel: float = Field(..., gt=0, description="Relative weight for accommodation.")
    activity: float = Field(..., gt=0, description="Relative weight for activities.")
    reasoning: str = Field("", description="One line on why this split fits the trip.")


class InitialPlanningTaskOutput(BaseModel):
    source: str = Field(..., description="Origin city/region/country for the trip (e.g., home city).")
    destination: str = Field(..., description="Trip destination city/region/country.")
    start_date: date = Field(..., description="Trip start date (YYYY-MM-DD).")
    end_date: date = Field(..., description="Trip end date (YYYY-MM-DD).")
    num_travelers: PositiveInt = Field(..., description="Number of travelers in the group.")
    interests: conlist(str, min_length=0) = Field(
        default_factory=list,
        description="List of interest tags (e.g., 'food', 'hiking', 'art').",
    )
    budget: PositiveFloat = Field(..., description="Total budget for the entire trip (single currency).")
    group_category: GroupCategory = Field(..., description="Group type for the trip.")

    allocated_flight_budget: PositiveFloat = Field(..., description="Budget allocated to flights/transport to destination.")
    allocated_hotel_budget: PositiveFloat = Field(..., description="Budget allocated to accommodation.")
    allocated_activity_budget: PositiveFloat = Field(..., description="Budget allocated to activities/experiences.")


class FlightOffer(BaseModel):
    """Details about a found flight option (Round Trip)."""
    outbound_airline: Union[str, None] = Field("Unknown", description="Airline for outbound leg")
    outbound_flight_number: Union[str, int, None] = Field("Unknown", description="Flight number for outbound leg")
    outbound_departure_time: str = Field(..., description="Departure datetime ISO string (Outbound)")
    outbound_arrival_time: str = Field(..., description="Arrival datetime ISO string (Outbound)")
    outbound_departure_timezone: Optional[str] = Field(None, description="Timezone of the outbound departure airport (origin), e.g. 'IST' or 'Asia/Kolkata'")
    outbound_arrival_timezone: Optional[str] = Field(None, description="Timezone of the outbound arrival airport (destination)")
    outbound_stops: Optional[int] = Field(None, ge=0, description="Number of stops on outbound leg (0 = non-stop), from the tool's 'stops' field")
    outbound_price: PositiveFloat = Field(..., description="Price for outbound leg (Total for all travelers)")

    return_airline: Union[str, None] = Field("Unknown", description="Airline for return leg")
    return_flight_number: Union[str, int, None] = Field("Unknown", description="Flight number for return leg")
    return_departure_time: str = Field(..., description="Departure datetime ISO string (Return)")
    return_arrival_time: str = Field(..., description="Arrival datetime ISO string (Return)")
    return_departure_timezone: Optional[str] = Field(None, description="Timezone of the return departure airport (destination)")
    return_arrival_timezone: Optional[str] = Field(None, description="Timezone of the return arrival airport (origin)")
    return_stops: Optional[int] = Field(None, ge=0, description="Number of stops on return leg (0 = non-stop), from the tool's 'stops' field")
    return_price: PositiveFloat = Field(..., description="Price for return leg (Total for all travelers)")

    total_price: PositiveFloat = Field(..., description="Total price (outbound + return)")

    outbound_booking_url: Optional[str] = Field(None, description="URL to book outbound flight")
    outbound_discount_info: Optional[str] = Field(None, description="Details about any discounts found for outbound")
    return_booking_url: Optional[str] = Field(None, description="URL to book return flight")
    return_discount_info: Optional[str] = Field(None, description="Details about any discounts found for return")


class FlightResearchTaskOutput(BaseModel):
    """Output of the flight research task."""
    source: str = Field(..., description="Origin airport/city")
    destination: str = Field(..., description="Destination airport/city")
    start_date: date = Field(..., description="Departure date")
    end_date: date = Field(..., description="Return date")
    num_travelers: PositiveInt = Field(..., description="Number of travelers")

    flights: List[FlightOffer] = Field(..., description="List of flight options.")
    updated_remaining_budget: Optional[float] = Field(..., description="Remaining budget = budget - actual_flight_cost")


class HotelOffer(BaseModel):
    """Details about a found hotel/resort/villa option for the entire stay."""
    name: str = Field(..., description="Property name")
    address: str = Field(..., description="Full address or area")
    latitude: float = Field(None, description="Latitude of the property if available")
    longitude: float = Field(None, description="Longitude of the property if available")
    check_in: str = Field(..., description="Check-in datetime ISO string, in local time")
    check_out: str = Field(..., description="Check-out datetime ISO string, in local time")
    nightly_rate: PositiveFloat = Field(..., description="Nightly rate (single currency)")
    total_cost: PositiveFloat = Field(..., description="Total cost for the full stay and guest count")
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Average user rating (0–5)")
    image_url: Optional[str] = Field(None, description="URL of a representative image")
    reviews_count: Optional[int] = Field(None, ge=0, description="Number of reviews")
    distance_to_interest_km: Optional[float] = Field(None, ge=0.0, description="Approx distance to key interest area in km")
    amenities: List[str] = Field(default_factory=list, description="Amenity tags")
    cancellation_policy: Optional[str] = Field(None, description="Summary of cancellation policy")
    booking_url: Optional[str] = Field(None, description="Direct booking link")
    discount_info: Optional[str] = Field(None, description="Any applicable discount notes")


class HotelResearchTaskOutput(BaseModel):
    """Output of the hotel research task."""
    destination: str = Field(..., description="City/area being visited")
    start_date: date = Field(..., description="Check-in date")
    end_date: date = Field(..., description="Check-out date")
    interests: conlist(str, min_length=0) = Field(default_factory=list, description="User interest tags used to bias location")
    num_travelers: PositiveInt = Field(..., description="Total guests")
    group_category: str = Field(..., description="Group type label (e.g., couple, family, friends)")

    hotels: Union[List[HotelOffer], str] = Field(
        ..., description="List of hotel options or an error message if none found within remaining budget"
    )
    updated_remaining_budget: float = Field(..., description="previous_remaining_budget - actual_hotel_cost")
    previous_remaining_budget: Optional[PositiveFloat] = Field(None, description="Remaining budget received from the flight task")


class HotelAnchor(BaseModel):
    """Reference hotel used to minimize travel time in the plan."""
    name: str = Field(..., description="Selected hotel name from previous step")
    address: str = Field(..., description="Hotel address or area")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Hotel latitude if available")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Hotel longitude if available")


class ActivityItem(BaseModel):
    """A planned activity that matches interests and budget."""
    name: str = Field(..., description="Activity or venue name")
    description: str = Field(..., description="Short activity description")
    category: Optional[str] = Field(None, description="e.g., tour, restaurant, museum, show")
    cost: float = Field(..., ge=0, description="Total cost for the group for this activity (0 for free attractions)")
    location: str = Field(..., description="Where the activity takes place (address/area)")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Lat if available")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Lng if available")
    scheduled_time: Optional[datetime] = Field(None, description="Planned start datetime (local) if scheduled")
    estimated_travel_time_minutes: Optional[int] = Field(None, ge=0, description="Approx travel time from hotel to activity")
    booking_url: Optional[str] = Field(None, description="Direct link to book or reserve")
    discount_info: Optional[str] = Field(None, description="Any promo/discount details")


class ActivityPlanningTaskOutput(BaseModel):
    """Output for the activity planning task."""
    destination: str = Field(..., description="Trip destination city/region")
    interests: conlist(str, min_length=0) = Field(default_factory=list, description="Interest tags guiding activity selection")
    group_category: str = Field(..., description="Group type label (e.g., couple, family, friends)")
    hotel_anchor: HotelAnchor = Field(..., description="Hotel details used to anchor/optimize the itinerary")

    activities: Union[List[ActivityItem], str] = Field(
        ..., description="List of planned activities, or an error message if none found within budget"
    )
    final_remaining_budget: float = Field(..., description="previous_remaining_budget - total_activity_cost")
    previous_remaining_budget: Optional[PositiveFloat] = Field(None, description="Remaining budget received from the hotel step")


class FlightSummary(BaseModel):
    """Condensed summary of the selected flight solution."""
    outbound_airline: Union[str, None] = Field("Unknown", description="Chosen carrier")
    outbound_flight_number: Union[str, int, None] = Field("Unknown", description="Booked/selected flight number")
    outbound_departure_time: datetime = Field(..., description="Outbound departure (ISO)")
    outbound_arrival_time: datetime = Field(..., description="Outbound arrival (ISO)")
    outbound_departure_timezone: Optional[str] = Field(None, description="Timezone of the outbound departure airport (origin)")
    outbound_arrival_timezone: Optional[str] = Field(None, description="Timezone of the outbound arrival airport (destination)")
    outbound_stops: Optional[int] = Field(None, ge=0, description="Number of stops on outbound leg (0 = non-stop)")
    outbound_price: PositiveFloat = Field(..., description="Price for outbound leg")
    outbound_booking_url: Optional[str] = Field(None, description="Deep link used to book, if available")
    outbound_discount_info: Optional[str] = Field(None, description="Promotions applied, if any")

    return_airline: Union[str, None] = Field("Unknown", description="Chosen carrier")
    return_flight_number: Union[str, int, None] = Field("Unknown", description="Booked/selected flight number")
    return_departure_time: datetime = Field(..., description="Return leg departure (ISO) if round trip")
    return_arrival_time: datetime = Field(..., description="Return leg arrival (ISO) if round trip")
    return_departure_timezone: Optional[str] = Field(None, description="Timezone of the return departure airport (destination)")
    return_arrival_timezone: Optional[str] = Field(None, description="Timezone of the return arrival airport (origin)")
    return_stops: Optional[int] = Field(None, ge=0, description="Number of stops on return leg (0 = non-stop)")
    return_price: PositiveFloat = Field(..., description="Price for return leg")
    return_booking_url: Optional[str] = Field(None, description="Deep link used to book, if available")
    return_discount_info: Optional[str] = Field(None, description="Promotions applied, if any")

    total_price: PositiveFloat = Field(..., description="Total paid/expected for flights for all travelers")


class HotelSummary(BaseModel):
    """Condensed summary of the selected accommodation."""
    name: str = Field(..., description="Property name")
    address: str = Field(..., description="Property full address")
    check_in: datetime = Field(..., description="Check-in datetime (local)")
    check_out: datetime = Field(..., description="Check-out datetime (local)")
    total_cost: PositiveFloat = Field(..., description="Total accommodation cost for the entire stay")
    booking_url: Optional[str] = Field(None, description="Booking link")
    discount_info: Optional[str] = Field(None, description="Promo code or deal if any")
    rating: Optional[float] = Field(None, description="Average user rating (0-10)")
    image_url: Optional[str] = Field(None, description="URL of a representative image")
    nightly_rate: Optional[float] = Field(None, description="Cost per night")


class ActivitySummary(BaseModel):
    """A single confirmed/planned activity."""
    name: str = Field(..., description="Activity name")
    description: str = Field(..., description="Short description")
    category: Optional[str] = Field(None, description="tour | restaurant | museum | show | other")
    cost: float = Field(..., ge=0, description="Cost for the group (0 for free attractions)")
    location: str = Field(..., description="Address or area")
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled start time (local) if any")
    booking_url: Optional[str] = Field(None, description="Reservation or ticket link")
    discount_info: Optional[str] = Field(None, description="Deal applied, if any")


class DayPlan(BaseModel):
    """Day-by-day plan aggregating activities."""
    day: date = Field(..., description="Calendar date of the plan day")
    activities: List[ActivitySummary] = Field(default_factory=list, description="Activities planned for the day")
    notes: Optional[str] = Field(None, description="Optional narrative/logistics for the day")


class AssemblyFailure(BaseModel):
    """If any specialist step failed and could not be resolved."""
    component: Literal["flights", "hotel", "activities"] = Field(..., description="Which component failed")
    reason: str = Field(..., description="Why assembly failed")
    tool_error: Optional[str] = Field(None, description="Original error message from tool if available")


class FinalItineraryOutput(BaseModel):
    """Final assembled itinerary. Single source of truth for the compiled plan."""
    source: str = Field(..., description="Trip source city/region")
    destination: str = Field(..., description="Trip destination city/region")
    start_date: date = Field(..., description="Trip start date")
    end_date: date = Field(..., description="Trip end date")
    num_travelers: PositiveInt = Field(..., description="Total number of travelers")
    group_category: str = Field(..., description="Group type label (e.g., couple, family, friends)")
    interests: List[str] = Field(default_factory=list, description="Interests that guided selection")

    failures: Optional[List[AssemblyFailure]] = Field(
        None, description="If present and non-empty, indicates unrecoverable assembly issues."
    )

    flights: Optional[FlightSummary] = Field(None, description="Chosen flight solution")
    hotel: Optional[HotelSummary] = Field(None, description="Chosen accommodation")
    itinerary_by_day: Optional[List[DayPlan]] = Field(None, description="Day-by-day schedule built from activities")

    total_cost: Optional[float] = Field(None, ge=0, description="Sum of flights + hotel + total activities (assembler emits 0 as a placeholder; Python overwrites with the exact value)")
    remaining_budget: Optional[float] = Field(
        None,
        description="Final remaining budget (original total budget - total_cost). May be negative if overspent.",
    )

    trace: Optional[dict[str, str]] = Field(
        default_factory=dict,
        description="Optional trace info (which node produced which component, revisions, etc.)",
    )


class CriticVerdict(BaseModel):
    """Holistic critic judgment over the assembled itinerary."""
    passed: bool = Field(..., description="True if the itinerary is coherent and good quality.")
    worst_component: Optional[Literal["flights", "hotel", "activities"]] = Field(
        None, description="If not passed, which component most needs rework."
    )
    notes: str = Field("", description="Short, actionable critique.")
