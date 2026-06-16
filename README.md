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
