#include <DHT.h>

#define DHTPIN 7
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  delay(3000);
  dht.begin();
  Serial.println("DHT22 Started");
}

void loop() {
  delay(4000);   // Longer delay

  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Reading failed!");
  } else {
    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.print(" % | Temperature: ");
    Serial.print(temperature);
    Serial.println(" °C");
  }
}