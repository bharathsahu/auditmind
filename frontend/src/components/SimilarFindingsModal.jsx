import React from 'react';
import { X, Brain, History, ShieldAlert, Sparkles } from 'lucide-react';

export default function SimilarFindingsModal({ isOpen, onClose, data, loading }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
      <div className="bg-white border border-slate-200 rounded-3xl w-full max-w-3xl p-6 shadow-2xl space-y-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-blue-50 border border-blue-100 text-blue-600">
              <Brain className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-slate-900 flex items-center gap-2">
                Hindsight Memory Recall & Reflection
              </h3>
              <p className="text-xs text-slate-500 font-medium">
                Finding Context: <strong className="text-blue-700 font-mono">{data?.finding_code}</strong> • {data?.title}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 p-1 rounded-lg hover:bg-slate-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-1">
          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center gap-3 text-slate-500">
              <Sparkles className="w-8 h-8 text-blue-600 animate-spin" />
              <p className="text-xs font-semibold">Searching persistent Hindsight memory bank...</p>
            </div>
          ) : (
            <>
              {/* Explanation Box */}
              <div className="p-4 rounded-2xl bg-blue-50/70 border border-blue-200/80 text-xs text-blue-950 space-y-2">
                <div className="font-bold flex items-center gap-1.5 text-blue-900">
                  <ShieldAlert className="w-4 h-4 text-amber-500" />
                  Hindsight Analysis & Historical Explanation
                </div>
                <p className="whitespace-pre-line text-slate-700 font-medium leading-relaxed">{data?.relevance_explanation}</p>
              </div>

              {/* Similar Memories List */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider flex items-center gap-2">
                  <History className="w-4 h-4 text-blue-600" />
                  Recalled Historical Memory Nodes ({data?.similar_memories?.length || 0})
                </h4>

                {data?.similar_memories?.length === 0 ? (
                  <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-2xl border border-slate-200">
                    No matching historical audit findings found in Hindsight memory.
                  </div>
                ) : (
                  data?.similar_memories?.map((mem, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-blue-300 transition-all space-y-2"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-blue-700 bg-blue-100/80 px-2.5 py-0.5 rounded-lg border border-blue-200">
                            {mem.reference_code || `MEM-${mem.id}`}
                          </span>
                          <span className="text-slate-600 font-semibold">Year: {mem.year || 'N/A'}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded-md bg-purple-50 text-purple-700 font-bold border border-purple-200">
                            {mem.category}
                          </span>
                        </div>
                        <span className="text-[11px] text-emerald-700 font-mono font-bold">
                          Relevance Score: {mem.relevance_score || 'High'}
                        </span>
                      </div>

                      <p className="text-xs text-slate-800 leading-relaxed bg-white p-3 rounded-xl border border-slate-200/80 font-mono">
                        "{mem.content}"
                      </p>

                      {mem.tags && mem.tags.length > 0 && (
                        <div className="flex items-center gap-1.5 pt-1">
                          {mem.tags.map((tag, tid) => (
                            <span key={tid} className="text-[10px] text-slate-600 bg-white px-2 py-0.5 rounded-md border border-slate-200">
                              #{tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-slate-100 pt-3 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-xs font-bold text-slate-700"
          >
            Close Recall Window
          </button>
        </div>
      </div>
    </div>
  );
}
