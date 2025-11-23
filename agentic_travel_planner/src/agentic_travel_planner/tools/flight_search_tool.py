import os
import requests
import json
from dotenv import load_dotenv
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

class FlightSearchToolInput(BaseModel):
    """Input schema for Flight Search Tool."""
    source: str = Field(..., description="Origin airport's 3-letter IATA Code from where the flight will take off (e.g., 'JFK', 'DEL', 'LAX').")
    destination: str = Field(..., description="Destination airport's 3-letter IATA Code where the flight will land (e.g., 'LAX', 'DEL', 'JFK').")
    start_date: str = Field(..., description="Departure date of the flight in YYYY-MM-DD format (e.g., '2025-12-01').")
    end_date: str = Field(..., description="Return date of the flight in YYYY-MM-DD format (e.g., '2025-12-15').")
    num_travelers: int = Field(default=1, description="Number of travelers.")


class FlightSearchTool(BaseTool):
    name: str = "search_flights"
    description: str = (
        "Search for round-trip flights between two locations with specified dates and number of travelers. "
        "Returns flight options with prices, airlines, and booking details from the booking.com API."
    )
    args_schema: Type[BaseModel] = FlightSearchToolInput

    def _run(
        self,
        source: str,
        destination: str,
        start_date: str,
        end_date: str,
        num_travelers: int
    ) -> str:
        """
        Call the Booking flights API and return a SMALL, summarized JSON payload,
        so the LLM doesn't hit token limits.
        """
        # --- 1. Build request ---
        url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
        api_key = os.getenv("RAPIDAPI_KEY")

        if not api_key:
            return json.dumps(
                {
                    "status": "error",
                    "error": "Missing RAPIDAPI_KEY in environment",
                },
                separators=(",", ":"),
            )

        params = {
            "fromId": f"{source}.AIRPORT",
            "toId": f"{destination}.AIRPORT",
            "departDate": start_date,
            "returnDate": end_date,
            "adults": str(num_travelers),
            "currency_code": "USD"
        }

        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "booking-com15.p.rapidapi.com",
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            response.raise_for_status()
            raw = response.json()

            # --- 2. Extract ONLY the cheap summary we care about ---
            aggregation = raw.get("data", {}).get("aggregation", {})
            stops = aggregation.get("stops", [])

            flights_summary = []
            for stop_info in stops:
                flights_summary.append(
                    {
                        "numberOfStops": stop_info.get("numberOfStops"),
                        "minPrice": stop_info.get("minPrice"),
                        "minPricePerAdult": stop_info.get("minPricePerAdult"),
                        "cheapestAirline": stop_info.get("cheapestAirline"),
                    }
                )

            result = {
                "status": "success",
                "message": "Flight search summary (cheapest options by stop-count). Full raw API response omitted to save tokens.",
                "flights_summary": flights_summary,
            }

            # IMPORTANT: no pretty indent → fewer tokens
            return json.dumps(result, separators=(",", ":"))

        except requests.exceptions.HTTPError as http_err:
            return json.dumps(
                {
                    "status": "error",
                    "error": "HTTP_403" if response.status_code == 403 else f"HTTP error {response.status_code}",
                    "details": response.text[:500]
                },
                separators=(",", ":"),
            )

        except requests.exceptions.RequestException as req_err:
            return json.dumps(
                {"status": "error", "error": f"Request failed: {req_err}"},
                separators=(",", ":"),
            )
        except json.JSONDecodeError as json_err:
            return json.dumps(
                {
                    "status": "error",
                    "error": f"Failed to parse API response: {json_err}",
                    "response_text": response.text,
                },
                separators=(",", ":"),
            )
