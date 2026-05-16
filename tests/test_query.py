"""
Tests for the query endpoint.
"""
import pytest
from unittest.mock import patch, Mock


@pytest.mark.asyncio
async def test_query_success_patient_role(test_client):
    """Test successful query with patient role."""
    # Mock the RAG pipeline
    mock_result = {
        "answer": "Hypertension is high blood pressure.",
        "sources": "[1] Hypertension Overview (StatPearls)",
        "role": "patient"
    }
    
    with patch('api.routers.query.rag_pipeline', return_value=mock_result):
        response = test_client.post(
            "/query",
            json={"question": "What is hypertension?", "role": "patient"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Hypertension is high blood pressure."
    assert data["sources"] == "[1] Hypertension Overview (StatPearls)"
    assert data["role"] == "patient"


@pytest.mark.asyncio
async def test_query_success_doctor_role(test_client):
    """Test successful query with doctor role."""
    # Mock the RAG pipeline
    mock_result = {
        "answer": "Hypertension is defined as BP ≥140/90 mmHg.",
        "sources": "[1] Hypertension Guidelines (StatPearls)",
        "role": "doctor"
    }
    
    with patch('api.routers.query.rag_pipeline', return_value=mock_result):
        response = test_client.post(
            "/query",
            json={"question": "What is hypertension?", "role": "doctor"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Hypertension is defined as BP ≥140/90 mmHg."
    assert data["sources"] == "[1] Hypertension Guidelines (StatPearls)"
    assert data["role"] == "doctor"


@pytest.mark.asyncio
async def test_query_default_role(test_client):
    """Test query with default role (patient)."""
    # Mock the RAG pipeline
    mock_result = {
        "answer": "Hypertension is high blood pressure.",
        "sources": "[1] Hypertension Overview (StatPearls)",
        "role": "patient"
    }
    
    with patch('api.routers.query.rag_pipeline', return_value=mock_result):
        response = test_client.post(
            "/query",
            json={"question": "What is hypertension?"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "patient"


@pytest.mark.asyncio
async def test_query_missing_question(test_client):
    """Test query with missing question field."""
    response = test_client.post(
        "/query",
        json={"role": "patient"}
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_query_empty_question(test_client):
    """Test query with empty question."""
    # Mock the RAG pipeline
    mock_result = {
        "answer": "Please provide a question.",
        "sources": "",
        "role": "patient"
    }
    
    with patch('api.routers.query.rag_pipeline', return_value=mock_result):
        response = test_client.post(
            "/query",
            json={"question": "", "role": "patient"}
        )
    
    # Should still process (validation allows empty string)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_query_invalid_role(test_client):
    """Test query with invalid role (should still work, pipeline handles it)."""
    # Mock the RAG pipeline - it normalizes invalid roles to "patient"
    mock_result = {
        "answer": "Hypertension is high blood pressure.",
        "sources": "[1] Hypertension Overview (StatPearls)",
        "role": "patient"
    }
    
    with patch('api.routers.query.rag_pipeline', return_value=mock_result):
        response = test_client.post(
            "/query",
            json={"question": "What is hypertension?", "role": "invalid"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "patient"  # Pipeline normalizes to patient


@pytest.mark.asyncio
async def test_query_pipeline_file_not_found(test_client):
    """Test query when prompt file is missing."""
    with patch('api.routers.query.rag_pipeline', side_effect=FileNotFoundError("Prompt file not found")):
        response = test_client.post(
            "/query",
            json={"question": "What is hypertension?", "role": "patient"}
        )
    
    assert response.status_code == 500
    data = response.json()
    assert "Configuration error" in data["detail"]


@pytest.mark.asyncio
async def test_query_pipeline_general_error(test_client):
    """Test query when RAG pipeline fails."""
    with patch('api.routers.query.rag_pipeline', side_effect=Exception("Pipeline error")):
        response = test_client.post(
            "/query",
            json={"question": "What is hypertension?", "role": "patient"}
        )
    
    assert response.status_code == 500
    data = response.json()
    assert "Error processing query" in data["detail"]


@pytest.mark.asyncio
async def test_query_with_special_characters(test_client):
    """Test query with special characters in question."""
    # Mock the RAG pipeline
    mock_result = {
        "answer": "Beta-blockers are medications.",
        "sources": "[1] Medications (StatPearls)",
        "role": "patient"
    }
    
    with patch('api.routers.query.rag_pipeline', return_value=mock_result):
        response = test_client.post(
            "/query",
            json={"question": "What are β-blockers?", "role": "patient"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "Beta-blockers" in data["answer"]

# Made with Bob