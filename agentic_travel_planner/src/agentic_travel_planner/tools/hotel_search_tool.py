import os
import json
import time
import requests
from typing import Dict, Optional, Union
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

from .cache import cached_get

load_dotenv()

RAPID_HOST = "booking-com15.p.rapidapi.com"
DEFAULT_HEADERS = {"X-RapidAPI-Host": RAPID_HOST, "Content-Type": "application/json"}


class HotelSearchToolInput(BaseModel):
    destination: str = Field(..., description="Destination city (e.g., 'London', 'New York').")
    start_date: str = Field(..., description="Check-in date YYYY-MM-DD.")
    end_date: str = Field(..., description="Check-out date YYYY-MM-DD.")
    num_travelers: Union[int, str] = Field(2, description="Number of travelers.")
    group_category: str = Field("Family", description="Group type.")
    interests: str = Field("", description="Interests (metadata only).")
    updated_remaining_budget: Union[float, int, str, None] = Field(None, description="Max total budget for hotel.")
    currency: str = Field("USD", description="Currency.")


def _get_nested(d: Dict, *keys):
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key)
        else:
            return None
    return d


def _extract_hotel_data(item: Dict, currency: str) -> Optional[Dict]:
    prop = item.get("property") or item
    name = prop.get("name") or prop.get("label") or _get_nested(prop, "displayName", "text")
    if not name:
        return None

    price = _get_nested(prop, "composite_price_breakdown", "gross_amount", "value")
    if price is None:
        price = _get_nested(prop, "priceBreakdown", "grossPrice", "value")
    if price is None:
        price = prop.get("price_breakdown", {}).get("all_inclusive_price")
    if price is None:
        return None

    score = prop.get("reviewScore") or prop.get("review_score") or 0
    url = prop.get("booking_url") or prop.get("url")
    return {
        "name": name,
        "price_total": float(price),
        "currency": currency,
        "review_score": score,
        "address": _get_nested(prop, "location", "displayLocation") or "Address unavailable",
        "url": url,
    }


def _geocode_hotel(name: str, address: str, destination: str, api_key: str):
    parts = []
    if name:
        parts.append(name)
    if address and address != "Address unavailable":
        parts.append(address)
    if destination:
        parts.append(destination)
    query_text = ", ".join(parts) if parts else destination
    if not query_text:
        return None, None

    url = "https://api.geoapify.com/v1/geocode/search"
    params = {"text": query_text, "limit": 1, "apiKey": api_key}
    try:
        data = cached_get(
            ("geocode", query_text),
            lambda: requests.get(url, params=params, timeout=20).json(),
        )
        features = data.get("features") or []
        if not features:
            return None, None
        coords = features[0].get("geometry", {}).get("coordinates", [None, None])
        lon, lat = coords[0], coords[1]
        if lon is None or lat is None:
            return None, None
        return lat, lon
    except Exception as e:
        print(f"[HotelSearchTool] Geocoding failed for '{query_text}': {e}")
        return None, None


def _fetch_dest_id(base_city: str, headers: dict) -> dict:
    url = f"https://{RAPID_HOST}/api/v1/hotels/searchDestination"
    resp = requests.get(url, headers=headers, params={"query": base_city}, timeout=20)
    resp.raise_for_status()
    return resp.json()


def _fetch_hotels(params: dict, headers: dict) -> dict:
    url = f"https://{RAPID_HOST}/api/v1/hotels/searchHotels"
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def search_hotels(
    destination: str,
    start_date: str,
    end_date: str,
    num_travelers: int = 2,
    group_category: str = "Family",
    interests: str = "",
    updated_remaining_budget: Optional[float] = None,
    currency: str = "USD",
) -> str:
    """Search Booking.com hotels (cheapest first), geocoded, filtered to the budget.

    Returns up to 5 valid hotels plus the remaining budget after the cheapest one.
    The raw search is cached by city/dates/guests, so re-searching with a different
    budget re-filters cached data instead of hitting the API again.
    """
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        return json.dumps({"error": "Missing RAPIDAPI_KEY"}, indent=2)

    headers = {**DEFAULT_HEADERS, "X-RapidAPI-Key": api_key}
    geoapify_key = os.getenv("GEOAPIFY_KEY") or os.getenv("GEOAPIFY_API_KEY")

    # --- Step 1: destination id (cached by city) ---
    base_city = (destination or "").split(",")[0].strip()
    try:
        dest_data = cached_get(("dest", base_city), lambda: _fetch_dest_id(base_city, headers))
        dest_list = dest_data.get("data") or dest_data.get("results") or []
        if not dest_list:
            return json.dumps({"error": f"City '{destination}' not found."}, indent=2)
        dest_id = dest_list[0].get("dest_id")
        search_type = dest_list[0].get("search_type", "CITY")
    except Exception as e:
        return json.dumps({"error": f"Destination search failed for '{base_city}': {str(e)}"}, indent=2)

    # --- Step 2: hotels (cached by search params, NOT budget) ---
    try:
        params = {
            "dest_id": dest_id,
            "search_type": search_type,
            "arrival_date": start_date,
            "departure_date": end_date,
            "adults": str(num_travelers),
            "currency_code": currency,
            "sort": "price_low_to_high",
        }
        cache_key = ("hotels", dest_id, start_date, end_date, num_travelers, currency)
        data = cached_get(cache_key, lambda: _fetch_hotels(params, headers))
        raw_list = data.get("data", {}).get("hotels") or data.get("result") or []
        time.sleep(1.1)

        valid_hotels = []
        for raw_item in raw_list:
            clean_hotel = _extract_hotel_data(raw_item, currency)
            if not clean_hotel:
                continue
            if geoapify_key:
                lat, lon = _geocode_hotel(clean_hotel["name"], clean_hotel["address"], destination, geoapify_key)
            else:
                lat, lon = None, None
            clean_hotel["latitude"] = lat
            clean_hotel["longitude"] = lon

            if updated_remaining_budget and clean_hotel["price_total"] > float(updated_remaining_budget):
                continue
            valid_hotels.append(clean_hotel)
            if len(valid_hotels) >= 5:
                break

        if not valid_hotels:
            return json.dumps({
                "status": "no_results",
                "message": f"No hotels found in {destination} under {updated_remaining_budget} {currency}",
                "debug_budget": updated_remaining_budget,
            }, indent=2)

        new_remaining_budget = updated_remaining_budget
        if updated_remaining_budget is not None:
            try:
                cheapest = min(valid_hotels, key=lambda h: h["price_total"])
                new_remaining_budget = max(0.0, float(updated_remaining_budget) - float(cheapest["price_total"]))
            except Exception:
                new_remaining_budget = updated_remaining_budget

        return json.dumps({
            "status": "success",
            "hotels": valid_hotels,
            "updated_remaining_budget": new_remaining_budget,
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Hotel search failed: {str(e)}"}, indent=2)


HotelSearchTool = StructuredTool.from_function(
    func=search_hotels,
    name="search_hotels",
    description="Search for hotels on Booking.com. Returns valid prices, ratings and coordinates.",
    args_schema=HotelSearchToolInput,
)
