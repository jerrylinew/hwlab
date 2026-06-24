"""FastAPI and camera plumbing for the HW lab."""

import asyncio
import os
import sys
import threading
import time
from collections.abc import Callable
from pathlib import Path

# "0" tells OpenCV's AVFoundation backend to *request* camera access, which
# pops the native macOS permission dialog on first use. Setting this to "1"
# would skip the request and silently fail until access is granted manually.
os.environ.setdefault("OPENCV_AVFOUNDATION_SKIP_AUTH", "0")

import cv2
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from command_block import commands
from cv import FaceDetector, HandDetector, ObjectDetector, init_acceleration


HandGesture = Callable[[object], None]
FaceGesture = Callable[[object], None]
ObjectGesture = Callable[[object], None]

# The prebuilt Vue web app. We serve it from this same server so students only
# ever start one thing. Built with `npm run build` in vue-client/.
WEB_DIST_DIR = Path(__file__).resolve().parent.parent / "vue-client" / "dist"


def _is_wsl() -> bool:
    """True when running inside Windows Subsystem for Linux."""
    if os.environ.get("WSL_DISTRO_NAME"):
        return True
    try:
        with open("/proc/version", encoding="utf-8") as version_file:
            return "microsoft" in version_file.read().lower()
    except OSError:
        return False


def _camera_help_message() -> str:
    """Platform-specific guidance shown when the webcam can't be opened."""
    if _is_wsl():
        return (
            "[cv] No camera found. You're running inside WSL, which does not "
            "share the Windows webcam with Linux (there is no /dev/video0). "
            "Run the Python client on native Windows instead: install Python "
            "for Windows, then start uvicorn from PowerShell/CMD (not WSL)."
        )
    if sys.platform == "darwin":
        return (
            "[cv] Could not open the camera. On macOS, allow camera access for "
            "your terminal in System Settings -> Privacy & Security -> Camera, "
            "then restart the server."
        )
    if sys.platform == "win32":
        return (
            "[cv] Could not open the camera. Make sure a webcam is connected and "
            "not in use by another app (Zoom, Teams, the Camera app), then "
            "restart the server. Check Settings -> Privacy & security -> Camera "
            "and allow desktop apps to access the camera."
        )
    return (
        "[cv] Could not open the camera. Make sure a webcam is connected, not "
        "in use by another app, and that this user can access /dev/video0."
    )


class CameraWorker:
    """Runs webcam detection in the background."""

    def __init__(
        self,
        on_hand_seen: HandGesture | None,
        on_face_seen: FaceGesture | None,
        on_object_seen: ObjectGesture | None,
        enable_hands: bool,
        enable_faces: bool,
        enable_objects: bool,
        object_model: str,
    ) -> None:
        self._on_hand_seen = on_hand_seen
        self._on_face_seen = on_face_seen
        self._on_object_seen = on_object_seen
        self._enable_hands = enable_hands
        self._enable_faces = enable_faces
        self._enable_objects = enable_objects
        self._object_model = object_model
        self._latest_frame: bytes | None = None
        self._lock = threading.Lock()
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
        commands.stop()

    def get_frame(self) -> bytes | None:
        with self._lock:
            return self._latest_frame

    def _open_camera(self) -> "cv2.VideoCapture | None":
        """Open the webcam, waiting through the macOS permission prompt.

        With OPENCV_AVFOUNDATION_SKIP_AUTH=0, the first open blocks on the
        native permission dialog. Retrying lets the feed connect as soon as
        access is granted, without restarting the server.
        """
        for attempt in range(10):
            if not self._running:
                return None
            # DirectShow opens faster and more reliably than the default MSMF
            # backend on Windows; other platforms use the default backend.
            if sys.platform == "win32":
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(0)
            if cap.isOpened():
                return cap
            cap.release()
            if attempt == 0:
                print("[cv] Waiting for camera (allow access if your OS prompts)...")
            time.sleep(1.0)
        return None

    def _run(self) -> None:
        print(f"[cv] Hardware acceleration: {init_acceleration()}")

        cap = self._open_camera()
        if cap is None:
            print(_camera_help_message())
            self._running = False
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        hand_detector = None
        face_detector = None
        object_detector = None

        if self._enable_hands:
            hand_detector = HandDetector(
                max_hands=2,
                detection_confidence=0.7,
                tracking_confidence=0.6,
                model_complexity=0,
                process_every_n_frames=2,
            )

        if self._enable_faces:
            face_detector = FaceDetector(
                detection_confidence=0.6,
                process_every_n_frames=3,
            )

        if self._enable_objects:
            object_detector = ObjectDetector(
                model_name=self._object_model,
                process_every_n_frames=3,
            )

        while self._running:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.05)
                continue

            frame = cv2.flip(frame, 1)
            hand_results = hand_detector.process(frame) if hand_detector else None
            face_results = face_detector.process(frame) if face_detector else None
            object_results = object_detector.process(frame) if object_detector else None

            if self._on_hand_seen and hand_results and hand_results.multi_hand_landmarks:
                for hand in hand_results.multi_hand_landmarks:
                    self._on_hand_seen(hand)

            if self._on_face_seen and face_results and face_results.faces:
                for face in face_results.faces:
                    self._on_face_seen(face)

            if self._on_object_seen and object_results and object_results.objects:
                for detected_object in object_results.objects:
                    self._on_object_seen(detected_object)

            if hand_detector:
                hand_detector.draw(frame, hand_results)
            if face_detector:
                face_detector.draw(frame, face_results)
            if object_detector:
                object_detector.draw(frame, object_results)

            ok, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ok:
                with self._lock:
                    self._latest_frame = jpeg.tobytes()

        cap.release()
        if hand_detector:
            hand_detector.close()
        if face_detector:
            face_detector.close()
        if object_detector:
            object_detector.close()


def create_app(
    on_hand_seen: HandGesture | None = None,
    on_face_seen: FaceGesture | None = None,
    on_object_seen: ObjectGesture | None = None,
    enable_hands: bool = True,
    enable_faces: bool = False,
    enable_objects: bool = False,
    object_model: str = "Cup",
) -> FastAPI:
    """Create the lab server around student gesture functions."""
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    camera_worker = CameraWorker(
        on_hand_seen=on_hand_seen,
        on_face_seen=on_face_seen,
        on_object_seen=on_object_seen,
        enable_hands=enable_hands,
        enable_faces=enable_faces,
        enable_objects=enable_objects,
        object_model=object_model,
    )

    @app.on_event("startup")
    async def on_startup() -> None:
        commands.start(asyncio.get_event_loop())
        camera_worker.start()

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        camera_worker.stop()

    @app.get("/video_feed")
    def video_feed():
        return StreamingResponse(
            _mjpeg_stream(camera_worker),
            media_type="multipart/x-mixed-replace; boundary=frame",
        )

    @app.get("/debug/status")
    def debug_status():
        return commands.debug_status()

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await commands.websocket(websocket)

    # Serve the prebuilt Vue web app from this same server, so the whole lab is
    # one process on one port. Mounted last so the API routes above win. If the
    # app hasn't been built yet, show a short hint instead.
    if (WEB_DIST_DIR / "index.html").exists():
        app.mount("/", StaticFiles(directory=WEB_DIST_DIR, html=True), name="web")
    else:

        @app.get("/", response_class=HTMLResponse)
        def index_not_built():
            return (
                "<html><body style='font-family: sans-serif; max-width: 640px; "
                "margin: 40px auto;'><h1>OpenCV Gesture &amp; Face Lab</h1>"
                "<p>The web app hasn't been built yet. Run "
                "<code>npm install &amp;&amp; npm run build</code> in "
                "<code>vue-client</code>, then restart this server.</p></body></html>"
            )

    return app


def _mjpeg_stream(camera_worker: CameraWorker):
    while True:
        frame = camera_worker.get_frame()
        if frame is not None:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        time.sleep(0.033)
