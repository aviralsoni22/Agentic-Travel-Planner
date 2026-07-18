import os
import json
import requests
from typing import Optional, Dict, Union
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

from .cache import cached_get

load_dotenv()


class FlightSearchToolInput(BaseModel):
    """Input schema for Flight Search Tool."""
    source: str = Field(..., description="Origin airport IATA Code (e.g., 'DEL').")
    destination: str = Field(..., description="Destination airport IATA Code (e.g., 'BOM').")
    start_date: str = Field(..., description="Departure date in YYYY-MM-DD format.")
    end_date: Optional[str] = Field(None, description="Return date (Ignored for one-way).")
    num_travelers: Union[int, str] = Field(default=1, description="Number of travelers.")


def _build_airline_map(raw_data: dict) -> Dict[str, str]:
    """Build {IATA_CODE: Airline Name} from the aggregation section."""
    airline_map: Dict[str, str] = {}
    aggregation = raw_data.get("data", {}).get("aggregation", {})
    for airline in aggregation.get("airlines", []):
        code = airline.get("iataCode")
        name = airline.get("name")
        if code and name:
            airline_map[code] = name
    return airline_map


def _fetch_flights(source: str, destination: str, start_date: str, num_travelers: int) -> dict:
    """Raw RapidAPI call. Cached by the caller so retries don't re-hit the API."""
    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        return {"__error__": "Missing RAPIDAPI_KEY"}

    params = {
        "fromId": f"{source}.AIRPORT",
        "toId": f"{destination}.AIRPORT",
        "departDate": start_date,
        "adults": str(num_travelers),
        "currency": "USD",
        "sortOrder": "BEST",
    }
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com",
    }
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def search_flights(
    source: str,
    destination: str,
    start_date: str,
    end_date: Optional[str] = None,
    num_travelers: int = 1,
) -> str:
    """Search one-way flights and extract airline, flight number, timings and price.

    ONE-WAY only. For a round trip, call this twice (outbound, then return with
    source/destination swapped). The end_date parameter is ignored.
    """
    try:
        key = ("flights", source, destination, start_date, num_travelers)
        raw_data = cached_get(key, lambda: _fetch_flights(source, destination, start_date, num_travelers))
        if isinstance(raw_data, dict) and raw_data.get("__error__"):
            return json.dumps({"status": "error", "error": raw_data["__error__"]})

        airline_map = _build_airline_map(raw_data)
        flight_offers = raw_data.get("data", {}).get("flightOffers", [])
        detailed_results = []

        for offer in flight_offers[:10]:
            segments = offer.get("segments", [])
            if not segments:
                continue
            departure_time = segments[0].get("departureTime")
            arrival_time = segments[-1].get("arrivalTime")

            flight_details = []
            for seg in segments:
                for leg in seg.get("legs", []):
                    flight_info = leg.get("flightInfo", {})
                    carrier_code = flight_info.get("carrierInfo", {}).get("operatingCarrier")
                    flight_number = flight_info.get("flightNumber")
                    airline_name = airline_map.get(carrier_code)

                    if not airline_name:
                        for carrier in leg.get("carriersData", []):
                            if carrier.get("code") == carrier_code:
                                airline_name = carrier.get("name")
                                if airline_name:
                                    airline_map[carrier_code] = airline_name
                                break
                    if not airline_name:
                        airline_name = carrier_code if carrier_code else "Unknown Airline"
                    if not flight_number:
                        flight_number = "N/A"

                    flight_details.append(f"{airline_name} {carrier_code} {flight_number}")

            price_data = offer.get("priceBreakdown", {}).get("total", {})
            total_price = price_data.get("units")
            currency = price_data.get("currencyCode")
            detailed_results.append({
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "duration": offer.get("duration", "Unknown"),
                "total_price": f"{total_price} {currency}",
                "flight_segments": flight_details,
                "stops": len(flight_details) - 1,
            })

        if not detailed_results:
            return json.dumps({"status": "success", "message": "No flights found.", "data": []})

        return json.dumps(
            {"status": "success", "data": detailed_results, "count": len(detailed_results)},
            separators=(",", ":"),
        )
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})


FlightSearchTool = StructuredTool.from_function(
    func=search_flights,
    name="search_flights",
    description=(
        "Searches for ONE-WAY flights and extracts airline names, flight numbers, "
        "timings, duration and price from the live API. Call twice for a round trip."
    ),
    args_schema=FlightSearchToolInput,
)
