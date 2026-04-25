#include <WiFi.h>
#include <ArduinoMqttClient.h>

const char* ssid = "rtbi";
const char* password = "rtbi@27.";

const char* broker = "a2rdkdsgtykmsp-ats.iot.ap-south-1.amazonaws.com";
const int port = 8883;

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);
// ----- AMAZON ROOT CA -----
const char* root_ca = R"EOF(
PASTE_ROOT_CA_HERE
)EOF";

// ----- DEVICE CERTIFICATE -----
const char* device_cert = R"KEY(
PASTE_DEVICE_CERT_HERE
)KEY";

// ----- PRIVATE KEY -----
const char* private_key = R"KEY(
PASTE_PRIVATE_KEY_HERE
)KEY";
void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected!");
    wifiClient.setCACert(root_ca);
    wifiClient.setCertificate(device_cert);
    wifiClient.setPrivateKey(private_key);
    Serial.println("Connecting to AWS...");

  if (!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code: ");
    Serial.println(mqttClient.connectError());
  } else {
    Serial.println("Connected to AWS!");
  }
}

void loop() {}
