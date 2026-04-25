int ldrPin = A0;

void setup() {
  Serial.begin(9600);
  analogReadResolution(12);
}

void loop() {
  int lightValue = analogRead(ldrPin);

  Serial.print("Light Value: ");
  Serial.print(lightValue);

  if (lightValue > 1200) {
    Serial.println("  -> DARK");
  } 
  else if (lightValue < 500) {
    Serial.println("  -> BRIGHT");
  } 
  else {
    Serial.println("  -> MEDIUM");
  }

  delay(500);
}