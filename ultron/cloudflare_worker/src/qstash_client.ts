// ─── Ultron v3 — QStash Client ───────────────────────────────
// Publishes tasks to QStash for async delivery to ClawCloud Brain.

import type { Env, TaskPayload } from './types';

/**
 * Publish a task to QStash for async delivery to the Brain agent.
 * Retries up to 3 times with exponential backoff on failure.
 *
 * @param task - The task payload to publish
 * @param env - Worker environment bindings
 * @returns The QStash message ID on success
 * @throws Error if all retries fail
 */
export async function publishTask(
  task: TaskPayload,
  env: Env
): Promise<string> {
  const maxRetries = 3;
  const backoffMs = [1000, 2000, 4000];

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch(env.QSTASH_URL, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.QSTASH_TOKEN}`,
          'Content-Type': 'application/json',
          'Upstash-Destination': env.CLAWCLOUD_BRAIN_URL,
          'Upstash-Retries': '3',
        },
        body: JSON.stringify(task),
      });

      if (!response.ok) {
        throw new Error(`QStash responded with ${response.status}: ${await response.text()}`);
      }

      const result = (await response.json()) as { messageId: string };
      return result.messageId;
    } catch (err) {
      if (attempt < maxRetries - 1) {
        // Wait with exponential backoff before retrying
        await new Promise((resolve) => setTimeout(resolve, backoffMs[attempt]));
      } else {
        // All retries failed — log error to KV and throw
        try {
          await env.KV.put(
            `errors:qstash:${Date.now()}`,
            JSON.stringify({
              task_id: task.task_id,
              error: String(err),
              timestamp: new Date().toISOString(),
              attempts: maxRetries,
            })
          );
        } catch {
          // KV write failure is non-critical; swallow
        }
        throw new Error(
          `QStash publish failed after ${maxRetries} attempts: ${err}`
        );
      }
    }
  }

  // TypeScript requires a return, but this is unreachable
  throw new Error('Unreachable');
}
