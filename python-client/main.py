"""Thumbs-Up Gesture Server.

Run with:
    uvicorn main:app --reload

Detects a thumbs-up gesture via webcam and sends a command to the
Seeed Studio XIAO ESP32C3. The annotated video feed is streamed at
/video_feed and commands are broadcast over WebSocket at /ws.

All CV logic lives in the cv/ module — this file is just the gesture
example and the server wiring.
"""

import asyncio
import concurrent.futures
import json
import threading
import time
from datetime import datetime, timezone

import cv2
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from starlette.websockets import WebSocketState

from xiao_client import send_command
from cv import init_acceleration, HandDetector, FaceDetector, is_thumbs_up

# ─── Configuration ───────────────────────────────────────────────────────────

websocket = True  # websocket for sending and receiving data from seed studio xiao

# Minimum seconds between sending the same command to the XIAO.
COMMAND_COOLDOWN_SECONDS = 2.0

# Number of consecutive frames a gesture must be detected before firing.
# Prevents single-frame false positives from triggering commands.
GESTURE_CONFIRM_FRAMES = 3

# ─── FastAPI app ─────────────────────────────────────────────────────────────

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── WebSocket command bus ───────────────────────────────────────────────────

class CommandBus:
    """Broadcasts commands to all connected WebSocket clients."""

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
        """Called from the camera thread to broadcast a command."""
        if self._loop is None:
            return
        message = json.dumps({
            "command": command,
            "sent_to_xiao": sent_to_xiao,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        asyncio.run_coroutine_threadsafe(self._broadcast(message), self._loop)

    async def _broadcast(self, message: str) -> None:
        for ws in list(self._clients):
            if ws.client_state == WebSocketState.CONNECTED:
                try:
                    await ws.send_text(message)
                except Exception:
                    self.disconnect(ws)


command_bus = CommandBus()


# ─── Camera worker ───────────────────────────────────────────────────────────

class CameraWorker:
    """Webcam + detection loop running in a background thread."""

    def __init__(self) -> None:
        self._latest_frame: bytes | None = None
        self._lock = threading.Lock()
        self._last_sent: dict[str, float] = {}
        self._running = False
        self._thread: threading.Thread | None = None
        self._send_pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        # Consecutive-frame gesture confirmation counters
        self._thumbs_up_count = 0

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        self._send_pool.shutdown(wait=False)

    def get_frame(self) -> bytes | None:
        with self._lock:
            return self._latest_frame

    def _maybe_send(self, command: str) -> None:
        """Send command to XIAO if cooldown has elapsed (non-blocking)."""
        now = time.monotonic()
        if now - self._last_sent.get(command, 0.0) < COMMAND_COOLDOWN_SECONDS:
            return
        self._last_sent[command] = now
        self._send_pool.submit(self._send_and_publish, command)

    @staticmethod
    def _send_and_publish(command: str) -> None:
        sent_ok = send_command(command) if websocket else False
        command_bus.publish(command, sent_ok)

    def _run(self) -> None:
        accel = init_acceleration()
        print(f"[cv] Hardware acceleration: {accel}")

        cap = cv2.VideoCapture(0)
        # Lower capture resolution to reduce processing load
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        hand_detector = HandDetector(
            max_hands=2,
            detection_confidence=0.7,
            tracking_confidence=0.6,
            model_complexity=0,       # lite model — much faster
            process_every_n_frames=2, # skip every other frame
        )
        face_detector = FaceDetector(
            detection_confidence=0.6,
            process_every_n_frames=3,
        )

        while self._running:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.05)
                continue

            frame = cv2.flip(frame, 1)

            # ── Detection ────────────────────────────────────────────────
            hand_results = hand_detector.process(frame)
            face_results = face_detector.process(frame)

            # ── Gesture: Thumbs Up ───────────────────────────────────────
            # Require GESTURE_CONFIRM_FRAMES consecutive positive detections
            # before firing, to suppress single-frame false positives.
            thumbs_detected = False
            if hand_results and hand_results.multi_hand_landmarks:
                for hand_lm in hand_results.multi_hand_landmarks:
                    if is_thumbs_up(hand_lm):
                        thumbs_detected = True
                        break

            if thumbs_detected:
                self._thumbs_up_count += 1
                if self._thumbs_up_count >= GESTURE_CONFIRM_FRAMES:
                    self._maybe_send("thumbs_up")
            else:
                self._thumbs_up_count = 0

            # ── Draw overlays ────────────────────────────────────────────
            hand_detector.draw(frame, hand_results)
            face_detector.draw(frame, face_results)

            # ── Encode and store ─────────────────────────────────────────
            ret, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                with self._lock:
                    self._latest_frame = jpeg.tobytes()

        cap.release()
        hand_detector.close()
        face_detector.close()


camera_worker = CameraWorker()


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup() -> None:
    command_bus.set_loop(asyncio.get_event_loop())
    camera_worker.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    camera_worker.stop()


def _mjpeg_stream():
    while True:
        frame = camera_worker.get_frame()
        if frame is not None:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        time.sleep(0.033)


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(
        _mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await command_bus.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        command_bus.disconnect(websocket)
