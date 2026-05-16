# Multi-stage build for Python API

# Stage 1: Builder - Install dependencies with uv
FROM python:3.11-slim AS builder

# Install uv package manager
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv pip install --system --no-cache -e .

# Stage 2: Runtime - Minimal production image
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY api/ ./api/
COPY rag/ ./rag/
COPY llm/ ./llm/
COPY ingestion/ ./ingestion/

# Create data directory for Chroma persistence
RUN mkdir -p /app/data/chroma

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5.0)" || exit 1

# Run the FastAPI application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Made with Bob