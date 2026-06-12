# OpenCV Gesture & Face Lab

A teaching setup where students write OpenCV gesture/face-detection code in
Python. When a gesture or face is detected, a command is sent to a Seeed
Studio XIAO webserver. A Vue app shows the live (annotated) webcam feed and a
log of commands sent.

## Quick start

```sh
nix develop
```

This sets up a Python virtualenv (OpenCV, MediaPipe, FastAPI) and gives you
Node.js for the Vue app.

### Run the Python client

```sh
cd python-client
uvicorn main:app --reload
```

- `main.py` opens your webcam, runs hand/face detection, and serves:
  - `GET /video_feed` - MJPEG stream of the annotated webcam feed
  - `WS /ws` - broadcasts each command as `{command, sent_to_xiao, timestamp}`
- `xiao_client.py` - set `XIAO_IP` to your Seeed Studio XIAO's IP address.

Look for `# STUDENTS:` comments in `main.py` - those are the places to add
your own gestures.

### Run the Vue viewer

```sh
cd vue-client
npm install
npm run dev
```

Open the printed local URL. You should see the webcam feed on the left and a
"Commands Sent" log on the right.
