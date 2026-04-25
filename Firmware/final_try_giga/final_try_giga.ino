#include <WiFi.h>
#include <Arduino_H7_Video.h>
#include <lvgl.h>
#include <TJpg_Decoder.h>

Arduino_H7_Video Display(800, 480, GigaDisplayShield);

const char* ssid     = "rtbi";
const char* password = "rtbi@27.";
const char* esp_ip   = "192.168.68.150";   // MUST match ESP

WiFiClient client;

#define IMG_W 160
#define IMG_H 120
#define MAX_IMAGE_SIZE 20000

// JPEG receive buffer
static uint8_t jpgBuffer[MAX_IMAGE_SIZE];

// Image buffer for LVGL (RGB565)
static uint16_t imgBuffer[IMG_W * IMG_H];

lv_obj_t *canvas;

/* ================= JPEG CALLBACK ================= */
bool tft_output(int16_t x, int16_t y,
                uint16_t w, uint16_t h,
                uint16_t *bitmap)
{
  for (uint16_t row = 0; row < h; row++)
  {
    memcpy(&imgBuffer[(y + row) * IMG_W + x],
           &bitmap[row * w],
           w * 2);
  }
  return true;
}

/* ================= WIFI ================= */
void connectWiFi()
{
  Serial.println("Connecting WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected");
  Serial.print("GIGA IP: ");
  Serial.println(WiFi.localIP());
}

/* ================= FETCH + DECODE ================= */
void fetchImage()
{
  Serial.println("Entering fetchImage()");

  if (!client.connect(esp_ip, 80))
  {
    Serial.println("ESP connect failed");
    return;
  }

  Serial.println("Connected to ESP");

  client.print("GET / HTTP/1.1\r\n");
  client.print("Host: ");
  client.print(esp_ip);
  client.print("\r\nConnection: close\r\n\r\n");

  Serial.println("Request sent");

  unsigned long timeout = millis();
  while (!client.available())
  {
    if (millis() - timeout > 5000)
    {
      Serial.println("Server timeout");
      client.stop();
      return;
    }
  }

  Serial.println("Server responded");

  int contentLength = 0;

  // ---- Read HTTP headers ----
  while (true)
  {
    String line = client.readStringUntil('\n');
    if (line == "\r" || line.length() == 0)
      break;

    if (line.indexOf("Content-Length:") >= 0)
    {
      int idx = line.indexOf(":");
      contentLength = line.substring(idx + 1).toInt();
    }
  }

  Serial.print("Content-Length: ");
  Serial.println(contentLength);

  if (contentLength <= 0 || contentLength > MAX_IMAGE_SIZE)
  {
    Serial.println("Invalid content length");
    client.stop();
    return;
  }

  // ---- Read JPEG body ----
  int received = 0;

  while (received < contentLength)
  {
    if (client.available())
    {
      jpgBuffer[received++] = client.read();
    }
  }

  client.stop();

  Serial.print("JPEG bytes received: ");
  Serial.println(received);

  if (received != contentLength)
  {
    Serial.println("JPEG incomplete");
    return;
  }

  if (jpgBuffer[0] != 0xFF || jpgBuffer[1] != 0xD8)
  {
    Serial.println("Invalid JPEG header");
    return;
  }

  Serial.println("Decoding JPEG...");

  memset(imgBuffer, 0, sizeof(imgBuffer));

  TJpgDec.drawJpg(0, 0, jpgBuffer, received);

  lv_obj_invalidate(canvas);

  // Force LVGL refresh
  for(int i=0;i<200;i++)
  {
    lv_timer_handler();
    delay(5);
  }

  Serial.println("Image displayed.");
}

/* ================= SETUP ================= */
void setup()
{
  Serial.begin(115200);
  delay(2000);

  Serial.println("Starting...");

  Display.begin();

  // Create canvas
  canvas = lv_canvas_create(lv_scr_act());
  lv_canvas_set_buffer(canvas,
                       imgBuffer,
                       IMG_W,
                       IMG_H,
                       LV_COLOR_FORMAT_RGB565);

  lv_obj_center(canvas);

  // Configure JPEG decoder
  TJpgDec.setCallback(tft_output);
  TJpgDec.setJpgScale(1);
  TJpgDec.setSwapBytes(true);   // VERY IMPORTANT

  connectWiFi();

  fetchImage();   // Only once
}

/* ================= LOOP ================= */
void loop()
{
  // do nothing
}