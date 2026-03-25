# ULTRON v3 — Autonomous AI Agent System

> **The most advanced personal autonomous AI agent ever built.**  
> Works while you sleep. Remembers everything forever. Costs $0/month.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ULTRON v3 SYSTEM                         │
│                                                                 │
│  GHOST (Any Device)                                             │
│  Discord App / Website                                          │
│       │                  │                                      │
│       ▼                  ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          CLOUDFLARE EDGE (Global, <50ms)                 │  │
│  │  Worker → Discord Handler → QStash Publisher             │  │
│  │  KV Store (AES-256-GCM encrypted) → Website API         │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │ QStash webhook                          │
│                       ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │       CLAWCLOUD BRAIN AGENT (4vCPU, 8GB RAM)             │  │
│  │  MRKL Router → MoA 8 Proposers → Critic → Synthesizer   │  │
│  │  Key Rotation Pool → Quota Brain → Circuit Breaker       │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│       ┌───────────────┼───────────────┐                        │
│       ▼               ▼               ▼                        │
│  ┌──────────┐  ┌────────────┐  ┌─────────────┐               │
│  │ Memory   │  │ Computer   │  │ GitHub      │               │
│  │ Agent    │  │ Use Agent  │  │ Actions     │               │
│  │ Zilliz×15│  │ Agent S3   │  │ Burst       │               │
│  │ Cognee   │  │ Xvfb       │  │ Compute     │               │
│  └──────────┘  └────────────┘  └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Setup

1. **Clone** the repository
2. **Copy** environment file:
   ```bash
   cp .env.example .env
   ```
3. **Fill in** your API keys in `.env`
4. **Run** the setup script:
   ```bash
   bash infrastructure/scripts/setup_dev.sh
   ```

## Project Structure

| Directory | Purpose |
|---|---|
| `cloudflare_worker/` | Edge router (TypeScript, Hono) |
| `packages/brain/` | Intelligence layer (Python) |
| `packages/memory/` | 5-tier memory system |
| `packages/infrastructure/` | Redis + Zilliz clients |
| `packages/interface/` | Discord bot |
| `packages/tools/` | 30+ tool registry |
| `packages/execution/` | Runtime + heartbeat |
| `website/` | React control panel |
| `config/` | Model routing, permissions |
| `skills/` | Domain-specific skills |

## Key Technologies

- **Brain**: LangChain + LangGraph, Mixture of Agents (8 proposers)
- **Memory**: Upstash Redis, Zilliz ×15, Cognee KG, Mem0
- **Edge**: Cloudflare Workers + KV (Hono framework)
- **Queue**: QStash (event-driven, no polling)
- **Interface**: Discord (py-cord) + React website
- **Compute**: ClawCloud Run ×3 + GitHub Actions

## License

MIT — Non-commercial research project.
