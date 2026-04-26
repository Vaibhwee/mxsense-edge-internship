"use client";

import { useEffect, useMemo, useState } from "react";
import { Circle, MapContainer, Marker, Popup, TileLayer, Tooltip, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet.markercluster/dist/MarkerCluster.css";
import "leaflet.markercluster/dist/MarkerCluster.Default.css";

function FitBounds({ positions }) {
  const map = useMap();
  useEffect(() => {
    if (!positions.length) return;
    const bounds = L.latLngBounds(positions.map((p) => [p.lat, p.lng]));
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 6 });
  }, [map, positions]);
  return null;
}

function statusToColor(status) {
  const s = String(status || "").toLowerCase();
  if (s === "online") return "#22c55e";
  if (s === "warning") return "#f0aa31";
  return "#3256ff";
}

function makeDivIcon(color, size = 14) {
  const glowSize = Math.max(16, Math.floor(size * 1.6));
  const anchor = Math.floor(size / 2);
  return L.divIcon({
    className: "",
    html: `<div style="
      width: ${size}px;
      height: ${size}px;
      border-radius: 999px;
      background: ${color};
      box-shadow: 0 0 0 3px rgba(0,0,0,0.25), 0 0 ${glowSize}px rgba(79, 208, 255, 0.25);
      border: 2px solid rgba(255,255,255,0.55);
    "></div>`,
    iconSize: [size, size],
    iconAnchor: [anchor, anchor],
  });
}

function DeviceClusters({ devices }) {
  const map = useMap();

  useEffect(() => {
    let clusterGroup = null;
    let cancelled = false;

    async function mountClusters() {
      await import("leaflet.markercluster");
      if (cancelled) return;

      clusterGroup = L.markerClusterGroup();

      devices.forEach((d) => {
        const marker = L.marker([d.lat, d.lng], {
          icon: makeDivIcon(statusToColor(d.status), 14),
        });

        marker.bindTooltip(`${d.id} / ${String(d.status).toUpperCase()}`, {
          direction: "top",
          offset: [0, -10],
          opacity: 0.9,
        });

        marker.bindPopup(`
          <div style="min-width:180px;">
            <div style="font-weight:800;margin-bottom:6px;">${d.name}</div>
            <div>Device ID: <strong>${d.id}</strong></div>
            <div>Status: <strong>${String(d.status).toUpperCase()}</strong></div>
            <div style="color:#6f86a7;margin-top:6px;">
              Lat, Lng: ${d.lat.toFixed(6)}, ${d.lng.toFixed(6)}
            </div>
          </div>
        `);

        clusterGroup.addLayer(marker);
      });

      map.addLayer(clusterGroup);
    }

    mountClusters();

    return () => {
      cancelled = true;
      if (clusterGroup) map.removeLayer(clusterGroup);
    };
  }, [devices, map]);

  return null;
}

export default function LocationsMap() {
  const [isClientReady, setIsClientReady] = useState(false);

  useEffect(() => {
    setIsClientReady(true);
  }, []);

  const edgeGateway = useMemo(
    () => ({
      id: "EDGE-GW-007",
      name: "Edge Gateway",
      site: "Plant 01 - Line A",
      lat: 13.0827,
      lng: 80.2707,
      status: "online",
    }),
    []
  );

  const deviceTemplates = useMemo(
    () => [
      { id: "DEV-101", status: "online" },
      { id: "DEV-102", status: "online" },
      { id: "DEV-103", status: "warning" },
      { id: "DEV-104", status: "online" },
      { id: "DEV-105", status: "offline" },
      { id: "DEV-106", status: "online" },
    ],
    []
  );

  const devices = useMemo(() => {
    const radiusMeters = 100;
    return deviceTemplates.map((device, idx) => {
      const angle = (idx / deviceTemplates.length) * Math.PI * 2;
      const distance = 35 + (idx % 3) * 20;
      const jitter = (idx % 2 === 0 ? 1 : -1) * (idx + 1) * 2;
      const effectiveMeters = Math.min(radiusMeters, distance + jitter);

      const latOffset = (effectiveMeters * Math.cos(angle)) / 111320;
      const lngOffset =
        (effectiveMeters * Math.sin(angle)) /
        (111320 * Math.cos((edgeGateway.lat * Math.PI) / 180));

      return {
        ...device,
        name: `Device ${idx + 1}`,
        lat: edgeGateway.lat + latOffset,
        lng: edgeGateway.lng + lngOffset,
      };
    });
  }, [deviceTemplates, edgeGateway.lat, edgeGateway.lng]);

  const positions = [
    { lat: edgeGateway.lat, lng: edgeGateway.lng },
    ...devices.map((d) => ({ lat: d.lat, lng: d.lng })),
  ];

  if (!isClientReady) {
    return <div className="locations-map-wrap" />;
  }

  return (
    <div className="locations-map-wrap">
      <MapContainer
        key="map1"
        center={[edgeGateway.lat, edgeGateway.lng]}
        zoom={16}
        scrollWheelZoom
        style={{ width: "100%", height: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <FitBounds positions={positions} />

        <Circle
          center={[edgeGateway.lat, edgeGateway.lng]}
          radius={100}
          pathOptions={{ color: "#22d3ee", fillColor: "#22d3ee", fillOpacity: 0.08, weight: 1.5 }}
        />

        <Marker position={[edgeGateway.lat, edgeGateway.lng]} icon={makeDivIcon("#38bdf8", 22)}>
          <Tooltip direction="top" offset={[0, -12]} opacity={0.95}>
            Edge Gateway
          </Tooltip>
          <Popup>
            <div style={{ minWidth: 200 }}>
              <div style={{ fontWeight: 800, marginBottom: 6 }}>Edge Gateway</div>
              <div>ID: {edgeGateway.id}</div>
              <div>Site: {edgeGateway.site}</div>
              <div style={{ marginTop: 6 }}>
                Status: <strong>{String(edgeGateway.status).toUpperCase()}</strong>
              </div>
            </div>
          </Popup>
        </Marker>

        <DeviceClusters devices={devices} />
      </MapContainer>

      <div className="locations-legend" aria-label="Legend">
        <div className="legend-row">
          <span className="legend-dot edge" />
          Edge Gateway
        </div>
        <div className="legend-row">
          <span className="legend-dot device" />
          Devices
        </div>
        <div className="legend-row">
          <span className="legend-dot coverage" />
          100m Coverage
        </div>
      </div>
    </div>
  );
}

