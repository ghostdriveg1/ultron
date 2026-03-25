# ULTRON v3 — TECHNICAL PLAN
**References:** Epic Brief v3.0, Core Flows v3.0  
**Date:** March 2026

---

## Complete Directory Structure

```
ultron/
├── cloudflare_worker/                    ← Brain entry point (TypeScript)
│   ├── src/
│   │   ├── index.ts                      ← Main Worker handler
│   │   ├── intent_parser.ts              ← Complexity detection
│   │   ├── discord_handler.ts            ← Discord webhook processing
│   │   ├── secrets_handler.ts            ← KV secrets management
│   │   ├── qstash_client.ts              ← Message queue client
│   │   └── types.ts                      ← TypeScript interfaces
│   ├── wrangler.toml                     ← Cloudflare config
│   └── package.json
│
├── packages/
│   ├── brain/                            ← Intelligence layer (Python)
│   │   ├── __init__.py
│   │   ├── complexity_detector.py        ← CONVERSATIONAL vs TASK
│   │   ├── instant_mode.py               ← Single model fast response
│   │   ├── epic_flow.py                  ← Full MoA + spec pipeline
│   │   ├── mrkl_router.py               ← Task type classification
│   │   ├── thinking_injector.py          ← CoT prompt injection
│   │   ├── prm_scorer.py                ← Process reward model
│   │   ├── tree_of_thoughts.py           ← ToT reasoning
│   │   ├── graph_of_thoughts.py          ← GoT reasoning
│   │   ├── lats.py                       ← Language Agent Tree Search
│   │   ├── reflexion.py                  ← Learn from failures
│   │   ├── moa_orchestrator.py           ← 8-proposer MoA coordinator
│   │   ├── self_consistency.py           ← ×5-10 verification
│   │   ├── entropy_gate.py               ← Claude Opus escalation
│   │   ├── puter_opus_caller.py          ← Puter.js Node.js bridge
│   │   ├── synthesizer.py                ← Gemini 3 Pro final answer
│   │   │
│   │   ├── proposers/                    ← 8 role-based models
│   │   │   ├── base_proposer.py
│   │   │   ├── architect.py              ← Gemini 2.5 Pro
│   │   │   ├── engineer.py               ← DeepSeek Coder V3
│   │   │   ├── qa_breaker.py             ← Gemini 2.5 Pro instance 2
│   │   │   ├── researcher.py             ← Grok 4.1 (2M context)
│   │   │   ├── reasoner.py               ← DeepSeek R1
│   │   │   ├── devils_advocate.py        ← Llama 4 Maverick
│   │   │   ├── domain_expert.py          ← Gemini Student Pro
│   │   │   └── fast_validator.py         ← Cerebras Llama 70B
│   │   │
│   │   ├── critics/
│   │   │   ├── sonnet_critic.py          ← Claude Sonnet 4.6
│   │   │   └── constitutional_critic.py  ← 3-round quality gate
│   │   │
│   │   ├── key_rotation/
│   │   │   ├── pool.py                   ← Key selection O(log n)
│   │   │   ├── quota_brain.py            ← Usage tracking + prediction
│   │   │   └── admission_control.py      ← Token bucket algorithm
│   │   │
│   │   ├── circuit_breaker.py            ← 3-layer loop prevention
│   │   ├── circuit_breaker/
│   │   │   ├── semantic_hash_ring.py     ← Action pattern detection
│   │   │   ├── progress_entropy_detector.py ← Token/quality ratio
│   │   │   ├── state_diff_monitor.py     ← Git diff based
│   │   │   └── token_budget_guardian.py  ← Hard quota limits
│   │   │
│   │   └── spec_engine/
│   │       ├── orchestrator.py           ← Runs 7 prompts in order
│   │       ├── epic_brief_prompt.py
│   │       ├── core_flows_prompt.py
│   │       ├── tech_plan_prompt.py
│   │       ├── arch_validation_prompt.py
│   │       ├── ticket_breakdown_prompt.py
│   │       ├── cross_artifact_prompt.py
│   │       └── ultron_brief_prompt.py
│   │
│   ├── memory/                           ← 5-tier memory system
│   │   ├── __init__.py
│   │   ├── core_memory.py                ← Always-in-context facts
│   │   ├── passport.py                   ← Context passport builder
│   │   ├── restore.py                    ← Context restoration
│   │   ├── mem0_extractor.py             ← Atomic fact extraction
│   │   ├── zilliz_client.py              ← Vector DB client
│   │   ├── knowledge_graph.py            ← Cognee graph operations
│   │   ├── ace_curator.py                ← Lesson extraction
│   │   ├── raptor_tree.py                ← Hierarchical compression
│   │   ├── zep_temporal.py               ← Temporal/episodic index
│   │   ├── retrieval_engine.py           ← Unified retrieval
│   │   ├── jsonl_archive.py              ← Lossless GitHub backup
│   │   └── pruning_engine.py             ← TTL + importance pruning
│   │
│   ├── tools/                            ← 30+ tool registry
│   │   ├── __init__.py
│   │   ├── registry.py                   ← Tool discovery + loading
│   │   ├── executor.py                   ← Safe execution wrapper
│   │   ├── permission_matrix.py          ← Access control
│   │   │
│   │   ├── document/
│   │   │   ├── pdf_tool.py               ← WeasyPrint + reportlab
│   │   │   ├── word_tool.py              ← python-docx
│   │   │   ├── excel_tool.py             ← openpyxl + pandas
│   │   │   ├── pptx_tool.py              ← python-pptx
│   │   │   └── latex_tool.py             ← pdflatex compiler
│   │   │
│   │   ├── code/
│   │   │   ├── writer_tool.py            ← Code generation
│   │   │   ├── runner_tool.py            ← Python/Node execution
│   │   │   ├── tester_tool.py            ← pytest/jest runner
│   │   │   ├── linter_tool.py            ← pylint/eslint
│   │   │   ├── fast_apply_tool.py        ← Deterministic edits
│   │   │   ├── github_tool.py            ← GitHub MCP wrapper
│   │   │   └── deploy_tool.py            ← Firebase/CF Pages deploy
│   │   │
│   │   ├── web/
│   │   │   ├── playwright_tool.py        ← Browser automation MCP
│   │   │   ├── firecrawl_tool.py         ← URL→Markdown MCP
│   │   │   ├── apify_tool.py             ← Structured scraping MCP
│   │   │   ├── arxiv_tool.py             ← Academic papers MCP
│   │   │   └── search_tool.py            ← Web search APIs
│   │   │
│   │   ├── che/                          ← Ghost-specific tools
│   │   │   ├── mass_balance_tool.py      ← Conservation equations
│   │   │   ├── thermo_tool.py            ← CoolProp thermodynamics
│   │   │   ├── vle_tool.py               ← Vapor-liquid equilibrium
│   │   │   ├── mccabe_thiele_tool.py     ← Distillation diagrams
│   │   │   ├── nist_tool.py              ← NIST chemistry data MCP
│   │   │   ├── pubchem_tool.py           ← Chemical properties MCP
│   │   │   └── unit_convert_tool.py      ← Pint unit conversion MCP
│   │   │
│   │   ├── computer_use/
│   │   │   ├── agent_s3_controller.py    ← Agent S3 integration
│   │   │   ├── gemini_vision.py          ← Screen understanding
│   │   │   ├── uitars_grounder.py        ← UI-TARS pixel coords
│   │   │   └── xvfb_manager.py           ← Virtual display
│   │   │
│   │   ├── communication/
│   │   │   ├── discord_tool.py           ← Send Discord messages
│   │   │   ├── notion_tool.py            ← Notion MCP
│   │   │   ├── n8n_tool.py              ← Workflow automation MCP
│   │   │   └── fastio_tool.py            ← File storage MCP
│   │   │
│   │   └── memory_tools/
│   │       ├── memory_read_tool.py
│   │       ├── memory_write_tool.py
│   │       └── graph_query_tool.py
│   │
│   ├── execution/                        ← Runtime environment
│   │   ├── __init__.py
│   │   ├── heartbeat.py                  ← 30-second perpetual loop
│   │   ├── remote_work_loop.py           ← Long-horizon projects
│   │   ├── hierarchical_planner.py       ← Global + Local planner
│   │   ├── sub_agent_manager.py          ← A2A parallel agents
│   │   ├── watchdog.py                   ← Self-healing monitor
│   │   ├── e2b_sandbox.py                ← Isolated code execution
│   │   └── entropy_scheduler.py          ← Priority queue
│   │
│   ├── self_mod/                         ← AlphaEvolve engine
│   │   ├── __init__.py
│   │   ├── alphaevolve.py                ← Evolutionary loop
│   │   ├── whitelist_enforcer.py         ← File protection
│   │   ├── canary_deployer.py            ← Safe deployment
│   │   ├── mutation_tester.py            ← Test quality verification
│   │   └── skill_builder.py              ← Auto-generates skills
│   │
│   └── interface/                        ← Communication layer
│       ├── __init__.py
│       ├── discord_bot.py                ← Discord gateway
│       ├── discord_sender.py             ← Message sending
│       └── notion_writer.py              ← Notion page creation
│
├── website/                              ← Master control panel (React)
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx             ← Live system status
│   │   │   ├── Chat.tsx                  ← Full conversation UI
│   │   │   ├── Projects.tsx              ← All projects + progress
│   │   │   ├── Memory.tsx                ← Memory browser
│   │   │   └── Settings.tsx              ← Secrets management
│   │   └── components/
│   │       ├── EntropyMonitor.tsx        ← Live entropy dashboard
│   │       ├── KeyPoolStatus.tsx         ← API key health
│   │       └── SecretField.tsx           ← Paste-and-save component
│   ├── package.json
│   └── vite.config.ts
│
├── mcp_servers/                          ← Custom MCP implementations
│   ├── nist_mcp/                         ← NIST chemistry data
│   ├── pubchem_mcp/                      ← Chemical properties
│   └── engineering_units_mcp/           ← Unit conversion
│
├── skills/                               ← Skills library
│   ├── che/
│   │   ├── mass_balance/SKILL.md
│   │   ├── thermo/SKILL.md
│   │   ├── latex_report/SKILL.md
│   │   └── distillation/SKILL.md
│   ├── coding/
│   │   ├── python/SKILL.md
│   │   ├── react/SKILL.md
│   │   ├── api_design/SKILL.md
│   │   └── testing/SKILL.md
│   └── document/
│       ├── latex/SKILL.md
│       └── pptx/SKILL.md
│
├── config/
│   ├── model_routing.json                ← Which model for what task
│   ├── permissions.json                  ← Tool permission matrix
│   └── whitelist.json                    ← Self-mod allowed files
│
├── state/                                ← Runtime state
│   ├── CURRENT_TASK.md                   ← What Ultron is doing now
│   └── SYSTEM_STATUS.md                  ← Health metrics
│
├── intent/
│   └── ULTRON_INTENT.md                  ← Ghost's long-term goals
│
├── docker-compose.yml                    ← Local development
├── .env.example                          ← All required env vars
├── requirements.txt                      ← Python dependencies
└── package.json                          ← Root Node.js config
```

---

## Service Architecture

| Service | Technology | Hosted On | Purpose |
|---|---|---|---|
| Brain Router | Cloudflare Worker (TypeScript) | Cloudflare Edge | Receives all Discord messages, routes to agents |
| Brain Agent | Python + LangGraph | ClawCloud Run #1 | MoA orchestration, MoA pipeline, spec engine |
| Memory Agent | Python | ClawCloud Run #2 | Mem0, Zilliz, Cognee, ACE, RAPTOR |
| Computer Use | Python + Xvfb | ClawCloud Run #3 | Agent S3, UI-TARS, virtual display |
| Watchdog | Python | Koyeb | Monitors ClawCloud health, triggers restart |
| Message Queue | QStash | Upstash Cloud | Event-driven task routing |
| Hot Memory | Redis | Upstash Cloud | Context passports, key pool, quota tracking |
| Vector Memory | Milvus | Zilliz Cloud ×15 | Semantic memory, 15M vectors |
| Knowledge Graph | Cognee + SQLite | ClawCloud Run #2 | Entity relationships |
| Structured Memory | Notion API | Notion Cloud | Human-readable memory, project docs |
| Code Memory | Git | GitHub | Procedural memory, lossless archive |
| Website | React + Vite | Cloudflare Pages | Master control panel |
| Secrets | KV | Cloudflare KV | All API keys encrypted |
| File Storage | Fast.io | Fast.io Cloud | Document outputs, 50GB free |

---

## Database / State Schemas

### Redis Keys (Upstash)

```
core_memory:{ghost_id}           → JSON: Ghost's always-loaded context
task_state:{task_id}             → JSON: current task snapshot
key_pool:{provider}              → JSON: all keys with quota data
quota:{provider}:{key_id}        → Integer: requests remaining
circuit_breaker:{agent_id}       → JSON: breaker state
session:{session_id}             → JSON: conversation history
project:{project_id}             → JSON: long-horizon project state
```

### Zilliz Collections (per account)

**Collection: episodic_memory**
```
{
  id: UUID,
  vector: float[768],           ← embedding of content
  content: string,              ← atomic fact or action
  fact_type: string,            ← "person"|"project"|"decision"|"lesson"
  entity: string,               ← "Steve"|"auth.py"|"OS project"
  project_id: string,
  session_id: string,
  timestamp: datetime,
  access_count: integer,        ← for pruning decisions
  importance: float,            ← 0.0-1.0
  episode_id: string,           ← for Zep temporal grouping
  provenance: string            ← where this fact came from
}
```

**Collection: codebase_knowledge**
```
{
  id: UUID,
  vector: float[768],
  file_path: string,
  function_name: string,
  content: string,              ← function signature + docstring
  dependencies: string[],       ← files this depends on
  dependents: string[],         ← files that depend on this
  project_id: string,
  last_modified: datetime
}
```

### Cloudflare KV

```
secret:{service}:{account_id}   → encrypted API key
secret:{service}:count          → number of keys stored
mcp_config                      → JSON: all MCP server URLs
model_routing                   → JSON: current model assignments
```

### GitHub Repository Files

```
/memory/events.jsonl            ← append-only event log (lossless)
/memory/daily/{date}.jsonl      ← daily activity archive
/state/CURRENT_TASK.md          ← human-readable current state
/state/SYSTEM_STATUS.md         ← health metrics
/docs/{project}/                ← DeepWiki per project
```

---

## API Contracts

### Cloudflare Worker (Internal)

**POST /internal/task**
```
Request:
{
  task_id: string,
  type: "CONVERSATIONAL"|"CODE"|"DOCUMENT"|"RESEARCH"|"CHE"|"REMOTE_WORK"|"COMPLEX",
  payload: {
    message: string,
    user_id: string,
    context_passport: object
  },
  priority: "URGENT"|"NORMAL"|"BACKGROUND",
  deadline: string (ISO-8601),
  callback: "discord"|"notion"|"github"
}

Response: 202 Accepted
{
  task_id: string,
  estimated_completion: string
}
```

**POST /internal/secret**
```
Request:
{
  service: string,
  key_id: string,
  value: string (will be encrypted)
}

Response: 200 OK
{
  stored: true,
  key_count: number
}
```

### Website ↔ Cloudflare Worker

**GET /api/status**
```
Response:
{
  brain_healthy: boolean,
  memory_healthy: boolean,
  active_tasks: number,
  quota_usage: {
    gemini: { used: number, total: number },
    groq: { used: number, total: number }
  },
  entropy_scores: {
    system: number,
    memory: number,
    codebase: number
  }
}
```

**POST /api/settings/key**
```
Request:
{
  service: "gemini"|"groq"|"openrouter"|"zilliz"|"puter"|"parallel_ai"|...,
  value: string
}

Response: 200 OK | 400 Bad Request
```

---

## Environment Variables

```bash
# Cloudflare (set in wrangler.toml secrets)
DISCORD_BOT_TOKEN=
DISCORD_PUBLIC_KEY=
CLAWCLOUD_BRAIN_URL=        # ClawCloud Instance 1 URL
QSTASH_URL=
QSTASH_TOKEN=

# Brain Agent (ClawCloud Instance 1)
REDIS_URL=                  # Upstash Redis URL
REDIS_TOKEN=                # Upstash Redis token
ZILLIZ_URI_1=               # First Zilliz account URI
ZILLIZ_TOKEN_1=
ZILLIZ_URI_2=
ZILLIZ_TOKEN_2=
# ... up to ZILLIZ_URI_15
NOTION_TOKEN=
GITHUB_TOKEN=               # ultron-agent account token
PUTER_AUTH_TOKEN=           # For Claude Opus access
PARALLEL_AI_KEY_1=
# ... up to PARALLEL_AI_KEY_20
GEMINI_KEY_1=
# ... up to GEMINI_KEY_20
GROQ_KEY_1=
# ... up to GROQ_KEY_10
OPENROUTER_KEY_1=
# ... up to OPENROUTER_KEY_10
CEREBRAS_KEY_1=
# ... up to CEREBRAS_KEY_5
TOGETHER_KEY_1=
# ... up to TOGETHER_KEY_5
FIRECRAWL_KEY=
APIFY_KEY=
E2B_KEY=
FASTIO_KEY=

# Memory Agent (ClawCloud Instance 2)
COGNEE_DB_PATH=/data/cognee.db
RAPTOR_INDEX_PATH=/data/raptor/

# Website (Cloudflare Pages env)
VITE_API_URL=               # Cloudflare Worker URL
```

---

## External Dependencies

### Python (requirements.txt)
```
langchain>=0.3.0
langgraph>=0.2.0
langchain-google-genai>=2.0.0
langchain-anthropic>=0.3.0
langchain-groq>=0.2.0
langchain-community>=0.3.0
mem0ai>=0.1.0
cognee>=0.1.0
pymilvus>=2.4.0
upstash-redis>=1.0.0
upstash-qstash>=2.0.0
openai>=1.0.0
pydantic>=2.0.0
httpx>=0.27.0
asyncio>=3.4.3
python-dotenv>=1.0.0
reportlab>=4.0.0
weasyprint>=62.0
python-docx>=1.1.0
openpyxl>=3.1.0
python-pptx>=0.6.23
coolprop>=6.6.0
pint>=0.23.0
scipy>=1.13.0
numpy>=2.0.0
matplotlib>=3.9.0
plotly>=5.22.0
thermo>=0.2.0
gitpython>=3.1.43
playwright>=1.44.0
mcp>=1.0.0
e2b>=0.17.0
```

### Node.js (package.json root)
```json
{
  "dependencies": {
    "wrangler": "^3.0.0",
    "@cloudflare/workers-types": "^4.0.0",
    "discord-interactions": "^3.0.0"
  }
}
```

### Website (website/package.json)
```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.24.0",
    "@tanstack/react-query": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "lucide-react": "^0.383.0",
    "recharts": "^2.12.0",
    "vite": "^5.3.0",
    "@vitejs/plugin-react": "^4.3.0"
  }
}
```

---

## Model Routing Configuration (config/model_routing.json)

```json
{
  "instant_mode": {
    "primary": "gemini-2.5-pro",
    "fallback": "gemini-2.5-flash",
    "max_tokens": 2000,
    "thinking_injection": true
  },
  "proposers": {
    "architect": { "model": "gemini-2.5-pro", "provider": "google" },
    "engineer": { "model": "deepseek-coder-v3", "provider": "groq" },
    "qa_breaker": { "model": "gemini-2.5-pro", "provider": "google", "instance": 2 },
    "researcher": { "model": "grok-4.1", "provider": "xai" },
    "reasoner": { "model": "deepseek-r1", "provider": "groq" },
    "devils_advocate": { "model": "meta-llama/llama-4-maverick", "provider": "together" },
    "domain_expert": { "model": "gemini-3.1-pro", "provider": "google_student" },
    "fast_validator": { "model": "llama-3.3-70b", "provider": "cerebras" }
  },
  "critic": {
    "model": "claude-sonnet-4-6",
    "provider": "puter"
  },
  "synthesizer": {
    "model": "gemini-3-pro",
    "provider": "google_student"
  },
  "oracle": {
    "model": "claude-opus-4-6",
    "provider": "puter",
    "max_calls_per_day": 8
  },
  "spec_engine": {
    "epic_brief": "gemini-3-pro",
    "core_flows": "gemini-2.5-pro",
    "tech_plan": "gemini-3-pro",
    "arch_validation": "claude-opus-4-6",
    "ticket_breakdown": "gemini-2.5-pro",
    "cross_artifact": "gemini-2.5-pro",
    "ultron_brief": "claude-opus-4-6"
  }
}
```

---

## MCP Server Registry

| Server | URL/Install | Purpose | Free |
|---|---|---|---|
| GitHub MCP | @modelcontextprotocol/server-github | Repo operations | ✅ |
| Semgrep MCP | npx semgrep-mcp | Security scanning | ✅ |
| Context7 MCP | npx @upstash/context7-mcp | Live library docs | ✅ |
| Playwright MCP | npx @playwright/mcp | Browser automation | ✅ |
| ArXiv MCP | npx arxiv-mcp-server | Academic papers | ✅ |
| Firecrawl MCP | @mendableai/firecrawl-mcp | URL→Markdown | ✅ Free tier |
| Apify MCP | @apify/mcp | Web scrapers | ✅ Free tier |
| Fast.io MCP | @fast-agent/mcp | File storage | ✅ 50GB free |
| n8n MCP | self-hosted on ClawCloud | Workflow automation | ✅ Self-hosted |
| Notion MCP | @notionhq/notion-mcp | Memory interface | ✅ |
| NIST MCP | custom (our build) | ChE thermochemistry | ✅ |
| PubChem MCP | custom (our build) | Chemical properties | ✅ |
| Eng Units MCP | custom (our build) | Unit conversion | ✅ |
| Bifrost Gateway | open source Apache 2.0 | All MCP management | ✅ |
