
from __future__ import annotations
from crewai import Agent, Crew, Process, Task
from enum import Enum
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from pydantic import BaseModel, Field, PositiveFloat, PositiveInt, root_validator, validator, conlist, model_validator
from agentic_travel_planner.tools import FlightSearchTool, ActivitySearchTool, HotelSearchTool
from datetime import date, datetime
from typing import List, Optional, Union, Literal, Dict

import re

_SAFE = re.compile(r"^[A-Za-z0-9_-]+$")

def assert_tool_names_safe(agents):
    offenders = []
    for ag in agents:
        role = getattr(ag, "role", repr(ag))
        for t in (getattr(ag, "tools", None) or []):
            name = getattr(t, "name", None)
            if not isinstance(name, str) or not _SAFE.match(name):
                offenders.append((role, type(t).__name__, name))
    if offenders:
        lines = "\n".join(f"- agent={a}, tool={tc}, name={repr(n)}" for a, tc, n in offenders)
        raise ValueError(
            "Invalid tool names (must match ^[A-Za-z0-9_-]+$):\n" + lines
        )


class GroupCategory(str, Enum):
    solo = "solo"
    couple = "couple"
    family = "family"
    girls_only = "Girls only"
    boys_only = "Boys only"
    mixed = "Boys and Girls both"
    business = "business"
    students = "students"
    other = "other"

class InitialPlanningTaskOutput(BaseModel):
    destination: str = Field(..., description="Trip destination city/region/country.")
    start_date: date = Field(..., description="Trip start date (YYYY-MM-DD).")
    end_date: date = Field(..., description="Trip end date (YYYY-MM-DD).")
    trip_duration: PositiveInt = Field(..., description="Trip duration in days.")
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
    source: str = Field(..., description="Origin city/region/country for the trip (e.g., home city).")

    class Config:
        title = "InitialPlanningTaskOutput"
        json_schema_extra = {
            "example": {
                "destination": "Bali, Indonesia",
                "start_date": "2026-01-10",
                "end_date": "2026-01-17",
                "trip_duration": 7,
                "num_travelers": 2,
                "interests": ["beaches", "temples", "food"],
                "budget": 180000.0,
                "group_category": "couple",
                "allocated_flight_budget": 72000.0,
                "allocated_hotel_budget": 75600.0,
                "allocated_activity_budget": 32400.0,
                "source": "Mumbai, India"
            }
        }




class FlightOffer(BaseModel):
    """Details about a found flight option."""
    airline: str = Field(..., description="Airline name/carrier")
    flight_number: str = Field(..., description="Flight number")
    departure_time: str = Field(..., description="Departure datetime ISO string")
    arrival_time: str = Field(..., description="Arrival datetime ISO string")
    price: PositiveFloat = Field(..., description="Total price for the travelers")
    booking_url: Optional[str] = Field(None, description="URL to book this flight")
    discount_info: Optional[str] = Field(
        None, description="Details about any discounts found"
    )
    



class FlightResearchTaskOutput(BaseModel):
    """
    Output of the flight research task.
    Includes passed routing info plus research results.
    """

    # --- Context from planning task ---
    source: str = Field(..., description="Origin airport/city")
    destination: str = Field(..., description="Destination airport/city")
    start_date: date = Field(..., description="Departure date")
    end_date: date = Field(..., description="Return date")
    num_travelers: PositiveInt = Field(..., description="Number of travelers")

    flights: Union[List[FlightOffer], str] = Field(
      ..., description="List of flight options or error message if no flights found"
    )
    updated_remaining_budget: Optional[float] = Field(..., description="Remaining budget = budget - actual_flight_cost")

    class Config:
        title = "FlightResearchTaskOutput"
        json_schema_extra = {
            "example": {
                "source": "Mumbai, India",
                "destination": "Bali, Indonesia",
                "start_date": "2026-01-10",
                "end_date": "2026-01-17",
                "num_travelers": 2,
                "flights": "6E 333, DHK056, CEB362",
                "updated_remaining_budget": 108000.0
            }
        }

class HotelOffer(BaseModel):
    """Details about a found hotel/resort/villa option for the entire stay."""
    name: str = Field(..., description="Property name")
    address: str = Field(..., description="Full address or area")
    check_in: str = Field(..., description="Check-in datetime ISO string")
    check_out: str = Field(..., description="Check-out datetime ISO string")
    nightly_rate: PositiveFloat = Field(..., description="Nightly rate (single currency)")
    total_cost: PositiveFloat = Field(..., description="Total cost for the full stay and guest count")
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Average user rating (0–5)")
    reviews_count: Optional[int] = Field(None, ge=0, description="Number of reviews")
    distance_to_interest_km: Optional[float] = Field(
        None, ge=0.0, description="Approx distance to key interest area in km"
    )
    amenities: List[str] = Field(default_factory=list, description="Amenity tags")
    cancellation_policy: Optional[str] = Field(None, description="Summary of cancellation policy")
    booking_url: Optional[str] = Field(None, description="Direct booking link")
    discount_info: Optional[str] = Field(None, description="Any applicable discount notes")


class HotelResearchTaskOutput(BaseModel):
    """
    Output of the hotel research task.
    Includes passed context plus research results constrained by remaining budget.
    """

    destination: str = Field(..., description="City/area being visited")
    start_date: date = Field(..., description="Check-in date")
    end_date: date = Field(..., description="Check-out date")
    interests: conlist(str, min_length=0) = Field(
        default_factory=list, description="User interest tags used to bias location"
    )
    num_travelers: PositiveInt = Field(..., description="Total guests")
    group_category: str = Field(..., description="Group type label (e.g., couple, family, friends)")

    # --- Required output fields ---
    hotels: Union[List[HotelOffer], str] = Field(
      ..., description="List of hotel options or an error message if none found within remaining budget"
    )
    updated_remaining_budget: float = Field(
      ..., description="previous_remaining_budget - actual_hotel_cost"
    )

    # --- Optional passthrough helpful for auditing (not required by spec) ---
    previous_remaining_budget: Optional[PositiveFloat] = Field(
        None, description="Remaining budget received from the flight task"
    )

    class Config:
        title = "HotelResearchTaskOutput"
        json_schema_extra = {
            "example": {
                "destination": "Bali, Indonesia",
                "start_date": "2026-01-10",
                "end_date": "2026-01-17",
                "interests": ["beaches", "food", "temples"],
                "num_travelers": 2,
                "group_category": "couple",
                "hotels": [
                    {
                        "cancellation_policy": "Free cancel until 48h before check-in",
                        "booking_url": "https://example.com/book/seaside-villa",
                        "discount_info": "Stay 7, pay 6 nights promo applied"
                    }
                ],
                "updated_remaining_budget": 48500.0,
                "previous_remaining_budget": 108000.0
            }
        }

        


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
    cost: PositiveFloat = Field(..., description="Total cost for the group for this activity")
    location: str = Field(..., description="Where the activity takes place (address/area)")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Lat if available")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Lng if available")
    scheduled_time: Optional[datetime] = Field(
        None, description="Planned start datetime (local) if scheduled"
    )
    estimated_travel_time_minutes: Optional[int] = Field(
        None, ge=0, description="Approx travel time from hotel to activity"
    )
    booking_url: Optional[str] = Field(None, description="Direct link to book or reserve")
    discount_info: Optional[str] = Field(None, description="Any promo/discount details")

class ActivityPlanningTaskOutput(BaseModel):
    """
    Output for the activity planning task.
    Uses remaining budget from hotel step and hotel location context to minimize travel time.
    """

    # --- Context passed in / required to plan ---
    destination: str = Field(..., description="Trip destination city/region")
    interests: conlist(str, min_length=0) = Field(
        default_factory=list, description="Interest tags guiding activity selection"
    )
    group_category: str = Field(..., description="Group type label (e.g., couple, family, friends)")
    hotel_anchor: HotelAnchor = Field(
      ..., description="Hotel details used to anchor/optimize the itinerary"
    )

    # --- Output required by the task spec ---
    activities: Union[List[ActivityItem], str] = Field(
      ..., description="List of planned activities, or an error message if none found within budget"
    )
    final_remaining_budget: float = Field(
      ..., description="previous_remaining_budget - total_activity_cost"
    )

    # --- Helpful passthrough (not required by spec, but useful for validation/auditing) ---
    previous_remaining_budget: Optional[PositiveFloat] = Field(
        None, description="Remaining budget received from the hotel step"
    )

    class Config:
        title = "ActivityPlanningTaskOutput"
        json_schema_extra = {
            "example": {
                "destination": "Kyoto, Japan",
                "interests": ["temples", "food", "gardens"],
                "group_category": "couple",
                "hotel_anchor": {
                    "name": "Hotel Granvia Kyoto",
                    "address": "JR Kyoto Station, Kyoto",
                    "latitude": 34.9855,
                    "longitude": 135.7586
                },
                "activities": [
                    {
                        "name": "Fushimi Inari Early Morning Walk",
                        "description": "Self-guided hike through the torii gates to avoid crowds.",
                        "category": "tour",
                        "cost": 0.0,
                        "location": "Fushimi Inari Taisha",
                        "latitude": 34.9671,
                        "longitude": 135.7727,
                        "scheduled_time": "2026-01-11T06:30:00",
                        "estimated_travel_time_minutes": 18,
                        "booking_url": None,
                        "discount_info": None
                    },
                    {
                        "name": "Kaiseki Dinner",
                        "description": "Traditional multi-course Japanese dinner experience.",
                        "category": "restaurant",
                        "cost": 220.0,
                        "location": "Gion district",
                        "latitude": 35.0037,
                        "longitude": 135.7788,
                        "scheduled_time": "2026-01-11T19:30:00",
                        "estimated_travel_time_minutes": 15,
                        "booking_url": "https://example.com/kaiseki",
                        "discount_info": "Weeknight prix-fixe"
                    }
                ],
                "final_remaining_budget": 1025.0,
                "previous_remaining_budget": 1245.0
            }
        }




# ---------- Building blocks (summaries carried from specialist outputs) ----------

class FlightSummary(BaseModel):
    """Condensed summary of the selected flight solution."""
    airline: str = Field(..., description="Chosen carrier")
    flight_number: str = Field(..., description="Booked/selected flight number")
    departure_time: datetime = Field(..., description="Outbound departure (ISO)")
    arrival_time: datetime = Field(..., description="Outbound arrival (ISO)")
    return_departure_time: Optional[datetime] = Field(None, description="Return leg departure (ISO) if round trip")
    return_arrival_time: Optional[datetime] = Field(None, description="Return leg arrival (ISO) if round trip")
    total_price: PositiveFloat = Field(..., description="Total paid/expected for flights for all travelers")
    booking_url: Optional[str] = Field(None, description="Deep link used to book, if available")
    discount_info: Optional[str] = Field(None, description="Promotions applied, if any")


class HotelSummary(BaseModel):
    """Condensed summary of the selected accommodation."""
    name: str = Field(..., description="Property name")
    address: str = Field(..., description="Property full address")
    check_in: datetime = Field(..., description="Check-in datetime (local)")
    check_out: datetime = Field(..., description="Check-out datetime (local)")
    total_cost: PositiveFloat = Field(..., description="Total accommodation cost for the entire stay")
    booking_url: Optional[str] = Field(None, description="Booking link")
    discount_info: Optional[str] = Field(None, description="Promo code or deal if any")


class ActivitySummary(BaseModel):
    """A single confirmed/planned activity."""
    name: str = Field(..., description="Activity name")
    description: str = Field(..., description="Short description")
    category: Optional[str] = Field(None, description="tour | restaurant | museum | show | other")
    cost: PositiveFloat = Field(..., description="Cost for the group")
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


# ---------- Final itinerary output ----------

class FinalItineraryOutput(BaseModel):
    """
    Final assembled itinerary to be emitted as Markdown text (without code fences).
    This model is the single source of truth for the compiled plan.
    """

    # Context
    destination: str = Field(..., description="Trip destination city/region")
    start_date: date = Field(..., description="Trip start date")
    end_date: date = Field(..., description="Trip end date")
    trip_duration: PositiveInt = Field(..., description="Duration in days")
    num_travelers: PositiveInt = Field(..., description="Total number of travelers")
    group_category: str = Field(..., description="Group type label (e.g., couple, family, friends)")
    interests: List[str] = Field(default_factory=list, description="Interests that guided selection")

    # Components (exactly one of failures OR all components populated)
    failures: Optional[List[AssemblyFailure]] = Field(
        None,
        description="If present and non-empty, indicates unrecoverable assembly issues."
    )

    flights: Optional[FlightSummary] = Field(None, description="Chosen flight solution")
    hotel: Optional[HotelSummary] = Field(None, description="Chosen accommodation")
    itinerary_by_day: Optional[List[DayPlan]] = Field(
        None, description="Day-by-day schedule built from activities"
    )

    # Costing
    total_cost: Optional[PositiveFloat] = Field(
        None, description="Sum of flights + hotel + total activities"
    )
    remaining_budget: Optional[float] = Field(
        None,
        description=(
            "Final remaining budget from the original total trip budget. "
            "This MUST equal the Budgeting_Agent's 'variance' field. "
            "It may be negative if the itinerary overspends the budget."
        ),
    )

    # Traceability (optional but useful for audits)
    trace: Optional[dict[str,str]] = Field(
        default_factory=dict,
        description="Optional: IDs/URIs to the JSON outputs from each specialist step"
    )

    class Config:
        title = "FinalItinerary"
        json_schema_extra = {
            "example": {
                "destination": "Kyoto, Japan",
                "start_date": "2026-01-10",
                "end_date": "2026-01-17",
                "trip_duration": 7,
                "num_travelers": 2,
                "group_category": "couple",
                "interests": ["temples", "food", "gardens"],
                "flights": {
                    "airline": "ANA",
                    "flight_number": "NH802",
                    "departure_time": "2026-01-10T10:15:00",
                    "arrival_time": "2026-01-10T19:20:00",
                    "return_departure_time": "2026-01-17T12:10:00",
                    "return_arrival_time": "2026-01-17T21:30:00",
                    "total_price": 1200.0,
                    "booking_url": "https://example.com/ana/nh802",
                    "discount_info": "New Year Fare"
                },
                "hotel": {
                    "name": "Hotel Granvia Kyoto",
                    "address": "JR Kyoto Station, Kyoto",
                    "check_in": "2026-01-10T15:00:00",
                    "check_out": "2026-01-17T11:00:00",
                    "total_cost": 900.0,
                    "booking_url": "https://example.com/granvia",
                    "discount_info": "Stay 7 nights promo"
                },
                "itinerary_by_day": [
                    {
                        "notes": "Use JR line from Kyoto Station for quick access."
                    }
                ],
                "total_cost": 2320.0,
                "remaining_budget": 1025.0,
                "trace": {
                    "flight_research_task": "output/flight_research.json",
                    "hotel_research_task": "output/hotel_research.json",
                    "activity_planning_task": "output/activity_planning.json"
                }
            }
        }

@CrewBase
class AgenticTravelPlanner():
    """AgenticTravelPlanner crew"""

    # agents: List
    # tasks: List
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def Flight_Researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['Flight_Researcher'], # type: ignore[index]
            tools=[FlightSearchTool()],
            verbose=True
        )
    
    @agent
    def Hotel_Researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['Hotel_Researcher'], # type: ignore[index]
            tools=[HotelSearchTool()],
            verbose=True
        )

    @agent
    def Activity_Booker(self) -> Agent:
        return Agent(
            config=self.agents_config['Activity_Booker'], # type: ignore[index]
            tools=[ActivitySearchTool()],
            verbose=True
        )

    @agent
    def Budgeting_Agent(self) -> Agent:
        return Agent(
            config=self.agents_config['Budgeting_Agent'], # type: ignore[index]
            verbose=True
        )
    
    @agent
    def Manager_and_Itinerary_Planner(self) -> Agent:
        return Agent(
            config=self.agents_config['Manager_and_Itinerary_Planner'], # type: ignore[index]
            allow_delegation=True,
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def i_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['i_planning_task'], # type: ignore[index]
            output_pydantic=InitialPlanningTaskOutput,
        )

    @task
    def flight_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['flight_research_task'], # type: ignore[index]
            output_pydantic=FlightResearchTaskOutput

        )
 
    @task
    def hotel_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['hotel_research_task'], # type: ignore[index]
            output_pydantic=HotelResearchTaskOutput,
        )

    @task
    def activity_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['activity_planning_task'], # type: ignore[index]
            output_pydantic = ActivityPlanningTaskOutput
        )

    @task
    def final_assembly_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_assembly_task'],
            output_pydantic = FinalItineraryOutput,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AgenticTravelPlanner crew"""
        manager = self.Manager_and_Itinerary_Planner()
        agents_wo_manager = [a for a in self.agents if a.id != manager.id]
        return Crew(
            agents=agents_wo_manager, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager, # Call the @agent method
        )