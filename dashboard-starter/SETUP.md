# Bobalytics Dashboard Setup

This folder contains starter components for the Next.js dashboard. Drop these into your `dashboard/` directory after running `create-next-app`.

## Quick setup (15 min)

From repo root:

```bash
# 1. Scaffold Next.js
npx create-next-app@latest dashboard --typescript --tailwind --app --no-src-dir --import-alias="@/*" --no-eslint

# 2. Install runtime deps
cd dashboard
npm install recharts react-flow-renderer langfuse lucide-react class-variance-authority clsx tailwind-merge @radix-ui/react-slot

# 3. Copy these starter files in:
#    - components/SessionTimeline.tsx
#    - components/BobcoinGauge.tsx
#    - components/RagasRadar.tsx
#    - components/RagTraces.tsx
#    - components/CodebaseGraph.tsx
#    - app/page.tsx (overwrite the default)
#    - app/layout.tsx (overwrite)
#    - app/globals.css (overwrite)
#    - app/api/traces/route.ts
#    - app/api/eval/route.ts
#    - app/api/codebase/route.ts

# 4. Create the data directory and parse Bob's usage report
mkdir -p public/data
cd ..
uv run python scripts/parse_usage.py
# (parse_usage.py writes to dashboard/public/data/bob_sessions.json)

# 5. Create .env.local in dashboard/
cp ../.env dashboard/.env.local
# Make sure LANGFUSE_* are present

# 6. Run
cd dashboard
npm run dev
# Open http://localhost:3000
```

## File-by-file purpose

| File | What it does | Data source |
|---|---|---|
| `components/SessionTimeline.tsx` | Bar chart of Bob sessions, color by mode | `/data/bob_sessions.json` |
| `components/BobcoinGauge.tsx` | Radial gauge, total spent vs 40 | `/data/bob_sessions.json` |
| `components/RagasRadar.tsx` | 4-axis radar of eval metrics | `/api/eval` → `eval/results/latest.json` |
| `components/RagTraces.tsx` | Line chart, retrieval/gen/total latency | `/api/traces` → Langfuse API |
| `components/CodebaseGraph.tsx` | Dependency network | `/api/codebase` → Python AST |
| `app/page.tsx` | Overview grid composing all 5 | — |
| `app/layout.tsx` | Sets dark theme | — |
| `app/globals.css` | IBM-indigo dark palette | — |

## Watch out for

- **`public/data/bob_sessions.json` must exist** before the dashboard loads. Run `scripts/parse_usage.py` first.
- **Langfuse env vars** must be set in `dashboard/.env.local` (not just the parent `.env`).
- **Python must be on PATH** for `/api/codebase` (uses `python3 -c '...'`).
- **React Flow** requires the explicit `react-flow-renderer` package (not the newer `@xyflow/react`). The starter uses v10 syntax.
- **Recharts v2** is correct. Don't upgrade to v3 (breaking API changes).

## If you run out of time

Drop in this priority order:
1. SessionTimeline (5 min, no external deps)
2. BobcoinGauge (5 min, no external deps)
3. RagasRadar (10 min, needs eval JSON)
4. RagTraces (15 min, needs Langfuse)
5. CodebaseGraph (15 min, most complex)

The first two alone are demo-grade with static data.
