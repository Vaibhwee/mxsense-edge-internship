"use client";

import { useState } from "react";
import AnalyticsCard from "./AnalyticsCard";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function AnalyticsOverview() {
  const [visible, setVisible] = useState({
    failures: true,
    inferences: true,
    success: true,
  });

  const activeDevices = {
    title: "Active vs Inactive Devices",
    data: [
      { name: "Active", value: 8 },
      { name: "Inactive", value: 2 },
    ],
  };

  const alertsDistribution = {
    title: "Alerts Distribution",
    data: [
      { name: "Open", value: 3 },
      { name: "Closed", value: 7 },
    ],
  };

  const jobStatus = {
    title: "Job Status",
    data: [
      { name: "Running", value: 2 },
      { name: "Queued", value: 5 },
      { name: "Completed", value: 10 },
    ],
  };

  const adaptationStatus = {
    title: "Adaptation Status",
    data: [
      { name: "Essense", value: 6 },
      { name: "Adapted", value: 4 },
    ],
  };

  const edgeDetails = {
    site: "Plant 01 - Line A",
    gateway: "MX-EDGE-GW-007",
    modelVersion: "v2.3.1",
    lastSync: "2 min ago",
    health: "Healthy",
    cpuUsage: "38%",
    memoryUsage: "62%",
    storageUsage: "71%",
    temperature: "54 C",
    uptime: "14d 06h",
  };

  const performanceTrends = [
    { time: "10:00", failures: 2, inferences: 20, success: 18 },
    { time: "10:05", failures: 1, inferences: 25, success: 24 },
    { time: "10:10", failures: 3, inferences: 30, success: 27 },
    { time: "10:15", failures: 2, inferences: 28, success: 26 },
    { time: "10:20", failures: 1, inferences: 32, success: 31 },
    { time: "10:25", failures: 2, inferences: 29, success: 27 },
  ];

  return (
    <div className="mt-6 w-full">
      <h2 className="text-xl font-semibold mb-4">Analytics Overview</h2>

      <div
        className="w-full border border-red-500"
        style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "24px" }}
      >
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: "24px" }}>
          <div style={{ height: 220 }}>
            <AnalyticsCard {...activeDevices} />
          </div>
          <div style={{ height: 220 }}>
            <AnalyticsCard {...alertsDistribution} />
          </div>
          <div style={{ height: 220 }}>
            <AnalyticsCard {...adaptationStatus} />
          </div>
          <div style={{ height: 220 }}>
            <AnalyticsCard {...jobStatus} />
          </div>
        </div>
        <div style={{ height: "fit-content", position: "sticky", top: "24px" }}>
          <div
            className="dashboard-hover-card dashboard-hover-edge bg-[#0b1b34] rounded-xl p-4 border border-blue-900/30 shadow-md overflow-y-auto"
            style={{ maxHeight: "calc(100vh - 8rem)" }}
          >
            <h3 className="text-sm font-semibold text-gray-200 mb-4">Edge Details</h3>
            <div className="space-y-3 text-sm">
              <div className="rounded-lg bg-[#102446] px-3 py-2">
                <p className="text-xs text-gray-400">Site</p>
                <p className="text-gray-100 font-medium">{edgeDetails.site}</p>
              </div>
              <div className="rounded-lg bg-[#102446] px-3 py-2">
                <p className="text-xs text-gray-400">Gateway</p>
                <p className="text-gray-100 font-medium">{edgeDetails.gateway}</p>
              </div>
              <div className="rounded-lg bg-[#102446] px-3 py-2">
                <p className="text-xs text-gray-400">Model Version</p>
                <p className="text-gray-100 font-medium">{edgeDetails.modelVersion}</p>
              </div>
              <div className="rounded-lg bg-[#102446] px-3 py-2">
                <p className="text-xs text-gray-400">Last Sync</p>
                <p className="text-gray-100 font-medium">{edgeDetails.lastSync}</p>
              </div>
              <div className="rounded-lg bg-[#102446] px-3 py-2">
                <p className="text-xs text-gray-400">Health</p>
                <p className="text-emerald-400 font-semibold">{edgeDetails.health}</p>
              </div>
            </div>

            <div className="mt-5">
              <h4 className="text-xs uppercase tracking-wide text-gray-400 mb-2">
                Runtime Metrics
              </h4>
              <div className="space-y-3 text-xs text-gray-300">
                <div className="rounded-md bg-[#102446] px-3 py-2">
                  <div className="mb-1 flex items-center justify-between">
                    <span>CPU Usage</span>
                    <span className="font-semibold text-gray-100">{edgeDetails.cpuUsage}</span>
                  </div>
                  <div
                    className="w-full rounded-full"
                    style={{ height: 8, background: "#1a3057" }}
                  >
                    <div
                      className="rounded-full"
                      style={{
                        height: 8,
                        width: edgeDetails.cpuUsage,
                        background: "linear-gradient(90deg, #22d3ee 0%, #60a5fa 100%)",
                        boxShadow: "0 0 10px rgba(34, 211, 238, 0.35)",
                        transition: "width 300ms ease",
                      }}
                    />
                  </div>
                </div>
                <div className="rounded-md bg-[#102446] px-3 py-2">
                  <div className="mb-1 flex items-center justify-between">
                    <span>Memory Usage</span>
                    <span className="font-semibold text-gray-100">{edgeDetails.memoryUsage}</span>
                  </div>
                  <div
                    className="w-full rounded-full"
                    style={{ height: 8, background: "#1a3057" }}
                  >
                    <div
                      className="rounded-full"
                      style={{
                        height: 8,
                        width: edgeDetails.memoryUsage,
                        background: "linear-gradient(90deg, #8b5cf6 0%, #c084fc 100%)",
                        boxShadow: "0 0 10px rgba(168, 85, 247, 0.35)",
                        transition: "width 300ms ease",
                      }}
                    />
                  </div>
                </div>
                <div className="rounded-md bg-[#102446] px-3 py-2">
                  <div className="mb-1 flex items-center justify-between">
                    <span>Storage Usage</span>
                    <span className="font-semibold text-gray-100">{edgeDetails.storageUsage}</span>
                  </div>
                  <div
                    className="w-full rounded-full"
                    style={{ height: 8, background: "#1a3057" }}
                  >
                    <div
                      className="rounded-full"
                      style={{
                        height: 8,
                        width: edgeDetails.storageUsage,
                        background: "linear-gradient(90deg, #10b981 0%, #4ade80 100%)",
                        boxShadow: "0 0 10px rgba(16, 185, 129, 0.35)",
                        transition: "width 300ms ease",
                      }}
                    />
                  </div>
                </div>
                <div className="flex items-center justify-between rounded-md bg-[#102446] px-3 py-2">
                  <span>Temperature</span>
                  <span className="font-semibold text-gray-100">{edgeDetails.temperature}</span>
                </div>
                <div className="flex items-center justify-between rounded-md bg-[#102446] px-3 py-2">
                  <span>Uptime</span>
                  <span className="font-semibold text-gray-100">{edgeDetails.uptime}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 w-full">
        <div className="dashboard-hover-card bg-[#0b1b34] rounded-xl p-4 border border-blue-900/30 shadow-md">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-200">Performance Trends</h3>
          </div>

          <div className="mb-4 flex flex-wrap items-center gap-4 text-xs">
            <label className="flex items-center gap-2 text-red-400">
              <input
                type="checkbox"
                checked={visible.failures}
                onChange={() =>
                  setVisible((prev) => ({
                    ...prev,
                    failures: !prev.failures,
                  }))
                }
              />
              Failures
            </label>
            <label className="flex items-center gap-2 text-sky-400">
              <input
                type="checkbox"
                checked={visible.inferences}
                onChange={() =>
                  setVisible((prev) => ({
                    ...prev,
                    inferences: !prev.inferences,
                  }))
                }
              />
              Inferences
            </label>
            <label className="flex items-center gap-2 text-emerald-400">
              <input
                type="checkbox"
                checked={visible.success}
                onChange={() =>
                  setVisible((prev) => ({
                    ...prev,
                    success: !prev.success,
                  }))
                }
              />
              Success Rate
            </label>
          </div>

          <div style={{ width: "100%", height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={performanceTrends} margin={{ top: 10, right: 20, left: 0, bottom: 6 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.18)" />
                <XAxis dataKey="time" tick={{ fill: "#9ca3af", fontSize: 11 }} axisLine={{ stroke: "#23324f" }} />
                <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} axisLine={{ stroke: "#23324f" }} />
                <Tooltip
                  contentStyle={{
                    background: "rgba(8, 14, 30, 0.95)",
                    border: "1px solid rgba(112, 151, 255, 0.22)",
                    borderRadius: 10,
                  }}
                  labelStyle={{ color: "#e5e7eb", fontWeight: 700 }}
                />
                <Legend wrapperStyle={{ color: "#d1d5db", fontSize: 12 }} />
                {visible.failures && (
                  <Line
                    type="monotone"
                    dataKey="failures"
                    name="Failures"
                    stroke="#ef4444"
                    strokeWidth={2.2}
                    dot={{ r: 2 }}
                    activeDot={{ r: 5 }}
                    isAnimationActive
                  />
                )}
                {visible.inferences && (
                  <Line
                    type="monotone"
                    dataKey="inferences"
                    name="Inferences"
                    stroke="#38bdf8"
                    strokeWidth={2.2}
                    dot={{ r: 2 }}
                    activeDot={{ r: 5 }}
                    isAnimationActive
                  />
                )}
                {visible.success && (
                  <Line
                    type="monotone"
                    dataKey="success"
                    name="Success Rate"
                    stroke="#22c55e"
                    strokeWidth={2.2}
                    dot={{ r: 2 }}
                    activeDot={{ r: 5 }}
                    isAnimationActive
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

