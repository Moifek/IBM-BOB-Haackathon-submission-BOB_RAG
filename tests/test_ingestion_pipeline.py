"""
Tests for the ingestion pipeline.
"""
import pytest
from unittest.mock import patch, Mock, mock_open
from pathlib import Path


def test_ingestion_success(sample_chunks, mock_chroma_client, mock_ollama_embeddings):
    """Test successful ingestion of documents."""
    with patch('ingestion.pipeline.load_chunks', return_value=sample_chunks), \
         patch('ingestion.pipeline.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('ingestion.pipeline.get_embeddings', return_value=mock_ollama_embeddings), \
         patch('pathlib.Path.mkdir'):
        
        from ingestion.pipeline import run
        
        count = run()
    
    assert count == 3  # sample_chunks has 3 items
    mock_chroma_client.create_collection.assert_called_once()


def test_ingestion_with_limit(sample_chunks, mock_chroma_client, mock_ollama_embeddings):
    """Test ingestion with limit parameter."""
    # Only return first 2 chunks when limit is applied
    limited_chunks = sample_chunks[:2]
    
    with patch('ingestion.pipeline.load_chunks', return_value=limited_chunks), \
         patch('ingestion.pipeline.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('ingestion.pipeline.get_embeddings', return_value=mock_ollama_embeddings), \
         patch('pathlib.Path.mkdir'):
        
        from ingestion.pipeline import run
        
        count = run(limit=2)
    
    assert count == 2


def test_ingestion_missing_data_file(mock_chroma_client, mock_ollama_embeddings):
    """Test ingestion when data file is missing."""
    with patch('ingestion.pipeline.load_chunks', side_effect=FileNotFoundError("File not found")), \
         patch('ingestion.pipeline.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('ingestion.pipeline.get_embeddings', return_value=mock_ollama_embeddings), \
         patch('pathlib.Path.mkdir'):
        
        from ingestion.pipeline import run
        
        count = run()
    
    assert count == 0  # Should return 0 when file not found


def test_ingestion_empty_chunks(mock_chroma_client, mock_ollama_embeddings):
    """Test ingestion with empty chunks list."""
    with patch('ingestion.pipeline.load_chunks', return_value=[]), \
         patch('ingestion.pipeline.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('ingestion.pipeline.get_embeddings', return_value=mock_ollama_embeddings), \
         patch('pathlib.Path.mkdir'):
        
        from ingestion.pipeline import run
        
        count = run()
    
    assert count == 0


def test_ingestion_creates_persist_directory(sample_chunks, mock_chroma_client, mock_ollama_embeddings):
    """Test that ingestion creates persist directory."""
    with patch('ingestion.pipeline.load_chunks', return_value=sample_chunks), \
         patch('ingestion.pipeline.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('ingestion.pipeline.get_embeddings', return_value=mock_ollama_embeddings), \
         patch('pathlib.Path.mkdir') as mock_mkdir:
        
        from ingestion.pipeline import run
        
        run()
    
    # Verify directory creation was attempted
    mock_mkdir.assert_called_once()


def test_ingestion_deletes_existing_collection(sample_chunks, mock_chroma_client, mock_ollama_embeddings):
    """Test that ingestion deletes existing collection before creating new one."""
    with patch('ingestion.pipeline.load_chunks', return_value=sample_chunks), \
         patch('ingestion.pipeline.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('ingestion.pipeline.get_embeddings', return_value=mock_ollama_embeddings), \
         patch('pathlib.Path.mkdir'):
        
        from ingestion.pipeline import run
        
        run()
    
    # Verify collection deletion was attempted
    mock_chroma_client.delete_collection.assert_called_once_with(name="medical_docs")


def test_ingestion_creates_collection(sample_chunks, mock_chroma_client, mock_ollama_embeddings):
    """Test that ingestion creates collection with correct name."""
    with patch('ingestion.pipeline.load_chunks', return_value=sample_chunks), \
         patch('ingestion.pipeline.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('ingestion.pipeline.get_embeddings', return_value=mock_ollama_embeddings), \
         patch('pathlib.Path.mkdir'):
        
        from ingestion.pipeline import run
        
        run()
    
    mock_chroma_client.create_collection.assert_called_once_with(name="medical_docs")


def test_ingestion_generates_embeddings(sample_chunks, mock_chroma_client, mock_ollama_embeddings):
    """Test that ingestion generates embeddings for documents."""
    with patch('ingestion.pipeline.load_chunks', return_value=sample_chunks), \
         patch('ingestion.pipeline.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('ingestion.pipeline.get_embeddings', return_value=mock_ollama_embeddings), \
         patch('pathlib.Path.mkdir'):
        
        from ingestion.pipeline import run
        
        run()
    
    # Verify embeddings were generated
    mock_ollama_embeddings.embed_documents.assert_called()


def test_ingestion_adds_to_collection(sample_chunks, mock_chroma_client, mock_ollama_embeddings):
    """Test that ingestion adds documents to collection."""
    mock_collection = mock_chroma_client.create_collection.return_value
    
    with patch('ingestion.pipeline.load_chunks', return_value=sample_chunks), \
         patch('ingestion.pipeline.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('ingestion.pipeline.get_embeddings', return_value=mock_ollama_embeddings), \
         patch('pathlib.Path.mkdir'):
        
        from ingestion.pipeline import run
        
        run()
    
    # Verify documents were added to collection
    mock_collection.add.assert_called()


def test_ingestion_batch_processing(mock_chroma_client, mock_ollama_embeddings):
    """Test that ingestion processes documents in batches."""
    # Create 150 chunks to test batch processing (batch_size=100)
    large_chunks = [
        {
            "content": f"Content {i}",
            "metadata": {"title": f"Title {i}", "source": "StatPearls", "chunk_id": i}
        }
        for i in range(150)
    ]
    
    mock_collection = mock_chroma_client.create_collection.return_value
    
    with patch('ingestion.pipeline.load_chunks', return_value=large_chunks), \
         patch('ingestion.pipeline.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('ingestion.pipeline.get_embeddings', return_value=mock_ollama_embeddings), \
         patch('pathlib.Path.mkdir'):
        
        from ingestion.pipeline import run
        
        count = run()
    
    assert count == 150
    # Should be called twice (100 + 50)
    assert mock_collection.add.call_count == 2


def test_ingestion_custom_persist_dir(sample_chunks, mock_chroma_client, mock_ollama_embeddings):
    """Test ingestion with custom persist directory from environment."""
    with patch('ingestion.pipeline.load_chunks', return_value=sample_chunks), \
         patch('ingestion.pipeline.chromadb.PersistentClient', return_value=mock_chroma_client) as mock_client_class, \
         patch('ingestion.pipeline.get_embeddings', return_value=mock_ollama_embeddings), \
         patch('pathlib.Path.mkdir'), \
         patch('os.getenv', return_value="/custom/chroma/path"):
        
        from ingestion.pipeline import run
        
        run()
    
    # Verify custom path was used
    call_kwargs = mock_client_class.call_args[1]
    assert call_kwargs["path"] == "/custom/chroma/path"


def test_ingestion_preserves_metadata(sample_chunks, mock_chroma_client, mock_ollama_embeddings):
    """Test that ingestion preserves document metadata."""
    mock_collection = mock_chroma_client.create_collection.return_value
    
    with patch('ingestion.pipeline.load_chunks', return_value=sample_chunks), \
         patch('ingestion.pipeline.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('ingestion.pipeline.get_embeddings', return_value=mock_ollama_embeddings), \
         patch('pathlib.Path.mkdir'):
        
        from ingestion.pipeline import run
        
        run()
    
    # Get the call arguments
    call_kwargs = mock_collection.add.call_args[1]
    
    # Verify metadata was passed
    assert "metadatas" in call_kwargs
    assert len(call_kwargs["metadatas"]) == 3
    assert call_kwargs["metadatas"][0]["title"] == "Hypertension Overview"


def test_ingestion_generates_document_ids(sample_chunks, mock_chroma_client, mock_ollama_embeddings):
    """Test that ingestion generates proper document IDs."""
    mock_collection = mock_chroma_client.create_collection.return_value
    
    with patch('ingestion.pipeline.load_chunks', return_value=sample_chunks), \
         patch('ingestion.pipeline.chromadb.PersistentClient', return_value=mock_chroma_client), \
         patch('ingestion.pipeline.get_embeddings', return_value=mock_ollama_embeddings), \
         patch('pathlib.Path.mkdir'):
        
        from ingestion.pipeline import run
        
        run()
    
    # Get the call arguments
    call_kwargs = mock_collection.add.call_args[1]
    
    # Verify IDs were generated
    assert "ids" in call_kwargs
    assert len(call_kwargs["ids"]) == 3
    assert call_kwargs["ids"][0] == "doc_0"
    assert call_kwargs["ids"][1] == "doc_1"
    assert call_kwargs["ids"][2] == "doc_2"

# Made with Bob