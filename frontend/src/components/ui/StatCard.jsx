export default function StatCard({ label, value, icon, change, description }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</p>
        {icon && <span className="text-xl">{icon}</span>}
      </div>
      <p className="text-2xl font-bold text-slate-900 mt-2">
        {value !== undefined && value !== null ? value : '—'}
      </p>
      {(change || description) && (
        <p className="text-xs text-slate-400 mt-1">
          {change && <span className="text-emerald-600 font-medium mr-1">{change}</span>}
          {description}
        </p>
      )}
    </div>
  )
}
