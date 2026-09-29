import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import MetricsCard from '../components/MetricsCard';
import { 
  ClipboardList, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  ShieldAlert, 
  Repeat, 
  Brain,
  Sparkles,
  ChevronRight,
  Download
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const [audits, setAudits] = useState([]);
  const [findings, setFindings] = useState([]);
  const [recurring, setRecurring] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [aData, fData, rData] = await Promise.all([
        api.getAudits(),
        api.getFindings(),
        api.getRecurringFindings()
      ]);
      setAudits(aData);
      setFindings(fData);
      setRecurring(rData.recurring_issues || []);
    } catch (err) {
      console.error('Failed loading dashboard metrics', err);
    } finally {
      setLoading(false);
    }
  };

  const totalAudits = audits.length;
  const openFindings = findings.filter(f => f.status === 'Open' || f.status === 'In Progress').length;
  const resolvedFindings = findings.filter(f => f.status === 'Resolved').length;
  const overdueRemediations = findings.filter(f => f.status === 'Overdue').length;
  const highRiskFindings = findings.filter(f => f.severity === 'High' || f.severity === 'Critical').length;
  const recurringCount = recurring.length;

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 p-7 rounded-3xl text-white shadow-lg shadow-blue-500/15">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-3 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-white/20 text-white border border-white/30 backdrop-blur-sm">
              Enterprise Compliance
            </span>
            <span className="text-xs text-blue-100 font-mono font-semibold">Memory Bank: auditmind_org</span>
          </div>
          <h2 className="text-2xl font-black tracking-tight text-white">Internal Audit Intelligence Dashboard</h2>
          <p className="text-xs text-blue-100 mt-1 max-w-2xl font-medium">
            Powered by <strong>Hindsight Memory</strong> — persistent organizational recall across historical audit cycles.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <a
            href="/api/reports/docx"
            download="AuditMind_Executive_Compliance_Report.docx"
            className="px-4 py-2.5 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs flex items-center gap-2 border border-white/20 transition-all backdrop-blur-sm"
          >
            <Download className="w-4 h-4 text-blue-200" />
            Export Executive Report (.docx)
          </a>
          <button
            onClick={() => navigate('/ai-assistant')}
            className="px-5 py-2.5 rounded-2xl bg-white text-blue-700 hover:bg-blue-50 font-bold text-xs flex items-center gap-2 shadow-md transition-all border border-blue-100"
          >
            <Brain className="w-4 h-4 text-blue-600" />
            Ask AI Audit Assistant
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricsCard
          title="Total Audits"
          value={totalAudits}
          subtitle="Across 2024-2026"
          icon={ClipboardList}
          color="blue"
        />
        <MetricsCard
          title="Open Findings"
          value={openFindings}
          subtitle="Action required"
          icon={AlertTriangle}
          color="amber"
        />
        <MetricsCard
          title="Resolved"
          value={resolvedFindings}
          subtitle="Verified closed"
          icon={CheckCircle2}
          color="emerald"
        />
        <MetricsCard
          title="Overdue"
          value={overdueRemediations}
          subtitle="Past due date"
          icon={Clock}
          color="rose"
        />
        <MetricsCard
          title="High Risk"
          value={highRiskFindings}
          subtitle="Critical & High"
          icon={ShieldAlert}
          color="rose"
        />
        <MetricsCard
          title="Recurring"
          value={recurringCount}
          subtitle="Hindsight patterns"
          icon={Repeat}
          color="purple"
        />
      </div>

      {/* Recurring Issues Alert Banner */}
      {recurringCount > 0 && (
        <div className="p-6 rounded-3xl bg-amber-50 border border-amber-200/90 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xs">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-2xl bg-amber-100 border border-amber-200 text-amber-700">
              <Sparkles className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-slate-900 text-sm">Hindsight Memory Alert: Recurring Control Failures</h3>
                <span className="text-[10px] bg-amber-200 text-amber-900 font-extrabold px-2.5 py-0.5 rounded-full border border-amber-300">
                  {recurringCount} Pattern Detected
                </span>
              </div>
              <p className="text-xs text-slate-700 mt-1 max-w-3xl font-medium">
                Transaction Approval Control <strong>#FIN-04</strong> has failed in <strong>2024, 2025, and 2026</strong> audits. Previous remediations failed to eliminate emergency authorization overrides.
              </p>
            </div>
          </div>
          <button
            onClick={() => navigate('/findings')}
            className="px-4 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs flex items-center gap-1.5 whitespace-nowrap shadow-md shadow-amber-600/20"
          >
            Review Findings <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Recent Audits & Findings Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Audits */}
        <div className="bg-white border border-slate-200/80 rounded-3xl p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <ClipboardList className="w-4 h-4 text-blue-600" />
              Recent Audits
            </h3>
            <button onClick={() => navigate('/audits')} className="text-xs text-blue-600 hover:text-blue-700 font-bold">
              View All
            </button>
          </div>

          <div className="space-y-3">
            {audits.slice(0, 4).map((audit) => (
              <div key={audit.id} className="p-4 rounded-2xl bg-slate-50/70 border border-slate-200/60 hover:border-blue-200 flex items-center justify-between transition-all">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-blue-700 font-bold">{audit.audit_code}</span>
                    <span className="text-xs text-slate-900 font-bold">{audit.name}</span>
                  </div>
                  <div className="text-[11px] text-slate-500 font-medium mt-0.5">
                    {audit.department} • Auditor: {audit.auditor}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${
                    audit.risk_level === 'High' ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  }`}>
                    {audit.risk_level}
                  </span>
                  <span className="text-[10px] bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded-md font-semibold">
                    {audit.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Findings */}
        <div className="bg-white border border-slate-200/80 rounded-3xl p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              Active Audit Findings
            </h3>
            <button onClick={() => navigate('/findings')} className="text-xs text-blue-600 hover:text-blue-700 font-bold">
              View All
            </button>
          </div>

          <div className="space-y-3">
            {findings.slice(0, 4).map((finding) => (
              <div key={finding.id} className="p-4 rounded-2xl bg-slate-50/70 border border-slate-200/60 hover:border-blue-200 flex items-center justify-between transition-all">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-amber-700 font-bold">{finding.finding_code}</span>
                    <span className="text-xs text-slate-900 font-bold truncate max-w-xs">{finding.title}</span>
                  </div>
                  <div className="text-[11px] text-slate-500 font-medium mt-0.5">
                    Owner: {finding.remediation_owner} • Due: {finding.due_date}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${
                    finding.severity === 'Critical' || finding.severity === 'High' 
                      ? 'bg-rose-50 text-rose-700 border-rose-200' 
                      : 'bg-amber-50 text-amber-700 border-amber-200'
                  }`}>
                    {finding.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
