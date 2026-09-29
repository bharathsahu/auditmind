import React from 'react';
import { Bell, Search, Database } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Navbar() {
  const navigate = useNavigate();

  return (
    <header className="h-16 border-b border-slate-200/80 bg-white/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20 shadow-xs">
      <div className="flex items-center gap-4 flex-1">
        <div className="relative w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search audits, findings, controls, or Hindsight memory..."
            onClick={() => navigate('/search')}
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-500/10 transition-all"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Memory status pill */}
        <div className="px-3 py-1 rounded-full bg-blue-50 border border-blue-200/80 flex items-center gap-2 text-xs text-blue-900 font-medium">
          <Database className="w-3.5 h-3.5 text-blue-600" />
          <span>Bank: <strong className="text-blue-700 font-mono">auditmind_org</strong></span>
        </div>

        <button className="relative p-2 rounded-xl text-slate-500 hover:text-blue-600 hover:bg-blue-50 transition-colors">
          <Bell className="w-4 h-4" />
          <span className="w-2 h-2 rounded-full bg-blue-600 absolute top-2 right-2" />
        </button>

        <div className="h-4 w-[1px] bg-slate-200" />

        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
          <span className="text-xs text-slate-600 font-semibold">Internal Audit Operations</span>
        </div>
      </div>
    </header>
  );
}
