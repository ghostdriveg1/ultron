// Ultron v3 - QStash Client
import type { Env, TaskPayload } from './types';

export async function publishTask(task: TaskPayload, env: Env): Promise<string> {
  const maxRetries = 3;
  const backoffMs = [1000, 2000, 4000];

  const brainPayload = {
    message: task.payload.message,
    user_id: task.payload.user_id,
    channel_id: task.payload.channel_id,
    task_id: task.task_id,
    task_type: task.type,
  };

  const qstashUrl = `https://qstash.upstash.io/v2/publish/${encodeURIComponent(env.CLAWCLOUD_BRAIN_URL + '/run')}`;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch(qstashUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.QSTASH_TOKEN}`,
          'Content-Type': 'application/json',
          'Upstash-Retries': '3',
        },
        body: JSON.stringify(brainPayload),
      });

      if (!response.ok) {
        throw new Error(`QStash responded with ${response.status}: ${await response.text()}`);
      }

      const result = (await response.json()) as { messageId: string };
      return result.messageId;

    } catch (err) {
      if (attempt < maxRetries - 1) {
        await new Promise((resolve) => setTimeout(resolve, backoffMs[attempt]));
      } else {
        throw new Error(`QStash publish failed after ${maxRetries} attempts: ${err}`);
      }
    }
  }
  throw new Error('Unreachable');
}
