import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import FindingModal from '../components/FindingModal';
import SimilarFindingsModal from '../components/SimilarFindingsModal';
import { AlertTriangle, Plus, Search, Filter, Brain } from 'lucide-react';

export default function Findings() {
  const [findings, setFindings] = useState([]);
  const [audits, setAudits] = useState([]);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('All');
  
  const [isFindingModalOpen, setIsFindingModalOpen] = useState(false);
  
  // Similar findings modal state
  const [isSimilarModalOpen, setIsSimilarModalOpen] = useState(false);
  const [similarData, setSimilarData] = useState(null);
  const [similarLoading, setSimilarLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [fData, aData] = await Promise.all([
        api.getFindings(),
        api.getAudits()
      ]);
      setFindings(fData);
      setAudits(aData);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateFinding = async (data) => {
    try {
      await api.createFinding(data);
      await loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleFindSimilar = async (findingId) => {
    try {
      setIsSimilarModalOpen(true);
      setSimilarLoading(true);
      const result = await api.findSimilarFindings(findingId);
      setSimilarData(result);
    } catch (err) {
      console.error('Failed fetching similar findings', err);
    } finally {
      setSimilarLoading(false);
    }
  };

  const filteredFindings = findings.filter(f => {
    const matchesSearch = f.title.toLowerCase().includes(search.toLowerCase()) ||
                          f.finding_code.toLowerCase().includes(search.toLowerCase()) ||
                          f.control_involved.toLowerCase().includes(search.toLowerCase());
    const matchesSev = severityFilter === 'All' || f.severity === severityFilter;
    return matchesSearch && matchesSev;
  });

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <AlertTriangle className="w-6 h-6 text-amber-500" />
            Audit Findings Management
          </h2>
          <p className="text-xs text-slate-500 font-medium mt-1">
            Track control exceptions and trigger <strong>Hindsight Memory Recall</strong> to check for past occurrences.
          </p>
        </div>
        <button
          onClick={() => setIsFindingModalOpen(true)}
          className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center gap-2 shadow-md shadow-blue-600/20 transition-all self-start"
        >
          <Plus className="w-4 h-4" />
          Log New Finding
        </button>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col md:flex-row items-center gap-4 bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by code, title, or control involved..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:border-blue-500 focus:bg-white"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-slate-50 border border-slate-200 text-slate-800 text-xs rounded-xl px-3 py-2 font-medium"
          >
            <option value="All">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
      </div>

      {/* Findings List */}
      <div className="space-y-4">
        {filteredFindings.map((finding) => (
          <div
            key={finding.id}
            className="bg-white border border-slate-200/80 hover:border-blue-300 rounded-3xl p-6 transition-all duration-200 space-y-4 shadow-xs"
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-100 pb-3">
              <div className="flex items-center gap-3">
                <span className="font-mono font-bold text-blue-700 text-xs bg-blue-50 px-3 py-1 rounded-xl border border-blue-200">
                  {finding.finding_code}
                </span>
                <h3 className="font-bold text-slate-900 text-base">{finding.title}</h3>
              </div>

              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
                  finding.severity === 'Critical' || finding.severity === 'High'
                    ? 'bg-rose-50 text-rose-700 border-rose-200'
                    : 'bg-amber-50 text-amber-700 border-amber-200'
                }`}>
                  {finding.severity} Severity
                </span>
                <span className="px-3 py-1 rounded-xl bg-slate-100 text-slate-700 text-xs border border-slate-200 font-bold">
                  {finding.status}
                </span>
              </div>
            </div>

            {/* Finding Body */}
            <p className="text-xs text-slate-700 font-medium leading-relaxed">{finding.description}</p>

            {/* Details Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs bg-slate-50/80 p-3.5 rounded-2xl border border-slate-200/60">
              <div>
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Control Involved</span>
                <span className="text-blue-900 font-bold">{finding.control_involved}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Root Cause</span>
                <span className="text-slate-800 font-medium">{finding.root_cause}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Remediation Owner</span>
                <span className="text-slate-800 font-medium">{finding.remediation_owner} (Due: {finding.due_date})</span>
              </div>
            </div>

            {/* Hindsight Action Button */}
            <div className="flex items-center justify-between pt-2">
              <div className="text-[11px] text-slate-500 font-medium">
                Created: {finding.created_date} • Audit: <span className="text-slate-900 font-bold">{finding.audit_name || 'Finance Audit'}</span>
              </div>

              <button
                onClick={() => handleFindSimilar(finding.id)}
                className="px-4 py-2.5 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center gap-2 shadow-md shadow-blue-600/20 transition-all border border-blue-500"
              >
                <Brain className="w-4 h-4 text-blue-100 animate-pulse" />
                Find Similar Historical Findings (Hindsight)
              </button>
            </div>
          </div>
        ))}
      </div>

      <FindingModal
        isOpen={isFindingModalOpen}
        onClose={() => setIsFindingModalOpen(false)}
        onSubmit={handleCreateFinding}
        audits={audits}
      />

      <SimilarFindingsModal
        isOpen={isSimilarModalOpen}
        onClose={() => setIsSimilarModalOpen(false)}
        data={similarData}
        loading={similarLoading}
      />
    </div>
  );
}
