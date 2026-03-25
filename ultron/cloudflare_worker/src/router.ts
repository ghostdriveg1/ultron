// ─── Ultron v3 — Discord Webhook Router ─────────────────────
// Core routing logic: signature verification → Ghost whitelist → classify → dispatch.

import { verifyDiscordSignature } from './auth';
import { publishTask } from './qstash_client';
import type { Env, DiscordMessage, TaskPayload, TaskType } from './types';

/** Keywords that indicate a task (not conversational) */
const TASK_KEYWORDS = [
  'build', 'create', 'write', 'calculate', 'research',
  'deploy', 'generate', 'design', 'implement', 'fix',
  'debug', 'analyze', 'test', 'refactor', 'optimize',
];

/**
 * Classify message mode: 'instant' (conversational) or 'deep' (complex task).
 */
function classifyMode(content: string): 'instant' | 'deep' {
  if (!content) return 'instant';

  const lower = content.toLowerCase();

  // Short message with no task keywords → instant
  if (content.length < 100) {
    const hasTaskKeyword = TASK_KEYWORDS.some((kw) => lower.includes(kw));
    if (!hasTaskKeyword) return 'instant';
  }

  return 'deep';
}

/**
 * Classify the task type from the message content.
 */
function classifyTaskType(content: string): TaskType {
  const lower = content.toLowerCase();

  if (/mass balance|thermo|distillation|heat transfer|reaction|coolprop/.test(lower)) return 'CHE';
  if (/write code|debug|implement|refactor|test|lint|deploy/.test(lower)) return 'CODE';
  if (/create.*report|write.*document|make.*pdf|latex|presentation/.test(lower)) return 'DOCUMENT';
  if (/research|find papers|arxiv|survey|compare/.test(lower)) return 'RESEARCH';
  if (/open.*app|click|screenshot|gui|hysys|aspen/.test(lower)) return 'COMPUTER_USE';
  if (/build.*forever|improve.*continuously|100.day|long.term/.test(lower)) return 'REMOTE_WORK';
  if (/improve.*self|optimize.*own|evolve/.test(lower)) return 'SELF_IMPROVEMENT';

  // Multi-step or long messages default to COMPLEX
  if (content.length > 200) return 'COMPLEX';

  return 'CONVERSATIONAL';
}

/**
 * Send a message to Discord via REST API.
 */
async function sendDiscordMessage(
  channelId: string,
  content: string,
  botToken: string
): Promise<void> {
  await fetch(`https://discord.com/api/v10/channels/${channelId}/messages`, {
    method: 'POST',
    headers: {
      'Authorization': `Bot ${botToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ content }),
  });
}

/**
 * Handle incoming Discord webhook requests.
 * Flow: verify signature → check author → classify → dispatch.
 */
export async function discordWebhookHandler(
  request: Request,
  env: Env
): Promise<Response> {
  // 1. Verify Discord signature
  const isValid = await verifyDiscordSignature(request, env.DISCORD_PUBLIC_KEY);
  if (!isValid) {
    await env.KV.put(
      `security:failed_auth:${Date.now()}`,
      JSON.stringify({ timestamp: new Date().toISOString() })
    );
    return new Response('Unauthorized', { status: 401 });
  }

  // 2. Parse body
  const body = (await request.json()) as DiscordMessage;

  // 3. Discord PING — respond with PONG
  if (body.type === 1) {
    return Response.json({ type: 1 });
  }

  // 4. Check Ghost whitelist
  const ghostId = env.DISCORD_GHOST_USER_ID;
  if (body.author?.id !== ghostId) {
    return new Response('OK', { status: 200 });
  }

  const content = body.content || '';
  const channelId = body.channel_id;

  // 5. Classify mode and task type
  const mode = classifyMode(content);
  const taskType = classifyTaskType(content);

  // 6. Build task payload
  const task: TaskPayload = {
    task_id: crypto.randomUUID(),
    type: taskType,
    payload: {
      message: content,
      user_id: body.author.id,
      channel_id: channelId,
    },
    priority: mode === 'instant' ? 'URGENT' : 'NORMAL',
    deadline: new Date(Date.now() + (mode === 'instant' ? 30000 : 300000)).toISOString(),
    callback: 'discord',
  };

  // 7. Route based on mode
  if (mode === 'instant') {
    // Direct forward to Brain for fast response
    try {
      const brainResponse = await fetch(env.CLAWCLOUD_BRAIN_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(task),
      });

      if (brainResponse.ok) {
        return Response.json({ task_id: task.task_id, mode: 'instant' });
      }
    } catch {
      // Fall through to QStash on failure
    }
  }

  // 8. Deep mode: send thinking indicator, publish to QStash
  await sendDiscordMessage(channelId, '🤔 Thinking...', env.DISCORD_BOT_TOKEN);

  try {
    await publishTask(task, env);
  } catch (err) {
    await sendDiscordMessage(
      channelId,
      `⚠️ Failed to queue task: ${err}`,
      env.DISCORD_BOT_TOKEN
    );
  }

  return Response.json({ task_id: task.task_id, mode: 'deep' });
}

/**
 * Handle POST /internal/task — internal bot-to-worker forwarding.
 * Validates X-Ultron-Token header (no Discord signature required).
 * Classifies and dispatches like the webhook, but skips sig/Ghost checks.
 */
export async function internalTaskHandler(
  request: Request,
  env: Env
): Promise<Response> {
  // 1. Validate shared token
  const token = request.headers.get('X-Ultron-Token');
  if (!token || token !== env.INTERNAL_AUTH_TOKEN) {
    return new Response('Unauthorized', { status: 401 });
  }

  // 2. Parse body
  const body = (await request.json()) as {
    content: string;
    channel_id: string;
    user_id: string;
  };

  const content = body.content || '';
  const channelId = body.channel_id;

  // 3. Classify mode and task type
  const mode = classifyMode(content);
  const taskType = classifyTaskType(content);

  // 4. Build task payload
  const task: TaskPayload = {
    task_id: crypto.randomUUID(),
    type: taskType,
    payload: {
      message: content,
      user_id: body.user_id,
      channel_id: channelId,
    },
    priority: mode === 'instant' ? 'URGENT' : 'NORMAL',
    deadline: new Date(Date.now() + (mode === 'instant' ? 30000 : 300000)).toISOString(),
    callback: 'discord',
  };

  // 5. Route based on mode
  if (mode === 'instant') {
    try {
      const brainResponse = await fetch(env.CLAWCLOUD_BRAIN_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(task),
      });

      if (brainResponse.ok) {
        return Response.json({ task_id: task.task_id, mode: 'instant' });
      }
    } catch {
      // Fall through to QStash on failure
    }
  }

  // 6. Deep mode: send thinking indicator, publish to QStash
  await sendDiscordMessage(channelId, '🤔 Thinking...', env.DISCORD_BOT_TOKEN);

  try {
    await publishTask(task, env);
  } catch (err) {
    await sendDiscordMessage(
      channelId,
      `⚠️ Failed to queue task: ${err}`,
      env.DISCORD_BOT_TOKEN
    );
  }

  return Response.json({ task_id: task.task_id, mode: 'deep' });
}

/**
 * Handle GET /api/status — fetch Brain health and return combined status.
 */
export async function statusHandler(env: Env): Promise<Response> {
  try {
    const brainResponse = await fetch(`${env.CLAWCLOUD_BRAIN_URL}/health`, {
      signal: AbortSignal.timeout(5000),
    });

    if (brainResponse.ok) {
      const health = await brainResponse.json();
      return Response.json(health);
    }

    return Response.json({
      brain_healthy: false,
      memory_healthy: false,
      active_tasks: 0,
      quota_usage: {},
      entropy_scores: { system: 0, memory: 0, codebase: 0 },
    });
  } catch {
    return Response.json({
      brain_healthy: false,
      memory_healthy: false,
      active_tasks: 0,
      quota_usage: {},
      entropy_scores: { system: 0, memory: 0, codebase: 0 },
    });
  }
}
