import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  ClipboardList, 
  AlertTriangle, 
  CheckSquare, 
  Bot, 
  FileText, 
  BrainCircuit, 
  Search as SearchIcon, 
  Settings,
  ShieldCheck
} from 'lucide-react';

export default function Sidebar() {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Audits', path: '/audits', icon: ClipboardList },
    { name: 'Findings', path: '/findings', icon: AlertTriangle },
    { name: 'Remediation', path: '/remediation', icon: CheckSquare },
    { name: 'AI Assistant', path: '/ai-assistant', icon: Bot, badge: 'Hindsight' },
    { name: 'Documents', path: '/documents', icon: FileText },
    { name: 'Memory Explorer', path: '/memory-explorer', icon: BrainCircuit, badge: 'Memory' },
    { name: 'Search', path: '/search', icon: SearchIcon },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200/80 flex flex-col justify-between h-screen sticky top-0 shadow-sm z-30">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-100 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-blue-500 to-sky-400 flex items-center justify-center shadow-md shadow-blue-500/20">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-extrabold text-xl tracking-tight text-slate-900 flex items-center gap-1.5">
              AuditMind
            </h1>
            <p className="text-[10px] uppercase font-bold text-blue-600 tracking-wider">AI Audit & Compliance</p>
          </div>
        </div>

        {/* Hindsight Memory Engine Status */}
        <div className="mx-4 my-4 p-3 rounded-xl bg-blue-50/80 border border-blue-100 flex items-center gap-3">
          <div className="w-2.5 h-2.5 rounded-full bg-blue-600 animate-pulse" />
          <div className="text-xs">
            <div className="text-blue-900 font-bold">Hindsight Memory Layer</div>
            <div className="text-blue-600 text-[11px] font-medium">Vectorize Active • Synced</div>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="px-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.name}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/25'
                      : 'text-slate-600 hover:text-blue-700 hover:bg-blue-50/60'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-blue-100 text-blue-700 border border-blue-200">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Profile */}
      <div className="p-4 border-t border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center font-bold text-xs text-white shadow-sm">
            LA
          </div>
          <div>
            <div className="text-xs font-bold text-slate-800">Lead Auditor</div>
            <div className="text-[10px] text-slate-500">auditor@auditmind.io</div>
          </div>
        </div>
        <button className="text-slate-400 hover:text-blue-600 p-1.5 rounded-lg hover:bg-blue-50">
          <Settings className="w-4 h-4" />
        </button>
      </div>
    </aside>
  );
}
