# Bob Prompts — DocRAG-MD Analysis Edition

> Token budget: 40 Bobcoins HARD. Target ≤25 spent. Every prompt is pre-scoped with explicit file mentions.

**Before using these prompts:** open `analysis-target/src/` and write down the actual file paths for each DocRAG-MD component. Replace the placeholders `<DOCRAG_X>` below with your real paths.

| Placeholder | Your actual path |
|---|---|
| `<DOCRAG_README>` | `analysis-target/README.md` |
| `<DOCRAG_ENTRY>` | `analysis-target/src/____________` |
| `<DOCRAG_RETRIEVAL>` | `analysis-target/src/____________` |
| `<DOCRAG_AGENTS>` | `analysis-target/src/____________` |
| `<DOCRAG_MCP>` | `analysis-target/src/____________` |
| `<DOCRAG_EVAL>` | `analysis-target/src/____________` |
| `<DOCRAG_CONFIG>` | `analysis-target/src/____________` |
| `<DOCRAG_LLM>` | `analysis-target/src/____________` |

---

## Session 1 — Context confirmation (FREE)

**Mode:** `/ask`

```
@/AGENTS.md

Read this file. In 4 bullets confirm:
1. What's the project
2. Where analysis-target/ lives and what it contains
3. Your hard token budget
4. Your most important constraint about file reads

Do not read any other file.
```

**Target:** 1 Bobcoin. **Export as:** `01-context.md`

---

## Session 2 — DocRAG-MD Architecture (with mermaid)

**Mode:** `/ask` then `/plan`

```
@/AGENTS.md
@<DOCRAG_README>
@<DOCRAG_ENTRY>
@<DOCRAG_RETRIEVAL>
@<DOCRAG_AGENTS>

Produce a single file: `docs/ARCHITECTURE.md`.

This documents the system in `analysis-target/` (DocRAG-MD).

Exact sections, in order:

1. ## Overview (3 sentences — what DocRAG-MD does)
2. ## Component Diagram (mermaid `flowchart LR` showing the major
   pipeline: query → hybrid retrieval → CRAG gate → LangGraph agents →
   generator → response. Use rounded rectangles for components,
   diamonds for decision points. Valid mermaid that renders on GitHub.)
3. ## Components (markdown table: Component | File | Responsibility | Key Functions)
4. ## Data Flow (5-step numbered list for an end-to-end query)
5. ## Notes (state any gaps — files you would have wanted to read but
   weren't authorized to)

Constraints:
- Read ONLY the 5 files mentioned above
- Do not read other files in analysis-target/
- Do not write any file other than docs/ARCHITECTURE.md
- The mermaid must use valid syntax that renders on GitHub
```

**Target:** 3 Bobcoins. **Export as:** `02-architecture.md`

---

## Session 3 — Code Map (DocRAG-MD functions)

**Mode:** `/ask`

```
@<DOCRAG_RETRIEVAL>
@<DOCRAG_AGENTS>
@<DOCRAG_MCP>
@<DOCRAG_EVAL>
@<DOCRAG_LLM>

Produce a single file: `docs/CODE_MAP.md`.

For each of the 5 files above, produce a section:

## `<filename>`

| Symbol | Type | Signature | Purpose (1 sentence) |
|---|---|---|---|

Use `list_code_definition_names` and `read_file` on the named files only.
List every public class, function, method. Skip private (prefixed `_`).

After the 5 sections, add:

## Dependency Map

Bullet list: which file imports from which (among the 5 named).

Constraints:
- Read only the 5 files mentioned
- Do not write any file other than docs/CODE_MAP.md
- Do not infer beyond what's in the code
- Do not read other DocRAG-MD files
```

**Target:** 3 Bobcoins. **Export as:** `03-code-map.md`

---

## Session 4 — Technical Debt Analysis

**Mode:** `/docrag-auditor`

```
@<DOCRAG_RETRIEVAL>
@<DOCRAG_AGENTS>
@<DOCRAG_MCP>
@<DOCRAG_EVAL>
@<DOCRAG_LLM>
@<DOCRAG_CONFIG>

Produce a single file: `docs/TECH_DEBT.md`.

Find between 4 and 6 technical debt items in the files above. For each:

## Finding N: <short title>
**Severity:** Low | Medium | High
**File(s):** `path:line_start-line_end`
**Issue:** (2 sentences)
**Suggested fix:** (2 sentences)
**Effort:** Small (<30 min) | Medium (1-2h) | Large (>2h)

Order: high-severity small-effort first.

At the bottom:

## Summary Table

Markdown table: # | Title | Severity | Effort | File

Constraints:
- Read only the 6 files mentioned
- Do not propose architectural rewrites (that's not debt)
- Each finding must cite specific line numbers
- Do not read other DocRAG-MD files
- Do not write any file other than docs/TECH_DEBT.md
```

**Target:** 4 Bobcoins. **Export as:** `04-tech-debt.md`

---

## Session 5 — Onboarding Guide

**Mode:** `/code`

```
@/docs/ARCHITECTURE.md
@/docs/CODE_MAP.md
@<DOCRAG_README>

Produce a single file: `docs/ONBOARDING.md`.

Audience: a new developer joining the DocRAG-MD team on day 1.
Strong Python skills, zero project context.

Structure:

# Onboarding: DocRAG-MD

## Day 1 (30 min read)
1. Read these files in order: `<file>` because `<reason>` ...
2. The mental model in one paragraph
3. The critical 20% of files (3-5 files max)

## Day 1 (1h hands-on)
Five hands-on tasks. Each = one command + expected output.

## When you're stuck
3 bullets: where to look, who to ask, common pitfalls.

Constraints:
- Read only the 3 files mentioned (the other Bob-generated docs + DocRAG README)
- Do not read source files directly
- Total under 250 lines
- No marketing language
```

**Target:** 2 Bobcoins. **Export as:** `05-onboarding.md`

---

## Session 6 — Scaffold codebase_mcp Server (THE SHOWCASE ARTIFACT)

**Mode:** `/docrag-auditor`

```
@/AGENTS.md
@/docs/CODE_MAP.md
@<DOCRAG_RETRIEVAL>
@<DOCRAG_AGENTS>
@<DOCRAG_MCP>

Create a new file: `src/codebase_mcp/server.py`.

This is a FastMCP server that exposes the DocRAG-MD codebase
(in analysis-target/) as queryable tools. Let external MCP clients
(Claude Desktop) ask questions about the DocRAG-MD structure.

Implement exactly these three tools:

1. `find_function(name: str) -> dict`
   - Searches analysis-target/src/ for the function/class named
   - Returns: file path (relative to analysis-target/), signature,
     docstring, line range
   - Returns error dict if not found

2. `explain_module(path: str) -> dict`
   - path is relative to analysis-target/, e.g. "src/retrieval/dense.py"
   - Returns: module docstring, public symbols list, imports
   - Uses Python `ast` module ONLY — no LLM calls
   - Returns error dict if path doesn't exist

3. `list_dependencies(path: str) -> dict`
   - Returns: imports grouped into stdlib / third-party / local
   - Uses `ast`

Requirements:
- FastMCP server registered with name "docrag-codebase"
- Each tool: async, ctx: Context as first parameter
- Use Python's `ast` module only (no extra deps)
- Type hints everywhere
- Google-style docstrings
- Module logger via logging.getLogger(__name__)
- `if __name__ == "__main__":` block running on stdio
- Hardcode the analysis_target root as "analysis-target/" (relative path)
- Max 220 lines

Also create `src/codebase_mcp/__init__.py` (empty).

Constraints:
- Read only the 5 files mentioned
- Write only the two new files
- Do not modify any existing file
- Do not add new pyproject.toml deps (confirm if needed)
```

**Target:** 4 Bobcoins. **Export as:** `06-codebase-mcp.md`

---

## Session 7 — One Targeted Refactor on a DocRAG-MD File

**Mode:** `/code`

**Prerequisite:** Pick the easiest "Small effort, High severity" finding from `docs/TECH_DEBT.md`. Replace `<DOCRAG_REFACTOR_FILE>` with that file's path. Replace `<N>` with the finding number.

**Pre-step:**
```powershell
git checkout -b refactor/docrag-improvement
```

```
@<DOCRAG_REFACTOR_FILE>
@/docs/TECH_DEBT.md

Apply the refactor described in `docs/TECH_DEBT.md` finding #<N>: <title>.

Modify only `<DOCRAG_REFACTOR_FILE>`.

After:
- All public function signatures used by other modules remain identical
- Add brief docstring to any new function
- Diff must be 20-70 lines, no more

After applying, report on:
- Whether the change preserves existing behavior
- What tests would need to pass to confirm
- Any risks

Constraints:
- Read only the 2 files mentioned
- Modify only <DOCRAG_REFACTOR_FILE>
- Do not change tests
- Do not modify other DocRAG-MD files
```

**Target:** 2 Bobcoins. **Export as:** `07-refactor.md`

After:
```powershell
git diff analysis-target\
git add analysis-target\
git commit -m "refactor: Bob-authored improvement to DocRAG-MD module"
```

---

## Session 8 — /review

**Mode:** built-in `/review`

```
/review
```

Bob reviews the uncommitted diff (or last commit). Approve git operations.

**Target:** 1 Bobcoin. **Export as:** `08-review.md`

---

## Session 9 — /create-pr

**Pre-step:**
```powershell
git push -u origin refactor/docrag-improvement
```

**Mode:** built-in `/create-pr`

```
/create-pr
```

Bob generates title + description. Copy, paste into PR on GitHub, merge.

**Target:** 1 Bobcoin. **Export as:** `09-pr-description.md`

After merging:
```powershell
git checkout main
git pull
```

---

## Sessions 10+ Reserve

Only if something failed. Hard stop at 35 Bobcoins.

---

## Per-session checklist

Before each session:
- [ ] Right mode selected
- [ ] All `@` mentions specified (and paths exist)
- [ ] Output target specified
- [ ] "Do not read other files" clause included
- [ ] Bobcoin target in mind
- [ ] Auto-approval OFF

After each session:
- [ ] Reviewed every action Bob approved
- [ ] Output is what was requested
- [ ] Session exported to docs/BOB_SESSIONS/
- [ ] Bobcoin cost logged in BOB_USAGE_REPORT.md
- [ ] Ran `uv run python scripts\parse_usage.py`
- [ ] Committed

---

## Running tally template

| # | Topic | Budget | Actual | Running |
|---|---|---|---|---|
| 0 | Smoke test | 1 | ___ | ___ |
| 1 | Context | 1 | ___ | ___ |
| 2 | Architecture | 3 | ___ | ___ |
| 3 | Code Map | 3 | ___ | ___ |
| 4 | Tech Debt | 4 | ___ | ___ |
| 5 | Onboarding | 2 | ___ | ___ |
| 6 | codebase_mcp | 4 | ___ | ___ |
| 7 | Refactor | 2 | ___ | ___ |
| 8 | /review | 1 | ___ | ___ |
| 9 | /create-pr | 1 | ___ | ___ |
| | **Total target: ≤22** | | | |

If running total ever exceeds 28 before Session 7 → **stop and reassess**.
