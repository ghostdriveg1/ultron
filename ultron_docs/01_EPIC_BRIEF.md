# ULTRON v3 — EPIC BRIEF
**Status:** Active Development  
**Author:** Ghost (SVNIT Surat, Chemical Engineering)  
**Version:** 3.0  
**Date:** March 2026  
**Classification:** Experimental Research Project — Non-Commercial  

---

## Summary

Ultron v3 is the most advanced personal autonomous AI agent system ever designed by a single student researcher on a zero-dollar budget. It combines Mixture of Agents intelligence, thermodynamic entropy-driven quality management, AlphaEvolve evolutionary optimization, Traycer-style spec-driven planning, persistent lossless memory, and computer use capabilities into a single unified system that runs 24 hours a day, 7 days a week, 365 days a year — autonomously, without human supervision.

Ultron accepts natural language instructions from Ghost via Discord or a web interface. It plans every complex task using a 7-document specification system before writing a single line of code. It executes using a swarm of 8 role-based AI agents with self-consistency verification, constitutional critique, and Claude Opus validation at critical decision points. It remembers everything forever using a 5-tier memory system that never forgets, never hallucinates about the past, and proactively surfaces relevant context. It improves itself continuously using AlphaEvolve evolutionary loops, Reflexion failure analysis, and ACE lesson playbooks. It produces professional-grade deliverables across every domain: code, documents, websites, research reports, chemical engineering calculations, and more.

The north star: Ghost types a message. Ultron handles everything. The work is done to a standard that exceeds any commercial AI system — at zero cost, forever.

---

## Context & Problem

### Who Is Affected

| Persona | Pain Today |
|---|---|
| **Ghost as student** | No AI tool runs autonomously for 100-day projects. All commercial tools require constant supervision. Session resets lose all context. No tool knows Ghost's personal history, preferences, or projects. |
| **Ghost as ChE student** | No AI tool has domain-specific ChE capabilities (mass balance, thermodynamics, distillation design, NIST data access). Generic tools give generic answers. |
| **Ghost as non-technical user** | Complex DevOps, secret management, and infrastructure setup is inaccessible. No tool manages its own infrastructure for the user. |
| **Ghost as researcher** | No tool automatically researches ArXiv papers, synthesizes findings, and applies them to ongoing work. |
| **Ghost as builder** | No tool autonomously builds projects for 100+ days, self-improves, and delivers production-ready results at zero cost. |

### The Core Problem

Every commercial AI system — Claude Code, Manus, Devin, GitHub Copilot, Augment Code — is fundamentally session-based. They work when you work. They stop when you stop. They forget between sessions. They cost money. They don't know you personally. They can't run for 100 days autonomously. They can't improve themselves. They can't build something while you sleep.

Ultron is the answer to all of these limitations simultaneously.

### Success Looks Like

- Ghost types "Build the most powerful calculator website ever" and never types another message about it for 100 days — receiving a production-grade, fully-tested, deployed application
- Ghost can message Ultron from any phone, any browser, anywhere in the world with zero setup
- Ultron correctly recalls that Steve is Ghost's friend who had a breakup with Priya in 2024, even if this was mentioned 200 days ago
- Ultron produces a lab report for HCl absorption that a SVNIT professor would give full marks
- Ultron autonomously improves its own codebase every idle moment, getting measurably better over time
- Ghost spends less than 2 hours total supervising any 100-day project

---

## Scope

### In — Core System (8 Weeks)

**Brain Layer:**
- MoA orchestrator with 8 role-based proposers (Architect, Engineer, QA, Researcher, Reasoner, Devil's Advocate, Domain Expert, Validator)
- MRKL Router for task classification (9 task types)
- Traycer-style Spec Engine (7-document planning system)
- Tree of Thoughts for complex reasoning
- Graph of Thoughts for synthesis
- LATS (Language Agent Tree Search) for simulation before execution
- Self-consistency verification (×5-10 samples)
- Constitutional Critic (3 rounds)
- Claude Sonnet 4.6 critic layer
- Gemini 3 Pro synthesizer
- Claude Opus 4.6 oracle gate (via Puter.js backend)
- Process Reward Models (step-level scoring)
- Reflexion (failure analysis and lesson extraction)
- AlphaEvolve (evolutionary algorithm optimization)
- Instant Mode (single call, <10 seconds) vs Deep Mode (full pipeline)
- Key rotation pool (unlimited accounts, adaptive quota management)
- Quota Brain (token budget tracking and intelligent routing)
- Circuit breaker (3-layer, per-agent, O(log n))

**Memory Layer:**
- Tier 0: Core Memory (Letta-style, always in context, Redis)
- Tier 1: Working Memory (context passport, sliding window, Redis)
- Tier 2: Insight Memory (Mem0 atomic facts, Cognee knowledge graph, RAPTOR hierarchy, Zep temporal, ACE playbook, Zilliz ×15 accounts)
- Tier 3: Archival Memory (lossless JSONL, GitHub permanent)
- Tier 4: Structured Memory (Notion, DeepWiki, human-readable)
- Real-time memory fabric (Redis pub/sub push, proactive context delivery)
- Memory pruning (3 policies: deduplication, TTL, importance scoring)
- Nightly consolidation job

**Execution Layer:**
- ClawCloud Run ×3 instances (12 vCPU, 24GB RAM, persistent, always-on)
- GitHub Actions burst compute (unlimited, parallel jobs)
- Koyeb watchdog (512MB, always-on backup heartbeat)
- QStash event-driven architecture (no polling)
- E2B sandboxes (isolated code execution)
- Docker security hardening (all flags)
- Circuit breaker (infinite loop prevention)
- Token budget guardian

**Tool Registry (30+ tools):**
- Document tools: PDF, Word, Excel, PowerPoint, LaTeX
- Code tools: write, run, test, lint, commit, PR, deploy
- Web tools: Playwright MCP, Firecrawl MCP, Apify MCP, ArXiv MCP
- ChE tools: mass balance, thermodynamics, VLE, McCabe-Thiele, NIST MCP, PubChem MCP, unit conversion
- Computer use: Agent S3 + Gemini Vision + UI-TARS-1.5-7B
- Memory tools: read, write, graph traversal, backup
- Communication: Discord, Notion, n8n workflows

**MCP Infrastructure:**
- Bifrost Gateway (central management, logging, health monitoring)
- GitHub MCP, Semgrep MCP, Context7 MCP, Run Python MCP
- Firecrawl MCP, Apify MCP, ArXiv MCP
- Fast.io MCP (50GB storage), Google DB Toolbox MCP
- n8n MCP, Playwright MCP, Notion MCP
- NIST Chemistry MCP (custom), PubChem MCP (custom), Engineering Units MCP (custom)

**Quality Layer:**
- 3-layer AI Judge (functional, quality, personal preference)
- Style Mirror (Ghost's coding style, 50-function sampling)
- 5 commit quality gates (tests, linting, TODOs, duplication, style)
- Mutation testing for self-modification safety
- Git-native commits (atomic, every edit)
- Fast Apply layer (deterministic code editing)
- CODEOWNERS (4 sacred files locked)
- Canary deployment + automatic rollback

**Self-Improvement:**
- AlphaEvolve (generate → evaluate → select → crossover → repeat)
- Self-modification whitelist (/tools/, /prompts/task_specific/, /config/model_routing.json)
- Reflexion loop (failure → reflect → lesson → store → load next time)
- ACE loop (Generator → Reflector → Curator → Playbook)
- AFlow workflow optimization (learns optimal pipeline per task type)
- Spec Engine self-improvement (AlphaEvolve applied to planning prompts)

**Entropy Engine:**
- Memory entropy (pruning trigger)
- Codebase entropy (refactor trigger)
- Decision diversity (groupthink prevention)
- Task queue entropy (dynamic priority sorting)
- Bug entropy (fix most dangerous first)
- Code write entropy (clean over quick)
- Fix validation entropy (revert if entropy rises)
- System health entropy (self-healing trigger)

**Interface:**
- Discord bot (primary, any device, any phone)
- Website master control panel (Cloudflare Pages)
- AG-UI protocol (real-time streaming)
- Settings tab (paste all credentials, no technical knowledge needed)
- Secrets stored in Cloudflare KV (never in GitHub)
- Infinite account scaling (paste more keys → automatically used)

**Protocols:**
- MCP (Model Context Protocol) — agent to tools
- A2A (Agent to Agent) — orchestrator to sub-agents
- AG-UI — agent to frontend

**Deployment:**
- Cloudflare Worker (brain router, edge, global)
- Cloudflare Pages (website)
- Cloudflare KV (secrets, encrypted)
- ClawCloud Run ×3 (persistent execution)
- Koyeb (watchdog)
- GitHub Actions (burst, deployment)
- Firebase Hosting (Ghost's project deployments)
- Fast.io (50GB document storage)

### Out — Not In This Version

- Voice/video interface
- Mobile app (native)
- Multi-user support (Ghost only)
- Paid API usage (zero cost constraint)
- Local GPU inference (cloud-only)
- Fine-tuning any models

---

## Non-Negotiables

1. **Zero cost forever.** Every component uses free tiers. No credit card charges ever.
2. **Works from any phone.** Ghost never needs a laptop to interact with Ultron.
3. **Never loses context.** API key rotation, service outages, and restarts never cause task loss.
4. **Autonomous 24/7.** Ultron works while Ghost sleeps. Always.
5. **Remembers everything.** No information ever lost. No memory ever corrupted.
6. **Plans before executing.** No complex task starts without full spec documentation.
7. **Self-improves continuously.** Every idle moment is used to get better.
8. **Delivers real files.** Not just text. Actual downloadable, deployable outputs.

---

## Key Performance Indicators

| KPI | Target | Measurement |
|---|---|---|
| Simple query response time | <10 seconds | Discord → reply timing |
| Complex task completion (100 days) | >85% of spec | Acceptance criteria checklist |
| Memory recall accuracy | >95% | Random sample of stored facts |
| Context loss rate on key rotation | 0% | Monitor for task discontinuities |
| Self-modification success rate | >90% | Canary pass rate |
| Code quality (AI judge) | >88% average | 3-layer judge scores |
| Uptime | >99% | Heartbeat monitoring |
| Ghost effort per 100-day project | <20 hours | Time tracking |

---

## Timeline

| Milestone | Target | Definition of Done |
|---|---|---|
| Week 1 | Foundation | Brain routes messages, Discord responds, keys rotate |
| Week 2 | Intelligence | MoA pipeline complete, all 8 roles active |
| Week 3 | Memory | All 5 tiers working, context passport functional |
| Week 4 | Tools | 30+ tools registered, document creation working |
| Week 5 | Quality | 3-layer judge, style mirror, quality gates active |
| Week 6 | Self-Improvement | AlphaEvolve, Reflexion, ACE all running |
| Week 7 | Spec Engine | 7-document system generates automatically |
| Week 8 | Full System | All components integrated, 100-day test starts |
