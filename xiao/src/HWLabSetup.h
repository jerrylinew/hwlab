#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>

using CommandHandler = void (*)(const String& command);
using StatusBuilder = void (*)(JsonDocument& doc);

struct HWLabSetupConfig {
  const char* apSsid = "HWLab-XIAO";
  const char* apPassword = "hwlab1234";
  unsigned long serialBaud = 115200;
};

void beginHWLab(const HWLabSetupConfig& config, CommandHandler commandHandler, StatusBuilder statusBuilder);
void handleHWLab();
void markCommandHandled(const String& command);
