/*
 * Capture images from OV7675 on Arduino GIGA and send them over Web Serial.
 */

#include "camera.h"
#include "ov767x.h"

// Use OV7675 camera
OV7675 ov767x;
Camera cam(ov767x);

#define IMAGE_MODE CAMERA_RGB565

constexpr uint16_t CHUNK_SIZE = 512;
constexpr uint8_t RESOLUTION  = CAMERA_R320x240;

constexpr uint8_t CONFIG_SEND_REQUEST = 2;
constexpr uint8_t IMAGE_SEND_REQUEST = 1;

uint8_t START_SEQUENCE[4] = {0xfa, 0xce, 0xfe, 0xed};
uint8_t STOP_SEQUENCE[4]  = {0xda, 0xbb, 0xad, 0x00};

FrameBuffer fb;

/* Blink helper */
void blinkLED(int ledPin, uint32_t count = 0xFFFFFFFF) {
  while (count--) {
    digitalWrite(ledPin, LOW);
    delay(50);
    digitalWrite(ledPin, HIGH);
    delay(50);
  }
}

void setup() {

  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(LEDR, OUTPUT);

  digitalWrite(LED_BUILTIN, HIGH);
  digitalWrite(LEDR, HIGH);

  Serial.begin(115200);

  // Initialize camera
  if (!cam.begin(RESOLUTION, IMAGE_MODE, 30)) {
    blinkLED(LEDR); // error indicator
  }

  blinkLED(LED_BUILTIN, 5);
}

/* Send chunk over serial */
void sendChunk(uint8_t* buffer, size_t bufferSize){
  Serial.write(buffer, bufferSize);
  Serial.flush();
  delay(1);
}

/* Capture and send frame */
void sendFrame(){

  if (cam.grabFrame(fb, 3000) == 0) {

    byte* buffer = fb.getBuffer();
    size_t bufferSize = cam.frameSize();

    digitalWrite(LED_BUILTIN, LOW);

    sendChunk(START_SEQUENCE, sizeof(START_SEQUENCE));

    for(size_t i = 0; i < bufferSize; i += CHUNK_SIZE){
      size_t chunkSize = min(bufferSize - i, CHUNK_SIZE);
      sendChunk(buffer + i, chunkSize);
    }

    sendChunk(STOP_SEQUENCE, sizeof(STOP_SEQUENCE));

    digitalWrite(LED_BUILTIN, HIGH);

  } else {
    blinkLED(LEDR, 20);
  }
}

/* Send camera configuration */
void sendCameraConfig(){

  Serial.write(IMAGE_MODE);
  Serial.write(RESOLUTION);
  Serial.flush();
  delay(1);
}

void loop() {

  if(!Serial) return;

  if(!Serial.available()) return;

  byte request = Serial.read();

  switch(request){

    case IMAGE_SEND_REQUEST:
      sendFrame();
      break;

    case CONFIG_SEND_REQUEST:
      sendCameraConfig();
      break;
  }
}