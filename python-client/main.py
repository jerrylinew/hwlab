"""OpenCV Gesture & Face Lab - student-editable client.

Run with:
    uvicorn main:app --reload

This script:
  1. Opens your webcam and runs MediaPipe hand + face detection on each frame.
  2. Draws what it sees on the video, which is streamed to the Vue app at
     /video_feed.
  3. When it recognizes a thumbs up, it sends the "true" command to the
     Seeed Studio XIAO webserver (see xiao_client.py) and reports it over a
     WebSocket (/ws) so the Vue app can show it in the "commands sent" panel.

Look for the "STUDENTS: " comments below - those are the spots you can
change to add your own gestures or behaviour.
"""

import asyncio
import json
import threading
import time
from datetime import datetime, timezone

import cv2
import mediapipe as mp
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from starlette.websockets import WebSocketState

from xiao_client import send_command

# How long (seconds) to wait before sending the same command again.
# This stops a held-up gesture from spamming the XIAO with commands.
COMMAND_COOLDOWN_SECONDS = 2.0

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CommandBus:
    """Keeps track of connected websocket clients and broadcasts commands."""

    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._clients.discard(websocket)

    def publish(self, command: str, sent_to_xiao: bool) -> None:
        """Called from the (non-async) camera thread to broadcast a command."""
        if self._loop is None:
            return
        message = json.dumps(
            {
                "command": command,
                "sent_to_xiao": sent_to_xiao,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        asyncio.run_coroutine_threadsafe(self._broadcast(message), self._loop)

    async def _broadcast(self, message: str) -> None:
        for websocket in list(self._clients):
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_text(message)
                except Exception:
                    self.disconnect(websocket)


command_bus = CommandBus()


# STUDENTS: example gesture - detects a "thumbs up" (fist with the thumb
# sticking straight up out of it), regardless of which way the hand is
# rotated.
def is_thumbs_up(hand_landmarks) -> bool:
    """Returns True if this hand is making a "thumbs up" gesture.

    Two things have to be true:
      1. The four fingers (index/middle/ring/pinky) are curled into a fist -
         each fingertip is at or below the middle joint.
      2. The thumb tip pokes out *above* the knuckle line of those
         curled fingers - i.e. it's clearly sticking up out of the fist,
         rather than resting across the front of it like a regular fist.

    We don't check which way the thumb points left/right - a thumbs-up can
    be held at many angles, so "pokes out above the fist" is a much more
    reliable signal than "thumb leans toward one particular side".
    """
    landmarks = hand_landmarks.landmark
    Lm = mp.solutions.hands.HandLandmark

    finger_tip_pip = [
        (Lm.INDEX_FINGER_TIP, Lm.INDEX_FINGER_PIP),
        (Lm.MIDDLE_FINGER_TIP, Lm.MIDDLE_FINGER_PIP),
        (Lm.RING_FINGER_TIP, Lm.RING_FINGER_PIP),
        (Lm.PINKY_TIP, Lm.PINKY_PIP),
    ]
    for tip, pip in finger_tip_pip:
        if landmarks[tip].y < landmarks[pip].y:
            return False  # this finger is extended, not curled

    knuckle_ys = [
        landmarks[Lm.INDEX_FINGER_MCP].y,
        landmarks[Lm.MIDDLE_FINGER_MCP].y,
        landmarks[Lm.RING_FINGER_MCP].y,
        landmarks[Lm.PINKY_MCP].y,
    ]
    return landmarks[Lm.THUMB_TIP].y < min(knuckle_ys)


class CameraWorker:
    """Runs the webcam + MediaPipe loop in a background thread."""

    def __init__(self) -> None:
        self._latest_frame_jpeg: bytes | None = None
        self._lock = threading.Lock()
        self._last_sent: dict[str, float] = {}
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def get_frame(self) -> bytes | None:
        with self._lock:
            return self._latest_frame_jpeg

    def _maybe_send_command(self, command: str) -> None:
        """Send `command` to the XIAO, but only if it hasn't been sent
        recently (see COMMAND_COOLDOWN_SECONDS)."""
        now = time.monotonic()
        last_sent = self._last_sent.get(command, 0.0)
        if now - last_sent < COMMAND_COOLDOWN_SECONDS:
            return
        self._last_sent[command] = now

        sent_ok = send_command(command)
        command_bus.publish(command, sent_ok)

    def _run(self) -> None:
        cap = cv2.VideoCapture(0)
        hands = mp.solutions.hands.Hands(
            max_num_hands=2, min_detection_confidence=0.6, min_tracking_confidence=0.5
        )
        face_detection = mp.solutions.face_detection.FaceDetection(
            min_detection_confidence=0.6
        )
        drawing = mp.solutions.drawing_utils

        while self._running:
            success, frame = cap.read()
            if not success:
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            hand_results = hands.process(rgb_frame)
            face_results = face_detection.process(rgb_frame)

            if hand_results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(
                    hand_results.multi_hand_landmarks, hand_results.multi_handedness
                ):
                    drawing.draw_landmarks(
                        frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
                    )

            if face_results.detections:
                for detection in face_results.detections:
                    drawing.draw_detection(frame, detection)

            ok, jpeg = cv2.imencode(".jpg", frame)
            if ok:
                with self._lock:
                    self._latest_frame_jpeg = jpeg.tobytes()

        cap.release()
        hands.close()
        face_detection.close()


camera_worker = CameraWorker()


@app.on_event("startup")
async def on_startup() -> None:
    command_bus.set_loop(asyncio.get_event_loop())
    camera_worker.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    camera_worker.stop()


def _mjpeg_generator():
    boundary = b"--frame"
    while True:
        frame = camera_worker.get_frame()
        if frame is not None:
            yield (
                boundary + b"\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )
        time.sleep(0.033)  # ~30 fps


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(
        _mjpeg_generator(), media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await command_bus.connect(websocket)
    try:
        while True:
            # We don't expect messages from the client, but keep the
            # connection alive and detect disconnects.
            await websocket.receive_text()
    except WebSocketDisconnect:
        command_bus.disconnect(websocket)
