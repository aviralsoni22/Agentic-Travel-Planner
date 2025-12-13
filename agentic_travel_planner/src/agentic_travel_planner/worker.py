import os
from celery import Celery
from agentic_travel_planner.crew import AgenticTravelPlanner

# 1. Setup Celery to talk to Redis
# We use 'redis' as the default hostname because that is the standard Docker service name.
# Use 'localhost' only if running manually without Docker.
# redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_url = "redis://redis:6379/0"

celery_app = Celery(
    "travel_tasks",
    broker=redis_url,
    backend=redis_url 
)

# 2. Force Update Configuration 
# This ensures the backend is definitely enabled and handles startup timing
celery_app.conf.update(
    result_backend=redis_url,
    task_track_started=True,
    broker_connection_retry_on_startup=True
)

@celery_app.task(bind=True, name="generate_plan_task")
def generate_plan_task(self, inputs: dict):
    """
    Background task that runs the CrewAI logic.
    """
    try:
        print(f"[Worker] Starting task {self.request.id} with inputs: {inputs}")
        
        # Initialize the Crew
        planner = AgenticTravelPlanner()
        crew_instance = planner.crew()
        
        # Run the Crew (Blocking call: 60-90 seconds)
        result = crew_instance.kickoff(inputs=inputs)
        
        # --- SERIALIZATION ---
        # Celery needs simple JSON. Pydantic objects crash it.
        
        # Check if returned Pydantic model (FinalItineraryOutput)
        if hasattr(result, 'pydantic') and result.pydantic is not None:
            print(f"[Worker] Task {self.request.id} completed successfully (Pydantic).")
            return result.pydantic.model_dump(mode='json')
            
        # Fallback to raw string
        print(f"[Worker] Task {self.request.id} completed (Raw).")
        return {"raw_output": result.raw}
        
    except Exception as e:
        print(f"[Worker] Task {self.request.id} FAILED: {str(e)}")
        return {"status": "failed", "error": str(e)}