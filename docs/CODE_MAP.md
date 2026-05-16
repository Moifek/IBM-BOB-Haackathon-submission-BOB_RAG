# DocRAG-MD Code Map

Function-level catalog of core DocRAG-MD components. This map covers the 5 key files in the retrieval and generation pipeline.

---

## `retrieval/hybrid_retriever.py`

Hybrid retrieval combining dense (PubMedBERT) and sparse (BM25) search with Reciprocal Rank Fusion.

| Function/Class | Purpose | Key Parameters | Return Type |
|----------------|---------|----------------|-------------|
| `rrf_fuse` | Reciprocal Rank Fusion - merges multiple ranked lists using RRF algorithm | `ranked_lists: list[list[dict]]`, `k: int = 60` | `list[dict]` |
| `_to_hit_dict` | Converts Qdrant hit object to standardized dict format | `hit` (Qdrant point) | `dict` |
| `_local_result` | Formats local document as search result dict | `doc: dict`, `score: float` | `dict` |
| `_local_lexical_search` | BM25 search over local document corpus (fallback) | `query: str`, `top_k: int = 10` | `list[dict]` |
| `_qdrant_hybrid_search` | Executes dense + sparse search in Qdrant, fuses with RRF | `query: str`, `top_k: int` | `list[dict]` |
| `hybrid_search` | **Main entry point** - Qdrant hybrid search with local fallback | `query: str`, `top_k: int = 10` | `list[dict]` |
| `_load_local_index` | Lazy-loads local StatPearls chunks and builds BM25 index | None | `tuple[list[dict], BM25Okapi \| None]` |
| `_get_sparse_embedder` | Lazy-loads or fits sparse embedder for BM25 vectors | None | `SparseEmbedder` |

**Key Implementation Details:**
- Uses named vectors in Qdrant: `dense` (768-dim PubMedBERT) and `sparse` (BM25)
- RRF formula: `score = sum(1 / (rank + k))` where k=60
- Fallback to local BM25 if Qdrant unavailable or empty
- Singleton pattern for sparse embedder and local index (module-level caching)

---

## `retrieval/crag.py`

CRAG (Corrective RAG) confidence gating using sigmoid-normalized reranker scores.

| Function/Class | Purpose | Key Parameters | Return Type |
|----------------|---------|----------------|-------------|
| `crag_gate` | Filters documents by confidence threshold using sigmoid normalization | `docs: list[dict]`, `threshold: float = 0.60` | `tuple[list[dict], bool]` |
| `sigmoid` (nested) | Sigmoid normalization function: `1 / (1 + exp(-x))` | `x: float` | `float` |

**Key Implementation Details:**
- Default threshold: 0.60 (configurable via `CRAG_CONFIDENCE_THRESHOLD` env var)
- Normalizes cross-encoder scores (range ~-10 to 10) to [0, 1] via sigmoid
- Returns `(docs, is_confident)` tuple - if top score < threshold, `is_confident=False`
- Caller should refuse to answer when `is_confident=False`

---

## `agents/rag_agent.py`

LangGraph-based RAG pipeline with standard and Deep Search modes.

### State Definition

| Class | Purpose | Key Fields |
|-------|---------|------------|
| `RAGState` | TypedDict for LangGraph state | `question`, `model_name`, `role`, `search_mode`, `queries`, `raw_docs`, `reranked_docs`, `is_confident`, `context`, `answer`, `sources`, `messages`, `progress_callback` |

### Graph Nodes (async functions)

| Function | Purpose | Key Parameters | Return Type |
|----------|---------|----------------|-------------|
| `query_transform_node` | Generates HyDE hypothetical document for query expansion | `state: RAGState`, `config: RunnableConfig` | `dict` (updates `queries`) |
| `search_node` | Executes hybrid search for all queries, deduplicates results | `state: RAGState` | `dict` (updates `raw_docs`) |
| `rerank_node` | Reranks documents and applies CRAG confidence gate | `state: RAGState` | `dict` (updates `reranked_docs`, `is_confident`) |
| `assemble_node` | Assembles context with lost-in-middle ordering and citations | `state: RAGState` | `dict` (updates `context`, `sources`) |
| `generate_node` | Generates final answer using LLM (or refusal if not confident) | `state: RAGState`, `config: RunnableConfig` | `dict` (updates `answer`) |

### Graph Management

| Function | Purpose | Key Parameters | Return Type |
|----------|---------|----------------|-------------|
| `build_rag_graph` | Constructs LangGraph StateGraph with 5 nodes | None | `StateGraph` (compiled) |
| `get_rag_graph` | Singleton accessor for compiled RAG graph | None | `StateGraph` |

### Entry Points

| Function | Purpose | Key Parameters | Return Type |
|----------|---------|----------------|-------------|
| `run_standard_rag` | Executes standard RAG pipeline (HyDE → search → rerank → CRAG → generate) | `question: str`, `model_name: str = "gemini"`, `role: str = "doctor"`, `progress_callback`, `config: dict \| None` | `dict` (answer, sources, is_confident, search_mode) |
| `run_rag` | **Main entry point** - routes to standard or Deep Search based on `search_mode` | `question: str`, `model_name: str = "gemini"`, `role: str = "doctor"`, `search_mode: str = "standard"`, `progress_callback` | `dict` (answer, sources, is_confident, search_mode) |

### Helper Functions

| Function | Purpose | Key Parameters | Return Type |
|----------|---------|----------------|-------------|
| `_emit_progress` | Emits progress events via callback (for WebSocket streaming) | `state: RAGState`, `step: str`, `status: str`, `**payload` | `None` (async) |
| `_stream_answer_chunks` | Streams answer text in chunks via progress callback | `answer: str`, `progress_callback` | `None` (async) |

**Key Implementation Details:**
- LangGraph pipeline: `query_transform → search → rerank → assemble → generate`
- Progress events: `planning`, `retrieval`, `assessment`, `generation` (each with `running`/`done` status)
- Deep Search mode delegates to `deep_search_agent.run_deep_search`
- Langfuse observability injected via `config["callbacks"]`
- Refusal message when `is_confident=False`: "I could not find sufficiently relevant information..."

---

## `generation/generator.py`

LCEL (LangChain Expression Language) generation chains with prompt templates.

| Function | Purpose | Key Parameters | Return Type |
|----------|---------|----------------|-------------|
| `_load_prompt` | Loads prompt template from `prompts/` directory | `name: str` | `PromptTemplate` |
| `build_chain` | Constructs LCEL chain: `prompt \| llm \| parser` | `model_name: str`, `use_cot: bool = False`, `mode: str = "rag"` | LCEL chain |
| `generate_answer` | **Main entry point** - generates answer from question + context | `question: str`, `context: str`, `model_name: str`, `use_cot: bool = False`, `mode: str = "rag"`, `config` | `str` (async) |

**Prompt Selection Logic:**
- `mode="graph"` or `"hybrid"` → `graph_qa.txt`
- `use_cot=True` → `cot_medical.txt` (chain-of-thought)
- Default → `clinical_qa.txt`

**Key Implementation Details:**
- LCEL pattern: `PromptTemplate | LLM | StrOutputParser()`
- Prompts stored in `generation/prompts/` directory
- Run name set to `"3_generate_answer"` for Langfuse tracing
- Async invocation with config passthrough for callbacks

---

## `generation/llm_router.py`

LLM factory supporting 4 models: Gemini Flash/Pro, BioMistral, GPT-4o.

| Function | Purpose | Key Parameters | Return Type |
|----------|---------|----------------|-------------|
| `get_llm` | **Factory function** - returns configured LLM instance based on model name | `model_name: str = "gemini"` | `ChatOpenAI` or `ChatVertexAI` or `ChatGoogleGenerativeAI` |

**Model Routing Logic:**

| `model_name` | LLM Class | Configuration |
|--------------|-----------|---------------|
| `"biomistral"` | `ChatOpenAI` | `base_url=BIOMISTRAL_URL` (llama.cpp server), `model="biomistral"`, `temperature=0.0`, `max_tokens=1024` |
| `"gemini"` | `ChatVertexAI` (if `GOOGLE_CLOUD_PROJECT` set) or `ChatGoogleGenerativeAI` | `model_name="gemini-2.5-flash"`, `temperature=0.0` |
| `"gemini-pro"` | `ChatVertexAI` (if `GOOGLE_CLOUD_PROJECT` set) or `ChatGoogleGenerativeAI` | `model_name="gemini-2.5-pro"`, `temperature=0.0` |
| `"gpt4o"` | `ChatOpenAI` | `model="gpt-4o"`, `temperature=0.0`, `api_key=OPENAI_API_KEY` |

**Key Implementation Details:**
- Vertex AI preferred for Gemini if `GOOGLE_CLOUD_PROJECT` env var set
- Falls back to Gemini API if only `GOOGLE_API_KEY` / `GEMINI_API_KEY` set
- BioMistral runs locally via llama.cpp server (default: `http://llama-cpp:8080/v1`)
- All models use `temperature=0.0` for deterministic outputs
- Raises `ValueError` for unknown model names

---

## Cross-File Dependencies

```
hybrid_retriever.py
    ↓ (provides search results)
rag_agent.py (search_node)
    ↓ (raw docs)
reranker.py (not in this map)
    ↓ (reranked docs)
crag.py (crag_gate)
    ↓ (filtered docs + confidence flag)
rag_agent.py (assemble_node)
    ↓ (context + sources)
generator.py (generate_answer)
    ↓ (uses)
llm_router.py (get_llm)
    ↓ (returns LLM instance)
generator.py (build_chain)
    ↓ (final answer)
rag_agent.py (generate_node)
```

## Usage Patterns

**Standard RAG Query:**
```python
from agents.rag_agent import run_rag

result = await run_rag(
    question="What is metformin used for?",
    model_name="gemini",
    search_mode="standard"
)
# result = {"answer": "...", "sources": [...], "is_confident": True, "search_mode": "standard"}
```

**Hybrid Search Only:**
```python
from retrieval.hybrid_retriever import hybrid_search

docs = hybrid_search("diabetes treatment", top_k=10)
# docs = [{"doc_id": "...", "title": "...", "content": "...", "score": 8.3}, ...]
```

**CRAG Confidence Check:**
```python
from retrieval.crag import crag_gate

filtered_docs, is_confident = crag_gate(reranked_docs, threshold=0.60)
if not is_confident:
    return "Cannot answer confidently"
```

**LLM Selection:**
```python
from generation.llm_router import get_llm

llm = get_llm("gemini-pro")  # or "gemini", "biomistral", "gpt4o"
```
