import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  LayoutDashboard,
  MessageSquare,
  FolderGit2,
  Brain,
  Settings as SettingsIcon,
  Key,
} from 'lucide-react';

import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Projects from './pages/Projects';
import Memory from './pages/Memory';
import Settings from './pages/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 2,
    },
  },
});

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/chat', icon: MessageSquare, label: 'Chat' },
  { to: '/projects', icon: FolderGit2, label: 'Projects' },
  { to: '/memory', icon: Brain, label: 'Memory' },
  { to: '/settings', icon: SettingsIcon, label: 'Settings' },
  { to: '/config-setup.html', icon: Key, label: 'API Config', external: true },
];

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="flex h-screen bg-gray-950 text-white">
          {/* ─── Sidebar ──────────────────────────────── */}
          <nav className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
            <div className="p-6 border-b border-gray-800">
              <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
                ULTRON v3
              </h1>
              <p className="text-xs text-gray-500 mt-1">Autonomous AI Agent</p>
            </div>

            <div className="flex-1 py-4">
              {navItems.map(({ to, icon: Icon, label, external }: any) => {
                const className = ({ isActive }: any) =>
                  `flex items-center gap-3 px-6 py-3 text-sm transition-colors ${
                    isActive
                      ? 'text-cyan-400 bg-cyan-400/10 border-r-2 border-cyan-400'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800'
                  }`;

                if (external) {
                  return (
                    <a
                      key={to}
                      href={to}
                      className="flex items-center gap-3 px-6 py-3 text-sm transition-colors text-gray-400 hover:text-white hover:bg-gray-800"
                    >
                      <Icon size={18} />
                      {label}
                    </a>
                  );
                }

                return (
                  <NavLink key={to} to={to} className={className}>
                    <Icon size={18} />
                    {label}
                  </NavLink>
                );
              })}
            </div>

            <div className="p-4 border-t border-gray-800 text-xs text-gray-600">
              v3.1.0 • $0/month
            </div>
          </nav>

          {/* ─── Main Content ─────────────────────────── */}
          <main className="flex-1 overflow-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/projects" element={<Projects />} />
              <Route path="/memory" element={<Memory />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
