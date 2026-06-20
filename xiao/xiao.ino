#include <ArduinoJson.h>
#include <WebServer.h>
#include <WiFi.h>

const char* AP_SSID = "HWLab-XIAO";
const char* AP_PASS = "hwlab1234";

WebServer server(80);

String lastCommand = "none";
bool ledOn = false;
unsigned long commandCount = 0;

#ifndef LED_BUILTIN
#define LED_BUILTIN 21
#endif

void setLed(bool on) {
  ledOn = on;
  digitalWrite(LED_BUILTIN, on ? LOW : HIGH);
}

void sendJson(JsonDocument& doc, int status = 200) {
  String body;
  serializeJson(doc, body);
  server.send(status, "application/json", body);
}

void addStatus(JsonDocument& doc) {
  doc["ok"] = true;
  doc["ssid"] = AP_SSID;
  doc["ip"] = WiFi.softAPIP().toString();
  doc["uptime_ms"] = millis();
  doc["last_command"] = lastCommand;
  doc["command_count"] = commandCount;
  doc["led_on"] = ledOn;
}

void handleStatus() {
  StaticJsonDocument<256> doc;
  addStatus(doc);
  sendJson(doc);
}

void handleGetCommand() {
  StaticJsonDocument<128> doc;
  doc["command"] = lastCommand;
  doc["led_on"] = ledOn;
  sendJson(doc);
}

bool applyCommand(const String& command) {
  if (command.length() == 0) {
    return false;
  }

  lastCommand = command;
  commandCount += 1;

  if (command == "thumbs_up" || command == "toggle") {
    setLed(!ledOn);
  } else if (command == "true" || command == "on") {
    setLed(true);
  } else if (command == "false" || command == "off") {
    setLed(false);
  }

  return true;
}

void handleSetCommand() {
  String command;

  if (server.hasArg("plain") && server.arg("plain").length() > 0) {
    StaticJsonDocument<128> request;
    DeserializationError error = deserializeJson(request, server.arg("plain"));
    if (error) {
      StaticJsonDocument<128> doc;
      doc["ok"] = false;
      doc["error"] = "invalid_json";
      sendJson(doc, 400);
      return;
    }
    command = request["command"] | "";
  } else if (server.hasArg("command")) {
    command = server.arg("command");
  }

  if (!applyCommand(command)) {
    StaticJsonDocument<128> doc;
    doc["ok"] = false;
    doc["error"] = "missing_command";
    sendJson(doc, 400);
    return;
  }

  StaticJsonDocument<256> doc;
  addStatus(doc);
  sendJson(doc);
}

void handleNotFound() {
  StaticJsonDocument<192> doc;
  doc["ok"] = false;
  doc["error"] = "not_found";
  doc["endpoints"] = "GET /status, GET /command, POST /command, POST /set";
  sendJson(doc, 404);
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  setLed(false);

  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASS);

  Serial.println();
  Serial.println("HW Lab XIAO access point started");
  Serial.print("SSID: ");
  Serial.println(AP_SSID);
  Serial.print("IP: ");
  Serial.println(WiFi.softAPIP());

  server.on("/", HTTP_GET, handleStatus);
  server.on("/status", HTTP_GET, handleStatus);
  server.on("/command", HTTP_GET, handleGetCommand);
  server.on("/command", HTTP_POST, handleSetCommand);
  server.on("/set", HTTP_POST, handleSetCommand);
  server.onNotFound(handleNotFound);
  server.begin();
}

void loop() {
  server.handleClient();
}
