#include <MCUFRIEND_kbv.h>
MCUFRIEND_kbv tft;

void setup() {
  Serial.begin(9600);
  uint16_t ID = tft.readID();
  Serial.print("ID = 0x");
  Serial.println(ID, HEX);

  tft.begin(0x9481);
  tft.fillScreen(0xF800); // RED
  delay(2000);
  tft.fillScreen(0x07E0); // GREEN
  delay(2000);
  tft.fillScreen(0x001F); // BLUE
}

void loop() {}
