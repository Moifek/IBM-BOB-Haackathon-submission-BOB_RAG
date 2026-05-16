"""
Tests for the RAG pipeline.
"""
import pytest
from unittest.mock import patch, Mock, mock_open
from pathlib import Path


def test_pipeline_success_patient_role(sample_sources):
    """Test successful pipeline execution with patient role."""
    # Mock dependencies
    mock_prompt_content = "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    
    # Create a proper mock LLM that returns an AIMessage-like object
    mock_ai_message = Mock()
    mock_ai_message.content = "This is a mock answer about hypertension."
    
    mock_llm = Mock()
    mock_llm.invoke.return_value = mock_ai_message
    
    with patch('rag.pipeline.search', return_value=sample_sources), \
         patch('rag.pipeline.get_llm', return_value=mock_llm), \
         patch('builtins.open', mock_open(read_data=mock_prompt_content)), \
         patch('pathlib.Path.exists', return_value=True):
        
        from rag.pipeline import rag_pipeline
        
        result = rag_pipeline(
            question="What is hypertension?",
            role="patient"
        )
    
    assert "answer" in result
    assert "sources" in result
    assert "role" in result
    assert result["role"] == "patient"
    assert len(result["sources"]) > 0


def test_pipeline_success_doctor_role(sample_sources):
    """Test successful pipeline execution with doctor role."""
    # Mock dependencies
    mock_prompt_content = "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    
    # Create a proper mock LLM that returns an AIMessage-like object
    mock_ai_message = Mock()
    mock_ai_message.content = "This is a mock answer about hypertension."
    
    mock_llm = Mock()
    mock_llm.invoke.return_value = mock_ai_message
    
    with patch('rag.pipeline.search', return_value=sample_sources), \
         patch('rag.pipeline.get_llm', return_value=mock_llm), \
         patch('builtins.open', mock_open(read_data=mock_prompt_content)), \
         patch('pathlib.Path.exists', return_value=True):
        
        from rag.pipeline import rag_pipeline
        
        result = rag_pipeline(
            question="What is hypertension?",
            role="doctor"
        )
    
    assert result["role"] == "doctor"
    assert "answer" in result


def test_pipeline_invalid_role_defaults_to_patient(sample_sources):
    """Test that invalid role defaults to patient."""
    # Mock dependencies
    mock_prompt_content = "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    
    # Create a proper mock LLM that returns an AIMessage-like object
    mock_ai_message = Mock()
    mock_ai_message.content = "This is a mock answer about hypertension."
    
    mock_llm = Mock()
    mock_llm.invoke.return_value = mock_ai_message
    
    with patch('rag.pipeline.search', return_value=sample_sources), \
         patch('rag.pipeline.get_llm', return_value=mock_llm), \
         patch('builtins.open', mock_open(read_data=mock_prompt_content)), \
         patch('pathlib.Path.exists', return_value=True):
        
        from rag.pipeline import rag_pipeline
        
        result = rag_pipeline(
            question="What is hypertension?",
            role="invalid_role"
        )
    
    assert result["role"] == "patient"


def test_pipeline_missing_prompt_file():
    """Test pipeline with missing prompt file."""
    with patch('rag.pipeline.search', return_value=[]), \
         patch('pathlib.Path.exists', return_value=False):
        
        from rag.pipeline import rag_pipeline
        
        with pytest.raises(FileNotFoundError) as exc_info:
            rag_pipeline(
                question="What is hypertension?",
                role="patient"
            )
        
        assert "Prompt template not found" in str(exc_info.value)


def test_pipeline_no_sources_found(mock_chat_ollama):
    """Test pipeline when no sources are found."""
    # Mock dependencies
    mock_prompt_content = "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    
    with patch('rag.pipeline.search', return_value=[]), \
         patch('rag.pipeline.get_llm', return_value=mock_chat_ollama), \
         patch('builtins.open', mock_open(read_data=mock_prompt_content)), \
         patch('pathlib.Path.exists', return_value=True):
        
        from rag.pipeline import rag_pipeline
        
        result = rag_pipeline(
            question="What is a very obscure medical term?",
            role="patient"
        )
    
    assert "couldn't find relevant information" in result["answer"]
    assert result["sources"] == ""


def test_pipeline_deduplicates_sources():
    """Test that pipeline deduplicates sources."""
    # Create duplicate sources
    duplicate_sources = [
        {
            "content": "Hypertension is elevated blood pressure.",
            "metadata": {"title": "Hypertension", "source": "StatPearls"},
            "distance": 0.15
        },
        {
            "content": "Hypertension is elevated blood pressure.",  # Duplicate
            "metadata": {"title": "Hypertension", "source": "StatPearls"},
            "distance": 0.16
        },
        {
            "content": "Treatment includes medications.",
            "metadata": {"title": "Treatment", "source": "StatPearls"},
            "distance": 0.22
        }
    ]
    
    mock_prompt_content = "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    
    # Create a proper mock LLM that returns an AIMessage-like object
    mock_ai_message = Mock()
    mock_ai_message.content = "This is a mock answer about hypertension."
    
    mock_llm = Mock()
    mock_llm.invoke.return_value = mock_ai_message
    
    with patch('rag.pipeline.search', return_value=duplicate_sources), \
         patch('rag.pipeline.get_llm', return_value=mock_llm), \
         patch('builtins.open', mock_open(read_data=mock_prompt_content)), \
         patch('pathlib.Path.exists', return_value=True):
        
        from rag.pipeline import rag_pipeline
        
        result = rag_pipeline(
            question="What is hypertension?",
            role="patient"
        )
    
    # Should have 2 unique sources, not 3
    citation_lines = [line for line in result["sources"].split("\n") if line.strip()]
    assert len(citation_lines) == 2


def test_pipeline_formats_citations_correctly(sample_sources):
    """Test that pipeline formats citations correctly."""
    mock_prompt_content = "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    
    # Create a proper mock LLM that returns an AIMessage-like object
    mock_ai_message = Mock()
    mock_ai_message.content = "This is a mock answer about hypertension."
    
    mock_llm = Mock()
    mock_llm.invoke.return_value = mock_ai_message
    
    with patch('rag.pipeline.search', return_value=sample_sources), \
         patch('rag.pipeline.get_llm', return_value=mock_llm), \
         patch('builtins.open', mock_open(read_data=mock_prompt_content)), \
         patch('pathlib.Path.exists', return_value=True):
        
        from rag.pipeline import rag_pipeline
        
        result = rag_pipeline(
            question="What is hypertension?",
            role="patient"
        )
    
    # Check citation format
    assert "[1]" in result["sources"]
    assert "Hypertension Overview" in result["sources"]
    assert "StatPearls" in result["sources"]


def test_pipeline_assembles_context_correctly(sample_sources):
    """Test that pipeline assembles context with source numbers."""
    mock_prompt_content = "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    
    # Track what context was passed to the LLM
    invoked_context = None
    
    def mock_invoke(inputs):
        nonlocal invoked_context
        invoked_context = inputs.get("context", "")
        mock_ai_message = Mock()
        mock_ai_message.content = "Mock answer"
        return mock_ai_message
    
    mock_llm = Mock()
    mock_llm.invoke = mock_invoke
    
    with patch('rag.pipeline.search', return_value=sample_sources), \
         patch('rag.pipeline.get_llm', return_value=mock_llm), \
         patch('builtins.open', mock_open(read_data=mock_prompt_content)), \
         patch('pathlib.Path.exists', return_value=True):
        
        from rag.pipeline import rag_pipeline
        
        result = rag_pipeline(
            question="What is hypertension?",
            role="patient"
        )
    
    # Verify context includes source markers
    assert invoked_context is not None
    assert "[Source 1]" in invoked_context
    assert "[Source 2]" in invoked_context


def test_pipeline_error_handling(sample_sources):
    """Test pipeline error handling when LLM fails."""
    mock_prompt_content = "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    
    mock_llm = Mock()
    mock_llm.invoke.side_effect = Exception("LLM error")
    
    with patch('rag.pipeline.search', return_value=sample_sources), \
         patch('rag.pipeline.get_llm', return_value=mock_llm), \
         patch('builtins.open', mock_open(read_data=mock_prompt_content)), \
         patch('pathlib.Path.exists', return_value=True):
        
        from rag.pipeline import rag_pipeline
        
        with pytest.raises(Exception) as exc_info:
            rag_pipeline(
                question="What is hypertension?",
                role="patient"
            )
        
        assert "LLM error" in str(exc_info.value)

# Made with Bob