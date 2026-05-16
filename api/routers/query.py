"""
Query router.

Provides endpoint to process medical questions using RAG pipeline.
"""
from fastapi import APIRouter, HTTPException

from api.schemas import QueryRequest, QueryResponse
from rag.pipeline import rag_pipeline

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a medical question using the RAG pipeline.
    
    Args:
        request: QueryRequest with question and role
    
    Returns:
        QueryResponse with answer, sources, and role
    
    Raises:
        HTTPException: If processing fails
    """
    try:
        # Execute RAG pipeline
        result = rag_pipeline(
            question=request.question,
            role=request.role
        )
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            role=result["role"]
        )
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

# Made with Bob
