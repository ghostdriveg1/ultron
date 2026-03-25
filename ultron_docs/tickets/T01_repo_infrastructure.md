# T1 — Repository Setup & Infrastructure

## Context
This is the foundation ticket. Nothing else can be built without this. Creates the entire repository structure, all configuration files, Docker setup, and development environment.

**Dependencies:** None (first ticket)  
**Blocks:** T2, T3, T4, T5, T6, T7, T8 (everything)

## Files to Create

| File | Purpose |
|---|---|
| `ultron/cloudflare_worker/wrangler.toml` | CF Worker config |
| `ultron/cloudflare_worker/package.json` | Worker dependencies |
| `ultron/cloudflare_worker/src/index.ts` | Worker skeleton |
| `ultron/cloudflare_worker/src/types.ts` | TypeScript interfaces |
| `ultron/docker-compose.yml` | Local dev environment |
| `ultron/.env.example` | All env var documentation |
| `ultron/requirements.txt` | All Python dependencies |
| `ultron/package.json` | Root Node.js config |
| `ultron/.gitignore` | Ignore secrets and build artifacts |
| `ultron/README.md` | Project overview |
| `ultron/config/model_routing.json` | Model assignments |
| `ultron/config/permissions.json` | Tool permission matrix |
| `ultron/config/whitelist.json` | Self-mod whitelist |
| `ultron/state/CURRENT_TASK.md` | Runtime state |
| `ultron/intent/ULTRON_INTENT.md` | Ghost's long-term goals |
| All `__init__.py` files | Python package markers |

## Implementation Plan

### Step 1: Create GitHub Repository
- Repository name: `ultron` (public, MIT license)
- Created under: `ghostdriveg1` account
- Branch protection: main branch protected
- CODEOWNERS file: mark sacred files

### Step 2: Create Cloudflare Worker Skeleton
```typescript
// cloudflare_worker/src/index.ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Receives Discord webhooks
    // Validates Discord signature
    // Routes to ClawCloud brain via QStash
    return new Response('OK')
  }
}

interface Env {
  DISCORD_BOT_TOKEN: string
  DISCORD_PUBLIC_KEY: string
  CLAWCLOUD_BRAIN_URL: string
  QSTASH_URL: string
  QSTASH_TOKEN: string
  KV: KVNamespace
}
```

### Step 3: Create docker-compose.yml
```yaml
version: '3.8'
services:
  brain:
    build: ./packages/brain
    env_file: .env
    volumes:
      - ./packages:/app/packages
    ports:
      - "8000:8000"
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Step 4: Create .env.example
Document every single environment variable with:
- Variable name
- Description
- Example value
- Which service uses it

### Step 5: Create config files
```json
// config/permissions.json
{
  "ALWAYS_ALLOWED": ["read_file", "search_web", "memory_read", "send_discord"],
  "ENTROPY_CHECKED": ["write_code", "create_document", "commit_github"],
  "GHOST_CONFIRM": ["delete_file", "deploy", "delete_repo"],
  "NEVER": ["delete_account", "billing_access"]
}

// config/whitelist.json
{
  "allowed": [
    "/tools/*",
    "/prompts/task_specific/*",
    "/config/model_routing.json",
    "/skills/generated/*"
  ],
  "forbidden": [
    "/brain/core/session.py",
    "/memory/restore.py",
    "/brain/key_rotation/pool.py",
    "/execution/watchdog.py",
    "/brain/circuit_breaker.py"
  ]
}
```

## Acceptance Criteria
- [ ] GitHub repo exists at github.com/ghostdriveg1/ultron
- [ ] All directories created with correct structure
- [ ] `wrangler deploy` runs without errors
- [ ] `docker-compose up` starts all services
- [ ] `.env.example` documents every required variable
- [ ] `requirements.txt` installs without conflicts
- [ ] All config files are valid JSON
- [ ] README explains the project clearly
- [ ] CODEOWNERS marks sacred files as protected

## Edge Cases
- If a Python dependency conflicts: pin exact version
- If wrangler version incompatible: specify exact version in package.json
- Ensure `.env` is in `.gitignore` — never commit secrets
