# BobRAG-MD + Bobalytics 🧬📊

> **Master's thesis-grade medical RAG, analyzed by IBM Bob as the codebase intelligence layer — in 22 Bobcoins.**

Built for the IBM Bob Hackathon (May 15–17, 2026), under a hard 40-Bobcoin budget.

[**▶ Demo video**](#) · [**Pitch deck**](docs/PITCH_DECK.pdf) · [**Bob usage report**](BOB_USAGE_REPORT.md) · [**Architecture (Bob-generated)**](docs/ARCHITECTURE.md)

---

![Bobalytics Dashboard](docs/screenshots/dashboard-overview.png)

*Bobalytics — the dashboard that monitors my AI worker the way enterprises monitor remote workers.*

---

## The thesis (one paragraph)

DocRAG-MD is my Master's thesis at Télécom Paris: a multi-component medical RAG platform built by a team of 5 over 4 months — hybrid retrieval (PubMedBERT + BM25 + RRF), CRAG confidence gating, LangGraph multi-agent orchestration, FastMCP, Langfuse, Ragas. About 50 Python files.

For the IBM Bob Hackathon, I vendored DocRAG-MD into this repo as a read-only `analysis-target/`, then gave it to IBM Bob under a 40-Bobcoin budget and asked: be the codebase intelligence layer. Generate architecture docs. Find tech debt. Build an MCP server that exposes the codebase as tools. Propose a refactor.

The submission has three layers in one repo: the vendored DocRAG-MD (subject of analysis), a minimal working RAG I built solo (proof of domain), and **Bobalytics** — a Next.js dashboard that visualizes Bob's work.

The framing: *Others built dashboards to monitor remote workers. I built one to monitor my AI worker.*

## The 5 visualizations (Bobalytics)

| Visualization | What it shows | Tech |
|---|---|---|
| **Bob Session Timeline** | All 9 Bob sessions, color-coded by mode, height = Bobcoins | Recharts bar |
| **Bobcoin Budget Gauge** | Total spent vs 40 hard limit, green/amber/red | Recharts radial |
| **RAG Query Traces** | Live latency per query stage (retrieval/generation/total) | Recharts + Langfuse |
| **Ragas Evaluation Radar** | Faithfulness, answer relevancy, context precision, context recall | Recharts radar |
| **DocRAG-MD Dependency Graph** | Import relationships among DocRAG-MD source modules | React Flow + Python AST |

## What IBM Bob did

| # | Deliverable | Bobcoins |
|---|---|---|
| 1 | `docs/ARCHITECTURE.md` — DocRAG-MD architecture with mermaid | 3 |
| 2 | `docs/CODE_MAP.md` — function-level catalog | 3 |
| 3 | `docs/TECH_DEBT.md` — 5 ranked findings with line refs | 4 |
| 4 | `docs/ONBOARDING.md` — day-1 developer guide | 2 |
| 5 | `src/codebase_mcp/server.py` — MCP server exposing DocRAG-MD as tools | 4 |
| 6 | Bob-authored refactor PR on DocRAG-MD (with /review + /create-pr) | 4 |
| | **Total Bob deliverables** | **~20** |
| | **Grand total (with confirmation + buffer)** | **~22 / 40** |

All sessions exported to [`docs/BOB_SESSIONS/`](docs/BOB_SESSIONS/). Full breakdown in [`BOB_USAGE_REPORT.md`](BOB_USAGE_REPORT.md).

## Repository structure

```
bobrag-md/
├── analysis-target/           ← VENDORED DocRAG-MD (read-only, what Bob analyzes)
│   ├── README.md
│   ├── src/                   ← original DocRAG-MD source files
│   ├── NOTICE.md              ← attribution + license note
│   └── ORIGINAL_LICENSE
│
├── src/bobrag/                ← Minimal working RAG (Ahmed, ~200 LOC)
├── src/codebase_mcp/          ← MCP server (Bob-built, exposes analysis-target/)
│
├── dashboard/                 ← Bobalytics Next.js app (Ahmed)
│
├── docs/                      ← Bob-generated documentation
│   ├── ARCHITECTURE.md
│   ├── CODE_MAP.md
│   ├── TECH_DEBT.md
│   ├── ONBOARDING.md
│   └── BOB_SESSIONS/          ← exported chat logs
│
└── BOB_USAGE_REPORT.md
```

## Quickstart

### System (Layer 1 — minimal working RAG)

```bash
git clone https://github.com/<you>/bobrag-md.git
cd bobrag-md

uv sync
docker compose up -d

cp .env.example .env       # fill in GEMINI_API_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY

uv run bobrag ingest                                  # ~30s
uv run bobrag query "What is metformin used for?"     # cited answer
uv run bobrag eval                                    # Ragas
uv run bobrag serve                                   # rag_mcp
```

### Dashboard (Bobalytics)

```bash
cd dashboard
npm install
cp ../.env .env.local

# Generate the data the dashboard reads
cd ..
uv run python scripts/parse_usage.py

cd dashboard
npm run dev
# Open http://localhost:3000
```

### Codebase MCP (Bob-built, exposing DocRAG-MD)

```bash
python -m src.codebase_mcp.server
# Then connect from Claude Desktop:
# Config: { "docrag-codebase": { "command": "python", "args": ["-m", "src.codebase_mcp.server"] } }
```

## Stack

| Layer | Choice |
|---|---|
| LLM | Gemini 2.5 Pro |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Retrieval (Layer 1) | Dense via Qdrant |
| MCP servers | FastMCP × 2 (rag_mcp + Bob-built codebase_mcp) |
| Observability | Langfuse |
| Evaluation | Ragas |
| Dashboard | Next.js 14, Tailwind, shadcn/ui, Recharts, React Flow |
| Analysis subject | DocRAG-MD (vendored in `analysis-target/`) |
| Build agent | **IBM Bob** |

## How Bob was used (the discipline)

Every Bob session followed these binding rules:

1. **Explicit `@/analysis-target/<file>` mentions** — Bob reads only what's named
2. **Cap of 7 files per session** — large codebase requires tight scoping
3. **Auto-approval OFF** — every action manually reviewed
4. **"Do not read other files" clause** in every prompt
5. **Token cost logged** before next session

Average Bobcoins per substantive deliverable: ~3.3. Total: ~22 / 40 (45% under budget on a 50+ file codebase).

## Why this approach beats "let Bob explore everything"

- **Token-efficient on a 50-file repo** — surgical scope vs naive exploration is the difference between 22 and 80+ Bobcoins
- **Honest** — judges can see exactly what Bob read for each output
- **Reproducible** — anyone can rerun a prompt with the same `@` mentions and get the same kind of output
- **Demoable** — every Bob output is screen-ready
- **Aligned with Bob's actual strength** — codebase intelligence on real complexity

## About the analysis subject (DocRAG-MD)

DocRAG-MD was built by:
- **Ahmed** (me)
- **Tahiana Andriambahoaka**
- **Oussama Rhouma**
- **Mohamed Khalil Ounis**
- **Mohamed Amar**

at Télécom Paris (Institut Polytechnique de Paris) as a Master's group project. It is vendored here read-only with attribution preserved (`analysis-target/NOTICE.md`). No changes flow back to the original DocRAG-MD repository.

The Bob-authored refactor in this submission lives in this repo's feature branch only.

## Author

**Ahmed** — AI Engineer, Advanced Master's in AI (Expert Data & MLOps), Télécom Paris.
Solo hackathon build, May 2026.

## License

MIT for everything I authored. `analysis-target/` retains its original DocRAG-MD license (see `analysis-target/ORIGINAL_LICENSE`).

## Acknowledgments

- **IBM Bob team** — for the agent that made this showcase possible
- **My DocRAG-MD teammates** — Tahiana, Oussama, Mohamed Khalil, Mohamed Amar — whose joint work is the analysis subject
- **lablab.ai** — for hosting the hackathon
