#include <WiFi.h>
#include <Arduino_H7_Video.h>
#include <lvgl.h>

Arduino_H7_Video Display(800, 480, GigaDisplayShield);

const char* ssid = "rtbi";
const char* password = "rtbi@27.";
const char* esp_ip = "192.168.68.134";

#define IMG_W 320
#define IMG_H 240
#define RAW_SIZE (IMG_W * IMG_H * 2)

// IMPORTANT: Static buffer (goes to SDRAM for LTDC)
static uint16_t canvasBuf[IMG_W * IMG_H];

uint8_t *rawBuffer;
lv_obj_t *canvas;

void setup()
{
  Serial.begin(115200);
  delay(2000);

  Serial.println("GIGA STARTING...");

  // ---------------- DISPLAY FIRST ----------------
  Display.begin();

  // Allocate network buffer
  rawBuffer = (uint8_t*)malloc(RAW_SIZE);
  if (!rawBuffer)
  {
    Serial.println("RAW buffer allocation failed!");
    while(1);
  }

  // Create LVGL canvas
  canvas = lv_canvas_create(lv_scr_act());
  lv_canvas_set_buffer(canvas,
                       canvasBuf,
                       IMG_W,
                       IMG_H,
                       LV_COLOR_FORMAT_RGB565);

  lv_obj_center(canvas);

  // RED test screen
  lv_canvas_fill_bg(canvas, lv_color_hex(0xFF0000), LV_OPA_COVER);

  for(int i=0;i<150;i++)
  {
    lv_timer_handler();
    delay(5);
  }

  Serial.println("Display OK");

  // ---------------- WIFI SECOND ----------------
  Serial.println("Connecting WiFi...");
  WiFi.begin(ssid, password);

  int timeout = 0;
  while (WiFi.status() != WL_CONNECTED && timeout < 30)
  {
    delay(500);
    Serial.print(".");
    timeout++;
  }

  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("\nWiFi failed!");
    return;
  }

  Serial.println("\nWiFi Connected");
  Serial.println(WiFi.localIP());

  // ---------------- CONNECT TO ESP ----------------
  Serial.println("Connecting to ESP...");

  WiFiClient client;

  if (!client.connect(esp_ip, 80))
  {
    Serial.println("ESP connection failed");
    return;
  }

  client.print("GET / HTTP/1.1\r\n");
  client.print("Host: ");
  client.print(esp_ip);
  client.print("\r\nConnection: close\r\n\r\n");

  // Wait for response
  unsigned long start = millis();
  while (!client.available())
  {
    if (millis() - start > 5000)
    {
      Serial.println("ESP timeout");
      client.stop();
      return;
    }
  }

  // Skip HTTP headers
  while (client.connected())
  {
    String line = client.readStringUntil('\n');
    if (line == "\r") break;
  }

  size_t received = 0;

  while (client.connected() && received < RAW_SIZE)
  {
    if (client.available())
      rawBuffer[received++] = client.read();
  }

  client.stop();

  Serial.print("Bytes received: ");
  Serial.println(received);

  if (received != RAW_SIZE)
  {
    Serial.println("Frame size mismatch");
    return;
  }

  // Swap RGB565 bytes
  for (int i = 0; i < IMG_W * IMG_H; i++)
  {
    canvasBuf[i] =
      (rawBuffer[i * 2 + 1] << 8) |
       rawBuffer[i * 2];
  }

  lv_obj_invalidate(canvas);

  for(int i=0;i<200;i++)
  {
    lv_timer_handler();
    delay(5);
  }

  Serial.println("Image displayed.");
}

void loop()
{
  // nothing
}