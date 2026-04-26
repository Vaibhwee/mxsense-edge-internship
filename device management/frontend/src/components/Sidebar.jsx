import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Cpu, LayoutDashboard } from 'lucide-react'

import { api } from '../api/client.js'

export default function Sidebar() {
  const [devices, setDevices] = useState([])
  const location = useLocation()

  useEffect(() => {
    let cancelled = false
    api
      .get('/devices/')
      .then((res) => {
        if (cancelled) return
        setDevices(res.data.devices ?? [])
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [])

  const isActive = (path) => location.pathname === path

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-3">
      <nav className="space-y-1">
        <Link
          to="/"
          className={[
            'flex items-center gap-2 rounded-lg px-3 py-2 text-sm',
            isActive('/') ? 'bg-slate-800 text-white' : 'text-slate-300 hover:bg-slate-800/60',
          ].join(' ')}
        >
          <LayoutDashboard className="h-4 w-4" />
          Dashboard
        </Link>
      </nav>

      <div className="mt-4 border-t border-slate-800 pt-3">
        <div className="px-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
          Devices
        </div>
        <div className="mt-2 max-h-[55vh] space-y-1 overflow-auto pr-1">
          {devices.length === 0 ? (
            <div className="px-3 py-2 text-sm text-slate-400">No devices yet</div>
          ) : (
            devices.map((id) => (
              <Link
                key={id}
                to={`/devices/${encodeURIComponent(id)}`}
                className={[
                  'flex items-center gap-2 rounded-lg px-3 py-2 text-sm',
                  location.pathname === `/devices/${id}`
                    ? 'bg-slate-800 text-white'
                    : 'text-slate-300 hover:bg-slate-800/60',
                ].join(' ')}
              >
                <Cpu className="h-4 w-4" />
                <span className="truncate">{id}</span>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

