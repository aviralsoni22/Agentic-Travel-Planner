from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from celery.result import AsyncResult
from .worker import generate_plan_task, celery_app

app = FastAPI(
    title="Async Agentic Travel Planner",
    description="Non-blocking API using Redis & Celery",
    version="2.0.0"
)

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
    task_result = AsyncResult(task_id, app=celery_app)

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