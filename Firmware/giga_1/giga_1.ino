#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "rtbi";
const char* password = "rtbi@27.";

const char* mqtt_server = "broker.hivemq.com";

WiFiClient wifiClient;
PubSubClient client(wifiClient);

void connectWiFi() {
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void connectMQTT() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");

    if (client.connect("GIGA_R1_Client")) {
      Serial.println("Connected to MQTT broker!");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 3 sec...");
      delay(3000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(2000);

  connectWiFi();

  client.setServer(mqtt_server, 1883);
}

void loop() {

  if (!client.connected()) {
    connectMQTT();
  }

  client.loop();

  float temperature = random(200, 350) / 10.0;
  int pressure = random(980, 1050);
  int gas = random(200, 500);

  String payload = "{";
  payload += "\"device_id\":\"GIGA_R1_01\",";
  payload += "\"temperature\":" + String(temperature) + ",";
  payload += "\"pressure\":" + String(pressure) + ",";
  payload += "\"gas\":" + String(gas);
  payload += "}";

  Serial.println("Publishing:");
  Serial.println(payload);

  client.publish("giga/test/data", payload.c_str());

  delay(5000);
}
