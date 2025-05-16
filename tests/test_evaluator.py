import pytest
import asyncio
from unittest.mock import patch, AsyncMock

from app.services.evaluator import evaluate_script, process_comparison_job

# Sample test scripts
SCRIPTS = [
    "Buy our amazing product today and change your life forever!",
    "Our product is the best in the market. Don't miss out!"
]

@pytest.mark.asyncio
async def test_evaluate_script():
    """Test that a single script can be evaluated."""
    # Mock the LLM client response
    with patch('app.services.llm_client.query_llm', new_callable=AsyncMock) as mock_query_llm:
        mock_query_llm.return_value = "Score: 8.5\nAnalysis: Great emotional appeal and clear call to action."
        
        # Call the evaluate_script function
        result = await evaluate_script(SCRIPTS[0])
        
        # Assertions
        assert result["script"] == SCRIPTS[0]
        assert result["score"] == 8.5
        assert "Great emotional appeal" in result["analysis"]
        
        # Verify the LLM was called with the correct prompt
        mock_query_llm.assert_called_once()
        prompt_arg = mock_query_llm.call_args[0][0]
        assert SCRIPTS[0] in prompt_arg

@pytest.mark.asyncio
async def test_process_comparison_job():
    """Test that multiple scripts can be processed in a comparison job."""
    job_id = "test-job-123"
    
    # Mock the evaluate_script function
    with patch('app.services.evaluator.evaluate_script', new_callable=AsyncMock) as mock_evaluate:
        # Configure the mock to return different scores for different scripts
        mock_evaluate.side_effect = lambda script, model=None: {
            SCRIPTS[0]: {"script": SCRIPTS[0], "score": 8.5, "analysis": "Great!"},
            SCRIPTS[1]: {"script": SCRIPTS[1], "score": 7.2, "analysis": "Good!"}
        }[script]
        
        # Process the comparison job
        await process_comparison_job(job_id, SCRIPTS)
        
        # Verify the evaluation function was called for each script
        assert mock_evaluate.call_count == len(SCRIPTS)
        
        # Get the stored result
        from app.services.evaluator import get_job_result
        result = get_job_result(job_id)
        
        # Assertions
        assert result["status"] == "COMPLETED"
        assert len(result["evaluations"]) == len(SCRIPTS)
        assert result["winner"]["script"] == SCRIPTS[0]  # First script has higher score
        assert result["winner"]["score"] == 8.5
