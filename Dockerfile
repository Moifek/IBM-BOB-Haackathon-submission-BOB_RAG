FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY data/ ./data/

# Install dependencies
RUN uv pip install --system -e .

# Create data directory if it doesn't exist
RUN mkdir -p /app/data/corpus

# Expose ports (if needed for future API)
EXPOSE 8000

# Default command
CMD ["python", "-m", "bobrag", "--help"]
