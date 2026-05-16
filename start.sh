#!/bin/bash

# DocRAG-MD MVP Startup Script
# This script checks prerequisites and starts the Docker Compose stack

set -e

echo "=========================================="
echo "DocRAG-MD MVP Startup"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed."
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! docker-compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not available."
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker is installed"
echo ""

# Check if data file exists
if [ ! -f "data/statpearls_chunks.jsonl" ]; then
    echo "⚠️  Warning: StatPearls data file not found!"
    echo ""
    echo "The application requires medical knowledge data to function."
    echo "Please run the following command to download the data:"
    echo ""
    echo "    bash download_data.sh 5000"
    echo ""
    echo "This will download and process ~5000 StatPearls articles."
    echo ""
    read -p "Do you want to continue without the data? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Please download the data first."
        exit 1
    fi
    echo ""
    echo "⚠️  Continuing without data. The API will start but queries will fail."
    echo ""
fi

echo "=========================================="
echo "Starting Docker Compose services..."
echo "=========================================="
echo ""
echo "This will:"
echo "  1. Pull and start Ollama service"
echo "  2. Download required AI models (~2.3 GB)"
echo "  3. Build and start the API service"
echo "  4. Build and start the frontend"
echo ""
echo "First run may take 10-15 minutes depending on your connection."
echo ""

# Start Docker Compose with build
docker-compose up --build

echo ""
echo "=========================================="
echo "Application stopped"
echo "=========================================="
echo ""
echo "To restart, run: bash start.sh"
echo "To stop services, run: docker-compose down"
echo "To view logs, run: docker-compose logs -f"
echo ""

# Made with Bob
