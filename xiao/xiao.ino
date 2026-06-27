#include "src/HWLabHardware.h"
#include "src/HWLabSetup.h"
#include <FastLED.h>

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
// short leg -> GND. A breadboard LED lights when the pin is HIGH.
Led led(D0);

// A piezo buzzer (optional): signal -> D2, other leg -> GND.
// Stays silent until you call buzzer.begin(D2) in setup().
Buzzer buzzer;

// A 16x16 drawing canvas.
LightGrid16x16 lightGrid;

// --- 16x16 LED matrix ------------------------------------------------------
// Wire a WS2812B/NeoPixel 16x16 panel: DIN -> D6, 5V -> 5V, GND -> GND.
// Install the "FastLED" library (Tools > Manage Libraries) to build this sketch.
#define MATRIX_PIN D6
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

// Your picture: one 0xRRGGBB color per pixel (index = y * 16 + x). It starts
// blank. Draw your own in the lab website's "Draw" tab, click "Copy code",
// and paste the array it gives you over the line below.
const uint32_t MY_ART[NUM_LEDS] = {0};

// Change WiFi settings here. The setup code lives in src/HWLabSetup.*
const char* WIFI_NAME = "";
const char* WIFI_PASSWORD = "";

// Reports status back to the lab website.
void addProjectStatus(JsonDocument& doc) {
  doc["led_on"] = led.isOn();
}

// Runs every time a command arrives. Each `if` maps a gesture to an action —
// copy a block and change the command name to add your own gesture.
void handleProjectCommand(const String& command) {
  if (command == "thumbs_up") {
    led.toggle();                 // thumbs-up flips the LED on/off
  }
  else if (command == "open_hand") {
    led.on();                     // open palm: LED on, and show your art
    lightGrid.drawFrame(MY_ART);
    renderMatrix();
  }
  else if (command == "fist" || command == "off") {
    led.off();                    // fist (or "off"): LED off, and clear the grid
    lightGrid.clear();
    renderMatrix();
  }
  else {
    Serial.print("Unknown command: ");
    Serial.println(command);
  }
}

void setup() {
  led.begin();
  // buzzer.begin(D2);   // Uncomment after wiring a buzzer signal pin.

  FastLED.addLeds<WS2812B, MATRIX_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(40);   // 256 LEDs at full white draw a LOT of current
  lightGrid.begin(matrixWriter);
  lightGrid.drawFrame(MY_ART);   // show your drawing on boot
  renderMatrix();

  HWLabSetupConfig config;
  config.apSsid = WIFI_NAME;
  config.apPassword = WIFI_PASSWORD;
  config.serialBaud = 115200;
  beginHWLab(config, handleProjectCommand, addProjectStatus);
}

void loop() {
  handleHWLab();
}
