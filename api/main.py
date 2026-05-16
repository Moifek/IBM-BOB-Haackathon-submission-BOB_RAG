"""
FastAPI application entry point for DocRAG-MD MVP.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import health, query


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 DocRAG-MD API starting up...")
    yield
    # Shutdown
    print("👋 DocRAG-MD API shutting down...")


app = FastAPI(
    title="DocRAG-MD MVP",
    description="Open-source medical RAG system using Ollama and Chroma",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(query.router, tags=["query"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "DocRAG-MD MVP API",
        "version": "0.1.0",
        "status": "running",
    }

# Made with Bob
