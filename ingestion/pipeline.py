"""
Ingestion pipeline for populating Chroma vector store with medical content.

Usage:
    python -m ingestion.pipeline [limit]
    
Example:
    python -m ingestion.pipeline 50  # Ingest first 50 documents
"""
import os
import sys
from pathlib import Path
from typing import Optional
import chromadb
from chromadb.config import Settings

from llm.ollama_client import get_embeddings
from ingestion.loader import load_chunks


def run(limit: Optional[int] = None) -> int:
    """
    Run the ingestion pipeline.
    
    Loads chunks from data/statpearls_chunks.jsonl, generates embeddings,
    and stores them in the Chroma vector store.
    
    Args:
        limit: Optional limit on number of documents to ingest (for testing)
    
    Returns:
        Number of documents successfully ingested
    """
    print("Starting ingestion pipeline...")
    
    # Load chunks
    data_path = "data/statpearls_chunks.jsonl"
    print(f"Loading chunks from {data_path}...")
    
    try:
        chunks = load_chunks(data_path, limit=limit)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run 'bash download_data.sh' first to download the data.")
        return 0
    
    if not chunks:
        print("No chunks loaded. Exiting.")
        return 0
    
    print(f"Loaded {len(chunks)} chunks")
    
    # Get Chroma persist directory from environment
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
    
    # Create persist directory if it doesn't exist
    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    
    # Initialize Chroma client with telemetry disabled
    print(f"Initializing Chroma client (persist_dir: {persist_dir})...")
    client = chromadb.PersistentClient(
        path=persist_dir,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    collection_name = "medical_docs"
    print(f"Getting or creating collection '{collection_name}'...")
    
    # Delete existing collection if it exists (for clean re-ingestion)
    try:
        client.delete_collection(name=collection_name)
        print(f"Deleted existing collection '{collection_name}'")
    except Exception:
        pass  # Collection doesn't exist, that's fine
    
    collection = client.create_collection(name=collection_name)
    
    # Get embeddings model
    print("Initializing embeddings model...")
    embeddings_model = get_embeddings()
    
    # Prepare documents for ingestion
    documents = []
    metadatas = []
    ids = []
    
    for i, chunk in enumerate(chunks):
        documents.append(chunk["content"])
        metadatas.append(chunk["metadata"])
        ids.append(f"doc_{i}")
    
    # Generate embeddings and add to collection
    print(f"Generating embeddings for {len(documents)} documents...")
    print("This may take a few minutes depending on the number of documents...")
    
    # Process in batches for progress reporting
    batch_size = 100
    total_ingested = 0
    
    for i in range(0, len(documents), batch_size):
        batch_end = min(i + batch_size, len(documents))
        batch_docs = documents[i:batch_end]
        batch_metas = metadatas[i:batch_end]
        batch_ids = ids[i:batch_end]
        
        # Generate embeddings for batch
        batch_embeddings = embeddings_model.embed_documents(batch_docs)
        
        # Add to collection
        collection.add(
            documents=batch_docs,
            metadatas=batch_metas,
            ids=batch_ids,
            embeddings=batch_embeddings
        )
        
        total_ingested += len(batch_docs)
        print(f"Ingested {total_ingested}/{len(documents)} documents...")
    
    print(f"✓ Successfully ingested {total_ingested} documents into Chroma")
    return total_ingested


if __name__ == "__main__":
    # Parse command-line arguments
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
            print(f"Limiting ingestion to {limit} documents")
        except ValueError:
            print(f"Error: Invalid limit '{sys.argv[1]}'. Must be an integer.")
            sys.exit(1)
    
    # Run the pipeline
    count = run(limit=limit)
    
    if count > 0:
        print(f"\nIngestion complete! {count} documents are now searchable.")
    else:
        print("\nIngestion failed or no documents were processed.")
        sys.exit(1)

# Made with Bob