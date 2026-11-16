import Badge from '../ui/Badge'
import Button from '../ui/Button'

export default function AgentStatusCard({
  name,
  displayName,
  description,
  status = 'pending',
  lastRun = null,
  onTrigger,
  isTriggering = false,
}) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:border-slate-300 transition-all flex flex-col justify-between">
      <div>
        <div className="flex items-start justify-between">
          <div>
            <h4 className="font-semibold text-slate-800 text-sm">{displayName}</h4>
            <p className="text-xs text-slate-400 font-mono mt-0.5">{name}</p>
          </div>
          <Badge status={status} />
        </div>
        <p className="text-xs text-slate-600 mt-3 line-clamp-2">{description}</p>
      </div>

      <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span>{lastRun ? `Last: ${new Date(lastRun).toLocaleTimeString()}` : 'Not run yet'}</span>
        <Button
          size="sm"
          variant="secondary"
          isLoading={isTriggering}
          onClick={() => onTrigger(name)}
        >
          Run Worklet
        </Button>
      </div>
    </div>
  )
}
