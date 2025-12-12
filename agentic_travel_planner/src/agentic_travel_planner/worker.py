import os
from celery import Celery
from agentic_travel_planner.crew import AgenticTravelPlanner

# 1. Setup Celery to talk to Redis
# We use 'travel_redis' as the hostname because that is defined in docker-compose
# 'localhost' is the fallback for local testing without Docker
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "travel_tasks",
    broker=redis_url,
    backend=redis_url
)

@celery_app.task(bind=True, name="generate_plan_task")
def generate_plan_task(self, inputs: dict):
    """
    Background task that runs the CrewAI logic.
    """
    try:
        print(f"[Worker] Starting task {self.request.id} with inputs: {inputs}")
        
        # Initialize the Crew
        # This uses your existing logic from crew.py
        planner = AgenticTravelPlanner()
        crew_instance = planner.crew()
        
        # Run the Crew
        # This is the blocking call that takes 60-90 seconds
        result = crew_instance.kickoff(inputs=inputs)
        
        # --- CRITICAL SERIALIZATION STEP ---
        # Celery needs a simple JSON/Dictionary to save to Redis.
        # It cannot crash on complex Pydantic objects.
        
        # Check if your crew returned a Pydantic model (FinalItineraryOutput)
        if hasattr(result, 'pydantic') and result.pydantic is not None:
            print(f"[Worker] Task {self.request.id} completed successfully (Pydantic).")
            return result.pydantic.model_dump(mode = 'json')
            
        # Fallback to raw string if Pydantic parsing failed
        print(f"[Worker] Task {self.request.id} completed (Raw).")
        return {"raw_output": result.raw}
        
    except Exception as e:
        print(f"[Worker] Task {self.request.id} FAILED: {str(e)}")
        # Return a failed status so the API knows what happened
        return {"status": "failed", "error": str(e)}