#include <WiFi.h>
#include <WiFiSSLClient.h>
#include <PubSubClient.h>
#include "DHT.h"

#define DHTPIN 2
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "rtbi";
const char* password = "rtbi@27.";

const char* mqtt_server = "a2rdkdsgtykmsp-ats.iot.ap-south-1.amazonaws.com";

WiFiSSLClient net;
PubSubClient client(net);

// ---------- ROOT CA ----------
const char* root_ca = R"EOF(
-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv
b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj
ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM
9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw
IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6
VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L
93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm
jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA
A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI
U5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs
N+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv
o/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU
5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy
rqXRfboQnoZsG4q5WTP468SQvvG5
-----END CERTIFICATE-----
)EOF";

// ---------- DEVICE CERT ----------
const char* device_cert = R"KEY(
-----BEGIN CERTIFICATE-----
MIIDWTCCAkGgAwIBAgIUTdIaQSErAlZhRmJOas17OdWWYZ4wDQYJKoZIhvcNAQEL
BQAwTTFLMEkGA1UECwxCQW1hem9uIFdlYiBTZXJ2aWNlcyBPPUFtYXpvbi5jb20g
SW5jLiBMPVNlYXR0bGUgU1Q9V2FzaGluZ3RvbiBDPVVTMB4XDTI2MDMwMjEwMjQ1
NVoXDTQ5MTIzMTIzNTk1OVowHjEcMBoGA1UEAwwTQVdTIElvVCBDZXJ0aWZpY2F0
ZTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAONfbsds9XQCKajveN+m
E5nUI8/CA9x1dRV4eqctb65aoypODMUlg+XNN5ylBc7bW0kWX/653PRVWOeNlEib
FW/VnUTd+70AVfSX4URhVHq8D8qyLhfBV0SaYBkV44GpiKzdfIsmAg4+heGfMC6p
lI/ofmBhoECj8N4FCxiRgPJXuqAFGXfK6l1Lp8KP1QZdnlx/ujixrBSKTFB5+hck
G5ph4iyCm2WNrqJz4TFkLymMQCf4KfeKLhkudpzPRt68W+f071lXkM3gzIYZLZ4h
Od27VqYR/fv4yrStFQsiIg3jjPYsk/IeDH8+9hRMFtKn1JeBC8iRz/r6gxRaE/nU
hK8CAwEAAaNgMF4wHwYDVR0jBBgwFoAUchfvZvrgvx0VDauDz7gTcUM5b+wwHQYD
VR0OBBYEFLLrla9/o6SqPmLWgDyf0T42SxLBMAwGA1UdEwEB/wQCMAAwDgYDVR0P
AQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4IBAQA4Q74CwYPOjHjqKH584eU1a5Pv
p5Rexy29O2bHqcdJcgMpVs0ke/v0TbojL2byQHI9eJVJMaCpA0c7ielZ/PoS6uJd
l9QkKrcUmqHKuSSLMw76tIeM33vA9es/JkR+gKLt9bNEYKKUeAqVlAzaTmH0MLih
2kfTyiWNcdWVENqnxxn+avc9rxzEpBQJYXY+/hwNdTGliFqFRN/alQWkzM20ZycQ
8zJdySysHmU2Ih3T6DVpFrUBbk1JUhLzZ4mLSyUul0z5pA5H0j3f2b1NM9OtXomL
AIk74S6htgGXavNvDszNrEpa6UI6vTxCenT8Dee9cxJ7Vn1XICzgAdyRGFfZ
-----END CERTIFICATE-----
)KEY";

// ---------- PRIVATE KEY ----------
const char* private_key = R"KEY(
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA419ux2z1dAIpqO9436YTmdQjz8ID3HV1FXh6py1vrlqjKk4M
xSWD5c03nKUFzttbSRZf/rnc9FVY542USJsVb9WdRN37vQBV9JfhRGFUerwPyrIu
F8FXRJpgGRXjgamIrN18iyYCDj6F4Z8wLqmUj+h+YGGgQKPw3gULGJGA8le6oAUZ
d8rqXUunwo/VBl2eXH+6OLGsFIpMUHn6FyQbmmHiLIKbZY2uonPhMWQvKYxAJ/gp
94ouGS52nM9G3rxb5/TvWVeQzeDMhhktniE53btWphH9+/jKtK0VCyIiDeOM9iyT
8h4Mfz72FEwW0qfUl4ELyJHP+vqDFFoT+dSErwIDAQABAoIBAQDYk3l4uf+fLcQy
50/ScGXxO9GUvrBg2Pzao7To8u2TPUB4NnoRe6eESBJ1wfajT+xG1OpBPxcJIRab
EQ+yjQ5BRU8VXwC/yccWQWlQcgk/E01TfJ9M/1u5u/ZXTrMzOaI3To2oGV8R5Fow
TCpf+CXLYeCmu7cie0YepN0p3MbfjgdVlIk+/ElTaJ+9BuzzrygC3EFy5Jtja7rX
VfT8wG37lVLrc4x84Ecmy0+AkAwOzzhSIysW8W5hku+R30+pKgL4JM5XuATXZpV7
mLdc6UNKKi0WQvESqJriGKOdeuZL+mWhq5IiNnNFnMYap749+MreJAcsJPzwp5QA
Cqg2Xm+xAoGBAPJIyKu7Q3qlGqZCSjQ1jiaWsUKEx6Y18vh1tgBOrY5fHnuF0BPW
IlvVbgXYJML0FuAvakA6Zk2woO5ImZNx/87boFeKHhU+0E1OXkOvJ0/BBewrK0Bv
F53b0bLubU9qHlO5RBPC6mVhPi0gIj6cychoN3H4Rquu/+/Djc68/9RJAoGBAPA+
jI2cWupgDPAKb/+9xPd2hsL/yxODXZsj/g5EsuO+lfiRJBnG3mY23q8BgZvoP9MU
BTMf1bplnpEyJ/1DlL4m5rcMUptQjWc9JpZ3AmkpOQaYpB6d3OImaVRhux5fN3Cf
64YeiptTqMnf7RCzp5/7cKLfMyBenHw+0iZvfKE3AoGBAK/axExhj4jlbYJfexyK
ArNfjSmK1p59ae2NAp0WfkJoJ+fgKDc9pZKiR0lWqNgX8sKlp6kWukqJeUV6zH2I
sPOj1a20QkGJZge2ahUWfKIWqAXTD4GlIK8jbgFBrXWGwJxkTFVLlHYhLs/yEuj/
RDaB7jx6yFC0pG+SsMrtw4KBAoGAbBT3zs3E6SSFLYjEkl2hu2MLhbbmecTj2+P5
bBnkESmw9r71atNZQsr0q+8VjDqUXDXpkPKFiPImwFO8Qeihhlqh+UAF+fHna8bL
EW5BG2Z8TUdmro9+zA9T266MLEHSA00u/IvI99BPY2LmmFj61LKeHegkbC+kXxE0
Ii6N90kCgYBFAn2z8+xxHHqtPVXTYDq2g8ztLMPZqqI9JAzvee4AD+c9NijXQTJ2
3WxLWVWFePmoyxxhfD5LRcPtGMVNi1UetUIur2/yWJnKGyXEGuoWkCQD29uKKwGs
G/N1C1pZpYzgrWp8qWEBpkFA3/eENPWp84xK9qPvfj11fnMOyZKvfg==
-----END RSA PRIVATE KEY-----
)KEY";

void connectAWS() {
  while (!client.connected()) {
    Serial.println("Connecting to AWS...");
    if (client.connect("dht22")) {
      Serial.println("Connected to AWS!");
    } else {
      Serial.print("Failed, rc=");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  net.setCACert(root_ca);
  net.setCertificate(device_cert);
  net.setPrivateKey(private_key);

  client.setServer(mqtt_server, 8883);
}

void loop() {

  if (!client.connected()) {
    connectAWS();
  }

  client.loop();

  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();
  
  unsigned long ts = millis();

  String payload = "{";
  payload += "\"device_id\":\"dht22\",";
  payload += "\"temperature\":" + String(temp) + ",";
  payload += "\"humidity\":" + String(hum) + ",";
  payload += "\"timestamp\":" + String(ts);
  payload += "}";

  Serial.println(payload);   

  client.publish("dht22/data", payload.c_str());  

  delay(5000);
}