"""
Citation handling utilities for RAG pipeline.

Provides functions to deduplicate sources, format citations,
and assemble context for LLM prompts.
"""
from typing import List, Dict


def deduplicate_sources(sources: List[Dict]) -> List[Dict]:
    """
    Remove duplicate sources based on content.
    
    Args:
        sources: List of source dicts with 'content' and 'metadata' keys
    
    Returns:
        List of unique sources
    """
    seen_content = set()
    unique_sources = []
    
    for source in sources:
        content = source.get("content", "")
        if content and content not in seen_content:
            seen_content.add(content)
            unique_sources.append(source)
    
    return unique_sources


def format_citations(sources: List[Dict]) -> str:
    """
    Format sources as numbered citations.
    
    Args:
        sources: List of source dicts with 'content' and 'metadata' keys
    
    Returns:
        Formatted citation string like "[1] Title (Source)\n[2] ..."
    """
    if not sources:
        return ""
    
    citations = []
    for i, source in enumerate(sources, start=1):
        metadata = source.get("metadata", {})
        title = metadata.get("title", "Unknown Title")
        source_name = metadata.get("source", "Unknown Source")
        citations.append(f"[{i}] {title} ({source_name})")
    
    return "\n".join(citations)


def assemble_context(sources: List[Dict]) -> str:
    """
    Combine source content into a single context string for LLM.
    
    Args:
        sources: List of source dicts with 'content' key
    
    Returns:
        Combined context string with source numbers
    """
    if not sources:
        return ""
    
    context_parts = []
    for i, source in enumerate(sources, start=1):
        content = source.get("content", "")
        if content:
            context_parts.append(f"[Source {i}]\n{content}")
    
    return "\n\n".join(context_parts)

# Made with Bob
