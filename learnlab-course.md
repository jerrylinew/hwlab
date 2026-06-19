# Course: OpenCV Gesture & Face Lab
description: Build a webcam gesture controller — detect hand gestures with Python and MediaPipe, stream the result to a live web viewer, and fire commands at a microcontroller.
pace: 2

## Unit: Getting Set Up

### Lesson: Before You Write Any Code

#### Section: What You're Building

Welcome to the **OpenCV Gesture & Face Lab**. By the end of this workshop you'll
have a working system that watches your webcam, recognizes hand gestures, and
turns them into commands — the same idea behind touchless kiosks, sign-language
tools, and gesture-controlled robots.

The project has **two halves** that run at the same time:

- **The Python "brain"** (`python-client/`) — opens your webcam, runs hand and
  face detection on every frame, and decides when a gesture happened.
- **The Vue "viewer"** (`vue-client/`) — a web page that shows the annotated
  camera feed on the left and a live log of commands on the right.

They talk to each other over two channels:

| Channel | What it carries |
|---|---|
| `GET /video_feed` | The live webcam image, with detection drawn on top |
| `WS /ws` | A real-time stream of commands as they're recognized |

Later, recognized commands are also sent over WiFi to a **Seeed Studio XIAO**
microcontroller, so a gesture in front of your laptop can blink an LED or drive
a motor across the room.

Here's the whole pipeline in one line:

> **webcam → OpenCV → MediaPipe detection → your gesture rule → command → (Vue viewer + XIAO)**

#### Section: Install Nix

This project uses **Nix** to install everything it needs — Python, Node.js, and
all the libraries — with one command, so everyone in the workshop gets an
identical setup. You only install Nix once per computer.

**On Mac or Linux**, run this in a terminal, then open a *new* terminal window
when it finishes:

```sh
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
```

**On Windows**, Nix can't run directly — you install it inside WSL2 (a Linux
environment inside Windows). In PowerShell **as Administrator**:

```powershell
wsl --install
```

Reboot if asked, open the new **Ubuntu** app, then run the same Mac/Linux
command above *inside* that Ubuntu terminal.

Confirm it worked:

```sh
nix --version
```

#### Section: Enter the Dev Shell

From the project's top folder, run:

```sh
nix develop
```

The first time, this takes a few minutes. It:

1. Downloads Python 3.11 and Node.js 22.
2. Creates a Python virtual environment in `python-client/.venv`.
3. Installs OpenCV, MediaPipe, FastAPI, and the rest of the Python libraries.

When it's done you'll see a prompt change and a "HW Lab dev shell ready"
message. **Every terminal you use for this lab should start with `nix develop`** —
it's what puts `python`, `uvicorn`, and `npm` on your path.

#### Section: Check Your Understanding

```quiz
type: mc
question: What is the main reason this project uses Nix?
- It makes the webcam run faster
- *It gives everyone an identical setup with all dependencies in one command
- It is required by MediaPipe
- It replaces the Vue viewer
```

```quiz
type: mc
question: You're on Windows. Where do you install and run Nix?
- Directly in PowerShell
- *Inside WSL2 (the Ubuntu Linux environment)
- In the Vue viewer
- You can't use this project on Windows at all
```

## Unit: Run the Lab

### Lesson: Two Terminals, Two Halves

#### Section: Start the Python Brain

Open a terminal, enter the dev shell, then start the Python server:

```sh
nix develop
cd python-client
uvicorn main:app --reload
```

`uvicorn` is the web server that runs `main.py`. The `--reload` flag restarts it
automatically whenever you save a change — handy once you start editing.

When it's running you'll see `Application startup complete` and a line saying
it's listening on `http://127.0.0.1:8000`. Behind the scenes the camera has
opened and detection is already running.

This server is **data only** — there's no UI here. If you open
`http://localhost:8000/` in a browser you'll get a small page reminding you to
open the Vue viewer instead. The real endpoints are `/video_feed` and `/ws`.

#### Section: Start the Vue Viewer

Leave the Python server running. Open a **second** terminal:

```sh
nix develop
cd vue-client
npm install
npm run dev
```

`npm install` downloads the web libraries (first time only). `npm run dev`
starts the viewer and prints a local URL — usually:

```
http://localhost:5173
```

Open that URL in your browser. The viewer already knows where the Python server
is, thanks to this setting in `vue-client/.env`:

```sh
VITE_PY_SERVER=http://localhost:8000
```

#### Section: What Success Looks Like

In the browser you should see:

- **Left ("Webcam Feed"):** your live camera image. Raise a hand and a skeleton
  of dots and lines snaps onto it. Look at the camera and a box appears around
  your face.
- **Right ("Commands Sent"):** a green "connected" badge, and the message
  *"No commands yet - try making a gesture or showing your face!"*

That empty command log is **expected** right now. Detection is running, but the
project doesn't send any commands yet — wiring that up is your job in Unit 4.

#### Section: When Things Break

A few problems are common on the first run:

**macOS: "not authorized to capture video" / the feed is black.**
macOS needs to grant your terminal camera access. Go to **System Settings →
Privacy & Security → Camera**, enable your terminal app (Terminal, iTerm, VS
Code…), then fully quit and reopen it and run `uvicorn` again.

**`AttributeError: module 'mediapipe' has no attribute 'solutions'`.**
Your MediaPipe is too new — this lab uses the `mp.solutions` API, which newer
wheels dropped on Apple Silicon. `requirements.txt` pins a working version;
reinstall it:

```sh
pip install -r python-client/requirements.txt
```

**`npm install` fails with a dependency conflict.**
Make sure you pulled the latest project files — the Vue dependencies are pinned
to versions that work together.

**Browser shows `{"detail":"Not Found"}`.**
You opened the Python server (`:8000`) instead of the Vue viewer (`:5173`).

#### Section: Check Your Understanding

```quiz
type: mc
question: Why is the "Commands Sent" log empty even though hand detection is clearly working?
- The WebSocket is broken
- Your camera has no permission
- *Detection runs, but the project doesn't send any commands yet — that's the exercise
- The Vue viewer is pointed at the wrong port
```

```quiz
type: mc
question: Which URL should you open in your browser to use the lab?
- http://localhost:8000
- http://127.0.0.1:8000/video_feed
- *http://localhost:5173
- http://localhost:8000/ws
```

## Unit: How It Works

### Lesson: From Pixels to Commands

#### Section: The Pipeline

Inside `main.py`, a background thread (`CameraWorker`) runs a loop, roughly 30
times a second:

1. **Grab a frame** from the webcam with OpenCV (`cap.read()`).
2. **Mirror it** so it feels like a mirror (`cv2.flip`).
3. **Run detection** — MediaPipe finds hands and faces in the frame.
4. **Draw** the landmarks and face boxes onto the frame.
5. **(Your job, Unit 4)** check each hand for a gesture, and if it matches, send
   a command.
6. **Encode** the frame as a JPEG so it can be streamed to the browser.

When a command *is* sent, two things happen: it's broadcast to the Vue viewer
over the `/ws` WebSocket as a small JSON message, and it's POSTed over WiFi to
the XIAO. The viewer's "Commands Sent" panel just renders those JSON messages:

```javascript
// CommandLog.vue — each message looks like:
// { command: "true", sent_to_xiao: false, timestamp: "2026-06-16T21:24:02Z" }
commands.value.unshift(data);
```

#### Section: Hand Landmarks 101

MediaPipe describes a hand as **21 landmarks** — points like the wrist, each
knuckle, and each fingertip. Every landmark has `x`, `y`, and `z` coordinates.

Two things to burn into your memory:

- Coordinates are **normalized** from 0 to 1, not pixels. `x = 0.5` means
  halfway across the image, no matter the resolution.
- **`y` grows *downward*.** The top of the image is `y = 0`; the bottom is
  `y = 1`. So "higher up in the image" means a **smaller** `y`.

You refer to landmarks by name through an enum:

```python
import mediapipe as mp
Lm = mp.solutions.hands.HandLandmark

# A landmark for one detected hand:
tip = hand_landmarks.landmark[Lm.INDEX_FINGER_TIP]
print(tip.x, tip.y)   # e.g. 0.42 0.18  -> left-ish, near the top
```

Each finger has, from the palm outward, an **MCP** (knuckle), a **PIP** (middle
joint), and a **TIP**. Comparing a fingertip's `y` to its PIP joint's `y` tells
you whether the finger is **extended** (tip higher → smaller `y`) or **curled**
(tip lower → larger `y`).

#### Section: Reading the Example Gesture

The project ships one gesture rule, `is_thumbs_up`. Read it slowly:

```python
def is_thumbs_up(hand_landmarks) -> bool:
    landmarks = hand_landmarks.landmark
    Lm = mp.solutions.hands.HandLandmark

    # 1. The four fingers must be CURLED into a fist:
    #    each fingertip is at or below (larger y than) its middle joint.
    finger_tip_pip = [
        (Lm.INDEX_FINGER_TIP, Lm.INDEX_FINGER_PIP),
        (Lm.MIDDLE_FINGER_TIP, Lm.MIDDLE_FINGER_PIP),
        (Lm.RING_FINGER_TIP, Lm.RING_FINGER_PIP),
        (Lm.PINKY_TIP, Lm.PINKY_PIP),
    ]
    for tip, pip in finger_tip_pip:
        if landmarks[tip].y < landmarks[pip].y:
            return False  # this finger is extended, not curled

    # 2. The thumb must poke ABOVE the line of knuckles
    #    (smaller y than every knuckle).
    knuckle_ys = [
        landmarks[Lm.INDEX_FINGER_MCP].y,
        landmarks[Lm.MIDDLE_FINGER_MCP].y,
        landmarks[Lm.RING_FINGER_MCP].y,
        landmarks[Lm.PINKY_MCP].y,
    ]
    return landmarks[Lm.THUMB_TIP].y < min(knuckle_ys)
```

The clever part: it never checks whether the thumb points left or right. A
thumbs-up looks different at every angle, but "thumb sticks out above a fist" is
true for all of them. **Good gesture rules describe the *shape*, not one exact
pose.**

#### Section: Check Your Understanding

```quiz
type: mc
question: A fingertip landmark has y = 0.2 and its PIP joint has y = 0.6. Compared to the joint, the fingertip is...
- *Higher up in the image, so the finger is extended
- Lower in the image, so the finger is curled
- In the exact center of the image
- Off-screen
```

```quiz
type: mc
question: Why does is_thumbs_up NOT check whether the thumb points left or right?
- Left and right don't exist in MediaPipe
- *A thumbs-up can be held at many angles, so checking the overall shape is more reliable
- It's a bug in the example
- The thumb has no landmark
```

## Unit: Make It Send Commands

### Lesson: Wire Up the Thumbs-Up

#### Section: The Missing Link

Open `main.py` and find the camera loop in `CameraWorker._run`. Right now, when
a hand is found, it only *draws* the landmarks:

```python
if hand_results.multi_hand_landmarks:
    for hand_landmarks, handedness in zip(
        hand_results.multi_hand_landmarks, hand_results.multi_handedness
    ):
        drawing.draw_landmarks(
            frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
        )
```

Notice what's missing: the `is_thumbs_up` function is never *called*, and neither
is `_maybe_send_command`. That's why the command log stays empty. You're going to
connect them.

#### Section: Your First Edit

Add a gesture check **inside** the hand loop, right after the landmarks are
drawn:

```python
if hand_results.multi_hand_landmarks:
    for hand_landmarks, handedness in zip(
        hand_results.multi_hand_landmarks, hand_results.multi_handedness
    ):
        drawing.draw_landmarks(
            frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
        )

        # STUDENTS: check gestures here and send a command when they match.
        if is_thumbs_up(hand_landmarks):
            self._maybe_send_command("true")
```

Save the file. Because you started `uvicorn` with `--reload`, the server
restarts on its own. Switch to the browser and give the camera a thumbs-up.

#### Section: Understand the Cooldown

Why call `_maybe_send_command` instead of sending directly? Because the loop runs
~30 times a second — a held thumbs-up would fire 30 commands per second. The
helper enforces a **cooldown**:

```python
COMMAND_COOLDOWN_SECONDS = 2.0

def _maybe_send_command(self, command: str) -> None:
    now = time.monotonic()
    last_sent = self._last_sent.get(command, 0.0)
    if now - last_sent < COMMAND_COOLDOWN_SECONDS:
        return                      # too soon — ignore
    self._last_sent[command] = now
    sent_ok = send_command(command)         # try to reach the XIAO
    command_bus.publish(command, sent_ok)   # tell the Vue viewer
```

So one gesture sends at most one command every 2 seconds. Try changing
`COMMAND_COOLDOWN_SECONDS` to `0.5` and see how the log fills faster.

#### Section: Test It

Make a thumbs-up at the camera. In the "Commands Sent" panel you should now see
a new row appear with the command `true` and a timestamp.

The badge will say **"not sent"** (yellow) rather than "sent to XIAO". That's
correct — you don't have a XIAO connected yet, so the command had nowhere to go.
You'll fix that in the hardware unit. The point for now: **your gesture rule
fired and traveled all the way to the browser.**

#### Section: Reflect

```quiz
type: frq
question: In your own words, explain what would go wrong if you called send_command directly in the camera loop instead of going through _maybe_send_command.
prompt: Think about how many times per second the loop runs. 2-3 sentences.
```

## Unit: Add Your Own Gesture

### Lesson: The Open-Palm Challenge

#### Section: The Plan

Time to invent a gesture. We'll detect an **open palm** — all four fingers
extended (the opposite of the fist test inside `is_thumbs_up`).

Remember the rule for a finger: a fingertip with a **smaller `y`** than its PIP
joint is **extended**. For an open palm, that must be true for all four fingers.

#### Section: Write `is_open_palm`

Add this new function near `is_thumbs_up` in `main.py`:

```python
def is_open_palm(hand_landmarks) -> bool:
    """True when all four fingers are extended (an open hand)."""
    landmarks = hand_landmarks.landmark
    Lm = mp.solutions.hands.HandLandmark

    finger_tip_pip = [
        (Lm.INDEX_FINGER_TIP, Lm.INDEX_FINGER_PIP),
        (Lm.MIDDLE_FINGER_TIP, Lm.MIDDLE_FINGER_PIP),
        (Lm.RING_FINGER_TIP, Lm.RING_FINGER_PIP),
        (Lm.PINKY_TIP, Lm.PINKY_PIP),
    ]
    for tip, pip in finger_tip_pip:
        if landmarks[tip].y > landmarks[pip].y:
            return False  # this finger is curled, not extended
    return True
```

Compare it to `is_thumbs_up`: the fist test used `<` to reject *extended*
fingers; here we use `>` to reject *curled* ones. Same landmarks, opposite goal.

#### Section: Wire It to a New Command

Back in the hand loop, add your new gesture next to the thumbs-up. Give it a
different command name so you can tell them apart in the log:

```python
        if is_thumbs_up(hand_landmarks):
            self._maybe_send_command("true")
        elif is_open_palm(hand_landmarks):
            self._maybe_send_command("stop")
```

Save, then test both: a thumbs-up logs `true`, an open palm logs `stop`. You now
have a two-gesture controller.

#### Section: Check Your Understanding

```quiz
type: mc
question: In is_open_palm, why does the check use `landmarks[tip].y > landmarks[pip].y` to return False?
- Because the thumb is special
- *A fingertip LOWER than its joint (larger y) means the finger is curled, which disqualifies an open palm
- Because y is measured in pixels
- To detect a fist instead
```

```quiz
type: mc
question: You want a thumbs-up and an open palm to send different things. What's the cleanest approach?
- Use the same command string for both
- Delete is_thumbs_up
- *Call _maybe_send_command with a different command name for each gesture
- Lower the camera resolution
```

## Unit: Talk to the Hardware

### Lesson: From Laptop to Microcontroller

#### Section: Meet the XIAO Client

When a command fires, `_maybe_send_command` calls `send_command`, which lives in
`xiao_client.py`. It just makes an HTTP request to the microcontroller:

```python
XIAO_IP = "192.168.1.42"   # TODO: replace with your XIAO's IP address
XIAO_PORT = 80

def send_command(command: str) -> bool:
    url = f"http://{XIAO_IP}:{XIAO_PORT}/command"
    try:
        response = requests.post(url, json={"command": command}, timeout=1.0)
        return response.ok
    except requests.RequestException:
        return False
```

Notice it **never raises** — if the XIAO is offline, it quietly returns `False`
so a network hiccup can't crash your camera loop.

#### Section: Set Your XIAO_IP

Your XIAO prints its IP address to the serial monitor when it connects to WiFi
(something like `192.168.1.42`). Copy that value into `XIAO_IP` in
`xiao_client.py` and save.

Your laptop and the XIAO must be on the **same WiFi network** for the request to
reach it.

#### Section: How a Command Travels

Put the whole chain together. When you make a thumbs-up:

1. `is_thumbs_up` returns `True` in the camera loop.
2. `_maybe_send_command("true")` checks the cooldown.
3. `send_command("true")` POSTs `{"command": "true"}` to
   `http://<XIAO_IP>:80/command`.
4. The return value (`True` if the XIAO answered, `False` if not) becomes the
   `sent_to_xiao` field.
5. `command_bus.publish` sends that to the Vue viewer over `/ws`.

That `sent_to_xiao` value is exactly what colors the badge in the log:
**green "sent to XIAO"** when the request succeeded, **yellow "not sent"** when
it didn't.

#### Section: Check Your Understanding

```quiz
type: mc
question: The "Commands Sent" log shows your command with a yellow "not sent" badge. What does that tell you?
- The gesture wasn't recognized
- The Vue viewer is disconnected
- *The command was recognized, but the request to the XIAO didn't succeed (offline, wrong IP, or different network)
- Your camera permission is off
```

```quiz
type: mc
question: Why does send_command catch exceptions and return False instead of letting them propagate?
- To make the XIAO faster
- *So a network problem can't crash the camera detection loop
- Because requests can't raise exceptions
- To hide bugs from students
```

## Unit: Capstone

### Lesson: Make It Yours

#### Section: Design a Control Scheme

You now know the whole loop: detect a hand shape, write a rule that returns
`True`/`False`, and map it to a command. Design your own scheme.

Pick **two or three gestures** and decide what command each should send. Some
ideas to detect: a peace sign (index and middle extended, ring and pinky
curled), a pointing finger (only the index extended), or a closed fist (all four
fingers curled — the first half of the thumbs-up test, on its own).

#### Section: Plan It Out

```quiz
type: frq
question: Describe your control scheme: which two or three gestures will you detect, what command will each one send, and for ONE of them, which landmarks you'll compare and how.
prompt: Example: "Peace sign → 'photo'. I'll check that INDEX_FINGER_TIP and MIDDLE_FINGER_TIP are above their PIP joints (extended), while RING and PINKY tips are below theirs (curled)."
```

#### Section: Stretch Goals

Want to go further? Try one of these:

- **Use the face.** `face_results.detections` already finds faces. Send a command
  when a face appears or disappears — a presence detector.
- **Count fingers.** Write a helper that returns *how many* fingers are extended,
  and send the number as the command.
- **Two-handed gestures.** The loop already handles up to two hands
  (`max_num_hands=2`). Trigger a command only when *both* hands make a fist.
- **Make the XIAO react.** On the microcontroller side, map `"true"` and `"stop"`
  to different LED colors or motor actions.

When it works, demo it to the group: make your gesture and watch the command
land in the log — and, if you've wired up a XIAO, in the real world.
