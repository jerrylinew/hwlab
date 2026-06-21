#include "src/HWLabHardware.h"
#include "src/HWLabSetup.h"

#ifndef LED_BUILTIN
#define LED_BUILTIN 21
#endif

// XIAO ESP32C3 pins used by the 4-pin RGB LED:
// D0 -> Red, D1 -> Green, D3 -> Blue, common pin -> 3.3V.
#ifndef D0
#define D0 2
#endif

#ifndef D1
#define D1 3
#endif

#ifndef D3
#define D3 5
#endif

RgbLed rgbLed(D0, D1, D3, true);
Buzzer buzzer;
LightGrid16x16 lightGrid;

bool builtInLedOn = false;

// Change WiFi settings here. The setup code lives in src/HWLabSetup.*,
const char* WIFI_NAME = "HWLab-XIAO";
const char* WIFI_PASSWORD = "hwlab1234";

// The following is a set of example code, you can remove it after you test your wiring 

enum class CommandCode {
  ThumbsUp,
  Red,
  Green,
  Blue,
  White,
  Off,
  Test,
  Beep,
  Unknown,
};

CommandCode commandCode(const String& command) {
  if (command == "thumbs_up") return CommandCode::ThumbsUp;
  if (command == "red") return CommandCode::Red;
  if (command == "green") return CommandCode::Green;
  if (command == "blue") return CommandCode::Blue;
  if (command == "white") return CommandCode::White;
  if (command == "off") return CommandCode::Off;
  if (command == "test") return CommandCode::Test;
  if (command == "beep") return CommandCode::Beep;
  return CommandCode::Unknown;
}

void setBuiltInLed(bool on) {
  builtInLedOn = on;
  digitalWrite(LED_BUILTIN, on ? LOW : HIGH);
}

void addProjectStatus(JsonDocument& doc) {
  doc["led_on"] = builtInLedOn;
  rgbLed.addStatus(doc);
}

void handleProjectCommand(const String& command) {
  // LED example for students: a thumbs-up from Python changes the RGB LED.
  switch (commandCode(command)) {
    case CommandCode::ThumbsUp:
      rgbLed.nextColor();
      setBuiltInLed(false);
      break;

    case CommandCode::Red:
      rgbLed.red();
      break;

    case CommandCode::Green:
      rgbLed.green();
      break;

    case CommandCode::Blue:
      rgbLed.blue();
      break;

    case CommandCode::White:
      rgbLed.white();
      break;

    case CommandCode::Off:
      rgbLed.off();
      setBuiltInLed(false);
      break;

    case CommandCode::Test:
      rgbLed.test();
      break;

    case CommandCode::Beep:
      // Connect a piezo buzzer signal pin to your chosen GPIO, then call
      // buzzer.begin(D2) in setup(). Example notes: "C4", "C#4", "A5".
      buzzer.playNote("C4", 250);
      break;

    case CommandCode::Unknown:
      Serial.print("Unknown command: ");
      Serial.println(command);
      break;
  }

  // Servo note for curriculum projects:
  // Install ESP32Servo, then add something like:
  //   #include <ESP32Servo.h>
  //   Servo servo;
  //   servo.attach(D2);
  //   servo.write(90);

  Serial.print("RGB color: ");
  Serial.println(rgbLed.colorName());
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  setBuiltInLed(false);

  rgbLed.begin(); // Starts white so the wiring is visibly alive before commands.
  // buzzer.begin(D2); // Uncomment after wiring a buzzer signal pin.
  // lightGrid.begin(yourPixelWriter); // Hook this to a real 16x16 LED driver.

  HWLabSetupConfig config;
  config.apSsid = WIFI_NAME;
  config.apPassword = WIFI_PASSWORD;
  config.serialBaud = 115200;
  beginHWLab(config, handleProjectCommand, addProjectStatus);
}

void loop() {
  handleHWLab();
}
