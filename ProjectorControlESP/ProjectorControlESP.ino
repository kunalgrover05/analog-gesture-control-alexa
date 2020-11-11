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
#include <SinricPro.h>
#include <SinricProTV.h>

ESP8266WebServer server(80);    // Create a webserver object that listens for HTTP request on port 80

#define BAUD_RATE 115200

const uint16_t kIrLed = 4;  // ESP8266 GPIO pin to use: 4 (D2).
IRsend irsend(kIrLed);  // Set the GwPIO to be used to sending the message.
WiFiClient espClient;

// setup function for WiFi connection
void setupWiFi() {
  Serial.print("\r\n[Wifi]: Connecting");
  WiFi.config(staticIP, gateway, subnet);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(250);
  }
  IPAddress localIP = WiFi.localIP();
  Serial.printf("connected!\r\n[WiFi]: IP-Address is %d.%d.%d.%d\r\n", localIP[0], localIP[1], localIP[2], localIP[3]);
}

// Setup function
void setup() {
  Serial.begin(BAUD_RATE);
  setupWiFi();
  irsend.begin();

  setupServer();
  setupSinricPro();
}

void loop() {
  // Reconnect if disconnected
  if (WiFi.status() != WL_CONNECTED) {
    setupWiFi();
  }
  server.handleClient();
  SinricPro.handle();
}
