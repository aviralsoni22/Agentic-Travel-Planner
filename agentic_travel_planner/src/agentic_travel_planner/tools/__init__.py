from .flight_search_tool import FlightSearchTool
from .hotel_search_tool import HotelSearchTool
from .activity_search_tool import ActivitySearchTool

__all__ = [
    "FlightSearchTool", "HotelSearchTool", "ActivitySearchTool",
    "search_flights", "search_hotels", "search_activities",
]

def search_flights():
    return FlightSearchTool()

def search_hotels():
    return HotelSearchTool()

def search_activities():
    return ActivitySearchTool()
