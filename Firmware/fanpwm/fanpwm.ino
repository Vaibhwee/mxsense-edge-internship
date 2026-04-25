const int fanPWM = 9;

void setup() {
  pinMode(fanPWM, OUTPUT);
}

void loop() {

  analogWrite(fanPWM, 50);  
  delay(4000);

  analogWrite(fanPWM, 120);  // medium
  delay(4000);

  analogWrite(fanPWM, 255);  // full speed
  delay(4000);
}
