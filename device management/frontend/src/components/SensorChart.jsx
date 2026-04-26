import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useMemo } from 'react'

function fmtTime(ts) {
  const d = new Date(ts)
  return isNaN(d.getTime()) ? '' : d.toLocaleTimeString()
}

function normalizeChartValue(value) {
  if (typeof value === 'number' || typeof value === 'boolean') return value
  if (typeof value === 'string' && value.trim() !== '') {
    const numericValue = Number(value)
    if (!Number.isNaN(numericValue)) return numericValue
  }
  return value
}

export default function SensorChart({ title, data, series }) {
  const visibleSeries = useMemo(() => {
    return (series || []).filter((item) =>
      (data || []).some((row) => {
        const value = normalizeChartValue(row?.[item.key])
        return typeof value === 'number' || typeof value === 'boolean'
      }),
    )
  }, [data, series])

  const chartData = useMemo(() => {
    return (data || []).map((row) => {
      const next = { ...row }
      visibleSeries.forEach((item) => {
        const normalizedValue = normalizeChartValue(next[item.key])
        if (typeof normalizedValue === 'boolean') {
          next[item.key] = normalizedValue ? 1 : 0
        } else {
          next[item.key] = normalizedValue
        }
      })
      return next
    })
  }, [data, visibleSeries])

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="text-sm font-semibold text-slate-100">{title}</div>
        <div className="text-xs text-slate-400">{data?.length ? `${data.length} pts` : '—'}</div>
      </div>

      <div className="h-64 min-w-0">
        {visibleSeries.length ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
              <CartesianGrid stroke="rgba(148,163,184,0.15)" strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={fmtTime}
                stroke="rgba(148,163,184,0.8)"
                fontSize={12}
              />
              <YAxis stroke="rgba(148,163,184,0.8)" fontSize={12} />
              <Tooltip
                contentStyle={{
                  background: 'rgba(15, 23, 42, 0.95)',
                  border: '1px solid rgba(51, 65, 85, 0.8)',
                  borderRadius: 12,
                }}
                labelFormatter={(v) => new Date(v).toLocaleString()}
              />
              <Legend />
              {visibleSeries.map((s) => (
                <Line
                  key={s.key}
                  type="monotone"
                  dataKey={s.key}
                  name={s.label ?? s.key}
                  stroke={s.color}
                  strokeWidth={2}
                  dot={
                    chartData.length <= 1
                      ? { r: 4, strokeWidth: 1, fill: s.color }
                      : { r: 2, strokeWidth: 0, fill: s.color }
                  }
                  activeDot={{ r: 4 }}
                  isAnimationActive={false}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-full items-center justify-center rounded-lg border border-dashed border-slate-800 bg-slate-950/30 px-6 text-center text-sm text-slate-400">
            No plottable sensor values are available for this section yet.
          </div>
        )}
      </div>
    </div>
  )
}
