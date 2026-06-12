"""OpenCV Gesture & Face Lab - student-editable client.

Run with:
    uvicorn main:app --reload

This script:
  1. Opens your webcam and runs MediaPipe hand + face detection on each frame.
  2. Draws what it sees on the video, which is streamed to the Vue app at
     /video_feed.
  3. When it recognizes a gesture (open hand / fist) or a face, it sends a
     "command" to the Seeed Studio XIAO webserver (see xiao_client.py) and
     reports it over a WebSocket (/ws) so the Vue app can show it in the
     "commands sent" panel.

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


def count_extended_fingers(hand_landmarks, handedness_label: str) -> int:
    """STUDENTS: this is the core of gesture detection.

    Returns how many fingers are "up" (extended) on one hand, by comparing
    the y-position of each fingertip to the joint below it (lower y = higher
    up on screen = extended), plus a special x-comparison for the thumb.
    """
    landmarks = hand_landmarks.landmark
    fingers_up = 0

    # Thumb: compare x instead of y because the thumb extends sideways.
    thumb_tip_x = landmarks[mp.solutions.hands.HandLandmark.THUMB_TIP].x
    thumb_ip_x = landmarks[mp.solutions.hands.HandLandmark.THUMB_IP].x
    if handedness_label == "Right":
        if thumb_tip_x < thumb_ip_x:
            fingers_up += 1
    else:
        if thumb_tip_x > thumb_ip_x:
            fingers_up += 1

    # Index, middle, ring, pinky: tip above the lower knuckle == extended.
    tip_joint_pairs = [
        (mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP, mp.solutions.hands.HandLandmark.INDEX_FINGER_PIP),
        (mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP, mp.solutions.hands.HandLandmark.MIDDLE_FINGER_PIP),
        (mp.solutions.hands.HandLandmark.RING_FINGER_TIP, mp.solutions.hands.HandLandmark.RING_FINGER_PIP),
        (mp.solutions.hands.HandLandmark.PINKY_TIP, mp.solutions.hands.HandLandmark.PINKY_PIP),
    ]
    for tip, pip in tip_joint_pairs:
        if landmarks[tip].y < landmarks[pip].y:
            fingers_up += 1

    return fingers_up


def classify_gesture(fingers_up: int) -> str | None:
    """STUDENTS: add your own gestures here!

    `fingers_up` is a number from 0 (fist) to 5 (open hand). Return a short
    command name, or None if this isn't a gesture you care about.
    """
    if fingers_up == 0:
        return "fist"
    if fingers_up == 5:
        return "open_hand"
    # STUDENTS: e.g. return "peace_sign" when fingers_up == 2
    return None


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
        face_detection = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.6)
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
                    drawing.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

                    handedness_label = handedness.classification[0].label
                    fingers_up = count_extended_fingers(hand_landmarks, handedness_label)
                    gesture = classify_gesture(fingers_up)
                    if gesture is not None:
                        cv2.putText(
                            frame, gesture, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
                        )
                        self._maybe_send_command(gesture)

            if face_results.detections:
                for detection in face_results.detections:
                    drawing.draw_detection(frame, detection)
                self._maybe_send_command("face_detected")

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
                boundary + b"\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
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
