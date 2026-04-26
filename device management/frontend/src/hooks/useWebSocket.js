import { useEffect, useMemo, useRef, useState } from 'react'
const base = "ws://localhost:8000";
export function useWebSocket(path, { onMessage } = {}) {
  const [status, setStatus] = useState('disconnected')
  const wsRef = useRef(null)
  const onMessageRef = useRef(onMessage)
  onMessageRef.current = onMessage

  const url = useMemo(() => {
  return `${base.replace(/\/$/, '')}${path.startsWith('/') ? path : `/${path}`}`
}, [path])

  useEffect(() => {
    let closedByEffect = false
    let retry = 0

    const connect = () => {
      if (closedByEffect) return
      setStatus('connecting')

      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        retry = 0
        setStatus('connected')
      }
      ws.onclose = () => {
        setStatus('disconnected')
        if (closedByEffect) return
        const delay = Math.min(15000, 500 * 2 ** retry)
        retry += 1
        setTimeout(connect, delay)
      }
      ws.onerror = () => {}
      ws.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data)
          console.log('WS DATA:', data)
          onMessageRef.current?.(data)
        } catch {
          // ignore
        }
      }
    }

    connect()
    return () => {
      closedByEffect = true
      try {
        wsRef.current?.close()
      } catch {
        // ignore
      }
    }
  }, [url])

  return { status }
}
