// ─── Ultron v3 — Secrets Handler ─────────────────────────────
// CRUD operations for encrypted API key storage in Cloudflare KV.

import { KVClient } from './kv_client';
import type { Env, SecretEntry } from './types';

/**
 * POST /api/settings/key — Store a new API key (encrypted).
 */
export async function handleSecretSave(
  request: Request,
  env: Env
): Promise<Response> {
  try {
    const body = (await request.json()) as SecretEntry;

    if (!body.service || body.service.trim().length === 0) {
      return Response.json(
        { error: 'Service name is required' },
        { status: 400 }
      );
    }

    if (!body.value || body.value.length < 10) {
      return Response.json(
        { error: 'API key must be at least 10 characters' },
        { status: 400 }
      );
    }

    const kvClient = new KVClient(env.KV, env.WORKER_ENCRYPTION_KEY);
    const keyId = crypto.randomUUID();
    const kvKey = `secret:${body.service}:${keyId}`;

    await kvClient.setSecret(kvKey, body.value);

    // Increment key count for service
    const countKey = `secret:${body.service}:count`;
    const currentCount = parseInt((await env.KV.get(countKey)) || '0', 10);
    await env.KV.put(countKey, String(currentCount + 1));

    return Response.json({
      stored: true,
      key_count: currentCount + 1,
      key_id: kvKey,
    });
  } catch (err) {
    return Response.json(
      { error: 'Failed to store secret', detail: String(err) },
      { status: 500 }
    );
  }
}

/**
 * GET /api/settings/keys/:service — List masked keys for a service.
 */
export async function handleSecretList(
  service: string,
  env: Env
): Promise<Response> {
  try {
    const kvClient = new KVClient(env.KV, env.WORKER_ENCRYPTION_KEY);
    const keys = await kvClient.listSecrets(`secret:${service}:`);

    // Filter out the :count key
    const secretKeys = keys.filter((k) => !k.endsWith(':count'));

    const masked: Array<{ key: string; masked_value: string }> = [];
    for (const k of secretKeys) {
      const value = await kvClient.getSecret(k);
      if (value) {
        const maskedValue =
          value.length > 8
            ? `${value.slice(0, 4)}...${value.slice(-4)}`
            : '****';
        masked.push({ key: k, masked_value: maskedValue });
      }
    }

    return Response.json({
      service,
      keys: masked,
      count: masked.length,
    });
  } catch (err) {
    return Response.json(
      { error: 'Failed to list secrets', detail: String(err) },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/settings/key/:key — Delete a specific key.
 */
export async function handleSecretDelete(
  key: string,
  env: Env
): Promise<Response> {
  try {
    const kvClient = new KVClient(env.KV, env.WORKER_ENCRYPTION_KEY);
    await kvClient.deleteSecret(key);

    // Decrement count
    const parts = key.split(':');
    if (parts.length >= 2) {
      const service = parts[1];
      const countKey = `secret:${service}:count`;
      const currentCount = parseInt((await env.KV.get(countKey)) || '1', 10);
      await env.KV.put(countKey, String(Math.max(0, currentCount - 1)));
    }

    return Response.json({ deleted: true, key });
  } catch (err) {
    return Response.json(
      { error: 'Failed to delete secret', detail: String(err) },
      { status: 500 }
    );
  }
}
