"""
Utility functions for the backend
"""

import logging
from typing import Dict, Any
import requests
from config import settings


logger = logging.getLogger(__name__)


def check_ollama_health() -> Dict[str, Any]:
    """
    Check if Ollama service is accessible
    
    Returns:
        Dict with health status information
    """
    try:
        response = requests.get(
            f"{settings.OLLAMA_BASE_URL}/api/tags",
            timeout=5
        )
        return {
            "status": "online" if response.status_code == 200 else "offline",
            "code": response.status_code,
            "url": settings.OLLAMA_BASE_URL
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "offline",
            "code": 0,
            "url": settings.OLLAMA_BASE_URL,
            "error": "Connection refused"
        }
    except Exception as e:
        return {
            "status": "error",
            "code": 0,
            "url": settings.OLLAMA_BASE_URL,
            "error": str(e)
        }


def format_duration(nanoseconds: int) -> str:
    """
    Convert nanoseconds to human-readable format
    
    Args:
        nanoseconds: Duration in nanoseconds
        
    Returns:
        Formatted duration string
    """
    milliseconds = nanoseconds / 1_000_000
    seconds = milliseconds / 1_000
    
    if seconds < 1:
        return f"{milliseconds:.2f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = seconds / 60
        return f"{minutes:.2f}m"


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def get_model_info(model_name: str) -> Dict[str, Any]:
    """
    Get information about a specific model
    
    Args:
        model_name: Name of the model
        
    Returns:
        Model information dictionary
    """
    try:
        response = requests.get(
            f"{settings.OLLAMA_BASE_URL}/api/tags",
            timeout=5
        )
        
        if response.status_code != 200:
            return {"error": "Unable to fetch model information"}
        
        models = response.json().get("models", [])
        for model in models:
            if model.get("name") == model_name:
                return model
        
        return {"error": f"Model {model_name} not found"}
    
    except Exception as e:
        return {"error": str(e)}


def validate_prompt(prompt: str, max_length: int = 10000) -> tuple[bool, str]:
    """
    Validate a prompt
    
    Args:
        prompt: Prompt to validate
        max_length: Maximum length allowed
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not prompt:
        return False, "Prompt cannot be empty"
    
    if len(prompt) > max_length:
        return False, f"Prompt exceeds maximum length of {max_length} characters"
    
    return True, ""
