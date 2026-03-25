import React, { useState, useEffect } from 'react';

interface MemoryTier {
  id: string;
  name: string;
  description: string;
  stats: Record<string, string>;
  color: string;
}

interface SearchResult {
  id: string;
  content: string;
  score: number;
}

const Memory: React.FC = () => {
  const [tiers, setTiers] = useState<MemoryTier[]>([]);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchTiers = async () => {
      try {
        const res = await fetch('/api/memory/tiers');
        if (res.ok) {
          setTiers(await res.json());
        }
      } catch (e) {
        console.error("Failed to fetch memory tiers", e);
      }
    };
    fetchTiers();
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/memory/search?q=${encodeURIComponent(query)}`);
      if (res.ok) {
        setResults(await res.json());
      }
    } catch (e) {
      console.error("Search failed", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '30px', fontFamily: 'Inter, sans-serif', backgroundColor: '#121212', minHeight: '100vh', color: '#e0e0e0' }}>
      <header style={{ marginBottom: '30px', borderBottom: '1px solid #333', paddingBottom: '20px' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: 0, color: '#fff' }}>Memory Tiers & Search</h1>
        <p style={{ color: '#888', marginTop: '10px', fontSize: '1.1rem' }}>Manage semantic chunks, context sliding windows, and cold storage.</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '24px', marginBottom: '40px' }}>
        {tiers.map(tier => (
          <div key={tier.id} style={{ backgroundColor: '#1e1e1e', padding: '24px', borderRadius: '12px', borderTop: `4px solid ${tier.color}` }}>
            <h2 style={{ margin: '0 0 15px 0', fontSize: '1.5rem', color: '#fff' }}>{tier.name}</h2>
            <p style={{ color: '#aaa', marginBottom: '20px' }}>{tier.description}</p>
            <div style={{ backgroundColor: '#121212', padding: '15px', borderRadius: '8px', fontFamily: 'monospace', color: tier.color }}>
              {Object.entries(tier.stats).map(([k, v]) => (
                <div key={k}>{k}: {v}</div>
              ))}
            </div>
          </div>
        ))}
        {tiers.length === 0 && <p style={{ color: '#888' }}>Loading memory infrastructure...</p>}
      </div>

      <div style={{ backgroundColor: '#1e1e1e', padding: '24px', borderRadius: '12px' }}>
        <h2 style={{ fontSize: '1.5rem', marginBottom: '20px', color: '#fff' }}>Semantic Knowledge Search</h2>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search Zilliz / FAISS collections..." 
            style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid #333', backgroundColor: '#121212', color: '#fff' }}
          />
          <button type="submit" disabled={loading} style={{ padding: '12px 24px', borderRadius: '8px', backgroundColor: '#1890ff', color: '#fff', border: 'none', cursor: 'pointer' }}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          {results.map(res => (
            <div key={res.id} style={{ padding: '15px', backgroundColor: '#2d2d2d', borderRadius: '8px' }}>
              <div style={{ color: '#888', fontSize: '0.85rem', marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
                <span>ID: {res.id}</span>
                <span style={{ color: '#52c41a' }}>Score: {res.score.toFixed(4)}</span>
              </div>
              <p style={{ margin: 0, color: '#e0e0e0', lineHeight: '1.5' }}>{res.content}</p>
            </div>
          ))}
          {results.length === 0 && !loading && <p style={{ color: '#888' }}>No results found.</p>}
        </div>
      </div>
    </div>
  );
};

export default Memory;
