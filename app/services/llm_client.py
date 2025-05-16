import os
from typing import Optional
import logging
from litellm import completion
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Default model to use if none specified
DEFAULT_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-4")

async def query_llm(prompt: str, model: Optional[str] = None) -> str:
    """
    Query an LLM using LiteLLM for provider-agnostic LLM calls.
    
    Args:
        prompt: The prompt text to send to the LLM
        model: The LLM model to use (defaults to env variable or gpt-4)
        
    Returns:
        The LLM response text
    """
    try:
        model_name = model or DEFAULT_MODEL
        
        # Log the model being used
        logging.info(f"Querying LLM model: {model_name}")
        
        # Make the LLM API call
        response = completion(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        
        # Extract content from response
        content = response.choices[0].message.content
        return content
    except Exception as e:
        logging.error(f"Error querying LLM: {str(e)}")
        raise
