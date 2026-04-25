#include <MCUFRIEND_kbv.h>
#include <Adafruit_GFX.h>

MCUFRIEND_kbv tft;

void setup() {
  Serial.begin(9600);
  uint16_t ID = tft.readID();   // Read LCD driver ID
  Serial.print("LCD ID: 0x");
  Serial.println(ID, HEX);

  if (ID == 0x0) {
    ID = 0x9481;   // Force ILI9481 if not detected
  }

  tft.begin(ID);
  tft.setRotation(1);  // Landscape mode

  tft.fillScreen(BLACK);
  tft.setTextColor(WHITE);
  tft.setTextSize(3);
  tft.setCursor(50, 120);
  tft.println("Hello Vaibhwee!");
}

void loop() {
}
