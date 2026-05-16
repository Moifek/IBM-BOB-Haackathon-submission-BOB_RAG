"""
Tests for the health check endpoint.
"""
import pytest
from unittest.mock import patch, AsyncMock
import httpx


@pytest.mark.asyncio
async def test_health_check_success(test_client):
    """Test successful health check when Ollama is accessible."""
    # Mock httpx.AsyncClient to simulate successful Ollama connection
    mock_response = AsyncMock()
    mock_response.status_code = 200
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        response = test_client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["ollama_connected"] is True


@pytest.mark.asyncio
async def test_health_check_ollama_down(test_client):
    """Test health check when Ollama is not accessible."""
    # Mock httpx.AsyncClient to simulate failed Ollama connection
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.side_effect = httpx.ConnectError("Connection refused")
        mock_client_class.return_value = mock_client
        
        response = test_client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["ollama_connected"] is False


@pytest.mark.asyncio
async def test_health_check_ollama_timeout(test_client):
    """Test health check when Ollama request times out."""
    # Mock httpx.AsyncClient to simulate timeout
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.side_effect = httpx.TimeoutException("Request timeout")
        mock_client_class.return_value = mock_client
        
        response = test_client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["ollama_connected"] is False


@pytest.mark.asyncio
async def test_health_check_ollama_error_status(test_client):
    """Test health check when Ollama returns error status."""
    # Mock httpx.AsyncClient to simulate error response
    mock_response = AsyncMock()
    mock_response.status_code = 500
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        response = test_client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["ollama_connected"] is False

# Made with Bob