#include <MCUFRIEND_kbv.h>
#include <Adafruit_GFX.h>

MCUFRIEND_kbv tft;

#define RED     0xF800
#define GREEN   0x07E0
#define BLUE    0x001F
#define BLACK   0x0000
#define WHITE   0xFFFF

void setup() {
  uint16_t ID = 0x9481;   // Force ILI9481
  tft.begin(ID);
  tft.setRotation(1);

  tft.fillScreen(RED);
  delay(1000);
  tft.fillScreen(GREEN);
  delay(1000);
  tft.fillScreen(BLUE);
  delay(1000);

  tft.fillScreen(BLACK);
  tft.setTextColor(WHITE);
  tft.setTextSize(3);
  tft.setCursor(40, 120);
  tft.println("ILI9481 OK");
}

void loop() {}
