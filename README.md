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
> ```
> vi ~/.config/nix/nix.conf
> ```
>
> ```
> experimental-features = nix-command flakes
> ```
> then press `:wq` to save.
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

You can run the Single Line command to get this repo and into the devshell. 

```sh
curl -sSL https://raw.githubusercontent.com/KaitoTLex/hwlab/refs/heads/main/setup.sh | bash
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

Open `python-client/main.py`. The part students edit is intentionally small:

```py
SEND_TO_XIAO = True  # change to False for Vue only

def when_hand_seen(hand):
    send_when(is_thumbs_up(hand), "thumbs_up")
```

Useful one-line blocks:

- `send("hello")` - send a command now to the XIAO and Vue command log
- `send_when(is_thumbs_up(hand), "thumbs_up")` - send when a gesture is seen
- `message = receive()` - read the last command from Vue or the XIAO getter API

Set `SEND_TO_XIAO = False` if the command should only go to the Vue website.
Leave it as `True` if the command should go to both Vue and the Seeed Studio XIAO.

Example:

```py
def when_hand_seen(hand):
    send_when(count_extended_fingers(hand) == 5, "open_hand")
```

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

## Adding to the Vue client

Open `vue-client/src/App.vue`. This is the student website file.

Useful values and one-line blocks:

- `latestCommand?.command` - the newest message from Python
- `sendToPython("hello")` - send a message back to Python for `receive()`
- `connected` - whether the website is connected to Python
- `videoFeedUrl` - the camera image URL if you want to show the webcam

The setup line is already there:

```vue
<script setup>
import { useHwLab } from "./useHwLab";

const { connected, latestCommand, sendToPython, videoFeedUrl } = useHwLab();
</script>
```
