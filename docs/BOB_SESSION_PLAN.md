# Bob Session Plan - DocRAG-MD Analysis

## Core File Mapping (8 files identified)

These are the ONLY files Bob will read during analysis sessions. Token discipline requires explicit file selection.

| # | Category | File Path | Purpose |
|---|----------|-----------|---------|
| 1 | Entry | `analysis-target/main.py` | Application entrypoint |
| 2 | Retrieval | `analysis-target/retrieval/hybrid_retriever.py` | Dense + BM25 + RRF fusion |
| 3 | Retrieval | `analysis-target/retrieval/crag.py` | Confidence gating logic |
| 4 | Agents | `analysis-target/agents/orchestrator.py` | LangGraph state machine |
| 5 | Agents | `analysis-target/agents/rag_agent.py` | Core RAG agent |
| 6 | Generation | `analysis-target/generation/llm_router.py` | LLM selection/routing |
| 7 | Generation | `analysis-target/generation/generator.py` | Response generation |
| 8 | MCP | `analysis-target/mcp_servers/medical_search_server.py` | FastMCP server |

## Supporting Files (for specific sessions)

| File | Used In |
|------|---------|
| `analysis-target/README.md` | Session 2, 5 |
| `analysis-target/pyproject.toml` | Session 2 |
| `analysis-target/retrieval/context_assembler.py` | Session 3, 4 |
| `analysis-target/agents/tools.py` | Session 3, 4 |
| `analysis-target/generation/observability.py` | Session 4, 6 |

## Session Breakdown (9 sessions, ~21 Bobcoins target)

### Session 1: Context Confirmation (Ask mode, 1 Bobcoin)
**Input:** `AGENTS.md` only
**Prompt:**
```
@/home/ahmed/Bob_Hackaton_Project/files/IBM-BOB-Haackathon-submission-BOB_RAG/AGENTS.md

Read this file. In 4 bullets: (1) project, (2) analysis-target location,
(3) token budget, (4) the file-reading rule. Read nothing else.
```
**Output:** Chat confirmation
**Success:** Bob understands constraints, cost ≤1 Bobcoin

---

### Session 2: Architecture Documentation (Ask→Plan, 3 Bobcoins)
**Mode:** Start in Ask, switch to Plan for writing
**Input files (4 max):**
- `@analysis-target/README.md`
- `@analysis-target/main.py`
- `@analysis-target/agents/orchestrator.py`
- `@analysis-target/retrieval/hybrid_retriever.py`

**Prompt:**
```
@analysis-target/README.md
@analysis-target/main.py
@analysis-target/agents/orchestrator.py
@analysis-target/retrieval/hybrid_retriever.py

You are analyzing DocRAG-MD, a medical RAG system. Read ONLY these 4 files.
Do not read other files in analysis-target/.

Create docs/ARCHITECTURE.md with:
1. System Overview (2 paragraphs)
2. Component Architecture (mermaid diagram showing: ingestion → retrieval → CRAG → agents → generation)
3. Key Technologies (table: component, tech, purpose)
4. Data Flow (numbered steps from query to response)

Target: 400-600 words + diagram. Switch to Plan mode to write the file.
```
**Output:** `docs/ARCHITECTURE.md`
**Success:** Mermaid renders, all 4 sections present, cost ≤3 Bobcoins

---

### Session 3: Code Map (Ask, 3 Bobcoins)
**Input files (5 max):**
- `@analysis-target/retrieval/hybrid_retriever.py`
- `@analysis-target/retrieval/crag.py`
- `@analysis-target/agents/rag_agent.py`
- `@analysis-target/generation/generator.py`
- `@analysis-target/generation/llm_router.py`

**Prompt:**
```
@analysis-target/retrieval/hybrid_retriever.py
@analysis-target/retrieval/crag.py
@analysis-target/agents/rag_agent.py
@analysis-target/generation/generator.py
@analysis-target/generation/llm_router.py

Read ONLY these 5 files. Do not read other files in analysis-target/.

Create docs/CODE_MAP.md with a function-level catalog:
- File path
- Class/function name
- Purpose (1 line)
- Key parameters
- Return type

Format as markdown tables, grouped by file. Include ALL public functions/classes.
Switch to Plan mode to write.
```
**Output:** `docs/CODE_MAP.md`
**Success:** All 5 files cataloged, cost ≤3 Bobcoins

---

### Session 4: Tech Debt Analysis (docrag-auditor mode, 4 Bobcoins)
**Input files (7-8 max):**
- `@analysis-target/retrieval/hybrid_retriever.py`
- `@analysis-target/retrieval/crag.py`
- `@analysis-target/retrieval/context_assembler.py`
- `@analysis-target/agents/orchestrator.py`
- `@analysis-target/agents/rag_agent.py`
- `@analysis-target/generation/generator.py`
- `@analysis-target/generation/llm_router.py`
- `@analysis-target/mcp_servers/medical_search_server.py`

**Prompt:**
```
@analysis-target/retrieval/hybrid_retriever.py
@analysis-target/retrieval/crag.py
@analysis-target/retrieval/context_assembler.py
@analysis-target/agents/orchestrator.py
@analysis-target/agents/rag_agent.py
@analysis-target/generation/generator.py
@analysis-target/generation/llm_router.py
@analysis-target/mcp_servers/medical_search_server.py

Read ONLY these 8 files. Do not read other files in analysis-target/.

Audit for tech debt. Create docs/TECH_DEBT.md with:
1. Executive Summary (severity distribution)
2. Top 5 Findings (ranked by impact)
   - Title
   - Severity (Critical/High/Medium/Low)
   - File + line numbers
   - Description
   - Recommendation
   - Effort estimate
3. Quick Wins (3-5 low-effort improvements)

Use docrag-auditor mode. Switch to Plan to write.
```
**Output:** `docs/TECH_DEBT.md`
**Success:** 5 ranked findings with line refs, cost ≤4 Bobcoins

---

### Session 5: Onboarding Guide (Code mode, 2 Bobcoins)
**Input files:**
- `@docs/ARCHITECTURE.md` (Bob's output)
- `@docs/CODE_MAP.md` (Bob's output)
- `@analysis-target/README.md`

**Prompt:**
```
@docs/ARCHITECTURE.md
@docs/CODE_MAP.md
@analysis-target/README.md

Read these 3 files. Do not read other files in analysis-target/.

Create docs/ONBOARDING.md for a new developer joining the DocRAG-MD team:
1. Project Overview (what it does, why it exists)
2. Prerequisites (tools, accounts, knowledge)
3. Setup Steps (numbered, copy-pasteable commands)
4. Architecture Walkthrough (reference ARCHITECTURE.md)
5. First Tasks (3 starter issues for day 1)
6. Key Files to Read First (5 files from CODE_MAP.md)
7. Common Pitfalls (3-4 gotchas)

Target: 600-800 words. Use Code mode to write.
```
**Output:** `docs/ONBOARDING.md`
**Success:** All 7 sections, actionable, cost ≤2 Bobcoins

---

### Session 6: Codebase MCP Server (docrag-auditor, 4 Bobcoins)
**Input files (5 max):**
- `@analysis-target/retrieval/hybrid_retriever.py`
- `@analysis-target/agents/orchestrator.py`
- `@analysis-target/generation/generator.py`
- `@analysis-target/mcp_servers/medical_search_server.py`
- `@docs/CODE_MAP.md`

**Prompt:**
```
@analysis-target/retrieval/hybrid_retriever.py
@analysis-target/agents/orchestrator.py
@analysis-target/generation/generator.py
@analysis-target/mcp_servers/medical_search_server.py
@docs/CODE_MAP.md

Read ONLY these 5 files. Do not read other files in analysis-target/.

Create src/codebase_mcp/server.py - a FastMCP server exposing DocRAG-MD as queryable tools:

Tools to implement:
1. search_codebase(query: str) -> list of relevant functions from CODE_MAP
2. explain_component(component: str) -> architecture explanation
3. get_tech_debt(severity: str) -> filtered findings
4. trace_data_flow(start: str, end: str) -> step-by-step flow

Use FastMCP patterns from medical_search_server.py. Include:
- Proper imports
- Tool decorators
- Docstrings
- Error handling

Use docrag-auditor mode to analyze, Code mode to write.
```
**Output:** `src/codebase_mcp/server.py`
**Success:** 4 tools implemented, FastMCP compliant, cost ≤4 Bobcoins

---

### Session 7: Refactor (Code mode, 2 Bobcoins)
**Branch:** `refactor/docrag-improvement`
**Input files:**
- `@analysis-target/retrieval/crag.py` (or another file from TECH_DEBT top 5)
- `@docs/TECH_DEBT.md`

**Prompt:**
```
@analysis-target/retrieval/crag.py
@docs/TECH_DEBT.md

Read these 2 files. Do not read other files in analysis-target/.

Based on TECH_DEBT.md findings for crag.py, implement ONE improvement:
- Add type hints if missing
- Extract magic numbers to constants
- Add docstrings
- Improve error handling
- Simplify complex logic

Make the change directly to analysis-target/retrieval/crag.py.
Use Code mode. Commit with message: "refactor: Bob-authored improvement to CRAG module"
```
**Output:** Modified `analysis-target/retrieval/crag.py`
**Success:** One clear improvement, git diff clean, cost ≤2 Bobcoins

---

### Session 8: Review Diff (built-in /review, 1 Bobcoin)
**Input:** Git diff from Session 7

**Prompt:**
```
/review
```
**Output:** Review comments
**Success:** Bob provides review, cost ≤1 Bobcoin

---

### Session 9: PR Description (built-in /create-pr, 1 Bobcoin)
**Input:** Git diff from Session 7

**Prompt:**
```
/create-pr
```
**Output:** PR description text
**Success:** PR description generated, cost ≤1 Bobcoin

---

## Post-Session Checklist (after EACH session)

- [ ] Export session: Bob → ⋯ → Export Session → `docs/BOB_SESSIONS/0X-name.md`
- [ ] Log cost in `BOB_USAGE_REPORT.md`
- [ ] Run `uv run python scripts/parse_usage.py`
- [ ] Commit: `git add . && git commit -m "Session X: <output>" && git push`
- [ ] Verify cumulative cost ≤ target

## Bobcoin Budget Tracking

| Session | Target | Actual | Cumulative | Status |
|---------|--------|--------|------------|--------|
| 1 | 1 | ___ | ___ | ⬜ |
| 2 | 3 | ___ | ___ | ⬜ |
| 3 | 3 | ___ | ___ | ⬜ |
| 4 | 4 | ___ | ___ | ⬜ |
| 5 | 2 | ___ | ___ | ⬜ |
| 6 | 4 | ___ | ___ | ⬜ |
| 7 | 2 | ___ | ___ | ⬜ |
| 8 | 1 | ___ | ___ | ⬜ |
| 9 | 1 | ___ | ___ | ⬜ |
| **Total** | **21** | **___** | **___** | **Target ≤25** |

## Emergency Protocols

**If at any point cumulative cost > 20 Bobcoins:**
1. STOP immediately
2. Skip remaining sessions
3. Submit with completed artifacts only
4. Document in BOB_USAGE_REPORT.md

**If a session exceeds budget by 2× (e.g., Session 2 costs 6 instead of 3):**
1. Abort session
2. Simplify prompt (fewer files, shorter output)
3. Retry once
4. If still over, skip and move to next session

## Success Criteria

- [ ] All 9 sessions completed
- [ ] 4 documentation files in `docs/`
- [ ] 1 MCP server in `src/codebase_mcp/`
- [ ] 1 refactor PR merged
- [ ] Total cost ≤25 Bobcoins
- [ ] All sessions exported to `docs/BOB_SESSIONS/`
- [ ] BOB_USAGE_REPORT.md complete
