"""
Pydantic models for API request/response schemas.
"""
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request schema for query endpoint."""
    question: str = Field(..., description="The medical question to answer")
    role: str = Field(default="patient", description="User role: 'doctor' or 'patient'")


class QueryResponse(BaseModel):
    """Response schema for query endpoint."""
    answer: str = Field(..., description="The generated answer")
    sources: str = Field(..., description="Formatted citations")
    role: str = Field(..., description="The role used for the query")


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    status: str = Field(..., description="Service status")
    ollama_connected: bool = Field(..., description="Whether Ollama is accessible")

# Made with Bob
