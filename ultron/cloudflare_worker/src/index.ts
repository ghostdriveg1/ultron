// ─── Ultron v3 — Cloudflare Worker Entry Point ──────────────
// Hono-based HTTP router exposing Discord webhook, secrets API, and status endpoints.

import { Hono } from 'hono';
import type { Env } from './types';
import { discordWebhookHandler, internalTaskHandler, statusHandler } from './router';
import { handleSecretSave, handleSecretList, handleSecretDelete } from './secrets_handler';

const app = new Hono<{ Bindings: Env }>();

// ─── Internal Bot→Worker Endpoint ────────────────────────────
app.post('/internal/task', async (c) => {
  return internalTaskHandler(c.req.raw, c.env);
});

// ─── Discord Webhook ─────────────────────────────────────────
app.post('/discord/webhook', async (c) => {
  return discordWebhookHandler(c.req.raw, c.env);
});

// ─── Secrets Management ──────────────────────────────────────
app.post('/api/settings/key', async (c) => {
  return handleSecretSave(c.req.raw, c.env);
});

app.get('/api/settings/keys/:service', async (c) => {
  const service = c.req.param('service');
  return handleSecretList(service, c.env);
});

app.delete('/api/settings/key/:key', async (c) => {
  const key = c.req.param('key');
  return handleSecretDelete(key, c.env);
});

// ─── Status ──────────────────────────────────────────────────
app.get('/api/status', async (c) => {
  return statusHandler(c.env);
});

// ─── Health Check ────────────────────────────────────────────
app.get('/health', (c) => {
  return c.json({ status: 'alive', version: '3.1' });
});

// ─── Export ──────────────────────────────────────────────────
export default app;
