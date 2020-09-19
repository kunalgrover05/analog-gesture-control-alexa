#include <Arduino.h>
#include "Secrets.h"

#ifdef ESP8266
#include <ESP8266WiFi.h>
#endif
#ifdef ESP32
#include <WiFi.h>
#endif

#include <IRsend.h>
#include <ESP8266WebServer.h>

#define WIFI_SSID SECRET_SSID
#define WIFI_PASS SECRET_PASSWORD
#define BAUD_RATE 115200

ESP8266WebServer server(80);    // Create a webserver object that listens for HTTP request on port 80
const uint16_t kIrLed = 4;  // ESP8266 GPIO pin to use: 4 (D2).
IRsend irsend(kIrLed);  // Set the GwPIO to be used to sending the message.
WiFiClient espClient;

// Callback for volume change
bool onAdjustVolume(int &volumeDelta) {
  for (int i = 0; i < abs(volumeDelta); ++i) {
    if (volumeDelta > 0) {
      irsend.sendNEC(0x00FF31CE); // Volume up
    } else {
      irsend.sendNEC(0x00FF39C6); // Volume down
    }
    delay(100);
  }
  return true;
}

// setup function for WiFi connection
void setupWiFi() {
  Serial.printf("\r\n[Wifi]: Connecting");
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.printf(".");
    delay(250);
  }

  IPAddress localIP = WiFi.localIP();
  Serial.printf("connected!\r\n[WiFi]: IP-Address is %d.%d.%d.%d\r\n", localIP[0], localIP[1], localIP[2], localIP[3]);
}

void handleVolume() {
  if (!server.hasArg("delta")) { // If the POST request doesn't have volume delta, invalid request return 400
    server.send(400, "text/plain", "400: Invalid Request");
    return;
  }

  int delta = server.arg("delta").toInt();
  onAdjustVolume(delta);
  server.send(200, "text/html", "<h1>Done</h1>");
  Serial.println("Done");
}

void handleNotFound() {
  server.send(404, "text/plain", "404: Not found"); // Send HTTP status 404 (Not Found) when there's no handler for the URI in the request
}

// Setup function
void setup() {
  setupWiFi();
  irsend.begin();

  server.on("/volume", HTTP_POST, handleVolume);
  server.onNotFound(handleNotFound);
  server.begin();
}

void loop() {
  server.handleClient();
}
