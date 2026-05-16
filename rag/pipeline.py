"""
RAG pipeline orchestration.

Combines retrieval, citation formatting, and LLM generation
to answer medical questions with cited sources.
"""
import os
from typing import Dict
from pathlib import Path

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from llm.ollama_client import get_llm
from rag.retriever import search
from rag.citations import deduplicate_sources, format_citations, assemble_context


def rag_pipeline(question: str, role: str = "patient") -> Dict[str, str]:
    """
    Execute the RAG pipeline to answer a medical question.
    
    Args:
        question: The medical question to answer
        role: User role - "doctor" or "patient" (default: "patient")
    
    Returns:
        Dict with 'answer' and 'sources' keys
    """
    # Validate role
    if role not in ["doctor", "patient"]:
        role = "patient"
    
    # Load appropriate prompt template
    prompt_file = f"llm/prompts/{role}_qa.txt"
    prompt_path = Path(prompt_file)
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {prompt_file}")
    
    with open(prompt_path, "r") as f:
        prompt_template = f.read()
    
    # Retrieve relevant sources
    sources = search(question, top_k=5)
    
    # Deduplicate sources
    unique_sources = deduplicate_sources(sources)
    
    # Assemble context from sources
    context = assemble_context(unique_sources)
    
    # If no sources found, return a message
    if not context:
        return {
            "answer": "I couldn't find relevant information to answer your question. Please try rephrasing or asking a different question.",
            "sources": "",
            "role": role
        }
    
    # Create LangChain LCEL chain
    llm = get_llm()
    prompt = PromptTemplate.from_template(prompt_template)
    output_parser = StrOutputParser()
    
    # Build the chain using LCEL
    chain = prompt | llm | output_parser
    
    # Execute the chain
    answer = chain.invoke({
        "context": context,
        "question": question
    })
    
    # Format citations
    citations = format_citations(unique_sources)
    
    return {
        "answer": answer,
        "sources": citations,
        "role": role
    }

# Made with Bob
