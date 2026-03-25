# ULTRON v3 — COMPLETE TICKET BREAKDOWN
**Total Tickets:** 40  
**References:** Epic Brief, Core Flows, Tech Plan  

---

# T1 — Repository Structure + Environment Setup

**Complexity:** LOW  
**Priority:** P0 (blocks everything)  
**Depends on:** Nothing  
**Blocks:** T2, T3, T4, T5  

## Context
Create the complete Ultron repository structure, all configuration files, Docker setup, and development environment. This is the foundation every other ticket builds on.

## Files to Create

| File | Purpose |
|---|---|
| `.gitignore` | Exclude: .env, __pycache__, node_modules, .venv, *.pyc |
| `pyproject.toml` | Python workspace configuration |
| `package.json` | Root npm workspace |
| `docker-compose.yml` | 3 ClawCloud-equivalent services locally |
| `.env.example` | All 40+ environment variables documented |
| `README.md` | Project overview, setup instructions |
| `infrastructure/scripts/setup_dev.sh` | One-command dev setup |
| All directories | Create entire directory tree from Tech Plan |

## docker-compose.yml Services

```yaml
services:
  brain:          # packages/brain - Python orchestrator
    build: ./packages/brain
    ports: ["8000:8000"]
    env_file: .env
    volumes: ["./memory:/app/memory"]
    
  worker:         # cloudflare_worker - local simulation
    build: ./cloudflare_worker
    ports: ["8787:8787"]
    
  website:        # website - React
    build: ./website
    ports: ["3000:3000"]
    
  redis:          # Local Redis for development
    image: redis:7-alpine
    ports: ["6379:6379"]
```

## Acceptance Criteria
- [ ] `git clone` + `./setup_dev.sh` produces running system in <5 minutes
- [ ] All directories from Tech Plan exist
- [ ] `.env.example` documents every variable with description
- [ ] `docker-compose up` starts all services with no errors
- [ ] `pytest packages/` runs and finds 0 tests (not fails, finds 0)
- [ ] README explains what Ultron is and how to set it up

## Edge Cases
- Developer on Windows: use WSL2, document in README
- Missing Python version: pyproject.toml specifies `requires-python = ">=3.11"`

---

# T2 — Cloudflare Worker Brain Entry Point

**Complexity:** MEDIUM  
**Priority:** P0  
**Depends on:** T1  
**Blocks:** T3, T5, T35  

## Context
The Cloudflare Worker is the first point of contact for all incoming messages. It receives Discord webhooks, routes to ClawCloud, and returns responses. It is the only component deployed to Cloudflare's global edge network — meaning it responds from the datacenter closest to Ghost, anywhere in the world.

## Files to Create

| File | Purpose |
|---|---|
| `cloudflare_worker/src/index.ts` | Main Worker export + Hono app |
| `cloudflare_worker/src/router.ts` | Route: /discord /webhook /health /secrets |
| `cloudflare_worker/src/kv_client.ts` | Cloudflare KV read/write with encryption |
| `cloudflare_worker/src/qstash_client.ts` | Forward tasks to ClawCloud via QStash |
| `cloudflare_worker/src/auth.ts` | Verify Discord signatures |
| `cloudflare_worker/src/types.ts` | TypeScript interfaces |
| `cloudflare_worker/wrangler.toml` | Cloudflare deployment config |

## Implementation Plan

### index.ts
```typescript
import { Hono } from 'hono'
import { discordRouter } from './router'

const app = new Hono<{ Bindings: Env }>()

app.route('/discord', discordRouter)
app.get('/health', (c) => c.json({ status: 'alive', version: '3.0' }))
app.post('/secrets/save', handleSecretSave)

export default app
```

### router.ts
```typescript
// POST /discord/webhook
// 1. Verify Discord signature (crypto.subtle)
// 2. If PING: return PONG immediately
// 3. Extract message content and author
// 4. Check author is Ghost (whitelist from KV)
// 5. Classify: instant vs deep mode
// 6. Instant: forward to brain, wait, return response
// 7. Deep: send "thinking..." to Discord, 
//          enqueue to QStash, return 200
```

### kv_client.ts
```typescript
// All values AES-256-GCM encrypted before KV storage
// Key: derived from WORKER_ENCRYPTION_KEY env var
async function getSecret(key: string): Promise<string>
async function setSecret(key: string, value: string): Promise<void>
async function listSecrets(prefix: string): Promise<string[]>
async function deleteSecret(key: string): Promise<void>
```

## Acceptance Criteria
- [ ] `wrangler dev` starts worker locally
- [ ] Discord PING returns PONG in <100ms
- [ ] Non-Ghost messages are silently ignored (no error, no response)
- [ ] Simple message → instant response in <15 seconds
- [ ] Complex message → "thinking..." response, task enqueued
- [ ] All secrets encrypted in KV (verify with `wrangler kv:key list`)
- [ ] `/health` returns 200 with version

## Edge Cases
- Discord signature verification fails: return 401, log attempt
- QStash unreachable: retry 3x with exponential backoff, then Discord alert
- KV write fails: retry once, then log critical error

---

# T3 — Discord Bot Interface

**Complexity:** MEDIUM  
**Priority:** P0  
**Depends on:** T1, T2  
**Blocks:** T5, T33  

## Context
The Discord bot is Ghost's primary interface to Ultron from any device. It must handle: receiving messages from Ghost, formatting and sending responses, splitting long responses (>2000 chars), sending proactive updates, and the escalation alert system.

## Files to Create

| File | Purpose |
|---|---|
| `packages/discord/bot.py` | Discord bot main with py-cord |
| `packages/discord/message_handler.py` | Process incoming messages |
| `packages/discord/formatter.py` | Format responses for Discord |
| `packages/discord/escalation.py` | Ghost alert system |
| `packages/discord/proactive.py` | Morning briefings, weekly reports |

## Implementation Plan

### bot.py
```python
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

@bot.event
async def on_message(message):
    if message.author.id != GHOST_DISCORD_ID:
        return  # Ignore non-Ghost messages
    if message.author.bot:
        return  # Ignore bot messages
    
    # Forward to Cloudflare Worker via HTTP
    # Worker routes to brain
    # Response comes back via webhook
    
@bot.slash_command(name="status")
async def status(ctx):
    """Show Ultron system status"""
    # Returns: uptime, active tasks, quota remaining, entropy score
```

### formatter.py
```python
def format_response(content: str, max_length: int = 2000) -> list[str]:
    """Split long responses into multiple Discord messages"""
    # Respect word boundaries
    # Add part numbers if split: [1/3], [2/3], [3/3]
    # Preserve code blocks (don't split inside ```)
    # Return list of message strings

def format_file_notification(filename: str, fast_io_url: str, github_url: str) -> str:
    """Format file delivery notification with links"""

def format_progress_update(task: str, phase: str, percent: int) -> str:
    """Format milestone progress update"""

def format_escalation(reason: str, attempts: int, context: dict) -> str:
    """Format circuit breaker escalation with options"""
```

### escalation.py
```python
async def send_ghost_alert(
    alert_type: Literal["circuit_breaker", "quota_critical", "error", "milestone"],
    context: dict,
    options: list[str] = None  # ["RETRY", "SKIP", "ABORT"]
) -> None:
    """Send structured alert to Ghost with action options"""
    # Format message
    # Send to Ghost's DM
    # Wait for response (timeout: 24 hours)
    # On response: dispatch to appropriate handler
```

## Acceptance Criteria
- [ ] Ghost sends "hello" → Ultron responds within 15 seconds
- [ ] Response >2000 chars → split into multiple messages with part numbers
- [ ] Code blocks never split across messages
- [ ] Morning briefing sent at 8AM Ghost's timezone
- [ ] Escalation message includes exactly 3 action options (RETRY/SKIP/ABORT)
- [ ] Ghost replying "RETRY" resumes the halted task

---

# T4 — Database Connections (Redis + Zilliz + Notion)

**Complexity:** MEDIUM  
**Priority:** P0  
**Depends on:** T1  
**Blocks:** T6, T9, T13  

## Context
Establish all database connections with proper connection pooling, retry logic, and health monitoring. All connections must gracefully handle service outages and reconnect automatically.

## Files to Create

| File | Purpose |
|---|---|
| `packages/infrastructure/redis_client.py` | Upstash Redis connection |
| `packages/infrastructure/zilliz_client.py` | Zilliz vector DB pool |
| `packages/infrastructure/notion_client.py` | Notion API client |
| `packages/infrastructure/health_check.py` | Monitor all connections |
| `packages/infrastructure/connection_pool.py` | Manage multiple accounts |

## Implementation Plan

### redis_client.py
```python
from upstash_redis import Redis
from tenacity import retry, stop_after_attempt, wait_exponential

class UltronRedis:
    def __init__(self):
        self._client = Redis(
            url=os.getenv("UPSTASH_REDIS_REST_URL"),
            token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
        )
    
    @retry(stop=stop_after_attempt(3), 
           wait=wait_exponential(multiplier=1, min=1, max=10))
    async def get(self, key: str) -> Optional[str]: ...
    
    async def set(self, key: str, value: str, ex: int = None) -> bool: ...
    async def hset(self, name: str, mapping: dict) -> int: ...
    async def zadd(self, name: str, mapping: dict) -> int: ...
    # ... all required operations
```

### zilliz_client.py
```python
from pymilvus import connections, Collection

class ZillizPool:
    """Manages connections to all 15 Zilliz accounts"""
    
    def __init__(self):
        self.accounts = self._load_accounts_from_kv()
        self.collections = {}
        self._connect_all()
    
    def _load_accounts_from_kv(self) -> list[dict]:
        """Load all Zilliz credentials from Cloudflare KV"""
    
    def get_collection_with_space(
        self, 
        collection_name: str,
        required_slots: int = 100
    ) -> Collection:
        """Returns collection with most available capacity"""
    
    async def insert(self, collection: str, data: list[dict]) -> list[str]:
        """Insert with automatic account rotation when full"""
    
    async def search(
        self,
        collection: str,
        query_vector: list[float],
        filter_expr: str = None,
        top_k: int = 10
    ) -> list[dict]:
        """Hybrid search: vector + metadata filter"""
```

## Acceptance Criteria
- [ ] Redis ping succeeds within 500ms
- [ ] All 15 Zilliz accounts connect on startup
- [ ] Connection failure → automatic retry with backoff
- [ ] After 3 failures → fallback to next account
- [ ] After all failures → Discord alert to Ghost
- [ ] Health check endpoint reports all connection statuses

---

# T5 — MRKL Router (Task Classification)

**Complexity:** HIGH  
**Priority:** P1  
**Depends on:** T2, T3, T4  
**Blocks:** T8, T27  

## Context
The MRKL Router is the brain's traffic director. It receives every message from Ghost and decides: which task type, which mode (instant/deep), which models, which tools, and what entropy score. This routing decision affects quality, speed, and quota usage for every single interaction.

## Files to Create

| File | Purpose |
|---|---|
| `packages/brain/mrkl_router.py` | Main routing logic |
| `packages/brain/complexity_detector.py` | Instant vs deep mode |
| `packages/brain/task_models.py` | Pydantic models for tasks |
| `packages/brain/instant_mode.py` | Fast single-call path |
| `packages/brain/deep_mode.py` | Full pipeline path |

## Implementation Plan

### mrkl_router.py
```python
class MRKLRouter:
    
    TASK_TYPES = {
        "CONVERSATIONAL": {
            "description": "Simple question, greeting, clarification",
            "examples": ["what is osmosis", "hello", "what time is it"],
            "mode": "instant",
            "models": ["gemini-2.5-flash"],
            "max_tokens": 1000
        },
        "DOCUMENT_CREATION": {
            "description": "Create PDF, Word, Excel, PowerPoint, LaTeX",
            "examples": ["write a lab report", "create a presentation"],
            "mode": "deep",
            "models": ["gemini-2.5-pro"],
            "tools": ["create_pdf", "create_word", "create_excel", "create_pptx"]
        },
        "CODE_TASK": {
            "description": "Write, debug, test, deploy code",
            "examples": ["build a website", "fix this bug", "write a Python script"],
            "mode": "deep",
            "models": ["deepseek-coder-v3", "gemini-2.5-pro"],
            "tools": ["write_code", "run_python", "run_tests", "commit_github"]
        },
        "RESEARCH_TASK": {
            "description": "Research, synthesis, literature review",
            "examples": ["research HCl absorption", "find papers on"],
            "mode": "deep",
            "models": ["grok-4.1", "gemini-2.5-pro"],
            "tools": ["search_arxiv", "browse_web", "parallel_research"]
        },
        "CHE_TASK": {
            "description": "Chemical engineering calculations",
            "examples": ["calculate mass balance", "McCabe-Thiele", "VLE"],
            "mode": "deep",
            "models": ["gemini-student-pro"],
            "tools": ["mass_balance", "thermo_calc", "nist_data"]
        },
        "REMOTE_WORK": {
            "description": "Long-running autonomous project",
            "examples": ["build X over 100 days", "continuously improve"],
            "mode": "deep",
            "models": ["all"],
            "triggers": ["spec_engine", "heartbeat_loop"]
        },
        "COMPLEX": {
            "description": "Multi-category, requires full Traycer Epic Flow",
            "examples": ["build an operating system", "create a startup"],
            "mode": "deep",
            "triggers": ["spec_engine", "sub_agents"]
        },
        "COMPUTER_USE": {
            "description": "Requires GUI interaction",
            "examples": ["open HYSYS", "use this website", "click"],
            "mode": "deep",
            "tools": ["computer_use"]
        },
        "SELF_IMPROVEMENT": {
            "description": "Improve Ultron itself",
            "examples": ["improve your memory system", "optimize yourself"],
            "mode": "deep",
            "triggers": ["self_modification"]
        }
    }
    
    async def classify(self, message: str, context: dict) -> TaskClassification:
        """
        Two-stage classification:
        Stage 1: Fast keyword matching (O(1)) for obvious cases
        Stage 2: Gemini Flash classification for ambiguous cases
        
        Returns TaskClassification with confidence score.
        If confidence < 0.7: default to COMPLEX (safer).
        """
    
    async def compute_entropy(self, task: TaskClassification) -> float:
        """
        Entropy score 0-100:
        - Ambiguity of requirements (0-30 points)
        - Number of components involved (0-20 points)  
        - Reversibility of actions (0-20 points)
        - Unknown unknowns detected (0-30 points)
        
        >60: Deep mode
        >85: Opus gate required
        """
```

## Acceptance Criteria
- [ ] "What is osmosis?" → CONVERSATIONAL, instant mode, <5 seconds
- [ ] "Build a website" → CODE_TASK, deep mode, spec engine triggers
- [ ] "Calculate mass balance for HCl absorption" → CHE_TASK
- [ ] Classification confidence <0.7 → defaults to COMPLEX (not fails)
- [ ] Routing decision logged to JSONL with trace_id
- [ ] 100 random test messages classified correctly in <5 seconds total

---

# T6 — Key Rotation Pool

**Complexity:** HIGH ⭐ (RECOMMENDED FOR TRAYCER)  
**Priority:** P0  
**Depends on:** T4  
**Blocks:** T7, T8  

## Context
The key rotation pool is the most critical infrastructure component. Without reliable API key management, Ultron cannot make any LLM calls. It must handle: storing all keys encrypted, selecting the best key per request, rotating instantly when quota exhausts, pre-warming next keys, and scaling automatically as Ghost adds more keys via the dashboard.

This ticket is marked as a TRAYCER CANDIDATE because: key rotation logic has complex concurrency requirements (multiple agents calling simultaneously), race conditions are easy to introduce and hard to debug, and errors here affect the entire system's reliability.

## Files to Create

| File | Purpose |
|---|---|
| `packages/key_rotation/pool.py` | Key pool management (O(log n)) |
| `packages/key_rotation/quota_brain.py` | Usage tracking + smart routing |
| `packages/key_rotation/admission_control.py` | Token bucket algorithm |
| `packages/key_rotation/provider_clients.py` | One client class per LLM provider |
| `packages/key_rotation/models.py` | Pydantic data models |
| `packages/key_rotation/tests/test_pool.py` | Comprehensive tests |

## Implementation Plan

### models.py
```python
class APIKey(BaseModel):
    key_id: str               # UUID
    provider: str             # "gemini" | "groq" | "openrouter" | etc
    model: str                # "gemini-2.5-pro" | "llama-3.3-70b" | etc
    api_key: str              # Encrypted in storage, decrypted in memory
    daily_limit: int          # Max requests per day
    rpm_limit: int            # Max requests per minute
    reset_hour_utc: int       # Hour when daily quota resets (0-23)
    tier: Literal["instant", "smart", "frontier", "oracle"]
    added_at: datetime
    last_used: Optional[datetime]

class KeyStatus(BaseModel):
    key_id: str
    quota_remaining: int
    rpm_remaining: int
    is_available: bool
    exhausted_until: Optional[datetime]
    consecutive_failures: int  # Circuit breaker for bad keys

class PoolStatus(BaseModel):
    total_keys: int
    available_keys: int
    total_daily_capacity: int
    used_today: int
    recommended_moa_depth: int
    recommended_self_consistency: int
```

### pool.py
```python
class KeyPool:
    """
    Thread-safe key pool with O(log n) selection.
    Uses Redis sorted sets for quota tracking.
    Supports horizontal scaling (add keys at runtime).
    """
    
    def __init__(self, redis: UltronRedis):
        self.redis = redis
        self._local_cache = {}     # 60-second TTL local cache
        self._lock = asyncio.Lock()
    
    async def select_best_key(
        self, 
        provider: str,
        model: str,
        required_tier: str = "smart"
    ) -> APIKey:
        """
        O(log n) selection using Redis ZRANGEBYSCORE.
        
        Algorithm:
        1. Check local cache first (avoid Redis roundtrip)
        2. ZRANGEBYSCORE available_keys:{provider}:{model} 1 +inf LIMIT 0 1
           (sorted by quota_remaining, highest first)
        3. Verify key is not rate-limited (rpm check)
        4. Return key, update local cache
        5. Background: pre-warm key at position 2
        
        Raises: NoKeysAvailableError if all keys exhausted
        """
    
    async def rotate_key(
        self, 
        exhausted_key_id: str,
        error_type: Literal["429", "401", "500"]
    ) -> APIKey:
        """
        Called when a key fails.
        
        429 (rate limit): Mark unavailable until reset_time
        401 (auth error): Mark permanently invalid, alert Ghost
        500 (server error): Mark temporarily unavailable, retry in 60s
        
        Returns: next available key
        Raises: AllKeysExhaustedError if no alternatives
        """
    
    async def add_key(
        self, 
        provider: str, 
        model: str, 
        api_key: str
    ) -> bool:
        """
        Called when Ghost adds a key via website settings.
        
        1. Validate key with test call
        2. Detect daily limit and RPM limit automatically
        3. Encrypt and store in Cloudflare KV
        4. Add to Redis sorted set with full quota
        5. Trigger auto-scaling recalculation
        6. Return True if valid, False if invalid
        """
    
    async def update_usage(
        self, 
        key_id: str, 
        tokens_used: int,
        requests_used: int = 1
    ) -> KeyStatus:
        """
        Update usage tracking after each API call.
        Uses Redis HINCRBY for atomic increment.
        Returns updated status.
        """
    
    async def get_pool_status(self) -> PoolStatus:
        """
        Returns current pool status for dashboard display.
        Calculates recommended MoA depth and self-consistency level.
        """
```

### admission_control.py
```python
class TokenBucketAdmissionControl:
    """
    Prevents quota explosion via proactive rate limiting.
    Token bucket algorithm: tokens refill at constant rate.
    
    Prevents the $47,000 disaster (runaway loop burning quota).
    """
    
    def __init__(self, redis: UltronRedis):
        self.redis = redis
    
    async def check_and_consume(
        self,
        provider: str,
        model: str,
        estimated_tokens: int
    ) -> Literal["PROCEED", "QUEUE", "REJECT"]:
        """
        PROCEED: enough quota, consume it
        QUEUE: quota tight, add to deferred queue (try in 60s)
        REJECT: quota critically low, use fallback model
        
        Thresholds:
        >20% remaining: PROCEED
        5-20% remaining: QUEUE low-priority tasks
        <5% remaining: REJECT, force fallback
        """
    
    async def predict_exhaustion(
        self, 
        provider: str,
        model: str
    ) -> Optional[datetime]:
        """
        Based on usage rate in last 6 hours:
        Predict when current quota will exhaust.
        If <2 hours: pre-warm next key now.
        """
```

## Acceptance Criteria
- [ ] Select best key: <5ms (O(log n) verified by benchmark)
- [ ] Key exhausted → new key selected → task continues in <100ms total
- [ ] 10 concurrent agents calling pool simultaneously → no race conditions (test with asyncio.gather)
- [ ] Ghost adds key via website → available in pool within 10 seconds
- [ ] Invalid key → rejected at validation, never enters pool
- [ ] Pool status accurately reflects all 130 accounts
- [ ] Quota prediction triggers pre-warming with 2 hours lead time
- [ ] 429 response → key marked unavailable until exact reset time (from Retry-After header)
- [ ] All operations atomic (no partial updates possible)
- [ ] NEVER logs raw API keys (only key_ids)

## Edge Cases
- All keys exhausted simultaneously: cascade to next model tier, Discord alert
- Key reset time wrong: verify by making test call at predicted reset
- Concurrent rotation (2 agents exhaust same key simultaneously): Redis lock prevents double rotation
- Provider outage (all keys returning 500): activate fallback model tier, Discord alert

---

# T7 — Quota Brain

**Complexity:** MEDIUM  
**Priority:** P1  
**Depends on:** T6  
**Blocks:** T8, T10  

## Context
Quota Brain is the intelligent layer on top of the key pool. While the pool handles individual key mechanics, Quota Brain makes strategic decisions: how many MoA proposers to activate, whether to enable Parallel.ai research, whether to run self-consistency, and how to route task types to the right model tiers.

## Files to Create

| File | Purpose |
|---|---|
| `packages/key_rotation/quota_brain.py` | Strategic quota management |
| `packages/key_rotation/auto_scaler.py` | Dynamic depth adjustment |
| `packages/key_rotation/tier_router.py` | Route tasks to model tiers |

## Implementation Plan

```python
class QuotaBrain:
    
    SCALING_THRESHOLDS = {
        "ultra": {
            "daily_available": 20000,
            "moa_proposers": 8,
            "self_consistency": 10,
            "research": "all_tasks",
            "constitutional_rounds": 3,
            "alphaevolve": True
        },
        "high": {
            "daily_available": 10000,
            "moa_proposers": 8,
            "self_consistency": 5,
            "research": "complex_only",
            "constitutional_rounds": 2,
            "alphaevolve": "coding_only"
        },
        "medium": {
            "daily_available": 5000,
            "moa_proposers": 5,
            "self_consistency": 3,
            "research": "off",
            "constitutional_rounds": 1,
            "alphaevolve": False
        },
        "emergency": {
            "daily_available": 0,
            "moa_proposers": 1,
            "self_consistency": 1,
            "research": "off",
            "constitutional_rounds": 0,
            "alphaevolve": False
        }
    }
    
    async def get_execution_config(self, task: Task) -> ExecutionConfig:
        """
        Returns optimal execution configuration based on:
        - Current quota across all providers
        - Task type and priority
        - Time of day (save quota for Ghost's active hours)
        - Whether task is time-sensitive
        """
    
    async def route_to_model(
        self, 
        role: str,          # "architect" | "engineer" | "qa" | etc
        task_type: str,
        quality_required: Literal["good", "high", "frontier", "opus"]
    ) -> tuple[str, str]:   # (provider, model)
        """
        Intelligent routing:
        - "good": Gemini Flash or Groq (fast, cheap)
        - "high": Gemini 2.5 Pro (quality, free)
        - "frontier": Gemini 3 Pro or GPT-5.4 (best free)
        - "opus": Claude Opus 4.6 via Puter.js (best overall)
        """
```

## Acceptance Criteria
- [ ] Adding 10 new keys → MoA depth automatically increases within 60 seconds
- [ ] Quota dropping below 5,000 → system switches to medium config automatically
- [ ] Emergency config → Discord alert to Ghost
- [ ] Route selection logged for every task (for debugging)
- [ ] Config survives ClawCloud restart (stored in Redis)

---

# T8 — MoA Orchestrator

**Complexity:** VERY HIGH ⭐ (RECOMMENDED FOR TRAYCER)  
**Priority:** P1  
**Depends on:** T5, T7  
**Blocks:** T9, T10, T11, T12  

## Context
The MoA Orchestrator is the core intelligence engine. It coordinates: research phase, 8 parallel proposers with different roles, self-consistency verification, PRM step scoring, constitutional critique, confidence checking, entropy gate, and Opus oracle. Getting this right is the difference between a powerful AI agent and a mediocre one.

This is the most complex single component in Ultron. It has the most interactions, the most failure modes, and the highest impact on quality. Strongly recommended for Traycer execution.

## Files to Create

| File | Purpose |
|---|---|
| `packages/brain/moa/orchestrator.py` | Main MoA coordinator (LangGraph) |
| `packages/brain/moa/proposers.py` | 8 role-based proposer instances |
| `packages/brain/moa/roles.py` | Role definitions + system prompts |
| `packages/brain/moa/parallel_runner.py` | Async parallel execution |
| `packages/brain/quality/self_consistency.py` | 5-10 sample verification |
| `packages/brain/quality/prm_scorer.py` | Step-level reward models |
| `packages/brain/quality/constitutional_critic.py` | 3-round critique |
| `packages/brain/quality/critic.py` | Sonnet 4.6 critic |
| `packages/brain/quality/synthesizer.py` | Gemini 3 Pro synthesis |
| `packages/brain/quality/confidence_checker.py` | Uncertainty estimation |
| `packages/brain/quality/ai_judge.py` | 3-layer final judge |

## LangGraph State Machine

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class MoAState(TypedDict):
    task: Task
    research_results: list[dict]
    proposals: Annotated[list[str], operator.add]  # 8 proposals
    self_consistency_result: dict
    prm_scores: list[float]
    critic_analysis: str
    constitutional_rounds: list[str]
    confidence_score: float
    entropy_score: float
    opus_invoked: bool
    opus_result: Optional[str]
    synthesis: str
    final_answer: str
    quality_score: float

def build_moa_graph() -> StateGraph:
    graph = StateGraph(MoAState)
    
    # Add all nodes
    graph.add_node("research", run_parallel_research)
    graph.add_node("proposers", run_parallel_proposers)
    graph.add_node("self_consistency", run_self_consistency)
    graph.add_node("prm_scoring", run_prm_scoring)
    graph.add_node("constitutional_critic", run_constitutional_critic)
    graph.add_node("confidence_check", run_confidence_check)
    graph.add_node("entropy_gate", check_entropy_gate)
    graph.add_node("opus_oracle", run_opus_oracle)
    graph.add_node("synthesizer", run_synthesis)
    graph.add_node("ai_judge", run_final_judge)
    
    # Define edges
    graph.set_entry_point("research")
    graph.add_edge("research", "proposers")
    graph.add_edge("proposers", "self_consistency")
    graph.add_edge("self_consistency", "prm_scoring")
    graph.add_edge("prm_scoring", "constitutional_critic")
    graph.add_edge("constitutional_critic", "confidence_check")
    graph.add_conditional_edges(
        "confidence_check",
        route_by_confidence,
        {
            "high_confidence": "entropy_gate",
            "low_confidence": "opus_oracle"  # Direct to Opus if uncertain
        }
    )
    graph.add_conditional_edges(
        "entropy_gate",
        route_by_entropy,
        {
            "low_entropy": "synthesizer",    # <85: proceed
            "high_entropy": "opus_oracle"    # >85: Opus validates
        }
    )
    graph.add_edge("opus_oracle", "synthesizer")
    graph.add_edge("synthesizer", "ai_judge")
    graph.add_edge("ai_judge", END)
    
    return graph.compile()
```

## Acceptance Criteria
- [ ] 8 proposers fire in parallel (verify with async timing logs)
- [ ] Total deep mode time: <5 minutes for standard task
- [ ] Opus only called when entropy >85 OR confidence <60
- [ ] Self-consistency: 3/5 agreement required to proceed
- [ ] Constitutional critic runs exactly 3 rounds
- [ ] LangGraph state persists in Redis (survives key rotation mid-pipeline)
- [ ] All intermediate results stored in Zilliz (for Reflexion learning)
- [ ] Quality score >80% before final answer delivered
- [ ] If quality <80%: one automatic retry with revised approach

---

# T9 — Role-Based Proposers (8 Agents)

**Complexity:** HIGH  
**Priority:** P1  
**Depends on:** T8  
**Blocks:** T10  

## Context
Each of the 8 proposers has a distinct role, temperature, model assignment, and system prompt. The diversity across roles is what makes MoA work — if all proposers think the same way, the ensemble adds no value.

## Files to Create

| File | Purpose |
|---|---|
| `packages/brain/moa/roles.py` | Role definitions (immutable system prompts) |
| `packages/brain/moa/proposers.py` | Proposer execution logic |
| `packages/brain/moa/parallel_runner.py` | asyncio.gather execution |

## Role Definitions

```python
ROLES = {
    "architect": {
        "model": "gemini-2.5-pro",
        "temperature": 0.3,
        "system_prompt": """You are the Architect. Your ONLY job is to evaluate 
        structure, scalability, and long-term design. 
        
        Always ask:
        - Will this design work in 2 years?
        - What are the hidden dependencies?
        - Where will this break under load?
        - Is this the simplest correct structure?
        
        NEVER discuss implementation details.
        ALWAYS think about the big picture.""",
        "output_focus": "architecture"
    },
    
    "engineer": {
        "model": "deepseek-coder-v3",   # Via Groq
        "temperature": 0.4,
        "system_prompt": """You are the Senior Engineer. Your ONLY job is 
        to think about concrete implementation.
        
        Always ask:
        - What's the simplest correct implementation?
        - Which existing library already solves this?
        - What's the most readable code?
        - How do I minimize lines of code without sacrificing clarity?
        
        ALWAYS recommend specific libraries.
        ALWAYS provide concrete code examples.""",
        "output_focus": "implementation"
    },
    
    "qa_breaker": {
        "model": "gemini-2.5-pro",      # Second instance
        "temperature": 0.7,             # Higher for creative failure modes
        "system_prompt": """You are the QA Engineer and your job is to BREAK things.
        
        Try to:
        - Find the input that crashes this
        - Find the race condition nobody thought of
        - Find the security vulnerability
        - Find what happens with empty inputs, huge inputs, null inputs
        - Find what happens at exactly the boundary conditions
        
        Be creative. Be malicious. Break it before it ships.""",
        "output_focus": "edge_cases"
    },
    
    "researcher": {
        "model": "grok-4.1",            # 2M context for large codebases
        "temperature": 0.4,
        "system_prompt": """You are the Research Specialist with access to 
        the latest information (up to today's date).
        
        Always:
        - Reference the most current best practices
        - Cite specific papers or documentation
        - Find if anyone has solved this exact problem before
        - Identify the state of the art approach
        
        The Parallel.ai research results are attached. Use them.""",
        "output_focus": "research"
    },
    
    "reasoner": {
        "model": "deepseek-r1",         # Via Puter.js
        "temperature": 0.2,             # Low for precision
        "system_prompt": """You are the Logical Reasoner. Your job is to 
        verify the logic of any proposed solution.
        
        For every claim:
        - Is the reasoning chain valid?
        - Is each step actually implied by the previous?
        - Is there a hidden assumption being made?
        - Is the mathematical reasoning correct?
        
        Think in formal logic. Reject hand-waving.""",
        "output_focus": "reasoning"
    },
    
    "devil_advocate": {
        "model": "llama-4-maverick",    # Via Together AI - different training
        "temperature": 0.8,
        "system_prompt": """You are the Devil's Advocate. Your job is to argue 
        the OPPOSITE of whatever the obvious answer is.
        
        If everyone says "use PostgreSQL", argue for MongoDB.
        If everyone says "build it", argue for "buy it".
        If everyone says "microservices", argue for monolith.
        
        Your goal is not to be right. Your goal is to surface 
        assumptions everyone else is making unconsciously.
        
        Be provocative. Make people defend their choices.""",
        "output_focus": "contrarian"
    },
    
    "domain_expert": {
        "model": "gemini-student-pro",  # Gemini Student account
        "temperature": 0.3,
        "system_prompt": """You are the Domain Expert for Ghost's specific field.
        
        Ghost is a Chemical Engineering student at SVNIT Surat.
        His relevant domains are:
        - Chemical engineering (thermodynamics, mass transfer, reactions)
        - Python programming (scientific computing focus)
        - Academic research and documentation
        - Competition presentations (AZeotropy, IIT Bombay)
        
        Always apply domain-specific knowledge.
        Use ChE terminology correctly.
        Reference relevant industry standards.""",
        "output_focus": "domain"
    },
    
    "validator": {
        "model": "llama-3.3-70b",       # Via Cerebras (2000 tok/s = instant)
        "temperature": 0.2,
        "system_prompt": """You are the Quick Validator. Your job is a 
        30-second sanity check.
        
        Check:
        1. Does this make basic sense?
        2. Any obvious factual errors?
        3. Any obvious logical contradictions?
        4. Any statements that are obviously false?
        
        Be fast. Be binary. YES/NO with brief reason.
        Don't do deep analysis. Just catch obvious problems.""",
        "output_focus": "sanity"
    }
}
```

## Acceptance Criteria
- [ ] All 8 proposers produce output in <35 seconds (parallel)
- [ ] Each proposer's output measurably reflects its role (QA finds edge cases, Engineer gives code)
- [ ] Devil's Advocate always argues opposite of majority view
- [ ] Validator response in <5 seconds (Cerebras speed verified)
- [ ] All 8 outputs stored in Zilliz with role metadata
- [ ] Role prompts are IMMUTABLE (stored in sacred files, never self-modified)

---

# T10 — Self-Consistency + PRM Step Scoring

**Complexity:** HIGH  
**Priority:** P1  
**Depends on:** T9  
**Blocks:** T11  

## Context
Self-consistency verification runs the same question through multiple models and requires agreement before proceeding. PRM (Process Reward Model) scores each reasoning step to catch errors before they cascade.

## Files to Create

| File | Purpose |
|---|---|
| `packages/brain/quality/self_consistency.py` | Multi-sample verification |
| `packages/brain/quality/prm_scorer.py` | Step-level scoring |

## Implementation Plan

### self_consistency.py
```python
class SelfConsistencyEngine:
    
    SAMPLE_MODELS = [
        ("gemini-2.5-pro", 0.3),
        ("deepseek-r1", 0.2),
        ("groq-llama-70b", 0.4),
        ("llama-4-maverick", 0.5),
        ("gemini-2.5-flash", 0.3),
    ]
    
    async def verify(
        self, 
        question: str,
        n_samples: int = 5,    # Adaptive based on quota
        agreement_threshold: float = 0.6   # 3/5 = 60%
    ) -> ConsistencyResult:
        """
        1. Run same question on n different models simultaneously
        2. Extract key claims from each response
        3. Cluster similar claims (semantic similarity >0.85)
        4. Return majority cluster
        5. Flag disagreements for constitutional critic
        
        Returns:
            ConsistencyResult(
                consensus: str,           # Majority answer
                confidence: float,        # Agreement percentage
                disagreements: list[str], # Claims only 1 model made
                should_escalate: bool     # True if agreement <60%
            )
        """

### prm_scorer.py
class PRMScorer:
    """
    Process Reward Model: score each reasoning step.
    Uses Gemini Flash (fast, cheap) to evaluate each step.
    Stops and flags if any step scores <0.5.
    """
    
    async def score_chain(
        self,
        reasoning_steps: list[str]
    ) -> list[StepScore]:
        """
        For each step, asks Gemini Flash:
        "On scale 0-1: Is this reasoning step 
         logically valid and factually correct?
         Only output the number."
        
        If any step <0.5: flag entire chain for revision.
        If consecutive steps <0.7: flag for constitutional critic.
        """
```

## Acceptance Criteria
- [ ] 5 parallel samples complete in <30 seconds
- [ ] 3/5 agreement → proceed (agreement_threshold=0.6)
- [ ] 2/5 or less agreement → escalate to Opus oracle
- [ ] PRM catches factual error in reasoning chain (test with known wrong reasoning)
- [ ] PRM step scoring adds <15 seconds to pipeline
- [ ] All samples stored in Zilliz for Reflexion learning

---

# T11 — Constitutional Critic (3 Rounds)

**Complexity:** MEDIUM  
**Priority:** P1  
**Depends on:** T10  
**Blocks:** T12  

## Context
The constitutional critic is inspired by Anthropic's Constitutional AI training methodology — applied at inference time. Three rounds of critique force increasingly refined output.

## Files to Create

| File | Purpose |
|---|---|
| `packages/brain/quality/constitutional_critic.py` | 3-round critique engine |

## Implementation Plan

```python
class ConstitutionalCritic:
    
    CRITIQUE_CONSTITUTION = """
    Evaluate this solution against these principles:
    
    1. CORRECTNESS: Is every factual claim verifiable and accurate?
    2. COMPLETENESS: Are there obvious missing pieces?
    3. SIMPLICITY: Is this more complex than necessary?
    4. SAFETY: Could this cause harm or data loss?
    5. CONSISTENCY: Does this contradict anything else in the context?
    6. EFFICIENCY: Is there a significantly better approach?
    7. GHOST_FIT: Does this match Ghost's coding style and preferences?
    """
    
    async def critique(
        self, 
        content: str,
        context: dict,
        n_rounds: int = 3    # Adaptive based on quota (1-3)
    ) -> CritiqueResult:
        """
        Round 1 (Find Flaws):
            Prompt: "You are the world's harshest critic.
                    Apply the constitution to this solution.
                    Find EVERY violation. Be brutal."
        
        Round 2 (Verify Flaws Are Real):
            Prompt: "Review these claimed flaws: {round1_output}
                    Which are genuine problems vs nitpicking?
                    Rank by severity: CRITICAL / MAJOR / MINOR"
        
        Round 3 (Confirm Fixes):
            Prompt: "For each CRITICAL and MAJOR flaw:
                    Propose the exact fix.
                    Will the fix introduce new problems?
                    Final score 0-100."
        
        Returns:
            CritiqueResult(
                flaws: list[Flaw],
                fixes: list[Fix],
                final_score: float,     # 0-100
                ready_to_proceed: bool  # score >70
            )
        """
```

## Acceptance Criteria
- [ ] 3 rounds complete in <30 seconds total
- [ ] Round 2 always filters Round 1 flaws (fewer flaws in Round 2 than Round 1)
- [ ] Final score <70 → content goes back for revision (max 2 revision cycles)
- [ ] Final score logged to Zilliz with task_id for learning
- [ ] In emergency quota mode (1 round only): still runs Round 1 minimum

---

# T12 — Sonnet Critic + Gemini Synthesizer + Confidence Check

**Complexity:** HIGH  
**Priority:** P1  
**Depends on:** T11  
**Blocks:** T18  

## Context
After constitutional critique, Claude Sonnet 4.6 reads all 8 proposals and the critique results to identify the best elements. Gemini 3 Pro synthesizes the final answer. Confidence check determines if Opus escalation is needed.

## Files to Create

| File | Purpose |
|---|---|
| `packages/brain/quality/critic.py` | Sonnet 4.6 critic |
| `packages/brain/quality/synthesizer.py` | Gemini 3 Pro synthesis |
| `packages/brain/quality/confidence_checker.py` | Uncertainty estimation |
| `packages/brain/quality/ai_judge.py` | 3-layer final judge |

## Implementation Plan

### critic.py (Claude Sonnet 4.6 via Puter.js)
```python
class SonnetCritic:
    async def analyze(
        self,
        proposals: list[str],       # 8 role-based proposals
        critique_results: CritiqueResult,
        research_context: dict
    ) -> CriticAnalysis:
        """
        Uses Claude Sonnet 4.6 (89.9% GPQA Diamond).
        
        Prompt: Read all 8 proposals + critique.
        Identify:
        - Best proposal (which role got it most right)
        - Best element from each other proposal
        - What the constitutional critique correctly flagged
        - What is still unresolved
        - Confidence level: HIGH/MEDIUM/LOW
        """

### synthesizer.py (Gemini 3 Pro - #1 LM Arena)
```python
class GeminiSynthesizer:
    async def synthesize(
        self,
        critic_analysis: CriticAnalysis,
        proposals: list[str],
        task: Task
    ) -> SynthesisResult:
        """
        Uses Gemini 3 Pro (65,536 token output window).
        
        Builds final answer by:
        1. Starting with best proposal as base
        2. Applying improvements from other roles
        3. Incorporating all constitutional fixes
        4. Ensuring style matches Ghost's preferences (from memory)
        5. Outputting complete, production-ready answer
        """

### confidence_checker.py
```python
class ConfidenceChecker:
    async def check(self, synthesis: str, task: Task) -> float:
        """
        Asks synthesizer model: 
        "On scale 0-100, how confident are you in this answer?
         Consider: completeness, accuracy, appropriateness.
         Output only the number."
        
        Routes based on score:
        >80: proceed to AI judge
        60-80: proceed but flag for Ghost review
        40-60: escalate to Opus oracle  
        <40: HALT, escalate to Ghost
        """
```

## Acceptance Criteria
- [ ] Sonnet critic always identifies the best proposal (not just summarizes)
- [ ] Gemini 3 Pro synthesis reads ALL 8 proposals (verify via token count)
- [ ] Confidence <60 → Opus oracle called (verify in logs)
- [ ] Final answer includes attribution: which role contributed which element
- [ ] 3-layer AI judge runs on every final answer before delivery
- [ ] Ghost-preference check: answer reflects Ghost's known preferences (verify via memory)

---

# T13 — Redis Memory (Tier 0 + Tier 1)

**Complexity:** MEDIUM  
**Priority:** P1  
**Depends on:** T4  
**Blocks:** T14  

## Context
Redis handles the two fastest memory tiers: Core Memory (always in context, never retrieved) and Working Memory (current session, sliding window). Both must be extremely fast (<5ms) as they're accessed on every single LLM call.

## Files to Create

| File | Purpose |
|---|---|
| `packages/memory/core_memory.py` | Tier 0: always-in-context facts |
| `packages/memory/working_memory.py` | Tier 1: current session state |
| `packages/memory/passport.py` | Context passport assembly |

## Implementation Plan

### core_memory.py (Letta-style)
```python
class CoreMemory:
    """
    Always-in-context facts about Ghost.
    Updated by Ultron when important facts discovered.
    Never exceeds 500 tokens total.
    
    Structure:
    - ghost_profile: name, context, communication_style
    - current_project: name, phase, deadline, priorities
    - today_focus: 3 most important things right now
    - recent_decisions: last 3 important decisions made
    - error_patterns: top 3 mistakes to avoid right now
    """
    
    REDIS_KEY = "core_memory:ghost"
    MAX_TOKENS = 500
    
    async def get_all(self) -> str:
        """Returns formatted core memory for prompt injection"""
    
    async def self_edit(
        self, 
        field: str, 
        new_value: str,
        reason: str
    ) -> bool:
        """
        Ultron updates core memory when important fact discovered.
        Never exceeds MAX_TOKENS total.
        If would exceed: remove least important field first.
        """
    
    def format_for_prompt(self, memory: dict) -> str:
        """
        Formats core memory as structured prompt injection:
        === CORE CONTEXT ===
        You are helping Ghost, a Chemical Engineering student...
        Current project: [project]
        Today's priorities: [priorities]
        ...
        """

### passport.py
```python
class PassportAssembler:
    """
    Assembles context passport from all memory tiers.
    Target: 800 tokens, assembled in <200ms.
    """
    
    async def assemble(
        self, 
        task_id: str,
        task_description: str
    ) -> Passport:
        """
        Parallel assembly from all sources:
        
        async with asyncio.TaskGroup() as tg:
            t_core = tg.create_task(core_memory.get_all())
            t_redis = tg.create_task(working_memory.get_current(task_id))
            t_zilliz = tg.create_task(insight_memory.search(task_description))
            t_cognee = tg.create_task(knowledge_graph.get_entities(task_description))
            t_playbook = tg.create_task(ace_loop.get_playbook(task_type))
        
        # Assemble passport within 800 token budget
        # Priority: core > checkpoint > top_memories > playbook > graph
        """
```

## Acceptance Criteria
- [ ] Core memory retrieved: <5ms (Redis GET)
- [ ] Passport assembled: <200ms (parallel sources)
- [ ] Core memory never exceeds 500 tokens (enforced)
- [ ] Core memory self-edit logged with reason (audit trail)
- [ ] Working memory sliding window: exactly last 50 interactions
- [ ] Passport survives key rotation (stored in Redis, not in-memory)

---

# T14 — Zilliz + Mem0 (Insight Memory Tier 2)

**Complexity:** VERY HIGH ⭐ (RECOMMENDED FOR TRAYCER)  
**Priority:** P1  
**Depends on:** T13  
**Blocks:** T15, T16  

## Context
This is the heart of Ultron's memory advantage over every other AI system. Mem0 transforms raw agent observations into atomic facts before storage, dramatically improving retrieval quality. Zilliz provides semantic search across 15M+ vectors. Together they give Ultron permanent, searchable, accurate memory of everything.

Getting this wrong causes memory pollution, retrieval failures, and hallucinations about past events. Getting it right means Ultron remembers Steve's breakup 200 days later and answers questions about it accurately.

## Files to Create

| File | Purpose |
|---|---|
| `packages/memory/insight/mem0_client.py` | Atomic fact extraction |
| `packages/memory/insight/zilliz_client.py` | Vector store operations |
| `packages/memory/insight/embeddings.py` | Embedding generation |
| `packages/memory/insight/dedup.py` | Duplicate detection |
| `packages/memory/pruning.py` | 3-policy pruning |

## Implementation Plan

### mem0_client.py
```python
from mem0 import MemoryClient

class Mem0Memory:
    """
    Wraps Mem0 with Zilliz backend.
    Transforms raw text → atomic facts before storage.
    
    Example transformation:
    Input: "Steve had a bad breakup with Priya in 2024 
            and he still has feelings for her"
    
    Extracted atomic facts:
    - steve.relationship.ex = "Priya"
    - steve.event.2024.type = "breakup"
    - steve.event.2024.severity = "bad"
    - steve.emotional.status = "still_has_feelings_for_Priya"
    - steve.relationship.current_status = "single_but_pining"
    """
    
    def __init__(self):
        self.client = MemoryClient(
            api_key=os.getenv("MEM0_API_KEY"),
            # Or self-hosted:
            # config={"vector_store": {"provider": "zilliz", ...}}
        )
    
    async def add(
        self, 
        content: str,
        metadata: dict,
        user_id: str = "ghost"
    ) -> list[str]:
        """
        Extract atomic facts and store.
        Returns list of fact IDs stored.
        
        Deduplication: before storing, check if fact already exists
        (cosine similarity > 0.95 with existing = skip)
        """
    
    async def search(
        self,
        query: str,
        n_results: int = 10,
        filters: dict = None,
        user_id: str = "ghost"
    ) -> list[MemoryResult]:
        """
        Hybrid search: semantic (vector) + metadata filter.
        
        Example: query="Steve girlfriend", filter={"entity": "Steve"}
        Returns all facts about Steve related to romantic relationships.
        """
    
    async def get_all_about(
        self,
        entity: str
    ) -> list[MemoryResult]:
        """
        Get everything stored about a specific entity.
        Used for: "Tell me everything you know about Steve"
        """

### pruning.py
```python
class MemoryPruner:
    """
    3-policy pruning to prevent memory pollution.
    Runs nightly as part of consolidation job.
    """
    
    async def run_full_pruning_cycle(self) -> PruningReport:
        """
        Policy 1: DEDUPLICATION
        - Embed all memories
        - Find clusters where cosine_similarity > 0.95
        - Keep centroid of cluster, delete others
        - Log: N memories deduplicated
        
        Policy 2: TTL (Time-To-Live)
        - Any memory: access_count < 3 AND age > 60 days
        - Move to GitHub JSONL archive
        - Delete from Zilliz
        - Log: N memories archived
        
        Policy 3: IMPORTANCE SCORING
        - Any memory: importance_score < 0.2
        - AND: not tagged as "critical"
        - AND: age > 30 days
        - Archive to GitHub, delete from Zilliz
        
        Tags that prevent deletion:
        "critical", "architectural_decision", "ghost_preference",
        "lesson_learned", "recurring_pattern"
        """
```

## Acceptance Criteria
- [ ] Store atomic fact: <100ms
- [ ] Retrieve "Steve's girlfriend situation": returns Priya facts in <50ms
- [ ] Deduplication: storing same fact twice → only stored once (test with identical content)
- [ ] After 200 tasks: retrieval speed unchanged (test with RAPTOR hierarchy)
- [ ] Pruning cycle: completes in <5 minutes for 1M memories
- [ ] After pruning: retrieval quality improves (measure before/after with test set)
- [ ] All pruned memories moved to GitHub archive (verify with file count)
- [ ] Zero data loss: any archived memory retrievable from GitHub JSONL

---

# T15 — Cognee Knowledge Graph

**Complexity:** HIGH  
**Priority:** P2  
**Depends on:** T14  
**Blocks:** T16  

## Context
The knowledge graph stores relationships between entities, not just facts about entities. This enables graph traversal queries like "what files depend on auth.py?" or "who in Ghost's network knows Priya?"

## Files to Create

| File | Purpose |
|---|---|
| `packages/memory/insight/cognee_client.py` | Knowledge graph operations |
| `packages/memory/insight/graph_extractor.py` | Extract relationships from text |

## Implementation Plan

```python
import cognee

class KnowledgeGraph:
    """
    Entities: person, file, concept, project, tool, organization
    Relationships: directed labeled edges
    
    Examples:
    Ghost --works_on--> UltronProject
    auth.py --imports--> database.py (×1)
    auth.py --called_by--> middleware.py (×47)
    Steve --ex_with--> Priya
    Ghost --knows--> Steve
    Ghost --studies_at--> SVNIT
    """
    
    async def add_entity(self, entity: Entity) -> str:
        """Add node to graph"""
    
    async def add_relationship(
        self, 
        from_entity: str,
        relationship: str,
        to_entity: str,
        weight: float = 1.0,
        metadata: dict = None
    ) -> str:
        """Add directed labeled edge"""
    
    async def traverse(
        self,
        start_entity: str,
        relationship_filter: str = None,
        max_depth: int = 3
    ) -> list[GraphPath]:
        """BFS traversal from entity"""
    
    async def find_dependents(
        self,
        file_path: str
    ) -> list[str]:
        """
        For codebase awareness:
        Find all files that depend on given file.
        Uses: called_by, imports, inherits_from relationships.
        Critical for safe code modification.
        """
    
    async def extract_relationships_from_text(
        self, 
        text: str
    ) -> list[Relationship]:
        """
        Uses Gemini Flash to extract entity-relationship-entity triples.
        "Steve had a breakup with Priya" →
        (Steve, had_breakup_with, Priya)
        """
```

## Acceptance Criteria
- [ ] Add relationship: <100ms
- [ ] Traverse 3-depth graph: <200ms
- [ ] "What files depend on auth.py?" returns correct dependents (test with known codebase)
- [ ] Relationship extraction from text: >85% accuracy (test with known sentences)
- [ ] Graph persists across restarts

---

# T16 — RAPTOR + Zep Temporal + ACE Playbook

**Complexity:** HIGH  
**Priority:** P2  
**Depends on:** T15  
**Blocks:** T17  

## Context
Three complementary memory layers that improve retrieval quality at scale:
- RAPTOR: hierarchical compression keeps retrieval fast as memory grows
- Zep: temporal indexing enables "what happened on Day 23?" queries
- ACE: lesson playbook prevents repeating mistakes

## Files to Create

| File | Purpose |
|---|---|
| `packages/memory/insight/raptor.py` | Hierarchical tree compression |
| `packages/memory/insight/zep_client.py` | Temporal indexing |
| `packages/memory/ace_loop.py` | Generator → Reflector → Curator |

## ACE Loop Implementation

```python
class ACELoop:
    """
    After every task: Generator → Reflector → Curator cycle.
    Builds a playbook of lessons for each task type.
    
    +10.6% benchmark improvement (published ArXiv 2025).
    """
    
    async def process_completed_task(
        self,
        task: Task,
        result: Result,
        intermediate_steps: list[Step]
    ) -> Optional[Lesson]:
        """
        GENERATOR phase:
        Runs automatically when task completes.
        Takes: task description, result, all intermediate steps
        
        REFLECTOR phase (Gemini Flash):
        "What went well? What went wrong? 
         What would you do differently?"
        
        CURATOR phase (Gemini Flash):
        "Extract exactly ONE reusable lesson:
         {task_pattern: ..., common_mistake: ..., 
          correct_approach: ..., time_saved_minutes: ...}
         
         If no lesson: return null."
        
        If lesson extracted:
        - Store in skill_playbooks Zilliz collection
        - Append to local /memory/playbooks/{task_type}.md
        """
    
    async def get_playbook(
        self,
        task_type: str
    ) -> list[Lesson]:
        """
        Get top-5 most relevant lessons for this task type.
        Injected into context passport before every task.
        """
```

## Acceptance Criteria
- [ ] RAPTOR: retrieval time stable at 1M vs 10M memories (benchmark)
- [ ] Zep temporal: "What was auth.py like 2 weeks ago?" returns correct answer
- [ ] ACE: after 10 similar tasks, relevant lesson appears in playbook
- [ ] ACE: same mistake never occurs twice in same task category (test with deliberate repeat)
- [ ] Lessons displayed in Notion memory browser for Ghost to review

---

# T17 — Notion + DeepWiki (Structured Memory Tier 4)

**Complexity:** MEDIUM  
**Priority:** P2  
**Depends on:** T16  
**Blocks:** T27  

## Context
Tier 4 memory is for humans. Ghost can browse all of Ultron's knowledge from any phone via Notion. DeepWiki auto-generates codebase documentation on every commit.

## Files to Create

| File | Purpose |
|---|---|
| `packages/memory/structured/notion_client.py` | Notion page management |
| `packages/memory/structured/deepwiki.py` | Live codebase documentation |
| `packages/memory/structured/project_logger.py` | Auto-document all decisions |

## Notion Database Structure

```python
NOTION_DATABASES = {
    "projects": {
        # One row per project
        "columns": ["name", "status", "phase", "deadline", 
                    "github_url", "live_url", "ticket_count",
                    "completion_percent"]
    },
    "decisions": {
        # One row per architectural/important decision
        "columns": ["decision", "reason", "alternatives_considered",
                    "timestamp", "project", "entropy_score"]
    },
    "memory_log": {
        # Human-readable memory browser
        "columns": ["entity", "fact", "timestamp", "importance"]
    },
    "task_history": {
        # Every task completed
        "columns": ["task", "result", "quality_score", "duration",
                    "tokens_used", "lessons_learned"]
    }
}
```

## Acceptance Criteria
- [ ] Every completed task → Notion row added within 60 seconds
- [ ] Every architectural decision logged with reasoning
- [ ] DeepWiki updates on every commit (GitHub Actions trigger)
- [ ] Ghost can search Notion from phone: "what did Ultron decide about auth?"
- [ ] Memory browser shows last 100 facts added

---

# T18 — Entropy Engine

**Complexity:** HIGH  
**Priority:** P1  
**Depends on:** T12  
**Blocks:** T19, T20  

## Context
The entropy engine is Ultron's quality management system based on thermodynamics. It continuously measures disorder in every system component and triggers corrective actions. It is what prevents Ultron from degrading over time — the thermodynamic second law problem that destroys all long-running agents.

## Files to Create

| File | Purpose |
|---|---|
| `packages/entropy_engine/engine.py` | Main orchestrator |
| `packages/entropy_engine/memory_entropy.py` | Memory quality score |
| `packages/entropy_engine/codebase_entropy.py` | Code quality score |
| `packages/entropy_engine/task_entropy.py` | Task complexity score |
| `packages/entropy_engine/bug_entropy.py` | Bug risk score |
| `packages/entropy_engine/decision_diversity.py` | MoA diversity score |
| `packages/entropy_engine/system_health.py` | Overall health score |

## Implementation Plan

```python
class EntropyEngine:
    
    async def compute_task_entropy(self, task: Task) -> float:
        """
        0-100 score. Higher = more disordered = needs more attention.
        
        Factors:
        - Ambiguity level (0-30): How clear are the requirements?
        - Dependency count (0-20): How many components involved?
        - Reversibility (0-20): Can mistakes be undone?
        - Unknown unknowns (0-30): What don't we know we don't know?
        
        Thresholds:
        0-60: Low complexity → proceed normally
        61-84: Medium → full MoA, AlphaEvolve if algorithmic
        85-100: Critical → Opus gate mandatory
        """
    
    async def compute_bug_entropy(self, bug: Bug) -> float:
        """
        Determines priority for bug fixing queue.
        
        Factors:
        - Crash frequency (0-25): Crashes 10x/hour vs 1x/day
        - Affected components (0-25): 1 file vs 20 files
        - Growth rate (0-25): Getting worse vs stable
        - Unknown depth (0-25): Shallow fix vs unknown root cause
        
        Sort bug queue by entropy score descending.
        Always fix highest entropy bug first.
        """
    
    async def run_system_scan(self) -> SystemHealthReport:
        """
        Runs every 6 hours.
        Scans: memory, codebase, decision diversity, system health.
        Triggers: pruning (memory), refactor (codebase), 
                  devil's advocate injection (diversity),
                  self-healing (system health).
        """
    
    async def validate_fix(
        self, 
        before_entropy: float,
        after_entropy: float
    ) -> bool:
        """
        After any fix attempt:
        Did entropy decrease? → fix worked
        Did entropy stay same? → fix didn't help, try different approach
        Did entropy increase? → fix MADE IT WORSE, REVERT IMMEDIATELY
        """
```

## Acceptance Criteria
- [ ] Task entropy computed for every task in <2 seconds
- [ ] Bug entropy sorts queue correctly (critical bugs always first)
- [ ] System scan completes in <5 minutes for full Ultron codebase
- [ ] Fix validation correctly identifies regression (test with known regression)
- [ ] Entropy scores displayed in website dashboard
- [ ] Memory entropy triggers pruning when score >70
- [ ] Codebase entropy triggers refactor proposal when score >60

---

# T19 — Circuit Breaker (3-Layer, Per-Agent)

**Complexity:** VERY HIGH ⭐ (RECOMMENDED FOR TRAYCER)  
**Priority:** P0  
**Depends on:** T18  
**Blocks:** T20, T32  

## Context
The circuit breaker prevents the catastrophic scenario: Ultron in an infinite loop, burning all API quota in hours, with no way to stop. The $47,000 AI disaster scenario.

Three layers catch different types of loops. Per-agent instances prevent one looping agent from stopping all others. O(log n) complexity ensures no performance impact.

This is the most critical safety component. Getting it wrong means potential quota exhaustion. Strongly recommended for Traycer execution.

## Files to Create

| File | Purpose |
|---|---|
| `packages/circuit_breaker/breaker.py` | Main circuit breaker per agent |
| `packages/circuit_breaker/semantic_hash.py` | Action fingerprint ring |
| `packages/circuit_breaker/entropy_detector.py` | Progress entropy detection |
| `packages/circuit_breaker/state_diff.py` | Git diff monitor |
| `packages/circuit_breaker/budget_guardian.py` | Token budget hard ceiling |
| `packages/circuit_breaker/tests/test_breaker.py` | Comprehensive loop tests |

## Implementation Plan

```python
class CircuitBreaker:
    """
    States: CLOSED (normal) → OPEN (tripped) → HALF_OPEN (testing)
    Per-agent instances: each sub-agent has its own breaker.
    Persistence: all state in Redis (survives restarts).
    """
    
    def __init__(self, agent_id: str, redis: UltronRedis):
        self.agent_id = agent_id
        self.redis = redis
        self.state_key = f"circuit_breaker:{agent_id}"
        
        # Three detectors
        self.semantic_detector = SemanticHashRing(agent_id)
        self.entropy_detector = ProgressEntropyDetector(agent_id)
        self.state_monitor = StateDiffMonitor(agent_id)
    
    async def check(
        self,
        action: dict,
        tokens_used: int,
        progress: float
    ) -> Literal["PROCEED", "HALT", "ESCALATE"]:
        """
        Called BEFORE every agent action. O(log n).
        
        State OPEN: return "HALT" immediately (fast path)
        State CLOSED/HALF_OPEN:
          1. semantic_detector.is_loop(action)     → O(log n)
          2. entropy_detector.is_loop(tokens, progress) → O(1)
          3. state_monitor.is_loop()               → O(1)
          
        If ANY detector triggers:
          → _handle_trip(which_detectors, action)
        Else:
          → return "PROCEED"
        """

class SemanticHashRing:
    """
    Detects loops even when agent uses different words for same action.
    
    Hash is based on: tool_name + target_type + operation_type
    Ignores: variable names, file paths, parameter values
    
    Window: last 10 actions
    Threshold: same fingerprint 3+ times = loop
    Complexity: O(log n) via sorted bucket lookup
    """
    
    def normalize_action(self, action: dict) -> str:
        """Extract semantic fingerprint ignoring surface variation"""
        core = f"{action['tool']}:{action.get('target_type', 'generic')}:{action.get('operation', 'execute')}"
        return hashlib.sha256(core.encode()).hexdigest()[:16]

class ProgressEntropyDetector:
    """
    Catches loops where action names vary but progress is zero.
    
    Primary detector (catches semantic hash misses).
    
    Loop signal: tokens_consumed rising + quality_score flat
    Formula: if tokens > 5000 AND progress_delta < 1.0 → loop
    Complexity: O(1)
    """

class StateDiffMonitor:
    """
    Catches invisible loops: agent "works" but nothing actually changes.
    
    Uses: git diff --stat → MD5 hash of output
    If last 3 git states identical: nothing is changing = loop
    
    Catches: agent reading same file repeatedly without modifying
    Catches: agent planning without executing
    Complexity: O(1) after first run (cached hash)
    """

class TokenBudgetGuardian:
    """
    Hard ceiling on token usage per task.
    Prevents runaway costs regardless of loop detection.
    
    Budgets:
    simple_task: 10,000 tokens
    complex_task: 100,000 tokens
    critical_task: 200,000 tokens
    daily_total: 2,000,000 tokens
    
    At 80%: warning log + Discord notice
    At 100%: HARD HALT, escalate to Ghost
    """
```

## Acceptance Criteria
- [ ] Semantic loop (same action different words): detected within 3 repetitions
- [ ] Progress entropy loop (tokens rise, no progress): detected within 10,000 tokens waste
- [ ] State diff loop (no git changes): detected within 5 cycles
- [ ] One agent looping: does NOT affect other agents (per-agent isolation test)
- [ ] Auto-recovery (Trip 1-2): Opus gives new approach, agent resumes
- [ ] Ghost escalation (Trip 3+): Discord message within 30 seconds
- [ ] HALF_OPEN timeout: 10 minutes, then back to OPEN
- [ ] Token budget: HARD HALT at 100% (test with deliberate overflow)
- [ ] O(log n) verified: 100 checks complete in <50ms total
- [ ] All state in Redis: circuit breaker survives ClawCloud restart

---

# T20 — Tool Registry + Pydantic Validation

**Complexity:** MEDIUM  
**Priority:** P1  
**Depends on:** T18, T19  
**Blocks:** T21, T22, T23, T24, T25  

## Context
Every tool Ultron uses must be registered with a strict Pydantic schema. This prevents hallucinated tool parameters from causing silent failures. The dispatcher routes tool calls through permission check → validation → execution → logging.

## Files to Create

| File | Purpose |
|---|---|
| `packages/tools/registry.py` | Central tool registration |
| `packages/tools/dispatcher.py` | Route + validate + execute |
| `packages/tools/permissions.py` | Permission matrix enforcement |
| `packages/tools/base_tool.py` | Abstract base class |
| `packages/tools/schemas/` | One Pydantic model per tool |

## Base Tool Implementation

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict

class BaseTool(ABC):
    """All tools inherit from this."""
    
    name: str
    description: str
    input_schema: type[BaseModel]
    output_schema: type[BaseModel]
    permission_level: Literal["READ", "WRITE", "DELETE", "DEPLOY"]
    requires_ghost_confirm: bool = False
    
    @abstractmethod
    async def execute(self, params: BaseModel) -> BaseModel:
        """Execute the tool. Must return output_schema instance."""
    
    async def dry_run(self, params: BaseModel) -> str:
        """Preview what this tool would do. Used for WRITE+ operations."""
        return f"Would execute {self.name} with {params}"

# Example: GitHub Commit Tool
class CommitGitHubParams(BaseModel):
    model_config = ConfigDict(extra='forbid')  # No hallucinated fields
    
    repo: str = Field(description="Repository name: owner/repo")
    branch: str = Field(description="Target branch name")
    files: list[str] = Field(min_length=1, description="Files to commit")
    message: str = Field(max_length=72, description="Commit message")
    
class CommitGitHubResult(BaseModel):
    success: bool
    commit_sha: str
    url: str
    files_committed: int

class CommitGitHubTool(BaseTool):
    name = "commit_github"
    description = "Commit files to GitHub repository"
    input_schema = CommitGitHubParams
    output_schema = CommitGitHubResult
    permission_level = "WRITE"
    
    async def execute(self, params: CommitGitHubParams) -> CommitGitHubResult:
        # Implementation using GitHub MCP
        ...
```

## Acceptance Criteria
- [ ] All 30+ tools registered with Pydantic schemas
- [ ] Hallucinated parameter → Pydantic ValidationError (not silent failure)
- [ ] Permission check before every tool call (no bypass possible)
- [ ] DELETE tools: Discord confirmation request sent, waits for reply
- [ ] Every tool call logged to JSONL with params_hash + result_hash
- [ ] Dry run available for all WRITE+ operations

---

# T21 — MCP Gateway (Bifrost)

**Complexity:** MEDIUM  
**Priority:** P1  
**Depends on:** T20  
**Blocks:** T22, T23, T24, T25  

## Context
Bifrost MCP Gateway is the central hub for all 17 MCP servers. It provides: unified authentication, rate limiting per server, health monitoring, and observability logging for every tool call.

## Files to Create

| File | Purpose |
|---|---|
| `packages/mcp_gateway/bifrost_client.py` | Connect to Bifrost |
| `packages/mcp_gateway/servers.py` | All 17 server configurations |
| `packages/mcp_gateway/health_monitor.py` | Server health tracking |
| `packages/mcp_gateway/auth_manager.py` | Per-server authentication |

## Server Registry

```python
MCP_SERVER_REGISTRY = {
    "github": MCPServer(
        name="github",
        url="https://github.mcp.anthropic.com/sse",
        auth_env="GITHUB_TOKEN",
        capabilities=["read_repo", "create_pr", "commit", "create_issue"],
        rate_limit_rpm=60,
        fallback=None
    ),
    "semgrep": MCPServer(
        name="semgrep",
        url="npx @semgrep/mcp",
        auth_env=None,
        capabilities=["security_scan"],
        rate_limit_rpm=10,
        fallback=None
    ),
    # ... all 17 servers
}
```

## Acceptance Criteria
- [ ] All 17 MCP servers connect on startup
- [ ] Server health check every 60 seconds
- [ ] Failed server: fallback activated or tool disabled gracefully
- [ ] Every MCP call logged with: server, tool, duration, success
- [ ] Rate limiting per server enforced (no 429s from MCP servers)

---

# T22 — Document Tools (PDF, Word, Excel, PowerPoint, LaTeX)

**Complexity:** MEDIUM  
**Priority:** P1  
**Depends on:** T21  
**Blocks:** T37  

## Context
Ghost wants to type "write my lab report" and receive a perfect PDF. Every document tool must produce professional-quality output that would pass academic or industry review.

## Files to Create

| File | Purpose |
|---|---|
| `packages/tools/documents/pdf_tool.py` | PDF creation |
| `packages/tools/documents/word_tool.py` | Word .docx creation |
| `packages/tools/documents/excel_tool.py` | Excel .xlsx creation |
| `packages/tools/documents/pptx_tool.py` | PowerPoint creation |
| `packages/tools/documents/latex_tool.py` | LaTeX → PDF compilation |
| `packages/tools/documents/fast_io_client.py` | Save to Fast.io cloud |

## LaTeX Special Implementation

```python
class LaTeXTool(BaseTool):
    async def execute(self, params: LaTeXParams) -> LaTeXResult:
        """
        1. Write .tex content to temp file
        2. Install texlive if not present (apt-get)
        3. pdflatex -interaction=nonstopmode file.tex
        4. Run twice (for references/bibliography)
        5. Check for .pdf output
        6. If compilation error: parse log, auto-fix common errors:
           - Undefined control sequence: suggest correct macro
           - Missing $ inserted: add math mode
           - Overfull hbox: add \allowbreak
        7. Retry compilation after fixes
        8. Upload to Fast.io + GitHub
        9. Return download URL
        """
```

## Acceptance Criteria
- [ ] PDF: creates valid PDF (verify with PyMuPDF)
- [ ] Word: opens in Microsoft Word without errors
- [ ] Excel: all formulas calculate correctly
- [ ] PowerPoint: all slides render correctly
- [ ] LaTeX: compiles without errors on first try for standard documents
- [ ] All files uploaded to Fast.io with permanent URL
- [ ] All files committed to GitHub /outputs/
- [ ] Discord notification with download link within 5 seconds of completion

---

# T23 — Code Tools + GitHub MCP

**Complexity:** HIGH  
**Priority:** P1  
**Depends on:** T21  
**Blocks:** T34  

## Context
Code tools are Ultron's hands for software development. Write code, execute it in E2B sandbox, run tests, lint, and commit to GitHub. The entire software development lifecycle automated.

## Files to Create

| File | Purpose |
|---|---|
| `packages/tools/code/writer_tool.py` | Code generation |
| `packages/tools/code/runner_tool.py` | E2B sandbox execution |
| `packages/tools/code/tester_tool.py` | Test suite runner |
| `packages/tools/code/linter_tool.py` | Static analysis |
| `packages/tools/code/git_tool.py` | Git operations via GitHub MCP |
| `packages/tools/code/fast_apply.py` | Deterministic code edits |

## Fast Apply Implementation

```python
class FastApplyTool(BaseTool):
    """
    Applies code edits deterministically.
    Uses diff-based editing, not full file replacement.
    
    Instead of: "rewrite entire file"
    Does: "replace lines 47-52 with this exact code"
    
    Zero corruption risk.
    Works with any file size.
    """
    async def execute(self, params: FastApplyParams) -> FastApplyResult:
        """
        1. Read current file content
        2. Parse the requested edit (old_content → new_content)
        3. Verify old_content exists exactly once in file
        4. Apply replacement
        5. Verify new_content is in file
        6. Run syntax check (ast.parse for Python, acorn for JS)
        7. If syntax error: revert and report error
        """
```

## Acceptance Criteria
- [ ] Generated Python code: passes pylint with score >8
- [ ] Generated JavaScript: passes ESLint
- [ ] E2B sandbox: code executes in isolated environment, cannot affect host
- [ ] Test suite runner: results parsed correctly (pass/fail counts)
- [ ] Fast Apply: never corrupts surrounding code (test with 100 random edits)
- [ ] Git commit: atomic (all-or-nothing), with message <72 chars
- [ ] Every code file committed with git-native per-edit commits

---

# T24 — Web Tools (Playwright + Firecrawl + Apify + ArXiv)

**Complexity:** MEDIUM  
**Priority:** P2  
**Depends on:** T21  
**Blocks:** T27  

## Context
Web tools give Ultron eyes on the internet. Playwright for interactive browsing, Firecrawl for clean content extraction, Apify for structured data scraping, ArXiv for academic research.

## Files to Create

| File | Purpose |
|---|---|
| `packages/tools/web/playwright_tool.py` | Interactive browser |
| `packages/tools/web/firecrawl_tool.py` | URL → clean Markdown |
| `packages/tools/web/apify_tool.py` | 3000+ specialized scrapers |
| `packages/tools/web/arxiv_tool.py` | Academic paper search |
| `packages/tools/web/search_tool.py` | Multi-source web search |

## Acceptance Criteria
- [ ] Playwright: can login to websites that require authentication
- [ ] Firecrawl: converts any URL to clean Markdown in <10 seconds
- [ ] ArXiv: search returns papers with abstracts in <5 seconds
- [ ] Web content: always wrapped in [WEB_CONTENT] tags before LLM
- [ ] Prompt injection prevention: instructions in web content are never followed

---

# T25 — ChE Domain Tools (NIST + PubChem + Mass Balance)

**Complexity:** HIGH  
**Priority:** P2  
**Depends on:** T20  
**Blocks:** T37  

## Context
These tools make Ultron uniquely valuable for Ghost as a Chemical Engineering student. No commercial AI system has domain-specific ChE tools. This is Ultron's unique competitive advantage.

## Files to Create

| File | Purpose |
|---|---|
| `packages/tools/che/mass_balance.py` | Mass balance calculations |
| `packages/tools/che/thermo_calc.py` | Thermodynamic properties |
| `packages/tools/che/vle_calc.py` | Vapor-liquid equilibrium |
| `packages/tools/che/mccabe_thiele.py` | Distillation design |
| `packages/tools/che/nist_mcp.py` | NIST Chemistry WebBook MCP |
| `packages/tools/che/pubchem_mcp.py` | PubChem compound data MCP |
| `packages/tools/che/unit_convert.py` | Engineering unit conversion |
| `packages/tools/che/plot_engineering.py` | Publication-quality ChE charts |

## NIST MCP Implementation

```python
class NISTChemistryMCP(BaseTool):
    """
    Custom MCP wrapper for NIST Chemistry WebBook API.
    Returns real thermochemical data, not training data.
    
    Example:
    Input: {"compound": "HCl", "temperature_K": 300}
    Output: {"Cp_J_mol_K": 29.14, "H_kJ_mol": -92.31, ...}
    
    Uses: NIST WebBook API (free, no key required)
    """
    
    BASE_URL = "https://webbook.nist.gov/cgi/cbook.cgi"
    
    async def get_thermochemical_data(
        self,
        compound: str,
        temperature_K: float,
        pressure_Pa: float = 101325
    ) -> NISTData:
        """Real data from NIST. Never from training knowledge."""
```

## Acceptance Criteria
- [ ] Mass balance: matrix solution correct for 3-component system (test with known result)
- [ ] NIST data: returns real values matching published tables
- [ ] McCabe-Thiele: generates correct diagram (verify against textbook example)
- [ ] Unit conversion: 100% accuracy on standard conversions (Pa↔bar↔psi↔atm)
- [ ] All ChE calculations: units explicitly tracked and verified (pint library)

---

# T26 — Computer Use (Agent S3 + Gemini Vision + UI-TARS)

**Complexity:** VERY HIGH  
**Priority:** P2  
**Depends on:** T20  
**Blocks:** T34  

## Context
Computer use enables Ultron to control GUI applications like a human. Critical for: software without APIs (HYSYS, ASPEN), specific web interactions requiring authentication, and any GUI-only task.

## Files to Create

| File | Purpose |
|---|---|
| `packages/computer_use/agent_s3.py` | Main Agent S3 controller |
| `packages/computer_use/vision.py` | Screen understanding |
| `packages/computer_use/ui_tars.py` | Pixel-level grounding |
| `packages/computer_use/xvfb_manager.py` | Virtual display management |
| `packages/computer_use/action_executor.py` | Click/type execution |

## Implementation Plan

```python
class ComputerUseController:
    """
    Coordinates: Xvfb → Screenshot → Gemini Vision → 
                 LATS planning → UI-TARS grounding → Execute → Repeat
    """
    
    async def execute_task(
        self,
        task_description: str,
        max_iterations: int = 50
    ) -> ComputerUseResult:
        """
        For each iteration:
        1. Take screenshot (Xvfb virtual display)
        2. Gemini Vision: "What is on screen? What actions possible?"
        3. LATS: "Plan optimal sequence to achieve goal"
        4. UI-TARS: "Where exactly is [element]?" → pixel coordinates
        5. Execute: click(x, y) or type(text)
        6. If iteration 50 reached without goal: escalate to Ghost
        """
    
    async def screenshot(self) -> Image:
        """Capture current virtual display state"""
    
    async def understand_screen(self, screenshot: Image) -> ScreenState:
        """Gemini Vision: parse current screen into structured state"""
    
    async def ground_element(
        self, 
        screenshot: Image,
        element_description: str
    ) -> tuple[int, int]:
        """UI-TARS: find pixel coordinates of described element"""
```

## Acceptance Criteria
- [ ] Virtual display starts without real monitor (Xvfb verified)
- [ ] Screenshot captures correct screen state
- [ ] Gemini Vision identifies buttons and text fields correctly (>85% accuracy)
- [ ] UI-TARS grounds elements within 5 pixels (test with known UI)
- [ ] Task "open browser, navigate to google.com, search for X": completes correctly
- [ ] HYSYS simulation: can enter values and read results (if HYSYS installed)
- [ ] Max iterations reached: escalates to Ghost with screenshot of current state

---

# T27 — Spec Engine (7-Document Planning System)

**Complexity:** VERY HIGH ⭐ (RECOMMENDED FOR TRAYCER)  
**Priority:** P2  
**Depends on:** T17, T24  
**Blocks:** T28, T34  

## Context
The Spec Engine replicates Traycer AI's functionality inside Ultron — for free, for every task, automatically. It generates all 7 planning documents before any complex task begins. This is the single highest-impact quality improvement in the entire architecture: planning before coding reduces hallucination by ~70%.

## Files to Create

| File | Purpose |
|---|---|
| `packages/brain/spec_engine/generator.py` | Runs 7 prompts in sequence |
| `packages/brain/spec_engine/validator.py` | Cross-artifact consistency |
| `packages/brain/spec_engine/notion_publisher.py` | Store in Notion |
| `packages/brain/spec_engine/prompts/` | 7 carefully engineered prompts |

## The 7 Prompts

```python
SPEC_PROMPTS = {
    "01_epic_brief": """
    You are a world-class product architect.
    Ghost has given you this project: {project_description}
    
    Generate an Epic Brief with:
    - Summary: what is being built, who it's for, success definition
    - Context & Problem: persona table, core problem, where in product
    - Success Looks Like: 5 specific measurable criteria
    - Scope IN (MVP by {deadline_1}): every feature, all mandatory
    - Scope OUT (Post-MVP): explicit exclusions
    
    Rules:
    → Every success criterion testable
    → Every scope item unambiguous  
    → Nothing can be TBD or "as needed"
    """,
    
    "02_core_flows": """
    Epic Brief: {epic_brief}
    
    For EVERY user journey:
    ## Flow N — [Name]
    Entry Point: exactly where user starts
    Steps: | Step | User Action | System Response | Error State |
    Exit State: exactly what is true when complete
    Ticket Owner: which ticket implements this
    
    After all flows:
    Implementation Sequence (Mermaid graph)
    Complete File Checklist (every file that needs to exist)
    """,
    
    # ... all 7 prompts
}
```

## Implementation

```python
class SpecEngine:
    
    async def generate_all_specs(
        self, 
        project_description: str,
        deadline_1: str,
        deadline_2: str,
        ghost_context: dict  # From Zilliz memory
    ) -> SpecPackage:
        """
        Runs all 7 prompts.
        Parallel where possible (Prompts 2+3 after 1).
        
        Sequence:
        Prompt 1 (Epic Brief) → wait
        Prompts 2+3 parallel (Core Flows + Tech Plan) → wait
        Prompts 4+5 parallel (Arch Validation + Ticket Breakdown) → wait
        Prompts 6+7 parallel (Cross-Artifact + Ultron Brief) → wait
        
        Total time: 8-10 minutes (parallel)
        
        Returns: SpecPackage with all 7 documents
        """
    
    async def validate_architecture(
        self,
        tech_plan: str
    ) -> ValidationResult:
        """
        Uses Claude Opus via Puter.js for architecture validation.
        Most critical document: if architecture is wrong, everything is wrong.
        """
    
    async def generate_ticket(
        self,
        spec_package: SpecPackage,
        ticket_number: int
    ) -> Ticket:
        """
        Generate one ticket at a time.
        Each ticket references the spec package.
        Each ticket has: context, files, implementation plan, 
                         acceptance criteria, edge cases.
        Saves to Notion automatically.
        """
    
    async def self_improve_prompts(self):
        """
        AlphaEvolve applied to the prompts themselves.
        After 10 projects: analyze which prompts led to good outcomes.
        Evolve prompts toward better spec quality.
        Runs nightly in self-improvement mode.
        """
```

## Acceptance Criteria
- [ ] Epic Brief generated in <3 minutes (Gemini 3 Pro)
- [ ] All 7 documents generated in <10 minutes (parallel)
- [ ] Architecture validation uses Claude Opus (verify via Puter.js logs)
- [ ] All documents saved to Notion (verify pages exist)
- [ ] Tickets generated: one per identified component
- [ ] Ghost notified on Discord when planning complete
- [ ] Spec quality score: >8.5/10 on first run (human evaluation)
- [ ] AlphaEvolve runs on prompts after 10 projects

---

# T28 — AlphaEvolve Integration

**Complexity:** HIGH  
**Priority:** P2  
**Depends on:** T27  
**Blocks:** T29  

## Files to Create

| File | Purpose |
|---|---|
| `packages/self_improvement/alphaevolve/evolver.py` | Main evolution loop |
| `packages/self_improvement/alphaevolve/evaluator.py` | Score variants |
| `packages/self_improvement/alphaevolve/crossover.py` | Combine top performers |

## Implementation

```python
class AlphaEvolve:
    """
    Evolutionary algorithm optimization.
    Proven to beat state-of-the-art algorithms.
    Applied to: code optimization, spec prompts, 
                algorithm design, self-modification proposals.
    """
    
    async def evolve(
        self,
        seed: str,              # Initial solution
        evaluator: Callable,    # Function that scores solutions
        n_variants: int = 10,   # Variants per generation
        n_generations: int = 10,
        selection_size: int = 3  # Top K survive
    ) -> EvolvedResult:
        """
        Generation loop:
        
        gen_1: [v1, v2, v3, v4, v5, v6, v7, v8, v9, v10]
               ↓ evaluate all
               scores: [0.7, 0.6, 0.8, 0.5, 0.9, 0.4, 0.7, 0.6, 0.8, 0.7]
               ↓ select top 3
               winners: [v5(0.9), v3(0.8), v9(0.8)]
               ↓ crossover: Gemini Pro reads all 3, combines best elements
               hybrid: v_hybrid
               ↓ generate 10 variants from hybrid as seed
        gen_2: [v11, v12, ... v20]
               ... repeat
        
        gen_10: best_ever
        
        Store all generations in Zilliz for analysis.
        Return highest-scoring solution found.
        """
    
    def _generate_variants(
        self, 
        seed: str, 
        n: int
    ) -> list[str]:
        """
        Use Gemini Flash (fast, cheap) with varying temperatures.
        Temperature range: 0.3 to 0.9 across variants.
        Higher temperature = more creative variations.
        """
    
    async def _crossover(
        self, 
        top_performers: list[str]
    ) -> str:
        """
        Use Gemini Pro (smart) to analyze top performers.
        Prompt: "These {n} solutions each have strengths.
                Combine the best elements of all into one."
        Returns: hybrid solution
        """
```

## Acceptance Criteria
- [ ] 10-generation evolution: final solution better than seed (measure with evaluator)
- [ ] Evaluator called exactly n_variants × n_generations times
- [ ] Top 3 selection: always correct (test with known scores)
- [ ] Crossover: hybrid outperforms any individual parent (>80% of the time)
- [ ] Applied to spec prompts: prompt quality improves over 10 projects

---

# T29 — Self-Modification Engine

**Complexity:** HIGH  
**Priority:** P3  
**Depends on:** T28  
**Blocks:** T30  

## Files to Create

| File | Purpose |
|---|---|
| `packages/self_improvement/self_modification/engine.py` | Main self-mod coordinator |
| `packages/self_improvement/self_modification/whitelist.py` | Allowed file enforcement |
| `packages/self_improvement/self_modification/canary.py` | Safe deployment |

## Acceptance Criteria
- [ ] Sacred files NEVER modified (hardcoded check, not configurable)
- [ ] Whitelist enforced: modifications outside allowed paths rejected
- [ ] Canary: runs for exactly 60 minutes before merge decision
- [ ] Canary failure → automatic rollback within 60 seconds
- [ ] All self-modifications logged to Notion with rationale

---

# T30 — Reflexion + ACE Curator

**Complexity:** MEDIUM  
**Priority:** P2  
**Depends on:** T29  
**Blocks:** T31  

## Files to Create

| File | Purpose |
|---|---|
| `packages/self_improvement/reflexion.py` | Failure analysis |
| `packages/self_improvement/ace_curator.py` | Lesson extraction |

## Acceptance Criteria
- [ ] Every failed task triggers Reflexion within 60 seconds
- [ ] Reflexion lesson stored in Zilliz + local playbook
- [ ] Same category task: lesson loaded in context passport
- [ ] Same mistake: cannot occur twice if lesson was extracted
- [ ] Playbook visible in Notion for Ghost to review

---

# T31 — AFlow Workflow Optimizer

**Complexity:** MEDIUM  
**Priority:** P3  
**Depends on:** T30  
**Blocks:** T32  

## Context
AFlow learns the optimal workflow sequence for each task type. After 50 tasks of the same type, the pipeline is automatically optimized.

## Files to Create

| File | Purpose |
|---|---|
| `packages/self_improvement/aflow.py` | Workflow optimization |

## Acceptance Criteria
- [ ] After 10 tasks same type: workflow analysis runs
- [ ] After 50 tasks same type: optimized pipeline active
- [ ] Optimized pipeline measurably better (compare quality scores before/after)

---

# T32 — QStash Event System

**Complexity:** MEDIUM  
**Priority:** P0  
**Depends on:** T19, T31  
**Blocks:** T33  

## Context
Replaces polling heartbeat with event-driven architecture. Every task arrives as a QStash webhook. Brain sleeps when no tasks. Wakes instantly when task arrives.

## Files to Create

| File | Purpose |
|---|---|
| `packages/infrastructure/qstash_handler.py` | Receive + process QStash messages |
| `packages/infrastructure/event_router.py` | Route events to handlers |

## Acceptance Criteria
- [ ] No polling: heartbeat loop only runs on webhook receive
- [ ] Task arrival: brain activates within 100ms of QStash delivery
- [ ] No tasks: brain uses 0% CPU (verify with process monitor)
- [ ] QStash delivery failure: automatic retry with exponential backoff

---

# T33 — ClawCloud Heartbeat + Watchdog

**Complexity:** MEDIUM  
**Priority:** P0  
**Depends on:** T32  
**Blocks:** T34  

## Files to Create

| File | Purpose |
|---|---|
| `packages/heartbeat/loop.py` | Main event-driven loop |
| `packages/heartbeat/watchdog.py` | Self-healing monitor |
| `packages/heartbeat/scheduler.py` | Task priority management |

## Acceptance Criteria
- [ ] ClawCloud restart: Ultron resumes from last checkpoint within 30 seconds
- [ ] Watchdog: detects silence >5 minutes → restart attempt
- [ ] Koyeb backup: activates if ClawCloud completely unreachable
- [ ] Morning briefing: sent to Ghost at 8AM every day
- [ ] Weekly report: sent Sunday with full week summary

---

# T34 — Remote Work Pipeline

**Complexity:** HIGH  
**Priority:** P2  
**Depends on:** T33, T26, T23  
**Blocks:** T38  

## Context
The remote work pipeline enables 100-day autonomous projects. Ghost gives a goal, Ultron executes indefinitely, self-improving throughout.

## Files to Create

| File | Purpose |
|---|---|
| `packages/heartbeat/remote_work.py` | Long-running project manager |
| `packages/heartbeat/improvement_loop.py` | Idle self-improvement |

## Acceptance Criteria
- [ ] "Build X over 100 days": task persists correctly through all ClawCloud restarts
- [ ] GitHub commits: at least 1 per day during active project
- [ ] Idle detection: >30 minutes no Ghost task → self-improvement mode
- [ ] ArXiv monitoring: relevant papers auto-applied to ongoing projects
- [ ] Day 25/50/75 checkpoints: Ghost notified with progress report

---

# T35 — Website (Cloudflare Pages + React)

**Complexity:** HIGH  
**Priority:** P1  
**Depends on:** T2  
**Blocks:** T36, T37  

## Files to Create

| File | Purpose |
|---|---|
| `website/src/App.tsx` | Main app with routing |
| `website/src/pages/Dashboard.tsx` | Overview + active tasks |
| `website/src/pages/Chat.tsx` | Conversation interface |
| `website/src/pages/Projects.tsx` | Project history |
| `website/src/pages/Memory.tsx` | Memory browser |
| `website/src/pages/Settings.tsx` | Master settings |

## Acceptance Criteria
- [ ] Works on any mobile browser (test on iPhone + Android)
- [ ] Chat page: identical experience to Discord
- [ ] Dashboard: shows active task, recent commits, entropy score
- [ ] Memory page: searchable with results in <2 seconds
- [ ] All pages load in <3 seconds on 4G connection

---

# T36 — Settings + Secrets Management

**Complexity:** HIGH  
**Priority:** P0  
**Depends on:** T35  
**Blocks:** T40  

## Context
The settings page is how Ghost manages ALL credentials. No GitHub Secrets. No .env files. No technical knowledge required. A 5-year-old should be able to add an API key.

## Files to Create

| File | Purpose |
|---|---|
| `website/src/pages/Settings.tsx` | Settings UI |
| `website/src/components/KeyManager.tsx` | API key CRUD |
| `website/src/components/QuotaDisplay.tsx` | Real-time quota |

## Acceptance Criteria
- [ ] Paste key → click Save → Ultron uses it in <10 seconds
- [ ] Invalid key → clear error message, not stored
- [ ] Keys displayed as: provider name, last 4 chars, quota status (NEVER full key)
- [ ] Delete key → removed from pool within 10 seconds
- [ ] Zero technical knowledge required (test with non-technical user)
- [ ] Works perfectly on mobile

---

# T37 — Dashboard + Observability

**Complexity:** MEDIUM  
**Priority:** P2  
**Depends on:** T35  
**Blocks:** T40  

## Files to Create

| File | Purpose |
|---|---|
| `website/src/pages/Dashboard.tsx` | Main dashboard |
| `website/src/components/EntropyDashboard.tsx` | Entropy visualization |
| `website/src/components/TaskList.tsx` | Active + recent tasks |

## Acceptance Criteria
- [ ] Real-time updates: dashboard refreshes every 30 seconds
- [ ] Entropy scores: visual gauge for all components
- [ ] Active task: current action shown with progress
- [ ] System health: all green when everything working

---

# T38 — Sub-Agents (A2A Protocol)

**Complexity:** HIGH  
**Priority:** P2  
**Depends on:** T34  
**Blocks:** T39  

## Context
Sub-agents enable true parallel intelligence. Each sub-agent has its own context, its own MoA pipeline, its own circuit breaker. They communicate via the A2A protocol — the 2026 industry standard.

## Files to Create

| File | Purpose |
|---|---|
| `packages/sub_agents/orchestrator.py` | Spawn + coordinate |
| `packages/sub_agents/a2a_protocol.py` | Standard messaging |
| `packages/sub_agents/agent_factory.py` | Create sub-agent instances |

## Acceptance Criteria
- [ ] 5 sub-agents: all active simultaneously, no interference
- [ ] Sub-agent crash: orchestrator detects, restarts, resumes from checkpoint
- [ ] A2A messages: correct format (test against A2A spec)
- [ ] Sub-agent result: merged correctly into orchestrator context

---

# T39 — Tree of Thoughts + LATS

**Complexity:** HIGH  
**Priority:** P2  
**Depends on:** T38  
**Blocks:** T40  

## Files to Create

| File | Purpose |
|---|---|
| `packages/brain/thinking/tree_of_thoughts.py` | Multi-path reasoning |
| `packages/brain/thinking/graph_of_thoughts.py` | Non-linear synthesis |
| `packages/brain/thinking/lats.py` | AlphaGo-style simulation |

## Acceptance Criteria
- [ ] ToT: 3 reasoning paths explored simultaneously
- [ ] GoT: insights from different paths combined (not just winner-take-all)
- [ ] LATS: simulates 5 approaches before implementing any
- [ ] On Game-of-24 test: success rate >60% (baseline CoT: 4%)

---

# T40 — Integration Testing + Production Deployment

**Complexity:** HIGH  
**Priority:** P0  
**Depends on:** T39 (all previous)  
**Blocks:** Nothing (final ticket)  

## Context
The final ticket. Full system integration test followed by production deployment to ClawCloud + Cloudflare.

## Files to Create

| File | Purpose |
|---|---|
| `tests/integration/test_full_pipeline.py` | End-to-end tests |
| `tests/integration/test_memory_flow.py` | Memory integration |
| `tests/integration/test_key_rotation.py` | Key rotation under load |
| `infrastructure/scripts/deploy_production.sh` | One-command deploy |

## Integration Tests

```python
class TestFullPipeline:
    
    async def test_simple_question(self):
        """Ghost sends "what is osmosis" → receives answer in <15 seconds"""
    
    async def test_document_creation(self):
        """Ghost sends "write a PDF about HCl" → receives PDF link in <5 minutes"""
    
    async def test_memory_recall(self):
        """Store fact → retrieve fact → correct answer returned"""
    
    async def test_key_rotation_seamless(self):
        """Exhaust key during task → task continues without interruption"""
    
    async def test_circuit_breaker(self):
        """Trigger deliberate loop → circuit trips in <5 attempts"""
    
    async def test_spec_engine(self):
        """Complex task → all 7 docs generated → tickets in Notion"""
    
    async def test_100_day_project(self):
        """Long-running task → persists through restart → continues correctly"""
```

## Acceptance Criteria
- [ ] All 10 integration tests pass
- [ ] End-to-end simple question: <15 seconds
- [ ] End-to-end document: <5 minutes
- [ ] Production deployment: zero-downtime (blue-green)
- [ ] Post-deployment: all health checks green
- [ ] Ghost can send first real message within 5 minutes of deployment

---

## Ticket Summary

| Ticket | Name | Complexity | Traycer? |
|---|---|---|---|
| T1 | Repo Structure | LOW | No |
| T2 | Cloudflare Worker | MEDIUM | No |
| T3 | Discord Bot | MEDIUM | No |
| T4 | Database Connections | MEDIUM | No |
| T5 | MRKL Router | HIGH | No |
| **T6** | **Key Rotation Pool** | **VERY HIGH** | **✅ YES** |
| T7 | Quota Brain | MEDIUM | No |
| **T8** | **MoA Orchestrator** | **VERY HIGH** | **✅ YES** |
| T9 | Role-Based Proposers | HIGH | No |
| T10 | Self-Consistency + PRM | HIGH | No |
| T11 | Constitutional Critic | MEDIUM | No |
| T12 | Critic + Synthesizer | HIGH | No |
| T13 | Redis Memory T0+T1 | MEDIUM | No |
| **T14** | **Zilliz + Mem0** | **VERY HIGH** | **✅ YES** |
| T15 | Knowledge Graph | HIGH | No |
| T16 | RAPTOR + Zep + ACE | HIGH | No |
| T17 | Notion + DeepWiki | MEDIUM | No |
| T18 | Entropy Engine | HIGH | No |
| **T19** | **Circuit Breaker** | **VERY HIGH** | **✅ YES** |
| T20 | Tool Registry | MEDIUM | No |
| T21 | MCP Gateway | MEDIUM | No |
| T22 | Document Tools | MEDIUM | No |
| T23 | Code Tools | HIGH | No |
| T24 | Web Tools | MEDIUM | No |
| T25 | ChE Domain Tools | HIGH | No |
| T26 | Computer Use | VERY HIGH | No |
| **T27** | **Spec Engine** | **VERY HIGH** | **✅ YES** |
| T28 | AlphaEvolve | HIGH | No |
| T29 | Self-Modification | HIGH | No |
| T30 | Reflexion + ACE | MEDIUM | No |
| T31 | AFlow | MEDIUM | No |
| T32 | QStash Events | MEDIUM | No |
| T33 | Heartbeat + Watchdog | MEDIUM | No |
| T34 | Remote Work Pipeline | HIGH | No |
| T35 | Website | HIGH | No |
| T36 | Settings + Secrets | HIGH | No |
| T37 | Dashboard | MEDIUM | No |
| T38 | Sub-Agents A2A | HIGH | No |
| T39 | Tree of Thoughts + LATS | HIGH | No |
| T40 | Integration + Deploy | HIGH | No |

**Recommended for Traycer (5 tickets):**
- T6: Key Rotation Pool (concurrency critical)
- T8: MoA Orchestrator (most complex single component)
- T14: Zilliz + Mem0 (memory quality critical)
- T19: Circuit Breaker (safety critical)
- T27: Spec Engine (highest quality impact)
