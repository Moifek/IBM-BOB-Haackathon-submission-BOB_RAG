#!/bin/bash
# Download StatPearls medical content for DocRAG-MD MVP
#
# Usage:
#   bash download_data.sh [num_articles]
#
# Example:
#   bash download_data.sh 5000

set -e  # Exit on error

# Default number of articles
NUM_ARTICLES=${1:-5000}

echo "================================================"
echo "StatPearls Data Download"
echo "================================================"
echo "Target: $NUM_ARTICLES articles"
echo ""

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo "Creating data/ directory..."
    mkdir -p data
fi

# Run the download script
echo "Running download script..."
python3 scripts/download_statpearls.py "$NUM_ARTICLES"

# Check if output file was created
if [ -f "data/statpearls_chunks.jsonl" ]; then
    echo ""
    echo "================================================"
    echo "✓ Download complete!"
    echo "================================================"
    echo "Output: data/statpearls_chunks.jsonl"
    
    # Show file size and line count
    FILE_SIZE=$(du -h data/statpearls_chunks.jsonl | cut -f1)
    LINE_COUNT=$(wc -l < data/statpearls_chunks.jsonl)
    
    echo "Size: $FILE_SIZE"
    echo "Chunks: $LINE_COUNT"
    echo ""
    echo "Next step: Run 'python -m ingestion.pipeline' to ingest into Chroma"
else
    echo ""
    echo "Error: Output file not created"
    exit 1
fi

# Made with Bob