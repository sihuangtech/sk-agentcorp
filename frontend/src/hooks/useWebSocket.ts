import { useEffect, useRef, useCallback } from 'react'
import { usePhantomStore } from '../lib/store'
import type { WSMessage } from '../lib/types'

/**
 * useWebSocket — Connects to the SK AgentCorp WebSocket and auto-refreshes
 * store data when relevant events arrive.
 */
export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  const activeCompanyId = usePhantomStore((s) => s.activeCompanyId)
  const loadCompanyData = usePhantomStore((s) => s.loadCompanyData)
  const fetchDashboardStats = usePhantomStore((s) => s.fetchDashboardStats)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const wsUrl = (import.meta.env.VITE_WS_URL || 'ws://localhost:8000') + '/ws'
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('[WS] Connected to SK AgentCorp')
    }

    ws.onmessage = (event) => {
      try {
        const msg: WSMessage = JSON.parse(event.data)

        switch (msg.type) {
          case 'agent_update':
          case 'task_update':
          case 'heartbeat':
            // Refresh all company data when we get any relevant update
            if (activeCompanyId) {
              loadCompanyData(activeCompanyId)
            }
            fetchDashboardStats()
            break
          case 'pong':
            // ping-pong keepalive, ignore
            break
          default:
            break
        }
      } catch {
        // ignore malformed messages
      }
    }

    ws.onclose = () => {
      console.log('[WS] Disconnected, reconnecting in 3s...')
      reconnectTimer.current = setTimeout(connect, 3000)
    }

    ws.onerror = () => {
      ws.close()
    }
  }, [activeCompanyId, loadCompanyData, fetchDashboardStats])

  useEffect(() => {
    connect()

    // Ping keepalive every 30s
    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000)

    return () => {
      clearInterval(pingInterval)
      clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [connect])
}
