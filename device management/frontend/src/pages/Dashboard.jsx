import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from '../api/client.js'
import DeviceCard from '../components/DeviceCard.jsx'
import SensorChart from '../components/SensorChart.jsx'
import { useWebSocket } from '../hooks/useWebSocket.js'

const sensorTabs = [
  { id: 'env', label: 'ENV' },
  { id: 'voc', label: 'VOC' },
  { id: 'gas', label: 'Gas' },
  { id: 'pm', label: 'PM' },
  { id: 'system', label: 'System' },
  { id: 'flow', label: 'Flow' },
  { id: 'force', label: 'Force' },
  { id: 'acoustic', label: 'Acoustic' },
  { id: 'distance', label: 'Distance' },
]

const seriesByType = {
  env: [
    { key: 'sht45_temperature', color: '#22c55e' },
    { key: 'sht45_humidity', color: '#06b6d4' },
    { key: 'bme688_temperature', color: '#a855f7' },
    { key: 'bme688_pressure', color: '#f59e0b' },
  ],
  voc: [
    { key: 'sgp41_voc_index', color: '#22c55e' },
    { key: 'sgp41_nox_index', color: '#f59e0b' },
    { key: 'zmod4410_voc_concentration', color: '#06b6d4' },
    { key: 'tgs2602_odor_level', color: '#a855f7' },
  ],
  gas: [
    { key: 'mq135_air_quality', color: '#22c55e' },
    { key: 'mq136_sulfur_level', color: '#f59e0b' },
    { key: 'tgs2600_contamination', color: '#06b6d4' },
    { key: 'ethylene_sensor_value', color: '#a855f7' },
  ],
  pm: [
    { key: 'pms7003_pm2_5', color: '#22c55e' },
    { key: 'pms7003_pm10', color: '#f59e0b' },
    { key: 'sps30_pm2_5', color: '#06b6d4' },
    { key: 'sps30_pm10', color: '#a855f7' },
  ],
  system: [
    { key: 'cpu_temp', color: '#22c55e' },
    { key: 'gpu_load', color: '#06b6d4' },
    { key: 'ram_usage', color: '#f59e0b' },
    { key: 'fan_speed', color: '#f43f5e' },
  ],
  flow: [
    { key: 'mpxv7002dp_pressure_diff', color: '#22c55e' },
    { key: 'sfm3003_flow_rate', color: '#06b6d4' },
  ],
  force: [
    { key: 'loadcell_2kg_force', color: '#22c55e' },
    { key: 'loadcell_5kg_force', color: '#06b6d4' },
  ],
  acoustic: [{ key: 'inmp441_noise_level', color: '#22c55e' }],
  distance: [{ key: 'value', color: '#22c55e' }],
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [summary, setSummary] = useState([])
  const [selectedDevice, setSelectedDevice] = useState(null)
  const [activeType, setActiveType] = useState('env')
  const [seriesRows, setSeriesRows] = useState([])
 
  const { status: wsStatus } = useWebSocket('/ws/dashboard/', {
    onMessage: (msg) => {
      const deviceId = msg?.device_id
      if (!deviceId) return
      if (selectedDevice && deviceId !== selectedDevice) return

      const payload = msg?.payload?.sensor_payload
      const block = msg?.[activeType] ?? payload?.[activeType]
      if (!block) return

      setSeriesRows((prev) => {
        const next = [...prev, { timestamp: msg.timestamp, ...block }]
        return next.slice(-300)
      })
    },
  })

  useEffect(() => {
    let cancelled = false
    api
      .get('/dashboard/summary/')
      .then((res) => {
        if (cancelled) return
        setSummary(res.data.devices ?? [])
        const first = (res.data.devices ?? [])[0]?.device_id
        setSelectedDevice((cur) => cur ?? first ?? null)
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!selectedDevice) return
    let cancelled = false
    api
      .get(`/devices/${encodeURIComponent(selectedDevice)}/sensor/${activeType}/?limit=300`)
      .then((res) => {
        if (cancelled) return
        setSeriesRows(res.data.rows ?? [])
      })
      .catch(() => setSeriesRows([]))
    return () => {
      cancelled = true
    }
  }, [selectedDevice, activeType])

  const chartSeries = useMemo(() => seriesByType[activeType] || [], [activeType])
  const title = useMemo(() => {
    const label = sensorTabs.find((t) => t.id === activeType)?.label ?? activeType
    return `${label} • ${selectedDevice ?? '—'}`
  }, [activeType, selectedDevice])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <div className="text-lg font-semibold text-slate-100">Dashboard</div>
          <div className="text-xs text-slate-400">
            WebSocket: <span className="font-medium text-slate-200">{wsStatus}</span>
          </div>
        </div>
        <button
          className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs font-medium hover:bg-slate-800"
          onClick={() => {
            api
              .get('/dashboard/summary/')
              .then((res) => setSummary(res.data.devices ?? []))
              .catch(() => {})
          }}
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
        {summary.map((d) => (
          <DeviceCard
            key={d.device_id}
            device={d}
            onClick={() => {
              setSelectedDevice(d.device_id)
              navigate(`/devices/${encodeURIComponent(d.device_id)}`)
            }}
          />
        ))}
      </div>

      <div className="flex flex-wrap gap-2">
        {sensorTabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveType(t.id)}
            className={[
              'rounded-full px-3 py-1.5 text-xs font-semibold tracking-wide',
              activeType === t.id
                ? 'bg-slate-100 text-slate-900'
                : 'border border-slate-800 bg-slate-900/40 text-slate-200 hover:bg-slate-800/60',
            ].join(' ')}
          >
            {t.label}
          </button>
        ))}
      </div>

      <SensorChart title={title} data={seriesRows} series={chartSeries} />
    </div>
  )
}
