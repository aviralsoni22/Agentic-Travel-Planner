
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, Field
# from typing import List, Optional
# from agentic_travel_planner.crew import AgenticTravelPlanner
# import uvicorn

# app = FastAPI(
#     title="Agentic Travel Planner API",
#     description="API for generating travel itineraries using CrewAI",
#     version="1.0.0"
# )

# class TravelPlanRequest(BaseModel):
#     source: str = Field(..., description="Origin city/region/country for the trip")
#     destination: str = Field(..., description="Trip destination city/region/country")
#     start_date: str = Field(..., description="Trip start date (YYYY-MM-DD)")
#     end_date: str = Field(..., description="Trip end date (YYYY-MM-DD)")
#     num_travelers: int = Field(..., description="Number of travelers")
#     budget: int = Field(..., description="Total budget for the trip")
#     interests: str = Field(..., description="Comma-separated list of interests")
#     group_category: str = Field(..., description="Group type (e.g., solo, couple, family, friends)")
#     currency: str = Field(..., description="Currency for the trip")

# @app.post("/plan")
# def generate_plan(request: TravelPlanRequest):
#     """
#     Trigger the CrewAI travel planner with the provided inputs.
#     """
#     inputs = request.dict()
    
#     # Ensure budget and other numeric fields are correctly typed if needed by the crew
#     # The Pydantic model ensures they are ints, which matches the main.py usage.
    
#     try:
#         # Initialize and kick off the crew
#         crew_instance = AgenticTravelPlanner().crew()
#         result = crew_instance.kickoff(inputs=inputs)
        
#         # Return the raw result or a structured response
#         # result.raw contains the final string output
        
#         if hasattr(result, 'pydantic') and result.pydantic is not None:
#             plan_obj = result.pydantic    
#             return {
#                 "status": "success",
#                 "plan": plan_obj.model_dump()
#             }
#         return {
#             "status": "success",
#             "plan": result.raw,
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from celery.result import AsyncResult
# Import the task we created in Step #2
# We use relative import since they are in the same package
from .worker import generate_plan_task 

app = FastAPI(
    title="Async Agentic Travel Planner",
    description="Non-blocking API using Redis & Celery",
    version="2.0.0"
)

# --- 1. Define the Input Model (Same as before) ---
class TravelPlanRequest(BaseModel):
    source: str = Field(..., description="Origin city/region/country")
    destination: str = Field(..., description="Trip destination city/region/country")
    start_date: str = Field(..., description="Trip start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Trip end date (YYYY-MM-DD)")
    num_travelers: int = Field(..., description="Number of travelers")
    budget: int = Field(..., description="Total budget for the trip")
    interests: str = Field(..., description="Comma-separated list of interests")
    group_category: str = Field(..., description="Group type")
    currency: str = Field(..., description="Currency")

# --- 2. The Submission Endpoint ---
@app.post("/plan")
def submit_plan(request: TravelPlanRequest):
    """
    Submits a job to the Redis Queue and returns a Task ID immediately.
    """
    # Convert Pydantic model to a standard dictionary
    inputs = request.model_dump()
    
    # .delay() is the Magic Command.
    # It sends the data to Redis instead of running the function here.
    # This takes ~0.1 seconds.
    task = generate_plan_task.delay(inputs)
    
    return {
        "status": "queued",
        "task_id": task.id,
        "message": "Plan is generating in the background. Poll /plan/status/{task_id}"
    }

# --- 3. The Status Check Endpoint ---
@app.get("/plan/status/{task_id}")
def get_status(task_id: str):
    """
    Check the status of the background job using the Task ID.
    """
    # Look up the task in Redis
    task_result = AsyncResult(task_id)

    if task_result.state == 'PENDING':
        return {"status": "processing", "message": "Agents are working..."}
    
    elif task_result.state == 'SUCCESS':
        # The worker returns the result dictionary here
        return {
            "status": "completed", 
            "plan": task_result.result
        }
    
    elif task_result.state == 'FAILURE':
        return {
            "status": "failed", 
            "error": str(task_result.result)
        }
    
    # Catch-all for other states (STARTED, RETRY, etc.)
    return {"status": task_result.state}