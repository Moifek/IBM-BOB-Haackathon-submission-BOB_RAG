"""
LLM client for Ollama integration.

Provides functions to get LLM and embedding instances configured
from environment variables.
"""
import os
from langchain_ollama import ChatOllama, OllamaEmbeddings


def get_llm() -> ChatOllama:
    """
    Returns a ChatOllama instance for text generation.
    
    Uses environment variables:
    - OLLAMA_BASE_URL: Base URL for Ollama API (default: http://localhost:11434)
    - OLLAMA_LLM_MODEL: Model name for text generation (default: llama3.2:3b-instruct)
    
    Returns:
        ChatOllama: Configured LLM instance
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_LLM_MODEL", "llama3.2:3b-instruct")
    
    return ChatOllama(
        base_url=base_url,
        model=model,
        temperature=0.0,
    )


def get_embeddings() -> OllamaEmbeddings:
    """
    Returns an OllamaEmbeddings instance for vector embeddings.
    
    Uses environment variables:
    - OLLAMA_BASE_URL: Base URL for Ollama API (default: http://localhost:11434)
    - OLLAMA_EMBED_MODEL: Model name for embeddings (default: nomic-embed-text)
    
    Returns:
        OllamaEmbeddings: Configured embeddings instance
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    
    return OllamaEmbeddings(
        base_url=base_url,
        model=model,
    )

# Made with Bob
