from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import uuid

from app import schemas
from app.services import evaluator

router = APIRouter(prefix="/api", tags=["scripts"])

# In-memory storage for job results (would use Redis in production)
job_results = {}

@router.post("/compare", response_model=schemas.ComparisonJob)
async def start_comparison(request: schemas.ComparisonRequest, background_tasks: BackgroundTasks):
    """
    Start a comparison job for multiple TV advertisement scripts.
    
    Returns a job ID that can be used to retrieve results.
    """
    scripts = request.scripts
    
    # Validate input
    if len(scripts) < 2:
        raise HTTPException(status_code=422, detail="Provide at least 2 scripts to compare.")
    
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Start background comparison task
    background_tasks.add_task(
        evaluator.process_comparison_job,
        job_id=job_id,
        scripts=scripts,
        model=request.model
    )
    
    return schemas.ComparisonJob(job_id=job_id, status="PROCESSING")

@router.get("/compare/{job_id}/results", response_model=schemas.ComparisonResult)
async def get_comparison_results(job_id: str):
    """
    Retrieve the results of a comparison job by its ID.
    
    If the job is still processing, a 202 status is returned.
    """
    result = evaluator.get_job_result(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if result.get("status") == "PROCESSING":
        raise HTTPException(status_code=202, detail="Results not ready yet")
    
    return result
