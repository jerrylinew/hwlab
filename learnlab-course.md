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
  face detection on every frame, and decides when a gesture happened. You only
  ever edit one small file here: `main.py`.
- **The Vue "website"** (`vue-client/`) — a web page you can customize. It shows
  the latest command coming from Python, lets you send a message *back* to
  Python, and can reveal the live annotated camera feed.

They talk to each other over two channels:

| Channel | What it carries |
|---|---|
| `GET /video_feed` | The live webcam image, with detection drawn on top |
| `WS /ws` | A two-way stream of commands — Python → website, and website → Python |

Later, recognized commands are also sent over WiFi to a **Seeed Studio XIAO**
microcontroller, so a gesture in front of your laptop can blink an LED or drive
a motor across the room.

Here's the whole pipeline in one line:

> **webcam → OpenCV → MediaPipe detection → your gesture rule → command → (Vue website + XIAO)**

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
- It replaces the Vue website
```

```quiz
type: mc
question: You're on Windows. Where do you install and run Nix?
- Directly in PowerShell
- *Inside WSL2 (the Ubuntu Linux environment)
- In the Vue website
- You can't use this project on Windows at all
```

## Unit: Run the Lab

### Lesson: Meet the Terminal

#### Section: What Is the Terminal?

You already used the **terminal** in Unit 1 to install Nix — now let's actually
learn it, because the rest of this lab lives here.

The terminal is just a way to tell your computer what to do by **typing**
instead of clicking. You type one line, press **Enter**, and the computer runs
it. That's the whole idea.

- **On Mac:** open the **Terminal** app (press ⌘-Space, type "Terminal", Enter).
- **On Windows:** open the **Ubuntu** app you installed in Unit 1 — that's your
  terminal.

You'll see a **prompt** — a line ending in `$` waiting for you to type:

```text
yourname@laptop ~ %
```

Every command has the same shape: a **command name**, sometimes followed by
**arguments**. For example, in `cd python-client`, the command is `cd` and the
argument is `python-client`. Spelling, spaces, and capitalization all matter —
the terminal is picky.

#### Section: Finding Your Way — `pwd`, `ls`, `cd`

Think of the terminal as standing inside one folder at a time. Three commands let
you look around and move:

```sh
pwd        # "print working directory" — which folder am I in right now?
ls         # "list" — what files and folders are in here?
cd NAME    # "change directory" — step INTO the folder called NAME
```

Two special moves with `cd`:

```sh
cd ..      # go UP one folder (to the parent)
cd ~       # jump to your home folder, from anywhere
```

Try it now. Navigate to the project folder and look inside — you should see the
two halves of the lab:

```sh
cd ~/hwlab     # or wherever you downloaded the project
ls
```

```text
README.md   python-client   vue-client
```

If `ls` shows `python-client` and `vue-client`, you're in the right place. If you
ever feel lost, type `pwd` to see exactly where you are.

#### Section: Three Shortcuts That Save You

These three habits will save you the most typing and the most frustration:

- **Tab to autocomplete.** Type `cd pyth` then press **Tab** — the terminal fills
  in `python-client/` for you. This avoids typos and is faster.
- **Up arrow for history.** Press **↑** to bring back the last command you ran, so
  you can re-run or edit it instead of retyping.
- **Ctrl-C to stop.** Some commands (like the servers you'll start next) keep
  running on purpose and "take over" the terminal. Press **Ctrl-C** to stop them
  and get your prompt back.

You don't need to memorize these — just know they exist and reach for them.

#### Section: Check Your Understanding

```quiz
type: mc
question: You're not sure which folder the terminal is currently "in." Which command tells you?
- ls
- *pwd
- cd ..
- nix develop
```

```quiz
type: mc
question: `ls` shows a folder called `python-client`. How do you step into it?
- pwd python-client
- *cd python-client
- ls python-client
- cd ..
```

```quiz
type: mc
question: You started a server and now the terminal won't accept new commands — it's "stuck" running the program. What gets your prompt back?
- Pressing Enter a few times
- Closing the laptop lid
- *Pressing Ctrl-C to stop the running program
- Typing pwd
```

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
open the Vue website instead. The real endpoints are `/video_feed` and `/ws`.

#### Section: Start the Vue Website

Leave the Python server running. Open a **second** terminal:

```sh
nix develop
cd vue-client
npm install
npm run dev
```

`npm install` downloads the web libraries (first time only). `npm run dev`
starts the viewer and prints a local URL — usually:

```text
http://localhost:5173
```

Open that URL in your browser. The website already knows where the Python
server is — it defaults to `http://localhost:8000`. (You can override that by
setting `VITE_PY_SERVER` in a `vue-client/.env` file, but you won't need to.)

#### Section: What Success Looks Like

The default page is titled **"My HW Lab Website"** — a page you'll customize
later. It has three parts:

- **Message From Python:** a big line that starts as *"No message yet."*
- **Send A Message To Python:** a button that sends `hello_from_vue` back to the
  Python side.
- **Show Camera Feed:** click to expand your live camera image. Raise a hand and
  a skeleton of dots and lines snaps onto it; look at the camera and a box
  appears around your face.

Now **give the camera a thumbs-up.** The "Message From Python" line should flip
to **`thumbs_up`**. The thumbs-up gesture is already wired up for you — in the
next units you'll understand how that wiring works, then add your own gestures.

If nothing happens, expand the camera feed first and confirm the hand skeleton
appears — detection has to see your hand before a gesture can fire.

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
You opened the Python server (`:8000`) instead of the Vue website (`:5173`).

#### Section: Check Your Understanding

```quiz
type: mc
question: You give a thumbs-up and "Message From Python" changes to `thumbs_up`. What does that confirm?
- Only that the camera turned on
- *The whole pipeline works — detection saw your hand, the gesture fired, and the command reached the website
- That you still need to wire up the gesture yourself
- That the XIAO is connected
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

The project keeps the messy plumbing out of your way. A background thread
(`CameraWorker`, in `lab_server.py`) runs a loop, roughly 30 times a second:

1. **Grab a frame** from the webcam with OpenCV (`cap.read()`).
2. **Mirror it** so it feels like a mirror (`cv2.flip`).
3. **Run detection** — MediaPipe finds hands and faces in the frame.
4. **Call your code** — for every hand it sees, it calls your `when_hand_seen(hand)`
   function in `main.py`. **This is the only part you edit.**
5. **Draw** the landmarks and face boxes onto the frame.
6. **Encode** the frame as a JPEG so it can be streamed to the browser.

You never touch steps 1–3, 5, or 6. You just fill in step 4: given one `hand`,
decide whether a gesture happened and send a command. When you *do* send one, it's
broadcast to the website over the `/ws` WebSocket as a small JSON message (and,
if enabled, POSTed over WiFi to the XIAO). Each message looks like:

```javascript
// each command message looks like:
// {
//   command: "thumbs_up",
//   sent_to_xiao: false,        // did the XIAO answer?
//   send_to_xiao_enabled: true, // is SEND_TO_XIAO turned on?
//   timestamp: "2026-06-16T21:24:02Z"
// }
```

#### Section: Hand Landmarks 101

MediaPipe describes a hand as **21 landmarks** — points like the wrist, each
knuckle, and each fingertip. Every landmark has an `x` (how far across) and a
`y` (how far down) coordinate.

Two things to burn into your memory:

- Coordinates are **normalized** from 0 to 1, not pixels. `x = 0.5` means
  halfway across the image, no matter the resolution.
- **`y` grows *downward*.** The top of the image is `y = 0`; the bottom is
  `y = 1`. So "higher up in the image" means a **smaller** `y`.

You refer to landmarks by name through an enum:

```python
import mediapipe as mp
HandLandmark = mp.solutions.hands.HandLandmark

# A landmark for one detected hand:
tip = hand_landmarks.landmark[HandLandmark.INDEX_FINGER_TIP]
print(tip.x, tip.y)   # e.g. 0.42 0.18  -> left-ish, near the top
```

Each finger has, from the palm outward, an **MCP** (knuckle), a **PIP** (middle
joint), and a **TIP**. To tell whether a finger is **extended** or **curled**, we
measure **distances** between landmarks rather than comparing raw `y` values. An
extended fingertip is the farthest point from the wrist; curl the finger and the
tip folds back toward the palm, ending up *closer* to the wrist than its own PIP
joint. That distance test holds **no matter how the hand is tilted** — comparing
`y` alone only works when the hand is upright.

#### Section: Reading the Example Gesture

The gesture rules live in `cv/gestures.py`. You *use* them from `main.py`, but
it's worth reading the one that's already wired up, `is_thumbs_up`. Read it slowly:

```python
# cv/gestures.py
import math
HandLandmark = mp.solutions.hands.HandLandmark

def _dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

def _extended(landmarks, tip, pip):
    # A finger is extended when its TIP is farther from the wrist than its
    # PIP joint. Curl it and the tip folds back toward the palm — closer in.
    wrist = landmarks[HandLandmark.WRIST]
    return _dist(landmarks[tip], wrist) > _dist(landmarks[pip], wrist)

def is_thumbs_up(hand_landmarks) -> bool:
    landmarks = hand_landmarks.landmark

    # 1. The four fingers must be CURLED into a fist (none extended).
    four_fingers = [
        (HandLandmark.INDEX_FINGER_TIP, HandLandmark.INDEX_FINGER_PIP),
        (HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.MIDDLE_FINGER_PIP),
        (HandLandmark.RING_FINGER_TIP, HandLandmark.RING_FINGER_PIP),
        (HandLandmark.PINKY_TIP, HandLandmark.PINKY_PIP),
    ]
    if any(_extended(landmarks, tip, pip) for tip, pip in four_fingers):
        return False

    # 2. The thumb must be EXTENDED out of the fist.
    if not _extended(landmarks, HandLandmark.THUMB_TIP, HandLandmark.THUMB_IP):
        return False

    # 3. ...and pointing UP. "Up" really is up, so here we DO use y:
    #    the thumb tip sits above the row of knuckles.
    knuckle_ys = [
        landmarks[HandLandmark.INDEX_FINGER_MCP].y,
        landmarks[HandLandmark.MIDDLE_FINGER_MCP].y,
        landmarks[HandLandmark.RING_FINGER_MCP].y,
        landmarks[HandLandmark.PINKY_MCP].y,
    ]
    return landmarks[HandLandmark.THUMB_TIP].y < min(knuckle_ys)
```

The `hand_landmarks` here is exactly the `hand` your `when_hand_seen(hand)`
function receives — so calling `is_thumbs_up(hand)` from `main.py` just works.

Notice the split: steps 1 and 2 use **distances to the wrist**, which don't care
how the hand is rotated. Only step 3 uses `y` — and that's on purpose, because
"thumbs-**up**" genuinely means *up* in the image. **Good gesture rules measure
shape (curled vs. extended) separately from orientation (which way is up).**

#### Section: Check Your Understanding

```quiz
type: mc
question: How does `_extended` decide a finger is extended rather than curled?
- *Its TIP is farther from the wrist than its PIP joint
- Its TIP has a smaller y value than its PIP joint
- Its TIP is on the left side of the image
- The finger is the longest one on the hand
```

```quiz
type: mc
question: Why measure distance-to-the-wrist instead of just comparing y values to detect a curled finger?
- y values are always wrong
- *Distances stay correct even when the hand is rotated or tilted; raw y only works when the hand is upright
- MediaPipe doesn't report y
- It makes the camera run faster
```

## Unit: Make It Send Commands

### Lesson: Read and Tweak the Gesture Block

#### Section: Your One Job — `when_hand_seen`

Open `main.py`. It's short — almost all of it is the one function you edit:

```python
from command_block import receive, send, send_when, set_send_to_xiao
from cv import count_extended_fingers, is_thumbs_up
from lab_server import create_app

# True  = send commands to the website AND the XIAO.
# False = send commands to the website only.
SEND_TO_XIAO = True
set_send_to_xiao(SEND_TO_XIAO)


def when_hand_seen(hand):
    """This runs every time the camera sees a hand."""
    send_when(is_thumbs_up(hand), "thumbs_up")


app = create_app(when_hand_seen)
```

That single line — `send_when(is_thumbs_up(hand), "thumbs_up")` — is the entire
thumbs-up feature. `when_hand_seen` is called once for **every hand** in the
frame, so `hand` is always a single hand.

#### Section: How `send_when` Reads

`send_when(condition, command)` is a "one-line gesture block." In plain English:

> *"When `condition` is true for a few frames in a row, send `command`."*

It does two smart things for you, both living in `command_block.py`:

1. **Confirm frames.** It waits until the gesture is seen `GESTURE_CONFIRM_FRAMES`
   (3) times in a row before firing, so a single bad frame can't trigger a false
   command.
2. **Cooldown.** After it fires, it ignores that same command for
   `COMMAND_COOLDOWN_SECONDS` (2.0). Otherwise a held thumbs-up — at ~30 frames a
   second — would spam dozens of commands.

```python
# command_block.py (you don't edit this — just understand it)
COMMAND_COOLDOWN_SECONDS = 2.0
GESTURE_CONFIRM_FRAMES = 3
```

#### Section: Make Your First Tweak

Edit `main.py` to feel the loop. Because you started `uvicorn` with `--reload`,
the server restarts itself every time you save.

- Change the command string to `send_when(is_thumbs_up(hand), "yes")`. Save, then
  thumbs-up: the message now reads `yes`.
- Add a plain `send`, which skips the gesture check and just fires (still
  rate-limited by the cooldown):

  ```python
  def when_hand_seen(hand):
      send_when(is_thumbs_up(hand), "thumbs_up")
      send("hand_visible")   # fires whenever ANY hand is on screen
  ```

#### Section: Test It

Make a thumbs-up at the camera. A new row appears with the command and a
timestamp, and its badge reads **"Vue only"** — that's expected, because you
haven't connected a XIAO yet. (Commands always reach the website regardless of
the XIAO.) You'll light up the **"XIAO + Vue"** badge in the hardware unit.

#### Section: Reflect

```quiz
type: frq
question: `send_when` waits for 3 confirming frames AND enforces a 2-second cooldown. Explain what each of those two rules prevents, and what would go wrong if you removed them.
prompt: Think about a single noisy frame, and about holding a gesture still for several seconds. 2-3 sentences.
```

## Unit: Add Your Own Gesture

### Lesson: The Open-Palm Challenge

#### Section: The Plan

Time to add a second gesture: an **open palm** (all five fingers extended). You
*could* write a landmark-by-landmark rule like `is_thumbs_up` does — but the lab
already ships a helper that counts extended fingers for you, so an open palm is a
one-liner.

#### Section: Meet `count_extended_fingers`

`cv/gestures.py` exports `count_extended_fingers(hand)`, which returns how many
fingers (0–5) are currently extended. An open palm is simply "all five":

```python
def when_hand_seen(hand):
    send_when(is_thumbs_up(hand), "thumbs_up")
    send_when(count_extended_fingers(hand) == 5, "open_hand")
```

Add that second line to `when_hand_seen` in `main.py` and save. A thumbs-up now
logs `thumbs_up`; an open hand logs `open_hand`. You have a two-gesture
controller — and you never had to touch the landmark math.

A closed fist is just as easy — that's zero extended fingers:

```python
    send_when(count_extended_fingers(hand) == 0, "fist")
```

#### Section: Going Deeper (Optional) — Write Your Own Classifier

Want full control? Add your own function to `cv/gestures.py`, right next to
`is_thumbs_up`, then import and use it from `main.py`. Reuse the `_extended`
helper that's already there — it reports whether one finger is extended, using
the rotation-safe distance-to-wrist test. For example, a "peace sign" extends
index + middle while curling ring + pinky:

```python
# cv/gestures.py
def is_peace_sign(hand_landmarks) -> bool:
    landmarks = hand_landmarks.landmark
    return (
        _extended(landmarks, HandLandmark.INDEX_FINGER_TIP,  HandLandmark.INDEX_FINGER_PIP)
        and _extended(landmarks, HandLandmark.MIDDLE_FINGER_TIP, HandLandmark.MIDDLE_FINGER_PIP)
        and not _extended(landmarks, HandLandmark.RING_FINGER_TIP,  HandLandmark.RING_FINGER_PIP)
        and not _extended(landmarks, HandLandmark.PINKY_TIP,        HandLandmark.PINKY_PIP)
    )
```

Then in `main.py`: `from cv import ..., is_peace_sign` and
`send_when(is_peace_sign(hand), "peace")`.

#### Section: Check Your Understanding

```quiz
type: mc
question: What is the simplest way to detect an open palm in this project?
- Rewrite the camera loop
- *Call `count_extended_fingers(hand) == 5` inside a `send_when(...)`
- Delete `is_thumbs_up`
- Lower the camera resolution
```

```quiz
type: mc
question: You want a thumbs-up and an open palm to send different commands. What's the cleanest approach?
- Use the same command string for both
- Delete `is_thumbs_up`
- *Add a second `send_when(...)` line in `when_hand_seen` with its own command name
- Increase `GESTURE_CONFIRM_FRAMES`
```

## Unit: Talk Back

### Lesson: Listening to the Website

#### Section: Messages Flow Both Ways

So far Python has done all the talking. But the `/ws` channel is two-way — the
website can send messages *to* Python too. On the default "My HW Lab Website"
page there's a **"Send A Message To Python"** button; clicking it sends
`hello_from_vue`.

To read it on the Python side, use the third one-line block, `receive()`:

```python
def when_hand_seen(hand):
    send_when(is_thumbs_up(hand), "thumbs_up")

    message = receive()              # the last message from the website (or XIAO)
    if message == "hello_from_vue":
        send("got_your_message")
```

`receive()` returns the most recent command string the website sent (or `None`
if there hasn't been one). Save, show the camera a hand, click the website button,
and watch `got_your_message` come back — a full round trip.

#### Section: Check Your Understanding

```quiz
type: mc
question: What does `receive()` return?
- The next gesture the camera will see
- *The most recent command the website (or XIAO) sent to Python, or None
- The number of extended fingers
- The webcam frame as a JPEG
```

## Unit: Talk to the Hardware

### Lesson: From Laptop to Microcontroller

#### Section: Meet the XIAO Client

When a command fires, the `send`/`send_when` blocks ultimately call
`send_command`, which lives in `xiao_client.py`. It just makes an HTTP request to
the microcontroller:

```python
XIAO_IP = "192.168.4.1"   # ESP32 access-point default
XIAO_PORT = 80

def send_command(command: str) -> bool:
    url = f"http://{XIAO_IP}:{XIAO_PORT}/command"
    try:
        resp = requests.post(url, json={"command": command}, timeout=1.0)
        return resp.ok
    except requests.RequestException:
        return False
```

Notice it **never raises** — if the XIAO is offline, it quietly returns `False`
so a network hiccup can't crash your camera loop. The XIAO's firmware lives in
`xiao/xiao.ino`, and there are two companion helpers in `xiao_client.py`:
`get_status()` and `get_command()` (the latter is what `receive()` uses to read
state back from the XIAO).

#### Section: Connect to the XIAO

The XIAO firmware in this lab runs its **own WiFi access point**, so its address
is the ESP32 default `192.168.4.1` — already set in `xiao_client.py`, usually
nothing to change. To reach it, **join the XIAO's WiFi network** from your laptop
(its name and password are set in `xiao/xiao.ino`).

> If your XIAO is instead configured to join an existing network, it will print a
> *different* IP to its serial monitor on boot — copy that into `XIAO_IP`, and
> make sure your laptop is on that same network.

One more switch: at the top of `main.py`, `SEND_TO_XIAO = True` sends commands to
both the website and the XIAO. Set it to `False` to develop gestures with no
hardware at all — commands still reach the website.

#### Section: How a Command Travels

Put the whole chain together. When you make a thumbs-up:

1. `is_thumbs_up(hand)` returns `True` inside `when_hand_seen`.
2. `send_when(..., "thumbs_up")` confirms it over a few frames, then calls `send`.
3. If `SEND_TO_XIAO` is on, `send_command("thumbs_up")` POSTs
   `{"command": "thumbs_up"}` to `http://<XIAO_IP>:80/command`.
4. The result (`True` if the XIAO answered, `False` otherwise) becomes the
   `sent_to_xiao` field; whether the toggle was on becomes `send_to_xiao_enabled`.
5. That message is broadcast to the website over `/ws`.

Those two fields color the badge in the log, which has **three** states:

| Badge | Meaning |
|---|---|
| **XIAO + Vue** | Sent to the website *and* the XIAO answered |
| **XIAO failed** | `SEND_TO_XIAO` is on, but the XIAO didn't answer (offline / wrong network) |
| **Vue only** | `SEND_TO_XIAO` is off — sent to the website on purpose, never tried the XIAO |

#### Section: Check Your Understanding

```quiz
type: mc
question: The "Commands Sent" log shows your command with an "XIAO failed" badge. What does that tell you?
- The gesture wasn't recognized
- The website is disconnected
- *The command fired and reached the website, and SEND_TO_XIAO is on, but the XIAO didn't answer (offline, wrong network, or wrong IP)
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

You now know the whole loop: in `when_hand_seen`, test a hand for a gesture and
`send_when` it maps to a command. Design your own scheme.

Pick **two or three gestures** and decide what command each should send. Easy
wins with `count_extended_fingers(hand)`: a closed fist (`== 0`), a pointing
finger (`== 1`), an open palm (`== 5`). For something the counter can't express
— like a peace sign — write a classifier in `cv/gestures.py` (see the optional
section in the Open-Palm lesson).

#### Section: Plan It Out

```quiz
type: frq
question: Describe your control scheme: which two or three gestures will you detect, what command will each one send, and for ONE of them, the exact `send_when(...)` line you'll add to `when_hand_seen`.
prompt: Example: "Open palm → 'stop'. I'll add `send_when(count_extended_fingers(hand) == 5, \"stop\")`."
```

#### Section: Stretch Goals

Want to go further? Try one of these:

- **React to faces.** `create_app` accepts a second callback:
  `create_app(when_hand_seen, when_face_seen)`. Write a `when_face_seen(face)`
  that fires a command — a presence detector.
- **Build your own website.** `App.vue` is yours to edit. Use the `command` from
  Python to change colors, show an image, or play a sound.
- **Talk back.** Use `receive()` plus a new button in `App.vue` to control Python
  from the page.
- **Two-handed gestures.** `when_hand_seen` is called once *per hand*, so a single
  call only ever sees one hand. To require *both* hands, track state across calls
  (e.g. remember the last hand's gesture in a module-level variable).
- **Make the XIAO react.** In `xiao/xiao.ino`, map commands like `"thumbs_up"` and
  `"open_hand"` to different LED colors or motor actions.

When it works, demo it to the group: make your gesture and watch the command
land in the log — and, if you've wired up a XIAO, in the real world.
