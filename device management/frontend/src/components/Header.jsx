import { Link, useNavigate } from 'react-router-dom'
import { LogOut } from 'lucide-react'

export default function Header() {
  const navigate = useNavigate()

  return (
    <header className="border-b border-slate-800 bg-slate-950/70 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-fuchsia-500 to-cyan-500" />
          <div className="leading-tight">
            <Link to="/" className="text-sm font-semibold tracking-wide text-slate-100">
              MXSense
            </Link>
            <div className="text-xs text-slate-400">Device Management Dashboard</div>
          </div>
        </div>

        <button
          className="inline-flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs font-medium text-slate-100 hover:bg-slate-800"
          onClick={() => {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            navigate('/login')
          }}
        >
          <LogOut className="h-4 w-4" />
          Logout
        </button>
      </div>
    </header>
  )
}

