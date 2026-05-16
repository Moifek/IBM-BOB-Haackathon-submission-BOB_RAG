"""
RAG retriever for similarity search using Chroma and Ollama embeddings.
"""
import os
from typing import List, Dict
import chromadb
from chromadb.config import Settings

from llm.ollama_client import get_embeddings


def search(query: str, top_k: int = 5) -> List[Dict]:
    """
    Perform similarity search on the Chroma vector store.
    
    Args:
        query: The search query string
        top_k: Number of top results to return (default: 5)
    
    Returns:
        List of dicts with 'content', 'metadata', and 'distance' keys
    """
    # Get Chroma persist directory from environment
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
    
    # Initialize Chroma client with telemetry disabled
    client = chromadb.PersistentClient(
        path=persist_dir,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get the collection (assumes it's named "medical_docs")
    collection = client.get_collection(name="medical_docs")
    
    # Get embeddings for the query
    embeddings = get_embeddings()
    query_embedding = embeddings.embed_query(query)
    
    # Perform similarity search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    # Format results
    formatted_results = []
    if results["documents"] and len(results["documents"]) > 0:
        for i in range(len(results["documents"][0])):
            formatted_results.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 0.0
            })
    
    return formatted_results

# Made with Bob
