import asyncio
from typing import List, Dict, Any, Optional
import logging

from app.services.llm_client import query_llm

# In-memory storage for job results (would use Redis in production)
job_results = {}

async def evaluate_script(script: str, model: Optional[str] = None) -> Dict[str, Any]:
    """
    Evaluate a single TV advertisement script using an LLM.
    
    Args:
        script: The advertisement script text
        model: Optional LLM model to use
        
    Returns:
        Dictionary with score and analysis
    """
    prompt = f"""
    You are an expert in TV advertisement effectiveness. Evaluate the following TV advertisement 
    script on a scale from 1-10, where 10 is the highest quality.
    
    SCRIPT:
    {script}
    
    Provide your evaluation in the following format:
    Score: [numeric score between 1-10]
    Analysis: [brief analysis explaining the score]
    """
    
    try:
        response = await query_llm(prompt, model)
        
        # Parse the response to extract score and analysis
        # This is a simple parsing that assumes the format is followed
        lines = response.strip().split("\n")
        score = 0
        analysis = ""
        
        for line in lines:
            if line.lower().startswith("score:"):
                try:
                    score = float(line.split(":", 1)[1].strip())
                except ValueError:
                    score = 0
            elif line.lower().startswith("analysis:"):
                analysis = line.split(":", 1)[1].strip()
        
        return {
            "script": script,
            "score": score,
            "analysis": analysis or response  # Fallback to full response if parsing fails
        }
    except Exception as e:
        logging.error(f"Error evaluating script: {e}")
        return {
            "script": script,
            "score": 0,
            "analysis": f"Error during evaluation: {str(e)}"
        }

async def process_comparison_job(job_id: str, scripts: List[str], model: Optional[str] = None):
    """
    Process a comparison job asynchronously.
    
    Args:
        job_id: Unique identifier for the job
        scripts: List of TV advertisement scripts to compare
        model: Optional LLM model to use
    """
    # Initialize job result
    job_results[job_id] = {"status": "PROCESSING"}
    
    try:
        # Evaluate all scripts concurrently
        evaluation_tasks = [evaluate_script(script, model) for script in scripts]
        evaluations = await asyncio.gather(*evaluation_tasks)
        
        # Sort evaluations by score (descending)
        evaluations = sorted(evaluations, key=lambda x: x["score"], reverse=True)
        
        # Store results
        job_results[job_id] = {
            "job_id": job_id,
            "status": "COMPLETED",
            "evaluations": evaluations,
            "winner": evaluations[0] if evaluations else None
        }
    except Exception as e:
        logging.error(f"Error processing comparison job {job_id}: {e}")
        job_results[job_id] = {
            "job_id": job_id,
            "status": "ERROR",
            "error": str(e),
            "evaluations": []
        }

def get_job_result(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the result of a job by its ID.
    
    Args:
        job_id: The unique job identifier
        
    Returns:
        Job result dictionary or None if not found
    """
    return job_results.get(job_id)
