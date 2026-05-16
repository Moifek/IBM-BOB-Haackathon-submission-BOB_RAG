# SUBMISSION CHECKLIST — BobRAG-MD (DocRAG Analysis Edition)

**Deadline:** May 17, 2026.
**Budget:** 40 Bobcoins HARD, target ≤25 spent.

---

## 🔴 Critical (without these you fail)

- [ ] Public GitHub repo, MIT license (with NOTICE.md in analysis-target/)
- [ ] README with demo video link + dashboard screenshot
- [ ] AGENTS.md at root
- [ ] `analysis-target/` populated with vendored DocRAG-MD source
- [ ] `uv run bobrag query "..."` works on fresh clone
- [ ] At least 3 dashboard visualizations functional
- [ ] At least 3 of 4 Bob-generated docs present (analyzing DocRAG-MD)
- [ ] BOB_USAGE_REPORT.md populated (≤30 Bobcoins)
- [ ] At least 5 Bob sessions exported
also need the app to be deployed
- [ ] Demo video uploaded and linked (2-3 min)
- [ ] Submission posted on lablab.ai

## 🟡 Strong differentiators

- [ ] All 5 dashboard visualizations
- [ ] All 4 Bob-generated docs (Architecture, Code Map, Tech Debt, Onboarding)
- [ ] `src/codebase_mcp/server.py` runs, exposes DocRAG-MD, connects to Claude Desktop
- [ ] Bob-authored refactor PR on a DocRAG-MD file (visible in git history)
- [ ] Custom `docrag-auditor` mode declared in Bob and used
- [ ] Mermaid diagram in ARCHITECTURE.md renders on GitHub
- [ ] Bobalytics shows real data (not placeholders)
- [ ] All 9 Bob sessions exported
- [ ] Langfuse dashboard URL or screenshots in README

## 🟢 Polish

- [ ] Pitch deck PDF in `docs/`
- [ ] All screenshots in `docs/screenshots/`
- [ ] LinkedIn post drafted
- [ ] Bobcoin overlay in demo video
- [ ] Dashboard deployed to Vercel

---

## ⏰ Hour gates

| Hour | Gate | If failed → |
|---|---|---|
| H+3 | Pre-flight done, DocRAG vendored, Bob signed in | Skip Phase 1 simplifications, focus on basics |
| H+10 | Minimal RAG works end-to-end | Drop Layer 1, frame submission as pure analysis |
| H+16 | Dashboard runs with 3+ viz | Static screenshots in README |
| H+24 | All Bob sessions complete (~22 Bobcoins) | Stop using Bob, submit current state |
| H+30 | Demo recorded | Upload raw recording (Loom 5min free tier) |
| H+34 | Fresh-clone test passed | Hot-fix and re-push |
| H+35 | Submitted | — |
| H+36 | Sleep | — |

---

## 🚨 Panic protocols

| If at H+24 | Triage |
|---|---|
| Bobcoins >30 | Stop, submit what you have |
| Dashboard <3 viz | Static screenshots only |
| Bob session 6 (codebase_mcp) failed | Skip MCP demo, keep other 5 deliverables |
| Sessions 7-9 (PR) failed | Document why: "exercised early-stop discipline at X Bobcoins" |
| Demo video not edited | Loom raw upload, no edit |
| Live Ragas in demo fails | Pre-record fallback, embed |

**Hard rule:** 80% complete submission > 100% complete non-submission.

---

## Submission form fields

- **Name:** BobRAG-MD + Bobalytics
- **Tagline:** Master's thesis-grade medical RAG, analyzed by IBM Bob as the codebase intelligence layer — in 22 Bobcoins.
- **Track:** Agentic Development
- **GitHub:** https://github.com/<you>/bobrag-md
- **Demo video:** [YouTube/Loom URL]
- **Tech stack:** IBM Bob, Gemini 2.5 Pro, FastMCP, Qdrant, Langfuse, Ragas, Next.js 14, Tailwind, Recharts, React Flow, Python, TypeScript
- **Bobcoins used:** ___ / 40
- **Team:** Solo (Ahmed)

---

Print this. Tape it to your monitor.
