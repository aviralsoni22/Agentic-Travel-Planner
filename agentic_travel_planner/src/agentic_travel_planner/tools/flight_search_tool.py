import os
import requests
import json
from dotenv import load_dotenv
from crewai.tools import BaseTool
from typing import Type, Optional, Dict, List
from pydantic import BaseModel, Field

load_dotenv()

class FlightSearchToolInput(BaseModel):
    """Input schema for Flight Search Tool."""
    source: str = Field(..., description="Origin airport IATA Code (e.g., 'DEL').")
    destination: str = Field(..., description="Destination airport IATA Code (e.g., 'BOM').")
    start_date: str = Field(..., description="Departure date in YYYY-MM-DD format.")
    end_date: Optional[str] = Field(None, description="Return date (Ignored for one-way).")
    num_travelers: int = Field(default=1, description="Number of travelers.")

class FlightSearchTool(BaseTool):
    name: str = "search_flights"
    description: str = (
        "Searches for flights and extracts dynamic details directly from the API response: "
        "Airline Names, Flight Numbers, Timings, Duration, and Price."
    )
    args_schema: Type[BaseModel] = FlightSearchToolInput

    def _build_airline_map(self, raw_data: dict) -> Dict[str, str]:
        """
        Dynamically builds a dictionary of {IATA_CODE: Airline Name} 
        by parsing the 'aggregation' and 'flightOffers' sections.
        """
        airline_map = {}

        aggregation = raw_data.get("data", {}).get("aggregation", {})
        airlines_list = aggregation.get("airlines", [])
        
        for airline in airlines_list:
            code = airline.get("iataCode")
            name = airline.get("name")
            if code and name:
                airline_map[code] = name

        return airline_map

    def _run(
        self,
        source: str,
        destination: str,
        start_date: str,
        end_date: Optional[str] = None,
        num_travelers: int = 1
    ) -> str:
        
        url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
        api_key = os.getenv("RAPIDAPI_KEY")

        if not api_key:
            return json.dumps({"status": "error", "error": "Missing RAPIDAPI_KEY"})

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

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            raw_data = response.json()
            
            airline_map = self._build_airline_map(raw_data)

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
                    legs = seg.get("legs", [])
                    for leg in legs:
                        flight_info = leg.get("flightInfo", {})
                        carrier_code = flight_info.get("carrierInfo", {}).get("operatingCarrier")
                        flight_number = flight_info.get("flightNumber")
                        airline_name = airline_map.get(carrier_code)
                        
                        if not airline_name:
                            carriers_data = leg.get("carriersData", [])
                            for carrier in carriers_data:
                                if carrier.get("code") == carrier_code:
                                    airline_name = carrier.get("name")
                                    
                                    if airline_name:
                                        airline_map[carrier_code] = airline_name
                                    break
                        
                        if not airline_name:
                            airline_name = carrier_code if carrier_code else "Unknown Airline"

                        if not flight_number:
                            flight_number = extract_flight_number(str(leg))

                        flight_str = f"{airline_name} {carrier_code} {flight_number}"
                        flight_details.append(flight_str)

                price_data = offer.get("priceBreakdown", {}).get("total", {})
                total_price = price_data.get("units")
                currency = price_data.get("currencyCode")
                detailed_results.append({
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "duration": offer.get("duration", "Unknown"), # Often available at root of offer
                    "total_price": f"{total_price} {currency}",
                    "flight_segments": flight_details,
                    "stops": len(flight_details) - 1
                })

            if not detailed_results:
                return json.dumps({"status": "success", "message": "No flights found.", "data": []})

            return json.dumps({
                "status": "success", 
                "data": detailed_results,
                "count": len(detailed_results)
            }, separators=(",", ":"))

        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)})

# --- TEST EXECUTION ---
# Modify the input parameters as needed
#if __name__ == "__main__":
 #   tool = FlightSearchTool()
    # Test with the input you provided logic for
    #print(tool._run(source="MAA", destination="JAI", start_date="2026-03-10", num_travelers=1))