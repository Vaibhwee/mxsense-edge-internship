import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { api } from '../api/client.js'

export default function Register() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  return (
    <div className="grid min-h-full place-items-center bg-slate-950 px-4 py-10 text-slate-100">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
        <div className="text-lg font-semibold">Create account</div>
        <div className="mt-1 text-sm text-slate-400">Register to access the dashboard.</div>

        {error ? (
          <div className="mt-4 rounded-lg border border-red-900/60 bg-red-950/40 p-3 text-sm text-red-200">
            {error}
          </div>
        ) : null}

        <form
          className="mt-5 space-y-3"
          onSubmit={(e) => {
            e.preventDefault()
            setLoading(true)
            setError('')
            api
              .post('/auth/register/', { username, email, password })
              .then(() => api.post('/auth/login/', { username, password }))
              .then((res) => {
                localStorage.setItem('access_token', res.data.access)
                localStorage.setItem('refresh_token', res.data.refresh)
                navigate('/')
              })
              .catch((err) => {
                const msg = err?.response?.data?.error
                setError(msg || 'Registration failed')
              })
              .finally(() => setLoading(false))
          }}
        >
          <label className="block">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">
              Username
            </div>
            <input
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/50 px-3 py-2 text-sm outline-none focus:border-cyan-500"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
            />
          </label>
          <label className="block">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Email</div>
            <input
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/50 px-3 py-2 text-sm outline-none focus:border-cyan-500"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </label>
          <label className="block">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">
              Password
            </div>
            <input
              type="password"
              className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/50 px-3 py-2 text-sm outline-none focus:border-cyan-500"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
            />
          </label>

          <button
            disabled={loading}
            className="w-full rounded-lg bg-gradient-to-r from-fuchsia-500 to-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950 hover:opacity-95 disabled:opacity-60"
          >
            {loading ? 'Creating…' : 'Create account'}
          </button>
        </form>

        <div className="mt-4 text-sm text-slate-400">
          Already have an account?{' '}
          <Link className="font-semibold text-slate-200 hover:underline" to="/login">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  )
}

