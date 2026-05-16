# DocRAG-MD Developer Onboarding Guide

Welcome to the DocRAG-MD team! This guide will get you productive on the codebase in your first day.

---

## Project Overview

**What it does:** DocRAG-MD is a production-grade multi-agent medical RAG platform for clinical question answering. It processes 301,000 StatPearls medical textbook chunks and integrates with 36M+ PubMed articles to answer medical questions with cited sources.

**Why it exists:** Medical professionals need accurate, evidence-based answers with verifiable citations. Generic RAG systems struggle with medical terminology and lack domain-specific optimizations. DocRAG-MD solves this with:
- **Multi-agent routing** - specialized agents for diagnosis, pharmacology, general medical questions
- **GraphRAG** - PrimeKG knowledge graph with 100k+ medical entities and 4M+ relationships
- **Self-RAG** - automatic fidelity checking with retry logic (max 2 attempts)
- **CRAG gating** - confidence thresholding to refuse low-quality answers

**Key metrics:** 62%+ accuracy on MedMCQA benchmarks (vs ~52% baseline), sub-3s response time, full observability via Langfuse.

---

## Prerequisites

### Required Tools
- **Python 3.11+** - Runtime environment
- **Docker Desktop** - For running 11 services (Qdrant, Postgres, Langfuse, etc.)
- **Node.js 20+** - Frontend development
- **uv** - Fast Python package manager ([install](https://github.com/astral-sh/uv))
- **Git** - Version control

### Required Accounts
- **Google Cloud / Gemini API** - For Gemini 2.5 Flash/Pro models (get key at [aistudio.google.com](https://aistudio.google.com))
- **OpenAI** (optional) - For GPT-4o model
- **Langfuse** (optional) - Observability (self-hosted via Docker or cloud)

### Required Knowledge
- **Python async/await** - All agents use async functions
- **LangChain LCEL** - Expression language for LLM chains
- **LangGraph** - State machines for multi-step agents
- **FastAPI** - REST + WebSocket API framework
- **React** - Frontend UI (basic familiarity sufficient)
- **Docker Compose** - Service orchestration

**Nice to have:** RAG concepts (embeddings, vector search, reranking), medical terminology basics, Qdrant vector DB.

---

## Setup Steps

### 1. Clone and Configure

```bash
git clone https://github.com/Ahmedfekhfakh/DocRAG-MD-.git
cd DocRAG-MD-

# Copy environment template
cp .env.example .env

# Edit .env - REQUIRED: Set your Gemini API key
nano .env  # or use your preferred editor
# Set: GOOGLE_API_KEY=AIza...
```

### 2. Download Data (~6 GB)

```bash
# Downloads StatPearls chunks + BioMistral 7B GGUF model
bash download_data.sh
```

**What this does:**
- Fetches 301k StatPearls medical textbook chunks (JSONL format)
- Downloads BioMistral 7B quantized model (Q4_K_M, ~4GB) for local inference
- Stores in `data/` directory

### 3. Launch Services

```bash
# Start all 11 Docker services
docker compose up --build

# Wait ~2 minutes for services to initialize
# Watch logs for "Application startup complete"
```

**Services started:**
- `qdrant` (vector DB) - :6333
- `llama-cpp` (BioMistral) - :8080
- `api` (FastAPI + MCP) - :8000, :9001, :9002
- `frontend` (React) - :3000
- `postgres`, `clickhouse`, `minio`, `redis` (Langfuse stack)
- `langfuse` (observability UI) - :3001
- `langfuse-worker` (background jobs)

### 4. Verify Installation

Open these URLs in your browser:
- **Frontend:** http://localhost:3000 - Chat UI should load
- **API Docs:** http://localhost:8000/docs - Swagger UI with 6 endpoints
- **Langfuse:** http://localhost:3001 - Observability dashboard (create account on first visit)
- **Qdrant:** http://localhost:6333/dashboard - Vector DB admin UI

**Quick test:**
```bash
# In a new terminal
curl http://localhost:8000/health
# Should return: {"status":"ok","qdrant":"ok","version":"0.1.0"}
```

### 5. Ingest Data (First Time Only)

```bash
# Embed and index StatPearls chunks into Qdrant
docker compose exec api python -m ingestion.pipeline

# Takes ~10-15 minutes for 301k chunks
# Progress bar shows: "Ingesting chunks: 100%|██████████| 301000/301000"
```

**What this does:**
- Loads StatPearls chunks from `data/statpearls_chunks.jsonl`
- Generates dense embeddings (PubMedBERT 768-dim)
- Generates sparse embeddings (BM25 tokenization)
- Uploads to Qdrant collection `medical_rag`

### 6. Test a Query

**Via Frontend:**
1. Go to http://localhost:3000
2. Select model: "Gemini Flash"
3. Select mode: "RAG"
4. Type: "What is metformin used for?"
5. Click "Send" - should get cited answer in ~2-3 seconds

**Via API:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is metformin used for?",
    "model": "gemini",
    "mode": "rag",
    "search_mode": "standard",
    "role": "doctor"
  }'
```

---

## Architecture Walkthrough

### High-Level Flow

```
User Query → Orchestrator (intent classification)
    ↓
Specialized Agent (diagnosis / pharmacology / general)
    ↓
HyDE Query Transform → Hybrid Search (dense + sparse + RRF)
    ↓
Reranking (cross-encoder) → CRAG Gate (confidence > 0.60)
    ↓
Context Assembly (dedup + lost-in-middle + citations)
    ↓
LLM Generation → Self-RAG (fidelity check, retry if needed)
    ↓
Response (answer + sources + confidence flag)
```

### Key Components (see [ARCHITECTURE.md](ARCHITECTURE.md) for details)

1. **Orchestrator** (`agents/orchestrator.py`) - Routes queries to specialized agents based on LLM-classified intent
2. **Hybrid Retriever** (`retrieval/hybrid_retriever.py`) - Combines dense (PubMedBERT) + sparse (BM25) search with RRF fusion
3. **CRAG Gate** (`retrieval/crag.py`) - Confidence thresholding using sigmoid-normalized reranker scores
4. **LLM Router** (`generation/llm_router.py`) - Factory for 4 models (Gemini Flash/Pro, BioMistral, GPT-4o)
5. **MCP Servers** (`mcp_servers/`) - FastMCP tools for medical search and citation lookup

### Data Flow Example

**Query:** "First-line treatment for hypertension?"

1. **Orchestrator** classifies intent as `GENERAL` → routes to General Agent
2. **HyDE** generates hypothetical answer: "ACE inhibitors and thiazide diuretics are first-line..."
3. **Hybrid Search** retrieves 10 chunks each for original query + HyDE query
4. **RRF Fusion** merges ranked lists: `score = sum(1 / (rank + 60))`
5. **Reranker** rescores top 20 → keeps top 5
6. **CRAG** checks top score: `sigmoid(8.3) = 0.9998 > 0.60` → confident
7. **Context Assembly** deduplicates, reorders (best at positions 0 and -1), formats citations
8. **Generator** calls Gemini Flash with context → answer with [1], [2] citations
9. **Self-RAG** checks fidelity: "faithful=true, complete=true" → done (no retry)
10. **Response** returned with 5 sources, `is_confident=true`

---

## First Tasks (Day 1)

### Task 1: Add a New Prompt Template (30 minutes)

**Goal:** Understand the generation pipeline by adding a custom prompt.

**Steps:**
1. Create `generation/prompts/pediatric_qa.txt`:
   ```
   You are a pediatric medical expert. Answer the following question for a parent audience.
   Use simple language and avoid medical jargon where possible.
   
   Question: {question}
   
   Context:
   {context}
   
   Answer:
   ```

2. Modify `generation/generator.py` line 15:
   ```python
   def build_chain(model_name: str, use_cot: bool = False, mode: str = "rag", audience: str = "doctor"):
       if audience == "parent":
           prompt = _load_prompt("pediatric_qa.txt")
       elif mode in ("graph", "hybrid"):
           prompt = _load_prompt("graph_qa.txt")
       # ... rest unchanged
   ```

3. Test:
   ```bash
   docker compose restart api
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "What is asthma?", "model": "gemini", "mode": "rag", "role": "patient"}'
   ```

**Success criteria:** Response uses simpler language than doctor-mode.

---

### Task 2: Add Logging to Silent Failure (45 minutes)

**Goal:** Improve observability by fixing a tech debt item.

**Context:** `retrieval/hybrid_retriever.py` line 95 has a bare `except Exception: pass` that silently falls back to local BM25 when Qdrant fails. See [TECH_DEBT.md](TECH_DEBT.md) Finding #2.

**Steps:**
1. Add logging import at top of `retrieval/hybrid_retriever.py`:
   ```python
   import logging
   log = logging.getLogger(__name__)
   ```

2. Replace lines 95-100:
   ```python
   def hybrid_search(query: str, top_k: int = 10) -> list[dict]:
       try:
           results = _qdrant_hybrid_search(query, top_k=top_k)
           if results:
               return results
           log.warning("Qdrant returned empty results", extra={"query": query[:50]})
       except Exception as e:
           log.error(
               "Qdrant hybrid search failed, falling back to local BM25",
               exc_info=True,
               extra={"query": query[:50], "error_type": type(e).__name__}
           )
       return _local_lexical_search(query, top_k=top_k)
   ```

3. Test by stopping Qdrant:
   ```bash
   docker compose stop qdrant
   docker compose restart api
   docker compose logs -f api  # Watch for error log
   curl -X POST http://localhost:8000/query -H "Content-Type: application/json" \
     -d '{"question": "test", "model": "gemini", "mode": "rag", "role": "doctor"}'
   docker compose start qdrant
   ```

**Success criteria:** Error log appears with "Qdrant hybrid search failed" message.

---

### Task 3: Run the Test Suite (20 minutes)

**Goal:** Understand test coverage and verify your environment.

**Steps:**
```bash
# Install test dependencies
docker compose exec api uv pip install pytest pytest-asyncio pytest-cov

# Run all tests
docker compose exec api pytest tests/ -v

# Run with coverage
docker compose exec api pytest tests/ --cov=. --cov-report=term-missing
```

**Expected output:** 40 tests pass. Coverage ~65% (retrieval and generation modules well-covered, agents less so).

**Explore tests:**
- `tests/test_hybrid_retriever.py` - Unit tests for RRF fusion, local fallback
- `tests/test_crag.py` - CRAG gate threshold tests
- `tests/test_generator.py` - Prompt loading, chain building
- `tests/test_orchestrator.py` - Intent classification, agent routing

---

## Key Files to Read First

Based on [CODE_MAP.md](CODE_MAP.md), prioritize these 5 files for deep understanding:

### 1. `agents/orchestrator.py` (200 lines)
**Why:** Entry point for all queries. Understand intent classification and agent routing.
**Key functions:** `classify_intent`, `route_to_agent`, `run_orchestrator`
**Read time:** 20 minutes

### 2. `retrieval/hybrid_retriever.py` (150 lines)
**Why:** Core retrieval logic. Understand dense+sparse fusion and RRF algorithm.
**Key functions:** `hybrid_search`, `rrf_fuse`, `_qdrant_hybrid_search`
**Read time:** 25 minutes

### 3. `agents/rag_agent.py` (200 lines)
**Why:** Standard RAG pipeline. Understand LangGraph state machine and node functions.
**Key functions:** `run_rag`, `query_transform_node`, `search_node`, `rerank_node`, `generate_node`
**Read time:** 30 minutes

### 4. `generation/llm_router.py` (50 lines)
**Why:** LLM abstraction layer. Understand model selection and configuration.
**Key function:** `get_llm`
**Read time:** 10 minutes

### 5. `retrieval/crag.py` (25 lines)
**Why:** Confidence gating logic. Understand sigmoid normalization and threshold.
**Key function:** `crag_gate`
**Read time:** 10 minutes

**Total reading time:** ~90 minutes for core understanding.

---

## Common Pitfalls

### 1. Qdrant Collection Empty After Restart
**Symptom:** Queries return "I could not find sufficiently relevant information..."
**Cause:** Qdrant data not persisted, or ingestion not run.
**Fix:**
```bash
docker compose exec api python -m ingestion.pipeline
# Wait 10-15 minutes for re-ingestion
```

### 2. BioMistral Model Not Found
**Symptom:** Error "Model file not found" when selecting BioMistral.
**Cause:** `download_data.sh` didn't complete or model file corrupted.
**Fix:**
```bash
# Re-download just the model
curl -L -o data/biomistral-7b-Q4_K_M.gguf \
  https://huggingface.co/TheBloke/BioMistral-7B-GGUF/resolve/main/biomistral-7b.Q4_K_M.gguf
docker compose restart llama-cpp
```

### 3. Langfuse Traces Not Appearing
**Symptom:** Queries work but no traces in Langfuse UI.
**Cause:** Langfuse keys not set in `.env` or Langfuse services not running.
**Fix:**
```bash
# Check Langfuse is running
docker compose ps | grep langfuse
# Should show: langfuse, langfuse-worker (both "Up")

# Create project in Langfuse UI (http://localhost:3001)
# Copy public + secret keys to .env
nano .env
# Set: LANGFUSE_PUBLIC_KEY=pk-lf-...
#      LANGFUSE_SECRET_KEY=sk-lf-...

docker compose restart api
```

### 4. Frontend Not Connecting to API
**Symptom:** Frontend loads but queries fail with network error.
**Cause:** API not running or CORS misconfigured.
**Fix:**
```bash
# Check API health
curl http://localhost:8000/health

# Check API logs
docker compose logs api | tail -50

# Restart API
docker compose restart api
```

### 5. Knowledge Graph Cache Stale
**Symptom:** Graph mode returns outdated or missing relations.
**Cause:** PrimeKG pickle cache out of sync with graph data.
**Fix:**
```bash
rm -f data/kg_cache.pkl
docker compose restart api
# Graph will rebuild cache on first query (~30 seconds)
```

---

## Development Workflow

### Making Changes

1. **Edit code** in your IDE (VSCode recommended with Python + Docker extensions)
2. **Restart affected service:**
   ```bash
   docker compose restart api      # For backend changes
   docker compose restart frontend # For React changes (or use hot reload)
   ```
3. **Test manually** via frontend or curl
4. **Run tests:**
   ```bash
   docker compose exec api pytest tests/test_<module>.py -v
   ```
5. **Check Langfuse** for traces and errors

### Adding a New Agent

1. Create `agents/new_agent.py` following the pattern in `diagnosis_agent.py`
2. Define state TypedDict with required fields
3. Implement 6 nodes: `query_and_search`, `graph_search`, `rerank`, `assemble`, `generate`, `self_reflect`
4. Build LangGraph with conditional retry edge
5. Add intent to `orchestrator.py` classification prompt
6. Add route in `orchestrator.py` `route_to_agent` function
7. Test with queries matching new intent

### Debugging Tips

- **Enable verbose logging:**
  ```bash
  # In .env
  LOG_LEVEL=DEBUG
  docker compose restart api
  ```

- **Inspect Qdrant collection:**
  ```bash
  curl http://localhost:6333/collections/medical_rag
  # Check points_count, vectors config
  ```

- **View Langfuse trace details:**
  1. Go to http://localhost:3001/traces
  2. Click on a trace
  3. Expand spans to see LLM calls, retrieval steps, timings

- **Test retrieval in isolation:**
  ```python
  from retrieval.hybrid_retriever import hybrid_search
  docs = hybrid_search("diabetes", top_k=5)
  print(docs)
  ```

---

## Getting Help

- **Documentation:** `docs/ARCHITECTURE.md`, `docs/CODE_MAP.md`, `docs/TECH_DEBT.md`
- **Code comments:** Most complex functions have docstrings
- **Team chat:** [Your team's Slack/Discord channel]
- **Issues:** Check GitHub Issues for known bugs and feature requests
- **Office hours:** [Your team's schedule]

---

## Next Steps

After completing the 3 first tasks:
1. Pick an issue from the backlog labeled `good-first-issue`
2. Read the relevant section of ARCHITECTURE.md
3. Explore the code in that module using CODE_MAP.md as a guide
4. Make your changes and submit a PR

**Recommended second-day tasks:**
- Add a new MCP tool to `mcp_servers/medical_search_server.py`
- Implement a new reranking strategy in `retrieval/reranker.py`
- Add a new evaluation metric to `evaluation/ragas_eval.py`

Welcome to the team! 🎉
