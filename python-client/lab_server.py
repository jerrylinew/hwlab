"""FastAPI and camera plumbing for the HW lab."""

import asyncio
import os
import threading
import time
from collections.abc import Callable

os.environ.setdefault("OPENCV_AVFOUNDATION_SKIP_AUTH", "1")

import cv2
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

from command_block import commands
from cv import FaceDetector, HandDetector, ObjectDetector, init_acceleration


HandGesture = Callable[[object], None]
FaceGesture = Callable[[object], None]
ObjectGesture = Callable[[object], None]


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

    def _run(self) -> None:
        print(f"[cv] Hardware acceleration: {init_acceleration()}")

        cap = cv2.VideoCapture(0)
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

    @app.get("/", response_class=HTMLResponse)
    def index():
        return """
        <html>
          <body style="font-family: sans-serif; max-width: 640px; margin: 40px auto;">
            <h1>OpenCV Gesture &amp; Face Lab - Python server</h1>
            <p>This server is running correctly. It only provides data, not the UI.</p>
            <p><strong>Open the Vue viewer instead</strong> (run <code>npm run dev</code>
               in <code>vue-client</code>, then open the URL it prints, usually
               <a href="http://localhost:5173">http://localhost:5173</a>).</p>
            <p>Endpoints served here:</p>
            <ul>
              <li><a href="/video_feed">/video_feed</a> - live annotated webcam stream</li>
              <li><code>/ws</code> - WebSocket of commands sent to the XIAO</li>
            </ul>
          </body>
        </html>
        """

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

    return app


def _mjpeg_stream(camera_worker: CameraWorker):
    while True:
        frame = camera_worker.get_frame()
        if frame is not None:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        time.sleep(0.033)
