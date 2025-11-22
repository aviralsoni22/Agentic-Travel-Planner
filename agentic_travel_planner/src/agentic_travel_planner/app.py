
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from agentic_travel_planner.crew import AgenticTravelPlanner
import uvicorn

app = FastAPI(
    title="Agentic Travel Planner API",
    description="API for generating travel itineraries using CrewAI",
    version="1.0.0"
)

class TravelPlanRequest(BaseModel):
    source: str = Field(..., description="Origin city/region/country for the trip")
    destination: str = Field(..., description="Trip destination city/region/country")
    start_date: str = Field(..., description="Trip start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Trip end date (YYYY-MM-DD)")
    trip_duration: int = Field(..., description="Trip duration in days")
    num_travelers: int = Field(..., description="Number of travelers")
    budget: int = Field(..., description="Total budget for the trip")
    interests: str = Field(..., description="Comma-separated list of interests")
    group_category: str = Field(..., description="Group type (e.g., solo, couple, family, friends)")

@app.post("/plan")
def generate_plan(request: TravelPlanRequest):
    """
    Trigger the CrewAI travel planner with the provided inputs.
    """
    inputs = request.dict()
    
    # Ensure budget and other numeric fields are correctly typed if needed by the crew
    # The Pydantic model ensures they are ints, which matches the main.py usage.
    
    try:
        # Initialize and kick off the crew
        crew_instance = AgenticTravelPlanner().crew()
        result = crew_instance.kickoff(inputs=inputs)
        
        # Return the raw result or a structured response
        # result.raw contains the final string output
        return {
            "status": "success",
            "plan": result.raw,
            # If you want structured output and your crew returns it, you might access result.pydantic or similar
            # For now, returning the raw text as requested.
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
