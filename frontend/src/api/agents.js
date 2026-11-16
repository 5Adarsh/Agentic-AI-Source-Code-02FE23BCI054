import api from './axios'

/**
 * Trigger an agent run or full pipeline coordinator
 */
export const triggerAgent = async (agentName, inputData = {}) => {
  const { data } = await api.post('/agents/trigger', {
    agent_name: agentName,
    input_data: inputData,
  })
  return data
}

/**
 * List agent executions
 */
export const listExecutions = async (params = {}) => {
  const { data } = await api.get('/agents/', { params })
  return data
}

/**
 * Get a specific execution status
 */
export const getExecution = async (executionId) => {
  const { data } = await api.get(`/agents/${executionId}`)
  return data
}

/**
 * Get logs for a specific execution
 */
export const getExecutionLogs = async (executionId, params = {}) => {
  const { data } = await api.get(`/agents/${executionId}/logs`, { params })
  return data
}

export const agentApi = {
  triggerAgent,
  listExecutions,
  getExecution,
  getExecutionLogs,
}
