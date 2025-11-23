import os
import requests
import json
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class ActivitySearchToolInput(BaseModel):
    """Input schema for Activity Search Tool."""
    updated_remaining_budget: str = Field(
        ...,
        description="Remaining budget for activities (string or number, e.g. '355.38')."
    )
    interests: str = Field(
        ...,
        description="Interests (e.g. 'museums, food, party')."
    )
    num_travelers: int = Field(
        default=1,
        description="Number of travelers."
    )
    group_category: str = Field(
        default="mixed",
        description="Group category (e.g. 'Boys only', 'Family', etc.)."
    )
    hotel_location: str = Field(
        ...,
        description="Name or address of the main hotel (e.g. 'Treebo Sunheads, Panaji, Goa, India')."
    )


class ActivitySearchTool(BaseTool):
    name: str = "search_activities"
    description: str = (
        "Search for activities, restaurants, and points of interest near the user's hotel "
        "that match their interests and fit within the remaining budget. Uses Geoapify."
    )
    args_schema: Type[BaseModel] = ActivitySearchToolInput

    def _run(
        self,
        updated_remaining_budget: str,
        interests: str,
        num_travelers: int = 1,
        group_category: str = "mixed",
        hotel_location: str = ""
    ) -> str:
        """
        Use Geoapify to:
        1. Geocode the hotel_location -> lat/lon.
        2. Search for nearby places that match the interests.
        3. Return a SMALL JSON list of candidate activities.

        NOTE: This implementation avoids hardcoded coordinates, so results are
        actually near the hotel (e.g. Panaji, Goa) instead of some demo city.
        """
        # --- 1. Budget parsing ---
        try:
            budget_value = float(str(updated_remaining_budget))
        except (ValueError, TypeError):
            budget_value = None

        api_key = (
            os.getenv("GEOAPIFY_API_KEY")
            or os.getenv("GEOAPIFY_KEY")
            or os.getenv("GEOAPIFY_TOKEN")
        )
        if not api_key:
            return json.dumps(
                {
                    "status": "error",
                    "error": "Missing GEOAPIFY_API_KEY in environment.",
                },
                indent=2,
            )

        if not hotel_location:
            return json.dumps(
                {
                    "status": "error",
                    "error": "hotel_location is required but was empty.",
                },
                indent=2,
            )

        # --- 2. Geocode hotel_location to get lat/lon (NO HARDCODED CITY) ---
        try:
            geocode_url = "https://api.geoapify.com/v1/geocode/search"
            geocode_params = {
                "text": hotel_location,
                "apiKey": api_key,
                "limit": 1,
            }
            geo_resp = requests.get(geocode_url, params=geocode_params, timeout=20)
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()
            features = geo_data.get("features") or []

            if not features:
                return json.dumps(
                    {
                        "status": "no_results",
                        "message": f"Could not geocode hotel location '{hotel_location}'.",
                        "coordinates_used": None,
                    },
                    indent=2,
                )

            # Geoapify returns coordinates as [lon, lat]
            coords = features[0].get("geometry", {}).get("coordinates", [None, None])
            lon, lat = coords[0], coords[1]

            if lon is None or lat is None:
                return json.dumps(
                    {
                        "status": "error",
                        "message": f"Geocoding returned invalid coordinates for '{hotel_location}'.",
                        "coordinates_used": None,
                    },
                    indent=2,
                )
        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "error": f"Geoapify geocoding failed: {str(e)}",
                },
                indent=2,
            )

        # --- 3. Build category filter from 'interests' ---
        interests_lower = interests.lower()
        categories = []

        # Clubs / nightlife
        if "club" in interests_lower or "nightlife" in interests_lower or "party" in interests_lower:
            categories.append("adult.nightclub")
            categories.append("catering.bar")
            categories.append("catering.pub")

        # Water sports / beach
        #if "water" in interests_lower or "beach" in interests_lower:
         #   categories.append("leisure.water_park")

        # Food
        if "food" in interests_lower or "restaurant" in interests_lower or "cafe" in interests_lower:
            categories.append("catering.restaurant")
            categories.append("catering.cafe")

        # History, museum, forts
        if "fort" in interests_lower or "history" in interests_lower or "museum" in interests_lower:
            categories.append("tourism.sights")
            categories.append("entertainment.museum")

        # Fallback (must be valid)
        if not categories:
            categories = ["tourism.sights", "catering.restaurant"]

        categories_str = ",".join(categories)

        # --- 4. Places search near the hotel coords (NOT hardcoded Puri/Odisha) ---
        try:
            places_url = "https://api.geoapify.com/v2/places"
            places_params = {
                "apiKey": api_key,
                "categories": categories_str,
                "limit": 10,  # keep it small
                # proximity bias ensures results are around the hotel
                "filter": f"circle:{lon},{lat},60000",
                "bias": f"proximity:{lon},{lat}",
            }
            places_resp = requests.get(places_url, params=places_params, timeout=20)
            if places_resp.status_code != 200:
                return json.dumps(
                    {
                        "status": "error",
                        "error": f"Geoapify Places search failed with status {places_resp.status_code}",
                        "details": places_resp.text,
                        "request_url": places_resp.url,
                    },
                    indent=2,
                )

            places_data = places_resp.json()

            features = places_data.get("features", [])

            if not features:
                return json.dumps(
                    {
                        "status": "no_results",
                        "message": f"No activities found matching {interests} near {hotel_location}",
                        "coordinates_used": f"{lat},{lon}",
                    },
                    indent=2,
                )

            # --- 5. Build a compact list of activity candidates ---
            activities = []
            estimated_cost_per_activity = 50.0  # simple placeholder
            cumulative_cost = 0.0

            for feat in features:
                props = feat.get("properties", {}) or {}
                g = feat.get("geometry", {}) or {}
                coords = g.get("coordinates", [None, None])
                lon2, lat2 = coords[0], coords[1]

                name = props.get("name") or props.get("address_line1") or "Unnamed place"
                formatted = props.get("formatted")

                # Fallback description from address pieces
                address_pieces = [
                    props.get("address_line1"),
                    props.get("address_line2"),
                    props.get("city"),
                    props.get("state"),
                    props.get("country"),
                ]
                description = ", ".join([p for p in address_pieces if p])

                if not description and formatted:
                    description = formatted

                # Category (pick first if list)
                raw_cats = props.get("categories")
                if isinstance(raw_cats, list) and raw_cats:
                    category = raw_cats[0]
                else:
                    category = raw_cats or "poi"

                cumulative_cost += estimated_cost_per_activity

                activities.append(
                    {
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
                    }
                )

                # Optional: stop if we would obviously exceed the budget
                if budget_value is not None and cumulative_cost >= budget_value:
                    break

            if not activities:
                return json.dumps(
                    {
                        "status": "no_results",
                        "message": f"No activities found matching {interests} near {hotel_location}",
                        "coordinates_used": f"{lat},{lon}",
                    },
                    indent=2,
                )

            return json.dumps(
                {
                    "status": "success",
                    "budget_context": (
                        f"Remaining Budget: {updated_remaining_budget}"
                        if updated_remaining_budget is not None
                        else "Remaining budget unknown"
                    ),
                    "activities_found": activities,
                    "instructions": (
                        "Select the best 3–4 activities from this list that fit "
                        "the user's interests, timings, and budget."
                    ),
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps(
                {
                    "status": "error",
                    "error": f"Geoapify Places search failed: {str(e)}",
                },
                indent=2,
            )

#If you want to test this tool, uncomment the following lines
#run "python activity_search_tool.py" in the terminal

# if __name__ == "__main__":
#     tool = ActivitySearchTool()
#     result = tool.run(
#         updated_remaining_budget="700.0",
#         interests="clubs, Water sports, food, forts, Beaches",
#         num_travelers=2,
#         group_category="Boys only",
#         hotel_location="Treebo Sunheads, Panaji, Goa, India"
#     )
#     print(result)

