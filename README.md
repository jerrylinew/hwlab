# OpenCV Gesture & Face

## Quick start

Make sure that Nix is installed on the computer.

You can follow the installation guide [here](https://nixos.org/download/)

```sh
nix develop
```

This sets up a Python venv, Node.js for the Vue app, and arduino-cli for flashing the XIAO.

### Run the Python client

```sh
cd python-client
uvicorn main:app --reload
```

- `main.py` — thumbs-up gesture example + FastAPI server
- `cv/` — all computer vision code (hand/face detection, gestures, GPU acceleration)
- `xiao_client.py` — HTTP client for sending commands to the XIAO

Endpoints:
- `GET /video_feed` — MJPEG stream of annotated webcam feed
- `WS /ws` — broadcasts `{command, sent_to_xiao, timestamp}` on each gesture

### Flash the XIAO ESP32C3

1. Install the ESP32 board package:
   ```sh
   arduino-cli core install esp32:esp32
   arduino-cli lib install ArduinoJson
   ```

2. Edit `xiao/xiao.ino` — set `WIFI_SSID` and `WIFI_PASS`.

3. Compile and upload:
   ```sh
   cd xiao
   arduino-cli compile --fqbn esp32:esp32:XIAO_ESP32C3
   arduino-cli upload -p /dev/ttyACM0 --fqbn esp32:esp32:XIAO_ESP32C3
   ```

4. Open Serial Monitor at 115200 baud — note the printed IP address.

5. Set that IP in `python-client/xiao_client.py` (`XIAO_IP`).

The XIAO serves:
- `POST /command` — accepts `{"command": "thumbs_up"}`, toggles LED
- `GET /status` — returns uptime, LED state, IP, WiFi RSSI

### Run the Vue viewer

```sh
cd vue-client
npm install
npm run dev
```

Open the printed local URL. Webcam feed on the left, command log on the right.

## Hardware acceleration

The CV module uses OpenCV's OpenCL backend to offload image processing to GPU
when available. This works across:

- **macOS (Apple Silicon)** — Metal via OpenCL compatibility layer
- **Linux (ARM/x86)** — Mesa OpenCL (for Intel/AMD iGPU) or proprietary drivers
- **Windows** — DirectX OpenCL layer, NVIDIA/AMD/Intel drivers

On startup the server prints which backend is active. If it falls back to CPU,
the frame-skipping and resolution scaling in `cv/hand_detector.py` keep it
responsive regardless.

## Adding new gestures

1. Write a detection function in `python-client/cv/gestures.py`
2. Import it in `main.py`
3. Add a check in the camera worker's `_run()` loop (follow the thumbs_up pattern)
4. Handle the new command in `xiao/xiao.ino` (`handle_command()`)

## Adding to the vue client
learn JS and Vue. Use these [elements](https://element-plus.org/en-US/component/overview) to help things look good.
