# ULTRON v3 — TECHNICAL PLAN
**References:** Epic Brief v3.0, Core Flows v3.0  
**Status:** Complete  
**Stack:** Python + TypeScript + React  

---

## Directory Structure

```
ultron/
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── pyproject.toml
├── package.json
│
├── cloudflare_worker/          ← Brain entry point (TypeScript)
│   ├── src/
│   │   ├── index.ts            ← Main Worker handler
│   │   ├── router.ts           ← Route incoming messages
│   │   ├── kv_client.ts        ← Cloudflare KV operations
│   │   ├── qstash_client.ts    ← QStash message queue
│   │   └── types.ts            ← Shared TypeScript types
│   ├── wrangler.toml
│   └── package.json
│
├── packages/
│   ├── brain/                  ← Core intelligence (Python)
│   │   ├── __init__.py
│   │   ├── mrkl_router.py      ← Task classification
│   │   ├── complexity_detector.py
│   │   ├── instant_mode.py     ← Single-call fast responses
│   │   ├── deep_mode.py        ← Full pipeline responses
│   │   │
│   │   ├── moa/                ← Mixture of Agents
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py ← MoA coordinator
│   │   │   ├── proposers.py    ← 8 role-based proposers
│   │   │   ├── roles.py        ← Role definitions + prompts
│   │   │   └── parallel_runner.py
│   │   │
│   │   ├── thinking/           ← Advanced reasoning
│   │   │   ├── __init__.py
│   │   │   ├── chain_of_thought.py
│   │   │   ├── tree_of_thoughts.py
│   │   │   ├── graph_of_thoughts.py
│   │   │   └── lats.py         ← Language Agent Tree Search
│   │   │
│   │   ├── quality/            ← Quality assurance
│   │   │   ├── __init__.py
│   │   │   ├── self_consistency.py
│   │   │   ├── prm_scorer.py   ← Process Reward Models
│   │   │   ├── constitutional_critic.py
│   │   │   ├── critic.py       ← Sonnet critic
│   │   │   ├── synthesizer.py  ← Gemini 3 Pro
│   │   │   ├── confidence_checker.py
│   │   │   └── ai_judge.py     ← 3-layer final judge
│   │   │
│   │   └── spec_engine/        ← Traycer-style planning
│   │       ├── __init__.py
│   │       ├── generator.py    ← Runs 7 prompts
│   │       ├── validator.py    ← Cross-artifact check
│   │       ├── notion_publisher.py
│   │       └── prompts/
│   │           ├── 01_epic_brief.txt
│   │           ├── 02_core_flows.txt
│   │           ├── 03_tech_plan.txt
│   │           ├── 04_arch_validation.txt
│   │           ├── 05_ticket_breakdown.txt
│   │           ├── 06_cross_artifact.txt
│   │           └── 07_ultron_brief.txt
│   │
│   ├── key_rotation/           ← API key management
│   │   ├── __init__.py
│   │   ├── pool.py             ← Key pool management
│   │   ├── quota_brain.py      ← Usage tracking + routing
│   │   ├── admission_control.py ← Token bucket algorithm
│   │   ├── provider_clients.py ← API client per provider
│   │   └── models.py           ← Key + quota data models
│   │
│   ├── memory/                 ← 5-tier memory system
│   │   ├── __init__.py
│   │   ├── core_memory.py      ← Tier 0: Always in context
│   │   ├── working_memory.py   ← Tier 1: Current session
│   │   ├── passport.py         ← Context passport assembly
│   │   ├── insight/            ← Tier 2: Semantic memory
│   │   │   ├── __init__.py
│   │   │   ├── mem0_client.py  ← Atomic fact extraction
│   │   │   ├── zilliz_client.py ← Vector store
│   │   │   ├── cognee_client.py ← Knowledge graph
│   │   │   ├── raptor.py       ← Hierarchical compression
│   │   │   ├── zep_client.py   ← Temporal + episodic
│   │   │   └── ace_loop.py     ← Lesson playbook
│   │   ├── archival/           ← Tier 3: Lossless
│   │   │   ├── __init__.py
│   │   │   ├── jsonl_writer.py
│   │   │   └── github_backup.py
│   │   ├── structured/         ← Tier 4: Human-readable
│   │   │   ├── __init__.py
│   │   │   ├── notion_client.py
│   │   │   └── deepwiki.py
│   │   ├── pruning.py          ← 3 pruning policies
│   │   ├── fabric.py           ← Real-time push
│   │   └── consolidation.py    ← Nightly job
│   │
│   ├── tools/                  ← Tool registry
│   │   ├── __init__.py
│   │   ├── registry.py         ← All tools registered
│   │   ├── dispatcher.py       ← Route to correct tool
│   │   ├── permissions.py      ← Permission matrix
│   │   ├── base_tool.py        ← Base class + Pydantic
│   │   │
│   │   ├── documents/
│   │   │   ├── pdf_tool.py
│   │   │   ├── word_tool.py
│   │   │   ├── excel_tool.py
│   │   │   ├── pptx_tool.py
│   │   │   ├── latex_tool.py
│   │   │   └── fast_io_client.py
│   │   │
│   │   ├── code/
│   │   │   ├── writer_tool.py
│   │   │   ├── runner_tool.py  ← E2B sandbox
│   │   │   ├── tester_tool.py
│   │   │   ├── linter_tool.py
│   │   │   └── git_tool.py
│   │   │
│   │   ├── web/
│   │   │   ├── playwright_tool.py
│   │   │   ├── firecrawl_tool.py
│   │   │   ├── apify_tool.py
│   │   │   ├── arxiv_tool.py
│   │   │   └── search_tool.py
│   │   │
│   │   ├── che/                ← Chemical Engineering
│   │   │   ├── mass_balance.py
│   │   │   ├── thermo_calc.py
│   │   │   ├── vle_calc.py
│   │   │   ├── mccabe_thiele.py
│   │   │   ├── nist_mcp.py
│   │   │   ├── pubchem_mcp.py
│   │   │   ├── unit_convert.py
│   │   │   └── plot_engineering.py
│   │   │
│   │   └── communication/
│   │       ├── discord_tool.py
│   │       ├── notion_tool.py
│   │       ├── n8n_tool.py
│   │       └── fast_io_tool.py
│   │
│   ├── mcp_gateway/            ← Bifrost + MCP servers
│   │   ├── __init__.py
│   │   ├── bifrost_client.py   ← Central gateway
│   │   ├── servers.py          ← Server registry
│   │   ├── health_monitor.py
│   │   └── auth_manager.py
│   │
│   ├── computer_use/           ← Agent S3 + GUI control
│   │   ├── __init__.py
│   │   ├── agent_s3.py         ← Main controller
│   │   ├── vision.py           ← Gemini Vision integration
│   │   ├── ui_tars.py          ← Pixel grounding model
│   │   ├── xvfb_manager.py     ← Virtual display
│   │   └── action_executor.py
│   │
│   ├── circuit_breaker/        ← Infinite loop prevention
│   │   ├── __init__.py
│   │   ├── breaker.py          ← Main circuit breaker
│   │   ├── semantic_hash.py    ← Action fingerprint ring
│   │   ├── entropy_detector.py ← Progress entropy
│   │   ├── state_diff.py       ← Git diff monitor
│   │   └── budget_guardian.py  ← Token budget
│   │
│   ├── entropy_engine/         ← Quality management
│   │   ├── __init__.py
│   │   ├── engine.py           ← Main entropy orchestrator
│   │   ├── memory_entropy.py
│   │   ├── codebase_entropy.py
│   │   ├── task_entropy.py
│   │   ├── bug_entropy.py
│   │   ├── decision_diversity.py
│   │   └── system_health.py
│   │
│   ├── self_improvement/       ← AlphaEvolve + self-mod
│   │   ├── __init__.py
│   │   ├── alphaevolve/
│   │   │   ├── evolver.py
│   │   │   ├── evaluator.py
│   │   │   └── crossover.py
│   │   ├── self_modification/
│   │   │   ├── engine.py
│   │   │   ├── whitelist.py
│   │   │   └── canary.py
│   │   ├── reflexion.py        ← Failure analysis
│   │   ├── ace_curator.py      ← Lesson extraction
│   │   └── aflow.py            ← Workflow optimization
│   │
│   ├── heartbeat/              ← Persistent loop
│   │   ├── __init__.py
│   │   ├── loop.py             ← Main 30-second loop
│   │   ├── scheduler.py        ← Task priority + scheduling
│   │   ├── watchdog.py         ← Self-healing monitor
│   │   └── remote_work.py      ← Long-running projects
│   │
│   ├── sub_agents/             ← Parallel sub-agent system
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── a2a_protocol.py     ← Agent-to-agent messaging
│   │   └── agent_factory.py
│   │
│   ├── observability/          ← Logging + monitoring
│   │   ├── __init__.py
│   │   ├── event_log.py        ← JSONL append-only log
│   │   ├── metrics.py          ← Performance tracking
│   │   ├── trace_propagation.py ← W3C trace IDs
│   │   └── replay_harness.py   ← VCR.py for debugging
│   │
│   └── discord/                ← Discord interface
│       ├── __init__.py
│       ├── bot.py              ← Discord bot main
│       ├── message_handler.py
│       ├── formatter.py        ← Message formatting
│       └── escalation.py       ← Ghost alert system
│
├── website/                    ← Master control panel (React)
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Chat.tsx
│   │   │   ├── Projects.tsx
│   │   │   ├── Memory.tsx
│   │   │   └── Settings.tsx
│   │   ├── components/
│   │   │   ├── KeyManager.tsx  ← Paste API keys here
│   │   │   ├── QuotaDisplay.tsx
│   │   │   ├── TaskList.tsx
│   │   │   └── EntropyDashboard.tsx
│   │   └── api/
│   │       └── ultron_client.ts
│   ├── package.json
│   └── vite.config.ts
│
├── skills/                     ← Skills library
│   ├── .agents/
│   │   └── skills/
│   │       ├── che/
│   │       │   ├── mass_balance/SKILL.md
│   │       │   ├── thermo/SKILL.md
│   │       │   ├── distillation/SKILL.md
│   │       │   ├── latex_report/SKILL.md
│   │       │   └── unit_conversion/SKILL.md
│   │       ├── documents/
│   │       │   ├── pdf/SKILL.md
│   │       │   ├── word/SKILL.md
│   │       │   ├── excel/SKILL.md
│   │       │   ├── pptx/SKILL.md
│   │       │   └── latex/SKILL.md
│   │       └── coding/
│   │           ├── python/SKILL.md
│   │           ├── react/SKILL.md
│   │           └── api_design/SKILL.md
│
├── memory/                     ← Persistent memory storage
│   ├── archive/                ← JSONL lossless archive
│   ├── skills/                 ← Auto-generated skill files
│   └── playbooks/              ← ACE lesson playbooks
│
└── infrastructure/
    ├── docker-compose.yml
    ├── clawcloud/
    │   ├── instance1.dockerfile ← Brain + orchestrator
    │   ├── instance2.dockerfile ← Memory + MCP
    │   └── instance3.dockerfile ← Computer use
    └── scripts/
        ├── deploy.sh
        ├── setup_accounts.sh
        └── health_check.sh
```

---

## Database Schema

### Upstash Redis Key Schema

```
# Key Rotation Pool
key_pool:{provider}:{model}         SET of key_ids
key_status:{provider}:{key_id}      STRING: "available" | "exhausted"
key_quota:{provider}:{key_id}       STRING: remaining quota count
key_quota_reset:{provider}:{key_id} STRING: Unix timestamp of reset

# Task Management
task:{task_id}                      HASH: mission, status, phase, created_at
task_queue                          SORTED SET: task_id → entropy_score
checkpoint:{task_id}                HASH: full task state snapshot

# Circuit Breaker
circuit_breaker:{agent_id}          HASH: state, trip_count, last_trip
cb_action_ring:{agent_id}           LIST: last 10 action fingerprints
cb_progress:{agent_id}              HASH: tokens_used, last_quality_score

# Memory - Tier 0 Core
core_memory:ghost                   HASH: name, context, current_project, today_priorities
core_memory:current_session         HASH: last_50_interactions, active_files, agent_states

# Quota Brain
quota_summary:{provider}            HASH: total_available, total_used, reset_time
quota_recommendation                HASH: moa_depth, self_consistency, research_enabled

# Sub-Agents  
subagent:{agent_id}:state           HASH: status, task, context_key
subagent:{agent_id}:messages        LIST: A2A messages queue

# Presence / Health
heartbeat:last_ping                 STRING: Unix timestamp
clawcloud:instance:{n}:health       STRING: "alive" | "dead"
system:entropy_score                STRING: current system entropy 0-100
```

### Zilliz Collections Schema

```python
# Collection 1: episodic_memory (insight tier)
schema = {
    "id": "VARCHAR(36)",          # UUID
    "session_id": "VARCHAR(36)",  # Which session created this
    "agent_id": "VARCHAR(50)",    # Which agent
    "timestamp": "INT64",         # Unix timestamp
    "episode_id": "VARCHAR(36)",  # Temporal grouping (Zep)
    "task_type": "VARCHAR(50)",   # CODING|DOCUMENT|RESEARCH|CHE|etc
    "entity": "VARCHAR(200)",     # Primary entity (Ghost, Steve, auth.py)
    "fact_type": "VARCHAR(50)",   # relationship|event|property|lesson
    "content": "VARCHAR(2000)",   # The atomic fact or insight
    "importance": "FLOAT",        # 0-1 importance score
    "access_count": "INT32",      # How many times retrieved
    "embedding": "FLOAT_VECTOR",  # 768-dimensional
}
# Index: IVF_FLAT on embedding, FLAT on task_type+entity

# Collection 2: knowledge_graph_nodes
schema = {
    "id": "VARCHAR(36)",
    "entity_name": "VARCHAR(200)",
    "entity_type": "VARCHAR(50)",   # person|file|concept|project
    "properties": "VARCHAR(2000)",  # JSON string of properties
    "embedding": "FLOAT_VECTOR",    # 768-dimensional
}

# Collection 3: archival_index (pointers to GitHub JSONL)
schema = {
    "id": "VARCHAR(36)",
    "task_id": "VARCHAR(36)",
    "action_type": "VARCHAR(50)",
    "timestamp": "INT64",
    "github_line": "INT64",         # Line in archive JSONL
    "summary_embedding": "FLOAT_VECTOR",
}

# Collection 4: skill_playbooks
schema = {
    "id": "VARCHAR(36)",
    "task_type": "VARCHAR(50)",
    "lesson": "VARCHAR(2000)",
    "success_rate": "FLOAT",
    "embedding": "FLOAT_VECTOR",
}
```

---

## API Contracts

### Cloudflare Worker Endpoints

```typescript
// POST /discord/webhook
// Called by Discord when Ghost sends a message
Request: {
    type: number,          // Discord interaction type
    data: {
        content: string,   // Ghost's message text
        author_id: string, // Ghost's Discord user ID
        channel_id: string
    }
}
Response: {
    type: number,          // Discord response type
    data: {
        content: string    // Ultron's response (if instant)
    }
}
// If deep mode: respond with "thinking..." immediately,
// send actual response via Discord webhook when complete

// POST /webhook/qstash
// QStash delivers task to ClawCloud
Request: {
    task_id: string,
    task_type: string,
    payload: object,
    priority: number
}
Response: 200 OK | 500 Error

// GET /health
Response: {
    status: "alive",
    uptime: number,
    version: string
}

// POST /secrets/save
// Called by website settings tab
Request: {
    provider: string,   // "gemini" | "groq" | etc
    key_id: string,     // user-defined identifier
    api_key: string,    // encrypted before sending
    metadata: object
}
Response: {
    success: boolean,
    message: string,
    quota_available: number
}
```

### Internal Python API (ClawCloud)

```python
# brain/mrkl_router.py
class MRKLRouter:
    def classify(self, message: str, context: dict) -> TaskClassification:
        """
        Returns: TaskClassification(
            task_type: Literal["CONVERSATIONAL", "DOCUMENT_CREATION", 
                               "CODE_TASK", "RESEARCH_TASK", "CHE_TASK",
                               "REMOTE_WORK", "COMPLEX", "COMPUTER_USE",
                               "SELF_IMPROVEMENT"],
            confidence: float,      # 0-1
            requires_deep_mode: bool,
            entropy_score: float,   # 0-100
            estimated_tokens: int
        )
        """

# brain/moa/orchestrator.py
class MoAOrchestrator:
    async def run(self, task: Task, mode: Literal["instant", "deep"]) -> Result:
        """
        instant mode: single model call, <10 seconds
        deep mode: full 8-proposer pipeline, 3-5 minutes
        Returns: Result(content, confidence, quality_score, sources)
        """

# key_rotation/pool.py
class KeyPool:
    def select_best_key(self, provider: str, model: str) -> str:
        """O(log n) key selection using Redis sorted set"""
    
    def rotate_key(self, exhausted_key_id: str) -> str:
        """Mark exhausted, select next, pre-warm"""
    
    def add_key(self, provider: str, key: str, metadata: dict) -> bool:
        """Add new key from website settings"""

# memory/passport.py  
class PassportAssembler:
    async def assemble(self, task_id: str) -> Passport:
        """
        Assembles context passport from all memory tiers.
        Returns 800-token structured context.
        Parallel: Redis + Zilliz + GitHub (if needed)
        Max latency: 200ms
        """

# circuit_breaker/breaker.py
class CircuitBreaker:
    def check(self, agent_id: str, action: dict, 
              tokens: int, progress: float) -> Literal["PROCEED", "HALT", "ESCALATE"]:
        """O(log n). Called before EVERY agent action."""
```

---

## Environment Variables

```bash
# Cloudflare Worker
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_API_TOKEN=
KV_NAMESPACE_ID=           # Secrets storage

# Discord
DISCORD_BOT_TOKEN=
DISCORD_CHANNEL_ID=        # Ghost's DM channel
DISCORD_WEBHOOK_URL=       # For sending messages

# Upstash Redis
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=
UPSTASH_QSTASH_URL=
UPSTASH_QSTASH_TOKEN=

# Zilliz (one per account - loaded dynamically from KV)
ZILLIZ_CLUSTER_URL_1=
ZILLIZ_API_KEY_1=
# ... up to account 15

# Notion
NOTION_TOKEN=
NOTION_DATABASE_ID=        # Projects database
NOTION_MEMORY_PAGE_ID=     # Memory pages root

# Puter.js
PUTER_AUTH_TOKEN=          # For Claude Opus calls

# Fast.io
FASTIO_API_KEY=

# GitHub
GITHUB_TOKEN=              # Ultron's agent account
GITHUB_REPO=               # ghostdriveg1/ultron
GITHUB_MEMORY_REPO=        # ghostdriveg1/ultron-memory

# ClawCloud
CLAWCLOUD_INSTANCE_1_URL=
CLAWCLOUD_INSTANCE_2_URL=
CLAWCLOUD_INSTANCE_3_URL=

# LLM Keys (loaded dynamically from KV in production)
# These are examples for local development only
GEMINI_API_KEY_DEV=
GROQ_API_KEY_DEV=

# E2B
E2B_API_KEY=

# MCP Servers
FIRECRAWL_API_KEY=
APIFY_API_KEY=
N8N_WEBHOOK_URL=

# App Configuration
ENVIRONMENT=production     # development | production
LOG_LEVEL=INFO
MAX_CONCURRENT_AGENTS=5
DEFAULT_TIMEOUT_SECONDS=300
HEARTBEAT_INTERVAL_SECONDS=30
```

---

## External Dependencies

### Python (packages/requirements.txt)

```txt
# Core
langchain==0.3.*
langgraph==0.2.*
langchain-google-genai==2.*
langchain-groq==0.1.*

# Memory
mem0ai==0.1.*
cognee==0.1.*
upstash-redis==1.*

# Tools
playwright==1.40.*
python-docx==1.1.*
openpyxl==3.1.*
python-pptx==0.6.*
reportlab==4.*
WeasyPrint==61.*

# Chemical Engineering
CoolProp==6.*
chemicals==1.*
pint==0.23.*
scipy==1.12.*
numpy==1.26.*
matplotlib==3.8.*
plotly==5.18.*

# Computer Use
pyautogui==0.9.*
Pillow==10.*

# Observability
structlog==24.*
opentelemetry-sdk==1.*

# MCP
mcp==1.*

# Utils
pydantic==2.*
httpx==0.27.*
asyncio-throttle==1.*
python-dotenv==1.*
tenacity==8.*           # Retry logic
```

### TypeScript (cloudflare_worker/package.json)

```json
{
  "dependencies": {
    "@cloudflare/workers-types": "^4.0.0",
    "hono": "^4.0.0"
  }
}
```

### Website (website/package.json)

```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-router-dom": "^6.0.0",
    "tailwindcss": "^3.0.0",
    "@tanstack/react-query": "^5.0.0",
    "recharts": "^2.0.0",
    "lucide-react": "^0.380.0"
  }
}
```

---

## MCP Server Registry

```python
MCP_SERVERS = {
    # Code & Development
    "github": {
        "url": "https://github.mcp.anthropic.com/sse",
        "capabilities": ["read_repo", "create_pr", "commit", "create_issue"],
        "auth": "GITHUB_TOKEN"
    },
    "semgrep": {
        "url": "npx @semgrep/mcp",
        "capabilities": ["security_scan", "code_analysis"],
        "auth": None  # Free for open source
    },
    "context7": {
        "url": "npx @upstash/context7-mcp",
        "capabilities": ["library_docs", "api_reference"],
        "auth": None
    },
    "run_python": {
        "url": "npx run-python-mcp",
        "capabilities": ["execute_python", "sandbox_run"],
        "auth": None
    },
    
    # Web & Research
    "playwright": {
        "url": "npx @playwright/mcp",
        "capabilities": ["browse", "click", "type", "screenshot"],
        "auth": None
    },
    "firecrawl": {
        "url": "npx firecrawl-mcp",
        "capabilities": ["url_to_markdown", "scrape", "crawl"],
        "auth": "FIRECRAWL_API_KEY"
    },
    "apify": {
        "url": "npx apify-mcp",
        "capabilities": ["scrape_structured", "3000_actors"],
        "auth": "APIFY_API_KEY"
    },
    "arxiv": {
        "url": "npx arxiv-mcp-server",
        "capabilities": ["search_papers", "get_abstract", "download_pdf"],
        "auth": None
    },
    
    # Storage & Data
    "fast_io": {
        "url": "npx fast-io-mcp",
        "capabilities": ["save_file", "get_file", "list_files", "semantic_search"],
        "auth": "FASTIO_API_KEY",
        "storage": "50GB_free"
    },
    "google_db": {
        "url": "npx @google/mcp-toolbox-for-databases",
        "capabilities": ["query_sql", "safe_database_access"],
        "auth": None
    },
    
    # Workflow
    "notion": {
        "url": "https://notion.mcp.anthropic.com/sse",
        "capabilities": ["read_page", "create_page", "update_page", "query_database"],
        "auth": "NOTION_TOKEN"
    },
    "n8n": {
        "url": "self_hosted_clawcloud",  # Self-hosted for free
        "capabilities": ["trigger_workflow", "create_workflow"],
        "auth": "N8N_API_KEY"
    },
    
    # ChE-Specific (Custom Built)
    "nist_chemistry": {
        "url": "local://nist_mcp",
        "capabilities": ["get_thermochemical_data", "search_compound"],
        "auth": None  # NIST API is free
    },
    "pubchem": {
        "url": "local://pubchem_mcp",
        "capabilities": ["get_compound_properties", "search_by_name"],
        "auth": None  # PubChem API is free
    },
    "engineering_units": {
        "url": "local://units_mcp",
        "capabilities": ["convert_units", "list_units"],
        "auth": None
    }
}
```

---

## WebSocket Events (QStash Message Format)

```python
# Message schema for all QStash messages
class UltronMessage(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    message_type: Literal[
        "TASK_NEW",          # Ghost sent new task
        "TASK_UPDATE",       # Task progress update  
        "TOOL_CALL",         # Execute a tool
        "TOOL_RESULT",       # Tool execution result
        "MEMORY_WRITE",      # Write to memory
        "MEMORY_READ",       # Read from memory
        "AGENT_SPAWN",       # Create sub-agent (A2A)
        "AGENT_RESULT",      # Sub-agent completed (A2A)
        "CIRCUIT_TRIP",      # Circuit breaker triggered
        "GHOST_ALERT",       # Send Discord message to Ghost
        "SELF_MOD_TRIGGER",  # Start self-modification
        "HEARTBEAT",         # Regular heartbeat check
    ]
    priority: int = Field(ge=0, le=100)  # Higher = more urgent
    payload: dict
    checkpoint_key: Optional[str]  # Redis key for state restore
    deadline: Optional[datetime]
    callback_channel: Literal["discord", "notion", "github", "none"]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    trace_id: str = Field(default_factory=lambda: str(uuid4()))  # W3C trace
```

---

## Security Architecture

```python
# Permission matrix (enforced in tools/permissions.py)
PERMISSION_MATRIX = {
    # Tool name: (permission_level, requires_ghost_confirm, can_be_reverted)
    "read_file":        ("READ",   False, True),
    "search_memory":    ("READ",   False, True),
    "browse_web":       ("READ",   False, True),
    "write_code":       ("WRITE",  False, True),
    "create_file":      ("WRITE",  False, True),
    "update_file":      ("WRITE",  False, True),
    "commit_github":    ("WRITE",  False, True),
    "create_pr":        ("WRITE",  False, True),
    "delete_file":      ("DELETE", True,  True),
    "delete_branch":    ("DELETE", True,  True),
    "deploy_pages":     ("DEPLOY", True,  False),
    "deploy_firebase":  ("DEPLOY", True,  False),
    "delete_repo":      ("NEVER",  True,  False),   # Hard-blocked
    "delete_account":   ("NEVER",  True,  False),   # Hard-blocked
}

# Sacred files (never self-modified)
SACRED_FILES = [
    "packages/brain/core/session.py",
    "packages/memory/core/restore.py",
    "packages/key_rotation/pool.py",
    "packages/heartbeat/watchdog.py",
    "packages/circuit_breaker/breaker.py",
    "packages/brain/security/",
    "packages/brain/moa/roles.py",  # System prompts locked
]

# Self-modification whitelist
SELF_MOD_ALLOWED = [
    "packages/tools/",
    "packages/brain/moa/proposers.py",  # Proposer prompts
    "packages/brain/spec_engine/prompts/",
    "packages/brain/thinking/",
    "packages/key_rotation/quota_brain.py",
    "packages/entropy_engine/",
    "packages/self_improvement/",
    "skills/",
    "memory/playbooks/",
]
```
