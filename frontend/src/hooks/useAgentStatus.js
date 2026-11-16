import { useState, useEffect, useCallback, useRef } from 'react'
import { getAgentStatus, getAgentLogs } from '../api/agents'
import { useAgentStore } from '../store/agentStore'

/**
 * Polls a single agent's status at a given interval.
 * Stops polling when status is 'completed' or 'failed'.
 */
export function useAgentStatus(agentId, executionId, intervalMs = 3000) {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const updateAgentStatus = useAgentStore((s) => s.updateAgentStatus)
  const appendLogs = useAgentStore((s) => s.appendLogs)
  const intervalRef = useRef(null)

  const fetchStatus = useCallback(async () => {
    if (!agentId || !executionId) return

    try {
      setError(null)
      const data = await getAgentStatus(agentId)
      setStatus(data.status)
      updateAgentStatus(agentId, data.status)

      // Also fetch logs
      try {
        const logsData = await getAgentLogs(agentId, executionId)
        if (logsData?.logs?.length) {
          appendLogs(agentId, logsData.logs)
        }
      } catch {
        // Log fetch failures are non-critical
      }

      // Stop polling when done
      if (data.status === 'completed' || data.status === 'failed') {
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
          intervalRef.current = null
        }
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [agentId, executionId, updateAgentStatus, appendLogs])

  useEffect(() => {
    if (!agentId || !executionId) return

    setLoading(true)
    fetchStatus()

    intervalRef.current = setInterval(fetchStatus, intervalMs)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [agentId, executionId, intervalMs, fetchStatus])

  return { status, loading, error, refetch: fetchStatus }
}
