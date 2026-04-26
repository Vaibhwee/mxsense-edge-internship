"use client";

import { useEffect, useMemo, useState } from "react";

export default function CameraStream({ streamUrl, deviceId }) {
  const [status, setStatus] = useState("connecting"); // connecting | online | offline
  const [imgKey, setImgKey] = useState(0);

  const offlineTimeoutMs = 6000;

  const shouldTry = useMemo(() => Boolean(streamUrl), [streamUrl]);

  useEffect(() => {
    if (!shouldTry) return;

    setStatus("connecting");
    const t = window.setTimeout(() => {
      setStatus((prev) => (prev === "connecting" ? "offline" : prev));
    }, offlineTimeoutMs);

    return () => window.clearTimeout(t);
  }, [shouldTry, streamUrl, deviceId]);

  function handleError() {
    setStatus("offline");
  }

  function handleLoad() {
    setStatus("online");
  }

  // If your app runs on HTTPS, browsers block `http://` camera streams (mixed content).
  // For dev, keep the app on HTTP or proxy the camera stream through your backend.
  return (
    <div className="camera-stream-shell">
      {status === "connecting" ? (
        <div className="camera-overlay">
          <div className="camera-spinner" aria-hidden="true" />
          <div className="camera-overlay-text">Connecting to camera...</div>
        </div>
      ) : null}

      {status === "offline" ? (
        <div className="camera-overlay">
          <div className="camera-overlay-text">Camera Offline</div>
        </div>
      ) : null}

      {shouldTry ? (
        <img
          key={imgKey}
          className="image-preview"
          src={streamUrl}
          alt={`Device Camera (${deviceId})`}
          onError={handleError}
          onLoad={handleLoad}
          loading="eager"
        />
      ) : (
        <div className="image-placeholder">Camera Offline</div>
      )}
    </div>
  );
}
