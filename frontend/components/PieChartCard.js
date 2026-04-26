"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

function safeNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

export default function PieChartCard({ title, data, colors }) {
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setAnimate(true), 0);
    return () => clearTimeout(t);
  }, []);

  const normalizedData = useMemo(() => {
    const arr = Array.isArray(data) ? data : [];
    return arr
      .map((d) => ({
        label: String(d?.label ?? "—"),
        value: safeNumber(d?.value),
      }))
      .filter((d) => d.label && Number.isFinite(d.value));
  }, [data]);

  const total = useMemo(
    () => normalizedData.reduce((sum, d) => sum + safeNumber(d.value), 0),
    [normalizedData]
  );
  const safeTotal = total > 0 ? total : 1;

  const chartColors = Array.isArray(colors) && colors.length ? colors : ["#2bc9ff", "#a86dff", "#49e27d"];

  function renderTooltip({ active, payload }) {
    if (!active || !payload || !payload.length) return null;
    const entry = payload[0];
    const label = entry?.payload?.label ?? entry?.name ?? "—";
    const value = safeNumber(entry?.payload?.value ?? entry?.value);
    const percent = (value / safeTotal) * 100;

    return (
      <div className="analytics-tooltip">
        <div className="analytics-tooltip-title">{label}</div>
        <div className="analytics-tooltip-row">
          <span className="analytics-tooltip-key">Count</span>
          <span className="analytics-tooltip-value">{value}</span>
        </div>
        <div className="analytics-tooltip-row">
          <span className="analytics-tooltip-key">Percent</span>
          <span className="analytics-tooltip-value">{percent.toFixed(1)}%</span>
        </div>
      </div>
    );
  }

  function LegendContent({ payload }) {
    if (!payload || payload.length === 0) return null;
    return (
      <div className="analytics-legend">
        {payload.map((entry, idx) => {
          const label = entry?.payload?.label ?? entry?.value ?? "—";
          const value = safeNumber(entry?.payload?.value);
          const percent = (value / safeTotal) * 100;
          return (
            <div className="analytics-legend-row" key={`${label}-${idx}`}>
              <span
                className="analytics-legend-swatch"
                style={{ background: entry?.color || chartColors[idx % chartColors.length] }}
              />
              <span className="analytics-legend-label">{label}</span>
              <span className="analytics-legend-metric">
                {Math.round(percent)}% ({value})
              </span>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div
      className={`analytics-pie-card${animate ? " is-animated" : ""}`}
      style={{
        opacity: animate ? 1 : 0,
        transform: animate ? "translateY(0px)" : "translateY(6px)",
        transition: "opacity 520ms ease, transform 520ms ease",
      }}
    >
      <div className="analytics-pie-title">{title}</div>

      <div className="analytics-pie-chart-shell">
        <ResponsiveContainer width="100%" height={165}>
          <PieChart>
            <Tooltip content={renderTooltip} />
            <Pie
              data={normalizedData}
              dataKey="value"
              nameKey="label"
              innerRadius={48}
              outerRadius={78}
              stroke="#0a162b"
              strokeWidth={1}
              isAnimationActive
              animationDuration={900}
              animationBegin={0}
              labelLine={false}
            >
              {normalizedData.map((entry, idx) => (
                <Cell
                  key={`${entry.label}-${idx}`}
                  fill={chartColors[idx % chartColors.length]}
                />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>

      <Legend verticalAlign="bottom" align="center" content={LegendContent} />
    </div>
  );
}

