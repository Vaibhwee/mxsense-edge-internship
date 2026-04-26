"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import DeviceManagementActionForm from "./DeviceManagementActionForm";
import MainLayout from "./layout/MainLayout";
import ImagePanel from "./ImagePanel";
import AnalyticsOverview from "./AnalyticsOverview";
import EdgeAIHealthModule from "./EdgeAIHealthModule";
import DeviceHealthModule from "./DeviceHealthModule";
const subtabPillClass = "ui-button ui-button-pill subtab-pill";
const ALLOWED_DEVICE_UIDS = new Set(["device_01", "device_02", "device_03", "device_04", "device_05"]);

function toSectionId(label) {
  return label
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function getPanelContent(activeModule, selectedSubTab) {
  const activeTab =
    selectedSubTab || activeModule.focusTab || activeModule.subTabs?.[0] || "Overview";
  const isPrimaryTab = activeTab === activeModule.focusTab;
  const panelOverride = activeModule.subTabPanels?.[activeTab];
  const isDeviceManagement = activeModule.slug === "device-management";

  return {
    tab: activeTab,
    title: panelOverride?.title || (isPrimaryTab ? activeModule.panelTitle : `${activeTab} section`),
    summary: isDeviceManagement
      ? activeModule.summary
      : isPrimaryTab
        ? activeModule.summary
        : `${activeModule.summary} You are viewing the ${activeTab} section.`,
    bullets: panelOverride?.bullets || activeModule.panelBullets,
  };
}

const dataDashboardDevices = [
  {
    name: "device_01",
    location: "Factory-Line-A",
    timestamp: "23/3/2026, 12:00:00 PM",
    metrics: [
      ["SoC temp", "44 C"],
      ["GPU load", "55%"],
      ["RAM", "3500MB"],
      ["Fan", "2100rpm"],
    ],
  },
  {
    name: "device_02",
    location: "Factory-Line-A",
    timestamp: "23/3/2026, 2:40:20 PM",
    metrics: [
      ["SoC temp", "41.2 C"],
      ["GPU load", "52%"],
      ["RAM", "3980MB"],
      ["Fan", "2350rpm"],
    ],
  },
  {
    name: "device_03",
    location: "Factory-Line-B",
    timestamp: "23/3/2026, 2:42:10 PM",
    metrics: [
      ["SoC temp", "47 C"],
      ["GPU load", "58%"],
      ["RAM", "4300MB"],
      ["Fan", "2550rpm"],
    ],
  },
  {
    name: "device_04",
    location: "Factory-Line-B",
    timestamp: "23/3/2026, 2:44:55 PM",
    metrics: [
      ["SoC temp", "39.8 C"],
      ["GPU load", "49%"],
      ["RAM", "3720MB"],
      ["Fan", "2050rpm"],
    ],
  },
  {
    name: "device_05",
    location: "Lab-Test",
    timestamp: "23/3/2026, 2:46:30 PM",
    metrics: [
      ["SoC temp", "43.3 C"],
      ["GPU load", "54.1%"],
      ["RAM", "4020MB"],
      ["Fan", "2200rpm"],
    ],
  },
];

const dataMetricTabs = [
  "ENV",
  "VOC",
  "Gas",
  "PM",
  "System",
  "Flow",
];

const GAS_SENSOR_LABELS = {
  CH2_ZE07_CO: "CO",
  CH2_ME3_NH3: "NH3",
  CH2_ME3_SO2: "SO2",
  CH2_ME3_H2S: "H2S",
  CH2_ME3_NO2: "NO2",
};

const dataChartSeriesByMetric = {
  ENV: [
    { color: "#f0aa31", values: [1000, 940, 1020] },
    { color: "#4bb5ff", values: [72, 74, 76] },
    { color: "#a86dff", values: [42, 44, 46] },
  ],
  VOC: [
    { color: "#f0aa31", values: [420, 448, 432] },
    { color: "#4bb5ff", values: [56, 52, 58] },
    { color: "#a86dff", values: [18, 20, 19] },
  ],
  Gas: [
    { color: "#f0aa31", values: [650, 670, 640] },
    { color: "#4bb5ff", values: [95, 102, 98] },
    { color: "#a86dff", values: [30, 28, 34] },
  ],
  PM: [
    { color: "#f0aa31", values: [140, 182, 160] },
    { color: "#4bb5ff", values: [26, 29, 25] },
    { color: "#a86dff", values: [10, 11, 9] },
  ],
  System: [
    { color: "#f0aa31", values: [780, 810, 765] },
    { color: "#4bb5ff", values: [68, 71, 73] },
    { color: "#a86dff", values: [39, 37, 41] },
  ],
  Flow: [
    { color: "#f0aa31", values: [510, 540, 530] },
    { color: "#4bb5ff", values: [48, 52, 50] },
    { color: "#a86dff", values: [21, 23, 20] },
  ],
  Force: [
    { color: "#f0aa31", values: [330, 360, 342] },
    { color: "#4bb5ff", values: [44, 49, 46] },
    { color: "#a86dff", values: [17, 19, 18] },
  ],
  Acoustic: [
    { color: "#f0aa31", values: [270, 252, 288] },
    { color: "#4bb5ff", values: [62, 58, 64] },
    { color: "#a86dff", values: [23, 22, 24] },
  ],
  Distance: [
    { color: "#f0aa31", values: [920, 905, 940] },
    { color: "#4bb5ff", values: [35, 33, 37] },
    { color: "#a86dff", values: [14, 15, 13] },
  ],
};

const dataChartConfig = {
  width: 760,
  height: 220,
  left: 56,
  right: 18,
  top: 18,
  bottom: 30,
  maxValue: 1200,
};

function getChartY(value, maxValue) {
  const { height, top, bottom } = dataChartConfig;
  const plotHeight = height - top - bottom;
  const safeMax = Math.max(Number(maxValue) || 1, 1);
  return top + plotHeight - (Number(value || 0) / safeMax) * plotHeight;
}

function getChartX(index, pointsCount) {
  const { width, left, right } = dataChartConfig;
  const plotWidth = width - left - right;
  const steps = Math.max(pointsCount - 1, 1);
  return left + (plotWidth * index) / steps;
}

function buildLinePoints(values, maxValue) {
  // This helper is used only when we know the pointsCount externally,
  // so we keep signature aligned with old code paths by defaulting to values.length.
  return values
    .map((value, index) => {
      const n = Number(value);
      if (!Number.isFinite(n)) return null;
      return `${getChartX(index, values.length)},${getChartY(n, maxValue)}`;
    })
    .filter(Boolean)
    .join(" ");
}

function CustomChartTooltip({
  x,
  y,
  maxX,
  title,
  rows,
}) {
  if (!rows || rows.length === 0) return null;

  const tooltipWidth = 270;
  const headerHeight = 20;
  const rowHeight = 18;
  const paddingX = 12;
  const paddingY = 10;
  const contentRows = rows.filter((row) => row && row.value !== undefined && row.value !== null);

  if (contentRows.length === 0) return null;

  const tooltipHeight = paddingY * 2 + headerHeight + contentRows.length * rowHeight;
  const safeX = Math.max(dataChartConfig.left + 8, Math.min(x + 12, maxX - tooltipWidth));
  const safeY = Math.max(dataChartConfig.top + 8, y);

  return (
    <g style={{ pointerEvents: "none" }}>
      <rect
        fill="#0f172a"
        height={tooltipHeight}
        opacity="0.97"
        rx="10"
        ry="10"
        stroke="rgba(112, 151, 255, 0.28)"
        width={tooltipWidth}
        x={safeX}
        y={safeY}
      />
      <text
        fill="#e6edf7"
        fontSize="12"
        fontWeight="700"
        x={safeX + paddingX}
        y={safeY + paddingY + 12}
      >
        {title || "—"}
      </text>
      {contentRows.map((row, idx) => {
        const rowY = safeY + paddingY + headerHeight + (idx + 1) * rowHeight - 2;
        return (
          <g key={`${row.label}-${idx}`}>
            <circle cx={safeX + paddingX + 4} cy={rowY - 4} fill={row.color} r="4" />
            <text fill={row.color} fontSize="12" x={safeX + paddingX + 14} y={rowY}>
              {`${row.label}: ${row.value}`}
            </text>
          </g>
        );
      })}
    </g>
  );
}

function DataSectionDashboard() {
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [selectedMetric, setSelectedMetric] = useState("ENV");
  const [hoveredPointIndex, setHoveredPointIndex] = useState(null);
  const [zoomLevel, setZoomLevel] = useState(1); // 1 = full range, higher = zoom in
  const [yZoomLevel, setYZoomLevel] = useState(1); // 1 = full Y range, higher = zoom in (may clip)
  const [isConnected, setIsConnected] = useState(false);
  const [hasData, setHasData] = useState(false);
  const [sectionChartRows, setSectionChartRows] = useState([]);
  const [apiDevices, setApiDevices] = useState([]);
  const [apiReadings, setApiReadings] = useState([]);
  const [apiLoaded, setApiLoaded] = useState(false);
  const [apiFailed, setApiFailed] = useState(false);
  const [refreshNonce, setRefreshNonce] = useState(0);
  const wsRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const reconnectDelayMs = 4000;

  const apiRoot = process.env.NEXT_PUBLIC_PLATFORM_API_ROOT || "http://127.0.0.1:8000/api";

  useEffect(() => {
    let active = true;

    function toArray(payload) {
      if (Array.isArray(payload)) return payload;
      if (payload && Array.isArray(payload.results)) return payload.results;
      return [];
    }

    async function loadData() {
      try {
        const [devicesRes, readingsRes] = await Promise.all([
          fetch(`${apiRoot}/api-gateway/devices/`, { cache: "no-store" }),
          fetch(`${apiRoot}/api-gateway/data/`, { cache: "no-store" }),
        ]);

        if (!devicesRes.ok || !readingsRes.ok) {
          if (!active) return;
          setApiFailed(true);
          setApiLoaded(true);
          return;
        }

        const [devicesPayload, readingsPayload] = await Promise.all([
          devicesRes.json(),
          readingsRes.json(),
        ]);
        console.log("[API] /devices and /data response received.", {
          devicesType: Array.isArray(devicesPayload) ? "array" : typeof devicesPayload,
          readingsType: Array.isArray(readingsPayload) ? "array" : typeof readingsPayload,
        });

        if (!active) return;
        setApiDevices(toArray(devicesPayload));
        setApiReadings(toArray(readingsPayload));
        setApiFailed(false);
        setApiLoaded(true);
      } catch {
        // Keep fallback mock data only when backend/RDS is unreachable.
        if (!active) return;
        console.error("[API] Failed to load devices/readings from backend.");
        setApiFailed(true);
        setApiLoaded(true);
      }
    }

    loadData();
    const intervalId = setInterval(loadData, 2000);
    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, [apiRoot, refreshNonce]);

  useEffect(() => {
    let isMounted = true;

    function clearReconnectTimer() {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    }

    function getWsUrl() {
      // Do not auto-guess /ws; this backend currently has no websocket route.
      // Enable WS only when explicitly configured.
      return process.env.NEXT_PUBLIC_WS_URL || null;
    }

    function connect() {
      clearReconnectTimer();
      const wsUrl = getWsUrl();
      if (!wsUrl) {
        console.info("[WS] Skipped: NEXT_PUBLIC_WS_URL is not configured.");
        setIsConnected(false);
        setHasData(false);
        return;
      }

      try {
        const socket = new WebSocket(wsUrl);
        wsRef.current = socket;

        socket.onopen = () => {
          if (!isMounted) return;
          console.log(`[WS] Connected: ${wsUrl}`);
          setIsConnected(true);
          setHasData(false);
        };

        socket.onmessage = (event) => {
          if (!isMounted) return;
          try {
            // Accept heartbeat/empty frames without marking disconnected.
            const payload = event.data ? JSON.parse(event.data) : null;
            const deviceId = payload?.device_id || null;
            const matchedDevice = apiDevices.find((d) => String(d?.device_id || d?.id) === String(deviceId));
            const enrichedPayload = payload && typeof payload === "object"
              ? {
                  ...payload,
                  device_id: payload.device_id || matchedDevice?.device_id || matchedDevice?.id || null,
                  device_uid:
                    payload.device_uid ||
                    matchedDevice?.device_uid ||
                    matchedDevice?.external_id ||
                    null,
                }
              : payload;
            console.log("[WS] Message received.", enrichedPayload);
          } catch {
            console.log("[WS] Message received (non-JSON).");
          }
          setHasData(true);
          // Trigger fresh REST fetch so UI reflects latest DB state.
          setRefreshNonce((n) => n + 1);
        };

        socket.onerror = () => {
          if (!isMounted) return;
          console.error("[WS] Connection error.");
          setIsConnected(false);
        };

        socket.onclose = () => {
          if (!isMounted) return;
          console.warn("[WS] Connection closed. Retrying...");
          setIsConnected(false);
          reconnectTimerRef.current = setTimeout(connect, reconnectDelayMs);
        };
      } catch {
        console.error("[WS] Failed to initialize WebSocket client.");
        setIsConnected(false);
        reconnectTimerRef.current = setTimeout(connect, reconnectDelayMs);
      }
    }

    connect();

    return () => {
      isMounted = false;
      clearReconnectTimer();
      setIsConnected(false);
      setHasData(false);
      if (wsRef.current) {
        wsRef.current.onopen = null;
        wsRef.current.onmessage = null;
        wsRef.current.onerror = null;
        wsRef.current.onclose = null;
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [apiRoot, apiDevices]);

  function metricToSensorType(metric) {
    const map = {
      ENV: "env",
      VOC: "voc",
      Gas: "gas",
      PM: "pm",
      System: "system",
      Flow: "flow",
      Force: "force",
      Acoustic: "acoustic",
      Distance: "distance",
    };
    return map[metric] || String(metric || "").toLowerCase();
  }

  function isSensorTypeMatch(sensorType, wantedType) {
    const actual = String(sensorType || "").toLowerCase().trim();
    const wanted = String(wantedType || "").toLowerCase().trim();
    if (!actual || !wanted) return false;
    // Backend often stores fan metrics under "system"; allow Flow tab to consume those rows.
    if (wanted === "flow" && actual === "system") return true;
    // Accept both normalized and raw table-like names (e.g. "gas", "gas_data").
    return actual === wanted || actual.includes(wanted) || wanted.includes(actual);
  }

  function isNumericLike(value) {
    if (typeof value === "number") return Number.isFinite(value);
    if (typeof value === "string" && value.trim() !== "") return Number.isFinite(Number(value));
    return false;
  }

  function toNumber(value) {
    if (typeof value === "number") return value;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }

  function formatMetricLabel(rawKey) {
    const key = String(rawKey || "").trim();
    const known = {
      5: "SoC Temp",
      6: "GPU Load",
      19: "RAM",
      20: "Fan Speed",
      mq135_air_quality: "MQ135 Air Quality",
      mq136_sulfur_level: "MQ136 Sulfur Level",
      tgs2600_contamination: "TGS2600 Contamination",
      ethylene_sensor_value: "Ethylene Sensor",
      sgp41_voc_index: "SGP41 VOC Index",
      sgp41_nox_index: "SGP41 NOx Index",
      zmod4410_voc_concentration: "ZMOD4410 VOC",
      bme688_gas_resistance: "BME688 Gas Resistance",
      tgs2602_odor_level: "TGS2602 Odor Level",
      soc_temp: "SoC Temp",
      gpu_load: "GPU Load",
      ram: "RAM",
      fan: "Fan",
      ram_mb: "RAM (MB)",
      fan_rpm: "Fan (RPM)",
      cpu_temp_c: "CPU Temp",
      temperature: "Temperature",
      humidity: "Humidity",
      pressure: "Pressure",
      voc: "VOC",
      pm1: "PM1",
      pm25: "PM2.5",
      pm10: "PM10",
      pms7003_pm1: "PMS7003 PM1",
      pms7003_pm2_5: "PMS7003 PM2.5",
      pms7003_pm10: "PMS7003 PM10",
      sps30_pm1: "SPS30 PM1",
      sps30_pm2_5: "SPS30 PM2.5",
      sps30_pm10: "SPS30 PM10",
      co2: "CO2",
    };
    if (known[key]) return known[key];
    // Numeric channel keys from some raw tables (e.g., "5", "6", "19", "20")
    if (/^\d+$/.test(key)) return `Channel ${key}`;
    return key
      .replace(/_/g, " ")
      .replace(/\s+/g, " ")
      .trim()
      .replace(/\b\w/g, (ch) => ch.toUpperCase());
  }

  function formatMetricValue(value) {
    if (typeof value === "number" && Number.isFinite(value)) {
      // Keep dashboard compact; avoid excessive precision.
      return Number.isInteger(value) ? String(value) : value.toFixed(2);
    }
    if (typeof value === "string") return value;
    return String(value ?? "—");
  }

  function pickCardMetricsFromPayload(payload) {
    const entries = Object.entries(payload || {}).filter(([, v]) => isNumericLike(v));
    const priorityKeys = ["soc_temp", "gpu_load", "ram", "fan"];
    const lookup = new Map(entries.map(([k, v]) => [String(k).toLowerCase(), [k, v]]));
    const usedKeys = new Set();
    const ordered = [];
    priorityKeys.forEach((pk) => {
      const hit = lookup.get(pk);
      if (hit) {
        ordered.push(hit);
        usedKeys.add(pk);
      }
    });
    const semantic = entries.filter(
      ([k]) => !/^\d+$/.test(String(k)) && !usedKeys.has(String(k).toLowerCase())
    );
    semantic.forEach((e) => ordered.push(e));
    if (ordered.length === 0) {
      entries.forEach((e) => ordered.push(e));
    }
    return ordered.slice(0, 4).map(([k, v]) => [formatMetricLabel(k), formatMetricValue(v)]);
  }

  function formatTimeLabel(ts) {
    if (!ts) return "—";
    const d = new Date(ts);
    if (Number.isNaN(d.getTime())) return "—";
    return d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit", second: "2-digit" });
  }

  function formatTooltipTimestamp(ts, fallbackLabel) {
    if (!ts) return fallbackLabel || "—";
    const d = new Date(ts);
    if (Number.isNaN(d.getTime())) return fallbackLabel || "—";
    return d.toLocaleString();
  }

  function formatGasSensorLabel(sensorCode) {
    const code = String(sensorCode || "").trim();
    if (!code) return "Gas";
    if (GAS_SENSOR_LABELS[code]) return GAS_SENSOR_LABELS[code];
    const trimmed = code.split("_").slice(2).join("_");
    if (trimmed) return trimmed;
    const fallback = code.split("_").slice(1).join("_");
    return fallback || code;
  }

  function pickGasValueFromRow(row) {
    if (!row || typeof row !== "object") return null;
    const sensorCode = String(row?.sensor_code || "").toUpperCase().trim();
    const preferredGasKeys = [
      sensorCode.startsWith("CH2") ? "gas_ppm" : null,
      "value",
      "gas_ppm",
      "voc_index",
      "gas",
      "ppm",
      "concentration",
      "ethylene_sensor_value",
      "mq135_air_quality",
      "mq136_sulfur_level",
      "tgs2600_contamination",
      "bme688_gas_resistance",
      "tgs2602_odor_level",
      "zmod4410_voc_concentration",
    ].filter(Boolean);
    for (const key of preferredGasKeys) {
      const n = toNumber(row?.[key]);
      if (n !== null) return n;
    }

    const dynamicKeys = Object.keys(row).filter(
      (key) =>
        key !== "timestamp" &&
        key !== "sensor_code" &&
        key !== "sensor_name" &&
        key !== "confidence" &&
        isNumericLike(row[key])
    );
    for (const key of dynamicKeys) {
      const n = toNumber(row?.[key]);
      if (n !== null) return n;
    }
    return null;
  }

  function pickSectionValueBySensor(row, metricUpper) {
    if (!row || typeof row !== "object") return null;
    const code = String(row?.sensor_code || "").toUpperCase().trim();

    if (metricUpper === "GAS" && code.startsWith("CH2")) {
      return toNumber(row?.gas_ppm) ?? toNumber(row?.value);
    }
    if (metricUpper === "VOC" && code.startsWith("CH1")) {
      return toNumber(row?.voc_index) ?? toNumber(row?.value);
    }
    if (metricUpper === "ENV" && code.startsWith("CH0")) {
      return (
        toNumber(row?.temperature_c) ??
        toNumber(row?.humidity_pct) ??
        toNumber(row?.pressure_pa) ??
        toNumber(row?.value)
      );
    }
    if (metricUpper === "PM" && code.startsWith("CH4")) {
      return (
        toNumber(row?.pm1) ??
        toNumber(row?.pm2_5) ??
        toNumber(row?.pm25) ??
        toNumber(row?.pm10) ??
        toNumber(row?.value)
      );
    }
    return toNumber(row?.value);
  }

  function isFanMetricKey(key) {
    const k = String(key || "").toLowerCase();
    return k.includes("fan") || k.includes("rpm");
  }

  function isGasMetricKey(key) {
    const k = String(key || "").toLowerCase();
    return (
      k === "gas" ||
      k.includes("gas") ||
      k.includes("mq") ||
      k.includes("tgs") ||
      k.includes("ethylene") ||
      k.includes("sulfur")
    );
  }

  const readingsByDevice = new Map();
  apiReadings.forEach((reading) => {
    const keys = [reading.device_uid, reading.device_id, reading.device]
      .map((v) => String(v || "").trim())
      .filter(Boolean);
    keys.forEach((key) => {
      if (!readingsByDevice.has(key)) readingsByDevice.set(key, []);
      readingsByDevice.get(key).push(reading);
    });
  });

  function getDeviceReadings(deviceLike) {
    const keys = [
      deviceLike?.device_id,
      deviceLike?.device_uid,
      deviceLike?.id,
      deviceLike?.external_id,
      deviceLike?.name,
    ]
      .map((v) => String(v || "").trim())
      .filter(Boolean);

    if (keys.length === 0) return [];

    const merged = [];
    const seen = new Set();
    keys.forEach((key) => {
      const rows = readingsByDevice.get(key) || [];
      rows.forEach((row, idx) => {
        const rid = String(row?.id || `${key}-${idx}`);
        if (seen.has(rid)) return;
        seen.add(rid);
        merged.push(row);
      });
    });
    return merged;
  }

  const shouldUseMockDevices = apiFailed;
  const effectiveDevices = shouldUseMockDevices ? dataDashboardDevices : apiDevices;

  const normalizedDevices = effectiveDevices.map((device) => {
    if (!shouldUseMockDevices) {
      const deviceId = String(device.device_id || device.id || "").trim();
      const deviceUid = String(device.device_uid || device.external_id || device.name || deviceId).trim();
      const perDeviceReadings = getDeviceReadings(device).slice();
      const wantedType = metricToSensorType(selectedMetric);
      const metricScoped = perDeviceReadings.filter(
        (r) => isSensorTypeMatch(r.sensor_type, wantedType)
      );
      const scopedReadings = (metricScoped.length > 0 ? metricScoped : perDeviceReadings).sort((a, b) => {
        const aTs = new Date(a.source_timestamp || a.created_at || 0).getTime();
        const bTs = new Date(b.source_timestamp || b.created_at || 0).getTime();
        return bTs - aTs;
      });
      const latestReading = scopedReadings[0];
      const latestPayload = latestReading?.payload || {};
      const healthPayload = device.health_payload || {};
      const metrics = pickCardMetricsFromPayload(
        Object.keys(healthPayload).length > 0 ? healthPayload : latestPayload
      );

      return {
        id: deviceId,
        device_id: deviceId,
        device_uid: deviceUid,
        name: deviceUid,
        location: String(device.location || device.assigned_line || "N/A"),
        timestamp: formatTimeLabel(device.last_seen_at || latestReading?.source_timestamp || device.updated_at),
        metrics:
          metrics.length > 0
            ? metrics
            : [
                ["SoC temp", "—"],
                ["GPU load", "—"],
                ["RAM", "—"],
                ["Fan", "—"],
              ],
      };
    }

    return {
      ...device,
      name: String(device.name || "").trim(),
    };
  });

  const selectedNormalized = selectedDevice ? String(selectedDevice).trim() : null;

  // Single source of truth: one device per normalized name.
  const uniqueDevices = Array.from(
    new Map(normalizedDevices.map((d) => [d.device_uid || d.name, d])).values()
  );

  const displayDevices = shouldUseMockDevices
    ? uniqueDevices
    : uniqueDevices.filter((device) => ALLOWED_DEVICE_UIDS.has(String(device.device_uid || "").trim()));

  const devices = displayDevices.map((d) => d.device_uid || d.name);

  const filteredDevices = displayDevices.filter(
    (device) => !selectedNormalized || selectedNormalized === (device.device_uid || device.name)
  );
  const selectedDeviceObj =
    displayDevices.find((d) => (d.device_uid || d.name) === selectedNormalized) || null;
  const selectedDeviceExternalId = selectedDeviceObj?.device_uid || null;
  const selectedMetricSensorType = metricToSensorType(selectedMetric);

  useEffect(() => {
    let active = true;
    async function loadSectionRows() {
      if (shouldUseMockDevices || !selectedDeviceExternalId || !selectedMetric) {
        setSectionChartRows([]);
        return;
      }
      try {
        const fetchRowsForSection = async (sectionName) => {
          const url = `${apiRoot}/api-gateway/data/section/?section=${encodeURIComponent(sectionName)}&device_id=${encodeURIComponent(selectedDeviceExternalId)}&limit=50`;
          const res = await fetch(url, { cache: "no-store" });
          if (!res.ok) return null;
          const payload = await res.json();
          return Array.isArray(payload?.results) ? payload.results : [];
        };

        let rows = await fetchRowsForSection(selectedMetric);
        if (rows === null) {
          if (!active) return;
          setSectionChartRows([]);
          return;
        }

        // Fallback: Flow tab can read System rows to extract fan telemetry.
        if (String(selectedMetric).toUpperCase() === "FLOW" && rows.length === 0) {
          const systemRows = await fetchRowsForSection("System");
          if (Array.isArray(systemRows) && systemRows.length > 0) rows = systemRows;
        }

        if (!active) return;
        const metricUpper = String(selectedMetric).toUpperCase();
        if (metricUpper === "VOC" || metricUpper === "PM") {
          console.log(`[${metricUpper}] section API rows`, rows);
        }
        if (metricUpper === "GAS") {
          console.log("[GAS] section API rows", rows.slice(0, 5));
        }
        setSectionChartRows(rows);
      } catch (err) {
        console.error(`[${selectedMetric}] section API fetch failed`, err);
        if (!active) return;
        setSectionChartRows([]);
      }
    }
    loadSectionRows();
    const intervalId = setInterval(loadSectionRows, 2000);
    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, [apiRoot, selectedMetric, selectedDeviceExternalId, shouldUseMockDevices]);

  useEffect(() => {
    setZoomLevel(1);
    setYZoomLevel(1);
    setHoveredPointIndex(null);
  }, [selectedMetric, selectedDeviceExternalId, shouldUseMockDevices]);

  const selectedDeviceReadings = selectedDeviceObj
    ? getDeviceReadings(selectedDeviceObj)
        .sort((a, b) => {
          const aTs = new Date(a.source_timestamp || a.created_at || 0).getTime();
          const bTs = new Date(b.source_timestamp || b.created_at || 0).getTime();
          return aTs - bTs;
        })
    : [];

  const selectedMetricReadings = selectedDeviceReadings.filter(
    (r) => isSensorTypeMatch(r.sensor_type, selectedMetricSensorType)
  );

  const selectedMetricUpper = String(selectedMetric || "").toUpperCase();
  const gasFallbackReadings =
    selectedMetricUpper === "GAS" && selectedMetricReadings.length === 0
      ? selectedDeviceReadings.filter((r) =>
          Object.keys(r?.payload || {}).some((key) => isGasMetricKey(key))
        )
      : [];

  // For real backend data, chart must reflect only the selected metric dataset.
  // Do not fallback to unrelated sensor rows (prevents random channel lines).
  const effectiveMetricReadings =
    gasFallbackReadings.length > 0 ? gasFallbackReadings : selectedMetricReadings;
  const chartReadings = shouldUseMockDevices
    ? effectiveMetricReadings.slice(-8)
    : effectiveMetricReadings.slice(-8);

  const preferredPayloadKeysByMetric = {
    Gas: [
      "ethylene_sensor_value",
      "mq135_air_quality",
      "mq136_sulfur_level",
      "tgs2600_contamination",
    ],
    VOC: [
      "sgp41_voc_index",
      "sgp41_nox_index",
      "zmod4410_voc_concentration",
      "bme688_gas_resistance",
      "tgs2602_odor_level",
    ],
    PM: [
      "pms7003_pm1",
      "pms7003_pm2_5",
      "pms7003_pm10",
      "sps30_pm1",
      "sps30_pm2_5",
      "sps30_pm10",
      "pm1",
      "pm25",
      "pm10",
      "particle_count",
    ],
    System: ["soc_temp", "gpu_load", "ram_mb"],
    SYSTEM: ["soc_temp", "gpu_load", "ram_mb"],
    Flow: ["fan_rpm", "fan", "flow_rate", "airflow", "flow"],
    FLOW: ["fan_rpm", "fan", "flow_rate", "airflow", "flow"],
  };

  let activeChartSeries = shouldUseMockDevices
    ? dataChartSeriesByMetric[selectedMetric] || dataChartSeriesByMetric.ENV
    : [];
  let chartLabels = shouldUseMockDevices ? buildChartLabels(selectedDevice) : [];
  let chartTimestampValues = chartLabels;

  const usingSectionRows = Array.isArray(sectionChartRows) && sectionChartRows.length > 0;

  if (usingSectionRows) {
    const metricUpper = String(selectedMetric || "").toUpperCase();
    if (metricUpper === "GAS") {
      const sortedRows = sectionChartRows
        .filter((row) => {
          const code = String(row?.sensor_code || "").trim();
          return row?.timestamp && Boolean(GAS_SENSOR_LABELS[code]);
        })
        .slice()
        .sort((a, b) => {
          const aTs = new Date(a?.timestamp || 0).getTime();
          const bTs = new Date(b?.timestamp || 0).getTime();
          return aTs - bTs;
        });
      const timestamps = Array.from(new Set(sortedRows.map((row) => row.timestamp)));
      const grouped = new Map();
      sortedRows.forEach((row) => {
        const code = String(row?.sensor_code || "GAS").trim() || "GAS";
        if (!grouped.has(code)) grouped.set(code, new Map());
        const n = pickGasValueFromRow(row);
        console.log("[GAS] parsed value", { sensor_code: code, value: n, timestamp: row?.timestamp });
        if (n !== null) grouped.get(code).set(row.timestamp, n);
      });
      const chartColors = ["#a86dff", "#49e27d", "#f0aa31", "#2bc9ff", "#ff7ad9", "#ff6b6b", "#7aa2ff"];
      activeChartSeries = Array.from(grouped.entries()).map(([code, byTs], idx) => ({
        key: code,
        label: formatGasSensorLabel(code),
        color: chartColors[idx % chartColors.length],
        values: timestamps.map((ts) => {
          const v = byTs.get(ts);
          return typeof v === "number" && Number.isFinite(v) ? v : null;
        }),
      }));
      chartLabels = timestamps.map((ts) => formatTimeLabel(ts));
      chartTimestampValues = timestamps.slice();
    } else {
    const availableKeys = Array.from(
      new Set(
        sectionChartRows.flatMap((row) =>
          Object.entries(row || {})
            .filter(([k, v]) => k !== "timestamp" && isNumericLike(v))
            .map(([k]) => k)
        )
      )
    );
    const preferredKeys = (preferredPayloadKeysByMetric[selectedMetric] || []).filter((k) =>
      availableKeys.includes(k)
    );
    const fallbackKeys = availableKeys.filter((k) => {
      if (preferredKeys.includes(k)) return false;
      if (String(selectedMetric).toUpperCase() === "SYSTEM" && isFanMetricKey(k)) return false;
      if (String(selectedMetric).toUpperCase() === "FLOW" && !isFanMetricKey(k)) return false;
      if (String(selectedMetric).toUpperCase() === "GAS" && !isGasMetricKey(k)) return false;
      return true;
    });
    const candidateKeys = [...preferredKeys, ...fallbackKeys].slice(0, 5);

    if (candidateKeys.length > 0) {
      const chartColors = ["#a86dff", "#49e27d", "#f0aa31", "#2bc9ff", "#ff7ad9"];
      activeChartSeries = candidateKeys.map((key, idx) => ({
        key,
        label: formatMetricLabel(key),
        color: chartColors[idx % chartColors.length],
        values: sectionChartRows.map((row) => {
          const metricUpper = String(selectedMetric || "").toUpperCase();
          const mapped = pickSectionValueBySensor(row, metricUpper);
          if (mapped !== null && key === "value") return mapped;
          const n = toNumber(row?.[key]);
          return n === null ? 0 : n;
        }),
      }));
      chartLabels = sectionChartRows.map((row) => formatTimeLabel(row?.timestamp));
      chartTimestampValues = sectionChartRows.map((row) => row?.timestamp || null);
    }
    }
  } else if (chartReadings.length > 0) {
    const availableKeys = Array.from(
      new Set(
        chartReadings.flatMap((r) =>
          Object.entries(r.payload || {})
            .filter(([, v]) => isNumericLike(v))
            .map(([k]) => k)
        )
      )
    );

    const preferredKeys = (preferredPayloadKeysByMetric[selectedMetric] || []).filter((k) =>
      availableKeys.includes(k)
    );
    const fallbackKeys = availableKeys.filter((k) => {
      if (preferredKeys.includes(k)) return false;
      if (String(selectedMetric).toUpperCase() === "SYSTEM" && isFanMetricKey(k)) return false;
      if (String(selectedMetric).toUpperCase() === "FLOW" && !isFanMetricKey(k)) return false;
      if (String(selectedMetric).toUpperCase() === "GAS" && !isGasMetricKey(k)) return false;
      return true;
    });
    const candidateKeys = [...preferredKeys, ...fallbackKeys].slice(0, 5);

    if (candidateKeys.length > 0) {
      const chartColors = ["#a86dff", "#49e27d", "#f0aa31", "#2bc9ff", "#ff7ad9"];
      activeChartSeries = candidateKeys.map((key, idx) => ({
        key,
        label: formatMetricLabel(key),
        color: chartColors[idx % chartColors.length],
        values: chartReadings.map((r) => {
          const n = toNumber((r.payload || {})[key]);
          return n === null ? 0 : n;
        }),
      }));
      chartLabels = chartReadings.map((r) => formatTimeLabel(r.source_timestamp || r.created_at));
      chartTimestampValues = chartReadings.map((r) => r.source_timestamp || r.created_at || null);
    }
  }

  // Zoom: show only the latest window to keep "current" readings in view.
  const fullPointsCount = activeChartSeries?.[0]?.values?.length || 0;
  const zoom = Math.max(1, Number(zoomLevel) || 1);
  if (fullPointsCount > 0 && zoom > 1) {
    const visibleCount = Math.max(3, Math.floor(fullPointsCount / zoom));
    const endIndex = fullPointsCount;
    const startIndex = Math.max(0, endIndex - visibleCount);

    activeChartSeries = activeChartSeries.map((s) => ({
      ...s,
      values: (s.values || []).slice(startIndex, endIndex),
    }));
    chartLabels = chartLabels.slice(startIndex, endIndex);
    chartTimestampValues = chartTimestampValues.slice(startIndex, endIndex);
  }

  const pointsCount = activeChartSeries?.[0]?.values?.length || 0;
  const chartTargetLabel = selectedDevice || "ALL DEVICES";
  const flatValues = activeChartSeries.flatMap((s) => s.values || []).map((v) => Number(v || 0));
  const rawMax = Math.max(...flatValues, 1);
  const baseChartMaxValue = Math.ceil(rawMax * 1.1);
  const yZoom = Math.max(1, Number(yZoomLevel) || 1);
  const chartMaxValue = Math.max(1, baseChartMaxValue / yZoom);
  const yAxisLabels = [
    chartMaxValue,
    Math.round(chartMaxValue * 0.75),
    Math.round(chartMaxValue * 0.5),
    Math.round(chartMaxValue * 0.25),
    0,
  ];
  const safeHoveredPointIndex =
    hoveredPointIndex === null || hoveredPointIndex >= pointsCount ? null : hoveredPointIndex;

  const hoverX = safeHoveredPointIndex !== null
    ? getChartX(safeHoveredPointIndex, pointsCount)
    : null;

  const hoverLabel = safeHoveredPointIndex !== null ? chartLabels[safeHoveredPointIndex] : null;
  const hoverTimestampRaw =
    safeHoveredPointIndex !== null ? chartTimestampValues[safeHoveredPointIndex] : null;

  const hoverSeriesRows = safeHoveredPointIndex !== null
    ? activeChartSeries.map((series) => ({
        color: series.color,
        label: series.label || series.key || "Metric",
        value: formatMetricValue(series.values?.[safeHoveredPointIndex]),
      }))
        .filter((row) => row.value !== undefined && row.value !== null && row.value !== "—")
    : [];

  function shouldShowXAxisLabel(index, total) {
    if (total <= 8) return true;
    const step = Math.max(Math.floor(total / 8), 1);
    return index % step === 0 || index === total - 1;
  }

  function parseDeviceTimestamp(ts) {
    // Expected format from your dummy data:
    // "23/3/2026, 12:00:00 PM"
    if (!ts || typeof ts !== "string") return null;
    const parts = ts.split(",");
    if (parts.length < 2) return null;
    const [d, t] = parts.map((x) => x.trim());

    const dateParts = d.split("/");
    if (dateParts.length !== 3) return null;
    const day = Number(dateParts[0]);
    const month = Number(dateParts[1]);
    const year = Number(dateParts[2]);
    if (!day || !month || !year) return null;

    const m = t.match(/^(\d{1,2}):(\d{2}):(\d{2})\s*(AM|PM)$/i);
    if (!m) return null;
    let hour = Number(m[1]);
    const minute = Number(m[2]);
    const second = Number(m[3]);
    const ampm = m[4].toUpperCase();
    if (ampm === "PM" && hour !== 12) hour += 12;
    if (ampm === "AM" && hour === 12) hour = 0;

    const dt = new Date(year, month - 1, day, hour, minute, second);
    return Number.isNaN(dt.getTime()) ? null : dt;
  }

  function buildChartLabels(selectedDeviceName) {
    const deviceObj = displayDevices.find((d) => (d.device_uid || d.name) === selectedDeviceName);
    const base = parseDeviceTimestamp(deviceObj?.timestamp) || new Date();
    if (!base) {
      return ["—", "—", "—"];
    }
    // Create evenly spaced time buckets for the demo chart.
    // (You can tune this later once real timestamp arrays come in.)
    const intervalSeconds = 60;
    return Array.from({ length: 3 }, (_, idx) => {
      const t = new Date(base.getTime() + idx * intervalSeconds * 1000);
      return t.toLocaleTimeString([], { hour: "numeric", minute: "2-digit", second: "2-digit" });
    });
  }

  const handleDeviceClick = (device) => {
    if (selectedDevice === device) {
      setSelectedDevice(null);
      return;
    }

    setSelectedDevice(device);
  };

  const deviceCards = filteredDevices.map((device) => (
    <article className="data-device-card" key={device.name}>
      <div className="data-card-header">
        <div className="data-card-copy">
          <h3>{device.name}</h3>
          <p>{device.location}</p>
        </div>
        <span className="data-card-timestamp">{device.timestamp}</span>
      </div>

      <div className="data-card-metrics">
        {device.metrics.map(([label, value]) => (
          <div className="data-card-metric" key={`${device.name}-${label}`}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
    </article>
  ));

  // UX rule: if dashboard data is visible, treat status as connected for display.
  const hasVisibleData =
    (Array.isArray(apiReadings) && apiReadings.length > 0) ||
    (Array.isArray(displayDevices) && displayDevices.length > 0);
  const showConnectedStatus = isConnected || hasVisibleData;

  return (
    <section className="data-main">
      {!shouldUseMockDevices && apiLoaded && displayDevices.length === 0 ? (
        <article className="data-device-card">
          <div className="data-card-header">
            <div className="data-card-copy">
              <h3>No devices found</h3>
              <p>Add device rows in the database to populate this module.</p>
            </div>
          </div>
        </article>
      ) : null}

      <div className="data-main-header">
        <div>
          <div className="device-selector">
            <button
              className={`ui-button ui-button-pill device-btn${selectedDevice === null ? " active" : ""}`}
              onClick={() => setSelectedDevice(null)}
              type="button"
            >
              ALL
            </button>
            {devices.map((device) => (
              <button
                className={`ui-button ui-button-pill device-btn${selectedDevice === device ? " active" : ""}`}
                key={device}
                onClick={() => handleDeviceClick(device)}
                type="button"
              >
                {device}
              </button>
            ))}
          </div>
          <p className={`websocket-status ${showConnectedStatus ? "is-connected" : "is-disconnected"}`}>
            <span className="websocket-status-dot" />
            {`WebSocket: ${showConnectedStatus ? "connected" : "disconnected"}`}
          </p>
        </div>
        <button className="ui-button ui-button-rect data-refresh-button" type="button">
          Refresh
        </button>
      </div>

      {selectedDevice !== null ? (
        <div
          className="data-main-split"
          style={{
            display: "grid",
            gridTemplateColumns: "7fr 3fr",
            gridTemplateAreas: `"left-top right-top" "left-bottom right-bottom"`,
            gap: "12px",
            alignItems: "start",
          }}
        >
          <div className="data-left-top" style={{ gridArea: "left-top" }}>{deviceCards}</div>

          <div className="data-right-top" style={{ gridArea: "right-top" }}>
            <ImagePanel deviceId={selectedDevice} title="Camera Data" />
          </div>

          <div className="data-left-bottom" style={{ gridArea: "left-bottom" }}>
            <div className="data-metric-tabs">
              {dataMetricTabs.map((metric) => (
                <button
                  className={`ui-button ui-button-pill data-metric-pill${selectedMetric === metric ? " active" : ""}`}
                  key={metric}
                  onClick={() => setSelectedMetric(metric)}
                  type="button"
                >
                  {metric}
                </button>
              ))}
            </div>

            <article className="data-chart-panel">
              <div className="data-chart-header">
                <h3>
                  {selectedMetric} - {chartTargetLabel}
                </h3>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span>{pointsCount} pts</span>
                  <div style={{ display: "flex", gap: "6px" }}>
                    <button
                      className="ui-button ui-button-rect"
                      type="button"
                      onClick={() => {
                        setZoomLevel((z) => (Number(z) || 1) * 2);
                        setHoveredPointIndex(null);
                      }}
                      style={{ padding: "6px 10px", fontSize: "12px" }}
                    >
                      Zoom In
                    </button>
                    <button
                      className="ui-button ui-button-rect"
                      type="button"
                      onClick={() => {
                        setZoomLevel((z) => Math.max(1, (Number(z) || 1) / 2));
                        setHoveredPointIndex(null);
                      }}
                      style={{ padding: "6px 10px", fontSize: "12px" }}
                    >
                      Zoom Out
                    </button>
                    <button
                      className="ui-button ui-button-rect"
                      type="button"
                      onClick={() => {
                        setYZoomLevel((z) => Math.min(10, (Number(z) || 1) * 1.5));
                        setHoveredPointIndex(null);
                      }}
                      style={{ padding: "6px 10px", fontSize: "12px" }}
                    >
                      Y +
                    </button>
                    <button
                      className="ui-button ui-button-rect"
                      type="button"
                      onClick={() => {
                        setYZoomLevel((z) => Math.max(1, (Number(z) || 1) / 1.5));
                        setHoveredPointIndex(null);
                      }}
                      style={{ padding: "6px 10px", fontSize: "12px" }}
                    >
                      Y -
                    </button>
                  </div>
                </div>
              </div>

              <div className="data-chart-shell">
                {!shouldUseMockDevices && pointsCount === 0 ? (
                  <div className="image-placeholder">No telemetry rows found for this device.</div>
                ) : null}
                <svg
                  aria-label={`${selectedMetric} chart for ${chartTargetLabel}`}
                  className="data-chart-svg"
                  role="img"
                  viewBox={`0 0 ${dataChartConfig.width} ${dataChartConfig.height}`}
                  onMouseLeave={() => setHoveredPointIndex(null)}
                  onWheel={(e) => {
                    // Scroll-wheel zoom on Y axis (prevent page scroll while hovering the chart).
                    if (!e) return;
                    try {
                      e.preventDefault();
                    } catch {
                      // no-op
                    }
                    const deltaY = Number(e.deltaY);
                    if (!Number.isFinite(deltaY) || deltaY === 0) return;
                    const zoomFactor = deltaY < 0 ? 1.25 : 1 / 1.25;
                    setYZoomLevel((z) => {
                      const next = (Number(z) || 1) * zoomFactor;
                      return Math.min(10, Math.max(1, next));
                    });
                    setHoveredPointIndex(null);
                  }}
                >
                  {yAxisLabels.map((label) => (
                    <g key={label}>
                      <line
                        className="data-chart-grid"
                        x1={dataChartConfig.left}
                        x2={dataChartConfig.width - dataChartConfig.right}
                        y1={getChartY(label, chartMaxValue)}
                        y2={getChartY(label, chartMaxValue)}
                      />
                      <text
                        className="data-chart-label"
                        textAnchor="end"
                        x={dataChartConfig.left - 8}
                        y={getChartY(label, chartMaxValue) + 4}
                      >
                        {label}
                      </text>
                    </g>
                  ))}

                  {chartLabels.map((label, index) => (
                    <g key={`${label}-${index}`}>
                      <line
                        className="data-chart-grid is-vertical"
                        x1={getChartX(index, pointsCount)}
                        x2={getChartX(index, pointsCount)}
                        y1={dataChartConfig.top}
                        y2={dataChartConfig.height - dataChartConfig.bottom}
                      />
                      <text
                        className="data-chart-label"
                        textAnchor="middle"
                        x={getChartX(index, pointsCount)}
                        y={dataChartConfig.height - 6}
                      >
                        {shouldShowXAxisLabel(index, chartLabels.length) ? label : ""}
                      </text>
                      <rect
                        fill="transparent"
                        height={dataChartConfig.height - dataChartConfig.bottom - dataChartConfig.top}
                        onMouseEnter={() => setHoveredPointIndex(index)}
                        width={Math.max((dataChartConfig.width - dataChartConfig.left - dataChartConfig.right) / Math.max(pointsCount - 1, 1), 12)}
                        x={getChartX(index, pointsCount) - Math.max((dataChartConfig.width - dataChartConfig.left - dataChartConfig.right) / Math.max(pointsCount - 1, 1), 12) / 2}
                        y={dataChartConfig.top}
                      />
                    </g>
                  ))}

                  {hoverX !== null ? (
                    <g>
                      <line
                        className="data-chart-hover-line-glow"
                        x1={hoverX}
                        x2={hoverX}
                        y1={dataChartConfig.top}
                        y2={dataChartConfig.height - dataChartConfig.bottom}
                      />
                      <line
                        className="data-chart-hover-line"
                        x1={hoverX}
                        x2={hoverX}
                        y1={dataChartConfig.top}
                        y2={dataChartConfig.height - dataChartConfig.bottom}
                      />
                    </g>
                  ) : null}

                  <line
                    className="data-chart-axis"
                    x1={dataChartConfig.left}
                    x2={dataChartConfig.left}
                    y1={dataChartConfig.top}
                    y2={dataChartConfig.height - dataChartConfig.bottom}
                  />
                  <line
                    className="data-chart-axis"
                    x1={dataChartConfig.left}
                    x2={dataChartConfig.width - dataChartConfig.right}
                    y1={dataChartConfig.height - dataChartConfig.bottom}
                    y2={dataChartConfig.height - dataChartConfig.bottom}
                  />

                  {activeChartSeries.map((series) => (
                    <g key={series.color}>
                      <polyline
                        className="data-chart-series"
                        points={buildLinePoints(series.values, chartMaxValue)}
                        stroke={series.color}
                      />
                      {series.values.map((value, index) => {
                        const n = Number(value);
                        if (!Number.isFinite(n)) return null;
                        return (
                          <circle
                            className={`data-chart-point${safeHoveredPointIndex === index ? " is-hovered" : ""}`}
                            cx={getChartX(index, pointsCount)}
                            cy={getChartY(n, chartMaxValue)}
                            fill={series.color}
                            key={`${series.color}-${index}`}
                            r={safeHoveredPointIndex === index ? "4" : "2.5"}
                          />
                        );
                      })}
                    </g>
                  ))}

                  {safeHoveredPointIndex !== null ? (
                    <CustomChartTooltip
                      maxX={dataChartConfig.width - dataChartConfig.right - 8}
                      rows={hoverSeriesRows}
                      title={formatTooltipTimestamp(hoverTimestampRaw, hoverLabel)}
                      x={hoverX ?? dataChartConfig.left}
                      y={dataChartConfig.top + 8}
                    />
                  ) : null}
                </svg>
              </div>
            </article>
          </div>

          <div className="data-right-bottom" style={{ gridArea: "right-bottom" }}>
            <ImagePanel deviceId={selectedDevice} title="Spectral Camera Data" />
          </div>
        </div>
      ) : (
        <div className="data-card-grid">{deviceCards}</div>
      )}
    </section>
  );
}


export default function EdgeConsoleShell({
  brand,
  modules,
  activeModule,
  overview,
  services,
  isHome = false,
  deviceManagementAction = null,
  selectedTab = null,
}) {
  const selectedTabLabel =
    typeof selectedTab === "string" && activeModule.subTabs?.includes(selectedTab) ? selectedTab : null;

  const defaultSubTab = selectedTabLabel
    ? selectedTabLabel
    : activeModule.subTabs?.includes(activeModule.focusTab)
      ? activeModule.focusTab
      : activeModule.subTabs?.[0] || activeModule.focusTab || "";
  const [activeSubTab, setActiveSubTab] = useState(defaultSubTab);

  useEffect(() => {
    setActiveSubTab(defaultSubTab);
  }, [defaultSubTab, activeModule.slug, selectedTabLabel]);
  const isDataModule = activeModule.slug === "data";

  const defaultOverviewCards = [
    ["Sites", overview.total_sites],
    ["Devices", overview.total_devices],
    ["Online", overview.active_devices],
    ["Adapters", overview.active_protocol_adapters],
    ["Sessions", overview.active_sessions],
    ["Queued Jobs", overview.queued_inference_jobs],
    ["Open Alerts", overview.open_alerts],
    ["Approvals", overview.pending_approvals],
  ];

  // Device-management specific dashboard strip.
  // Note: overview payload does not yet expose camera assignment counts,
  // so we derive a reasonable placeholder from available device counts.
  const assignedCameras = Math.max(
    0,
    Math.min(
      Number(overview.total_devices || 0),
      Math.round(Number(overview.active_devices || 0) * 0.7)
    )
  );
  const unassignedDevices = Math.max(
    0,
    Number(overview.total_devices || 0) - assignedCameras
  );

  const deviceManagementOverviewCards = [
    ["Registered Devices", overview.total_devices],
    ["Devices Online", overview.active_devices],
    ["Cameras Assigned", assignedCameras],
    ["Cameras Unassigned", unassignedDevices],
    ["Provisioning Sessions", overview.active_sessions],
    ["Pending Sync Jobs", overview.pending_sync_jobs],
    ["Pending Approvals", overview.pending_approvals],
    ["Unhealthy Services", overview.unhealthy_services],
  ];

  const overviewCards =
    activeModule.slug === "device-management"
      ? deviceManagementOverviewCards
      : defaultOverviewCards;
  const rawPanel = getPanelContent(activeModule, activeSubTab);
  const isDeviceManagementActionPage =
    activeModule.slug === "device-management" && deviceManagementAction;

  const activePanel = isDeviceManagementActionPage
    ? {
        tab: deviceManagementAction?.subTab || rawPanel.tab,
        title: deviceManagementAction?.title || rawPanel.title,
        summary: deviceManagementAction?.description || rawPanel.summary,
        bullets: deviceManagementAction?.bullets || [],
      }
    : rawPanel;

  const activeSectionId = toSectionId(activePanel.tab);
  const activeActionButtons = isDeviceManagementActionPage
    ? []
    : activeModule.subTabActions?.[activePanel.tab] || [];
  const showDetailPanel = false;

  return (
    <MainLayout
      brand={brand}
      modules={modules}
      activeModuleSlug={activeModule.slug}
      activeModuleTitle={activeModule.title}
      isDataModule={isDataModule}
    >
      {isDataModule ? (
        <DataSectionDashboard />
      ) : activeModule.slug === "edge-ai-health" ? (
        <EdgeAIHealthModule />
      ) : activeModule.slug === "device-health" ? (
        <DeviceHealthModule />
      ) : (
        <>
          {activeModule.slug !== "dashboard" ? (
            <div
              className="console-topbar"
              aria-label={`${activeModule.title} sections`}
              role="tablist"
            >
              {activeModule.subTabs.map((tab) => (
                isDeviceManagementActionPage ? (
                  <Link
                    aria-selected={tab === activePanel.tab}
                    className={`${subtabPillClass}${tab === activePanel.tab ? " active" : ""}`}
                    href={`/dashboard?tab=${encodeURIComponent(tab)}`}
                    id={`tab-${toSectionId(tab)}`}
                    key={tab}
                    role="tab"
                  >
                    {tab}
                  </Link>
                ) : (
                  <button
                    aria-controls={`section-${toSectionId(tab)}`}
                    aria-selected={tab === activePanel.tab}
                    className={`${subtabPillClass}${tab === activePanel.tab ? " active" : ""}`}
                    id={`tab-${toSectionId(tab)}`}
                    key={tab}
                    onClick={() => setActiveSubTab(tab)}
                    role="tab"
                    type="button"
                  >
                    {tab}
                  </button>
                )
              ))}
            </div>
          ) : null}

          {activeModule.slug !== "dashboard" ? (
            <div className={`console-panels is-single-panel`}>
              <article
                aria-labelledby={`tab-${activeSectionId}`}
                className="focus-panel"
                id={`section-${activeSectionId}`}
                role="tabpanel"
              >
                <>
                  <span className="focus-tab">{activePanel.tab}</span>
                  <h2>{activePanel.title}</h2>
                  <p className="focus-summary">{activePanel.summary}</p>
                  {!isDeviceManagementActionPage && activePanel.bullets.length ? (
                    <ul className="focus-list">
                      {activePanel.bullets.map((item, index) => (
                        <li key={`${activePanel.tab}-${index}`}>{item}</li>
                      ))}
                    </ul>
                  ) : isDeviceManagementActionPage ? (
                    <DeviceManagementActionForm action={deviceManagementAction} actionTab={activePanel.tab} />
                  ) : null}

                  {!isDeviceManagementActionPage &&
                  activeModule.slug === "device-management" &&
                  activeActionButtons.length ? (
                    <div className="focus-actions" aria-label={`${activePanel.tab} actions`}>
                      {activeActionButtons.map((label) => {
                        const actionSlug = toSectionId(label);
                        return (
                          <Link
                            className="ui-button ui-button-pill"
                            href={`/dashboard/device-management/actions/${actionSlug}`}
                            key={`${activePanel.tab}-${label}`}
                          >
                            {label}
                          </Link>
                        );
                      })}
                    </div>
                  ) : null}
                </>
              </article>
            </div>
          ) : null}

          {activeModule.slug === "dashboard" && !isDeviceManagementActionPage ? (
            <AnalyticsOverview />
          ) : null}

          {!isDeviceManagementActionPage && activeModule.slug !== "dashboard" ? (
            <div className="overview-strip mt-4">
              {overviewCards.map(([label, value]) => (
                <article className="overview-card dashboard-hover-card" key={label}>
                  <span>{label}</span>
                  <strong>{value}</strong>
                </article>
              ))}
            </div>
          ) : null}

          {null}
        </>
      )}
    </MainLayout>
  );
}
