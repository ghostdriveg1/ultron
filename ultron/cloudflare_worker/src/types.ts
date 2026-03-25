// ─── Ultron v3 — Cloudflare Worker Type Definitions ──────────
// All TypeScript interfaces for the Worker layer.

/** Cloudflare Worker environment bindings */
export interface Env {
  KV: KVNamespace;
  DISCORD_BOT_TOKEN: string;
  DISCORD_PUBLIC_KEY: string;
  DISCORD_GHOST_USER_ID: string;
  CLAWCLOUD_BRAIN_URL: string;
  QSTASH_URL: string;
  QSTASH_TOKEN: string;
  WORKER_ENCRYPTION_KEY: string;
  INTERNAL_AUTH_TOKEN: string;
}

/** Discord webhook payload */
export interface DiscordMessage {
  type: number;
  data?: Record<string, unknown>;
  content?: string;
  author: {
    id: string;
    bot: boolean;
  };
  channel_id: string;
}

/** Task type classification */
export type TaskType =
  | 'CONVERSATIONAL'
  | 'CODE'
  | 'DOCUMENT'
  | 'RESEARCH'
  | 'CHE'
  | 'REMOTE_WORK'
  | 'COMPLEX'
  | 'COMPUTER_USE'
  | 'SELF_IMPROVEMENT';

/** Task payload sent to Brain via QStash */
export interface TaskPayload {
  task_id: string;
  type: TaskType;
  payload: {
    message: string;
    user_id: string;
    channel_id: string;
  };
  priority: 'URGENT' | 'NORMAL' | 'BACKGROUND';
  deadline: string;
  callback: 'discord' | 'notion' | 'github';
}

/** Encrypted secret entry for KV storage */
export interface SecretEntry {
  service: string;
  value: string;
}

/** Health check response */
export interface HealthResponse {
  status: string;
  version: string;
}

/** Status response from Brain */
export interface StatusResponse {
  brain_healthy: boolean;
  memory_healthy: boolean;
  active_tasks: number;
  quota_usage: Record<string, { used: number; total: number }>;
  entropy_scores: {
    system: number;
    memory: number;
    codebase: number;
  };
}
