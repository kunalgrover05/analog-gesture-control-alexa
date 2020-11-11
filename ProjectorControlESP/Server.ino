/**
 * Runs a local HTTP server which takes in commands to change volume.
 */
// Callback for volume change
bool onAdjustVolume(int &volumeDelta) {
  for (int i = 0; i < abs(volumeDelta); ++i) {
    if (volumeDelta > 0) {
      irsend.sendNEC(0x00FF31CE); // Volume up
    } else {
      irsend.sendNEC(0x00FF39C6); // Volume down
    }
    delay(120);
  }
  return true;
}

void handleNotFound() {
  Serial.println("Not found");
  server.send(404); // Send HTTP status 404 (Not Found) when there's no handler for the URI in the request
}

void handleVolume() {
  Serial.println("Got request");
  unsigned long start = millis();
  if (!server.hasArg("delta")) { // If the POST request doesn't have volume delta, invalid request return 400
    server.send(400);
    return;
  }

  int delta = server.arg("delta").toInt();
  onAdjustVolume(delta);
  server.send(200);

  unsigned long timeTaken = millis() - start;
  Serial.printf("Done in %u ms\n", timeTaken);
  Serial.println(ESP.getFreeHeap());
}

void setupServer() {
  server.on("/volume", HTTP_GET, handleVolume);
  server.onNotFound(handleNotFound);
  server.begin();
}
