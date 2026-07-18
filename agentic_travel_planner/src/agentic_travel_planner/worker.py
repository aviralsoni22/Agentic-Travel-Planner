import os
from celery import Celery

from agentic_travel_planner.graph import build_graph
from agentic_travel_planner import tools

# Redis: honor REDIS_URL (docker-compose sets it); fall back to the compose service name.
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery("travel_tasks", broker=redis_url, backend=redis_url)
celery_app.conf.update(
    result_backend=redis_url,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)

# Compile the graph once at import (reused across tasks in this worker process).
_GRAPH = build_graph()


def _initial_state(inputs: dict) -> dict:
    return {
        **inputs,
        "feedback": [],
        "revision_count": 0,
        "flight_retries": 0,
        "hotel_retries": 0,
        "activity_retries": 0,
        "api_calls": 0,
    }


@celery_app.task(bind=True, name="generate_plan_task")
def generate_plan_task(self, inputs: dict):
    """Background task: run the LangGraph pipeline and return a JSON-serializable plan."""
    try:
        print(f"[Worker] Starting task {self.request.id} with inputs: {inputs}")
        tools.reset_counter()

        final_state = _GRAPH.invoke(
            _initial_state(inputs),
            config={"recursion_limit": 60},  # bounded by revision caps; headroom for loops
        )

        itinerary = final_state.get("final_itinerary")
        if itinerary is not None:
            print(f"[Worker] Task {self.request.id} completed ({tools.API_CALLS['count']} API calls).")
            return itinerary.model_dump(mode="json")

        print(f"[Worker] Task {self.request.id} produced no itinerary.")
        return {"status": "failed", "error": "No itinerary was produced."}

    except Exception as e:
        print(f"[Worker] Task {self.request.id} FAILED: {str(e)}")
        return {"status": "failed", "error": str(e)}
