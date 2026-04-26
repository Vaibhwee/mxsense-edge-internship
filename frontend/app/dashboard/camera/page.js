import LiveCameraFeed from "./LiveCameraFeed";

/**
 * Camera monitoring page – /dashboard/camera
 *
 * Edit DEVICE_IDS to match your registered ESP32 device IDs.
 */
const DEVICE_IDS = ["esp32-cam-001", "esp32-cam-002"];

export const metadata = {
  title: "Camera Monitor | Mxsense",
};

export default function CameraPage() {
  return (
    <main
      style={{
        padding: "24px",
        background: "#080b14",
        minHeight: "100vh",
        color: "#e5e7eb",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1 style={{ fontSize: "20px", fontWeight: 700, marginBottom: "20px" }}>
        Live Camera Feeds
      </h1>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(560px, 1fr))",
          gap: "20px",
        }}
      >
        {DEVICE_IDS.map((id) => (
          <LiveCameraFeed key={id} deviceId={id} intervalMs={5000} />
        ))}
      </div>
    </main>
  );
}
