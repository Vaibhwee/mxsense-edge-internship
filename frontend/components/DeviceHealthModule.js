"use client";

import { useEffect, useMemo, useState } from "react";

const ALLOWED_DEVICE_UIDS = new Set(["device_01", "device_02", "device_03", "device_04", "device_05"]);

function StatusPill({ status }) {
  const normalized = String(status || "").toUpperCase();
  const cls =
    normalized === "HEALTHY"
      ? "health-pill is-green"
      : normalized === "WARNING"
        ? "health-pill is-amber"
        : normalized === "CRITICAL"
          ? "health-pill is-red"
          : "health-pill";
  return <span className={cls}>{normalized || "NO DATA"}</span>;
}

export default function DeviceHealthModule() {
  const apiRoot = process.env.NEXT_PUBLIC_PLATFORM_API_ROOT || "http://127.0.0.1:8000/api";
  const [devices, setDevices] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    async function loadDevices() {
      try {
        const res = await fetch(`${apiRoot}/api-gateway/devices/`, { cache: "no-store" });
        const payload = res.ok ? await res.json() : null;
        const rows = Array.isArray(payload?.results) ? payload.results : Array.isArray(payload) ? payload : [];
        if (!active) return;
        const normalized = rows
          .map((d) => ({
            ...d,
            device_id: d?.device_id || d?.id,
            device_uid: d?.device_uid || d?.external_id || d?.name || d?.id,
          }))
          .filter((d) => ALLOWED_DEVICE_UIDS.has(String(d?.device_uid || "").trim()));
        setDevices(normalized);
        const firstId = normalized.find((d) => d?.device_id)?.device_id || "";
        setSelectedId((prev) => prev || firstId);
      } catch {
        if (!active) return;
        setDevices([]);
      }
    }
    loadDevices();
    return () => {
      active = false;
    };
  }, [apiRoot]);

  const selectedDevice = useMemo(
    () => devices.find((d) => String(d?.device_id) === String(selectedId)) || null,
    [devices, selectedId]
  );

  useEffect(() => {
    let active = true;
    async function loadHealth() {
      if (!selectedId) {
        setHealth(null);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${apiRoot}/monitoring/device-health/${selectedId}/`, { cache: "no-store" });
        const payload = res.ok ? await res.json() : null;
        if (!active) return;
        setHealth(payload);
      } catch {
        if (!active) return;
        setError("Failed to load device health.");
        setHealth(null);
      } finally {
        if (active) setLoading(false);
      }
    }
    loadHealth();
    return () => {
      active = false;
    };
  }, [apiRoot, selectedId]);

  return (
    <section className="health-module">
      <div className="health-header">
        <div>
          <h2 className="health-title">Device Health</h2>
          <p className="health-subtitle">Hardware reliability (flow, fan, connectivity).</p>
        </div>

        <div className="health-selector">
          <label className="health-label" htmlFor="device-health-device">
            Device
          </label>
          <select
            id="device-health-device"
            className="health-select"
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value)}
          >
            {devices.map((d) => (
              <option key={d.device_id} value={d.device_id}>
                {d.device_uid}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="health-grid">
        <div className="health-card">
          <div className="health-card-row">
            <span className="health-card-k">Status</span>
            <StatusPill status={health?.status} />
          </div>
          <div className="health-metric">
            <span>Health score</span>
            <strong>{health?.score ?? "—"}</strong>
          </div>
          <div className="health-metric">
            <span>Last seen</span>
            <strong>{health?.last_seen ? new Date(health.last_seen).toLocaleString() : "—"}</strong>
          </div>
        </div>

        <div className="health-card">
          <div className="health-card-row">
            <span className="health-card-k">Device</span>
            <span className="health-card-v">
              {selectedDevice?.device_uid || selectedId || "—"}
            </span>
          </div>

          {loading ? (
            <div className="health-muted">Loading...</div>
          ) : error ? (
            <div className="health-error">{error}</div>
          ) : (
            <div className="health-kv-grid">
              <div className="health-kv">
                <span>Flow OK</span>
                <strong>{health?.flow_ok === null || health?.flow_ok === undefined ? "—" : health.flow_ok ? "Yes" : "No"}</strong>
              </div>
              <div className="health-kv">
                <span>Fan OK</span>
                <strong>{health?.fan_ok === null || health?.fan_ok === undefined ? "—" : health.fan_ok ? "Yes" : "No"}</strong>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

