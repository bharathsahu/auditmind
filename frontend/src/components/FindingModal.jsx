import React, { useState } from 'react';
import { X, AlertOctagon } from 'lucide-react';

export default function FindingModal({ isOpen, onClose, onSubmit, audits = [] }) {
  const [formData, setFormData] = useState({
    audit_id: audits[0]?.id || 1,
    title: '',
    description: '',
    severity: 'High',
    control_involved: 'Transaction Approval Control #FIN-04',
    root_cause: '',
    business_impact: '',
    recommendation: '',
    management_response: '',
    remediation_owner: 'Finance Controls Team',
    due_date: new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0],
    status: 'Open',
    evidence: '',
    created_date: new Date().toISOString().split('T')[0]
  });

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ ...formData, audit_id: Number(formData.audit_id) });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-white border border-slate-200 rounded-3xl w-full max-w-2xl p-6 shadow-2xl space-y-4 my-8">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 className="font-bold text-lg text-slate-900 flex items-center gap-2">
            <AlertOctagon className="w-5 h-5 text-amber-500" />
            Log New Audit Finding
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 p-1 rounded-lg hover:bg-slate-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 text-xs">
          <div>
            <label className="block text-slate-700 font-semibold mb-1">Associated Audit *</label>
            <select
              value={formData.audit_id}
              onChange={(e) => setFormData({ ...formData, audit_id: e.target.value })}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900"
            >
              {audits.map((a) => (
                <option key={a.id} value={a.id}>
                  [{a.audit_code}] {a.name} ({a.department})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-700 font-semibold mb-1">Finding Title *</label>
            <input
              type="text"
              required
              placeholder="e.g. Incomplete approval documentation for wire transfer"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:border-blue-500 focus:bg-white"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-700 font-semibold mb-1">Severity</label>
              <select
                value={formData.severity}
                onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900"
              >
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1">Control Involved</label>
              <input
                type="text"
                value={formData.control_involved}
                onChange={(e) => setFormData({ ...formData, control_involved: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-700 font-semibold mb-1">Detailed Finding Description</label>
            <textarea
              rows={2}
              required
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-700 font-semibold mb-1">Root Cause</label>
              <input
                type="text"
                placeholder="e.g. API sync latency or policy override"
                value={formData.root_cause}
                onChange={(e) => setFormData({ ...formData, root_cause: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900"
              />
            </div>
            <div>
              <label className="block text-slate-700 font-semibold mb-1">Business Impact</label>
              <input
                type="text"
                placeholder="e.g. Compliance risk exposure"
                value={formData.business_impact}
                onChange={(e) => setFormData({ ...formData, business_impact: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-700 font-semibold mb-1">Remediation Owner</label>
              <input
                type="text"
                value={formData.remediation_owner}
                onChange={(e) => setFormData({ ...formData, remediation_owner: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900"
              />
            </div>
            <div>
              <label className="block text-slate-700 font-semibold mb-1">Target Due Date</label>
              <input
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-700 font-semibold mb-1">Auditor Recommendation</label>
            <input
              type="text"
              placeholder="e.g. Enforce hard-stop verification"
              value={formData.recommendation}
              onChange={(e) => setFormData({ ...formData, recommendation: e.target.value })}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold shadow-md shadow-blue-600/20"
            >
              Save & Retain in Hindsight
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
