export default function Alert({ type = 'info', message, title, onClose }) {
  const styles = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    warning: 'bg-amber-50 border-amber-200 text-amber-800',
    error: 'bg-red-50 border-red-200 text-red-800',
  }

  const icons = {
    info: 'ℹ️',
    success: '✅',
    warning: '⚠️',
    error: '❌',
  }

  return (
    <div className={`p-4 rounded-lg border flex items-start justify-between ${styles[type]}`}>
      <div className="flex gap-3">
        <span className="text-base">{icons[type]}</span>
        <div>
          {title && <h4 className="font-semibold text-sm">{title}</h4>}
          <p className="text-xs mt-0.5">{message}</p>
        </div>
      </div>
      {onClose && (
        <button onClick={onClose} className="text-xs font-bold opacity-60 hover:opacity-100">
          ✕
        </button>
      )}
    </div>
  )
}
