"use client";

import { useMemo, useState } from "react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

function safeNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

function normalizeData(data) {
  const arr = Array.isArray(data) ? data : [];
  return arr
    .map((d) => ({
      label: String(d?.label ?? "—"),
      value: safeNumber(d?.value),
    }))
    .filter((d) => d.label && Number.isFinite(d.value));
}

function getDominant(values) {
  if (!values?.length) return { label: "—", value: 0, percent: 0 };
  const total = values.reduce((sum, d) => sum + safeNumber(d.value), 0);
  const max = values.reduce((best, d) => (safeNumber(d.value) > safeNumber(best.value) ? d : best), values[0]);
  const percent = total > 0 ? (safeNumber(max.value) / total) * 100 : 0;
  return { label: max.label, value: max.value, percent };
}

function iconForTitle(title) {
  const t = String(title || "").toLowerCase();

  // Inline SVG icons to match the dashboard style without extra deps.
  if (t.includes("active") || t.includes("device") || t.includes("adapter")) {
    return (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M7 7h10v10H7V7Z"
          stroke="currentColor"
          strokeWidth="2"
          opacity="0.9"
        />
        <path
          d="M4 9V6.5C4 5.12 5.12 4 6.5 4H9"
          stroke="currentColor"
          strokeWidth="2"
          opacity="0.65"
          strokeLinecap="round"
        />
        <path
          d="M20 9V6.5C20 5.12 18.88 4 17.5 4H15"
          stroke="currentColor"
          strokeWidth="2"
          opacity="0.65"
          strokeLinecap="round"
        />
        <path
          d="M4 15v2.5C4 18.88 5.12 20 6.5 20H9"
          stroke="currentColor"
          strokeWidth="2"
          opacity="0.65"
          strokeLinecap="round"
        />
        <path
          d="M20 15v2.5C20 18.88 18.88 20 17.5 20H15"
          stroke="currentColor"
          strokeWidth="2"
          opacity="0.65"
          strokeLinecap="round"
        />
      </svg>
    );
  }

  if (t.includes("alert")) {
    return (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 9v4"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
        <path
          d="M12 17h.01"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
        <path
          d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"
          stroke="currentColor"
          strokeWidth="2"
          opacity="0.9"
        />
      </svg>
    );
  }

  if (t.includes("job") || t.includes("running") || t.includes("queued") || t.includes("completed")) {
    return (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 2v4"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.9"
        />
        <path
          d="M7 8h10"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.7"
        />
        <path
          d="M5 10v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V10a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2Z"
          stroke="currentColor"
          strokeWidth="2"
          opacity="0.9"
        />
        <path
          d="M9 14h6"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.7"
        />
      </svg>
    );
  }

  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 2 20 6v12l-8 4-8-4V6l8-4Z"
        stroke="currentColor"
        strokeWidth="2"
        opacity="0.9"
      />
      <path
        d="M12 8v4"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        opacity="0.65"
      />
    </svg>
  );
}

export default function AnalyticsCard({ title, data }) {
  const [isHovered, setIsHovered] = useState(false);
  const chartData = useMemo(() => {
    const arr = Array.isArray(data) ? data : [];
    return arr
      .map((d) => ({
        label: String(d?.name ?? "—"),
        value: safeNumber(d?.value),
      }))
      .filter((d) => d.label && Number.isFinite(d.value));
  }, [data]);

  const total = useMemo(
    () => chartData.reduce((sum, d) => sum + safeNumber(d.value), 0),
    [chartData]
  );
  const safeTotal = total > 0 ? total : 1;

  const palette = ["#2bc9ff", "#a86dff", "#49e27d", "#3256ff", "#f0aa31", "#ff7ad9"];
  const chartColors = chartData.map((_, idx) => palette[idx % palette.length]);

  function getCenterLabel() {
    const t = String(title || "").toLowerCase();
    if (t.includes("alert")) return "Alerts";
    if (t.includes("job")) return "Jobs";
    if (t.includes("adapter") || t.includes("adaptation")) return "Devices";
    if (t.includes("device")) return "Devices";
    if (t.includes("online") || t.includes("offline")) return "Devices";
    return "Total";
  }

  const centerLabel = getCenterLabel();

  function TooltipContent({ active, payload }) {
    if (!active || !payload || !payload.length) return null;
    const entry = payload[0];
    const label = entry?.payload?.label ?? "—";
    const value = safeNumber(entry?.payload?.value ?? entry?.value);
    const percent = (value / safeTotal) * 100;

    return (
      <div className="analytics-card-tooltip">
        <div className="analytics-card-tooltip-title">{label}</div>
        <div className="analytics-card-tooltip-row">
          <span className="analytics-card-tooltip-key">Count</span>
          <span className="analytics-card-tooltip-value">{value}</span>
        </div>
        <div className="analytics-card-tooltip-row">
          <span className="analytics-card-tooltip-key">Percent</span>
          <span className="analytics-card-tooltip-value">{percent.toFixed(1)}%</span>
        </div>
      </div>
    );
  }

  return (
    <div
      className="bg-[#0b1b34] rounded-xl p-3 border border-blue-900/30 shadow-md flex flex-col items-center justify-center"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        height: "100%",
        position: "relative",
        zIndex: isHovered ? 10 : 2,
        pointerEvents: "auto",
        cursor: "pointer",
        transition: "all 300ms ease-in-out",
        transform: isHovered ? "translateY(-4px) scale(1.05)" : "none",
        background: isHovered ? "#13243a" : undefined,
        borderColor: isHovered ? "rgba(56, 189, 248, 0.55)" : undefined,
        boxShadow: isHovered
          ? "0 22px 40px rgba(0,0,0,0.35), 0 0 28px rgba(56,189,248,0.35)"
          : undefined,
      }}
    >
      <div className="flex flex-col items-center justify-center">
        <h3 className="text-sm font-semibold text-gray-300 mb-2 text-center">{title}</h3>

        <div
          style={{
            position: "relative",
            width: 118,
            height: 118,
            flex: "none",
          }}
          aria-hidden="true"
        >
          <ResponsiveContainer width={118} height={118}>
            <PieChart>
              <Tooltip content={TooltipContent} />
              <Pie
                data={chartData}
                dataKey="value"
                nameKey="label"
                innerRadius={34}
                outerRadius={52}
                paddingAngle={1.2}
                isAnimationActive
                animationDuration={900}
                animationBegin={0}
              >
                {chartData.map((entry, idx) => (
                  <Cell
                    key={`${entry.label}-${idx}`}
                    fill={chartColors[idx % chartColors.length]}
                  />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>

          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              pointerEvents: "none",
            }}
          >
            <div
              style={{
                color: "#eef3ff",
                fontSize: 16,
                fontWeight: 1000,
                lineHeight: 1,
              }}
            >
              {total}
            </div>
            <div
              style={{
                marginTop: 6,
                color: "#d1d5db",
                fontSize: 10,
                fontWeight: 800,
                lineHeight: 1.2,
              }}
            >
              {centerLabel}
            </div>
          </div>
        </div>

        <div className="mt-2 text-xs text-gray-400 space-y-0.5 text-center">
          {chartData.map((item, i) => (
            <div key={`${item.label}-${i}`}>
              {item.label}: {item.value}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

