"""
BobRAG-MD Minimal Pipeline
A simplified medical RAG for IBM Bob Hackathon demonstration.
"""

import os
import logging
from typing import List, Dict, Any
from pathlib import Path

import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from langfuse import Langfuse
from langfuse.decorators import observe

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


class BobRAGPipeline:
    """Minimal medical RAG pipeline with Gemini, Qdrant, and Langfuse."""
    
    def __init__(self):
        """Initialize pipeline components."""
        # Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"))
        
        # Qdrant
        self.qdrant = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
        self.collection = os.getenv("QDRANT_COLLECTION", "bobrag_medical")
        
        # Embeddings
        self.embedder = SentenceTransformer(
            os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        )
        self.embedding_dim = self.embedder.get_sentence_embedding_dimension()
        
        # Langfuse
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "http://localhost:3000")
        )
        
        # Config
        self.top_k = int(os.getenv("RETRIEVAL_TOP_K", "5"))
        
        logger.info("BobRAG pipeline initialized")
    
    def _ensure_collection(self):
        """Create Qdrant collection if it doesn't exist."""
        collections = self.qdrant.get_collections().collections
        if not any(c.name == self.collection for c in collections):
            self.qdrant.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.collection}")
    
    @observe(name="embed_query")
    def _embed(self, text: str) -> List[float]:
        """Embed text using sentence-transformers."""
        return self.embedder.encode(text).tolist()
    
    @observe(name="retrieve_context")
    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant documents from Qdrant."""
        query_vector = self._embed(query)
        
        results = self.qdrant.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=self.top_k
        )
        
        contexts = []
        for hit in results:
            contexts.append({
                "text": hit.payload.get("text", ""),
                "source": hit.payload.get("source", "unknown"),
                "score": hit.score
            })
        
        logger.info(f"Retrieved {len(contexts)} contexts")
        return contexts
    
    @observe(name="generate_answer")
    def generate(self, query: str, contexts: List[Dict[str, Any]]) -> str:
        """Generate answer using Gemini with retrieved context."""
        # Build context string
        context_str = "\n\n".join([
            f"[Source: {ctx['source']}]\n{ctx['text']}"
            for ctx in contexts
        ])
        
        # Prompt
        prompt = f"""You are a medical information assistant. Answer the question based ONLY on the provided context.
If the context doesn't contain enough information, say so clearly.
Always cite sources using [Source: ...] format.

Context:
{context_str}

Question: {query}

Answer:"""
        
        response = self.model.generate_content(prompt)
        answer = response.text
        
        logger.info("Generated answer")
        return answer
    
    @observe(name="query_pipeline")
    def query(self, question: str) -> Dict[str, Any]:
        """Full RAG pipeline: retrieve + generate."""
        logger.info(f"Query: {question}")
        
        # Retrieve
        contexts = self.retrieve(question)
        
        # Generate
        answer = self.generate(question, contexts)
        
        return {
            "question": question,
            "answer": answer,
            "contexts": contexts
        }
    
    def ingest(self, corpus_dir: str = "data/corpus"):
        """Ingest documents from corpus directory."""
        self._ensure_collection()
        
        corpus_path = Path(corpus_dir)
        if not corpus_path.exists():
            logger.warning(f"Corpus directory not found: {corpus_dir}")
            return
        
        points = []
        point_id = 0
        
        for file_path in corpus_path.glob("*.txt"):
            logger.info(f"Ingesting: {file_path.name}")
            
            text = file_path.read_text(encoding="utf-8")
            
            # Simple chunking
            chunk_size = int(os.getenv("CHUNK_SIZE", "384"))
            chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))
            
            for i in range(0, len(text), chunk_size - chunk_overlap):
                chunk = text[i:i + chunk_size]
                if len(chunk.strip()) < 50:  # Skip tiny chunks
                    continue
                
                vector = self._embed(chunk)
                
                points.append(PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "text": chunk,
                        "source": file_path.name
                    }
                ))
                point_id += 1
        
        if points:
            self.qdrant.upsert(
                collection_name=self.collection,
                points=points
            )
            logger.info(f"Ingested {len(points)} chunks from {corpus_path}")
        else:
            logger.warning("No documents found to ingest")
