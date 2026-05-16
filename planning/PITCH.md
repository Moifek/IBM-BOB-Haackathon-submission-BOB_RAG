# BobRAG-MD — Pitch

## The provocative claim

**Bob can be the intelligence layer for a complex, real codebase in 22 Bobcoins.**

Not "Bob wrote my whole project." That's overclaim. The interesting answer is more honest: pair an experienced engineer with disciplined Bob usage on a real, complex codebase — and watch what falls out.

## What I built

For this hackathon I vendored my Master's thesis project — **DocRAG-MD**, a multi-component medical RAG platform built by 5 people over 4 months at Télécom Paris — into the submission repo as a read-only `analysis-target/`. Then I gave it to IBM Bob, under a 40-Bobcoin hard budget, and asked Bob to be its codebase intelligence layer.

In nine sessions, Bob produced six artifacts on the DocRAG-MD codebase:

| Artifact | Bobcoins |
|---|---|
| `ARCHITECTURE.md` with mermaid diagram | 3 |
| `CODE_MAP.md` (function-level catalog) | 3 |
| `TECH_DEBT.md` (5 ranked findings, line-referenced) | 4 |
| `ONBOARDING.md` (day-1 developer guide) | 2 |
| `codebase_mcp/server.py` (FastMCP server exposing DocRAG-MD as queryable tools) | 4 |
| Bob-authored refactor PR (with /review + /create-pr) | 4 |
| **Total** | **~20 Bobcoins** |

Final spend (including buffer): **~22 / 40**. Forty-five percent under budget on a ~50-file codebase.

Alongside Bob's analysis, I built two things solo:
1. A **minimal working RAG** (~200 LOC) — proof the domain works end-to-end
2. **Bobalytics** — a Next.js dashboard with five visualizations of Bob's work: session timeline, Bobcoin gauge, RAG traces, Ragas evaluation radar, DocRAG-MD dependency graph

## Why this submission wins on every criterion

### Application of Tech (Bob usage)

Every Bob feature, used substantively:
- All four core modes (Ask, Plan, Code, custom)
- AGENTS.md as persistent project context, binding all sessions
- Custom mode (`docrag-auditor`) authored and active during analysis sessions
- `/review` and `/create-pr` integrated into the git workflow
- `read_file`, `search_files`, `list_code_definition_names` used surgically — never as exploration
- Every session exported, every Bobcoin logged

The submission can prove every claim. Open `docs/BOB_SESSIONS/` and follow along.

### Originality

Three things together are unique to this submission:

1. **Bob analyzing a vendored real codebase, not a toy** — most submissions will use Bob on hackathon-fresh code. I gave it real, multi-author, multi-component complexity.
2. **Token discipline as a first-class feature** — most submissions have no explicit Bobcoin budget. Mine has a hard limit, a log, and a dashboard visualizing it.
3. **Bobalytics framing** — "dashboard to monitor my AI worker the way enterprises monitor remote workers" is a memorable inversion that fits the hackathon's enterprise tone.

### Business Value

The submission directly answers the three questions enterprise dev leads are asking right now:

- *"Can we get teams productive on legacy / unfamiliar codebases without long onboarding?"*
  → Bob produces complete onboarding documentation in 2 Bobcoins. New-hire ramp-up compressed from weeks to hours.

- *"How do we control AI spend on coding assistants?"*
  → Surgical, scoped prompting cuts costs ~5× vs unbounded sessions. The discipline is the product.

- *"How do we trust AI to touch production code?"*
  → Manual approval workflow, exported session logs, `/review` before every change, Bob-authored PR descriptions. Fully auditable.

### Presentation

Built around discrete Bob-produced artifacts, each screen-ready:
- Architecture mermaid diagram (renders on GitHub)
- Tech debt findings (ranked table)
- Onboarding guide (structured doc)
- Working MCP server (demoable via Claude Desktop)
- A real merged git PR (real evidence of agentic dev)
- Bobalytics dashboard (visual backdrop for the entire 2-min demo)

## The hidden discipline

Three behaviors made this work at scale:

**Surgical file selection.** Before each Bob session, I manually identified which 5–7 specific files Bob would read. Bob never picked files on its own. Without this, a 50-file codebase would burn 80+ Bobcoins instead of 22.

**Explicit "do not" clauses.** Every prompt included some variant of *"Do not read other files in analysis-target/."* This single line saved an estimated 10–15 Bobcoins.

**One artifact per session.** No "while you're at it" outputs. When the named output was complete, the session ended.

These three behaviors are the playbook any enterprise team can copy on day one with Bob.

## The honest caveats

- **Single developer, focused domain.** I built DocRAG-MD originally; the domain isn't unfamiliar to me. Bob's leverage may differ for engineers genuinely new to the codebase.
- **Vendored, not live integration.** Bob analyzed a copy, not the live DocRAG-MD repo. Real-world Bob usage on enterprise repos involves more access-control complexity than this submission models.
- **Single refactor PR.** Bob authored one PR for the demo. A larger production engagement would surface dozens; the methodology generalizes, the scale isn't proven here.

What this submission **doesn't** claim:
- That Bob replaces senior engineers
- That every Bob session is cheap (only disciplined ones)
- That this scales to repos with hundreds of files without further scoping infrastructure

## What I'd build next

- **`bob-budget` CLI** — programmatic enforcement of per-session Bobcoin limits
- **Reusable "Codebase Auditor Kit"** — package the AGENTS.md, docrag-auditor mode, prompt templates, and Bobalytics dashboard for any team to use Bob this way on their own repo
- **Quality evaluation for Bob-generated docs** — a framework that scores Bob-produced documentation against expert-written baselines

## The ask

Score this submission against the four criteria:

- **Application of Tech:** every Bob mode used substantively on real complexity, custom mode authored, AGENTS.md binding, full session export
- **Originality:** Bob-on-vendored-real-codebase + token discipline + Bobalytics dashboard inversion = unique combination
- **Business Value:** direct answers to three enterprise questions about agentic dev
- **Presentation:** dashboard backdrop, demoable artifacts, reproducible from README

Thank you for reading.

— Ahmed
