import os
import json
import requests
from dotenv import load_dotenv
from typing import Union
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

from .cache import cached_get

load_dotenv()


class ActivitySearchToolInput(BaseModel):
    """Input schema for Activity Search Tool."""
    updated_remaining_budget: Union[float, int, str] = Field(..., description="Remaining budget for activities (e.g. '355.38').")
    interests: str = Field(..., description="Interests (e.g. 'museums, food, party').")
    num_travelers: Union[int, str] = Field(default=1, description="Number of travelers.")
    group_category: str = Field(default="mixed", description="Group category (e.g. 'Boys only', 'Family').")
    hotel_location: str = Field(..., description="Name or address of the main hotel to anchor the search near.")


def _geocode(hotel_location: str, api_key: str):
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {"text": hotel_location, "apiKey": api_key, "limit": 1}
    data = cached_get(("geocode", hotel_location), lambda: requests.get(url, params=params, timeout=20).json())
    features = data.get("features") or []
    if not features:
        return None, None
    coords = features[0].get("geometry", {}).get("coordinates", [None, None])
    return coords[1], coords[0]  # lat, lon


def _categories_for(interests: str) -> list[str]:
    il = interests.lower()
    cats: list[str] = []
    if "club" in il or "nightlife" in il or "party" in il:
        cats += ["adult.nightclub", "catering.bar", "catering.pub"]
    if "food" in il or "restaurant" in il or "cafe" in il:
        cats += ["catering.restaurant", "catering.cafe"]
    if "fort" in il or "history" in il or "museum" in il:
        cats += ["tourism.sights", "entertainment.museum"]
    return cats or ["tourism.sights", "catering.restaurant"]


def search_activities(
    updated_remaining_budget: str,
    interests: str,
    num_travelers: int = 1,
    group_category: str = "mixed",
    hotel_location: str = "",
) -> str:
    """Find activities/restaurants/POIs near the hotel matching interests and budget.

    Geocodes the hotel, then searches Geoapify Places within ~60km. Both calls are
    cached, so re-planning near the same hotel adds no new API calls.
    """
    try:
        budget_value = float(str(updated_remaining_budget))
    except (ValueError, TypeError):
        budget_value = None

    api_key = os.getenv("GEOAPIFY_API_KEY") or os.getenv("GEOAPIFY_KEY") or os.getenv("GEOAPIFY_TOKEN")
    if not api_key:
        return json.dumps({"status": "error", "error": "Missing GEOAPIFY_API_KEY in environment."}, indent=2)
    if not hotel_location:
        return json.dumps({"status": "error", "error": "hotel_location is required but was empty."}, indent=2)

    try:
        lat, lon = _geocode(hotel_location, api_key)
        if lat is None or lon is None:
            return json.dumps({
                "status": "no_results",
                "message": f"Could not geocode hotel location '{hotel_location}'.",
            }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": f"Geoapify geocoding failed: {str(e)}"}, indent=2)

    categories_str = ",".join(_categories_for(interests))

    try:
        url = "https://api.geoapify.com/v2/places"
        params = {
            "apiKey": api_key,
            "categories": categories_str,
            "limit": 10,
            "filter": f"circle:{lon},{lat},60000",
            "bias": f"proximity:{lon},{lat}",
        }
        places_data = cached_get(
            ("places", round(lat, 4), round(lon, 4), categories_str),
            lambda: requests.get(url, params=params, timeout=20).json(),
        )
        features = places_data.get("features", [])
        if not features:
            return json.dumps({
                "status": "no_results",
                "message": f"No activities found matching {interests} near {hotel_location}",
                "coordinates_used": f"{lat},{lon}",
            }, indent=2)

        activities = []
        estimated_cost_per_activity = 50.0  # placeholder — Geoapify has no pricing
        cumulative_cost = 0.0
        for feat in features:
            props = feat.get("properties", {}) or {}
            g = feat.get("geometry", {}) or {}
            coords = g.get("coordinates", [None, None])
            lon2, lat2 = coords[0], coords[1]

            name = props.get("name") or props.get("address_line1") or "Unnamed place"
            formatted = props.get("formatted")
            address_pieces = [props.get("address_line1"), props.get("address_line2"),
                              props.get("city"), props.get("state"), props.get("country")]
            description = ", ".join([p for p in address_pieces if p]) or formatted

            raw_cats = props.get("categories")
            category = raw_cats[0] if isinstance(raw_cats, list) and raw_cats else (raw_cats or "poi")

            cumulative_cost += estimated_cost_per_activity
            activities.append({
                "name": name,
                "description": description or formatted,
                "category": category,
                "cost": estimated_cost_per_activity,
                "location": formatted or description,
                "latitude": lat2,
                "longitude": lon2,
                "scheduled_time": None,
                "estimated_travel_time_minutes": None,
                "booking_url": None,
                "discount_info": None,
            })
            if budget_value is not None and cumulative_cost >= budget_value:
                break

        return json.dumps({
            "status": "success",
            "budget_context": f"Remaining Budget: {updated_remaining_budget}",
            "activities_found": activities,
            "instructions": "Select the best 3-4 activities that fit the interests, timings and budget.",
        }, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": f"Geoapify Places search failed: {str(e)}"}, indent=2)


ActivitySearchTool = StructuredTool.from_function(
    func=search_activities,
    name="search_activities",
    description=(
        "Search activities, restaurants and points of interest near the hotel that match "
        "the user's interests and fit the remaining budget. Uses Geoapify."
    ),
    args_schema=ActivitySearchToolInput,
)
