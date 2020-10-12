/**
 * Uses SinricPro's Alexa Smart home skill to send commands to devices.
 * Used for basic functionality such as On/Off
 */
bool onPowerState(const String &deviceId, bool &state) {
  Serial.printf("TV turned %s\r\n", state?"on":"off");
  if (state) {
      irsend.sendNEC(0xFF15EA);
  } else {
      irsend.sendNEC(0xFF15EA);
      delay(1000);
      irsend.sendNEC(0xFF15EA);
  }
  return true; 
}

void setupSinricPro() {
  SinricProTV& myTV = SinricPro[TV_ID];
  
  // set callback functions to device
  myTV.onPowerState(onPowerState);

  // setup SinricPro
  SinricPro.onConnected([](){ Serial.printf("Connected to SinricPro\r\n"); }); 
  SinricPro.onDisconnected([](){ Serial.printf("Disconnected from SinricPro\r\n"); });
  SinricPro.begin(APP_KEY, APP_SECRET);
}
