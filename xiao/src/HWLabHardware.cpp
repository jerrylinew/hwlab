#include "HWLabHardware.h"

#include <math.h>

Led::Led(int pin, bool activeLow) : _pin(pin), _activeLow(activeLow), _on(false) {}

void Led::begin() {
  pinMode(_pin, OUTPUT);
  write();
}

void Led::write() {
  digitalWrite(_pin, (_on != _activeLow) ? HIGH : LOW);
}

void Led::on() { set(true); }
void Led::off() { set(false); }
void Led::toggle() { set(!_on); }

void Led::set(bool isOn) {
  _on = isOn;
  write();
}

bool Led::isOn() const { return _on; }

RgbLed::RgbLed(int redPin, int greenPin, int bluePin, bool commonAnode, bool usePwm)
  : _redPin(redPin), _greenPin(greenPin), _bluePin(bluePin), _commonAnode(commonAnode), _usePwm(usePwm), _colorIndex(-1), _colorName("off"), _red(0), _green(0), _blue(0) {}

void RgbLed::begin() {
  pinMode(_redPin, OUTPUT);
  pinMode(_greenPin, OUTPUT);
  pinMode(_bluePin, OUTPUT);
  white();
}

void RgbLed::writePin(int pin, int value) {
  int brightness = constrain(value, 0, 255);
  if (_usePwm) {
    analogWrite(pin, _commonAnode ? 255 - brightness : brightness);
    return;
  }

  bool on = brightness > 0;
  digitalWrite(pin, _commonAnode ? (on ? LOW : HIGH) : (on ? HIGH : LOW));
}

void RgbLed::setColor(const String& name, int redValue, int greenValue, int blueValue) {
  _colorName = name;
  _red = constrain(redValue, 0, 255);
  _green = constrain(greenValue, 0, 255);
  _blue = constrain(blueValue, 0, 255);
  writePin(_redPin, _red);
  writePin(_greenPin, _green);
  writePin(_bluePin, _blue);
}

void RgbLed::off() { setColor("off", 0, 0, 0); }
void RgbLed::white() { setColor("white", 255, 255, 255); }
void RgbLed::red() { setColor("red", 255, 0, 0); }
void RgbLed::green() { setColor("green", 0, 255, 0); }
void RgbLed::blue() { setColor("blue", 0, 0, 255); }
void RgbLed::yellow() { setColor("yellow", 255, 160, 0); }
void RgbLed::purple() { setColor("purple", 180, 0, 255); }
void RgbLed::cyan() { setColor("cyan", 0, 180, 255); }

void RgbLed::nextColor() {
  _colorIndex = (_colorIndex + 1) % 6;
  if (_colorIndex == 0) red();
  if (_colorIndex == 1) green();
  if (_colorIndex == 2) blue();
  if (_colorIndex == 3) yellow();
  if (_colorIndex == 4) purple();
  if (_colorIndex == 5) cyan();
}

void RgbLed::test() {
  red(); delay(300);
  green(); delay(300);
  blue(); delay(300);
  white();
}

void RgbLed::addStatus(JsonDocument& doc) const {
  doc["rgb_color"] = _colorName;
  doc["rgb_red"] = _red;
  doc["rgb_green"] = _green;
  doc["rgb_blue"] = _blue;
  doc["rgb_common_anode"] = _commonAnode;
  doc["rgb_use_pwm"] = _usePwm;
}

String RgbLed::colorName() const { return _colorName; }

Buzzer::Buzzer(int pin) : _pin(pin) {}

void Buzzer::begin(int pin) {
  if (pin >= 0) _pin = pin;
  if (_pin >= 0) pinMode(_pin, OUTPUT);
}

void Buzzer::playNote(const String& note, int durationMs) {
  if (_pin < 0) return;
  int frequency = noteFrequency(note);
  if (frequency <= 0) {
    delay(durationMs);
    return;
  }
  tone(_pin, frequency, durationMs);
  delay(durationMs);
  noTone(_pin);
}

void Buzzer::playMelody(const String notes[], const int durationsMs[], int noteCount) {
  for (int i = 0; i < noteCount; i++) {
    playNote(notes[i], durationsMs[i]);
    delay(30);
  }
}

void Buzzer::stop() {
  if (_pin >= 0) noTone(_pin);
}

int Buzzer::noteFrequency(const String& rawNote) const {
  String note = rawNote;
  note.trim();
  note.toUpperCase();
  if (note == "REST" || note == "R") return 0;

  int semitone = 0;
  char letter = note.charAt(0);
  if (letter == 'C') semitone = 0;
  else if (letter == 'D') semitone = 2;
  else if (letter == 'E') semitone = 4;
  else if (letter == 'F') semitone = 5;
  else if (letter == 'G') semitone = 7;
  else if (letter == 'A') semitone = 9;
  else if (letter == 'B') semitone = 11;
  else return 0;

  int index = 1;
  if (note.charAt(index) == '#') {
    semitone += 1;
    index += 1;
  } else if (note.charAt(index) == 'B') {
    semitone -= 1;
    index += 1;
  }

  int octave = note.substring(index).toInt();
  int midi = (octave + 1) * 12 + semitone;
  return static_cast<int>(round(440.0 * pow(2.0, (midi - 69) / 12.0)));
}

void LightGrid16x16::begin(PixelWriter writer) {
  _writer = writer;
  clear();
}

void LightGrid16x16::clear(uint32_t color) {
  for (int i = 0; i < 16 * 16; i++) _pixels[i] = color;
}

void LightGrid16x16::setPixel(int x, int y, uint32_t color) {
  if (x < 0 || x >= 16 || y < 0 || y >= 16) return;
  _pixels[y * 16 + x] = color;
}

uint32_t LightGrid16x16::getPixel(int x, int y) const {
  if (x < 0 || x >= 16 || y < 0 || y >= 16) return 0;
  return _pixels[y * 16 + x];
}

void LightGrid16x16::fillRect(int x, int y, int width, int height, uint32_t color) {
  for (int yy = y; yy < y + height; yy++) {
    for (int xx = x; xx < x + width; xx++) setPixel(xx, yy, color);
  }
}

void LightGrid16x16::drawRect(int x, int y, int width, int height, uint32_t color) {
  drawLine(x, y, x + width - 1, y, color);
  drawLine(x, y + height - 1, x + width - 1, y + height - 1, color);
  drawLine(x, y, x, y + height - 1, color);
  drawLine(x + width - 1, y, x + width - 1, y + height - 1, color);
}

void LightGrid16x16::drawLine(int x0, int y0, int x1, int y1, uint32_t color) {
  int dx = abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
  int dy = -abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
  int err = dx + dy;
  while (true) {
    setPixel(x0, y0, color);
    if (x0 == x1 && y0 == y1) break;
    int e2 = 2 * err;
    if (e2 >= dy) { err += dy; x0 += sx; }
    if (e2 <= dx) { err += dx; y0 += sy; }
  }
}

void LightGrid16x16::drawChar(int x, int y, char value, uint32_t color) {
  const byte* glyph = glyphFor(value);
  for (int col = 0; col < 5; col++) {
    byte bits = glyph[col];
    for (int row = 0; row < 7; row++) {
      if (bits & (1 << row)) setPixel(x + col, y + row, color);
    }
  }
}

void LightGrid16x16::drawText(int x, int y, const String& text, uint32_t color) {
  for (int i = 0; i < text.length(); i++) drawChar(x + i * 6, y, text.charAt(i), color);
}

void LightGrid16x16::scrollText(const String& text, int offset, uint32_t color) {
  clear();
  drawText(16 - offset, 4, text, color);
}

void LightGrid16x16::drawBitmap(const uint16_t* rows, int height, uint32_t color) {
  for (int y = 0; y < height; y++) {
    for (int x = 0; x < 16; x++) {
      if (rows[y] & (1 << (15 - x))) setPixel(x, y, color);
    }
  }
}

void LightGrid16x16::drawFrame(const uint32_t* pixels) {
  for (int i = 0; i < 16 * 16; i++) _pixels[i] = pixels[i];
}

void LightGrid16x16::show() {
  if (!_writer) return;
  for (int y = 0; y < 16; y++) {
    for (int x = 0; x < 16; x++) _writer(x, y, getPixel(x, y));
  }
}

// Scale a 0xRRGGBB color's brightness by level/255 (0 = off, 255 = full).
static uint32_t scaleColor(uint32_t color, int level) {
  int r = ((color >> 16) & 0xFF) * level / 255;
  int g = ((color >> 8) & 0xFF) * level / 255;
  int b = (color & 0xFF) * level / 255;
  return ((uint32_t)r << 16) | ((uint32_t)g << 8) | (uint32_t)b;
}

uint32_t LightGrid16x16::chroma(uint8_t hue) {
  // Walk the spectrum: red (0) -> green (85) -> blue (170) -> back to red (255).
  if (hue < 85) {
    return ((uint32_t)(255 - hue * 3) << 16) | ((uint32_t)(hue * 3) << 8);
  }
  if (hue < 170) {
    hue -= 85;
    return ((uint32_t)(255 - hue * 3) << 8) | (uint32_t)(hue * 3);
  }
  hue -= 170;
  return ((uint32_t)(hue * 3) << 16) | (uint32_t)(255 - hue * 3);
}

void LightGrid16x16::playAnimation(Animation anim, int frame, uint32_t color) {
  switch (anim) {
    case Animation::Rainbow:
      for (int y = 0; y < 16; y++) {
        for (int x = 0; x < 16; x++) setPixel(x, y, chroma((uint8_t)((x + y) * 8 + frame * 4)));
      }
      break;

    case Animation::Pulse: {
      int t = frame % 32;                       // 0..31
      int level = (t < 16 ? t : 31 - t) * 17;   // triangle wave 0..255..0
      clear(scaleColor(color, level));
      break;
    }

    case Animation::Sparkle: {
      clear(0x000000);
      // Deterministic "random" sparkles seeded by the frame (no random() so the
      // animation is reproducible and testable).
      for (int i = 0; i < 24; i++) {
        uint32_t h = (uint32_t)frame * 2654435761u ^ (uint32_t)i * 40503u;
        int idx = h % 256;
        setPixel(idx % 16, idx / 16, color);
      }
      break;
    }

    case Animation::Wipe: {
      clear(0x000000);
      int col = frame % 17;   // 0..16 columns filled, then repeat
      for (int x = 0; x <= col && x < 16; x++) {
        for (int y = 0; y < 16; y++) setPixel(x, y, color);
      }
      break;
    }

    case Animation::Spin: {
      clear(0x000000);
      float angle = frame * 0.3926991f;   // ~22.5 degrees per frame
      int x1 = 8 + (int)round(cos(angle) * 7);
      int y1 = 8 + (int)round(sin(angle) * 7);
      drawLine(8, 8, x1, y1, color);
      break;
    }
  }
}

const byte* LightGrid16x16::glyphFor(char value) const {
  static const byte blank[5] = {0, 0, 0, 0, 0};
  static const byte glyphs[36][5] = {
    {0x7E,0x11,0x11,0x11,0x7E},{0x7F,0x49,0x49,0x49,0x36},{0x3E,0x41,0x41,0x41,0x22},{0x7F,0x41,0x41,0x22,0x1C},
    {0x7F,0x49,0x49,0x49,0x41},{0x7F,0x09,0x09,0x09,0x01},{0x3E,0x41,0x49,0x49,0x7A},{0x7F,0x08,0x08,0x08,0x7F},
    {0x00,0x41,0x7F,0x41,0x00},{0x20,0x40,0x41,0x3F,0x01},{0x7F,0x08,0x14,0x22,0x41},{0x7F,0x40,0x40,0x40,0x40},
    {0x7F,0x02,0x0C,0x02,0x7F},{0x7F,0x04,0x08,0x10,0x7F},{0x3E,0x41,0x41,0x41,0x3E},{0x7F,0x09,0x09,0x09,0x06},
    {0x3E,0x41,0x51,0x21,0x5E},{0x7F,0x09,0x19,0x29,0x46},{0x46,0x49,0x49,0x49,0x31},{0x01,0x01,0x7F,0x01,0x01},
    {0x3F,0x40,0x40,0x40,0x3F},{0x1F,0x20,0x40,0x20,0x1F},{0x3F,0x40,0x38,0x40,0x3F},{0x63,0x14,0x08,0x14,0x63},
    {0x07,0x08,0x70,0x08,0x07},{0x61,0x51,0x49,0x45,0x43},{0x3E,0x51,0x49,0x45,0x3E},{0x00,0x42,0x7F,0x40,0x00},
    {0x42,0x61,0x51,0x49,0x46},{0x21,0x41,0x45,0x4B,0x31},{0x18,0x14,0x12,0x7F,0x10},{0x27,0x45,0x45,0x45,0x39},
    {0x3C,0x4A,0x49,0x49,0x30},{0x01,0x71,0x09,0x05,0x03},{0x36,0x49,0x49,0x49,0x36},{0x06,0x49,0x49,0x29,0x1E}
  };
  char upper = toupper(value);
  if (upper >= 'A' && upper <= 'Z') return glyphs[upper - 'A'];
  if (upper >= '0' && upper <= '9') return glyphs[26 + upper - '0'];
  return blank;
}
