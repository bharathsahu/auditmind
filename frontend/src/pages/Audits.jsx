import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import AuditModal from '../components/AuditModal';
import { ClipboardList, Plus, Search, Filter, UserCheck } from 'lucide-react';

export default function Audits() {
  const [audits, setAudits] = useState([]);
  const [search, setSearch] = useState('');
  const [filterDept, setFilterDept] = useState('All');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAudits();
  }, []);

  const loadAudits = async () => {
    try {
      setLoading(true);
      const data = await api.getAudits();
      setAudits(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAudit = async (newAudit) => {
    try {
      await api.createAudit(newAudit);
      await loadAudits();
    } catch (err) {
      console.error(err);
    }
  };

  const filteredAudits = audits.filter(a => {
    const matchesSearch = a.name.toLowerCase().includes(search.toLowerCase()) ||
                          a.audit_code.toLowerCase().includes(search.toLowerCase()) ||
                          a.department.toLowerCase().includes(search.toLowerCase());
    const matchesDept = filterDept === 'All' || a.department === filterDept;
    return matchesSearch && matchesDept;
  });

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <ClipboardList className="w-6 h-6 text-blue-600" />
            Audit Management
          </h2>
          <p className="text-xs text-slate-500 font-medium mt-1">
            Create, manage, and inspect historical internal audit scopes and execution statuses.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center gap-2 shadow-md shadow-blue-600/20 transition-all self-start"
        >
          <Plus className="w-4 h-4" />
          Create New Audit Scope
        </button>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col md:flex-row items-center gap-4 bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by audit code, name, or department..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:border-blue-500 focus:bg-white"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={filterDept}
            onChange={(e) => setFilterDept(e.target.value)}
            className="bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded-xl px-3 py-2 font-medium"
          >
            <option value="All">All Departments</option>
            <option value="Finance Controls">Finance Controls</option>
            <option value="Global Markets">Global Markets</option>
            <option value="IT Risk & Security">IT Risk & Security</option>
            <option value="Compliance & Ethics">Compliance & Ethics</option>
          </select>
        </div>
      </div>

      {/* Audits Table */}
      <div className="bg-white border border-slate-200/80 rounded-3xl overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase font-bold text-[10px] tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-6 py-4">Audit ID</th>
                <th className="px-6 py-4">Audit Name</th>
                <th className="px-6 py-4">Department</th>
                <th className="px-6 py-4">Type</th>
                <th className="px-6 py-4">Risk Level</th>
                <th className="px-6 py-4">Auditor</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Dates</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700 font-medium">
              {filteredAudits.map((a) => (
                <tr key={a.id} className="hover:bg-blue-50/40 transition-colors">
                  <td className="px-6 py-4 font-mono font-bold text-blue-700">{a.audit_code}</td>
                  <td className="px-6 py-4 font-bold text-slate-900">
                    {a.name}
                    <div className="text-[11px] text-slate-500 font-normal line-clamp-1 mt-0.5">{a.description}</div>
                  </td>
                  <td className="px-6 py-4">{a.department}</td>
                  <td className="px-6 py-4 text-slate-600">{a.audit_type}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold border ${
                      a.risk_level === 'High' 
                        ? 'bg-rose-50 text-rose-700 border-rose-200' 
                        : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                    }`}>
                      {a.risk_level} Risk
                    </span>
                  </td>
                  <td className="px-6 py-4 flex items-center gap-1.5 text-slate-700 font-semibold">
                    <UserCheck className="w-3.5 h-3.5 text-blue-600" />
                    {a.auditor}
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-800 border border-slate-200 text-[11px] font-bold">
                      {a.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-500 font-mono text-[11px] whitespace-nowrap">
                    {a.start_date} → {a.end_date}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <AuditModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateAudit}
      />
    </div>
  );
}
