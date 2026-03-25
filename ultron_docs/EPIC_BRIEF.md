# ULTRON v3 — EPIC BRIEF
**Status:** Active  
**Author:** Ghost (Chemical Engineering Student, SVNIT Surat)  
**Version:** 3.0  
**Date:** March 2026  
**Classification:** Experimental Research Project — Non-Commercial

---

## Summary

Ultron v3 is the most advanced personal autonomous AI agent system ever designed by a single student researcher. It is a 24/7 cloud-native agent that accepts natural language instructions from a non-technical user via Discord or a web interface, autonomously plans and executes complex multi-step tasks, produces real professional-grade deliverables, runs continuously for days to weeks without human supervision, improves its own codebase autonomously during idle periods, and costs absolutely nothing to operate.

Ultron is not a chatbot. It is not a coding assistant. It is a fully autonomous AI colleague that works while you sleep, remembers everything forever, never loses context, never repeats mistakes, and gets smarter every single day — automatically, without any intervention.

The system combines research-validated techniques from Google DeepMind (AlphaEvolve), NeurIPS 2025 (Context Folding, Observation Masking), TogetherAI (Mixture of Agents), and enterprise production patterns (MCP, A2A, AG-UI protocols) into a unified architecture that runs entirely on free-tier cloud services.

---

## Context & Problem

### Who Is Affected

| Persona | Pain Today |
|---|---|
| **Ghost (non-technical student)** | Cannot use Claude Code (needs terminal), cannot afford Devin ($2000/month), cannot use Augment (needs daily supervision), has no persistent AI memory across sessions |
| **Chemical Engineering students** | No AI tool has domain-specific ChE tools (HYSYS, ASPEN equivalent, thermodynamic calculations) |
| **Students with complex projects** | All existing agents stop when the user stops — 100-day autonomous projects are impossible |
| **Non-technical users generally** | Every autonomous agent requires technical setup, terminal knowledge, API management |

### The Core Problem

Every existing autonomous AI agent suffers from at least one fatal flaw:

1. **No persistent memory** — Manus, Claude Code, ChatGPT reset between sessions. Decisions made on Day 1 are forgotten by Day 7. Architecture drifts. Quality degrades.

2. **Stops when user stops** — Augment Code, Cursor, Claude Code require constant human supervision. They are tools, not agents.

3. **Prohibitively expensive** — Devin costs $500-2000/month. No student can afford this.

4. **Requires technical knowledge** — All existing agents require terminal access, API key management, configuration files. Non-technical users are excluded.

5. **No domain specialization** — No agent has chemical engineering tools, thermodynamic databases, or discipline-specific calculation capabilities.

6. **No self-improvement** — Existing agents plateau at their initial quality. They never get better on their own.

### Success Looks Like

- Ghost types "build me the most powerful calculator website ever" on Discord from his phone, goes to sleep, and wakes up 3 days later to find a deployed, working, beautiful website with a link in Discord — having typed zero lines of code
- Ultron remembers every conversation, every project, every decision Ghost has ever made — perfectly, forever, retrievable in under 100ms
- A 100-day autonomous OS project produces a working, documented, tested system — with Ghost spending less than 2 hours total
- Code quality matches or exceeds what a senior engineer would produce — with consistent style, zero architectural drift, and 94% test coverage
- The entire system costs exactly $0 per month to operate

---

## Scope

### In Scope — MVP (8 Weeks)

**Core Brain:**
- Mixture of Agents (MoA) with 8 role-based proposers
- MRKL Router for intelligent task classification
- Traycer-inspired Epic Flow spec generation (7 prompts)
- Tree of Thoughts + Graph of Thoughts reasoning
- LATS (Language Agent Tree Search) for complex decisions
- Reflexion for learning from failures
- Process Reward Models (step-by-step verification)
- Constitutional Critic (3-round quality gate)
- Self-consistency (×5-10 verification)
- Entropy Engine (quality and priority management)
- Circuit Breaker (3-layer infinite loop prevention)
- Claude Opus 4.6 oracle via Puter.js (critical decisions)
- AlphaEvolve for algorithm optimization

**Memory System:**
- Upstash Redis (working memory, context passport)
- Zilliz Cloud ×15 accounts (vector memory, 15M vectors)
- Mem0 atomic fact extraction
- Knowledge graph via Cognee
- ACE loop (Generator/Reflector/Curator lessons)
- RAPTOR hierarchical memory compression
- Zep temporal/episodic indexing
- Letta-style Core Memory (always in context)
- Nightly JSONL backup to GitHub

**Execution:**
- ClawCloud Run ×3 (24GB RAM persistent, always-on)
- GitHub Actions (unlimited burst compute, public repo)
- E2B sandboxes (isolated code execution)
- QStash event-driven architecture (no polling)
- Docker sandboxing with full security hardening
- Dual heartbeat (ClawCloud primary + Koyeb watchdog)

**Tools (30+):**
- Document tools: PDF, Word, Excel, PowerPoint, LaTeX
- Code tools: write, run, test, lint, commit, deploy
- Web tools: Playwright MCP, Firecrawl MCP, Apify MCP
- ChE tools: mass balance, thermodynamics, VLE, McCabe-Thiele
- Computer use: Agent S3 + Gemini Vision + UI-TARS-1.5-7B
- Communication: Discord, Notion, n8n workflows
- Memory tools: read, write, graph traversal, backup
- MCP servers: GitHub, Semgrep, Context7, ArXiv, Fast.io

**Interface:**
- Discord bot (primary, works from any phone)
- Website master control panel (Cloudflare Pages)
- Settings tab for all secrets (paste-and-save, no technical knowledge)
- AG-UI real-time streaming

**Self-Improvement:**
- AlphaEvolve evolutionary loop
- Self-modification with whitelist constraints
- Canary deployment with auto-rollback
- Skills library (1,234+ community skills + custom ChE skills)
- Spec Engine auto-generates Traycer-quality docs

### Out of Scope (Post v3)

- Mobile app (Discord handles mobile access)
- Voice interface
- Multi-user support (single user: Ghost)
- Video generation
- Hardware integration
- Paid API usage (everything must remain $0)

---

## Architecture Principles

1. **Quality over speed** — Deep mode takes 3 minutes, instant mode takes 10 seconds. Quality never sacrificed for speed.
2. **Memory is sacred** — Zero information loss. Everything stored in 3+ redundant locations.
3. **Free forever** — If a component requires payment, find a free alternative or remove it.
4. **No manual work** — After 30-minute initial setup, Ghost never touches a config file again.
5. **Entropy drives everything** — Task priority, debugging order, quality gates all driven by thermodynamic entropy scores.
6. **Specs before code** — For every complex project, Ultron generates full documentation before writing a single line.
7. **Circuit breaker** — No infinite loops. Every action has an escape route.
8. **Whitelist not blacklist** — Self-modification only touches explicitly allowed files.

---

## Success Metrics (Measurable)

| Metric | Target | How Measured |
|---|---|---|
| Task completion (100-day project) | 85%+ functional | AI judge evaluation |
| Memory retrieval accuracy | 90%+ | Benchmark against Mem0 |
| Context restoration time | <100ms | Redis response time |
| Daily token usage vs budget | <25% of available | Quota Brain tracker |
| Self-modification success rate | >80% | Test suite pass rate |
| Hallucination rate on specs | <10% | Cross-artifact validation |
| Code quality score | 8.5+/10 | AI judge + linter |
| Ghost effort per 100-day project | <20 hours | Logged interaction time |
| Monthly cost | $0 | Bank statement |
| System uptime | >99% | Monitoring logs |

---

## Timeline

| Phase | Duration | Deliverable |
|---|---|---|
| Phase 0: Specs | 1 day | All 40 tickets generated |
| Phase 1: Foundation | Week 1 | Repo, CF Worker, Discord, basic memory |
| Phase 2: Brain Core | Week 2 | MoA, Router, Key Rotation, Entropy |
| Phase 3: Memory | Week 3 | Full memory stack, Mem0, Knowledge Graph |
| Phase 4: Tools | Week 4 | All tools, MCP servers, Computer Use |
| Phase 5: Intelligence | Week 5 | Tree of Thoughts, LATS, Reflexion |
| Phase 6: Self-Improvement | Week 6 | AlphaEvolve, Self-Mod, Spec Engine |
| Phase 7: Website | Week 7 | Full control panel, settings, AG-UI |
| Phase 8: Polish | Week 8 | Testing, documentation, deployment |
