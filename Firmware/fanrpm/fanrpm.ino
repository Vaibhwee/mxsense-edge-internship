const int tachPin = 2;

void setup() {
  Serial.begin(115200);
  pinMode(tachPin, INPUT_PULLUP);
}

void loop() {

  int pulses = 0;
  int lastState = digitalRead(tachPin);

  unsigned long startTime = millis();

  while (millis() - startTime < 1000) {   // measure for 1 second
    int currentState = digitalRead(tachPin);

    if (currentState != lastState) {
      pulses++;
      lastState = currentState;
    }
  }

  int rpm = (pulses / 40) * 60;

  Serial.print("RPM: ");
  Serial.println(rpm);
}