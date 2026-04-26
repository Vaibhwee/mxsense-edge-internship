import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'

import { api } from '../api/client.js'
import SensorChart from '../components/SensorChart.jsx'
import { useWebSocket } from '../hooks/useWebSocket.js'

const tabs = [
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

export default function DeviceDetail() {
  const { deviceId } = useParams()
  const [detail, setDetail] = useState(null)
  const [activeType, setActiveType] = useState('env')
  const [rows, setRows] = useState([])
 
  const { status: wsStatus } = useWebSocket(`/ws/device/${encodeURIComponent(deviceId)}/`, {
    onMessage: (msg) => {
      const payload = msg?.payload?.sensor_payload
      const block = msg?.[activeType] ?? payload?.[activeType]
      if (!block) return
      setRows((prev) => [...prev, { timestamp: msg.timestamp, ...block }].slice(-300))
    },
  })

  useEffect(() => {
    let cancelled = false
    api
      .get(`/devices/${encodeURIComponent(deviceId)}/`)
      .then((res) => {
        if (cancelled) return
        setDetail(res.data)
      })
      .catch(() => setDetail(null))
    return () => {
      cancelled = true
    }
  }, [deviceId])

  useEffect(() => {
    let cancelled = false
    api
      .get(`/devices/${encodeURIComponent(deviceId)}/sensor/${activeType}/?limit=300`)
      .then((res) => {
        if (cancelled) return
        setRows(res.data.rows ?? [])
      })
      .catch(() => setRows([]))
    return () => {
      cancelled = true
    }
  }, [deviceId, activeType])

  const chartSeries = useMemo(() => seriesByType[activeType] || [], [activeType])
  const title = useMemo(() => {
    const label = tabs.find((t) => t.id === activeType)?.label ?? activeType
    return `${label} • ${deviceId}`
  }, [activeType, deviceId])

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="text-lg font-semibold text-slate-100">{deviceId}</div>
            <div className="text-xs text-slate-400">
              WebSocket: <span className="font-medium text-slate-200">{wsStatus}</span>
            </div>
          </div>
          <div className="text-xs text-slate-400">
            Firmware: <span className="text-slate-200">{detail?.header?.firmware_version ?? '—'}</span>
            <span className="mx-2 text-slate-700">|</span>
            Location: <span className="text-slate-200">{detail?.header?.location_tag ?? '—'}</span>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2 md:grid-cols-4">
          {[
            ['SoC temp', detail?.device_health?.soc_temp_c, '°C'],
            ['GPU', detail?.device_health?.gpu_load_percent, '%'],
            ['RAM', detail?.device_health?.ram_usage_mb, 'MB'],
            ['Fan', detail?.device_health?.fan_speed_rpm, 'rpm'],
          ].map(([k, v, unit]) => (
            <div key={k} className="rounded-lg bg-slate-950/50 p-3">
              <div className="text-xs text-slate-400">{k}</div>
              <div className="text-sm font-semibold text-slate-100">
                {v ?? '—'}
                {v != null ? unit : ''}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {tabs.map((t) => (
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

      <SensorChart title={title} data={rows} series={chartSeries} />
    </div>
  )
}
