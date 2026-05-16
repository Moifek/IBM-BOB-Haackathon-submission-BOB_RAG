# AGENTS.md — BobRAG-MD

> **For Bob:** Read only what is explicitly mentioned via `@/path` in each prompt. Do not explore. Token discipline (40 Bobcoin hard limit) is the project's binding constraint. The analysis subject lives in `analysis-target/` — a vendored copy of the DocRAG-MD repo.

---

## 1. Identity

**Name:** BobRAG-MD + Bobalytics
**Tagline:** *Master's thesis-grade medical RAG, analyzed by IBM Bob as the codebase intelligence layer — in 22 Bobcoins.*
**Type:** IBM Bob Hackathon submission (May 15–17, 2026)
**License:** MIT (analysis outputs); `analysis-target/` retains its original DocRAG-MD license
**Owner:** Ahmed (solo)
**Bobcoin budget:** 40 HARD LIMIT, target ≤25 spent

## 2. The submission's three-layer structure

### Layer 0 — `analysis-target/` (vendored DocRAG-MD)
A read-only snapshot of my Master's thesis project: a multi-component medical RAG platform built by a team of 5 over 4 months at Télécom Paris. ~50 files across hybrid retrieval, LangGraph agents, FastMCP, Langfuse/Ragas. **This is what Bob analyzes.**

### Layer 1 — Minimal working RAG (`src/bobrag/`)
A simplified ~200-LOC medical RAG that Ahmed built solo as a working demo proof. Single retrieval path, Gemini, one MCP tool. Just enough to show "yes, this domain works."

### Layer 2 — Bob's analysis outputs (`docs/`, `src/codebase_mcp/`)
What Bob produced after analyzing DocRAG-MD: ARCHITECTURE.md, CODE_MAP.md, TECH_DEBT.md, ONBOARDING.md, a codebase_mcp server exposing DocRAG-MD as queryable tools, and one suggested refactor.

### Layer 3 — Bobalytics dashboard (`dashboard/`)
Next.js + Tailwind dashboard visualizing Bob's work: session timeline, Bobcoin gauge, RAG traces, Ragas radar, DocRAG-MD dependency graph.

## 3. The thesis (the pitch in one line)

> *"My Master's thesis took 5 people 4 months. For the IBM Bob hackathon, I gave it to Bob — under a 40-Bobcoin budget — and asked: be its intelligence layer."*

## 4. North Star Outcomes

### Ahmed-built
1. ✅ `analysis-target/` populated with DocRAG-MD source (read-only)
2. ✅ Working minimal RAG: `bobrag query` returns cited answers (Layer 1)
3. ✅ FastMCP `rag_mcp` exposed
4. ✅ Langfuse traces visible
5. ✅ Ragas eval on 5 questions
6. ✅ Bobalytics dashboard with 5 visualizations

### Bob-generated (~22 Bobcoins, target ≤25)
7. ✅ `docs/ARCHITECTURE.md` — DocRAG-MD architecture with mermaid
8. ✅ `docs/CODE_MAP.md` — DocRAG-MD function catalog
9. ✅ `docs/TECH_DEBT.md` — DocRAG-MD ranked findings
10. ✅ `docs/ONBOARDING.md` — DocRAG-MD onboarding guide
11. ✅ `src/codebase_mcp/server.py` — MCP tools over DocRAG-MD
12. ✅ One Bob-authored refactor PR on a DocRAG-MD file
13. ✅ 9 sessions exported to `docs/BOB_SESSIONS/`
14. ✅ `BOB_USAGE_REPORT.md` filled in

## 5. Architecture

### Layer 1 — Minimal RAG (drastically simplified vs DocRAG-MD)

```
[Query] → [Embed] → [Qdrant search] → [Gemini + cite] → [Response]
              ↓                              ↓
        [Langfuse trace]               [Langfuse trace]
```

One file: `src/bobrag/pipeline.py` (~150 LOC). No LangGraph, no CRAG, no BM25. Just a working demo.

### Layer 0 — DocRAG-MD (what Bob analyzes)

The original architecture in `analysis-target/`:
- Hybrid retrieval (PubMedBERT dense + BM25 sparse + RRF fusion)
- CRAG confidence gating
- LangGraph multi-agent state machine
- FastMCP server
- Langfuse instrumentation
- Ragas evaluation
- ~50+ Python files

This is what Bob will read and document.

## 6. Token discipline rules (BINDING)

Every Bob prompt:
1. Explicit `@/analysis-target/<path>` mentions for every DocRAG-MD file Bob reads
2. Cap at 5-7 files per session for large-codebase analysis
3. "Do not read other files in analysis-target/" clause in every prompt
4. Output specification (write to `docs/X.md` with exact sections)
5. Bobcoin target in mind (2-4 per session for analysis, 1 for utility)
6. Auto-approval OFF

**Why caps matter:** DocRAG-MD is ~50 files. A naive "explore the repo" prompt could read 30+ files = 10+ Bobcoins per session = budget blown. Discipline is non-negotiable.

## 7. Bob task catalog (9 sessions, ~21 Bobcoins)

| # | Task | Mode | Inputs (@analysis-target/...) | Output | Bobcoins |
|---|---|---|---|---|---|
| 1 | Context confirmation | Ask | AGENTS.md | (chat) | 1 |
| 2 | Architecture doc | Ask→Plan | README.md, main entrypoint, 2 core files | docs/ARCHITECTURE.md | 3 |
| 3 | Code map | Ask | 5 selected core source files | docs/CODE_MAP.md | 3 |
| 4 | Tech debt | docrag-auditor | 7-8 source files | docs/TECH_DEBT.md | 4 |
| 5 | Onboarding | Code | ARCHITECTURE.md, CODE_MAP.md, README.md | docs/ONBOARDING.md | 2 |
| 6 | codebase_mcp scaffold | docrag-auditor | 5 files | src/codebase_mcp/server.py | 4 |
| 7 | Refactor on one DocRAG file | Code | 1 specific source file + TECH_DEBT.md | modified file | 2 |
| 8 | /review on diff | built-in | git diff | review | 1 |
| 9 | /create-pr description | built-in | git diff | PR text | 1 |
| | **Subtotal** | | | | **21** |
| | **Reserve** | | | | **+4** |

Hard ceiling: 25 Bobcoins.

## 8. Hard scope boundaries

**IN scope:**
- Minimal working RAG (Layer 1, ~200 LOC, single-file pipeline)
- Bob analyzing 5-8 selected DocRAG-MD files per session
- Bobalytics dashboard with 5 visualizations
- One Bob-authored refactor on a DocRAG-MD file (committed in a feature branch within bobrag-md repo)
- All 4 Bob-generated documentation artifacts

**OUT of scope:**
- Bob reading the entire DocRAG-MD repo (token suicide)
- Modifying or pushing anything back to the original DocRAG-MD repo
- Rebuilding DocRAG-MD's hybrid retrieval / CRAG / multi-agent stack in Layer 1
- "Bob explores the repo" prompts
- Multi-tenant, auth, mobile, web UI beyond Bobalytics

## 9. Demo storyline (2-minute video)

**Visual: Bobalytics dashboard is the backdrop.**

1. **(0:00–0:15) Hook**
   *"This is DocRAG-MD — my Master's thesis. Four months, five people, fifty-plus files of medical RAG code. For the IBM Bob hackathon, I gave it to Bob, under a 40-Bobcoin budget, and asked: be the codebase intelligence layer."*
   [Show `analysis-target/src/` tree, then dashboard]

2. **(0:15–0:35) Walk the dashboard**
   - Session timeline scrolling 9 sessions
   - Bobcoin gauge 22/40 amber
   - Ragas radar
   - Codebase dependency graph of DocRAG-MD

3. **(0:35–0:55) Working layer proof**
   [Terminal] `bobrag query "What is metformin used for?"` → cited answer
   [Dashboard] new RAG trace appears

4. **(0:55–1:20) Bob's outputs**
   - `docs/ARCHITECTURE.md` mermaid renders
   - `docs/TECH_DEBT.md` 5 ranked findings
   - `docs/ONBOARDING.md` day-1 guide

5. **(1:20–1:40) Live codebase MCP**
   - Claude Desktop → codebase_mcp
   - *"What does the hybrid retriever do? Where is RRF computed?"* → live grounded answer

6. **(1:40–1:55) The PR**
   - Feature branch with Bob-authored DocRAG-MD refactor
   - `/review` + Bob PR description

7. **(1:55–2:00) Close**
   *"Twenty-two of forty Bobcoins. Six deliverables. Bob as intelligence layer."*

## 10. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Bob reads too many DocRAG-MD files | High | Critical | Cap 7 files/session, reject unauthorized reads |
| Token overrun | Medium | Critical | Hard stop at 30 Bobcoins |
| Bobalytics build >6h | Medium | Medium | Drop graph chart first, then radar |
| Demo machine breaks | Low | Critical | Record by H+30 |
| Live Langfuse rate-limited | Low | Low | Pre-cache 5 traces as static JSON |

## 11. Definition of done

- [ ] Public GitHub repo, MIT license, DocRAG-MD's original license preserved in `analysis-target/`
- [ ] README has demo video + dashboard screenshot
- [ ] `uv run bobrag query "..."` works on fresh clone
- [ ] `cd dashboard && npm install && npm run dev` works
- [ ] All 5 dashboard viz functional
- [ ] All 4 Bob-generated docs present
- [ ] codebase_mcp connects to Claude Desktop
- [ ] One Bob-authored PR visible in git log
- [ ] All 9 Bob sessions exported
- [ ] BOB_USAGE_REPORT.md shows ≤25 Bobcoins
- [ ] Demo video uploaded
- [ ] Submission posted on lablab.ai
