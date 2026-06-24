# OpenCV Gesture & Face Lab

Watch your webcam, recognize hand gestures and faces with Python + MediaPipe, and
show the result on a live web page. One server, one click to start.

## Quick start

You need **no terminal experience** and you do **not** need Python, Node, or an
IDE installed. The launcher sets everything up for you the first time.

1. **Download the project.** On GitHub click the green **Code** button →
   **Download ZIP**, then unzip it. (Or `git clone` if you know how.)
2. **Start it:**
   - **Mac:** double-click **`Start HW Lab.command`**.
   - **Windows:** double-click **`Start HW Lab.bat`**.
3. The first run installs everything automatically (a few minutes). When it's
   ready, your browser opens to **http://localhost:8000** with the live camera
   feed and command log. Later runs start in seconds.

Leave the little black window open while you work — it *is* the running lab.

**To stop the lab (and turn the camera off):**
- **Mac:** double-click **`Stop HW Lab.command`**, or
- **Windows:** double-click **`Stop HW Lab.bat`**.

You can also press **Ctrl-C** in the black window, or close it. Any of these
shuts the server down and releases the webcam, so the camera light turns off.

> **First-run security prompt:** macOS ("cannot verify the developer") — right-click
> the file → **Open** → **Open**. Windows ("Windows protected your PC") — click
> **More info** → **Run anyway**. You only do this once.

> **Camera permission:** the first time, your OS asks to allow camera access —
> click **Allow**. See [Troubleshooting](#troubleshooting) if the feed is black.

## How it's put together

The whole lab runs as **one Python server** (FastAPI/uvicorn on port 8000) that:

- opens your webcam and runs hand/face detection on every frame,
- serves the **web page** you see in the browser (a prebuilt Vue app), and
- streams data to that page.

| Endpoint | What it serves |
|---|---|
| `/` | The web app (camera feed + command log) |
| `/video_feed` | MJPEG stream of the annotated webcam feed |
| `/ws` | WebSocket of commands, both directions |
| `/debug/status` | Live pipeline health (JSON) |

You only ever edit one file: **`python-client/main.py`**.

## Adding your own gestures

Edit your code right on the lab page in the **Edit Your Gestures** panel — no
separate editor needed. It loads `python-client/main.py`; click **Save & Run**
and the lab compile-checks it (a typo won't crash anything — it points at the bad
line), saves, and restarts with your change. The part you edit is intentionally
small:

```py
SEND_TO_XIAO = True  # change to False for web-page only

def when_hand_seen(hand):
    send_when(is_thumbs_up(hand), "thumbs_up")
```

Useful one-line blocks:

- `send("hello")` — send a command now to the web page (and XIAO, later)
- `send_when(is_thumbs_up(hand), "thumbs_up")` — send when a gesture is seen
- `message = receive()` — read the last command sent back from the web page

Save the file — the server reloads automatically and your change is live.

## Advanced / optional

These are **not** part of the normal workshop flow.

**Edit the web page live.** The page students see is prebuilt and served by the
Python server. If you want to change the page itself with hot-reload, run the Vue
dev server separately (needs Node 22):

```sh
cd vue-client
npm install
npm run dev        # opens on http://localhost:5173, talks to the Python server on :8000
```

After editing, rebuild the shipped page with `npm run build`.

**Run the Python server by hand** (instead of the launcher), e.g. to see logs:

```sh
cd python-client
uv run uvicorn main:app --reload --port 8000
```

`uv` reads `pyproject.toml`, creates the environment, and runs the server. If you
don't have `uv`, the launchers install it for you; or install it from
<https://docs.astral.sh/uv/>.

## Hardware acceleration

The CV module uses OpenCV's OpenCL backend to offload image processing to the GPU
when available (Apple Silicon via Metal/OpenCL, Intel/AMD/NVIDIA on Windows and
Linux). On startup the server prints which backend is active; if it falls back to
CPU, frame-skipping and resolution scaling keep it responsive.

## Troubleshooting

### The camera feed is black / "could not open the camera"

The first time, your OS must grant camera access.

- **macOS:** a permission dialog should pop up automatically on first run — click
  **Allow**. If you previously denied it, go to **System Settings → Privacy &
  Security → Camera**, enable your terminal/launcher, then start the lab again.
- **Windows:** make sure no other app (Zoom, Teams, the Camera app) is using the
  webcam, and that **Settings → Privacy & security → Camera** allows desktop apps
  to use the camera.

### `AttributeError: module 'mediapipe' has no attribute 'solutions'`

This lab uses MediaPipe's legacy `mp.solutions` API, which newer wheels (0.10.30+)
dropped. `pyproject.toml` pins a working version (`mediapipe==0.10.14`). If you
hit this, refresh the environment:

```sh
cd python-client
uv sync
```

## XIAO microcontroller (later unit)

The optional hardware unit flashes a Seeed Studio XIAO ESP32C3 so a gesture can
blink an LED across the room. This is documented in the course and will be
revised; note that on Windows the board appears as a `COM` port (e.g. `COM5`),
not `/dev/ttyACM0`.
