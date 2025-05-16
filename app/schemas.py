from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ComparisonRequest(BaseModel):
    """Request model for script comparison."""
    scripts: List[str] = Field(..., description="List of TV advertisement scripts to compare")
    model: Optional[str] = Field(None, description="LLM model to use for evaluation")

class ScriptEvaluation(BaseModel):
    """Model for individual script evaluation results."""
    script: str = Field(..., description="The original script text")
    score: float = Field(..., description="Score from 1-10")
    analysis: str = Field(..., description="Qualitative analysis of the script")

class ComparisonJob(BaseModel):
    """Response model for job creation."""
    job_id: str = Field(..., description="Unique identifier for this comparison job")
    status: str = Field(..., description="Current status of the job")

class ComparisonResult(BaseModel):
    """Response model for comparison results."""
    job_id: str = Field(..., description="Unique identifier for this comparison job")
    status: str = Field(..., description="Status of the job (COMPLETED or ERROR)")
    evaluations: List[ScriptEvaluation] = Field(..., description="Individual evaluations for each script")
    winner: Optional[ScriptEvaluation] = Field(None, description="The highest scoring script")
    error: Optional[str] = Field(None, description="Error message if job failed")
