#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

/* WIFI */
const char* ssid = "rtbi";
const char* password = "rtbi@27.";

/* AWS */
const char* mqtt_server = "a2rdkdsgtykmsp-ats.iot.ap-south-1.amazonaws.com";
const int mqtt_port = 8883;
const char* mqtt_topic = "mxsense/ch3/test";
const char* thingName = "dummy_esp32";

WiFiClientSecure net;
PubSubClient client(net);

/* ROOT CA */
static const char* root_ca = R"EOF(
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

/* DEVICE CERT */
static const char* device_cert = R"KEY(
-----BEGIN CERTIFICATE-----
MIIDWTCCAkGgAwIBAgIUWd0rDbW8VXqLLyJ7TRR2Dj7xe6QwDQYJKoZIhvcNAQEL
BQAwTTFLMEkGA1UECwxCQW1hem9uIFdlYiBTZXJ2aWNlcyBPPUFtYXpvbi5jb20g
SW5jLiBMPVNlYXR0bGUgU1Q9V2FzaGluZ3RvbiBDPVVTMB4XDTI2MDIyNDEwMTY0
N1oXDTQ5MTIzMTIzNTk1OVowHjEcMBoGA1UEAwwTQVdTIElvVCBDZXJ0aWZpY2F0
ZTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALOHnGwcVrWF+vtSwFy0
B4tPfe3Pmab+EpQySB06VUmsF8toOde1dK+FkEwA8c7tpn2v+wM+ploGmmJ1FYs9
lfj3wK3bnZwMgntCAhfxG6Z3KJj4NZhgbRt0HFyZKzmlXX2yyumwBYROrSBUScLd
voBA9jHkr1iqE/RxlgyNFfWGTLepbGrdfQEn3HHltYjfGyeER8GRMkGp/KIhjerU
x+GpOWf4eCFmOUUuAAs3DaQHOi/NeLNlqJ9p4a1oDKf4krnn/7gkCFv2w+iBvn/9
Wou5UomY3wGhTXqXOIhvpzfPqOdEmzqKEl//YF5zLSltX2j5zvkwmn9NdtiZLoZS
1q0CAwEAAaNgMF4wHwYDVR0jBBgwFoAULaZ9f6QUfnwtgZge9WTm9sPvUykwHQYD
VR0OBBYEFOTL18gkR77qXgCFw/l6nZ5lYQLvMAwGA1UdEwEB/wQCMAAwDgYDVR0P
AQH/BAQDAgeAMA0GCSqGSIb3DQEBCwUAA4IBAQCO/8hrggSX4Fm3QFSPHF9bleea
EkWGt5qpX/FJivbXMwhap55k0hH1k+2KO/GUMOH1q7iZAW6KwsoQ7h+fBK3DrZpV
Ckukvfcz50XJgoOWYREXgC2pCqGyM5CHu6GeX/w758rGTAiA6qndW4VFJHi4qhLd
hOwIIHn6WXv3WdEHHSx0TbobdRjM5Nw6ePXt6R5yxO03M/RcSY0tFu62nW/k/qMJ
XCjqDOeODFk0fOPZEdUWlwSz2GnniZWc9gzPvY4lnFduGy0Q227cddPnHFjt4XSJ
XtSuvspGMkH5VpJF3ett2ndqEmoWsRGnKlMB5mVt0QejiOKGemwyqQ1nPFbt
-----END CERTIFICATE-----
)KEY";

/* PRIVATE KEY */
static const char* private_key = R"KEY(
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAs4ecbBxWtYX6+1LAXLQHi0997c+Zpv4SlDJIHTpVSawXy2g5
17V0r4WQTADxzu2mfa/7Az6mWgaaYnUViz2V+PfArdudnAyCe0ICF/EbpncomPg1
mGBtG3QcXJkrOaVdfbLK6bAFhE6tIFRJwt2+gED2MeSvWKoT9HGWDI0V9YZMt6ls
at19ASfcceW1iN8bJ4RHwZEyQan8oiGN6tTH4ak5Z/h4IWY5RS4ACzcNpAc6L814
s2Won2nhrWgMp/iSuef/uCQIW/bD6IG+f/1ai7lSiZjfAaFNepc4iG+nN8+o50Sb
OooSX/9gXnMtKW1faPnO+TCaf0122JkuhlLWrQIDAQABAoIBABGgBKlQdurHRoaZ
7yyqt/rjSPep4+nTE7vc29uSuIDNFmDv0I3u0I/SywHLLfIkvq2kMz50ThyUfV+h
IwZSe4C/wfjPkL+bMswrBM2Y7CABnsi1xX06KjwBwC8PEoFMTMtkXCtpDoGYv8Jm
w/8Pif5JYmIvk09fEypyZErDJx69cHzH2Vkd5rvia0f2KEwcQgpv1PRXBpkUM2gK
BJm7gKgqBlGeJB9l4UECCgQc/ASGJAoOl6mFU+/XxPz84NC/aS+UcJBlNGbQy98W
3jcYecofVjBz2zB/Y/ave0w6fv57ndmCmb8rwN6RZ1CwkqRMEQgBFyp2vyPX1q8n
q1VaD/kCgYEA2mfZXDFxI4mb/Vl3ajLItmml728P+9J0/GwWYdv3tWo8G5bBm0eY
qTeR38G3fJ/C7EkfwQDcxvWzncnhxdUZdueiVrAz8bR45/od33yRvgdVRQbXpyWJ
Vdr1R5EFI/j07XA0OQZ++4HYvlenO+Rbu+zvvpwNqIF7lFz6a4eEKrcCgYEA0m6s
4paO+LWme8SUKaoZVPUuBqtQUJx0Z5KJCbDMlYsiX80O2H4M4ViFKskFVKMYwM2B
zVaBBmGMDmH6Yz9n55RL3JBXqpZqGLuXJYUu8DVnx886B9xPLO/ytn0dMcyOpKlC
Yz80OqotFVSMTqir4tNASf7XSHful1KLU07OdbsCgYAhf7QzE9JKpRyr60EJpOhs
MiAlbV+CPHF9FgcI03hW9whpIuJnMsATlFZnf4rpLofzPfQE4mD6k00Ncp2SfnD9
b+HScgxFkmzJB+/1C2I/R1io0bfaB0PdS0w7wd6L+e93S7J23Kw1X2EjMMaRxSDc
3iaXkc/2fIW759bxD0QSWQKBgGMEfQlp+wCAyUP37hfk2GKns+6jcflchVGvHBiZ
PssnWxdlMBUiywDGXHMTgBShYiZnDSsIB1JvWC30YJOO5F+N4lx49ydn+6iDrM2U
689P8fONSSsluYPVrIm+OZyTOpO0qW518Sehp/EfhZ4FtEvZR6kJ51dMR9Kgnrqm
nHO9AoGBANl/d879vTg6Cd7gKi3GB2SGOal30jy1oqA3DwwSPX8m7U0Qk8r4ddhY
vpumS6Hl9BmEVRG1RqSiaiL2Uuo3vUrwkbgI+KFS9OAz1zM55rUExWODWdouID9N
P/CviEBF1CPtDCqvN0IOugR/X5Q9Fl352/Anwa0WmQIfjDp1WL3z
-----END RSA PRIVATE KEY-----
)KEY";


void connectAWS() {

  net.setCACert(root_ca);
  net.setCertificate(device_cert);
  net.setPrivateKey(private_key);

  client.setServer(mqtt_server, mqtt_port);

  Serial.print("Connecting to AWS IoT");

  while (!client.connected()) {

    if (client.connect(thingName)) {
      Serial.println(" Connected!");
    } 
    else {
      Serial.print(" Failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying...");
      delay(2000);
    }
  }
}

void setup() {

  Serial.begin(115200);
  delay(2000);
  Serial.println("\nBOOTED");

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }

  Serial.println(" Connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  connectAWS();
}

void loop() {

  if (!client.connected()) {
    connectAWS();
  }

  client.loop();

  String payload = "{";
  payload += "\"device_id\":\"dummy_esp32\",";
  payload += "\"status\":\"vision_ready\",";
  payload += "\"temperature\":28.5";
  payload += "}";

  client.publish(mqtt_topic, payload.c_str());

  Serial.println("Message Published:");
  Serial.println(payload);

  delay(5000);
}
