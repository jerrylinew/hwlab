#include "HWLabSetup.h"

#include <WebServer.h>
#include <WiFi.h>

namespace {
WebServer server(80);
HWLabSetupConfig setupConfig;
CommandHandler onCommand = nullptr;
StatusBuilder onStatus = nullptr;
String serialBuffer;
String lastCommand = "none";
unsigned long commandCount = 0;

void sendJson(JsonDocument& doc, int status = 200) {
  String body;
  serializeJson(doc, body);
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.send(status, "application/json", body);
}

void sendSerialJson(JsonDocument& doc) {
  serializeJson(doc, Serial);
  Serial.println();
}

void addStatus(JsonDocument& doc) {
  doc["ok"] = true;
  doc["ssid"] = setupConfig.apSsid;
  doc["ip"] = WiFi.softAPIP().toString();
  doc["uptime_ms"] = millis();
  doc["last_command"] = lastCommand;
  doc["command_count"] = commandCount;
  doc["wifi_clients"] = WiFi.softAPgetStationNum();
  doc["free_heap"] = ESP.getFreeHeap();
  doc["transport"] = "xiao";
  if (onStatus) onStatus(doc);
}

void sendStatusHttp() {
  StaticJsonDocument<768> doc;
  addStatus(doc);
  sendJson(doc);
}

void sendStatusSerial() {
  StaticJsonDocument<768> doc;
  addStatus(doc);
  sendSerialJson(doc);
}

void runCommand(const String& command) {
  if (command.length() == 0) {
    return;
  }
  markCommandHandled(command);
  if (onCommand) onCommand(command);
}

void handleGetCommand() {
  StaticJsonDocument<128> doc;
  doc["ok"] = true;
  doc["command"] = lastCommand;
  sendJson(doc);
}

void handleSetCommand() {
  String command;
  if (server.hasArg("plain") && server.arg("plain").length() > 0) {
    StaticJsonDocument<192> request;
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

  runCommand(command);
  sendStatusHttp();
}

void handleNotFound() {
  StaticJsonDocument<192> doc;
  doc["ok"] = false;
  doc["error"] = "not_found";
  doc["endpoints"] = "GET /status, GET /command, POST /command, POST /set";
  sendJson(doc, 404);
}

void handleSerialLine(const String& rawLine) {
  String line = rawLine;
  line.trim();
  if (line.length() == 0) return;

  String command;
  if (line.startsWith("{")) {
    StaticJsonDocument<192> request;
    DeserializationError error = deserializeJson(request, line);
    if (error) {
      StaticJsonDocument<128> doc;
      doc["ok"] = false;
      doc["error"] = "invalid_serial_json";
      sendSerialJson(doc);
      return;
    }
    if (request["status"] | false) {
      sendStatusSerial();
      return;
    }
    command = request["command"] | "";
  } else if (line == "status") {
    sendStatusSerial();
    return;
  } else {
    command = line;
  }

  runCommand(command);
  sendStatusSerial();
}

void handleSerialInput() {
  while (Serial.available() > 0) {
    char value = static_cast<char>(Serial.read());
    if (value == '\n') {
      handleSerialLine(serialBuffer);
      serialBuffer = "";
    } else if (value != '\r') {
      serialBuffer += value;
      if (serialBuffer.length() > 240) serialBuffer = "";
    }
  }
}
}

void beginHWLab(const HWLabSetupConfig& config, CommandHandler commandHandler, StatusBuilder statusBuilder) {
  setupConfig = config;
  onCommand = commandHandler;
  onStatus = statusBuilder;

  Serial.begin(setupConfig.serialBaud);
  WiFi.mode(WIFI_AP);
  WiFi.softAP(setupConfig.apSsid, setupConfig.apPassword);

  Serial.println();
  Serial.println("HW Lab XIAO access point started");
  Serial.print("SSID: ");
  Serial.println(setupConfig.apSsid);
  Serial.print("IP: ");
  Serial.println(WiFi.softAPIP());

  server.on("/", HTTP_GET, sendStatusHttp);
  server.on("/status", HTTP_GET, sendStatusHttp);
  server.on("/command", HTTP_GET, handleGetCommand);
  server.on("/command", HTTP_POST, handleSetCommand);
  server.on("/set", HTTP_POST, handleSetCommand);
  server.on("/", HTTP_OPTIONS, []() { server.send(204); });
  server.on("/status", HTTP_OPTIONS, []() { server.send(204); });
  server.on("/command", HTTP_OPTIONS, []() { server.send(204); });
  server.on("/set", HTTP_OPTIONS, []() { server.send(204); });
  server.onNotFound(handleNotFound);
  server.begin();
}

void handleHWLab() {
  handleSerialInput();
  server.handleClient();
}

void markCommandHandled(const String& command) {
  lastCommand = command;
  commandCount += 1;
  Serial.print("Command received: ");
  Serial.println(command);
}
