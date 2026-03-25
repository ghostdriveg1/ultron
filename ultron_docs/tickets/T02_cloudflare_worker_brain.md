# T2 — Cloudflare Worker Brain (Entry Point)

## Context
The Cloudflare Worker is the single entry point for ALL external communication. It receives Discord webhooks, validates them, classifies intent, and routes tasks via QStash to the ClawCloud brain agent. This is the nervous system entry point.

**Dependencies:** T1  
**Blocks:** T3 (Discord bot needs Worker URL), T6 (Router needs Worker)

## Files to Create/Modify

| File | Action | Purpose |
|---|---|---|
| `cloudflare_worker/src/index.ts` | Create | Main request handler |
| `cloudflare_worker/src/intent_parser.ts` | Create | Complexity classification |
| `cloudflare_worker/src/discord_handler.ts` | Create | Discord signature verification |
| `cloudflare_worker/src/secrets_handler.ts` | Create | KV secrets management API |
| `cloudflare_worker/src/qstash_client.ts` | Create | Message queue publisher |
| `cloudflare_worker/src/types.ts` | Modify | Add all TypeScript interfaces |

## Implementation Plan

### Step 1: Discord Signature Verification
```typescript
// discord_handler.ts
async function verifyDiscordSignature(
  request: Request,
  env: Env
): Promise<boolean> {
  const signature = request.headers.get('X-Signature-Ed25519')
  const timestamp = request.headers.get('X-Signature-Timestamp')
  // Use crypto.subtle to verify Ed25519 signature
  // Return false = reject with 401
  // Return true = proceed
}
```

### Step 2: Intent Classification
```typescript
// intent_parser.ts
type TaskType = 'CONVERSATIONAL' | 'CODE' | 'DOCUMENT' | 
                'RESEARCH' | 'CHE' | 'REMOTE_WORK' | 'COMPLEX'

function classifyIntent(message: string): TaskType {
  // Rule-based fast classification
  // Keywords: "build", "create", "write" → COMPLEX
  // Keywords: "what", "how", "when" → CONVERSATIONAL  
  // Keywords: "calculate", "mass balance" → CHE
  // Short questions → CONVERSATIONAL
  // Long tasks → COMPLEX
}
```

### Step 3: QStash Routing
```typescript
// qstash_client.ts
async function routeToAgent(
  taskType: TaskType,
  payload: object,
  env: Env
): Promise<void> {
  await fetch(env.QSTASH_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.QSTASH_TOKEN}`,
      'Content-Type': 'application/json',
      'Upstash-Destination': env.CLAWCLOUD_BRAIN_URL
    },
    body: JSON.stringify({
      task_id: crypto.randomUUID(),
      type: taskType,
      payload,
      timestamp: new Date().toISOString()
    })
  })
}
```

### Step 4: Secrets Management Endpoint
```typescript
// secrets_handler.ts
// POST /api/settings/key
// Receives key from website, encrypts, stores in KV
// Returns success/failure
// Never logs key values
```

### Step 5: Main Handler
```typescript
// index.ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url)
    
    // Route: Discord webhook
    if (url.pathname === '/discord' && request.method === 'POST') {
      const valid = await verifyDiscordSignature(request, env)
      if (!valid) return new Response('Unauthorized', { status: 401 })
      
      const body = await request.json()
      
      // Discord PING verification
      if (body.type === 1) return Response.json({ type: 1 })
      
      // Actual message
      const message = body.data?.options?.[0]?.value || body.content
      const taskType = classifyIntent(message)
      await routeToAgent(taskType, body, env)
      
      return Response.json({ type: 5 }) // Deferred response
    }
    
    // Route: Settings (from website)
    if (url.pathname === '/api/settings/key') {
      return handleSecretStorage(request, env)
    }
    
    // Route: Status (for website dashboard)
    if (url.pathname === '/api/status') {
      return handleStatus(request, env)
    }
    
    return new Response('Not Found', { status: 404 })
  }
}
```

## Acceptance Criteria
- [ ] Discord message received → QStash message published within 50ms
- [ ] Invalid Discord signature → 401 returned, nothing processed
- [ ] PING request → immediately returns `{ type: 1 }`
- [ ] API key pasted in website → stored in KV encrypted within 200ms
- [ ] `/api/status` returns system health JSON
- [ ] Worker handles 1000+ requests/minute without errors
- [ ] No secrets ever appear in Worker logs

## Edge Cases
- Discord sends retry if no 200 within 3 seconds: return 200 immediately, process async via QStash
- KV write fails: return error to website, don't silently lose the key
- QStash unavailable: store task in KV queue for retry
