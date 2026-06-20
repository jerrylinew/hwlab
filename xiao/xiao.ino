#include <ArduinoJson.h>
#include <WebServer.h>
#include <WiFi.h>

const char* AP_SSID = "HWLab-XIAO";
const char* AP_PASS = "hwlab1234";

WebServer server(80);

String lastCommand = "none";
bool ledOn = false;
unsigned long commandCount = 0;
String rgbColorName = "off";
int rgbRed = 0;
int rgbGreen = 0;
int rgbBlue = 0;

#ifndef LED_BUILTIN
#define LED_BUILTIN 21
#endif

#ifndef D0
#define D0 2
#endif

#ifndef D1
#define D1 3
#endif

#ifndef D3
#define D3 5
#endif

const int RGB_RED_PIN = D0;
const int RGB_GREEN_PIN = D1;
const int RGB_BLUE_PIN = D3;

const int RGB_COLOR_COUNT = 6;
const char* RGB_COLOR_NAMES[RGB_COLOR_COUNT] = {
  "red", "green", "blue", "yellow", "purple", "cyan"
};
const int RGB_COLORS[RGB_COLOR_COUNT][3] = {
  {255, 0, 0},
  {0, 255, 0},
  {0, 0, 255},
  {255, 160, 0},
  {180, 0, 255},
  {0, 180, 255},
};
int rgbColorIndex = -1;

void setLed(bool on) {
  ledOn = on;
  digitalWrite(LED_BUILTIN, on ? LOW : HIGH);
}

void writeRgbPin(int pin, int value) {
  // The 4-pin LED is wired to 3.3V, so each color pin is active-low.
  analogWrite(pin, 255 - constrain(value, 0, 255));
}

void setRgbColor(const String& name, int red, int green, int blue) {
  rgbColorName = name;
  rgbRed = constrain(red, 0, 255);
  rgbGreen = constrain(green, 0, 255);
  rgbBlue = constrain(blue, 0, 255);

  writeRgbPin(RGB_RED_PIN, rgbRed);
  writeRgbPin(RGB_GREEN_PIN, rgbGreen);
  writeRgbPin(RGB_BLUE_PIN, rgbBlue);
}

void nextRgbColor() {
  rgbColorIndex = (rgbColorIndex + 1) % RGB_COLOR_COUNT;
  setRgbColor(
    RGB_COLOR_NAMES[rgbColorIndex],
    RGB_COLORS[rgbColorIndex][0],
    RGB_COLORS[rgbColorIndex][1],
    RGB_COLORS[rgbColorIndex][2]
  );
}

void sendJson(JsonDocument& doc, int status = 200) {
  String body;
  serializeJson(doc, body);
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
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
  doc["rgb_color"] = rgbColorName;
  doc["rgb_red"] = rgbRed;
  doc["rgb_green"] = rgbGreen;
  doc["rgb_blue"] = rgbBlue;
  doc["wifi_clients"] = WiFi.softAPgetStationNum();
  doc["free_heap"] = ESP.getFreeHeap();
}

void handleStatus() {
  StaticJsonDocument<512> doc;
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

  Serial.print("Command received: ");
  Serial.println(command);

  if (command == "thumbs_up") {
    nextRgbColor();
    setLed(false);
  } else if (command == "toggle") {
    setLed(!ledOn);
  } else if (command == "true" || command == "on") {
    setLed(true);
  } else if (command == "false" || command == "off") {
    setLed(false);
    setRgbColor("off", 0, 0, 0);
  } else if (command == "red") {
    setRgbColor("red", 255, 0, 0);
  } else if (command == "green") {
    setRgbColor("green", 0, 255, 0);
  } else if (command == "blue") {
    setRgbColor("blue", 0, 0, 255);
  } else if (command == "yellow") {
    setRgbColor("yellow", 255, 160, 0);
  } else if (command == "purple") {
    setRgbColor("purple", 180, 0, 255);
  } else if (command == "cyan") {
    setRgbColor("cyan", 0, 180, 255);
  } else if (command == "white") {
    setRgbColor("white", 255, 255, 255);
  }

  Serial.print("RGB color: ");
  Serial.println(rgbColorName);

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

  StaticJsonDocument<512> doc;
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
  pinMode(RGB_RED_PIN, OUTPUT);
  pinMode(RGB_GREEN_PIN, OUTPUT);
  pinMode(RGB_BLUE_PIN, OUTPUT);
  setLed(false);
  setRgbColor("off", 0, 0, 0);

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
  server.on("/", HTTP_OPTIONS, []() { server.send(204); });
  server.on("/status", HTTP_OPTIONS, []() { server.send(204); });
  server.on("/command", HTTP_OPTIONS, []() { server.send(204); });
  server.on("/set", HTTP_OPTIONS, []() { server.send(204); });
  server.onNotFound(handleNotFound);
  server.begin();
}

void loop() {
  server.handleClient();
}
