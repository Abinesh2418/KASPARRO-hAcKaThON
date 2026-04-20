"""
Pydantic models for request and response validation
"""

from pydantic import BaseModel, Field
from typing import Optional


class GenerateRequest(BaseModel):
    """Request model for text generation endpoint"""
    
    prompt: str = Field(
        ...,
        description="The prompt to send to the model",
        example="What is the capital of France?"
    )
    model: Optional[str] = Field(
        None,
        description="Model name (uses default if not specified)",
        example="deepseek-r1:32b"
    )
    stream: bool = Field(
        False,
        description="Whether to stream the response"
    )
    temperature: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Controls randomness of the model (0-1)"
    )
    top_p: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter"
    )
    top_k: Optional[int] = Field(
        None,
        ge=1,
        description="Top-k sampling parameter"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Explain quantum computing in simple terms",
                "model": "deepseek-r1:32b",
                "stream": False,
                "temperature": 0.7
            }
        }


class GenerateResponse(BaseModel):
    """Response model for text generation endpoint"""
    
    model: str = Field(description="Name of the model used")
    response: str = Field(description="The generated text response")
    created_at: str = Field(description="Timestamp when response was created")
    done: bool = Field(description="Whether generation is complete")
    total_duration: int = Field(description="Total time taken in nanoseconds")
    load_duration: int = Field(description="Time to load the model in nanoseconds")
    prompt_eval_count: int = Field(description="Number of tokens in the prompt")
    prompt_eval_duration: int = Field(description="Time to evaluate the prompt in nanoseconds")
    eval_count: int = Field(description="Number of tokens in the response")
    eval_duration: int = Field(description="Time to generate the response in nanoseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "deepseek-r1:32b",
                "response": "Quantum computing uses quantum mechanics principles...",
                "created_at": "2026-04-21T10:30:00Z",
                "done": True,
                "total_duration": 2500000000,
                "load_duration": 500000000,
                "prompt_eval_count": 10,
                "prompt_eval_duration": 800000000,
                "eval_count": 50,
                "eval_duration": 1200000000
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    
    status: str = Field(
        description="Health status (healthy/unhealthy)",
        example="healthy"
    )
    message: str = Field(
        description="Detailed status message",
        example="Backend and Ollama service are running"
    )
    service_url: str = Field(
        description="URL of the Ollama service",
        example="http://100.127.36.42:11434"
    )


class ErrorResponse(BaseModel):
    """Response model for error responses"""
    
    detail: str = Field(description="Error details")
    status_code: int = Field(description="HTTP status code")
