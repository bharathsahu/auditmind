import React from 'react';

export default function MetricsCard({ title, value, subtitle, icon: Icon, color = 'blue', trend }) {
  const colorMap = {
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    rose: 'bg-rose-50 text-rose-600 border-rose-100',
    amber: 'bg-amber-50 text-amber-600 border-amber-100',
    emerald: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    purple: 'bg-purple-50 text-purple-600 border-purple-100',
  };

  return (
    <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs hover:shadow-md hover:border-blue-200 transition-all duration-200">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-bold text-slate-500 tracking-wider uppercase">{title}</span>
        {Icon && (
          <div className={`p-2.5 rounded-xl border ${colorMap[color] || colorMap.blue}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-extrabold text-slate-900 tracking-tight">{value}</span>
        {trend && (
          <span className={`text-xs font-semibold ${trend.startsWith('+') ? 'text-amber-600' : 'text-emerald-600'}`}>
            {trend}
          </span>
        )}
      </div>
      {subtitle && <p className="text-xs text-slate-500 font-medium mt-1">{subtitle}</p>}
    </div>
  );
}
