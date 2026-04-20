"""
FastAPI Backend for Ollama Model Integration
This API serves as a wrapper around the Ollama local LLM service.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
from typing import Optional
from config import settings
from models import GenerateRequest, GenerateResponse, HealthResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Kasparo Backend API",
    description="API wrapper for Ollama LLM Model",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify backend and Ollama service status
    """
    try:
        response = requests.get(
            f"{settings.OLLAMA_BASE_URL}/api/tags",
            timeout=5
        )
        if response.status_code == 200:
            return HealthResponse(
                status="healthy",
                message="Backend and Ollama service are running",
                service_url=settings.OLLAMA_BASE_URL
            )
        else:
            return HealthResponse(
                status="unhealthy",
                message=f"Ollama service returned status {response.status_code}",
                service_url=settings.OLLAMA_BASE_URL
            )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            message=f"Error connecting to Ollama service: {str(e)}",
            service_url=settings.OLLAMA_BASE_URL
        )


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    Generate response from the Ollama LLM model.
    
    Args:
        request: GenerateRequest containing prompt, model, and optional parameters
        
    Returns:
        GenerateResponse with the model's response
        
    Raises:
        HTTPException: If Ollama service is unavailable or request fails
    """
    try:
        logger.info(f"Generating response for prompt: {request.prompt[:50]}...")
        
        payload = {
            "model": request.model or settings.DEFAULT_MODEL,
            "prompt": request.prompt,
            "stream": request.stream,
        }
        
        # Add optional parameters
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.top_k is not None:
            payload["top_k"] = request.top_k
        
        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=settings.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            logger.error(f"Ollama error: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Ollama service error: {response.text}"
            )
        
        result = response.json()
        logger.info("Response generated successfully")
        
        return GenerateResponse(
            model=result.get("model", ""),
            response=result.get("response", ""),
            created_at=result.get("created_at", ""),
            done=result.get("done", True),
            total_duration=result.get("total_duration", 0),
            load_duration=result.get("load_duration", 0),
            prompt_eval_count=result.get("prompt_eval_count", 0),
            prompt_eval_duration=result.get("prompt_eval_duration", 0),
            eval_count=result.get("eval_count", 0),
            eval_duration=result.get("eval_duration", 0)
        )
    
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Ollama service at {settings.OLLAMA_BASE_URL}. Make sure Ollama is running."
        )
    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        raise HTTPException(
            status_code=504,
            detail="Request to Ollama service timed out. Try a simpler prompt or increase timeout."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/generate-with-history")
async def generate_with_history(request: GenerateRequest, history: Optional[str] = None):
    """
    Generate response with conversation history context.
    
    Args:
        request: GenerateRequest containing prompt and model info
        history: Optional conversation history to include in context
        
    Returns:
        GenerateResponse with the model's response
    """
    try:
        # Combine history with current prompt
        full_prompt = f"{history}\n\n{request.prompt}" if history else request.prompt
        
        payload = {
            "model": request.model or settings.DEFAULT_MODEL,
            "prompt": full_prompt,
            "stream": request.stream,
        }
        
        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=settings.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Ollama service error: {response.text}"
            )
        
        result = response.json()
        return GenerateResponse(
            model=result.get("model", ""),
            response=result.get("response", ""),
            created_at=result.get("created_at", ""),
            done=result.get("done", True),
            total_duration=result.get("total_duration", 0),
            load_duration=result.get("load_duration", 0),
            prompt_eval_count=result.get("prompt_eval_count", 0),
            prompt_eval_duration=result.get("prompt_eval_duration", 0),
            eval_count=result.get("eval_count", 0),
            eval_duration=result.get("eval_duration", 0)
        )
    
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Ollama service at {settings.OLLAMA_BASE_URL}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/models")
async def list_models():
    """
    List all available models on the Ollama service
    """
    try:
        response = requests.get(
            f"{settings.OLLAMA_BASE_URL}/api/tags",
            timeout=5
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to fetch models from Ollama"
            )
        
        return response.json()
    
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Ollama service at {settings.OLLAMA_BASE_URL}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching models: {str(e)}"
        )


@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": "Kasparo Backend API",
        "version": "1.0.0",
        "description": "FastAPI wrapper for Ollama LLM Model",
        "endpoints": {
            "health": "/health",
            "generate": "/api/generate",
            "models": "/api/models",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
