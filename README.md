# OpenCV Gesture & Face

## Quick start

Make sure that Nix is installed on the computer

```sh
nix develop
```

This sets up a Python venv and gives you Node.js for the Vue app. This is the simple dev shell with all the necessary dependencies. 

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

A lot of this is currently a lot of the code is done and documented within the `main.py` so visit it if you have any possible questions. 

Open the printed local URL. You should see the webcam feed on the left and a
"Commands Sent" log on the right.
