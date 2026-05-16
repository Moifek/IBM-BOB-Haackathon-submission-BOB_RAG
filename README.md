------------------------
IBM BOB Agentic Framework (Custom)
------------------------
## BOB Agentic Framework

This project uses the BOB Framework for AI-assisted development. The framework coordinates specialized AI modes to handle implementation, validation, and documentation tasks.

### Agent Roster

- **🔀 Orchestrator**: Coordinates workflow and manages task delegation
- **💻 Code Mode**: Implements features and writes code
- **✅ Validator**: Verifies implementations and runs tests
- **📝 Documenter**: Generates feature documentation

### Workflow

The framework follows a structured workflow:
1. Orchestrator analyzes requests and creates TODO lists
2. Code mode implements each task
3. Validator verifies implementation immediately
4. Process repeats with retry protocol (max 3 attempts)
5. Final validation and git diff review
6. Optional pull request creation
7. Documentation generation

### Key Features

- **Context Caching**: Reduces redundant file reads across mode switches
- **Incremental Validation**: Catches issues early with immediate verification
- **Bounded Execution**: Caps retries at 3 attempts with diagnostic analysis
- **Safety Mechanisms**: Blocks destructive commands requiring user approval
- **GitHub Integration**: Auto-generates PR descriptions from git diffs
- **Jira Integration**: Fetches requirements and posts completion summaries

### Framework Documentation

For detailed information about the BOB framework configuration:
- [Framework Overview](.bob/README.md)
- [Global Rules](.bob/AGENTS.md)
- [Custom Modes](.bob/custom_modes.yaml)
- [Mode-Specific Rules](.bob/rules-code/*)


 -------------------
 *PRODUCT*
 -------------------
# DocRAG-MD MVP
**Medical Q&A powered by retrieval-augmented generation**

![100% Open Source](https://img.shields.io/badge/100%25-Open%20Source-brightgreen)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)

DocRAG-MD is a lightweight, open-source medical question-answering system that uses retrieval-augmented generation (RAG) to provide evidence-based answers from medical literature. Built with Ollama, Chroma, and FastAPI, it offers role-based prompting for both patients and healthcare professionals.

---

## 🚀 Quick Start

Get up and running in 3 commands:

```bash
# 1. Clone and navigate
git clone <repository-url>
cd docrag-md-mvp

# 2. Download medical literature (5000 articles from StatPearls)
bash download_data.sh 5000

# 3. Start all services
docker compose up --build
```

Access the application:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Ollama (llama3.2:3b-instruct) | Answer generation |
| **Embeddings** | Ollama (nomic-embed-text) | Document vectorization |
| **Vector Store** | Chroma (embedded, file-backed) | Semantic search |
| **API** | FastAPI | REST endpoints |
| **Frontend** | React 18 + Vite + Tailwind CSS | User interface |
| **Container** | Docker Compose | Orchestration |

**Why this stack?**
- ✅ 100% open-source and self-hosted
- ✅ No API keys or external dependencies
- ✅ Runs on consumer hardware (8GB+ RAM recommended)
- ✅ Fast cold-start (~2.3 GB data)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│                    http://localhost:3000                     │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      API (FastAPI)                           │
│                    http://localhost:8000                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   /health    │  │    /query    │  │   /docs      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────┬───────────────────┬────────────────────────────┘
             │                   │
             ▼                   ▼
┌─────────────────────┐  ┌─────────────────────┐
│   Ollama Service    │  │   Chroma Vector DB  │
│  (LLM + Embeddings) │  │   (File-backed)     │
│  localhost:11434    │  │   ./data/chroma     │
└─────────────────────┘  └─────────────────────┘
```

**Request Flow:**
1. User submits question + role (patient/doctor)
2. API embeds query using Ollama
3. Chroma retrieves top-k relevant documents
4. API constructs role-specific prompt with context
5. Ollama generates answer with citations
6. Frontend displays answer + source documents

---

## 📡 API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-16T22:45:00Z",
  "services": {
    "ollama": "connected",
    "chroma": "connected"
  }
}
```

### Medical Q&A
```http
POST /query
Content-Type: application/json

{
  "question": "What are the symptoms of diabetes?",
  "role": "patient"
}
```

**Parameters:**
- `question` (string, required): Medical question
- `role` (string, required): Either `"patient"` or `"doctor"`

**Response:**
```json
{
  "answer": "Diabetes symptoms include increased thirst, frequent urination...",
  "sources": [
    {
      "title": "Diabetes Mellitus Type 2",
      "content": "Type 2 diabetes is characterized by...",
      "metadata": {
        "book_id": "NBK551501",
        "chunk_index": 0
      }
    }
  ],
  "role": "patient"
}
```

---

## ⚙️ Configuration

Configure via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_LLM_MODEL` | `llama3.2:3b-instruct` | Model for answer generation |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Model for embeddings |
| `CHROMA_PERSIST_DIR` | `./data/chroma` | Vector database storage path |
| `API_PORT` | `8000` | FastAPI server port |

**Example `.env` file:**
```bash
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_LLM_MODEL=llama3.2:3b-instruct
OLLAMA_EMBED_MODEL=nomic-embed-text
CHROMA_PERSIST_DIR=/app/data/chroma
API_PORT=8000
```

---

## 📁 Project Structure

```
docrag-md-mvp/
├── api/                    # FastAPI application
│   ├── main.py            # App entry point
│   ├── schemas.py         # Pydantic models
│   └── routers/           # API endpoints
│       ├── health.py      # Health check
│       └── query.py       # Q&A endpoint
├── llm/                   # LLM integration
│   ├── ollama_client.py   # Ollama API client
│   └── prompts/           # Role-based prompts
│       ├── doctor_qa.txt  # Doctor prompt template
│       └── patient_qa.txt # Patient prompt template
├── rag/                   # RAG pipeline
│   ├── pipeline.py        # Main RAG orchestration
│   ├── retriever.py       # Vector search
│   └── citations.py       # Source formatting
├── ingestion/             # Data ingestion
│   ├── loader.py          # StatPearls loader
│   └── pipeline.py        # Chunking + embedding
├── frontend/              # React UI
│   ├── src/
│   │   ├── components/    # React components
│   │   └── api/           # API client
│   └── Dockerfile
├── scripts/               # Utility scripts
│   └── download_statpearls.py
├── tests/                 # Test suite
│   ├── conftest.py        # Pytest fixtures
│   ├── test_*.py          # Unit tests
│   └── integration/       # Integration tests
├── docker-compose.yml     # Service orchestration
├── Dockerfile             # API container
├── download_data.sh       # Data download script
└── pyproject.toml         # Python dependencies
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Install dependencies
pip install -e ".[dev]"

# Run all tests (40 tests, <30s, no network)
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_ollama_client.py  # LLM tests
pytest tests/test_retriever.py      # RAG tests
pytest tests/test_api.py            # API tests
```

**Test Coverage:**
- ✅ Unit tests for all modules
- ✅ Integration tests for RAG pipeline
- ✅ API endpoint tests
- ✅ Mock-based (no external dependencies)
- ✅ Fast execution (<30 seconds)

---

## 🗺️ Roadmap (v2 Backlog)

Features removed from proprietary version for MVP simplicity:

### Advanced RAG
- [ ] Self-RAG (self-reflection on retrieval quality)
- [ ] CRAG (corrective retrieval)
- [ ] HyDE (hypothetical document embeddings)
- [ ] Deep search integration (PubMed API)

### Knowledge Graph
- [ ] PrimeKG integration (biomedical knowledge graph)
- [ ] Entity linking and relationship extraction
- [ ] Graph-based reasoning

### Multi-Agent System
- [ ] Orchestrator agent for task decomposition
- [ ] Specialist agents (diagnosis, treatment, research)
- [ ] Agent collaboration protocols

### Observability
- [ ] Langfuse integration for tracing
- [ ] Performance metrics dashboard
- [ ] Cost tracking

### Evaluation
- [ ] RAGAS metrics (faithfulness, relevance)
- [ ] MedMCQA benchmark integration
- [ ] Automated quality assessment

### Infrastructure
- [ ] MCP server support
- [ ] PostgreSQL for user authentication
- [ ] Horizontal scaling support

---

## 📊 Metrics

**Simplification from proprietary version:**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Docker services | 11 | 4 | **-64%** |
| Python dependencies | 22 | 9 | **-59%** |
| Cold-start data | ~6.3 GB | ~2.3 GB | **-63%** |
| External APIs | 3 | 0 | **-100%** |
| Setup complexity | High | Low | **Simplified** |

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Development setup:**
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

## 👥 Authors

- **Original Architecture**: DocRAG-MD Team
- **Open-Source MVP**: Rebuilt for community use

---

## 🙏 Acknowledgments

- **StatPearls**: Medical literature corpus
- **Ollama**: Local LLM inference
- **Chroma**: Vector database
- **FastAPI**: Modern Python web framework
- **React**: Frontend framework

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/docrag-md-mvp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/docrag-md-mvp/discussions)
- **Documentation**: [Full Docs](./ARCHITECTURE.md)

---

**Built with ❤️ for the open-source medical AI community**