import React, { useState } from 'react';
import { api } from '../services/api';
import { Search as SearchIcon, Brain, ClipboardList, Sparkles } from 'lucide-react';

export default function Search() {
  const [query, setQuery] = useState('');
  const [searchMode, setSearchMode] = useState('hindsight');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      setLoading(true);
      if (searchMode === 'hindsight') {
        const res = await api.recallMemory(query);
        setResults({ type: 'hindsight', data: res.results || [] });
      } else {
        const [audits, findings] = await Promise.all([api.getAudits(), api.getFindings()]);
        const q = query.toLowerCase();
        const matchedAudits = audits.filter(a => a.name.toLowerCase().includes(q) || a.audit_code.toLowerCase().includes(q) || a.department.toLowerCase().includes(q));
        const matchedFindings = findings.filter(f => f.title.toLowerCase().includes(q) || f.finding_code.toLowerCase().includes(q) || f.control_involved.toLowerCase().includes(q));
        setResults({ type: 'structured', audits: matchedAudits, findings: matchedFindings });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <SearchIcon className="w-6 h-6 text-blue-600" />
          Organizational Search & Memory Discovery
        </h2>
        <p className="text-xs text-slate-500 font-medium mt-1">
          Perform dual-mode search across structured database records and <strong>Hindsight AI Memory</strong>.
        </p>
      </div>

      {/* Mode Switcher */}
      <div className="flex gap-3">
        <button
          onClick={() => setSearchMode('hindsight')}
          className={`px-4 py-2.5 rounded-2xl text-xs font-bold flex items-center gap-2 transition-all ${
            searchMode === 'hindsight'
              ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
              : 'bg-white border border-slate-200 text-slate-700'
          }`}
        >
          <Brain className="w-4 h-4" />
          AI Historical Hindsight Memory Search
        </button>

        <button
          onClick={() => setSearchMode('structured')}
          className={`px-4 py-2.5 rounded-2xl text-xs font-bold flex items-center gap-2 transition-all ${
            searchMode === 'structured'
              ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
              : 'bg-white border border-slate-200 text-slate-700'
          }`}
        >
          <ClipboardList className="w-4 h-4" />
          Structured Database Record Search
        </button>
      </div>

      {/* Search Input */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          placeholder={
            searchMode === 'hindsight'
              ? "Search Hindsight memory (e.g. 'Have we had missing transaction approvals in previous audits?')..."
              : "Search by Audit Code, Finding Title, Control ID..."
          }
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 bg-white border border-slate-200/80 rounded-2xl px-4 py-3.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 shadow-xs"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3.5 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center gap-2 shadow-md shadow-blue-600/20"
        >
          <SearchIcon className="w-4 h-4" />
          Search
        </button>
      </form>

      {/* Results Display */}
      {loading && (
        <div className="py-12 flex items-center justify-center gap-3 text-slate-500 font-medium text-xs">
          <Sparkles className="w-6 h-6 text-blue-600 animate-spin" />
          Searching organizational memory...
        </div>
      )}

      {results && (
        <div className="space-y-4">
          {results.type === 'hindsight' ? (
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase text-slate-500 tracking-wider">
                Recalled Hindsight Memories ({results.data.length})
              </h3>
              {results.data.map((mem, idx) => (
                <div key={idx} className="p-4 rounded-2xl bg-white border border-slate-200 space-y-2 shadow-xs">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-mono font-bold text-blue-700">{mem.reference_code}</span>
                    <span className="text-slate-500 font-semibold">Year: {mem.year}</span>
                  </div>
                  <p className="text-xs text-slate-800 font-mono bg-slate-50 p-3.5 rounded-xl border border-slate-200/60">
                    "{mem.content}"
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-6">
              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase text-slate-500">Matched Audits ({results.audits.length})</h3>
                {results.audits.map(a => (
                  <div key={a.id} className="p-3.5 bg-white rounded-2xl border border-slate-200 text-xs text-slate-900 font-medium shadow-xs">
                    <span className="font-mono text-blue-700 font-bold">{a.audit_code}</span> — {a.name} ({a.department})
                  </div>
                ))}
              </div>

              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase text-slate-500">Matched Findings ({results.findings.length})</h3>
                {results.findings.map(f => (
                  <div key={f.id} className="p-3.5 bg-white rounded-2xl border border-slate-200 text-xs text-slate-900 font-medium shadow-xs">
                    <span className="font-mono text-amber-700 font-bold">{f.finding_code}</span> — {f.title} ({f.severity})
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
