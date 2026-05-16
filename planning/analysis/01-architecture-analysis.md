# 01 — Architecture Analysis (DocRAG-MD as it stands)

> **Scope.** Honest, top-down read of the current code. Used as the
> baseline for the MVP downsize plan (`02`) and the agentic rebuild
> blueprint (`03`).

---

## 1. What the product actually is

DocRAG-MD is a **multi-agent medical Q&A platform** built around
RAG over StatPearls (~301k chunks) plus a knowledge-graph traversal
on PrimeKG (~100k nodes, 4M edges) and a live PubMed deep-search
mode. It exposes a React chat UI that lets a user pick:

- **Role** — patient / doctor (changes the prompt template only)
- **Model** — Gemini 2.5 Flash, Gemini 2.5 Pro, BioMistral 7B
  (local llama.cpp), GPT-4o
- **Mode** — `rag` (StatPearls only), `graph` (KG only), `hybrid`
  (KG + StatPearls), `deep_search` (PubMed E-utilities)

The pitch is "production-grade clinical Q&A": it claims **62%+
MedMCQA accuracy** on 150 questions vs ~52% baseline (no
independent verification of those numbers in the repo).

There is **no model training anywhere**. Every model used
(PubMedBERT, MiniLM cross-encoder, BioMistral) is downloaded
pre-trained and used inference-only. The "training" that happens
in the project is just BM25 IDF fitting on the corpus
(`ingestion/embedders/sparse_embedder.py`) — that's vocabulary
+ idf statistics, not gradient-based training.

---

## 2. Top-level repo map

```
DocRAG-MD-/
├── api/                 FastAPI app + 6 routers
│   ├── main.py          lifespan: preloads KG, reranker, dense embedder
│   ├── schemas.py       Pydantic: QueryRequest/Response, Auth, Eval
│   └── routers/         health, auth, query, ws, ingest, evaluate
├── agents/              LangGraph StateGraphs
│   ├── orchestrator.py     LLM intent classifier → 4 routes
│   ├── diagnosis_agent.py  KG filter: disease_phenotype_*, disease_disease
│   ├── pharmacology_agent.py KG filter: indication, drug_drug, etc.
│   ├── general_agent.py    KG filter: all medical relations
│   ├── deep_search_agent.py PubMed multi-iteration with follow-ups
│   ├── rag_agent.py        Entry: standard pipeline OR deep_search
│   ├── eval_agent.py       MedMCQA benchmark loop
│   └── tools.py            @tool wrappers (mostly unused dead code)
├── retrieval/
│   ├── hybrid_retriever.py dense + sparse RRF, Qdrant-first w/ local fallback
│   ├── reranker.py         cross-encoder/ms-marco-MiniLM-L-6-v2
│   ├── crag.py             sigmoid(top_score) > 0.60 confidence gate
│   ├── context_assembler.py dedupe + lost-in-middle + [N] citations
│   ├── knowledge_graph.py  PrimeKG loader + NetworkX MultiGraph + pickle cache
│   ├── deep_search.py      PubMed esearch / esummary / efetch
│   ├── source_drilldown.py extra chunks from same StatPearls article
│   ├── self_reflect.py     LLM judge: faithful? complete? → retry
│   ├── qdrant_client.py    singleton client
│   └── query_transform/    hyde.py, decompose.py, multi_query.py
├── generation/
│   ├── llm_router.py       4-LLM factory (Gemini / Vertex / OpenAI / llama.cpp)
│   ├── generator.py        LCEL: prompt | llm | parser
│   ├── observability.py    Optional Langfuse callback handler
│   └── prompts/            5 .txt templates (clinical, cot, graph, patient, patient_cot)
├── ingestion/
│   ├── pipeline.py         load → embed dense+sparse → upsert Qdrant
│   ├── loaders/statpearls_loader.py  read JSONL
│   └── embedders/          dense (PubMedBERT), sparse (BM25 IDF)
├── mcp_servers/            fastmcp servers on :9001 (search) and :9002 (lookup)
├── evaluation/             RAGAS + MedMCQA driver
├── frontend/               React 18 + Vite + Tailwind, single App.jsx
├── scripts/download_all.py StatPearls tarball + PrimeKG csv downloader
├── tests/                  ~40 tests, mostly mocked
├── docker-compose.yml      11 services
├── Dockerfile              python:3.11-slim, CPU torch
└── pyproject.toml          22 prod deps, uv-managed
```

---

## 3. Runtime topology — 11 Docker services

| Service           | Port      | Role                                                  | MVP-essential? |
|-------------------|-----------|-------------------------------------------------------|----------------|
| `qdrant`          | 6333      | Vector DB (dense + sparse named vectors)              | yes            |
| `llama-cpp`       | 8080      | BioMistral-7B Q4_K_M, ctx 4096                        | no             |
| `api`             | 8000/9001/9002 | FastAPI + MCP search + MCP citation              | yes (API)      |
| `frontend`        | 3000      | React build served by nginx, proxies /api and /ws     | yes            |
| `postgres`        | 5432      | Auth users + Langfuse metadata                        | no             |
| `clickhouse`      | —         | Langfuse analytics                                    | no             |
| `minio`           | —         | Langfuse S3-compatible event store                    | no             |
| `minio-init`      | —         | One-shot MinIO bucket bootstrap                       | no             |
| `redis`           | —         | Langfuse cache                                        | no             |
| `langfuse`        | 3001      | Observability UI                                      | no             |
| `langfuse-worker` | —         | Langfuse async jobs                                   | no             |

**6 of the 11 services exist solely to host Langfuse.** Two more
exist for auth (`postgres`) and local LLM (`llama-cpp`). The
actual product logic lives in `api` + `frontend` + `qdrant`.

---

## 4. Request flow (standard mode)

```
Frontend (App.jsx)
  ws.send({question, model, mode, search_mode, role})
       │
       ▼
api/routers/ws.py  ── if search_mode == "deep" ── agents.rag_agent.run_rag(deep)
       │                                                │
       │ standard                                       └─ deep_search_agent
       ▼
agents.orchestrator.run_orchestrator(question, model, mode, search_mode)
       │
       ▼
classify_intent (LLM call → DIAGNOSTIC | PHARMACOLOGIE | GENERAL | BENCHMARK)
       │
       ├─► diagnosis_agent.run_diagnosis_pipeline   ┐
       ├─► pharmacology_agent.run_pharmacology_pipeline
       ├─► general_agent.run_general_pipeline       │ All three are the SAME
       └─► eval_agent.run_evaluation                │ pipeline w/ different
                                                    │ KG relation filters.
       ▼ (specialized pipeline)                     ┘
query_transform_and_search   (HyDE in parallel with hybrid_search)
       ▼
graph_search                 (only if mode in {graph, hybrid})
       ▼
rerank                       (cross-encoder MiniLM, top_k=5)
       ▼
crag_gate                    (sigmoid(top_score) >= 0.60 ?)
       ▼
assemble_context             (dedup + lost-in-middle + [N] citations)
       ▼
generate                     (LCEL: prompt | llm | parser)
       ▼
self_reflect                 (LLM judges faithful & complete; retry up to 2)
       ▼
END  → ws.send({type: answer, sources, intent, is_confident})
```

That gives **5 LLM calls per request worst-case** (classify +
extract terms + HyDE + generate + self-reflect), times up to 3
(initial + 2 retries) for a self-RAG retry storm = **15 LLM
calls in the worst case for a single user message.**

---

## 5. Agent inventory

| Agent                  | Real differentiation                                                        | Verdict for MVP            |
|------------------------|-----------------------------------------------------------------------------|----------------------------|
| `orchestrator`         | LLM intent classifier, then routes                                          | Cut. One agent is enough.  |
| `diagnosis_agent`      | Identical pipeline, KG filter `disease_phenotype_*`, `disease_disease`      | Cut.                       |
| `pharmacology_agent`   | Identical pipeline, KG filter `indication`, `drug_drug`, `contraindication` | Cut.                       |
| `general_agent`        | Identical pipeline, no KG filter                                            | Keep, simplify.            |
| `deep_search_agent`    | LangGraph with plan → search → drilldown → assess → maybe-loop → generate   | Optional. Cut for MVP.     |
| `eval_agent`           | Loops MedMCQA, picks first A/B/C/D in answer                                | Cut.                       |
| `rag_agent`            | Wrapper that routes between standard and deep_search                        | Cut, fold into one entry.  |

The "multi-agent" framing is mostly architectural cosplay: the
three specialized agents are **copies of the same StateGraph**
(diff = 4 lines of KG relation filter). The orchestrator burns an
LLM call to pick which copy to run.

---

## 6. Retrieval stack

- **Dense:** PubMedBERT (`pritamdeka/PubMedBERT-mnli-snli-...`),
  768-dim, ~440 MB download, CPU-bound on `sentence-transformers`.
- **Sparse:** Custom BM25 IDF embedder, vocab + idf JSON state,
  encoded into Qdrant `SparseVector`.
- **Fusion:** Reciprocal Rank Fusion with k=60.
- **Rerank:** cross-encoder `ms-marco-MiniLM-L-6-v2`, ~90 MB.
- **CRAG:** sigmoid(top_rerank_score) >= 0.60 → confident.
- **HyDE:** LLM generates a 2-3 sentence hypothetical passage,
  searched in parallel with the original query.
- **Lost-in-middle:** best chunk at index 0, second-best at -1.
- **Source drilldown** (deep_search only): pull more chunks from
  the same StatPearls title.
- **Fallback:** if Qdrant is empty/unreachable, in-process BM25
  scan over the JSONL — slow but means the app boots without
  full ingestion.

That's a lot. The retrieval pipeline alone has ~7 distinct stages
(HyDE, dense, sparse, RRF, rerank, CRAG, assemble) and each one
is one more thing that can fail or look impressive on a slide.

---

## 7. Knowledge Graph

`retrieval/knowledge_graph.py` loads `data/kg.csv` (PrimeKG
~500 MB), filters to 9 medical relation types, builds a
NetworkX `MultiGraph`, pickles it to `data/kg_cache.pkl`. The
graph is held in `app.state.kg` for the process lifetime.

Querying is **substring-matching the entity name across all
nodes** (no embedding lookup, no fuzzy alias resolution beyond a
`(disease)` suffix stripper). On a 100k-node graph this is a
linear scan per term, per request. It works because the LLM
extracts only a handful of terms.

The graph adds value for `mode="graph"` and `mode="hybrid"` (a
~15-line "Knowledge Graph — Diagnostic Relations" block prepended
to the LLM context). For `mode="rag"` it is unused.

**Memory cost:** several GB resident after pickle load.
**Boot cost:** 30-90 s first time (CSV parse), <10 s from cache.

---

## 8. LLM router

`generation/llm_router.py` — 4 backends through one factory:

| Name          | Backend                                                | When you'd use it              |
|---------------|--------------------------------------------------------|--------------------------------|
| `gemini`      | Vertex AI `gemini-2.5-flash` if `GOOGLE_CLOUD_PROJECT` is set, else `langchain-google-genai` | Default, fast, cheap |
| `gemini-pro`  | Same factory, `gemini-2.5-pro`                         | Higher reasoning, slower       |
| `gpt4o`       | `ChatOpenAI(model="gpt-4o")`                           | Comparison, requires API key   |
| `biomistral`  | `ChatOpenAI(base_url=llama-cpp:8080)` w/ fake api_key  | "Local / private" demo         |

The router itself is fine. The cost is **everything that exists
to support `biomistral`**: the `llama-cpp` Docker service, the
4.1 GB GGUF in `models/`, the `download_data.sh` GGUF leg, and
the latency/quality tradeoff that makes the demo look bad.

---

## 9. Self-RAG and CRAG

- **CRAG (`retrieval/crag.py`)** — 22 lines. Sigmoid-normalize the
  top reranker score and compare to threshold. If below: keep the
  docs but flag `is_confident=False` and fall through to a canned
  "I could not find sufficiently relevant information…" answer.
- **Self-RAG (`retrieval/self_reflect.py`)** — Post-generation,
  ask the LLM: `{"faithful": bool, "complete": bool, "reason": ...}`.
  If false on either, increment retry count, reformulate question
  with the reason, run the full pipeline again. Cap at 2 retries.

Both are real techniques and worth keeping in the long-term
product. For a hackathon MVP they multiply LLM cost and add
latency for marginal quality wins on demo questions.

---

## 10. Data pipeline

- `scripts/download_all.py` pulls **statpearls_NBK430685.tar.gz**
  (~1.7 GB) from NCBI, parses JATS XML, splits into ~400-word
  chunks, writes `data/statpearls_chunks.jsonl` (~301k chunks
  unbounded; `DATA_CHUNK_LIMIT=5000` for smoke tests). It also
  pulls **PrimeKG `kg.csv`** (~500 MB) from Harvard Dataverse.
- `download_data.sh` then pulls **BioMistral-7B.Q4_K_M.gguf**
  (~4.1 GB) from HuggingFace.
- `ingestion/pipeline.py` reads JSONL, fits BM25 idf, dense-embeds
  with PubMedBERT, upserts to Qdrant in batches of 64.

**Total cold-start data weight:** ~6.3 GB download + ~1.7 GB
JSONL on disk + several GB of process RAM at runtime.

---

## 11. Observability

`generation/observability.py` exposes `create_langfuse_handler()`
which is no-op when `LANGFUSE_PUBLIC_KEY` is missing. So Langfuse
**is technically optional in code**. But the docker-compose has
all 6 Langfuse services wired and starts them by default. To run
without Langfuse you have to remove or `--scale 0` six services.

---

## 12. Auth

`api/routers/auth.py` is a from-scratch Postgres + bcrypt
implementation: `_ensure_database()`, `_ensure_table()`,
`/auth/signup`, `/auth/login`. No JWT, no sessions — the
frontend just stores `{username, role}` after login and sends
`role` on every WS message. The `role` only switches the prompt
template.

For an MVP this is far more infrastructure than the feature
needs.

---

## 13. Frontend

Single-page React 18:

- **`App.jsx`** — owns WebSocket lifecycle, message log, model /
  mode / search-mode / role state, streaming-delta accumulation,
  trace-event merging.
- **`components/`** — `ChatWindow`, `MessageBubble`,
  `ModelSelector`, `ModeSelector`, `SearchModeSelector`,
  `SourcePanel`, `DeepSearchTracePanel`, `AuthPage`,
  `LandingPage`, `DarkModeToggle`.
- **`api/client.js`** — `createChatSocket()` thin WS wrapper.
- Nginx proxies `/api/*` and `/ws/*` to the backend.

The frontend is the **least bloated part of the system**. It is
already MVP-shaped.

---

## 14. Tests

7 files, ~40 tests, `pytest-asyncio` with `asyncio_mode = "auto"`,
heavy use of `unittest.mock.patch` and `AsyncMock`.

- `test_api.py` — endpoint smoke (mocks orchestrator).
- `test_agents.py` — RAG pipeline + deep-search routing.
- `test_retrieval.py` — RRF, CRAG, dedup, lost-in-middle.
- `test_ingestion.py` — **actually downloads and runs PubMedBERT**
  (the `test_dense_embedder_shape` and `test_dense_embed_query`
  cases). Slow on a cold cache.
- `test_generator.py` — LLM router + chain plumbing.
- `test_deep_search.py` — full deep-search graph with everything
  mocked.
- `test_downloader.py` — XML parsing without network.

---

## 15. Heavy / fragile components — what costs the most

Ranked by "pain per unit of demo value":

1. **Langfuse v3 stack (postgres + clickhouse + minio + redis +
   langfuse + langfuse-worker)** — 6 services for telemetry the
   demo audience never sees.
2. **BioMistral 7B GGUF + llama.cpp service** — 4.1 GB download,
   one full Docker service, slower and lower-quality than Gemini
   Flash on the same questions. Provides the "runs locally" story
   but kills the bring-up time.
3. **PrimeKG (500 MB CSV + pickle cache + NetworkX in RAM)** —
   only used in `graph` and `hybrid` modes. Adds 30-90 s to first
   boot and several GB of RAM. The "GraphRAG" demo lift is real
   but the cost is huge.
4. **PubMedBERT dense embedder (~440 MB) + cross-encoder reranker
   (~90 MB)** — both download via `sentence-transformers`. The
   reranker runs synchronously on CPU per request — clearly the
   bottleneck on a laptop demo.
5. **Self-RAG retry loop** — multiplies LLM cost by up to 3x and
   adds 5-15 s of tail latency.
6. **Multi-agent orchestrator + 3 specialized clones** — extra
   LLM call on every request, and the specialization is just a KG
   relation filter you could pass as a parameter.
7. **Auth via Postgres + bcrypt** — full DB service for a feature
   (role-based prompt) that doesn't need a DB.
8. **MCP servers (medical_search, citation_lookup)** — extra
   ports, extra processes. Useful for external Claude/Cursor
   integration; useless for a self-contained demo.
9. **MedMCQA + RAGAS evaluation** — pulls HuggingFace datasets,
   nice for a slide, irrelevant to the live demo.
10. **301k-chunk full StatPearls corpus** — the MVP demo can ride
    on 5-10k chunks from the same source without anyone noticing.

---

## 16. What's actually load-bearing for "medical RAG"

If you strip everything above to its core purpose, the system is:

```
question
  → embed
  → vector search
  → take top-k chunks
  → format with citations
  → ask Gemini to answer using only those chunks
  → return answer + sources
```

That's ~150 lines of Python. Everything else is **optimization,
defensiveness, observability, or feature-fan-out** layered on top.

The MVP plan in `02-mvp-downsize-plan.md` rebuilds the system
from that core outward, picking up only the layers that move the
needle for a hackathon demo.
