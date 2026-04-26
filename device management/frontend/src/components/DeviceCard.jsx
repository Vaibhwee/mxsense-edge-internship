export default function DeviceCard({ device, onClick }) {
  const health = device.health || {}
  return (
    <button
      onClick={onClick}
      className="w-full rounded-xl border border-slate-800 bg-slate-900/40 p-4 text-left hover:bg-slate-900/70"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="truncate text-sm font-semibold text-slate-100">{device.device_id}</div>
          <div className="truncate text-xs text-slate-400">{device.location_tag ?? '—'}</div>
        </div>
        <div className="text-xs text-slate-400">{device.timestamp ? new Date(device.timestamp).toLocaleString() : '—'}</div>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
        <div className="rounded-lg bg-slate-950/50 p-2">
          <div className="text-slate-400">SoC temp</div>
          <div className="font-semibold text-slate-100">{health.soc_temp_c ?? '—'}{health.soc_temp_c != null ? '°C' : ''}</div>
        </div>
        <div className="rounded-lg bg-slate-950/50 p-2">
          <div className="text-slate-400">GPU load</div>
          <div className="font-semibold text-slate-100">{health.gpu_load_percent ?? '—'}{health.gpu_load_percent != null ? '%' : ''}</div>
        </div>
        <div className="rounded-lg bg-slate-950/50 p-2">
          <div className="text-slate-400">RAM</div>
          <div className="font-semibold text-slate-100">{health.ram_usage_mb ?? '—'}{health.ram_usage_mb != null ? 'MB' : ''}</div>
        </div>
        <div className="rounded-lg bg-slate-950/50 p-2">
          <div className="text-slate-400">Fan</div>
          <div className="font-semibold text-slate-100">{health.fan_speed_rpm ?? '—'}{health.fan_speed_rpm != null ? 'rpm' : ''}</div>
        </div>
      </div>
    </button>
  )
}

