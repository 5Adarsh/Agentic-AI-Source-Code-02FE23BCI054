export default function AgentLogViewer({ logs = [] }) {
  if (!logs || logs.length === 0) {
    return (
      <div className="bg-slate-900 text-slate-400 p-6 rounded-xl font-mono text-xs text-center border border-slate-800">
        No execution logs recorded yet. Run an agent or pipeline to view dynamic output.
      </div>
    )
  }

  const levelStyles = {
    info: 'text-blue-400',
    warning: 'text-amber-400',
    error: 'text-red-400',
    debug: 'text-slate-400',
    critical: 'text-red-500 font-bold',
  }

  return (
    <div className="bg-slate-900 rounded-xl p-4 font-mono text-xs max-h-72 overflow-y-auto border border-slate-800 space-y-1.5 shadow-inner">
      {logs.map((log, idx) => (
        <div key={idx} className="flex items-start gap-2 text-slate-300">
          <span className="text-slate-500 shrink-0">
            {log.logged_at ? new Date(log.logged_at).toLocaleTimeString() : `[step-${idx}]`}
          </span>
          <span className={`uppercase text-[10px] font-semibold px-1 rounded bg-slate-800 shrink-0 ${levelStyles[log.level] || 'text-slate-300'}`}>
            {log.level || 'INFO'}
          </span>
          <span className="break-all">{log.message}</span>
        </div>
      ))}
    </div>
  )
}
