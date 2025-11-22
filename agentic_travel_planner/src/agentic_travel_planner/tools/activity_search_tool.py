import os
import requests
import json
from crewai.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class ActivitySearchToolInput(BaseModel):
    """Input schema for Activity Search Tool."""
    updated_remaining_budget: str = Field(..., description="Remaining budget for activities.")
    interests: str = Field(..., description="Interests (e.g. 'museums, food, party').")
    num_travelers: int = Field(default=1, description="Number of travelers.")
    group_category: str = Field(..., description="Group category (e.g. Family).")
    hotel_location: str = Field(..., description="Hotel name or location address.")

class ActivitySearchTool(BaseTool):
    name: str = "search_activities"
    description: str = "Search for activities using the official Geoapify Places API (Step 1: Geocode, Step 2: Search)."
    args_schema: Type[BaseModel] = ActivitySearchToolInput

    def _get_coordinates(self, location_name: str, api_key: str) -> tuple[float, float]:
        """Helper: Converts a text address into Lat/Lon coordinates."""
        url = "https://api.geoapify.com/v1/geocode/search"
        
        # Clean the input: Remove "Address unavailable" text if present
        clean_location = location_name.replace("Address unavailable", "").strip()
        clean_location = clean_location.strip(", ")
        
        if not clean_location or len(clean_location) < 3:
            clean_location = "London, UK" # Fallback

        params = {
            "text": clean_location,
            "limit": "1",
            "apiKey": api_key
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("features"):
                    props = data["features"][0]["properties"]
                    return props.get("lat"), props.get("lon")
        except Exception as e:
            print(f"Geocoding Warning: {e}")
            
        return None, None

    def _map_interests_to_categories(self, interests: str) -> str:
        """Helper: Maps user text interests to Geoapify category codes."""
        categories = []
        interests_lower = interests.lower()
        
        if "museum" in interests_lower or "history" in interests_lower:
            categories.append("entertainment.museum")
            categories.append("tourism.sights")
        if "food" in interests_lower or "restaurant" in interests_lower:
            categories.append("catering.restaurant")
            categories.append("catering.cafe")
        if "party" in interests_lower or "nightlife" in interests_lower:
            categories.append("entertainment.culture")
            categories.append("catering.pub")
        if "park" in interests_lower or "nature" in interests_lower:
            categories.append("leisure.park")
            
        # Default fallback if nothing matches
        if not categories:
            categories = ["tourism.attraction"]
            
        return ",".join(categories)

    def _run(
        self,
        updated_remaining_budget: str,
        interests: str,
        num_travelers: int,
        group_category: str,
        hotel_location: str
    ) -> str:
        
        # 1. AUTHENTICATION
        api_key = os.getenv("GEOAPIFY_KEY")
        if not api_key:
            return json.dumps({"error": "Missing GEOAPIFY_KEY in .env file"}, indent=2)

        # 2. STEP 1: GEOCODE HOTEL LOCATION
        # We need exact coordinates (Lat/Lon) to use the Places API "Circle" filter
        lat, lon = self._get_coordinates(hotel_location, api_key)
        
        if not lat:
            # Hard Fallback to London Center if geocoding fails completely
            lat, lon = 51.5072, -0.1276 

        # 3. STEP 2: SEARCH PLACES API
        url = "https://api.geoapify.com/v2/places"
        
        category_string = self._map_interests_to_categories(interests)
        
        # Search within a 5km (5000 meter) radius of the hotel
        params = {
            "categories": category_string,
            "filter": f"circle:{lon},{lat},5000", 
            "limit": "10",
            "apiKey": api_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            features = data.get("features", [])
            
            activities = []
            for feature in features:
                props = feature.get("properties", {})
                
                name = props.get("name") or props.get("formatted")
                # Skip unnamed results (often just random buildings)
                if not props.get("name"): 
                    continue

                # Estimate cost (API doesn't provide this, but Agent needs it for budget)
                est_cost = 30 * num_travelers 

                activities.append({
                    "name": name,
                    "address": props.get("address_line2") or props.get("formatted", ""),
                    "category": props.get("categories", ["general"])[0],
                    "estimated_cost": est_cost,
                    "currency": "USD",
                    "location_match": "Nearby Hotel"
                })

            if not activities:
                return json.dumps({
                    "status": "no_results",
                    "message": f"No activities found matching {interests} near {hotel_location}",
                    "coordinates_used": f"{lat},{lon}"
                }, indent=2)

            return json.dumps({
                "status": "success",
                "budget_context": f"Remaining Budget: {updated_remaining_budget}",
                "activities_found": activities,
                "instructions": "Select the best 3-4 activities from this list that fit the user's budget and interests."
            }, indent=2)

        except Exception as e:
            return json.dumps({"error": f"Geoapify Places search failed: {str(e)}"}, indent=2)
