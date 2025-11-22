import os
import json
import time
import requests
from typing import Type, Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator
from crewai.tools import BaseTool

load_dotenv()

# Constants
RAPID_HOST = "booking-com15.p.rapidapi.com"
# Note: We use headers to force JSON response where possible
DEFAULT_HEADERS = {
    "X-RapidAPI-Host": RAPID_HOST,
    "Content-Type": "application/json"
}

class HotelSearchToolInput(BaseModel):
    destination: str = Field(..., description="Destination city (e.g., 'London', 'New York').")
    start_date: str = Field(..., description="Check-in date YYYY-MM-DD.")
    end_date: str = Field(..., description="Check-out date YYYY-MM-DD.")
    num_travelers: int = Field(2, description="Number of travelers.")
    group_category: str = Field("Family", description="Group type.")
    interests: str = Field("", description="Interests (metadata only).")
    updated_remaining_budget: Optional[float] = Field(None, description="Max total budget for hotel.")
    currency_code: str = Field("USD", description="Currency code.")

class HotelSearchTool(BaseTool):
    name: str = "search_hotels"
    description: str = "Search for hotels on Booking.com. Returns valid prices and details."
    args_schema: Type[BaseModel] = HotelSearchToolInput

    def _get_nested(self, d: Dict, *keys):
        """Helper to safely get nested keys."""
        for key in keys:
            if isinstance(d, dict):
                d = d.get(key)
            else:
                return None
        return d

    def _extract_hotel_data(self, item: Dict, currency: str) -> Optional[Dict]:
        """
        Normalize the messy Booking.com API response into a clean format.
        Handles cases where data is inside a 'property' wrapper or at root.
        """
        # 1. Unwrap if necessary
        prop = item.get("property") or item
        
        # 2. Extract Name
        name = prop.get("name") or prop.get("label") or self._get_nested(prop, "displayName", "text")
        if not name:
            return None # Skip invalid entries

        # 3. Extract Price (The trickiest part)
        price = None
        
        # Path A: composite_price_breakdown -> gross_amount -> value
        price = self._get_nested(prop, "composite_price_breakdown", "gross_amount", "value")
        
        # Path B: priceBreakdown -> grossPrice -> value
        if price is None:
            price = self._get_nested(prop, "priceBreakdown", "grossPrice", "value")

        # Path C: price_breakdown -> all_inclusive_price
        if price is None:
            price = prop.get("price_breakdown", {}).get("all_inclusive_price")

        if price is None:
            return None # Skip hotels with no price data

        # 4. Extract Rating
        score = prop.get("reviewScore") or prop.get("review_score") or 0
        
        # 5. Extract Image/URL (Optional)
        url = prop.get("booking_url") or prop.get("url")

        return {
            "name": name,
            "price_total": float(price),
            "currency": currency,
            "review_score": score,
            "address": self._get_nested(prop, "location", "displayLocation") or "Address unavailable",
            "url": url
        }

    def _run(self, **kwargs) -> str:
        inp = HotelSearchToolInput(**kwargs)
        api_key = os.getenv("RAPIDAPI_KEY")
        
        if not api_key:
            return json.dumps({"error": "Missing RAPIDAPI_KEY"}, indent=2)

        headers = {**DEFAULT_HEADERS, "X-RapidAPI-Key": api_key}

        # --- Step 1: Get Destination ID ---
        try:
            dest_url = f"https://{RAPID_HOST}/api/v1/hotels/searchDestination"
            dest_resp = requests.get(dest_url, headers=headers, params={"query": inp.destination})
            dest_resp.raise_for_status()
            dest_data = dest_resp.json()
            
            dest_list = dest_data.get("data") or dest_data.get("results") or []
            if not dest_list:
                return json.dumps({"error": f"City '{inp.destination}' not found."}, indent=2)
            
            dest_id = dest_list[0].get("dest_id")
            search_type = dest_list[0].get("search_type", "CITY")
            
        except Exception as e:
            return json.dumps({"error": f"Destination search failed: {str(e)}"}, indent=2)

        # --- Step 2: Search Hotels ---
        try:
            search_url = f"https://{RAPID_HOST}/api/v1/hotels/searchHotels"
            params = {
                "dest_id": dest_id,
                "search_type": search_type,
                "arrival_date": inp.start_date,
                "departure_date": inp.end_date,
                "adults": str(inp.num_travelers),
                "currency_code": inp.currency_code,
                "sort": "price_low_to_high" # Get cheapest first to fit budget
            }
            
            hotel_resp = requests.get(search_url, headers=headers, params=params)
            hotel_resp.raise_for_status()
            data = hotel_resp.json()
            
            # Handle different root structures (data.hotels, or just results)
            raw_list = data.get("data", {}).get("hotels") or data.get("result") or []

            valid_hotels = []
            for raw_item in raw_list:
                clean_hotel = self._extract_hotel_data(raw_item, inp.currency_code)
                
                if clean_hotel:
                    # Apply Budget Filter
                    if inp.updated_remaining_budget:
                        if clean_hotel['price_total'] > float(inp.updated_remaining_budget):
                            continue # Skip expensive hotels
                    
                    valid_hotels.append(clean_hotel)
                    
                if len(valid_hotels) >= 5:
                    break

            if not valid_hotels:
                return json.dumps({
                    "status": "no_results", 
                    "message": f"No hotels found in {inp.destination} under {inp.updated_remaining_budget} {inp.currency_code}",
                    "debug_budget": inp.updated_remaining_budget
                }, indent=2)

            return json.dumps({
                "status": "success",
                "hotels": valid_hotels,
                "updated_remaining_budget": inp.updated_remaining_budget # Pass it back or modify if needed
            }, indent=2)

        except Exception as e:
            return json.dumps({"error": f"Hotel search failed: {str(e)}"}, indent=2)