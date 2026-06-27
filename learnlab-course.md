# Course: AI and Computer Vision Lab
description: Build a gesture controller with your webcam — make a thumbs-up or a smile trigger an action, watch it happen live in your browser, and even light up a real gadget.
pace: 2

## Unit: Getting Set Up

### Lesson: Before You Write Any Code

#### Section: What You're Building

Welcome! By the end of this workshop you'll have built something that **watches
your webcam, recognizes your hand gestures, and turns them into actions** — like
giving a thumbs-up to turn on a light. It's the same idea behind touchless
kiosks, sign-language apps, and gesture-controlled robots.

Here's the whole thing in one sentence:

> **Your camera sees a gesture → your code decides what it means → something happens.**

There are **three pieces** working together:

- **The camera watcher** — software running on your computer that looks at your
  webcam and figures out what your hands and face are doing.
- **The web page** — a page that opens in your browser and shows the live camera
  view and the gestures it spots as they happen.
- **The gadget** *(optional, later)* — a small gizmo that can blink a light or
  spin a motor when you make a gesture, so the action can happen out in the real
  world and not just on screen.

The good news: most of this is already built for you. **Your job is to write the
rules** — the part that says "when the camera sees *this*, do *that*." You'll do
that by editing one short file, and you'll see your changes come to life
instantly in the browser.

#### Section: Download the Project

You don't need to install Python, Node, or any code editor first — the lab
installs everything it needs the first time you start it. You just need the
project files.

1. Go to the project on GitHub — **[github.com/jerrylinew/hwlab](https://github.com/jerrylinew/hwlab)** — and
   click the green **Code** button, then **Download ZIP**.
2. Find the downloaded `hwlab.zip` (usually in your **Downloads** folder) and
   **unzip** it — double-click on Mac, or right-click → **Extract All** on
   Windows.
3. You now have a folder called `hwlab` with everything inside.

That's it — no terminal yet.

#### Section: Start the Lab

Inside the `hwlab` folder there are two launchers. Use the one for your computer:

- **Mac:** double-click **`Start HW Lab.command`**.
- **Windows:** double-click **`Start HW Lab.bat`**.

> ⚠️ **First-time security warning — this is expected.** The launcher isn't
> signed by the App Store, so your computer blocks it the very first time and you
> have to allow it once:
>
> - **Mac:** double-clicking shows a warning that the file *"cannot be opened
>   because it is from an unidentified developer"* (or *"Apple could not verify…"*).
>   Click **Done**, then open **System Settings → Privacy & Security** and scroll
>   down to the **Security** section. You'll see a note that
>   *"Start HW Lab.command" was blocked* — click **Open Anyway**, then confirm
>   with **Open Anyway** and your password or Touch ID. Now double-click the
>   launcher again. You only do this once.
> - **Windows:** a blue **"Windows protected your PC"** box appears — click
>   **More info**, then **Run anyway**.

The **first time**, a black window opens and spends a few minutes installing
Python, the camera libraries, and everything else automatically. When it's
ready, your web browser opens to the lab at **http://localhost:8000**, showing
your webcam with detection drawn on top. Later starts take only a few seconds.

One more first-time prompt, once the lab is running:

- **"Allow camera access?"** — click **Allow**, or the feed stays black.

**Leave the black window open while you work.** It *is* the lab — closing it (or
pressing **Ctrl-C** inside it) stops everything.

#### Section: Check Your Understanding

```quiz
type: mc
question: Before starting the lab the first time, what do you need to install yourself?
- Python, Node, and a code editor
- *Nothing — the launcher installs everything automatically
- Only a web browser plugin
- A virtual machine
```

```quiz
type: mc
question: After the lab starts, where do you see your webcam feed?
- In the black launcher window
- *In your web browser, at http://localhost:8000
- In a separate camera app you install
- You have to start a second program for the website
```

```quiz
type: mc
question: What happens if you close the black launcher window while working?
- Nothing, it keeps running in the background
- *It stops the lab — leave it open while you work
- It saves your code
- It restarts your computer
```

## Unit: Run the Lab

### Lesson: The Launcher Window

#### Section: What the Black Window Is

When you double-clicked the launcher, a plain black window opened with scrolling
text. That window is a **terminal** — the place where the lab program runs and
prints what it's doing. You mostly **don't type anything in it**; the launcher
already ran the right commands for you.

You only need to know two things about it:

- **Leave it open while you work.** That window *is* the running lab. The camera,
  the detection, and the web page all come from the program inside it.
- **To stop the lab, double-click the Stop launcher** (`Stop HW Lab.command` on
  Mac, `Stop HW Lab.bat` on Windows). This shuts the lab down and **turns the
  camera off** — you'll see the camera light go dark. (Pressing **Ctrl-C** in the
  black window or closing it does the same thing.)

Stopping the lab is how you turn the webcam off when you're done.

#### Section: Check Your Understanding

```quiz
type: mc
question: What is the black window that opens when you start the lab?
- A virus warning you should close immediately
- *A terminal where the lab program runs — leave it open while you work
- The web page you customize
- A place you must type commands to start the camera
```

```quiz
type: mc
question: How do you stop the lab and turn the camera off?
- Restart your computer
- *Double-click the Stop launcher (or press Ctrl-C in the black window)
- Refresh the web page
- Unplug the webcam
```

### Lesson: Your Lab in the Browser

#### Section: What Success Looks Like

When the lab is running, your browser shows the page at
**http://localhost:8000**, titled **"OpenCV Gesture & Face Lab."** It has:

- **Webcam Feed** (left): your live camera image. Raise a hand and a skeleton of
  dots and lines snaps onto it; look at the camera and a box appears around your
  face.
- **Commands Sent** (right): a log of commands, with **"Latest from Python"**
  starting at *none*.
- **Debug Status** (bottom): live health for Python, the web page, and the XIAO.

Now **give the camera a thumbs-up.** "Latest from Python" should flip to
**`thumbs_up`** and a new row appears in the command log. The thumbs-up gesture
is already wired up for you — in the next units you'll understand how that wiring
works, then add your own gestures.

If nothing happens, check that the hand skeleton appears on the feed first —
detection has to see your hand before a gesture can fire.

#### Section: When Things Break

A few problems are common on the first run:

**The camera feed is black.**
Your computer needs permission to use the webcam.
- *Mac:* a permission dialog should pop up the first time — click **Allow**. If
  you dismissed it, go to **System Settings → Privacy & Security → Camera**,
  enable your launcher, then start the lab again.
- *Windows:* close any app already using the camera (Zoom, Teams, the Camera
  app), and check **Settings → Privacy & security → Camera** allows desktop apps
  to use the camera. Then restart the lab.

**The browser didn't open by itself.**
Open it yourself and go to **http://localhost:8000**.

**`AttributeError: module 'mediapipe' has no attribute 'solutions'`.**
A rare library mismatch. Stop the lab, then in the `python-client` folder run
`uv sync` to restore the pinned versions, and start the lab again.

#### Section: Check Your Understanding

```quiz
type: mc
question: You give a thumbs-up and "Latest from Python" changes to `thumbs_up`. What does that confirm?
- Only that the camera turned on
- *The whole pipeline works — detection saw your hand, the gesture fired, and the command reached the web page
- That you still need to wire up the gesture yourself
- That the XIAO is connected
```

```quiz
type: mc
question: Which URL shows your lab in the browser?
- http://localhost:5173
- *http://localhost:8000
- http://localhost:8000/video_feed
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

**A closer look at step 3 — the computer vision.** "Run detection" is where the
real CV happens, and everything you build sits on top of it, so it's worth
understanding. **MediaPipe** is a library from Google that runs small,
pre-trained machine-learning models on each frame — entirely **on your laptop**,
in real time, with no cloud and no internet round-trip. For this lab it runs two
separate pipelines:

- **Hands.** First a *palm detector* scans the whole frame and finds *where* any
  hands are. Then, for each hand it found, a second *landmark model* zooms into
  that region and pinpoints 21 specific points — fingertips, knuckles, the wrist
  (the next section is all about these). It also labels each hand **Left** or
  **Right**.
- **Face.** A face detector returns a bounding box, plus a few key points like
  the eyes and nose, for every face in view.

A few things that explain the behavior you'll see:

- It works **frame by frame** — each frame is analyzed on its own. Once
  MediaPipe has locked onto a hand, it *tracks* that hand into the next frame
  instead of re-scanning from scratch. That's cheaper, and it's why the
  landmarks glide smoothly as you move rather than flickering.
- Every detection comes with a **confidence score**, and low-confidence ones are
  thrown out. So a blurry, fast-moving, or half-out-of-frame hand may simply not
  register — hold it flat and well-lit and it snaps right back.
- By step 4 the hard ML work is already done. All you receive is the clean
  result: a list of hands, each carrying its 21 landmarks. Your job is just to
  read those numbers and decide whether a gesture happened.

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

The gesture rules live in `cv/gestures.py`. You *call* them from `main.py`, and
you can open `cv/gestures.py` right in the lab editor (pick it from the file tabs)
to read or change them. It's worth reading the one that's already wired up,
`is_thumbs_up`. Read it slowly:

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

You edit your code **right on the lab page** — scroll down to the **Edit Your
Gestures** panel. It opens `main.py`, where you'll spend most of your time. Use
the **file tabs** at the top of the panel to switch files: `main.py` and
`cv/gestures.py` are both editable, while the rest are read-only (marked with a
🔒) so you can read the lab's plumbing without breaking it. There's no separate
code editor to install. When you click **Save & Run** — or press **Cmd-S** (Mac)
/ **Ctrl-S** (Windows) — the lab checks your code for typos, saves it, and
restarts itself with your changes.

`main.py` is short — almost all of it is the one function you edit:

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

In the **Edit Your Gestures** panel, make a small change and click **Save & Run**
to feel the loop — the lab restarts itself with your new code each time you save.
(If you make a typo, Save & Run won't break the lab; it tells you which line to
fix.)

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

Want full control? Open `cv/gestures.py` from the file tabs in the lab editor and
add your own function, right next to `is_thumbs_up`, then import and use it from
`main.py`. Reuse the `_extended`
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
`send_when(is_peace_sign(hand), "peace")`. That's it — `cv` automatically picks up
any gesture you add to `gestures.py`, so you never have to edit another file.

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

## Unit: Set Up the Arduino IDE

### Lesson: Install the IDE and the XIAO Board

#### Section: Why You Need the Arduino IDE

So far everything has run on your laptop. To make a **real gadget** react — light
an LED, beep a buzzer, draw on a panel — you have to load a program onto the
**Seeed Studio XIAO ESP32C3** microcontroller. The tool that compiles that
program and copies it onto the board is the **Arduino IDE**.

You'll do this once: install the IDE, teach it about the XIAO board, then upload
the lab firmware. After that, every gesture you make can reach into the real
world.

> 📷 *The screenshots below are reference shots from the official guides — your
> screen may look slightly different by version. Replace them with your own as
> needed.*

#### Section: Install the Arduino IDE

Follow Arduino's official guide:
**[Download and install Arduino IDE](https://support.arduino.cc/hc/en-us/articles/360019833020-Download-and-install-Arduino-IDE)**.

1. Go to **[arduino.cc/en/software](https://www.arduino.cc/en/software)** and
   download the **Arduino IDE 2.x** for your operating system (Windows, macOS, or
   Linux).

   ![Arduino IDE download page](images/arduino-download.png)

2. **Windows:** run the downloaded `.exe`, accept the license, keep the default
   options, and click **Install**. If Windows asks to install USB drivers, click
   **Yes / Install** — the board needs them.

   **macOS:** open the downloaded file and **drag the Arduino IDE icon into your
   Applications folder**, then open it. The first time, macOS may warn it's from
   an unidentified developer — open **System Settings → Privacy & Security** and
   click **Open Anyway**.

   ![Installing the Arduino IDE](images/arduino-install.png)

3. Open the Arduino IDE. You should see a blank sketch with `setup()` and
   `loop()`. You're ready.

#### Section: Add the XIAO ESP32C3 Board

A fresh Arduino IDE doesn't know about the XIAO yet. Teach it, following
Seeed's guide:
**[XIAO ESP32C3 Getting Started](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/)**.

1. Open **File → Preferences** (macOS: **Arduino IDE → Settings**). In the
   **Additional boards manager URLs** field, paste:

   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```

   Click **OK**.

   ![Adding the board manager URL in Preferences](https://files.seeedstudio.com/wiki/XIAO_WiFi/add_board.png)

2. Open **Tools → Board → Boards Manager**, type **`esp32`** in the search box,
   find **esp32 by Espressif Systems**, and click **Install**. (This downloads a
   few hundred MB — give it a minute.)

   ![Installing the esp32 board package](https://files.seeedstudio.com/wiki/XIAO_WiFi/add_esp32c3.png)

3. Plug the XIAO into a USB port. Then open **Tools → Board → ESP32 Arduino** and
   scroll down to choose **XIAO_ESP32C3**.

   ![Selecting the XIAO_ESP32C3 board](https://files.seeedstudio.com/wiki/Seeed-Studio-XIAO-ESP32/XIAO_ESP32_board.png)

4. Open **Tools → Port** and pick the port that appeared when you plugged in the
   board (often `COM3` or higher on Windows, or `/dev/cu.usbmodem…` on macOS).

#### Section: A Simple LED on GPIO0 (Your First Sketch)

Before uploading the big lab firmware, prove the whole chain works with the
classic first program — a **blinking LED.** Unlike many dev boards, the XIAO
ESP32C3 has **no built-in user LED**, so you'll wire your own to **GPIO0**.

**Wiring:**

![Breadboard wiring: an LED on GPIO0 (D0) through a 220 Ω resistor to GND](https://raw.githubusercontent.com/jerrylinew/hwlab/main/images/led-gpio0-wiring.png)

- The LED's **long leg** (positive) goes to **GPIO0 — the pin labeled `D0`** —
  through a **220 Ω resistor** so it doesn't draw too much current.
- The LED's **short leg** (negative) goes to **GND**.

In the Arduino IDE, **File → New Sketch**, delete what's there, and type this in
yourself:

```cpp
#define LED_PIN D0   // the pin your LED's long leg connects to

void setup() {
  pinMode(LED_PIN, OUTPUT);   // get the pin ready
}

void loop() {
  digitalWrite(LED_PIN, HIGH);  // LED ON  (a breadboard LED lights on HIGH)
  delay(500);                   // wait half a second
  digitalWrite(LED_PIN, LOW);   // LED OFF
  delay(500);                   // wait half a second
}
```

Click the **→ Upload** button (top-left). When it finishes, your LED blinks once
a second. 🎉 You just compiled and ran code on real hardware.

> **Make it yours:** change both `delay(500)` values to `delay(100)` for a fast
> blink, or `delay(1000)` for a slow one. Upload again and watch it change.

Here a breadboard LED lights when the pin goes **HIGH**; pulling it `LOW` turns
it off. (That's the opposite of boards with a built-in LED, which are usually
*active-low* — the XIAO simply doesn't have one.)

#### Section: Change the WiFi Password

⚠️ **Before you upload, change the WiFi password.** Every XIAO ships with the
same default network name and password, so in a room full of labs they'd all
collide — and anyone nearby could join yours. Near the top of `xiao/xiao.ino`,
edit these two lines:

```cpp
const char* WIFI_NAME = "HWLab-XIAO";     // pick a unique name
const char* WIFI_PASSWORD = "hwlab1234";  // pick your own password (8+ characters)
```

Give your network a name you'll recognize and a password **at least 8
characters** long (the ESP32 requires it). Then upload, and when you join the
XIAO's WiFi from your laptop later, use the new name and password.

#### Section: Check Your Understanding

```quiz
type: mc
question: Why do you paste a URL into "Additional boards manager URLs" in Preferences?
- To connect to the XIAO's WiFi
- *So the Arduino IDE can download the ESP32 board package and know about the XIAO_ESP32C3
- To set the upload speed
- To install Python
```

```quiz
type: mc
question: You wire an LED from D0 through a resistor to GND, but it never lights — even though the pin goes HIGH. What's the most likely fix?
- *Flip the LED around — the long leg (positive) must go to D0, the short leg to GND
- Delete the resistor
- The XIAO's built-in LED is broken
- Switch to a buzzer
```

### Lesson: Hardware Modifications

#### Section: Beyond the LED

The simple LED is enough to demo the whole pipeline. But the firmware can drive
more, and each add-on works the same way: wire it to a pin, and call a small
helper. This lesson is optional — pick up a **buzzer** or a **16×16 LED grid**
when you want a bigger payoff.

#### Section: Add a Buzzer

A piezo buzzer is the same idea as an LED — one signal pin — but it makes
*sound*. The firmware ships a `Buzzer` submodule that plays musical notes by
name.

**Wiring** *(a wiring photo will be added here)*:

- The buzzer's **signal** pin goes to **`D2`**.
- The buzzer's **other** pin goes to **GND**.

Then tell the firmware which pin it's on by uncommenting one line in `setup()`:

```cpp
// xiao/xiao.ino
void setup() {
  led.begin();
  buzzer.begin(D2);   // <-- uncomment this after wiring the buzzer
  ...
}
```

Now any command can make noise:

```cpp
buzzer.playNote("C4", 250);   // note name, milliseconds
buzzer.playNote("A5", 100);   // higher and shorter

// play a little tune:
const String notes[]   = {"C4", "E4", "G4", "C5"};
const int    durs[]    = {200, 200, 200, 400};
buzzer.playMelody(notes, durs, 4);
```

Note names are a letter (`C`–`B`), an optional `#` for sharp, and an octave
number — so `"C4"`, `"F#4"`, `"A5"`. Use `"REST"` for a silent beat.

#### Section: Wire the Panel and Install the Library (16×16 Grid)

For a bigger payoff than one LED, the firmware includes **`LightGrid16x16`** — a
16×16 drawing canvas. To light a real panel:

1. Wire a **WS2812B / NeoPixel 16×16 matrix**: its `DIN` to pin **`D6`**, `5V` to
   `5V`, and `GND` to `GND`. *(A wiring photo will be added here.)*
2. In the Arduino IDE, open **Tools → Manage Libraries**, search **Adafruit
   NeoPixel**, and install it.
3. In `xiao/xiao.ino`, change `#define USE_LED_MATRIX 0` to **`1`** and upload
   again.

The mapping from "draw on a grid" to "set the right LED" — including the zig-zag
wiring of most panels — is handled for you in the `matrixWriter` function. You
just draw; `renderMatrix()` pushes your drawing to the panel.

#### Section: The LightGrid API

You draw onto the grid, then call `renderMatrix()` to show it. Coordinates run
`x` 0–15 left to right and `y` 0–15 top to bottom. Colors are `0xRRGGBB`
(e.g. `0xFF0000` red, `0x00FF00` green, `0x0000FF` blue).

```cpp
lightGrid.clear();                       // turn everything off
lightGrid.clear(0x202020);               // ...or fill with a dim color
lightGrid.setPixel(3, 5, 0xFF0000);      // one red pixel at (3, 5)
lightGrid.fillRect(0, 0, 4, 4, 0x00FF00); // a solid 4x4 green square
lightGrid.drawRect(0, 0, 16, 16, 0x0000FF); // a blue border around the edge
lightGrid.drawLine(0, 0, 15, 15, 0xFFFFFF); // a white diagonal
lightGrid.drawText(1, 4, "HI", 0xFF00FF);   // small text
renderMatrix();                          // <-- nothing shows until you call this
```

A quick example you can drop into `setup()` (after `lightGrid.begin(...)`): a blue
frame with green text inside.

```cpp
lightGrid.clear();
lightGrid.drawRect(0, 0, 16, 16, 0x0000FF);
lightGrid.drawText(2, 5, "GO", 0x00FF00);
renderMatrix();
```

| Call | What it does |
|---|---|
| `clear(color)` | Fill the whole grid (default black/off) |
| `setPixel(x, y, color)` | Light one pixel |
| `getPixel(x, y)` | Read a pixel's color back |
| `fillRect(x, y, w, h, color)` | Solid rectangle |
| `drawRect(x, y, w, h, color)` | Rectangle outline |
| `drawLine(x0, y0, x1, y1, color)` | A line between two points |
| `drawText(x, y, text, color)` | Draw letters and digits |
| `drawBitmap(rows, height, color)` | Draw a static image (next section) |
| `renderMatrix()` | Push everything you drew to the panel |

#### Section: Draw a Static Image From a Bitmap

To draw a **picture** instead of shapes, describe it as a **bitmap**: one number
per row, where each *bit* is one pixel — `1` lights up, `0` stays dark. Because
the grid is 16 wide, each row is a 16-bit number, and the leftmost pixel is the
highest bit.

The firmware includes a `SMILEY` bitmap you can edit pixel by pixel:

```cpp
// xiao/xiao.ino — change the 1s and 0s to draw your own image
const uint16_t SMILEY[16] = {
  0b0000000000000000,
  0b0001111111110000,
  0b0011000000011000,
  0b0110000000001100,
  0b0100110001100100,
  0b1100110001100110,
  0b1100000000000110,
  0b1100000000000110,
  0b1100100000010110,
  0b1100110000110110,
  0b0110011111100100,
  0b0110000000001100,
  0b0011000000011000,
  0b0001111111110000,
  0b0000000000000000,
  0b0000000000000000,
};

// draw it in green:
lightGrid.clear();
lightGrid.drawBitmap(SMILEY, 16, 0x00FF00);
renderMatrix();
```

`drawBitmap(rows, height, color)` walks each row and lights every `1` in the
color you pass. Design your own image by flipping bits — a heart, an arrow, your
initials. There are no built-in pictures: the bitmap is yours to define.

#### Section: Wire It to Your Gestures

In the example firmware, gestures already drive the grid (when `USE_LED_MATRIX`
is `1`): an **open palm** draws the smiley, a **fist** clears it. The handler
looks like this:

```cpp
case CommandCode::OpenHand:
  led.on();
  lightGrid.clear();
  lightGrid.drawBitmap(SMILEY, 16, 0x00FF00);
  renderMatrix();
  break;

case CommandCode::Fist:
  led.off();
  lightGrid.clear();
  renderMatrix();
  break;
```

Swap in your own bitmap, change the color, or draw text instead — then make the
gesture and watch your panel light up.

#### Section: Check Your Understanding

```quiz
type: mc
question: Which call makes the buzzer play a note?
- led.toggle()
- *buzzer.playNote("C4", 250)
- buzzer.on()
- lightGrid.show()
```

```quiz
type: mc
question: What do you need before the 16×16 matrix code will work?
- Nothing, it's on by default
- *Wire the panel to D6, install the Adafruit NeoPixel library, and set USE_LED_MATRIX to 1
- A second XIAO board
- A different web browser
```

```quiz
type: mc
question: You called several `lightGrid` drawing functions but the panel stays dark. What did you forget?
- To plug in the LED on D0
- *To call `renderMatrix()` — drawing only changes the buffer until you push it to the panel
- To install Python
- To lower the camera resolution
```

```quiz
type: mc
question: In a `drawBitmap` row like `0b0001111111110000`, what does each bit control?
- The brightness of the whole row
- *One pixel — a 1 lights that pixel in the chosen color, a 0 leaves it dark
- The color of the row
- Nothing; the number is decorative
```

## Unit: Talk to the Hardware

### Lesson: From Laptop to Microcontroller

#### Section: Upload the Lab Firmware

Now load the real thing. In the IDE, **File → Open**, navigate into your `hwlab`
folder, and open **`xiao/xiao.ino`**. With **XIAO_ESP32C3** and the right
**Port** still selected, click **→ Upload**.

When it's done, the XIAO starts its own WiFi network (`HWLab-XIAO`) and is ready
to receive commands over WiFi — which is what the rest of this unit walks you
through.

The firmware drives that same LED on `D0` through a tiny helper class, `Led`, so
you control it in plain English instead of raw `digitalWrite`:

```cpp
// xiao/xiao.ino — already set up for you
Led led(D0);            // a single LED on GPIO0 (HIGH = on)

void setup() {
  led.begin();          // get the pin ready
}
```

```cpp
led.on();               // turn it on
led.off();              // turn it off
led.toggle();           // flip it
led.set(true);          // on; led.set(false) is off
bool lit = led.isOn();  // is it currently on?
```

In the example firmware a **thumbs-up** from Python toggles this LED, an **open
palm** turns it on, and a **fist** turns it off. Want a second LED? `Led` works
on any free pin — add `Led led2(D1);`, call `led2.begin()` in `setup()`, and
light it from a different command.

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

Want to go further? Try one of these — each one is a knob already wired into the
project, just waiting for you to turn it on.

- **React to faces.** Set `ENABLE_FACE_CV = True` in `main.py` and fill in
  `when_face_seen(face)`. Every face gives you `face.emotion` (`"happy"`,
  `"surprised"`, or `"neutral"`) and `face.mouth_open`. Try
  `send_when(face.emotion == "happy", "happy")` — now a smile triggers an action.
- **Recognize objects, not just hands.** Set `ENABLE_OBJECT_CV = True` and pick an
  `OBJECT_MODEL` — `"Cup"`, `"Shoe"`, `"Chair"`, or `"Camera"`. Then in
  `when_object_seen(thing)`, fire on `thing.label`. This uses
  [MediaPipe Objectron](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/objectron.md);
  hold up a cup and watch it light up.
- **Invent a brand-new gesture.** The finger counter can't tell a peace sign from
  a rock-on sign — but the 21 hand landmarks can. Open `cv/gestures.py`, copy the
  `is_thumbs_up` function as a template, and write your own classifier using the
  [hand-landmark map](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker#models)
  (each named point like `INDEX_FINGER_TIP` is a spot you can measure distances
  between).
- **Two-handed gestures.** `when_hand_seen` is called once *per hand*, so a single
  call only ever sees one hand. To require *both* hands, remember the last hand's
  gesture in a module-level variable and check it on the next call.
#### Section: Build More — On the Screen

`App.vue` is yours to redesign. It's a standard
[Vue](https://vuejs.org/guide/introduction.html) single-file component, and the
`command` coming from Python is just a value you can react to. The basic idea:
when a `command` arrives, change what's on the page. From there, anything the web
can do is fair game — swap colors, show images, animate a score counter, or play
a sound.

Resources to take further at home:

- [Vue tutorial](https://vuejs.org/tutorial/) — a hands-on, in-browser intro to
  components, reactivity, and events.
- [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Learn) — how HTML, CSS,
  and JavaScript actually work, including the
  [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
  for sound and the [Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
  for drawing.

#### Section: Build More — In the Real World

The XIAO only blinks an LED and beeps a buzzer *because that's all we wired up*.
The board has many more pins, and each one can drive a new piece of hardware. The
basic idea: solder or plug a part into a pin, then add a `case` to the
`handleProjectCommand` switch in `xiao/xiao.ino` that controls it when a command
arrives.

Resources to add more hardware later:

- [XIAO ESP32C3 wiki](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/) —
  the full pinout and what each pin can do.
- [Seeed Grove modules](https://wiki.seeedstudio.com/Grove_System/) — plug-and-play
  sensors and actuators (servos, displays, distance sensors) that need no soldering.
- [Arduino Project Hub](https://projecthub.arduino.cc/) and
  [Adafruit Learn](https://learn.adafruit.com/) — step-by-step builds you can adapt,
  from servo motors to LED strips.

#### Section: Take It Home

Everything you built runs entirely on your own laptop — no cloud account, no
subscription. To keep tinkering after the workshop and show it off to friends:

1. **Clone the project to your own machine** from
   [github.com/jerrylinew/hwlab](https://github.com/jerrylinew/hwlab). The first
   `uvicorn main:app --reload` installs everything it needs, just like in the lab.
2. **Save your work** with `git`. Run `git add -A && git commit -m "my gestures"`
   after each change so you can always get back to a version that worked. New to
   git? The [GitHub "Hello World" guide](https://docs.github.com/en/get-started/start-your-journey/hello-world)
   walks you through it.
3. **Make it your own demo.** Pick a gesture and a payoff your friends will
   actually react to — a thumbs-up that plays your favorite sound, a peace sign
   that turns the grid into a heart, a smile that flips a light on.

When it works, demo it: make your gesture and watch the command land in the log —
and, if you've wired up a XIAO, out in the real world. Then hand the camera to a
friend and let them try.
