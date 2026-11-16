export default function EmptyState({
  title = 'No data available',
  description = 'No records have been imported or harvested yet.',
  action = null,
  icon = '📭',
}) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-white rounded-xl border border-dashed border-slate-300">
      <span className="text-4xl mb-3">{icon}</span>
      <h3 className="text-lg font-semibold text-slate-800">{title}</h3>
      <p className="text-sm text-slate-500 max-w-sm mt-1 mb-5">{description}</p>
      {action && <div>{action}</div>}
    </div>
  )
}
