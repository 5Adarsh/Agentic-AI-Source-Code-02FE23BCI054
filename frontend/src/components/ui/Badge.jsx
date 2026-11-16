export default function Badge({ status = 'unverified', children }) {
  const styles = {
    verified: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    partially_verified: 'bg-blue-100 text-blue-800 border-blue-200',
    unverified: 'bg-amber-100 text-amber-800 border-amber-200',
    duplicate: 'bg-red-100 text-red-800 border-red-200',
    requires_review: 'bg-purple-100 text-purple-800 border-purple-200',
    pending: 'bg-slate-100 text-slate-800 border-slate-200',
    running: 'bg-indigo-100 text-indigo-800 border-indigo-200 animate-pulse',
    completed: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    failed: 'bg-red-100 text-red-800 border-red-200',
  }

  const normalized = (status || '').toLowerCase().replace(' ', '_')
  const badgeStyle = styles[normalized] || 'bg-slate-100 text-slate-700 border-slate-200'

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize ${badgeStyle}`}
    >
      {children || status.replace('_', ' ')}
    </span>
  )
}
