import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

/**
 * KeyPoolStatus — Fetches /api/status every 30s and displays quota usage bars.
 */
export default function KeyPoolStatus() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['status'],
    queryFn: () => fetch('/api/status').then((r) => r.json()),
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
        <h3 className="text-sm font-semibold text-gray-400 mb-3">Key Pool Status</h3>
        <p className="text-gray-500 text-sm">Loading...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
        <h3 className="text-sm font-semibold text-gray-400 mb-3">Key Pool Status</h3>
        <p className="text-red-400 text-sm">Failed to fetch status</p>
      </div>
    );
  }

  const quotaData = Object.entries(data.quota_usage || {}).map(
    ([provider, usage]: [string, any]) => ({
      provider,
      used: usage.used || 0,
      total: usage.total || 0,
      remaining: Math.max(0, (usage.total || 0) - (usage.used || 0)),
    })
  );

  return (
    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
      <h3 className="text-sm font-semibold text-gray-400 mb-4">API Key Pool Status</h3>

      {quotaData.length === 0 ? (
        <p className="text-gray-500 text-sm">No quota data available yet</p>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={quotaData}>
            <XAxis dataKey="provider" tick={{ fontSize: 12, fill: '#9ca3af' }} />
            <YAxis tick={{ fontSize: 12, fill: '#9ca3af' }} />
            <Tooltip
              contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8 }}
              labelStyle={{ color: '#e5e7eb' }}
            />
            <Bar dataKey="used" fill="#22d3ee" name="Used" radius={[4, 4, 0, 0]} />
            <Bar dataKey="remaining" fill="#374151" name="Remaining" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}

      <div className="flex gap-4 mt-4 text-xs text-gray-500">
        <span>🟢 {data.brain_healthy ? 'Brain Online' : '🔴 Brain Offline'}</span>
        <span>🟢 {data.memory_healthy ? 'Memory Online' : '🔴 Memory Offline'}</span>
        <span>📋 {data.active_tasks || 0} active tasks</span>
      </div>
    </div>
  );
}
