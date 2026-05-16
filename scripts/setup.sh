#!/usr/bin/env bash
# scripts/setup.sh — BobRAG-MD bootstrap (minimal stack)
set -euo pipefail

echo "🧬 BobRAG-MD setup"
echo "=================="

# Prereqs
command -v uv >/dev/null 2>&1 || {
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
}
command -v docker >/dev/null 2>&1 || {
  echo "❌ Docker required."
  exit 1
}

# Python deps
echo "📦 uv sync..."
uv sync

# Pull images ahead of demo time
docker pull qdrant/qdrant:latest >/dev/null
docker pull langfuse/langfuse:latest >/dev/null 2>&1 || true

# Bootstrap .env if missing
[ -f .env ] || { cp .env.example .env; echo "📝 .env created — fill in keys"; }

# Bring up infra
docker compose up -d

# Wait for Qdrant
for i in {1..30}; do
  curl -sf http://localhost:6333/healthz >/dev/null 2>&1 && { echo "✅ Qdrant ready"; break; }
  sleep 1
done

echo ""
echo "✅ Setup complete."
echo "  → bobrag ingest"
echo "  → bobrag query \"What is metformin used for?\""
