#include <DHT.h>
#include <math.h>

#define DHTPIN 2
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

/* ---------- Global Variables ---------- */
float T = 0;
float RH = 0;
float dewPoint = 0;
float absoluteHumidity = 0;

bool warmup_done = false;
bool baseline_stable = false;
bool env_in_range = false;
bool run_valid = false;

unsigned long warmupStart;
const unsigned long warmupTime = 30000;  // 30 sec warmup

float lastT = 0;
float lastRH = 0;

/* ---------- Dew Point ---------- */
float calculateDewPoint(float T, float RH) {
  float a = 17.27;
  float b = 237.7;
  float gamma = (a * T / (b + T)) + log(RH / 100.0);
  return (b * gamma) / (a - gamma);
}

/* ---------- Absolute Humidity (g/m3) ---------- */
float calculateAbsoluteHumidity(float T, float RH) {
  float es = 6.112 * exp((17.67 * T) / (T + 243.5));
  float AH = (es * RH * 2.1674) / (273.15 + T);
  return AH;
}

/* ---------- ENV Range Check ---------- */
bool checkEnvRange(float T, float RH) {
  return (T > 20 && T < 35 && RH > 30 && RH < 75);
}

/* ---------- Baseline Stability Check ---------- */
bool checkBaselineStable(float T, float RH) {
  float dT = abs(T - lastT);
  float dRH = abs(RH - lastRH);

  lastT = T;
  lastRH = RH;

  return (dT < 0.2 && dRH < 0.5);
}

/* ---------- Setup ---------- */
void setup() {
  Serial.begin(115200);
  dht.begin();
  warmupStart = millis();
}

/* ---------- Loop ---------- */
void loop() {

  T = dht.readTemperature();
  RH = dht.readHumidity();

  if (isnan(T) || isnan(RH)) {
    Serial.println("Sensor read error");
    return;
  }

  dewPoint = calculateDewPoint(T, RH);
  absoluteHumidity = calculateAbsoluteHumidity(T, RH);

  // Warmup logic
  if (millis() - warmupStart > warmupTime) {
    warmup_done = true;
  }

  if (warmup_done) {
    baseline_stable = checkBaselineStable(T, RH);
  }

  env_in_range = checkEnvRange(T, RH);

  run_valid = warmup_done && baseline_stable && env_in_range;

  /* ---------- JSON Output ---------- */
  Serial.print("{");
  Serial.print("\"T\":"); Serial.print(T, 2); Serial.print(",");
  Serial.print("\"RH\":"); Serial.print(RH, 2); Serial.print(",");
  Serial.print("\"dewpoint\":"); Serial.print(dewPoint, 2); Serial.print(",");
  Serial.print("\"absolute_humidity\":"); Serial.print(absoluteHumidity, 2); Serial.print(",");
  Serial.print("\"warmup_done\":"); Serial.print(warmup_done ? "true" : "false"); Serial.print(",");
  Serial.print("\"baseline_stable\":"); Serial.print(baseline_stable ? "true" : "false"); Serial.print(",");
  Serial.print("\"env_in_range\":"); Serial.print(env_in_range ? "true" : "false"); Serial.print(",");
  Serial.print("\"run_valid\":"); Serial.print(run_valid ? "true" : "false");
  Serial.println("}");

  delay(2000);
}
