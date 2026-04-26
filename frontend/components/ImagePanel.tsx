"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { resolveDisplayImageUrl } from "../lib/resolveImageUrl";

const FETCH_TIMEOUT_MS = 20_000;

export default function ImagePanel({
  deviceId,
  title = "Live Camera",
}: {
  deviceId: string;
  title?: string;
}) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [timestamp, setTimestamp] = useState<string>("");
  /** Browser failed to load the image URL (expired presign, 403, mixed content, etc.). */
  const [imageLoadFailed, setImageLoadFailed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  /** Camera service has no ESP32 / IP mapping for this device. */
  const [cameraNotAssigned, setCameraNotAssigned] = useState(false);
  /** Camera assigned but no capture in camera-service DB yet. */
  const [waitingForCapture, setWaitingForCapture] = useState(false);
  /** Last image came from platform DB because camera service was unreachable. */
  const [fromDbFallback, setFromDbFallback] = useState(false);
  const [loading, setLoading] = useState(false);

  const shouldRender = useMemo(() => Boolean(deviceId) && deviceId !== "ALL", [deviceId]);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    if (!shouldRender) {
      setImageUrl(null);
      setTimestamp("");
      setImageLoadFailed(false);
      setError(null);
      setCameraNotAssigned(false);
      setWaitingForCapture(false);
      setFromDbFallback(false);
      return;
    }

    const platformApiRoot =
      process.env.NEXT_PUBLIC_PLATFORM_API_ROOT || "http://127.0.0.1:8000/api";

    async function refresh() {
      if (!mountedRef.current) return;
      setLoading(true);
      setImageUrl(null);
      setTimestamp("");
      setImageLoadFailed(false);
      setError(null);
      setCameraNotAssigned(false);
      setWaitingForCapture(false);
      setFromDbFallback(false);

      const ac = new AbortController();
      const timeoutId = window.setTimeout(() => ac.abort(), FETCH_TIMEOUT_MS);

      try {
        const res = await fetch(
          `${platformApiRoot}/api-gateway/latest-image/?device_id=${encodeURIComponent(deviceId)}`,
          { cache: "no-store", signal: ac.signal }
        );

        const data = await res.json().catch(() => ({}));

        if (!mountedRef.current) return;

        if (!res.ok) {
          throw new Error(data?.detail || `HTTP ${res.status}`);
        }

        const assigned = data?.camera_assigned;
        const freshImageUrl = data?.image_url || data?.url || null;

        if (assigned === false) {
          setImageUrl(null);
          setTimestamp("");
          setCameraNotAssigned(true);
          return;
        }

        const fromDb = data?.image_source === "platform_db";

        if (assigned === true) {
          if (freshImageUrl) {
            const raw = String(freshImageUrl);
            setImageUrl(resolveDisplayImageUrl(raw) ?? raw);
            setTimestamp(new Date().toLocaleTimeString());
            setFromDbFallback(fromDb);
          } else {
            setWaitingForCapture(true);
          }
          return;
        }

        if (freshImageUrl) {
          const raw = String(freshImageUrl);
          setImageUrl(resolveDisplayImageUrl(raw) ?? raw);
          setTimestamp(new Date().toLocaleTimeString());
          setFromDbFallback(fromDb);
          return;
        }
      } catch (e: unknown) {
        if (!mountedRef.current) return;
        if (e instanceof Error && e.name === "AbortError") {
          setError("Request timed out — is the platform API reachable?");
        } else {
          const message = e instanceof Error ? e.message : "Failed to fetch latest image.";
          setImageUrl(null);
          setTimestamp("");
          setError(message);
        }
      } finally {
        window.clearTimeout(timeoutId);
        if (mountedRef.current) setLoading(false);
      }
    }

    refresh();
    const intervalId = window.setInterval(refresh, 5000);
    return () => clearInterval(intervalId);
  }, [deviceId, shouldRender]);

  let placeholder: string | null = null;
  if (!imageUrl && !error) {
    if (cameraNotAssigned) {
      placeholder = "Camera not assigned — register the ESP32 IP for this device";
    } else if (waitingForCapture) {
      placeholder = "Waiting for first capture from the assigned camera…";
    } else {
      placeholder = loading ? "Loading…" : "No image available";
    }
  }

  const showImage = Boolean(imageUrl) && !imageLoadFailed;
  const loadFailText =
    "Image link failed to load — often an expired pre-signed URL, blocked URL, or HTTP/HTTPS mismatch. Try capture again or check storage/CORS.";

  return (
    <div className="image-panel">
      <div className="image-panel-header">
        <h3 className="image-panel-title">{title}</h3>
        <span className="image-panel-subtitle">{deviceId}</span>
      </div>

      <div className="image-preview-shell">
        {showImage ? (
          <img
            key={imageUrl}
            src={imageUrl!}
            alt={title}
            className="image-preview"
            onLoad={() => setImageLoadFailed(false)}
            onError={() => setImageLoadFailed(true)}
          />
        ) : imageUrl && imageLoadFailed ? (
          <div className="image-placeholder">{loadFailText}</div>
        ) : error ? (
          <div className="image-placeholder">{error}</div>
        ) : (
          <div className="image-placeholder">{placeholder}</div>
        )}

        {showImage && fromDbFallback ? (
          <div className="image-panel-hint">
            Stored image from platform database — camera service unreachable or down.
          </div>
        ) : null}
        {showImage && timestamp ? (
          <div className="image-timestamp">{timestamp}</div>
        ) : null}
      </div>
    </div>
  );
}
