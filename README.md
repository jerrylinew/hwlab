# OpenCV Gesture & Face

## Installing Nix

This project uses a Nix **flake** (`flake.nix`) to provide all dependencies. You
only need to install Nix once.

### Mac / Linux

Run the official installer (this is the recommended Determinate Systems
installer, which enables flakes for you automatically):

```sh
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
```

After it finishes, open a **new** terminal so the `nix` command is on your PATH.

> If you instead use the official upstream installer from
> [nixos.org](https://nixos.org/download), flakes are not on by default. Enable
> them by adding this line to `~/.config/nix/nix.conf` (create the file if it
> doesn't exist):
>
> ```
> experimental-features = nix-command flakes
> ```

### Windows

Nix does not run natively on Windows — install it inside **WSL2** (Windows
Subsystem for Linux).

1. Open PowerShell **as Administrator** and install WSL:

   ```powershell
   wsl --install
   ```

   Reboot if prompted, then launch the "Ubuntu" app from the Start menu and
   create your Linux username/password.

2. Inside the Ubuntu (WSL) terminal, install Nix exactly as in the
   **Mac / Linux** section above:

   ```sh
   curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
   ```

3. Open a new WSL terminal and run all the commands below from there.

> Note: webcam access from inside WSL2 requires extra setup (USB passthrough via
> `usbipd-win`). If you can't get the camera working in WSL, run the Python
> client directly on Windows instead (install Python 3.11, then
> `pip install -r python-client/requirements.txt`).

## Quick start

Once Nix is installed, start the dev shell from the project root:

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

Open the printed local URL. You should see the webcam feed on the left and a
"Commands Sent" log on the right.

## Troubleshooting

### macOS: "not authorized to capture video" / camera fails to initialize

The first time the Python client touches your webcam, macOS needs to grant the
terminal camera access. The app sets `OPENCV_AVFOUNDATION_SKIP_AUTH=1` so it
won't crash, but you still have to allow the camera:

1. Open **System Settings -> Privacy & Security -> Camera**.
2. Enable the toggle for your terminal app (Terminal, iTerm, VS Code, etc.).
3. Fully quit and reopen that terminal, then run `uvicorn main:app --reload`
   again.

If the video feed is black, it's almost always this permission.

### `AttributeError: module 'mediapipe' has no attribute 'solutions'`

This lab uses MediaPipe's legacy `mp.solutions` API, which newer wheels
(0.10.30+) no longer ship on macOS arm64. `requirements.txt` pins a working
version (`mediapipe==0.10.14`). If you hit this error, your venv has a newer
build - reinstall the pinned deps:

```sh
pip install -r python-client/requirements.txt
```
1. Write a detection function in `python-client/cv/gestures.py`
2. Import it in `main.py`
3. Add a check in the camera worker's `_run()` loop (follow the thumbs_up pattern)
4. Handle the new command in `xiao/xiao.ino` (`handle_command()`)

## Adding to the vue client
learn JS and Vue. Use these [elements](https://element-plus.org/en-US/component/overview) to help things look good.
