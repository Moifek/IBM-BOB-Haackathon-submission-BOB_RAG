# MASTER PLAYBOOK (Windows + DocRAG analysis edition)

> Read once end-to-end. Execute step by step. Check off each line.
> Total: ~36 hours · Bobcoin budget: 40 (target ≤25 spent) · OS: **Windows native**

---

## Phase overview

| Phase | Hours | Bobcoins | Output |
|---|---|---|---|
| 0. Pre-flight + DocRAG vendor | 0–3 | 0–1 | Bob set up, repo ready, DocRAG vendored |
| 1. Build minimal RAG | 3–10 | 0 | Working `bobrag query` |
| 2. Build Bobalytics | 10–16 | 0 | Dashboard with 5 viz |
| 3. Bob sessions | 16–24 | ~22 | 4 docs, codebase_mcp, refactor PR |
| 4. Polish + record | 24–32 | 0 | Demo video, screenshots, README |
| 5. Submit | 32–36 | 0 | Submitted, sleep |

---

# PHASE 0 — Pre-flight (0–3h) ⚙️

## 0.1 Prerequisites

Open **PowerShell** and run:

```powershell
node --version       # need v20+
python --version     # need 3.11+
git --version
docker --version
```

Install if missing:
- Node: https://nodejs.org (LTS)
- Python: https://python.org/downloads (3.11+, check "Add to PATH")
- Git: https://git-scm.com/download/win
- Docker Desktop: https://docker.com/products/docker-desktop

Install uv:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Close and reopen PowerShell. Verify: `uv --version`.

## 0.2 Bob ready
- [ ] Bob signed in
- [ ] Auto-approval DISABLED (bottom-right)
- [ ] Bobcoin balance: ___

## 0.3 Extract starter kit

Extract `bobrag-md-starter-kit-FINAL.zip` to `C:\Users\<you>\dev\bobrag-md`.

## 0.4 Vendor DocRAG-MD into analysis-target/

```powershell
cd C:\Users\<you>\dev
git clone https://github.com/<you>/docrag-md.git docrag-md-source
cd bobrag-md
mkdir analysis-target
xcopy /E /I /Y ..\docrag-md-source\src analysis-target\src
xcopy /Y ..\docrag-md-source\README.md analysis-target\
xcopy /Y ..\docrag-md-source\pyproject.toml analysis-target\ 2>$null
xcopy /Y ..\docrag-md-source\LICENSE analysis-target\ORIGINAL_LICENSE 2>$null
```

Add NOTICE:
```powershell
@"
# analysis-target/
Vendored snapshot of DocRAG-MD (Telecom Paris thesis project, team of 5).
Included read-only as Bob's analysis subject for the IBM Bob hackathon.
Original repo: https://github.com/<you>/docrag-md
"@ | Out-File -Encoding UTF8 analysis-target\NOTICE.md
```

Verify vendored size:
```powershell
(Get-ChildItem -Recurse analysis-target\src -Filter *.py).Count
```

If >60 .py files, prune notebooks/tests/data dumps.

## 0.5 GitHub repo

Create empty public `bobrag-md` repo on github.com.

```powershell
git init
git branch -M main
git add .
git commit -m "Initial scaffold with vendored DocRAG-MD analysis target"
git remote add origin https://github.com/<you>/bobrag-md.git
git push -u origin main
```

## 0.6 API keys + .env

```powershell
Copy-Item .env.example .env
notepad .env  # fill in GEMINI_API_KEY, LANGFUSE_*
```

## 0.7 Open in Bob

Bob → File → Open Folder → `C:\Users\<you>\dev\bobrag-md` → trust authors.

## 0.8 Declare docrag-auditor mode

In Bob chat:
1. ⋯ → Modes → + Create new mode
2. Name: `DocRAG Auditor`, Slug: `docrag-auditor`
3. Open `.bob/modes/docrag-auditor.md`, copy body, paste into Role Definition
4. Save

## 0.9 Smoke test

In Bob (`/ask`):

```
@/AGENTS.md

Read this file. In 4 bullets: (1) project, (2) analysis-target location,
(3) token budget, (4) the file-reading rule. Read nothing else.
```

- [ ] Bob responds correctly
- [ ] Bobcoin cost: ___ recorded in BOB_USAGE_REPORT.md
- [ ] Session exported → `docs/BOB_SESSIONS/00-smoke-test.md`
- [ ] Committed and pushed

✅ End Phase 0. ~1 Bobcoin. ~3h.

---

# PHASE 1 — Minimal RAG (3–10h) 🐍

Build a much smaller system this time: 5 Python files, ~200 LOC. Demo proof, not headline.

## 1.1 pyproject.toml

```powershell
@"
[project]
name = 'bobrag'
version = '0.1.0'
description = 'Minimal medical RAG + DocRAG-MD analysis via IBM Bob'
requires-python = '>=3.11'
dependencies = [
    'qdrant-client>=1.9',
    'sentence-transformers>=3.0',
    'google-generativeai>=0.7',
    'fastmcp>=0.2',
    'langfuse>=2.40',
    'ragas>=0.2',
    'pydantic>=2.7',
    'pydantic-settings>=2.3',
    'typer>=0.12',
    'python-dotenv>=1.0',
    'rich>=13.7',
    'pyyaml>=6.0',
    'datasets>=2.20',
]

[project.scripts]
bobrag = 'bobrag.cli:app'

[build-system]
requires = ['hatchling']
build-backend = 'hatchling.build'

[tool.hatch.build.targets.wheel]
packages = ['src/bobrag']
"@ | Out-File -Encoding UTF8 pyproject.toml

uv sync
```

## 1.2 Qdrant

```powershell
@"
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - 6333:6333
    volumes:
      - qdrant_data:/qdrant/storage
volumes:
  qdrant_data:
"@ | Out-File -Encoding UTF8 docker-compose.yml

docker compose up -d
```

## 1.3 Python files (~5h)

Write these 5 in order:

- `src/bobrag/__init__.py` — empty
- `src/bobrag/config.py` (~50 LOC) — pydantic settings
- `src/bobrag/pipeline.py` (~150 LOC) — ingest + search + generate + query (one file, simple functions)
- `src/bobrag/rag_mcp.py` (~50 LOC) — FastMCP with one tool `ask_medical`
- `src/bobrag/evaluation.py` (~80 LOC) — Ragas runner writing `eval/results/latest.json`
- `src/bobrag/cli.py` (~60 LOC) — Typer: ingest, query, eval, serve

## 1.4 Data (~1h)

10-15 medical .md abstracts in `data/corpus/`. 5 golden questions in `eval/golden_questions.yaml`.

## 1.5 Verify

```powershell
uv run bobrag ingest
uv run bobrag query "What is metformin used for?"
uv run bobrag eval
```

- [ ] All three work
- [ ] Langfuse shows traces

## 1.6 Commit

```powershell
git add .
git commit -m "Phase 1: minimal working RAG (Layer 1)"
git push
```

✅ End Phase 1. ~10h elapsed. 1 Bobcoin total.

---

# PHASE 2 — Bobalytics (10–16h) ⚛️

## 2.1 Scaffold Next.js

```powershell
cd C:\Users\<you>\dev\bobrag-md
npx create-next-app@latest dashboard --typescript --tailwind --app --no-src-dir --import-alias="@/*" --no-eslint
```

## 2.2 Install dashboard deps

```powershell
cd dashboard
npm install recharts react-flow-renderer langfuse lucide-react class-variance-authority clsx tailwind-merge "@radix-ui/react-slot"
```

## 2.3 Copy starter components

```powershell
cd ..
Copy-Item dashboard-starter\app\page.tsx dashboard\app\page.tsx -Force
Copy-Item dashboard-starter\app\layout.tsx dashboard\app\layout.tsx -Force
Copy-Item dashboard-starter\app\globals.css dashboard\app\globals.css -Force
mkdir dashboard\components -Force 2>$null
Copy-Item dashboard-starter\components\*.tsx dashboard\components\
mkdir dashboard\app\api\eval -Force 2>$null
mkdir dashboard\app\api\traces -Force 2>$null
mkdir dashboard\app\api\codebase -Force 2>$null
Copy-Item dashboard-starter\app\api\eval\route.ts dashboard\app\api\eval\
Copy-Item dashboard-starter\app\api\traces\route.ts dashboard\app\api\traces\
Copy-Item dashboard-starter\app\api\codebase\route.ts dashboard\app\api\codebase\
```

## 2.4 CRITICAL Windows fix in codebase API

Edit `dashboard\app\api\codebase\route.ts`. Two changes:

**A)** Replace `python3` with `python`, fix quote escaping:

```ts
// OLD: const { stdout } = await execAsync(`python3 -c '${py.replace(/'/g, "'\\''")}'`, {
// NEW:
const escaped = py.replace(/"/g, '\\"').replace(/\n/g, ' ');
const { stdout } = await execAsync(`python -c "${escaped}"`, {
```

**B)** Point at DocRAG-MD source, not BobRAG-MD:

```ts
// OLD: root = Path("${repoRoot.replace(/\\/g, '/')}/src/bobrag")
// NEW:
root = Path("${repoRoot.replace(/\\/g, '/')}/analysis-target/src")
```

This makes the codebase graph visualize DocRAG-MD's modules — the actual subject of analysis.

## 2.5 Dashboard env

```powershell
Copy-Item .env dashboard\.env.local
```

## 2.6 Parse usage script

Create `scripts\parse_usage.py` (see full content in the starter kit).

Run it:
```powershell
uv run python scripts\parse_usage.py
```

## 2.7 Run dashboard

```powershell
cd dashboard
npm run dev
```

Open http://localhost:3000. All 5 viz should render.

## 2.8 Commit

```powershell
cd ..
git add .
git commit -m "Phase 2: Bobalytics dashboard"
git push
```

✅ End Phase 2. ~16h elapsed.

---

# PHASE 3 — Bob sessions on DocRAG-MD (16–24h) 🤖

## Pre-session file selection (do this once before Session 2)

Open `analysis-target/src/` in Bob's file explorer. Identify these specific files and write the paths down:

```
[ ] Main entrypoint / __init__:     analysis-target/src/_____________
[ ] Retrieval module:                analysis-target/src/_____________
[ ] Agents / orchestration:          analysis-target/src/_____________
[ ] MCP server:                      analysis-target/src/_____________
[ ] Evaluation module:               analysis-target/src/_____________
[ ] Config/settings:                 analysis-target/src/_____________
[ ] LLM wrapper:                     analysis-target/src/_____________
[ ] CRAG / gating logic:             analysis-target/src/_____________
```

These are the **only files** you'll mention in prompts. Bob will never see other DocRAG-MD files.

## Per-session ritual

Before: clean git, correct mode, auto-approval OFF, BOB_USAGE_REPORT.md open.
During: reject any unauthorized file read approval.
After: export session, log cost, run `parse_usage.py`, commit.

## Sessions 1-9

Refer to `docs/BOB_PROMPTS.md` for exact prompt text. **Update the `@` paths to your DocRAG-MD file paths** identified above.

| # | Time | Mode | Budget | Actual |
|---|---|---|---|---|
| 1 | 15m | /ask | 1 | ___ |
| 2 | 45m | /ask → /plan | 3 | ___ |
| 3 | 40m | /ask | 3 | ___ |
| 4 | 60m | /docrag-auditor | 4 | ___ |
| 5 | 30m | /code | 2 | ___ |
| 6 | 75m | /docrag-auditor | 4 | ___ |
| 7 | 45m | /code | 2 | ___ |
| 8 | 15m | /review | 1 | ___ |
| 9 | 20m | /create-pr | 1 | ___ |

## Session 7 special: Bob refactors a DocRAG file

```powershell
git checkout -b refactor/docrag-improvement
```

After Bob makes the change:
```powershell
git diff analysis-target\
git add analysis-target\
git commit -m "refactor: Bob-authored improvement to DocRAG-MD module"
```

After Sessions 8 + 9:
```powershell
git push -u origin refactor/docrag-improvement
```

Create PR on GitHub, paste Bob's description, merge.

```powershell
git checkout main
git pull
```

**Important:** This is on YOUR bobrag-md repo's vendored copy, not the original DocRAG-MD repo. No effect on your team's project.

✅ End Phase 3. ~22 Bobcoins. ~24h.

---

# PHASE 4 — Polish + record (24–32h) 🎬

## 4.1 Refresh dashboard

```powershell
uv run python scripts\parse_usage.py
cd dashboard; npm run dev
```

## 4.2 Screenshots (~45m)

To `docs/screenshots/`:
- dashboard-overview.png
- analysis-target-tree.png
- architecture-mermaid.png (rendered on GitHub)
- tech-debt.png
- claude-mcp.png
- pr-merged.png

## 4.3 Demo prep + record (~2.5h)

Reset state, rehearse 3 times timed.

Use **OBS Studio** (https://obsproject.com) or **Loom**.

Hook (memorize):
> *"This is DocRAG-MD — my Master's thesis. Four months, five people, fifty-plus files of medical RAG code. For the IBM Bob hackathon, I gave it to Bob — under a 40-Bobcoin budget — and asked: be the codebase intelligence layer."*

Then dashboard tour → working RAG → Bob's docs → MCP → PR → close.

Target: 2:00, max 2:30.

Upload to YouTube unlisted or Loom. Note URL.

## 4.4 Pitch deck (~1h)

8 slides PowerPoint → export PDF → `docs/PITCH_DECK.pdf`.

## 4.5 Update README

Replace `[▶ Demo video](#)` with your URL. Add screenshots.

## 4.6 Commit

```powershell
git add .
git commit -m "Phase 4: screenshots, video, deck, polish"
git push
```

---

# PHASE 5 — Submit (32–36h) ✅

## 5.1 Fresh-clone test

```powershell
cd C:\temp
Remove-Item -Recurse -Force bobrag-test -ErrorAction SilentlyContinue
git clone https://github.com/<you>/bobrag-md.git bobrag-test
cd bobrag-test
Copy-Item C:\Users\<you>\dev\bobrag-md\.env .
uv sync
docker compose up -d
Start-Sleep 5
uv run bobrag ingest
uv run bobrag query "test"
cd dashboard; npm install; npm run dev
```

Both must work.

## 5.2 Submit

On lablab.ai dashboard:
- Name, tagline, track, GitHub URL, video URL, tech stack, Bobcoins used
- Submit, screenshot confirmation.

## 5.3 Sleep.

---

# Panic protocols

| At H+24 if... | Triage |
|---|---|
| Bobcoins >30 | Stop, submit what you have |
| Dashboard incomplete | Screenshots in README, drop "live" |
| Session 6 incomplete | Skip MCP demo in video |
| Demo not recorded | Loom raw, no edit |
| Layer 1 RAG broken | Frame submission as pure analysis |

Submit imperfect > don't submit.

---

# Quick reference

```powershell
# System
cd C:\Users\<you>\dev\bobrag-md
uv sync
docker compose up -d
uv run bobrag ingest
uv run bobrag query "..."
uv run bobrag eval
uv run bobrag serve

# Dashboard
cd dashboard
npm install
npm run dev

# Bob report parser
uv run python scripts\parse_usage.py

# Git
git add . ; git commit -m "..." ; git push
```
