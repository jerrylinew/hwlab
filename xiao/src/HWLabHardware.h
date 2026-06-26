#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>

// A single small LED on one GPIO pin. The simplest possible output.
// activeLow = true for LEDs wired so the pin must go LOW to light (like the
// XIAO's built-in LED); false for a plain LED + resistor to GND (the usual
// breadboard wiring, e.g. on GPIO0 / D0).
class Led {
public:
  explicit Led(int pin, bool activeLow = false);

  void begin();
  void on();
  void off();
  void toggle();
  void set(bool isOn);
  bool isOn() const;

private:
  void write();

  int _pin;
  bool _activeLow;
  bool _on;
};

class RgbLed {
public:
  RgbLed(int redPin, int greenPin, int bluePin, bool commonAnode = true, bool usePwm = false);

  void begin();
  void setColor(const String& name, int red, int green, int blue);
  void off();
  void white();
  void red();
  void green();
  void blue();
  void yellow();
  void purple();
  void cyan();
  void nextColor();
  void test();
  void addStatus(JsonDocument& doc) const;

  String colorName() const;

private:
  void writePin(int pin, int value);

  int _redPin;
  int _greenPin;
  int _bluePin;
  bool _commonAnode;
  bool _usePwm;
  int _colorIndex;
  String _colorName;
  int _red;
  int _green;
  int _blue;
};

class Buzzer {
public:
  explicit Buzzer(int pin = -1);

  void begin(int pin = -1);
  void playNote(const String& note, int durationMs = 250);
  void playMelody(const String notes[], const int durationsMs[], int noteCount);
  void stop();

private:
  int noteFrequency(const String& note) const;
  int _pin;
};

class LightGrid16x16 {
public:
  using PixelWriter = void (*)(int x, int y, uint32_t color);

  void begin(PixelWriter writer = nullptr);
  void clear(uint32_t color = 0x000000);
  void setPixel(int x, int y, uint32_t color);
  uint32_t getPixel(int x, int y) const;
  void fillRect(int x, int y, int width, int height, uint32_t color);
  void drawRect(int x, int y, int width, int height, uint32_t color);
  void drawLine(int x0, int y0, int x1, int y1, uint32_t color);
  void drawChar(int x, int y, char value, uint32_t color);
  void drawText(int x, int y, const String& text, uint32_t color);
  // Draw a static 1-bit image. Each entry in `rows` is one 16-pixel row: the
  // most-significant bit is the left pixel (x=0), the least-significant the
  // right (x=15). A set bit is drawn in `color`, a clear bit is left alone.
  void drawBitmap(const uint16_t* rows, int height, uint32_t color);
  void scrollText(const String& text, int offset, uint32_t color);
  void show();

private:
  const byte* glyphFor(char value) const;

  uint32_t _pixels[16 * 16] = {0};
  PixelWriter _writer = nullptr;
};
