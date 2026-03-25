import { useState, useEffect } from 'react';
import SecretField from '../components/SecretField';
import KeyPoolStatus from '../components/KeyPoolStatus';

/**
 * Settings page — paste-and-save UX for all API keys.
 * No forms, no submit buttons. Each field auto-saves on paste.
 * Fetches per-service key counts and shows status badges.
 */

interface ServiceGroup {
  title: string;
  service: string;
  keys: Array<{ label: string; placeholder: string }>;
}

interface ServiceStatus {
  count: number;
  keys: Array<{ key: string; masked: string }>;
}

const SERVICE_GROUPS: ServiceGroup[] = [
  {
    title: '🔵 Gemini',
    service: 'gemini',
    keys: Array.from({ length: 20 }, (_, i) => ({
      label: `Gemini Key ${i + 1}`,
      placeholder: 'AIzaSy...',
    })),
  },
  {
    title: '🟢 Groq',
    service: 'groq',
    keys: Array.from({ length: 10 }, (_, i) => ({
      label: `Groq Key ${i + 1}`,
      placeholder: 'gsk_...',
    })),
  },
  {
    title: '🟣 OpenRouter',
    service: 'openrouter',
    keys: Array.from({ length: 10 }, (_, i) => ({
      label: `OpenRouter Key ${i + 1}`,
      placeholder: 'sk-or-...',
    })),
  },
  {
    title: '⚡ Cerebras',
    service: 'cerebras',
    keys: Array.from({ length: 5 }, (_, i) => ({
      label: `Cerebras Key ${i + 1}`,
      placeholder: 'csk-...',
    })),
  },
  {
    title: '🔶 Together',
    service: 'together',
    keys: Array.from({ length: 5 }, (_, i) => ({
      label: `Together Key ${i + 1}`,
      placeholder: 'tog-...',
    })),
  },
  {
    title: '📊 Zilliz',
    service: 'zilliz',
    keys: Array.from({ length: 15 }, (_, i) => ({
      label: `Zilliz Account ${i + 1}`,
      placeholder: 'https://...',
    })),
  },
  {
    title: '🖥️ Puter',
    service: 'puter',
    keys: [{ label: 'Puter Auth Token', placeholder: 'puter_...' }],
  },
  {
    title: '🔍 Parallel AI',
    service: 'parallel_ai',
    keys: Array.from({ length: 20 }, (_, i) => ({
      label: `Parallel AI Key ${i + 1}`,
      placeholder: 'pai-...',
    })),
  },
  {
    title: '🔥 Firecrawl',
    service: 'firecrawl',
    keys: [{ label: 'Firecrawl Key', placeholder: 'fc-...' }],
  },
  {
    title: '🕷️ Apify',
    service: 'apify',
    keys: [{ label: 'Apify Key', placeholder: 'apify_api_...' }],
  },
  {
    title: '📦 E2B',
    service: 'e2b',
    keys: [{ label: 'E2B Key', placeholder: 'e2b_...' }],
  },
  {
    title: '📁 Fast.io',
    service: 'fastio',
    keys: [{ label: 'Fast.io Key', placeholder: 'fio_...' }],
  },
  {
    title: '📝 Notion',
    service: 'notion',
    keys: [{ label: 'Notion Token', placeholder: 'ntn_...' }],
  },
  {
    title: '🐙 GitHub',
    service: 'github',
    keys: [{ label: 'GitHub Token', placeholder: 'ghp_...' }],
  },
];

/**
 * Derive status badge from key count.
 * 🟢 = has keys, 🟡 = low (<3), 🔴 = no keys
 */
function getStatusBadge(count: number): string {
  if (count === 0) return '🔴';
  if (count < 3) return '🟡';
  return '🟢';
}

export default function Settings() {
  const [serviceStatuses, setServiceStatuses] = useState<Record<string, ServiceStatus>>({});

  // Fetch key counts for each service on mount
  useEffect(() => {
    async function fetchAllStatuses() {
      const statuses: Record<string, ServiceStatus> = {};

      await Promise.all(
        SERVICE_GROUPS.map(async (group) => {
          try {
            const resp = await fetch(`/api/settings/keys/${group.service}`);
            if (resp.ok) {
              const data = await resp.json();
              const keys = (data.keys || []).map((k: { key: string; masked_value: string }) => ({
                key: k.key,
                masked: k.masked_value,
              }));
              statuses[group.service] = { count: data.count || 0, keys };
            } else {
              statuses[group.service] = { count: 0, keys: [] };
            }
          } catch {
            statuses[group.service] = { count: 0, keys: [] };
          }
        })
      );

      setServiceStatuses(statuses);
    }

    fetchAllStatuses();
  }, []);

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">Settings</h1>
      <p className="text-gray-400 mb-8">
        Paste API keys below. They are encrypted and stored securely in Cloudflare KV.
      </p>

      <KeyPoolStatus />

      <div className="space-y-8 mt-8">
        {SERVICE_GROUPS.map((group) => {
          const status = serviceStatuses[group.service];
          const count = status?.count ?? 0;
          const badge = getStatusBadge(count);

          return (
            <section key={group.service} className="bg-gray-900 rounded-xl p-6 border border-gray-800">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">{group.title}</h2>
                <span className="text-sm text-gray-400 flex items-center gap-1.5">
                  {badge}
                  <span className="font-mono">{count} key{count !== 1 ? 's' : ''}</span>
                </span>
              </div>
              <div className="space-y-3">
                {group.keys.map((key, idx) => (
                  <SecretField
                    key={`${group.service}-${idx}`}
                    service={group.service}
                    label={key.label}
                    placeholder={key.placeholder}
                    initialSavedKeys={status?.keys}
                  />
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}
