import os
import asyncio
from celery import Celery
from typing import List, Dict, Any, Optional

from app.services.evaluator import evaluate_script

# Configure Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("koth", broker=redis_url, backend=redis_url)

# Configure Celery serialization
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="evaluate_script")
def evaluate_script_task(script: str, model: Optional[str] = None) -> Dict[str, Any]:
    """
    Celery task to evaluate a single script.
    
    This runs the async evaluate_script function in a synchronous context.
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(evaluate_script(script, model))

@celery_app.task(name="aggregate_results")
def aggregate_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Celery task to aggregate individual script evaluation results.
    
    Args:
        results: List of script evaluation results
        
    Returns:
        Aggregated comparison results
    """
    # Sort evaluations by score (descending)
    evaluations = sorted(results, key=lambda x: x["score"], reverse=True)
    
    return {
        "status": "COMPLETED",
        "evaluations": evaluations,
        "winner": evaluations[0] if evaluations else None
    }
