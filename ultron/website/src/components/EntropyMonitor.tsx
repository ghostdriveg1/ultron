import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface EntropyData {
  time: string;
  entropy: number;
  cpu: number;
  memory: number;
}

const EntropyMonitor: React.FC = () => {
  const [data, setData] = useState<EntropyData[]>([]);

  useEffect(() => {
    const fetchEntropy = async () => {
      try {
        const res = await fetch('/api/entropy');
        if (res.ok) {
          const newData = await res.json();
          setData(prev => {
            const next = [...prev, newData];
            if (next.length > 20) return next.slice(1);
            return next;
          });
        }
      } catch (e) {
        console.error("Failed to fetch entropy", e);
      }
    };
    
    fetchEntropy();
    const interval = setInterval(fetchEntropy, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ backgroundColor: '#1e1e1e', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
      <h3 style={{ color: '#fff', marginBottom: '15px', fontFamily: 'Inter, sans-serif' }}>System Entropy & Health</h3>
      <div style={{ height: '300px', width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="time" stroke="#888" />
            <YAxis stroke="#888" />
            <Tooltip contentStyle={{ backgroundColor: '#333', border: 'none', borderRadius: '8px', color: '#fff' }} />
            <Line type="monotone" dataKey="entropy" stroke="#ff4d4f" strokeWidth={3} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="cpu" stroke="#1890ff" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="memory" stroke="#52c41a" strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: '15px', color: '#ccc', fontFamily: 'Inter, sans-serif' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#ff4d4f' }}></div>
          <span>System Entropy</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#1890ff' }}></div>
          <span>CPU Usage</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#52c41a' }}></div>
          <span>Memory Usage</span>
        </div>
      </div>
    </div>
  );
};

export default EntropyMonitor;
