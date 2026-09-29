import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { CheckSquare, User } from 'lucide-react';

export default function Remediation() {
  const [remediations, setRemediations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRemediations();
  }, []);

  const loadRemediations = async () => {
    try {
      setLoading(true);
      const data = await api.getRemediations();
      setRemediations(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (id, newStatus) => {
    try {
      await api.updateRemediationStatus(id, newStatus, 'Status updated by lead auditor', 'Updated verification record');
      await loadRemediations();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div>
        <h2 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <CheckSquare className="w-6 h-6 text-emerald-600" />
          Remediation Action Tracking
        </h2>
        <p className="text-xs text-slate-500 font-medium mt-1">
          Monitor corrective actions, completion evidence, and resolved audit findings across teams.
        </p>
      </div>

      <div className="bg-white border border-slate-200/80 rounded-3xl overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase font-bold text-[10px] tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-6 py-4">Remediation Action</th>
                <th className="px-6 py-4">Owner</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Due Date</th>
                <th className="px-6 py-4">Completion Date</th>
                <th className="px-6 py-4">Evidence & Comments</th>
                <th className="px-6 py-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700 font-medium">
              {remediations.map((r) => (
                <tr key={r.id} className="hover:bg-blue-50/40 transition-colors">
                  <td className="px-6 py-4 font-bold text-slate-900 max-w-xs">
                    {r.action}
                  </td>
                  <td className="px-6 py-4 flex items-center gap-1.5 font-bold text-slate-800">
                    <User className="w-3.5 h-3.5 text-blue-600" />
                    {r.owner}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold border ${
                      r.status === 'Resolved'
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                        : r.status === 'Overdue'
                        ? 'bg-rose-50 text-rose-700 border-rose-200'
                        : 'bg-amber-50 text-amber-700 border-amber-200'
                    }`}>
                      {r.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-[11px] text-slate-500">{r.due_date}</td>
                  <td className="px-6 py-4 font-mono text-[11px] text-slate-500">
                    {r.completion_date || '—'}
                  </td>
                  <td className="px-6 py-4 max-w-xs text-slate-600 text-[11px]">
                    <div className="truncate font-mono">{r.evidence || 'No evidence uploaded'}</div>
                    <div className="text-[10px] text-slate-400 italic mt-0.5">{r.comments}</div>
                  </td>
                  <td className="px-6 py-4">
                    {r.status !== 'Resolved' && (
                      <button
                        onClick={() => handleStatusChange(r.id, 'Resolved')}
                        className="px-3.5 py-1.5 rounded-xl bg-emerald-50 hover:bg-emerald-600 text-emerald-700 hover:text-white border border-emerald-200 text-[11px] font-bold transition-all shadow-xs"
                      >
                        Mark Resolved
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
