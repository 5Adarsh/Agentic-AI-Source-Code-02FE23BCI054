import { useState, useEffect } from 'react'
import { agentApi } from '../../api/agents'
import Card from '../../components/ui/Card'
import Button from '../../components/ui/Button'
import Alert from '../../components/ui/Alert'
import Spinner from '../../components/ui/Spinner'
import AgentPipelineView from '../../components/agents/AgentPipelineView'
import AgentLogViewer from '../../components/agents/AgentLogViewer'

const SEVEN_AGENTS = [
  {
    id: 'faculty_profile_agent',
    name: '1. Faculty Profile Agent',
    icon: '👤',
    responsibility:
      'Registers and identifies faculty, maintains ORCID and Google Scholar identifiers, resolves faculty identity across sources, and detects homonym/identity conflicts.',
  },
  {
    id: 'scholar_harvest_agent',
    name: '2. Google Scholar Harvest Agent',
    icon: '🌾',
    responsibility:
      'Harvests publication records from scholar CSV uploads and supported integrations, extracts citations, DOIs, URLs, and normalizes metadata.',
  },
  {
    id: 'scopus_wos_agent',
    name: '3. Scopus / WoS Verification Agent',
    icon: '🔍',
    responsibility:
      'Integrates official Scopus and Web of Science APIs to verify DOI, title, author, and year match; stores tamper-proof evidence chains; enables manual verification workflows.',
  },
  {
    id: 'duplicate_detection_agent',
    name: '4. Duplicate Detection Agent',
    icon: '⚡',
    responsibility:
      'Performs exact DOI matching, fuzzy title distance, author similarity, and year comparison; generates candidate pairs with confidence scores; requires human sign-off.',
  },
  {
    id: 'citation_analytics_agent',
    name: '5. Citation Analytics Agent',
    icon: '📊',
    responsibility:
      'Deterministically calculates total publications, total citations, h-index, i10-index, yearly growth trajectories, and faculty-wise research comparisons.',
  },
  {
    id: 'validation_agent',
    name: '6. Validation Agent',
    icon: '🛡️',
    responsibility:
      'Validates DOI regex syntax, cross-checks publication titles, author completeness, publication year bounds, and assigns quality audit statuses.',
  },
  {
    id: 'dashboard_agent',
    name: '7. Dashboard Agent',
    icon: '📋',
    responsibility:
      'Aggregates institution-wide and department-level summaries, computes compliance metrics, and formats standardized NIRF and NAAC accreditation tables.',
  },
]

export default function AgentsPage() {
  const [executions, setExecutions] = useState([])
  const [selectedExecution, setSelectedExecution] = useState(null)
  const [logs, setLogs] = useState([])
  const [runningAgent, setRunningAgent] = useState(null)
  const [pipelineRunning, setPipelineRunning] = useState(false)
  const [statusMessage, setStatusMessage] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchExecutions = async () => {
    try {
      const res = await agentApi.listExecutions({ limit: 50 })
      const list = Array.isArray(res) ? res : (res?.data || [])
      setExecutions(list)
      if (list && list.length > 0 && !selectedExecution) {
        setSelectedExecution(list[0])
        loadLogs(list[0].id)
      }
    } catch (err) {
      console.error('Failed to load agent executions:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchExecutions()
  }, [])

  const loadLogs = async (executionId) => {
    try {
      const res = await agentApi.getExecutionLogs(executionId)
      const list = Array.isArray(res) ? res : (res?.data || [])
      setLogs(list)
    } catch {
      setLogs([])
    }
  }

  const handleSelectExecution = (exec) => {
    setSelectedExecution(exec)
    loadLogs(exec.id)
  }

  const handleTriggerAgent = async (agentName) => {
    setRunningAgent(agentName)
    setStatusMessage(null)
    try {
      const res = await agentApi.triggerAgent(agentName, {})
      setStatusMessage({
        type: 'success',
        text: `Agent '${agentName}' triggered successfully.`,
      })
      await fetchExecutions()
      if (res && res.id) {
        setSelectedExecution(res)
        loadLogs(res.id)
      }
    } catch (err) {
      setStatusMessage({
        type: 'error',
        text: err.response?.data?.detail || `Failed to trigger ${agentName}.`,
      })
    } finally {
      setRunningAgent(null)
    }
  }

  const handleRunPipeline = async () => {
    setPipelineRunning(true)
    setStatusMessage(null)
    try {
      const res = await agentApi.triggerAgent('coordinator', {})
      setStatusMessage({
        type: 'success',
        text: 'Full 7-Agent LangGraph Pipeline executed successfully.',
      })
      await fetchExecutions()
      if (res && res.id) {
        setSelectedExecution(res)
        loadLogs(res.id)
      }
    } catch (err) {
      setStatusMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Pipeline execution failed.',
      })
    } finally {
      setPipelineRunning(false)
    }
  }

  // Get last execution record for each agent with resilient normalization
  const getAgentLastRun = (agentId) => {
    const cleanId = agentId.toLowerCase().replace(/[^a-z0-9]/g, '').replace('agent', '')
    return executions.find((e) => {
      const eName = (e.agent_name || '').toLowerCase().replace(/[^a-z0-9]/g, '')
      return (
        eName.includes(cleanId) ||
        cleanId.includes(eName.replace('agent', '')) ||
        e.agent_name?.toLowerCase() === agentId.toLowerCase()
      )
    })
  }

  const completedAgentIds = SEVEN_AGENTS.filter((a) => {
    const run = getAgentLastRun(a.id)
    return run && run.status === 'completed'
  }).map((a) => a.id)

  return (
    <div className="space-y-6">
      {/* Title & Pipeline Run Action */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">
            AI Agent Operations & Monitoring Center
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time execution telemetry and LangGraph coordinator pipeline for all 7 independent scholarly AI agents.
          </p>
        </div>

        <Button
          onClick={handleRunPipeline}
          isLoading={pipelineRunning}
          className="bg-red-600 hover:bg-red-700 text-white font-bold px-4 py-2 text-xs shadow-md shadow-red-600/20"
        >
          ⚡ Run Complete 7-Agent Pipeline
        </Button>
      </div>

      {statusMessage && (
        <Alert
          type={statusMessage.type}
          message={statusMessage.text}
          onClose={() => setStatusMessage(null)}
        />
      )}

      {/* Execution Pipeline Visualization */}
      <AgentPipelineView
        currentAgent={runningAgent}
        completedAgents={completedAgentIds}
      />

      {/* The 7 Core AI Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {SEVEN_AGENTS.map((agent) => {
          const lastRun = getAgentLastRun(agent.id)
          const isRunning = runningAgent === agent.id

          return (
            <div
              key={agent.id}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between hover:border-blue-300 transition-all"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{agent.icon}</span>
                    <h3 className="font-bold text-slate-900 text-sm leading-tight">
                      {agent.name}
                    </h3>
                  </div>
                  {lastRun ? (
                    <span
                      className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                        lastRun.status === 'completed'
                          ? 'bg-emerald-100 text-emerald-800'
                          : lastRun.status === 'running'
                          ? 'bg-blue-100 text-blue-800 animate-pulse'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {lastRun.status}
                    </span>
                  ) : (
                    <span className="text-[10px] uppercase font-semibold text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
                      Standby
                    </span>
                  )}
                </div>

                <p className="text-xs text-slate-600 leading-relaxed mb-4">
                  {agent.responsibility}
                </p>

                {/* Telemetry info */}
                <div className="text-[11px] space-y-1 bg-slate-50 p-2.5 rounded-lg border border-slate-100 mb-4 text-slate-600">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Last Executed:</span>
                    <span className="font-medium text-slate-800">
                      {lastRun?.completed_at
                        ? new Date(lastRun.completed_at).toLocaleTimeString()
                        : 'Never'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Records Processed:</span>
                    <span className="font-mono font-bold text-slate-800">
                      {lastRun?.output_data?.records_processed ??
                        lastRun?.output_summary?.records_processed ??
                        (lastRun ? 'Available' : '0')}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Duration:</span>
                    <span className="font-mono text-slate-800">
                      {lastRun?.duration_seconds ? `${lastRun.duration_seconds.toFixed(2)}s` : '—'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2 border-t border-slate-100">
                <Button
                  size="sm"
                  className="w-full bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs"
                  isLoading={isRunning}
                  onClick={() => handleTriggerAgent(agent.id)}
                >
                  ▶ Run Agent
                </Button>
                {lastRun && (
                  <button
                    onClick={() => handleSelectExecution(lastRun)}
                    className="px-2.5 py-1.5 text-xs font-semibold rounded bg-slate-100 hover:bg-slate-200 text-slate-700 whitespace-nowrap cursor-pointer"
                    title="View Execution Logs"
                  >
                    View Logs
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Execution Logs Viewer */}
      <div className="mt-8">
        <h2 className="text-base font-bold text-slate-900 mb-3">
          Agent Execution Logs & State Inspector
        </h2>
        <AgentLogViewer
          logs={logs}
          selectedExecution={selectedExecution}
          onSelectExecution={handleSelectExecution}
        />
      </div>
    </div>
  )
}
