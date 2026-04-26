"use client";

import { useEffect, useMemo, useState } from "react";

import { resolveDisplayImageUrl } from "../lib/resolveImageUrl";

export default function CameraSnapshot({
  baseUrl,
  refreshMs = 2500,
  deviceId,
}) {
  const [imageSrc, setImageSrc] = useState(null);
  const [status, setStatus] = useState("loading"); // loading | online | offline

  useEffect(() => {
    if (!baseUrl) return;

    let isMounted = true;

    function loadOnce() {
      if (!isMounted) return;
      setStatus((prev) => (prev === "offline" ? "loading" : prev));
      const root = resolveDisplayImageUrl(baseUrl) ?? baseUrl;
      setImageSrc(`${root}?t=${Date.now()}`);
    }

    loadOnce();
    const id = window.setInterval(loadOnce, refreshMs);

    return () => {
      isMounted = false;
      window.clearInterval(id);
    };
  }, [baseUrl, refreshMs]);

  function handleError() {
    setStatus("offline");
  }

  function handleLoad() {
    setStatus("online");
  }

  // For HTTPS pages, `http://` snapshots may be blocked (mixed content).
  // In dev, run the frontend on HTTP or proxy `/snapshots` through your backend.
  return (
    <div className="camera-stream-shell">
      {status === "loading" ? (
        <div className="camera-overlay">
          <div className="camera-spinner" aria-hidden="true" />
          <div className="camera-overlay-text">Loading camera...</div>
        </div>
      ) : null}

      {status === "offline" ? (
        <div className="camera-overlay">
          <div className="camera-overlay-text">Camera Offline</div>
        </div>
      ) : null}

      {imageSrc ? (
        <img
          key={imageSrc}
          className="image-preview"
          src={imageSrc}
          alt={`Device Camera (${deviceId})`}
          onError={handleError}
          onLoad={handleLoad}
          loading="eager"
        />
      ) : (
        <div className="image-placeholder">Loading camera...</div>
      )}
    </div>
  );
}

