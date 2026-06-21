#pragma once

#include <Arduino.h>
#include <ArduinoJson.h>

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
  void scrollText(const String& text, int offset, uint32_t color);
  void show();

private:
  const byte* glyphFor(char value) const;

  uint32_t _pixels[16 * 16] = {0};
  PixelWriter _writer = nullptr;
};
