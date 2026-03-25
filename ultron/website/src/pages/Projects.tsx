import React, { useState, useEffect } from 'react';

interface Project {
  id: string;
  name: string;
  status: string;
  description: string;
  progress: number;
  milestones: string;
  color: string;
}

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const res = await fetch('/api/projects');
        if (res.ok) {
          const data = await res.json();
          setProjects(data);
        }
      } catch (e) {
        console.error("Failed to fetch projects", e);
      }
    };
    fetchProjects();
    const interval = setInterval(fetchProjects, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '30px', fontFamily: 'Inter, sans-serif', backgroundColor: '#121212', minHeight: '100vh', color: '#e0e0e0' }}>
      <header style={{ marginBottom: '30px', borderBottom: '1px solid #333', paddingBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', margin: 0, color: '#fff' }}>Projects & Specs</h1>
          <p style={{ color: '#888', marginTop: '10px', fontSize: '1.1rem' }}>Active engineering targets managed by the Spec Engine.</p>
        </div>
        <button style={{
          padding: '12px 24px', borderRadius: '8px', border: 'none', backgroundColor: '#1890ff', 
          color: '#fff', fontSize: '1rem', cursor: 'pointer', fontWeight: 'bold'
        }}>
          + New Project
        </button>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
        {projects.map(proj => (
          <div key={proj.id} style={{ backgroundColor: '#1e1e1e', borderRadius: '12px', overflow: 'hidden' }}>
            <div style={{ backgroundColor: '#2d2d2d', padding: '15px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, color: '#fff', fontSize: '1.2rem' }}>{proj.name}</h3>
              <span style={{ backgroundColor: proj.color || '#52c41a', color: '#121212', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 'bold' }}>
                {proj.status}
              </span>
            </div>
            <div style={{ padding: '20px' }}>
              <p style={{ color: '#aaa', margin: '0 0 15px 0' }}>{proj.description}</p>
              <div style={{ width: '100%', backgroundColor: '#121212', height: '8px', borderRadius: '4px', marginBottom: '10px' }}>
                <div style={{ width: `${proj.progress}%`, height: '100%', backgroundColor: proj.color || '#52c41a', borderRadius: '4px' }}></div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#888', fontSize: '0.9rem' }}>
                <span>{proj.milestones}</span>
                <span>{proj.progress}% Complete</span>
              </div>
            </div>
          </div>
        ))}
        {projects.length === 0 && (
          <p style={{ color: '#888' }}>No active projects found. Create one to begin.</p>
        )}
      </div>
    </div>
  );
};

export default Projects;
