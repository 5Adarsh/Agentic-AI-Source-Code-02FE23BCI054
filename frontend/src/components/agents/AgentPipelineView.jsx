const AGENTS = [
  { id: 'faculty_profile_agent', name: '1. Faculty Profile', icon: '👤' },
  { id: 'scholar_harvest_agent', name: '2. Scholar Harvest', icon: '🌾' },
  { id: 'scopus_wos_agent', name: '3. Scopus/WoS Verify', icon: '🔍' },
  { id: 'duplicate_detection_agent', name: '4. Duplicate Detect', icon: '⚡' },
  { id: 'citation_analytics_agent', name: '5. Citation Analytics', icon: '📊' },
  { id: 'validation_agent', name: '6. Validation', icon: '🛡️' },
  { id: 'dashboard_agent', name: '7. Dashboard Aggregator', icon: '📋' },
]

export default function AgentPipelineView({ currentAgent = null, completedAgents = [] }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm overflow-x-auto">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-4">
        LangGraph Multi-Agent Orchestration Topology
      </h4>

      <div className="flex items-center min-w-[700px] justify-between">
        {AGENTS.map((agent, index) => {
          const isCurrent = currentAgent === agent.id
          const isCompleted = completedAgents.includes(agent.id)

          return (
            <div key={agent.id} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1 text-center">
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center text-lg transition-all ${
                    isCurrent
                      ? 'bg-indigo-600 text-white ring-4 ring-indigo-100 shadow-md scale-110'
                      : isCompleted
                      ? 'bg-emerald-500 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-400 border border-slate-200'
                  }`}
                >
                  {isCompleted ? '✓' : agent.icon}
                </div>
                <span className="text-xs font-medium text-slate-700 mt-2 line-clamp-1">
                  {agent.name}
                </span>
                <span className="text-[10px] text-slate-400">
                  {isCurrent ? 'Running...' : isCompleted ? 'Passed' : 'Standby'}
                </span>
              </div>

              {index < AGENTS.length - 1 && (
                <div
                  className={`h-0.5 flex-1 mx-2 transition-colors ${
                    isCompleted ? 'bg-emerald-400' : 'bg-slate-200'
                  }`}
                />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
