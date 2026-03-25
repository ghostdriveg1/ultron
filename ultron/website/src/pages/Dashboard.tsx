import React, { useState, useEffect } from 'react';
import EntropyMonitor from '../components/EntropyMonitor';

interface LogEntry {
  time: string;
  level: string;
  message: string;
}

interface DashboardStats {
  globalStatus: string;
  activeAgents: string;
  queuedTasks: number;
  recentLogs: LogEntry[];
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    globalStatus: 'Connecting...',
    activeAgents: '0 / 0',
    queuedTasks: 0,
    recentLogs: []
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('/api/status');
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (e) {
        console.error("Failed to fetch dashboard stats", e);
      }
    };
    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '30px', fontFamily: 'Inter, sans-serif', backgroundColor: '#121212', minHeight: '100vh', color: '#e0e0e0' }}>
      <header style={{ marginBottom: '30px', borderBottom: '1px solid #333', paddingBottom: '20px' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: 0, background: 'linear-gradient(90deg, #1890ff, #52c41a)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Ultron Command Center
        </h1>
        <p style={{ color: '#888', marginTop: '10px', fontSize: '1.1rem' }}>Overall system health and execution status.</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '30px' }}>
        <div style={{ backgroundColor: '#1e1e1e', padding: '24px', borderRadius: '12px', borderLeft: '4px solid #52c41a' }}>
          <h4 style={{ margin: 0, color: '#888', textTransform: 'uppercase', fontSize: '0.85rem', letterSpacing: '1px' }}>Global Status</h4>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '10px 0 0 0', color: '#fff' }}>{stats.globalStatus}</p>
        </div>
        <div style={{ backgroundColor: '#1e1e1e', padding: '24px', borderRadius: '12px', borderLeft: '4px solid #1890ff' }}>
          <h4 style={{ margin: 0, color: '#888', textTransform: 'uppercase', fontSize: '0.85rem', letterSpacing: '1px' }}>Active Agents</h4>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '10px 0 0 0', color: '#fff' }}>{stats.activeAgents}</p>
        </div>
        <div style={{ backgroundColor: '#1e1e1e', padding: '24px', borderRadius: '12px', borderLeft: '4px solid #ff4d4f' }}>
          <h4 style={{ margin: 0, color: '#888', textTransform: 'uppercase', fontSize: '0.85rem', letterSpacing: '1px' }}>Queued Tasks</h4>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', margin: '10px 0 0 0', color: '#fff' }}>{stats.queuedTasks}</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '15px' }}>Live Metrics</h2>
          <EntropyMonitor />
        </div>
        
        <div style={{ backgroundColor: '#1e1e1e', padding: '24px', borderRadius: '12px' }}>
          <h2 style={{ fontSize: '1.5rem', margin: '0 0 20px 0', borderBottom: '1px solid #333', paddingBottom: '10px' }}>Recent Logs</h2>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {stats.recentLogs.map((log, i) => (
              <li key={i} style={{ fontSize: '0.9rem' }}>
                <span style={{ color: '#888', marginRight: '10px' }}>[{log.time}]</span>
                <span style={{ color: log.level === 'WARN' || log.level === 'ERROR' ? '#ff4d4f' : '#52c41a' }}>[{log.level}]</span> {log.message}
              </li>
            ))}
            {stats.recentLogs.length === 0 && <li style={{ color: '#888' }}>No recent logs.</li>}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
