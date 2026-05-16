"""
Health check router.

Provides endpoint to check API and Ollama connectivity.
"""
import os
import httpx
from fastapi import APIRouter

from api.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Checks if the API is running and if Ollama is accessible.
    
    Returns:
        HealthResponse with status and Ollama connectivity
    """
    ollama_connected = False
    
    # Check Ollama connectivity
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{ollama_base_url}/api/tags")
            ollama_connected = response.status_code == 200
    except Exception:
        ollama_connected = False
    
    return HealthResponse(
        status="healthy",
        ollama_connected=ollama_connected
    )

# Made with Bob
