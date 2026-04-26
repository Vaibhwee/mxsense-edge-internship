"use client";

/**
 * LiveCameraFeed
 *
 * Polls `{NEXT_PUBLIC_PLATFORM_API_ROOT}/api-gateway/latest-image/?device_id=…` every `intervalMs`
 * (Django platform DB — same source as the dashboard Live Camera panel).
 *
 * Usage:
 *   <LiveCameraFeed deviceId="esp32-cam-001" intervalMs={5000} />
 */

import { useCallback, useEffect, useRef, useState } from "react";

import { resolveDisplayImageUrl } from "../../../lib/resolveImageUrl";

const PLATFORM_API_ROOT =
  process.env.NEXT_PUBLIC_PLATFORM_API_ROOT || "http://127.0.0.1:8000/api";

const CAMERA_API_BASE =
  process.env.NEXT_PUBLIC_CAMERA_API_URL || "http://localhost:8009";

export default function LiveCameraFeed({
  deviceId,
  intervalMs = 5000,
  showControls = true,
}) {
  const [imageUrl, setImageUrl] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState(null);
  const [cameraNotAssigned, setCameraNotAssigned] = useState(false);
  const [waitingForCapture, setWaitingForCapture] = useState(false);
  const [loading, setLoading] = useState(false);
  const [paused, setPaused] = useState(false);
  const intervalRef = useRef(null);

  const fetchLatestImage = useCallback(async () => {
    if (!deviceId) return;
    setLoading(true);

    try {
      setCameraNotAssigned(false);
      setWaitingForCapture(false);
      const res = await fetch(
        `${PLATFORM_API_ROOT}/api-gateway/latest-image/?device_id=${encodeURIComponent(deviceId)}`,
        { cache: "no-store" }
      );

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data.detail || `HTTP ${res.status}`);
      }

      const assigned = data.camera_assigned;
      const url = data.image_url || data.url || null;

      if (assigned === false) {
        setImageUrl(null);
        setLastUpdated(null);
        setError(null);
        setCameraNotAssigned(true);
      } else if (assigned === true) {
        if (url) {
          const resolved = resolveDisplayImageUrl(url) ?? url;
          setImageUrl(resolved);
          setLastUpdated(new Date());
          setError(null);
        } else {
          setImageUrl(null);
          setLastUpdated(null);
          setError(null);
          setWaitingForCapture(true);
        }
      } else if (url) {
        const resolved = resolveDisplayImageUrl(url) ?? url;
        setImageUrl(resolved);
        setLastUpdated(new Date());
        setError(null);
      } else {
        setImageUrl(null);
        setLastUpdated(null);
        setError(null);
      }
    } catch (err) {
      setError(err.message ?? "Failed to fetch image.");
    } finally {
      setLoading(false);
    }
  }, [deviceId]);

  useEffect(() => {
    if (!deviceId || paused) return;

    fetchLatestImage();
    intervalRef.current = setInterval(fetchLatestImage, intervalMs);

    return () => clearInterval(intervalRef.current);
  }, [deviceId, intervalMs, paused, fetchLatestImage]);

  const handleCaptureNow = async () => {
    try {
      setLoading(true);
      const res = await fetch(
        `${CAMERA_API_BASE}/api/v1/devices/${encodeURIComponent(deviceId)}/capture-and-store`,
        { method: "POST" }
      );
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `HTTP ${res.status}`);
      }
      await fetchLatestImage();
    } catch (err) {
      setError(err.message ?? "Capture failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="live-camera-feed">
      {/* Header */}
      <div className="feed-header">
        <span className="feed-title">
          Camera Feed — <code>{deviceId}</code>
        </span>
        {loading && <span className="feed-status loading">Refreshing…</span>}
        {!loading && lastUpdated && (
          <span className="feed-status ok">
            Updated {lastUpdated.toLocaleTimeString()}
          </span>
        )}
      </div>

      {/* Image */}
      <div className="feed-image-wrapper">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt="Live Camera"
            className="feed-image"
          />
        ) : error ? (
          <div className="feed-placeholder error">{error}</div>
        ) : cameraNotAssigned ? (
          <div className="feed-placeholder">
            Camera not assigned — register the ESP32 IP for this device
          </div>
        ) : waitingForCapture ? (
          <div className="feed-placeholder">
            Waiting for first capture from the assigned camera…
          </div>
        ) : (
          <div className="feed-placeholder">Waiting for first image…</div>
        )}
      </div>

      {/* Error banner */}
      {error && imageUrl && (
        <div className="feed-error-banner">⚠ {error}</div>
      )}

      {/* Controls */}
      {showControls && (
        <div className="feed-controls">
          <button
            className="btn-capture"
            onClick={handleCaptureNow}
            disabled={loading}
          >
            Capture Now
          </button>
          <button
            className="btn-toggle"
            onClick={() => setPaused((p) => !p)}
          >
            {paused ? "▶ Resume" : "⏸ Pause"}
          </button>
          <span className="feed-interval">
            Auto-refresh: {intervalMs / 1000}s
          </span>
        </div>
      )}

      <style jsx>{`
        .live-camera-feed {
          display: flex;
          flex-direction: column;
          gap: 8px;
          background: #0f1117;
          border: 1px solid #2a2d3a;
          border-radius: 10px;
          padding: 16px;
          max-width: 640px;
          font-family: system-ui, sans-serif;
        }

        .feed-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 13px;
          color: #9ca3af;
        }

        .feed-title {
          font-weight: 600;
          color: #e5e7eb;
        }

        .feed-title code {
          background: #1e2130;
          padding: 1px 6px;
          border-radius: 4px;
          font-size: 12px;
          color: #60a5fa;
        }

        .feed-status {
          font-size: 11px;
          padding: 2px 8px;
          border-radius: 12px;
        }

        .feed-status.loading {
          background: #1e3a5f;
          color: #93c5fd;
        }

        .feed-status.ok {
          background: #14532d;
          color: #86efac;
        }

        .feed-image-wrapper {
          border-radius: 6px;
          overflow: hidden;
          background: #1a1d2e;
          min-height: 200px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .feed-image {
          width: 100%;
          height: auto;
          display: block;
          object-fit: contain;
        }

        .feed-placeholder {
          color: #6b7280;
          font-size: 13px;
          text-align: center;
          padding: 40px 20px;
        }

        .feed-placeholder.error {
          color: #f87171;
        }

        .feed-error-banner {
          background: #450a0a;
          color: #fca5a5;
          font-size: 12px;
          padding: 6px 12px;
          border-radius: 6px;
          border: 1px solid #7f1d1d;
        }

        .feed-controls {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
        }

        .btn-capture,
        .btn-toggle {
          padding: 5px 14px;
          border-radius: 6px;
          font-size: 12px;
          font-weight: 500;
          cursor: pointer;
          border: none;
          transition: opacity 0.15s;
        }

        .btn-capture {
          background: #2563eb;
          color: #fff;
        }

        .btn-capture:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .btn-toggle {
          background: #374151;
          color: #d1d5db;
        }

        .btn-capture:hover:not(:disabled),
        .btn-toggle:hover {
          opacity: 0.85;
        }

        .feed-interval {
          font-size: 11px;
          color: #6b7280;
          margin-left: auto;
        }
      `}</style>
    </div>
  );
}
