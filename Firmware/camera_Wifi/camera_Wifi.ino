#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>

// Select correct camera model
#define CAMERA_MODEL_ESP32S3_EYE
#include "camera_pins.h"

const char* ssid = "ESP32_CAM";
const char* password = "12345678";

WebServer server(80);

void handleCapture() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    server.send(500, "text/plain", "Camera capture failed");
    return;
  }

  WiFiClient client = server.client();
  server.sendHeader("Content-Type", "image/jpeg");
  server.send(200);
  client.write(fb->buf, fb->len);

  esp_camera_fb_return(fb);
}

void setup() {
  Serial.begin(115200);

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 12;
  config.fb_count = 2;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed: 0x%x\n", err);
    return;
  }

  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);

  Serial.println("Access Point Started");
  Serial.println(WiFi.softAPIP());

  server.on("/capture", handleCapture);
  server.begin();
}

void loop() {
  server.handleClient();
}
