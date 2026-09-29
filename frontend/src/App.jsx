import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Audits from './pages/Audits';
import Findings from './pages/Findings';
import Remediation from './pages/Remediation';
import AIAssistant from './pages/AIAssistant';
import Documents from './pages/Documents';
import MemoryExplorer from './pages/MemoryExplorer';
import Search from './pages/Search';
import Login from './pages/Login';

export default function App() {
  const [user, setUser] = useState({
    id: 1,
    username: 'auditor',
    full_name: 'Lead Internal Auditor',
    role: 'Lead Auditor'
  });

  if (!user) {
    return <Login onLoginSuccess={(u) => setUser(u)} />;
  }

  return (
    <Router>
      <div className="flex min-h-screen bg-slate-950 text-slate-100">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <Navbar />
          <main className="flex-1 overflow-y-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/audits" element={<Audits />} />
              <Route path="/findings" element={<Findings />} />
              <Route path="/remediation" element={<Remediation />} />
              <Route path="/ai-assistant" element={<AIAssistant />} />
              <Route path="/documents" element={<Documents />} />
              <Route path="/memory-explorer" element={<MemoryExplorer />} />
              <Route path="/search" element={<Search />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}
