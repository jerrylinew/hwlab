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

// --- 16x16 LED matrix (optional) -------------------------------------------
// Turn this on AFTER you (1) wire a WS2812B/NeoPixel 16x16 panel's DIN to D6,
// and (2) install the "FastLED" library (Tools > Manage Libraries).
// Left at 0, the sketch compiles with no extra libraries.
#define USE_LED_MATRIX 1  

#if USE_LED_MATRIX
#include <FastLED.h>
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

// A static image to draw — a smiley face. Each row is 16 pixels wide; a 1 bit
// lights up. Edit the bits to design your own picture.
const uint16_t SMILEY[16] = {
  0b0000000000000000,
  0b0001111111110000,
  0b0011000000011000,
  0b0110000000001100,
  0b0100110001100100,
  0b1100110001100110,
  0b1100000000000110,
  0b1100000000000110,
  0b1100100000010110,
  0b1100110000110110,
  0b0110011111100100,
  0b0110000000001100,
  0b0011000000011000,
  0b0001111111110000,
  0b0000000000000000,
  0b0000000000000000,
};
#endif

// Change WiFi settings here. The setup code lives in src/HWLabSetup.*,
const char* WIFI_NAME = "";
const char* WIFI_PASSWORD = "";

// The following is a set of example code, you can remove it after you test your wiring

void addProjectStatus(JsonDocument& doc) {
  doc["led_on"] = led.isOn();
}

// This runs every time a command arrives from Python. Each `if` checks the
// command text and decides what the hardware should do. Add your own gesture by
// copying an `if` block and changing the command name and the action.
void handleProjectCommand(const String& command) {
  if (command == "thumbs_up") {
    led.toggle();   // thumbs-up flips the LED on/off
  }
  else if (command == "open_hand") {
    led.on();       // open palm turns the LED on
#if USE_LED_MATRIX
    lightGrid.clear();
    lightGrid.drawBitmap(SMILEY, 16, 0x00FF00);  // open palm -> green smiley
    renderMatrix();
#endif
  }
  else if (command == "fist" || command == "off") {
    led.off();      // a fist (or the "off" command) turns the LED off
#if USE_LED_MATRIX
    lightGrid.clear();
    renderMatrix();
#endif
  }
  else if (command == "on") {
    led.on();
  }
  else if (command == "beep") {
    // Connect a piezo buzzer signal pin to your chosen GPIO, then call
    // buzzer.begin(D2) in setup(). Example notes: "C4", "C#4", "A5".
    buzzer.playNote("C4", 250);
  }
  else {
    Serial.print("Unknown command: ");
    Serial.println(command);
  }

  // Servo note for curriculum projects:
  // Install ESP32Servo, then add something like:
  //   #include <ESP32Servo.h>
  //   Servo servo;
  //   servo.attach(D2);
  //   servo.write(90);

  Serial.print("LED is now ");
  Serial.println(led.isOn() ? "on" : "off");
}

void setup() {
  led.begin();         // simple LED on D0
  // buzzer.begin(D2); // Uncomment after wiring a buzzer signal pin.

#if USE_LED_MATRIX
  FastLED.addLeds<WS2812B, MATRIX_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(40);   // 256 LEDs at full white draw a LOT of current
  lightGrid.begin(matrixWriter);
  lightGrid.drawBitmap(SMILEY, 16, 0x00FF00);  // show a face on boot
  renderMatrix();
#endif

  HWLabSetupConfig config;
  config.apSsid = WIFI_NAME;
  config.apPassword = WIFI_PASSWORD;
  config.serialBaud = 115200;
  beginHWLab(config, handleProjectCommand, addProjectStatus);
}

void loop() {
  handleHWLab();
}
