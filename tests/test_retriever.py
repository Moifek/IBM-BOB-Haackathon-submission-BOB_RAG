"""
Tests for the RAG retriever.
"""
import pytest
from unittest.mock import patch, Mock


def test_search_success(mock_chroma_client, mock_ollama_embeddings):
    """Test successful search with default top_k."""
    with patch('rag.retriever.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('rag.retriever.get_embeddings', return_value=mock_ollama_embeddings):
        
        from rag.retriever import search
        
        results = search("What is hypertension?")
    
    assert len(results) == 2
    assert results[0]["content"] == "Hypertension is elevated blood pressure."
    assert results[0]["metadata"]["title"] == "Hypertension Overview"
    assert "distance" in results[0]


def test_search_custom_top_k(mock_chroma_client, mock_ollama_embeddings):
    """Test search with custom top_k value."""
    # Modify mock to return 3 results
    mock_collection = mock_chroma_client.get_collection.return_value
    mock_collection.query.return_value = {
        "documents": [["Doc1", "Doc2", "Doc3"]],
        "metadatas": [[
            {"title": "Title1", "source": "Source1"},
            {"title": "Title2", "source": "Source2"},
            {"title": "Title3", "source": "Source3"}
        ]],
        "distances": [[0.1, 0.2, 0.3]]
    }
    
    with patch('rag.retriever.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('rag.retriever.get_embeddings', return_value=mock_ollama_embeddings):
        
        from rag.retriever import search
        
        results = search("What is hypertension?", top_k=3)
    
    assert len(results) == 3
    # Verify query was called with correct n_results
    mock_collection.query.assert_called_once()
    call_kwargs = mock_collection.query.call_args[1]
    assert call_kwargs["n_results"] == 3


def test_search_empty_results(mock_chroma_client, mock_ollama_embeddings):
    """Test search when no results are found."""
    # Mock empty results
    mock_collection = mock_chroma_client.get_collection.return_value
    mock_collection.query.return_value = {
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]]
    }
    
    with patch('rag.retriever.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('rag.retriever.get_embeddings', return_value=mock_ollama_embeddings):
        
        from rag.retriever import search
        
        results = search("Very obscure query")
    
    assert len(results) == 0


def test_search_chroma_initialization(mock_chroma_client, mock_ollama_embeddings):
    """Test that Chroma client is initialized correctly."""
    with patch('rag.retriever.chromadb.PersistentClient', return_value=mock_chroma_client) as mock_client_class, \
         patch('rag.retriever.get_embeddings', return_value=mock_ollama_embeddings):
        
        from rag.retriever import search
        
        search("What is hypertension?")
    
    # Verify PersistentClient was called with correct settings
    mock_client_class.assert_called_once()
    call_kwargs = mock_client_class.call_args[1]
    assert "path" in call_kwargs
    assert "settings" in call_kwargs


def test_search_uses_embeddings(mock_chroma_client, mock_ollama_embeddings):
    """Test that search uses embeddings for query."""
    with patch('rag.retriever.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('rag.retriever.get_embeddings', return_value=mock_ollama_embeddings):
        
        from rag.retriever import search
        
        search("What is hypertension?")
    
    # Verify embeddings were generated
    mock_ollama_embeddings.embed_query.assert_called_once_with("What is hypertension?")


def test_search_collection_name(mock_chroma_client, mock_ollama_embeddings):
    """Test that search uses correct collection name."""
    with patch('rag.retriever.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('rag.retriever.get_embeddings', return_value=mock_ollama_embeddings):
        
        from rag.retriever import search
        
        search("What is hypertension?")
    
    # Verify correct collection was accessed
    mock_chroma_client.get_collection.assert_called_once_with(name="medical_docs")


def test_search_formats_results_correctly(mock_chroma_client, mock_ollama_embeddings):
    """Test that search formats results with all required fields."""
    with patch('rag.retriever.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('rag.retriever.get_embeddings', return_value=mock_ollama_embeddings):
        
        from rag.retriever import search
        
        results = search("What is hypertension?")
    
    # Verify result structure
    for result in results:
        assert "content" in result
        assert "metadata" in result
        assert "distance" in result
        assert isinstance(result["metadata"], dict)


def test_search_with_missing_metadata(mock_chroma_client, mock_ollama_embeddings):
    """Test search when metadata is missing."""
    # Mock results without metadata
    mock_collection = mock_chroma_client.get_collection.return_value
    mock_collection.query.return_value = {
        "documents": [["Document content"]],
        "metadatas": None,  # Missing metadata
        "distances": [[0.15]]
    }
    
    with patch('rag.retriever.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('rag.retriever.get_embeddings', return_value=mock_ollama_embeddings):
        
        from rag.retriever import search
        
        results = search("What is hypertension?")
    
    assert len(results) == 1
    assert results[0]["metadata"] == {}  # Should default to empty dict


def test_search_with_missing_distances(mock_chroma_client, mock_ollama_embeddings):
    """Test search when distances are missing."""
    # Mock results without distances
    mock_collection = mock_chroma_client.get_collection.return_value
    mock_collection.query.return_value = {
        "documents": [["Document content"]],
        "metadatas": [[{"title": "Title", "source": "Source"}]],
        "distances": None  # Missing distances
    }
    
    with patch('rag.retriever.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('rag.retriever.get_embeddings', return_value=mock_ollama_embeddings):
        
        from rag.retriever import search
        
        results = search("What is hypertension?")
    
    assert len(results) == 1
    assert results[0]["distance"] == 0.0  # Should default to 0.0


def test_search_custom_persist_dir(mock_chroma_client, mock_ollama_embeddings):
    """Test search with custom persist directory from environment."""
    with patch('rag.retriever.chromadb.PersistentClient', return_value=mock_chroma_client) as mock_client_class, \
         patch('rag.retriever.get_embeddings', return_value=mock_ollama_embeddings), \
         patch('os.getenv', return_value="/custom/path"):
        
        from rag.retriever import search
        
        search("What is hypertension?")
    
    # Verify custom path was used
    call_kwargs = mock_client_class.call_args[1]
    assert call_kwargs["path"] == "/custom/path"

# Made with Bob