import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { BrainCircuit, Database, Search, Sparkles, Network } from 'lucide-react';

export default function MemoryExplorer() {
  const [memories, setMemories] = useState([]);
  const [categories, setCategories] = useState({});
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [testQuery, setTestQuery] = useState('');
  const [testResults, setTestResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMemoryData();
  }, []);

  const loadMemoryData = async () => {
    try {
      setLoading(true);
      const [mList, catData] = await Promise.all([
        api.getMemories(),
        api.getMemoryCategories()
      ]);
      setMemories(mList);
      setCategories(catData.categories || {});
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunRecall = async () => {
    if (!testQuery.trim()) return;
    try {
      const res = await api.recallMemory(testQuery);
      setTestResults(res.results || []);
    } catch (err) {
      console.error(err);
    }
  };

  const filteredMemories = memories.filter(
    m => selectedCategory === 'All' || m.category === selectedCategory
  );

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 p-7 rounded-3xl text-white shadow-lg shadow-blue-500/15 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-3 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-white/20 text-white border border-white/30 backdrop-blur-sm">
              Hindsight Engine Demo
            </span>
            <span className="text-xs text-blue-100 font-mono font-semibold">Bank ID: auditmind_org</span>
          </div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            <BrainCircuit className="w-6 h-6 text-blue-200" />
            Hindsight Memory Explorer
          </h2>
          <p className="text-xs text-blue-100 mt-1 font-medium">
            Inspect persistent long-term memory nodes, categorization, temporal index, and historical finding relationships.
          </p>
        </div>
      </div>

      {/* Historical Finding Lineage Visualization Card */}
      <div className="bg-white border border-slate-200/80 rounded-3xl p-6 space-y-4 shadow-xs">
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <Network className="w-4 h-4 text-blue-600" />
          Recurring Control Lineage Graph (Hindsight Temporal Chain)
        </h3>
        <p className="text-xs text-slate-500 font-medium">
          Visualizes how Hindsight connects finding occurrences across consecutive audit years:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
          {/* Node 2024 */}
          <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-mono font-bold text-slate-500">2024 AUDIT</span>
              <span className="font-mono text-blue-700 font-bold">AUD-2024-012</span>
            </div>
            <div className="text-xs font-bold text-slate-900">Finding #FND-2024-012</div>
            <p className="text-[11px] text-slate-600 font-medium">Missing transaction approval for high-value wire transfer.</p>
            <div className="text-[10px] text-emerald-700 font-mono font-bold">Outcome: Dual Signoff Rule</div>
          </div>

          {/* Node 2025 */}
          <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-mono font-bold text-slate-500">2025 AUDIT</span>
              <span className="font-mono text-purple-700 font-bold">AUD-2025-024</span>
            </div>
            <div className="text-xs font-bold text-slate-900">Finding #FND-2025-024</div>
            <p className="text-[11px] text-slate-600 font-medium">Incomplete approval for high-value transaction transfers.</p>
            <div className="text-[10px] text-amber-700 font-mono font-bold">Recurrence: Emergency Bypass</div>
          </div>

          {/* Node 2026 */}
          <div className="p-4 rounded-2xl bg-blue-50/80 border border-blue-200 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-mono font-bold text-blue-800">2026 AUDIT (CURRENT)</span>
              <span className="font-mono text-blue-700 font-bold">AUD-2026-031</span>
            </div>
            <div className="text-xs font-bold text-slate-900">Finding #FND-2026-031</div>
            <p className="text-[11px] text-slate-700 font-medium">Incomplete approval documentation for high-value transaction.</p>
            <div className="text-[10px] text-rose-700 font-mono font-bold">Active: ERP API Sync Lag</div>
          </div>
        </div>
      </div>

      {/* Memory Sandbox Testing Box */}
      <div className="bg-white border border-slate-200/80 rounded-3xl p-6 space-y-4 shadow-xs">
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-blue-600" />
          Raw Hindsight Memory Recall Tester
        </h3>

        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Type a test query (e.g. 'transaction approval' or 'high value transfer')..."
            value={testQuery}
            onChange={(e) => setTestQuery(e.target.value)}
            className="flex-1 bg-slate-50 border border-slate-200 rounded-2xl px-4 py-2.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white"
          />
          <button
            onClick={handleRunRecall}
            className="px-5 py-2.5 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center gap-2 shadow-md shadow-blue-600/20"
          >
            <Search className="w-3.5 h-3.5" />
            Test Recall
          </button>
        </div>

        {testResults && (
          <div className="p-4 rounded-2xl bg-blue-50/70 border border-blue-200 space-y-2">
            <span className="text-[10px] font-bold uppercase text-blue-900 tracking-wider">
              Recalled Memory Nodes ({testResults.length})
            </span>
            {testResults.map((r, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-white border border-slate-200 text-xs text-slate-800 font-mono">
                [{r.year}] <strong>{r.reference_code}</strong> ({r.category}): {r.content}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Category Pills & Memories List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-600" />
            Stored Hindsight Memory Nodes ({filteredMemories.length})
          </h3>

          <div className="flex gap-2">
            <button
              onClick={() => setSelectedCategory('All')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold ${
                selectedCategory === 'All' ? 'bg-blue-600 text-white shadow-xs' : 'bg-white text-slate-600 border border-slate-200'
              }`}
            >
              All
            </button>
            {Object.keys(categories).map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-bold ${
                  selectedCategory === cat ? 'bg-blue-600 text-white shadow-xs' : 'bg-white text-slate-600 border border-slate-200'
                }`}
              >
                {cat} ({categories[cat]})
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredMemories.map((mem) => (
            <div key={mem.id} className="p-5 rounded-3xl bg-white border border-slate-200/80 space-y-2 shadow-xs hover:border-blue-200 transition-all">
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono font-bold text-blue-700">{mem.reference_code || `MEM-${mem.id}`}</span>
                <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200">
                  {mem.category}
                </span>
              </div>
              <p className="text-xs text-slate-800 font-mono leading-relaxed bg-slate-50 p-3.5 rounded-2xl border border-slate-200/60">
                "{mem.content}"
              </p>
              <div className="flex items-center justify-between text-[11px] text-slate-500 font-semibold">
                <span>Year: {mem.year}</span>
                <span>Bank: {mem.bank_id}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
