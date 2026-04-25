#include <Arduino_GigaDisplay.h>

GigaDisplay display;

void setup() {
  display.begin();
  display.fillScreen(0xF800);  // Red
}

void loop() {}
