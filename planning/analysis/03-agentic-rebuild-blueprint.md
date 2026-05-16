# 03 — Agentic Rebuild Blueprint (DocRAG-MD MVP, Open-Source Stack)

> **Audience.** This document is for the AI agent team that will
> rebuild DocRAG-MD into the open-source MVP described in
> `02-mvp-downsize-plan.md`. Each task block below is a
> **self-contained contract** an agent can pick up without
> re-reading the whole repo.

> **Stack reminder (no proprietary APIs).**
> - **LLM + embeddings:** Ollama (`llama3.2:3b-instruct` +
>   `nomic-embed-text`).
> - **Vector store:** Chroma (embedded, file-backed, in-process).
> - **API:** FastAPI, single `/health` + `/query` POST.
> - **Frontend:** React 18 + Vite + Tailwind (existing, gutted).
> - **Container:** 2 services (`api`, `ollama`) + one-shot
>   `ollama-init`.
> - **No** Gemini, OpenAI, Vertex, BioMistral, PubMedBERT,
>   PrimeKG, Langfuse, Postgres, MCP, MedMCQA, RAGAS, auth.

---

## 0. Working principles for every agent

1. **Read first.** Before changing a file, read it fully and
   read what imports it. The repo is small enough that a
   `grep`-then-read pass takes a few minutes.
2. **Delete in commits, don't comment-out.** Every "we'll keep
   this just in case" line accrues confusion. `git` is the
   safety net.
3. **Match the existing code style.** French docstrings stay
   French. English identifiers stay English. LCEL for chains.
4. **No new test frameworks.** Existing `pytest` + `pytest-asyncio`
   with `asyncio_mode = "auto"` is the standard.
5. **Mock anything that hits the network in tests.** Tests must
   pass with no Ollama running and no internet.
6. **One PR per agent task.** Each contract below = one branch
   = one PR.
7. **Update `docs/analysis/CHANGELOG.md`** with a one-line entry
   per merged task so the next agent knows what landed.

---

## 1. Target file tree (post-rebuild)

```
docrag-md-mvp/
├── api/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, lifespan, CORS
│   ├── schemas.py                 # Pydantic models
│   └── routers/
│       ├── __init__.py
│       ├── health.py              # GET /health
│       └── query.py               # POST /query
├── rag/
│   ├── __init__.py
│   ├── pipeline.py                # rag_pipeline(question, role) → {answer, sources}
│   ├── retriever.py               # search(query, top_k) → list[dict]
│   └── citations.py               # deduplicate, format_citations, assemble_context
├── llm/
│   ├── __init__.py
│   ├── ollama_client.py           # get_llm(), get_embeddings()
│   └── prompts/
│       ├── doctor_qa.txt
│       └── patient_qa.txt
├── ingestion/
│   ├── __init__.py
│   ├── pipeline.py                # run(limit) → int
│   └── loader.py                  # load_chunks(path, limit)
├── scripts/
│   └── download_statpearls.py     # StatPearls JATS XML → JSONL
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_query.py
│   ├── test_pipeline.py
│   ├── test_retriever.py
│   ├── test_citations.py
│   └── test_ingestion_pipeline.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Single-screen chat
│   │   ├── main.jsx
│   │   ├── index.css
│   │   ├── api/
│   │   │   └── client.js         # postQuery()
│   │   └── components/
│   │       ├── ChatWindow.jsx
│   │       ├── MessageBubble.jsx
│   │       ├── SourcePanel.jsx
│   │       ├── RoleSelector.jsx  # patient / doctor toggle
│   │       └── DarkModeToggle.jsx
│   ├── public/
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── package.json
│   ├── nginx.conf
│   └── Dockerfile
├── docs/
│   └── analysis/
│       ├── 01-architecture-analysis.md
│       ├── 02-mvp-downsize-plan.md
│       ├── 03-agentic-rebuild-blueprint.md
│       └── CHANGELOG.md
├── data/                          # .gitignore'd
│   ├── statpearls_chunks.jsonl
│   └── chroma/
├── .env.example
├── .dockerignore
├── docker-compose.yml             # 4 services: ollama, ollama-init, api, frontend
├── Dockerfile                     # Python 3.11 + uv
├── start.sh
├── download_data.sh               # StatPearls only
├── pyproject.toml
├── uv.lock
├── LICENSE
└── README.md
```

---

## 2. Agent roster

The work is distributed across **4 agents** working in sequence:

| Agent          | Role                                                       | Depends on     |
|----------------|------------------------------------------------------------|----------------|
| `orchestrator` | Coordinates workflow, assigns tasks, tracks progress       | nothing        |
| `coder`        | Implements all code changes (scaffold, backend, data, frontend, infra, tests) | `orchestrator` |
| `validator`    | Validates code quality, tests, and acceptance criteria     | `coder`        |
| `documenter`   | Rewrites README and CHANGELOG                              | `validator`    |

**Note:** The `coder` agent is responsible for all technical implementation work that was previously split across `architect`, `backend`, `data`, `frontend`, `infra`, and `tester` agents. This consolidation simplifies coordination while maintaining clear task boundaries within the implementation phases.

---

## 3. Task contracts

### TASK 1 — `coder`: Complete MVP implementation

This is a comprehensive task covering all code implementation. The coder should work through the phases sequentially, validating each phase before proceeding to the next.

**See the full implementation contract in the sections below, organized by phase.**

---

### TASK 2 — `documenter`: README + CHANGELOG

**Goal.** Rewrite `README.md` to match the open-source MVP. Add
`docs/analysis/CHANGELOG.md`.

**README structure** (one page, in this order):

1. Hero: title, one-sentence pitch, "100% open-source" badge.
2. Demo gif placeholder (link to `docs/screenshots/`).
3. **Quick start** — 3 commands:
   ```bash
   git clone … && cd docrag-md-mvp
   bash download_data.sh 5000
   docker compose up --build
   ```
4. **Stack:** Python, FastAPI, LangChain LCEL, Chroma, Ollama
   (`llama3.2:3b-instruct` + `nomic-embed-text`), React, Tailwind.
   Explicitly mention "no API keys, no cloud calls, no data
   leaves your machine."
5. **Architecture** — re-use the ASCII diagram from `02`
   Section 5.
6. **Endpoints** — 2 endpoints from `02` Section 14.
7. **Configuration** — table of the 5 env vars.
8. **Project structure** — tree from this doc Section 1.
9. **Tests** — `uv run pytest tests/ -v`.
10. **Roadmap (v2 backlog)** — bulleted list of features cut for
    MVP (KG, multi-agent, deep search, observability, auth,
    rerank, hybrid retrieval). Link to `02-mvp-downsize-plan.md`.
11. **License + authors.**

**Drop from the existing README:**
- All Langfuse screenshots and section.
- The "11 Docker services" table.
- The `gemini`/`gpt4o`/`biomistral` model section.
- The "62%+ MedMCQA accuracy" claim (we don't run that
  benchmark anymore).
- All MCP server documentation.

**`docs/analysis/CHANGELOG.md`** — start with:
```markdown
# Rebuild Changelog

## 2026-05-XX — Open-source MVP rebuild

- Replaced Gemini / GPT-4o / BioMistral with Ollama
  (llama3.2:3b-instruct + nomic-embed-text).
- Replaced PubMedBERT + cross-encoder + Qdrant + BM25 with
  Ollama embeddings + Chroma (embedded).
- Removed PrimeKG knowledge graph (was 500 MB CSV +
  NetworkX MultiGraph).
- Removed Langfuse stack (postgres + clickhouse + minio +
  redis + langfuse + langfuse-worker = 6 services).
- Removed Postgres-backed auth.
- Removed multi-agent orchestrator and 3 specialized agent
  clones; replaced with a single `rag_pipeline()` function.
- Removed Self-RAG retry loop, CRAG gate, HyDE, multi-query
  expansion, question decomposition.
- Removed deep search agent + PubMed E-utilities.
- Removed MCP servers (medical_search, citation_lookup).
- Removed RAGAS + MedMCQA evaluation.
- Reduced Docker services: 11 → 4.
- Reduced cold-start data: ~6.3 GB → ~2.3 GB (mostly Ollama
  models).
- Reduced pyproject deps: 22 → 9.
```

**Acceptance.**
- README renders cleanly on GitHub.
- No reference to deleted features.
- The three quick-start commands work on a fresh clone.

**Out of scope.** Logos, screenshots polishing, marketing copy.

---

## 4. Execution order and parallelism

```
                    ┌───────────────┐
                    │ orchestrator  │   (coordinates)
                    └───────┬───────┘
                            │
                            ▼
                       ┌────────┐
                       │ coder  │   (implements all phases)
                       └────┬───┘
                            │
                            ▼
                      ┌──────────┐
                      │validator │   (validates)
                      └────┬─────┘
                           │
                           ▼
                      ┌────────────┐
                      │documenter  │   (documents)
                      └────────────┘
```

The `coder` agent works through 6 implementation phases sequentially:
1. Scaffold and cleanup
2. Backend implementation
3. Data pipeline
4. Frontend rebuild
5. Infrastructure
6. Test suite

Each phase must be validated before proceeding to the next.

---

## 5. Quality gates between tasks

After each phase, before proceeding:

**Phase 1 (Scaffold):**
- `uv pip install -e .` succeeds
- `uvicorn api.main:app` boots and returns scaffold health

**Phase 2 (Backend):**
- `POST /query` returns 200 with mocked dependencies
- No proprietary API imports remain

**Phase 3 (Data):**
- `bash download_data.sh 5000` creates valid JSONL
- `python -m ingestion.pipeline 50` completes successfully

**Phase 4 (Frontend):**
- `npm run build` produces `dist/`
- Dev server connects to API

**Phase 5 (Infrastructure):**
- `docker compose config` validates
- `docker compose build` succeeds

**Phase 6 (Tests):**
- Full suite under 30s, no network
- All tests pass

**Final validation (before documenter):**
- `docker compose up --build` works end-to-end
- All acceptance criteria met

---

## 6. Common pitfalls and how to avoid them

| Pitfall                                                       | Mitigation                                                  |
|---------------------------------------------------------------|--------------------------------------------------------------|
| `langchain-ollama` version drift breaks `embed_documents`     | Pin to `langchain-ollama>=0.2.0,<0.4.0` in `pyproject.toml`  |
| Chroma defaults to a telemetry call on first init             | Always pass `Settings(anonymized_telemetry=False)`          |
| Ollama model not pulled before `api` boots                     | `ollama-init` is `service_completed_successfully` dependency |
| Embedding dim mismatch between query and stored vecs          | Use the **same** `OLLAMA_EMBED_MODEL` for ingest and search |
| Tests accidentally touch real Ollama                          | Mock `langchain_ollama.OllamaEmbeddings` and `ChatOllama` at the import site |
| Chroma persist dir not shared between `api` runs              | Mount `./data` volume in compose; never write to `/tmp`     |
| Frontend can't reach API in dev (CORS)                        | `allow_origins` already includes `:5173`; keep it           |
| `httpx` removed accidentally — health check breaks            | `httpx` is in the keep list; verify in pyproject            |

---

## 7. v2 backlog (after MVP demo)

Re-introduce, in this order, only after the MVP demo lands:

1. **Hybrid retrieval** — bring back BM25 sparse + RRF using
   `chromadb`'s built-in BM25 or a thin wrapper. Adds `~+5-10%`
   recall on rare-term queries.
2. **Reranking** — small cross-encoder (`bge-reranker-base` via
   Ollama if/when it lands, otherwise `sentence-transformers`).
3. **Self-RAG** — single retry on low-confidence answers.
4. **Knowledge graph** — start with a tiny, hand-curated graph
   (10-20 diseases, 50 drugs); avoid PrimeKG until you actually
   need 100k nodes.
5. **Multi-agent** — only re-introduce if there's a *real*
   reason for separate pipelines (e.g., a pharmacology agent
   that calls a drug-interaction API the diagnosis agent
   doesn't).
6. **Deep search** — PubMed E-utilities behind a feature flag.
7. **Observability** — start with stdout JSON logs, add
   OpenTelemetry traces, only consider Langfuse if traffic
   justifies it.
8. **Auth** — JWT + bcrypt, in-process SQLite first. Postgres
   only when multi-instance.
9. **Larger LLM** — bump to `llama3.1:8b-instruct` or
   `mistral:7b-instruct` once you have a GPU host or a
   dedicated inference machine.

Each v2 item should ship as a separate PR with its own task
contract in this same style.

---

## 8. Final acceptance for the rebuilt MVP

Sign-off requires every box checked:

- [ ] `git clone` + `bash download_data.sh 5000` +
      `docker compose up --build` works on a fresh Ubuntu VM
      with Docker installed and **no API keys**.
- [ ] After ~10-15 min (model download + ingest), the chat at
      `http://localhost:3000` answers 5 demo medical questions
      with `[N]`-cited sources.
- [ ] `curl -X POST localhost:8000/query -H 'Content-Type: application/json' -d '{"question":"What is hypertension?","role":"doctor"}'`
      returns 200.
- [ ] `uv run pytest tests/ -v` passes in <30 s with no
      network.
- [ ] `docker compose ps` shows exactly 4 services running:
      `ollama`, `api`, `frontend`, plus the exited `ollama-init`.
- [ ] Repo size on disk (excluding `data/` and Ollama models) is
      under 50 MB.
- [ ] No file in the codebase references: `gemini`,
      `langchain_google_genai`, `langchain_google_vertexai`,
      `langchain_openai`, `gpt4o`, `biomistral`, `langfuse`,
      `qdrant`, `primekg`, `pubmedbert`, `bcrypt`, `psycopg2`,
      `fastmcp`, or `mcp_servers`.

When all 7 boxes are checked, the rebuild is done.

---

## APPENDIX: Detailed implementation specifications for coder

The following sections provide the complete implementation details for each phase of the coder's work. Reference these when implementing each phase.

### A. Phase 1: Scaffold and cleanup

See Section 3, TASK 1, Phase 1 above for the complete list of files to delete and create.

### B. Phase 2: Backend implementation

See original document sections for complete code listings of:
- `llm/ollama_client.py`
- `llm/prompts/*.txt`
- `rag/retriever.py`
- `rag/citations.py`
- `rag/pipeline.py`
- `api/schemas.py`
- `api/routers/query.py`
- `api/routers/health.py`
- `api/main.py`

### C. Phase 3: Data pipeline

See original document sections for complete code listings of:
- `ingestion/loader.py`
- `ingestion/pipeline.py`
- `scripts/download_statpearls.py`
- `download_data.sh`

### D. Phase 4: Frontend rebuild

See original document sections for complete code listings of:
- `components/RoleSelector.jsx`
- `api/client.js`
- `App.jsx`
- `nginx.conf`

### E. Phase 5: Infrastructure

See original document sections for complete code listings of:
- `docker-compose.yml`
- `Dockerfile`
- `start.sh`
- `.dockerignore`

### F. Phase 6: Test suite

See original document sections for complete code listings of:
- `tests/conftest.py`
- `tests/test_health.py`
- `tests/test_query.py`
- `tests/test_pipeline.py`
- `tests/test_retriever.py`
- `tests/test_citations.py`
- `tests/test_ingestion_pipeline.py`

---

**Note:** For the complete code listings referenced in the appendix, refer to the original blueprint document sections TASK B through TASK F. The coder should implement these sequentially as part of their comprehensive implementation task.
