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
        num_travelers: int = 1
    ) -> str:
        """
        Search for flights using the RapidAPI booking.com endpoint.

        Args:
            source: Origin airport/city
            destination: Destination airport/city
            start_date: Departure date (YYYY-MM-DD)
            end_date: Return date (YYYY-MM-DD)
            num_travelers: Number of adult travelers

        Returns:
            JSON string with flight search results
        """
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key:
            return json.dumps({
                "error": "RAPIDAPI_KEY environment variable is not set. Please add it to your .env file.",
                "status": "error"
            }, indent=2)

        url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"

        querystring = {
            "fromId": f"{source}.AIRPORT",
            "toId": f"{destination}.AIRPORT",
            "departDate": start_date,
            "returnDate": end_date,
            "adults": str(num_travelers),
            "currency_code": "USD"
        }

        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "booking-com15.p.rapidapi.com"
        }

        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            result = response.json()

            # Format the response for better readability
            return json.dumps(result, indent=2)

        except requests.exceptions.HTTPError as http_err:
            return json.dumps({
                "error": f"HTTP error occurred: {http_err}",
                "status_code": http_err.response.status_code,
                "response_text": http_err.response.text,
                "status": "error"
            }, indent=2)
        except requests.exceptions.RequestException as req_err:
            return json.dumps({
                "error": f"Failed to search flights: {req_err}",
                "status": "error"
            }, indent=2)
        except json.JSONDecodeError as json_err:
            return json.dumps({
                "error": f"Failed to parse API response: {json_err}",
                "response_text": response.text,
                "status": "error"
            }, indent=2)