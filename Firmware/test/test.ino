#define USE_SPECIAL
#define USE_MEGA_16BIT_SHIELD

#include <MCUFRIEND_kbv.h>
MCUFRIEND_kbv tft;

#define BLACK   0x0000
#define BLUE    0x001F
#define RED     0xF800
#define GREEN   0x07E0
#define WHITE   0xFFFF
#define YELLOW  0xFFE0

void setup() {
  Serial.begin(9600);
  delay(500);

  uint16_t ID = tft.readID();
  Serial.print("Detected ID = 0x");
  Serial.println(ID, HEX);

  // Try common controllers
  if (ID == 0xD3D3 || ID == 0xFFFF || ID == 0x0000) {
    Serial.println("Trying common drivers...");
    
    // Try 9341 first (most common)
    tft.begin(0x9341);
  } 
  else {
    tft.begin(ID);
  }

  tft.setRotation(0);

  // Color test sequence
  tft.fillScreen(RED);
  delay(1000);

  tft.fillScreen(GREEN);
  delay(1000);

  tft.fillScreen(BLUE);
  delay(1000);

  tft.fillScreen(WHITE);
  delay(1000);

  tft.fillScreen(BLACK);
  delay(1000);

  // Draw simple text
  tft.setTextColor(YELLOW);
  tft.setTextSize(3);
  tft.setCursor(40, 100);
  tft.print("WORKING!");
}

void loop() {
}
