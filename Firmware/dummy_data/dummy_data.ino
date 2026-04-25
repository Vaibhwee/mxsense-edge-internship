#include <WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// Public MQTT broker
const char* mqtt_server = "broker.hivemq.com";

WiFiClient wifiClient;
PubSubClient client(wifiClient);

unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE  100
char msg[MSG_BUFFER_SIZE];

void setup() {
  Serial.begin(115200);
  
  // Connect WiFi
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected");
  Serial.println(WiFi.localIP());

  client.setServer(mqtt_server, 1883);
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (client.connect("GIGA_Dummy_Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 2000) {
    lastMsg = now;

    float dummyTemp = random(250, 350) / 10.0;
    float dummyHumidity = random(400, 800) / 10.0;

    snprintf(msg, MSG_BUFFER_SIZE,
             "{\"temp\":%.1f,\"humidity\":%.1f}",
             dummyTemp, dummyHumidity);

    Serial.print("Publishing message: ");
    Serial.println(msg);

    client.publish("giga/test/dummy", msg);
  }
}