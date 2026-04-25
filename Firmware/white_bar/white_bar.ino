#include <WiFi.h>
#include <Arduino_H7_Video.h>
#include <lvgl.h>
#include <TJpg_Decoder.h>

/* ================= DISPLAY ================= */
Arduino_H7_Video Display(800, 480, GigaDisplayShield);

/* ================= WIFI ================= */
const char* ssid = "rtbi";
const char* password = "rtbi@27.";
const char* esp_ip = "192.168.68.134";   // <<< PUT YOUR ESP IP HERE

WiFiClient client;

/* ================= IMAGE ================= */
#define IMG_W 320
#define IMG_H 240
#define MAX_IMAGE_SIZE 60000

uint8_t jpgBuffer[MAX_IMAGE_SIZE];
uint32_t jpgSize = 0;

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

/* ================= WIFI CONNECT ================= */
void connectWiFi()
{
  Serial.println("Connecting to WiFi");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nGIGA Connected!");
  Serial.println(WiFi.localIP());
}

/* ================= FETCH IMAGE ================= */
void fetchImage()
{
  Serial.println("Connecting to ESP...");

  if (!client.connect(esp_ip, 80))
  {
    Serial.println("ESP Connection failed");
    return;
  }

  Serial.println("Connected to ESP");

  client.print("GET / HTTP/1.1\r\n");
  client.print("Host: ");
  client.print(esp_ip);
  client.print("\r\n");
  client.print("Connection: close\r\n\r\n");

  unsigned long timeout = millis();
  while (!client.available())
  {
    if (millis() - timeout > 5000)
    {
      Serial.println("Timeout");
      client.stop();
      return;
    }
  }

  int contentLength = 0;

  while (client.available())
  {
    String line = client.readStringUntil('\n');

    if (line.startsWith("Content-Length:"))
    {
      contentLength = line.substring(15).toInt();
    }

    if (line == "\r") break;
  }

  Serial.print("Content-Length: ");
  Serial.println(contentLength);

  if (contentLength <= 0 || contentLength > MAX_IMAGE_SIZE)
  {
    Serial.println("Invalid Content-Length");
    client.stop();
    return;
  }

  jpgSize = 0;

  while (jpgSize < contentLength)
  {
    if (client.available())
    {
      jpgBuffer[jpgSize++] = client.read();
    }
  }

  client.stop();

  Serial.print("Bytes received: ");
  Serial.println(jpgSize);

  Serial.print("First byte: ");
  Serial.println(jpgBuffer[0], HEX);
  Serial.print("Second byte: ");
  Serial.println(jpgBuffer[1], HEX);

  if (jpgBuffer[0] != 0xFF || jpgBuffer[1] != 0xD8)
  {
    Serial.println("JPEG CORRUPTED");
    return;
  }

  memset(imgBuffer, 0, sizeof(imgBuffer));

  TJpgDec.drawJpg(0, 0, jpgBuffer, jpgSize);

  lv_obj_invalidate(canvas);

  Serial.println("Display Updated");
}

/* ================= SETUP ================= */
void setup()
{
  Serial.begin(115200);

  Display.begin();

  canvas = lv_canvas_create(lv_scr_act());

  lv_canvas_set_buffer(canvas,
                       imgBuffer,
                       IMG_W,
                       IMG_H,
                       LV_COLOR_FORMAT_RGB565);

  lv_obj_center(canvas);

  TJpgDec.setCallback(tft_output);
  TJpgDec.setJpgScale(1);

  connectWiFi();
}

/* ================= LOOP ================= */
void loop()
{
  fetchImage();
  lv_timer_handler();
  delay(3000);
}