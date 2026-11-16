import { create } from 'zustand'

export const useAgentStore = create((set, get) => ({
  agents: [],
  activeExecutionId: null,
  pollingInterval: null,
  logs: {},         // { [agentId]: string[] }
  statuses: {},     // { [agentId]: 'idle' | 'running' | 'completed' | 'failed' }

  /**
   * Set all agent statuses from API response
   */
  setAgents: (agents) => {
    const statuses = {}
    agents.forEach((a) => { statuses[a.id] = a.status })
    set({ agents, statuses })
  },

  /**
   * Update a single agent's status
   */
  updateAgentStatus: (agentId, status) => {
    set((state) => ({
      statuses: { ...state.statuses, [agentId]: status },
      agents: state.agents.map((a) =>
        a.id === agentId ? { ...a, status } : a,
      ),
    }))
  },

  /**
   * Append logs for an agent execution
   */
  appendLogs: (agentId, newLogs) => {
    set((state) => ({
      logs: {
        ...state.logs,
        [agentId]: [...(state.logs[agentId] || []), ...newLogs],
      },
    }))
  },

  /**
   * Clear logs for an agent
   */
  clearLogs: (agentId) => {
    set((state) => ({
      logs: { ...state.logs, [agentId]: [] },
    }))
  },

  /**
   * Set the active execution being tracked
   */
  setActiveExecution: (executionId) => {
    set({ activeExecutionId: executionId })
  },

  /**
   * Reset all agent state
   */
  reset: () => {
    set({ agents: [], activeExecutionId: null, logs: {}, statuses: {} })
  },
}))
