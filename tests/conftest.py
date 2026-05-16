"""
Pytest configuration and shared fixtures for DocRAG-MD MVP tests.
"""
import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def sample_question():
    """Sample medical question for testing."""
    return "What is hypertension?"


@pytest.fixture
def sample_role():
    """Sample role for testing."""
    return "doctor"


@pytest.fixture
def sample_chunks():
    """Sample medical data chunks for testing."""
    return [
        {
            "content": "Hypertension is a condition where blood pressure is consistently elevated above 140/90 mmHg.",
            "metadata": {
                "title": "Hypertension Overview",
                "source": "StatPearls",
                "chunk_id": 0
            }
        },
        {
            "content": "Treatment of hypertension includes lifestyle modifications and antihypertensive medications.",
            "metadata": {
                "title": "Hypertension Treatment",
                "source": "StatPearls",
                "chunk_id": 1
            }
        },
        {
            "content": "Diabetes mellitus is characterized by elevated blood glucose levels.",
            "metadata": {
                "title": "Diabetes Overview",
                "source": "StatPearls",
                "chunk_id": 2
            }
        }
    ]


@pytest.fixture
def sample_sources():
    """Sample retrieval results for testing."""
    return [
        {
            "content": "Hypertension is a condition where blood pressure is consistently elevated.",
            "metadata": {
                "title": "Hypertension Overview",
                "source": "StatPearls"
            },
            "distance": 0.15
        },
        {
            "content": "Treatment includes lifestyle modifications and medications.",
            "metadata": {
                "title": "Hypertension Treatment",
                "source": "StatPearls"
            },
            "distance": 0.22
        }
    ]


@pytest.fixture
def mock_ollama_embeddings():
    """Mock for OllamaEmbeddings."""
    mock = Mock()
    mock.embed_query.return_value = [0.1] * 768  # Mock embedding vector
    mock.embed_documents.return_value = [[0.1] * 768, [0.2] * 768]  # Mock batch embeddings
    return mock


@pytest.fixture
def mock_chat_ollama():
    """Mock for ChatOllama."""
    mock = Mock()
    mock.invoke.return_value = Mock(content="This is a mock answer about hypertension.")
    return mock


@pytest.fixture
def mock_chroma_client():
    """Mock for Chroma client."""
    mock_collection = Mock()
    mock_collection.query.return_value = {
        "documents": [["Hypertension is elevated blood pressure.", "Treatment includes medications."]],
        "metadatas": [[
            {"title": "Hypertension Overview", "source": "StatPearls"},
            {"title": "Hypertension Treatment", "source": "StatPearls"}
        ]],
        "distances": [[0.15, 0.22]]
    }
    mock_collection.add.return_value = None
    mock_collection.count.return_value = 2
    
    mock_client = Mock()
    mock_client.get_collection.return_value = mock_collection
    mock_client.create_collection.return_value = mock_collection
    mock_client.delete_collection.return_value = None
    
    return mock_client


@pytest.fixture
def test_client():
    """FastAPI TestClient for API testing."""
    from api.main import app
    return TestClient(app)

# Made with Bob
