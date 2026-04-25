#include "esp_camera.h"
#include <WiFi.h>

/* ================= WIFI ================= */
const char* ssid = "rtbi";
const char* password = "rtbi@27.";

/* Camera Pins (XIAO ESP32S3 Sense) */
#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     10
#define SIOD_GPIO_NUM     40
#define SIOC_GPIO_NUM     39
#define Y9_GPIO_NUM       48
#define Y8_GPIO_NUM       11
#define Y7_GPIO_NUM       12
#define Y6_GPIO_NUM       14
#define Y5_GPIO_NUM       16
#define Y4_GPIO_NUM       18
#define Y3_GPIO_NUM       17
#define Y2_GPIO_NUM       15
#define VSYNC_GPIO_NUM    38
#define HREF_GPIO_NUM     47
#define PCLK_GPIO_NUM     13

WiFiServer server(80);

void setup() {

  Serial.begin(115200);

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;

  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;

  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;

  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;

  config.pin_pwdn  = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = 20000000;

  // 🔥 IMPORTANT: RGB565, NOT JPEG
  config.pixel_format = PIXFORMAT_RGB565;

  config.frame_size = FRAMESIZE_QVGA; // 320x240
  config.fb_count = 1;
  config.fb_location = CAMERA_FB_IN_PSRAM;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Camera init FAILED");
    while (1);
  }

  Serial.println("Camera init OK");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.println(WiFi.localIP());

  server.begin();
}

void loop() {

  WiFiClient client = server.available();
  if (!client) return;

  while (!client.available()) delay(1);

  while (client.connected()) {
    String line = client.readStringUntil('\n');
    if (line == "\r") break;
  }

  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    client.stop();
    return;
  }

  Serial.println("Sending RAW frame...");

  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: application/octet-stream");
  client.println("Content-Length: 153600");
  client.println("Connection: close");
  client.println();

  client.write(fb->buf, 153600);

  esp_camera_fb_return(fb);
  client.stop();
}
