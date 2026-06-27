#include "src/HWLabHardware.h"
#include "src/HWLabSetup.h"

// XIAO ESP32C3 pin fallbacks, so this still compiles when no board is selected.
// With the XIAO_ESP32C3 board chosen, D0..D6 come from the board package.
#ifndef D0
#define D0 2
#endif

#ifndef D2
#define D2 4
#endif

#ifndef D6
#define D6 21
#endif

// --- Your outputs ----------------------------------------------------------
// A simple single LED on GPIO0 (D0): long leg -> D0 through a 220Ω resistor,
// short leg -> GND. A breadboard LED lights when the pin is HIGH, so activeLow
// stays false here.
Led led(D0);

// A piezo buzzer (optional submodule): signal -> D2, other leg -> GND.
// It stays silent until you call buzzer.begin(D2) in setup().
Buzzer buzzer;

// A 16x16 drawing canvas. It does nothing until you connect a real panel below.
LightGrid16x16 lightGrid;

// --- 16x16 LED matrix -------------------------------------------
// Turn this on AFTER you (1) wire a WS2812B/NeoPixel 16x16 panel's DIN to D6,
// and (2) install the "FastLED" library (Tools > Manage Libraries).
// Left at 0, the sketch compiles with no extra libraries.

#if USE_LED_MATRIX
#include <FastLED.h>
#define MATRIX_PIN D6 //need to set number
#define NUM_LEDS (16 * 16)
#define MATRIX_SERPENTINE true   // most 16x16 panels zig-zag row to row
CRGB leds[NUM_LEDS];

// LightGrid16x16 calls this for every pixel when you call lightGrid.show().
// It turns a grid (x, y) into the right LED number, undoing the panel's zig-zag.
void matrixWriter(int x, int y, uint32_t color) {
  int col = (MATRIX_SERPENTINE && (y % 2 == 1)) ? (15 - x) : x;
  leds[y * 16 + col] = CRGB(color);   // CRGB reads a 0xRRGGBB value directly
}

// Push whatever is in the LightGrid buffer out to the real panel.
void renderMatrix() {
  lightGrid.show();   // walks the grid, calling matrixWriter for each pixel
  FastLED.show();     // lights the LEDs
}

// Change WiFi settings here. The setup code lives in src/HWLabSetup.*,
const char* WIFI_NAME = "";
const char* WIFI_PASSWORD = "";

void addProjectStatus(JsonDocument& doc) {
  doc["led_on"] = led.isOn();
}

// This is where commands from Python land. Start simple: one gesture, one job.
// Add your own behaviour by adding more `if` blocks below.
void handleProjectCommand(const String& command) {
  if (command == "thumbs_up") {
    led.toggle();   // thumbs-up flips the LED on/off
    // A prebuilt animation as a reward: a rainbow sweep across the panel.
    // (Blocking — it plays for ~2.5s, then the loop carries on.)
    //
    // This is test code for if you want to see if your 16x16 matrix works. 
    // for (int f = 0; f < 80; f++) {
    //   lightGrid.playAnimation(LightGrid16x16::Animation::Rainbow, f);
    //   renderMatrix();
    //   delay(30);
    // }
  }

  Serial.print("LED is now ");
  Serial.println(led.isOn() ? "on" : "off");
}
//this piece of code runs once
void setup() {
  led.begin();         // simple LED on D0

  FastLED.addLeds<WS2812B, MATRIX_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(40);
  lightGrid.begin(matrixWriter);
  lightGrid.playAnimation(LightGrid16x16::Animation::Rainbow, 0);  // a splash on boot
  renderMatrix();

  HWLabSetupConfig config;
  config.apSsid = WIFI_NAME;
  config.apPassword = WIFI_PASSWORD;
  config.serialBaud = 115200;
  beginHWLab(config, handleProjectCommand, addProjectStatus);
}
//this piece of code runs forever
void loop() {
  handleHWLab();
}
