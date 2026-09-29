import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { BrainCircuit, Database, Search, Sparkles, Network, GitBranch, Layers, Tag, Calendar, AlertCircle } from 'lucide-react';

export default function MemoryExplorer() {
  const [memories, setMemories] = useState([]);
  const [graphData, setGraphData] = useState({ nodes: [], links: [], lineage_chains: [] });
  const [categories, setCategories] = useState({});
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedNode, setSelectedNode] = useState(null);
  const [testQuery, setTestQuery] = useState('');
  const [testResults, setTestResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMemoryData();
  }, []);

  const loadMemoryData = async () => {
    try {
      setLoading(true);
      const [mList, catData, gData] = await Promise.all([
        api.getMemories(),
        api.getMemoryCategories(),
        api.getMemoryGraph()
      ]);
      setMemories(mList);
      setCategories(catData.categories || {});
      setGraphData(gData || { nodes: [], links: [], lineage_chains: [] });
      if (mList.length > 0) {
        setSelectedNode(mList[0]);
      }
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
              Hindsight Engine Active
            </span>
            <span className="text-xs text-blue-100 font-mono font-semibold">Bank ID: auditmind_org</span>
          </div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            <BrainCircuit className="w-6 h-6 text-blue-200" />
            Hindsight Memory & Lineage Graph Explorer
          </h2>
          <p className="text-xs text-blue-100 mt-1 font-medium">
            Inspect persistent long-term memory nodes, category breakdowns, temporal index, and recurring finding lineage chains across 2024–2026.
          </p>
        </div>

        <div className="flex items-center gap-3 bg-white/10 p-3 rounded-2xl border border-white/20 backdrop-blur-md">
          <div className="text-right">
            <div className="text-xs text-blue-200 font-bold uppercase">Memory Nodes</div>
            <div className="text-lg font-black">{memories.length}</div>
          </div>
          <div className="w-px h-8 bg-white/20"></div>
          <div className="text-right">
            <div className="text-xs text-blue-200 font-bold uppercase">Lineage Connections</div>
            <div className="text-lg font-black">{graphData.links?.length || 0}</div>
          </div>
        </div>
      </div>

      {/* Historical Finding Lineage Visualization Card */}
      <div className="bg-white border border-slate-200/80 rounded-3xl p-6 space-y-4 shadow-xs">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-blue-600" />
            Recurring Control Lineage Chains across Audit Cycles
          </h3>
          <span className="text-xs font-mono font-bold text-blue-700 bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
            Lineage Patterns Detected: {graphData.lineage_chains?.length || 1}
          </span>
        </div>
        
        <p className="text-xs text-slate-500 font-medium">
          Hindsight automatically connects identical control failure occurrences across fiscal years (2024 $\rightarrow$ 2025 $\rightarrow$ 2026):
        </p>

        {graphData.lineage_chains && graphData.lineage_chains.length > 0 ? (
          graphData.lineage_chains.map((lc, idx) => (
            <div key={idx} className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-3">
              <div className="text-xs font-bold text-slate-900 flex items-center gap-2">
                <Layers className="w-3.5 h-3.5 text-blue-600" />
                <span>Control Scope: <strong>{lc.control}</strong></span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {lc.chain.map((item, cidx) => (
                  <div key={cidx} className={`p-4 rounded-2xl border shadow-xs space-y-2 relative ${
                    item.year === 2026 ? 'bg-blue-50/80 border-blue-300' : 'bg-white border-slate-200'
                  }`}>
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-mono font-bold text-slate-500">{item.year} FISCAL YEAR</span>
                      <span className="font-mono text-blue-700 font-bold">{item.finding_code}</span>
                    </div>
                    <div className="text-xs font-bold text-slate-900 line-clamp-1">{item.title}</div>
                    <div className="flex items-center justify-between text-[10px]">
                      <span className="font-bold text-rose-700">{item.severity} Severity</span>
                      <span className="text-slate-400 font-mono">Linked</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-2xl bg-slate-50 border border-slate-200/80">
            <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono font-bold text-slate-500">2024 AUDIT</span>
                <span className="font-mono text-blue-700 font-bold">FND-2024-012</span>
              </div>
              <div className="text-xs font-bold text-slate-900">Missing Wire Signoff</div>
              <p className="text-[11px] text-slate-600">Manual approval override without dual authorization.</p>
            </div>
            <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono font-bold text-slate-500">2025 AUDIT</span>
                <span className="font-mono text-purple-700 font-bold">FND-2025-024</span>
              </div>
              <div className="text-xs font-bold text-slate-900">Single Approver Bypass</div>
              <p className="text-[11px] text-slate-600">Emergency bypass utilized repeatedly.</p>
            </div>
            <div className="p-4 rounded-2xl bg-blue-50/80 border border-blue-200 shadow-xs space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono font-bold text-blue-800">2026 AUDIT (CURRENT)</span>
                <span className="font-mono text-blue-700 font-bold">FND-2026-031</span>
              </div>
              <div className="text-xs font-bold text-slate-900">API Approval Sync Lag</div>
              <p className="text-[11px] text-slate-700">ERP approval webhook failure causing unvalidated releases.</p>
            </div>
          </div>
        )}
      </div>

      {/* Memory Sandbox & Inspect Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Recall Sandbox */}
        <div className="lg:col-span-2 bg-white border border-slate-200/80 rounded-3xl p-6 space-y-4 shadow-xs">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-600" />
            Raw Hindsight Memory Hybrid Recall Tester
          </h3>

          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Type a query (e.g. 'transaction approval' or 'high value transfer')..."
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
                Recalled Nodes ({testResults.length})
              </span>
              {testResults.map((r, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-white border border-slate-200 text-xs text-slate-800 font-mono space-y-1">
                  <div className="flex items-center justify-between font-bold text-blue-700">
                    <span>[{r.year || '2026'}] {r.reference_code || `MEM-${r.id}`}</span>
                    <span className="text-[10px] text-slate-500">{r.category}</span>
                  </div>
                  <p className="text-slate-700 font-sans">{r.content}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Col: Node Detail Inspector */}
        <div className="bg-white border border-slate-200/80 rounded-3xl p-6 space-y-4 shadow-xs">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-blue-600" />
            Selected Node Inspector
          </h3>

          {selectedNode ? (
            <div className="space-y-3 text-xs">
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-2xl space-y-1">
                <div className="text-[10px] font-bold uppercase text-blue-900">Reference Code</div>
                <div className="font-mono text-sm font-bold text-blue-700">{selectedNode.reference_code || `MEM-${selectedNode.id}`}</div>
              </div>

              <div className="space-y-1">
                <div className="text-[10px] font-bold uppercase text-slate-500">Category & Year</div>
                <div className="font-semibold text-slate-800">{selectedNode.category} ({selectedNode.year || 2026})</div>
              </div>

              <div className="space-y-1">
                <div className="text-[10px] font-bold uppercase text-slate-500">Content Excerpt</div>
                <div className="p-3 bg-slate-50 rounded-2xl border border-slate-200 text-slate-800 font-mono text-[11px] leading-relaxed">
                  {selectedNode.content}
                </div>
              </div>

              {selectedNode.tags && (
                <div className="space-y-1">
                  <div className="text-[10px] font-bold uppercase text-slate-500">Tags</div>
                  <div className="flex flex-wrap gap-1">
                    {selectedNode.tags.split(',').map((t, idx) => (
                      <span key={idx} className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-mono text-[10px]">
                        #{t.trim()}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-xs text-slate-400 italic py-6 text-center">Select any node below to inspect metadata.</div>
          )}
        </div>
      </div>

      {/* Stored Memories Directory */}
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
            <div 
              key={mem.id} 
              onClick={() => setSelectedNode(mem)}
              className={`p-5 rounded-3xl bg-white border space-y-2 shadow-xs cursor-pointer transition-all ${
                selectedNode && selectedNode.id === mem.id ? 'border-blue-500 ring-2 ring-blue-500/20' : 'border-slate-200/80 hover:border-blue-300'
              }`}
            >
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
