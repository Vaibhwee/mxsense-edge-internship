#include "esp_camera.h"
#include <WiFi.h>
#include "board_config.h"

void startCameraServer();
void setupLedFlash();

void setup() {
  delay(3000);   // give USB time to attach
  
  Serial.begin(115200);
  delay(2000);  // allow serial to attach
  Serial.println("\nBooting...");

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
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;

  // 🔥 Safe camera configuration
  config.frame_size = FRAMESIZE_QVGA;      // 320x240
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_LATEST;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 15;                // safer quality
  config.fb_count = 1;                     // single framebuffer

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed 0x%x\n", err);
    return;
  }

  Serial.println("Camera initialized successfully");

  sensor_t *s = esp_camera_sensor_get();
  s->set_framesize(s, FRAMESIZE_QVGA);

#if defined(LED_GPIO_NUM)
  setupLedFlash();
#endif

  // 🔥 Access Point Mode
  WiFi.mode(WIFI_AP);
  WiFi.softAP("ESP32_CAM", "12345678");
  WiFi.setSleep(false);

  Serial.println("Access Point Started");
  Serial.print("IP Address: ");
  Serial.println(WiFi.softAPIP());  // correct for AP mode

  startCameraServer();

  Serial.println("Camera Ready!");
  Serial.println("Open browser: http://192.168.4.1");
}

void loop() {
  delay(10000);
}
