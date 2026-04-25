#include "esp_camera.h"
#include <WiFi.h>

// ===== WIFI =====
const char* ssid = "rtbi";
const char* password = "rtbi@27.";

WiFiServer server(80);

void setup() {
  Serial.begin(115200);
  delay(2000);

  // ===== CAMERA CONFIG =====
  camera_config_t config;

  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;

  config.pin_d0 = 15;
  config.pin_d1 = 17;
  config.pin_d2 = 18;
  config.pin_d3 = 16;
  config.pin_d4 = 14;
  config.pin_d5 = 12;
  config.pin_d6 = 11;
  config.pin_d7 = 48;

  config.pin_xclk = 10;
  config.pin_pclk = 13;
  config.pin_vsync = 38;
  config.pin_href  = 47;

  config.pin_sccb_sda = 40;
  config.pin_sccb_scl = 39;

  config.pin_pwdn  = -1;
  config.pin_reset = -1;

  config.xclk_freq_hz = 20000000;

  config.frame_size = FRAMESIZE_QQVGA;  // 160x120   // 320x240
  config.pixel_format = PIXFORMAT_JPEG;
  config.jpeg_quality = 12;
  config.fb_count     = 2;

  config.fb_location  = CAMERA_FB_IN_PSRAM;
  config.grab_mode    = CAMERA_GRAB_LATEST;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Camera init FAILED");
    return;
  }

  Serial.println("Camera init SUCCESS");

  // ===== WIFI CONNECT =====
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  Serial.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("ESP IP: ");
  Serial.println(WiFi.localIP());

  server.begin();
  Serial.println("Server started");
}

void loop() {

  WiFiClient client = server.available();
  if (!client) return;

  Serial.println("Client Connected!");

  while (client.connected() && client.available())
  {
    client.read();
  }
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    client.stop();
    return;
  }

  // ===== SEND HTTP HEADER =====
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: image/jpeg");
  client.print("Content-Length: ");
  client.println(fb->len);
  client.println("Connection: close");
  client.println();

  // ===== SAFE CHUNKED SEND =====
  size_t remaining = fb->len;
  uint8_t *bufPtr = fb->buf;

  while (remaining > 0)
  {
    size_t chunkSize = remaining > 1024 ? 1024 : remaining;
    size_t sent = client.write(bufPtr, chunkSize);

    if (sent > 0)
    {
      remaining -= sent;
      bufPtr += sent;
    }
    else
    {
      delay(1);  // wait and retry if TCP buffer is full
    }
  }

  client.flush();
  delay(50);   // ensure TCP stack finishes sending

  esp_camera_fb_return(fb);
  client.stop();

  Serial.println("Image sent successfully");
}
